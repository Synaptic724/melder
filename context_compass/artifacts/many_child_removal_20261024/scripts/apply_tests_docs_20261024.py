"""Apply melder_1's 0.2.8267 edits to tests_components.md and tests_architecture.md.

Usage: python apply_tests_docs_20261024.py <system_docs dir> <verified_at timestamp>
Every edit is anchored on text and asserts a single match; each file is written only if it is unchanged since read.
"""
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
stamp = sys.argv[2]
report = []

COMPONENT_OLD = "tests/component/melder/aether/conduit/test_conduit_component_many_child_disposed_with_its_holder.py"
COMPONENT_NEW = "tests/component/melder/aether/conduit/test_conduit_component_many_child_belongs_to_the_scope_that_built_it.py"
INTEGRATION_OLD = "tests/integration/melder/conduit/test_conduit_integration_many_child_disposed_with_its_holder.py"
INTEGRATION_NEW = "tests/integration/melder/conduit/test_conduit_integration_many_child_belongs_to_the_scope_that_built_it.py"
LIFETIME_OLD = "tests/integration/melder/conduit/test_conduit_integration_holder_children_lifetime.py"
LIFETIME_NEW = "tests/integration/melder/conduit/test_conduit_integration_holder_cleanup_leaves_its_many_children.py"


def edit(name, edits):
    path = root / name
    raw = path.read_bytes()
    doc = raw.decode("utf-8")
    assert "\r\n" not in doc
    for old, new in edits:
        assert doc.count(old) == 1, (name, doc.count(old), old[:90])
        doc = doc.replace(old, new)
        report.append(new)
    assert path.read_bytes() == raw, name + " changed while the edits were prepared"
    path.write_bytes(doc.encode("utf-8"))
    print("wrote", path, len(doc.split("\n")) - 1, "lines")


TC_HANDOFF = (
    "2026-10-24 a `many` belongs to the scope that built it (0.2.8267;\n"
    "STORY-2026-10-24-remove_many_child_holder_ownership): the Aether Component Cluster swaps\n"
    "`test_conduit_component_many_child_disposed_with_its_holder.py` for\n"
    "`test_conduit_component_many_child_belongs_to_the_scope_that_built_it.py` (24 tests: on every route the scope that\n"
    "melded a holder records its `many` child and disposes it once when it ends, controls, the specializer), and the\n"
    "Conduit Integration Cluster swaps `test_conduit_integration_many_child_disposed_with_its_holder.py` and\n"
    "`test_conduit_integration_holder_children_lifetime.py` for\n"
    "`test_conduit_integration_many_child_belongs_to_the_scope_that_built_it.py` (2 tests: a borrower and a cluster\n"
    "member) and `test_conduit_integration_holder_cleanup_leaves_its_many_children.py` (10 tests: purge, transfer, the\n"
    "child spell's purge, a failing child, teardown order); the unit `test_creations_holder_children.py` (thirteen\n"
    "record cases) is deleted with the record, and the Spellbook Compiler Unit Cluster's lowering and door-held entries\n"
    "say a miss registers its children in the innermost scope. The six changed or new modules are remeasured in the\n"
    "core map; the key-file union stays 282 paths (three swapped one for one). Counts are recounted from disk (unit 518\n"
    "`.py`, 515 of them `test_*.py`; component 172, 170; integration 185, 178; 863 test modules in the three tiers): this\n"
    "lane removes one module net, and the count also takes in the two 0.2.8266 regression modules\n"
    "(`test_conduit_component_refused_cache_save_does_not_fail_meld.py`, `test_caching_system_refused_save.py`), which no\n"
    "cluster lists yet.\n\n"
)

edit("tests_components.md", [
    (
        "  order, call shape, unresolved inputs, and the store a miss's `many` children register in (the holder's,\n"
        "  0.2.8235)\n",
        "  order, call shape, unresolved inputs, and the store a miss's `many` children register in (the meld's\n"
        "  innermost scope, as at the plan top, with no adoption line; 0.2.8267)\n",
    ),
    (
        "  every other site and plan keeps its guard (`test_site_plan_door_held_root.py`)\n",
        "  every other site and plan keeps its guard, and the root's miss registers its `many` child in the\n"
        "  innermost scope (0.2.8267) (`test_site_plan_door_held_root.py`)\n",
    ),
    (
        "- holder-owned many children (0.2.8235): a slotted holder's disposal-bearing `many` child is recorded in the store\n"
        "  that owns the holder and disposed exactly once, when that owner ends - not when the lesser or spellspace that\n"
        "  first melded the holder ends (`unique`, `unique_per_conduit`, lineage; nested and override routes); controls\n"
        "  for holders built where they live; the opt-in singleton specializer builds one child, not one per warm meld\n",
        "- a `many` belongs to the scope that built it (0.2.8267;\n"
        "  `test_conduit_component_many_child_belongs_to_the_scope_that_built_it.py`): a slotted holder's disposal-bearing\n"
        "  `many` child is recorded in the store of the lesser or spellspace that first melded the holder and disposed exactly\n"
        "  once, when that scope ends, while the holder's owner keeps serving the holder (`unique`, `unique_per_conduit`,\n"
        "  lineage; nested and override routes); controls for holders built where they live; the opt-in singleton\n"
        "  specializer builds one child, recorded by the scope that built it\n",
    ),
    ("- `" + COMPONENT_OLD + "` (2026-10-14)\n", "- `" + COMPONENT_NEW + "` (2026-10-24)\n"),
    (
        "- holder-owned many children (0.2.8235): a borrowed `unique` holder first melded by its borrower and a cluster\n"
        "  holder first melded by a member keep their disposal-bearing `many` child open until the holder's owner ends\n",
        "- a `many` belongs to the scope that built it (0.2.8267;\n"
        "  `test_conduit_integration_many_child_belongs_to_the_scope_that_built_it.py`): a borrower that first melds a\n"
        "  contracted `unique` and a cluster member that first melds a cluster holder dispose the `many` child they built\n"
        "  when they tear down, once, while the holder lives on with its owner\n",
    ),
    (
        "- holder records (0.2.8238): purging a holder disposes its `many` child after it (also for a holder without disposal\n"
        "  methods, in a spellspace and by the owner of a `unique`), nothing accumulates over purge-and-meld cycles, a `many`\n"
        "  purge of the child's spell leaves a live holder's child open, and an ownership move carries the child\n",
        "- holder cleanup (0.2.8267; `test_conduit_integration_holder_cleanup_leaves_its_many_children.py`): purging a holder -\n"
        "  whole or one instance, with or without disposal methods, in a spellspace and by the owner of a `unique` - runs only\n"
        "  the holder's own methods and leaves its `many` child to the store that built it, which disposes it once at its end\n"
        "  and raises a failing child's disposal there; a `many` purge of the child's spell disposes every child its store\n"
        "  recorded; an ownership move leaves the child in the store that built it (with `include_dependencies` it moves with\n"
        "  its spell and is disposed once, at the target); teardown disposes a holder before its `many` child\n",
    ),
    ("- `" + INTEGRATION_OLD + "` (2026-10-14)\n", "- `" + INTEGRATION_NEW + "` (2026-10-24)\n"),
    ("- `" + LIFETIME_OLD + "` (2026-10-14)\n", "- `" + LIFETIME_NEW + "` (2026-10-24)\n"),
    (
        "builders - not every `test_*.py` module beneath it. The 862 test modules of the\n",
        "builders - not every `test_*.py` module beneath it. The 863 test modules of the\n",
    ),
    (
        "- path: `" + COMPONENT_OLD + "`\n  start_line: 1\n  end_line: 535\n  loc: 535\n  verified_at: 2026-10-15T22:33:31Z\n",
        "- path: `" + COMPONENT_NEW + "`\n  start_line: 1\n  end_line: 511\n  loc: 511\n  verified_at: " + stamp + "\n",
    ),
    (
        "- path: `tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_lowering.py`\n"
        "  start_line: 1\n  end_line: 1475\n  loc: 1475\n  verified_at: 2026-10-15T22:33:31Z\n",
        "- path: `tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_lowering.py`\n"
        "  start_line: 1\n  end_line: 1468\n  loc: 1468\n  verified_at: " + stamp + "\n",
    ),
    (
        "- path: `tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_door_held_root.py`\n"
        "  start_line: 1\n  end_line: 403\n  loc: 403\n  verified_at: 2026-10-15T22:33:31Z\n",
        "- path: `tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_door_held_root.py`\n"
        "  start_line: 1\n  end_line: 402\n  loc: 402\n  verified_at: " + stamp + "\n",
    ),
    (
        "- path: `" + INTEGRATION_OLD + "`\n  start_line: 1\n  end_line: 218\n  loc: 218\n  verified_at: 2026-10-15T22:33:31Z\n",
        "- path: `" + INTEGRATION_NEW + "`\n  start_line: 1\n  end_line: 197\n  loc: 197\n  verified_at: " + stamp + "\n",
    ),
    (
        "- path: `" + LIFETIME_OLD + "`\n  start_line: 1\n  end_line: 415\n  loc: 415\n  verified_at: 2026-10-14T23:59:35Z\n",
        "- path: `" + LIFETIME_NEW + "`\n  start_line: 1\n  end_line: 440\n  loc: 440\n  verified_at: " + stamp + "\n",
    ),
    (
        "- path: `tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_lowering_managed.py`\n"
        "  start_line: 1\n  end_line: 883\n  loc: 883\n  verified_at: 2026-10-16T11:13:43Z\n",
        "- path: `tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_lowering_managed.py`\n"
        "  start_line: 1\n  end_line: 878\n  loc: 878\n  verified_at: " + stamp + "\n",
    ),
    (
        "- `tests/integration/melder/crystallizer/test_ordered_disposal_replay.py`\n\n## Open Questions",
        "- `tests/integration/melder/crystallizer/test_ordered_disposal_replay.py`\n"
        "- `" + COMPONENT_NEW + "`\n- `" + INTEGRATION_NEW + "`\n- `" + LIFETIME_NEW + "`\n\n## Open Questions",
    ),
    (
        "## Context / Handoff Summary\n\n2026-10-24 Python 3.15 cells and publication without a test rerun",
        "## Context / Handoff Summary\n\n" + TC_HANDOFF + "2026-10-24 Python 3.15 cells and publication without a test rerun",
    ),
])

TA_HANDOFF = (
    "2026-10-24 a `many` belongs to the scope that built it (0.2.8267): the inventory is recounted from disk (unit 518\n"
    "`.py`, 515 of them `test_*.py`; component 172, 170; integration 185, 178; 863 test modules in the three tiers) - the\n"
    "lane deletes four modules (the 0.2.8235 and 0.2.8238 feature tests, one of them a unit test of the removed holder\n"
    "record) and adds three for the new contract, catalogued in `tests_components`; the count also takes in the two\n"
    "0.2.8266 regression modules. No tier, conftest, declared marker or shared support module changes, and no extent in\n"
    "this map moves.\n\n"
)

edit("tests_architecture.md", [
    (
        "- `component/`: 171 `.py` files, 169 of them `test_*.py` (143, 81)\n",
        "- `component/`: 172 `.py` files, 170 of them `test_*.py` (143, 81)\n",
    ),
    (
        "Recounted 2026-10-19 with `rg --files tests/<tier> -g '*.py'` (pycache excluded); the three tiers' 862 `test_*.py`\n",
        "Recounted 2026-10-24 with `rg --files tests/<tier> -g '*.py'` (pycache excluded); the three tiers' 863 `test_*.py`\n",
    ),
    (
        "## Context / Handoff Summary\n\n2026-10-24 Python 3.14.9, 3.15.0 and 3.15.1 cells",
        "## Context / Handoff Summary\n\n" + TA_HANDOFF + "2026-10-24 Python 3.14.9, 3.15.0 and 3.15.1 cells",
    ),
])

for block in report + [TC_HANDOFF, TA_HANDOFF]:
    for line in block.split("\n"):
        if len(line) > 120 and not line.lstrip().startswith(("- path: `", "- `", "`test", "`tests")):
            print("LONG", len(line), line[:100])
