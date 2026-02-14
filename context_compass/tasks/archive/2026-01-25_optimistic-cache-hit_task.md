# Task: Add optimistic cache hit return

## Metadata
- Task ID: TASK-2026-01-25-optimistic-cache-hit
- Story: STORY-2026-01-25-fast-path-runtime
- Status: draft
- Owner:
- Priority: p1
- Created: 2026-01-25
- Updated: 2026-01-25

## Objective
Introduce a no-lock cache hit shortcut for eligible existence modes when
overrides and mutation overrides are absent.

## Scope Boundaries
- In scope:
  - Cached instance lookup and immediate return.
- Out of scope:
  - Plan execution path.

## Steps / Checklist
- [ ] Identify reuse-eligible existence modes.
- [ ] Add no-lock cache read in meld path.
- [ ] Gate cache hit on empty overrides.

## Deliverables
- Optimistic cache hit path with explicit gating.

## Files / Paths Impacted
- src/melder/aether/conduit/meld/meld.py

## Validation
- Not run.
- Recommended commands:
  - pytest tests/unit/melder/aether/conduit/meld -k cache

## Risks / Rollback Notes
- Risk: cache hit violates override semantics.
  Mitigation: require empty override and mutation payloads.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Task created; optimistic cache hit path pending.
