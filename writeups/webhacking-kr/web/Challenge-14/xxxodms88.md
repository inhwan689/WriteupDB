---
title: "Challenge 14"
ctf_name: "webhacking.kr"
challenge_name: "Challenge-14"
category: "web"
difficulty: "easy"
author: "xxxodms88"
date: "2026-04-14"
solved: true
tags:
  - javascript
  - client-side
---

# Challenge 14

## 문제 개요

webhacking.kr의 Challenge 14번 문제.
입력창에 올바른 패스워드를 입력하면 통과하는 클라이언트 사이드 JavaScript 문제.

## 풀이

### 소스코드 분석

페이지 소스(`Ctrl+U`)를 확인하면 JavaScript 로직이 노출되어 있다.

```javascript
var ul = document.URL;
ul = ul.indexOf(".kr");
ul = ul * 30;
if(ul == pw.input_pwd.value) {
    alert("Password is " + ul * pw.input_pwd.value);
} else {
    alert("Wrong");
}
```

### 계산

1. `document.URL` = `webhacking.kr/challenge/javascript/js1.html`
2. `.kr`의 위치: `indexOf(".kr")` = **17**
3. `ul = 17 * 30 = 510`
4. 입력값으로 `510` 입력 시 조건 통과
5. alert 출력: `510 * 510 = 260100`

### 개발자 도구로 확인

Console에서 직접 계산 결과 `510` 확인.

## 플래그

```
260100
```