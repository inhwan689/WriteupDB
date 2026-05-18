---
ctf_name: "0xV01DCTF"
challenge_name: "Canvas-Drift"
category: "misc"           # web / pwn / rev / crypto / misc
difficulty: "easy"      # easy / medium / hard / insane
author: "4BO{M7MD}"
date: "2026-05-18"
points: 100
tags: []
---

# 문제명

## 문제 설명

> `canvas.ppm` 파일이 주어진다.

- 문제 URL / 파일 등 접속 정보

## 풀이

### 분석

PPM(P6) 포맷 파일로, 헤더를 확인하면 80x40 크기의 이미지다.
 
```
P6
80 40
255
```
 
픽셀 데이터를 분석하면 RGB 값이 `44`(`,`)와 `45`(`-`) 두 종류만 존재한다.
 
```python
unique = sorted(set(pixel_data))
# [44, 45]
```
 
두 값의 차이가 1비트이므로, 각 바이트를 0/1로 매핑한 비트 스트림으로 볼 수 있다.
 
- `44` → `0`
- `45` → `1`

### 취약점

--

### 익스플로잇

```python
with open('canvas.ppm', 'rb') as f:
    data = f.read()
 
# 헤더 스킵
i = 0
lines = []
while len(lines) < 3:
    line = b''
    while data[i:i+1] != b'\n':
        line += data[i:i+1]
        i += 1
    i += 1
    lines.append(line)
 
pixel_data = data[i:]
bits = [1 if b == 45 else 0 for b in pixel_data]
 
result = []
for j in range(0, len(bits) - 7, 8):
    byte = 0
    for k in range(8):
        byte = (byte << 1) | bits[j + k]
    result.append(chr(byte))
 
print(''.join(result))
```

## 플래그

```
`0xV01D{LSB_PIXELS_TELL_STORIES}`
```

## 배운 점

PPM은 헤더 이후 RGB 픽셀 값이 바이너리로 나열되는 단순한 포맷이라 조작이 쉽다.
픽셀 값 자체를 비트 스트림으로 사용하는 인코딩 방식 — 일반적인 LSB 스테가노그래피와 달리 이미지로서의 위장보다 데이터 인코딩에 집중한 형태다.
