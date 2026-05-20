---
ctf_name: "HACK FOR A CHANGE 2026"
challenge_name: "Slum Survey Photo"
category: "misc"
difficulty: "easy"
author: "yuninam2128"
date: "2026-05-19"
points: 100
tags: [forensics, png, trailing-data, file-format, strings]
---

# SDG #1

## 문제 설명

A community mapping NGO published an aerial photograph of an informal settlement as part of an SDG 1 housing survey. The image was released publicly without a thorough review. Standard image viewers show nothing unusual. Not every tool that reads a file is an image viewer.

- 문제 파일: `Slum Survey Photo`

## 풀이

### 분석

문제에서 제공된 파일은 PNG 이미지였다. 일반 이미지 뷰어로 열면 노이즈처럼 보이는 항공사진만 나타나고, 겉보기에는 특별한 정보가 보이지 않는다.

하지만 문제 설명에 다음과 같은 힌트가 있다.

```text
Standard image viewers show nothing unusual.
Not every tool that reads a file is an image viewer.
```

이 문장은 이미지를 눈으로 보는 것이 아니라, 파일 자체를 바이트 단위로 확인해야 한다는 뜻이다. 즉, PNG 메타데이터나 파일 구조, 혹은 이미지 끝부분에 붙은 추가 데이터를 의심할 수 있다.

PNG 파일은 여러 청크(chunk)로 구성되며, 정상적인 PNG 파일은 마지막에 `IEND` 청크를 가진다. 일반 이미지 뷰어는 `IEND` 청크까지만 읽고 이미지를 표시한다. 따라서 `IEND` 뒤에 데이터가 붙어 있어도 이미지 뷰어에서는 아무 이상 없이 보일 수 있다.

### 취약점

이 문제의 핵심은 PNG 파일의 `IEND` 청크 뒤에 추가 데이터가 붙어 있었다는 점이다.

일반 이미지 뷰어는 PNG 구조상 필요한 부분만 읽기 때문에, 파일 끝에 붙은 데이터를 무시한다. 하지만 `xxd`, `strings`, `binwalk` 같은 도구로 파일을 직접 읽으면 이미지 뷰어가 보여주지 않는 데이터를 확인할 수 있다.

즉, 이 문제는 전형적인 이미지 포렌식 문제이며, 세부 유형은 다음과 같다.

```text
PNG trailing data / appended data
```

### 익스플로잇

먼저 파일 타입을 확인한다.

```bash
file Slum_Survey_Photo.png
```

PNG 이미지 파일임을 확인할 수 있다.

이후 `strings`로 파일 안에 포함된 출력 가능한 문자열을 확인한다.

```bash
strings Slum_Survey_Photo.png
```

출력 결과 중 플래그 형식의 문자열이 나타난다.

```text
SDG{254f5ddb51aa5205679c9afd0c46ccbc}
```

또는 `xxd`로 파일의 끝부분을 직접 확인할 수도 있다.

```bash
xxd Slum_Survey_Photo.png | tail
```

PNG의 마지막 청크인 `IEND` 이후에 추가 문자열이 붙어 있는 것을 확인할 수 있다.

```text
IEND
SDG{254f5ddb51aa5205679c9afd0c46ccbc}
```

PNG 구조상 `IEND` 뒤의 데이터는 이미지 렌더링에는 사용되지 않는다. 그래서 일반 이미지 뷰어에서는 아무것도 이상해 보이지 않았지만, 파일을 직접 읽는 도구를 사용하면 숨겨진 플래그가 드러난다.

## 플래그

```text
SDG{254f5ddb51aa5205679c9afd0c46ccbc}
```

## 배운 점

이미지 포렌식 문제에서는 눈에 보이는 픽셀만 확인하면 안 된다. 이미지 파일은 렌더링되는 데이터 외에도 메타데이터, 숨겨진 청크, 압축 데이터, 파일 뒤에 덧붙은 데이터 등을 포함할 수 있다.

특히 PNG 파일은 `IEND` 청크가 파일의 논리적 끝을 의미하므로, `IEND` 뒤에 데이터가 남아 있다면 이미지 뷰어는 이를 무시한다. 따라서 이런 유형의 문제에서는 `file`, `strings`, `xxd`, `binwalk` 같은 도구로 파일 자체를 확인하는 과정이 필요하다.