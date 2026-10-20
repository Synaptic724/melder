"""
Remap `path:line` citations into the source files fix #1 changed (find_spell_by_spell_id_2026_10_17).

Usage: python remap_citations.py <old_root> <new_root> <doc>... [--write]

For each changed file (old_root/<path> differs from new_root/<path>), the old and new texts are aligned with
difflib, line for line. Every citation `path:N`, `path:N-M` and the comma lists that follow one (`path:N, M-K`) in
each document is reported with its old and new numbers. A number whose old line sits inside an unchanged block maps
exactly; one whose line was edited, removed or inserted around is reported as UNMAPPED and is never rewritten -
those are opened and fixed by hand. With --write, only documents whose every changed-file citation mapped are
rewritten; nothing else in them changes.
"""
import difflib
import pathlib
import re
import sys

CITE = re.compile(r"(?P<path>src/[A-Za-z0-9_/.]*\.py):(?P<nums>\d+(?:\s*-\s*\d+)?(?:,\s*\d+(?:\s*-\s*\d+)?)*)")
NUM = re.compile(r"(\d+)(?:\s*-\s*(\d+))?")


def line_map(old_text: str, new_text: str) -> dict:
    old = old_text.split("\n")
    new = new_text.split("\n")
    sm = difflib.SequenceMatcher(None, old, new, autojunk=False)
    mapping = {}
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                mapping[i1 + k + 1] = j1 + k + 1
    return mapping


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    write = "--write" in sys.argv[1:]
    if len(args) < 3:
        raise SystemExit(__doc__)
    old_root, new_root = pathlib.Path(args[0]), pathlib.Path(args[1])
    maps = {}
    for doc in args[2:]:
        path = pathlib.Path(doc)
        text = path.read_text(encoding="utf-8")
        unmapped = 0
        changed = 0

        def repl(match):
            nonlocal unmapped, changed
            rel = match.group("path")
            old_file, new_file = old_root / rel, new_root / rel
            if not old_file.exists() or not new_file.exists():
                return match.group(0)
            old_text = old_file.read_text(encoding="utf-8")
            new_text = new_file.read_text(encoding="utf-8")
            if old_text == new_text:
                return match.group(0)
            if rel not in maps:
                maps[rel] = line_map(old_text, new_text)
            mapping = maps[rel]

            def one(m):
                nonlocal unmapped, changed
                a = int(m.group(1))
                b = int(m.group(2)) if m.group(2) else None
                na = mapping.get(a)
                nb = mapping.get(b) if b is not None else None
                ok = na is not None and (b is None or nb is not None)
                where = f"{doc}:{text.count(chr(10), 0, match.start()) + 1}"
                label = f"{a}" + (f"-{b}" if b is not None else "")
                if not ok:
                    unmapped += 1
                    print(f"UNMAPPED {where} {rel}:{label}")
                    return m.group(0)
                new_label = f"{na}" + (f"-{nb}" if nb is not None else "")
                if new_label != label:
                    changed += 1
                    print(f"MAP      {where} {rel}:{label} -> {new_label}")
                return new_label

            return f"{rel}:" + NUM.sub(one, match.group("nums"))

        new_doc = CITE.sub(repl, text)
        print(f"{doc}: changed={changed} unmapped={unmapped}")
        if write and unmapped == 0 and new_doc != text:
            path.write_text(new_doc, encoding="utf-8")
            print(f"written {doc}")


if __name__ == "__main__":
    main()
