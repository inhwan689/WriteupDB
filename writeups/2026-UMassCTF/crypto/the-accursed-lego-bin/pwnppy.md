---
ctf_name: "UMassCTF"
challenge_name: "The Accursed Lego Bin"
category: "crypto"           # web / pwn / rev / crypto / misc
difficulty: "easy"      # easy / medium / hard / insane
author: "pwnppy"
date: "2026-04-11"
points: 100
tags: [CRYPTO]
---

# The Accursed Lego Bin

## 문제 설명

> I dropped my message into the bin of Legos. It's all scrambled up now. Please help.

- **문제 분류**: Crypto

## 풀이

### 분석

`output.txt`에는 7제곱된 형태의 `seed`값과 비트 단위로 셔플링된 `flag`의 헥사 값이 포함되어 있다.
1.  **시드 복구**: 주어진 `enc_seed`는 원래 시드의 7제곱($seed^7$)이므로, 7제곱근을 구하여 원래의 정수 시드를 찾는다.
2.  **셔플링 역추적**: `random.seed()`가 동일하면 `random.shuffle()`의 결과도 동일하다는 점을 이용하여, 셔플링된 인덱스를 역으로 매핑한다.

### 취약점

- **PRNG**의 특성을 활용한다.
- 파이썬의 `random` 모듈은 시드 값이 같으면 항상 같은 난수 시퀀스를 생성하므로, 셔플링에 사용된 시드만 알아내면 셔플링 과정을 역산할 수 있다.

### 익스플로잇

1.  **시드 계산**: `decimal` 모듈을 사용하여 높은 정밀도로 7제곱근을 구한 뒤 반올림하여 원래의 정수 `seed`를 구한다.
2.  **인덱스 재생성**: 0부터 전체 비트 길이까지의 리스트를 만든 후, 문제 로직과 동일하게 10번의 셔플링을 수행하여 최종적으로 비트들이 위치한 인덱스 번호를 파악한다.
3.  **역치환**: 셔플링된 위치에 있는 비트들을 원래의 인덱스 위치로 되돌린 후, 8비트씩 묶어 문자로 변환한다.

```python
import random
import decimal

def decrypt():
    data = {}
    with open("./output.txt", "r") as f:
        for line in f:
            if " = " in line:
                key, val = line.strip().split(" = ")
                data[key] = val

    enc_seed = int(data['seed'])
    flag_hex = data['flag']

    decimal.getcontext().prec = 1000 
    seed = int(round(pow(decimal.Decimal(enc_seed), decimal.Decimal(1)/7)))

    flag_bytes = bytes.fromhex(flag_hex)
    shuffled_bits = []
    for b in flag_bytes:
        shuffled_bits.extend(list(bin(b)[2:].zfill(8)))

    num_bits = len(shuffled_bits)
    indices = list(range(num_bits))
    
    for i in range(10):
        random.seed(seed * (i + 1))
        random.shuffle(indices)

    original_bits = [None] * num_bits
    for current_pos, original_pos in enumerate(indices):
        original_bits[original_pos] = shuffled_bits[current_pos]

    recovered_flag = ""
    for i in range(0, num_bits, 8):
        byte_str = "".join(original_bits[i:i+8])
        recovered_flag += chr(int(byte_str, 2))

    print(f"[*] Recovered Seed: {seed}")
    print(f"[+] Flag: {recovered_flag}")

if __name__ == "__main__":
    decrypt()
```

## 플래그

```
UMASS{tH4Nk5_f0R_uN5CR4m8L1nG_mY_M3554g3}
```

## 배운 점

- 큰 수의 거듭제곱근을 구할 때 정확도를 위해 decimal 모듈을 사용한다.
- 비트 단위 연산, 인덱스 매핑하기.
