---
ctf_name: "SillyCTF2"
challenge_name: "The End of Linux"
category: "web"           # web / pwn / rev / crypto / misc
difficulty: "easy"      # easy / medium / hard / insane
author: "pwnppy"
date: "2026-04-05"
points: 500
tags: [web]
---

# The End of Linux

## 문제 설명

> y2k

- **문제 분류**: Web

## 풀이

### 분석

문제의 제목 'The End of Linux'와 설명 'y2k'는 시간 표현 방식과 관련된 문제임을 보여준다. 유닉스/리눅스 기반 시스템은 시간을 1970년 1월 1일 00:00:00 UTC부터 경과한 초(Seconds) 단위로 계산하는 **Unix Timestamp**를 사용한다.

### 취약점

이 문제의 핵심 취약점은 **정수 오버플로우(Integer Overflow)** 이다.

32비트 유닉스 시스템에서 시간을 저장하는 `time_t` 자료형은 부호가 있는 32비트 정수(Signed 32-bit Integer)를 사용한다. 이 자료형이 가질 수 있는 최대값은 $2^{31} - 1$인 **2,147,483,647**이며, 이 시간은 **2038년 1월 19일 03:14:07 UTC**에 해당한다. 

만약 서버가 입력받은 `timestamp`를 32비트 정수형으로 처리하거나 특정 임계값(2038년 문제 등)을 검증하는 로직이 있다면, 해당 값을 초과하는 데이터를 보냄으로써 의도하지 않은 동작(Flag 출력 등)을 유도할 수 있다.

### 익스플로잇

1. **대상 값 선정**: 
    - `2147483648`: $2^{31}$ (32비트 부호 있는 정수 최대값 + 1)
    - `2147483649`: $2^{31} + 1$
    - `4294967295`: $2^{32} - 1$ (32비트 부호 없는 정수 최대값)
2. **Fetch API를 이용한 스크립트 실행**:

```javascript
const targets = [2147483648, 2147483649, 4294967295];

targets.forEach(t => {
    fetch('/api/status', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ timestamp: t })
    })
    .then(res => res.json())
    .then(data => {
        console.log(`Send [${t}]:`, data);
        if (data.flag) console.warn("!!! FLAG !!!", data.flag);
    });
});
```

## 플래그

```
sillyctf{maybe_n0t_the_3nd}
```

## 배운 점

**Data Type Limits**: 정수형 자료형의 범위(Signed vs Unsigned)에 따른 오버플로우 가능성을 생각해야 한다.
