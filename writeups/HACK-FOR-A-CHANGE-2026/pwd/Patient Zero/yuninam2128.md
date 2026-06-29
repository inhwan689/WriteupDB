---
ctf_name: "HACK FOR A CHANGE 2026"
challenge_name: "Patient Zero"
category: "pwd"
difficulty: "medium"
author: "yuninam2128"
date: "2026-05-27"
points: 200
tags: [crypto, rsa, coppersmith, small-exponent, lll]
---

# Patient Zero

## 문제 설명

A rural clinic's patient records were encrypted before transmission to the regional health authority. The encryption was implemented by a volunteer developer who prioritized speed over security. We have the public key and one encrypted record. Recover the contents before the outbreak response window closes.

- 제공 파일: `encrypt.py`, `public.txt`

## 풀이

### 1. 코드 분석

먼저 `encrypt.py`를 보면 RSA 공개키와 암호화 방식이 그대로 들어 있다.

```python
n = 108060031931266353758801330782473639320039225201311917178449705019176660696244872351271382486864507377607807538618062847665115562029186118435965272613853246476229261400861607263122402792644231190189479726984543802757846539830277258662001776505200445021146928156972061161319057790512542181820218329738735817807
e = 3

prefix = b"SDGCTF_SECURE_MSG_V1::"
suffix = b"::END"
padded = prefix + flag + suffix
m = bytes_to_long(padded)
c = pow(m, e, n)
```

핵심 포인트는 다음 두 가지다.

1. `e = 3`인 작은 공개지수를 사용했다.
2. 평문 전체가 랜덤 패딩 없이 `known_prefix + secret + known_suffix` 형태다.

즉, 우리가 모르는 부분은 가운데 `flag`뿐이고 나머지는 전부 안다.

또 `public.txt`에는 아래 정보가 주어진다.

```text
n = ...
e = 3
c = ...
flag_length = 37
```

따라서 전체 평문은 아래와 같은 꼴이다.

```text
m = b"SDGCTF_SECURE_MSG_V1::" + flag + b"::END"
```

여기서 `flag_length = 37`이므로 미지수는 정확히 37바이트다.

### 2. 왜 취약한가

이 문제는 textbook RSA에 가까운 구조라서 안전하지 않다.

`m = base + x * 256^len(suffix)` 로 두면, 모르는 값 `x`는 37바이트짜리 정수이고 다음 식을 만족한다.

```text
(base + x * 256^5)^3 ≡ c (mod n)
```

여기서 `e = 3`이고, `x < 256^37`이므로 미지수의 크기는 대략 `2^296` 정도다.  
반면 `n`은 1024비트이므로 `n^(1/3)` 크기보다 `x`가 충분히 작다.  
이 조건은 Coppersmith의 univariate small root 공격 조건에 정확히 들어맞는다.

즉, 이 문제의 정석 해법은 다음이다.

1. 알려진 prefix/suffix를 이용해 단변수 다항식 `f(x)`를 만든다.
2. Coppersmith + LLL로 작은 정수 해 `x`를 찾는다.
3. `x`를 바이트열로 복원하면 flag가 나온다.

### 3. 식 정리

suffix 길이는 5바이트이므로 `shift = 256^5` 로 두고,

```text
base = bytes_to_long(prefix) * 256^(37+5) + bytes_to_long(suffix)
m = base + x * shift
```

그러면 RSA 식은 다음과 같다.

```text
(base + x*shift)^3 ≡ c (mod n)
```

`shift`는 `n`과 서로소이므로 양변에 `shift^(-3)`를 곱해 monic polynomial 형태로 바꿀 수 있다.

```text
f(x) = (x + base * shift^(-1))^3 - c * shift^(-3)  (mod n)
```

이제 `x < X = 256^37` 인 작은 해를 찾으면 된다.

### 4. 시행착오

처음에는 `sympy`의 `Matrix.lll()`로 바로 풀려고 했는데, 큰 계수에서 `OverflowError`가 계속 났다.

```text
integer division result too large for a float
```

그래서 중간에 다음 방법들을 시도했다.

1. `sympy` 기본 LLL 사용
2. pure Python으로 직접 LLL 구현
3. `olll` 패키지 사용
4. 37바이트 전체를 미지수로 두는 방식과, `SDG{...}` 내부 32바이트만 미지수로 두는 방식 둘 다 시도

이 과정에서 얻은 교훈은 두 가지였다.

1. 이론은 맞아도 LLL 구현이 부실하면 다항식이 제대로 안 나온다.
2. 계수를 `mod n`의 대표값 그대로 두는 것보다 `[-n/2, n/2]` 구간으로 중심화하는 편이 더 안정적이다.

결정적으로 `python-flint`를 설치해서 FLINT의 정수 행렬 LLL을 사용하자 바로 풀렸다.

### 5. 최종 익스플로잇

최종적으로 사용한 핵심 코드는 아래와 같다.

```python
from flint import fmpz_mat
from sympy import symbols, Poly, gcd
from itertools import combinations

n = 108060031931266353758801330782473639320039225201311917178449705019176660696244872351271382486864507377607807538618062847665115562029186118435965272613853246476229261400861607263122402792644231190189479726984543802757846539830277258662001776505200445021146928156972061161319057790512542181820218329738735817807
c = 101152276854699288579635065162580765335408709468039751066531788331872303065558676852319962668516098486786410496046310747688468318560576827726316036446042463953732005451440091228071654720345329261729169723573094495518764419262996988094624225182888028536813778566220841955011906206159282463095638064168000715988

prefix = b"SDGCTF_SECURE_MSG_V1::SDG{"
suffix = b"}::END"
unknown_len = 32

b2l = lambda b: int.from_bytes(b, "big")
l2b = lambda n, l=None: n.to_bytes(l or ((n.bit_length()+7)//8), "big")

x = symbols('x')
m0 = b2l(prefix + b"\x00" * unknown_len + suffix)
shift = 256 ** len(suffix)
inv_shift = pow(shift, -1, n)
inv_shift3 = pow(pow(shift, 3, n), -1, n)

fmod = Poly((x + m0 * inv_shift)**3 - (c * inv_shift3 % n), x, modulus=n)

coeffs = []
for i in range(fmod.degree() + 1):
    a = int(fmod.nth(i))
    if a > n // 2:
        a -= n
    coeffs.append(a)

f = Poly(sum(coeffs[i] * x**i for i in range(len(coeffs))), x, domain='ZZ')
X = 2 ** (8 * unknown_len)

m = 3
polys = []
for i in range(m):
    for j in range(f.degree()):
        polys.append(Poly((n ** (m - i)) * (x ** j) * (f.as_expr() ** i), x, domain='ZZ'))

D = max(p.degree() for p in polys)
rows = [[int(p.nth(k)) * (X**k) for k in range(D + 1)] for p in polys]

M = fmpz_mat(len(rows), D + 1, [a for row in rows for a in row])
R = M.lll()

H = []
for row in R.tolist():
    coeffz = [int(row[k] // (X**k)) for k in range(D + 1)]
    h = Poly(sum(coeffz[k] * x**k for k in range(D + 1)), x, domain='ZZ').primitive()[1]
    H.append(h)
    for factor, _ in h.factor_list()[1]:
        if factor.degree() == 1:
            a, b = factor.all_coeffs()
            if (-b) % a == 0:
                r = int(-b // a)
                if 0 <= r < X and fmod.eval(r) % n == 0:
                    print(b"SDG{" + l2b(r, unknown_len) + b"}")
                    raise SystemExit

for i, j in combinations(range(len(H)), 2):
    g = gcd(H[i], H[j]).primitive()[1]
    if g.degree() == 1:
        a, b = g.all_coeffs()
        if (-b) % a == 0:
            r = int(-b // a)
            if 0 <= r < X and fmod.eval(r) % n == 0:
                print(b"SDG{" + l2b(r, unknown_len) + b"}")
                raise SystemExit
```

실행 결과는 다음과 같다.

```text
FOUND b'SDG{373a6ef451648ef0bcfd6d4ea4bbf84d}'
```

### 6. 왜 32바이트로 바꿔서 풀었는가

원래 `flag_length = 37` 이지만, 일반적인 CTF 플래그 형식인 `SDG{...}`를 이용하면 내부 내용은 32바이트라고 추정할 수 있다.

```text
37 = len("SDG{") + 32 + len("}")
```

그래서 실제 미지수는 아래처럼 32바이트만 두고 풀 수 있었다.

```text
SDG{????????????????????????????????}
```

이렇게 하면 `X = 2^256` 이 되어 `n^(1/3)`보다 더 여유 있게 작아지고, LLL도 훨씬 안정적으로 동작한다.

실제로 37바이트 전체를 직접 미지수로 두는 접근도 가능하지만, 내 환경에서는 LLL 구현 문제 때문에 훨씬 까다로웠다.

## 플래그

```text
SDG{373a6ef451648ef0bcfd6d4ea4bbf84d}
```

## 배운 점

이 문제는 "RSA를 썼다"는 사실만으로 안전하지 않다는 걸 보여준다.  
RSA에서 중요한 것은 단순히 큰 `n`을 쓰는 것이 아니라, 안전한 패딩과 적절한 파라미터를 같이 써야 한다는 점이다.

특히 아래 조합은 매우 위험하다.

1. 작은 공개지수 `e = 3`
2. 랜덤 패딩 없음
3. 알려진 형식의 평문
4. 모르는 부분이 충분히 작음

이 조건이 만나면 Coppersmith 공격으로 평문 일부 또는 전체를 복구할 수 있다.  
실전에서는 반드시 OAEP 같은 안전한 padding을 사용해야 한다.
