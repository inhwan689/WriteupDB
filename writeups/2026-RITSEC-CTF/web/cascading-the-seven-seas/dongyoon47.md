---
ctf_name: "RISTEC CTF 2026"
challenge_name: "Cascading the seven sea"
category: "web"           # web / pwn / rev / crypto / misc
difficulty: "easy"      # easy / medium / hard / insane
author: "dongyoon47"
date: "2026-04-05"
points: 10
tags: [web, css]
---

# Cascading the sever sea

## 문제 설명

don't worry i consulted a marine biologist on this one...
Author: sy1vi3
- https://css.ctf.ritsec.club/

## 풀이
처음 접속했을 때 브라우저가 지원 안 된다는 검은 경고창이 떠서 일단 그거부터 해결해야 해서 크롬에서 실험 기능 켜고 다시 들어가니까 그제서야 정상적으로 문제 화면이 뜸
화면에는 0~9, QWERTYUIOP, ASDFGHJKL, _, {, }, RETURN 같은 버튼들이 있음
이걸 보고 뭔가 문자열을 직접 입력하는 형식이라고 생각
DevTools로 CSS를 확인해보니까 실제로 각 버튼이 눌릴 때마다 --keyboard 값에 아스키 코드가 들어가도록 되어 있음 자바스크립트가 아니라 CSS만으로 입력 처리랑 출력까지 다 하도록 만든 문제
소스를 더 보면 AX, BX, CX, DX, IP 같은 레지스터 비슷한 값들이랑 메모리처럼 보이는 값들이 엄청 많고
문제는 질문이 3개 나오고 거기에 맞는 답을 순서대로 입력한 뒤 RETURN을 누르면 다음으로 넘어가는 방식
이거 입력
1.	PACIFIC 
2.	HORSE 
3.	RS{CR3D1T_T0_LYR4_R3B4N3_F1BDF5} 
플래그는 RS{CR3D1T_T0_LYR4_R3B4N3_F1BDF5}

### 분석

### 취약점

### 익스플로잇

```python
# 풀이 코드 예시
```

## 플래그

```
RS{CR3D1T_T0_LYR4_R3B4N3_F1BDF5}
```

## 배운 점

