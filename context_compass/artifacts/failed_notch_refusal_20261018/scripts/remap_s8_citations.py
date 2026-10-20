"""Remap the numeric `path:line` citations into the files S8 edits, in src_architecture.md and src_components.md,
line by line (melder_1; adapted from S7's remap).

The pre-edit copies are the files as S3 landed them, taken before apply_s8_rollback.py ran (--pre <dir>, holding
the same relative paths); difflib maps every old line to its new one. A range's start maps to the start of a
replaced block and its end to the block's end. The Context / Handoff Summary sections are history and are left as
written. Citations into the error file are none; the CCM's is remapped like the rest.
Usage: remap_s8_citations.py --root <tree> --pre <dir> --check|--apply
"""
import difflib
import pathlib
import re
import sys

RELS = (
    "src/melder/aether/spellbook/spellbook.py",
    "src/melder/aether/conduit/conduit.py",
    "src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py",
)
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
        raise SystemExit("line %d out of range in %s" % (n, new_path.name))

    def start(n: int) -> int:
        tag, i1, _i2, j1, _j2 = locate(n)
        return j1 + (n - 1 - i1) + 1 if tag == "equal" else j1 + 1

    def end(n: int) -> int:
        tag, i1, _i2, j1, j2 = locate(n)
        return j1 + (n - 1 - i1) + 1 if tag == "equal" else j2

    return start, end, len(old_lines), len(new_lines)


def main() -> None:
    """Report every changed citation; write the documents only with --apply."""
    args = sys.argv[1:]
    if len(args) != 5 or args[0] != "--root" or args[2] != "--pre" or args[4] not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    root = pathlib.Path(args[1])
    pre = pathlib.Path(args[3])
    maps = {}
    for rel in RELS:
        start, end, old_n, new_n = line_map(pre / rel, root / rel)
        maps[rel] = (start, end)
        print("%s: %d -> %d lines" % (pathlib.Path(rel).name, old_n, new_n))
    alternatives = "|".join(re.escape(rel) for rel in RELS)
    cite = re.compile(r"(" + alternatives + r"):(\d+(?:-\d+)?(?:, \d+(?:-\d+)?)*)")
    for rel_doc in DOCS:
        doc = root / rel_doc
        raw = doc.read_bytes()
        if b"\r\n" in raw:
            raise SystemExit("CRLF in %s" % doc.name)
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
                print("%s:%d\n  - %s\n  + %s" % (doc.name, idx + 1, lines[idx].strip()[:150], new_line.strip()[:150]))
                lines[idx] = new_line
        print("%s: %d lines changed" % (doc.name, changes))
        if args[4] == "--apply":
            text = "\n".join(lines)
            doc.write_bytes(text.encode("utf-8"))
            if doc.read_bytes().decode("utf-8") != text:
                raise SystemExit("read-back mismatch in %s" % doc.name)
    if args[4] == "--apply":
        print("applied")


main()
