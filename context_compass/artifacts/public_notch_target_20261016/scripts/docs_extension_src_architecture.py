"""Bring src_architecture to the owner's extension (index moves by spell_id) and the spell_id wording.

Run from context_compass/:  python docs_extension_src_architecture.py <NOW>
Each replacement must match exactly once; the file stays LF.
"""
import pathlib
import sys

NOW = sys.argv[1]
DOC = pathlib.Path("system_docs/src_architecture.md")

EDITS = [
    # 1. System Boundary and External Interfaces: the three verbs' bullet.
    ("""  opposite correctly. The code settles it. `notch_spell`'s docstring has said so since 0.2.8249; the add and
  remove docstrings still carry the old wording.
  `notch_spell` names the version to make active by `spell_id=` - the id `bind` or `bind_inactive` returned - or by
  `spell=`, exactly one, and resolves an id inside the call to the exact version the conduit's Spellbook owns,
  active or parked (0.2.8249). Before the transaction and again inside the held window it refuses a version that
  Spellbook does not own or one of another index (ValueError); a non-str id or a str given as `spell` is a
  TypeError. `get_spell_by_id` and `find_spell_by_id` still answer a parked id with the index's active member, so a
  parked version is named by its id.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:5622, 5731 (`notch_spell`; starts the transaction)
  - src/melder/aether/conduit/conduit.py:5753-5859 (`_resolve_notch_target`, `_owned_notch_target`)
  - src/melder/aether/conduit/conduit.py:5861, 5916 (`add_to_spell_index`; starts it)
  - src/melder/aether/conduit/conduit.py:5939, 5987 (`remove_from_spell_index`; starts it)
""",
     """  opposite correctly. The code settles it, and since 0.2.8249 all three Conduit docstrings say so.
  All three name the spell they act on by `spell_id=` - the spell_id `bind` or `bind_inactive` returned - or by
  `spell=`, exactly one, and resolve a spell_id inside the call to the exact spell the conduit's Spellbook owns,
  active or parked (0.2.8249; the two index moves on the owner's extension). Both or neither is a ValueError, a
  non-str spell_id or a str given as `spell` a TypeError, and a spell_id that Spellbook does not own a ValueError
  before anything starts. Before the transaction and again inside the held window a notch also refuses a spell of
  another index (ValueError); the index moves leave the rest to their seams (RuntimeError: an active spell, another
  Book's spell or target index, a non-member or only member on removal). `get_spell_by_id` and `find_spell_by_id`
  still answer a parked spell_id with the index's active member, so a parked spell is named by its spell_id.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:5622, 5731 (`notch_spell`; starts the transaction)
  - src/melder/aether/conduit/conduit.py:5753-5969 (`_resolve_notch_target`, `_owned_notch_target`,
    `_check_spell_argument`, `_owned_spell_by_id`, `_resolve_spell_to_move`)
  - src/melder/aether/conduit/conduit.py:5971, 6061 (`add_to_spell_index`; starts it)
  - src/melder/aether/conduit/conduit.py:6084, 6159 (`remove_from_spell_index`; starts it)
"""),
    # 2. Architecture Summary.
    ("""fan-out). A notch names its target by version id or by Spell and checks that it is the Book's version of that
index before anything moves (0.2.8249).
""",
     """fan-out). A notch names its target by spell_id or by Spell and checks that it is the Book's version of that
index before anything moves; the two index moves take a spell_id the same way (0.2.8249).
"""),
    ("""`src/melder/aether/conduit/conduit.py:Conduit.notch_spell`, `Conduit._owned_notch_target` (the target check),
`Conduit._deactivate_borrowed_spell` and
""",
     """`src/melder/aether/conduit/conduit.py:Conduit.notch_spell`, `Conduit._owned_notch_target` (the target check),
`Conduit._resolve_spell_to_move` (the index moves' spell_id), `Conduit._deactivate_borrowed_spell` and
"""),
    # 3. Sequence: SpellIndex Mutation Entry, step 1.
    ("""   The entry point is the Conduit. A notch names its target by `spell_id=` (the id
   `bind` or `bind_inactive` returned) or by `spell=`, exactly one:
   `_resolve_notch_target` checks the arguments and `_owned_notch_target` resolves the
   id through the Spellbook's `_get_owned_spell` - the exact owned version, active or
   parked - and refuses a version the Spellbook does not own or one of another index
   before anything starts (0.2.8249).
""",
     """   The entry point is the Conduit. Each verb names its spell by `spell_id=` (the
   spell_id `bind` or `bind_inactive` returned) or by `spell=`, exactly one, checked by
   the shared `_check_spell_argument` (0.2.8249). A notch's `_owned_notch_target`
   resolves the spell_id through the Spellbook's `_get_owned_spell` - the exact owned
   spell, active or parked - and refuses a spell the Spellbook does not own or one of
   another index before anything starts; the index moves' `_resolve_spell_to_move`
   resolves it the same way (`_owned_spell_by_id`) and refuses only a spell_id the
   Spellbook does not own, leaving the rest to their seams (step 5).
"""),
    # 3b. Step 5: the seams' refusals.
    ("""   - add/remove are membership-only moves that leave the spell owned and
     inactive with its id-keyed state untouched; add destroys an emptied source
     index, remove mints a fresh inactive index instead of destroying anything.
""",
     """   - add/remove are membership-only moves that leave the spell owned and
     inactive with its id-keyed state untouched; add destroys an emptied source
     index, remove mints a fresh inactive index instead of destroying anything;
   - before moving, the add and remove seams refuse (RuntimeError) a spell the
     Spellbook does not own and an active one; add also a target index it does not
     own, remove a spell outside the source index or its only member.
"""),
    ("""   - src/melder/aether/conduit/conduit.py:5622-5751
   - src/melder/aether/conduit/conduit.py:5753-5859
   - src/melder/aether/conduit/conduit.py:6056-6085
""",
     """   - src/melder/aether/conduit/conduit.py:5622-5751
   - src/melder/aether/conduit/conduit.py:5753-5969
   - src/melder/aether/conduit/conduit.py:5971-6172
   - src/melder/aether/conduit/conduit.py:6228-6257
"""),
    # 4. Operational Invariants: the notch-target entry.
    ("""  both or neither (ValueError) and a non-str id or a str given as `spell` (TypeError); `_owned_notch_target`
  resolves the id through `Spellbook._get_owned_spell` -""",
     """  both or neither (ValueError) and a non-str spell_id or a str given as `spell` (TypeError); `_owned_notch_target`
  resolves the spell_id through `Spellbook._get_owned_spell` -"""),
    ("""  lock-order edge is added: `_get_owned_spell` takes the Book lock alone and the identity reads take none.
  EVIDENCE: `src/melder/aether/conduit/conduit.py:Conduit.notch_spell`, `Conduit._resolve_notch_target`,
  `Conduit._owned_notch_target`, `src/melder/aether/spellbook/spellbook.py:Spellbook._get_owned_spell`,
  `Spellbook._apply_notch`, `Spellbook._reactivate_owned_spell` and
""",
     """  lock-order edge is added: `_get_owned_spell` takes the Book lock alone and the identity reads take none.
  `add_to_spell_index` and `remove_from_spell_index` take the same two forms (0.2.8249, the owner's extension):
  `_resolve_spell_to_move` runs the shared `_check_spell_argument` - its messages name the verb - and resolves a
  spell_id through `_owned_spell_by_id` (`_get_owned_spell`), refusing one the Book does not own before the
  transaction; a resolved or given Spell then meets the seams' checks as before - owned, parked, and for add a
  target index the Book owns, for remove a member of the source index and not its only member - so nothing new is
  checked inside the window, and a seam's refusal there ends the transaction as failed before anything moves.
  EVIDENCE: `src/melder/aether/conduit/conduit.py:Conduit.notch_spell`, `Conduit._resolve_notch_target`,
  `Conduit._owned_notch_target`, `Conduit._check_spell_argument`, `Conduit._resolve_spell_to_move`,
  `Conduit._owned_spell_by_id`, `src/melder/aether/spellbook/spellbook.py:Spellbook._get_owned_spell`,
  `Spellbook._apply_notch`, `Spellbook._reactivate_owned_spell`, `Spellbook._apply_add_to_index`,
  `Spellbook._apply_remove_from_index` and
"""),
    # 5. Failure Modes: the notch refusals, reworded, and the index moves' refusals.
    ("""  `spell` or `spell_id`, not both." and "notch_spell needs the version to make active: pass spell_id=<the id bind or
  bind_inactive returned>, or spell=<its Spell object>."; TypeError "notch_spell `spell_id` must be a string; got
  <type>." and, for a str given as `spell`, one that names `spell_id=`; ValueError "notch_spell: version '<id>' is
  not owned by this conduit's Spellbook. ..." (remedy: notch through the conduit of the Spellbook that owns it, or
  stage the class on this index with bind_inactive) and "notch_spell: version '<id>' belongs to another SpellIndex,
  not the one passed. ..." (remedy: pass `conduit.get_spell_by_id('<id>').spell_index`, or move the version with
  add_to_spell_index first). A refusal before the transaction changes nothing; one inside the window (another
  operation moved the target after the first check) ends the transaction as failed, and the Spellbook is never
  called.
  EVIDENCE: `src/melder/aether/conduit/conduit.py:Conduit._resolve_notch_target` and `Conduit._owned_notch_target`.
""",
     """  `spell` or `spell_id`, not both." and "notch_spell needs a spell: pass spell_id=<the spell_id bind or
  bind_inactive returned>, or spell=<its Spell object>."; TypeError "notch_spell `spell_id` must be a string; got
  <type>." and, for a str given as `spell`, one that names `spell_id=`; ValueError "notch_spell: spell_id '<id>' is
  not owned by this conduit's Spellbook. ..." (remedy: notch through the conduit of the Spellbook that owns it, or
  stage the class on this index with bind_inactive, which returns the spell_id to pass) and "notch_spell: spell_id
  '<id>' belongs to another SpellIndex, not the one passed. ..." (remedy: pass
  `conduit.get_spell_by_id('<id>').spell_index`, or move it with add_to_spell_index first). A refusal before the
  transaction changes nothing; one inside the window (another operation moved the target after the first check)
  ends the transaction as failed, and the Spellbook is never called.
  EVIDENCE: `src/melder/aether/conduit/conduit.py:Conduit._check_spell_argument` and `Conduit._owned_notch_target`.
- `Conduit.add_to_spell_index` and `remove_from_spell_index` refuse before anything starts (0.2.8249): the same
  argument refusals worded for the verb ("<verb> accepts either `spell` or `spell_id`, not both.", "<verb> needs a
  spell: ...", the two TypeErrors) and ValueError "<verb>: spell_id '<id>' is not owned by this conduit's
  Spellbook. Call <verb> through the conduit of the Spellbook that owns it." Past that the Spellbook refuses as it
  always did, inside the window (RuntimeError; the transaction ends as failed and nothing moves): a spell another
  Book owns, an active spell ("... is active in its index; notch away from it before moving it."), a target index
  the Book does not own (add), a spell outside the source index or its only member (remove; "... use cleanup_spell
  to dispose it instead."). Until 0.2.8249 neither verb could be called from public code, since no public call
  returns a parked spell's Spell object, and their docstrings said the Spellbook admits the transaction.
  EVIDENCE: `src/melder/aether/conduit/conduit.py:Conduit._resolve_spell_to_move`, `Conduit._owned_spell_by_id`,
  `src/melder/aether/spellbook/spellbook.py:Spellbook._apply_add_to_index` and
  `Spellbook._apply_remove_from_index`.
"""),
    ("""- A notch to the Spell `get_spell_by_id` or `find_spell_by_id` returns for a parked id is a silent no-op, by their
  contract: they answer a parked id with the index's active member. Name a parked version by `spell_id=`.
""",
     """- A notch to the Spell `get_spell_by_id` or `find_spell_by_id` returns for a parked spell_id is a silent no-op, by
  their contract: they answer a parked spell_id with the index's active member. Name a parked version by `spell_id=`.
"""),
    # 6. C1 Code Map: conduit.py remeasured.
    ("""- path: `src/melder/aether/conduit/conduit.py`
  start_line: 1
  end_line: 7612
  loc: 7612
  verified_at: 2026-10-16T13:51:54Z
""",
     """- path: `src/melder/aether/conduit/conduit.py`
  start_line: 1
  end_line: 7784
  loc: 7784
  verified_at: """ + NOW + """
"""),
    ("""    `notch_spell` names its target by `spell_id=` or `spell=` and checks it before and inside its transaction
    (0.2.8249).
""",
     """    `notch_spell` names its target by `spell_id=` or `spell=` and checks it before and inside its transaction,
    and `add_to_spell_index` / `remove_from_spell_index` take `spell_id=` too (0.2.8249).
"""),
    # 7. Context / Handoff Summary: the lane's entry.
    ("""2026-10-16 public notch target (0.2.8249): `Conduit.notch_spell` takes `spell_id=` - the id `bind` or `bind_inactive`
returned - beside `spell=`, exactly one, and resolves it inside the call to the exact version the Book owns, active
or parked (owner ruling, option A: "just use the private version if its inside the public call thats
reasonable"), so the stage -> notch -> meld loop runs on public calls.""",
     """2026-10-16 public notch target (0.2.8249): `Conduit.notch_spell` takes `spell_id=` - the spell_id `bind` or
`bind_inactive` returned - beside `spell=`, exactly one, and resolves it inside the call to the exact version the
Book owns, active or parked (owner ruling, option A: "just use the private version if its inside the public call
thats reasonable"), so the stage -> notch -> meld loop runs on public calls."""),
    ("""which had drifted 29 lines above the method since earlier lanes. Open for the owner: whether `add_to_spell_index`
and `remove_from_spell_index` take the same keyword.
""",
     """which had drifted 29 lines above the method since earlier lanes. On the owner's extension `add_to_spell_index` and
`remove_from_spell_index` take `spell_id=` the same way and their docstrings say the conduit admits the
transaction; the same sections and a fourth failure mode carry it, the conduit.py citations and code-map extent are
remeasured (the file grew 172 lines), and this lane's text says spell_id, as the owner asked, not "version id".
"""),
]


def main() -> None:
    """Apply every edit; refuse unless each matches exactly once."""
    text = DOC.read_text(encoding="utf-8")
    assert "\r\n" not in text
    for old, new in EDITS:
        count = text.count(old)
        assert count == 1, (count, old[:80])
        text = text.replace(old, new, 1)
    DOC.write_text(text, encoding="utf-8")
    long = [i + 1 for i, line in enumerate(text.split("\n")) if len(line) > 120]
    print("ok; lines over 120:", long[:20])


if __name__ == "__main__":
    main()
