# Story: JIT/AOT Post-Conjure Bind Propagation

## Metadata
- Story ID: STORY-2026-02-15-jit-aot-post-conjure-bind-propagation
- Epic: EPIC-2026-02-14-jit-aot-phase-split-configuration
- Status: ready
- Owner: codex
- Priority: p1
- Created: 2026-02-15
- Updated: 2026-02-15

## User Narrative
As a runtime maintainer, I want binds added after conjure to inherit the same
mode defaults so spell behavior stays consistent during long-lived runtime use.

## Value / MRP Alignment
This prevents mode drift between pre-conjure and post-conjure binds.

## Requirements (Functional)
- When `Spellbook.bind(...)` runs after conduit exists, stamp mode and `resolution_required` from active config.
- Keep existing ownership and risk-manager registration behavior intact.

## Requirements (Non-Functional)
- No broad bind refactor.
- No change to behavior when full AOT remains enabled.

## Scope Boundaries
- In scope:
- Bind path where `_conjured` and `_conduit` are both active.
- Out of scope:
- Conjure loop and transfer path.

## Dependencies / Related Work
- `TASK-2026-02-15-discovery-jit-aot-propagation-contract-surfaces`
- `STORY-2026-02-15-jit-aot-config-flag-and-fluent-api`

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-02-15-implement-jit-aot-post-conjure-bind-propagation - implement post-conjure bind stamping.
- [ ] Task: TASK-2026-02-15-discovery-jit-aot-propagation-contract-surfaces - confirm exact bind touchpoint and side-effect boundaries.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- Newly bound spells after conjure inherit configured mode and expected `resolution_required` value.
- Existing bind side effects (owner stamp, creation registration, risk manager registration) remain intact.

## Validation / Test Plan
- Unit tests for post-conjure bind behavior under AOT default and JIT opt-in modes.

## UX / API / Data Notes
- Internal behavior; no API shape changes.

## Risks / Mitigations
- Risk: mode stamp order may conflict with existing creation registration order.
  Mitigation: confirm ordering in discovery task and assert via tests.

## Open Questions
- Should post-conjure bind mode stamping happen before or after risk manager registration?

## Decision Log
- 2026-02-15: Story created as dedicated lane for late-bind propagation requirement.

## Notes
- DATE: 2026-02-15
  TYPE: PLAN
  CLAIM: Post-conjure bind propagation should attach to the existing conditional branch where Spellbook already stamps owner conduit metadata for newly bound spells.
  EVIDENCE: src/melder/spellbook/spellbook.py:2534-2574
  IMPACT: Keeps this change local to one stable bind branch and limits regression risk.
  NEXT: Complete propagation discovery map, then implement targeted bind-path updates.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Ready story for late-bind propagation. Waiting on discovery gate completion.

