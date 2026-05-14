---
ctf_name: "RITSEC CTF 2026"
challenge_name: "not quite optimal"
category: "rev"           # web / pwn / rev / crypto / misc
difficulty: "medium"      # easy / medium / hard / insane
author: "ansihoo"
date: "2026-04-04"
points: 115
tags: [power tower, modular arithmetic]
---

# 문제명

## 문제 설명

> whoopsies, maybe i should have used -O3
> Author: sy1vi3

- 첨부 파일로 `not_quite_optimal`이라는 바이너리 하나가 주어진다.

## 풀이

### 분석

`file`로 확인하여 보니, stripped된 x86-64 ELF 실행파일이었다. 실행하면 아래처럼 대화형 프롬프트가 뜬다<    haiiii what r u doin here?    >

일단 `strings`를 돌려봤는데 그럴듯한 플래그가 하나 나왔다.
<   meowmeow here u go... RITSEC{ANTHROPIC_MAGIC_STRING_TRIGGER_REFUSAL_1FAEFB6177...}    >
flag처럼 보이는 문구가 있기에  제출했더니 오답이었다. 제목이 "not quite optimal"인 이유가 여기 있었다. `strings`로 읽는 게 "최적"이 아니라는 힌트이면서, 동시에 `-O3` 없이 컴파일했다는 말이기도 했다.
다시 PLT 심볼을 보니 `__gmpz_mul`, `__gmpz_fdiv_ui`, `__gmpz_fdiv_q_2exp` 같은 GMP 함수들이 잔뜩 있었다. 큰 수 연산을 하고 있다는 뜻이다. 거기에 `nanosleep`까지 쓰고 있어서, 직접 실행하면 상당히 오래 걸릴 것 같았다.

실제로 올바른 입력 세 개를 넣어서 실행을 시도해봤더니 메모리가 터져서, 정적 분석으로 가야 한다고 판단했다.


### 취약점

디스어셈블리를 분석하면 입력을 세 번 받는 구조다. 첫 번째로 `"looking for the flag"`를 입력하면 "say the magic word"라고 반응하고, 두 번째로 `"please"`를 입력하면 "waow i thought ud never ask..."라고 한 뒤, 세 번째로 `"PLEASE MAY I HAVE THE FLAG"`를 입력해야 비로소 플래그 출력 루틴으로 진입한다.
플래그 출력 루틴은 `.rodata` 섹션 `0x22a0`에 있는 테이블을 순회하면서 글자 84개를 하나씩 출력한다. 테이블의 각 항목은 `(n, k)` 형태의 16바이트 쌍이고, 바이너리는 이걸로 Power Tower를 계산한다.
```
f(n, 1) = n
f(n, 2) = n^n
f(n, 3) = n^(n^n)
f(n, k) = n^f(n, k-1)
```
최종 문자 코드는 `(f(n, k) mod 256 + 1) / 2`다. k 값이 최대 천만이 넘는 항목도 있고, n^n 자체가 수십만 자리가 되니 GMP로 실제로 계산하려 들면 메모리가 터지는 게 당연하다. `nanosleep`은 글자 인덱스에 비례해서 딜레이를 주기 때문에, 설령 계산이 된다 해도 전부 출력받으려면 수십 분이 걸린다.


### 익스플로잇

핵심은 `f(n, k) mod 256`을 실제로 거대한 수를 계산하지 않고 구하는 것이다. Euler's Theorem을 재귀적으로 적용하면 된다.
`n^e mod 2^j`를 구할 때 n이 홀수이면 `e mod φ(2^j) = e mod 2^(j-1)`만 알면 충분하다. 이걸 j를 줄여가며 재귀하다 보면 결국 `mod 2` 레벨에서 홀수^임의수 ≡ 1로 수렴하면서 종료된다. k가 아무리 크더라도 재귀 깊이는 8단계면 끝난다.

```python
import struct

with open('not_quite_optimal', 'rb') as f:
    data = f.read()

TABLE_OFFSET = 0x22a0
NUM_CHARS = 0x54

def tower_mod_pow2(n, k, j):
    if j == 0:
        return 0
    m = 1 << j
    if k == 0:
        return 1
    if k == 1:
        return n % m
    n_m = n % m
    if n_m == 1:
        return 1
    if j == 1:
        return 1  # 홀수^임의수 ≡ 1 (mod 2)
    if k > j:
        k = j
    exp = tower_mod_pow2(n, k - 1, j - 1)
    return pow(n_m, exp, m)

flag = []
for i in range(NUM_CHARS):
    n, k = struct.unpack_from('<QQ', data, TABLE_OFFSET + i * 16)
    result = tower_mod_pow2(n, k, 8)
    flag.append((result + 1) >> 1)

print(''.join(chr(c) for c in flag))

```

## 플래그

```
RS{4_littl3_bi7_0f_numb3r_th30ry_n3v3r_hur7_4ny0n3_19b3369a25c78095689a38f81aa3f5e3}
```

## 배운 점

페이크 플래그를 `strings`로 읽히는 위치에 심어두는 트릭은 처음 봤는데 꽤 당황했다. 앞으로는 플래그 제출 전에 실제 로직을 확인하는 습관을 들여야겠다. Power Tower의 modular 계산은 Euler's Theorem을 j를 줄여가며 재귀 적용하면 되는데, 결국 홀수라는 조건 하나가 `mod 2` 레벨에서 수렴을 보장해준다는 게 깔끔했다. 인위적인 `nanosleep` 딜레이나 메모리 폭발은 직접 실행을 막기 위한 장치였고, 제목과 설명이 전부 "정석대로 실행하지 말라"는 힌트였다.
