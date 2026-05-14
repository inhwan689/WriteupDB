---
ctf_name: "UMass CTF 2026"
challenge_name: "Batcave Bitflips"
category: "rev"           # web / pwn / rev / crypto / misc
difficulty: "medium"      # easy / medium / hard / insane
author: "ttzero25"
date: "2026-04-11"
points: 100
tags: [XOR, custom hash, bitflip]
---

# 문제명
Batcave Bitflips

## 문제 설명
Batman's new state-of-the-art AI agent has deleted all of the source code to the Batcave license verification program! There's an old debug version lying around, but that thing has been hit by more cosmic rays than Superman!

- https://ctf.umasscybersec.org/challenges#Batcave%20Bitflips-13

## 풀이

### 분석

1. IDA로 main 함수 흐름 파악
```
입력 (fgets)
  → hash(입력값, var_50)        커스텀 해시 계산, 결과를 var_50에 저장
  → bytes_to_hex(var_50, 0x20)  해시를 hex 문자열로 변환해 화면에 출력
  → verify(var_50)              해시값이 EXPECTED와 일치하는지 검증
  → decrypt_flag(var_50)        해시값을 키로 FLAG 복호화
  → FLAG 출력
```

2. verify 함수 확인 -> `memcmp`로 입력값의 해시 32바이트를 바이너리 내 `EXPECTED`와 비교
```asm
mov  edx, 20h        ; 비교 길이 = 32바이트
lea  rcx, EXPECTED   ; 정답 해시 (하드코딩)
call _memcmp         ; hash(입력값) == EXPECTED ?
```

여기서 hash 함수는 `substitute`, `mix`, `derive_final`, `expand_state` 등의 서브루틴을 사용하는 커스텀 알고리즘. 
역산이 불가능하고 CrackStation 크랙도 실패. 

3. 그대신 심볼 테이블을 확인
```
0x4020  LICENSE_KEY   ← 라이선스 키가 .data에 저장되어 있음
0x4040  EXPECTED      ← 정답 해시값
0x4060  FLAG          ← 암호화된 플래그
```

바이너리에서 직접 추출 결과는 아래와 같음:

```python
with open('batcave_license_checker', 'rb') as f:
    data = f.read()

data_offset = 0x3000  # .data 섹션 파일 오프셋

license_key = data[data_offset + 0x20 : data_offset + 0x40]
expected    = data[data_offset + 0x40 : data_offset + 0x60]
flag_enc    = data[data_offset + 0x60 : data_offset + 0x80]
```

```
LICENSE_KEY  :  !_batman-robin-alfred_((67||67))
EXPECTED     :  3b54751a2406af05778047c5e483d348cb8730de1a9145ab15c79b2204022bee
FLAG (암호화) :  6e193449777df05a07b433a68ce6e617fbe96fae2ee526c370e3c47d277f2b00
```

라이선스 키가 바이너리에 하드코딩되어 있음을 확인함


### 취약점

`decrypt_flag` 함수의 핵심 루프를 디스어셈블 했을 때 발견할 수 있었던 건,

```asm
movzx  ecx, byte ptr [FLAG + i]   ; FLAG[i] 읽기
movzx  eax, byte ptr [key + i]    ; key[i] 읽기
or     ecx, eax                    ; FLAG[i] = FLAG[i] | key[i]  ← 수상함
mov    byte ptr [FLAG + i], cl
```

연산이 OR (`|`, opcode `0x09`)인데, OR은 비트를 되돌릴 수 없어 복호화 연산으로 사용할 수 없다. 실제로 OR로 계산하면 읽을 수 없는 값이 나온다.

여기서 문제 제목 "bitflips"을 근거로 원래 코드는 XOR (`^`, opcode `0x31`)이었는데 출제자가 opcode 바이트를 직접 수정해 OR로 바꿔놓은 것이라 예상

```
XOR opcode: 0x31  =  0011 0001
OR  opcode: 0x09  =  0000 1001
                     ↑↑     ↑   ← 비트가 뒤집혀 있음
```


### 익스플로잇

올바른 라이선스 키(`LICENSE_KEY`)를 입력하면 `hash(입력값) == EXPECTED`가 성립하므로, 복호화 키는 EXPECTED와 동일
OR 대신 XOR로 복호화하면 FLAG를 얻을 수 있음

```python
flag_enc = bytes.fromhex('6e193449777df05a07b433a68ce6e617fbe96fae2ee526c370e3c47d277f2b00')
key      = bytes.fromhex('3b54751a2406af05778047c5e483d348cb8730de1a9145ab15c79b2204022bee')

flag = bytes([flag_enc[i] ^ key[i] for i in range(32)])
print(flag.split(b'\x00')[0].decode())
```


## 플래그

```
UMASS{__p4tche5_0n_p4tche$__#}
```

## 배운 점

- OR과 XOR의 차이. OR은 비트를 0→1로만 바꾸므로 되돌릴 수 없다. 복호화/암호화에는 XOR을 사용하며, XOR은 같은 키로 두 번 연산하면 원래 값으로 돌아오는 성질이 있다.
