---
ctf_name: "BreakTheSyntaxCTF"
challenge_name: "pokecollector"
category: "web"           # web / pwn / rev / crypto / misc
difficulty: "easy"      # easy / medium / hard / insane
author: "pwnppy"
date: "2026-05-10"
points: 50
tags: [web]
---

# pokecollector

## 문제 설명

> Opening card packs has become painfully expensive, so I wrote an app to open Pokemon packs. Mewtwo is mine though.

## 풀이

### 분석

`app.js` 소스 코드를 분석하면 사용자가 카드를 확인했을 때 호출되는 `saveToCollection(pokemonId, pokemonName)` 함수를 확인할 수 있다. 

이 함수는 `/api/collection/add` 엔드포인트로 `pokemon_id`와 `pokemon_name`을 포함한 JSON 데이터를 `POST` 요청으로 보낸다. 서버 측에서 해당 포켓몬을 실제로 획득했는지에 대한 별도의 검증 절차가 없으므로, 개발자 도구(Console)를 통해 직접 함수를 호출하여 컬렉션에 추가할 수 있다.

### 익스플로잇

로그인 후 브라우저 콘솔창에서 아래 코드를 실행하여 ID가 150번인 뮤츠를 강제로 컬렉션에 추가한다.

```javascript
await saveToCollection(150, "Mewtwo");
navigateTo('collection');
```

## 플래그

```
BtSCTF{g1t_g0tt4_c4tch_3m_4ll}
```

## 배운 점

클라이언트 사이드에서 서버로 전달하는 데이터는 변조될 수 있으므로, 중요한 로직은 반드시 서버 측에서 검증해야 한다.
