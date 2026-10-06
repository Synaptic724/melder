# component_patch_devops_control_plane

## Metadata
- Patch ID: rebind_after_first_meld_2026_10_03
- Status: promoted (src_architecture, src_components, graph at 0.2.8219); archived 2026-10-03T21:08:00Z
- Owner: user (agent fable_1)
- Created: 2026-10-03T20:12:00Z
- Updated: 2026-10-03T21:08:00Z

<!-- BEGIN ENTRY: "ConduitResolutionState: verdict retirement" -->
## Before
- The state holds `_spell_validity` and `_root_validity` keyed by version id. Verdicts are written by Phase 6
  (`bulk_set_spell_validity` / `bulk_set_root_validity`), by the visibility-failure recorder and by
  `Meld._force_resolution_revalidation` (gated). Nothing retires one id's verdicts; only `cleanup()` clears
  the maps, with the conduit.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/conduit_resolution_state.py:137-230
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/conduit_resolution_state.py:271-325

## After
- `forget_spell(spell_id, *, change_reason=None) -> bool` pops both verdicts for the id under the state lock,
  marks the state dirty with `change_reason` only when a verdict existed, and returns whether one did. It
  raises ValueError on an empty id and RuntimeError on a cleaned state. It does not call the RiskManager:
  forgetting is a change of scope, not of verdict; a callback would mark `spell:<id>` or the lineage risky in
  conduits that never register the lineage again (a peer that resolved the id through a contract), and the
  owner-scoped `RiskManager.register_spell` recomputes risk from the live verdict on the rebind.

## Interface Deltas
- One new internal verb; nothing public.

## State / Failure Deltas
- After `forget_spell`, `get_spell_validity(id)` and `get_root_validity(id)` answer `initial_validity`
  (unknown) again; `is_dirty()` is True and `last_change_reason` is the supplied reason when something was
  forgotten; diagnostics and `last_validated_at` are unchanged.

## Validation Expectations
- Unit: spell-only, root-only and both verdicts forgotten; return value True/False; dirty + reason only on a
  hit; other ids untouched; no `on_resolution_validity_change` call on a mock RiskManager; empty id raises
  ValueError; cleaned state raises RuntimeError.
<!-- END ENTRY: "ConduitResolutionState: verdict retirement" -->

<!-- BEGIN ENTRY: "SpellSystemStates: unregister_index and register_index" -->
## Before
- `unregister_index` computes the impact closure, pops the lineage state, the spell-id index, the dirty entry,
  the topology, the owner maps and the reverse edges, notifies the RiskManager with `SpellValidity.cleaned`
  (structural) and cleans the removed state. `_resolution_by_conduit_id` is never touched, so every conduit
  that resolved the id keeps its `valid` root/spell verdict for a definition that no longer exists.
- `register_index` creates or updates the lineage state, refreshes the spell-id index and the owner maps, and
  marks the state structurally gated (`register_or_rebind`) + dirty. A late bind then runs phases 1-4 eagerly
  and the state is valid before the first meld, so `Meld._gated_validation_required` is False, the structural
  rerun that would re-gate the conduit verdict never happens, and a verdict recorded for an earlier life of
  the same content-stable id is read as current.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:299-353
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:743-832
  - src/melder/aether/spellbook/spellbook.py:5360-5480
  - src/melder/aether/conduit/meld/meld.py:893-949
  - src/melder/aether/conduit/meld/meld.py:1208-1270

## After
- `unregister_index` calls `_forget_resolution_verdicts_locked(current_spell_id, change_reason=
  cleaned_up_spell)` inside its lock, in the main branch (after the owner maps, before the reverse edges) and
  in the "state missing" branch (for `spell_index.selected_spell_id`). The structural callback and the state
  cleanup are unchanged.
- `register_index` calls `_forget_resolution_verdicts_locked(current_id, change_reason=register_or_rebind)`
  inside its lock, right after refreshing the spell-id index and before the structural gate. A first-time id
  finds nothing; a rebind of the same class at the same address, a notch back to a member that was active
  before and a transfer re-registration each retire the version id's verdicts frame-wide.
- `forget_spell_resolution_verdicts(spell_id, *, change_reason=None) -> int` is the public form (takes the
  lock, raises RuntimeError when cleaned); `_forget_resolution_verdicts_locked` is the locked helper that
  visits `self._resolution_by_conduit_id.values()` and counts the states that held a verdict.
- The class docstring's Lifecycle paragraph states both axes of retirement and why.

## Interface Deltas
- Two new internal verbs; two existing verbs gain a side effect on the resolution axis; nothing public.

## State / Failure Deltas
- Invariant: an id with no registered lineage has no resolution verdict in any conduit of the frame; a freshly
  registered version id has none either. Per-conduit diagnostics are not pruned (Phase 6 replaces the
  snapshot wholesale on every pass, so a dead spell's diagnostic cannot outlive the next validation).
- Cost: O(number of conduit states) dict pops on bind and on removal; nothing on the meld path.

## Dependency / Ordering
- Lock order registry -> conduit state only; the helper runs no callback. `drop_conduit_resolution_state` and
  `cleanup` pop states under the same registry lock before cleaning them, so every state the helper visits is
  live.
- `Spellbook.cleanup_and_remove_spell` calls `unregister_index` first, then `RiskManager.unregister_spell`
  for the owner conduit, then releases the framewide lookup, then cleans the Spell - unchanged order; the
  rebind's `register_index` runs before `_register_spell_with_risk_manager`, which recomputes risk from the
  now-unknown verdict.

## Validation Expectations
- Unit: after `unregister_index`, a verdict set for the id in two conduit states is gone in both while other
  ids stay; the "state missing" branch forgets too; after `register_index` of an index whose selected id holds
  a verdict, the verdict is gone, and a first-time id leaves other verdicts alone; the structural RiskManager
  call pattern of the existing tests is unchanged (gated then cleaned, 2 calls); no
  `on_resolution_validity_change` call from the forgetting; the public verb returns the count and raises when
  cleaned.
- Integration (Melder-only fixture): the four-case probe 4/4; M1 replacement re-resolved with its own phase
  5-11 artifacts and a valid root verdict, old product alive; M3 a linked peer that melded the old definition
  melds the replacement with its override; M4 both products disposed by the scope's cleanup; M2/M2b dependents
  rebuilt (guards). Component: M5 the Book's validation flag True after the rebind, False after the
  revalidating meld.
<!-- END ENTRY: "SpellSystemStates: unregister_index and register_index" -->
