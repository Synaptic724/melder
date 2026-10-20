"""
tests_architecture for fix #1 (find_spell_by_spell_id_2026_10_17): exact-once edits, all or nothing.

Usage: python docs_tests_architecture_fix1.py <repo_root> [--check]

Metadata, the recounted inventory under Source Coverage and Evidence, the one citation fix #1's codemod moved (the
notch-revalidation module's race test, one line further down since a comment became two lines) and a handoff entry.
The lane adds no tier, conftest, marker or shared support module, so nothing else here changes. The index is
regenerated after this script.
"""
import pathlib
import sys

DOC = "context_compass/system_docs/tests_architecture.md"

EDITS = [
    ("- Updated: 2026-10-16\n", "- Updated: 2026-10-17\n"),
    ("- `unit/`: 511 `.py` files, 508 of them `test_*.py` (465 on 2026-09-26, 334 on 2026-06-13)\n",
     "- `unit/`: 512 `.py` files, 509 of them `test_*.py` (465 on 2026-09-26, 334 on 2026-06-13)\n"),
    ("- `integration/`: 177 `.py` files, 170 of them `test_*.py` (149, 88)\n",
     "- `integration/`: 179 `.py` files, 172 of them `test_*.py` (149, 88)\n"),
    ("Recounted 2026-10-16 with `find tests/<tier> -name '*.py'` (pycache excluded); the three tiers' 844 `test_*.py`\n",
     "Recounted 2026-10-17 with `find tests/<tier> -name '*.py'` (pycache excluded); the three tiers' 847 `test_*.py`\n"),
    ("  EVIDENCE: tests/integration/melder/conduit/test_conduit_integration_notch_revalidation.py:623-672\n",
     "  EVIDENCE: tests/integration/melder/conduit/test_conduit_integration_notch_revalidation.py:624-673\n"),
    ("## Context / Handoff Summary\n\n2026-10-16 contract recheck on notch (0.2.8250)",
     "## Context / Handoff Summary\n\n"
     "2026-10-17 lookup by spell_id is exact (0.2.8253): the inventory is recounted from disk (unit 512 `.py`,\n"
     "component 168, integration 179, mocks 44, experimentation 204; 847 test modules in the three tiers) - the lane\n"
     "adds one unit module (the Rift rooms' lookups by spell_id over doubles) and two integration modules (a lender\n"
     "and borrower world; a capability room) and renames one component module, catalogued in `tests_components`.\n"
     "Its codemod renamed the lookups in 82 test files and rewrote a comment in the notch-revalidation module as two\n"
     "lines, so the race test's evidence under `## Failure Modes and Error Paths` moves one line (624-673). No tier,\n"
     "conftest, declared marker or shared support module changes, and no extent in this map moves.\n\n"
     "2026-10-16 contract recheck on notch (0.2.8250)"),
]


def main() -> None:
    """Apply every edit exactly once to a copy in memory; write it unless --check."""
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    check = "--check" in sys.argv[1:]
    if len(args) != 1:
        raise SystemExit(__doc__)
    root = pathlib.Path(args[0]).resolve()
    doc = root / DOC
    raw = doc.read_bytes()
    if b"\r" in raw:
        raise SystemExit("FAIL: the document is expected to be LF")
    text = raw.decode("utf-8")
    for old, new in EDITS:
        n = text.count(old)
        if n != 1:
            raise SystemExit(f"FAIL anchor count {n}: {old[:90]!r}")
        text = text.replace(old, new)
        for ln in new.split("\n"):
            if len(ln) > 120:
                print(f"NOTE over 120 ({len(ln)}): {ln[:100]}...")
    if check:
        print("check only: nothing written")
        return
    doc.write_bytes(text.encode("utf-8"))
    print("written", DOC)


if __name__ == "__main__":
    main()
