# Task: Resolve contract sockets for plan eligibility

## Metadata
- Task ID: TASK-2026-01-25-contract-resolution-plan
- Story: STORY-2026-01-25-plan-compilation-phase8
- Status: draft
- Owner:
- Priority: p1
- Created: 2026-01-25
- Updated: 2026-01-25

## Objective
Pre-resolve contract sockets during plan compilation when wiring is stable, and
mark plans ineligible when contracts are late-bound.

## Scope Boundaries
- In scope:
  - Contract socket resolution checks and eligibility flags.
- Out of scope:
  - Contract mutation redesign.

## Steps / Checklist
- [ ] Identify contract socket resolution logic in MeldEngine.
- [ ] Define eligibility rules for stable contract wiring.
- [ ] Store provider resolution or ineligible markers in plan.

## Deliverables
- Contract resolution metadata in RootExecutionPlan.

## Files / Paths Impacted
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py
- src/melder/aether/conduit/meld/contracts/spell_contract.py

## Validation
- Not run.
- Recommended commands:
  - pytest tests/unit/melder/aether/conduit/meld -k contract

## Risks / Rollback Notes
- Risk: plan uses stale contract wiring.
  Mitigation: include contract wiring in plan signature and gating.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Task created; contract resolution planning pending.
