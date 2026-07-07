# Ophir Powermeter Setup (new machine)

How to get the dual Ophir powermeter connection working with this app on a
fresh Windows machine. There are two non-obvious gotchas — a vendor type-library
bug and a DLL load-order conflict — both explained below. The load-order fix is
already in the code (`gui.py`); the type-library fix is a one-time per-machine
registry step you have to run yourself.

---

## 1. Prerequisites

1. **Install Ophir StarLab** (or PMManager) from Ophir/Newport.
   Default install path is one of:
   - `C:\Program Files\Ophir Optronics\StarLab 4.00\`
   - `C:\Program Files\Newport\PMManager 4.00\`

   This installs `OphirLMMeasurement.dll`, its `boost_*` dependency DLLs, the
   USB drivers, and registers the COM object. Confirm StarLab itself can see
   both meters before touching the Python app.

2. **Plug in both powermeters** over USB (the app expects exactly two).

3. **Install 64-bit Python with pywin32.**
   - The app runs on **64-bit** CPython (this machine uses the system
     `pythoncore-3.14-64`). The interpreter's bitness must match — 64-bit.
   - `pip install pywin32 numpy scipy matplotlib pyserial pyqt5 pyqtgraph ttkthemes`
   - ⚠️ The repo's `.venv` here is **32-bit and has no pywin32** — do **not**
     run the app from it. Use the 64-bit interpreter.

---

## 2. Fix the type-library version mismatch (one-time, per machine)

**Symptom if skipped:** `Dispatch("OphirLMMeasurement.CoLMMeasurement")` fails with
`com_error (-2147319779, 'Library not registered')` — even though StarLab is
installed and "Register COM" / `regsvr32` were run.

**Why:** `OphirLMMeasurement.dll` has file version **10.11** and its COM object
asks Windows for type library version **10.11** at runtime, but the DLL only
embeds/registers a **10.10** type library. `LoadRegTypeLib(10,11)` never falls
back to a lower minor, so every IDispatch call fails. `regsvr32` can't fix it —
it only ever registers the embedded 10.10. This affects both StarLab and
PMManager; no 10.11 `.tlb` ships anywhere.

**Fix:** produce a genuine 10.11 type library (identical GUID/interfaces, minor
version bumped 10.10 → 10.11) and register it.

### 2a. Generate the patched 10.11 typelib

Save this as `make_1011_tlb.py` and run it with your **64-bit** Python
(`python make_1011_tlb.py`). It auto-finds the installed `COM x64` DLL, extracts
its type library, bumps the version, writes a `.tlb`, and verifies it loads as
10.11.

```python
import struct, os, glob, pythoncom

# Find the installed COM x64 DLL (StarLab or PMManager)
CANDIDATES = [
    r"C:\Program Files\Ophir Optronics\StarLab 4.00\COM x64\OphirLMMeasurement.dll",
    r"C:\Program Files\Newport\PMManager 4.00\COM x64\OphirLMMeasurement.dll",
]
CANDIDATES += glob.glob(r"C:\Program Files\**\COM x64\OphirLMMeasurement.dll", recursive=True)
SRC = next((p for p in CANDIDATES if os.path.exists(p)), None)
assert SRC, "Could not find COM x64\\OphirLMMeasurement.dll - set SRC manually"
OUT = os.path.join(os.path.dirname(SRC), "OphirLMMeasurement_1011.tlb")
print("source DLL:", SRC)

data = open(SRC, "rb").read()

# --- locate the embedded type library resource via PE parsing ---
e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
assert data[e_lfanew:e_lfanew+4] == b"PE\0\0"
coff = e_lfanew + 4
num_sections = struct.unpack_from("<H", data, coff+2)[0]
size_opt = struct.unpack_from("<H", data, coff+16)[0]
opt = coff + 20
assert struct.unpack_from("<H", data, opt)[0] == 0x20B, "expected PE32+ (64-bit) DLL"
rsrc_rva = struct.unpack_from("<I", data, opt + 112 + 2*8)[0]

sections = []
for i in range(num_sections):
    b = opt + size_opt + i*40
    vsize, vaddr, rawsize, rawptr = struct.unpack_from("<IIII", data, b+8)
    sections.append((vaddr, vsize, rawptr, rawsize))

def rva_to_off(rva):
    for vaddr, vsize, rawptr, rawsize in sections:
        if vaddr <= rva < vaddr + max(vsize, rawsize):
            return rawptr + (rva - vaddr)
    raise ValueError("RVA not mapped")

rsrc_off = rva_to_off(rsrc_rva)
leaves = []
def walk(off):
    n = struct.unpack_from("<H", data, off+12)[0] + struct.unpack_from("<H", data, off+14)[0]
    for i in range(n):
        _, o = struct.unpack_from("<II", data, off+16 + i*8)
        child = rsrc_off + (o & 0x7FFFFFFF)
        if o & 0x80000000:
            walk(child)
        else:
            rva, size, _, _ = struct.unpack_from("<IIII", data, child)
            leaves.append((rva, size))
walk(rsrc_off)

tlb = None
for rva, size in leaves:
    blob = data[rva_to_off(rva):rva_to_off(rva)+size]
    if blob[:4] == b"MSFT":
        tlb = bytearray(blob); break
assert tlb is not None, "no MSFT type library resource found"

# --- MSFT header version dword @0x18 is (minor<<16)|major ; bump minor to 11 ---
ver = struct.unpack_from("<I", tlb, 0x18)[0]
major = ver & 0xFFFF
struct.pack_into("<I", tlb, 0x18, (11 << 16) | major)
open(OUT, "wb").write(tlb)
print("wrote", OUT)

pythoncom.CoInitialize()
la = pythoncom.LoadTypeLib(OUT).GetLibAttr()
print(f"verify: guid={la[0]} version={la[3]}.{la[4]}")   # expect ...=10.11
```

You should see `verify: ... version=10.11`. This leaves
`OphirLMMeasurement_1011.tlb` next to the DLL.

### 2b. Register the 10.11 typelib (elevated)

Save this as `ophir_1011.reg`, **editing the two paths** if your install dir
differs (they must point at the `.tlb` from step 2a). `a.b` is the registry
spelling of version 10.11.

```
Windows Registry Editor Version 5.00

[HKEY_LOCAL_MACHINE\SOFTWARE\Classes\TypeLib\{F7267688-9A91-4B70-AE35-86A2D6E74D2A}\a.b]
@="Ophir LM Measurement 10.11 Type Library"
[HKEY_LOCAL_MACHINE\SOFTWARE\Classes\TypeLib\{F7267688-9A91-4B70-AE35-86A2D6E74D2A}\a.b\0]
[HKEY_LOCAL_MACHINE\SOFTWARE\Classes\TypeLib\{F7267688-9A91-4B70-AE35-86A2D6E74D2A}\a.b\0\win32]
@="C:\\Program Files\\Ophir Optronics\\StarLab 4.00\\COM x64\\OphirLMMeasurement_1011.tlb"
[HKEY_LOCAL_MACHINE\SOFTWARE\Classes\TypeLib\{F7267688-9A91-4B70-AE35-86A2D6E74D2A}\a.b\0\win64]
@="C:\\Program Files\\Ophir Optronics\\StarLab 4.00\\COM x64\\OphirLMMeasurement_1011.tlb"
[HKEY_LOCAL_MACHINE\SOFTWARE\Classes\TypeLib\{F7267688-9A91-4B70-AE35-86A2D6E74D2A}\a.b\FLAGS]
@="0"
[HKEY_LOCAL_MACHINE\SOFTWARE\Classes\TypeLib\{F7267688-9A91-4B70-AE35-86A2D6E74D2A}\a.b\HELPDIR]
@="C:\\Program Files\\Ophir Optronics\\StarLab 4.00\\COM x64"

[HKEY_LOCAL_MACHINE\SOFTWARE\Classes\WOW6432Node\TypeLib\{F7267688-9A91-4B70-AE35-86A2D6E74D2A}\a.b]
@="Ophir LM Measurement 10.11 Type Library"
[HKEY_LOCAL_MACHINE\SOFTWARE\Classes\WOW6432Node\TypeLib\{F7267688-9A91-4B70-AE35-86A2D6E74D2A}\a.b\0]
[HKEY_LOCAL_MACHINE\SOFTWARE\Classes\WOW6432Node\TypeLib\{F7267688-9A91-4B70-AE35-86A2D6E74D2A}\a.b\0\win32]
@="C:\\Program Files\\Ophir Optronics\\StarLab 4.00\\COM x64\\OphirLMMeasurement_1011.tlb"
[HKEY_LOCAL_MACHINE\SOFTWARE\Classes\WOW6432Node\TypeLib\{F7267688-9A91-4B70-AE35-86A2D6E74D2A}\a.b\0\win64]
@="C:\\Program Files\\Ophir Optronics\\StarLab 4.00\\COM x64\\OphirLMMeasurement_1011.tlb"
[HKEY_LOCAL_MACHINE\SOFTWARE\Classes\WOW6432Node\TypeLib\{F7267688-9A91-4B70-AE35-86A2D6E74D2A}\a.b\FLAGS]
@="0"
[HKEY_LOCAL_MACHINE\SOFTWARE\Classes\WOW6432Node\TypeLib\{F7267688-9A91-4B70-AE35-86A2D6E74D2A}\a.b\HELPDIR]
@="C:\\Program Files\\Ophir Optronics\\StarLab 4.00\\COM x64"
```

Then, in an **Administrator** terminal:

```powershell
reg import ophir_1011.reg
```

### 2c. Verify

In a **normal** (non-admin) terminal, with the 64-bit Python:

```powershell
python -c "import pythoncom, win32com.client; pythoncom.CoInitialize(); c=win32com.client.Dispatch('OphirLMMeasurement.CoLMMeasurement'); c.StopAllStreams(); c.CloseAll(); print(list(c.ScanUSB()))"
```

Expected: a list of two serial-number strings, e.g. `['3127106', '3136252']`.

---

## 3. DLL load-order (already fixed in code — don't undo it)

**Symptom if broken:** `python main.py` fails with
`com_error (-2147023782, 'A dynamic link library (DLL) initialization routine failed.')`
even though step 2c passes.

**Why:** `PyQt5`/`pyqtgraph` (pulled in by `graphingProcess`) load native DLLs
that, if loaded **before** the Ophir DLL is created, make the Ophir DLL's
`DllMain` fail. It is purely load order — whichever loads first wins.

**Fix (already in `gui.py`):** `graphingProcess` is imported lazily inside
`startPyqtProcess()` instead of at the top of `gui.py`, so the powermeter loads
first. `graphingProcess` runs in its own child process anyway, so the main
process never needs PyQt5 at import time.

👉 If you ever add plotting/PyQt imports, **keep anything that pulls in
PyQt5/pyqtgraph out of `gui.py`'s module-level imports.**

---

## 4. Run

From a **normal, non-elevated** terminal (admin is only needed for the one-time
step 2b) with the 64-bit Python:

```powershell
python main.py
```

---

## Troubleshooting quick reference

| Error | Meaning | Fix |
|-------|---------|-----|
| `-2147319779 Library not registered` | typelib 10.11 not registered | Step 2 |
| `-2147221005 Invalid class string` | COM object not registered at all | Reinstall StarLab / run its Register COM |
| `-2147023782 DLL initialization routine failed` | Qt loaded before Ophir (or a bad interpreter) | Ensure step 3 intact; use 64-bit Python |
| `ModuleNotFoundError: win32com` | wrong interpreter (e.g. the 32-bit `.venv`) | Use 64-bit Python with pywin32 |
| `AttributeError: ...ScanUSB` | masked typelib failure | Step 2 |

**Note:** these fixes can be wiped if StarLab is reinstalled/upgraded. The `.tlb`
and the `a.b` registry key normally survive a reinstall (StarLab only writes the
10.10 key), but if the connection breaks again after an Ophir update, re-run
step 2. If Ophir ever ships a build whose file version and type-library version
match, this whole workaround becomes unnecessary.
