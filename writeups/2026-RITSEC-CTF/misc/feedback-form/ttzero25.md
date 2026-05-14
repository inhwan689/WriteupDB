---
ctf_name: "RITSEC CTF"
challenge_name: "feedback form"
category: "misc"
difficulty: "easy"
author: "ttzero25"
date: "2026-04-05"
---

# 문제명
feedback form

## 문제 설명
문제와 함께 구글폼 url이 제공됨

## 풀이
주어진 구글폼 url에 들어가면, username/team token과 각 분야별 관심도, 대회를 알게된 경로 등에 대해 필수응답/선택응답인 문항들이 나옴
해당 필수 응답들에 대해 답하고 제출하기를 누르면 설문에 응답해줘서 고맙다는 메시지와 함께 RS{...} 양식의 flag가 나옴

## 플래그
![flag](images/flag.png)
```
flag{REDACTED}
```

## 배운 점
구글폼 양식 문제는 처음 마주쳤는데 오래 시간 끌지말고 필수 응답만 빠르게 답하고 넘어갈 것
