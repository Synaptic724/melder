Completed: 2026-02-07
Summary: Closed per reprioritization directive; superseded by full AOT codegen epic and ticket set.

# Story: Add Meld-Locked Full Revalidation Path for Escalated Events

## Metadata
- Story ID: STORY-2026-02-07-meld-locked-full-revalidation
- Epic: EPIC-2026-02-07-phase-5-7-spell-isolated-revalidation
- Status: ready
- Owner: Mark + Codex
- Priority: p0
- Created: 2026-02-07
- Updated: 2026-02-07

## User Narrative
As a runtime maintainer, I want escalated full revalidation to run under a meld validation lock path, so that we avoid duplicate concurrent full revalidation and stabilize shared artifact updates.

## Value / MRP Alignment
This story gives a deterministic safety lane for heavy revalidation events while preserving high-throughput local path behavior.

## Requirements (Functional)
- Implement full revalidation execution path under a meld validation lock.
- Ensure only one full revalidation run executes for the active locked scope/event window.
- Ensure waiting meld calls resume with fresh validity state after full revalidation.
- Preserve error propagation and diagnostics behavior.

## Requirements (Non-Functional)
- Lock is used only for escalated full revalidation, not all meld calls.
- Avoid deadlocks with existing spell-level locks and cleanup flows.

## Scope Boundaries
- In scope:
- Locked full revalidation execution flow for escalated route.
- Wait/recheck behavior for concurrent meld callers.
- Out of scope:
- Replacing existing transaction semantics.
- Global pause of all meld paths.

## Dependencies / Related Work
- `src/melder/aether/conduit/meld/meld.py`
- `src/melder/spellbook/spellbook.py` (`_run_resolution_phases_for_conduit`)
- `src/melder/aether/conduit/meld/meld_gate.py` (for behavioral compatibility considerations)

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-02-07-full-lock-path - Implement locked full revalidation route.
- [ ] Task: TASK-2026-02-07-full-lock-recheck - Add post-lock validity recheck and waiter behavior.
- [ ] Task: TASK-2026-02-07-full-lock-tests - Add concurrency tests for single-flight full revalidation behavior.

## Acceptance Criteria
- Escalated events route to locked full revalidation path.
- Concurrent escalated requests do not run duplicate full revalidation work.
- Non-escalated requests remain on target-first path without entering full lock route.

## Validation / Test Plan
- Add integration tests for concurrent escalated meld calls.
- Validate no deadlock and proper error handling under failures/cancellation.

## UX / API / Data Notes
- No public API changes expected.
- Internal diagnostics should indicate locked full path invocation.

## Risks / Mitigations
- Risk: Lock scope too broad and harms throughput.
- Mitigation: Limit lock to escalated route only and keep critical section minimal.
- Risk: Lock ordering conflicts with spell-level locks.
- Mitigation: Define strict lock order and test with stress scenarios.

## Open Questions
- UNKNOWN: Final lock object ownership location for implementation (existing proxy object integration point).

## Decision Log
- 2026-02-07: Full revalidation will be protected by meld validation lock path for escalated events only.

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
This story defines the controlled safety lane for heavy revalidation events. It prevents duplicate concurrent full revalidation while preserving target-first behavior as the default path.

