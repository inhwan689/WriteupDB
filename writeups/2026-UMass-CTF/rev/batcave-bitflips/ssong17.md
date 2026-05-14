---
ctf_name: "UMass-CTF"
challenge_name: "Batcave Bitflips"
category: "rev"           # web / pwn / rev / crypto / misc
difficulty: "medium"      # easy / medium / hard / insane
author: "ssong17"
date: "2026-04-11"
points: 100
tags: [태그1, 태그2]
---

# 문제명

## 문제 설명

Batman's new state-of-the-art AI agent has deleted all of the source code to the Batcave license verification program! There's an old debug version lying around, but that thing has been hit by more cosmic rays than Superman!

- 문제 URL / 파일 등 접속 정보: batcave_license_checker ELF 파일

## 풀이

### 분석

사용자로부터 라이선스 키를 입력받아 내부 hash 함수를 거친 뒤, verify 함수에서 memcmp를 통해 정답 해시값과 비교한다.

hash 함수는 내부적으로 expand_state, substitute, mix, rotate 등의 SPN 구조 연산을 0xbeeeef 번 반복한다. 비트 손실이 발생하는 연산이 포함되어 있어 역연산이 수학적으로 불가능하게 설계되어 있다.

### 취약점

해시 역연산 로직은 분석 시간을 낭비하게 만드는 함정이었다.

정답 해시값 배열이 메모리에 평문으로 노출되어 있으며, 프로그램 시작 시 초기화되는 전역 변수 FLAG에 암호화된 원본 플래그 데이터가 하드코딩되어 있다.

### 익스플로잇

1. GDB를 사용하여 검증에 사용되는 정답 해시값 32바이트를 추출한다.

2. GDB를 사용하여 프로그램 시작 시 로드되는 원본 FLAG 전역 변수의 32바이트 데이터를 추출한다.

3. 추출한 두 데이터를 순서대로 XOR 연산하여 원본 플래그를 복구한다.

```python
flag_enc = [0x6e, 0x19, 0x34, 0x49, 0x77, 0x7d, 0xf0, 0x5a, 0x07, 0xb4, 0x33, 0xa6, 0x8c, 0xe6, 0xe6, 0x17, 0xfb, 0xe9, 0x6f, 0xae, 0x2e, 0xe5, 0x26, 0xc3, 0x70, 0xe3, 0xc4, 0x7d, 0x27, 0x7f, 0x2b, 0x00]

expected = [0x3b, 0x54, 0x75, 0x1a, 0x24, 0x06, 0xaf, 0x05, 0x77, 0x80, 0x47, 0xc5, 0xe4, 0x83, 0xd3, 0x48, 0xcb, 0x87, 0x30, 0xde, 0x1a, 0x91, 0x45, 0xab, 0x15, 0xc7, 0x9b, 0x22, 0x04, 0x02, 0x2b, 0xee]

flag = "".join([chr(f ^ e) for f, e in zip(flag_enc, expected)])

print("FLAG:", flag.strip('\x00\xee'))
```

## 플래그

```
UMASS{__p4tche5_0n_p4tche$__#}
```

## 배운 점

비정상적으로 연산량이 많거나 복잡한 함수를 발견했을 때는 이를 직접 리버싱하기보다 우회할 수 있는 다른 메모리 데이터가 있는지 전체적인 구조를 먼저 파악하는 것이 중요하다
