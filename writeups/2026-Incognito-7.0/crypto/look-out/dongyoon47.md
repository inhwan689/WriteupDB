---
ctf_name: "Incognito 7.0"
challenge_name: "look out"
category: "crypto"
difficulty: "easy"
author: "dongyoon47"
date: "2026-04-14"
points: 150
tags: [PDF metadata, XOR, steganography]
---

# look out

## 문제 설명

> Look it's plane, no it's a jet, no it's a bird!!!!!!!

첨부 파일은 `Untitled_document.pdf` 하나뿐이다.

## 풀이

### 분석

문제 설명만 봐서는 별 단서가 없어서 PDF 본문보다는 메타데이터와 숨은 구조를 먼저 확인했다.

PDF를 문자열 기준으로 살펴보면 눈에 띄는 두 군데가 있다.

1. 접근성 태그의 `Alt` 값
2. 문서 메타데이터의 `Subject` 값

`Alt` 값은 각 글자가 `char(정수)` 형태로 들어 있었고, 이를 이어 붙이면 다음 문자열이 나온다.

```text
LOOKSLIKEAKEYTOME
```

문제 제목과 설명을 보면 "보이는 것"보다 문서 안쪽을 보라는 느낌이 강해서, 이 문자열을 XOR 키로 써보는 방향이 자연스럽다.

한편 `Subject` 필드에는 긴 이진수 문자열이 들어 있다.

```text
0010010100100110001001100011111100111111000101110001110100000011...
```

이 값을 바이트열로 바꾼 뒤, 위에서 얻은 키를 소문자로 변환한 `lookslikeakeytome`로 반복 XOR 하면 플래그가 복원된다.

### 익스플로잇

아래 스크립트로 바로 복호화할 수 있다.

```python
subject_bits = (
    "0010010100100110001001100011111100111111000101110001110100000011"
    "0000110000010010001101000001001000011000000001110011000000001100"
    "0000101100000010000000000001011000000010000111010000101100110110"
    "0000011100001010000011010011010001010010010000000100110001011101"
    "0101111001011100010110110101011001011000010110000100011000010001"
)

key = b"lookslikeakeytome"
data = int(subject_bits, 2).to_bytes(len(subject_bits) // 8, "big")
flag = bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
print(flag.decode())
```

출력 결과는 실제 플래그이며, 아래에는 마스킹해서 적는다.

## 플래그

```text
IIITL{REDACTED}
```

## 배운 점

PDF 문제는 화면에 보이는 텍스트만 보지 말고 메타데이터, 접근성 태그, 구조 트리까지 같이 확인해야 한다. 특히 `Alt`, `Subject`, `Keywords` 같은 필드는 간단한 숨김 채널로 자주 쓰인다.
