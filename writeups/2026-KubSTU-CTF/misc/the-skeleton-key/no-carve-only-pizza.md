---
ctf_name: KubSTU CTF 2026
challenge_name: The skeleton key
category: misc
difficulty: medium
author: no-carve-only-pizza
date: 2026-05-02
points: 871
tags: [Packet Tracer, Cisco IOS, network, switch]
---

# The skeleton key

## TL;DR

Packet Tracer 파일 안의 네트워크 장비 설정을 확인해 보니 핵심 장비는 `CORE_ROOT` 멀티레이어 스위치였다. 배너에 숨겨진 Base64 문자열을 decode하면 enable password가 나오고, 관리자 권한으로 들어간 뒤 장애 인터페이스인 `FastEthernet0/15`를 shutdown하면 된다.

```text
KubSTU(gazebo_is_stronger_than_tarask)
```

## 분석

문제 설명에서 "스위치 포트에서 오류가 계속 발생한다", "권한 레벨 때문에 들어갈 수 없다", "설정을 밀지 말라"는 내용이 있었다. 그래서 전체 설정 초기화가 아니라 현재 설정을 유지한 채로 문제 포트를 찾아 조치하는 문제라고 판단했다.

`.pkt` 파일을 XML로 복호화한 뒤 장비 목록을 확인했다. 그중 핵심 장비는 다음 스위치였다.

```text
hostname CORE_ROOT
```

설정 안에는 enable secret이 걸려 있었다.

```text
enable secret 5 $1$mERr$sFd10v6X4h2wrH5ktVhK91
username admin privilege 15 secret 5 $1$mERr$sFd10v6X4h2wrH5ktVhK91
```

직접 비밀번호가 보이지는 않지만, MOTD banner에 힌트가 있었다.

```text
SESSION_ENCRYPTION_SALT [V.2]:
ZDIwX1NhbHRvTmF6YWQ=

HINT: The salt is the key to your elevation.
```

Base64 decode를 하면 다음 문자열이 나온다.

```text
d20_SaltoNazad
```

이 값으로 MD5-crypt를 확인하면 설정에 있던 enable secret 해시와 일치한다.

```bash
openssl passwd -1 -salt mERr d20_SaltoNazad
```

결과:

```text
$1$mERr$sFd10v6X4h2wrH5ktVhK91
```

따라서 enable password는 `d20_SaltoNazad`이다.

## 문제 포트

관리자 권한으로 설정을 확인하면 `FastEthernet0/15`에 수상한 description이 걸려 있었다.

```text
interface FastEthernet0/15
 description "SECRET_PROJECT_FLAG_INSIDE: KubSTU(gazebo_is_stronger_than_tarask)"
 shutdown
```

문제 설명의 "오류가 계속 쌓이는 포트"와 명령 로그를 종합하면 장애 포트는 `FastEthernet0/15`이고, 이 포트를 비활성화하는 것이 의도된 해결이었다.

## 해결 명령

Packet Tracer에서 다음처럼 처리하면 된다.

```text
enable
d20_SaltoNazad
configure terminal
interface fa0/15
shutdown
end
write memory
```

## 배운 점

이 문제는 단순히 플래그 문자열을 찾는 것보다, 장비 설정 안의 힌트를 이용해 권한을 올리고, 실제 장애 포트를 찾아 네트워크 경고를 멈추는 흐름이 중요했다.

`shutdown`은 포트를 끄는 명령이다. 고장난 포트나 잘못 연결된 포트가 계속 문제를 만들 때, 전체 설정을 삭제하지 않고 해당 포트만 조치할 수 있다.
