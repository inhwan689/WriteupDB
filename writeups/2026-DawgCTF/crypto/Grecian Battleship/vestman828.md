---
ctf_name: "2026-DawgCTF"
challenge_name: "Grecian Battleship"
category: "crypto"
difficulty: "medium"
author: "vestman828"
date: "2026-04-12"
tags: [crypto]
---

# Sussy Friend

## 문제 설명

> 2026-DawgCTF에 Grecian Battleship 문제입니다. Crypto입니다.

## 풀이

### 분석

1. 파일을 확인하니 ELF 실행파일 + PyInstaller 원파일 번들이었습니다.
2. 파일 끝의 MEI... 쿠키를 파싱해서 내부 TOC를 추출했습니다.
3. TOC에서 핵심 엔트리 battleship(파이썬 바이트코드)와 PYZ-00.pyz를 꺼냈습니다.
4. battleship 코드를 xdis로 디스어셈블해서 로직/상수를 읽었습니다.
5. 여기서 중요한 상수인 move_script를 얻었습니다:
   [(2,4), (2,3), (2,1), (0,0), (1,1), (3,1), (3,4), (2,2), (0,4), (3,3)]
6. 문제 제목이 ancient + cryptography라서, 이 좌표를 고전 5x5 좌표암호(Polybius/Playfair식)로 해석했습니다.
7. 표준 5x5 알파벳 격자(행-열)로 매핑하면 문자열이 POMAGRUNET로 나왔고, 실행파일 내부 다른 모듈/문자열엔 별도 플래그가
   없어 이 값을 플래그로 확정했습니다.

즉 핵심은 PyInstaller 역추출 -> battleship 바이트코드 분석 -> move_script 좌표를 고전 5x5 암호로 변환이었습니다.

### 익스플로잇

```python
(작성한 익스가 없음)
```

## 플래그

```
POMAGRUNET
```

## 배운 점

-
