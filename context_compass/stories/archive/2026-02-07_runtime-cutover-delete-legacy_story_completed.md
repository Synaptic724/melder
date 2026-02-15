Completed: 2026-02-08
Summary: Delivered Runtime Cutover and Legacy Removal and confirmed story acceptance criteria.

# Story: Runtime Cutover and Legacy Removal

## Metadata
- Story ID: STORY-2026-02-07-runtime-cutover-delete-legacy
- Epic: EPIC-2026-02-07-full-aot-codegen-cutover
- Status: done
- Owner:
- Priority: p0
- Created: 2026-02-07
- Updated: 2026-02-08

## User Narrative
As a maintainer, I want runtime to be dispatch-only and legacy execution removed,
so architecture cannot regress into mixed execution ownership.

## Value / MRP Alignment
Enforces one execution model by construction.

## Requirements (Functional)
- `MeldRuntime` dispatches to generated executors only.
- Remove interpreter helper execution paths from runtime modules.
- Remove legacy engine references and dead compatibility shims.
- Keep hard-fail behavior for missing generated artifacts.

## Requirements (Non-Functional)
- No fallback branches.
- Clear errors for missing phase artifacts.

## Scope Boundaries
- In scope:
- Runtime cutover and deletion of legacy execution assets.
- Out of scope:
- New user-facing API features.

## Dependencies / Related Work
- All generator stories above.

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-02-07-runtime-cutover-dispatch-only
- [x] Task: TASK-2026-02-07-remove-interpreter-executors
- [x] Task: TASK-2026-02-07-delete-legacy-engine-artifacts

## Acceptance Criteria
- Runtime has no interpreter/engine execution dependencies.
- Source search finds no active legacy execution wiring.

## Validation / Test Plan
- Structural source assertions + unit tests for dispatch wiring.

## UX / API / Data Notes
- Internal cleanup only.

## Risks / Mitigations
- Risk: hidden dependency on removed helpers.
- Mitigation: full suite and path coverage tests.

## Open Questions
- None.

## Decision Log
- 2026-02-07: remove legacy execution entirely in cutover branch.

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Story locks runtime architecture to generated-executor-only behavior. Current
progress removed no-overrides interpreter-style helper execution from Phase12
compiler output and deleted the no-overrides step-loop helper implementation.
Runtime dispatch remains generated-only, and legacy engine wording in meld
contracts/runtime-facing docs was cleaned to match the cutover architecture.
Override step helper execution was also removed by deleting
`_resolve_step_instance_with_overrides` and inlining emitted override step
semantics. Current targeted codegen regression bundle passes at 193 tests.

