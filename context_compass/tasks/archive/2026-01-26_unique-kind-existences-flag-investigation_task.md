# Task: Investigate unique_kind_existences exists-flag fast path

## Metadata
- Task ID: TASK-2026-01-26-unique-kind-existences-flag-investigation
- Story: STORY-2026-01-25-fast-path-runtime
- Status: draft
- Owner:
- Priority: p2
- Created: 2026-01-26
- Updated: 2026-01-26

## Objective
Investigate whether a boolean exists-flag for unique_kind_existences can enable a
safe, faster reuse check and document the recommended design.

## Scope Boundaries
- In scope:
  - Define which Existence values qualify as unique_kind_existences.
  - Identify the correct storage location (Spell, Creations, Conduit, SpellSpace).
  - Determine concurrency and lifecycle semantics (cleanup, revalidation, transfer).
  - Document risks and invalidation requirements.
- Out of scope:
  - Code changes.

## Steps / Checklist
- [ ] Review current reuse checks and existence routing in meld runtime.
- [ ] Define unique_kind_existences and any exclusions (e.g., per-path).
- [ ] Evaluate where an exists-flag can live without breaking scoping rules.
- [ ] Document concurrency + invalidation rules.
- [ ] Propose an implementation plan and testing approach.

## Deliverables
- Design note with recommended location, semantics, and invalidation rules.

## Files / Paths Impacted
- context_compass/tasks/2026-01-26_unique-kind-existences-flag-investigation_task.md

## Validation
- Not run.
- Recommended commands:
  - None (design-only).

## Risks / Rollback Notes
- Risk: a global exists-flag breaks per-conduit or per-spellspace scoping.
  Mitigation: scope the flag to the correct creations container and key.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Task created to investigate a unique_kind_existences exists-flag fast path and
capture the recommended design.
