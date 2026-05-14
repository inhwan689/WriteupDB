---
ctf_name: "UMassCTF"
challenge_name: "BrOWSER BOSS FIGHT"
category: "web"           # web / pwn / rev / crypto / misc
difficulty: "easy"      # easy / medium / hard / insane
author: "kimrebin"
date: "2026-04-12"
points: 100
tags: [태그1, 태그2]
---

# 문제명
BrOWSER BOSS FIGHT
## 문제 설명

> This familiar brick castle is hiding something... can you break in and defeat the Koopa King?

- http://browser-boss-fight.web.ctf.umasscybersec.org:32770

## 풀이

### 분석

제시된 url로 접속해 보면 input key를 받는 입력창과 잠긴 문 이미지의 버튼이 있다. 올바른 input key를 입력해야 무언가를 얻을 수 있을 것 같다. 하지만 input key를 임의로 입력하면 내가 무엇을 입력하든, key의 값은 다음 스크립트 코드에 의해 "WEAK_NON_KOOPA_KNOCK"라는 값으로 바뀐 후 서버에 전송된다. 그리고는 key를 시도하지 말라는 문구가 쓰인 kamek.html로 리다이렉트된다.


            document.getElementById('key-form').onsubmit = function() {
                const knockOnDoor = document.getElementById('key');
                // It replaces whatever they typed with 'WEAK_NON_KOOPA_KNOCK'
                knockOnDoor.value = "WEAK_NON_KOOPA_KNOCK"; 
                return true; 
            };
        

### 취약점

브라우저에서 어떤 input key를 넣든 key의 값을 고정해서 보내지만, 이를 burpsuite에서 낚아채서 key값을 바꿔 보낼 수 있다.

### 익스플로잇

burpsuite를 이용하여 브라우저에서 key를 아무거나 써서 보내고 서버 응답을 관찰한다. 그럼 리다이렉트가 되기 전에 서버로부터 302응답이 온다. 그 패킷을 살펴보면 다음과 같이 힌트가 적혀있다:
A note outside: "King Koopa, if you forget the key, check under_the_doormat! - Sincerely, your faithful servant, Kamek"

under_the_doormat를 확인해보라는 힌트를 얻어, key의 값을 burpsuite로 "under_the_doormat"로 수정한 후 서버로 보내면, "bowsers_castle.html"으로 리다이렉트를 성공하게 된다. 이 페이지에서는 다음과 같은 문구가 적혀있었다:
I don't know how you got in, but you can't possibly defeat me! I removed the axe!

여기서 axe가 있어야 진행할 수 있다는 것을 알 수 있다. 다시 이 페이지를 새로고침하여 서버로 오는 패킷을 확인하면 cookie값에 여러 속성들의 값이 있는 것을 볼 수 있다. 여기서 "hasAxe=false"라는 쿠키도 확인할 수 있다. 이를 "hasAxe=true"로 바꾸고 forwarding 하면 플래그 값이 나온다. 


## 플래그

```
UMASS{br0k3n_1n_2_b0wz3r5_c4st13}
```

## 배운 점

302 응답은 리다이렉트 명령이라는 점, 서버의 응답에 정보가 노출되어있을 수 있다는 점, 쿠키를 조작하는 것을 통해 Broken Authentication 취약점을 익스플로잇 할 수 있다는 점을 알게 되었다.
