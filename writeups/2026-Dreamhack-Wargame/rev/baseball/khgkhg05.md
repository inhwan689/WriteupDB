---
ctf_name: "Dreamhack-Wargame"
challenge_name: "baseball"
category: "rev"           # web / pwn / rev / crypto / misc
difficulty: "medium"      # easy / medium / hard / insane
author: "khgkhg05"
date: "2026-05-05"
points: 
tags: [태그1, 태그2]
---

# 문제명

baseball

## 문제 설명

주어진 실행 파일 `baseball`과 입출력 파일들을 분석하여, `flag_out.txt`에 인코딩된 원문 flag를 복구하는 문제이다.

프로그램은 다음과 같이 실행된다.
`./baseball <table filename> <input filename>`

## 풀이

IDA로 Decompile한 뒤, 분석을 용이하게 하기 위해 새로운 C 프로그램으로 복원하였다.
해당 파일은 `baseball.c`이다.

해당 파일을 바탕으로 table 복호화 C 프로그램을 만들었다.
해당 파일은 `baseball_decode_table.c`이다.

### 분석

`baseball` 파일은 실행할 때 `<table filename>`과 `<input filename>`을 요구한다.
`table file`의 크기가 64byte이지 않으면 오류 메시지를 출력하며 프로그램을 종류한다.

어떠한 함수에게 매개변수로 `input file`의 내용과 `input file`, 포인터 변수를 전달하며 해당 함수를 호출한다.

`index[i + 0] = input[j + 0] >> 2`
`index[i + 1] = input[j + 1] >> 4 | (input[j + 0] << 4) & 0x30`
`index[i + 2] = input[j + 2] >> 6 | (input[j + 1] << 2) & 0x3C`
`index[i + 3] = input[j + 2] & 0x3F`
위 식을 예시를 들어 분석해보자.

`input[0] = aaaa aaaa`
`input[1] = bbbb bbbb`
`input[2] = cccc cccc`라고 하자.

`index[0] = 00aa aaaa`
`index[1] = 00aa bbbb`
`index[2] = 00bb bbcc`
`index[3] = 00cc cccc`

위 분석을 통해 알 수 있는 점은 input 3바이트를 조작하여 index 4바이트를 만들어내며, 만들어진 index의 상위 2비트는 0이라는 점이다.

위 식을 반복하여 `index[]` 배열을 설정한 후, `output[i] = table[index]`를 수행한다.

입력값에 대해 모두 위 연산을 진행한 후, `input_file_end - input_file_start` 값이 1일 때 '='을 두 번, 2일 때 '='을 한 번 padding한다.

`table file`의 크기가 64byte여야 하는 점, 위 연산의 논리 분석 결과, '='으로 padding하는 점 등을 고려했을 때 이 함수는 `base64 encoding`을 수행하는 함수임을 알 수 있다.
이때 `base64 encoding`은 일반적인 방식이 아닌, 주어진 `table`을 바탕으로 수행한다.

### 취약점

주어진 `text_in.txt`를 `base64 encoding`한 결과가 `text_out.txt`이다.
`input`이 주어졌으므로 `index`를 구할 수 있다.
`output` 또한 주어졌으므로 `output[i] = table[index]`를 이용하여 `table`을 구할 수 있다.

### 익스플로잇

`table[]`를 선언한 후 `memset(table, '?', 64)` 함수를 이용하여 설정한다.
`base64 encoding`의 결과값의 각 바이트에서 상위 2비트까지는 실 데이터 값이 아닌 점, `base64 encoding`을 역산할 수 있는 점을 이용하여 아래와 같이 table을 구할 수 있다.

```
int j = 0;

for (int i = 0; j + 2 < 149; i += 4, j += 3)
{
	index[i] = input[j] >> 2;
    index[i + 1] = (input[j + 1] >> 4) | ((input[j] << 4) & 0x30);
    index[i + 2] = (input[j + 2] >> 6) | ((input[j + 1] << 2) & 0x3C);
    index[i + 3] = input[j + 2] & 0x3F;
}

index[196] = input[147] >> 2;
index[197] = (input[148] >> 4) | ((input[147] << 4) & 0x30);
index[198] = (input[148] << 2) & 0x3C;

for (int i = 0; i < 199; i++)
	table[index[i]] = output[i];
```

이후 `table`을 출력하고, 쓰이지 않아서 위치를 확정할 수 없는 문자들을 출력하여 파악한다.

`baseball_decode_table.c`의 실행결과는 아래와 같다.
`?hs?RF/tuI?W3d?YnSvV7OUQbZcN4J2?1GL+ejA8?r?lpg5ak?Bo0qyDHm??M9?P
unused : C E K T X f i w x z 6
unknown index : 0 3 10 14 31 40 42 49 58 59 62`

?의 위치에 `unknown index`를 임의로 배정하여 `table`을 설정한 후, `base64 decoder`를 통해 flag를 출력한다.

`base64 decoder` 사용은 images 폴더에 기록해두었다.

```C
`baseball_decode_table.c`
```

## 플래그

```
DH{REDACTED}
```

## 배운 점

base64는 입력 3바이트(24비트)를 6비트 index 4개로 나누는 방식으로 동작한다.
`0x30`, `0x3C`, `0x3F`와 같은 마스크는 6비트 index를 만들기 위한 비트 추출에 사용된다.
일단 base64와 custom base64의 차이는 encoding 구조가 아니라 alphabet table이다.
known plaintext와 그 출력값이 주어지면 `table[index] = output_char` 관계를 이용해 custom alphabet을 복원할 수 있다.
table 전체를 복원하지 못하더라도, 목표 ciphertext에 등장하는 문자들의 역매핑만 알면 decoding이 가능하다.
