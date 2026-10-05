"""Copy regenerated build-asset files from the VM copy back to the device tree (melder_0, 2026-09-30).

The device refuses deletes and its generated files are CRLF, while the asset runner writes LF. For every file
under a `manifest/` or `payloads/` directory of src/melder/_build_assets in the VM copy: skip it when its content
equals the device copy apart from line endings; otherwise overwrite the device file in place, keeping the device
file's line ending (CRLF for a new file when its siblings are CRLF). Files present only on the device are reported,
never deleted. Usage: python copy_back_assets.py <vm repo root> <device repo root>"""
import hashlib
import pathlib
import sys

VM, DEVICE = (pathlib.Path(value) for value in sys.argv[1:3])
BASE = pathlib.Path("src/melder/_build_assets")


def canonical(raw: bytes) -> bytes:
    """Return the bytes with CRLF and CR folded to LF."""
    return raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


vm_files = sorted(p.relative_to(VM) for p in (VM / BASE).rglob("*")
                  if p.is_file() and {"manifest", "payloads"} & set(p.relative_to(VM / BASE).parts[:-1])
                  and "__pycache__" not in p.parts)
for relative in vm_files:
    new = canonical((VM / relative).read_bytes())
    target = DEVICE / relative
    if target.exists():
        old = target.read_bytes()
        crlf = b"\r\n" in old
        if canonical(old) == new:
            print(f"SKIP   {relative.relative_to(BASE)}: identical apart from line endings (device CRLF={crlf})")
            continue
    else:
        siblings = [p for p in target.parent.glob("*.py") if p.is_file()]
        crlf = any(b"\r\n" in p.read_bytes() for p in siblings)
    payload = new.replace(b"\n", b"\r\n") if crlf else new
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(payload)
    print(f"COPIED {relative.relative_to(BASE)}: {'CRLF' if crlf else 'LF'} kept, sha256 "
          f"{hashlib.sha256(payload).hexdigest()[:16]}")
device_only = sorted(p.relative_to(DEVICE) for p in (DEVICE / BASE).rglob("*")
                     if p.is_file() and {"manifest", "payloads"} & set(p.relative_to(DEVICE / BASE).parts[:-1])
                     and "__pycache__" not in p.parts and p.relative_to(DEVICE) not in set(vm_files))
for relative in device_only:
    print(f"DEVICE-ONLY {relative.relative_to(BASE)} (left in place)")
