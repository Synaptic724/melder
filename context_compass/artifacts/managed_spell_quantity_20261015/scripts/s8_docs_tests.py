"""S8: the tests docs for parked_versions_wired_at_conjure_2026_10_16 (exact replacements, LF).

Run from the repository root: python s8_docs_tests.py <NOW>
tests_components: the two new test files (Protects, key files, code-map records, sources), the remeasured records,
the suites' module counts and the core-set count; tests_architecture: the inventory recount. Every old text must
occur exactly once; nothing is written unless all of them do.
"""
import pathlib
import sys

NOW = sys.argv[1]
TC = pathlib.Path("context_compass/system_docs/tests_components.md")
TA = pathlib.Path("context_compass/system_docs/tests_architecture.md")
UNIT = "tests/unit/melder/spellbook/test_spellbook_creation_system_parked_versions.py"
INTEG = "tests/integration/melder/spellbook/test_spellbook_integration_parked_before_conjure.py"

TC_EDITS = [
    # Unit Test Suite.
    ("  flagged lineages and RiskManager's Book flag that leaves them out (see\n"
     "  `### Subcomponent: DevOps Control Plane Unit Cluster`)\n\nInputs:\n",
     "  flagged lineages and RiskManager's Book flag that leaves them out (see\n"
     "  `### Subcomponent: DevOps Control Plane Unit Cluster`)\n"
     "- conjure's wiring of the versions parked before it (0.2.8248): each parked version gets the active loop's owner\n"
     "  stamp and nothing else, under the Book lock, a raising stamp logged (see\n"
     "  `### Subcomponent: Spellbook Runtime And Binding Unit Cluster`)\n\nInputs:\n"),
    ("- the densest tier: 502 `test_*.py` modules among 505 `.py` files (recounted 2026-10-15)\n",
     "- the densest tier: 505 `test_*.py` modules among 508 `.py` files (recounted 2026-10-16)\n"),
    ("- 165 `test_*.py` modules among 167 `.py` files (recounted 2026-10-15)\n",
     "- 166 `test_*.py` modules among 168 `.py` files (recounted 2026-10-16)\n"),
    ("- 166 `test_*.py` modules among 173 `.py` files (recounted 2026-10-15); the others",
     "- 167 `test_*.py` modules among 174 `.py` files (recounted 2026-10-16); the others"),
    # Integration Runtime Suite.
    ("  binding names, notches, borrowers and lessers, the release registry, ownership transfers and a restored world\n"
     "  (see `### Subcomponent: Conduit Integration Cluster`)\n",
     "  binding names, notches, borrowers and lessers, the release registry, ownership transfers and a restored world\n"
     "  (see `### Subcomponent: Conduit Integration Cluster`)\n"
     "- versions staged before conjure (0.2.8248): every family staged with `bind_inactive` before conjure melds after a\n"
     "  notch as one staged after it (see `### Subcomponent: Spellbook Integration Cluster`)\n"),
    # Spellbook Runtime And Binding Unit Cluster.
    ("  the FORWARDREF format (`test_scan_bind_option_parity.py`)\nKey Files (C1):\n",
     "  the FORWARDREF format (`test_scan_bind_option_parity.py`)\n"
     "- the versions parked before conjure (0.2.8248; `test_spellbook_creation_system_parked_versions.py`):\n"
     "  `define_conduit_into_spells` stamps each parked version once with the active loop's arguments (the root's id,\n"
     "  name and store, its dynamic flag and gate controller, the caching posture; three postures), under the Book lock\n"
     "  (a prober thread is kept out of it during every stamp); a parked existing object is stamped but not registered\n"
     "  while an active one is; a parked version's resolution flag is left as it was; one raising parked stamp is\n"
     "  logged with its id and the method tag while every other version is wired; a Book with nothing parked is wired\n"
     "  as before\n"
     "Key Files (C1):\n"),
    ("- `tests/unit/melder/spellbook/bind/test_spell_index_selected_probe.py` (2026-10-15)\n",
     "- `tests/unit/melder/spellbook/bind/test_spell_index_selected_probe.py` (2026-10-15)\n"
     "- `" + UNIT + "` (parked versions, 2026-10-16)\n"),
    # Spellbook Integration Cluster.
    ("  and `bind_inactive` forward the options; SpellBinder ends in the same Spell\nKey Files (C1):\n",
     "  and `bind_inactive` forward the options; SpellBinder ends in the same Spell\n"
     "- versions staged before conjure (0.2.8248; `test_spellbook_integration_parked_before_conjure.py`): in a dynamic\n"
     "  world a version staged with `bind_inactive` before conjure melds after a notch exactly as one staged after it,\n"
     "  for unique, unique_per_conduit, many, managed_spell_quantity, an existing object and a function; before its\n"
     "  notch neither is meldable by id (KeyError); a staged existing object is not registered in the store; a managed\n"
     "  version staged before conjure has its pool (count 0) and its registry entry from conjure on and leases from it\n"
     "  after the notch, `with` giving the object back. The creation cache's generation history ends at 21\n"
     "  (`test_cache_schema_version_integration.py`: generation 21 is admitted, 1-20 load cold)\n"
     "Key Files (C1):\n"),
    ("- `tests/integration/melder/spellbook/test_managed_bind_options_integration.py` (2026-10-15)\n",
     "- `tests/integration/melder/spellbook/test_managed_bind_options_integration.py` (2026-10-15)\n"
     "- `" + INTEG + "` (2026-10-16)\n"),
    # Code map: new records.
    ("- path: `tests/unit/melder/spellbook/test_spellbook_creation_system_dependency_flags.py`\n"
     "  start_line: 1\n  end_line: 283\n  loc: 283\n  verified_at: 2026-09-30T20:10:45Z\n",
     "- path: `tests/unit/melder/spellbook/test_spellbook_creation_system_dependency_flags.py`\n"
     "  start_line: 1\n  end_line: 283\n  loc: 283\n  verified_at: 2026-09-30T20:10:45Z\n"
     "- path: `" + UNIT + "`\n  start_line: 1\n  end_line: 366\n  loc: 366\n  verified_at: " + NOW + "\n"
     "  note: conjure's owner stamp of the versions parked before it (0.2.8248).\n"),
    ("  note: managed bind options through a real Spellbook and its root (0.2.8242).\n",
     "  note: managed bind options through a real Spellbook and its root (0.2.8242).\n"
     "- path: `" + INTEG + "`\n  start_line: 1\n  end_line: 250\n  loc: 250\n  verified_at: " + NOW + "\n"
     "  note: versions staged before or after conjure meld after a notch, every family (0.2.8248).\n"),
    # Code map: remeasured records.
    ("  end_line: 483\n  loc: 483\n  verified_at: 2026-10-15T22:33:31Z\n"
     "  note: the owner stamp through a transfer's flip, migration and rollback (0.2.8246).\n",
     "  end_line: 484\n  loc: 484\n  verified_at: " + NOW + "\n"
     "  note: the owner stamp through a transfer's flip, migration and rollback (0.2.8246).\n"),
    ("  end_line: 880\n  loc: 880\n  verified_at: 2026-10-15T22:33:31Z\n"
     "  note: the plans' managed site: lease, miss, returns, recorded children, overrides (0.2.8245).\n",
     "  end_line: 883\n  loc: 883\n  verified_at: " + NOW + "\n"
     "  note: the plans' managed site: lease, miss, returns, recorded children, overrides (0.2.8245); the missing-pool\n"
     "    text (0.2.8248).\n"),
    ("  end_line: 174\n  loc: 174\n  verified_at: 2026-10-15T22:33:31Z\n"
     "  note: the meld doors' purge, existing-object and live-probe answers for a managed spell (0.2.8243).\n",
     "  end_line: 174\n  loc: 174\n  verified_at: " + NOW + "\n"
     "  note: the meld doors' purge, existing-object and live-probe answers for a managed spell (0.2.8243).\n"),
    # Core set and module count.
    ("above - 250 paths (recounted 2026-10-16) - and nothing else.",
     "above - 252 paths (recounted 2026-10-16) - and nothing else."),
    ("builders - not every `test_*.py` module beneath it. The 836 test modules of the\n",
     "builders - not every `test_*.py` module beneath it. The 838 test modules of the\n"),
    # Information Sources.
    ("- `tests/unit/melder/test_package_public_surface.py`\n- direct filesystem inventory of `tests/`\n",
     "- `tests/unit/melder/test_package_public_surface.py`\n"
     "- `" + UNIT + "`\n- `" + INTEG + "`\n"
     "- `tests/integration/melder/spellbook/test_cache_schema_version_integration.py`\n"
     "- direct filesystem inventory of `tests/`\n"),
    # Handoff, newest first.
    ("## Context / Handoff Summary\n\n2026-10-16 non-resolvable definitions (0.2.8247):",
     "## Context / Handoff Summary\n\n"
     "2026-10-16 parked versions wired at conjure (0.2.8248): the Spellbook Runtime And Binding Unit Cluster gains\n"
     "`test_spellbook_creation_system_parked_versions.py` (the parked stamp, 9 tests) and the Spellbook Integration\n"
     "Cluster `test_spellbook_integration_parked_before_conjure.py` (every family staged before or after conjure, 27\n"
     "tests), each a key file with a code-map record; the cache-schema test expects generation 21; the records of the\n"
     "managed lowering, meld-door and transfer-stamp files are remeasured (their assertions and docstrings follow the\n"
     "new missing-pool text and the conjure stamp). The three suites' module counts, left at 2026-10-15 by the entry\n"
     "below, are recounted from disk (unit 505 of 508 `.py`, component 166 of 168, integration 167 of 174; 838 test\n"
     "modules), and the core set is 252 paths, equal to the code map.\n\n"
     "2026-10-16 non-resolvable definitions (0.2.8247):"),
]

TA_EDITS = [
    ("- `unit/`: 507 `.py` files, 504 of them `test_*.py`",
     "- `unit/`: 508 `.py` files, 505 of them `test_*.py`"),
    ("- `integration/`: 173 `.py` files, 166 of them `test_*.py`",
     "- `integration/`: 174 `.py` files, 167 of them `test_*.py`"),
    ("the three tiers' 836 `test_*.py`\n", "the three tiers' 838 `test_*.py`\n"),
    ("## Context / Handoff Summary\n\n2026-10-16 non-resolvable definitions (0.2.8247):",
     "## Context / Handoff Summary\n\n"
     "2026-10-16 parked versions wired at conjure (0.2.8248): the inventory is recounted from disk (unit 508 `.py`,\n"
     "component 168, integration 174, mocks 44, experimentation 204; 838 test modules in the three tiers) - the lane\n"
     "adds one unit and one integration module, catalogued in `tests_components`. No tier, conftest, marker or shared\n"
     "support module changes, and no extent in this map moves.\n\n"
     "2026-10-16 non-resolvable definitions (0.2.8247):"),
]


def apply(path: pathlib.Path, edits: list) -> str:
    """Apply every edit to one document in memory, refusing a missing or repeated old text."""
    text = path.read_bytes().decode("utf-8")
    assert "\r\n" not in text, path
    for old, new in edits:
        count = text.count(old)
        if count != 1:
            raise SystemExit(f"{path.name}: expected one occurrence, found {count}: {old[:90]!r}")
        text = text.replace(old, new)
    return text


def main() -> None:
    """Write both documents only when every edit of both applies."""
    tc = apply(TC, TC_EDITS)
    ta = apply(TA, TA_EDITS)
    TC.write_bytes(tc.encode("utf-8"))
    TA.write_bytes(ta.encode("utf-8"))
    for name, text in (("tests_components", tc), ("tests_architecture", ta)):
        long_lines = [n for n, line in enumerate(text.split("\n"), 1) if len(line) > 120 and "`" not in line]
        print(name, "lines", len(text.split("\n")) - 1, "long non-code lines", long_lines[:10])


if __name__ == "__main__":
    main()
