---
ctf_name: "RITSECCTF"
challenge_name: "Cascading the Seven Seas"
category: "Web"           # web / pwn / rev / crypto / misc
difficulty: "easy"      # easy / medium / hard / insane
author: "junseok-dubu"
date: "2026-04-05"
points: 100
tags: [태그1, 태그2]
---

# 문제명

Cascading the Seven Seas

## 문제 설명

> 문제에서 주어진 설명을 여기에 작성합니다.

- don't worry i consulted a marine biologist on this one...
- https://css.ctf.ritsec.club/

## 풀이

해당 사이트로 들어가서 개발자도구 F12 키를 누르면 css 가 뜬다. css 내부에 정답 문자열이 들어가있는 메

### 분석

문제 사이트에 접속해 개발자도구를 열어 보니, 일반적인 웹 문제처럼 서버와 통신하며 정답을 검증하는 구조가 아니라 브라우저 내부의 CSS와 JavaScript로 동작하는 형태였다. 특히 `.cpu` 요소의 CSS 커스텀 변수에 레지스터와 메모리처럼 보이는 값들이 저장되어 있었고, `--m숫자` 형태의 변수들이 대량으로 존재했다. 실제 덤프에는 `--m256 = 86`, `--m257 = 85`처럼 바이트 코드처럼 보이는 값과 함께 문제 문자열에 해당하는 ASCII 값도 들어 있었다.

메모리 구간을 아스키로 변환해 보니 문제 문장이 복원되었다.

- 1. Which ocean is the largest?
- 2. Name an aquatic mammal:
- 3. What's the flag?

또한 정답/오답 메시지에 해당하는 문자열도 메모리에 포함되어 있었다. 예를 들어 `--m1218` 이후에는 `You win!!! Press any key to exit`, `--m1259` 이후에는 `Incorrect. Press any key to exit`가 들어 있었다.

### 취약점

이 문제의 취약점은 정답 검증 로직과 문제 데이터가 서버가 아니라 클라이언트 측 CSS/JS에 노출되어 있다는 점이다.

- 개발자도구로 CSS 변수 확인
- 메모리처럼 저장된 문자열 복원
- 코드 흐름 및 검증 방식 분석

을 통해 문제 내용을 직접 알아낼 수 있었다.

### 익스플로잇

1. 사이트 접속 후 개발자도구를 열었다.
2. `.cpu` 요소의 CSS 커스텀 변수를 확인했다.
3. `--m1299 ~ --m1390` 구간을 아스키 문자로 변환해 문제 문장을 복원했다.
4. 1번 문제는 일반 상식이므로 `PACIFIC`을 입력했다.
5. 2번 문제는 처음에는 `WHALE`, `DOLPHIN` 등을 시도했으나 틀렸다.
6. 문제 설명의 `consulted a marine biologist on this one` 문구를 힌트로 보고, 일반적인 aquatic mammal 정답이 아니라 말장난을 유도한다고 판단했다.
7. `SEAHORSE`를 떠올렸고, 입력은 한 단어만 받는 형태이므로 `HORSE`를 입력해 통과했다.
8. 3번 문제는 `What's the flag?`였고, 이후 m256 이후의 바이트코드와 m800대의 규칙적인 값들을 보고, 플래그를 직접 저장한 것이 아니라 문자들에 대한 검증 테이블이라고 판단했다.
9. 플래그 형식이 RS{로 시작하고 }로 끝난다고 두고, 안에 있는 문자를 복원했다.
10. 그 결과 최종 플래그는 RS{CR3D1T_T0_LYR4_R3B4N3_F1BDF5}로 구할 수 있었다.


```python
# 풀이 코드 예시

s = getComputedStyle(document.querySelector('.cpu')) out = '' 
for i in range(1299, 1391): 
	v = int(s.getPropertyValue(f'--m{i}').strip() or 0) 
	out += '\n' if v == 0 else chr(v) 
print(out)
```

## 플래그

```
RS{CR3D1T_T0_LYR4_R3B4N3_F1BDF5}
```

## 배운 점

이 문제를 통해 웹 문제라고 해서 반드시 서버 취약점만 보는 것이 아니라, 클라이언트 측 코드와 CSS까지 자세히 분석해야 한다는 점을 배웠다. 또한 문제 설명 문구 하나가 단순 장식이 아니라 정답 추론에 직접 연결되는 힌트가 될 수 있다는 점도 다시 확인할 수 있었다.
