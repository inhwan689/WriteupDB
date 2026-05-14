---
ctf_name: "HackForAChange 2026"
challenge_name: "pharmacy-xor-oracle"
category: "crypto"           # web / pwn / rev / crypto / misc
difficulty: "easy"      # easy / medium / hard / insane
author: "laneeeey"
date: "2026-04-01"
points: 300
tags: [XOR, oracle, chosen-plaintext]
---

# pharmacy-xor-oracle

## 문제 설명

> RxSecure 시스템은 마약성 의약품 처방 코드를 보호하기 위해 자체 암호화 방식을 사용한다.  
해당 시스템은 반복 키 XOR 기반 암호화를 사용하며, 인증된 사용자에게는 암호화 테스트 API(encryption oracle)를 제공한다.

## 풀이

### 분석

문제에서 제공된 정보:
- 암호 방식: repeating-key XOR
- 키 길이: 16바이트
- 암호화 오라클 제공
- 암호문: dbded5d3878d848286817a2274767523dc8a858fd180d08688832c2475207672

XOR 암호는 C = P ⊕ K 구조이다.
따라서 양변에 P를 XOR하면 K = C ⊕ P 이 성립하며 평문과 암호문을 알면 키를 복구할 수 있다.

### 취약점

1. 고정된 XOR 키 사용
2. 암호화 오라클 제공

-> chosen-plaintext 공격이 가능하다.

### 익스플로잇

1. 키 복구

암호화 API는 hex 형태의 입력을 받기 때문에 아래와 같이 입력한다.

plaintext: 00000000000000000000000000000000

결과로 나온 암호문:
b9b8b7b6b5b4b3b2b1b0181716151413

XOR 특성상 0 ⊕ K = K 이기에 해당 값이 키 임을 알 수 있다.

2. 복호화
제공된 암호문을 키와 XOR하면 평문을 얻을 수 있다.

```python
def xor_hex(cipher_hex, key_hex):
    c = bytes.fromhex(cipher_hex)
    k = bytes.fromhex(key_hex)
    return bytes(c[i] ^ k[i % len(k)] for i in range(len(c)))

key = "b9b8b7b6b5b4b3b2b1b0181716151413"
cipher = "dbded5d3878d848286817a2274767523dc8a858fd180d08688832c2475207672"

plaintext = xor_hex(cipher, key)

print(plaintext)
```
복호화 결과는 raw bytes 형태로 출력되지만 해당 값은 ASCII로 표현된 문자열이다.  
따라서 decode하여 해석하면 다음과 같은 32자리 hex 문자열을 얻을 수 있다.

복구한 proof code
bfbe297071b5bca0e229d4c49343c5ba

이 값을 사이트 proof code(32 hex characters) 입력칸에 제출하면 flag를 획득할 수 있다.

## 플래그

```
flag{REDACTED}
```
실제 flag는 획득했지만 현재 기록이 남아 있지 않아 마스킹하여 기재하였다.

## 배운 점

- 입력이 hex 형태로 처리되는 경우 ASCII 문자열과 실제 바이트 데이터를 구분하는 것이 중요하다.
- XOR 연산 자체보다도 입력과 출력 데이터의 인코딩 방식을 정확히 해석하는 것이 문제 해결의 핵심이었다.
- 단순한 암호 구조라도 구현 방식(고정 키, 오라클 제공)에 따라 심각한 보안 취약점이 발생할 수 있음을 확인했다.
