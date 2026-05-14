def dec_line(s):
    b = ""

    for c in s:
        if c == "#":
            continue
        elif c == "\t":
            b += "1"
        else:
            b += "0"

    d = b""
    i = 0
    while i < len(b):
        d += bytes([int(b[i:i+8], 2)])
        i += 8

    return d


f = open("/mnt/c/Users/fbxog/dev/ctf/blank.txt", "r", encoding="utf-8")
ls = f.read().splitlines()
f.close()

res = ""

i = 0
while i < len(ls):
    l = dec_line(ls[i])
    r = dec_line(ls[i + 1])

    t = b""
    j = 0
    while j < len(l) and j < len(r):
        t += bytes([l[j] ^ r[j]])
        j += 1

    res += t.decode()
    i += 2

print("IIITL{REDACTED}")
