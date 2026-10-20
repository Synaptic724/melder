"""Land S7's document edits in the four system documents (melder_1; STORY-2026-10-17-book_teardown_leaves_parked_
versions_uncleaned, 0.2.8260). Each old text must occur exactly once; every new line stays within 120 characters
(a lone unbreakable token excepted); files must be LF; every write is read back. {now} is the UTC time of the run.
Usage: land_s7_docs.py --root <tree> --check|--apply
"""
import datetime
import pathlib
import sys

ARCH = "context_compass/system_docs/src_architecture.md"
COMP = "context_compass/system_docs/src_components.md"
TCOMP = "context_compass/system_docs/tests_components.md"
TARCH = "context_compass/system_docs/tests_architecture.md"

ARCH_INVARIANT = (
    "## Operational Invariants\n",
    "## Operational Invariants\n"
    "- A Book's teardown retires its parked versions (2026-10-19, 0.2.8260;\n"
    "  STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned, on the owner's word, chat 2026-10-19: \"Go\n"
    "  ahead\"): `Spellbook._cleanup_spells`, after its loop over the active versions (unregister each index from\n"
    "  SpellSystemStates, clean the Spell, clean its index), walks `_inactive_spells`. For each parked version it reads\n"
    "  the version's index while the version is live and notes the index when no active member holds it, then retires\n"
    "  the version locally - `_spellbook_cleanup` set, then `Spell.cleanup()`, the teardown the parked branch of\n"
    "  `_dispose_spell` runs - and last it cleans every noted index, one `remove_from_spell_index` minted (a shared\n"
    "  index was cleaned with its active member). Every step is best-effort and logged, as in the active loop. A\n"
    "  parked version holds no lineage registration, resolution-map entry or frame lookup of its own, and the root's\n"
    "  teardown has already unregistered its index from the frame (0.2.8259; an unconjured Book registered none), so\n"
    "  nothing else is owed: the Book's record subtree leaves with the Book (`emit_spellbook_removed`) and the root's\n"
    "  store unregisters a parked managed version's pool with the rest. After the teardown every version the Book\n"
    "  owned reads cleaned and its own `cleanup()` returns; until 0.2.8260 a parked one stayed uncleaned, a minted\n"
    "  index with it, and its `cleanup()` routed to the torn-down Book and raised \"Spellbook has already been\n"
    "  cleaned.\". Locks: the loop runs under the Book lock and takes each spell's and index's lock under it, the\n"
    "  order the active loop and conjure's ownership stamping already take; no new edge, no user code.\n"
    "  EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook._cleanup_spells`, `Spellbook._cleanup_components`,\n"
    "  `Spellbook._dispose_spell`, `src/melder/aether/spellbook/spell.py:Spell.cleanup` and\n"
    "  `src/melder/aether/spellbook/bind/spell_index.py:SpellIndex.cleanup`.\n",
)
ARCH_FAILURE = (
    "## Failure Modes and Error Paths\n",
    "## Failure Modes and Error Paths\n"
    "- Fixed in 0.2.8260: a Book's teardown no longer leaves its parked versions behind. `Spellbook._cleanup_spells`\n"
    "  reached an index only through its active member, so after a root's teardown, or a direct `Spellbook.cleanup()`,\n"
    "  a version parked on a shared index, or alone in an index `remove_from_spell_index` minted, read `cleaned` False,\n"
    "  a minted index stayed uncleaned, and the version's own `cleanup()` raised RuntimeError \"Spellbook has already\n"
    "  been cleaned.\". Each now reads cleaned and its `cleanup()` returns.\n"
    "  EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook._cleanup_spells` and\n"
    "  `src/melder/aether/spellbook/spell.py:Spell.cleanup`.\n",
)
ARCH_SEQUENCE = (
    "2. `Spellbook.cleanup()` cleans spells and SpellIndex keys, then configuration\n"
    "   and validators, nulls references, logger last.\n",
    "2. `Spellbook.cleanup()` cleans spells and SpellIndex keys - its parked versions and the indexes only they\n"
    "   hold included (0.2.8260) - then configuration and validators, nulls references, logger last.\n",
)
ARCH_8256 = (
    "  the frame, where no call could notch, move, dispose or clean them. Not changed: the direct doors send\n"
    "  index-link borrowers no emission, and Book teardown leaves parked versions uncleaned\n"
    "  (STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned).\n",
    "  the frame, where no call could notch, move, dispose or clean them. Not changed: the direct doors send\n"
    "  index-link borrowers no emission. Book teardown retires the parked versions since 0.2.8260\n"
    "  (STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned).\n",
)
ARCH_MAP = (
    "- path: `src/melder/aether/spellbook/spellbook.py`\n"
    "  start_line: 1\n"
    "  end_line: 7858\n"
    "  loc: 7858\n"
    "  verified_at: 2026-10-19T00:01:11Z\n"
    "  note: Spellbook core and conjure pipeline;",
    "- path: `src/melder/aether/spellbook/spellbook.py`\n"
    "  start_line: 1\n"
    "  end_line: 7903\n"
    "  loc: 7903\n"
    "  verified_at: {now}\n"
    "  note: Spellbook core and conjure pipeline;",
)
ARCH_MAP_NOTE = (
    "    root's teardown unregisters the indexes that hold only parked versions (0.2.8259).\n"
    "- path: `src/melder/aether/spellbook/spellbook_creation_system.py`\n",
    "    root's teardown unregisters the indexes that hold only parked versions (0.2.8259). `_cleanup_spells` retires\n"
    "    the Book's parked versions and cleans the indexes only they hold (0.2.8260).\n"
    "- path: `src/melder/aether/spellbook/spellbook_creation_system.py`\n",
)
ARCH_HANDOFF = (
    "\n## Context / Handoff Summary\n\n",
    "\n## Context / Handoff Summary\n\n"
    "2026-10-19 a Book's teardown retires its parked versions (0.2.8260;\n"
    "STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned, on the owner's word \"Go ahead\"): after the\n"
    "active versions `_cleanup_spells` retires every parked version locally and cleans every index only parked\n"
    "versions hold, so no version of a dead Book reads live or refuses its own cleanup. The cleanup sequence, a new\n"
    "operational invariant, a fixed failure mode and the code map carry it, and the 0.2.8256 invariant no longer lists\n"
    "Book teardown as unchanged; the component map carries the per-component contract. Every numeric citation into\n"
    "spellbook.py past the edit moved 45 lines and was remapped line by line.\n\n",
)
ARCH_UPDATED = ("- Updated: 2026-10-18\n", "- Updated: 2026-10-19\n")

COMP_CLEANUP = (
    "- Cleanup is idempotent, unregisters local lineages from SpellSystemStates, and clears spells, configuration, "
    "validators, and logger. EVIDENCE: src/melder/aether/spellbook/spellbook.py:_cleanup_spells\n",
    "- Cleanup is idempotent, unregisters local lineages from SpellSystemStates, cleans its spells - the parked\n"
    "  versions and the indexes only they hold included since 0.2.8260 - and clears configuration, validators, and\n"
    "  logger. EVIDENCE: src/melder/aether/spellbook/spellbook.py:_cleanup_spells\n",
)
COMP_8256 = (
    "  not a caller's removal and never meets the check: `_cleanup_spells` cleans each active spell and its\n"
    "  index (its parked versions are STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned).\n",
    "  not a caller's removal and never meets the check: `_cleanup_spells` cleans each active spell and its\n"
    "  index, then retires the parked versions and the indexes only they hold (0.2.8260).\n",
)
COMP_INVARIANT = (
    "- An index keeps an active version while it holds parked ones (0.2.8256; the owner's choice of the refusal,\n",
    "- A Book's teardown retires its parked versions (0.2.8260;\n"
    "  STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned): after its loop over the active versions,\n"
    "  `_cleanup_spells` walks `_inactive_spells` - it reads each parked version's index while the version is live,\n"
    "  noting it when no active member holds it, retires the version locally (`_spellbook_cleanup` set, then\n"
    "  `Spell.cleanup()`, as the parked branch of `_dispose_spell` does), and last cleans every noted index, one\n"
    "  `remove_from_spell_index` minted (a shared index was cleaned with its active member). Each step is\n"
    "  best-effort and logged. A parked version holds no lineage registration, resolution-map entry or frame lookup\n"
    "  of its own, and the root's teardown already unregistered its index from the frame (0.2.8259; an unconjured\n"
    "  Book registered none). After the teardown every version the Book owned reads cleaned and its own `cleanup()`\n"
    "  returns; until 0.2.8260 a parked one stayed uncleaned and its `cleanup()` raised \"Spellbook has already been\n"
    "  cleaned.\". Locks: under the Book lock, each spell's and index's lock taken under it, the active loop's order;\n"
    "  no new lock-order edge.\n"
    "  EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook._cleanup_spells`, `Spellbook._cleanup_components`,\n"
    "  `Spellbook._dispose_spell` and `src/melder/aether/spellbook/spell.py:Spell.cleanup`.\n"
    "- An index keeps an active version while it holds parked ones (0.2.8256; the owner's choice of the refusal,\n",
)
COMP_MAP = (
    "- path: `src/melder/aether/spellbook/spellbook.py`\n"
    "  start_line: 1\n"
    "  end_line: 7858\n"
    "  loc: 7858\n"
    "  verified_at: 2026-10-19T00:01:11Z\n"
    "- path: `src/melder/aether/spellbook/spellbinder.py`\n",
    "- path: `src/melder/aether/spellbook/spellbook.py`\n"
    "  start_line: 1\n"
    "  end_line: 7903\n"
    "  loc: 7903\n"
    "  verified_at: {now}\n"
    "- path: `src/melder/aether/spellbook/spellbinder.py`\n",
)
COMP_HANDOFF = (
    "\n## Context / Handoff Summary\n\n",
    "\n## Context / Handoff Summary\n\n"
    "2026-10-19 a Book's teardown retires its parked versions (0.2.8260;\n"
    "STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned, on the owner's word \"Go ahead\"): Spellbook\n"
    "Core's cleanup line and a new invariant say `_cleanup_spells` retires every parked version locally after the\n"
    "active versions and cleans every index only parked versions hold; the 0.2.8256 invariant's teardown sentence says\n"
    "so too; the code map's spellbook.py extent is remeasured. Every numeric citation into spellbook.py past the edit\n"
    "moved 45 lines and was remapped line by line.\n\n",
)
COMP_UPDATED = ("- Updated: 2026-10-18\n", "- Updated: 2026-10-19\n")

TC_CATALOG = (
    "  index behind; and residency reads French parked in its own index, then active after a notch\n"
    "Key Files (C1):\n",
    "  index behind; and residency reads French parked in its own index, then active after a notch\n"
    "- a Book's teardown retires its parked versions (0.2.8260;\n"
    "  `test_book_teardown_retires_parked_versions_integration.py`, 8 tests): after the root's teardown a version\n"
    "  parked on a shared index, and one alone in an index `remove_from_spell_index` minted, read cleaned - the frame\n"
    "  kept or collapsed - with the minted index cleaned and the version's own `cleanup()` returning; a direct\n"
    "  `Spellbook.cleanup()` retires a version parked before conjure; the teardown unregisters the pools of an active\n"
    "  and a parked managed version and cleans the parked Spell; an active-only Book and a parked version disposed\n"
    "  first tear down as before\n"
    "Key Files (C1):\n",
)
TC_KEYFILE = (
    "- `tests/integration/melder/spellbook/test_separated_version_is_known_to_its_frame_integration.py` (2026-10-19)\n",
    "- `tests/integration/melder/spellbook/test_separated_version_is_known_to_its_frame_integration.py` (2026-10-19)\n"
    "- `tests/integration/melder/spellbook/test_book_teardown_retires_parked_versions_integration.py` (2026-10-19)\n",
)
TC_MAP = (
    "    against a second bind; the root's teardown takes its index; residency reads it parked (0.2.8259).\n",
    "    against a second bind; the root's teardown takes its index; residency reads it parked (0.2.8259).\n"
    "- path: `tests/integration/melder/spellbook/test_book_teardown_retires_parked_versions_integration.py`\n"
    "  start_line: 1\n"
    "  end_line: 330\n"
    "  loc: 330\n"
    "  verified_at: {now}\n"
    "  note: a Book's teardown retires its parked versions and the indexes only they hold, and a version's own\n"
    "    `cleanup()` returns afterwards; active-only and disposed-first controls (0.2.8260).\n",
)
TC_SOURCES = (
    "- `tests/integration/melder/spellbook/test_separated_version_is_known_to_its_frame_integration.py`\n"
    "- direct filesystem inventory of `tests/`\n",
    "- `tests/integration/melder/spellbook/test_separated_version_is_known_to_its_frame_integration.py`\n"
    "- `tests/integration/melder/spellbook/test_book_teardown_retires_parked_versions_integration.py`\n"
    "- direct filesystem inventory of `tests/`\n",
)
TC_COUNT_INTEG = (
    "- 176 `test_*.py` modules among 183 `.py` files (recounted 2026-10-19); the others are benches and the\n",
    "- 177 `test_*.py` modules among 184 `.py` files (recounted 2026-10-19); the others are benches and the\n",
)
TC_COUNT_SPELLBOOK = ("- No harness or support module of its own; the 53 test_*.py modules in\n",
                      "- No harness or support module of its own; the 54 test_*.py modules in\n")
TC_COUNT_CORE = ("above - 273 paths (recounted 2026-10-19) - and nothing else.",
                 "above - 274 paths (recounted 2026-10-19) - and nothing else.")
TC_COUNT_TREE = ("builders - not every `test_*.py` module beneath it. The 857 test modules of the\n",
                 "builders - not every `test_*.py` module beneath it. The 858 test modules of the\n")
TC_HANDOFF = (
    "\n## Context / Handoff Summary\n\n",
    "\n## Context / Handoff Summary\n\n"
    "2026-10-19 a Book's teardown retires its parked versions (0.2.8260;\n"
    "STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned): the Spellbook Integration Cluster gains\n"
    "`test_book_teardown_retires_parked_versions_integration.py` (8 tests: a parked version on a shared index and\n"
    "alone in a minted one, with the frame kept and collapsed; a version parked before conjure under a direct Book\n"
    "cleanup; an active and a parked managed version; two controls), a key file with a code-map record. Counts are\n"
    "recounted from disk (integration 177 of 184, spellbook tree 54; 858 test modules in the three tiers); the core\n"
    "key-file union is 274 paths.\n\n",
)
TC_UPDATED = ("- Updated: 2026-10-18T23:13:06Z\n", "- Updated: {now}\n")

TA_COUNT = ("- `integration/`: 183 `.py` files, 176 of them `test_*.py` (149, 88)\n",
            "- `integration/`: 184 `.py` files, 177 of them `test_*.py` (149, 88)\n")
TA_RECOUNT = (
    "Recounted 2026-10-18 with `find tests/<tier> -name '*.py'` (pycache excluded); the three tiers' 857 `test_*.py`\n",
    "Recounted 2026-10-19 with `find tests/<tier> -name '*.py'` (pycache excluded); the three tiers' 858 `test_*.py`\n",
)
TA_HANDOFF = (
    "\n## Context / Handoff Summary\n\n",
    "\n## Context / Handoff Summary\n\n"
    "2026-10-19 a Book's teardown retires its parked versions (0.2.8260): the inventory is recounted from disk\n"
    "(integration 184 `.py`, 177 of them `test_*.py`; 858 test modules in the three tiers) - the lane adds one\n"
    "integration module (a Book's teardown retiring its parked versions), catalogued in `tests_components`. No tier,\n"
    "conftest, declared marker or shared support module changes, and no extent in this map moves.\n\n",
)
TA_UPDATED = ("- Updated: 2026-10-18\n", "- Updated: 2026-10-19\n")

EDITS = {
    ARCH: [ARCH_UPDATED, ARCH_SEQUENCE, ARCH_INVARIANT, ARCH_8256, ARCH_FAILURE, ARCH_MAP, ARCH_MAP_NOTE, ARCH_HANDOFF],
    COMP: [COMP_UPDATED, COMP_CLEANUP, COMP_INVARIANT, COMP_8256, COMP_MAP, COMP_HANDOFF],
    TCOMP: [TC_UPDATED, TC_COUNT_INTEG, TC_COUNT_SPELLBOOK, TC_CATALOG, TC_KEYFILE, TC_COUNT_CORE, TC_COUNT_TREE,
            TC_MAP, TC_SOURCES, TC_HANDOFF],
    TARCH: [TA_UPDATED, TA_COUNT, TA_RECOUNT, TA_HANDOFF],
}


def check_lines(old: str, new: str, label: str) -> None:
    """Refuse a new line over 120 characters that the edit adds (lines the old text already had are kept)."""
    kept = set(old.split("\n"))
    for line in new.split("\n"):
        if line in kept:
            continue
        stripped = line.strip()
        if stripped.startswith("- ") and " " not in stripped[2:]:
            continue
        if len(line) > 120:
            raise SystemExit("%s: new line over 120 chars (%d): %s" % (label, len(line), line))


def main() -> None:
    """Apply every edit in memory, report, and write only with --apply."""
    args = sys.argv[1:]
    if len(args) != 3 or args[0] != "--root" or args[2] not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    root = pathlib.Path(args[1])
    now = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    results = {}
    for rel, edits in EDITS.items():
        path = root / rel
        raw = path.read_bytes()
        if b"\r\n" in raw:
            raise SystemExit("CRLF in %s" % rel)
        text = raw.decode("utf-8")
        before = text.count("\n")
        for number, (old, new) in enumerate(edits, 1):
            new = new.replace("{now}", now)
            check_lines(old, new, "%s edit %d" % (path.name, number))
            if text.count(old) != 1:
                raise SystemExit("%s edit %d: old text found %d times" % (path.name, number, text.count(old)))
            text = text.replace(old, new)
        results[rel] = text
        print("%s: %d edits, %d -> %d lines" % (path.name, len(edits), before, text.count("\n")))
    if args[2] == "--apply":
        for rel, text in results.items():
            path = root / rel
            path.write_bytes(text.encode("utf-8"))
            if path.read_bytes().decode("utf-8") != text:
                raise SystemExit("read-back mismatch: %s" % rel)
        print("applied", now)


main()
