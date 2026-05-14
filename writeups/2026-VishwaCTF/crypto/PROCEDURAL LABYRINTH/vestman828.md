---
ctf_name: "2026-VishwaCTF"
challenge_name: "PROCEDURAL LABYRINTH"
category: "crypto"
difficulty: "medium"
author: "vestman828"
date: "2026-04-05"
tags: [misc]
---

# PROCEDURAL LABYRINTH

## 문제 설명

> 2026-VishwaCTF에 PROCEDURAL LABYRINTH 문제입니다. Crypto입니다.

## 풀이

### 분석

텍스트로 만든 미로가 주어집니다.
유일한 탈출 경로를 움직이는 데 쓰인 이동 패턴을 인코딩된 데이터로 해석하는 문제일 것으로 보았습니다.

정답은 복원한 경로를 두 행씩 묶어서 처리하는 것이었습니다.
각 인접한 행 쌍에서 경로는 다음 두 경우 중 하나로 이동합니다.

오른쪽으로 한 칸 이동: (x, x+1)
왼쪽으로 한 칸 이동: (x, x-1)

이 패턴은 자연스럽게 이진 비트열로 매핑할 수 있습니다.

오른쪽 이동 = 0
왼쪽 이동 = 1

이렇게 탈출 경로 전체에 대해 비트를 수집한 뒤, 이를 8비트씩 묶어 ASCII로 디코딩하면 됩니다.
그러면 곧바로 다음과 같이 읽을 수 있는 문자열이 나타납니다.


### 익스플로잇

```python
from collections import deque

with open("chal.txt", "r", encoding="utf-8") as f:
    lines = [line.rstrip("\n") for line in f]

# Keep only the maze body
maze = [line for line in lines if line and set(line) <= set("#.><")]
H, W = len(maze), len(maze[0])

grid = [list(row) for row in maze]

start = end = None
for r in range(H):
    for c in range(W):
        if grid[r][c] == '>':
            start = (r, c)
        elif grid[r][c] == '<':
            end = (r, c)

# BFS to recover the unique path
q = deque([start])
parent = {start: None}
DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]

while q:
    r, c = q.popleft()
    if (r, c) == end:
        break
    for dr, dc in DIRS:
        nr, nc = r + dr, c + dc
        if 0 <= nr < H and 0 <= nc < W:
            if grid[nr][nc] in ".><" and (nr, nc) not in parent:
                parent[(nr, nc)] = (r, c)
                q.append((nr, nc))

# Reconstruct path
path = []
cur = end
while cur is not None:
    path.append(cur)
    cur = parent[cur]
path.reverse()

# Record one x-position per row along the solved path
row_to_col = {}
for r, c in path:
    row_to_col[r] = c

xs = [row_to_col[r] for r in range(H)]

# Decode: every two rows encode one bit
bits = []
for i in range(0, len(xs) - 1, 2):
    a, b = xs[i], xs[i + 1]
    if b == a + 1:
        bits.append('0')
    elif b == a - 1:
        bits.append('1')
    else:
        raise ValueError(f"Unexpected pair at rows {i}, {i+1}: {a}, {b}")

# Convert bits to bytes
out = bytearray()
for i in range(0, len(bits), 8):
    chunk = ''.join(bits[i:i+8])
    if len(chunk) < 8:
        break
    out.append(int(chunk, 2))

# Drop trailing null padding if present
flag = out.rstrip(b'\x00').decode()
print(flag)
```

## 플래그

```
VishwaCTF{p4th_1s_th3_m3ss4g3_00_eaaa5c9b}
```

## 배운 점

Weight 40아래인 Bad CTF는 거르자
