---
ctf_name: "RITSEC-CTF-2026"
challenge_name: "Ocean Wildlife"
category: "forrensics"           # web / pwn / rev / crypto / misc
difficulty: "easy"      # easy / medium / hard / insane
author: "kimrebin"
date: "2026-04-05"
points: 
tags: 
---

# 문제명

## 문제 설명
> You have recieved a message in a bottle, saying something about the strange behavior of sea creatures. I wonder what that could be about?
- https://ctfd.ritsec.club/challenges#Ocean%20Wildlife-38

## 풀이

### 분석

문제 파일로 `metadata.yaml`과 `mystery_message_0.db3`가 주어졌다.  
우선 `.db3` 파일은 `strings`로 확인했을 때 `SQLite format 3` 문자열이 보여 SQLite 데이터베이스 파일임을 알 수 있었다.

또한 출력 결과에서 다음과 같은 정보들을 확인할 수 있었다.

- `topics`, `messages`, `metadata`, `schema` 테이블 
- ROS2 bag 관련 문자열 
- `/draw_commands` 
- `std_msgs/msg/String`
- `cdr`
- `turtlesim`
- `draw_text_node`

특히 `draw_commands`와 `turtlesim` 관련 문자열을 통해서 이 문제는 거북이가 특정 좌표로 이동하면서 무언가를 그리는 과정을 rosbag에 저장한 문제라고 생각했다.

### 취약점

이 문제는 저장된 rosbag 데이터에서 메시지를 분석해 숨겨진 내용을 복원하는 포렌식 문제이다.  


### 익스플로잇


가장 먼저 `strings mystery_message_0.db3`를 실행해 파일 내부 문자열을 확인했다.
다음과 같은 문자열이 확인되었다.

- `{"cmd": "pen", ...}`
- `{"cmd": "teleport", "x": ..., "y": ..., "theta": 0.0}`

이로부터 거북이가 좌표를 이동하며 글자를 그리고 있음을 알 수 있었다.

문자열을 계속 확인하던 중 마지막 부분에서 다음 로그를 발견했다.


```

## 플래그

```
 RS{f0ll0w_th3_5ea_Turtles}
```

## 배운 점

.db3 파일이 SQLite일 수 있다는 점과 ROS2 bag이 SQLite 기반으로 저장될 수 있다는 것을 알게되었다.
로그, 메시지, 직렬화 데이터가 플래그의 단서가 될 수 있다는 것도 알게되었다.


