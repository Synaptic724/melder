"""Catalogue the rule-1 tests (0.2.8247) in tests_components and recount tests_architecture (melder_1, 2026-10-16).

usage (from the repository root): python <this script> <UTC timestamp> [--check]
Exact-text edits; each anchor must occur once; line endings kept.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from apply_lib import one  # the lane's exact-text replacement (refuses a missing or repeated anchor)

TS = sys.argv[1]
CHECK = "--check" in sys.argv[2:]
TC = pathlib.Path("context_compass/system_docs/tests_components.md")
TA = pathlib.Path("context_compass/system_docs/tests_architecture.md")
A = "tests/unit/melder/aether/dev_ops/spell_system_states/test_spell_system_states_non_resolvable.py"
B = "tests/unit/melder/aether/dev_ops/risk_manager/test_risk_manager_non_resolvable.py"
D = "tests/component/melder/aether/dev_ops/spell_system_states/test_non_resolvable_validation_flag_component.py"


def apply(path, steps, check_only):
    """Exact-text steps; a new line may pass 120 characters only when it holds one unbreakable token."""
    raw = path.read_bytes().decode("utf-8")
    crlf = raw.count("\r\n") > 0 and raw.count("\r\n") == raw.count("\n")
    text = raw.replace("\r\n", "\n")
    for old, new in steps:
        for line in new.splitlines():
            if len(line) > 120 and len(line.strip().split()) != 1 and line not in old:
                raise SystemExit(f"{path}: new prose line longer than 120 characters ({len(line)}): {line!r}")
        text = one(text, old, new, str(path))
    if not check_only:
        path.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))
    print(("checked " if check_only else "applied ") + str(path) + (" (CRLF kept)" if crlf else ""))


SUITE_OLD = (
    "  through an ownership transfer (see `### Subcomponent: Managed Spell Pools Unit Cluster` and the spellbook\n"
    "  clusters)\n"
)
SUITE_NEW = SUITE_OLD + (
    "- the control plane's capability flag (0.2.8247): `SpellState.non_resolvable`, the registry's published set of\n"
    "  flagged lineages and RiskManager's Book flag that leaves them out (see\n"
    "  `### Subcomponent: DevOps Control Plane Unit Cluster`)\n"
)
CLUSTER_ANCHOR = "### Subcomponent: Managed Spell Pools Unit Cluster\n"
CLUSTER_NEW = (
    "### Subcomponent: DevOps Control Plane Unit Cluster\n"
    "Parent Component: Unit Test Suite\n"
    "Purpose:\n"
    "- verify the per-frame control plane's capability flag and the Book flag RiskManager distils from its risk sets,\n"
    "  on a real `SpellSystemStates` registry rather than a stub\n"
    "Protects:\n"
    "- `SpellState.non_resolvable` (0.2.8247; `test_spell_system_states_non_resolvable.py`, 34 tests): `update_flags`\n"
    "  and `has_flag` leave validity alone and refuse a cleaned state; `clear_dirty` keeps the flag; `register_index`\n"
    "  sets it for resolvable=False, clears it for True, keeps it with no capability only for an unchanged selection,\n"
    "  refuses a non-bool before registering anything, writes it before the gate's RiskManager callback and\n"
    "  re-publishes once when the flag changed on a lineage already gated; the published `non_resolvable_index_ids`\n"
    "  follows every registration path, `unregister_index` and cleanup's tombstone, is replaced rather than mutated,\n"
    "  and agrees with each lineage's flag\n"
    "- RiskManager's distillation (0.2.8247; `test_risk_manager_non_resolvable.py`, 11 tests): a flagged lineage alone\n"
    "  leaves the Book flag down while the risk sets keep it, one unflagged risky lineage raises it, `spell:` keys and\n"
    "  removed lineages count, a registration that clears the flag raises the Book flag at its event - also in a\n"
    "  borrower after a notch back to a lineage already gated - and `register_conduit` and `register_spell` write the\n"
    "  flag once; the registry stub of `test_risk_manager.py` answers an empty set, so its 21 tests keep their meaning\n"
    "Key Files (C1):\n"
    f"- `{A}` (2026-10-16)\n"
    f"- `{B}` (2026-10-16)\n"
    "\n"
    "### Subcomponent: Managed Spell Pools Unit Cluster\n"
)
COMP_PROTECTS_OLD = "  `test_conduit_component_purge.py` pins a managed purge: 0, before any lock, the pool kept\n"
COMP_PROTECTS_NEW = COMP_PROTECTS_OLD + (
    "- non-resolvable definitions and the Book flag (0.2.8247; `test_non_resolvable_validation_flag_component.py`, 9\n"
    "  tests): automatic and dynamic worlds holding a Protocol definition keep the Book flag down, so later melds skip\n"
    "  the validation gate while a meld of the definition is still refused; an override consumer of a definition melds\n"
    "  without the gate; a notch to a definition and back moves the flag; an index-linked borrower revalidates the\n"
    "  version it gets back after a repeat notch; a transferred definition keeps the exclusion on its new owner and a\n"
    "  rolled-back transfer on its source; a contract consumer beside a definition still follows its lender's notch;\n"
    "  and four threads melding while 40 notches flip the lineage never build the definition (a lookup that lands\n"
    "  inside a notch's swap may raise the pre-existing KeyError, which the test accepts). Every flag check asserts\n"
    "  that the registry's published set agrees with the lineage's flag\n"
)
COMP_KEYS_OLD = "- `tests/component/melder/aether/conduit/test_conduit_component_managed_spell_quantity.py` (2026-10-15)\n"
COMP_KEYS_NEW = COMP_KEYS_OLD + f"- `{D}`\n"
UNIT_C1_OLD = (
    "- path: `tests/unit/melder/aether/test_static_rooms_managed_spell_quantity.py`\n"
    "  start_line: 1\n  end_line: 100\n  loc: 100\n  verified_at: 2026-10-15T22:33:31Z\n"
    "  note: static rooms treat a managed spell like `many` (0.2.8243).\n"
)
UNIT_C1_NEW = UNIT_C1_OLD + (
    f"- path: `{A}`\n  start_line: 1\n  end_line: 484\n  loc: 484\n  verified_at: {TS}\n"
    "  note: the capability flag, `register_index`'s write and re-publication, the published set (0.2.8247).\n"
    f"- path: `{B}`\n  start_line: 1\n  end_line: 296\n  loc: 296\n  verified_at: {TS}\n"
    "  note: RiskManager's Book flag ignores flagged lineages, on a real registry (0.2.8247).\n"
)
COMP_C1_OLD = (
    "- path: `tests/component/melder/aether/conduit/test_conduit_component_managed_spell_quantity.py`\n"
    "  start_line: 1\n  end_line: 491\n  loc: 491\n  verified_at: 2026-10-15T22:33:31Z\n"
    "  note: leases through real melds, injections and `managed_spell_meld` (0.2.8245).\n"
)
COMP_C1_NEW = COMP_C1_OLD + (
    f"- path: `{D}`\n  start_line: 1\n  end_line: 456\n  loc: 456\n  verified_at: {TS}\n"
    "  note: non-resolvable definitions keep the Book flag down through worlds, notches, transfers and races (0.2.8247).\n"
)
SB_OLD = ("- path: `tests/unit/melder/spellbook/test_spellbook.py`\n"
          "  start_line: 1\n  end_line: 5285\n  loc: 5285\n  verified_at: 2026-10-15T22:33:31Z\n")
SB_NEW = ("- path: `tests/unit/melder/spellbook/test_spellbook.py`\n"
          f"  start_line: 1\n  end_line: 5288\n  loc: 5288\n  verified_at: {TS}\n")
CSB_OLD = ("- path: `tests/component/melder/spellbook/test_spellbook_component_spellbook.py`\n"
           "  start_line: 1\n  end_line: 1705\n  loc: 1705\n  verified_at: 2026-09-26T22:11:36Z\n")
CSB_NEW = ("- path: `tests/component/melder/spellbook/test_spellbook_component_spellbook.py`\n"
           f"  start_line: 1\n  end_line: 1713\n  loc: 1713\n  verified_at: {TS}\n")
SOURCES_OLD = "- `tests/component/melder/aether/conduit/test_conduit_component_purge.py`\n"
SOURCES_NEW = SOURCES_OLD + f"- `{A}`\n- `{B}`\n- `{D}`\n"
TC_HANDOFF_OLD = "## Context / Handoff Summary\n\n2026-10-15 managed spells (0.2.8241-0.2.8246): the lane's 28 test files join"
TC_HANDOFF_NEW = (
    "## Context / Handoff Summary\n\n"
    "2026-10-16 non-resolvable definitions (0.2.8247): a new DevOps Control Plane Unit Cluster carries the\n"
    "capability-flag and Book-flag unit tests (`test_spell_system_states_non_resolvable.py`,\n"
    "`test_risk_manager_non_resolvable.py`), the Aether Component Cluster gains\n"
    "`test_non_resolvable_validation_flag_component.py`, and the Unit Test Suite names the cluster. Of the five test\n"
    "files whose doubles follow the new `register_index` keyword, the two the map lists (`test_spellbook.py`,\n"
    "`test_spellbook_component_spellbook.py`) are remeasured; the registry stub in `test_risk_manager.py` answers the\n"
    "published set. The core set is 250 paths, equal to the code map; tier and subtree counts are recounted from disk\n"
    "(836 test modules in the three tiers; unit aether 204, component aether 77).\n"
    "\n"
    "2026-10-15 managed spells (0.2.8241-0.2.8246): the lane's 28 test files join"
)

TC_STEPS = [
    ("- Updated: 2026-10-15\n", "- Updated: 2026-10-16\n"),
    ("- The aether tree carries 202 `test_*.py` modules beneath these; they are the\n",
     "- The aether tree carries 204 `test_*.py` modules beneath these; they are the\n"),
    ("- No harness or support module of its own; the 76 test_*.py modules in\n  tests/component/melder/aether/",
     "- No harness or support module of its own; the 77 test_*.py modules in\n  tests/component/melder/aether/"),
    ("builders - not every `test_*.py` module beneath it. The 833 test modules of the\n",
     "builders - not every `test_*.py` module beneath it. The 836 test modules of the\n"),
    ("above - 247 paths (recounted 2026-10-15) - and nothing else.",
     "above - 250 paths (recounted 2026-10-16) - and nothing else."),
    (SUITE_OLD, SUITE_NEW),
    (CLUSTER_ANCHOR, CLUSTER_NEW),
    (COMP_PROTECTS_OLD, COMP_PROTECTS_NEW),
    (COMP_KEYS_OLD, COMP_KEYS_NEW),
    (UNIT_C1_OLD, UNIT_C1_NEW),
    (COMP_C1_OLD, COMP_C1_NEW),
    (SB_OLD, SB_NEW),
    (CSB_OLD, CSB_NEW),
    (SOURCES_OLD, SOURCES_NEW),
    (TC_HANDOFF_OLD, TC_HANDOFF_NEW),
]

TA_STEPS = [
    ("- Updated: 2026-10-15\n", "- Updated: 2026-10-16\n"),
    ("- `unit/`: 505 `.py` files, 502 of them `test_*.py` (465 on 2026-09-26, 334 on 2026-06-13)\n",
     "- `unit/`: 507 `.py` files, 504 of them `test_*.py` (465 on 2026-09-26, 334 on 2026-06-13)\n"),
    ("- `component/`: 167 `.py` files, 165 of them `test_*.py` (143, 81)\n",
     "- `component/`: 168 `.py` files, 166 of them `test_*.py` (143, 81)\n"),
    ("Recounted 2026-10-15 with `find tests/<tier> -name '*.py'` (pycache excluded); the three tiers' 833 `test_*.py`\n",
     "Recounted 2026-10-16 with `find tests/<tier> -name '*.py'` (pycache excluded); the three tiers' 836 `test_*.py`\n"),
    ("## Context / Handoff Summary\n\n2026-10-15 managed spells (no notch here; the lane landed 0.2.8241-0.2.8246):",
     "## Context / Handoff Summary\n\n"
     "2026-10-16 non-resolvable definitions (0.2.8247): the inventory is recounted from disk (unit 507 `.py`,\n"
     "component 168, integration 173, mocks 44, experimentation 204; 836 test modules in the three tiers) - the lane\n"
     "adds two unit modules and one component module, catalogued in `tests_components`. No tier, conftest, marker or\n"
     "shared support module changes, and no extent in this map moves.\n"
     "\n"
     "2026-10-15 managed spells (no notch here; the lane landed 0.2.8241-0.2.8246):"),
]

apply(TC, TC_STEPS, CHECK)
apply(TA, TA_STEPS, CHECK)
