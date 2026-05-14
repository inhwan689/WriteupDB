---
ctf_name: "DawgCTF"
challenge_name: "Better Call AT&T!"
category: "misc"           # web / pwn / rev / crypto / misc
difficulty: "medium"      # easy / medium / hard / insane
author: "Chik0magenta"
date: "2026-04-11"
points: 100
tags: [osint, geolocation, google-maps, street-view, video-analysis]
---

# Better Call AT&T!

## 문제 설명

> I was watching my favorite show Better Call Saul recently and noticed something peculiar, can you figure out what the phone number for this parking garage is? I wanna recreate the shot... Your flag will be the number for the garage without dashes, e.g DawgCTF{2015552124}.

- 문제에는 위 설명과, 드라마 스크린샷으로 보이는 사진이 한 장 주어졌다.

## 풀이

### 분석

문제는 드라마 Better Call Saul의 로케이션으로 등장한 주차장의 전화번호를 찾는 OSINT 문제이다.

### 핵심 단서

주어진 이미지를 Google Lens를 이용해 검색한 결과,
약 4분 길이의 드라마 클립을 찾을 수 있었다.

https://youtu.be/N723si1wAG8?si=bh78N5ElQ_ZbhwcB

영상의 0:14 부근에서 문제에 주어진 이미지와 동일한 장면을 확인할 수 있었으나,
전화번호는 직접적으로 드러나지 않았다.


### 탐색 과정

처음에는 "Better Call Saul parking garage" 등의 키워드로 검색하여
해당 장면이 등장하는 주차장을 찾으려 했다.

이 과정에서 드라마 팬덤 위키를 통해 특정 주차장 후보를 찾았지만,
실제로 확인해보니 구조가 일치하지 않거나 단순 공터에 가까운 장소로,
문제에서 요구하는 조건과 맞지 않았다.

이로 인해 단순 키워드 검색만으로는 해결할 수 없는 문제라고 판단하였다.

---

이후 영상 속 배경 요소에 집중하였다.

영상의 0:14에서 확인되는 AT&T 건물과,
0:32에서 등장하는 'New Mexico Bank & Trust' 건물이 주요 단서였다.

특히 은행 건물의 간판은 식별성이 높아 위치 특정에 결정적인 역할을 했다.

조사 결과 해당 건물은
'320 Gold Ave SW, Albuquerque, NM 87102'에 위치함을 확인하였다.

---

이후 Google Maps의 Street View 기능을 활용하여
해당 위치 주변을 탐색하였다.

영상 속 구도를 기준으로:

- AT&T 건물은 정면 방향
- 은행 건물은 약간 사선 방향

이라는 점에 주목하여,
카메라의 위치와 방향을 역추적하였다.

---

이 과정을 통해 두 건물이 동시에 보이는 위치를 좁혀 나갔고,
결국 '401 2nd St NW, Albuquerque, NM 87102'에 위치한
Convention Center Parking을 촬영 장소로 특정할 수 있었다.

---

마지막으로 해당 위치와 연관된 전화번호를 조사하여
+1 505-768-4575를 확인하였고,
문제의 형식에 맞게 하이픈을 제거하여 플래그를 완성하였다.


## 플래그

```
DawgCTF{5057684575}
```

## 배운 점

 - 위치를 특정하는 OSINT 문제를 풀 때, 중요 단서가 될 수 있는 배경 정보를 놓치지 않는 것이 중요하다.
 - 구글 지도의 거리뷰 기능을 활용하여 타깃의 대략적인 방향을 잡는 방법을 배웠다.