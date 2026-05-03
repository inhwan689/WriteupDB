---
ctf_name: "DawgCTF"
challenge_name: "Crazy Looking Building"
category: "misc"
difficulty: "easy"
author: "Chik0magenta"
date: "2026-04-11"
points: 50
tags: [osint, reverse-image-search, architecture]
---

# Crazy Looking Building

## 문제 설명

> I used to work at this crazy looking building. I've attached a picture of it, can you guess where it is?  
> If you can, the flag is the nickname the building has.

- 문제에는 독특한 형태의 건물 이미지가 주어졌다.

---

## 풀이

### 분석

이미지는 일반적인 건물이 아닌, 계단식 피라미드 형태의 매우 독특한 구조를 가지고 있다.  
이러한 특징적인 건축물은 온라인에 널리 알려져 있을 가능성이 높다고 판단하였다.

---

### 핵심 단서

주어진 이미지를 Google Lens로 검색한 결과, 해당 건물이 체트 홀리필드 연방 빌딩임을 확인할 수 있었다.

이 건물은 독특한 외형으로 인해 “The Ziggurat Building”이라는 별명으로도 알려져 있다.

---

### 탐색 과정

역이미지 검색을 통해 건물의 정체를 빠르게 특정할 수 있었다.

이후 해당 건물의 별명을 조사하였으며,  
“The Ziggurat”이라는 명칭이 사용됨을 확인하였다.

그러나 문제에서 요구하는 플래그를 제출하였을 때 오답이 발생하였다.

---

이후 문제에서 요구하는 형식을 다시 확인한 결과,  
예시에서 단순 별명이 아닌 전체 명칭을 사용하는 것을 확인하였다.

이에 따라 별명을 확장한  
“The Ziggurat Building”을 사용해야 함을 알게 되었고,  
공백을 언더스코어로 변환하여 제출하였다.

---

### 결과

“The Ziggurat Building”이 정답이며,  
플래그 형식에 맞게 제출하였다.

---

## 플래그

```
DawgCTF{The_Ziggurat_Building}
```

---

## 배운 점

- 특징적인 건축물은 역이미지 검색으로 빠르게 식별할 수 있다.
- 문제에서 요구하는 출력 형식은 예시를 통해 정확히 파악해야 한다.
- 단순한 정답이 아닌, 문제에서 요구하는 “표현 방식”이 중요한 경우가 많다.