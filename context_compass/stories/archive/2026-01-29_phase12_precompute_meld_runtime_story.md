# Story: Phase 12 precomputes meld runtime planning artifacts

## Metadata
- Story ID: STORY-2026-01-29-phase12-precompute-meld-runtime
- Epic: N/A
- Status: in_progress
- Owner:
- Priority: p0
- Created: 2026-01-29
- Updated: 2026-01-29

## User Narrative
As a system owner, I want Phase 12 to precompute the remaining meld-engine planning work (root creations maps, flap map, true spell refs, override-capable routing, etc.) so meld execution only performs minimal runtime assembly and instance creation.

## Value / MRP Alignment
Moves remaining execution planning into the phase system so runtime meld is deterministic, lightweight, and override-capable while preserving correctness.

## Requirements (Functional)
- Phase 12 precomputes all feasible MeldEngine planning outputs (root creations mapping, flap map, true spell references, instance routing, contract/override payload lookup) and packages them as phase artifacts.
- Phase 12 artifacts must remain valid with overrides and mutation overrides; the runtime should use precomputed routing plus per-call override payloads without rebuilding plans.
- MeldRuntime should execute via a minimal assembly function that takes creations + precomputed artifacts and constructs instances without recomputing routing.
- Define explicit boundaries for what cannot be precomputed (e.g., per-call override payload values, live creations containers, cancellation checks).
- Phase 12 plans must include optimistic object refs keyed by spell id and an "available" param that maps spell types to creations targets.
- Phase 12 should emit multiple plan variants, including a no-overrides fast path and override/mutation-aware paths, with explicit selection gates.
- Phase 12 is the terminal execution stage: it returns the root object and delegates creations placement without engine-side re-planning.

## Requirements (Non-Functional)
- Preserve correctness of override/contract behavior.
- Keep artifacts immutable and cleanable.
- Avoid new module-level mutable state.

## Scope Boundaries
- In scope:
  - Full audit of MeldEngine/MeldRuntime runtime computations to identify precomputable outputs.
  - Define Phase 12 artifact schema capturing root creations flap map, true spell refs, and execution routing metadata.
  - Draft the minimal runtime execution/assembly flow with explicit inputs.
  - Ticket the code changes and test plan for the Phase 12 implementation.
- Out of scope:
  - Implementing Phase 12 artifacts and runtime changes (separate implementation task).
  - Performance benchmarking.

## Dependencies / Related Work
- Story: STORY-2026-01-29-phase11-execution-plan-precompute
- Task: TASK-2026-01-29-phase12-feasibility-scan
- Artifact: context_compass/artifacts/phase12_precompute_meld_runtime/phase12_precompute_audit.md

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-01-29-phase12-precompute-meld-runtime - Investigate and design Phase 12 precompute artifacts
- [ ] Task: TASK-2026-01-29-phase12-runtime-execution-implementation - Substitute Phase 12 execution in runtime/engine

## Acceptance Criteria
- Documented inventory of MeldEngine runtime computations and which move to Phase 12.
- Proposed Phase 12 artifact schema covering root creations flap map, true spell refs, and override-capable routing data.
- Defined minimal runtime execution function signature and flow (inputs/outputs).
- Implementation plan + tests outlined for the Phase 12 build.

## Validation / Test Plan
- Not run (planning-only).

## UX / API / Data Notes
- Phase 12 artifacts may adjust internal data models but should preserve public API behavior.

## Risks / Mitigations
- Risk: Over-precomputing yields stale artifacts when overrides change.
  - Mitigation: separate mutable per-call payloads from immutable routing plans and include plan/version gating.
- Risk: Creations container layout prevents safe precomputation.
  - Mitigation: limit Phase 12 to routing/lookup metadata and keep creations references runtime-bound.

## Open Questions
- What is the exact definition and expected shape of the root creations flap map?
- Which MeldEngine steps truly depend on live creations containers vs. pure routing metadata?

## Decision Log
- 2026-01-29: Phase 12 should move remaining meld-engine planning into precomputed artifacts, leaving only minimal runtime assembly.
- 2026-01-29: Confirmed Option A (new Phase 12 ExecutionAssemblyPlan), Option D1 (routing table creations delegation), and Option E1 (pre-resolved refs with validation).

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
- Phase 12 precompute audit expanded with a method-by-method extraction map (instance routing, creations targeting, lock hints, optimistic ref validation) plus a confirmed direction to pursue Option A (new Phase 12 ExecutionAssemblyPlan), Option D1 (routing table creations delegation), and Option E1 (pre-resolved refs with validation). Phase 11 now selects plan variants by override/mutation presence and MeldRuntime precomputes override targets/flags to remove duplicated override detection ahead of Phase 12. Phase 12 is intended to be the final execution stage that returns the root instance and delegates creations placement.
- Implementation started: SpellCrafter now compiles Phase 12 ExecutionAssemblyPlan variants with the new builder scaffolding.
