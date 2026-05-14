---
ctf_name: "RITSEC-CTF-2026"
challenge_name: "Pork-Lubber"
category: "misc"           # web / pwn / rev / crypto / misc
difficulty: "easy"      # easy / medium / hard / insane
author: "ssong17"
date: "2026-04-05"
points: 10
tags: [IPinfo]
---

# 문제명
Pork Lubber

## 문제 설명
Arrr! In what U.S. state be the land-lubber who be given the subnet that includes the address 44.30.122.69, as be known by the crown's reckonin'?

Respond with: RS{two-letter state abbreviation}

You only have 5 attempts to solve this challenge!

- 문제 URL / 파일 등 접속 정보: 대상 IP 44.30.122.69

## 풀이


### 분석
44.30.122.69라는 IP 주소가 포함된 서브넷이 미국의 어느 State에 할당되어 있는지 알아내는 문제. 정답 형식은 해당 주의 2자리 약어를 사용하여 RS{} 포맷으로 제출해야 한다.


### 취약점 

취약점은 아니긴 한데,,, 공개된 IP 정보 데이터베이스를 조회하면 특정 IP 주소의 할당 국가 및 지역 정보를 쉽게 파악할 수 있다.

### 익스플로잇

1. IP 주소의 지리적 위치를 조회할 수 있는 사이트에 접속 (https://ipinfo.io/countries/us)
2. 대상 IP인 44.30.122.69 검색
3. 검색 결과, 해당 IP가 미국 Virginia State에 속해있다는 것을 알 수 있다.
4. Virginia State의 2자리 약어는 VA이다.

## 플래그

```
RS{VA}
```

## 배운 점

특정 IP 주소가 물리적으로 어느 지역(주)에 할당되어 있는지 추적하고 확인하는 방법을 배웠다.
