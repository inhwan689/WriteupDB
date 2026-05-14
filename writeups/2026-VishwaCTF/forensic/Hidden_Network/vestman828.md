---
ctf_name: "2026-VishwaCTF"
challenge_name: "Hidden_Network"
category: "forensic"
difficulty: "medium"
author: "vestman828"
date: "2026-04-05"
tags: [PCAP]
---

# Hidden_Network

## 문제 설명

> 2026-VishwaCTF에 Hidden_Network 문제입니다. Forensic입니다.

## 풀이

### 분석

pcap 안의 HTTP 응답 본문 앞부분에 U+200B(zero-width space)와 U+200C(zero-width non-joiner)가 섞여 있었고, 이를 비트열로 해석하면 ASCII 문자열로 복원됩니다.
매핑은 다음과 같았습니다.

U+200B → 0
U+200C → 1

### 익스플로잇

```python
(삭제해버려서 첨부하지 못했습니다..)
```

## 플래그

```
VishwaCTF{H1DDN3TWRKK}
```

## 배운 점

Weight 40아래인 Bad CTF는 거르자
