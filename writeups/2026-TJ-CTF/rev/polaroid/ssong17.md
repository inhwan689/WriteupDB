---
ctf_name: "TJ"
challenge_name: "polaroid"
category: "rev"           # web / pwn / rev / crypto / misc
difficulty: "easy"      # easy / medium / hard / insane
author: "ssong17"
date: "2026-05-17"
points: 50
tags: [태그1, 태그2]
---

# 문제명

## 문제 설명

this old polaroid won't develop. it needs a password, and the password is somewhere on the film.

- 문제 URL / 파일 등 접속 정보: polaroid ELF 파일

## 풀이

### 분석

업로드된 파일을 실제로 확인해 보니, 처음 예상했던 ELF가 아니라 **macOS용 Mach-O 64비트 arm64 실행 파일**이었다.

파일 헤더를 보면 매직 값이 `CF FA ED FE`이고, 심볼 테이블에는 `main`과 `encrypted` 정도만 남아 있었다.  
문자열 영역에는 다음 문자열들이 존재했다.

```text
usage: %s <password>
nope
flag.png
wb
fopen
developed flag.png
```

`main` 함수를 디스어셈블해 보면 프로그램의 동작은 크게 두 단계다.

1. 입력한 password가 특정 문자열과 정확히 일치하는지 검사
2. 내부 `encrypted` 데이터를 password로 XOR해서 PNG 파일로 복원

비밀번호 검증 부분은 한 글자씩 직접 비교하는 형태로 구현되어 있었고, 비교되는 문자열은 다음과 같았다.

```text
exposeTheNegative
```

즉, 이 문자열이 프로그램이 요구하는 password다.

그 다음 로직에서는 `flag.png`를 `wb` 모드로 열고, 바이너리 내부의 `encrypted` 영역 전체를 순회하면서 각 바이트를 password와 반복 XOR해 출력 파일에 기록한다.

동작을 의사코드로 정리하면 다음과 같다.

```c
if (argc != 2) {
    fprintf(stderr, "usage: %s <password>\n", argv[0]);
    return 1;
}

if (strlen(argv[1]) != 17) return 1;
if (argv[1] != "exposeTheNegative") return 1;

fp = fopen("flag.png", "wb");
for (i = 0; i < 0x18b4; i++) {
    fputc(encrypted[i] ^ argv[1][i % 17], fp);
}
fclose(fp);
puts("developed flag.png");
```

### 취약점

복호화에 필요한 password가 코드 내부에 **평문으로 하드코딩**되어 있고, `encrypted` 데이터 역시 바이너리 안에 그대로 포함되어 있다.  
게다가 복호화 방식이 단순한 **반복 XOR**이므로, 프로그램을 직접 실행하지 않아도 정적 분석만으로 원본 PNG를 쉽게 복원할 수 있다.

### 익스플로잇

실제로는 바이너리의 `encrypted` 영역을 추출한 뒤, 키 `exposeTheNegative`를 반복 XOR해 PNG를 복원하면 된다.

```python
import pathlib

src = pathlib.Path("polaroid")
data = src.read_bytes()

enc = data[0x720:0x720 + 0x18b4]
key = b"exposeTheNegative"

plain = bytes(b ^ key[i % len(key)] for i, b in enumerate(enc))
pathlib.Path("developed_flag.png").write_bytes(plain)
```

복호화 결과물의 시작 바이트는 PNG 시그니처 `89 50 4E 47 0D 0A 1A 0A`로 정상적이다.  
이미지를 열어 보면 텍스트가 거꾸로 되어 있으므로 180도 회전해서 읽으면 된다.

## 플래그

```
tjctf{develop_the_picture}
```

## 배운 점

