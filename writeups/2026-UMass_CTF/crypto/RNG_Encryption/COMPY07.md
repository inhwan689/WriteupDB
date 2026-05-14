---
ctf_name: "UMass CTF"
challenge_name: "RNG Encryption"
category: "crypto"
difficulty: "easy"
author: "COMPY07"
date: "2026-04-14"
points: 100
tags: [crypto, rsa]
---

# RNG Encryption

## 문제 설명

> 암호화된 메시지를 해독하고 플래그를 찾아내세요!

- `encoder.py` — 암호화 로직
- `output.txt` — seed와 flag 암호문 제공됨

## 풀이

### 분석

제공된 `encoder.py`의 암호화 흐름을 요약하면 다음과 같다.

1. `text = "I_LOVE_RNG"` (known plaintext)
2. `(n, seed) = RSA_enc(text)`
    - `seed = pow(plain_num, 7, n)` ← RSA ciphertext of "I_LOVE_RNG"
3. `flag_bits`를 10번 `random.shuffle` (`seed*(i+1)`로 seeding)
4. `enc_seed = pow(seed, 7, n)` ← seed를 다시 한번 RSA 암호화
5. `output.txt`에 `enc_seed`와 `shuffled_flag`를 출력

### 취약점

RSA에서 e=7이고 n은 4096비트(2048비트 소수 두 개의 곱)이다.
`plain_num = int.from_bytes("I_LOVE_RNG".encode(), "big")`는 고작 79비트 길이를 가진다.

- `seed = plain_num^7 mod n`
    - `plain_num^7`의 비트 수 = 79 × 7 = 553비트 -> n보다 훨씬 작음
    - 따라서 mod 연산이 실질적으로 발생하지 않음: `seed = plain_num^7`

- `enc_seed = seed^7 mod n`
    - `seed^7`의 비트 수 = 553 × 7 = 3871비트 -> 역시 n보다 작음
    - 마찬가지로: `enc_seed = seed^7 = plain_num^49`

`plain_num`은 우리가 이미 알고 있는 값("I_LOVE_RNG")이므로, 모듈러 연산 없이도 아래와 같이 직접 seed 복원이 가능하다.

`seed = plain_num ** 7`

### 익스플로잇

복호화는 다음 3단계로 진행된다.

seed복원, shuffle 역산하고 그냥 문자열로 출력하면 될 것이다.


이 과정을 코드로 작성하면 다음과 같다.

```python
import random

plain_text = "I_LOVE_RNG"
plain_num = int.from_bytes(plain_text.encode(), "big")
e = 7

# output.txt에서 제공된 enc_seed와 enc_flag_hex
enc_seed = <output.txt의 seed 값>
enc_flag_hex = "a9fa3c5e51d4cea498554399848ad14aa0764e15a6a2110b6613f5dc87fa70f17fafbba7eb5a2a5179"

# Step 1: seed 복원 (no modular reduction 취약점 이용)
seed = plain_num ** e

# Step 2: flag_bits 추출
enc_flag_bytes = bytes.fromhex(enc_flag_hex)
flag_bits = []
for byte in enc_flag_bytes:
    flag_bits.extend(list(bin(byte)[2:].zfill(8)))

# Step 3: shuffle 역순 적용 함수
def invert_shuffle(arr, rng_seed):
    indices = list(range(len(arr)))
    random.seed(rng_seed)
    random.shuffle(indices)
    result = [None] * len(arr)
    for i, idx in enumerate(indices):
        result[idx] = arr[i]
    return result

# 역순으로 (i=9 → i=0) 원복
for i in range(9, -1, -1):
    flag_bits = invert_shuffle(flag_bits, seed * (i + 1))

# Step 4: 비트 → 문자열 변환
flag = ""
for i in range(0, len(flag_bits), 8):
    flag += chr(int(''.join(flag_bits[i:i+8]), 2))

print(flag)
```

플래그

```
UMASS{tH4Nk5_f0R_uN5CR4m8L1nG_mY_M3554g3}
```

배운 점

RSA에서 e가 작고 메시지가 충분히 작으면 모듈러 환원이 일어나지 않아 암호화가 완전히 무의미해짐을 직접 확인했다.
