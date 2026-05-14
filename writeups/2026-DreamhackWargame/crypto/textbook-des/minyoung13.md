---
ctf_name: "Dreamhack Wargame"
challenge_name: "Textbook-DES"
category: "crypto"           # web / pwn / rev / crypto / misc
difficulty: "easy"      # easy / medium / hard / insane
author: "minyoung13"
date: "2026-05-05"
points: 0
tags: [des, tripledes]
---

# Textbook-DES

## 문제 설명

> DES가 더이상 안전하지 않다구요? 혹시 Triple-DES라고 들어보셨나요?

- https://dreamhack.io/wargame/challenges/1214
- 첨부파일 : cipher.py, flag, prob.py

## 풀이

### 분석

문제에서 제공된 cipher.py를 보면, 2-key Triple DES 구조로 구현되어 있다.
- 키 구성: key1, key2, key1 

encrypt 함수는 mode 문자열(E/D)에 따라 DES encrypt/decrypt를 순서대로 적용하는 구조이다.
flag는 EDE로 암호화되며, 이를 한번에 복호화하는 것(DED 모드로 암호화하는 것)은 코드 단에서 제한되고 있다.

### 취약점

사용자가 E/D를 선택할 수 있어, 복호화 oracle을 제공하는 것과 동일하다.
주어진 문제에서는 DED 모드로 암호화하는 것이 막혀 있으나, 모드의 조합으로 복호화된 flag를 구할 수 있다.

### 익스플로잇

1. 2를 입력하여 EDE 모드로 암호화된 flag를 받는다.
2. DDD, EED, EED 순서로 암호화하여 원문을 찾아낸다.

이를 나타내면 아래와 같다.
```
EDE(flag) -> E1 - D2 - E1 - P
DDD(C) -> D1 - D2 - D1 - E1 - D2 - E1 - P => D1 - D2 - D2 - E1 - P
EED(C) -> D1 - E2 - E1 - D1 - D2 - D2 - E1 - P => D1 - D2 - E1 - P
EED(C) -> D1 - E2 - E1 - D1 - D2 - E1 - P => P
```

```python
from pwn import *

def enc(msg, mode):
    p.sendlineafter(b'> ', b'1')
    p.sendlineafter(b'> ', msg)
    p.sendlineafter(b'> ', mode)
    p.recvuntil(b'> ')
    msg_enc = p.recvline()[:-1].decode()
    return msg_enc


# p = process("./prob.py")
p = remote('host8.dreamhack.games', 16957)

p.sendlineafter(b'> ', b'2')
p.recvuntil(b'> ')
flag_enc = p.recvline()[:-1].decode()

plain1 = enc(flag_enc, b'DDD')
plain2 = enc(plain1, b'EED')
flag = enc(plain2, b'EED')

flag_bytes = bytes.fromhex(flag)
print(flag_bytes)
```

## 플래그

```
flag{REDACTED}
```

## 배운 점

- 특정 모드가 제한되더라도 조합을 통해 평문을 얻어낼 수 있음을 알게 되었다.
