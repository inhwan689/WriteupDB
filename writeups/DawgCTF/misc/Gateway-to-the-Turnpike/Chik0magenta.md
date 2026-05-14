---
ctf_name: "DawgCTF"
challenge_name: "Gateway-to-the-Turnpike"
category: "misc"
difficulty: "easy"
author: "Chik0magenta"
date: "2026-04-11"
points: 50
tags: [osint, geolocation, reverse-image-search]
---

# Gateway to the Turnpike

## 문제 설명

> They say all roads lead to Rome, but in this part of the mid-Atlantic, all roads lead to a very confusing set of gas stations. I snapped this photo on a road trip a while back. Do you think you could tell me the ZIP code of the place this was taken? Limit of ten attempts.

- 문제에는 도로와 여러 개의 주유소가 보이는 사진이 주어졌다.

---

## 풀이

### 분석

문제 설명에서 “mid-Atlantic”, “confusing set of gas stations”라는 표현이 주어졌으며,  
이미지 또한 여러 주유소가 한 지점에 밀집된 독특한 구조를 보여준다.

이는 특정 지역의 특징적인 도로 구조를 기반으로 위치를 특정하는  
Geo-OSINT 문제로 판단하였다.

---

### 핵심 단서

주어진 이미지를 Google Lens로 검색한 결과,  
해당 장소가 Breezewood임을 확인할 수 있었다.

Breezewood는 미국 펜실베이니아에 위치한 지역으로,  
고속도로가 직접 연결되지 않아 일반 도로를 통해 우회해야 하며,  
이로 인해 주유소와 상업 시설이 밀집된 독특한 구조로 유명하다.

---

### 탐색 과정

역이미지 검색을 통해 해당 장소가 Breezewood임을 빠르게 특정할 수 있었다.

추가적으로 지도 검색을 통해 해당 지역의 상세 정보를 확인하였고,  
해당 지역의 ZIP 코드를 조사하였다.

---

### 결과

Breezewood의 ZIP 코드는 **15533**이며,  
이를 플래그 형식에 맞게 제출하였다.

---

## 플래그

```
15533
```

---

## 배운 점

- 이미지에 특징적인 구조가 있을 경우, 역이미지 검색이 매우 효과적이다.
- 특정 지역의 구조적 특징(도로, 상업시설 밀집 등)을 통해 위치를 빠르게 특정할 수 있다.
- OSINT 문제에서는 단서가 설명문에 직접적으로 포함되는 경우도 많다는 점을 확인하였다.