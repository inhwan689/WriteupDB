#!/usr/bin/env python3
"""
Incognito 7.0 - Scheduler (rev, 350pt)
Author: gyh3257

핵심: 동일 우선순위 4스레드 -> 깨진 mutex race condition ->
      배열 전환 63회 > 44 -> hash = 0xe903d23a -> flag 출력
"""
import subprocess
import re

HOST = "ctf.axiosiiitl.dev"
PORT = 1337

# 4스레드, 타입 1~4 각 1개, 동일 priority(50), unique burst (합계 2000 <= 4000)
payload = "4\n1\n50\n200\n2\n50\n400\n3\n50\n600\n4\n50\n800\n"

print(f"[*] Connecting to {HOST}:{PORT}...")
result = subprocess.run(
    ["nc", HOST, str(PORT)],
    input=payload,
    capture_output=True,
    text=True,
    timeout=120,
)

output = result.stdout + result.stderr
print(output)

flag = re.search(r'IIITL\{[^}]+\}', output)
if flag:
    print(f"FLAG: {flag.group()}")
else:
    print("[-] Flag not found")
