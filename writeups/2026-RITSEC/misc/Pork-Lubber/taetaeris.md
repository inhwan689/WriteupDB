---
ctf_name: "RITSEC"
challenge_name: "Pork Lubber"
category: "misc"           # web / pwn / rev / crypto / misc
difficulty: "easy"      # easy / medium / hard / insane
author: "taetaeris"
date: "2026-04-07"
points: 10
tags: [OSINT,IP-Lookup]
---

# 문제명
Pork Lubber

## 문제 설명

> 문제에서 주어진 설명을 여기에 작성합니다.
Arrr! In what U.S. state be the land-lubber who be given the subnet that includes the address 44.30.122.69, as be known by the crown's reckonin'?

Respond with: RS{two-letter state abbreviation}

You only have 5 attempts to solve this challenge!

- 문제 URL / 파일 등 접속 정보

## 풀이

### 분석
문제에서 주어진 IP 주소 44.30.122.69는 일반적인 상업용 대역과는 조금 다른 특성을 가지고 있습니다. 44.0.0.0/8 대역은 전 세계 아마추어 무선 패킷 라디오 네트워크인 AMPRNet(44Net)에 할당된 대역입니다.

### 취약점
이 문제는 특정 시스템의 취약점을 공격하는 것이 아니라, 공개된 네트워크 할당 정보를 정확히 추적하는 OSINT 기술을 요구합니다.
1. ARIN Whois 조회: 북미 지역 IP 할당 기관인 ARIN에서 해당 IP의 소윶와 서브넷 범위를 확인합니다.
2. AMPRNet Portal: 44Net은 독자적인 관리 체계를 가지고 있으므로, 세부 서브넷의 지역 조정자 정보를 확인해야 합니다.


### 익스플로잇
1. Whois 레코드 확인
ARIN Whois를 통해 44.30.122.69를 검색하면 다음과 같은 정보를 얻을 수 있습니다.
-NetRange: 44.30.122.0 - 44.30.122.255
-Organization: Deteque(AMPRNet 관련 인프라 제공)
-Location: 이 서브넷은 버지니아주에 위치한 데이터 센터 인프라와 연결되어 할당되어 있습니다.
2. 데이터 교차 검증
AMPRNet의 게이트웨이 및 서브넷 할당 리스트를 확인하면, 해당 대역은 Virginia 지역의 아마추어 무선 통신 및 테스트를 위해 할당된 주소임을 알 수 있습니다.
3. 약어 추출
버지니아주의 2글자 약어는 VA입니다.

```python
# 풀이 코드 예시
```


## 플래그

```
RS{VA}
```

## 배운 점
- 특수 IP 대역의 이해: 44.0.0./8 대역이 아마추어 무선용이라는 특수한 목적을 가지고 있음을 알게 되었습니다.
- OSINT 정보의 정확성: IP 지오로케이션 서비스마다 결과가 미세하게 다를 수 있으나, 'Crown's reckonin(정부/기관의 기록)'이라는 힌트를 통해 공신력 있는 Whois 레코드(ARIN)를 신뢰하는 것이 중요하다는 점을 배웠습니다.
