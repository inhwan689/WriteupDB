---
ctf_name: RITSEC CTF 2026
challenge_name: cascading-the-seven-seas
category: misc
difficulty: hard
author: no-carve-only-pizza
date: 2026-04-03
points: 416
tags: [CSS, x86, reverse-engineering, z3, brute-force]
---

# Cascading the Seven Seas

## 개요

순수 CSS만으로 x86 16비트(8086) CPU 에뮬레이터를 구현한 문제.  
Chromium 기반 브라우저에서만 동작하며, 해적 퀴즈 3개를 모두 맞혀야 플래그가 출력된다.

- **URL**: https://css.ctf.ritsec.club/
- **점수**: 416 pts

## 분석

### CSS x86 에뮬레이터 구조

페이지 소스를 보면 자바스크립트가 전혀 없다.  
`@property`, `@function`, `@keyframes`만으로 레지스터·메모리·클럭 사이클을 구현했다.

```css
/* 레지스터 */
@property --AX { syntax: "<integer>"; initial-value: 0; inherits: false; }
@property --IP { syntax: "<integer>"; initial-value: 769; inherits: false; }

/* 메모리: --m0 ~ --m1567 */
@property --m256 { syntax: "<integer>"; initial-value: 86; inherits: false; }
```

IP 초기값이 `769 = 0x301`이므로 코드 실행은 m769(0x301)부터 시작한다.

### 메모리 맵

| 주소 | 용도 |
|------|------|
| 0x0000–0x00FF | m0=204(RET), m1~=0x90(NOP 슬레드) |
| 0x0100–0x031F | x86 코드 영역 |
| 0x0320–0x04BF | 퀴즈 답 검증 테이블 |
| 0x04C0–0x05AF | 문자열 영역 |
| 0x05B0–0x05FF | 사용자 입력 버퍼 |

각 퀴즈마다 별도 테이블 사용:
- Quiz 1: `0x0470`
- Quiz 2: `0x0420`
- Quiz 3: `0x0320`

### 비교 함수 역공학 (0x01A7)

CSS에서 `--mN`의 `initial-value`를 전부 추출해 바이너리를 재구성한 뒤,  
capstone으로 디스어셈블했다.

```
0x01A7  compareAnswer(di=input_buf, si=table_ptr, length)

; 글자마다 반복:
0x01CF  mov bx, [cx+2]      ; ptr1 = entry[2:4]
0x01D2  mov al, [bx+di]     ; val1 = input[ptr1]
0x01D5  xchg dx, ax
0x01D8  mov bx, [cx+4]      ; ptr2 = entry[4:6]
0x01DB  mov al, [bx+di]     ; val2 = input[ptr2]
0x01DE  add dx, ax           ; dx = val1 + val2
0x01E2  mov bx, [cx]        ; ptr0 = entry[0:2]
0x01E4  mov al, [bx+di]     ; val0 = input[ptr0]
0x01E7  xor dx, ax           ; dx = (val1+val2) XOR val0
0x01EC  cmp dx, [si-2]      ; expected = entry[6:8]
```

각 테이블 엔트리(8바이트) 구조:

```
entry = [ ptr0(2B) | ptr1(2B) | ptr2(2B) | expected(2B) ]

검증 조건: ( input[ptr1] + input[ptr2] ) XOR input[ptr0] == expected
```

## 풀이

### Quiz 1 — Which ocean is the largest?

코드에서 `cmp ax, 7` → 7글자.  
비교 함수를 Python으로 에뮬레이션해 `PACIFIC`으로 통과 확인.

**정답: `PACIFIC`**

### Quiz 2 — Name an aquatic mammal

코드에서 `cmp ax, 5` → 5글자.  
테이블(0x0420)에서 5개 제약 조건 추출:

```
(inp[1]+inp[4]) XOR inp[3] = 199
(inp[3]+inp[2]) XOR inp[4] = 224
(inp[4]+inp[3]) XOR inp[0] = 208
(inp[4]+inp[0]) XOR inp[3] = 222
(inp[1]+inp[3]) XOR inp[2] = 240
```

대문자 A–Z 전수탐색(26⁵)으로 유일해 도출:

```python
from itertools import product

constraints = [
    (3,1,4,199), (4,3,2,224), (0,4,3,208),
    (3,4,0,222), (2,1,3,240),
]

def check(inp):
    for p0,p1,p2,exp in constraints:
        if (inp[p1]+inp[p2]) ^ inp[p0] != exp:
            return False
    return True

for chars in product(range(65,91), repeat=5):
    if check(chars):
        print(''.join(chr(c) for c in chars))
# 출력: HORSE
```

**정답: `HORSE`**

### Quiz 3 — What's the flag?

코드에서 `cmp ax, 0x20` → 32글자.  
테이블(0x0320)에서 32개 제약 조건 추출 후 z3 SMT Solver 사용:

```python
from z3 import *

inp = [BitVec(f'c{i}', 16) for i in range(32)]
s = Solver()

for v in inp:
    s.add(v >= 32, v <= 126)

# 플래그 형식
s.add(inp[0]==ord('R'), inp[1]==ord('S'),
      inp[2]==ord('{'), inp[31]==ord('}'))

# 32개 제약 추가 (테이블에서 추출)
constraints = [
    (18,12,25,247),(5,11,0,177),(14,20,28,223),(6,23,12,214),
    (28,3,15,209),(2,1,4,222),(14,27,3,220),(1,24,19,193),
    (29,7,22,57),(8,9,6,247),(6,27,30,51),(18,10,6,202),
    (10,28,3,211),(16,21,26,81),(12,20,24,254),(11,10,4,150),
    (13,28,17,239),(2,15,12,202),(12,19,18,218),(4,27,30,37),
    (6,17,26,212),(17,14,16,210),(31,27,17,220),(31,18,29,229),
    (13,25,7,59),(28,18,10,226),(31,30,8,244),(7,5,9,163),
    (16,28,30,77),(27,12,6,225),(5,27,28,181),(31,18,10,219),
]
for p0,p1,p2,exp in constraints:
    s.add(((inp[p1]+inp[p2])^inp[p0]) == exp)

if s.check() == sat:
    m = s.model()
    print(''.join(chr(m[inp[i]].as_long()) for i in range(32)))
```

**정답: `RS{CR3D1T_T0_LYR4_R3B4N3_F1BDF5}`**

## 플래그

```
RS{REDACTED}
```

## 핵심 포인트

CSS가 Turing-complete하게 x86을 에뮬레이션한다는 사실을 인지하는 것이 출발점.  
소스를 CSS라고 무시하지 않고 x86 바이너리 역공학으로 접근해야 풀린다.
