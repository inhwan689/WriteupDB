---
ctf_name: "2026-VishwaCTF"
challenge_name: "Where in the City?"
category: "osint"
difficulty: "medium"
author: "vestman828"
date: "2026-04-05"
tags: [osint]
---

# Where in the City?

## 문제 설명

> 2026-VishwaCTF에 출제된 Where in the City? 문제입니다. Osint입니다.

## 풀이

### 분석

multi-stage city cycling event, the first stage involved racing against the clock라는 문제 설명을 통해
https://punegrandtour.in/prologue-goodluck-chowk-deccan-gymkhana-deccan-bus-stop/
위 링크를 찾게 되었고, 해당 대회가 Pune Grand Tour 2026임을 알 수 있습니다.

https://indianexpress.com/article/cities/pune/traffic-changes-in-place-for-prologue-of-pune-grand-tour-2026-cycling-race-10479751
에 따르면 Khandoji Baba chowk가 별도 폐쇄 구간으로 명시돼 있고.
구글맵에 Khandoji Baba chowk를 검색, challenge.jpeg와 같은 것을 로드뷰로 확인했습니다.


### 익스플로잇

```python
(열심히 구글링 하기)
```

## 플래그

```
VishwaCTF{khanduji_baba}
```

## 배운 점

Weight 40아래인 Bad CTF는 거르자
