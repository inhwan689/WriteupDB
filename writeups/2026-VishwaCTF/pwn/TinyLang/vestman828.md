---
ctf_name: "2026-VishwaCTF"
challenge_name: "TinyLang"
category: "pwn"
difficulty: "medium"
author: "vestman828"
date: "2026-04-05"
tags: [OOB]
---

# TinyLang

## 문제 설명

> 2026-VishwaCTF에 TinyLang 문제입니다. Pwn입니다.

## 풀이

### 분석

```
  int g_count;                       // 0x4140
  char g_table[/*...*/];             // 0x40a0
  void (*g_errfn)(char *);           // 0x4150 (초기값:
  error_handler)

  void error_handler(char *s) {
      printf("Error: %s\n", s);
  }

  void system_trampoline(char *cmd) {
      system(cmd);
  }

  // print 경로에서 호출되는 검색 함수 (0x1330)
  void lookup_and_print_or_error(char *name) {
      for (int i = 0; i < g_count; i++) {
          char *entry = (char *)g_table + i * 0x14;   //
  stride = 20 bytes
          if (strcmp(entry, name) == 0) {
              int v = *(int *)(entry + 0x10);         //
  value offset
              printf("%d\n", v);
              return;
          }
      }
      g_errfn(name); // 못 찾으면 함수포인터 간접호출
  }

  // 명령 파서 (0x13b0)
  void handle_line(char *line) {
      if (strncmp(line, "let ", 4) == 0) {
          char *body = line + 4;               //
  "<name> = <value>"
          char *eq = strstr(body, " = ");
          if (!eq) return;

          *eq = '\0';
          int val = strtol(eq + 3, NULL, 10);

          int idx = g_count;
          char *dst = (char *)g_table + idx * 0x14;   //
  20-byte 간격

          // 취약점: 20바이트 슬롯에 64바이트 복사
          memcpy(dst, body,
  0x40);                     // <-- OOB/overlap write
          *(int *)(dst + 0x10) = val;

          g_count = idx + 1;
          return;
      }

      if (strncmp(line, "print ", 6) == 0) {
          char *name = line + 6;
          name[strcspn(name, "\n")] = '\0';
          lookup_and_print_or_error(name);
      }
  }
```
의사코드로 옮기면 위와 같습니다.
memcpy(dst, body, 0x40); with dst = base + idx * 0x14
에서, 0x14보다 복사 크기가 더 커서
OOB가 발생하며, g_errfn 덮기 가능합니다.
이를 통해 RCE를 합니다.

### 익스플로잇

```python
(삭제되어서 남아있지 않습니다..)
```

## 플래그

```
V15hw4CTF{cu570m_14ngu4g3_f4113d_6cec7cd0}
```

## 배운 점

Weight 40아래인 Bad CTF는 거르자
