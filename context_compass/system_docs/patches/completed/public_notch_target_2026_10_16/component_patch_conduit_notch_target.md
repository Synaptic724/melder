# Component patch: Conduit - the public notch target

## Metadata
- Patch ID: public_notch_target_2026_10_16
- Component: `Conduit.notch_spell` (src/melder/aether/conduit/conduit.py)
- Writer: melder_0 (synaptic_python_developer)
- Created: 2026-10-16T12:50:00Z
- Status: built as patched (0.2.8249); promoted into src_components (Conduit Runtime, SpellIndex Mutation Surface,
  the notch flow) and src_architecture; its refusals reworded to spell_id on the owner's extension; archived

## Before (0.2.8248)
- `notch_spell(self, *, spell_index: Any, spell: Any, change_reason=...)`: dynamic gate (RuntimeError on an
  automatic frame), owning-Book check (RuntimeError), then the metadata (`spell_index._id`, `spell.spell_id`,
  `spell._key`, the lineage gate ops), the outgoing id read from `spell_index.selected_spell_id`,
  `mediator.start_transaction(NOTCH)`, `self._spellbook._notch_spell(spell_index=, spell=, change_reason=)` inside
  a `try` that ends the transaction as failed and re-raises, `end_transaction(success=True)`, then - when the
  outgoing id differs from the target's - `_deactivate_borrowed_spell(outgoing_id)` and
  `_conduit_ward._emit_index_notch(spell_index, outgoing_id, spell.spell_id)`; returns the seam's result.
- Nothing checks the target. The only public ways to obtain a Spell for a parked id return the index's live spell,
  so the public form is a silent no-op (C1); a parked version of another index is accepted and corrupts both indexes
  (C3); the active version of another index, or another Book's version, raises RuntimeError "Owned spell_id not
  parked for reactivation" after the index's active version was parked (C4, C5).

## After
- Signature: `notch_spell(self, *, spell_index: Any, spell: Any = None, spell_id: Optional[str] = None,
  change_reason=...)`. Order of work: the dynamic gate and the owning-Book check (unchanged), then
  `spell = self._resolve_notch_target(spell_index=spell_index, spell=spell, spell_id=spell_id)`, then the unchanged
  metadata, outgoing-id read and admission; inside the `try`,
  `self._owned_notch_target(spell_index=spell_index, spell_id=spell.spell_id, spell=spell)` runs before
  `_notch_spell`; the rest is unchanged.
- `_resolve_notch_target(*, spell_index, spell, spell_id) -> Spell`:
  - both given: ValueError "notch_spell accepts either `spell` or `spell_id`, not both.";
  - neither: ValueError naming both keywords and where an id comes from (`bind`, `bind_inactive`);
  - `spell_id` not a str: TypeError "notch_spell `spell_id` must be a string; got <type>.";
  - `spell` a str: TypeError saying `spell` takes a Spell and an id goes in `spell_id=`;
  - then `_owned_notch_target(spell_index=, spell_id=<the id, or spell.spell_id>, spell=<None, or the object>)`,
    whose result it returns.
- `_owned_notch_target(*, spell_index, spell_id, spell) -> Spell` (planned as `_refuse_foreign_notch_target`;
  one helper resolves and checks, so each refusal text exists once):
  - `owned = self._spellbook._get_owned_spell(spell_id)`; None, or not the very `spell` object when one was
    given -> ValueError "notch_spell: version '<id>' is not owned by this conduit's Spellbook. ..." (remedy:
    notch through the conduit of the Spellbook that owns it, or stage the class on this index with
    bind_inactive, which returns the id to pass);
  - `owned.spell_index is not spell_index` -> ValueError "notch_spell: version '<id>' belongs to another SpellIndex,
    not the one passed. ..." (remedy: pass the version's own index - `conduit.get_spell_by_id(<id>).spell_index` -
    or move it onto this index with add_to_spell_index first);
  - returns `owned`.
- The docstring states the exactly-one rule, the resolution, both checks and when they run, the no-op, the return
  value and every raise.

Amendment (owner, 2026-10-16): the refusals say spell_id - "notch_spell: spell_id '<id>' is not owned ...",
"... belongs to another SpellIndex ...", "notch_spell needs a spell: pass spell_id=<the spell_id bind or
bind_inactive returned>, ..." - and the argument checks are shared with the index moves
(component_patch_conduit_index_move_target.md).

## Interface deltas
- `spell` gains a default (None); `spell_id: Optional[str] = None` is new. All arguments stay keyword-only.
- Raises: ValueError and TypeError as above (new); RuntimeError unchanged for an automatic frame, a cleaned conduit
  and a conduit without a Book; whatever the seam and the transaction raised before.
- Returns: unchanged (the seam's result - the now-active Spell); the docstring now says so.

## State and failure deltas
- A refusal before admission mutates nothing and starts no transaction (no seal, no gate freeze, no metadata).
- A refusal inside the window ends the transaction as failed (`end_transaction(success=False)`), whose `on_end`
  reopens the frozen gates; the seam is never called.
- C3, C4 and C5 become ValueError refusals with both indexes intact; C1 is no longer the only public form.

## Dependency and ordering
- `_get_owned_spell` takes the Book lock alone (cold path), never under a conduit, ward or registry lock held here;
  the in-window call runs while the transaction holds its claims, which are mediator scope claims, not locks the
  Book lock nests under. The identity reads (`spell.spell_index`, `is`) take no lock. No new lock edge.
- The internal callers - `RestoreEngine._enforce_selections` and the graft runner's selection adoption - resolve
  their target with `_get_owned_spell` on the Book whose conduit they notch through, staged on the index they pass,
  so both checks hold for them; their suites run as regression evidence.

## Validation expectations
- Unit (new file tests/unit/melder/aether/conduit/test_conduit_notch_target.py, the stubbed Book of the conduit
  unit conftest): by id the Book's `_get_owned_spell` is asked and the resolved Spell reaches `_notch_spell` and the
  metadata; by object an owned member passes through unchanged; both, neither, a non-str id, a str `spell`, an
  unknown id, another index's version (by id and by object) and a Spell the Book does not own are refused with no
  transaction started and the seam not called; a target moved to another index after the first check is refused
  inside the window, the transaction ended as failed and the seam not called; an automatic conduit still raises the
  dynamic-mode RuntimeError.
- Integration (new file tests/integration/melder/aether/conduit/test_notch_spell_by_id_integration.py): notch by id
  promotes a version staged after conjure and one staged before conjure and the meld builds it; notch back by id
  restores the first version; a notch to the active id is a no-op; C3, C4 and C5 raise ValueError with both indexes'
  selection, members and melds intact; an index-linked borrower follows a notch made by id.
- Unchanged and green: the notch lifecycle, op-guard, index-link and race integration tests, the S8 parked tests,
  the crystallizer restore/membership/graft suites, the conduit and spellbook unit and component trees, GIL off and on.
- Acceptance: a probe runs the README loop as written (stage, notch by id, meld, notch back) on public calls only.
