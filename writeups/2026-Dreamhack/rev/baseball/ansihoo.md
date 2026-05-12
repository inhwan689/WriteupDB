---
ctf_name: "2026-Dreamhack"
challenge_name: "baseball"
category: "rev"           # web / pwn / rev / crypto / misc
difficulty: "medium"      # easy / medium / hard / insane
author: "ansihoo"
date: "2026-05-12"
points: 500
tags: [crypto, Base64]
---

# 문제명
baseball

## 문제 설명

바이너리를 분석하여 플래그를 얻어주세요.
얻은 플래그는 DH{<flag>} 형식으로 인증해주세요.

ELF 64비트 바이너리인 baseball, 평문 텍스트 text_in.txt, 그 인코딩 결과인 text_out.txt, 그리고 플래그가 인코딩된 flag_out.txt

- 문제 URL / 파일 등 접속 정보

## 풀이

### 분석

baseball 바이너리를 실행하면 Usage : ./baseball <table filename> <input filename> 메시지를 출력한다. 테이블 파일과 입력 파일 두 인자를 받는 구조로, 테이블을 기반으로 입력을 인코딩해 결과를 출력하는 프로그램임을 알 수 있다. text_out.txt를 보면 영문자, 숫자, 특수문자로 구성된 200자짜리 문자열이 담겨 있다. text_in.txt는 149바이트 평문이고, 표준 Base64로 인코딩하면 정확히 200자가 나온다. 즉, 이 바이너리는 커스텀 알파벳 테이블을 사용하는 Base64 인코더다. objdump로 바이너리를 역어셈블하면 핵심 동작을 확인할 수 있다. 프로그램은 첫 번째 인자로 받은 테이블 파일을 열어 정확히 64바이트를 읽고, 이를 Base64 인코딩의 치환 테이블로 사용한다. 그 뒤 두 번째 인자로 받은 입력 파일을 3바이트씩 읽으며 표준 Base64와 동일한 비트 분할(>> 2, & 3, << 4 등)을 수행하되, 결과 인덱스를 표준 알파벳 대신 로드한 커스텀 테이블에서 조회해 출력한다.

### 취약점

테이블 파일이 제공되지 않았지만, text_in.txt와 text_out.txt가 함께 주어져 있다. 평문과 암호문을 모두 알고 있으므로, 두 파일을 대조해 커스텀 알파벳 테이블을 역산(Known-Plaintext Attack)할 수 있다. Base64는 입력 3바이트를 6비트씩 네 개의 인덱스로 분리한 뒤 테이블에서 문자를 조회한다. 평문 바이트와 그에 대응하는 출력 문자를 알면 인덱스 → 문자 매핑을 직접 복원할 수 있다.

### 익스플로잇

149바이트 평문을 3바이트씩 순회하며 각 그룹에서 네 개의 인덱스와 그에 대응하는 출력 문자를 추출해 테이블을 재구성했다. 149 % 3 = 2이므로 마지막 그룹(2바이트)도 별도로 처리했다. 복원된 64자리 커스텀 알파벳은 다음과 같다. ?hs?RF/tuI?W3d?YnSvV7OUQbZcN4J2?1GL+ejA8?r?lpg5ak?Bo0qyDHm??M9?P
일부 인덱스는 평문에서 해당 인덱스가 한 번도 등장하지 않아 ?로 남았지만, flag_out.txt를 디코딩하는 데는 문제가 없었다. 이후 복원한 테이블로 역방향 딕셔너리(문자 → 인덱스)를 만들고, flag_out.txt의 각 문자를 6비트 값으로 변환한 뒤 8비트씩 묶어 바이트로 복원했다.

```python
import base64

text_in  = open('text_in.txt',  'rb').read()
text_out = open('text_out.txt', 'r').read().strip()
flag_out = open('flag_out.txt', 'r').read().strip()

table = ['?'] * 64

def record(idx, ch):
    if table[idx] == '?' or table[idx] == ch:
        table[idx] = ch

for i in range(0, len(text_in) - 2, 3):
    b0, b1, b2 = text_in[i], text_in[i+1], text_in[i+2]
    base = i // 3 * 4
    c0, c1, c2, c3 = text_out[base], text_out[base+1], text_out[base+2], text_out[base+3]
    record(b0 >> 2,                      c0)
    record(((b0 & 3) << 4) | (b1 >> 4), c1)
    record(((b1 & 0xf) << 2) | (b2 >> 6), c2)
    record(b2 & 0x3f,                    c3)

i = len(text_in) - 2
b0, b1 = text_in[i], text_in[i+1]
base = i // 3 * 4
c0, c1, c2 = text_out[base], text_out[base+1], text_out[base+2]
record(b0 >> 2,                      c0)
record(((b0 & 3) << 4) | (b1 >> 4), c1)
record(((b1 & 0xf) << 2),           c2)

char_to_idx = {c: i for i, c in enumerate(table) if c != '?'}

bits = []
for ch in flag_out:
    if ch == '=':
        break
    idx = char_to_idx[ch]
    for bit in range(5, -1, -1):
        bits.append((idx >> bit) & 1)

flag_bytes = bytes(
    sum(bits[i+j] << (7-j) for j in range(8))
    for i in range(0, len(bits) - 7, 8)
)

print(flag_bytes.decode())
```

## 플래그

```
DH{Did you know how base64 works}
```

## 배운 점

커스텀 Base64는 표준 알파벳 대신 임의의 64자리 문자열을 치환 테이블로 사용하는 변형이다. 알고리즘 자체는 표준과 동일하므로, 평문-암호문 쌍 하나만 있으면 테이블 전체를 복원할 수 있다. 바이너리 분석 없이도 출력 길이와 문자 구성만으로 Base64 계열 인코딩임을 빠르게 추측할 수 있다는 점도 유용한 경험이었다.
