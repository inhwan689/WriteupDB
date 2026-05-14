---
ctf_name: "Incognito 7.0"
challenge_name: "Never Gonna Give You Flag"
category: "misc"
difficulty: "medium"
author: ""
date: "2026-04-15"
points: 250
tags: [steganography, xor, rot13]
---
 
# Never Gonna Give You Flag
 
## 문제 설명
 
> Told you it's just another harmless file. A simple piece of code. Nothing unusual. Nothing hidden. Or is it so??
> Things aren't always what they look like. Sometimes, the real story lies beneath the surface — buried, fragmented, and carefully concealed.
> Follow the trail. Reconstruct what was broken. Uncover what was hidden. And when everything finally comes together… make sure you know how to use it.
 
- 첨부 파일: `chall.txt`
- URL: `https://rick-roll-0k02.onrender.com/`
 
## 풀이
 
`chall.txt`는 실제로 ZIP 앞에 데이터가 붙은 파일이다. ZIP 시그니처 위치를 찾아 분리하면 앞부분은 난독화된 C++ 코드, ZIP 내부엔 `x/a`, `x/b`, `x/c`, `x/hehe.h`, `x/i`(JPEG)가 있다.
 
앞의 C++ 코드는 `#define haha 10` 기반으로 문자를 생성하는데, 오프셋을 계산하면 URL `https://tinyurl.com/g0t-y0u4-ur1`이 나온다.
 
`x/a`의 `IMG_KEY = "rickroll_key_123"`으로 JPEG에서 steghide로 `Decrypt.jar`를 추출한다. (`x/hehe.h`의 `random_key_456`은 함정)
 
`Decrypt.jar`를 `javap -c`로 분석하면 사용법과 알고리즘을 알 수 있다.
 
```
Usage: java Decrypt "[part1]|[part2]|[part3]"
```
 
- **part1**: Caesar unshift (shift = -17)
- **part2**: hex → XOR(`"secret"`) → Base64 decode
- **part3**: ROT13 → reverse
 
`https://rick-roll-0k02.onrender.com/`에 tinyurl을 입력하면 Output Panel에 입력값이 출력됨.
 
```
[ZZZKC{i1tb_45]|[1721260800224b1d2d245c073e57000807134e58]|[A01G4P5HSO0}q]
```
 
### 익스플로잇
 
```python
import base64
 
def caesar_unshift(s, shift=17):
    result = ""
    for c in s:
        if c.isupper():
            result += chr((ord(c) - 65 - shift + 26) % 26 + 65)
        elif c.islower():
            result += chr((ord(c) - 97 - shift + 26) % 26 + 97)
        else:
            result += c
    return result
 
def xor_decrypt(data, key="secret"):
    return bytes([b ^ ord(key[i % len(key)]) for i, b in enumerate(data)])
 
def rot13(s):
    result = ""
    for c in s:
        if c.isupper():
            result += chr((ord(c) - 65 + 13) % 26 + 65)
        elif c.islower():
            result += chr((ord(c) - 97 + 13) % 26 + 97)
        else:
            result += c
    return result
 
part1 = caesar_unshift("ZZZKC{i1tb_45")
part2 = base64.b64decode(xor_decrypt(bytes.fromhex("1721260800224b1d2d245c073e57000807134e58"))).decode()
part3 = rot13("A01G4P5HSO0}q")[::-1]
 
print(part1 + part2 + part3.split("}")[0] + "}")
```
 
## 플래그
 
```
IIITL{r1ck_45t13y_15_l3g3nd}
```
 
## 배운 점
 
- `file` 명령어로 실제 파일 형식을 확인해야 한다.
- 난독화 코드는 매크로 값을 역추적하면 숨겨진 문자열을 복원할 수 있다.
- `steghide` 사용 시 올바른 키를 찾는 것이 중요하며, 함정 키를 주의해야 한다.
- Java `.class` 파일은 `javap -c`로 알고리즘을 역분석할 수 있다.