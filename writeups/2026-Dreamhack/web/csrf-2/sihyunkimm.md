---
ctf_name: "Dreamhack"
challenge_name: "csrf-2"
category: "web"
difficulty: "easy"
author: "sihyunkimm"
date: "2026-05-12"
points: 14
tags: [csrf, web]
---

# csrf-2

## 문제 설명

> 여러 기능과 입력받은 URL을 확인하는 봇이 구현된 서비스입니다. CSRF 취약점을 이용해 플래그를 획득하세요.

- 접근: Dreamhack VM

## 풀이

### 분석

- `/change_password`는 GET 요청으로 동작하며 CSRF 취약점이 있음  
- 로그인된 사용자가 해당 URL에 접속하기면 비밀번호를 변경할 수 있음  
- `/flag`는 봇을 admin 세션으로 만들어 `param`를 포함한 `/vuln` 페이지를 내부에서 렌더링함  
- `/vuln`의 출력 필터로 인해 `<script>`나 이벤트 핸들러(`on...`)는 사용할 수 없음

### 취약점

- CSRF: 비밀번호 변경이 GET으로 구현되어 있고 CSRF 취약점이 있음
- `frame`, `script`, `on` 문자열이 차단되지만, 자동으로 GET 요청을 발생시키는 태그(ex: 이미지 로드)는 차단되지 않음

### 익스플로잇

`/flag` 페이지에 `param`으로 다음 페이로드를 제출

```html
<img src="/change_password?pw=1234">
```

서버 내부의 봇이 admin 세션으로 `/vuln` 페이지를 열고, `<img>`가 로드되며 `/change_password?pw=1234`에 GET 요청을 보냄
admin 계정의 비밀번호가 `1234`로 변경되어 admin 계정을 1234로 로그인한 뒤 메인 페이지에서 `FLAG` 값을 획득할 수 있음

## 플래그

```
DH{REDACTED}
```

## 배운 점

- GET으로 비밀번호를 변경하는 설계는 CSRF 위험이 있음
- 입력 필터링이 있어도 자동 요청을 유발하는 태그(`<img>` 등)를 통해 우회할 수 있음
