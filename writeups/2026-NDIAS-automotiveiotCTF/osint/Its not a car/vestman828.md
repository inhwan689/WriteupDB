---
ctf_name: "2026-NDIAS-automotiveiotCTF"
challenge_name: "It’s not a car."
category: "osint"
difficulty: "medium"
author: "vestman828"
date: "2026-05-15"
tags: [osint]
---

# It’s not a car.

## 문제 설명

> 2026-NDIAS-automotiveiotCTF에 It’s not a car. 문제입니다. Osint입니다.

## 풀이

### 분석

https://www.google.com/maps/place/3000+S+Las+Vegas+Blvd,+Las+Vegas,+NV+89109/@36.1342942,-115.1679381,17z/data=!3m1!4b1!4m6!3m5!1s0x80c8c4129cd25bcf:0x9ecb1120f7ec353!8m2!3d36.1346099!4d-115.1654787!16s%2Fg%2F11c37_dwkp?hl=en&entry=ttu&g_ep=EgoyMDI2MDUxMi4wIKXMDSoASAFQAw%3D%3D

https://www.rwlasvegas.com/location-directions/
에서

https://maps.google.com/?cid=715141131972559699&g_mp=CiVnb29nbGUubWFwcy5wbGFjZXMudjEuUGxhY2VzLkdldFBsYWNlEAMYASAF&hl=en&gl=US&source=embed,

https://www.google.com/maps/place/3000+S+Las+Vegas+Blvd,+Las+Vegas,+NV+89109/@36.1342942,-115.1679381,17z/data=!3m1!4b1!4m6!3m5!1s0x80c8c4129cd25bcf:0x9ecb1120f7ec353!8m2!3d36.1346099!4d-115.1654787!16s%2Fg%2F11c37_dwkp?hl=en&entry=ttu&g_ep=EgoyMDI2MDUxMy4wIKXMDSoASAFQAw%3D%3D

로 리다이렉팅 할 수 있는데,
파라미터에 좌표(@36.1342942,-115.1679381,17z)가 있다.

### 익스플로잇

```python
-
```

## 플래그

```
FLAG{36.134_-115.167}
```

## 배운 점

-
