#!/usr/bin/env python3
"""
Batcave Bitflips — UMassCTF 2026 (rev/medium)

Key insight: decrypt_flag uses hash output as the key, but verify() requires
hash output == EXPECTED. So the decryption key IS EXPECTED itself — no need
to actually run the (broken, 12.5M-round) hash function.

The decrypt_flag function in the binary uses OR instead of XOR (one of the
3 cosmic ray bitflips). Patching it mentally to XOR and applying:

    plaintext_flag[i] = FLAG_ENC[i] XOR EXPECTED[i]
"""

EXPECTED = bytes.fromhex(
    "3b54751a2406af05778047c5e483d348"
    "cb8730de1a9145ab15c79b2204022bee"
)

FLAG_ENC = bytes.fromhex(
    "6e1934497 77df05a07b433a68ce6e617"
    "fbe96fae2ee526c370e3c47d277f2b00".replace(" ", "")
)

assert len(EXPECTED) == 32 and len(FLAG_ENC) == 32

flag = bytes(FLAG_ENC[i] ^ EXPECTED[i % 32] for i in range(32))
# strip null terminator and any trailing garbage
flag = flag.split(b'\x00', 1)[0]
print(flag.decode('ascii'))
