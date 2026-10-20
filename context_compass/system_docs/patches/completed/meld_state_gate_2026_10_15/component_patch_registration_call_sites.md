# Component patch: the registration call sites pass the capability (meld_state_gate_2026_10_15)

## Metadata
- Patch ID: meld_state_gate_2026_10_15
- Components: Spellbook (`bind`, `_apply_notch`) and TransferOfOwnership (`_flip_registry_and_spellbooks`,
  `_rollback_spellbook_move`)
- Files: `src/melder/aether/spellbook/spellbook.py`, `src/melder/aether/conduit/conduit_ward/transfer/
  transfer_of_ownership.py` - both melder_0's (EPIC-2026-10-14-managed_spell_quantity; the transfer file is in its
  S6 lane). Edited only after the owner hands the four lines over.
- Tests: five test doubles in melder_0's test lanes that mirror the old signature (below), in the same handoff.
- Status: active; pending the handoff
- Owner: user; melder_1 (synaptic_python_developer) (patch)
- Created: 2026-10-15T21:00:00Z
- Updated: 2026-10-15T22:32:34Z

## Component purpose and boundary
- Current boundary: these four calls are where a lineage's selected version is (re)registered in the frame's
  SpellSystemStates; SpellIndex holds ids only, so only the caller holds the Spell whose capability is meant.
- Target boundary: unchanged; each call passes that Spell's capability.

## Before / after
- Before:
  - `Spellbook.bind`: `self._spell_system_states.register_index(spell_index=new_spell.spell_index,
    owner_spellbook_id=self._id)`
  - `Spellbook._apply_notch`: `self._spell_system_states.register_index(spell_index=spell_index,
    owner_spellbook_id=self._id)`
  - `TransferOfOwnership._flip_registry_and_spellbooks`: `tgt_states.register_index(spell_index=spell_obj.spell_index,
    owner_spellbook_id=tgt_book._id)` - after `src_states.unregister_index(...)`, so on one frame registry the
    lineage gets a fresh state.
  - `TransferOfOwnership._rollback_spellbook_move`: `src_states.register_index(spell_obj.spell_index)` - a fresh state
    when the two Books use different registries.
- After: the same calls with one keyword each: `resolvable=new_spell.resolvable` (bind), `resolvable=spell.resolvable`
  (notch: the promoted member), `resolvable=spell_obj.resolvable` (flip and rollback: the active member moved).
- Left as is: `TransferOfOwnership._mark_lineage_disabled` registers a missing state without a capability; that state
  is unflagged (conservative) and the flip that follows passes the capability.

## Test doubles that follow the keyword
With only the four keywords applied, 45 unit tests failed: two `register_index` lambdas reject the keyword and two
transfer `build_spell` doubles return a SimpleNamespace without `resolvable`. A real Spell always carries
`resolvable` (default True) and the real registry takes the keyword, so the doubles are corrected to mirror that;
no production fallback is added.
- `tests/unit/melder/spellbook/test_spellbook.py`: both lambdas take `resolvable=None`; the bind one records
  `(spell_index, new_spell, resolvable)` and the test asserts that bind passes True.
- `tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py` and
  `test_transfer_of_ownership_contracts.py`: the fake `register_index` takes `*, resolvable: Optional[bool] = None`
  (its stale `spell:` Args line corrected) and `build_spell` sets `resolvable=True`.
- `tests/component/melder/spellbook/test_spellbook_component_spell_crafter.py` and
  `test_spellbook_component_spellbook.py`: the fake `register_index` takes `*, resolvable: object = None`, with an
  Args line.
The apply script `apply_call_sites.py` in the lane's artifact folder writes the four keywords and these doubles;
its `--check` finds every anchor in the real tree.

## Interface deltas
- None beyond the keyword. No behaviour changes for a resolvable version (the flag is cleared, which it already is).

## State and lifecycle deltas
- A lineage whose selected version is resolvable=False carries `non_resolvable` from its bind, keeps it through
  validation and through a transfer (and its rollback), loses it at a notch to a resolvable version and regains it at a
  notch back.

## Failure mode deltas
- `Spell.resolvable` raises RuntimeError on a cleaned Spell; each of the four Spells is live at its call (bound or
  promoted a moment before, or the member being moved).

## Dependency and ordering constraints
1. Needs component_patch_spell_state_model.md (the keyword) first.
2. Each call stays where it is; `bind` and `_apply_notch` still call `register_spell` after `register_index`.

## Validation expectations
- Component, both GIL modes: bind a Protocol definition before and after conjure (automatic and dynamic): the
  lineage carries the flag, the Book flag is down after the first meld of anything else; notch to a resolvable
  version raises the flag until that version's first meld; notch back lowers it; transfer a definition between roots:
  the target's flag stays down; a failed transfer (rollback) keeps the flag.
- The existing bind, notch and transfer suites (unit, component, integration) stay green.

## Unknowns and open decisions
- DECISION_REQUEST (owner): hand these four lines and the five test files to melder_1, or have melder_0 apply
  them (apply_call_sites.py) in its lane.

## Context / Handoff Summary
- What changed: written before any edit; the change is built and validated on a scratch tree first; amended
  2026-10-15T22:12:54Z with the five test doubles.
- Remaining risks: melder_0's S6 edits around the flip; the keyword is one argument and rebases trivially.
- Next entrypoint: code_description_patch_risk_distillation.md.
