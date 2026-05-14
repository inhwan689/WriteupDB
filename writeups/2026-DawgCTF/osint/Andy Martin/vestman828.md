---
ctf_name: "2026-DawgCTF"
challenge_name: "Andy Martin"
category: "osint"
difficulty: "medium"
author: "vestman828"
date: "2026-04-12"
tags: [osint]
---

# Andy Martin

## 문제 설명

> 2026-DawgCTF에 Andy Martin 문제입니다. Osint입니다.

## 풀이

### 분석

https://thedisplacednation.com/2013/01/30/random-nomad-andy-martin-uk-qualified-social-worker-football-geek-now-a-sao-paulo-resident/
이런 인터뷰를 찾게 되었고, 여기에서
@andyhpmartin 라는 핸들을 얻었다.

즉, 우리가 찾는 Andy Martin은
이름: Andy Martin
기사 제목: “RANDOM NOMAD: Andy Martin, UK-qualified Social Worker, Football Geek & Now a São Paulo Resident”
게시일: 2013-01-30
영국 출신
사회복지사
축구광
당시 거주지 São Paulo
라는 프로필을 가진 사람일 것으로 추측했습니다.

이 사람의 Flickr 프로필도 존재함을 확인했습니다:
Flickr 프로필: About andy martin
Flickr ID: 53651949@N05
값:
Occupation: social worker
Hometown: london
Current city: são paulo
Country: brazil
Website: thebookisonthetable.me


그리고 결정적으로
"andyhpmartin" London
"andyhpmartin" Sutton
"andyhpmartin" Croydon
이런 식의 검색을 해보기 시작했는데

localguides-ranking.com의 Andy Martin 페이지에 다음 값이 나옵니다.
페이지 제목: Andy Martin - Rank 86 on Google Local Guides Ranking
링크 텍스트: Google Maps profile
값:
Points: 124,874
Reviews: 188
Photos: 17,970
Videos: 476
Places added: 52

그리고 그 페이지의 Google Maps profile 링크를 실제로 따라가면,
https://www.google.com/maps/contrib/101832575045909613341/

구글 리뷰 기여자 프로필이 나옵니다.

여기서 7년전 리뷰까지만 나오는데,
7년 전이면 아슬아슬하게 2018-7-12 범위이기에 일단 한 번 살펴보았습니다.

구글맵 앱으로 보았더니 런던(Andy Martin의 출신지(=hometown))만 골라서 볼 수 있었고,
그 중 맨 아래에 있던 장소부터 천천히 식당으로 보이는 곳만 시도해보았는데,
2번째 식당이 플래그 였습니다.

### 익스플로잇

```python
(사용한 익스플로잇 없음)
```

## 플래그

```
Poppies Fish & Chips
```

## 배운 점

-
