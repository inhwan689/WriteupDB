---
ctf_name: "RitsecCTF 2026"
challenge_name: "T-reasure Chest"
category: "rev"           # web / pwn / rev / crypto / misc
difficulty: "easy"      # easy / medium / hard / insane
author: "minyoung13"
date: "2026-04-05"
points: 10
tags: [TEA, crypto]
---

# 문제명
- T-reasure Chest

## 문제 설명

> Score! You found a treasure chest! Now if only you could figure out how to unlock it... maybe there's a magic word?
> Author: @somnomly

-  첨부파일 : 'treasure' (ELF 바이너리)

## 풀이

### 분석

문제에서 제공된 바이너리를 실행하려고 하면 GLIBC 버전 문제로 실행이 되지 않았다.  
따라서 동적 분석 대신 정적 분석 도구를 사용하여 접근하였다.

1. `file` 명령어로 확인한 결과, 64-bit ELF 파일이며 strip 되어 있어 심볼 정보가 제거되어 있었다.
2. Ghidra로 바이너리를 로드하고 Auto Analysis를 수행하였다.
3. 함수 목록을 확인한 뒤, `puts`, `fgets` 등을 사용하는 함수를 기준으로 main 함수를 식별하였다. (FUN_0040131b)

4. FUN_0040131b 함수 분석
- 사용자 입력을 `fgets`로 받음
- 특정 함수(`FUN_004012a9`)를 호출하여 입력값을 변환
- 변환된 결과를 `memcmp`로 비교 (local_10(문자열의 길이+8로 나눈 나머지) == 0x22 이고, local_20 == &DAT_00404080)
- 즉, 입력값을 특정한 방식으로 변환한 결과가 정해진 값과 같아야 한다.

5. FUN_004012a9(buf, len, key) 함수 분석
- 버퍼를 8바이트 단위로 읽고(`param_1 + (local_c << 3)`) 함수(`FUN_004011c6`)를 호출하여 변환 수행
- 입력은 8바이트 단위로 읽지만 반복은 len/4만큼 수행

6. FUN_004011c6(input, key)
- 32 rounds 반복
- 64bit input을 두 개의 32bit 블록으로 나누어 반복적으로 업데이트 후 64bit 암호문 생성
- 두 개의 블록이 서로에게 영향을 주는 구조
```
for 32 rounds:
    sum += delta (0x9E3779B9)
    v0 += f(v1, key[0], key[1], sum)
    v1 += f(v0, key[2], key[3], sum)
```
7. key 분석

- FUN_0040131b에서 local_38, local_30 을 리틀엔디안으로 변환하면 `tiny_encrypt_key`이다.
```c
local_38 = 0x636e655f796e6974;
local_30 = 0x79656b5f74707972;
```
- 즉, 입력값을 `tiny_encrypt_key`로 암호화한다.

### 취약점

입력 검증 로직을 분석하여, 미리 정의된 암호문(DAT_00404080)을 복호화함으로써 원래 입력값을 구할 수 있다.

### 익스플로잇

1. DAT_00404080 값 확인
2. TEA 복호화 함수 구현

```python
import struct

key_bytes = b"tiny_encrypt_key"

# 4개의 32bit 정수로 변환 (little endian)
key = list(struct.unpack("<4I", key_bytes))

cipher = bytes([
    0x38,0x75,0x5b,0xcb,0x44,0xd2,0xbe,0x5d,
    0x96,0x9c,0x56,0x43,0xea,0x98,0x06,0x75,
    0x4a,0x48,0x13,0xe6,0xd4,0xe8,0x8e,0x4f,
    0x72,0x70,0x8b,0xff,0xdc,0x99,0xf8,0x76,
    0xc5,0xc9
])

def tea_decrypt(v0, v1, key):
    delta = 0x9E3779B9
    sum_val = (delta * 32) & 0xffffffff

    for _ in range(32):
        v1 = (v1 - (((v0 << 4) + key[2]) ^ (v0 + sum_val) ^ ((v0 >> 5) + key[3]))) & 0xffffffff
        v0 = (v0 - (((v1 << 4) + key[0]) ^ (v1 + sum_val) ^ ((v1 >> 5) + key[1]))) & 0xffffffff
        sum_val = (sum_val - delta) & 0xffffffff

    return v0, v1

plaintext = b""

for i in range(0, len(cipher) - (len(cipher) % 8), 8):
    block = cipher[i:i+8]

    v0, v1 = struct.unpack("<2I", block)
    d0, d1 = tea_decrypt(v0, v1, key)

    plaintext += struct.pack("<2I", d0, d1)

print(plaintext.decode())
```

## 플래그

```
RS{oh_its_a_TEAreasure_chest}
```

## 배운 점

- 본 문제는 사용자 입력을 TEA 알고리즘으로 암호화한 후, 특정 암호문과 비교하는 구조이다.
- 암호문을 TEA 복호화(역연산)하여 원문을 얻을 수 있다.
- TEA (Tiny Encryption Algorithm) 의 구조와 특징을 알아볼 수 있었다.
    - magic number 0x9E3779B9 (= -0x61C88647 = 2654435769)
    - 32 rounds
    - v0 += ((v1 << 4) + k0) ^ (v1 + sum) ^ ((v1 >> 5) + k1);
    - v1 += ((v0 << 4) + k2) ^ (v0 + sum) ^ ((v0 >> 5) + k3);