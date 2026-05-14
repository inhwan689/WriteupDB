---
ctf_name: "2026-VishwaCTF"
challenge_name: "Sunny Day Picnic"
category: "stego"
difficulty: "medium"
author: "vestman828"
date: "2026-04-05"
tags: [LSB]
---

# Sunny Day Picnic

## 문제 설명

> 2026-VishwaCTF에 Sunny Day Picnic 문제입니다. Stego입니다.

## 풀이

### 분석

  1. picnic.png 기본 점검

  - strings/hex 확인 시 EXIF 쪽에 VishwaCTF{41_m0d31_d3t3ct3d_try_h4rd3r}가 보였지만, 힌트(“obvious trap 주의”) 때문에
    미끼 문자열로 판단했습니다.

  2. PNG 끝부분(append data) 확인

  - PNG는 IEND 청크로 끝나야 하는데, 파일 길이와 IEND 종료 위치를 비교하니 뒤에 198바이트가 추가되어 있었습니다.
  - 이 tail 데이터를 잘라보니 PK... 시그니처가 있는 ZIP 데이터였습니다. (힌트 2와 일치)

  3. EXIF 메타데이터(위치 정보) 추출

  - eXIf 청크를 TIFF 형식으로 파싱해서 GPS 태그를 읽었습니다.
  - 좌표: 12.3456, 78.9101 (힌트 4와 일치)

  4. LSB 스테가노그래피 복원

  - 이미지 RGB 채널의 LSB를 여러 방식으로 추출해보니, RGB interleaved LSB에서
    K3Y_X0r_w1th_GPS_C00rd1n4t3s!_ 가 나왔습니다. (힌트 3과 일치)

  5. XOR로 최종 키 생성

  - 힌트 1대로, 위 LSB 문자열과 GPS 문자열(12.3456,78.9101)을 반복 XOR해서 키 바이트를 만들고, 이를 hex 문자열로 사용:
  - 7a01776c6c05447340095a516e7761626d6d030447521d590c5a0a42116e

  6. 숨겨진 ZIP 복호화

  - 위 hex 문자열을 ZIP 비밀번호로 넣어 flag.txt 복호화 성공.

### 익스플로잇

```python
(삭제해버려서 첨부하지 못했습니다..)
```

## 플래그

```
VishwaCTF{steg0_1s_h4rd_but_Fun}
```

## 배운 점

Weight 40아래인 Bad CTF는 거르자
