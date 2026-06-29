---
ctf_name: "RIFFHACK"
challenge_name: "Moon Prism Packet Secrets"
category: "misc"           # web / pwn / rev / crypto / misc
difficulty: "easy"      # easy / medium / hard / insane
author: "aswe0810m"
date: "2026-06-23"
points: 50
tags: [forensic, file-carving]
---

# Moon Prism Packet Secrets

## 문제 설명

> A late-night idol rehearsal leak includes one selfie and a whisper of intercepted packets. The photo looks harmless, but the gradient refuses to keep the guardians' secret quiet.

- 제공 파일: `luna_selfie.png`, `moon_chat.pcap`

## 풀이

### 분석

PNG 파일은 640x360 RGB 이미지(5743 bytes)이고, pcap은 694 bytes짜리 소규모 패킷 캡처 파일이다.
pcap에 UDP 패킷 6개로 구성된 Artemis-Luna 대화가 들어 있다:

Artemis: That idol selfie felt too heavy. Did you stash the intel?

Luna: Affirmative. Append the rehearsal diary after the MOONSHINE marker.

Artemis: Got it. Carve after the sentinel, it's still a ZIP.

Luna: Remember, the instructions live only in this capture. Delete after listening.

대화 내용으로부터 PNG 안에 MOONSHINE 마커 뒤로 ZIP이 숨겨져 있다는 힌트를 얻는다.

### 취약점

PNG 파일 포맷은 `IEND` 청크 이후의 데이터를 무시한다. 이 특성을 이용해서 `IEND` 뒤에 임의의 데이터를 append해도 이미지 뷰어에서는 정상적으로 렌더링된다.
실제 파일 구조: [PNG 이미지 데이터] [IEND @ offset 5397] [\n] [MOONSHINE @ 5406] [\n] [ZIP(PK) @ 5416]

### 익스플로잇

1. PNG의 `IEND` 이후 338바이트의 추가 데이터 확인
2. `MOONSHINE` sentinel 마커 뒤에서 `PK\x03\x04` ZIP 시그니처 발견
3. ZIP을 carve하여 추출, 내부에 `diary_entry.txt` 존재

```python
data = open('luna_selfie.png', 'rb').read()
pk_offset = data.find(b'PK\x03\x04')
open('hidden.zip', 'wb').write(data[pk_offset:])
# unzip hidden.zip -> diary_entry.txt -> flag
```

## 플래그

```
bitctf{{m00n_pr15m_p4yl04d}}
```

## 배운 점

- PNG는 `IEND` 이후 데이터를 무시하는데, 이건 PNG만의 특성이 아니라 대부분의 파일 포맷에 해당한다. JPEG는 `FF D9`(EOI) 뒤를, ZIP은 End of Central Directory부터 역방향으로 파싱하므로 앞에 데이터가 붙어도 동작한다. 즉 "뷰어에서 정상으로 보인다 ≠ 파일이 깨끗하다"를 항상 전제해야 한다.
- 파일 시그니처(매직 바이트)를 기준으로 데이터를 식별하고 추출하는 기법을 File Carving이라 한다. 이번에는 `PK\x03\x04`로 ZIP을 수동 추출했는데, `binwalk`, `foremost`, `scalpel` 같은 도구로 자동화할 수도 있다.
- pcap은 네트워크 패킷을 그대로 저장한 파일이며, Global Header → (Packet Header + Data) 반복 구조로 되어 있다. 이번에는 `strings`만으로 충분했지만, 실전에서는 Wireshark로 TCP stream reassembly, HTTP object 추출, DNS exfiltration 탐지 등을 다루게 된다.
- 문제에서 제공하는 모든 파일을 분석해야 한다. 이 문제에서는 pcap이 PNG 은닉 방식에 대한 힌트 역할이었다.
