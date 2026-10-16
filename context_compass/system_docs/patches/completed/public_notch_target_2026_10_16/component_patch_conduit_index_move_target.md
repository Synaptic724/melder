# Component patch: Conduit - add_to_spell_index and remove_from_spell_index by spell_id

## Metadata
- Patch ID: public_notch_target_2026_10_16
- Component: `Conduit.add_to_spell_index`, `Conduit.remove_from_spell_index` (src/melder/aether/conduit/conduit.py)
- Writer: melder_0 (synaptic_python_developer)
- Created: 2026-10-16T15:09:19Z
- Status: built as patched (0.2.8249, the owner's extension); promoted into src_components (Conduit Runtime,
  SpellIndex Mutation Surface, the index-move flow), src_architecture, tests_components and tests_architecture;
  archived

## Before (0.2.8248, and 0.2.8249 until this extension)
- `add_to_spell_index(self, *, spell: Any, target_index: Any)`: dynamic gate (RuntimeError on an automatic frame),
  owning-Book check (RuntimeError), metadata from `spell.spell_id` and `spell._key`, the source lineage read before
  admission (`spell.spell_index`, whether the move empties it, its members), `start_transaction(ADD_TO_INDEX)`,
  `Spellbook._add_to_spell_index` inside a `try` that ends the transaction as failed and re-raises,
  `end_transaction(success=True)`, then the index-link fan-out (member added on the target; member removed, or the
  index destroyed, on the source).
- `remove_from_spell_index(self, *, spell: Any, source_index: Any)`: the same gates, metadata,
  `start_transaction(REMOVE_FROM_INDEX)`, `Spellbook._remove_from_spell_index`, end, fan-out (member removed).
- Both take only a Spell object and move only a spell parked in the Book: the seams raise RuntimeError for a spell
  another Book owns, for an active spell ("notch away from it before moving it") and - remove - for a spell outside
  `source_index` or its only member ("use cleanup_spell"); add - for a target index the Book does not own. No public
  call returns a parked spell's Spell object (`get_spell_by_id` answers a parked spell_id with the index's active
  spell), so neither verb can be used from public code.
- Both docstrings say the Spellbook admits the transaction; the conduit does. The remove docstring says removing the
  active member leaves the index selecting a non-member; the seam refuses an active member.

## After
- Signatures: `add_to_spell_index(self, *, spell: Any = None, spell_id: Optional[str] = None, target_index: Any)` and
  `remove_from_spell_index(self, *, spell: Any = None, spell_id: Optional[str] = None, source_index: Any)`. After the
  dynamic gate and the Book check: `spell = self._resolve_spell_to_move(verb=..., spell=spell, spell_id=spell_id)`;
  everything after it is unchanged and reads the resolved spell.
- `_check_spell_argument(*, verb, spell, spell_id) -> str`, shared with `_resolve_notch_target`:
  - both given: ValueError "<verb> accepts either `spell` or `spell_id`, not both.";
  - neither: ValueError "<verb> needs a spell: pass spell_id=<the spell_id bind or bind_inactive returned>, or
    spell=<its Spell object>.";
  - a non-str `spell_id`: TypeError "<verb> `spell_id` must be a string; got <type>.";
  - a str `spell`: TypeError "<verb> `spell` takes a Spell object; to name a spell by its spell_id, pass
    spell_id='<id>'.";
  - returns the spell_id to resolve (`spell_id`, or `spell.spell_id`).
- `_owned_spell_by_id(*, verb, spell_id) -> Spell`: `self._spellbook._get_owned_spell(spell_id)`; None ->
  ValueError "<verb>: spell_id '<id>' is not owned by this conduit's Spellbook. Call <verb> through the conduit of the
  Spellbook that owns it."
- `_resolve_spell_to_move(*, verb, spell, spell_id) -> Spell`: the argument check, then `_owned_spell_by_id` for a
  `spell_id`; a `spell` is returned as given (the seams check it as before).
- Docstrings: the conduit admits the transaction; name the spell by `spell_id` (the spell_id `bind` or
  `bind_inactive` returned) or `spell`; every refusal, the seams' included; remove: only a parked member is split
  out - the active one is refused, so notch away first - and the only member is refused (`cleanup_spell` disposes it).

## Interface deltas
- `spell` gains a default (None); `spell_id: Optional[str] = None` is new; all arguments stay keyword-only, so every
  existing call keeps working.
- Raises: ValueError and TypeError as above (new, before any transaction); the seams' RuntimeErrors unchanged;
  RuntimeError unchanged for an automatic frame, a cleaned conduit and a conduit without a Book.
- Returns: unchanged (the seam's result, the moved Spell).

## State and failure deltas
- A refusal by the argument check or `_owned_spell_by_id` starts nothing (no metadata, no transaction, no fan-out).
- A spell_id that resolves to an active spell, or (remove) to a spell outside `source_index`, reaches the seam and
  is refused there as `spell=` is: the transaction ends as failed and nothing moves.

## Dependency and ordering
- `_get_owned_spell` takes the Book lock alone (cold path) and releases it before admission; no new lock edge.
- The index-move tests that pass a Spell object (index lifecycle and depth, index-link follow, notch lifecycle, op
  guards, the crystallizer membership integration, the find-by-id component test) run unchanged as regression.

## Validation expectations
- Unit (new file tests/unit/melder/aether/conduit/test_conduit_index_move_target.py, the stubbed Book of the conduit
  unit conftest): for each verb, both, neither, a non-str spell_id and a str `spell` are refused before the Book is
  asked and before any transaction; an unknown spell_id is refused after `_get_owned_spell` answers None, nothing
  started; a resolved spell_id reaches the transaction metadata and the Book's entry; `spell=` is passed through
  without asking `_get_owned_spell`.
- Integration (new file tests/integration/melder/aether/conduit/test_index_moves_by_spell_id_integration.py): in a
  dynamic world, `add_to_spell_index(spell_id=..., target_index=...)` moves a parked spell onto another index and
  `remove_from_spell_index(spell_id=..., source_index=...)` splits a parked spell into a fresh index, each meldable
  after a notch to it; an unknown spell_id, both or neither are refused with the indexes intact; an active spell_id
  is refused by the seam with the indexes intact.
