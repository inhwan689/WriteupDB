---
ctf_name: "Dreamhack"
challenge_name: "Secure-Mail"
category: "rev"           # web / pwn / rev / crypto / misc
difficulty: "medium"      # easy / medium / hard / insane
author: "ansihoo"
date: "2026-05-05"
points: 500
tags: [태그1, 태그2]
---

# 문제명

## 문제 설명

> 중요한 정보가 적혀있는 보안 메일을 발견하였습니다.

보안 메일의 비밀번호는 생년월일 6자리인 것으로 파악되나, 저희는 비밀번호 정보를 가지고 있지 않습니다.

비밀번호를 알아내고 보안 메일을 읽어 중요한 정보를 알아내주세요!

입력 힌트: placeholder="Input your birthday eg.) 850810" → 6자리, 숫자만

## 풀이

### 분석

문제 파일을 열어보니 단일 HTML 안에 한 줄짜리 난독화된 자바스크립트가 들어 있었다. 정적으로 읽기는 어려웠지만, Confirm 버튼이 호출하는 검증 함수를 따라가 보니 비밀번호를 어떤 해시로 변환해 키를 만들고 그 키로 미리 박혀 있는 큰 바이트 배열을 복호화한 뒤, 복호화 결과를 다시 해시해서 정해진 값과 비교하는 구조였다. 비교가 통과되면 결과 문자열을 이미지 태그의 src로 출력하는 흐름이었다.
식별해야 할 요소는 해시 함수, 대칭키 알고리즘, 비교 대상 해시값 세 가지였다. 코드를 직접 읽기보다 Node의 vm 모듈로 스크립트를 컨텍스트에 로드한 뒤 함수와 객체를 직접 호출해 동적으로 식별했다. 빈 문자열을 해시했을 때 결과가 d41d8cd98f00b204e9800998ecf8427e로 나왔는데 이는 MD5의 알려진 값과 일치했다. 대칭키 클래스의 toString 결과 안에는 "Cipher Block Chaining" 문자열과 IV 길이 16바이트 검증이 있었고, 형제 속성에 Counter와 padding이 있었다. 이는 aes-js 라이브러리의 CBC 모드와 정확히 일치하는 시그니처라서 알고리즘은 AES-128-CBC였고, 키와 IV는 모두 MD5의 16바이트가 동일하게 사용되며 패딩 제거 없이 raw 블록 단위로 복호화되는 구조였다. 비교 대상 해시값은 코드 내 문자열 디코더를 직접 호출해 b6a2741a0f734e251a150c5ffe593ca6라는 16바이트로 추출했다.

### 취약점

이 문제의 핵심 약점은 키 공간이 너무 좁다는 것이다. 비밀번호가 6자리 숫자라 단순 계산으로는 100만 조합이지만, 유효한 YYMMDD는 약 37,000개로 줄어든다. 검증이 전적으로 클라이언트 측에서 이뤄지고 서버 통신이 없기 때문에 횟수 제한 없이 오프라인 브루트포스가 가능하다. 키와 IV를 같은 값으로 쓴 것도 CBC의 권장 사용법에서 벗어나는 패턴이며, 난독화는 정적 분석에 드는 시간을 늘릴 뿐 알고리즘을 숨겨주지는 못했다.

### 익스플로잇

처음에는 난독화된 검증 함수를 그대로 호출해 브루트포스를 시도했지만 한 번 호출에 약 1.1초가 걸려 전체 11시간 이상이 필요한 상황이었다. 그래서 분석한 알고리즘을 표준 crypto 라이브러리로 다시 구현해 속도를 끌어올렸다. 암호문 배열은 검증 함수가 한 번 호출되면 함수 내부에서 var 키워드 없이 할당돼 전역에 누출되는 구조라, 임의 비밀번호로 한 번 호출한 뒤 전역에서 읽어 와 바이너리로 저장했다. 그 다음 파이썬에서 동일 검증을 재구현했다.
전체 후보를 약 11초 만에 순회했고 35,124번째에서 일치를 찾았다. 정답은 960229로, 1996년 2월 29일이라는 윤년 생일이라 일반 순서 브루트포스에서는 비교적 뒤쪽에 있었다. 복호화된 평문은 data:image/png;base64로 시작하는 데이터 URL이었고, base64 부분만 디코딩하니 PNG 이미지가 복원되었다. 이미지에는 흰 배경에 검은 글씨로 플래그가 적혀 있었다.
```python
import hashlib
from Crypto.Cipher import AES
from datetime import datetime

ciphertext = open('cipher.bin', 'rb').read()
EXPECTED = bytes.fromhex('b6a2741a0f734e251a150c5ffe593ca6')

def try_pass(p):
    key = hashlib.md5(p.encode()).digest()
    cipher = AES.new(key, AES.MODE_CBC, key)
    plain = cipher.decrypt(ciphertext)
    if hashlib.md5(plain).digest() == EXPECTED:
        return plain
    return None

for yy in range(100):
    for mm in range(1, 13):
        for dd in range(1, 32):
            try:
                datetime(2000 + yy if yy < 30 else 1900 + yy, mm, dd)
            except ValueError:
                continue
            p = f'{yy:02d}{mm:02d}{dd:02d}'
            plain = try_pass(p)
            if plain:
                print('FOUND:', p)
                open('plain.txt', 'wb').write(plain)
                raise SystemExit
```

## 플래그

```
DH{Brutef0rce_th3_secur3_mail}
```

## 배운 점

가장 크게 느낀 것은 클라이언트 측 검증은 그 자체로 보안 수단이 될 수 없다는 점이다. 검증 로직과 암호문이 모두 사용자 쪽에 노출되는 환경에서는 키 공간이 작으면 시간 문제로 풀리며, 6자리 생년월일처럼 가짓수가 적은 입력을 단독 키 재료로 쓰는 설계는 위험하다는 것을 체감했다. 실무에서는 PBKDF2나 Argon2 같은 KDF로 키를 늘리거나 서버 측 시도 횟수 제한과 결합해야 의미 있는 방어가 된다. 또한 난독화는 암호화가 아니라는 점을 다시 확인했다. Node vm이나 브라우저 개발자 도구처럼 동적 실행이 가능한 환경에서는 함수와 객체를 직접 호출할 수 있어 알고리즘이 금방 드러나며, MD5 같은 표준 해시는 known answer 한 번이면 식별이 끝난다. 마지막으로 속도 측면에서, 난독화 함수를 그대로 호출해 브루트포스했을 때 비현실적이던 11시간이 알고리즘만 표준 라이브러리로 옮겨 다시 짜니 11초로 줄어든 경험을 통해, 무조건 빠른 풀이를 짜기보다 병목을 식별해 그 부분만 재구현하는 접근이 훨씬 효율적이라는 점을 배웠다.
