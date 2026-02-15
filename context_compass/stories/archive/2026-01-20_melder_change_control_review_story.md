- Completed: 2026-01-20
- Summary: Tracked and closed change-control review follow-up tasks, with object map and findings delivered.

# Story: Change-Control + DevOps Review Follow-Ups

## Metadata
- Story ID: STORY-2026-01-20-change-control-review
- Epic: EPIC-2026-01-20-change-control-devops-review
- Status: completed
- Owner:
- Priority: p1
- Created: 2026-01-20
- Updated: 2026-01-20

## User Narrative
As a Melder maintainer, I want review findings captured as actionable tasks, so
that we can resolve correctness gaps in the change-control/DevOps stack.

## Value / MRP Alignment
Solidifies the change-control core by addressing known gaps before expanding
features, reducing rework risk.

## Requirements (Functional)
- Track each review finding as a task with file references and outcomes.
- Ensure tasks cover admission, embargo, dirty-root lifecycle, and audit data.

## Requirements (Non-Functional)
- Tasks must be scoped to the single aetheric frame design.
- Keep changes deterministic and thread-safe.

## Scope Boundaries
- In scope:
  - Admission/embargo scope updates when staged metadata changes.
  - Dirty-root lifecycle rules after revalidation.
  - Request validation for initiator metadata.
  - Link mirror integration or removal.
- Out of scope:
  - New queueing, priority, or DLQ behavior.
  - Cross-frame coordination.

## Dependencies / Related Work
- `context_compass/epics/completed/2026-01-20_melder_change_control_devops_review_epic.md`

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-01-20-change-control-staged-scope-refresh - Refresh embargo scopes on staged updates.
- [x] Task: TASK-2026-01-20-change-control-dirty-root-lifecycle - Preserve dirty roots on partial revalidation.
- [x] Task: TASK-2026-01-20-change-control-initiator-validation - Enforce initiator id validation in requests.
- [x] Task: TASK-2026-01-20-change-control-link-mirror - Wire link mirror lifecycle or remove unused registry.
- [x] Task: TASK-2026-01-20-change-control-object-map - Compile change-control + DevOps object map.
- [x] Task: TASK-2026-01-20-change-control-review-findings - Deliver review findings with references.
- [x] Task: TASK-2026-01-20-change-control-link-mirror-admission - Define admission behavior for link mirror registry.
- [x] Task: TASK-2026-01-20-change-control-scope-key-hash-conflict - Normalize scope key/hash conflict checks.

## Acceptance Criteria
- Tasks are created with clear objectives and file impact notes.
- Follow-up work is ready to execute in order.

## Validation / Test Plan
- Review-only; each task will add or update its own test coverage plan.

## UX / API / Data Notes
- No new public APIs required; changes should preserve existing call sites.

## Risks / Mitigations
- Risk: changes alter admission behavior.
  - Mitigation: add tests around admission/embargo scopes.

## Open Questions
- None yet; refine per task.

## Decision Log
- 2026-01-20: Break review findings into tasks.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
This story tracks the follow-up tasks derived from the change-control/DevOps
review so each gap can be fixed independently.
