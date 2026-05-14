---
ctf_name: "2026-DawgCTF"
challenge_name: "Through the Looking Bit"
category: "misc"
difficulty: "medium"
author: "vestman828"
date: "2026-04-12"
tags: [misc]
---

# Through the Looking Bit

## 문제 설명

> 2026-DawgCTF에 Through the Looking Bit 문제입니다. Misc입니다.

## 풀이

### 분석

미러사이트를 운영하고 있고, 어떠한 방식으로 "소통"을 해보라고 합니다.

https://lug.umbc.edu/mirror/
여기에 가보면,

Access the mirror:
HTTPS: https://mirror.lug.umbc.edu
HTTP: http://mirror.lug.umbc.edu
RSYNC: rsync://mirror.lug.umbc.edu

이런 것을 볼 수 있는데,

rsync rsync://mirror.lug.umbc.edu/
이렇게 rsync로 접속해볼 수 있습니다.

그러면
0,1 문자로 이뤄진 아스키 아트가 나오는데

rsync rsync://mirror.lug.umbc.edu/ > banner.txt
grep -E '^[ 01_\/|]+$' banner.txt
이걸 파일로 저장해 둔 뒤,

reflection이라는 문제 속 키워드에서 힌트를 받아
비트를 반전시킨 뒤 바이트 단위로 끊어보면
플래그를 얻습니다.

### 익스플로잇

```python
lines = open("banner.txt").read().splitlines()
bits = ''.join(c for line in lines for c in line if c in '01')
bits = bits.translate(str.maketrans('01', '10'))  # invert
text = ''.join(chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8))
print(text)
```

## 플래그

```
DawgCTF{R3ync_1s_b3tt3r_th5n_http}
```

## 배운 점

-
