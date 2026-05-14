---
ctf_name: "2026-DawgCTF"
challenge_name: "owo?"
category: "osint"
difficulty: "medium"
author: "vestman828"
date: "2026-04-12"
tags: [osint]
---

# Andy Martin

## 문제 설명

> 2026-DawgCTF에 owo? 문제입니다. Osint입니다.

## 풀이

### 분석

지형과 사진 속 닭 구조물에 'wv'같은 문구가 보이는 것 같아서,
wv = west virginia 일 것으로 추측했습니다.

그리고 나서 피자헛 위치들을 모아놓은 공식 사이트를 통해 조사해보기 시작했습니다.

https://locations.pizzahut.com/wv/petersburg/444-virginia-ave
444 Virginia Ave, Petersburg, WV 26847

근처를 구글 로드뷰로 살펴보면 사진 속 닭 구조물과, 피자헛을 확인할 수 있습니다.

따라서 Zip Code는 26847입니다.

### 익스플로잇

```python
(사용한 익스플로잇 없음)
```

## 플래그

```
26847
```

## 배운 점

-
