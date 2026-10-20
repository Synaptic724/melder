# Component patch: the state vocabulary and register_index (meld_state_gate_2026_10_15)

## Metadata
- Patch ID: meld_state_gate_2026_10_15
- Components: SpellState, SpellSystemState, SpellSystemStates
  (`src/melder/aether/aetheric_frame/dev_ops/spell_system_states/`: `spell_state.py`, `spell_system_state.py`,
  `spell_system_states.py`)
- Status: active
- Owner: user; melder_1 (synaptic_python_developer) (patch, and writer of these three files)
- Created: 2026-10-15T21:00:00Z
- Updated: 2026-10-15T22:32:34Z

## Component purpose and boundary
- Current boundary: the three-axis state model - `SpellValidity` (the gate), `SpellState` flags (the explanation,
  each owned by the subsystem that sets it), `SpellStateChangeReason` (the last event) - and the frame registry that
  holds one `SpellSystemState` per lineage. Nothing in it can say that a lineage owes no resolution verdict.
- Target boundary: the explanation axis gains one flag that says so, written by the registration of the lineage's
  selected version; the gate axis and every existing flag keep their meaning.

## Before / after
- Before: a lineage whose selected version is resolvable=False carries the same flags as any other; `register_index`
  takes no capability.
- After:
  - `SpellState.non_resolvable` is appended after `transfer_in_progress` under a new "Capability" group: the selected
    version is a resolvable=False definition, kept for discovery and versioning, whose consumers receive the value by
    override; it owes no resolution verdict. Members are `auto()` values and flags are never persisted, so appending
    changes no existing value.
  - `SpellSystemState.update_flags(*, flags_to_add=None, flags_to_remove=None)`: under the state lock, adds then
    removes (the order `set_validity` uses), ignores None entries, and leaves validity, the change reason,
    `transitively_dirty` and `last_validated_at` alone. It publishes nothing: flag-only updates stay local, as
    `set_validity`'s contract already says. It returns whether the flag set changed.
  - `SpellSystemState._republish_validity()`: reads the validity under the state lock and publishes it to the
    attached RiskManager outside that lock, contained like `set_validity`'s publication; it changes nothing. The
    registry calls it when a flag that RiskManager reads changed while the validity did not.
  - `SpellSystemState.has_flag(flag) -> bool`: membership under the state lock, without copying the set.
  - `SpellSystemStates.register_index(spell_index, owner_spellbook_id=None, *, resolvable=None)`: inside the registry
    lock, after the state is found (or created) and its current id updated, and before `mark_structural_change`:
    `False` adds `non_resolvable`; `True` removes it; `None` removes it when the state is new or the index now selects
    a different version than the state tracked, and keeps it otherwise. Everything else is unchanged: the spell-id
    index, the verdict retirement, the owner index, the gate and the dirty set. When the write changed the flag
    and the lineage was already `gated` (so the gate publishes no event), it then calls `_republish_validity()`,
    still under the registry lock.
  - `SpellSystemStates.index_has_flag(index_id, flag) -> bool`: under the registry lock, False for an empty id or an
    unregistered index, otherwise the state's `has_flag`. A state held in the registry is live while that lock is
    held: `unregister_index` pops a state before it cleans it, and the registry's own cleanup cleans under the lock.
    It is the per-lineage read; RiskManager reads the published set below instead.
  - `SpellSystemStates.non_resolvable_index_ids -> FrozenSet[str]` (read-only property): the registered lineages
    whose state carries the flag, as one immutable set read without a lock. `register_index` puts the lineage in
    or out (`_publish_non_resolvable_membership_locked`) right after the capability write and before
    `mark_structural_change`, so the refresh its event runs reads the new set; `unregister_index` takes the lineage
    out after it pops the state; the set is replaced whole, never mutated (nothing is replaced when the membership
    already matches). Cleanup leaves an empty set as a documented tombstone, so a lock-free read racing it finds a
    set; after cleanup the property raises the cleaned-registry RuntimeError.

## Interface deltas
- Inputs: `register_index` takes the keyword-only `resolvable: Optional[bool]` (the selected version's
  `Spell.resolvable`, or None for a registration that does not change the selection).
- Outputs: `has_flag` and `index_has_flag` return bools; `update_flags` returns whether the flag set changed;
  `non_resolvable_index_ids` returns a frozenset.
- Error semantics: `register_index` raises TypeError for a capability that is neither None nor a bool, before it
  registers anything; `update_flags` and `has_flag` raise RuntimeError on a cleaned state (`check_cleaned`).

## State and lifecycle deltas
- Owned state: one more possible member in `SpellSystemState._flags`; the registry gains one field,
  `_non_resolvable_index_ids` (a frozenset replaced whole under its lock, emptied as a tombstone at cleanup).
- Lifecycle: `register_index` sets and clears the flag; validation never clears it (`clear_dirty` clears only the
  topology flags); `unregister_index` removes the state with all its flags, as before; the transfer flip registers a
  fresh state, so it must pass the capability (component_patch_registration_call_sites.md).

## Failure mode deltas
- New: TypeError for a non-bool capability.
- Removed: none. Changed: none - a caller that passes nothing never sets the flag, which is today's behaviour.

## Dependency and ordering constraints
1. The flag is written before `mark_structural_change`, so the RiskManager callback that the gate publishes already
   sees it; a gate that publishes nothing (already `gated`) is followed by `_republish_validity()` when the flag
   changed.
2. Lock order: registry lock, then state lock - `register_index`'s existing order; `index_has_flag` takes the same.
   The published set is written under the registry lock and read under none.
3. No caller is required to pass the capability for correctness; without it a flagged lineage loses the flag at its
   next selection change, which is the conservative direction (its risk counts again).

## Validation expectations
- Unit, both GIL modes: `update_flags` and `has_flag` semantics and their cleaned refusal; `clear_dirty` keeps the flag;
  `register_index` - False on a new index sets the flag before the gate publishes (a recording risk manager sees it
  in its callback), True clears it, None keeps it for an unchanged selection and clears it for a changed one and for
  a new state, TypeError leaves the registry unchanged; `unregister_index` removes it; `index_has_flag` for empty,
  unknown and registered ids; a flag change on a lineage already `gated` publishes exactly one event, carrying the
  new flag, and an unchanged flag publishes none; the published set follows every registration path, unregister
  and cleanup, is replaced rather than mutated, agrees with each lineage's flag, and is already right when the
  gate's callback runs.
- The existing spell_system_states unit and component suites stay green.

## Unknowns and open decisions
- UNKNOWN: none.
- DECISION_REQUEST: none (the flag's name follows the approved recommendation).

## Context / Handoff Summary
- What changed: written before any edit; amended 2026-10-15T21:20:19Z with `_republish_validity` and the result of
  `update_flags`, and 2026-10-15T22:12:54Z with the published set `non_resolvable_index_ids`.
- Remaining risks: none in these files; the call sites decide whether the flag is ever set.
- Next entrypoint: component_patch_risk_manager.md.
