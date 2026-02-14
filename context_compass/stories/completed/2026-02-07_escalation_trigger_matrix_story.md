Completed: 2026-02-07
Summary: Closed per reprioritization directive; superseded by full AOT codegen epic and ticket set.

# Story: Define Escalation Trigger Matrix for Full Revalidation

## Metadata
- Story ID: STORY-2026-02-07-escalation-trigger-matrix
- Epic: EPIC-2026-02-07-phase-5-7-spell-isolated-revalidation
- Status: ready
- Owner: Mark + Codex
- Priority: p0
- Created: 2026-02-07
- Updated: 2026-02-07

## User Narrative
As a runtime maintainer, I want an explicit escalation trigger matrix, so that we can run target-first revalidation by default and invoke full revalidation only when required.

## Value / MRP Alignment
A trigger matrix makes behavior deterministic, testable, and maintainable while protecting throughput.

## Requirements (Functional)
- Define explicit trigger classes for escalation to full revalidation.
- Wire trigger classes to routing decision in meld revalidation flow.
- Ensure trigger decision is observable in diagnostics/logging.
- Preserve existing transaction-driven change signals.

## Requirements (Non-Functional)
- Trigger checks must be cheap and deterministic.
- No dependence on spellbook-global lock.

## Scope Boundaries
- In scope:
- Trigger taxonomy and routing decision logic.
- Tests proving each trigger routes correctly.
- Out of scope:
- Full implementation of each escalated behavior (covered by related stories).

## Dependencies / Related Work
- `src/melder/aether/conduit/meld/meld.py`
- `src/melder/aether/dev_ops/spell_system_states/*`
- `src/melder/aether/dev_ops/change_control_manager/*`

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-02-07-trigger-taxonomy - Define trigger categories and map them to escalation behavior.
- [ ] Task: TASK-2026-02-07-trigger-routing - Implement routing decision integration in meld revalidation path.
- [ ] Task: TASK-2026-02-07-trigger-tests - Add tests for each trigger route and default non-escalated path.

## Acceptance Criteria
- Trigger matrix is explicitly defined in code/docs.
- Non-trigger events stay on target-first local revalidation.
- Trigger events route to full revalidation path deterministically.

## Validation / Test Plan
- Add unit tests for routing decisions.
- Add integration checks for representative transaction/change-control events.

## UX / API / Data Notes
- No public API changes expected.
- Internal diagnostics should capture route decision (`local` vs `full`).

## Risks / Mitigations
- Risk: Matrix too broad hurts throughput.
- Mitigation: Start with strict minimal trigger set and expand only with failing evidence.
- Risk: Matrix too narrow misses required full revalidation.
- Mitigation: Add targeted regression cases for link/contract/ownership change flows.

## Open Questions
- UNKNOWN: Final set of trigger classes agreed for v1 rollout.

## Decision Log
- 2026-02-07: Adopt explicit escalation trigger matrix to control local vs full revalidation route.

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
This story defines when full revalidation is required. It is the policy backbone that allows target-first revalidation to be safe and predictable.

