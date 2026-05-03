---
ctf_name: "DawgCTF"
challenge_name: "Locksmith"
category: "misc"
difficulty: "medium"
author: "Chik0magenta"
date: "2026-04-11"
points: 100
tags: [osint, reverse-image-search, hardware-identification, visual-analysis]
---

# Locksmith

## 문제 설명

> I saw this weird lock at the escape room I work at.  
> Can you figure out what series it is, and how tall the lock body is?  
>
> The flag will be in the following format: DawgCTF{BEST500_95MM}

- 다이얼 형태의 기계식 자물쇠 이미지가 주어졌다.

---

## 풀이

### 분석

이미지는 버튼식(푸시버튼) 자물쇠로 보이며,  
일반적인 열쇠형이 아닌 특정 브랜드의 기계식 조합 자물쇠로 추정되었다.

따라서 모델명을 식별한 뒤, 해당 모델의 규격을 조사하는 OSINT 문제로 판단하였다.

---

### 핵심 단서

이미지를 역검색한 결과, 해당 자물쇠가 Simplex 브랜드 제품임을 확인할 수 있었다.

---

### 탐색 과정

Google Lens를 사용하여 이미지를 검색한 결과,  
유사한 제품으로 “Simplex 919” 모델이 검색되었다.

해당 제품 페이지에서는 자물쇠 규격 도면이 제공되었고,  
높이가 95mm로 표시되어 있어 이를 기반으로:
```
DawgCTF{SIMPLEX919_95MM}
```

를 제출하였으나 오답이 발생하였다.

---

이에 따라 초기 검색 결과가 정확하지 않을 가능성을 고려하고,  
이미지의 세부 디테일을 다시 확인하였다.

특히 자물쇠 상단의 회전 노브(핸들) 부분의 형태와 각인을 비교한 결과,  
검색 결과로 나온 모델과 실제 이미지 사이에 미세한 차이가 존재함을 확인하였다.

---

이후 Simplex 공식 제품군을 기준으로  
유사 모델들을 비교한 결과, 이미지와 가장 일치하는 제품이  
“Simplex 900 시리즈”임을 확인하였다.

또한 해당 모델의 규격을 조사하여  
자물쇠 본체 높이가 95mm임을 확인하였다.

---

### 결과

모델명과 높이를 조합하여 최종 플래그를 완성하였다.

---

## 플래그

```
DawgCTF{SIMPLEX900_95MM}
```

---

## 배운 점

- 역이미지 검색 결과는 항상 정답이 아니며, 유사 모델이 섞여 나올 수 있다.
- 하드웨어 식별에서는 디테일 비교(형태, 각인, 구조)가 매우 중요하다.
- 공식 사이트 또는 신뢰 가능한 자료를 통해 최종 검증을 수행하는 것이 필요하다.
- OSINT 문제에서는 “첫 검색 결과를 의심하는 태도”가 정답에 도달하는 데 핵심이 된다.