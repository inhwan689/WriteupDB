"""
picoCTF 2019 - Vault Door 3
buffer permutation 의 역연산: target 문자열을 password 자리로 다시 풀어낸다.
"""

target = 'jU5t_a_sna_3lpm16g84c_u_4_m0r846'
p = [''] * 32

for i in range(8):
    p[i] = target[i]
for i in range(8, 16):
    p[23 - i] = target[i]
for i in range(16, 32, 2):
    p[46 - i] = target[i]
for i in range(31, 16, -2):
    p[i] = target[i]

password = ''.join(p)
assert len(password) == 32 and all(p), p

# 검증: 복원된 password를 다시 변환해 target과 일치하는지 확인
buf = [''] * 32
for i in range(8):
    buf[i] = password[i]
for i in range(8, 16):
    buf[i] = password[23 - i]
for i in range(16, 32, 2):
    buf[i] = password[46 - i]
for i in range(31, 16, -2):
    buf[i] = password[i]
assert ''.join(buf) == target

print(f"picoCTF{{{password}}}")
