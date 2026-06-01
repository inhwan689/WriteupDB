---
ctf_name: "Dreamhack CTF Season 8 Round #5 (All-Round)"
challenge_name: "Centrism"
category: "crypto"
difficulty: "easy"
author: "vestman828"
date: "2026-06-01"
tags: [rsa, fermat_factorization]
---

# Centrism

## 문제 설명

> Dreamhack CTF Season 8 Round #5 (All-Round)에 Centrism 문제입니다. Crypto입니다.

## 풀이

### 분석

```py
from math import gcd
from random import getrandbits
from sympy import nextprime, prevprime
from Crypto.Util.number import bytes_to_long

e = 65537

while True:
    center = getrandbits(512)
    p = int(prevprime(center - getrandbits(256)))
    q = int(nextprime(center + getrandbits(256)))

    if gcd(e, (p - 1) * (q - 1)) == 1:
        break

n = p * q
m = bytes_to_long(open("./flag").read().encode())
c = pow(m, e, n)

print(f"n = {n}")
print(f"c = {c}")
```

`p`와 `q`는 같은 512비트 `center`를 기준으로 만들어집니다.
각각 `center`에서 256비트 이하의 값만큼 떨어진 위치의 이전/다음 소수이므로 두 소수의 차이는 매우 작습니다.

RSA modulus가

```txt
n = pq = ((p+q)/2)^2 - ((q-p)/2)^2
```

꼴이라는 점을 이용하면, `ceil(sqrt(n))`부터 시작하는 Fermat factorization으로 바로 인수분해할 수 있습니다.

### 익스플로잇

```py
from math import isqrt
from Crypto.Util.number import long_to_bytes

e = 65537
n = ...  # server output
c = ...  # server output

a = isqrt(n)
if a * a < n:
    a += 1

while True:
    b2 = a*a - n
    b = isqrt(b2)
    if b*b == b2:
        break
    a += 1

p = a - b
q = a + b
assert p * q == n

phi = (p - 1) * (q - 1)
d = pow(e, -1, phi)
m = pow(c, d, n)

print(long_to_bytes(m))
```

## 플래그

```
DH{ferm4t_f0und_th3_cen7er_of_m4ss:iqg6gEtFtoOAxxm4VIGcJQ==}
```

## 배운 점

RSA에서 두 소수의 크기가 비슷한 것 자체는 정상적이지만, 두 소수가 너무 가깝게 생성되면 Fermat factorization으로 쉽게 깨집니다.
