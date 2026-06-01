---
ctf_name: "Dreamhack CTF Season 8 Round #5 (All-Round)"
challenge_name: "Albireo"
category: "crypto"
difficulty: "medium"
author: "vestman828"
date: "2026-06-01"
tags: [elliptic_curve, gcd, linear_algebra]
---

# Albireo

## 문제 설명

> Dreamhack CTF Season 8 Round #5 (All-Round)에 Albireo 문제입니다. Crypto입니다.

## 풀이

### 분석

```py
from generator import gen_params

p, a, b, G = gen_params()
E = EllipticCurve(GF(p), [a, b])
G = E(G)

print("Average P-G and P+G, get P. What could go wrong?")
for i in range(7):
    P = E.random_point()
    print(f"({(P+G)[0]} + {(P-G)[0]}) // 2 == {P[0]}")

P = E.lift_x(ZZ(input("\nP_x: ")))
if ((P+G)[0] + (P-G)[0]) // 2 == P[0]:
    print(open("./flag").read())
else:
    print("Wait, what?")
```

서버는 곡선 파라미터 `p, a, b`와 기준점 `G`를 직접 주지 않습니다.
대신 임의의 점 `P`에 대해 `x(P+G)`, `x(P-G)`, `x(P)`를 7번 출력합니다.

짧은 Weierstrass 곡선 `y^2 = x^3 + ax + b`의 3차 summation polynomial은 다음과 같습니다.

```txt
S3(x1, x2, x3)
= (x1-x2)^2*x3^2
  - 2*((x1+x2)*(x1*x2+a)+2*b)*x3
  + (x1*x2-a)^2 - 4*b*(x1+x2)
```

`x = x(P)`, `g = x(G)`, `u = x(P+G)`, `v = x(P-G)`라고 하면
`S3(x, g, u) = 0`, `S3(x, g, v) = 0 (mod p)`입니다.
두 식을 빼고 `u-v`로 나누면 다음 식을 얻습니다.

```txt
(u+v)(x-g)^2 - 2((x+g)(xg+a)+2b) = 0 (mod p)
```

이를 전개하면 미지수 벡터 `(g^2, g, a, ag, b, 1)`에 대한 선형식이 됩니다.

```txt
(u+v-2x)g^2 + (-2(u+v)x-2x^2)g - 2xa - 2ag - 4b + (u+v)x^2 = 0
```

7개의 출력으로 행렬을 만들면 실제 벡터가 `mod p`에서 영공간에 있으므로,
임의의 6개 행으로 만든 행렬식들은 모두 `p`의 배수가 됩니다.
따라서 이 행렬식들의 `gcd`를 구하면 `p`를 복원할 수 있습니다.

`p`를 구한 뒤에는 `GF(p)`에서 영공간을 구해 `g, a, b`를 복원합니다.
마지막 검증식은 다음 조건과 같습니다.

```txt
x(P+G) + x(P-G) = 2x(P)
```

덧셈 공식을 대입하면 `P_x`는 아래 3차식의 근이면 됩니다.

```txt
X^3 - 3gX^2 - aX - ag - 2b = 0 (mod p)
```

이 근 중 실제 곡선 위 점으로 lift되는 값을 서버에 입력하면 플래그가 출력됩니다.

### 익스플로잇

```py
import re
from itertools import combinations
from math import gcd
from sage.all import *

out = """
Average P-G and P+G, get P. What could go wrong?
(...) // 2 == ...
"""

samples = []
for u, v, x in re.findall(r"\((\d+) \+ (\d+)\) // 2 == (\d+)", out):
    samples.append((ZZ(u), ZZ(v), ZZ(x)))

rows = []
for u, v, x in samples:
    s = u + v
    rows.append([
        s - 2*x,             # g^2
        -2*s*x - 2*x**2,     # g
        -2*x,                # a
        -2,                  # ag
        -4,                  # b
        s*x**2,              # 1
    ])

g_det = 0
for idxs in combinations(range(len(rows)), 6):
    d = Matrix(ZZ, [rows[i] for i in idxs]).det()
    g_det = gcd(g_det, abs(d))

p = max(factor(g_det), key=lambda t: t[0].nbits())[0]
F = GF(p)

M = Matrix(F, rows)
for vec in M.right_kernel().basis():
    if vec[-1] != 0:
        vec = vec / vec[-1]
        break

g2, g, a, ag, b, _ = vec
assert g**2 == g2
assert a*g == ag

R = PolynomialRing(F, "X")
X = R.gen()
poly = X**3 - 3*g*X**2 - a*X - a*g - 2*b
E = EllipticCurve(F, [a, b])

for root, _ in poly.roots():
    try:
        E.lift_x(root)
        print(ZZ(root))
        break
    except (ValueError, ArithmeticError):
        pass
```

## 플래그

```
DH{GCD_stands_for_Getting_Curve_Details:j4U9/atyyu4pyLsQW13sVQ==}
```

## 배운 점

타원곡선에서 점 자체를 숨겨도 `x(P+G)`, `x(P-G)`, `x(P)` 같은 x좌표 관계를 여러 번 주면 summation polynomial과 선형대수만으로 곡선 정보를 복원할 수 있습니다.
