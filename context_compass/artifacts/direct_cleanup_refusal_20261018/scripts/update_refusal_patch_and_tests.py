"""Update S9's patch docs and red tests for the owner's pick (2026-10-18): the refusal on all three cleanup doors,
each message naming the three remedies; `cleanup_spell`'s message reworded; a third remedy test.

Each file is re-read right before it is written; every anchor must occur exactly once; LF kept; read back.
Usage: update_refusal_patch_and_tests.py --check | --apply
"""
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[4]
PATCH = REPO / "context_compass/system_docs/patches/active/direct_cleanup_refusal_2026_10_18"
TEST = REPO / ("tests/integration/melder/spellbook/"
               "test_direct_cleanup_refuses_active_member_with_parked_versions_integration.py")


def swap(text: str, old: str, new: str, label: str) -> str:
    """Replace one anchored block; the anchor must occur exactly once."""
    count = text.count(old)
    if count != 1:
        raise SystemExit("anchor %s found %d times" % (label, count))
    return text.replace(old, new)


def check_widths(block: str, label: str) -> None:
    """Refuse a written line over the 120-character cap."""
    for line in block.split("\n"):
        if len(line) > 120:
            raise SystemExit("%s: line over 120 chars (%d): %s" % (label, len(line), line))


ARCH = [
    ("""  versions_uncleaned, S7); retiring a whole lineage through a direct removal (the owner's alternative, not taken).
""", """  versions_uncleaned, S7); retiring a whole lineage through a direct removal (the owner's alternative, not taken);
  an index kept alive with parked versions and nothing active (the hole rule, weighed and not taken by the owner on
  2026-10-18; the story's DECISION and TRADEOFF notes).
"""),
    ("""- Docstrings only: `Spell.cleanup` (its Raises lists the new refusal).
""", """- Spellbook, `cleanup_spell`'s refusal (`_dispose_spell`): its message is reworded to name the same remedies; when
  and what it refuses is unchanged.
- Docstrings only: `Spell.cleanup` (its Raises lists the new refusal) and `Spellbook.cleanup_spell` (its Contract
  names the remedies).
"""),
    ("""- Public behaviour, **Breaking:** `Spellbook.cleanup_and_remove_spell(spell)` and a direct `Spell.cleanup()` of the
  active member of an index that holds parked versions raise RuntimeError "Spellbook cannot remove spell <id>: it
  is the active member of a multi-member index; notch away from it before disposing it, or dispose the index's
  parked versions first with cleanup_spell." and change nothing. Signatures are unchanged. The message names no
  door, because `cleanup_spell` can meet it too (component patch, State and failure deltas).
""", """- Public behaviour, **Breaking:** `Spellbook.cleanup_and_remove_spell(spell)` and a direct `Spell.cleanup()` of the
  active member of an index that holds parked versions raise RuntimeError "Spellbook cannot remove spell <id>: it
  is the active member of a multi-member index, and disposing it would leave the index's parked versions without an
  active one. Notch the index to one of them, dispose them with cleanup_spell, or move them out with
  remove_from_spell_index first." and change nothing. Signatures are unchanged. The message names no door, because
  `cleanup_spell` can meet it too (component patch, State and failure deltas).
- Public behaviour: `cleanup_spell`'s refusal of the same member keeps its type and its moment and names the same
  remedies: "cleanup_spell: spell <id> is the active member of a multi-member index, and disposing it would leave
  the index's parked versions without an active one. Notch the index to one of them, dispose them with
  cleanup_spell, or move them out with remove_from_spell_index first." (it said "...; notch away from it before
  disposing it.").
"""),
    ("""1. These patch docs, linked from the story; the owner's word on the exact edits. 2. spellbook.py (held, M1-33) and
spell.py claimed from melder_0 by message. 3. Red tests. 4. The code and the two docstrings. 5. The tests, GIL off
and on; probe D1-D3 re-run. 6. System documents with their indexes, the graph, the release note; the next free
notch. 7. Closure; the rebuild last.
""", """1. These patch docs, linked from the story; the owner's word on the exact edits. 2. spellbook.py and spell.py held
(M1-33, M0-195), S9 landing before S1 (M1-37). 3. Red tests. 4. The code, the reworded message and the three
docstrings. 5. The tests, GIL off and on; probe D1-D3 re-run. 6. System documents with their indexes, the graph, the
release note; the next free notch. 7. Closure; the rebuild last; the two files handed back to melder_0.
"""),
    ("""- Remove the check: the direct doors clean the index under its parked versions again. Nothing persisted, cached or
  emitted changes, so no cache generation or record version moves either way.
""", """- Remove the check and restore `_dispose_spell`'s old wording: the direct doors clean the index under its parked
  versions again. Nothing persisted, cached or emitted changes, so no cache generation or record version moves
  either way.
"""),
]
COMP = [
    ("""- None in signatures. Behaviour: RuntimeError "Spellbook cannot remove spell <id>: it is the active member of a
  multi-member index; notch away from it before disposing it, or dispose the index's parked versions first with
  cleanup_spell." from both public doors. `cleanup_and_remove_spell`'s and `Spell.cleanup`'s docstrings name
  it under Raises, and the method's Contract says the sole-member rule.
""", """- None in signatures. Behaviour: RuntimeError "Spellbook cannot remove spell <id>: it is the active member of a
  multi-member index, and disposing it would leave the index's parked versions without an active one. Notch the
  index to one of them, dispose them with cleanup_spell, or move them out with remove_from_spell_index first." from
  both public doors. `_dispose_spell` words `cleanup_spell`'s refusal the same way after its "cleanup_spell: spell
  <id>" prefix. `cleanup_and_remove_spell`'s and `Spell.cleanup`'s docstrings name it under Raises, the method's
  Contract says the sole-member rule, and `cleanup_spell`'s Contract names the remedies.
"""),
    ("""  `cleanup_spell(French)`, then `English.cleanup()` removes English with its index.
""", """  `cleanup_spell(French)`, then `English.cleanup()` removes English with its index; `remove_from_spell_index(French)`,
  then `English.cleanup()` removes English with its index and leaves French parked, alone in a fresh index.
- Integration: `cleanup_spell(English)` raises its refusal naming the three remedies, and changes nothing.
"""),
]
TESTS = [
    ("""`Conduit.cleanup_spell` refuses the active member of a multi-member index ("notch away from it first"). Until the fix
the two other public doors - a direct `Spell.cleanup()` and `Spellbook.cleanup_and_remove_spell` - cleaned the index
under its parked versions, leaving a version no later call could notch, move, dispose or clean (probe D2 and D3,
artifacts/correctness_defects_20261017/probes/probe_direct_cleanup_active_member.py). Both now refuse the same way,
and the sole member of an index is removed as before.
""", """`Conduit.cleanup_spell` refuses the active member of a multi-member index. Until the fix the two other public doors -
a direct `Spell.cleanup()` and `Spellbook.cleanup_and_remove_spell` - cleaned the index under its parked versions,
leaving a version no later call could notch, move, dispose or clean (probe D2 and D3,
artifacts/correctness_defects_20261017/probes/probe_direct_cleanup_active_member.py). All three now refuse it, each
message naming the remedies - notch the index to a parked version, dispose the parked versions, or move them out -
and the sole member of an index is removed as before (the owner's choice, 2026-10-18).
"""),
    ("""import contextlib
from typing""", """import contextlib
import re
from typing"""),
    ("""    return "is the active member of a multi-member index; notch away from it before disposing it"
""", """    return re.escape(
        "is the active member of a multi-member index, and disposing it would leave the index's parked versions "
        "without an active one. Notch the index to one of them, dispose them with cleanup_spell, or move them out "
        "with remove_from_spell_index first."
    )
"""),
    ("""

def test_after_the_refusal_a_notch_away_lets_the_old_version_go() -> None:
""", """

def test_cleanup_spell_refusal_names_the_remedies() -> None:
    \"\"\"
    `cleanup_spell(English)` keeps its refusal of the active member and now names the same three remedies.

    Contract:
        - It raises the multi-member RuntimeError, prefixed "cleanup_spell: spell <spell_id>", and changes nothing.
    \"\"\"
    with _world("cleanup_spell_refused") as world:
        prefix = "^cleanup_spell: spell " + re.escape(world.english.spell_id) + " "
        with pytest.raises(RuntimeError, match=prefix + _refusal()):
            world.lender.cleanup_spell(spell=world.english)

        _assert_nothing_changed(world)


def test_after_the_refusal_a_notch_away_lets_the_old_version_go() -> None:
"""),
    ("""

@pytest.mark.parametrize("door", ["spell_cleanup", "cleanup_and_remove_spell"])
""", """

def test_after_the_refusal_moving_the_parked_version_out_lets_the_member_go() -> None:
    \"\"\"
    The third remedy: move French out with `remove_from_spell_index`; English is then its index's sole member and is
    removed with it, while French stays parked, alone in a fresh index.
    \"\"\"
    with _world("refused_then_move_parked_out") as world:
        assert world.french is not None
        english_id, french_id = world.english.spell_id, world.french.spell_id
        with pytest.raises(RuntimeError, match=_refusal()):
            world.english.cleanup()

        world.lender.remove_from_spell_index(spell_id=french_id, source_index=world.index)
        world.english.cleanup()

        assert world.english.cleaned and world.index.cleaned
        assert english_id not in world.book._spells_by_id
        assert not world.french.cleaned
        assert world.book._inactive_spells[french_id] is world.french
        assert world.french.spell_index is not world.index
        assert world.french.spell_index.spells_in_index() == {french_id}


@pytest.mark.parametrize("door", ["spell_cleanup", "cleanup_and_remove_spell"])
"""),
]


def edit(path: pathlib.Path, pairs: list, apply: bool) -> None:
    """Apply the anchored replacements to one file; write it only with --apply."""
    raw = path.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("CRLF in %s" % path.name)
    text = raw.decode("utf-8")
    for n, (old, new) in enumerate(pairs):
        check_widths(new, "%s#%d" % (path.name, n))
        text = swap(text, old, new, "%s#%d" % (path.name, n))
    if apply:
        path.write_bytes(text.encode("utf-8"))
        if path.read_bytes().decode("utf-8") != text:
            raise SystemExit("read-back mismatch in %s" % path.name)


def main() -> None:
    """Check every anchor in all three files first, then write them with --apply."""
    if len(sys.argv) != 2 or sys.argv[1] not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    plan = [(PATCH / "architecture_patch.md", ARCH), (PATCH / "component_patch_spellbook_removal_path.md", COMP),
            (TEST, TESTS)]
    for path, pairs in plan:
        edit(path, pairs, apply=False)
    print("all anchors found")
    if sys.argv[1] == "--apply":
        for path, pairs in plan:
            edit(path, pairs, apply=True)
        print("applied")


main()
