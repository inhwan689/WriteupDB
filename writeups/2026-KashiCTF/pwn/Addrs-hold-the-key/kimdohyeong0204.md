---
ctf_name: "KashiCTF"
challenge_name: "Addrs-hold-the-key"
category: "pwn"           
difficulty: "easy"      
author: "kimdohyeong0204"
date: "2026-04-03"
points: 100
tags: [태그1, 태그2]
---

# 문제명
Addrs-hold-the-key
## 문제 설명

> Do you even know what ret is?

https://kashictf.iitbhucybersec.in/challenges#Addrs%20hold%20the%20key-14

## 풀이
문제에 주어진 호스트 주소로 접속
이후 2 14 4198857 15 0 을 입력하면 flag가 출력된다.
### 분석

문제를 분석한 내용을 작성합니다.
문제에 주어진 호스트 주소로 접속하니 몇가지를 입력하게 시켰다. 그리고 strings vuln 명령어를 실행하니 print_flag 함수가 있는 것을 확인하였다. 이를 통해 입력칸을 적절히 입력하여 리턴 주소에 print_flag 함수의 주소를 넣으면 함수가 실행될 것이라고 생각했다.
### 취약점

발견한 취약점을 설명합니다.
인덱스를 0~9로 입력하라고 했지만 이를 검증하지 않는다. arr은 스택에 있는데 스택에는 리턴 주소도 있기 때문에 print_flag 주소를 넣을 수 있다.
### 익스플로잇

풀이 과정을 단계별로 작성합니다.
1. strings vuln 명령어로 print_flag 함수가 있음을 확인

2. objdump -d vuln > vuln.asm 명령어로 arr의 위치와 print_flag의 위치를 확인
배열의 주소, print_flag의 주소를 확인하고 return 주소에 print_flag주소로 덮어쓴다.



```python
# 풀이 코드 예시
```

## 플래그

```
kashiCTF{made_u_return_lol_nnkVVug8GX}}
```

## 배운 점

이 문제를 통해 배운 내용을 정리합니다.
pwn 문제의 초반 접근 방법에 대해서 배울 수 있었다. 어셈블리어에 나와있는 주소값들을 이용하여 문제를 풀어 메모리에 대한 지식을 늘릴 수 있었다.

