---
ctf_name: "Dreamhack"
challenge_name: "csrf-2"
category: "web"           # web / pwn / rev / crypto / misc
difficulty: "easy"      # easy / medium / hard / insane
author: "penguink-hub"
date: "2026-05-12"
points: 0
tags: [web,csrf,xss]
---

# 문제명

## 문제 설명

> 여러 기능과 입력받은 URL을 확인하는 봇이 구현된 서비스입니다. CSRF 취약점을 이용해 플래그를 획득하세요.


## 풀이

### 분석

웹 서비스는 로그인, 비밀번호 변경, XSS 테스트용 /vuln 엔드포인트, 그리고 관리자 봇을 통한 CSRF 확인 기능을 제공합니다. 플래그는 admin 계정의 비밀번호로 저장되어 있으며, admin으로 로그인하면 메인 페이지에서 플래그를 확인할 수 있습니다.
주요 엔드포인트는 다음과 같습니다.
/flag (POST): param을 입력받아 관리자 봇이 admin 세션 쿠키를 가지고 /vuln?param=입력값 에 접속합니다.
/vuln (GET): param을 HTML로 그대로 반환하되 frame, script, on 문자열을 필터링합니다.
/change_password (GET): 현재 세션의 사용자 비밀번호를 pw 파라미터 값으로 변경합니다.

### 취약점

이 문제는 XSS와 CSRF 취약점을 연계하여 admin 비밀번호를 변경하는 문제입니다. /vuln은 param을 HTML로 그대로 렌더링하므로 태그 삽입이 가능하고, /change_password는 GET 요청만으로 비밀번호를 변경할 수 있어 CSRF에 취약합니다. 관리자 봇이 admin 세션 쿠키를 가진 채로 /vuln에 접속하므로, img 태그의 src로 /change_password를 지정하면 봇의 쿠키와 함께 GET 요청이 발생하여 admin 비밀번호가 변경됩니다.
필터는 frame, script, on을 차단하지만 img 태그는 차단하지 않으므로 필터를 우회할 수 있습니다.

### 익스플로잇

목표는 관리자 봇을 이용해 admin 비밀번호를 변경한 뒤 로그인하여 플래그를 획득하는 것입니다.

/flag 페이지에 접속합니다.
param 입력란에 아래 payload를 입력하고 제출합니다.
good 알림이 뜨면 봇이 /change_password에 접근하여 admin 비밀번호가 변경된 것입니다.
/login 페이지에서 admin / hacked123으로 로그인합니다.
메인 페이지에서 플래그를 확인합니다.


## 플래그

```
DH{REDACTED}
```

## 배운 점

XSS 필터가 적용되어 있어도 script나 on 이벤트 핸들러 외에 img 태그처럼 GET 요청을 유발하는 다른 방법이 존재한다는 것을 배웠다. 또한 상태를 변경하는 엔드포인트가 GET 방식으로 구현되어 있으면 CSRF에 취약하며, 관리자 봇의 세션 쿠키를 이용해 XSS와 CSRF를 연계하면 권한 상승까지 이어질 수 있다는 것을 배웠다.


