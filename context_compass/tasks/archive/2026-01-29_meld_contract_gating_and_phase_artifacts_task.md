# Task: Stabilize meld contract gating and phase artifacts

## Metadata
- Task ID: TASK-2026-01-29_meld_contract_gating_and_phase_artifacts
- Story:
- Status: in_progress
- Owner:
- Priority: p1
- Created: 2026-01-29
- Updated: 2026-01-29

## Objective
Restore a clean baseline by aligning meld contract gating behavior and phase-artifact expectations with current system intent, fixing the reported failing tests without unrelated refactors.

## Scope Boundaries
- In scope:
  - Fix failing meld contract resolution tests (unit + integration).
  - Align meld runtime phase-artifact access with test fixtures/stubs.
  - Update phase ordering expectations to include execution_plan.
- Out of scope:
  - New features unrelated to contract gating.
  - Broad refactors or public API changes.
  - Any behavior change not tied to the reported failures.

## Steps / Checklist
- [ ] Inspect failing tests and current meld/Spellbook behavior.
- [ ] Propose targeted code vs test changes with file/symbol list.
- [ ] Implement approved fixes with docstring/comment updates.
- [ ] Update/extend tests to cover corrected behavior.
- [ ] Summarize changes and recommend validation commands.

## Deliverables
- Updated meld/Spellbook behavior or tests that match intended contracts.
- Passing unit/integration tests for the reported failures.

## Files / Paths Impacted
- `src/melder/aether/conduit/meld/meld.py`
- `src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py`
- `tests/unit/melder/aether/conduit/meld/test_meld.py`
- `tests/unit/melder/aether/conduit/meld/meld_runtime/test_meld_runtime.py`
- `tests/unit/melder/spellbook/test_spell.py`
- `tests/integration/melder/conduit/test_conduit_integration_links_contracts.py`
- `tests/integration/melder/conduit/test_conduit_integration_spell_contract_variants.py`

## Validation
- Not run.
- Recommended commands:
  - `pytest tests/unit/melder/aether/conduit/meld/meld_runtime/test_meld_runtime.py -q`
  - `pytest tests/unit/melder/aether/conduit/meld/test_meld.py -q`
  - `pytest tests/unit/melder/spellbook/test_spell.py::test_run_all_phases_invokes_crafter_in_order -q`
  - `pytest tests/integration/melder/conduit/test_conduit_integration_links_contracts.py -q`
  - `pytest tests/integration/melder/conduit/test_conduit_integration_spell_contract_variants.py -q`

## Risks / Rollback Notes
- Risk: Contract-gating behavior affects runtime resolution; verify behavior matches system intent before broad validation.
- Rollback: Revert meld contract gating and phase artifact handling to prior behavior if regressions occur.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Created task to stabilize meld contract gating and phase artifact expectations per reported failing tests; execution_plan is confirmed to be part of run_all_phases. Next: inspect code/tests and propose concrete changes for approval.
