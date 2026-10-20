"""Remap the numeric `path:line` citations into conduit.py, spellbook.py and conduit_ward.py in src_architecture.md and
src_components.md after S3's src edits (melder_0, 2026-10-19; adapted from melder_1's remap_s7_citations.py).

The pre-edit copies are the backups apply_src.py took (/tmp/m0_mq/bak_s3/<name>.pre_s3); difflib maps every old line to
its new one. A range's start maps to the start of a replaced block and its end to the block's end. The Context /
Handoff Summary sections are history and are left as written.
Usage: remap_s3_citations.py --check|--apply
"""
import difflib
import pathlib
import re
import sys

ROOT = pathlib.Path.home() / "mnt/melder_private"
BACKUP = pathlib.Path("/tmp/m0_mq/bak_s3")
FILES = {
    "src/melder/aether/conduit/conduit.py": "conduit.py.pre_s3",
    "src/melder/aether/spellbook/spellbook.py": "spellbook.py.pre_s3",
    "src/melder/aether/conduit/conduit_ward/conduit_ward.py": "conduit_ward.py.pre_s3",
}
DOCS = ("context_compass/system_docs/src_architecture.md", "context_compass/system_docs/src_components.md")


def line_map(old_path: pathlib.Path, new_path: pathlib.Path) -> tuple:
    """Return (start, end) maps from pre-edit line numbers to post-edit ones, and both line counts."""
    old_lines = old_path.read_bytes().decode("utf-8").splitlines()
    new_lines = new_path.read_bytes().decode("utf-8").splitlines()
    ops = difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False).get_opcodes()

    def locate(n: int) -> tuple:
        for tag, i1, i2, j1, j2 in ops:
            if i1 <= n - 1 < i2:
                return tag, i1, i2, j1, j2
        raise SystemExit("line %d out of range of %s" % (n, old_path.name))

    def start(n: int) -> int:
        tag, i1, _i2, j1, _j2 = locate(n)
        return j1 + (n - 1 - i1) + 1 if tag == "equal" else j1 + 1

    def end(n: int) -> int:
        tag, i1, _i2, j1, j2 = locate(n)
        return j1 + (n - 1 - i1) + 1 if tag == "equal" else j2

    return start, end, len(old_lines), len(new_lines)


def main() -> None:
    """Report every changed citation; write the documents only with --apply."""
    if len(sys.argv) != 2 or sys.argv[1] not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    maps = {}
    for rel, backup in FILES.items():
        start, end, old_n, new_n = line_map(BACKUP / backup, ROOT / rel)
        maps[rel] = (start, end)
        print("%s: %d -> %d lines" % (rel, old_n, new_n))
    alternatives = "|".join(re.escape(rel) for rel in FILES)
    cite = re.compile(r"(" + alternatives + r"):(\d+(?:-\d+)?(?:, \d+(?:-\d+)?)*)")
    for rel_doc in DOCS:
        doc = ROOT / rel_doc
        raw = doc.read_bytes()
        if b"\r" in raw:
            raise SystemExit("CR in %s" % doc.name)
        lines = raw.decode("utf-8").split("\n")
        stop = lines.index("## Context / Handoff Summary")
        changes = 0
        for idx in range(stop):
            def repl(match: re.Match) -> str:
                start, end = maps[match.group(1)]
                parts = []
                for part in match.group(2).split(", "):
                    if "-" in part:
                        first, last = (int(x) for x in part.split("-"))
                        parts.append("%d-%d" % (start(first), end(last)))
                    else:
                        parts.append("%d" % start(int(part)))
                return match.group(1) + ":" + ", ".join(parts)
            new_line = cite.sub(repl, lines[idx])
            if new_line != lines[idx]:
                changes += 1
                print("%s:%d\n  - %s\n  + %s" % (doc.name, idx + 1, lines[idx].strip()[:160], new_line.strip()[:160]))
                lines[idx] = new_line
        print("%s: %d lines changed" % (doc.name, changes))
        if sys.argv[1] == "--apply":
            text = "\n".join(lines)
            doc.write_bytes(text.encode("utf-8"))
            if doc.read_bytes().decode("utf-8") != text:
                raise SystemExit("read-back mismatch in %s" % doc.name)
    if sys.argv[1] == "--apply":
        print("applied")


main()
