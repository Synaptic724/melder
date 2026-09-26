"""Refresh tests_components.md (2026-09-26): anchored edits, section rewrites, C2 inserts, C1 rebuild.

--out writes the result to a separate file; without it the document is rewritten in place.
"""
import argparse
import datetime
import pathlib
import re
import sys
from typing import Dict, List, Tuple

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from edit_tc_part1 import EDITS_1
from edit_tc_part2 import EDITS_2
from edit_tc_part3 import SECTIONS_3
from edit_tc_part4 import SECTIONS_4, EDITS_4
from edit_tc_part5 import PROTECTS_5, EDITS_5
from edit_tc_part6 import INSERT_BEFORE_6
from edit_tc_part7 import EDITS_7


def apply_edits(t: str, edits: List[Tuple[str, str, int]]) -> str:
    """Replace each anchor exactly `count` times; raise on any mismatch."""
    for old, new, count in edits:
        found = t.count(old)
        if found != count:
            raise SystemExit(f"ANCHOR {found}!={count}: {old[:80]!r}")
        t = t.replace(old, new)
    return t


def replace_sections(t: str, sections: Dict[str, str]) -> str:
    """Replace the body after each heading up to the next H2/H3 heading."""
    for heading, body in sections.items():
        assert t.count(heading) == 1, heading
        start = t.index(heading) + len(heading)
        nxt = re.search(r"^#{2,3} ", t[start:], re.M)
        end = start + nxt.start()
        t = t[:start] + body + t[end:]
    return t


def insert_protects(t: str, blocks: Dict[str, str]) -> str:
    """Insert each block before the first `Key Files (C1):` line after its heading."""
    for heading, block in blocks.items():
        assert t.count(heading) == 1, heading
        h = t.index(heading)
        k = t.index("Key Files (C1):\n", h)
        nxt = re.search(r"^#{2,3} ", t[h + len(heading):], re.M)
        assert k < h + len(heading) + nxt.start(), heading
        t = t[:k] + block + t[k:]
    return t


def insert_before(t: str, inserts: Dict[str, str]) -> str:
    """Insert each block immediately before its anchor heading."""
    for heading, block in inserts.items():
        assert t.count(heading) == 1, heading
        i = t.index(heading)
        t = t[:i] + block + t[i:]
    return t


def key_file_paths(t: str) -> List[str]:
    """Return the ordered, deduplicated path bullets of every Key Files (C1) block."""
    out: List[str] = []
    lines = t.split("\n")
    i = 0
    while i < len(lines):
        if lines[i].strip() == "Key Files (C1):":
            i += 1
            while i < len(lines) and (lines[i].startswith("- ") or lines[i].startswith("  ")):
                m = re.match(r"^- `([^`]+)`", lines[i])
                if m and ("/" in m.group(1) or m.group(1) == "pyproject.toml") and "*" not in m.group(1):
                    if m.group(1) not in out:
                        out.append(m.group(1))
                i += 1
        else:
            i += 1
    return out


def rebuild_c1(t: str, root: pathlib.Path, now: str) -> Tuple[str, int, List[str], List[str]]:
    """Remeasure every C1 entry, append missing Key Files paths, report changes."""
    start = t.index("## C1 Code Map (Core)\n")
    end = t.index("## Diagrams\n")
    region = t[start:end]
    entry_re = re.compile(r"^- path: `([^`]+)`\n  start_line: \d+\n  end_line: \d+\n  loc: \d+\n  verified_at: \S+\n", re.M)
    existing = [m.group(1) for m in entry_re.finditer(region)]
    changed: List[str] = []

    def measure(path: str) -> int:
        """Return the file's line count by splitlines()."""
        return len((root / path).read_bytes().decode("utf-8", "replace").splitlines())

    def entry(path: str) -> str:
        """Render one measured C1 entry."""
        n = measure(path)
        return f"- path: `{path}`\n  start_line: 1\n  end_line: {n}\n  loc: {n}\n  verified_at: {now}\n"

    def remeasure(m: "re.Match[str]") -> str:
        """Re-render one existing entry, noting a changed range."""
        old = m.group(0)
        new = entry(m.group(1))
        if re.search(r"end_line: (\d+)", old).group(1) != re.search(r"end_line: (\d+)", new).group(1):
            changed.append(m.group(1))
        return new

    region = entry_re.sub(remeasure, region)
    union = key_file_paths(t)
    missing = [p for p in union if p not in existing]
    for p in missing:
        assert (root / p).exists(), p
    region = region.rstrip("\n") + "\n" + "".join(entry(p) for p in missing) + "\n"
    stray = [p for p in existing if p not in union]
    t = t[:start] + region + t[end:]
    return t, len(set(existing) | set(missing)), missing, changed + ["STRAY " + s for s in stray]


def main() -> int:
    """Apply every edit group in order, rebuild C1, write the result."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out")
    ap.add_argument("--now", default=datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"))
    a = ap.parse_args()
    root = pathlib.Path(a.root)
    doc = root / "context_compass/system_docs/tests_components.md"
    t = doc.read_text(encoding="utf-8")
    t = apply_edits(t, EDITS_1)
    t = apply_edits(t, EDITS_2)
    t = replace_sections(t, SECTIONS_3)
    t = replace_sections(t, SECTIONS_4)
    t = apply_edits(t, EDITS_4)
    t = insert_protects(t, PROTECTS_5)
    t = apply_edits(t, EDITS_5)
    t = insert_before(t, INSERT_BEFORE_6)
    t = apply_edits(t, EDITS_7)
    t, count, missing, changed = rebuild_c1(t, root, a.now)
    t = t.replace("__CORE_COUNT__", str(count))
    print("core", count, "added", len(missing), "range changes", changed)
    for p in missing:
        print("  +", p)
    out = pathlib.Path(a.out) if a.out else doc
    out.write_text(t, encoding="utf-8")
    print("wrote", out, len(t.split("\n")) - 1, "lines")
    return 0


if __name__ == "__main__":
    sys.exit(main())
