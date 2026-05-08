---
ctf_name: "2026-KubSTU_CTF"
challenge_name: "Unlucky_13"
category: "crypto"
difficulty: "medium"
author: "yeahhbean"
date: "2026-05-05"
points: 0
tags: [rsa, low-exponent, stream-cipher, xor]
---

# Unlucky_13

## 문제 설명

> 13겹의 암호화. 운이 없으면 풀 수 없다.

- 주어진 파일: `encrypt.py`, `output.txt` (n, e, c 제공)

## 풀이

### 분석

암호화 파이프라인:

```
layer1 = FLAG XOR cursed_prng(13, len(FLAG))
layer2 = forgotten_cipher(fc_key, layer1)   # RC4 유사, fc_key = sha256(b"Unlucky13")[:16]
c      = layer2^e mod n,  e = 3
```

### 취약점

**RSA Small Exponent (e=3) + No Padding**

`e=3`에 패딩이 없고, 메시지(layer2)가 짧아 `layer2^3 < n`이 성립한다.
이 경우 모듈러 연산이 의미가 없어지므로 `c = layer2^3` 이 되어,
`c`의 정수 세제곱근으로 `layer2`를 바로 복원할 수 있다.

이후 `forgotten_cipher`(RC4 유사)와 XOR PRNG를 역순으로 되돌리면 플래그가 나온다.

- `forgotten_cipher`는 대칭 구조라 같은 키로 한 번 더 돌리면 복호화됨
- `cursed_prng`도 동일 seed로 재생성 후 XOR하면 복호화됨

### 익스플로잇

```python
import hashlib

n = 13658633037131788032351618427072247476717954542396408633560773884364554559070511401338131167308785959562652843354491812218130569318378376258845006015571936307529619165627684367938035500689095197148634390329808425228615805061358885887601807910577877331466810636357076781023936730357996997258012513541846157478488478454563307821991031194437503266795021183758263745762989760240683361817082008819321416765453826690538816962208131444601183340450621147225799934380535423737829891317625290259915071423282523846993193854126576514135696151799274710837198613476445017109884172011540789567531049972285279517155764888481047450059
e = 3
c = 58106402945252412885867908042116794819464305744971899578073020304067543548070807457178658563488157040731309267600804875202490191851964629071348907183348604959890636799938893288492152226256276862912678404321252232876509325092153164813635360471085498336853220078206620458027876601442698309483452313201963351276803179820555434275959791505894082437152805771101360567738286600728

UNLUCKY_NUMBER = 13

def iroot3(x):
    lo, hi = 0, 1
    while hi**3 <= x:
        hi *= 2
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if mid**3 <= x:
            lo = mid
        else:
            hi = mid
    return lo

def cursed_prng(seed, length):
    state = seed
    out = []
    for _ in range(length):
        state = (state * 1313 + 131313) % (2**32)
        out.append(state & 0xFF)
    return bytes(out)

def forgotten_cipher(key, data):
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]
    i = j = 0
    out = []
    for b in data:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        out.append(b ^ S[(S[i] + S[j]) % 256])
    return bytes(out)

# Step 1: 정수 세제곱근으로 layer2 복원
m = iroot3(c)
assert m**3 == c
layer2 = m.to_bytes((m.bit_length() + 7) // 8, 'big')

# Step 2: forgotten_cipher 역복호화 (대칭이라 동일 키로 재실행)
secret = b"Unlucky" + str(UNLUCKY_NUMBER).encode()
fc_key = hashlib.sha256(secret).digest()[:16]
layer1 = forgotten_cipher(fc_key, layer2)

# Step 3: cursed_prng XOR 역복호화
flag = bytes(a ^ b for a, b in zip(layer1, cursed_prng(UNLUCKY_NUMBER, len(layer1))))
print(flag.decode())
```

## 플래그

```
KubSTU{unLucky_13_l4y3r5_0f_encrypt10n_n0_luck_h3r3}
```

## 배운 점

- RSA는 반드시 OAEP 같은 패딩과 함께 써야 한다. 패딩 없이 작은 `e`를 사용하면 메시지가 짧을 경우 정수 세제곱근만으로 복호화된다.
- 스트림 암호/XOR 레이어를 여러 겹 둘러도 핵심 레이어(RSA) 설계가 취약하면 전체가 무너진다.
- RC4 유사 스트림 암호는 대칭 구조이므로 같은 키로 한 번 더 돌리면 복호화된다.
