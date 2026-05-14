---
ctf_name: "Dreamhack"
challenge_name: "session-basic"
category: "web"
difficulty: "easy"
author: "sihyunkimm"
date: "2026-05-05"
points: 14
tags: [session]
---

# session-basic

## 문제 설명

쿠키와 세션으로 인증 상태를 관리하는 간단한 로그인 서비스입니다.
admin 계정으로 로그인에 성공하면 플래그를 획득할 수 있습니다.
서비스 파일과 서버가 주어집니다.

## 풀이

### 분석

코드를 보면 `session_storage` 딕셔너리에 세션ID -> username 를 보관함. 서버 시작 시 임의의 세션ID를 생성해 `admin` 계정으로 미리 넣어두고 있음:

```python
session_storage[os.urandom(32).hex()] = 'admin'
```

또한 `/admin` 라우트는 인증이 주석처리되어 있어 `session_storage` 전체를 반환함.

### 취약점

- 민감한 세션 정보를 인증 없이 전부 노출하는 정보유출(정보공개) 취약점
- 공격자는 노출된 `admin`의 세션 ID를 브라우저 쿠키에 설정해 세션 탈취로 인증을 우회할 수 있음

### 익스플로잇

1. `/admin` 경로에 접속해 출력된 `session_storage`에서 `admin`에 대응하는 세션 ID를 확인한다.

2. 브라우저에서 쿠키 이름 `sessionid`에 해당 세션 ID 값을 넣는다.
   - 개발자 도구 → Application → Cookies 에서 직접 추가한 뒤 접속

3. 루트(`/`) 페이지에 접속하면 `admin`으로 인식되어 플래그가 노출된다.

```text
Hello admin, flag is DH{REDACTED}
```

## 플래그

DH{REDACTED}

## 배운 점

- TODO를 잊지 말아야 함. 특히 인증 관련이라면.
