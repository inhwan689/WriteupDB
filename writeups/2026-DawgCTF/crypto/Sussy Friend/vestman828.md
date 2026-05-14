---
ctf_name: "2026-DawgCTF"
challenge_name: "Sussy Friend"
category: "crypto"
difficulty: "medium"
author: "vestman828"
date: "2026-04-12"
tags: [crypto]
---

# Sussy Friend

## 문제 설명

> 2026-DawgCTF에 Sussy Friend 문제입니다. Crypto입니다.

## 풀이

### 분석

어몽어스 게임의 스크린샷들이 주어집니다.
일단 풀이부터 설명하자면, 각 스크린샷의 크루원 배치를 Hexahue(색상 2x3 치환 암호)로 읽는 문제입니다.

1) 왜 Hexahue라고 판단했는가

1. 매 프레임마다 항상 6명의 핵심 색상 크루원(빨강/초록/노랑/파랑/시안/핑크)이 등장합니다.
2. 배치가 문자 하나처럼 프레임마다 바뀝니다.
3. 일부 프레임은 흑/백/회색 크루원만 나오는데, Hexahue에서 숫자 계열이 정확히 흑/백/회색으로 표현됩니다.
4. 즉, 프레임 1장 = Hexahue 문자 1개 구조입니다.

참고 차트: https://www.boxentriq.com/alphabets/hexahue

2) 읽는 규칙

1. 각 프레임에서 6명을 위에서 아래로 3행으로 나눕니다.
2. 각 행은 왼쪽→오른쪽 순서로 읽습니다.
3. 그러면 2x3 색 배열이 되고, Hexahue 표에서 대응 문자/숫자를 찾습니다.

색 약어:

- R 빨강, G 초록, Y 노랑, B 파랑, C 시안, P 핑크
- K 검정, W 흰색, A 회색(Gray)

3) 각 스크린샷 디코딩

1. screenshot_0: R G / P Y / B C → C
2. screenshot_1: K A / W K / A W → 0
3. screenshot_2: Y G / B C / P R → L
4. screenshot_3: K A / W K / A W → 0
5. screenshot_4: B C / Y P / R G → R
6. screenshot_5: W A / K A / W K → 5
7. screenshot_6: P R / G Y / B C → A
8. screenshot_7: B C / Y P / R G → R
9. screenshot_8: R G / Y B / P C → E
10. screenshot_9: R G / Y B / C P → F
11. screenshot_10: B C / P R / G Y → U
12. screenshot_11: Y B / C G / P R → N

연결하면:
C0L0R5AREFUN

따라서 최종 플래그는 DawgCTF{C0L0R5AREFUN}입니다.

### 익스플로잇

```python
(작성한 익스가 없음)
```

## 플래그

```
DawgCTF{C0L0R5AREFUN}
```

## 배운 점

대부분의 이름없는 CTF는 크립토를 너무 MISC스럽게 내는 경향이 있는 것 같다.
