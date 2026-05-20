---
ctf_name: "2026-NDIAS-automotiveiotCTF"
challenge_name: "RAMN ECU D"
category: "crypto"
difficulty: "hard"
author: "vestman828"
date: "2026-05-16"
tags: [crypto]
---

# RAMN ECU D

## 문제 설명

> 2026-NDIAS-automotiveiotCTF에 RAMN ECU D 문제입니다. Crypto입니다.

## 풀이

### 분석

`canproxy.py` 프로토콜을 그대로 구현해 TCP로 직접 CAN 프레임을 송수신했다.

초기 확인:

- `3E 00` -> `7E 00` (TesterPresent 정상)
- `10 03` -> `50 03` (Extended Session 진입)
- `22 4E 44` -> `7F 22 33` (보호 DID, 인증 전 접근 거부)

중간 단계에서 확인한 Authentication 응답 특징:

- 만료 인증서 사용 시 `29 01` -> `7F 29 33`
- 인증서의 notAfter만 미래로 바꾼 경우(서명은 깨짐) `29 01` -> `7F 29 35`

즉, `0x33`과 `0x35`는 서로 다른 실패 지점이며, 먼저 시간 검사를 통과해야 다음 단계로 갈 수 있음을 확인했다.

- `0x08004450` 부근: UDS Authentication service 핸들러
- `0x08003BC4` 부근: 실제 0x29 하위 파싱/검증 로직
- `0x080026D8` 부근: LV(length-value) 파서

핸들러에서 인증 성공 시 컨텍스트 상태 바이트를 `2`로 설정한다.

- 인증 상태 저장 바이트: 컨텍스트 `+0x1C`
- 보호 DID `0x4E44`는 이 상태를 검사해 미인증이면 `7F 22 33`을 반환한다.

실제 ECU-D 변형 펌웨어에서 확인한 포맷:

- `29 01 <cfg:1> <LV cert> <LV clientChallenge>`
- `29 03 <LV signature> <LV ephemeralKey>`

여기서 LV는 `uint16_be length + value` 형식이다.

디스어셈블리 상 시간 비교 상수로 `1800000000`(Unix time, 2027-01-15 UTC 근처)이 사용된다.

- leaked cert의 notAfter는 2025-05-12라 만료됨
- 따라서 원본 cert는 시간 검증에서 탈락 (`7F2933`)

펌웨어 내부 `0x0800F118`에 20개 엔트리 신뢰 테이블 존재:

- 회사명 문자열 포인터
- 메타데이터
- 공개키 DER(SPKI) 포인터/길이
- 해시 포인터

즉, 인증서는 결국 이 테이블 내 공급자 키 체인 검증을 통과해야 한다.

신뢰 테이블 RSA 공개키들 간 `gcd(n_i, n_j)`를 계산한 결과,

- Entry 6 (Garnet)와 Entry 15 (Polaris)가 **공통 소수(prime)** 를 공유

이건 RSA 키 생성 치명적 실패다.

두 공개키 모듈러스 `n1, n2`에 대해:

- `p = gcd(n1, n2)`
- `q = n1 / p`
- `phi = (p-1)(q-1)`
- `d = e^{-1} mod phi`

으로 Entry 6의 개인키를 복원 가능.

1. leaked leaf 개인키(문제에서 제공된 `key.pem`)는 계속 사용
2. 복원한 Entry 6 개인키로 새 leaf 인증서를 서명
   - subject public key는 leaked key의 공개키
   - notAfter를 충분히 미래(2032)로 설정
3. `29 01`에 위 forged cert 전송 -> challenge 획득
4. challenge에 대해 leaked key로 서명하여 `29 03` 전송

이 흐름으로 인증 성공 후 DID 접근 가능해진다.

### 익스플로잇

```python
import datetime
import math
import socket
import struct
import sys
import time
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.x509.oid import NameOID

REQ_ID = 0x7E3
RESP_ID = 0x7EB
FW_BASE = 0x08000000
TABLE_BASE = 0x0800F118
ENTRY_SIZE = 0x14

CONTROL_PING = 1
CONTROL_PONG = 2


class ProxyCAN:
    def __init__(self, host: str, port: int):
        self.sock = socket.create_connection((host, port), timeout=5)
        self.sock.settimeout(3)
        self._handshake()

    def _recv_exact(self, n: int) -> bytes:
        out = b""
        while len(out) < n:
            chunk = self.sock.recv(n - len(out))
            if not chunk:
                raise EOFError("TCP closed")
            out += chunk
        return out

    def _send_control(self, value: int) -> None:
        self.sock.sendall(b"\x00\x00" + bytes([value]))

    def _handshake(self) -> None:
        self._send_control(CONTROL_PING)
        deadline = time.time() + 5
        while time.time() < deadline:
            header = self._recv_exact(2)
            length = int.from_bytes(header, "big")
            if length == 0:
                c = self._recv_exact(1)[0]
                if c == CONTROL_PING:
                    self._send_control(CONTROL_PONG)
                elif c == CONTROL_PONG:
                    return
            else:
                _ = self._recv_exact(length)
        raise TimeoutError("Handshake timeout")

    def send_frame(self, can_id: int, data: bytes) -> None:
        frame = struct.pack("<IB3x8s", can_id, len(data), data.ljust(8, b"\x00"))
        self.sock.sendall(len(frame).to_bytes(2, "big") + frame)

    def recv_frame(self, predicate, timeout: float = 3.0):
        end = time.time() + timeout
        while time.time() < end:
            header = self._recv_exact(2)
            length = int.from_bytes(header, "big")
            if length == 0:
                c = self._recv_exact(1)[0]
                if c == CONTROL_PING:
                    self._send_control(CONTROL_PONG)
                continue
            raw = self._recv_exact(length)
            can_id, dlc, data = struct.unpack("<IB3x8s", raw)
            data = data[:dlc]
            if predicate(can_id, data):
                return can_id, data
        raise TimeoutError("CAN receive timeout")

    def close(self) -> None:
        try:
            self.sock.close()
        except OSError:
            pass


class ISO15765:
    def __init__(self, bus: ProxyCAN, txid: int, rxid: int):
        self.bus = bus
        self.txid = txid
        self.rxid = rxid

    def request(self, payload: bytes, timeout: float = 3.0) -> bytes:
        if len(payload) <= 7:
            self.bus.send_frame(self.txid, bytes([len(payload)]) + payload)
        else:
            total = len(payload)
            self.bus.send_frame(self.txid, bytes([0x10 | ((total >> 8) & 0xF), total & 0xFF]) + payload[:6])
            _, fc = self.bus.recv_frame(lambda cid, d: cid == self.rxid and d and (d[0] >> 4) == 0x3, timeout)
            bs = fc[1] if len(fc) > 1 else 0
            st = fc[2] if len(fc) > 2 else 0
            idx = 6
            sn = 1
            sent = 0
            while idx < total:
                chunk = payload[idx : idx + 7]
                self.bus.send_frame(self.txid, bytes([0x20 | (sn & 0xF)]) + chunk)
                idx += len(chunk)
                sn = (sn + 1) & 0xF
                sent += 1
                if st and st <= 0x7F:
                    time.sleep(st / 1000.0)
                if bs and sent >= bs and idx < total:
                    sent = 0
                    _, fc = self.bus.recv_frame(lambda cid, d: cid == self.rxid and d and (d[0] >> 4) == 0x3, timeout)
                    bs = fc[1] if len(fc) > 1 else 0
                    st = fc[2] if len(fc) > 2 else 0

        _, d = self.bus.recv_frame(lambda cid, x: cid == self.rxid and len(x) > 0, timeout)
        ptype = d[0] >> 4
        if ptype == 0:
            return d[1 : 1 + (d[0] & 0xF)]
        if ptype == 1:
            total = ((d[0] & 0xF) << 8) | d[1]
            out = bytearray(d[2:])
            self.bus.send_frame(self.txid, b"\x30\x00\x00")
            while len(out) < total:
                _, cf = self.bus.recv_frame(lambda cid, x: cid == self.rxid and x and (x[0] >> 4) == 0x2, timeout)
                out.extend(cf[1:])
            return bytes(out[:total])
        return d


def hexs(b: bytes) -> str:
    return b.hex().upper()


def table_entry(fw: bytes, index: int):
    off = TABLE_BASE - FW_BASE + index * ENTRY_SIZE
    name_ptr, meta, pkey_ptr, pkey_len, _hash_ptr = struct.unpack_from("<IIIII", fw, off)
    name_end = fw.find(b"\x00", name_ptr - FW_BASE)
    name = fw[name_ptr - FW_BASE : name_end].decode("ascii")
    pkey_der = fw[pkey_ptr - FW_BASE : pkey_ptr - FW_BASE + pkey_len]
    pub = serialization.load_der_public_key(pkey_der)
    if not isinstance(pub, rsa.RSAPublicKey):
        raise ValueError("Selected entry is not RSA")
    n = pub.public_numbers().n
    e = pub.public_numbers().e
    return name, n, e


def recover_shared_prime_key(fw: bytes, idx_a: int, idx_b: int):
    name_a, n_a, e_a = table_entry(fw, idx_a)
    _name_b, n_b, _e_b = table_entry(fw, idx_b)
    g = math.gcd(n_a, n_b)
    if g == 1 or g == n_a or g == n_b:
        raise ValueError("No shared prime found")

    p = g
    q = n_a // p
    phi = (p - 1) * (q - 1)
    d = pow(e_a, -1, phi)

    priv = rsa.RSAPrivateNumbers(
        p=p,
        q=q,
        d=d,
        dmp1=d % (p - 1),
        dmq1=d % (q - 1),
        iqmp=pow(q, -1, p),
        public_numbers=rsa.RSAPublicNumbers(e=e_a, n=n_a),
    ).private_key()
    return name_a, priv


def build_forged_leaf(issuer_name: str, signer_priv, leaked_leaf_priv, leaked_leaf_cert):
    issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, issuer_name),
            x509.NameAttribute(NameOID.COMMON_NAME, "Recovered Supplier Root CA"),
        ]
    )

    builder = (
        x509.CertificateBuilder()
        .subject_name(leaked_leaf_cert.subject)
        .issuer_name(issuer)
        .public_key(leaked_leaf_priv.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc))
        .not_valid_after(datetime.datetime(2032, 1, 1, tzinfo=datetime.timezone.utc))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
    )
    cert = builder.sign(private_key=signer_priv, algorithm=hashes.SHA256())
    return cert.public_bytes(serialization.Encoding.DER)


def uds(iso: ISO15765, data: bytes) -> bytes:
    resp = iso.request(data, timeout=4.0)
    print(f">> {hexs(data)}")
    print(f"<< {hexs(resp)}")
    return resp


def main() -> int:
    host = sys.argv[1] if len(sys.argv) > 1 else "20.210.80.68"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 13337

    fw = Path("leak/ECUD.bin").read_bytes()
    leaked_cert = x509.load_pem_x509_certificate(Path("leak/cert.pem").read_bytes())
    leaked_priv = serialization.load_pem_private_key(Path("leak/key.pem").read_bytes(), password=None)

    # Entry 6 and 15 share a prime; entry 6 private key is recoverable.
    issuer_name, recovered_ca_priv = recover_shared_prime_key(fw, 6, 15)
    forged_cert_der = build_forged_leaf(issuer_name, recovered_ca_priv, leaked_priv, leaked_cert)

    bus = ProxyCAN(host, port)
    iso = ISO15765(bus, REQ_ID, RESP_ID)

    try:
        uds(iso, b"\x10\x03")
        uds(iso, b"\x22\x4E\x44")

        # 0x29 0x01: cfg byte + LV(cert) + LV(challengeClient)
        r1 = uds(iso, b"\x29\x01\x00" + len(forged_cert_der).to_bytes(2, "big") + forged_cert_der + b"\x00\x00")
        if not (len(r1) >= 23 and r1[0:3] == b"\x69\x01\x11"):
            print("[!] 0x29 0x01 did not return expected challenge")
            return 1

        ch_len = (r1[3] << 8) | r1[4]
        challenge = r1[5 : 5 + ch_len]

        # 0x29 0x03 format expected by this firmware variant:
        # LV(signature) + LV(ephemeralPublicKeyServer)
        to_sign = b"RAMN-CTF-AUTH:" + challenge
        signature = leaked_priv.sign(to_sign, padding.PKCS1v15(), hashes.SHA256())
        r3 = uds(iso, b"\x29\x03" + len(signature).to_bytes(2, "big") + signature + b"\x00\x00")
        if not (len(r3) >= 3 and r3[0:3] == b"\x69\x03\x12"):
            print("[!] 0x29 0x03 did not complete")
            return 1

        did = uds(iso, b"\x22\x4E\x44")
        if did.startswith(b"\x62\x4E\x44"):
            value = did[3:]
            print("[+] Protected DID 0x4E44:", value.decode("ascii", errors="replace"))
            return 0

        print("[!] DID still locked or unexpected response")
        return 1
    finally:
        bus.close()


if __name__ == "__main__":
    raise SystemExit(main())
```

## 플래그

```
FLAG{G00D_1MPL_P00R_K3Y_G3N}
```

## 배운 점

-
