---
ctf_name: "RITSEC-CTF"
challenge_name: "not-quite-optimal"
category: "rev"           # web / pwn / rev / crypto / misc
difficulty: "easy"      # easy / medium / hard / insane
author: "kjs24"
date: "2026-04-05"
points: 10
tags: []
---

# 문제명
not-quite-optimal
## 문제 설명

whoopsies, maybe i should have used -O3

- 문제 URL / 파일 등 접속 정보
그냥 not_quite_optimal 바이너리 하나
## 풀이

### 분석

처음에는 IDA에서 `main`부터 전체 흐름을 따라가면서 어떤 조건에서 출력 루틴으로 들어가는지 확인했다.  
문제 특성상 눈에 보이는 문자열이나 출력 문구에 낚일 가능성이 높아 보여서, 문자열 자체를 믿기보다는 실제로 어떤 함수가 최종 출력을 담당하는지를 기준으로 분석했다.

IDA에서 함수들을 따라가다 보면 특정 입력을 비교하는 흐름이 나오고, 그 분기를 통과했을 때만 별도의 계산 함수가 호출되는 구조를 확인할 수 있다.  
이 과정에서 `"please"`나 `"PLEASE MAY I HAVE THE FLAG"` 같은 비교 문자열이 보이긴 하지만, 이 부분은 어디까지나 진입 조건일 뿐이고, 핵심은 그 뒤에 호출되는 계산 루틴이다.

계산 함수 쪽을 보면 `libgmp` 관련 함수들이 계속 호출되고 있었다.  
처음에는 단순히 큰 수를 이용한 장난인가 싶었는데, 호출 흐름을 계속 따라가 보니 어떤 상수 테이블을 순회하면서 문자 하나씩 만들어 출력하는 구조라는 점이 보였다.

그래서 `.rodata`를 확인했고, `0x22a0` 부근에 16바이트 단위로 반복되는 데이터가 있다는 것을 확인했다.  
이 구간을 GDB에서 직접 덤프해 보면 다음처럼 일정한 형식으로 값이 들어 있다.

- 앞 8바이트: `a`
- 뒤 8바이트: `b`

즉 `(a, b)` 형태의 쌍 테이블이고, 이 값을 하나씩 읽어서 문자 하나를 만드는 구조였다.

예를 들어 초반 엔트리는 다음과 같이 확인할 수 있었다.

- `0x22a0 -> (706619, 2)`
- `0x22b0 -> (1649525, 2)`
- `0x22c0 -> (3315141, 2)`
- `0x22d0 -> (3672983, 2)`
- `0x22e0 -> (4928205, 2)`

이후 GDB로 문자 생성 루틴에 브레이크를 걸고 한 단계씩 따라가면서, 각 테이블 엔트리마다 결과값이 어떻게 만들어지는지 확인했다.  
GMP를 이용해 재귀적으로 거듭제곱 비슷한 계산을 수행하고 있었고, 실제로는 일반적인 `a^b`가 아니라 **지수 위에 지수가 다시 올라가는 형태**의 연산이었다.

다만 끝까지 따라가 보면 최종적으로 필요한 값은 거대한 정수 그 자체가 아니라 마지막 1바이트뿐이라는 점을 확인할 수 있었다.  


### 취약점

발견한 취약점을 설명합니다.

### 익스플로잇

-먼저 IDA에서 main과 주변 함수들을 보면서 어떤 조건에서 핵심 루틴으로 들어가는지 확인했다.
-그 뒤 문자열 비교를 담당하는 부분과, 그 분기를 통과했을 때 호출되는 GMP 기반 계산 함수를 찾았다.
-다음으로 .rodata의 0x22a0 부근을 확인해 16바이트 단위의 (a, b) 테이블을 찾았다.
이 부분은 GDB에서도 직접 덤프해서 구조를 확인했다.
-그 다음에는 문자 생성 함수에 브레이크를 걸고, 테이블 한 엔트리씩 처리할 때 어떤 값이 만들어지는지 따라갔다.
-그 결과 내부 연산이 사실상 a ↑↑ b mod 256 꼴이고, 마지막에 (x + 1) >> 1 변환을 거쳐 ASCII 문자 하나가 된다는 점을 확인할 수 있었다.
-이제 필요한 정보가 다 모였으므로, 바이너리에서 테이블을 그대로 읽고 같은 계산을 수행하는 복원 스크립트를 작성했다.


```python
# 풀이 코드 예시
#!/usr/bin/env python3
import struct
from functools import lru_cache

BIN_PATH = "./not_quite_optimal"
TABLE_OFF = 0x22A0
TABLE_CNT = 84

def lambda_pow2(m: int) -> int:
    if m == 1:
        return 1
    if m == 2:
        return 1
    if m == 4:
        return 2
    return m >> 2

@lru_cache(None)
def tetration_mod_pow2(a: int, h: int, mod: int) -> int:
    if mod == 1:
        return 0
    if h == 0:
        return 1 % mod
    if h == 1:
        return a % mod

    lam = lambda_pow2(mod)
    exp = tetration_mod_pow2(a, h - 1, lam)
    return pow(a, exp, mod)

def extract_pairs(path: str):
    with open(path, "rb") as f:
        data = f.read()

    pairs = []
    for i in range(TABLE_CNT):
        a, b = struct.unpack_from("<QQ", data, TABLE_OFF + i * 16)
        pairs.append((a, b))
    return pairs

def solve(path: str):
    pairs = extract_pairs(path)
    out = []

    for a, b in pairs:
        x = tetration_mod_pow2(a, b, 256)
        ch = (x + 1) >> 1
        out.append(chr(ch))

    return "".join(out)

if __name__ == "__main__":
    print(solve(BIN_PATH))
```

## 플래그

```
RS{example}
```

## 배운 점

리버싱 문제 처음인데 수학적 접근을 통해 풀이를 간소화 시킬 수 있다는 걸 배움
