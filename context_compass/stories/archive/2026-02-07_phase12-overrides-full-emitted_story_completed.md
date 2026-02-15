Completed: 2026-02-08
Summary: Delivered Phase12 Overrides Full Emitted Executors and confirmed story acceptance criteria.

# Story: Phase12 Overrides Full Emitted Executors

## Metadata
- Story ID: STORY-2026-02-07-phase12-overrides-full-emitted
- Epic: EPIC-2026-02-07-full-aot-codegen-cutover
- Status: done
- Owner:
- Priority: p0
- Created: 2026-02-07
- Updated: 2026-02-08

## User Narrative
As a runtime maintainer, I want override execution fully generated from phase plans,
so no override execution depends on runtime interpreter logic.

## Value / MRP Alignment
Completes generated execution for the dominant dynamic runtime path.

## Requirements (Functional)
- Emit override-specialized executors from override plan + shape key.
- Generated override executors must inline target resolution, root positional
  arg mapping, existing-instance override hard-fails, and lifecycle semantics.
- All override requests must be normalized through Phase10 TargetSpec patch-map
  resolution to SocketRef maps before codegen substitution is applied.
- Compile specialization on shape miss and reuse from bounded cache on hit.
- No generic step-loop fallback.

## Requirements (Non-Functional)
- Bounded, deterministic specialization cache.
- Stable shape keys across equivalent payloads.

## Scope Boundaries
- In scope:
- Override specialization generator and runtime dispatch.
- Out of scope:
- Mutation overrides.

## Dependencies / Related Work
- STORY-2026-02-07-phase-contract-codegen-completeness

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-02-07-phase12-overrides-emitter-core
- [x] Task: TASK-2026-02-07-phase12-overrides-target-routing-and-root-args
- [x] Task: TASK-2026-02-07-phase12-overrides-shape-cache-compiler
- [x] Task: TASK-2026-02-07-override-shape-key-stability-audit
- [x] Task: TASK-2026-02-07-override-specialization-l2-source-cache
- [x] Task: TASK-2026-02-08-phase12-overrides-schema-consumer

## Acceptance Criteria
- Override meld route runs only generated specialization executors.
- Existing-instance override rejection semantics preserved.
- No runtime interpreter helper fallback exists.

## Validation / Test Plan
- Override matrix tests (specificity, conflicts, root args).
- Shape cache hit/miss and eviction tests.

## UX / API / Data Notes
- Reuses existing override frontend payload format.

## Risks / Mitigations
- Risk: shape-key under/over-partitioning.
- Mitigation: explicit key contract tests and benchmarked cache behavior.

## Open Questions
- None.

## Decision Log
- 2026-02-07: override routes must be generated, not interpreted.

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
This story removes interpreter behavior from override runtime paths. Completed
shape-key stability hardening by replacing plan-object identity coupling with
deterministic plan semantics and adding regression tests for equivalent-plan key
reuse and semantic-change invalidation. Added follow-on schema-consumer ticket
to remove remaining override specialization coupling to live `ExecutionPlan`
objects in compile and runtime shape-key paths. Runtime now requires Phase11
override execution IR rows for specialization compile and shape-key signature
construction, and no longer uses live-plan signature fallback paths for override
execution. Override cache behavior now has explicit deterministic ordering and
FIFO eviction tests. Runtime now also supports optional persisted L2 source
cache artifacts for override specializations with strict metadata validation,
corrupt/stale invalidation, and per-spell bounded eviction. A follow-up emitter
pass removed `_resolve_step_instance_with_overrides` from generated execution
flow and inlined override-aware step semantics directly in emitted source
blocks. Added direct regressions for root-override and targeted-override
rejection when shared instances already exist.

