---
ctf_name: "Dreamhack CTF Season 8 Round #4 (Crypto)"
challenge_name: "wNAF"
category: "crypto"
difficulty: "medium"
author: "vestman828"
date: "2026-05-02"
tags: [LLL]
---

# wNAF

## 문제 설명

> Dreamhack CTF Season 8 Round #4 (Crypto)에 wNAF 문제입니다. Crypto입니다.

## 풀이

### 분석

```py
from random import random
import secrets
from cryptography.hazmat.primitives.asymmetric import ec

N = 0x1FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFA51868783BF2F966B7FCC0148F709A5D03BB5C9B8899C47AEBB6FB71E91386409
W = 13
SIGS = 20
CURVE = ec.SECP521R1()


def point(k):
    q = ec.derive_private_key(k, CURVE).public_key().public_numbers()
    return q.x, q.y

def wnaf(k):
    out = []
    pos = 0
    while k:
        if k & 1:
            digit = k % (1 << W)
            if digit >= 1 << (W - 1):
                digit -= 1 << W
            k -= digit
            out.append((pos, digit))
        k >>= 1
        pos += 1
    return out


d = secrets.randbelow(N - 1) + 1
q = point(d)

sigs = []
for _ in range(SIGS):
    z = secrets.randbelow(N - 1) + 1
    while True:
        k = secrets.randbelow(N - 1) + 1
        r = point(k)[0] % N
        s = ((z + r * d) * pow(k, -1, N)) % N
        if r and s:
            break

    trace = []
    for pos, digit in wnaf(k):
        entry = [pos]
        if random() < 0.3:
            entry.append(point(digit % N)[0])
        trace.append(entry)
    sigs.append([z, r, s, trace])

print(f"Q: {list(q)}")
for i, sig in enumerate(sigs):
    print(f"sig{i}: {sig}")

if d == int(input("d: ")):
    print(open("flag").read())
```

서버는 P-521 ECDSA 서명 20개와 공개키 Q를 출력하고, 개인키 d를 맞히면 플래그를 줍니다.
핵심 취약점은 nonce k의 wNAF 표현에서 각 non-zero 자리 pos를 전부 누출하고, 약 30% 확률로 해당 자리 digit의 점 x좌표까지 추가로 누출한다는 점입니다.

### 취약점 분석

서명식:
* `r = x(kG) mod N`
* `s = (z + r*d) * k^{-1} mod N`
nonce k는 wNAF(W=13)로 분해되어 trace로 출력됩니다.

* 항상 누출: non-zero digit 위치 pos
* 부분 누출: point(digit % N)[0] (x 좌표)

wNAF digit는 홀수이며 범위가 [-(2^(W-1)-1), ..., +(2^(W-1)-1)] 입니다.
P-521에서 x(P) = x(-P) 이므로 x좌표만 알면 부호는 모르지만 절댓값은 구분 가능합니다.
따라서 많은 digit에 대해 "위치 + 절댓값(부호 미상)" 정보가 생깁니다.

### 시나리오

#### 1) x좌표 -> |digit| 테이블 생성
`recover_abs_digit_table()`:
* 홀수 a in [1, 2^(W-1)-1]에 대해 point(a).x를 미리 계산
* x -> a 매핑 캐시(p521_wnaf_w13_xabs.pkl) 생성
이로써 trace의 x좌표를 |digit|로 역변환 가능

#### 2) 미지수 모델링
각 서명에 대해:
* `alpha_i = s_i * r_i^{-1} mod N`
* `beta_i = -z_i * r_i^{-1} mod N`
* `d = alpha_i * k_i + beta_i mod N`

`k_i = sum(digit_{i,j} * 2^{pos_{i,j}})`
digit를 u로 치환:
* 절댓값 누출된 경우: `digit = abs * (2u+1), u in {-1,0} (부호 선택)`
* 절댓값 미누출된 경우: `digit = 2u+1, u in [-2^(W-2), 2^(W-2)-1]`
즉 모든 digit를 작은 범위 정수 u로 표현 가능.

#### 3) 다중 서명 결합 + 격자 구성
여러 서명의 d가 동일해야 하므로, 기준 서명(base)과의 차분으로
선형 합동식들을 만듭니다:

`A * u ≡ b (mod N)`

solve_subset()은 이를 CVP 형태 격자로 임베딩하고, LLL + Babai(babai_closest_vector)로 근사해를 구합니다.

* 변수별 bound(누출/미누출)에 따라 가중치 부여
* K_VALUES, C로 스케일 조정
* 후보 subset을 엔트로피 기준으로 정렬해 빠르게 시도


### 익스플로잇

```py
# sage -python ex_fast.py
from pwn import *
import ast
import os
import pickle
import re
from itertools import combinations

from cryptography.hazmat.primitives.asymmetric import ec
from sage.all import Matrix, ZZ, QQ, vector

HOST = "host3.dreamhack.games"
PORT = 21870

N = 0x1FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFA51868783BF2F966B7FCC0148F709A5D03BB5C9B8899C47AEBB6FB71E91386409
W = 13
BND = (1 << (W - 1)) - 1
UNK_B = 1 << (W - 2)
CURVE = ec.SECP521R1()

C = 1 << 15
K_VALUES = [1 << 18, 1 << 20, 1 << 22]
MAX_TRIES_PER_SIZE = 30

context.log_level = "info"


def parse_output(io):
    text = io.recvuntil(b"d: ", timeout=20).decode(errors="ignore")
    Q = None
    sigs = {}

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        m = re.match(r"^Q\s*[:=]\s*(.+)$", line)
        if m:
            Q = ast.literal_eval(m.group(1))
            continue

        m = re.match(r"^sig(\d+)\s*[:=]\s*(.+)$", line)
        if m:
            idx = int(m.group(1))
            sigs[idx] = ast.literal_eval(m.group(2))
            continue

    sig_list = [sigs[i] for i in sorted(sigs)]

    if Q is None or not sig_list:
        raise RuntimeError("failed to parse Q/signatures from server output")

    return Q, sig_list


def point(k):
    q = ec.derive_private_key(int(k), CURVE).public_key().public_numbers()
    return q.x, q.y


def center(x):
    x %= N
    if x > N // 2:
        x -= N
    return int(x)


def nearest_int(x):
    return ZZ((x + QQ(1) / 2).floor())

def babai_closest_vector(B, target):
    B = B.LLL(delta=0.99)
    G = B.change_ring(QQ).gram_schmidt()[0]

    y = vector(QQ, target)
    v = vector(ZZ, [0] * B.ncols())

    for i in reversed(range(B.nrows())):
        denom = G[i].dot_product(G[i])
        if denom == 0:
            continue

        c = nearest_int(y.dot_product(G[i]) / denom)
        if c:
            y -= c * B[i]
            v += c * B[i]

    return v


def recover_abs_digit_table():
    cache = f"p521_wnaf_w{W}_xabs.pkl"

    if os.path.exists(cache):
        with open(cache, "rb") as f:
            return pickle.load(f)

    log.info("building x-coordinate -> abs(digit) table")

    table = {}
    for a in range(1, BND + 1, 2):
        table[point(a)[0]] = a

    with open(cache, "wb") as f:
        pickle.dump(table, f)

    return table


def parse_trace(trace, x_to_abs):
    out = []

    for e in trace:
        pos = e[0]

        if len(e) == 2:
            abs_digit = x_to_abs[e[1]]
            out.append((pos, abs_digit))
        else:
            out.append((pos, None))

    return out


def entropy_score(parsed_trace):
    score = 0

    for _, abs_digit in parsed_trace:
        score += 1 if abs_digit is not None else 12

    return score


def solve_subset(indices, Q, sigs, parsed, K):
    base = indices[0]

    alpha = []
    beta = []

    for z, r, s, _ in sigs:
        rinv = pow(r, -1, N)
        alpha.append((s * rinv) % N)
        beta.append((-z * rinv) % N)

    const = {sig_idx: beta[sig_idx] for sig_idx in indices}
    vars_meta = []

    for sig_idx in indices:
        for pos, abs_digit in parsed[sig_idx]:
            two_pos = pow(2, pos, N)

            if abs_digit is None:
                const[sig_idx] = (const[sig_idx] + alpha[sig_idx] * two_pos) % N
                coeff = alpha[sig_idx] * 2 * two_pos
                bound = UNK_B
                meta = (sig_idx, pos, "unknown", None)
            else:
                const[sig_idx] = (const[sig_idx] + alpha[sig_idx] * abs_digit * two_pos) % N
                coeff = alpha[sig_idx] * 2 * abs_digit * two_pos
                bound = 1
                meta = (sig_idx, pos, "leaked", abs_digit)

            vars_meta.append((sig_idx, center(coeff), bound, meta))

    rows = len(indices) - 1
    cols = len(vars_meta)
    dim = cols + rows

    A = [[0] * cols for _ in range(rows)]
    b = []

    for row_idx, sig_idx in enumerate(indices[1:]):
        b.append(center(const[base] - const[sig_idx]))

        for col_idx, (owner, coeff, _, _) in enumerate(vars_meta):
            if owner == sig_idx:
                A[row_idx][col_idx] = center(coeff)
            elif owner == base:
                A[row_idx][col_idx] = center(-coeff)

    weights = [max(1, C // bound) for _, _, bound, _ in vars_meta]

    B = Matrix(ZZ, dim, dim)

    for i in range(cols):
        B[i, i] = weights[i]

        for j in range(rows):
            B[i, cols + j] = K * A[j][i]

    for j in range(rows):
        B[cols + j, cols + j] = K * N

    target = vector(ZZ, [-(w // 2) for w in weights] + [K * bb for bb in b])
    closest = babai_closest_vector(B, target)

    us = []

    for i, w in enumerate(weights):
        if closest[i] % w != 0:
            return None

        us.append(int(closest[i] // w))

    digits_by_sig = {idx: [] for idx in indices}

    for u, (_, _, _, meta) in zip(us, vars_meta):
        sig_idx, pos, kind, abs_digit = meta

        if kind == "unknown":
            if not (-UNK_B <= u < UNK_B):
                return None

            digit = 2 * u + 1

            if abs(digit) > BND:
                return None
        else:
            if u not in (-1, 0):
                return None

            digit = abs_digit * (2 * u + 1)

        digits_by_sig[sig_idx].append((pos, digit))

    ds = []

    for sig_idx in indices:
        k = sum(digit * (1 << pos) for pos, digit in digits_by_sig[sig_idx])

        if not (1 <= k < N):
            return None

        z, r, s, _ = sigs[sig_idx]
        d = ((s * k - z) * pow(r, -1, N)) % N
        ds.append(d)

    if len(set(ds)) != 1:
        return None

    d = ds[0]

    if list(point(d)) != list(Q):
        return None

    return d


def solve(Q, sigs):
    x_to_abs = recover_abs_digit_table()
    parsed = [parse_trace(sig[3], x_to_abs) for sig in sigs]

    bitlen = N.bit_length()
    order = sorted(range(len(sigs)), key=lambda i: entropy_score(parsed[i]))

    for subset_size in range(3, min(6, len(order)) + 1):
        candidates = []

        for indices in combinations(order[:10], subset_size):
            ent = sum(entropy_score(parsed[i]) for i in indices)
            vars_count = sum(len(parsed[i]) for i in indices)
            constraints = (subset_size - 1) * bitlen

            if ent > constraints + 120:
                continue

            candidates.append((ent, vars_count, indices))

        candidates.sort()

        log.info(f"subset_size={subset_size}, candidates={len(candidates)}")

        for ent, vars_count, indices in candidates[:MAX_TRIES_PER_SIZE]:
            for K in K_VALUES:
                log.info(f"trying indices={indices}, entropy≈{ent}, vars={vars_count}, K={K}")

                d = solve_subset(indices, Q, sigs, parsed, K)

                if d is not None:
                    return d

    return None


def main():
    io = remote(HOST, PORT)

    Q, sigs = parse_output(io)

    log.info(f"parsed {len(sigs)} signatures")

    d = solve(Q, sigs)

    if d is None:
        log.failure("failed; try increasing MAX_TRIES_PER_SIZE or K_VALUES")
        io.close()
        return

    log.success(f"d = {d}")

    io.sendline(str(d).encode())

    print(io.recvall(timeout=5).decode(errors="ignore"))


if __name__ == "__main__":
    main()
```


## 플래그

```
DH{yet_another_ECDSA_nonce_leakage_challenge:FCqnictJTCxI3z6QuKqMmw==}
```

## 배운 점

LLL로 해결 가능한 게임은 상당히 많이 등장한다.
