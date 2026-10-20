"""Bring tests_components and tests_architecture to the owner's extension (two new test files) and spell_id wording.

Run from context_compass/:  python docs_extension_tests_docs.py <NOW>
Each replacement must match exactly once; both files stay LF. Counts were recounted from disk on this pass.
"""
import pathlib
import sys

NOW = sys.argv[1]

COMPONENTS = [
    ("- the densest tier: 506 `test_*.py` modules among 509 `.py` files (recounted 2026-10-16)\n",
     "- the densest tier: 507 `test_*.py` modules among 510 `.py` files (recounted 2026-10-16)\n"),
    ("- The aether tree carries 205 `test_*.py` modules beneath these; they are the\n",
     "- The aether tree carries 206 `test_*.py` modules beneath these; they are the\n"),
    ("- 168 `test_*.py` modules among 175 `.py` files (recounted 2026-10-16); the others are benches and the\n",
     "- 169 `test_*.py` modules among 176 `.py` files (recounted 2026-10-16); the others are benches and the\n"),
    ("- The aether tree carries 45 `test_*.py` modules beneath these; they are the\n",
     "- The aether tree carries 46 `test_*.py` modules beneath these; they are the\n"),
    # Spellbook Runtime And Binding Unit Cluster: the notch bullet in spell_id wording, then the index moves.
    ("""  Book): by id the Book's `_get_owned_spell` is asked and the resolved version reaches the transaction metadata,
  `_notch_spell` and the fan-out; an owned `spell` passes through; `change_reason` is passed on; the active version
  by id does not fan out; both or neither target, a non-str id, a str given as `spell`, an unknown id, another
  index's version by id and by object, a Spell the Book does not own and a stale Spell are refused with no
  transaction started and the seam not called; a target moved after the first check is refused inside the window
  with the transaction ended as failed; an automatic conduit still raises the dynamic-mode RuntimeError before the
  Book is asked
""",
     """  Book): by spell_id the Book's `_get_owned_spell` is asked and the resolved version reaches the transaction
  metadata, `_notch_spell` and the fan-out; an owned `spell` passes through; `change_reason` is passed on; the
  active version by spell_id does not fan out; both or neither target, a non-str spell_id, a str given as `spell`,
  an unknown spell_id, another index's version by spell_id and by object, a Spell the Book does not own and a stale
  Spell are refused with no transaction started and the seam not called; a target moved after the first check is
  refused inside the window with the transaction ended as failed; an automatic conduit still raises the
  dynamic-mode RuntimeError before the Book is asked
- the index moves by spell_id (0.2.8249, the owner's extension; `test_conduit_index_move_target.py`, 16 tests over
  the same stub Book): for `add_to_spell_index` and `remove_from_spell_index` a spell_id is resolved through
  `_get_owned_spell` and the resolved Spell reaches the transaction metadata, the Book's entry and the index-link
  fan-out (add: the member added on the target and removed from the source); `spell=` passes through without
  asking the Book; both or neither, a non-str spell_id, a str given as `spell` and an unknown spell_id are refused
  in the verb's own words with no transaction started, the Book's entries not called and nothing fanned out; an
  automatic conduit raises the dynamic-mode RuntimeError before the Book is asked
"""),
    ("- `tests/unit/melder/aether/conduit/test_conduit_notch_target.py` (public notch target, 2026-10-16)\n",
     "- `tests/unit/melder/aether/conduit/test_conduit_notch_target.py` (public notch target, 2026-10-16)\n"
     "- `tests/unit/melder/aether/conduit/test_conduit_index_move_target.py` (index moves by spell_id, 2026-10-16)\n"),
    # Spellbook Integration Cluster: the notch bullet in spell_id wording, then the index moves.
    ("""- the public notch target (0.2.8249; `test_notch_spell_by_id_integration.py`, 10 tests): in a dynamic world a
  notch by the id `bind_inactive` returned promotes a version staged after conjure and one staged before it, the
  next meld builds it and the call returns it; a notch back by id restores the first version with both members
  kept; the active id is a no-op; a parked version of another index (by id and by object), another index's active
  version, another Book's version and an unknown id are refused with ValueError while both indexes keep their
  selection, members and melds; an index-linked borrower melds the version notched in by id
""",
     """- the public notch target (0.2.8249; `test_notch_spell_by_id_integration.py`, 10 tests): in a dynamic world a
  notch by the spell_id `bind_inactive` returned promotes a version staged after conjure and one staged before it,
  the next meld builds it and the call returns it; a notch back by spell_id restores the first version with both
  members kept; the active spell_id is a no-op; a parked version of another index (by spell_id and by object),
  another index's active version, another Book's version and an unknown spell_id are refused with ValueError while
  both indexes keep their selection, members and melds; an index-linked borrower melds the version notched in by
  spell_id
- the index moves by spell_id (0.2.8249, the owner's extension; `test_index_moves_by_spell_id_integration.py`, 10
  tests): in a dynamic world `add_to_spell_index(spell_id=...)` moves a parked spell onto another index, where a
  notch to it melds it, and `remove_from_spell_index(spell_id=...)` splits it into a fresh index of its own while
  the source keeps its active spell; an unknown spell_id, another Book's spell_id, both and neither are refused
  with ValueError, and an active spell's spell_id with the Book's RuntimeError, each leaving both indexes'
  selection, members and melds intact
"""),
    ("- `tests/integration/melder/aether/conduit/test_notch_spell_by_id_integration.py` (2026-10-16)\n\n",
     "- `tests/integration/melder/aether/conduit/test_notch_spell_by_id_integration.py` (2026-10-16)\n"
     "- `tests/integration/melder/aether/conduit/test_index_moves_by_spell_id_integration.py` (2026-10-16)\n\n"),
    # C1 Code Map (Core): the two notch records remeasured and reworded, the two new records.
    ("""- path: `tests/unit/melder/aether/conduit/test_conduit_notch_target.py`
  start_line: 1
  end_line: 252
  loc: 252
  verified_at: 2026-10-16T13:54:00Z
  note: the notch target named by id or Spell, resolved and checked before and inside the transaction (0.2.8249).
""",
     """- path: `tests/unit/melder/aether/conduit/test_conduit_notch_target.py`
  start_line: 1
  end_line: 252
  loc: 252
  verified_at: """ + NOW + """
  note: the notch target named by spell_id or Spell, resolved and checked before and inside the transaction
    (0.2.8249).
- path: `tests/unit/melder/aether/conduit/test_conduit_index_move_target.py`
  start_line: 1
  end_line: 232
  loc: 232
  verified_at: """ + NOW + """
  note: the index moves name their spell by spell_id or Spell; the argument checks and the resolution (0.2.8249).
"""),
    ("""- path: `tests/integration/melder/aether/conduit/test_notch_spell_by_id_integration.py`
  start_line: 1
  end_line: 271
  loc: 271
  verified_at: 2026-10-16T13:54:00Z
  note: the stage -> notch -> meld loop by id, its revert, and foreign targets refused intact (0.2.8249).
""",
     """- path: `tests/integration/melder/aether/conduit/test_notch_spell_by_id_integration.py`
  start_line: 1
  end_line: 271
  loc: 271
  verified_at: """ + NOW + """
  note: the stage -> notch -> meld loop by spell_id, its revert, and foreign targets refused intact (0.2.8249).
- path: `tests/integration/melder/aether/conduit/test_index_moves_by_spell_id_integration.py`
  start_line: 1
  end_line: 226
  loc: 226
  verified_at: """ + NOW + """
  note: add and remove by spell_id in a dynamic world; the refusals leave both indexes intact (0.2.8249).
"""),
    # Information Sources.
    ("""- `tests/unit/melder/aether/conduit/test_conduit_notch_target.py`
- `tests/integration/melder/aether/conduit/test_notch_spell_by_id_integration.py`
- direct filesystem inventory of `tests/`
""",
     """- `tests/unit/melder/aether/conduit/test_conduit_notch_target.py`
- `tests/integration/melder/aether/conduit/test_notch_spell_by_id_integration.py`
- `tests/unit/melder/aether/conduit/test_conduit_index_move_target.py`
- `tests/integration/melder/aether/conduit/test_index_moves_by_spell_id_integration.py`
- direct filesystem inventory of `tests/`
"""),
    # Context / Handoff Summary: the lane's entry.
    ("""`test_conduit_notch_target.py` (16 tests: the id resolved and passed on, every refusal with nothing started, the
in-window re-check) and the Spellbook Integration Cluster `test_notch_spell_by_id_integration.py` (10 tests: the
loop and its revert by id, the no-op, the foreign targets refused with both indexes intact, an index-linked
borrower following), each a key file with a code-map record; the Unit Test Suite and the Integration Runtime Suite
name the protection, and their module counts are recounted from disk (unit 506 of 509 `.py`, aether tree 205;
integration 168 of 175, aether tree 45; 840 test modules in the three tiers).
""",
     """`test_conduit_notch_target.py` (16 tests: the spell_id resolved and passed on, every refusal with nothing started,
the in-window re-check) and the Spellbook Integration Cluster `test_notch_spell_by_id_integration.py` (10 tests:
the loop and its revert by spell_id, the no-op, the foreign targets refused with both indexes intact, an
index-linked borrower following), each a key file with a code-map record; the Unit Test Suite and the Integration
Runtime Suite name the protection. On the owner's extension the same two clusters gain
`test_conduit_index_move_target.py` (16 tests: the index moves' argument checks and spell_id resolution, nothing
started on a refusal) and `test_index_moves_by_spell_id_integration.py` (10 tests: add and remove by spell_id, the
refusals with both indexes intact), each a key file with a code-map record, and the notch files say spell_id. The
module counts are recounted from disk (unit 507 of 510 `.py`, aether tree 206; component 166 of 168; integration
169 of 176, aether tree 46; 842 test modules in the three tiers).
"""),
]

ARCHITECTURE = [
    ("""- `unit/`: 509 `.py` files, 506 of them `test_*.py` (465 on 2026-09-26, 334 on 2026-06-13)
- `component/`: 168 `.py` files, 166 of them `test_*.py` (143, 81)
- `integration/`: 175 `.py` files, 168 of them `test_*.py` (149, 88)
""",
     """- `unit/`: 510 `.py` files, 507 of them `test_*.py` (465 on 2026-09-26, 334 on 2026-06-13)
- `component/`: 168 `.py` files, 166 of them `test_*.py` (143, 81)
- `integration/`: 176 `.py` files, 169 of them `test_*.py` (149, 88)
"""),
    ("""Recounted 2026-10-16 with `find tests/<tier> -name '*.py'` (pycache excluded); the three tiers' 840 `test_*.py`
""",
     """Recounted 2026-10-16 with `find tests/<tier> -name '*.py'` (pycache excluded); the three tiers' 842 `test_*.py`
"""),
    ("""2026-10-16 public notch target (0.2.8249): the inventory is recounted from disk (unit 509 `.py`, component 168,
integration 175, mocks 44, experimentation 204; 840 test modules in the three tiers) - the lane adds one unit and
one integration module, catalogued in `tests_components`. No tier, conftest, marker or shared support module
changes, and no extent in this map moves.
""",
     """2026-10-16 public notch target (0.2.8249): the inventory is recounted from disk (unit 510 `.py`, component 168,
integration 176, mocks 44, experimentation 204; 842 test modules in the three tiers) - the lane adds two unit and
two integration modules (the notch target, then on the owner's extension the index moves by spell_id),
catalogued in `tests_components`. No tier, conftest, marker or shared support module changes, and no extent in
this map moves.
"""),
]


def apply(path: str, edits: list) -> None:
    """
    Apply one document's edits; refuse unless each matches exactly once.

    Args:
        path: The document, relative to context_compass/.
        edits: (old, new) pairs.
    """
    doc = pathlib.Path(path)
    text = doc.read_text(encoding="utf-8")
    assert "\r\n" not in text
    for old, new in edits:
        count = text.count(old)
        assert count == 1, (path, count, old[:90])
        text = text.replace(old, new, 1)
    doc.write_text(text, encoding="utf-8")
    long = [i + 1 for i, line in enumerate(text.split("\n")) if len(line) > 120]
    print(path, "ok; lines:", len(text.split("\n")) - 1, "over 120:", long[:10])


def main() -> None:
    """Apply both documents' edits."""
    apply("system_docs/tests_components.md", COMPONENTS)
    apply("system_docs/tests_architecture.md", ARCHITECTURE)


if __name__ == "__main__":
    main()
