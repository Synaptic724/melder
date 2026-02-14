# Story: Optional codegen and Cython executor spike

## Metadata
- Story ID: STORY-2026-01-25-fast-path-codegen
- Epic: EPIC-2026-01-25-fast-path-meld-compiled-plans
- Status: draft
- Owner:
- Priority: p3
- Created: 2026-01-25
- Updated: 2026-01-25

## User Narrative
As a performance engineer, I want an optional codegen or Cython executor path so
we can push warm and cold root performance lower once the plan model is stable.

## Value / MRP Alignment
Keeps the core fast path in Python while enabling a future higher-performance
option without changing semantics.

## Requirements (Functional)
- Codegen executor that emits a specialized Python function per plan.
- Debug mode to dump generated code for inspection.
- Cython feasibility spike on tight loop execution.

## Requirements (Non-Functional)
- Codegen is optional and gated by configuration.

## Scope Boundaries
- In scope:
  - Codegen executor spike and debug dump.
  - Cython feasibility report.
- Out of scope:
  - Productionizing Cython in v1.

## Dependencies / Related Work
- RootExecutionPlan model and fast-path executor.

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-01-25-codegen-research - Research codegen entrypoints and constraints.
- [ ] Task: TASK-2026-01-25-plan-codegen-executor - Emit and compile plan executors.
- [ ] Task: TASK-2026-01-25-codegen-debug-dump - Dump generated code for inspection.
- [ ] Task: TASK-2026-01-25-codegen-tests - Add unit tests for codegen output.
- [ ] Task: TASK-2026-01-25-cython-feasibility-spike - Evaluate Cython for executor.

## Acceptance Criteria
- Optional codegen path compiles and executes plan correctly.
- Debug dump provides readable generated code.
- Cython spike results are documented.

## Validation / Test Plan
- Not run.
- Recommended: pytest tests/unit/melder/aether/conduit/meld -k codegen

## UX / API / Data Notes
- Internal only, no public API changes.

## Risks / Mitigations
- Risk: codegen introduces subtle bugs.
  Mitigation: keep behind a flag and add targeted tests.

## Open Questions
- Should codegen be tied to a plan signature version or runtime flag?

## Decision Log
- TBD.

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Story created; optional codegen and Cython spike pending.
