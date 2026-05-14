---
ctf_name: "2026-VishwaCTF"
challenge_name: "Silent Eyes Become The Wise"
category: "stego"
difficulty: "medium"
author: "vestman828"
date: "2026-04-05"
tags: [LSB_stego]
---

# Silent Eyes Become The Wise

## 문제 설명

> 2026-VishwaCTF에 Silent Eyes Become The Wise 문제입니다. Stego입니다.

## 풀이

### 분석

```
= RESTART: C:\Users\user\Downloads\kotama.py
=== NORMAL ===
unit = 0.05455416666666667
morse =  / .-. . .-- .-- .. ..- -. - -. ..- -. . ...-
decoded =  REWWIUNTNUNEV

=== REVERSED ===
unit = 0.05455416666666667
morse = -... . .- -.. .- - .- -.. .. --. --. . .-. / 
decoded = BEADATADIGGER 
```
opera.wav 모스부호 분석 결과는 위와 같았습니다.(각각 정방향, 역재생 했을때의 모스부호)

역재생을 시도해 본 이유는 문제 설명에 `a haunting **opera** that seems to say _walk back_. `라고 되어 있었기 때문입니다.

melody.wav에는 표준적인 RIFF/WAVE 청크만 존재했고, 파일 끝(EOF) 뒤에 눈에 띄는 추가 페이로드도 없었습니다. 따라서 이 파일은 LSB 스테가노그래피가 적용되었을 가능성이 높다고 판단했습니다.
melody.wav에서,
channels=2, nbBits=3, headerPos=ENDING, compress=True에서
파싱 결과가 Data::FILE 형식으로 떨어졌고,
SilentEye의 FILE 데이터로 정상 파싱되었고, 추출된 파일명은 notes.rar이었습니다.
이 파일의 비밀번호는 앞서 해독한 모스부호인 BEADATADIGGER 였습니다.
열어보니 qr코드 사진 3장이 나왔고,
각 qr코드를 서로 조합한 뒤
base64->base85->base92를 거치면 플래그가 나옵니다.


### 익스플로잇

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import butter, filtfilt, hilbert, medfilt

MORSE = {
    ".-":"A", "-...":"B", "-.-.":"C", "-..":"D", ".":"E",
    "..-.":"F", "--.":"G", "....":"H", "..":"I", ".---":"J",
    "-.-":"K", ".-..":"L", "--":"M", "-.":"N", "---":"O",
    ".--.":"P", "--.-":"Q", ".-.":"R", "...":"S", "-":"T",
    "..-":"U", "...-":"V", ".--":"W", "-..-":"X", "-.--":"Y",
    "--..":"Z",
    "-----":"0", ".----":"1", "..---":"2", "...--":"3", "....-":"4",
    ".....":"5", "-....":"6", "--...":"7", "---..":"8", "----.":"9",
    ".-.-.-":".", "--..--":",", "..--..":"?", "-..-.":"/",
    "-....-":"-", "-.--.":"(", "-.--.-":")"
}

def decode_morse(s: str) -> str:
    words = []
    for word in s.split(" / "):
        chars = []
        for ch in word.split():
            chars.append(MORSE.get(ch, f"[{ch}]"))
        words.append("".join(chars))
    return " ".join(words)

def bandpass(x, lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    b, a = butter(order, [lowcut / nyq, highcut / nyq], btype="band")
    return filtfilt(b, a, x)

def runs(binary):
    out = []
    start = 0
    current = int(binary[0])
    for i in range(1, len(binary)):
        if int(binary[i]) != current:
            out.append((current, start, i))
            start = i
            current = int(binary[i])
    out.append((current, start, len(binary)))
    return out

def demod_morse_from_signal(sig, sr, lowcut=750, highcut=850, thr_k=0.8, min_on_sec=0.02):
    filtered = bandpass(sig, lowcut, highcut, sr)

    env = np.abs(hilbert(filtered))
    win = int(sr * 0.01)
    if win % 2 == 0:
        win += 1
    if win < 3:
        win = 3
    env = medfilt(env, kernel_size=win)

    thr = env.mean() + thr_k * env.std()
    mask = env > thr

    segments = runs(mask.astype(np.uint8))
    durations = [(v, (e - s) / sr) for v, s, e in segments]

    on_durs = np.array([d for v, d in durations if v == 1 and d > min_on_sec])
    if len(on_durs) == 0:
        return {
            "unit": None,
            "morse": "",
            "decoded": "",
            "threshold": thr,
            "env": env,
            "mask": mask,
            "durations": durations,
        }

    unit = np.percentile(on_durs, 20)

    symbols = []
    for val, dur in durations:
        if dur < unit * 0.4:
            continue

        if val == 1:
            symbols.append("." if dur < unit * 2 else "-")
        else:
            if dur < unit * 2:
                pass
            elif dur < unit * 5:
                symbols.append(" ")
            else:
                symbols.append(" / ")

    morse_text = "".join(symbols)
    decoded = decode_morse(morse_text)

    return {
        "unit": unit,
        "morse": morse_text,
        "decoded": decoded,
        "threshold": thr,
        "env": env,
        "mask": mask,
        "durations": durations,
    }

# =========================
# Load file
# =========================
sr, y = wavfile.read("opera.wav")

# Stereo -> mono
if y.ndim > 1:
    y = y.mean(axis=1)

y = y.astype(np.float32)
y /= np.max(np.abs(y)) + 1e-9

# =========================
# Analyze both directions
# =========================
normal = y
reversed_y = y[::-1]

lowcut = 750
highcut = 850

res_normal = demod_morse_from_signal(normal, sr, lowcut=lowcut, highcut=highcut, thr_k=0.8)
res_reversed = demod_morse_from_signal(reversed_y, sr, lowcut=lowcut, highcut=highcut, thr_k=0.8)

print("=== NORMAL ===")
print("unit =", res_normal["unit"])
print("morse =", res_normal["morse"])
print("decoded =", res_normal["decoded"])

print("\n=== REVERSED ===")
print("unit =", res_reversed["unit"])
print("morse =", res_reversed["morse"])
print("decoded =", res_reversed["decoded"])

# Save reversed wave
wavfile.write("opera_reversed.wav", sr, (reversed_y * 32767).astype(np.int16))

# Envelope plots
for title, res in [("NORMAL", res_normal), ("REVERSED", res_reversed)]:
    env = res["env"]
    thr = res["threshold"]
    t = np.arange(len(env)) / sr

    plt.figure(figsize=(15, 4))
    plt.plot(t, env, label="envelope")
    plt.axhline(thr, linestyle="--", label="threshold")
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.show()
```
```python
# .rar을 추출해내는 익스플로잇입니다.
import struct
import math
import zlib


def and_mask(n: int) -> int:
    return (1 << n) - 1


class EncodedState:
    """
    Reproduces SilentEye-like bit assembly behavior:
    append(swap_bits) into byte stream with carry.
    """
    def __init__(self, swap_bits: int):
        self.swap = swap_bits
        self.bit_count = 0
        self.carry = 0
        self.buf = bytearray()

    def append(self, val: int):
        bits_left = 8 - self.bit_count
        tmp = 0

        if bits_left < self.swap:
            tmp = val
            val = val & and_mask(bits_left)

        self.carry += (val << self.bit_count)

        if self.bit_count + self.swap >= 8:
            self.buf.append(self.carry & 0xFF)
            self.bit_count = 0
            self.carry = 0
        else:
            self.bit_count += self.swap

        if bits_left < self.swap:
            rem = self.swap - bits_left
            self.carry += (tmp >> bits_left)
            self.bit_count += rem


def load_wave_samples(path: str):
    data = open(path, "rb").read()

    if data[:4] not in (b"RIFF", b"RIFX") or data[8:12] != b"WAVE":
        raise ValueError("Not a RIFF/WAVE file")

    # Parse fmt/data chunks
    pos = 12
    fmt = None
    data_off = None
    data_size = None

    while pos + 8 <= len(data):
        cid = data[pos:pos + 4]
        sz = struct.unpack("<I", data[pos + 4:pos + 8])[0]
        payload = data[pos + 8:pos + 8 + sz]

        if cid == b"fmt ":
            fmt = payload
        elif cid == b"data":
            data_off = pos + 8
            data_size = sz
            break

        pos += 8 + sz + (sz & 1)

    if fmt is None or data_off is None:
        raise ValueError("Missing fmt/data chunk")

    audio_format, channels, sample_rate, byte_rate, block_align, bps = struct.unpack("<HHIIHH", fmt[:16])
    if audio_format != 1:
        raise ValueError("Only PCM expected here")
    if bps != 16:
        raise ValueError(f"Expected 16-bit PCM, got {bps}")

    raw = data[data_off:data_off + data_size]

    # To match the extraction behavior used in this solve:
    # RIFF -> parse samples as big-endian words.
    # (This mirrors the same behavior used in the successful recovery.)
    sample_byteorder = "big" if data[:4] == b"RIFF" else "little"

    vals = []
    for i in range(0, len(raw), 2):
        vals.append(int.from_bytes(raw[i:i + 2], sample_byteorder, signed=False))

    nframes = len(vals) // channels
    vals = vals[:nframes * channels]
    frames = [vals[i * channels:(i + 1) * channels] for i in range(nframes)]

    return frames, nframes, channels


def extract_notes_rar(path: str = "melody.wav"):
    # Discovered correct parameters
    channels_used = 2
    nb_bits = 3
    header_position = "ENDING"      # read 32-bit size from end-header region
    compressed = True               # zlib-compressed payload

    frames, nframes, channels = load_wave_samples(path)
    if channels < channels_used:
        raise ValueError("Not enough channels")

    mask = and_mask(nb_bits)

    # 1) decode embedded payload size (32 bits)
    header_samples = math.ceil(32 / (channels_used * nb_bits))
    start = 0 if header_position == "BEGINNING" else (nframes - header_samples)

    st = EncodedState(nb_bits)
    bits_read = 0
    for i in range(start, nframes):
        s = frames[i]
        for ch in range(channels_used):
            if bits_read >= 32:
                break
            st.append(s[ch] & mask)
            bits_read += nb_bits
        if bits_read >= 32:
            break

    if len(st.buf) < 4:
        raise RuntimeError("Failed to decode embedded size")

    payload_size = sum(st.buf[i] << (8 * i) for i in range(4))

    # 2) extract payload bytes (INLINE path with this sample set effectively works)
    st2 = EncodedState(nb_bits)
    need_bits = payload_size * 8
    bits_read = 0

    idx = header_samples if header_position == "BEGINNING" else 0
    while idx < nframes and bits_read < need_bits:
        s = frames[idx]
        for ch in range(channels_used):
            if bits_read >= need_bits:
                break
            st2.append(s[ch] & mask)
            bits_read += nb_bits
        idx += 1

    payload = bytes(st2.buf)

    # 3) decompress (Qt-style: first 4 bytes are expected size, then zlib stream)
    if compressed:
        if len(payload) < 4:
            raise RuntimeError("Compressed payload too short")
        raw = zlib.decompress(payload[4:])
    else:
        raw = payload

    # 4) SilentEye data format parsing: first byte is format char ('0'..'7')
    data_format = raw[0] - ord("0")
    if data_format != 5:
        raise RuntimeError(f"Unexpected data format: {data_format} (expected FILE=5)")

    rest = raw[1:]
    sep = rest.find(b"<")
    if sep < 0:
        raise RuntimeError("Invalid FILE payload format")

    filename = rest[:sep].decode("utf-8", errors="ignore")
    file_data = rest[sep + 1:]

    with open(filename, "wb") as f:
        f.write(file_data)

    print(f"[+] extracted file: {filename}")
    print(f"[+] embedded payload size: {payload_size} bytes")
    print(f"[+] output file size: {len(file_data)} bytes")


if __name__ == "__main__":
    extract_notes_rar("melody.wav")
```

## 플래그

```
VishwaCTF{s1lent_eye5_c4tch_everyth1n9}
```

## 배운 점

Weight 40아래인 Bad CTF는 거르자
