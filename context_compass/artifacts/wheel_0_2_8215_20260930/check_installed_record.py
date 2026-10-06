"""Check an installed melder tree against its dist-info RECORD: every hash and size, no stray or missing file, no .pyc.

Usage: python check_installed_record.py <site-packages> <dist-info name>
"""
import base64
import hashlib
import pathlib
import sys

SITE = pathlib.Path(sys.argv[1])
INFO = sys.argv[2]
listed, bad = set(), []
for line in (SITE / INFO / "RECORD").read_text(encoding="utf-8").splitlines():
    path, digest, size = line.rsplit(",", 2)
    listed.add(path)
    if not digest:
        continue
    data = (SITE / path).read_bytes()
    actual = "sha256=" + base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode("ascii")
    if actual != digest or len(data) != int(size):
        bad.append(path)
present = {str(p.relative_to(SITE)).replace("\\", "/") for root in ("melder", INFO)
           for p in (SITE / root).rglob("*") if p.is_file()}
pyc = sorted(p for p in present if p.endswith(".pyc"))
print(f"{INFO}: RECORD rows {len(listed)}, hash or size mismatches {len(bad)}, stray {sorted(present - listed)}, "
      f"missing {sorted(listed - present)}, pyc {len(pyc)}")
print("direct_url.json:", (SITE / INFO / "direct_url.json").read_text(encoding="utf-8"))
print("INSTALLER:", (SITE / INFO / "INSTALLER").read_text(encoding="utf-8"))
if bad or present != listed or pyc:
    raise SystemExit("installed tree does not match its RECORD")
