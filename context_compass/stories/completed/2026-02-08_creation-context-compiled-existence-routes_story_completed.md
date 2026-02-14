Completed: 2026-02-08
Summary: Closed and turned in for Compile Existence Routes Inside CreationContext.

# Story: Compile Existence Routes Inside CreationContext

## Metadata
- Story ID: STORY-2026-02-08-creation-context-compiled-existence-routes
- Epic: EPIC-2026-02-08-creation-context-end-to-end-existence-codegen
- Status: done
- Owner: Codex
- Priority: p0
- Created: 2026-02-08
- Updated: 2026-02-08

## User Narrative
As a performance-focused melder maintainer, I want `CreationContext` to execute through compiled existence-specific routes, so that each meld call pays minimal Python dispatch overhead from entrance to final instance return.

## Value / MRP Alignment
This story hardens the spell-owned runtime core by moving existence orchestration into generated executors, matching the phase12 codegen strategy and reducing interpreted call chains.

## Requirements (Functional)
- Add a codegen module that emits and compiles existence lane executors.
- Bind compiled no-overrides and with-overrides executors onto `CreationContext`.
- Preserve current semantics for:
  - override rejection on existing instances
  - lock ordering
  - registration/reuse behavior by existence type

## Requirements (Non-Functional)
- Keep `CreationContext.execute` as a two-lane entrance.
- Avoid defensive normalization in hot path.
- Keep cleanup deterministic and idempotent.

## Scope Boundaries
- In scope:
  - `creation_context.py`, new codegen module, builder wiring.
  - benchmark validation for melder.
- Out of scope:
  - API changes to `Meld.meld`.
  - phase12 emitter contract redesign.

## Dependencies / Related Work
- Task: TASK-2026-02-08-creation-context-codegen-module
- Task: TASK-2026-02-08-creation-context-builder-binding
- Task: TASK-2026-02-08-creation-context-benchmark-validation

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-02-08-creation-context-codegen-module - Add compiler for existence lane source
- [x] Task: TASK-2026-02-08-creation-context-builder-binding - Wire builder/context to compiled routes
- [x] Task: TASK-2026-02-08-creation-context-benchmark-validation - Validate benchmark and compile checks

## Acceptance Criteria
- `CreationContext.execute` dispatches into compiled route callables (no interpreted route matrix).
- Existence-specific paths are compiled for all supported existences.
- Benchmark run completed and reported.

## Validation / Test Plan
- `py_compile` on touched files.
- melder single timings benchmark slice.
- melder rotation benchmark slice.

## UX / API / Data Notes
- No public API changes expected.

## Risks / Mitigations
- Risk: compiled source branch drift from current semantics.
  - Mitigation: preserve existing branch and lock behavior exactly in generated source.

## Open Questions
- UNKNOWN: whether additional gains require inlining more override payload processing into generated source.

## Decision Log
- 2026-02-08: prioritize existence-level codegen cutover first, then consider deeper override-lane inlining.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
Story is active and tied directly to user request for full existence route codegen in `CreationContext`.
