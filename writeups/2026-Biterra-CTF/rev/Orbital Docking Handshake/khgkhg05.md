---
ctf_name: "Biterra CTF"
challenge_name: "Orbital Docking Handshake"
category: "rev"
difficulty: "easy"
author: "khgkhg05"
date: "2026-06-23"
points: 0
tags: [rev, decompile, xor]
---

# Orbital Docking Handshake

## 문제 설명

> Trace the handshake routine, recover the correct phrase, and align the approach window.

`orbital_docking_handshake` 바이너리에서 올바른 `Docking phrase`와 `Alignment window`를 복구하는 문제다.

프로그램 실행 시 두 입력을 차례대로 받는다.

```text
Docking phrase:
Alignment window :
```

두 값이 모두 맞으면 내부에 저장된 `encoded_flag` 배열을 복호화해서 플래그를 출력한다.

## 풀이

### 분석

IDA로 디컴파일한 결과를 바탕으로 검증 루틴을 C 코드로 복원했다. 복원한 파일은 `orbital_docking_handshake.c`이다.

핵심 데이터는 `obfuscated_phrase`와 `encoded_flag` 두 배열이다.

```c
uint8_t obfuscated_phrase[] = {
    0x7F, 0x43, 0x5E, 0x25, 0x37, 0x11,
    0xEF, 0xF6, 0xD0, 0xCD, 0xAB, 0xB5,
};

uint8_t encoded_flag[] = {
    0xDA, 0xA1, 0xB5, 0xAD, 0xA4, 0xA8, 0x9B, 0xA0, 0xDF,
    0x88, 0x96, 0xDF, 0x80, 0x30, 0x91, 0x55, 0x68, 0x3A,
    0x7F, 0x7C, 0x1A, 0x58, 0x57, 0x75, 0x42, 0x70, 0x4C,
    0x32, 0x79, 0x28, 0x6B, 0x2E, 0x1A, 0x00, 0x00
};
```

프로그램은 먼저 입력받은 phrase와 비교할 정답 문자열을 만든다. 

```c
for (int i = 0; i < 0xC; i++)
{
    unsigned char mask = 17 * i + 27;

    phrase2[i] = obfuscated_phrase[i] ^ mask;
}

phrase2[12] = 0;
```

즉 `obfuscated_phrase[i]`를 `17 * i + 27`과 XOR하면 실제 phrase가 나온다.

그 다음 alignment window 값을 계산한다.

```c
for (int i = 0; phrase2[i]; i++)
    offset += phrase2[i] * (i + 3);

offset = offset % 1000 + 200;
```

최종 검증은 `strcmp(phrase, phrase2)`와 `atoi(window) == offset`으로 이루어진다.

```c
if (!strcmp(phrase, phrase2))
{
    if (atoi(window) == offset)
    {
        puts("Docking accepted. Flag: ");

        for (int i = 0; i < 0x21; i++)
            printf("%c", encoded_flag[i] ^ (5 * i + phrase2[i % 0xC] + offset));

        return 0;
    }
}
```

따라서 필요한 값은 세 가지다.

1. `obfuscated_phrase`에서 복구한 phrase
2. phrase로 계산한 offset
3. `encoded_flag`를 같은 식으로 복호화한 flag

### 취약점

메모리 취약점이나 런타임 공격이 필요한 문제는 아니다. 검증에 필요한 모든 값이 바이너리 내부에 상수 배열로 들어 있고, 연산도 XOR와 덧셈만 사용한다.

따라서 IDA 디컴파일 결과를 C 코드로 복원한 뒤, 검증 루틴을 그대로 재현하면 입력값과 플래그를 직접 계산할 수 있다.

### 익스플로잇

`decoded.c`는 `orbital_docking_handshake.c`에서 확인한 로직을 바탕으로 실제 값을 뽑아내기 위해 작성한 복호화 코드다.

먼저 phrase를 복구한다.

```c
for (int i = 0; i < 0xC; i++)
{
    unsigned char mask = 17 * i + 27;

    phrase[i] = obfuscated_phrase[i] ^ mask;
}

phrase[12] = 0;
```

이 결과는 다음과 같다.

```text
dockhandsync
```

그 다음 alignment window를 계산한다.

```c
for (int i = 0; phrase[i]; i++)
    offset += phrase[i] * (i + 3);

offset = offset % 1000 + 200;
```

계산 결과는 다음과 같다.

```text
1108
```

마지막으로 `encoded_flag`를 원래 프로그램과 같은 식으로 복호화한다.

```c
for (int i = 0; i < 0x21; i++)
    flag[i] = encoded_flag[i] ^ (5 * i + phrase[i % 0xC] + offset);

printf("%s", flag);
```

`decoded.c` 실행 결과에서 앞의 `0x21`바이트를 보면 플래그가 나온다.

```text
bitctf{{0rb1t4l_d0ck1ng_r0ut1n3}}
```

복구한 입력값을 실제 분석용 실행 파일에도 넣어 확인했다.

```bash
$ printf 'dockhandsync\n1108\n' | ./orbital_docking_handshake.exec
Orbital Docking Handshake
Trace the handshake routine, recover the correct phrase, and align the approach window.
Hint for analysis: the shortest path is still the cleanest one.
Docking phrase: Alignment window : Docking accepted. Flag:
bitctf{{0rb1t4l_d0ck1ng_r0ut1n3}}
```

정리하면 정답 입력은 다음과 같다.

```text
Docking phrase: dockhandsync
Alignment window: 1108
```

## 플래그

```text
bitctf{{0rb1t4l_d0ck1ng_r0ut1n3}}
```

## 추가 파일

- `orbital_docking_handshake.c`: IDA 디컴파일 결과를 바탕으로 분석 대상 프로그램의 핵심 로직을 C 코드로 복원한 파일
- `decoded.c`: 복원한 로직에서 phrase, alignment window, flag 복호화 부분만 추려 실제 플래그를 뽑기 위해 작성한 파일

확인 순서는 `orbital_docking_handshake.c`에서 검증 루틴을 먼저 보고, `decoded.c`에서 같은 로직으로 플래그가 복호화되는 과정을 보면 된다.

## 배운 점

이번 문제에서 가장 중요했던 부분은 IDA 디컴파일 결과를 그대로 C 코드처럼 믿으면 안 된다는 점이었다. 특히 AArch64 호출 규약에서는 첫 번째 인자가 `x0`로 전달되고, 함수 반환값도 다시 `x0`로 돌아온다. 그래서 같은 레지스터가 처음에는 출력 버퍼 포인터였다가, 함수 호출 이후에는 반환값으로 재사용될 수 있다.

예를 들어 `build_expected_phrase(char *phrase2)`처럼 보이는 함수에서 `phrase2`는 처음에 `x0`로 들어온 인자다. 그런데 루프 안에서 `mask_for(i)`를 호출하면 그 반환값도 `x0`에 담긴다. 이때 IDA가 `x0`의 생명주기가 바뀐 것을 제대로 분리하지 못하면, 원래 포인터였던 `phrase2`에 마스크 반환값이 다시 들어온 것처럼 이상한 C 코드를 만든다.

실제로 디컴파일 결과에서 다음과 같은 형태가 보일 수 있다.

```c
phrase2 = (char *)mask_for(i);
v3[i] = obfuscated_phrase[i] ^ (unsigned __int8)phrase2;
```

하지만 이것은 `phrase2`에 진짜 포인터를 대입한다는 뜻이 아니다. 호출 후 `x0`에 `mask_for(i)`의 반환값이 들어왔는데, IDA가 기존에 붙인 `char *phrase2` 타입을 계속 끌고 가면서 생긴 타입 추론 실패로 봐야 한다. 올바른 의미는 다음에 가깝다.

```c
uint8_t mask = mask_for(i);
out[i] = obfuscated_phrase[i] ^ mask;
```

또 `v3 = phrase2;` 같은 코드가 보이는 이유도 이 관점에서 이해할 수 있다. 원래 출력 버퍼 포인터를 보존해야 하는데, `x0`는 `mask_for()` 호출 후 반환값으로 덮이기 때문이다. 따라서 실제 출력 버퍼 접근은 `phrase2`가 아니라 보존된 포인터인 `v3`를 통해 이루어진다.

이 때문에 함수 끝의 `return phrase2;` 같은 표현도 의심해야 한다. 어셈블리에서 마지막에 원래 버퍼 주소를 `x0`로 복구하는 코드가 없다면, 이 함수는 포인터를 반환하는 함수가 아니라 단순히 버퍼를 채우는 `void` 함수일 가능성이 높다. 더 정확한 복원은 다음 형태다.

```c
void build_expected_phrase(char *out)
{
    for (int i = 0; i < 12; i++)
        out[i] = obfuscated_phrase[i] ^ mask_for(i);

    out[12] = '\0';
}
```

정리하면 이 문제는 문자열 XOR 자체보다, 디컴파일러가 호출 규약과 레지스터 재사용 때문에 잘못 합친 변수를 사람이 다시 분해하는 과정이 핵심이었다. 디컴파일 결과에 이상한 캐스팅이나 포인터 대입이 보일 때는 고수준 C 코드로만 해석하지 말고, 해당 레지스터가 인자였는지 반환값이었는지까지 같이 확인해야 한다.
