---
ctf_name: "Dreamhack"
challenge_name: "Secret Message"
category: "rev"           # web / pwn / rev / crypto / misc
difficulty: "easy"      # easy / medium / hard / insane
author: "ssong17"
date: "2026-04-11"
points: -
tags: [태그1, 태그2]
---

# 문제명

## 문제 설명

드림이는 비밀스런 이미지 파일을 자신이 공부한 알고리즘을 통해 인코딩 하였어요.

인코딩 프로그램을 분석하여 원본 이미지를 알아내주세요.

원본 파일을 구한 경우 imageviewer.py를 통해 이미지를 볼 수 있습니다.

- 문제 URL / 파일 등 접속 정보: 이미지 파일, 이미지 뷰어 파이썬 파일, prob ELF 파일

## 풀이

### 분석

secretMessage.raw 파일을 읽어 특정 알고리즘으로 압축/암호화하여 secretMessage.enc를 생성한 후 원본을 삭제함.


- FUN_001007fa:
데이터의 연속성을 이용한 RLE 계열의 압축 알고리즘을 사용함.

현재 읽은 문자(local_10)와 이전 문자(local_c)가 같을 경우, 중복되는 문자의 개수를 세어 0x00 ~ 0xff 사이의 바이트 값으로 기록함.

-> [문자][문자][중복 횟수]

예를 들어, dddd는 dd를 먼저 출력하고, 나머지 d 2개에 대한 개수인 2를 뒤에 붙여 dd2로 저장함.

코드흐름은 다음과 같다.

1. secretMessage.raw와 secretMessage.enc 파일을 각각 rb, wb 모드로 오픈.

2. fgetc를 통해 한 바이트씩 읽으며 이전 바이트와 비교.

3. 연속된 문자가 발견되면 반복 횟수를 fputc로 기록.

4. 작업 완료 후 원본 .raw 파일 삭제.

### 취약점

해당 바이너리가 수행하는 "암호화"는 암호학적으로 안전한 알고리즘이 아닌, 단순한 데이터 압축 방식

바이너리 내부에 인코딩 로직이 그대로 노출되어 있어, 역연산 과정을 통해 원본 데이터를 100% 복구할 수 있음.

### 익스플로잇

기드라로 분석한 인코딩 로직을 역으로 수행하는 복호화 도구를 C언어로 작성하여 원본 이미지 데이터를 복구함.

```C
#include <stdio.h>
void Decryption(FILE *enc, FILE *dec);

int main() {
    FILE *enc;
    FILE *dec;

    enc = fopen("secretMessage.enc", "rb");
    dec = fopen("secretMessage.raw", "wb");

    Decryption(enc, dec);
    puts("done!");

    fclose(enc);
    fclose(dec);

    return 0;
}

void Decryption(FILE *enc, FILE *dec) {
    int prev = -1;
    int curr;

    while ((curr = fgetc(enc)) != EOF) {
        fputc(curr, dec);
        if (curr == prev) {
            int count = fgetc(enc);
            if (count == EOF) break;
            for (int i = 0; i < count; i++) fputc(curr, dec);
        } prev = curr;
    }
}
```

## 플래그

```
DH{93589e6c1db065fa95075ab5e3790bc1}
```

## 배운 점

.
