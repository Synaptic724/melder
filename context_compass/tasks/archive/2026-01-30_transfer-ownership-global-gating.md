# Task: Gate ownership transfer across dependents and linked conduits

## Metadata
- Task ID: 2026-01-30_transfer-ownership-global-gating
- Story: N/A
- Status: completed
- Owner: codex
- Priority: p1
- Created: 2026-01-30
- Updated: 2026-01-30

## Objective
When a spell ownership transfer completes, gate the moved lineage and all dependent
lineages, and mark resolution state dirty for all conduits linked to the owner
(including target). Use SpellSystemStates to drive risk tracking and revalidation.

## Scope Boundaries
- In scope:
  - Use SpellSystemStates.mark_structural_change + compute_impact_closure for the moved lineage.
  - Mark ConduitResolutionState dirty for linked/clustered/owner/target conduits.
  - Update docstrings for touched methods.
- Out of scope:
  - Changes to contract semantics outside transfer.
  - Broad revalidation logic changes unrelated to transfer.

## Steps / Checklist
- [x] Implement transfer impact gating for moved lineage + dependents.
- [x] Mark linked/clustered/owner/target conduits dirty so phases 5-11 rerun.
- [x] Update docstrings for new helpers and modified methods.

## Deliverables
- Ownership transfer gating across dependents and linked conduits.

## Files / Paths Impacted
- src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py

## Validation
- Not run (relied on user test runs).

## Risks / Rollback Notes
- Risk: More conduits will rerun phases after transfer, increasing validation work.
- Rollback: Revert transfer gating helper and conduit dirty marking.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Ownership transfer currently dirties only the source spellbook, leaving the target
lineage valid with `_crafter=None`. This change gates the moved lineage and all
impacted dependents and marks linked conduits dirty so phases 5-11 rerun.
