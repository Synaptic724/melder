"""
Copy regenerated build-asset files from the VM mirror back to the device tree
(melder_0, 2026-10-01; adapted from the 2026-09-30 lane's helper).

Purpose:
    The device's connected folder refuses deletes, and the system-documents
    builder deletes stale payloads before it writes, so the asset runner runs in
    the VM mirror. This script carries its outputs back.

Contract:
    - Scope: every file under a `manifest/` or `payloads/` directory of
      `src/melder/_build_assets/<asset>/` in the mirror, `__pycache__` and
      `*.tmp` excluded.
    - Line endings: generated `.py` files are written CRLF, the device
      checkout's form for these files (Git stores them LF and canonicalizes on
      commit; the build fingerprints fold CRLF). This differs from the
      2026-09-30 helper, which kept whatever the device file had: a failed
      device run left three of these files LF. Any other file keeps the
      device file's existing ending (LF when new) and is reported.
    - A device file whose bytes already equal the intended bytes is skipped.
      Otherwise it is overwritten in place; the report says whether the
      content changed or only the line endings did.
    - Never deletes. Files under those directories that exist only on the
      device are reported and left in place.

Usage:
    python copy_back_assets.py <mirror repo root> <device repo root>
"""

import hashlib
import pathlib
import sys
from typing import List, Set


class CopyBackPolicy:
    """
    Constants for the copy-back scope.

    Attributes:
        BASE: Repo-relative build-asset directory.
        GENERATED_DIR_NAMES: Directory names that hold generated outputs.
        SKIP_DIR_NAME: Bytecode directory never copied.
        CRLF_SUFFIX: File suffix written CRLF on the device.
    """

    BASE: str = "src/melder/_build_assets"
    GENERATED_DIR_NAMES: Set[str] = {"manifest", "payloads"}
    SKIP_DIR_NAME: str = "__pycache__"
    CRLF_SUFFIX: str = ".py"


def canonical(raw: bytes) -> bytes:
    """
    Return `raw` with CRLF and lone CR line endings folded to LF.

    Args:
        raw: File bytes.

    Returns:
        bytes: Newline-canonical bytes.
    """
    return raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def generated_files(repo: pathlib.Path) -> List[pathlib.Path]:
    """
    List the generated build-asset files under one repository root.

    Args:
        repo: Repository root.

    Returns:
        List[pathlib.Path]: Repo-relative paths, sorted.
    """
    base = repo / CopyBackPolicy.BASE
    found: List[pathlib.Path] = []
    for path in base.rglob("*"):
        if not path.is_file() or path.suffix == ".tmp":
            continue
        inner = path.relative_to(base).parts[:-1]
        if CopyBackPolicy.SKIP_DIR_NAME in inner:
            continue
        if CopyBackPolicy.GENERATED_DIR_NAMES & set(inner):
            found.append(path.relative_to(repo))
    return sorted(found)


def intended_bytes(mirror_bytes: bytes, device_path: pathlib.Path) -> bytes:
    """
    Return the bytes the device file should hold.

    Args:
        mirror_bytes: The regenerated file as the mirror holds it.
        device_path: The device file (may not exist yet).

    Returns:
        bytes: CRLF for generated `.py` files; otherwise the device file's
            existing line ending, LF for a new file.
    """
    text = canonical(mirror_bytes)
    if device_path.suffix == CopyBackPolicy.CRLF_SUFFIX:
        return text.replace(b"\n", b"\r\n")
    if device_path.exists() and b"\r\n" in device_path.read_bytes():
        return text.replace(b"\n", b"\r\n")
    return text


def main(argv: List[str]) -> int:
    """
    Copy the mirror's generated build assets onto the device tree.

    Args:
        argv: `<mirror repo root> <device repo root>`.

    Returns:
        int: 0 always; the report is the result.
    """
    mirror = pathlib.Path(argv[0]).resolve()
    device = pathlib.Path(argv[1]).resolve()
    mirror_files = generated_files(mirror)
    copied = 0
    for relative in mirror_files:
        target = device / relative
        payload = intended_bytes((mirror / relative).read_bytes(), target)
        label = str(relative.relative_to(CopyBackPolicy.BASE))
        if target.exists():
            current = target.read_bytes()
            if current == payload:
                print(f"SKIP       {label}: already the intended bytes")
                continue
            reason = "line endings only" if canonical(current) == canonical(payload) else "content changed"
        else:
            reason = "new file"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        copied += 1
        ending = "CRLF" if b"\r\n" in payload else "LF"
        print(f"COPIED     {label}: {reason}, {ending}, sha256 {hashlib.sha256(payload).hexdigest()[:16]}")
    mirror_set = set(mirror_files)
    for relative in generated_files(device):
        if relative not in mirror_set:
            print(f"DEVICE-ONLY {relative.relative_to(CopyBackPolicy.BASE)} (left in place)")
    print(f"copied {copied} of {len(mirror_files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
