---
ctf_name: "Ritsec-CTF"
challenge_name: "Ocean wildlife"
category: "misc"
difficulty: "easy"
author: "Chik0magenta"
date: "2026-01-01"
points: 10
tags: [ros2, rosbag, sqlite, turtlesim]
---

# Ocean wildlife

## 문제 설명

> You have recieved a message in a bottle, saying something about the strange behavior of sea creatures. I wonder what that could be about?

문제 파일로 `ocean_wildlife.zip` 이 주어진다. 설명을 보면 바다 생물의 이상한 행동과 관련된 메시지가 있다고 하며, 파일 내부에 숨겨진 정보를 찾아야 한다.

## 풀이

### 분석

우선 ZIP 파일 내부를 확인하면 다음과 같은 파일이 들어 있다.

- `mystery_message/metadata.yaml`
- `mystery_message/mystery_message_0.db3`

`metadata.yaml` 내용을 보면 이것이 일반 압축 파일이 아니라 `rosbag2` 형식의 ROS2 bag 데이터라는 것을 알 수 있다.  
특히 아래와 같은 토픽 정보가 포함되어 있다.

- `/draw_commands` - `std_msgs/msg/String`
- `/turtle1/pose`
- `/turtle1/color_sensor`

이 중 가장 눈에 띄는 것은 `/draw_commands` 토픽이다. 이름 그대로 무언가를 그리는 명령이 들어 있을 가능성이 높다.

또한 `mystery_message_0.db3` 는 SQLite 데이터베이스 파일이므로, SQLite로 열어서 직접 메시지를 확인할 수 있다.

### 취약점

이 문제는 전통적인 의미의 취약점을 이용하는 문제는 아니다.  
대신 포렌식 관점에서 숨겨진 데이터를 해석하는 것이 핵심이다.

문제의 포인트는 다음과 같다.

- ZIP 안에 평범한 이미지나 텍스트가 아니라 ROS2 bag 파일이 들어 있다.
- 실제 메시지는 SQLite 내부에 저장되어 있다.
- `/draw_commands` 토픽의 데이터는 단순 문자열이 아니라 ROS2 직렬화 포맷(CDR)으로 저장되어 있다.
- 이를 올바르게 파싱하면 `teleport`, `pen` 명령이 나오고, 그 명령을 따라가면 거북이가 글자를 그린다.

즉, 숨겨진 메시지는 파일에 직접 적혀 있는 것이 아니라, 그리기 명령을 복원해야만 볼 수 있다.

### 익스플로잇

풀이 과정은 다음과 같다.

1. ZIP 파일 내부를 확인해 ROS2 bag 구조임을 파악한다.
2. `metadata.yaml` 에서 `/draw_commands` 토픽이 존재함을 확인한다.
3. `.db3` 파일을 SQLite로 열어 `topics`, `messages` 테이블을 조사한다.
4. `/draw_commands` 에 해당하는 메시지들을 시간순으로 꺼낸다.
5. 각 메시지의 CDR 직렬화 데이터를 해석해 JSON 문자열을 복원한다.
6. JSON 안의 `teleport` 와 `pen` 명령을 좌표로 렌더링한다.
7. 화면에 그려지는 텍스트를 읽어 플래그를 획득한다.

복원한 명령은 대략 아래와 같은 형태였다.

```json
{"cmd": "teleport", "x": 1.044999999999999, "y": 5.845, "theta": 0.0}
{"cmd": "pen", "r": 255, "g": 255, "b": 255, "width": 3, "off": 0}
```

여기서 의미는 다음과 같다.

teleport: 거북이를 특정 좌표로 이동
pen off = 0: 펜을 켜고 이동하면서 선을 그림
pen off = 1: 펜을 끄고 이동만 수행
이 명령을 순서대로 따라가며 선을 그리면 최종적으로 문자열이 나타난다.

```python
import sqlite3
import struct
import json

conn = sqlite3.connect("mystery_message_0.db3")
cur = conn.cursor()

topic_id = cur.execute(
    "SELECT id FROM topics WHERE name='/draw_commands'"
).fetchone()[0]

rows = cur.execute(
    "SELECT data FROM messages WHERE topic_id=? ORDER BY timestamp",
    (topic_id,)
).fetchall()

commands = []
for (data,) in rows:
    # ROS2 std_msgs/String CDR parsing
    length = struct.unpack_from("<I", data, 4)[0]
    s = data[8:8 + length - 1].decode()
    commands.append(json.loads(s))

for cmd in commands[:10]:
    print(cmd)
```

이후 명령을 이용해 직접 렌더링하면 텍스트가 나타나고, 최종 플래그를 읽을 수 있다.

## 플래그

RS{f0ll0w_th3_5ea_Turtles}

## 배운 점

ROS2 bag 파일은 포렌식 문제의 데이터 은닉 매체로도 활용될 수 있다.
.db3 파일은 SQLite이므로 직접 테이블을 열어볼 수 있다.
ROS2 메시지는 CDR 직렬화 형식으로 저장되므로, 단순 문자열처럼 바로 읽히지 않을 수 있다.
turtlesim 같은 시각적 도구를 이용하면 좌표 기반 명령으로 텍스트나 그림을 숨길 수 있다.
포렌식 문제에서는 파일 확장자보다 내부 구조와 메타데이터를 먼저 확인하는 습관이 중요하다.