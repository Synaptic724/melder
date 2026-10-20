"""S8: exact text replacements from a JSON spec, keeping each file's line endings (bytes in, bytes out).

Run from the repository root:
    python s8_replace.py <spec.json>
The spec is a list of {"path": ..., "old": ..., "new": ..., "count": 1}; "old" must occur exactly "count" times
(default 1). "\n" in "old" and "new" stands for the file's own newline (CRLF files stay CRLF).
"""
import json
import pathlib
import sys


def main() -> None:
    """Apply every replacement of the spec, each file read and written once per entry."""
    spec = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    for entry in spec:
        path = pathlib.Path(entry["path"])
        text = path.read_bytes().decode("utf-8")
        newline = "\r\n" if "\r\n" in text else "\n"
        old = entry["old"].replace("\n", newline)
        new = entry["new"].replace("\n", newline)
        expected = entry.get("count", 1)
        found = text.count(old)
        if found != expected:
            raise SystemExit(f"{path}: expected {expected} occurrence(s), found {found}: {entry['old'][:80]!r}")
        path.write_bytes(text.replace(old, new).encode("utf-8"))
        print(f"{path}: replaced {found} ({'CRLF' if newline == chr(13) + chr(10) else 'LF'})")


if __name__ == "__main__":
    main()
