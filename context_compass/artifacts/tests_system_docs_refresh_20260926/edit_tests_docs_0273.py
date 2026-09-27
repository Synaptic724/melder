"""Fold melder_2's two 0.2.73 test files (M2-9) into both tests docs: counts, clusters, C1 entries."""
import datetime
import pathlib
import sys
from typing import List, Tuple

ROOT = pathlib.Path.home() / "mnt/melder_private"
TC = ROOT / "context_compass/system_docs/tests_components.md"
TA = ROOT / "context_compass/system_docs/tests_architecture.md"
UNIT = "tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_door_held_root.py"
INTEG = "tests/integration/melder/conduit/test_conduit_integration_door_held_first_build.py"


def entry(path: str, now: str) -> str:
    """Render one measured C1 entry."""
    n = len((ROOT / path).read_bytes().decode("utf-8", "replace").splitlines())
    return f"- path: `{path}`\n  start_line: 1\n  end_line: {n}\n  loc: {n}\n  verified_at: {now}\n"


def apply(t: str, edits: List[Tuple[str, str]]) -> str:
    """Replace each anchor exactly once."""
    for old, new in edits:
        if t.count(old) != 1:
            raise SystemExit(f"ANCHOR {t.count(old)}: {old[:70]!r}")
        t = t.replace(old, new)
    return t


def main() -> int:
    """Edit both documents in place."""
    now = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    tc = TC.read_text(encoding="utf-8")
    tc = apply(tc, [
        ("- the densest tier: 461 `test_*.py` modules among 464 `.py` files",
         "- the densest tier: 462 `test_*.py` modules among 465 `.py` files"),
        ("- The spellbook tree carries 140 `test_*.py` modules beneath these",
         "- The spellbook tree carries 141 `test_*.py` modules beneath these"),
        ("- 141 `test_*.py` modules among 148 `.py` files; the others are benches and the",
         "- 142 `test_*.py` modules among 149 `.py` files; the others are benches and the"),
        ("the 34 test_*.py modules in\n  tests/integration/melder/conduit/",
         "the 35 test_*.py modules in\n  tests/integration/melder/conduit/"),
        ("The 743 test modules of the\nthree CI tiers", "The 745 test modules of the\nthree CI tiers"),
        ("  entry with no registered state (see `### Flow: Concurrent-Writer Stand-In`)\n",
         "  entry with no registered state (see `### Flow: Concurrent-Writer Stand-In`)\n"
         "- the door-held root (0.2.73): the normal plan of a `unique_per_conduit` or\n"
         "  spellspace root does not take the slot guard its route door already holds;\n"
         "  every other site and plan keeps its guard (`test_site_plan_door_held_root.py`)\n"),
        ("(key-set plans, 2026-09-26)\n- `tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_pool_snapshot_reads.py`\n",
         "(key-set plans, 2026-09-26)\n- `tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_pool_snapshot_reads.py`\n"
         f"- `{UNIT}`\n"),
        ("- teardown: idempotent cleanup that blocks meld, and dependents disposed before\n  their dependencies\n",
         "- teardown: idempotent cleanup that blocks meld, and dependents disposed before\n  their dependencies\n"
         "- door-held first builds (0.2.73): concurrent first melds of one root, on one\n"
         "  conduit or in one shared SpellSpace, construct it and its dependency once\n"),
        ("- `tests/integration/melder/conduit/test_ordered_disposal_runtime.py`\n",
         "- `tests/integration/melder/conduit/test_ordered_disposal_runtime.py`\n"
         f"- `{INTEG}`\n"),
        ("above - 181 paths - and nothing else.", "above - 183 paths - and nothing else."),
        ("## Diagrams\n### ASCII Component Diagram (C3/C2)\n",
         entry(UNIT, now) + entry(INTEG, now) + "\n## Diagrams\n### ASCII Component Diagram (C3/C2)\n"),
        ("moved out of `## Indexing` (portability rule). C1 ranges remeasured and the core\n",
         "moved out of `## Indexing` (portability rule). melder_2's two 0.2.73 tests (door-held\n"
         "first builds) are included. C1 ranges remeasured and the core\n"),
    ])
    TC.write_text(tc, encoding="utf-8")
    ta = TA.read_text(encoding="utf-8")
    ta = apply(ta, [
        ("- `unit/`: 464 `.py` files (334 on 2026-06-13)", "- `unit/`: 465 `.py` files (334 on 2026-06-13)"),
        ("- `integration/`: 148 `.py` files (88)", "- `integration/`: 149 `.py` files (88)"),
    ])
    TA.write_text(ta, encoding="utf-8")
    print("ok", now)
    return 0


if __name__ == "__main__":
    sys.exit(main())
