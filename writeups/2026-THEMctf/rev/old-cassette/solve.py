"""
THEM?!CTF 2026 - Old Cassette (rev)
Flag: THEM?!CTF{0LD_T4P3_N3V3R_D1E5K7}

CHIP-8 ROM 분석:
- 키스트림 PRNG: period=34, tail=329
- 각 문자: char = mem[sprite_table[VA&7] + offset] ^ VA ^ VB
- 후반 CALL 0x2AC 직전 LD V5, 0xFF로 V5 리셋 (255 × (2^32-1) 스텝)
"""

rom = open("main.bin", "rb").read()
BASE = 0x200
mem = bytearray(4096)

FONT = [
    0xF0,0x90,0x90,0x90,0xF0, 0x20,0x60,0x20,0x20,0x70,
    0xF0,0x10,0xF0,0x80,0xF0, 0xF0,0x10,0xF0,0x10,0xF0,
    0x90,0x90,0xF0,0x10,0x10, 0xF0,0x80,0xF0,0x10,0xF0,
    0xF0,0x80,0xF0,0x90,0xF0, 0xF0,0x10,0x20,0x40,0x40,
    0xF0,0x90,0xF0,0x90,0xF0, 0xF0,0x90,0xF0,0x10,0xF0,
    0xF0,0x90,0xF0,0x90,0x90, 0xE0,0x90,0xE0,0x90,0xE0,
    0xF0,0x80,0x80,0x80,0xF0, 0xE0,0x90,0x90,0x90,0xE0,
    0xF0,0x80,0xF0,0x80,0xF0, 0xF0,0x80,0xF0,0x80,0x80,
]
for i, b in enumerate(FONT):
    mem[i] = b
for i, b in enumerate(rom):
    if BASE + i < 4096:
        mem[BASE + i] = b

DATA_TABLE = bytes(mem[0x800:0x900])  # 256바이트 PRNG 테이블
SPRITE_BASES = {0:0x400, 1:0x460, 2:0x4C0, 3:0x520, 4:0x600, 5:0x660, 6:0x6C0, 7:0x720}


def step_key(VA, VB):
    V0 = DATA_TABLE[VB]
    key = {0x00: 0xa9, 0x40: 0x5c, 0x80: 0xd3, 0xC0: 0x76}[VB & 0xC0]
    V0 = (V0 ^ VB ^ key) & 0xFF
    old_VA, old_VB = VA, VB
    s = VB + V0
    VB = s & 0xFF
    carry = 1 if s > 0xFF else 0
    VA = (VA + carry) & 0xFF
    val16 = (old_VA << 8) | old_VB
    val16 = ((val16 << 5) | (val16 >> 11)) & 0xFFFF
    return (VA ^ (val16 >> 8)) & 0xFF, (VB ^ (val16 & 0xFF)) & 0xFF


# PRNG 주기 탐색
VA, VB = 0xa7, 0xc3
seen, states = {}, [(VA, VB)]
i = 0
while True:
    if (VA, VB) in seen:
        TAIL, PERIOD = seen[(VA, VB)], i - seen[(VA, VB)]
        break
    seen[(VA, VB)] = i
    VA, VB = step_key(VA, VB)
    states.append((VA, VB))
    i += 1


def get_state(n):
    if n < len(states):
        return states[n]
    return states[(n - TAIL) % PERIOD + TAIL]


def get_op(addr):
    off = addr - BASE
    return (rom[off] << 8) | rom[off + 1] if 0 <= off < len(rom) - 1 else 0


# 코드에서 연산 목록 추출
ops = []
V5 = 0x18  # CALL 0xDB8 이후 초기값
addr = 0x91e
while addr < 0xDB0:
    op = get_op(addr)
    if op == 0x2282:  # CALL 0x282
        v9 = (get_op(addr-8) & 0xFF) if (get_op(addr-8) >> 8) == 0x69 else 0
        vc = (get_op(addr-6) & 0xFF) if (get_op(addr-6) >> 8) == 0x6C else 0
        vd = (get_op(addr-4) & 0xFF) if (get_op(addr-4) >> 8) == 0x6D else 0
        ve = (get_op(addr-2) & 0xFF) if (get_op(addr-2) >> 8) == 0x6E else 0
        adv = v9 + vc*256 + vd*65536 + ve*16777216
        offset = None
        v1 = None
        for s in range(addr+2, addr+80, 2):
            op2 = get_op(s)
            if (op2 >> 8) == 0x61:
                v1 = op2 & 0xFF
            if op2 == 0xF11E:
                offset = v1
                break
            if op2 in (0x22AC, 0x2282):
                break
        ops.append(('282', adv, offset))
        addr += 2
    elif op == 0x22AC:  # CALL 0x2AC
        if (get_op(addr-2) >> 8) == 0x65:  # LD V5, kk
            V5 = get_op(addr-2) & 0xFF
        adv = V5 * (2**32 - 1)
        offset = None
        v1 = None
        for s in range(addr+2, addr+80, 2):
            op2 = get_op(s)
            if (op2 >> 8) == 0x61:
                v1 = op2 & 0xFF
            if op2 == 0xF11E:
                offset = v1
                break
            if op2 in (0x22AC, 0x2282):
                break
        ops.append(('2AC', adv, offset))
        addr += 2
    else:
        addr += 2


# 복호화
mem_work = bytearray(mem)
step = 0
flag = []

for op_type, adv, offset in ops:
    step += adv
    VA, VB = get_state(step)
    mem_work[0x58B] = VA
    mem_work[0x58C] = VB
    if offset is not None:
        I = SPRITE_BASES[VA & 7] + offset
        enc = mem_work[I]
        char = (enc ^ VA ^ VB) & 0xFF
        mem_work[I] = VB
        flag.append(chr(char) if 32 <= char < 127 else f"[{char:02x}]")

print("Flag:", "".join(flag))
