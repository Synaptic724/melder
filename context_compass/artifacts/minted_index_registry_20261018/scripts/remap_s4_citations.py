"""Remap the numeric `path:line` citations into spellbook.py, spell.py and mutation_research.py in src_architecture.md
and src_components.md after S4's edits A-D, line by line (melder_1; adapted from S9's remap).

The pre-edit text of each file is rebuilt by undoing its edits (their exact strings, read from apply_s4.py's EDITS);
difflib maps every old line to its new one. A range's start maps to the start of a replaced block and its end to the
block's end. The Context / Handoff Summary sections are history and are left as written. mutation_research.py is
CRLF in the working tree and is compared with its line endings normalized.
Usage: remap_s4_citations.py --root <tree> --check|--apply
"""
import ast
import difflib
import pathlib
import re
import sys

LANE = pathlib.Path(__file__).resolve().parents[1]
FILES = {
    "src/melder/aether/spellbook/spellbook.py": "SPELLBOOK",
    "src/melder/aether/spellbook/spell.py": "SPELL",
    "src/melder/mutation_research/mutation_research.py": "RESEARCH",
}
DOCS = ("context_compass/system_docs/src_architecture.md", "context_compass/system_docs/src_components.md")


def edits_by_file() -> dict:
    """Read apply_s4.py's EDITS (its file names are module-level names, given here) and group them by file."""
    tree = ast.parse((LANE / "scripts/apply_s4.py").read_text(encoding="utf-8"))
    names = {}
    edits = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            target = node.targets[0].id
            if target in ("SPELLBOOK", "SPELL", "RESEARCH"):
                names[target] = ast.literal_eval(node.value)
            elif target == "EDITS":
                edits = node.value
    if edits is None or len(names) != 3:
        raise SystemExit("apply_s4.py: EDITS or a file name not found")
    groups = eval(compile(ast.Expression(edits), "apply_s4.py", "eval"), {"__builtins__": {}}, names)
    by_file = {}
    for group in sorted(groups):
        for rel, label, old, new in groups[group]:
            by_file.setdefault(rel, []).append((label, old, new))
    return by_file


def line_map(path: pathlib.Path, edits: list) -> tuple:
    """Return (start, end) maps from pre-edit line numbers to post-edit ones, and both line counts."""
    new_text = path.read_bytes().decode("utf-8").replace("\r\n", "\n")
    old_text = new_text
    for label, old, new in reversed(edits):
        if old_text.count(new) != 1:
            raise SystemExit("%s: cannot undo %s" % (path.name, label))
        old_text = old_text.replace(new, old)
    redo = old_text
    for _label, old, new in edits:
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
        tag, i1, _i2, j1, _j2 = locate(n)
        return j1 + (n - 1 - i1) + 1 if tag == "equal" else j1 + 1

    def end(n: int) -> int:
        tag, i1, _i2, j1, j2 = locate(n)
        return j1 + (n - 1 - i1) + 1 if tag == "equal" else j2

    return start, end, len(old_lines), len(new_lines)


def main() -> None:
    """Report every changed citation; write the documents only with --apply."""
    args = sys.argv[1:]
    if len(args) != 3 or args[0] != "--root" or args[2] not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    root = pathlib.Path(args[1])
    grouped = edits_by_file()
    maps = {}
    for rel in FILES:
        start, end, old_n, new_n = line_map(root / rel, grouped[rel])
        maps[rel] = (start, end)
        print("%s: %d -> %d lines" % (rel.rsplit("/", 1)[1], old_n, new_n))
    cite = re.compile(r"(src/melder/(?:aether/spellbook/(?:spellbook|spell)|mutation_research/mutation_research)\.py)"
                      r":(\d+(?:-\d+)?(?:, \d+(?:-\d+)?)*)")
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
        if args[2] == "--apply":
            text = "\n".join(lines)
            doc.write_bytes(text.encode("utf-8"))
            if doc.read_bytes().decode("utf-8") != text:
                raise SystemExit("read-back mismatch in %s" % doc.name)
    if args[2] == "--apply":
        print("applied")


main()
