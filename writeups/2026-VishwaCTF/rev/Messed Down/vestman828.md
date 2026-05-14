---
ctf_name: "2026-VishwaCTF"
challenge_name: "Messed Down"
category: "rev"
difficulty: "medium"
author: "vestman828"
date: "2026-04-05"
tags: [rev]
---

# Messed Down

## 문제 설명

> 2026-VishwaCTF에 Messed Down 문제입니다. Rev입니다.

## 풀이

### 분석

문제 파일은 MessedDown라는 ELF64 바이너리입니다. 실행해 보면 입력을 받아들이는 것처럼 보이지만, 어떤 값을 넣어도 항상 다음과 같은 형태의 메시지만 출력합니다.
```
Security is Compromised!
Need to add another stage :)
Enter Secret:
Your Secret "..." is invalid!
```
처음에는 단순한 secret checker처럼 보이지만, 실제 핵심은 입력 검증이 아니라 난독화된 제어 흐름을 끝까지 유지하면서 플래그가 스택에 조립되는 과정에 있습니다.

디컴파일 결과 함수 경계는 많이 깨져 있었지만, 다음과 같은 중요한 저장 루틴은 비교적 명확하게 확인할 수 있었습니다.

uint32_t idx = *(uint32_t *)(rsp + 0x4bc);
uint64_t chunk = rdx;

*(uint64_t *)(rsp + 0x258 + ((uint64_t)idx * 8)) = chunk;

즉,

idx는 현재 플래그 조각 인덱스이고
rdx에 들어 있는 8바이트 값이
rsp + 0x258부터 시작하는 스택 버퍼에 차례대로 저장됩니다.

주변 스택에는 "Your Secret \"", " is invalid!\n" 같은 사용자용 문자열도 함께 존재했기 때문에, 이 문제는 출력 문자열과 플래그 데이터를 같은 스택 프레임 내부에서 섞어 다루고 있음을 알 수 있습니다.

문제는 실행 흐름 중간에 jmp rax 형태의 간접 점프가 반복적으로 등장한다는 점입니다.

goto *(void *)rax;

이 분기들이 그대로 실행되면 중간에 잘못된 주소로 튀면서 죽어 버리기 때문에, 플래그가 끝까지 조립되기 전에 에뮬레이션이 종료됩니다.

실제로 [rsp+0x258 + idx*8]에 대한 쓰기를 추적해 보면, 처음에는 다음 정도만 얻을 수 있습니다.

idx 0 -> VishwaCT
idx 1 -> F{h3y_g3
idx 2 -> n1u5_w45

즉, 플래그가 조립되고 있다는 사실은 보이지만, 전체를 복구하려면 제어 흐름을 인위적으로 이어 줘야 합니다.

그래서 Unicorn으로 바이너리를 에뮬레이션하면서, 특정 jmp rax 지점에서 rax 값을 원하는 다음 블록으로 덮어쓰는 방식으로 흐름을 보정했습니다.

패치한 분기는 다음과 같습니다.

0x40e7d -> 0x6a2cb
0x6a432 -> 0x75c23
0x75d19 -> 0x465fd

이후에는 추가적인 8바이트 조각들이 정상적으로 기록됩니다.

idx 3 -> _7h15_l1
idx 4 -> 77l3_h4r
idx 5 -> d3r_7h15
idx 6 -> _71m3}

이를 순서대로 이어 붙이면 최종 플래그를 얻을 수 있습니다.


### 익스플로잇

```python
from unicorn import *
from unicorn.x86_const import *
from elftools.elf.elffile import ELFFile
import struct, re

BINARY = 'MessedDown'
with open(BINARY, 'rb') as f:
    ef = ELFFile(f)
    entry = ef.header['e_entry']
    segs = [p for p in ef.iter_segments() if p['p_type'] == 'PT_LOAD']

PAGE = 0x1000
pg = lambda x: x & ~(PAGE - 1)
pgu = lambda x: (x + PAGE - 1) & ~(PAGE - 1)

mu = Uc(UC_ARCH_X86, UC_MODE_64)

for p in segs:
    vaddr = p['p_vaddr']
    memsz = p['p_memsz']
    off = p['p_offset']
    filesz = p['p_filesz']
    flags = p['p_flags']

    st = pg(vaddr)
    en = pgu(vaddr + memsz)

    perms = 0
    if flags & 4:
        perms |= UC_PROT_READ
    if flags & 2:
        perms |= UC_PROT_WRITE
    if flags & 1:
        perms |= UC_PROT_EXEC

    mu.mem_map(st, en - st, perms)
    with open(BINARY, 'rb') as f:
        f.seek(off)
        mu.mem_write(vaddr, f.read(filesz))

mu.mem_map(0x85000, 0x3000, UC_PROT_READ | UC_PROT_WRITE)

STACK_BASE = 0x70000000
STACK_SIZE = 0x200000
mu.mem_map(STACK_BASE, STACK_SIZE, UC_PROT_READ | UC_PROT_WRITE)

rsp = STACK_BASE + STACK_SIZE - 0x1000
arg = b'./MessedDown\x00'
arg_addr = rsp - 0x200
mu.mem_write(arg_addr, arg)
mu.mem_write(rsp, b''.join(struct.pack('<Q', v) for v in [1, arg_addr, 0, 0, 0, 0]))

mu.reg_write(UC_X86_REG_RSP, rsp)
mu.reg_write(UC_X86_REG_RDX, 0)

stdin_data = bytearray(b'AAAA\n')
stdin_pos = 0
frame_base = 0x701feaf8
stores = []

patch = {
    0x40e7d: 0x6a2cb,
    0x6a432: 0x75c23,
    0x75d19: 0x465fd,
}

def hook(mu, addr, size, user):
    global stdin_pos

    if size == 2:
        op = bytes(mu.mem_read(addr, 2))

        if op == b'\x0f\x05':  # syscall
            rax = mu.reg_read(UC_X86_REG_RAX)
            rsi = mu.reg_read(UC_X86_REG_RSI)
            rdx = mu.reg_read(UC_X86_REG_RDX)

            if rax == 0:  # read
                n = min(rdx, len(stdin_data) - stdin_pos)
                if n > 0:
                    mu.mem_write(rsi, bytes(stdin_data[stdin_pos:stdin_pos + n]))
                    stdin_pos += n
                mu.reg_write(UC_X86_REG_RAX, n)
                mu.reg_write(UC_X86_REG_RIP, addr + 2)

            elif rax == 1:  # write
                mu.reg_write(UC_X86_REG_RAX, rdx)
                mu.reg_write(UC_X86_REG_RIP, addr + 2)

            elif rax in (60, 231):  # exit
                mu.reg_write(UC_X86_REG_RAX, 0)
                mu.reg_write(UC_X86_REG_RIP, addr + 2)

            else:
                mu.reg_write(UC_X86_REG_RAX, 0xfffffffffffffff2)
                mu.reg_write(UC_X86_REG_RIP, addr + 2)

        elif op == b'\xff\xe0':  # jmp rax
            if addr in patch:
                mu.reg_write(UC_X86_REG_RAX, patch[addr])

    if addr == 0x6dbb2:
        idx = int.from_bytes(mu.mem_read(frame_base + 0x4bc, 4), 'little')
        rdx = mu.reg_read(UC_X86_REG_RDX)
        stores.append((idx, rdx.to_bytes(8, 'little')))
        if idx > 10:
            mu.emu_stop()

mu.hook_add(UC_HOOK_CODE, hook)
mu.emu_start(entry, 0, count=30000000)

for idx, b in stores:
    print(idx, b)

frame = bytes(mu.mem_read(frame_base, 0x520))
m = re.search(rb'VishwaCTF\{[^\x00]{0,120}', frame)
if m:
    print('FLAG =', m.group().decode())
```

## 플래그

```
VishwaCTF{h3y_g3n1u5_w45_7h15_l177l3_h4rd3r_7h15_71m3}
```

## 배운 점

Weight 40아래인 Bad CTF는 거르자
