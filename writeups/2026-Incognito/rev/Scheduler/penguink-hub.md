---
ctf_name: "Incognito 7.0"
challenge_name: "Scheduler"
category: "rev"            # web / pwn / rev / crypto / misc
difficulty: "medium"       # easy / medium / hard / insane
author: "penguink-hub"
date: "2026-04-14"
points: 350
tags: [reversing, scheduler, static-binary, input-validation]
---

# Scheduler

## 문제 설명

> 스레드 수, payload, priority, burst time을 입력해 내부 검증을 통과하면 vault에 접근할 수 있는 리버싱 문제이다.

- 문제 접속 정보: `nc ctf.axiosiiitl.dev 1337`
- 제공 파일: `scheduler_challenge`

## 풀이

### 분석

문제를 실행하면 먼저 생성할 thread 수를 입력받고, 이후 각 thread마다 payload, priority, burst time을 순서대로 입력받는다.

입력 형식은 다음과 같다.

- thread 개수: 1~4
- payload 선택
  - 1: X77
  - 2: Y88
  - 3: Z99
  - 4: W66
- priority
  - 0 = Highest
  - 99 = Lowest
- burst time

처음에는 단순히 payload를 1, 2, 3, 4 순서로 넣고 priority와 burst를 비슷한 값으로 맞춰 여러 번 시도했다.  
하지만 대부분 다음과 같은 실패 메시지만 출력되었다.

- `[-] STATE_LOCK_MAINTAINED`
- `[-] SYSTEM DIAGNOSTIC: Symmetric parameter anomaly detected.`
- `[-] FATAL_EXCEPTION`

이 결과를 통해 단순한 범위 검사가 아니라, 입력값 조합 자체를 이용한 내부 검증 로직이 존재한다고 판단할 수 있었다.

특히 다음과 같은 특징을 확인할 수 있었다.

1. thread 수는 4개를 모두 사용하는 경우가 가장 유력했다.
2. payload를 1, 2, 3, 4 순서로 넣는 것이 가장 자연스러운 흐름이었다.
3. 모든 priority와 burst를 지나치게 대칭적으로 넣으면 `Symmetric parameter anomaly detected`가 발생했다.
4. 일부 큰 값이나 비정상적인 입력에서는 `FATAL_EXCEPTION`이 발생했다.
5. 즉, 이 문제는 실제 스케줄러 구현을 묻는 문제가 아니라, 내부 검증식을 만족하는 입력 조합을 찾는 reversing 문제라고 볼 수 있었다.

문자열과 동작을 기준으로 보면 바이너리는 다음과 같은 구조를 가진다.

- 사용자 입력으로 여러 task를 구성한다.
- 각 task의 `payload`, `priority`, `burst` 값을 내부적으로 조합한다.
- 계산 결과가 특정 조건 또는 해시와 일치하면 성공 경로로 이동한다.
- 일치하지 않으면 `STATE_LOCK_MAINTAINED` 또는 `FATAL_EXCEPTION`으로 종료된다.

실제로 바이너리 동작상 최종 성공 경로에서는 `[+] 0xHASH_MATCH:` 문자열이 출력되는 것을 확인할 수 있었다.  
따라서 핵심은 이 분기문을 만족시키는 입력을 찾는 것이다.

### 취약점

이 문제는 메모리 오염이나 버퍼 오버플로우를 이용하는 문제가 아니다.  
핵심은 프로그램 내부의 입력 검증 로직을 역으로 분석해, 올바른 조합을 만드는 것이다.

즉, 취약점이라기보다는 다음과 같은 구조라고 보는 편이 맞다.

1. 프로그램이 thread별 입력값을 구조체 형태로 저장한다.
2. 저장된 값들을 기준으로 내부 상태를 계산한다.
3. 특정한 해시 또는 검증 조건을 만족하면 성공한다.
4. 그렇지 않으면 실패 메시지를 출력한다.

따라서 이 문제의 핵심은 숨겨진 검증식을 만족하는 입력 조합을 찾는 것이다.

### 익스플로잇

여러 번의 입력 실험 끝에 다음 값이 성공 조건을 만족하는 조합임을 확인할 수 있었다.

- thread 수: `4`

1번 thread
- payload: `1`
- priority: `0`
- burst: `560`

2번 thread
- payload: `2`
- priority: `0`
- burst: `561`

3번 thread
- payload: `3`
- priority: `0`
- burst: `562`

4번 thread
- payload: `4`
- priority: `0`
- burst: `700`

입력 순서를 그대로 적으면 다음과 같다.

```text
4
1
0
560
2
0
561
3
0
562
4
0
700
```

이 조합으로 내부 비교를 만족시키면 [+] 0xHASH_MATCH: 경로로 진입할 수 있다.
로컬 환경에서는 이후 flag.txt가 없을 수 있지만, 원격 서버에서는 이어서 플래그가 출력되는 구조로 보인다.이후 성공하면 내부 해시 검증을 통과하며 성공 경로로 진입한다.


결과적으로 정답 입력은 다음과 같다.
4
1 0 560
2 0 561
3 0 562
4 0 700

## 플래그

```
IIITL{REDACTED}
```

## 배운 점
이 문제는 제목만 보면 운영체제의 스케줄링 문제처럼 보이지만, 실제로는 입력 조합을 이용한 검증 로직을 역으로 분석하는 reversing 문제였다.

핵심 포인트는 다음과 같다.

1) 실패 메시지를 기준으로 분기 조건을 추정할 것
2) 대칭적인 입력이 실패한다는 점을 통해 단순 조합이 아님을 파악할 것
3) 최종적으로 특정 burst 조합을 맞춰 0xHASH_MATCH 경로를 열 것

