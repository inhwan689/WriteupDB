---
ctf_name: "UN SDG 3"
challenge_name: "EHR Parameter Pollution"
category: "web"
difficulty: "easy"
author: "sihyunkimm"
date: "2026-03-31"
points: 100
tags: [parameter-pollution, authorization-bypass]
---

# EHR Parameter Pollution

## 문제 설명

> EHR 시스템에서 특정 환자 정보 조회 API가 HTTP Parameter Pollution에 취약하다는 상황이 주어집니다.

## 풀이

### 분석

초기에는 아무 커스텀 파라미터를 추가해 요청을 보냈고, 서버가 `patient_id not in authorized list` 오류를 반환.  
이후 `verify access` 요청에서 `Get the SYS-ADMIN record first to obtain the admin_access_code.` 메시지를 획득. 즉, SYS-ADMIN 레코드 접근이 가능한 형태로 파라미터를 조작하면 Access code에 접근할 수 있음. 이를 제출해 Flag 획득.

### 취약점

1. HTTP Parameter Pollution
2. 과도한 에러 메시지 노출

### 익스플로잇

1. Additional query parameters 에 앞서 알아낸 &patient_id=SYS-ADMIN 를 제출
2. 응답으로 반환되는 Access code를 확보하고 이를 다시 제출해 Flag 획득

## 플래그

```
SDG{REDACTED}
```

## 배운 점

- 자세한 에러 메시지는 개발 과정에서는 도움이 되지만 외부로 노출되면 약점이 될 수 있다는 것을 알게 됨.
