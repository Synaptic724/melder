Completed: 2026-02-08
Summary: Closed and turned in for Runtime Migration and Codegen Cutover.

# Story: Runtime Migration and Codegen Cutover

## Metadata
- Story ID: STORY-2026-02-08-runtime-migration-codegen-cutover
- Epic: EPIC-2026-02-08-spell-owned-creation-context-cutover
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-08
- Updated: 2026-02-08

## User Narrative
As a performance-focused runtime engineer, I want runtime resolver and execution internals moved into spell-owned `CreationContext`, so that the hot path uses specialized lanes with minimal call overhead.

## Value / MRP Alignment
This story delivers the core performance outcome: runtime work lives in one spell-specialized executor object with direct lane dispatch. That is the architecture needed to reduce repeated call stack overhead.

## Requirements (Functional)
- Migrate `_resolver` and all supporting runtime helpers from meld-owned context flow into spell-owned `CreationContext`.
- Keep two lanes in spell-owned context:
  - normal lane (no overrides)
  - overrides lane
- Preserve current existence semantics and lock usage contracts for creations/spell locks.
- Preserve override specialization behavior using phase 10/11/12 artifacts.
- Bind and reuse lane executors in spell-owned context for repeated calls.
- Remove replaced legacy runtime helpers/classes once cutover is complete.

## Requirements (Non-Functional)
- No backward compatibility layers.
- No extra polymorphic command dispatch object graph if it adds overhead without measurable gain.
- Keep fast lane branch bias toward no-overrides path.

## Scope Boundaries
- In scope:
  - Runtime helper migration into spell-owned context class(es).
  - Lane specialization and codegen wiring inside spell-owned context.
  - Deletion of replaced legacy runtime path files/symbols.
- Out of scope:
  - New override feature semantics.
  - New spell lifecycle invalidation engine.

## Dependencies / Related Work
- `src/melder/aether/conduit/meld/meld_context/creation_context.py:CreationContext._resolver`
- `src/melder/aether/conduit/meld/meld_context/creation_context.py:CreationContext._dispatch_meld_runtime`
- `src/melder/aether/conduit/meld/meld_context/creation_context.py:CreationContext._execute_no_overrides`
- `src/melder/aether/conduit/meld/meld_context/creation_context.py:CreationContext._execute_with_overrides`
- `src/melder/aether/conduit/meld/meld_context/meld_context.py:MeldContext`

## Tasks (Implementation Checklist)
- [x] Task: `TASK-2026-02-08-migrate-runtime-resolver-into-creation-context` - move resolver/supporting methods into spell-owned runtime object.
- [x] Task: `TASK-2026-02-08-creation-context-lane-specialization-and-codegen` - finalize normal/override lane specialization and codegen wiring.
- [x] Task: `TASK-2026-02-08-delete-legacy-meldcontext-runtime-path` - remove obsolete runtime path objects and stale symbols.
- [x] Task: `TASK-2026-02-08-creation-context-architecture-components-docs` - sync architecture/component docs after cutover.

## Acceptance Criteria
- Runtime resolver and execution internals are owned by spell-owned context.
- Context execute path selects normal/override lane with no extra meld runtime delegation layer.
- Existing existence lock behavior remains correct.
- Replaced legacy runtime context/path code is deleted.

## Validation / Test Plan
- Not run.
- Planned validation:
  - Unit parity tests for existence routing and lock behavior.
  - Unit parity tests for override lane semantics.
  - Benchmark comparison of hot-path call depth and runtime delta.

## UX / API / Data Notes
- External `meld(...)` behavior remains the same.
- Internal execution call graph is reduced and re-owned by spell context.

## Risks / Mitigations
- Risk: migration misses a helper path and creates partial behavior regression.
  - Mitigation: migrate by method cluster and remove old path in same change.
- Risk: codegen lane binding keeps hidden dependency on removed runtime context.
  - Mitigation: wire lane inputs through explicit context contract only.

## Open Questions
- UNKNOWN: residual benchmark delta after removing `MeldContext` and switching to direct creations params.
  - Evidence target: benchmark suite under `benchmarks/testing_other_di/` and meld runtime benchmarks.

## Decision Log
- 2026-02-08: runtime methods move into spell-owned context object.
- 2026-02-08: no compatibility shim path after migration.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
This story now has the hard runtime cutover implemented in code:
- `MeldContext` runtime files are deleted.
- Runtime executors consume direct creations parameters.
- `CreationContext` owns routing and generated executor dispatch without context pooling.
Next step is validation breadth (unit/bench) and user acceptance.
