"""S9 landing (0.2.8256): system-document edits for the direct cleanup refusal.

src_components, src_architecture, tests_components and tests_architecture: each replacement's old text must occur
exactly once; new lines stay within 120 characters unless a long backticked path makes them unbreakable; LF only.
Usage (repository root): land_s9_docs.py --check | --apply
"""
import datetime
import pathlib
import re
import sys

DOCS = pathlib.Path("context_compass/system_docs")
STAMP = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
TEST_FILE = "test_direct_cleanup_refuses_active_member_with_parked_versions_integration.py"
TEST_PATH = "tests/integration/melder/spellbook/" + TEST_FILE
STORY = "STORY-2026-10-17-direct_cleanup_of_active_member_orphans_parked_versions"
S7 = "STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned"
S8 = "STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers"

SRC_COMPONENTS = [
    (
        "  locked section is not ordered against the rest of the removal.\n\nInvariants/Guarantees:\n",
        "  locked section is not ordered against the rest of the removal.\n"
        "- `cleanup_and_remove_spell` refuses the active member of an index that still holds parked versions\n"
        "  (0.2.8256): in its first `_lock` section, after it resolves the spell and before `unregister_index`, it\n"
        "  reads `SpellIndex.is_sole_member` under the index lock - Spellbook -> index, the order `_dispose_spell`\n"
        "  takes - and raises with nothing changed, so no lock or lock-order edge is added. Book teardown and the\n"
        "  parked disposal set `_spellbook_cleanup` before they clean a spell and never reach the method;\n"
        "  `_dispose_spell` reaches it only for a sole member. `cleanup_spell` decides and removes in two `_lock`\n"
        "  sections with no transaction, so a version staged onto the index between them now meets this refusal -\n"
        "  raised after the spell was invalidated (creation context cleared, resolution required again, lineage\n"
        "  gated), with nothing removed - where the removal used to clean the index under it. A staging or index move\n"
        "  that starts after the first locked section is still not ordered against the rest of the removal (callers\n"
        "  quiesce moves before a direct removal, as before Book teardown).\n"
        "\nInvariants/Guarantees:\n",
    ),
    (
        "- Existing-object spells are registered into Creations on conjure/bind.\n- A conjure refused by",
        "- Existing-object spells are registered into Creations on conjure/bind.\n"
        "- An index keeps an active version while it holds parked ones (0.2.8256; the owner's choice of the refusal,\n"
        "  2026-10-18): `cleanup_spell`, `cleanup_and_remove_spell` and a direct `Spell.cleanup()` refuse its active\n"
        "  member with nothing changed, each message naming the remedies - notch the index to a parked version,\n"
        "  dispose the parked versions with `cleanup_spell`, or move them out with `remove_from_spell_index`, which\n"
        "  mints an index for each - and the sole member of an index is removed with its index. No caller's removal\n"
        "  leaves a parked version on a cleaned index, and Melder picks no version for the agent. Book teardown is\n"
        "  not a caller's removal and never meets the check: `_cleanup_spells` cleans each active spell and its\n"
        "  index (its parked versions are " + S7 + ").\n"
        "  EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook.cleanup_and_remove_spell`,\n"
        "  `Spellbook._dispose_spell`, `Spellbook._cleanup_spells` and\n"
        "  `src/melder/aether/spellbook/spell.py:Spell.cleanup`.\n"
        "- A conjure refused by",
    ),
    (
        "  raised AttributeError), besides the \"not owned by this spellbook\" and multi-member refusals.\n",
        "  raised AttributeError), besides the \"not owned by this spellbook\" and multi-member refusals.\n"
        "- RuntimeError \"cleanup_spell: spell <id> is the active member of a multi-member index, and disposing it\n"
        "  would leave the index's parked versions without an active one. Notch the index to one of them, dispose\n"
        "  them with cleanup_spell, or move them out with remove_from_spell_index first.\" (0.2.8256; it ended \"...;\n"
        "  notch away from it before disposing it.\"), and RuntimeError \"Spellbook cannot remove spell <id>: it is\n"
        "  the active member of a multi-member index, ...\" with the same remedies from `cleanup_and_remove_spell`\n"
        "  and a direct `Spell.cleanup()` (0.2.8256, Breaking): both used to remove the version and clean the index\n"
        "  under its parked versions, which stayed in the Book uncleaned where no later call could notch, move,\n"
        "  dispose or clean them. Either refusal changes nothing.\n",
    ),
    (
        "  back. Cost: about 1 us on a ~18 us direct cleanup; bind, Book teardown and meld unchanged (measured).\n",
        "  back. Cost: about 1 us on a ~18 us direct cleanup; bind, Book teardown and meld unchanged (measured).\n"
        "- The Book refuses that removal for the active version of an index that also holds parked versions\n"
        "  (0.2.8256): `cleanup_and_remove_spell` checks `SpellIndex.is_sole_member` in its first `_lock` section,\n"
        "  before anything is unregistered, so the direct call raises with nothing changed; `Spell.cleanup` takes\n"
        "  no new lock (Spellbook Core).\n",
    ),
    (
        "  races the call (0.2.8230; that race raised AttributeError).\n\nObservability:\n- EXCEPTIONS ONLY",
        "  races the call (0.2.8230; that race raised AttributeError).\n"
        "- RuntimeError from a direct `Spell.cleanup()`, raised by `Spellbook.cleanup_and_remove_spell`: the spell is\n"
        "  not its Book's active version (a parked version, for one); it is the active version of an index that also\n"
        "  holds parked versions (0.2.8256; nothing changes, and the message names the remedies); or the Book has\n"
        "  been cleaned and did not clean this spell.\n"
        "\nObservability:\n- EXCEPTIONS ONLY",
    ),
    (
        "  another call.\"; 0.2.8232), not owned by this conduit's Book, or the active member of a multi-member index.\n",
        "  another call.\"; 0.2.8232), not owned by this conduit's Book, or the active member of a multi-member\n"
        "  index - a refusal whose message names the remedies since 0.2.8256 (notch the index to a parked version,\n"
        "  dispose the parked versions, or move them out with `remove_from_spell_index`).\n",
    ),
    (
        "- path: `src/melder/aether/spellbook/spellbook.py`\n  start_line: 1\n  end_line: 7771\n  loc: 7771\n"
        "  verified_at: 2026-10-17T23:12:45Z\n",
        "- path: `src/melder/aether/spellbook/spellbook.py`\n  start_line: 1\n  end_line: 7802\n  loc: 7802\n"
        "  verified_at: " + STAMP + "\n",
    ),
    (
        "- path: `src/melder/aether/spellbook/spell.py`\n  start_line: 1\n  end_line: 1968\n  loc: 1968\n"
        "  verified_at: 2026-10-17T23:12:45Z\n",
        "- path: `src/melder/aether/spellbook/spell.py`\n  start_line: 1\n  end_line: 1972\n  loc: 1972\n"
        "  verified_at: " + STAMP + "\n",
    ),
    (
        "## Context / Handoff Summary\n\n2026-10-18 managed settings leave the spell_id (0.2.8254; part A of\n",
        "## Context / Handoff Summary\n\n"
        "2026-10-18 direct cleanup refusal (0.2.8256; " + STORY + ",\n"
        "on the owner's choice of the refusal): Spellbook Core carries the refusal in `cleanup_and_remove_spell` - its\n"
        "check, its lock order and the race it now refuses inside `cleanup_spell` - the invariant that an index keeps\n"
        "an active version while it holds parked ones, and the reworded and new messages; the Binding Pipeline carries\n"
        "the direct `Spell.cleanup()` route's refusal and its failure entry; Conduit Runtime's `cleanup_spell` entry\n"
        "names the remedies; the code map remeasures spellbook.py and spell.py. The numeric citations into\n"
        "spellbook.py past the check moved 27 lines (31 past `cleanup_spell`'s docstring) and were remapped line by\n"
        "line (14 lines).\n\n"
        "2026-10-18 managed settings leave the spell_id (0.2.8254; part A of\n",
    ),
]

SRC_ARCHITECTURE = [
    (
        "## Operational Invariants\n- A managed spell's settings are not part of its spell_id (2026-10-18, 0.2.8254;",
        "## Operational Invariants\n"
        "- An index keeps an active version while it holds parked ones (2026-10-18, 0.2.8256; the owner's choice, chat\n"
        "  2026-10-18: \"Refusal\" - all three cleanup calls refuse, the messages naming the remedies, Book teardown\n"
        "  unaffected): `Conduit.cleanup_spell` (`Spellbook._dispose_spell`), `Spellbook.cleanup_and_remove_spell` and\n"
        "  a direct `Spell.cleanup()` - which routes to `cleanup_and_remove_spell` - refuse the active member of an\n"
        "  index that also holds parked versions before anything is unregistered, and change nothing; the sole member\n"
        "  of an index is removed with its index, as before. Retiring an active version while parked ones remain is\n"
        "  the agent's order, and Melder picks no version: (a) notch the index to a parked version, then\n"
        "  `cleanup_spell` the old one, now parked; (b) `cleanup_spell` the parked versions, then the active one\n"
        "  alone, and its index goes; (c) `remove_from_spell_index` each parked version (each move mints an index of\n"
        "  its own, the version parked in it), then the active one. Known gaps on those paths, filed: a parked\n"
        "  `cleanup_spell` leaves index-link borrowers a copy (STORY-2026-10-17-parked_cleanup_leaves_borrower_copies)\n"
        "  and a minted index is missing from the frame registry\n"
        "  (STORY-2026-10-17-minted_index_missing_from_frame_registry). The check is `SpellIndex.is_sole_member`, read\n"
        "  under the index lock in `cleanup_and_remove_spell`'s first Book-locked section (Spellbook -> index, the\n"
        "  order `_dispose_spell` already took), so no lock or lock-order edge is added. Book teardown never meets it:\n"
        "  `_cleanup_spells` and the parked disposal set `_spellbook_cleanup` before they clean a spell, so its\n"
        "  `cleanup()` does not route to the Book. `cleanup_spell` takes no transaction and decides and removes in two\n"
        "  Book-locked sections, so a version staged onto the index between them now meets the check after the spell\n"
        "  was invalidated, and the call raises with nothing removed. Until 0.2.8256 the two direct doors removed the\n"
        "  version and cleaned the index under its parked versions, which stayed in the Book uncleaned and unknown to\n"
        "  the frame, where no call could notch, move, dispose or clean them. Not changed: the direct doors send\n"
        "  index-link borrowers no emission, and Book teardown leaves parked versions uncleaned\n"
        "  (" + S7 + ").\n"
        "  EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook.cleanup_and_remove_spell`,\n"
        "  `Spellbook._dispose_spell`, `Spellbook.cleanup_spell`, `Spellbook._cleanup_spells`,\n"
        "  `src/melder/aether/spellbook/spell.py:Spell.cleanup`, `Spell._direct_removal_route` and\n"
        "  `src/melder/aether/spellbook/bind/spell_index.py:SpellIndex.is_sole_member`.\n"
        "- A managed spell's settings are not part of its spell_id (2026-10-18, 0.2.8254;",
    ),
    (
        "## Failure Modes and Error Paths\n- Breaking (0.2.8254): every managed spell's spell_id moves once",
        "## Failure Modes and Error Paths\n"
        "- Breaking (0.2.8256): `Spellbook.cleanup_and_remove_spell(spell)` and a direct `Spell.cleanup()` of the\n"
        "  active version of an index that also holds parked versions raise RuntimeError \"Spellbook cannot remove\n"
        "  spell <id>: it is the active member of a multi-member index, and disposing it would leave the index's\n"
        "  parked versions without an active one. Notch the index to one of them, dispose them with cleanup_spell, or\n"
        "  move them out with remove_from_spell_index first.\" and change nothing. Before, they removed the version and\n"
        "  cleaned the index under its parked versions: each stayed parked in the Book, uncleaned and unknown to the\n"
        "  frame - a notch to it raised AttributeError, `add_to_spell_index` and `cleanup_spell` of it raised\n"
        "  \"SpellIndex has already been cleaned.\", the Book's teardown left it and its own `cleanup()` then raised\n"
        "  \"Spellbook has already been cleaned.\". `cleanup_spell`'s refusal of the same member now names the same\n"
        "  remedies after its \"cleanup_spell: spell <id> is the active member of a multi-member index\" prefix (it\n"
        "  said \"...; notch away from it before disposing it.\"). The sole member of an index is removed by any of the\n"
        "  three, with its index, as before.\n"
        "  EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook.cleanup_and_remove_spell` and\n"
        "  `Spellbook._dispose_spell`.\n"
        "- Breaking (0.2.8254): every managed spell's spell_id moves once",
    ),
    (
        "## Context / Handoff Summary\n\n2026-10-18 managed settings leave the spell_id (0.2.8254; part A of\n",
        "## Context / Handoff Summary\n\n"
        "2026-10-18 direct cleanup refusal (0.2.8256; " + STORY + ",\n"
        "on the owner's choice \"Refusal\"): `Spellbook.cleanup_and_remove_spell` and a direct `Spell.cleanup()` refuse\n"
        "the active version of an index that holds parked versions, as `cleanup_spell` refuses it, and all three\n"
        "messages name the remedies (notch first, dispose the parked versions, or move them out); Book teardown never\n"
        "meets the check. A new operational invariant, a Breaking failure mode and the code map (two files\n"
        "remeasured) carry it; the component map carries the per-component contracts. Every numeric citation into\n"
        "spellbook.py past the check moved 27 lines (31 past `cleanup_spell`'s docstring) and was remapped line by\n"
        "line. Open: the direct doors' silence to index-link borrowers, Book teardown's parked versions (S7), and the\n"
        "hole rule (an index alive with nothing active), which the owner proposed and then withdrew for the refusal.\n\n"
        "2026-10-18 managed settings leave the spell_id (0.2.8254; part A of\n",
    ),
    (
        "- path: `src/melder/aether/spellbook/spellbook.py`\n  start_line: 1\n  end_line: 7771\n  loc: 7771\n"
        "  verified_at: 2026-10-17T23:03:04Z\n",
        "- path: `src/melder/aether/spellbook/spellbook.py`\n  start_line: 1\n  end_line: 7802\n  loc: 7802\n"
        "  verified_at: " + STAMP + "\n",
    ),
    (
        "    answers its own spell, no index read (0.2.8253).\n- path: `src/melder/aether/spellbook/spellbook_creation_system.py`",
        "    answers its own spell, no index read (0.2.8253); `cleanup_and_remove_spell` refuses the active member of an\n"
        "    index that holds parked versions and `_dispose_spell`'s refusal names the same remedies (0.2.8256).\n"
        "- path: `src/melder/aether/spellbook/spellbook_creation_system.py`",
    ),
    (
        "- path: `src/melder/aether/spellbook/spell.py`\n  start_line: 1\n  end_line: 1968\n  loc: 1968\n"
        "  verified_at: 2026-10-17T23:03:04Z\n",
        "- path: `src/melder/aether/spellbook/spell.py`\n  start_line: 1\n  end_line: 1972\n  loc: 1972\n"
        "  verified_at: " + STAMP + "\n",
    ),
    (
        "    index steps among them (0.2.8253).\n- path: `src/melder/aether/spellbook/existence/existence.py`",
        "    index steps among them (0.2.8253); `cleanup`'s Raises names the multi-member refusal and its remedies\n"
        "    (0.2.8256).\n"
        "- path: `src/melder/aether/spellbook/existence/existence.py`",
    ),
]

TESTS_COMPONENTS = [
    (
        "- the densest tier: 509 `test_*.py` modules among 512 `.py` files (recounted 2026-10-17)\n",
        "- the densest tier: 510 `test_*.py` modules among 513 `.py` files (recounted 2026-10-18)\n",
    ),
    (
        "- No harness or support module of its own; the 53 test_*.py modules in\n  tests/unit/melder/utilities/",
        "- No harness or support module of its own; the 54 test_*.py modules in\n  tests/unit/melder/utilities/",
    ),
    (
        "- 173 `test_*.py` modules among 180 `.py` files (recounted 2026-10-18); the others are benches and the\n",
        "- 175 `test_*.py` modules among 182 `.py` files (recounted 2026-10-18); the others are benches and the\n",
    ),
    (
        "- The aether tree carries 48 `test_*.py` modules beneath these; they are the\n",
        "- The aether tree carries 49 `test_*.py` modules beneath these; they are the\n",
    ),
    (
        "- No harness or support module of its own; the 44 test_*.py modules in\n  tests/integration/melder/conduit/",
        "- No harness or support module of its own; the 45 test_*.py modules in\n  tests/integration/melder/conduit/",
    ),
    (
        "- No harness or support module of its own; the 51 test_*.py modules in\n  tests/integration/melder/spellbook/",
        "- No harness or support module of its own; the 52 test_*.py modules in\n  tests/integration/melder/spellbook/",
    ),
    (
        "builders - not every `test_*.py` module beneath it. The 848 test modules of the\n",
        "builders - not every `test_*.py` module beneath it. The 851 test modules of the\n",
    ),
    (
        "  French, and a transfer with dependencies after a notch moves Greeter's index with French active\n"
        "Key Files (C1):\n",
        "  French, and a transfer with dependencies after a notch moves Greeter's index with French active\n"
        "- a cleanup of an index's active version refuses while parked versions remain (0.2.8256;\n"
        "  `" + TEST_FILE + "`, 9 tests): in a dynamic\n"
        "  world with English active and French parked on Greeter's index, contracted whole by a linked borrower,\n"
        "  `English.cleanup()` and `cleanup_and_remove_spell` - by the Spell and by its spell_id - raise the\n"
        "  multi-member RuntimeError naming the three remedies and change nothing (the index live and selecting\n"
        "  English, both versions uncleaned and found by the frame, the lineage registered, the borrower's copies as\n"
        "  staged, English meldable); `cleanup_spell(English)` raises its own refusal naming the same remedies; after\n"
        "  a refusal each remedy works - a notch to French and then `cleanup_spell` of the parked English,\n"
        "  `cleanup_spell(French)` and then `English.cleanup()`, `remove_from_spell_index(French)` and then\n"
        "  `English.cleanup()` (French stays parked, alone in a fresh index); and English alone on its index is still\n"
        "  removed by either door, its index cleaned and gone from the frame\n"
        "Key Files (C1):\n",
    ),
    (
        "- `tests/integration/melder/spellbook/test_spellbook_integration_parked_before_conjure.py` (2026-10-16)\n"
        "- `tests/integration/melder/aether/conduit/test_notch_spell_by_id_integration.py` (2026-10-16)\n",
        "- `tests/integration/melder/spellbook/test_spellbook_integration_parked_before_conjure.py` (2026-10-16)\n"
        "- `" + TEST_PATH + "` (2026-10-18)\n"
        "- `tests/integration/melder/aether/conduit/test_notch_spell_by_id_integration.py` (2026-10-16)\n",
    ),
    (
        "  note: versions staged before or after conjure meld after a notch, every family (0.2.8248).\n",
        "  note: versions staged before or after conjure meld after a notch, every family (0.2.8248).\n"
        "- path: `" + TEST_PATH + "`\n"
        "  start_line: 1\n  end_line: 312\n  loc: 312\n  verified_at: " + STAMP + "\n"
        "  note: the three cleanup doors refuse an index's active version while parked versions remain; the\n"
        "    remedies; a sole member still removed (0.2.8256).\n",
    ),
    (
        "test_rift_spell_id_lookups_return_that_spell_integration.py`\n- direct filesystem inventory of `tests/`\n",
        "test_rift_spell_id_lookups_return_that_spell_integration.py`\n"
        "- `" + TEST_PATH + "`\n"
        "- direct filesystem inventory of `tests/`\n",
    ),
    (
        "## Context / Handoff Summary\n\n2026-10-18 managed settings leave the spell_id (0.2.8254; part A of\n",
        "## Context / Handoff Summary\n\n"
        "2026-10-18 direct cleanup refusal (0.2.8256; " + STORY + "):\n"
        "the Spellbook Integration Cluster gains `" + TEST_FILE + "`\n"
        "(9 tests: both direct doors refused with nothing changed, `cleanup_spell`'s message, the three remedies, the\n"
        "sole-member controls), a key file with a code-map record. Counts are recounted from disk (unit 510 of 513\n"
        "`.py`, utilities tree 54; integration 175 of 182, aether tree 49, conduit tree 45, spellbook tree 52; 851 test\n"
        "modules in the three tiers). Besides this lane's module they take in the two red-test modules written for the\n"
        "held " + S8 + " (one unit, one integration;\n"
        "18 tests that fail until that story lands and catalogues them), and the conduit tree's count, one short since\n"
        "0.2.8254's module.\n\n"
        "2026-10-18 managed settings leave the spell_id (0.2.8254; part A of\n",
    ),
]

TESTS_ARCHITECTURE = [
    (
        "- `unit/`: 512 `.py` files, 509 of them `test_*.py` (465 on 2026-09-26, 334 on 2026-06-13)\n",
        "- `unit/`: 513 `.py` files, 510 of them `test_*.py` (465 on 2026-09-26, 334 on 2026-06-13)\n",
    ),
    (
        "- `integration/`: 180 `.py` files, 173 of them `test_*.py` (149, 88)\n",
        "- `integration/`: 182 `.py` files, 175 of them `test_*.py` (149, 88)\n",
    ),
    (
        "(pycache excluded); the three tiers' 848 `test_*.py`\n",
        "(pycache excluded); the three tiers' 851 `test_*.py`\n",
    ),
    (
        "## Context / Handoff Summary\n\n2026-10-18 managed settings leave the spell_id (0.2.8254): the inventory is",
        "## Context / Handoff Summary\n\n"
        "2026-10-18 direct cleanup refusal (0.2.8256): the inventory is recounted from disk (unit 513 `.py`, component\n"
        "168, integration 182, mocks 44, experimentation 204; 851 test modules in the three tiers) - the lane adds one\n"
        "integration module (the three cleanup doors refusing an index's active version while parked versions remain),\n"
        "catalogued in `tests_components`. The count also takes in the two red-test modules written for the held\n"
        + S8 + " (one unit, one integration), whose 18 tests\n"
        "fail on purpose until that story lands and catalogues them. No tier, conftest, declared marker or shared\n"
        "support module changes, and no extent in this map moves.\n\n"
        "2026-10-18 managed settings leave the spell_id (0.2.8254): the inventory is",
    ),
]

PLAN = [
    ("src_components.md", SRC_COMPONENTS),
    ("src_architecture.md", SRC_ARCHITECTURE),
    ("tests_components.md", TESTS_COMPONENTS),
    ("tests_architecture.md", TESTS_ARCHITECTURE),
]


def too_long(line: str) -> bool:
    """A line over 120 characters is allowed only when a backticked token of 60 or more makes it unbreakable."""
    if len(line) <= 120:
        return False
    return not any(len(token) >= 60 for token in re.findall(r"`([^`]+)`", line))


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    problems = []
    results = {}
    for name, pairs in PLAN:
        path = DOCS / name
        raw = path.read_bytes()
        if b"\r\n" in raw:
            raise SystemExit("CRLF in " + name)
        text = raw.decode("utf-8")
        for index, (old, new) in enumerate(pairs, 1):
            count = text.count(old)
            if count != 1:
                problems.append("%s #%d: old text found %d times: %r" % (name, index, count, old[:90]))
                continue
            for line in new.split("\n"):
                if too_long(line):
                    problems.append("%s #%d: line of %d chars: %s" % (name, index, len(line), line))
            text = text.replace(old, new, 1)
        results[name] = text
        print("%s: %d replacements, %d lines" % (name, len(pairs), text.count("\n")))
    if problems:
        for problem in problems:
            print("PROBLEM", problem)
        raise SystemExit(1)
    if mode == "--apply":
        for name, text in results.items():
            path = DOCS / name
            path.write_bytes(text.encode("utf-8"))
            if path.read_bytes().decode("utf-8") != text:
                raise SystemExit("read-back mismatch: " + name)
        print("applied at", STAMP)


main()
