# Task: Rewire ownership transfer to re-register lineage and gate target

## Metadata
- Task ID: TASK-2026-01-30-transfer-ownership-state
- Story: 
- Status: in_progress
- Owner: 
- Priority: p0
- Created: 2026-01-30
- Updated: 2026-01-30

## Objective
Ensure ownership transfer unregisters lineage from the source SpellSystemStates, registers it in the target SpellSystemStates, and gates impacted conduits so meld revalidation runs before resolution.

## Scope Boundaries
- In scope:
  - Add a strict unregister API to SpellSystemStates.
  - Update ownership transfer to unregister, re-register, and gate without fallbacks.
  - Keep coarse conduit dirtying for impacted conduits.
- Out of scope:
  - Fine-grained per-spell revalidation targeting.
  - Broader validation pipeline changes unrelated to transfer.

## Steps / Checklist
- [ ] Add SpellSystemStates.unregister_lineage with lock-guarded cleanup of indices.
- [ ] Update TransferOfOwnership to unregister from source, register on target, and gate/dirty.
- [ ] Remove fallback/best-effort behavior that masks missing system state during transfer.
- [ ] Update docstrings for touched methods.
- [ ] Update tests affected by ownership transfer behavior if needed.

## Deliverables
- Updated `src/melder/aether/dev_ops/spell_system_states/spell_system_states.py`
- Updated `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py`

## Files / Paths Impacted
- `src/melder/aether/dev_ops/spell_system_states/spell_system_states.py`
- `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py`

## Validation
- Not run.
- Recommended commands:
  - `pytest tests/integration/melder/conduit/test_conduit_integration_lifecycle.py::test_conduit_transfer_spell_ownership_moves_registry_and_meld`

## Risks / Rollback Notes
- Incorrect unregister may leave stale indices or break validation.
- Rollback by reverting the unregister/transfer changes.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
- Created task for strict ownership transfer re-registration and gating. Next: implement unregister_lineage and update transfer flow, then validate with integration test.
