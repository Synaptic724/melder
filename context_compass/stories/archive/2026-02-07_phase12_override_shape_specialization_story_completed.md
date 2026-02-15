Completed: 2026-02-07
Summary: Completed override re-enable path using Phase12 specialization codegen with bounded caching and no engine fallback.

# Story: Phase 12 Override-Shape Specialization

## Metadata
- Story ID: STORY-2026-02-07-phase12-override-shape-specialization
- Epic: EPIC-2026-02-07-phase12-spell-scoped-execution
- Status: done
- Owner:
- Priority: p1
- Created: 2026-02-07
- Updated: 2026-02-07

## User Narrative
As a performance-focused runtime owner, I want repeated override shapes to compile into reusable spell-scoped specializations, so repeated override calls can run a locked-in fast path.

## Value / MRP Alignment
Re-enables overrides through runtime codegen after the codegen-only cutover,
without reintroducing `MeldEngine` or fallback execution paths.

## Requirements (Functional)
- Preserve and consume the existing override frontend targeting contract
  (TargetSpec wildcard/path -> SocketRef maps from Phase 10).
- Normalize override input into a stable shape signature.
- Build and cache specialization executors by spell + shape signature.
- Reuse specialization executors on repeated calls with same shape.

## Requirements (Non-Functional)
- Bounded cache size with deterministic eviction.
- No fallback to engine/baseline execution path on this branch.

## Scope Boundaries
- In scope:
- Specialization keying and cache lifecycle.
- Runtime selection and compilation routing for override executors.
- Out of scope:
- Full mutation-aware specialization in first cut.
- Global cross-spell specialization sharing.

## Dependencies / Related Work
- `context_compass/stories/completed/2026-02-07_phase12_no_overrides_executor_story_completed.md`

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-02-07-override-frontend-socketref-contract - Lock frontend targeting contract for runtime override codegen input.
- [x] Task: TASK-2026-02-07-override-shape-signature-contract - Define stable override-shape signature contract.
- [x] Task: TASK-2026-02-07-override-specialization-cache - Implement bounded spell-scoped specialization cache.
- [x] Task: TASK-2026-02-07-override-specialization-runtime-routing - Route runtime to specialization executors by shape key.

## Acceptance Criteria
- Override runtime codegen consumes Phase 10 frontend targeting payloads directly.
- Repeated override shapes hit cached specialization path.
- Cache remains bounded and eviction behavior is deterministic.
- Runtime does not depend on `MeldEngine` for override execution.

## Validation / Test Plan
- Unit tests for signature stability, cache hit/miss, and eviction.
- Integration tests covering override correctness parity.

## UX / API / Data Notes
- Internal optimization only; no API surface changes.

## Risks / Mitigations
- Risk: overspecialization causing cache churn.
- Mitigation: strict shape keying and bounded per-spell cache.
- Risk: frontend targeting payload drift from Phase 10 semantics.
- Mitigation: contract task and parity tests against patch-map targeting outputs.

## Open Questions
- Include root spell id only, or full plan variant signature in specialization key?
- Should specialization compile eagerly on first miss or lazily after N repeats?

## Decision Log
- 2026-02-07: Deferred behind no-overrides Phase 12 cutover.
- 2026-02-07: Overrides remain unsupported until this story is complete.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
Story now captures the exact re-enable path for overrides in the no-backcompat
branch: preserve current frontend mapping semantics and add runtime override codegen.

