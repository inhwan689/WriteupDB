---
ctf_name: "2026 RITSEC CTF"
challenge_name: "Captain Mark's Compass"
category: "crypto"           # web / pwn / rev / crypto / misc
difficulty: "easy"      # easy / medium / hard / insane
author: "yuninam2128"
date: "2026-04-07"
points: 10
tags: [lcg, markov-chain, gcd]
---

# 문제명

## 문제 설명

> Old Captain Mark was the most erratic pirate on the seven seas. They say his compass was cursed! It didn't point North, but spun wildly, giving coordinates based on the Captain's shifting mood (though he generally preferred to stay his course).
>
> We found his final logbook which lists the last 850 coordinates he visited before disappearing. At the very end of the log lies the encrypted location of his buried treasure.
>
> We also recovered a rotting scrap of his navigation script, but the numbers for the winds and tides were washed away by the sea. Chart the Captain's madness and dig up the treasure!

- 문제 URL / 파일 등 참고 정보 : https://ctfd.ritsec.club/challenges#Captain%20Mark's%20Compass-7


## 풀이

### 분석

문제에서 주어진 `navigate.py`를 보면, 내부 상태값 `sval`은 다음 식으로 갱신된다.

```python
self.sval = (a * self.sval + b) % self.P
```

즉, 상태마다 서로 다른 `(a, b)`를 가지는 LCG를 쓰고 있다. 다만 일반적인 LCG와 다른 점은, 매 출력 후 다음에 사용할 `(a, b)`를 마르코프 전이 행렬에 따라 바꾼다는 점이다.

정리하면:

1. 현재 상태의 `(a, b)`로 `sval`을 1번 갱신한다.
2. 그 값을 로그북에 남긴다.
3. 전이 확률에 따라 다음 상태를 정한다.
4. 마지막에는 `lcg.next() & 0xff`를 키스트림으로 써서 플래그와 XOR 한다.

따라서 해야 할 일은 다음 두 가지다.

1. 로그북 850개 숫자만으로 모듈러스 `P`를 복구한다.
2. 자주 등장하는 `(a, b)` 쌍을 찾아 상태들을 복원한 뒤, 마지막 ciphertext를 복호화한다.

### 취약점

같은 상태가 연속으로 유지된 구간에서는 완전히 평범한 LCG처럼 동작한다.  
관측값을 `x_i`라고 하면 같은 상태에서:

```text
x_{i+1} = a x_i + b mod P
x_{i+2} = a x_{i+1} + b mod P
```

차분 `d_i = x_{i+1} - x_i`를 두면:

```text
d_{i+1} = a d_i mod P
```

따라서 같은 상태가 3번 연속 유지된 곳에서는 아래 식이 항상 성립한다.

```text
d_{i+2} * d_i - d_{i+1}^2 ≡ 0 mod P
```

즉, 로그에서 이런 값들을 많이 만든 뒤 GCD를 구하면 `P`의 배수가 튀어나오고, 충분히 많은 구간을 모으면 실제 `P`를 복원할 수 있다.

또한 `P`를 안 뒤에는 연속된 세 관측값 `(x_i, x_{i+1}, x_{i+2})`에서

```text
a = (x_{i+2} - x_{i+1}) * (x_{i+1} - x_i)^(-1) mod P
b = x_{i+1} - a x_i mod P
```

로 `(a, b)` 후보를 계산할 수 있다.  
진짜 상태에서 나온 `(a, b)`는 여러 번 반복되지만, 상태가 바뀐 경계에서 계산한 가짜 값들은 거의 한 번만 나온다. 그래서 빈도수를 세면 실제 상태 수와 각 상태의 파라미터를 자연스럽게 복원할 수 있다.

### 익스플로잇

먼저 로그북에서 차분 기반 식의 gcd를 모아 `P`를 복구했다.

```python
import re
import ast
from math import gcd
from functools import reduce

text = open("logbook.txt").read()
obs = ast.literal_eval(re.search(r'Log: (\[.*\])\nCiphertext', text, re.S).group(1))

diffs = [obs[i + 1] - obs[i] for i in range(len(obs) - 1)]
T = [diffs[i + 2] * diffs[i] - diffs[i + 1] * diffs[i + 1] for i in range(len(diffs) - 2)]

vals = []
for i in range(len(T) - 2):
    a, b, c = T[i:i + 3]
    if a and b and c:
        g = gcd(gcd(abs(a), abs(b)), abs(c))
        if g > 1:
            vals.append(g)

P = reduce(gcd, [v for v in vals if v.bit_length() > 100])
print(P)
```

복구된 `P`는 다음과 같았다.

```text
114998001088122878165469494209865851580646945385760011250661037287215114047884823814201471683151719773292295650809857617855325511069020132311210674811529707856845753203740687736866355160800098819362158152761107736460621045328980768188047601931528470157
```

이제 모든 연속된 세 값에 대해 `(a, b)` 후보를 계산하고 빈도를 세면 상위 5개가 압도적으로 많이 나온다. 이 5개가 실제 상태였다.

```python
from collections import Counter

ctr = Counter()
for i in range(len(obs) - 2):
    x0, x1, x2 = [x % P for x in obs[i:i + 3]]
    d0 = (x1 - x0) % P
    d1 = (x2 - x1) % P
    if d0 == 0:
        continue
    a = d1 * pow(d0, -1, P) % P
    b = (x1 - a * x0) % P
    if (a * x1 + b) % P == x2:
        ctr[(a, b)] += 1

for (a, b), cnt in ctr.most_common(5):
    print(cnt, a, b)
```

이렇게 얻은 5개 상태를 이용해 각 로그값 사이의 전이를 전부 라벨링할 수 있었고, 마지막 관측값 이후의 상태열만 남게 된다.

마지막 복호화는 `obs[849]`를 시작 상태값으로 두고, 가능한 다음 상태를 따라가며 키스트림 바이트 `next() & 0xff`를 만들어 ciphertext와 XOR 하면 된다.  
플래그 포맷이 `RS{...}`인 점을 이용해 빔서치로 후보를 줄이면 정답이 하나로 수렴한다.

```python
import math

ct = bytes.fromhex(re.search(r'Ciphertext: ([0-9a-f]+)', text).group(1))

heads = [
    # 복구한 5개 (a, b)
]

trans = [
    [140, 13, 18, 12, 16],
    [8, 118, 13, 12, 13],
    [21, 6, 114, 12, 12],
    [10, 20, 12, 112, 19],
    [20, 6, 8, 25, 88],
]

probs = [[c / sum(row) for c in row] for row in trans]
charset = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_{}")

beam = [(0.0, 4, obs[-1] % P, "")]
prefix = "RS{"

for depth in range(len(ct)):
    new_beam = []
    for score, st, sval, plain in beam:
        for ns, (a, b) in enumerate(heads):
            nxt = (a * sval + b) % P
            ch = chr((nxt & 0xff) ^ ct[depth])
            if ch not in charset:
                continue
            cand = plain + ch
            if depth < len(prefix) and cand != prefix[:depth + 1]:
                continue
            if cand[:3] != "RS{":
                continue
            if "}" in cand[:-1]:
                continue
            new_beam.append((score - math.log(probs[st][ns]), ns, nxt, cand))
    beam = sorted(new_beam, key=lambda x: x[0])[:5000]

for item in beam:
    if item[3].endswith("}"):
        print(item[3])
        break
```

최종적으로 다음 플래그를 얻을 수 있었다.

## 플래그

```text
RS{w04h_h1dd3n_M4rk0v_br34k5_LCGs}
```

## 배운 점

상태 전이가 섞여 있어도, 같은 상태가 충분히 오래 유지되는 구간이 있으면 LCG의 구조가 그대로 드러난다는 점이 핵심이었다.  
특히 `(d_{i+2} d_i - d_{i+1}^2)` 형태로 모듈러를 복구하는 고전적인 기법이, 마르코프 체인과 결합된 변형 LCG에도 그대로 통한다는 점이 인상적이었다.
