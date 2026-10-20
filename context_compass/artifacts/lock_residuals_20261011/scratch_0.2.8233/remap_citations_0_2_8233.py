"""
Remap `path:line` citations into the two files 0.2.8233 changed so each still points at the line it pointed at before
the change (whether or not that line was right before; stale citations stay stale, recorded in the ticket).

Usage: python remap_citations_0_2_8233.py <base tree> <landed tree> <doc> [<doc> ...]
"""
import difflib
import pathlib
import re
import sys

BASE, LANDED = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
FILES = ("src/melder/aether/spellbook/spellbook.py", "src/melder/aether/spellbook/spell.py")


def line_map(rel: str) -> dict[int, int]:
    old = (BASE / rel).read_bytes().decode("utf-8").splitlines()
    new = (LANDED / rel).read_bytes().decode("utf-8").splitlines()
    mapping: dict[int, int] = {}
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(a=old, b=new, autojunk=False).get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                mapping[i1 + k + 1] = j1 + k + 1
    return mapping


MAPS = {rel: line_map(rel) for rel in FILES}
CITE = re.compile(r"(src/melder/aether/spellbook/(?:spellbook|spell)\.py):(\d+(?:\s*-\s*\d+)?(?:,\s*\d+)*)")

for doc in sys.argv[3:]:
    path = pathlib.Path(doc)
    text = path.read_bytes().decode("utf-8")
    changes = []

    def remap(match: re.Match) -> str:
        rel, numbers = match.group(1), match.group(2)
        mapping = MAPS[rel]

        def one(n: re.Match) -> str:
            value = int(n.group(0))
            if value not in mapping:
                raise SystemExit(f"{doc}: {rel}:{value} cites a line this change rewrote - remap it by hand")
            return str(mapping[value])

        new_numbers = re.sub(r"\d+", one, numbers)
        if new_numbers != numbers:
            changes.append(f"{rel}:{numbers} -> {new_numbers}")
        return f"{rel}:{new_numbers}"

    text = CITE.sub(remap, text)
    path.write_bytes(text.encode("utf-8"))
    print(doc, "remapped", len(changes))
    for change in changes:
        print("   ", change)
