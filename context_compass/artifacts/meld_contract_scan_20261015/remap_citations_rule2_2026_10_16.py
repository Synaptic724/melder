"""Remap numeric path:line citations in the system docs across rule 2 (0.2.8250; melder_1, 2026-10-16).

usage: python remap_citations.py <repo root> <pristine src root> [--apply]
"""
import difflib
import pathlib
import re
import sys

ROOT = pathlib.Path(sys.argv[1])
BASE = pathlib.Path(sys.argv[2])
APPLY = "--apply" in sys.argv[3:]
FILES = [
    "melder/aether/spellbook/spellbook.py",
    "melder/aether/conduit/conduit.py",
    "melder/aether/conduit/conduit_ward/conduit_ward.py",
    "melder/aether/conduit/meld/meld.py",
    "melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py",
    "melder/aether/spellbook/spell_compiler/validation/strategies/contract_provider_presence_strategy.py",
    "melder/utilities/custom_exceptions/spellbook_validation_error.py",
]
DOCS = ["src_architecture.md", "src_components.md", "tests_components.md", "tests_architecture.md"]


def lines(path):
    return path.read_bytes().decode("utf-8").replace("\r\n", "\n").split("\n")


def mapping(old, new):
    """old 1-based line -> (new 1-based line, exact) ; exact False when the old line sits in a changed hunk."""
    out = {}
    sm = difflib.SequenceMatcher(a=old, b=new, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        for k in range(i1, i2):
            if tag == "equal":
                out[k + 1] = (j1 + (k - i1) + 1, True)
            else:
                out[k + 1] = (j1 + 1, False)
    return out


maps = {}
for rel in FILES:
    maps[rel] = mapping(lines(BASE / rel), lines(ROOT / "src" / rel))

pat = re.compile(r"(src/(" + "|".join(re.escape(f) for f in FILES) + r")):(\d+(?:\s*-\s*\d+)?(?:,\s*\d+(?:\s*-\s*\d+)?)*)")
for doc in DOCS:
    path = ROOT / "context_compass" / "system_docs" / doc
    raw = path.read_bytes().decode("utf-8")
    crlf = raw.count("\r\n") > 0 and raw.count("\r\n") == raw.count("\n")
    text = raw.replace("\r\n", "\n")
    changes = []

    def repl(m):
        rel = m.group(2)
        nums = m.group(3)
        def one(n):
            new, exact = maps[rel][int(n)]
            if not exact:
                changes.append(f"   INEXACT {rel}:{n} -> {new}")
            return str(new)
        new_nums = re.sub(r"\d+", lambda x: one(x.group(0)), nums)
        if new_nums != nums:
            changes.append(f"   {rel}:{nums} -> {new_nums}")
        return f"{m.group(1)}:{new_nums}"

    new_text = pat.sub(repl, text)
    print(doc, len(changes), "changes")
    for c in changes:
        print(c)
    if APPLY and new_text != text:
        path.write_bytes((new_text.replace("\n", "\r\n") if crlf else new_text).encode("utf-8"))
        print("   written")
