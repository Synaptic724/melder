# Story: JIT/AOT Transfer Ownership Propagation (Non-Contracted)

Completed: 2026-02-15
Summary: Closed after user acceptance; linked discovery/implementation tasks are complete and validated for this story scope.


## Metadata
- Story ID: STORY-2026-02-15-jit-aot-transfer-ownership-propagation-non-contracted
- Epic: EPIC-2026-02-14-jit-aot-phase-split-configuration
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-02-15
- Updated: 2026-02-15

## User Narrative
As a dynamic-runtime maintainer, I want transfer-of-ownership to apply destination
mode defaults for owned spells so transferred runtime behavior stays coherent.

## Value / MRP Alignment
This captures the user-approved transfer propagation rule while preserving the
contracted-spell owner boundary.

## Requirements (Functional)
- Re-stamp mode and `resolution_required` when ownership transfers to target conduit.
- Apply only to owned spell lineages being transferred.
- Do not rewrite owner semantics for contracted spells.

## Requirements (Non-Functional)
- Keep transfer preflight/execute flow deterministic.
- Avoid broad contract system rewrites.

## Scope Boundaries
- In scope:
- Transfer-of-ownership path for owned lineages.
- Out of scope:
- Contracting/linking behavior unrelated to ownership transfer.

## Dependencies / Related Work
- `TASK-2026-02-15-discovery-jit-aot-propagation-contract-surfaces`
- `STORY-2026-02-15-jit-aot-config-flag-and-fluent-api`

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-02-15-implement-jit-aot-transfer-ownership-propagation-non-contracted - apply target-default propagation on owned transfer.
- [ ] Task: TASK-2026-02-15-discovery-jit-aot-propagation-contract-surfaces - confirm exact transfer and exclusion touchpoints.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- Owned lineages transferred to target conduit are re-stamped by destination defaults.
- Contracted-spell owner semantics remain unchanged.
- Transfer flow stays valid in dynamic mode.

## Validation / Test Plan
- Unit tests for transfer propagation in owned-lineage path and explicit exclusion checks for contracted paths.

## UX / API / Data Notes
- Internal behavior only.

## Risks / Mitigations
- Risk: propagation touches borrowed/contracted paths by mistake.
  Mitigation: target only owned-transfer branches validated by discovery evidence.

## Open Questions
- At which exact transfer stage should context invalidation/re-gate occur relative to propagation writes?

## Decision Log
- 2026-02-15: Story created to enforce user requirement that contracted spells remain under their own owner semantics.

## Notes
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Transfer helper already guards dependency transfer to owned-only spells, and contracted spell registration is maintained in separate spellbook contracted maps.
  EVIDENCE: src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1160-1173, src/melder/spellbook/spellbook.py:1428-1468
  IMPACT: Owned-only propagation boundary can be implemented without changing contracted ownership behavior.
  NEXT: Confirm all transfer touchpoints in discovery task and then implement owned-only propagation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Ready transfer-lane story, explicitly scoped to non-contracted ownership flow.


