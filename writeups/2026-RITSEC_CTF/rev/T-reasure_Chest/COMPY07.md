---
ctf_name: "RITSEC CTF"
challenge_name: "T-reasure Chest"
category: "rev"
difficulty: "easy"
author: "COMPY07"
date: "2026-04-05"
points: 110
tags: [reverse]
---

# T-reasure Chest

## 문제 설명

> Score! You found a treasure chest! Now if only you could figure out how to unlock it... maybe there's a magic word?

- 바이너리 파일 제공

## 풀이

### 분석

바이너리를 디컴파일하면 
tiny_encrypt_key로 하드코딩된 검증 시스템이 보인다.
사용자 입력을 8바이트 단위로 패딩해서 암호화 후 unk_404080(상수)와 비교해서 일치하면 flag 출력 하는 로직이 있다.


```c
v8 = strlen(s);   
v7 = v8 % 8;     
v8 += v7;        
```
이게 패딩 계산


`x + (x % 8) = 34` 를 만족하는 값은 x = 29 (29 + 5 = 34)로 알아냇다.

암호화 범위는 `34 >> 2 = 8` 루프 → 4블록 × 8바이트 = 32바이트 이고, 나머지 `[32:34]` 2바이트는 암호화되지 않는다.
그래서 실제 상수 가져올 때도 뒤에 2개는 빼고 가져옴


### 취약점

`sub_4011C6` 내부를 보면:
```c
v6 -= 1640531527;  // 0x9E3779B9
v4 += ((v3 >> 5) + a2[1]) ^ (v3 + v6) ^ (16 * v3 + *a2);
v3 += ((v4 >> 5) + a2[3]) ^ (v4 + v6) ^ (16 * v4 + a2[2]);
```

`0x9E3779B9`, 32라운드, 두 32-bit word 교차 연산한다.

키가 바이너리에 하드코딩되어 있어서 `unk_404080` 의 암호문을 그대로 복호화하면 flag를 얻을 수 있다.

### 익스플로잇

IDA에서 `unk_404080` 덤프:
```
38 75 5B CB 44 D2 BE 5D  96 9C 56 43 EA 98 06 75
4A 48 13 E6 D4 E8 8E 4F  72 70 8B FF DC 99 F8 76
C5 C9
```
(여기서 뒤에 2개 C5C9은 빼버리고)


그냥 역산해서 `sum` 을 최종값(`0x9E3779B9 * 32`)에서 시작해 감소시키며 진행한다.

```python
import struct
import ctypes

KEY = b"tiny_encrypt_key"
TARGET = bytes.fromhex("38755BCB44D2BE5D969C5643EA9806754A4813E6D4E88E4F72708BFFDC99F876")

"""

38 75 5B CB 44 D2 BE 5D  96 9C 56 43 EA 98 06 75
4A 48 13 E6 D4 E8 8E 4F  72 70 8B FF DC 99 F8 76


"""


def solution(block, key):
    v0, v1 = struct.unpack('<II', block)
    k = struct.unpack('<4I', key)

    d = 0x9E3779B9

    total = ctypes.c_uint32(d * 32).value
    for _ in range(32):
        v1 = ctypes.c_uint32(v1 - (((v0 >> 5) + k[3]) ^ (v0 + total) ^ ((v0 << 4) + k[2]))).value
        v0 = ctypes.c_uint32(v0 - (((v1 >> 5) + k[1]) ^ (v1 + total) ^ ((v1 << 4) + k[0]))).value
        total = ctypes.c_uint32(total - d).value

    return struct.pack('<II', v0, v1)


result = b''

for i in range(4):
    result += solution(TARGET[i * 8:(i + 1) * 8], KEY)
result += b''
print(result.rstrip(b'\x00').decode())
```

## 플래그
```
RS{REDACTED}
```

## 배운 점
- 코드 분석 능력이 올라갔음.
- 그리고 이러한 암호화가 TEA (Tiny Encryption Algorithm)라는 것을 알았음.