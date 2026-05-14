---
ctf_name: "2026-VishwaCTF"
challenge_name: "Plain_Sights"
category: "crypto"
difficulty: "medium"
author: "vestman828"
date: "2026-04-05"
tags: [misc]
---

# Plain_Sights

## 문제 설명

> 2026-VishwaCTF에 Plain_Sights 문제입니다. Crypto입니다.

## 풀이

### 분석

Jfr?Dirf?Fev?Qvcjxjxc
라는 문자열만 주어집니다.

Qvcjxjxc는 A B C D E D E C 의 패턴을 가졌고, 이는 흔한 영단어의 패턴으로 보이지 않았습니다.
따라서 사전에서 찾아보면 그 후보가 얼마 없을 것이라고 생각했습니다.
따라서 wordfreq을 통해 찾아보니 후보가 3개 나왔고, 그 중 begining이 가장 유력해 보였습니다.
Qvcjxjxc = Begining이므로
q=b
v=e
c=g
j=i
x=n
로 매핑할 수 있고,

그러면 원본 문자열은
I?? ???? ??e begining
일 것입니다.

??e는 the일것이라고 추측했고,
같은 방식으로 문자를 매핑하면
It? ???t The Begining가 됩니다.

???t는 Just일 것으로 추측했고, 실제로 이게 플래그였습니다.


### 익스플로잇

```python
#Qvcjxjxc의 후보를 알아내는 데까지만 쓰인 익스플로잇입니다.
from wordfreq import iter_wordlist

def pattern(word):
    mp, out, nxt = {}, [], 0
    for ch in word:
        if ch not in mp:
            mp[ch] = chr(65 + nxt)
            nxt += 1
        out.append(mp[ch])
    return "".join(out)

for w in iter_wordlist("en", wordlist="large"):
    if len(w) == 8 and w.isalpha() and pattern(w) == "ABCDEDEC":
        print(w)
```

## 플래그

```
VishwaCTF{Its_Just_The_Begining}
```

## 배운 점

Weight 40아래인 Bad CTF는 거르자
