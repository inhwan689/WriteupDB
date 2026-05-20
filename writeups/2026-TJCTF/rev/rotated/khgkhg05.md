---
ctf_name: "TJCTF 2026"
challenge_name: "rotated"
category: "rev"
difficulty: "medium"
author: "khgkhg05"
date: "2026-05-15"
points: 282
tags: [byte shift, bash obfuscation, base64, gzip]
---

# rotated

## 문제 설명

> this file isn't making any sense to me. can you discover what it means? hint: look at the title
> hint 2: consider each byte separately

- 제공 파일: `chall`
- 문제 제목과 힌트처럼 파일의 각 바이트가 일정하게 회전/이동되어 있는 리버싱 문제다.
- 제출 디렉터리에는 풀이 과정에서 사용한 `patch_byte.c`, 컴파일 결과인 `patch_byte.exec`, 패치 결과물인 `chall_patch`, 실행 결과 생성된 `script.sh`도 함께 포함했다.

## 풀이

### 분석

먼저 `file`로 확인하면 원본 `chall`은 정상적인 실행 파일로 인식되지 않는다.

```bash
$ file chall
chall: data
```

문제 제목이 `rotated`이고, 힌트에서 각 바이트를 따로 보라고 했으므로 파일 전체에 동일한 byte shift가 적용되어 있다고 판단했다. 실제로 각 바이트에서 `0x1d`를 빼서 새 파일을 만들면 정상적인 ELF 실행 파일이 된다.

```c
#include <stdio.h>

int main(void)
{
    FILE* in;
    FILE* out;
    int c;

    in = fopen("chall", "rb");
    out = fopen("chall_patch", "wb");

    while ((c = fgetc(in)) != EOF)
    {
        unsigned char binary = (unsigned char)c;
        binary -= 0x1D;
        fputc(binary, out);
    }

    fclose(in);
    fclose(out);

    return 0;
}
```

패치 후 파일 형식을 다시 확인하면 `chall_patch`가 64-bit ELF로 인식된다.

```bash
$ file chall_patch
chall_patch: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), statically linked, no section header
```

### 취약점

원본 바이너리는 실행 로직 자체를 암호화한 것이 아니라, 파일의 모든 바이트를 같은 값만큼 shift해 둔 형태였다. 즉 파일 전체에 대해 다음과 같은 단순 변환이 적용되어 있었다.

```text
patched_byte = original_byte - 0x1d
```

따라서 올바른 shift 값을 찾으면 바이너리를 그대로 복구할 수 있다. 복구된 바이너리는 실행 시 `script.sh`를 생성한다.

### 익스플로잇

`patch_byte.c`를 컴파일하고 실행하여 `chall_patch`를 생성한다.

```bash
$ gcc patch_byte.c -o patch_byte.exec
$ ./patch_byte.exec
```

이후 패치된 바이너리를 실행하면 난독화된 Bash 스크립트가 생성된다.

```bash
$ ./chall_patch
$ file script.sh
script.sh: Bourne-Again shell script, ASCII text executable, with very long lines
```

생성된 `script.sh`는 `${*}`, `${@//.../...}`, 대소문자 변환, 불필요한 escape 등을 섞어 명령어를 알아보기 어렵게 만든 Bash 난독화 스크립트다. 핵심 명령만 정리하면 아래와 같다.

```bash
printf 'H4sIAEDAzmkC/0tNzshXUPLJz8/OzEtXSMsvUkhUSMtJTLdXUlBWSHEvyEpxjzKPzAo0THSzzPY18jL0y7Es8XMJNfY19rJ0Tre1BQCGqZA9QQAAAA==' | base64 -d | gunzip -c
```

이를 실행하면 한 줄의 `echo` 명령이 나온다.

```bash
$ printf 'H4sIAEDAzmkC/0tNzshXUPLJz8/OzEtXSMsvUkhUSMtJTLdXUlBWSHEvyEpxjzKPzAo0THSzzPY18jL0y7Es8XMJNfY19rJ0Tre1BQCGqZA9QQAAAA==' | base64 -d | gunzip -c
echo "Looking for a flag?" # dGpjdGZ7...
```

주석 뒤의 문자열은 다시 base64로 인코딩되어 있다. 이를 디코딩하면 최종 플래그가 나온다.

```bash
$ printf 'dGpjdGZ7...==' | base64 -d
tjctf{...}
```

## 플래그

```text
tjctf{REDACTED}
```

## 추가 파일

제출물에는 문제 풀이 흐름을 재현할 수 있도록 현재 문제 디렉터리에 있던 파일을 함께 첨부했다.

| 파일 | 설명 |
|------|------|
| `chall` | 문제에서 주어진 원본 파일 |
| `patch_byte.c` | `chall`의 각 바이트에서 `0x1d`를 빼서 `chall_patch`를 생성하는 패치 코드 |
| `patch_byte.exec` | `patch_byte.c`를 컴파일한 실행 파일 |
| `chall_patch` | byte shift를 복구한 ELF 실행 파일 |
| `script.sh` | `chall_patch` 실행 결과 생성된 난독화 Bash 스크립트 |

## 배운 점

파일이 `data`로만 보이더라도 매직 바이트가 깨져 있는 경우에는 전체 바이트에 단순 산술 변환이 적용된 것인지 먼저 의심해볼 수 있다. 또한 Bash 난독화는 복잡해 보여도 실제로는 `eval`에 전달되는 문자열을 따라가면 최종 명령을 분리할 수 있고, 이번 문제처럼 `base64`와 `gzip` 조합으로 한 번 더 감춰진 경우가 많다.
