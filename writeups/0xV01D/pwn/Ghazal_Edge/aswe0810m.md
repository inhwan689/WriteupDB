---
ctf_name: "0xV01D"
challenge_name: "Ghazal_Edge"
category: "pwn"           # web / pwn / rev / crypto / misc
difficulty: "easy"      # easy / medium / hard / insane
author: "aswe0810m"
date: "2026-05-19"
points: 10
tags: [Partial Overwrite, SBO]
---

# 문제명

## 문제 설명

- A compact service accepts one record and then leaves through a narrow exit path. The public binary is the contract.

- 문제 URL / 파일 등 접속 정보
- nc 34.62.69.250 41051
## 풀이

### 분석

문제에서 제공된 파일들을 살펴보면 라이브러리 파일들과 no_eyes라는 파일이 존재하였다. 파일을 실행해보면 Welcome 이라는 문자열이 출력되고 Input: 으로 입력을 받았다. 만약 입력이 스택 버퍼를 벗어나지 않는다면 Return reaced safely라는 문자열이 출력되는 것으로 보아 스택 버퍼 오버플로우를 활용하는 문제로 보였다. 또한 문제에서 기본적으로 제공한 README_NOTE.txt 파일에는 AI를 속여서 다른 플래그를 출력하게하는 내용이 있었고, crash_notes.txt에는 문제를 어떻게 풀면 좋을지 힌트를 주는 내용이 있었다. cyclic offset이라고 버퍼와 리턴 주소 사이의 거리를 알려주고, recommendation overwrite으로 return주소를 어떤 바이트로 덮어야하는지에 대한 내용이 있었다. 하지만 내용이 완전히 정확하지 않고, 분석해야되는 부분이 있었다.

### 취약점

gdb로 실행파일을 확인해보았을 때 문자열을 입력받는 부분에서 버퍼의 크기는 0x20인데, 0x100만큼 입력을 받는 것을 알 수 있었다. 따라서 스택 버퍼 오버플로우 문제가 발생할 수 있는 취약점이 있고, 파일 자체에 카나리가 없어 쉽게 프로그램 실행 흐름을 조작할 수 있을 것으로 보았다.

### 익스플로잇

처음에 프로그램을 실행하려고 할 때 파일에 실행권한을 주고, 라이브러리에도 실행권한을 주어야 파일을 실행할 수 있었다. 다음으로 gdb로 프로그램을 확인해보았을 때, 그냥 파일의 경우 라이브러리를 현재 주소에서 불러와서 사용하고 있어 바로 gdb로 분석할 수 없었고 patchelf를 통해서 patchelf --set-interpreter $(pwd)/ld-linux-x86-64.so.2 --set-rpath $(pwd) no_eyes_patched 해주어야 gdb가 정상적으로 작동하였다. 파일 자체가 stripped 되어있어 바로 disass main으로 확인할 수 없었고, start 명령으로 __libc_start_main 에 진입하기 전에 rdi에 있는 값으로 main함수의 주소를 알 수 있었다. 이를 통해 main 함수를 x/30i (main 주소)로 디스어셈블 해서 main함수의 동작을 확인 할 수 있었다. 함수의 동작을 보면 init으로 먼저 초기 설정을 한 후, signal로 스택 버퍼 오버플로우가 일어나는지 확인하고 일어난다면 단순히 진입했다가 리턴하는 함수로 들어갔다. 이후 스택에 버퍼를 만들어 입력을 받고 나오는 함수로 들어갔는데, 이때 스택 버퍼 오버플로우를 이용할 수 있었다. 또한 프로그램 내부에 셸코드를 실행하는 함수 자체가 존재하는 것을 ghidra를 통해 확인할 수 있었고, 프로그램 자체에 Full RELRO가 적용되어 있지만, 하위 바이트들은 변하지 않는것을 활용하여 셸코드 내부로 리턴주소를 변경할 수 있었다. 이때 버퍼와 리턴 주소 사이의 거리는 버퍼 크기 0x20, RSP 0x8 해서 0x28만큼의 거리가 있었다.

```python
from pwn import *

p = remote("34.62.69.250", 41051)

payload = b'A'*0x20 + b'B'*0x8 + b'\x2a'

p.sendafter(b"Input: ", payload)

p.interactive()

## 플래그

```
0xV01D{one_byte_pie_overwrite_needs_no_eyes}
```

## 배운 점

파일이 stripped 되어 있다면, 심볼로 바로 main함수에 접근할 수 없고, start를 통해서 main 함수의 주소를 알아내고 들어가야 한다는 점을 알게되었다. Partial Overwrite을 통해서 상위 주소는 모르지만 하위 주소만 변경하는 방법으로 다른 함수에 접근할 수 있다는 것도 알 수 있었다. 또한 ghidra를 활용하여 프로그램을 분석하는 것을 해보았는데, ghidra를 사용하는 방법과 ghidra를 통해서 프로그램을 확인하는 방법을 배울 수 있었다.