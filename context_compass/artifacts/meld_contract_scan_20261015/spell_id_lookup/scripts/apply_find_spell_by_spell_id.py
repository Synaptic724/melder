"""
Fix #1 of TASK-2026-10-16-recheck_contract_consumers_when_provider_changes (owner, 2026-10-17):
`Spellbook.find_spell_by_id` -> `find_spell_by_spell_id` and `Conduit.get_spell_by_id` ->
`get_spell_by_spell_id`, both exact - a lookup by spell_id returns the spell that owns the spell_id,
active or parked, never the spell its index has active. Callers that need the index's active spell
take an explicit index step.

Usage: python apply_find_spell_by_spell_id.py <root> <since_version> [--check]
  <root>           a tree holding src/melder (the repository root or a scratch copy)
  <since_version>  the notch this lands as; written where a docstring says "until <version>"
  --check          verify every block hash and anchor; write nothing
After writing, the tree holds no `find_spell_by_id` and no `.get_spell_by_id(` call in src/melder
(generated _build_assets payloads excepted; the Rift room command keeps its own name).
"""
import pathlib
import re
import sys

from apply_engine import EditEngine
import edits_callers
import edits_lookup
import edits_sites


def verify_tree(root: pathlib.Path) -> None:
    """Fail on any code use of the old names in src/melder; list the prose mentions left for review."""
    rift_files = ("command_system.py", "static_command_system.py")
    bad = []
    prose = []
    for path in sorted((root / "src" / "melder").rglob("*.py")):
        rel = path.relative_to(root).as_posix()
        if "/_build_assets/" in rel:
            continue
        text = path.read_text(encoding="utf-8")
        for number, line in enumerate(text.splitlines(), 1):
            code_use = (
                re.search(r"\.find_spell_by_id\(", line)
                or re.search(r"def find_spell_by_id\b", line)
                or re.search(r"\.get_spell_by_id\(", line)
                or (re.search(r"def get_spell_by_id\b", line) and not rel.endswith(rift_files))
            )
            if code_use:
                bad.append(f"{rel}:{number}: {line.strip()}")
            elif re.search(r"\bfind_spell_by_id\b|\bget_spell_by_id\b", line) and not rel.endswith(rift_files):
                prose.append(f"{rel}:{number}: {line.strip()}")
    for item in prose:
        print("PROSE", item)
    for item in bad:
        print("LEFT", item)
    if bad:
        raise SystemExit(f"FAIL {len(bad)} old-name code uses left")
    print(f"tree ok: no code use of the old names; {len(prose)} prose mentions listed")


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    check = "--check" in sys.argv[1:]
    if len(args) != 2 or not re.fullmatch(r"\d+\.\d+\.\d+", args[1]):
        raise SystemExit(__doc__)
    root = pathlib.Path(args[0]).resolve()
    engine = EditEngine(root, args[1])
    edits_lookup.register(engine)
    edits_callers.register(engine)
    edits_sites.register(engine)
    engine.run(check)
    if not check:
        verify_tree(root)


if __name__ == "__main__":
    main()
