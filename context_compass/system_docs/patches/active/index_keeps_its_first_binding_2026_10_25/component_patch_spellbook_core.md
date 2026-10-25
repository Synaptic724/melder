# component_patch_spellbook_core

## Metadata
- Patch ID: index_keeps_its_first_binding_2026_10_25
- Component: Spellbook Core (Binding and Conjure), with its CachingSystem
- Status: draft
- Owner: Mark
- Author: melder_1 (synaptic_python_developer)
- Created: 2026-10-25T09:13:34Z
- Updated: 2026-10-25T09:13:34Z

## Component Purpose and Boundary
- Current boundary: the Book stages, moves and notches versions of its indexes without regard to how they are bound;
  the notch repoints the frame claim of the incoming version's key unconditionally, after the park and promotion.
- Target boundary: the Book admits a version onto an index only when the index admits it (`check_admits`), checked
  before anything is registered or moved, and the notch moves the index's address claim by compare-and-set before the
  park, refusing an address another spell holds.

## Before/After Behavior Summary
- `bind_inactive`. Before: Bind built the version and a fresh index; the spell_id collision check; the hooks
  (`_add_hooks_to_spell`); the posture check; registration (`_inactive_spells`, `_spell_ids`, the owner stamp when
  conjured); then `_apply_add_to_index` folded the version onto the caller's index and refused another Book's index
  there - after registration, so the version stayed parked in this Book under its fresh index and a retry was refused
  as a spell_id collision. No binding check. After: right after the collision check, before the hooks and
  registration, `spell_index.check_cleaned()`, the ownership check (`spell_index.selected_spell_id in
  self._spell_ids`, RuntimeError "bind_inactive: target index <id> is not owned by this spellbook; ..."), then
  `spell_index.check_admits(new_spell, verb="bind_inactive")`. Each raises while `registration_started` is False, so
  the handler retires the unpublished Spell and its fresh index (`Bind._cleanup_unpublished_spell`), as for a
  collision. Ownership comes first: for another Book's index the binding is moot. The docstring states the rule
  and the refusals; its stale "all four are part of a managed spell's id" says they are settings of the spell, not
  part of its spell_id (0.2.8254).
- `_apply_add_to_index`. After the existing checks (owned, parked, the same index a no-op, the target owned):
  `target_index.check_admits(spell, verb="add_to_spell_index")` before the move. On `bind_inactive`'s path it runs
  again and passes.
- `_apply_notch`. Before: under the Book lock, park the outgoing version and clean its creation context, promote the
  incoming one, `spell_index.update(new_id)`, then `update_lookup(spell._key, new_id)`, which set the claim
  whoever held it. After: under the Book lock, after the no-op return for the active version, read the claim's holder
  (`get_lookup`), then `repoint_lookup(spell._key, new_id, from_spell_id=<the outgoing version's spell_id, or None>)`.
  A holder returned is refused: RuntimeError, logged, nothing moved. Then the park and the promotion, as before; if
  either raises, the claim is put back to its holder before the error propagates. `update_lookup` is no longer
  called. The rest is unchanged.
- `_notch_spell`. Unchanged code: a seam refusal raises before its `try`, so no reversal runs, `Conduit.notch_spell`
  ends the transaction as failed and no borrower fan-out runs. Its docstring names the refusal.
- `_revert_refused_notch`. The branch `if refused._key != restored._key: self._restore_binding_key(...)` goes: every
  version of an index shares its key, and the seam run back toward the restored version moves the claim back by the
  same compare-and-set. The branch without an active version (`_revert_refused_activation`, then
  `_restore_binding_key`) stays.
- `_apply_remove_from_index`. The minted index is `SpellIndex.for_binding(spell_id, spellframe=spell.spellframe,
  spell_name=spell.spell_name, binding_name=spell.binding_name)`: the split version keeps its binding, its source
  index's, so `add_to_spell_index` moves it back and its index goes active once its address is free.
- CachingSystem: `CACHE_VERSION_HISTORY` gains 24, "spell_index_keeps_its_binding", with the comment block's entry:
  bundles written by worlds that could hold an index under two bindings are retired (the owner's call 1); a release
  change cold-starts them anyway (generation 9).

## Interface Deltas
- Inputs: none; every verb keeps its signature.
- Outputs: none.
- Error semantics: `bind_inactive` raises ValueError (another binding) and RuntimeError (another Book's index) before
  registering anything; `add_to_spell_index` raises ValueError (another binding) before moving anything;
  `notch_spell` raises RuntimeError naming the holder - "notch_spell refused: the address of SpellIndex <id> - <its
  binding> - is held by spell_id '<holder>', ..." - with the remedy for this Book's other index (move the version back
  with `add_to_spell_index` and notch there, or dispose that index's versions first) or another Book's spell (notch
  once it is disposed, or bind the class as a new spell at another address).

## State and Lifecycle Deltas
- Owned state changes: none in the Book.
- Lifecycle/cleanup changes: none. Book teardown's release by key now always meets the index's one claim, held by its
  active version.

## Failure Mode Deltas
- New failure mode: the refusals above.
- Removed failure modes: C5 (a notch across addresses moved the index's address and left the parked version holding the
  old one); C7 (a split version notched active took the address its source index's active version held: two active
  spells at one address); the cross-Book take (a notch took another Book's address, and its teardown later freed it
  while the other spell still served it); T4 (a parked version's claim outlived its Book); the foreign-index staging
  that left the version registered.
- Changed failure mode: a never-compiled split version notched while its address is taken is refused for the taken
  address (RuntimeError) instead of as a failed structural check (SpellbookValidationError).

## Dependency and Ordering Constraints
1. `SpellIndex.check_admits` and `SpellIndex.for_binding` (component_patch_binding_pipeline).
2. `AethericFrame.repoint_lookup` (component_patch_aetheric_frame_services), called under the Book lock - the order
   `update_lookup` had.
3. Inside the held `notch` window: the Book, the acting conduit, the conduits linked to it and the binding key sealed
   EXCLUSIVE, so no admitted operation of this frame moves the claim between the holder read and the compare-and-set.

## Validation Expectations
- tests/component/melder/spellbook/test_spellbook_component_index_keeps_its_first_binding.py: the admitted stagings,
  the three way-in refusals, the foreign index registering nothing, the add refusal, the notch keeping its address,
  the two C7 refusals (compiled and never compiled), the split version going active once free, the cross-Book refusal.
- The suites with the staging tests rewritten; the notch-refusal tests of 0.2.8262 (a shared key) unchanged.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none.

## Context / Handoff Summary
- What changed: the Book's way-in checks, the notch's claim move and refusal, the minted index's binding, the cache
  generation.
- Remaining risks: tests staging under other bindings; a notch path that parks before it checks its target (backlog).
- Next entrypoint: code_description_patch_spellbook_core.md.
