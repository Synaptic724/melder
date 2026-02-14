# Task: Remove remaining MeldEngine duplication and plan snapshots

## Metadata
- Task ID: TASK-2026-01-30-remove-meldengine-duplication
- Story: N/A
- Status: in_progress
- Owner:
- Priority: p0
- Created: 2026-01-30
- Updated: 2026-01-30

## Objective
Remove remaining runtime duplication in MeldEngine by consuming precomputed
Phase 11 step metadata, and stop returning snapshot copies from execution plan
accessors.

## Scope Boundaries
- In scope:
  - Use plan_step.shared_instance/existence/lock hints in MeldEngine.
  - Remove redundant plan fields (spell_id) and rely on spell reference.
  - Return live data structures from ExecutionPlan accessors (no dict/list copies).
  - Update docstrings/comments in touched code.
- Out of scope:
  - New phases or tests.
  - Architecture/components docs.

## Steps / Checklist
- [x] Add plan_step lock-hint boolean and use it in MeldEngine.
- [x] Remove plan_step spell_id field and update consumers.
- [x] Use plan_step shared/existence fields instead of recomputing.
- [x] Return live structures from ExecutionPlan accessors.

## Deliverables
- MeldEngine no longer recomputes shared/existence/lock logic.
- ExecutionPlan accessors return real structures (no snapshots).

## Files / Paths Impacted
- src/melder/spellbook/spell_crafter/blueprints/execution_plan.py
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py

## Validation
- Not run.
- Recommended commands:
  - pytest -q

## Risks / Rollback Notes
- Risk: External callers may mutate plan data structures when snapshots removed.
  - Rollback: restore copy-on-access behavior.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
- MeldEngine now uses plan_step shared/existence/lock hints and no longer recomputes them.
- ExecutionPlan accessors return live structures (no snapshot copies).
- Removed redundant plan_step spell_id field in favor of spell reference.
