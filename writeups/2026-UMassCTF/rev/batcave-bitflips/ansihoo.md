---
ctf_name: "UMassCTF"
challenge_name: "batcave-bitflips"
category: "rev"           # web / pwn / rev / crypto / misc
difficulty: "medium"      # easy / medium / hard / insane
author: "ansihoo"
date: "2026-04-10"
points: 100
tags: [bitflip, xor]
---

# 문제명
batcave-bitflips

## 문제 설명

> Batman's new state-of-the-art AI agent has deleted all of the source code to the Batcave license verification program! There's an old debug version lying around, but that thing has been hit by more cosmic rays than Superman! 

- batcave_license_checker

## 풀이

### 분석

일단 file이랑 strings 돌려봤다. stripped 안 된 64비트 PIE ELF고, strings에서 `!_batman-robin-alfred_((67||67))`라는 라이선스 키가 그냥 박혀있었다. 근데 이걸로 실행하면 INVALID 뜬다. 문제 설명에서 cosmic ray가 바이너리를 망가뜨렸다고 했으니까 뭔가 비트가 날아갔겠구나 싶었다. objdump로 함수 목록 보니까 expand_state, substitute, mix, rotate, hash, verify, decrypt_flag 이렇게 있었고, 구조 자체는 단순했다. 키를 해싱해서 EXPECTED랑 memcmp하고, 맞으면 decrypt_flag 호출하는 흐름이었다. .data 섹션 덤프하니까 0x4020에 키, 0x4040에 EXPECTED 해시 32바이트, 0x4060에 암호화된 FLAG 32바이트, 0x4080부터 256바이트짜리 SBOX가 있었다.

### 취약점

비트플립이 총 4군데 있었다. 첫 번째는 SBOX인데, 0x43이 인덱스 24랑 92 두 군데에 중복으로 들어있고 0x44가 없었다. SBOX는 원래 0~255 순열이어야 하는데 깨져있는 거다. 두 번째는 rotate 함수 안에 SIB 바이트가 0xc5로 되어 있어서 b<<3이 되고 있었는데, 원래는 b>>5랑 OR해야 ROL3이 맞다. 세 번째는 hash 루프 카운터가 0xbeeeee(약 1250만)로 너무 크게 박혀있었다. 네 번째가 제일 중요했는데, decrypt_flag 함수 안에서 XOR(0x31) 써야 할 자리에 OR(0x09)가 들어있었다. 0x09랑 0x31이 비트 3, 5만 다른 관계라서 전형적인 비트플립이었다.

### 익스플로잇

1~3번 비트플립들이 해시를 완전히 망가뜨려서 키로 EXPECTED를 재현하는 건 사실상 불가능했다. 근데 중요한 포인트가 EXPECTED 자체는 손상되지 않았다는 거다. 그리고 decrypt_flag는 hash 결과랑 FLAG를 XOR해서 플래그를 내놓는 구조인데, 원래 공식이 `FLAG_plain[i] = flag_enc[i] XOR EXPECTED[i]`인 거니까 그냥 직접 XOR하면 끝이었다. 스크립트 짜서 돌렸더니 바로 나왔다.

```python
flag_enc = bytes([
    0x6e,0x19,0x34,0x49,0x77,0x7d,0xf0,0x5a,
    0x07,0xb4,0x33,0xa6,0x8c,0xe6,0xe6,0x17,
    0xfb,0xe9,0x6f,0xae,0x2e,0xe5,0x26,0xc3,
    0x70,0xe3,0xc4,0x7d,0x27,0x7f,0x2b,0x00,
])
expected = bytes([
    0x3b,0x54,0x75,0x1a,0x24,0x06,0xaf,0x05,
    0x77,0x80,0x47,0xc5,0xe4,0x83,0xd3,0x48,
    0xcb,0x87,0x30,0xde,0x1a,0x91,0x45,0xab,
    0x15,0xc7,0x9b,0x22,0x04,0x02,0x2b,0xee,
])
flag = bytes(a ^ b for a, b in zip(flag_enc, expected))
print(flag.split(b'\x00')[0].decode())
```

## 플래그

```
UMASS{p4tche5_0n_p4tche$#}
```

## 배운 점

비트플립이 여러 개 겹쳐있으면 전부 고치려 하기보다 뭐가 멀쩡한지 찾는 게 빠르다. 나는 해시 역산이나 바이너리 패치에 시간 쏟다가 EXPECTED가 손상 안 됐다는 걸 뒤늦게 캐치했는데, 처음부터 .data 섹션 값들을 신뢰하고 접근했으면 훨씬 빨리 풀었을 것 같다. 그리고 라이선스 검증 구조(key → hash → memcmp → decrypt)에서 복호화 함수 opcode 하나 다른 거 놓치면 한참 헤맬 수 있으니까 짧은 함수일수록 어셈블리 꼼꼼히 보는 습관을 들여야겠다.
