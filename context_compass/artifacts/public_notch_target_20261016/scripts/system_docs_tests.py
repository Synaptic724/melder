"""Catalogue the public notch target's tests in tests_components and recount tests_architecture (0.2.8249).

Run from the context_compass root:  python <this file> <NOW>
Exact, asserted replacements on LF files; prints new lines over 120 characters that are not unbreakable paths.
The counts were recounted from disk with `find tests/<tier> -name '*.py'` (pycache excluded) just before this ran.
"""
import pathlib
import sys

NOW = sys.argv[1]
UNIT_FILE = "tests/unit/melder/aether/conduit/test_conduit_notch_target.py"
INTEGRATION_FILE = "tests/integration/melder/aether/conduit/test_notch_spell_by_id_integration.py"

TESTS_COMPONENTS = [
    (  # Unit Test Suite: protection
        "  `### Subcomponent: Spellbook Runtime And Binding Unit Cluster`)\n"
        "\n"
        "Inputs:\n"
        "- local runtime classes and helper fixtures; `MagicMock` collaborators where the\n",
        "  `### Subcomponent: Spellbook Runtime And Binding Unit Cluster`)\n"
        "- the public notch target (0.2.8249): `notch_spell` resolving a version id through the Book, passing an owned\n"
        "  `spell` through, and refusing every malformed or foreign target with nothing started, the in-window re-check\n"
        "  included (see `### Subcomponent: Spellbook Runtime And Binding Unit Cluster`)\n"
        "\n"
        "Inputs:\n"
        "- local runtime classes and helper fixtures; `MagicMock` collaborators where the\n",
    ),
    (
        "- the densest tier: 505 `test_*.py` modules among 508 `.py` files (recounted 2026-10-16)\n",
        "- the densest tier: 506 `test_*.py` modules among 509 `.py` files (recounted 2026-10-16)\n",
    ),
    (
        "- The aether tree carries 204 `test_*.py` modules beneath these; they are the\n",
        "- The aether tree carries 205 `test_*.py` modules beneath these; they are the\n",
    ),
    (  # Integration Runtime Suite: protection
        "  notch as one staged after it (see `### Subcomponent: Spellbook Integration Cluster`)\n"
        "\n"
        "Inputs:\n"
        "- real runtime objects\n",
        "  notch as one staged after it (see `### Subcomponent: Spellbook Integration Cluster`)\n"
        "- the public notch target (0.2.8249): the stage -> notch -> meld loop and its revert by version id in real worlds,\n"
        "  and every foreign target refused with both indexes intact (see `### Subcomponent: Spellbook Integration Cluster`)\n"
        "\n"
        "Inputs:\n"
        "- real runtime objects\n",
    ),
    (
        "- 167 `test_*.py` modules among 174 `.py` files (recounted 2026-10-16); the others are benches and the\n",
        "- 168 `test_*.py` modules among 175 `.py` files (recounted 2026-10-16); the others are benches and the\n",
    ),
    (
        "- The aether tree carries 44 `test_*.py` modules beneath these; they are the\n",
        "- The aether tree carries 45 `test_*.py` modules beneath these; they are the\n",
    ),
    (  # Spellbook Runtime And Binding Unit Cluster: protection
        "  logged with its id and the method tag while every other version is wired; a Book with nothing parked is wired\n"
        "  as before\n"
        "Key Files (C1):\n",
        "  logged with its id and the method tag while every other version is wired; a Book with nothing parked is wired\n"
        "  as before\n"
        "- the public notch target (0.2.8249; `test_conduit_notch_target.py`, 16 tests over the conduit conftest's stub\n"
        "  Book): by id the Book's `_get_owned_spell` is asked and the resolved version reaches the transaction metadata,\n"
        "  `_notch_spell` and the fan-out; an owned `spell` passes through; `change_reason` is passed on; the active version\n"
        "  by id does not fan out; both or neither target, a non-str id, a str given as `spell`, an unknown id, another\n"
        "  index's version by id and by object, a Spell the Book does not own and a stale Spell are refused with no\n"
        "  transaction started and the seam not called; a target moved after the first check is refused inside the window\n"
        "  with the transaction ended as failed; an automatic conduit still raises the dynamic-mode RuntimeError before the\n"
        "  Book is asked\n"
        "Key Files (C1):\n",
    ),
    (
        "- `tests/unit/melder/spellbook/test_spellbook_creation_system_parked_versions.py` (parked versions, 2026-10-16)\n",
        "- `tests/unit/melder/spellbook/test_spellbook_creation_system_parked_versions.py` (parked versions, 2026-10-16)\n"
        f"- `{UNIT_FILE}` (public notch target, 2026-10-16)\n",
    ),
    (  # Spellbook Integration Cluster: protection
        "  (`test_cache_schema_version_integration.py`: generation 21 is admitted, 1-20 load cold)\n"
        "Key Files (C1):\n",
        "  (`test_cache_schema_version_integration.py`: generation 21 is admitted, 1-20 load cold)\n"
        "- the public notch target (0.2.8249; `test_notch_spell_by_id_integration.py`, 10 tests): in a dynamic world a\n"
        "  notch by the id `bind_inactive` returned promotes a version staged after conjure and one staged before it, the\n"
        "  next meld builds it and the call returns it; a notch back by id restores the first version with both members\n"
        "  kept; the active id is a no-op; a parked version of another index (by id and by object), another index's active\n"
        "  version, another Book's version and an unknown id are refused with ValueError while both indexes keep their\n"
        "  selection, members and melds; an index-linked borrower melds the version notched in by id\n"
        "Key Files (C1):\n",
    ),
    (
        "- `tests/integration/melder/spellbook/test_spellbook_integration_parked_before_conjure.py` (2026-10-16)\n",
        "- `tests/integration/melder/spellbook/test_spellbook_integration_parked_before_conjure.py` (2026-10-16)\n"
        f"- `{INTEGRATION_FILE}` (2026-10-16)\n",
    ),
    (  # C1 Code Map: the unit file after the parked-versions record
        "  verified_at: 2026-10-16T11:13:43Z\n"
        "  note: conjure's owner stamp of the versions parked before it (0.2.8248).\n",
        "  verified_at: 2026-10-16T11:13:43Z\n"
        "  note: conjure's owner stamp of the versions parked before it (0.2.8248).\n"
        f"- path: `{UNIT_FILE}`\n"
        "  start_line: 1\n"
        "  end_line: 252\n"
        "  loc: 252\n"
        f"  verified_at: {NOW}\n"
        "  note: the notch target named by id or Spell, resolved and checked before and inside the transaction (0.2.8249).\n",
    ),
    (  # C1 Code Map: the integration file after the parked-before-conjure record
        "  verified_at: 2026-10-16T11:13:43Z\n"
        "  note: versions staged before or after conjure meld after a notch, every family (0.2.8248).\n",
        "  verified_at: 2026-10-16T11:13:43Z\n"
        "  note: versions staged before or after conjure meld after a notch, every family (0.2.8248).\n"
        f"- path: `{INTEGRATION_FILE}`\n"
        "  start_line: 1\n"
        "  end_line: 271\n"
        "  loc: 271\n"
        f"  verified_at: {NOW}\n"
        "  note: the stage -> notch -> meld loop by id, its revert, and foreign targets refused intact (0.2.8249).\n",
    ),
    (  # Information Sources
        "- `tests/integration/melder/spellbook/test_cache_schema_version_integration.py`\n"
        "- direct filesystem inventory of `tests/`\n",
        "- `tests/integration/melder/spellbook/test_cache_schema_version_integration.py`\n"
        f"- `{UNIT_FILE}`\n"
        f"- `{INTEGRATION_FILE}`\n"
        "- direct filesystem inventory of `tests/`\n",
    ),
    (  # Context / Handoff Summary
        "## Context / Handoff Summary\n"
        "\n"
        "2026-10-16 parked versions wired at conjure (0.2.8248): the Spellbook Runtime And Binding Unit Cluster gains\n",
        "## Context / Handoff Summary\n"
        "\n"
        "2026-10-16 public notch target (0.2.8249): the Spellbook Runtime And Binding Unit Cluster gains\n"
        "`test_conduit_notch_target.py` (16 tests: the id resolved and passed on, every refusal with nothing started, the\n"
        "in-window re-check) and the Spellbook Integration Cluster `test_notch_spell_by_id_integration.py` (10 tests: the\n"
        "loop and its revert by id, the no-op, the foreign targets refused with both indexes intact, an index-linked\n"
        "borrower following), each a key file with a code-map record; the Unit Test Suite and the Integration Runtime Suite\n"
        "name the protection, and their module counts are recounted from disk (unit 506 of 509 `.py`, aether tree 205;\n"
        "integration 168 of 175, aether tree 45; 840 test modules in the three tiers).\n"
        "\n"
        "2026-10-16 parked versions wired at conjure (0.2.8248): the Spellbook Runtime And Binding Unit Cluster gains\n",
    ),
]

TESTS_ARCHITECTURE = [
    (
        "- `unit/`: 508 `.py` files, 505 of them `test_*.py` (465 on 2026-09-26, 334 on 2026-06-13)\n",
        "- `unit/`: 509 `.py` files, 506 of them `test_*.py` (465 on 2026-09-26, 334 on 2026-06-13)\n",
    ),
    (
        "- `integration/`: 174 `.py` files, 167 of them `test_*.py` (149, 88)\n",
        "- `integration/`: 175 `.py` files, 168 of them `test_*.py` (149, 88)\n",
    ),
    (
        "Recounted 2026-10-16 with `find tests/<tier> -name '*.py'` (pycache excluded); the three tiers' 838 `test_*.py`\n",
        "Recounted 2026-10-16 with `find tests/<tier> -name '*.py'` (pycache excluded); the three tiers' 840 `test_*.py`\n",
    ),
    (
        "## Context / Handoff Summary\n"
        "\n"
        "2026-10-16 parked versions wired at conjure (0.2.8248): the inventory is recounted from disk (unit 508 `.py`,\n",
        "## Context / Handoff Summary\n"
        "\n"
        "2026-10-16 public notch target (0.2.8249): the inventory is recounted from disk (unit 509 `.py`, component 168,\n"
        "integration 175, mocks 44, experimentation 204; 840 test modules in the three tiers) - the lane adds one unit and\n"
        "one integration module, catalogued in `tests_components`. No tier, conftest, marker or shared support module\n"
        "changes, and no extent in this map moves.\n"
        "\n"
        "2026-10-16 parked versions wired at conjure (0.2.8248): the inventory is recounted from disk (unit 508 `.py`,\n",
    ),
]


def apply(path: pathlib.Path, edits: list) -> None:
    """Apply every edit once, in order, to one LF document and report over-long new lines."""
    text = path.read_bytes().decode("utf-8")
    if "\r\n" in text:
        raise SystemExit(f"{path}: expected LF")
    for old, new in edits:
        found = text.count(old)
        if found != 1:
            raise SystemExit(f"{path}: {found} occurrences of {old[:90]!r}")
        text = text.replace(old, new, 1)
    path.write_bytes(text.encode("utf-8"))
    for _old, new in edits:
        for line in new.splitlines():
            if len(line) > 120 and "tests/" not in line:
                print("LONG", path.name, len(line), line[:70])
    print(f"{path}: {len(edits)} edits; {text.count(chr(10))} lines")


if __name__ == "__main__":
    apply(pathlib.Path("system_docs/tests_components.md"), TESTS_COMPONENTS)
    apply(pathlib.Path("system_docs/tests_architecture.md"), TESTS_ARCHITECTURE)
