"""
Land the 0.2.8235 tests_components.md changes (TASK-2026-10-14-fix_many_child_follows_holder).

Adds the two new test modules to their clusters and the C1 code map, remeasures the touched
test_site_plan_lowering.py entry, and recounts the counts the new modules change. Every anchor must match exactly
once; the document stays LF. Regenerate tests_components_index.md afterwards.

Run from the repository root: python land_tests_docs_0_2_8235.py <verified_at UTC timestamp>
"""
import pathlib
import sys

COMP = "tests/component/melder/aether/conduit/test_conduit_component_many_child_disposed_with_its_holder.py"
INTEG = "tests/integration/melder/conduit/test_conduit_integration_many_child_disposed_with_its_holder.py"
LOWER = "tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_lowering.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    assert count == 1, (label, count)
    return text.replace(old, new)


def edit(text: str, stamp: str) -> str:
    text = replace_once(text, "- Updated: 2026-10-12\n", "- Updated: 2026-10-14\n", "metadata")
    text = replace_once(
        text,
        "- key-set plan lowering (`test_site_plan_lowering.py`): demand, placement, guard\n"
        "  order, call shape and unresolved inputs\n",
        "- key-set plan lowering (`test_site_plan_lowering.py`): demand, placement, guard\n"
        "  order, call shape, unresolved inputs, and the store a miss's `many` children register in (the holder's,\n"
        "  0.2.8235)\n",
        "compiler unit protects",
    )
    text = replace_once(
        text,
        "  through `_time_func`) and stretches again, and prewarming keeps 40 of each\n"
        "Key Files (C1):\n",
        "  through `_time_func`) and stretches again, and prewarming keeps 40 of each\n"
        "- holder-owned many children (0.2.8235): a slotted holder's disposal-bearing `many` child is recorded in the store\n"
        "  that owns the holder and disposed exactly once, when that owner ends - not when the lesser or spellspace that\n"
        "  first melded the holder ends (`unique`, `unique_per_conduit`, lineage; nested and override routes); controls\n"
        "  for holders built where they live; the opt-in singleton specializer builds one child, not one per warm meld\n"
        "Key Files (C1):\n",
        "aether component protects",
    )
    text = replace_once(
        text,
        "- `tests/component/melder/aether/conduit/test_kernel_pool_elastic_retention.py` (elastic pools, 2026-10-12)\n",
        "- `tests/component/melder/aether/conduit/test_kernel_pool_elastic_retention.py` (elastic pools, 2026-10-12)\n"
        f"- `{COMP}` (2026-10-14)\n",
        "aether component key files",
    )
    text = replace_once(
        text,
        "  conduit or in one shared SpellSpace, construct it and its dependency once\n"
        "Key Files (C1):\n",
        "  conduit or in one shared SpellSpace, construct it and its dependency once\n"
        "- holder-owned many children (0.2.8235): a borrowed `unique` holder first melded by its borrower and a cluster\n"
        "  holder first melded by a member keep their disposal-bearing `many` child open until the holder's owner ends\n"
        "Key Files (C1):\n",
        "conduit integration protects",
    )
    text = replace_once(
        text,
        "- `tests/integration/melder/conduit/test_conduit_integration_door_held_first_build.py`\n",
        "- `tests/integration/melder/conduit/test_conduit_integration_door_held_first_build.py`\n"
        f"- `{INTEG}` (2026-10-14)\n",
        "conduit integration key files",
    )
    text = replace_once(
        text,
        "- path: `tests/component/melder/aether/conduit/test_kernel_pool_elastic_retention.py`\n"
        "  start_line: 1\n"
        "  end_line: 169\n"
        "  loc: 169\n"
        "  verified_at: 2026-10-12T20:34:01Z\n",
        "- path: `tests/component/melder/aether/conduit/test_kernel_pool_elastic_retention.py`\n"
        "  start_line: 1\n"
        "  end_line: 169\n"
        "  loc: 169\n"
        "  verified_at: 2026-10-12T20:34:01Z\n"
        f"- path: `{COMP}`\n"
        "  start_line: 1\n"
        "  end_line: 513\n"
        "  loc: 513\n"
        f"  verified_at: {stamp}\n",
        "code map component",
    )
    text = replace_once(
        text,
        "- path: `tests/integration/melder/conduit/test_conduit_integration_door_held_first_build.py`\n"
        "  start_line: 1\n"
        "  end_line: 324\n"
        "  loc: 324\n"
        "  verified_at: 2026-09-26T22:15:16Z\n",
        "- path: `tests/integration/melder/conduit/test_conduit_integration_door_held_first_build.py`\n"
        "  start_line: 1\n"
        "  end_line: 324\n"
        "  loc: 324\n"
        "  verified_at: 2026-09-26T22:15:16Z\n"
        f"- path: `{INTEG}`\n"
        "  start_line: 1\n"
        "  end_line: 186\n"
        "  loc: 186\n"
        f"  verified_at: {stamp}\n",
        "code map integration",
    )
    text = replace_once(
        text,
        f"- path: `{LOWER}`\n"
        "  start_line: 1\n"
        "  end_line: 1179\n"
        "  loc: 1179\n"
        "  verified_at: 2026-09-26T22:11:36Z\n",
        f"- path: `{LOWER}`\n"
        "  start_line: 1\n"
        "  end_line: 1390\n"
        "  loc: 1390\n"
        f"  verified_at: {stamp}\n",
        "code map lowering",
    )
    text = replace_once(
        text,
        "- 156 `test_*.py` modules among 158 `.py` files\n",
        "- 164 `test_*.py` modules among 166 `.py` files (recounted 2026-10-14)\n",
        "component tier count",
    )
    text = replace_once(
        text,
        "the 70 test_*.py modules in\n  tests/component/melder/aether/",
        "the 75 test_*.py modules in\n  tests/component/melder/aether/",
        "component aether count",
    )
    text = replace_once(
        text,
        "- 157 `test_*.py` modules among 164 `.py` files; the others are benches and the\n",
        "- 158 `test_*.py` modules among 165 `.py` files (recounted 2026-10-14); the others are benches and the\n",
        "integration tier count",
    )
    text = replace_once(
        text,
        "the 36 test_*.py modules in\n  tests/integration/melder/conduit/",
        "the 37 test_*.py modules in\n  tests/integration/melder/conduit/",
        "integration conduit count",
    )
    text = replace_once(
        text,
        "- the densest tier: 476 `test_*.py` modules among 479 `.py` files\n",
        "- the densest tier: 480 `test_*.py` modules among 483 `.py` files (recounted 2026-10-14)\n",
        "unit tier count",
    )
    text = replace_once(
        text,
        "above - 214 paths - and nothing else.",
        "above - 217 paths (recounted 2026-10-14) - and nothing else.",
        "core set",
    )
    text = replace_once(
        text,
        "The 789 test modules of the\nthree CI tiers",
        "The 802 test modules of the\nthree CI tiers",
        "three tier total",
    )
    text = replace_once(
        text,
        "## Context / Handoff Summary\n\n",
        "## Context / Handoff Summary\n\n"
        "2026-10-14 holder-owned many children (0.2.8235): the Aether Component Cluster gains\n"
        "`test_conduit_component_many_child_disposed_with_its_holder.py` (each slotted holder's `many` child recorded in and\n"
        "disposed with the holder's owner; the specializer building one child) and the Conduit Integration Cluster\n"
        "`test_conduit_integration_many_child_disposed_with_its_holder.py` (borrower and cluster member); the Spellbook\n"
        "Compiler Unit Cluster's site-plan test pins a miss's children to the holder's store. The core set is 217 paths and\n"
        "the tier counts are recounted from disk (802 test modules in the three tiers; the unit tier's 4 and 7 of the\n"
        "component tier's 8 new modules came from earlier lanes). Only the two new code-map entries and the touched\n"
        "`test_site_plan_lowering.py` were measured; 15 other stale ranges here and 2 in tests_architecture are left as\n"
        "found.\n\n",
        "handoff",
    )
    return text


def main() -> int:
    stamp = sys.argv[1]
    path = pathlib.Path("context_compass/system_docs/tests_components.md")
    raw = path.read_bytes()
    assert b"\r" not in raw
    text = edit(raw.decode("utf-8"), stamp)
    path.write_bytes(text.encode("utf-8"))
    long_lines = [
        (number, len(line)) for number, line in enumerate(text.split("\n"), 1)
        if len(line) > 120 and "`tests/" not in line and "`src/" not in line
    ]
    print("tests_components.md lines", text.count("\n"), "long prose lines", long_lines[:10])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
