---
ctf_name: KubSTU CTF 2026
challenge_name: Nut legends
category: misc
difficulty: medium
author: no-carve-only-pizza
date: 2026-05-02
points: 852
tags: [Packet Tracer, Cisco IOS, VLAN, web]
---

# Nut legends

## TL;DR

시작 지점은 `COOPER R.` PC이고 목표는 `Server#1` 웹 서버였다. 라우터 설정은 VLAN 10과 VLAN 20을 라우팅할 준비가 되어 있었지만, 서버가 스위치의 잘못된 access port에 연결되어 있어서 VLAN 20에 들어가지 못하고 있었다. 서버 포트를 VLAN 20으로 고치면 웹 페이지에 접근할 수 있고, `copyrights.html` 안에서 flag를 찾을 수 있다.

```text
kubstu(end_user_license_agreement)
```

## 네트워크 구성

복호화한 Packet Tracer XML에서 장비는 다음처럼 구성되어 있었다.

```text
COOPER R. PC
Switch0
Mastif_0828 Router
Server#1
```

PC와 서버의 IP는 다음과 같다.

```text
COOPER R.
IP:      10.10.10.10
Gateway: 10.10.10.1
VLAN:    10

Server#1
IP:      10.20.20.100
Gateway: 10.20.20.1
VLAN:    20
```

라우터 `Mastif_0828`에는 router-on-a-stick 구성이 되어 있었다.

```text
interface GigabitEthernet0/0.10
 encapsulation dot1Q 10
 ip address 10.10.10.1 255.255.255.0

interface GigabitEthernet0/0.20
 encapsulation dot1Q 20
 ip address 10.20.20.1 255.255.255.0
```

즉 VLAN 10과 VLAN 20 사이의 라우팅은 라우터가 담당한다.

## 문제 원인

스위치 설정을 보면 VLAN 포트는 이렇게 잡혀 있었다.

```text
interface FastEthernet0/1
 switchport access vlan 10
 switchport mode access

interface FastEthernet0/2
 switchport access vlan 20
 switchport mode access

interface FastEthernet0/24
 switchport mode trunk
```

`Fa0/1`은 PC용 VLAN 10, `Fa0/2`는 서버용 VLAN 20, `Fa0/24`는 라우터로 가는 trunk 포트로 보인다.

하지만 실제 케이블 연결은 다음과 같았다.

```text
COOPER R. FastEthernet0   <-> Switch0 FastEthernet0/1
Router GigabitEthernet0/0 <-> Switch0 FastEthernet0/24
Server#1 FastEthernet0    <-> Switch0 FastEthernet0/7
```

서버가 `Fa0/7`에 꽂혀 있는데, `Fa0/7`에는 VLAN 20 설정이 없다. 그래서 서버는 `10.20.20.100`을 가지고 있어도 실제 스위치 레벨에서 VLAN 20 네트워크에 제대로 속하지 못했다.

문제 설명의 "여러 OSI 계층에서 막혀 있다"는 말은 여기서 맞아떨어진다. IP 설정만 맞아도, 스위치 VLAN이 틀리면 통신이 되지 않는다.

## 해결

해결 방법은 두 가지다.

첫 번째 방법은 서버 케이블을 `Fa0/7`에서 `Fa0/2`로 옮기는 것이다. `Fa0/2`는 이미 VLAN 20 access port로 설정되어 있다.

두 번째 방법은 현재 서버가 꽂힌 `Fa0/7`을 VLAN 20 access port로 바꾸는 것이다.

```text
enable
configure terminal
interface fa0/7
switchport mode access
switchport access vlan 20
end
write memory
```

이후 `COOPER R.`에서 다음 주소로 접속할 수 있다.

```text
http://10.20.20.100/
```

## 웹 힌트

서버의 `index.html`에는 다음 힌트가 있었다.

```text
[ TARGET: STORAGE_SERVER_VLAN20 ]

NOTICE:
The key is archived in 'copyrights'.
Search the legal directory.
```

따라서 `copyrights.html`을 확인한다.

```text
http://10.20.20.100/copyrights.html
```

그 안의 Cisco 라이선스 문구처럼 보이는 URL 중간에 flag가 숨어 있었다.

```text
https://www.cisco.com/c/en/us/about/legal/cloud-and-software/kubstu(end_user_license_agreement)
```

## 이미지 파일

문제 설명에서는 이미지 파일을 강조했고, 서버에는 `cscoptlogo177x111.jpg`가 있었다. 이 이미지는 웹 서버 접근 경로를 유도하는 아티팩트였고, 최종 문자열은 이미지 내부가 아니라 `copyrights.html` 안에 있었다.

## 배운 점

이 문제의 핵심은 IP 주소만 보는 것이 아니라, 스위치의 VLAN 설정과 실제 케이블 연결을 같이 확인하는 것이다.

같은 스위치에 꽂혀 있어도 access VLAN이 다르면 서로 다른 네트워크에 있는 것처럼 동작한다. 그래서 서버 IP와 gateway가 맞아도, 서버가 잘못된 VLAN 포트에 연결되어 있으면 통신이 실패한다.
