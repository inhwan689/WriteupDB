---
ctf_name: "WarGame"
challenge_name: "welcome"
category: "pwn"           # web / pwn / rev / crypto / misc
difficulty: "easy"      # easy / medium / hard / insane
author: "kimdohyeong0204"
date: "2026-05-05"
points: 0
tags: [pwnable]
---

# 문제명
welcome
## 문제 설명

> 문제에서 주어진 설명을 여기에 작성합니다.
이 문제는 서버에서 작동하고 있는 서비스(welcome)의 바이너리와 소스 코드가 주어집니다.
"접속 정보 보기"를 눌러 서비스 정보를 얻은 후 플래그를 획득하세요.
서버로부터 얻은 플래그의 내용을 워게임 사이트에 인증하면 점수를 획득할 수 있습니다.
플래그의 형식은 DH{...} 입니다.
- 문제 URL / 파일 등 접속 정보
https://dreamhack.io/wargame/challenges/27
## 풀이
VM 접속하기로 서버를 생성후 리눅스에서 해당 서버로 접속시 flag 출력
### 분석

특별히 분석할 내용 x

### 취약점

특별한 취약점 x

### 익스플로잇

주어진 호스트 주소로 접속 후 플래그 출력

```python
# 풀이 코드 예시
```

## 플래그

```
DH{5cc72596cba7104569abb37f71b8ccf3}
```

## 배운 점

이번 주차는 시험 기간이 늦게 끝난 관계로 쉬운 ctf문제를 진행했습니다. 
