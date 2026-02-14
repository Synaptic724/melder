Completed: 2026-02-13
Summary: Closed by user direction as out-of-scope for the current meld optimization wave; no code implementation was performed.

# Task: Cache Meld Contract Defaults Metadata

## Metadata
- Task ID: TASK-2026-02-13-meld-contract-defaults-caching
- Story: STORY-2026-02-13-optimize-meld-paths
- Status: blocked_out_of_scope
- Owner: codex
- Priority: p0
- Created: 2026-02-13
- Updated: 2026-02-13

## Objective
Remove per-call `inspect.signature(...)` cost from meld contract-default checks
by introducing cached contract-default metadata on the spell runtime path.

## Scope Boundaries
- In scope:
- Current `Meld._iter_spell_contract_defaults` runtime inspection path.
- Metadata caching design and integration into contract check flow.
- Unit/integration coverage for unchanged behavior.
- Out of scope:
- Mutation contract behavior changes.
- Broader non-contract meld path optimization.

## Steps / Checklist
- [ ] Trace current producers/consumers of SpellContract-default metadata in meld.
- [ ] Design and document cache location and lifecycle ownership.
- [ ] Implement cache population/update and runtime use in meld checks.
- [ ] Add tests for correctness and regression safety.

## Deliverables
- Cached contract-default metadata path replacing hot-path signature inspection.
- Updated tests demonstrating unchanged contract resolution behavior.
- Story/task notes capturing performance rationale and constraints.

## Files / Paths Impacted
- `src/melder/aether/conduit/meld/meld.py`
- `src/melder/spellbook/spell.py`
- `tests/unit/melder/aether/conduit/meld/test_meld.py`
- `tests/integration/melder/spellbook/test_spellbook_integration_resolution_contract*.py`

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/conduit/meld/test_meld.py`
  - `python -m pytest -q tests/integration/melder/spellbook/test_spellbook_integration_resolution_contract.py tests/integration/melder/spellbook/test_spellbook_integration_resolution_contract_extra.py tests/integration/melder/spellbook/test_spellbook_integration_resolution_contract_more.py tests/integration/melder/spellbook/test_spellbook_integration_resolution_contract_ticket_coverage.py`

## Risks / Rollback Notes
- Risk: stale cached metadata after rebind/mutation-style updates.
- Rollback: keep old signature inspection path behind a guarded fallback while validating cache lifecycle.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Task closed without implementation by explicit user direction.
Reason:
- Mutation/revalidation area is not yet fully in scope for this optimization wave.
Next step:
- Continue with remaining meld tasks (input keypath, override shape, validation gate, dynamic gate).
