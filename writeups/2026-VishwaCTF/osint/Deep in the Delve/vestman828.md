---
ctf_name: "2026-VishwaCTF"
challenge_name: "Deep in the Delve"
category: "osint"
difficulty: "medium"
author: "vestman828"
date: "2026-04-05"
tags: [osint]
---

# Deep in the Delve

## 문제 설명

> 2026-VishwaCTF에 The Deep in the Delve 문제입니다. Osint입니다.

## 풀이

### 분석

https://techcrunch.com/2026/03/22/delve-accused-of-misleading-customers-with-fake-compliance
에서 해당 스타트업 기업을 알 수 있습니다.
```
An anonymous Substack post published this week accuses compliance startup Delve of “falsely” convincing “hundreds of customers they were compliant” with privacy and security regulations, ....
```
https://deepdelver.substack.com/p/delve-fake-compliance-as-a-service
그리고 substack 핸들은 이를 통해 deepdelver임도 알았습니다.
거기에 더해,
```
5.11 Signs of who was involved - Selin Kocalar’s involvement
One of the entries has sskocalar@gmail.com as the company contact email.
```
을 통해 Selin Kocalar의 이메일도 획득합니다.

### 익스플로잇

```python
(열심히 구글링 하기)
```

## 플래그

```
VishwaCTF{Delve_deepdelver_sskocalar@gmail.com}
```

## 배운 점

Weight 40아래인 Bad CTF는 거르자
