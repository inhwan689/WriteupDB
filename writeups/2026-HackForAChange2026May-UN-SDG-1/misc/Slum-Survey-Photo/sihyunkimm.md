---
ctf_name: "Hack For A Change 2026 May: UN-SDG-1"
challenge_name: "Slum-Survey-Photo"
category: "misc"
difficulty: "easy"
author: "sihyunkimm"
date: "2026-05-19"
points: 100
tags: [Steganography, Text-Extraction]
---

# Slum-Survey-Photo

## 문제 설명

> 주어진 이미지 파일에서 플래그를 찾는 문제

- 제공 파일: 이미지 파일 (슬럼 조사 관련 사진)

## 풀이

### 분석

주어진 이미지 파일을 일반적인 이미지 뷰어로 보면 특별한 흔적이 보이지 않습니다. 그러나 이미지 파일은 바이너리 데이터이며, 텍스트 편집기로 열면 파일에 내장된 텍스트 데이터를 볼 수 있습니다.

### 취약점

이 문제는 Steganography의 가장 기초적인 형태입니다. 해킹이라기보단 이미지 파일에 평문 텍스트를 직접 임베드하는 방식으로, 텍스트 편집기에서 읽을 수 있는 수준의 취약한 은닉입니다.

### 익스플로잇

1. 제공받은 이미지 파일을 텍스트 에디터(메모장, VSCode 등)로 엽니다.
2. Ctrl+F (또는 Cmd+F)를 눌러 플래그 시작 문구인 "SDG"를 검색합니다.
3. 검색 결과에서 플래그 전체를 확인할 수 있습니다.


## 플래그

```
SDG{REDACTED}
```

## 배운 점

