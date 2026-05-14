---
ctf_name: "2026-VishwaCTF"
challenge_name: "The Eaze-y Way Out"
category: "crypto"
difficulty: "medium"
author: "vestman828"
date: "2026-04-05"
tags: [vigenere]
---

# Hidden_Network

## 문제 설명

> 2026-VishwaCTF에 The Eaze-y Way Out 문제입니다. Crypto입니다.

## 풀이

### 분석

enc = "AriozzYCQ{Vawr_Xjxggmpezlox}"만 주어졌습니다.
문제의 설명을 통해 힌트를 얻을 수 있었는데, A<->Z 와 같이 거울처럼 대칭하여 각 문자를 바꾸는게 1단계였습니다.
이후에는 vigenere_decrypt을 통해 최종 플래그를 얻을 수 있었습니다.
key = "EAZE" 역시 제목에서 힌트를 얻었습니다.

### 익스플로잇

```python
def atbash(text: str) -> str:
    result = []

    for ch in text:
        if 'A' <= ch <= 'Z':
            result.append(chr(ord('Z') - (ord(ch) - ord('A'))))
        elif 'a' <= ch <= 'z':
            result.append(chr(ord('z') - (ord(ch) - ord('a'))))
        else:
            result.append(ch)

    return ''.join(result)


def vigenere_decrypt(ciphertext: str, key: str) -> str:
    result = []
    key = key.upper()
    key_index = 0

    for ch in ciphertext:
        if 'A' <= ch <= 'Z':
            shift = ord(key[key_index % len(key)]) - ord('A')
            plain = (ord(ch) - ord('A') - shift) % 26
            result.append(chr(plain + ord('A')))
            key_index += 1
        elif 'a' <= ch <= 'z':
            shift = ord(key[key_index % len(key)]) - ord('A')
            plain = (ord(ch) - ord('a') - shift) % 26
            result.append(chr(plain + ord('a')))
            key_index += 1
        else:
            result.append(ch)

    return ''.join(result)


enc = "AriozzYCQ{Vawr_Xjxggmpezlox}"
key = "EAZE"

step1 = atbash(enc)
step2 = vigenere_decrypt(step1, key)

print("After Atbash :", step1)
print("Final result :", step2)
```

## 플래그

```
VishwaCTF{Eaze_Cryptography}
```

## 배운 점

Weight 40아래인 Bad CTF는 거르자
