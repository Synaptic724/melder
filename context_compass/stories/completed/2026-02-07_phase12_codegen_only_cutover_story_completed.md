Completed: 2026-02-07
Summary: Cut over meld runtime to codegen-only no-overrides execution and removed engine-backed runtime path.

# Story: Phase 12 Codegen-Only Runtime Cutover

## Metadata
- Story ID: STORY-2026-02-07-phase12-codegen-only-cutover
- Epic: EPIC-2026-02-07-phase12-spell-scoped-execution
- Status: done
- Owner:
- Priority: p0
- Created: 2026-02-07
- Updated: 2026-02-07

## User Narrative
As a runtime maintainer, I want meld execution to be codegen-only and independent
of `MeldEngine`, so execution ownership is singular and hotpath overhead is lower.

## Value / MRP Alignment
This story finishes the core architectural cutover: runtime dispatches precompiled
artifacts only, and mixed execution ownership is removed.

## Requirements (Functional)
- Remove `MeldEngine` execution integration from `MeldRuntime` no-overrides paths.
- Reject override/mutation calls with explicit unsupported errors until override
  runtime codegen is implemented.
- Keep override frontend targeting inputs (TargetSpec wildcard/path and SocketRef
  maps) intact for future override codegen compilation.

## Requirements (Non-Functional)
- No backward-compat fallback paths in the cutover branch.
- Keep failure mode deterministic and explicit for unsupported override/mutation calls.

## Scope Boundaries
- In scope:
- `MeldRuntime` execution path removal of `MeldEngine` for no-overrides routes.
- Explicit override/mutation unsupported behavior during cutover.
- Dead-path cleanup in meld runtime module.
- Out of scope:
- Re-enabling overrides/mutations.
- Mutation-aware runtime codegen.

## Dependencies / Related Work
- `context_compass/stories/completed/2026-02-07_phase12_no_overrides_executor_story_completed.md`
- `context_compass/stories/completed/2026-02-07_phase12_override_shape_specialization_story_completed.md`

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-02-07-disable-overrides-hard-fail - Reject overrides/mutations with explicit unsupported runtime errors.
- [x] Task: TASK-2026-02-07-remove-meldengine-from-meldruntime - Remove `MeldEngine` execution integration from runtime paths.
- [x] Task: TASK-2026-02-07-prune-meldruntime-engine-assets - Remove runtime engine/frame/context pooling and related dead helpers.
- [x] Task: TASK-2026-02-07-delete-meld-engine-module - Delete engine module and remove remaining references.

## Acceptance Criteria
- No no-overrides execution route instantiates or executes `MeldEngine`.
- Override/mutation calls fail with explicit unsupported messages.
- Runtime module no longer carries dead engine fallback plumbing.

## Validation / Test Plan
- Unit tests for override/mutation unsupported error behavior.
- Unit/integration tests for no-overrides codegen execution route.
- Benchmark run comparing pre/post cutover no-overrides hotpath.

## UX / API / Data Notes
- Public API surface remains unchanged.
- Behavior change is runtime-only: overrides/mutations are temporarily unsupported.

## Risks / Mitigations
- Risk: users expecting override behavior see failures.
- Mitigation: explicit error messaging and dedicated follow-up story for override runtime codegen.
- Risk: hidden engine dependencies remain and break at runtime.
- Mitigation: reference sweep and compile/test gate before closure.

## Open Questions
- UNKNOWN: whether any external tests/tools import `MeldEngine` directly.

## Decision Log
- 2026-02-07: No-backcompat cutover approved for this branch.
- 2026-02-07: Overrides/mutations are intentionally unsupported until runtime override codegen lands.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
Story captures the strict cutover phase: make runtime codegen-only now, delete
engine execution path, and intentionally defer override support.


