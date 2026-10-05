"""Prepare a `uv pip install --target` tree for the Windows venv: Windows direct_url, no uv cache stamp, true RECORD.

Usage: python prepare_windows_install.py <target dir> <windows wheel url>
Then verifies every RECORD row (sha256 and size) and that the tree holds exactly the RECORD's files.
"""
import base64
import hashlib
import pathlib
import sys

TARGET = pathlib.Path(sys.argv[1])
URL = sys.argv[2]
INFO = TARGET / "melder-0.2.8215.dist-info"


def record_hash(data: bytes) -> str:
    """Return the RECORD form of a sha256 digest."""
    return "sha256=" + base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode("ascii")


direct = f'{{"url":"{URL}","archive_info":{{}}}}'.encode("utf-8")
(INFO / "direct_url.json").write_bytes(direct)
stamp = INFO / "uv_cache.json"
if stamp.exists():
    stamp.unlink()
rows = []
for line in (INFO / "RECORD").read_text(encoding="utf-8").splitlines():
    path = line.rsplit(",", 2)[0]
    if path == "melder-0.2.8215.dist-info/uv_cache.json":
        continue
    if path == "melder-0.2.8215.dist-info/direct_url.json":
        line = f"{path},{record_hash(direct)},{len(direct)}"
    rows.append(line)
(INFO / "RECORD").write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")

listed = set()
bad = []
for line in (INFO / "RECORD").read_text(encoding="utf-8").splitlines():
    path, digest, size = line.rsplit(",", 2)
    listed.add(path)
    file = TARGET / path
    if not digest:
        continue
    data = file.read_bytes()
    if record_hash(data) != digest or len(data) != int(size):
        bad.append(path)
present = {str(p.relative_to(TARGET)).replace("\\", "/") for p in TARGET.rglob("*") if p.is_file()
           and p.relative_to(TARGET).parts[0] in ("melder", INFO.name)}  # uv's own .lock is not installed
print(f"RECORD rows {len(listed)}; mismatched {len(bad)}; stray {sorted(present - listed)}; "
      f"missing {sorted(listed - present)}; pyc {sum(1 for p in present if p.endswith('.pyc'))}")
print("direct_url.json:", direct.decode("utf-8"))
if bad or present != listed:
    raise SystemExit("target tree does not match its RECORD")
