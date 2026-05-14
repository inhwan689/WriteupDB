---
ctf_name: "UMDCTF 2026"
challenge_name: "umdmarket"
category: "web"
difficulty: "hard"
author: "oscarjhk"
date: "2026-04-24"
tags: ["WebTransport", "HMAC", "Replay Attack", "Logic Bug"]
---

# umdmarket

## 문제 설명

> Predicting the future is now legal in all 50 states.

문제 서버는 예측 시장 형태의 웹 앱이다.
신규 계정은 내부 잔고 `1,000,000`으로 시작하고, 플래그 구매에는 `10,000,000`이 필요하다.

서비스 주소는 다음과 같다.

```text
https://umdmarket.challs.umdctf.io
```

## 풀이

### 분석

프론트엔드 번들을 확인하면 `/docs`에 WebTransport 기반 바이너리 프로토콜 설명이 포함되어 있다.
WebTransport 서버는 UDP 4443번 포트에서 동작한다.

```text
WebTransport URL: https://umdmarket.challs.umdctf.io:4443/wt
serverCertificateHashes: ac02c9f7e1558563180ed412dedb9e793fd9b3ab36d64beb7e178283a68a4c9f
```

프로토콜의 정수 필드는 모두 little-endian이다.
풀이에 필요한 주요 메시지 타입은 다음과 같다.

```text
0x20 REGISTER
0x22 SUBSCRIBE
0x24 FETCH_TICKERS
0x26 RESEND
0x30 TRADE
0x40 PORTFOLIO
0x50 BUY_FLAG
```

시세는 unreliable datagram으로 내려온다.

```text
QUOTE:
  type:uint8 = 0x01
  seq:uint16
  ticker_id:uint16
  yes_price:uint16
  hmac:8 bytes
```

거래 요청은 서버가 보낸 signed quote를 그대로 되돌려 보내는 구조다.

```text
TRADE:
  type:uint8 = 0x30
  seq:uint16
  ticker_id:uint16
  yes_price:uint16
  hmac:8 bytes
  side:uint8
  qty:uint32
```

`side` 값은 다음과 같다.

```text
0x00 BUY_YES
0x01 BUY_NO
0x02 SELL_YES
0x03 SELL_NO
```

즉 클라이언트는 가격을 직접 정하지 못하고, 서버가 발급한 HMAC이 붙은 quote를 제출해야 한다.
정상적으로는 최신 quote만 거래에 사용할 수 있어야 한다.

### 취약점

문제의 핵심은 `RESEND` API에 있다.
이 API는 손실된 datagram을 복구하기 위해 과거 sequence number의 quote를 다시 요청하는 기능이다.

```text
RESEND:
  type:uint8 = 0x26
  seq:uint16
  ticker_id:uint16
```

서버는 요청받은 과거 sequence number의 가격을 찾아 응답한다.
응답 형식은 다음과 같다.

```text
status:uint8 = 0x00
seq:uint16
ticker_id:uint16
yes_price:uint16
hmac:8 bytes
```

문제는 응답 quote의 `yes_price`는 과거 가격인데, `seq`와 `hmac`은 새로 발급된 유효한 값이라는 점이다.
`TRADE` 쪽에서는 quote의 HMAC과 freshness만 검증하기 때문에, 과거 가격을 현재 가격처럼 사용할 수 있다.

예를 들어 원래 quote가 다음과 같았다고 하자.

```text
old quote:       seq=5,  ticker=13, yes_price=877
RESEND response: seq=77, ticker=13, yes_price=877, hmac=<fresh valid hmac>
```

이 경우 `yes_price=877`은 과거 가격이지만, `seq=77`과 HMAC은 현재 거래 검증을 통과한다.
결국 공격자는 resend window 안의 과거 저가와 고가를 골라내어 무위험 차익거래를 만들 수 있다.

YES 포지션에서는 낮은 `yes_price`로 사고 높은 `yes_price`로 판다.

```text
buy YES  using min old yes_price
sell YES using max old yes_price
```

NO 포지션은 가격이 `10000 - yes_price`로 계산되므로 반대로 잡으면 된다.

```text
buy NO  using 10000 - max old yes_price
sell NO using 10000 - min old yes_price
```

서버에는 거래 cooldown이 있어서 바로 연속 주문이 되지는 않는다.
따라서 exploit은 주문이 받아들여질 때까지 cooldown과 market warmup 에러를 처리하면서 재시도해야 한다.

### 익스플로잇

WebTransport는 브라우저 API이므로 solver는 Playwright로 Chromium을 띄운 뒤 페이지 컨텍스트 안에서 exploit JavaScript를 실행한다.

전체 흐름은 다음과 같다.

1. 랜덤 계정을 등록한다.
2. 모든 ticker 목록을 가져오고 subscribe한다.
3. 약 50초 동안 quote를 모아 resend window를 채운다.
4. 각 ticker에서 과거 최저가와 최고가를 찾는다.
5. YES/NO 양쪽 중 기대 수익이 가장 큰 포지션을 고른다.
6. `RESEND`로 과거 가격이 들어간 fresh quote를 발급받는다.
7. 해당 quote로 매수한 뒤, 반대쪽 과거 가격 quote를 다시 `RESEND`로 발급받아 매도한다.
8. 잔고가 `10,000,000` 이상이 될 때까지 반복한다.
9. `BUY_FLAG`를 호출해 플래그를 구매한다.

핵심 로직은 다음과 같이 표현할 수 있다.

```javascript
async function resend(seq, tickerId) {
  const b = await request(cat(u8(0x26), u16(seq), u16(tickerId)));
  const v = dv(b);
  return {
    seq: v.getUint16(1, true),
    tickerId: v.getUint16(3, true),
    yesPrice: v.getUint16(5, true),
    hmac: b.slice(7, 15),
  };
}

async function trade(q, side, qty) {
  return await request(
    cat(
      u8(0x30),
      u16(q.seq),
      u16(q.tickerId),
      u16(q.yesPrice),
      q.hmac,
      u8(side),
      u32(qty),
    ),
  );
}
```

수익 기회는 resend window 안의 quote들을 기준으로 계산한다.

```javascript
const yesEntry = min.yesPrice;
const yesExit = max.yesPrice;

const noEntry = 10000 - max.yesPrice;
const noExit = 10000 - min.yesPrice;
```

실제 solver 실행은 다음과 같다.

```bash
python3 solver.py
```

solver는 최종적으로 `BUY_FLAG` 응답을 출력한다.

## 플래그

```text
UMDCTF{fu7ur3_j4n3_s7r33t_h1r3}
```

## 배운 점

HMAC으로 quote를 서명하더라도, 서명 대상 데이터가 어떤 시간적 의미를 가지는지까지 검증하지 않으면 replay 계열 취약점이 생길 수 있다.
이 문제에서는 과거 가격과 fresh sequence가 섞이면서, 서버 입장에서는 유효한 quote처럼 보이지만 경제적으로는 절대 허용되면 안 되는 stale price 거래가 가능해졌다.

또한 WebTransport datagram처럼 손실 복구 기능이 들어가는 프로토콜에서는 `RESEND`가 단순한 편의 기능이 아니라 보안 경계가 될 수 있다.
복구된 메시지가 원래의 시간성과 freshness를 보존하는지 반드시 같이 검증해야 한다.
