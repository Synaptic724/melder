"""Bring src_components to the owner's extension (index moves by spell_id) and the spell_id wording.

Run from context_compass/:  python docs_extension_src_components.py <NOW>
Each replacement must match exactly once; the file stays LF.
"""
import pathlib
import sys

NOW = sys.argv[1]
DOC = pathlib.Path("system_docs/src_components.md")

INDEX_MOVE_FLOW = """### Flow: Conduit Index Moves by spell_id -> Spellbook Seams
1. `Conduit.add_to_spell_index(spell_id=..., target_index=...)` or `Conduit.remove_from_spell_index(spell_id=...,
   source_index=...)` (or `spell=`): `check_cleaned`, the dynamic gate (RuntimeError), the owning-Book check
   (RuntimeError).
2. `Conduit._resolve_spell_to_move` -> `Conduit._check_spell_argument`: exactly one of `spell` and `spell_id`
   (ValueError), a str spell_id and no str `spell` (TypeError), each message naming the verb; then, for a spell_id,
   `Conduit._owned_spell_by_id` -> `Spellbook._get_owned_spell(spell_id)` (Book lock) -> the owned spell, else
   ValueError; a `spell` passes through as given (0.2.8249).
3. Metadata from the resolved Spell (add also reads the spell's source index before the move: whether the move
   empties it, and its members); `start_transaction(ADD_TO_INDEX)` or `start_transaction(REMOVE_FROM_INDEX)`.
4. Inside the window: `Spellbook._add_to_spell_index` -> `Spellbook._apply_add_to_index`, or
   `Spellbook._remove_from_spell_index` -> `Spellbook._apply_remove_from_index`; each seam refuses first
   (RuntimeError: another Book's spell, an active spell; add: a target index the Book does not own; remove: a spell
   outside the source index, or its only member). Any raise -> `end_transaction(success=False)` and the raise
   propagates.
5. `end_transaction(success=True)`; the index-link fan-out - add: `ConduitWard._emit_index_member_added` on the
   target, then `_emit_index_destroy` (the move emptied the source) or `_emit_index_member_removed` on the source;
   remove: `_emit_index_member_removed` - and the moved Spell is returned.

"""

EDITS = [
    # Spellbook Core: the three mediator acquisitions, remeasured.
    ("  - src/melder/aether/conduit/conduit.py:5708, 5896, 5976 (notch/add/remove\n",
     "  - src/melder/aether/conduit/conduit.py:5708, 6041, 6148 (notch/add/remove\n"),
    # Conduit Runtime: the notch paragraph in spell_id wording, and the index moves after it.
    ("""names the version to make active by `spell_id` - the id `bind` or `bind_inactive` returned - or by its Spell,
exactly one. `_resolve_notch_target` refuses both or neither (ValueError) and a non-str id or a str given as `spell`
(TypeError), then hands the id to `_owned_notch_target`, which resolves it through the Book's `_get_owned_spell` (the
exact owned version, active or parked; the Book lock alone) and refuses, with a ValueError naming the version and
the remedy, a version the Book does not own, a `spell` that is not the object the Book owns under that id, and a
version whose `spell_index` is not the index passed.""",
     """names the version to make active by `spell_id` - the spell_id `bind` or `bind_inactive` returned - or by its
Spell, exactly one. `_resolve_notch_target` runs the shared `_check_spell_argument`, which refuses both or neither
(ValueError) and a non-str spell_id or a str given as `spell` (TypeError), then hands the spell_id to
`_owned_notch_target`, which resolves it through the Book's `_get_owned_spell` (the exact owned version, active or
parked; the Book lock alone) and refuses, with a ValueError naming its spell_id and the remedy, a version the Book
does not own, a `spell` that is not the object the Book owns under that spell_id, and a version whose `spell_index`
is not the index passed."""),
    ("""did). `get_spell_by_id` keeps answering a parked id with the index's active member.
EVIDENCE: `src/melder/aether/conduit/conduit.py:Conduit.notch_spell`, `Conduit._resolve_notch_target`,
`Conduit._owned_notch_target` and `src/melder/aether/spellbook/spellbook.py:Spellbook._get_owned_spell`.
""",
     """did). `get_spell_by_id` keeps answering a parked spell_id with the index's active member.
EVIDENCE: `src/melder/aether/conduit/conduit.py:Conduit.notch_spell`, `Conduit._resolve_notch_target`,
`Conduit._owned_notch_target` and `src/melder/aether/spellbook/spellbook.py:Spellbook._get_owned_spell`.

Index moves by spell_id (2026-10-16, 0.2.8249, the owner's extension): `add_to_spell_index(*, spell=None,
spell_id=None, target_index)` and `remove_from_spell_index(*, spell=None, spell_id=None, source_index)` name the
parked spell they move the same two ways. After the dynamic gate and the Book check, `_resolve_spell_to_move` runs
`_check_spell_argument` (the notch's argument rules, each message naming the verb) and resolves a spell_id through
`_owned_spell_by_id` - the Book's `_get_owned_spell`, with a ValueError naming the spell_id and the remedy when the
Book owns none - before the transaction starts; a `spell` passes through as given. The seams keep their own
refusals (RuntimeError inside the window, the transaction ended as failed): another Book's spell, an active spell,
a target index the Book does not own (add), a spell outside the source index or its only member (remove). Both
docstrings now say the conduit admits the transaction, and remove's no longer says that removing the active member
leaves the index selecting a non-member - the seam refuses an active member.
EVIDENCE: `src/melder/aether/conduit/conduit.py:Conduit.add_to_spell_index`, `Conduit.remove_from_spell_index`,
`Conduit._resolve_spell_to_move`, `Conduit._check_spell_argument`, `Conduit._owned_spell_by_id` and
`src/melder/aether/spellbook/spellbook.py:Spellbook._apply_add_to_index`, `Spellbook._apply_remove_from_index`.
"""),
    # Conduit Runtime: Responsibilities, Inputs, Outputs.
    ("""  change-control transactions; a notch resolves and checks its target by version id (0.2.8249; Subcomponent:
  SpellIndex Mutation Surface).
""",
     """  change-control transactions; a notch resolves and checks its target by spell_id, and the index moves resolve
  theirs the same way (0.2.8249; Subcomponent: SpellIndex Mutation Surface).
"""),
    ("- A SpellIndex and the version to make active - its id or its Spell - for `notch_spell(...)` (0.2.8249).\n",
     """- A SpellIndex and the version to make active - its spell_id or its Spell - for `notch_spell(...)`, and a parked
  spell - its spell_id or its Spell - with the target or source index for `add_to_spell_index(...)` /
  `remove_from_spell_index(...)` (0.2.8249).
"""),
    ("- The now-active Spell from `notch_spell(...)`.\n",
     "- The now-active Spell from `notch_spell(...)`; the moved Spell from `add_to_spell_index(...)` /\n"
     "  `remove_from_spell_index(...)`.\n"),
    # Conduit Runtime: Failure Modes.
    ("""- ValueError or TypeError from `notch_spell` for its target (0.2.8249): both or neither of `spell` and `spell_id`,
  a version the Book does not own and a version of another index are ValueErrors naming the version and the
  remedy; a non-str id and a str given as `spell` are TypeErrors.""",
     """- ValueError or TypeError from `notch_spell` for its target (0.2.8249): both or neither of `spell` and `spell_id`,
  a version the Book does not own and a version of another index are ValueErrors naming its spell_id and the
  remedy; a non-str spell_id and a str given as `spell` are TypeErrors."""),
    ("""  accepted, corrupting the indexes or leaving the index with no active version (`src_architecture`, Failure
  Modes and Error Paths).
""",
     """  accepted, corrupting the indexes or leaving the index with no active version (`src_architecture`, Failure
  Modes and Error Paths).
- ValueError or TypeError from `add_to_spell_index` / `remove_from_spell_index` before anything starts (0.2.8249):
  the same argument rules worded for the verb, and a spell_id the Book does not own; their seams still raise
  RuntimeError inside the window (another Book's spell, an active spell, a target index the Book does not own, a
  spell outside the source index or its only member), the transaction ended as failed and nothing moved.
"""),
    # SpellIndex Mutation Surface: Contract/Interface.
    ("""- `Conduit.add_to_spell_index(spell=, target_index=)` opens `add_to_index` at
  `src/melder/aether/conduit/conduit.py:5916`, then calls `Spellbook._add_to_spell_index(...)`, which
  delegates the move-in to `_apply_add_to_index(...)`.
- `Conduit.remove_from_spell_index(spell=, source_index=)` opens
  `remove_from_index` at `src/melder/aether/conduit/conduit.py:5987`, then calls
""",
     """- `Conduit.add_to_spell_index(spell_id= | spell=, target_index=)` resolves a spell_id to the spell the Book owns
  (`_resolve_spell_to_move`; 0.2.8249), opens `add_to_index` at
  `src/melder/aether/conduit/conduit.py:6061`, then calls `Spellbook._add_to_spell_index(...)`, which
  delegates the move-in to `_apply_add_to_index(...)`.
- `Conduit.remove_from_spell_index(spell_id= | spell=, source_index=)` resolves it the same way, opens
  `remove_from_index` at `src/melder/aether/conduit/conduit.py:6159`, then calls
"""),
    ("""  DO NOT TRUST THE ADD AND REMOVE DOCSTRINGS HERE. Both say "Delegates to the
  owning Spellbook, WHICH ADMITS the [...] change-control transaction". That is
  false, and both methods call `mediator.start_transaction(...)` a few lines
  further down. `src/melder/aether/spellbook/spellbook.py:3811-3813` states it correctly.
  `notch_spell`'s docstring said the same until 0.2.8249 and now says the conduit
  admits the transaction. Raised on TASK-2026-08-02-stale-source-docstrings.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:5622, 5861, 5939 (public verbs)
  - src/melder/aether/conduit/conduit.py:5753, 5806 (`_resolve_notch_target`, `_owned_notch_target`)
""",
     """  THE ADD AND REMOVE DOCSTRINGS WERE WRONG UNTIL 0.2.8249. Both said "Delegates to
  the owning Spellbook, WHICH ADMITS the [...] change-control transaction", while
  both methods call `mediator.start_transaction(...)` a few lines further down;
  `src/melder/aether/spellbook/spellbook.py:3811-3813` states it correctly.
  `notch_spell`'s docstring said the same. Since 0.2.8249 all three say the conduit
  admits the transaction (raised on TASK-2026-08-02-stale-source-docstrings).
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:5622, 5971, 6084 (public verbs)
  - src/melder/aether/conduit/conduit.py:5753, 5791, 5846, 5897, 5932 (`_resolve_notch_target`,
    `_owned_notch_target`, `_check_spell_argument`, `_owned_spell_by_id`, `_resolve_spell_to_move`)
"""),
    # SpellIndex Mutation Surface: Behavior.
    ("""- A notch's target (0.2.8249): exactly one of `spell_id` and `spell`; the id resolves through
  `Spellbook._get_owned_spell` to the exact owned version, active or parked. A version the Book does not own, a
  `spell` that is not the object it owns under that id, and a version of another index are refused (ValueError)""",
     """- A notch's target (0.2.8249): exactly one of `spell_id` and `spell`; the spell_id resolves through
  `Spellbook._get_owned_spell` to the exact owned version, active or parked. A version the Book does not own, a
  `spell` that is not the object it owns under that spell_id, and a version of another index are refused (ValueError)"""),
    ("""  checks the incoming one, so it must only ever be handed a parked member of the index it is notching.
""",
     """  checks the incoming one, so it must only ever be handed a parked member of the index it is notching.
- The index moves' spell (0.2.8249): exactly one of `spell_id` and `spell` (`_check_spell_argument`); a spell_id
  resolves through `_owned_spell_by_id` (`_get_owned_spell`), and one the Book does not own is refused before the
  transaction. Everything else is the seams' to refuse inside the window, as before (RuntimeError: another Book's
  spell, an active spell; add: a target index the Book does not own; remove: a spell outside the source index, or
  its only member).
"""),
    # Method-Level Call Flows: the notch flow's argument step, and a new flow for the index moves.
    ("""2. `Conduit._resolve_notch_target`: exactly one of `spell` and `spell_id` (ValueError), a str id and no str `spell`
   (TypeError); then""",
     """2. `Conduit._resolve_notch_target` -> `Conduit._check_spell_argument`: exactly one of `spell` and `spell_id`
   (ValueError), a str spell_id and no str `spell` (TypeError); then"""),
    ("""   `ConduitWard._emit_index_notch(spell_index, outgoing_id, spell.spell_id)`; returns the now-active Spell.

### Flow: SpellSpace Scoped Meld
""",
     """   `ConduitWard._emit_index_notch(spell_index, outgoing_id, spell.spell_id)`; returns the now-active Spell.

""" + INDEX_MOVE_FLOW + """### Flow: SpellSpace Scoped Meld
"""),
    # C1 Code Map (Core): conduit.py remeasured.
    ("""- path: `src/melder/aether/conduit/conduit.py`
  start_line: 1
  end_line: 7612
  loc: 7612
  verified_at: 2026-10-16T13:53:05Z
""",
     """- path: `src/melder/aether/conduit/conduit.py`
  start_line: 1
  end_line: 7784
  loc: 7784
  verified_at: """ + NOW + """
"""),
    # Context / Handoff Summary: the lane's entry.
    ("""by id. Spellbook Core's mediator citations and the Conduit Runtime's `link` TypeError citation (5296-5298, stale
since earlier lanes) point at their code again, and the code map remeasures conduit.py. The seam docstrings in
spellbook.py (`_notch_spell`, `_apply_notch`) still say the notch claims the Book INTENT.
""",
     """by spell_id. Spellbook Core's mediator citations and the Conduit Runtime's `link` TypeError citation (5296-5298,
stale since earlier lanes) point at their code again, and the code map remeasures conduit.py. The seam docstrings
in spellbook.py (`_notch_spell`, `_apply_notch`) still say the notch claims the Book INTENT. On the owner's
extension the Conduit Runtime and the SpellIndex Mutation Surface carry `spell_id=` on `add_to_spell_index` /
`remove_from_spell_index` (the shared argument check, `_owned_spell_by_id`, the seams' refusals kept, the corrected
docstrings - the surface's warning about them is resolved), a new flow follows an index move by spell_id, the
conduit.py citations and code-map extent are remeasured again (the file grew 172 lines), and this lane's text says
spell_id, as the owner asked, not "version id".
"""),
]


def main() -> None:
    """Apply every edit; refuse unless each matches exactly once."""
    text = DOC.read_text(encoding="utf-8")
    assert "\r\n" not in text
    for old, new in EDITS:
        count = text.count(old)
        assert count == 1, (count, old[:90])
        text = text.replace(old, new, 1)
    DOC.write_text(text, encoding="utf-8")
    print("ok; lines:", len(text.split("\n")) - 1)


if __name__ == "__main__":
    main()
