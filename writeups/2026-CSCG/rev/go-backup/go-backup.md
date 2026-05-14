---
ctf_name: "CSCG 2026"
challenge_name: "GO! Backup"
category: rev
difficulty: medium
author: go-backup
date: 2026-04-05
points: 114
tags: [go, reverse-engineering, checksum, ean13, isbn10, luhn]
---

# GO! Backup

## TL;DR

Go 바이너리는 입력을 직접 저장하지 않는다. 대신 각 문자를 체크섬 합이 원래 문자의 ASCII 값과 일치하는 유효한 `EAN-13`, `ISBN-10`, 또는 신용카드 번호로 변환한다.

`backup.pdf`에 나온 값들의 체크섬 규칙을 역으로 적용하면 숨겨진 메시지를 복원할 수 있고, 최종 플래그를 `DHM{REDACTED}` 형태로 얻을 수 있다.

## 개요

챌린지에서 두 개의 파일이 제공된다:

- `backup`: 정적 링크된 Go ELF 바이너리
- `backup.pdf`: 프로그램이 생성한 출력 문서

프로그램을 테스트로 실행해보면, 입력 문자열을 받아 세 가지 카테고리로 출력한다:

- `EANs`
- `ISBNs`
- `Credit Cards`

예를 들어, `test`를 입력하면 다음과 같은 결과가 나온다:

```text
EANs: [3125254846864]
ISBNs:
  ISBN 1-500-40107-2
Credit Cards: [4499494849448985 8999984789472694]
```

즉, 이것은 일반적인 백업 유틸리티가 아니다. 입력 문자를 체크섬이 유효한 코드로 인코딩하는 변환기다.

## PDF 데이터

PDF를 렌더링하면 총 24개의 값을 얻을 수 있다:

- Products 아래 8개의 EAN-13 값
- Books 아래 8개의 ISBN-10 값
- Cards 아래 8개의 신용카드 번호

### EAN-13

```text
4932413071222
9215337181228
4055572232713
3177777536937
5194353145886
8022631001531
2177559451930
9375914288310
```

### ISBN-10

```text
0-024-00310-7
0-238-30610-0
3-505-52102-7
0-022-11111-5
6-052-75101-0
8-323-17020-7
6-422-29100-0
5-112-73112-5
```

### 신용카드 번호

```text
5217 8047 6654 5209
4885 3738 2748 6781
5839 8995 9849 6843
9587 9819 8899 9895
8837 9988 4989 4933
8986 9899 9996 6281
9999 9929 4769 3935
9999 4893 9899 9945
```

## 핵심 아이디어

정적 분석을 통해 세 가지 중요한 생성 함수를 확인할 수 있다:

- `main.a640`: EAN-13 값 생성
- `main.eee5`: ISBN-10 값 생성
- `main.dd16`: 신용카드 번호 생성

핵심 관찰 포인트는, 이 함수들이 단순히 랜덤한 유효 코드를 생성하는 것이 아니라는 점이다. 체크섬 합이 원본 문자의 ASCII 값과 일치하는 유효한 코드를 생성한다.

즉, 출력된 각 코드는 정확히 하나의 원본 문자에 대응된다.

## 체크섬 역산

### 1. EAN-13

EAN-13에서 마지막 자리는 체크 디짓이다. 앞 12자리에 가중치 `1, 3, 1, 3, ...`을 번갈아 적용한다.

```text
d1*1 + d2*3 + d3*1 + d4*3 + ... + d12*3
```

바이너리는 이 가중합을 문자 값으로 사용한다.

```python
def ean_sum(s):
    return sum(int(ch) * (1 if i % 2 == 0 else 3) for i, ch in enumerate(s[:12]))
```

### 2. ISBN-10

ISBN-10에서 마지막 자리는 체크 문자이다. 앞 9자리에 가중치 `1..9`를 적용한다.

```text
1*d1 + 2*d2 + 3*d3 + ... + 9*d9
```

```python
def isbn_sum(s):
    digits = [int(ch) for ch in s if ch.isdigit()][:9]
    return sum((i + 1) * x for i, x in enumerate(digits))
```

### 3. 신용카드 번호 (Luhn 알고리즘)

카드 번호는 Luhn 알고리즘을 사용한다. 앞 15자리의 Luhn 기여값을 계산하면, 그 합이 원본 문자 값이 된다.

```python
def luhn15_sum(s):
    d = [int(ch) for ch in s if ch.isdigit()][:15]
    total = 0
    for i, x in enumerate(d):
        off = 14 - i
        if off % 2 == 0:
            y = x * 2
            if y > 9:
                y -= 9
        else:
            y = x
        total += y
    return total
```

## 메시지 복원

위 공식을 적용하면 세 개의 청크를 얻을 수 있다.

### EAN에서 복원

```text
DHM{h1dd
```

### ISBN에서 복원

```text
3n_1n_ch
```

### 신용카드 번호에서 복원

```text
3cksums}
```

이를 연결하면 플래그를 얻을 수 있다:

```text
DHM{REDACTED}
```

## 풀이 스크립트

```python
eans = [
    "4932413071222",
    "9215337181228",
    "4055572232713",
    "3177777536937",
    "5194353145886",
    "8022631001531",
    "2177559451930",
    "9375914288310",
]

isbns = [
    "0-024-00310-7",
    "0-238-30610-0",
    "3-505-52102-7",
    "0-022-11111-5",
    "6-052-75101-0",
    "8-323-17020-7",
    "6-422-29100-0",
    "5-112-73112-5",
]

cards = [
    "5217804766545209",
    "4885373827486781",
    "5839899598496843",
    "9587981988999895",
    "8837998849894933",
    "8986989999966281",
    "9999992947693935",
    "9999489398999945",
]

def ean_sum(s):
    return sum(int(ch) * (1 if i % 2 == 0 else 3) for i, ch in enumerate(s[:12]))

def isbn_sum(s):
    digits = [int(ch) for ch in s if ch.isdigit()][:9]
    return sum((i + 1) * x for i, x in enumerate(digits))

def luhn15_sum(s):
    d = [int(ch) for ch in s if ch.isdigit()][:15]
    total = 0
    for i, x in enumerate(d):
        off = 14 - i
        if off % 2 == 0:
            y = x * 2
            if y > 9:
                y -= 9
        else:
            y = x
        total += y
    return total

flag = (
    "".join(chr(ean_sum(x)) for x in eans)
    + "".join(chr(isbn_sum(x)) for x in isbns)
    + "".join(chr(luhn15_sum(x)) for x in cards)
)

print(flag)
```

## 결론

처음에는 바코드나 데이터 형식 문제처럼 보이지만, 실제로는 체크섬 시스템 자체를 은닉 채널로 사용하는 문제다.

중요한 통찰은 숨겨진 값이 최종 체크 디짓이 아니라, 최종 체크 디짓이 계산되기 전의 가중 체크섬 합이라는 점이다.
