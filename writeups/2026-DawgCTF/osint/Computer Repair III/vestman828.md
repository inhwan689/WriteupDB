---
ctf_name: "2026-DawgCTF"
challenge_name: "Computer Repair III"
category: "osint"
difficulty: "medium"
author: "vestman828"
date: "2026-04-12"
tags: [osint]
---

# Andy Martin

## 문제 설명

> 2026-DawgCTF에 Computer Repair III 문제입니다. Osint입니다.

## 풀이

### 분석

사진에서 육안으로 식별 가능한 주요 부품은 다음과 같습니다.

블로워 냉각팬: 우측 대형 팬. WD19 계열에서 발열이 큰 USB/DP/PD 허브 쪽을 식히는 용도입니다. 팬 표기 DC28000NZD0, 관련 Dell 부품번호로 0C96VF가 유통됩니다.
RJ-45 이더넷 포트: 후면 LAN 포트. WD19S/WD19 모두 기가비트 이더넷을 갖습니다.
전면 USB-C 포트: 사진 아래쪽 중앙 좌측. WD19S의 전면 USB 3.2 Gen2 Type-C와 일치합니다.
전면 USB-A 포트: 사진 아래쪽 중앙 우측의 파란 포트. WD19S의 전면 USB-A PowerShare와 일치합니다.
후면 USB-C 포트: 사진 상단 중앙 쪽의 Type-C. WD19S의 후면 USB-C with DisplayPort 포트와 대응됩니다.
후면 USB-A 포트들: 사진 상단 쪽 파란 USB-A. WD19S는 후면 USB-A 2개입니다.
도킹 케이블 모듈 연결용 보드-투-보드 커넥터: 좌측의 긴 검은 커넥터. WD19 계열은 호스트로 가는 USB-C 케이블 모듈이 분리식이며, Dell 문서에도 “USB Type-C cable module” 분리 절차가 따로 있습니다. 사진 구조가 그와 정확히 맞습니다.
좌측 금속 브래킷/슬레드: 본체 하우징 및 케이블 모듈 고정용 섀시 파트로 보입니다. 사진의 스티커에 W1NP2로 읽히는 표기가 보이는데, 이 값으로 중고시장에서는 WD19/WD19S 본체 모듈이 유통됩니다. 다만 이 부분은 공식 Dell 문서보다 비공식 유통 정보에 가깝기 때문에 보조 근거 정도로만 보는 게 맞습니다.
사진 2의 작은 보드: 실크스크린에 LED1, SW2, UL indicator가 보입니다. 즉, 이건 메인 로직보드가 아니라 상태 LED/버튼 보드, 실질적으로는 상판의 Sleep/Wake/Power 버튼 회로 쪽으로 해석하는 게 자연스럽습니다. Dell은 WD19S 상단에 전원 버튼이 있다고 문서에 명시합니다.

그래서 결론을 정리하면,
이 보드는 일반 미니PC나 씬클라이언트가 아니라, Dell WD19 계열 USB-C 도킹 스테이션 내부 메인보드입니다.

따라서 WD19DC 또는 WD19TB입니다.

### 익스플로잇

```python
(사용한 익스플로잇 없음)
```

## 플래그

```
DawgCTF{WD19TB}
```

## 배운 점

-
