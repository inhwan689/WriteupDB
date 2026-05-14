---
ctf_name: "picoctf"
challenge_name: "Old-Sessions"
category: "web"           # web / pwn / rev / crypto / misc
difficulty: "easy"      # easy / medium / hard / insane
author: "underconnor"
date: "2026-04-12"
points: 0
tags: [web]
---

# Old Sessions

## 문제 설명

> Proper session timeout controls are critical for securing user accounts. If a user logs in on a public or shared computer but doesn’t explicitly log out (instead simply closing the browser tab), and session expiration dates are misconfigured, the session may remain active indefinitely.
This then allows an attacker using the same browser later to access the user’s account without needing credentials, exploiting the fact that sessions never expire and remain authenticated.
Additional details will be available after launching your challenge instance.

- https://play.picoctf.org/practice/challenge/739?originalEvent=79&page=1
## 풀이

### 분석

간단한 로그인 및 회원가입 페이지가 존재하고, 계정을 생성 후 로그인을 하면 set-cookie를 통해 세션 데이터가 쿠키로 들어온다는 점을 확인함

### 취약점

/sessions 페이지에 세션 데이터를 저장하고 있어 해당 페이지에 방문해서 어드민 세션을 확보할 수 있다.

### 익스플로잇

일반 유저 권한 계정을 생성하여 영구적인 세션 토큰이 발급된다는 점을 확인하고, /sessions 에서 얻은 어드민 세션 정보로 쿠키를 바꿔 접속하여 flag획득 

```js
# 풀이 코드 예시
```

## 플래그

```
picoCTF{s3t_s3ss10n_3xp1rat10n5_77b6684a}
```

## 배운 점

항상 세션은 유효기간을 두어야 한다는 점과, 세션 정보를 안전하게 보관해야 한다는 점을 배웠다.