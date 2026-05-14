---
ctf_name: "2026-DawgCTF"
challenge_name: "Let's Avoid Doing Mathn"
category: "misc"
difficulty: "medium"
author: "vestman828"
date: "2026-04-12"
tags: [misc]
---

# Andy Martin

## 문제 설명

> 2026-DawgCTF에 Let's Avoid Doing Math 문제입니다. Misc입니다.

## 풀이

### 분석

1. 로그 120개로 3클래스 confusion matrix를 만듭니다.

- known minor: detected minor=38, medium=0, major=2
- known medium: detected minor=3, medium=30, major=7
- known major: detected minor=1, medium=8, major=31

2. 각 클래스마다 one-vs-rest로 Accuracy, FPR, FNR 계산:

- minor: TP=38, FP=4, FN=2, TN=76
    - accuracy = (TP+TN)/120 = 114/120 = 0.95
    - FPR = FP/(FP+TN) = 4/80 = 0.05
    - FNR = FN/(FN+TP) = 2/40 = 0.05
- medium: TP=30, FP=8, FN=10, TN=72
    - accuracy = 102/120 = 0.85
    - FPR = 8/80 = 0.1
    - FNR = 10/40 = 0.25
- major: TP=31, FP=9, FN=9, TN=71
    - accuracy = 102/120 = 0.85
    - FPR = 9/80 = 0.1125
    - FNR = 9/40 = 0.225

3. 문제 문구대로 “growing order of importance” = minor, medium, major 순서로 나열.
4. 포맷 조건:

- 모든 값 0.x 형태(leading zero 1개)
- trailing zero 없음
- comma-separated, 공백 없음

최종:
0.95,0.05,0.05,0.85,0.1,0.25,0.85,0.1125,0.225

### 익스플로잇

```python
(사용한 익스플로잇 없음)
```

## 플래그

```
0.95,0.05,0.05,0.85,0.1,0.25,0.85,0.1125,0.225
```

## 배운 점

-
