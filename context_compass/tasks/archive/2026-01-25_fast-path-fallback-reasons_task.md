# Task: Track fast-path fallback reasons

## Metadata
- Task ID: TASK-2026-01-25-fast-path-fallback-reasons
- Story: STORY-2026-01-25-fast-path-runtime
- Status: draft
- Owner:
- Priority: p2
- Created: 2026-01-25
- Updated: 2026-01-25

## Objective
Capture structured fallback reasons when fast-path gating fails.

## Scope Boundaries
- In scope:
  - Enumerated fallback reasons and counters.
- Out of scope:
  - Full metrics pipeline.

## Steps / Checklist
- [ ] Define fallback reason enum or constants.
- [ ] Record reason when fast path is skipped.
- [ ] Expose counters via logger or diagnostics object.

## Deliverables
- Fallback reason counters in runtime.

## Files / Paths Impacted
- src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py

## Validation
- Not run.
- Recommended commands:
  - pytest tests/unit/melder/aether/conduit/meld -k fallback

## Risks / Rollback Notes
- Risk: fallback tracking adds overhead.
  Mitigation: allow disabling metrics.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Task created; fallback reason tracking pending.
