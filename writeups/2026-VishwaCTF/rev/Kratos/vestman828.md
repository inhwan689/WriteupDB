---
ctf_name: "2026-VishwaCTF"
challenge_name: "Kratos"
category: "rev"
difficulty: "medium"
author: "vestman828"
date: "2026-04-05"
tags: [IL2CPP]
---

# Blinded

## 문제 설명

> 2026-VishwaCTF에 Kratos 문제입니다. Rev입니다.

## 풀이

### 분석

이 APK는 Unity IL2CPP 빌드입니다.

먼저 unpack된 APK 디렉터리 구조를 확인했습니다. 핵심 파일은 다음과 같았습니다.

assets/bin/Data/Managed/Metadata/global-metadata.dat
lib/arm64-v8a/libil2cpp.so

전형적인 Unity IL2CPP 타깃이므로, classes.dex보다는 메타데이터와 네이티브 바이너리 분석에 집중했습니다.

Assembly-CSharp.dll을 디컴파일했습니다.

복원된 핵심 구조는 다음과 같았습니다.

private byte[] flagCipher;
private byte xorKey;

[Address(RVA = "0x1E0E8E0", ...)]
private string ComputeSHA256(string rawData)

[Address(RVA = "0x1E0EB2C", ...)]
private string DecryptFlag()

[Address(RVA = "0x1E0EBF8", ...)]
public buttonBehaviour()

즉, 실제로 확인해야 할 핵심 함수는 ComputeSHA256, DecryptFlag, 그리고 생성자였습니다.

Cpp2IL의 diffable output에서는 다음과 같은 데이터를 확인할 수 있었습니다.

internal static readonly __StaticArrayInitTypeSize=29 6575F9E821FA4C5B68106F37789E675A1A8D7966CECD5852397B34AFBDFD1138;
Field RVA Decoded (hex blob):
[3C 03 19 02 1D 0B 29 3E 2C 11 13 5A 1F 35 0D 5A 5D 35 01 18 5E 1E 5A 19 35 2D 5A 2E 17]

이 29바이트 blob은 암호화된 플래그 바이트 배열로 보였습니다.

libil2cpp.so에서 대상 RVA를 직접 disassemble하여 확인했습니다.

생성자 (RVA 0x1E0EBF8)의 중요한 명령은 다음과 같습니다.
01E0ED10: mov      w8, #0x6a

이 명령으로 XOR 키가 0x6A로 설정됩니다.
DecryptFlag (RVA 0x1E0EB2C)에서
중요한 루프는 다음과 같습니다.

01E0EBAC: ldrb     w8, [x8, x9]
01E0EBB0: ldrb     w10, [x19, #0x48]
01E0EBB4: eor      w8, w10, w8
01E0EBB8: strb     w8, [x20, x9]

여기서 [x19, #0x48]는 xorKey이고, flagCipher의 각 바이트와 XOR 연산을 수행합니다.

즉, 복호화는 단순히 다음과 같습니다.
plaintext[i] = cipher[i] ^ 0x6A



### 익스플로잇

```python
flag_cipher_hex = "3C0319021D0B293E2C11135A1F350D5A5D3501185E1E5A19352D5A2E17"
xor_key = 0x6A
cipher = bytes.fromhex(flag_cipher_hex)
flag = bytes(b ^ xor_key for b in cipher).decode('utf-8')
print(flag)
```

## 플래그

```
VishwaCTF{y0u_g07_kr4t0s_G0D}
```

## 배운 점

Weight 40아래인 Bad CTF는 거르자
