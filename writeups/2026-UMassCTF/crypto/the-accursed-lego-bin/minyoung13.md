---
ctf_name: "UmassCTF 2026"
challenge_name: "The Accursed Lego Bin"
category: "crypto"           # web / pwn / rev / crypto / misc
difficulty: "easy"      # easy / medium / hard / insane
author: "minyoung13"
date: "2026-04-11"
points: 100
tags: [RSA, random, shuffle]
---

# The Accursed Lego Bin

## 문제 설명

> I dropped my message into the bin of Legos. It's all scrambled up now. Please help.

-  첨부파일 : 'encoder.py', 'output.txt'

## 풀이

### 분석

문제에서 제공된 `encoder.py`를 보면 전체 흐름은 다음과 같다.

1. flag를 비트 단위로 변환
2. 특정 seed를 기반으로 `random.shuffle`을 10번 수행
3. 결과를 hex로 출력

### 취약점

문제에서 구할 수 있는 암호 요소들은 다음과 같다.
- e = 7
- seed = plain^7 mod n
- enc_seed = seed^7 mod n = plain^49 mod n
- plain = "I_LOVE_RNG"

- 이때 n은 4096bit이고, plain은 짧은 문자열이므로 plain^49 < n
- 따라서 enc_seed = plain^49 mod n = plain^49, seed = plain^7 mod n = plain^7

### 익스플로잇

1. seed = plain^7 계산
2. flag : hex to bit
3. shuffle 역순으로 되돌리기
4. bit to string

```python
import random

# 주어진 값
enc_flag_hex = "a9fa3c5e51d4cea498554399848ad14aa0764e15a6a2110b6613f5dc87fa70f17fafbba7eb5a2a5179"

# Step 1: seed 복구
plain = int.from_bytes(b"I_LOVE_RNG", "big")
seed = pow(plain, 7)

# Step 2: hex → bit 배열
enc_bytes = bytes.fromhex(enc_flag_hex)

bits = []
for b in enc_bytes:
    bits.extend(list(bin(b)[2:].zfill(8)))

# Step 3: shuffle 복원
def unshuffle(arr, seed):
    random.seed(seed)
    idx = list(range(len(arr)))
    random.shuffle(idx)

    res = [None] * len(arr)
    for i, j in enumerate(idx):
        res[j] = arr[i]
    return res

for i in reversed(range(10)):
    bits = unshuffle(bits, seed * (i + 1))

# Step 4: bit → string
flag = ""
for i in range(0, len(bits), 8):
    byte = bits[i:i+8]
    flag += chr(int(''.join(byte), 2))

print("FLAG:", flag)
```

## 플래그

```
UMASS{tH4Nk5_f0R_uN5CR4m8L1nG_mY_M3554g3}
```

## 배운 점

- random.shuffle은 내부적으로 인덱스를 섞어서 재배열하는 것과 동일
- 따라서 seed가 동일하면 결과를 완전히 재현 가능
- 여러 번 shuffle된 데이터는 역순으로 unshuffle하면 복구 가능
- RSA에서 작은 지수(e=7) & 작은 평문은 Low exponent 공격에 취약