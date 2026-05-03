---
ctf_name: "DawgCTF"
challenge_name: "Дмитрий-шесть"
category: "misc"
difficulty: "easy"
author: "Chik0magenta"
date: "2026-04-11"
points: 50
tags: [osint, reverse-image-search]
---

# Дмитрий-шесть (Dmitriy-Six)

## 문제 설명

> My friend from Ukraine sent me this weird picture, he says that it's the key to a secret treasure room underground. Do you know where this picture was taken? The flag will be the official name of it, and should be 6 letters total, all capital letters. Limit of ten attempts.

- 문제에는 지하철, 혹은 지하 시설로 보이는 이미지가 세 장 주어졌다.

---

## 풀이

### 분석

이미지는 일반적인 지하 시설이 아닌, 군사적이거나 비밀 시설로 보이는 구조를 가지고 있다.  
문제 설명에서 “Ukraine”, “secret treasure room underground” 등의 표현이 사용된 점을 고려할 때,  
소련 시절의 비밀 지하 시설과 관련된 OSINT 문제로 판단하였다.

---

### 핵심 단서

주어진 이미지를 Google Lens로 검색한 결과,  
해당 이미지가 Metro-2(D-6)와 관련된 자료임을 확인할 수 있었다.

Metro-2는 소련 시절 구축된 비밀 지하철 시스템으로,
정부 및 군사 시설을 연결하는 용도로 사용된 것으로 알려져 있다.

---

### 탐색 과정

역이미지 검색을 통해 대상이 Metro-2임을 비교적 빠르게 특정할 수 있었다.

그러나 문제에서 요구하는 플래그 조건이  
“6 letters, all capital letters”였기 때문에,  
숫자가 포함된 "METRO2"는 정답이 아닐 것이라고 판단하였다.

이에 따라 다음과 같은 후보들을 시도하였다:

- METROT  
- ODESSA  
- KGBSYS
- KGBMET  

하지만 모두 오답이었다.

---

이후 조건을 다시 검토하면서,  
문제에서 사용된 “letters”가 엄밀한 의미가 아니라  
단순히 “문자 수”를 의미할 가능성을 고려하였다.

가장 자연스럽고 널리 사용되는 명칭은 "Metro-2"였기 때문에,  
이를 대문자로 변환한 "METRO2"를 입력하였다.

---

### 결과

"METRO2"가 정답으로 처리되었으며,  
플래그 형식에 맞게 제출하였다.

---

## 플래그

```
METRO2
```


---

## 배운 점

- 역이미지 검색을 통해 대상 자체를 빠르게 특정할 수 있음을 확인하였다.
- OSINT 문제에서는 대상 식별 이후, 문제의 출력 형식을 정확히 해석하는 것이 중요하다.
- 문제에서 제시된 조건(letters, characters 등)은 항상 엄밀하게 사용되지 않을 수 있으므로, 정답에 대한 확신이 있다면 조건을 재검토하는 유연한 사고가 필요하다.