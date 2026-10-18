"""Remap the numeric `path:line` citations into spellbook.py and spell.py in src_architecture.md and
src_components.md after S9's edits E1-E7 (0.2.8256), line by line.

The pre-edit text is rebuilt by undoing E1-E7 (their exact strings, read from apply_s9_refusal.py) on the current
file; difflib maps every old line to its new one. A range's start maps to the start of a replaced block and its end
to the block's end. The Context / Handoff Summary sections are history and are left as written.
Usage: remap_s9_citations.py --check | --apply
"""
import ast
import difflib
import pathlib
import re
import sys

LANE = pathlib.Path(__file__).resolve().parents[1]
REPO = pathlib.Path(__file__).resolve().parents[4]
DOCS = [REPO / "context_compass/system_docs/src_architecture.md",
        REPO / "context_compass/system_docs/src_components.md"]
TARGETS = {"spellbook.py": ("SPELLBOOK_EDITS", REPO / "src/melder/aether/spellbook/spellbook.py"),
           "spell.py": ("SPELL_EDITS", REPO / "src/melder/aether/spellbook/spell.py")}


def edit_lists() -> dict:
    """Read SPELLBOOK_EDITS and SPELL_EDITS from apply_s9_refusal.py as literals."""
    tree = ast.parse((LANE / "scripts/apply_s9_refusal.py").read_text(encoding="utf-8"))
    found = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id in ("SPELLBOOK_EDITS", "SPELL_EDITS"):
                found[node.targets[0].id] = ast.literal_eval(node.value)
    return found


def line_map(path: pathlib.Path, edits: list) -> tuple:
    """Return (start_map, end_map) callables from old line numbers to new ones for one file."""
    new_text = path.read_text(encoding="utf-8")
    old_text = new_text
    for label, old, new in reversed(edits):
        if old_text.count(new) != 1:
            raise SystemExit("%s: cannot undo %s" % (path.name, label))
        old_text = old_text.replace(new, old)
    redo = old_text
    for label, old, new in edits:
        redo = redo.replace(old, new)
    if redo != new_text:
        raise SystemExit("%s: undo/redo mismatch" % path.name)
    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()
    ops = difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False).get_opcodes()

    def locate(n: int) -> tuple:
        for tag, i1, i2, j1, j2 in ops:
            if i1 <= n - 1 < i2:
                return tag, i1, i2, j1, j2
        raise SystemExit("%s: line %d out of range" % (path.name, n))

    def start(n: int) -> int:
        tag, i1, i2, j1, j2 = locate(n)
        return j1 + (n - 1 - i1) + 1 if tag == "equal" else j1 + 1

    def end(n: int) -> int:
        tag, i1, i2, j1, j2 = locate(n)
        return j1 + (n - 1 - i1) + 1 if tag == "equal" else j2

    return start, end, len(old_lines), len(new_lines)


def main() -> None:
    """Report every changed citation; write the docs only with --apply."""
    if len(sys.argv) != 2 or sys.argv[1] not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    lists = edit_lists()
    maps = {}
    for name, (list_name, path) in TARGETS.items():
        start, end, old_n, new_n = line_map(path, lists[list_name])
        maps[name] = (start, end)
        print("%s: %d -> %d lines" % (name, old_n, new_n))
    cite = re.compile(r"(src/melder/aether/spellbook/(spellbook|spell)\.py:)(\d+(?:-\d+)?(?:, \d+(?:-\d+)?)*)")
    for doc in DOCS:
        raw = doc.read_bytes()
        if b"\r\n" in raw:
            raise SystemExit("CRLF in %s" % doc.name)
        lines = raw.decode("utf-8").split("\n")
        stop = lines.index("## Context / Handoff Summary")
        changes = 0
        for idx in range(stop):
            def repl(m: re.Match) -> str:
                start, end = maps[m.group(2) + ".py"]
                parts = []
                for part in m.group(3).split(", "):
                    if "-" in part:
                        a, b = (int(x) for x in part.split("-"))
                        parts.append("%d-%d" % (start(a), end(b)))
                    else:
                        parts.append("%d" % start(int(part)))
                return m.group(1) + ", ".join(parts)
            new_line = cite.sub(repl, lines[idx])
            if new_line != lines[idx]:
                changes += 1
                print("%s:%d\n  - %s\n  + %s" % (doc.name, idx + 1, lines[idx].strip()[:150], new_line.strip()[:150]))
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
