---
ctf_name: "Dreamhack"
challenge_name: "Long-Sleep"
category: "rev"           # web / pwn / rev / crypto / misc
difficulty: "easy"      # easy / medium / hard / insane
author: "ansihoo"
date: "2026-06-23"
points: 500
tags: [sha256, anti-debug]
---

# 문제명

## 문제 설명

> 스스로 플래그를 생성한다는 stripped ELF 바이너리. 실행하면 "Wait! I'm generating flag!!" 이후 `DH{...}` 형태로 플래그를 출력하도록 설계되어 있다.
파일: `prob` (ELF 64-bit LSB PIE, x86-64, stripped, 14464 bytes)

- 문제 URL / 파일 등 접속 정보

## 풀이

### 분석

`_start`가 `__libc_start_main`에 넘기는 main은 `0x1367`로, 동작은 다음과 같다.

1. `puts("Wait! I'm generating flag!!")`
2. 내부 함수 `0x1411` 호출 → 32바이트 다이제스트를 스택에 생성
3. `printf("Here's your flag: DH{")`
4. 32바이트를 `%02x`로 출력
5. `puts("}")`

함수 `0x1411`은 rodata의 문자열 `"I will evolve into SUPER FLAG!!!!"`(느낌표 4개)에 대해 자체 구현된 SHA-256(`init`=0x19f5, `update`=0x1a73, `transform`=0x1552, `final`=0x1b14)을 계산한다.

초기화 상수는 표준값(`0x6a09e667 …`), sigma/Sigma 회전도 표준과 동일했다. 단, `init_array`에 등록된 `0x1229`(integrity_check)가 코드 영역의 SHA-256을 하드코딩 값과 비교해 통과해야 전역 카운터가 1이 되고, 그래야 `0x1411`이 `exit(0)`하지 않고 진행된다.

또한 `transform` 내부에서 카운터가 0이 아니면 `0x14d2`(nanosleep 기반)가 호출되는데, 슬립 값을 매 블록마다 2배씩 늘려서 정상 실행 시 사실상 멈춰버린다(anti-tamper/시간지연). 그래서 바이너리를 그냥 돌려서 출력을 받는 건 비현실적이고, 정적으로 해시를 재현하는 게 정답 경로다.

### 취약점

플래그 생성 알고리즘 전체가 바이너리 안에 들어 있어 정적 재현이 가능하다. 핵심 함정은 **SHA-256의 round constant(K) 64개가 표준값에서 변조**되어 있다는 점이다.

- 표준 `K[0] = 0x428a2f98`
- 이 바이너리 `K[0] = 0x418a2fa8` (rodata `0x20c0`, 리틀엔디언 로드)

즉 표준 sha256으로 계산하면 절대 안 맞고, 바이너리에 박힌 K 배열을 그대로 써야 한다.rodata `0x20c0`에서 K 64개(256바이트)를 추출하고, 표준 init/sigma + 커스텀 K로 `"I will evolve into SUPER FLAG!!!!"`를 해싱한다.

### 익스플로잇

rodata `0x20c0`에서 K 64개(256바이트)를 추출하고, 표준 init/sigma + 커스텀 K로 `"I will evolve into SUPER FLAG!!!!"`를 해싱한다.

```python
import struct
def rotr(x, n): return ((x >> n) | (x << (32 - n))) & 0xffffffff
M = 0xffffffff
H = [0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,
     0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19]

def custom_sha256(msg, K):
    h = H[:]; ml = len(msg) * 8
    msg += b'\x80'
    while len(msg) % 64 != 56: msg += b'\x00'
    msg += struct.pack('>Q', ml)
    for off in range(0, len(msg), 64):
        w = list(struct.unpack('>16I', msg[off:off+64])) + [0]*48
        for i in range(16, 64):
            s0 = rotr(w[i-15],7) ^ rotr(w[i-15],18) ^ (w[i-15] >> 3)
            s1 = rotr(w[i-2],17) ^ rotr(w[i-2],19) ^ (w[i-2] >> 10)
            w[i] = (w[i-16] + s0 + w[i-7] + s1) & M
        a,b,c,d,e,f,g,hh = h
        for i in range(64):
            S1 = rotr(e,6) ^ rotr(e,11) ^ rotr(e,25)
            ch = (e & f) ^ ((~e & M) & g)
            t1 = (hh + S1 + ch + K[i] + w[i]) & M
            S0 = rotr(a,2) ^ rotr(a,13) ^ rotr(a,22)
            maj = (a & b) ^ (a & c) ^ (b & c)
            t2 = (S0 + maj) & M
            hh,g,f,e,d,c,b,a = g,f,e,(d+t1)&M,c,b,a,(t1+t2)&M
        h = [(x+y) & M for x,y in zip(h, [a,b,c,d,e,f,g,hh])]
    return ''.join('%08x' % x for x in h)

data = open('prob','rb').read()
idx = data.find(bytes.fromhex('a82f8a4192443751'))   # K[0..1]
K = list(struct.unpack('<64I', data[idx:idx+256]))    # 0x20c0
print("DH{" + custom_sha256(b'I will evolve into SUPER FLAG!!!!', K) + "}")
```

## 플래그

```
DH{406b2742ffb2a6cac02abb8f303fa12067f8061339979855108ce4a2e38ef558}
```

## 배운 점

- "SHA-256처럼 생긴" 루틴이라도 init 상수·회전량·**round constant**가 표준과 같다고 가정하면 안 된다. 변조 포인트를 바이트 단위로 대조해야 한다.
- nanosleep 슬립 값을 지수적으로 키우는 anti-tamper는 동적 실행을 막기 위한 미끼다. 알고리즘이 전부 바이너리 안에 있으면 동적 실행을 포기하고 정적 재현으로 푸는 게 빠르다.
- stripped PIE에서 `_start`가 `__libc_start_main`에 넘기는 인자를 따라가면 진짜 main을 찾을 수 있다.
