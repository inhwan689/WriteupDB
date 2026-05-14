---
ctf_name: "DawgCTF"
challenge_name: "Computer Repair II"
category: "misc"
difficulty: "easy"
author: "Chik0magenta"
date: "2026-04-11"
points: 125
tags: [osint, reverse-image-search, hardware-identification]
---

# Computer Repair II

## 문제 설명

> I just got another pic from the warehouse, not a lot to go on here, but could you figure out the screen size of this laptop?

- 노트북의 일부가 보이는 이미지가 주어졌다.

---

## 풀이

### 분석

이미지에는 노트북의 모니터와 키보드 일부만 보이며, 직접적인 스펙 정보는 포함되어 있지 않다.  
따라서 모델명을 식별한 뒤 해당 모델의 기본 사양을 조사하는 OSINT 문제로 판단하였다.

---

### 핵심 단서

이미지에서 Dell 로고와 함께, 두꺼운 베젤과 넘패드가 포함된 키보드 레이아웃을 통해
Latitude 5xxx 시리즈 노트북임을 유추할 수 있었으며,
역이미지 검색을 통해 정확한 모델이 Dell Latitude 5590임을 확인하였다.

---

### 탐색 과정

Google Lens를 사용하여 이미지를 검색한 결과,  
해당 노트북 모델명을 빠르게 식별할 수 있었다.

이후 해당 모델의 기본 사양을 조사한 결과,  
디스플레이 크기가 15.6인치임을 확인하였다.

문제에서 요구하는 형식에 맞게 소수점 표기를 유지하여 제출하였다.

---

## 플래그

```
DawgCTF{15.6IN}
```

---

## 배운 점

- 하드웨어 식별 문제에서는 모델명만 알아내면 해결이 매우 쉬워진다.
- Google Lens는 노트북, 스마트폰 등 상용 제품 식별에 매우 강력하다.
- 단, 표시된 값과 실제 스펙 표기를 구분해서 확인하는 것이 중요하다.