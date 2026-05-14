---
ctf_name: "2026-DawgCTF"
challenge_name: "The Lookout's Legend"
category: "osint"
difficulty: "medium"
author: "vestman828"
date: "2026-04-12"
tags: [osint]
---

# Andy Martin

## 문제 설명

> 2026-DawgCTF에 The Lookout's Legend 문제입니다. Osint입니다.

## 풀이

### 분석

구글 이미지 검색등을 통해 조사하다가
https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRU6FRei98areLHtXzFSenjRlvL-3CdZ77QDQ&s
유사해보이는 이미지를 찾았습니다.

이 이미지를 통해 또 한 번 '비슷한 이미지 찾기' 검색을 하니

https://www.facebook.com/groups/Altoonahashustle/posts/3613010052106813/
이런 게시글을 볼 수 있었습니다.

여기에서 장소를 Wopsy라고 지칭하는 것을 보았고, 시도해보았더니 실제로 Wopsy가 플래그였습니다.

### 익스플로잇

```python
(사용한 익스플로잇 없음)
```

## 플래그

```
WOPSY
```

## 배운 점

-
