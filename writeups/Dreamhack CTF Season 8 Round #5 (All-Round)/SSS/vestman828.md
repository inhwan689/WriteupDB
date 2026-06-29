---
ctf_name: "Dreamhack CTF Season 8 Round #5 (All-Round)"
challenge_name: "SSS"
category: "crypto"
difficulty: "medium"
author: "vestman828"
date: "2026-06-01"
tags: [shamir_secret_sharing, lcg, lattice]
---

# SSS

## 문제 설명

> Dreamhack CTF Season 8 Round #5 (All-Round)에 SSS 문제입니다. Crypto입니다.

## 풀이

### 분석

```py
n, k = 5, 3
BITS = 512

class ShamirSecretSharing:
    def split(self, n, k, seed):
        coeffs = []
        for _ in range(k):
            coeffs.append(seed % self.p)
            seed //= self.p
        self.coeffs = coeffs

        shares = []
        for x_val in range(1, n + 1):
            y_val = 0
            for i, c in enumerate(coeffs):
                y_val = (y_val + c * pow(x_val, i, self.p)) % self.p
            shares.append((x_val, y_val))
        return shares
```

`split`은 RNG state를 `p`진법으로 쪼개서 Shamir polynomial의 계수로 사용합니다.
`k = 3`이고 RNG state는 `2^1533` 미만이며, `p`는 512비트 소수라서 다음처럼 표현됩니다.

```txt
state = c0 + c1*p + c2*p^2
```

출력되는 share는 항상 `x = 1` 하나뿐입니다.

```txt
y = c0 + c1 + c2 (mod p)
```

`c0 + c1 + c2 < 3p`이므로 어떤 `t in {0,1,2}`에 대해

```txt
c0 + c1 + c2 = y + t*p
```

입니다. 따라서

```txt
state - (y + t*p)
= (p-1)c1 + (p^2-1)c2
= (p-1)(c1 + (p+1)c2)
```

가 되어, 각 state는 `p-1`로 나눈 나머지를 거의 알고 있는 상태가 됩니다.

```txt
state = y + t*p + (p-1)z
```

이제 `t`의 경우의 수는 `3^4 = 81`개뿐이므로 모두 시도합니다.
고정된 `t`에 대해 LCG 식

```txt
s_i = A_i*s_0 + B_i (mod 2^1533)
```

과 위 식을 합치면

```txt
z_i = A_i*z_0 + C_i (mod 2^1533 / gcd(p-1, 2^1533))
```

꼴의 식이 나옵니다. 실제 `z_i`들은 `2^1533 / (p-1)`보다 작으므로, 작은 해를 찾는 lattice 문제로 풀 수 있습니다.
state를 복원하면 각 블록의 키는 `sha256(str(state % p).encode())`로 계산됩니다.

### 익스플로잇

```py
from itertools import product
from hashlib import sha256
from math import gcd
from sage.all import *

A = ...      # printed RNG a
B = ...      # printed RNG b
p = ...      # printed prime
ys = [...]   # share y values
cts = [bytes.fromhex(x) for x in [...]]

M = 1 << (511 * 3)
m = p - 1
g = gcd(m, M)
N = M // g
m0 = m // g
inv_m0 = inverse_mod(m0, N)
Z = M // m + 10

alphas = [1]
betas = [0]
for _ in range(1, 4):
    alphas.append((alphas[-1] * A) % M)
    betas.append((A * betas[-1] + B) % M)

def babai_closest_vector(B, target):
    B = B.LLL()
    G = B.gram_schmidt()[0]
    diff = vector(QQ, target)

    for i in reversed(range(B.nrows())):
        c = round((diff * G[i]) / (G[i] * G[i]))
        diff -= c * B[i]

    return vector(ZZ, target) - vector(ZZ, diff)

def xor_key(ct, key):
    return bytes(c ^ key[i % len(key)] for i, c in enumerate(ct))

for ts in product(range(3), repeat=4):
    bases = [ys[i] + ts[i] * p for i in range(4)]

    Cs = []
    ok = True
    for i in range(1, 4):
        num = alphas[i] * bases[0] + betas[i] - bases[i]
        if num % g != 0:
            ok = False
            break
        Cs.append((num // g * inv_m0) % N)
    if not ok:
        continue

    Bmat = Matrix(ZZ, [
        [1, alphas[1] % N, alphas[2] % N, alphas[3] % N],
        [0, N, 0, 0],
        [0, 0, N, 0],
        [0, 0, 0, N],
    ])
    target = vector(ZZ, [0, -Cs[0], -Cs[1], -Cs[2]])

    close = babai_closest_vector(Bmat, target)
    zs = list(close - target)
    if any(z < 0 or z > Z for z in zs):
        continue

    states = [bases[i] + m * ZZ(zs[i]) for i in range(4)]
    if any(s < 0 or s >= M for s in states):
        continue
    if any(states[i+1] != (A * states[i] + B) % M for i in range(3)):
        continue

    flag = b""
    for state, ct in zip(states, cts):
        secret = state % p
        key = sha256(str(secret).encode()).digest()
        flag += xor_key(ct, key)

    if flag.startswith(b"DH{"):
        print(flag)
        break
```

## 플래그

```
DH{e2be0d433b32bbe5712b36744b65ceaacc71695389c89e967816b3edf7bc74c7}
```

## 배운 점

Shamir share를 하나만 공개해도 안전해 보일 수 있지만, 계수를 RNG state의 자리수로 직접 만들면 share가 state의 모듈러 정보를 누출합니다. 연속된 LCG state에 대한 부분 정보는 격자로 복원할 수 있습니다.
