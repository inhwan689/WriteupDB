---
ctf_name: "KubSTU CTF 2026"
challenge_name: "Cat girl conspiracy"
category: "crypto"
difficulty: "hard"
author: "ttzero25"
date: "2026-05-01"
points: 1000
tags: [SHA256, hash, steganography, file-analysis]
---

# 문제명

## 문제 설명

> 이상한 아카이브인데다가 이름도 이상해. 최대한 빨리 처리해 줘. 플래그 형식: KUBSTU{}

- 첨부 파일: `64_what_could_this_mean.zip

## 풀이

### 분석

압축 파일을 열면 다음과 같은 구조가 나온다.
64_what_could_this_mean.zip
├── what_could_this_mean.txt    # 3968자 hex string
├── 0/ ~ 9/
├── A/ ~ Z/
├── _/
├── {/
└── }/

각 폴더 안에는 <16자리 hex>.jpg 형식의 고양이 이미지가 들어 있으며, 총 1890개다.

핵심:
폴더 이름 = 0~9, A~Z, _, {, } → 플래그에 쓰일 수 있는 문자 집합
파일 이름 = 16자리 hex 값 (8 bytes)
txt 파일 = 의미를 알 수 없는 긴 hex 문자열 (3968자)

### 취약점

문제 파일명 `64_what_could_this_mean`에서 **"64"** 가 핵심 단서다.

txt 파일의 hex 문자열 길이를 계산하면:

```
3968 hex chars ÷ 64 = 62
```

SHA-256 해시 하나의 크기는 256 bits = 32 bytes = 64 hex chars로, 정확히 나누어 떨어진다.
즉, txt = 이미지 파일들의 SHA-256 해시 62개를 순서대로 이어붙인 것이다.
실제로 이미지 파일 하나의 SHA-256을 계산해보면 txt 안에서 발견된다.

```python
import hashlib

with open('extract/4/08d5a7a1a105978f.jpg', 'rb') as f:
    data = f.read()

sha = hashlib.sha256(data).hexdigest()
print(sha in hex_data)  # True (위치: 768번째 문자)
```

### 익스플로잇

모든 이미지(1890개)의 SHA-256을 계산해 해시 → 폴더명 사전을 구성한 뒤,
txt를 64자씩 나누어 각 해시에 대응하는 폴더명(= 플래그 문자)을 순서대로 이어 붙인다.

```python
import os, hashlib

# 1. 모든 이미지의 SHA-256 → 폴더명 사전 구축
sha_to_folder = {}
for folder in os.listdir('extract'):
    path = f'extract/{folder}'
    if os.path.isdir(path):
        for fname in os.listdir(path):
            with open(f'{path}/{fname}', 'rb') as f:
                data = f.read()
            sha = hashlib.sha256(data).hexdigest()
            sha_to_folder[sha] = folder

# 2. txt를 64자씩 나누어 플래그 조립
hex_data = open('extract/what_could_this_mean.txt').read().strip()

flag = ''
for i in range(0, len(hex_data), 64):
    chunk = hex_data[i:i+64]
    if len(chunk) == 64:
        flag += sha_to_folder.get(chunk, '?')

print(flag)
```

## 플래그

```
KUBSTU{A7_LE4ST_N0W_Y0U_H4V3_A_BUNCH_0F_P1CTUR3S_OF_C4T_GIRL5}
```

## 배운 점

파일명, 폴더명, 파일 개수 등 메타데이터 자체가 힌트가 될 수 있다.
