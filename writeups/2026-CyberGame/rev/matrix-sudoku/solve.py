import hashlib
import binascii
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from itertools import permutations

CTXT = "7b324bfbfe9cf9ccdce792276ae92032e9acb2b3342be9e954eb6b8f37d0babf9ea0dfd6c7462b2f3bfd591654940309"
raw = binascii.unhexlify(CTXT)
IV, ENC = raw[:16], raw[16:]

def gen_key(matrix):
    return hashlib.sha256(str(matrix).encode()).hexdigest()

def try_decrypt(grid):
    key = bytes.fromhex(gen_key(grid))
    try:
        return unpad(AES.new(key, AES.MODE_CBC, IV).decrypt(ENC), 16).decode('utf-8')
    except Exception:
        return None

for d1 in range(6, 11):
    for d2 in range(11, 16):
        for d3 in range(16, 21):
            for d4 in range(22, 26):
                if 1 + d1 + d2 + d3 + d4 != 65:
                    continue
                r1_rest = [v for v in range(6,11)  if v != d1]
                r2_rest = [v for v in range(11,16) if v != d2]
                r3_rest = [v for v in range(16,21) if v != d3]
                r4_rest = [v for v in range(22,26) if v != d4]

                for p0 in permutations([2,3,4,5]):
                    r0 = [1, p0[0], p0[1], p0[2], p0[3]]
                    for p1 in permutations(r1_rest):
                        r1 = [p1[0], d1, p1[1], p1[2], p1[3]]
                        for p2 in permutations(r2_rest):
                            r2 = [p2[0], p2[1], d2, p2[2], p2[3]]
                            for p3 in permutations(r3_rest):
                                r3 = [p3[0], p3[1], p3[2], d3, p3[3]]
                                for p4 in permutations(r4_rest):
                                    r4 = [21, p4[0], p4[1], p4[2], d4]
                                    grid = [r0, r1, r2, r3, r4]
                                    result = try_decrypt(grid)
                                    if result:
                                        print("Flag:", result)
                                        exit()
