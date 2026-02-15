Completed: 2026-02-07
Summary: Closed per reprioritization directive; superseded by full AOT codegen epic and ticket set.

# Task: Fix RiskManager structural validity gating regression

## Metadata
- Task ID: TASK-2026-02-07-risk-manager-validation-gate-regression
- Story:
- Status: in_progress
- Owner:
- Priority: p1
- Created: 2026-02-07
- Updated: 2026-02-07

## Objective
Restore correct meld validation gating by fixing RiskManager structural validity
lookup and ensuring unregister_lineage cleanup/notifications are reliable.

## Scope Boundaries
- In scope:
  - Fix RiskManager structural validity retrieval to use SpellSystemState.
  - Make SpellSystemStates.unregister_lineage notify RiskManager safely and
    always cleanup removed state.
  - Update unit tests for risk notification ordering.
  - Remove runtime print diagnostics in meld.
- Out of scope:
  - Any new public API surface changes.
  - Broad refactors of DevOps or meld pipelines.
  - Performance tuning unrelated to the regression.

## Steps / Checklist
- [x] Update RiskManager structural validity lookup and docstrings.
- [x] Make unregister_lineage notification + cleanup deterministic.
- [x] Update unit tests to match valid call ordering (gated then cleaned).
- [x] Remove runtime print diagnostics in Meld.

## Deliverables
- Correct structural validity gating in RiskManager.
- Reliable unregister_lineage cleanup + notification behavior.
- Updated tests reflecting expected risk-manager call order.

## Files / Paths Impacted
- src/melder/aether/dev_ops/risk_manager/risk_manager.py
- src/melder/aether/dev_ops/spell_system_states/spell_system_states.py
- src/melder/aether/conduit/meld/meld.py
- tests/unit/melder/aether/dev_ops/spell_system_states/test_spell_system_states.py
- tests/unit/melder/aether/dev_ops/risk_manager/test_risk_manager.py (if added)

## Validation
- Not run.
- Recommended commands:
  - pytest tests/unit/melder/aether/dev_ops

## Risks / Rollback Notes
- RiskManager changes could alter validation-required gating; rollback by
  reverting RiskManager/_unregister_lineage edits to pre-regression behavior.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Regression traced to RiskManager using a non-existent SpellIndex.validity and
unregister_lineage swallowing errors. Fixes update RiskManager validity source,
stabilize unregister_lineage cleanup/notification, add RiskManager unit tests,
and update unit tests to expect gated+cleaned notification order. No runtime
print diagnostics were found in meld at time of change.

