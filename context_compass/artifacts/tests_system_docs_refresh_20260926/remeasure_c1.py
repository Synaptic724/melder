"""Remeasure every `- path:` C1 entry of a tests document; optionally append new entries before a heading."""
import pathlib
import re
import sys
from typing import List

REPO = pathlib.Path.home() / "mnt/melder_private"
STAMP = sys.argv[2]


def loc(rel: str) -> int:
    """Line count of a repo file (splitlines)."""
    return len((REPO / rel).read_bytes().decode("utf-8", "replace").splitlines())


def main() -> int:
    """argv: doc stamp [--add path ... --before '## Heading']"""
    doc = REPO / "context_compass/system_docs" / sys.argv[1]
    lines = doc.read_text(encoding="utf-8").split("\n")
    changed = 0
    cur = None
    for i, line in enumerate(lines):
        m = re.match(r"^- path: `([^`]+)`$", line)
        if m:
            cur = m.group(1)
            if not (REPO / cur).exists():
                print("MISSING", cur)
                cur = None
            continue
        if cur is None:
            continue
        s = line.strip()
        if s.startswith("end_line:") or s.startswith("loc:"):
            n = loc(cur)
            new = re.sub(r"\d+", str(n), line)
            if new != line:
                changed += 1
            lines[i] = new
        elif s.startswith("verified_at:"):
            lines[i] = re.sub(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", STAMP, line)
            cur = None
    args = sys.argv[3:]
    if args and args[0] == "--add":
        before = args[args.index("--before") + 1]
        paths = args[1:args.index("--before")]
        idx = lines.index(before)
        while idx > 0 and lines[idx - 1] == "":
            idx -= 1
        block: List[str] = []
        for p in paths:
            n = loc(p)
            block += [f"- path: `{p}`", "  start_line: 1", f"  end_line: {n}", f"  loc: {n}", f"  verified_at: {STAMP}"]
        lines[idx:idx] = block
        print("added", len(paths))
    doc.write_text("\n".join(lines), encoding="utf-8")
    print(sys.argv[1], "ranges changed", changed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
