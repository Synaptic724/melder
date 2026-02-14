Completed: 2026-02-07
Summary: Closed per reprioritization directive; superseded by full AOT codegen epic and ticket set.

# Epic: Phase 12 Spell-Scoped Execution

## Metadata
- Epic ID: EPIC-2026-02-07-phase12-spell-scoped-execution
- Status: in_progress
- Owner:
- Priority: p0
- Created: 2026-02-07
- Updated: 2026-02-07
- Target Window: 2026-Q1
- Related Program/Initiative: Meld hotpath simplification

## Problem / Opportunity
`MeldRuntime` still contains mixed execution ownership across spell-scoped
artifacts and runtime assembly logic. `MeldEngine` remains in the runtime path,
which keeps execution policy fragmented and blocks full codegen migration.

## MRP Alignment (Most Reasonable Product)
Move to a pure codegen execution model where SpellCrafter owns executable
artifacts and runtime is dispatch-only. No backward-compat fallback paths.

## Goals (Outcomes)
- Remove `MeldEngine` from active meld execution paths.
- Make no-overrides execution fully spell-scoped Phase 12 codegen.
- Disable overrides/mutations until runtime override codegen strategy lands.
- Retain override frontend targeting (TargetSpec wildcard/path + SocketRef maps)
  as the canonical input contract for future override codegen.

## Non-Goals (Explicit Exclusions)
- Public API redesign for `Conduit.meld`.
- Supporting overrides/mutations during no-overrides cutover.
- Cross-module refactors outside SpellCrafter/MeldRuntime/Meld.

## Scope Boundaries
- In scope:
- Spell-scoped Codegen IR and Phase 12 no-overrides artifact generation.
- Runtime cutover to Phase 12-only no-overrides execution.
- Runtime hard-fail behavior for overrides/mutations until future story lands.
- Removal of `MeldEngine` execution integration.
- Out of scope:
- Non-meld subsystems.
- Global repo-wide cleanup.

## Success Metrics
- No no-overrides path in `MeldRuntime` instantiates or executes `MeldEngine`.
- No-overrides execution is served by spell-scoped Phase 12 executor artifacts.
- Overrides/mutations fail deterministically with explicit unsupported messaging.

## Requirements (Functional + Non-Functional)
- Functional: compile and store per-spell no-overrides executors from phase-produced IR.
- Functional: runtime executes Phase 12 executor directly for no-overrides paths.
- Functional: runtime rejects override/mutation execution until override codegen is implemented.
- Non-functional: remove fallback branches and mixed execution ownership.

## Constraints / Assumptions
- Phase 11 artifacts remain the semantic source of truth.
- Override frontend targeting remains in Phase 10 patch maps and is reused for future codegen.

## Dependencies / External References
- `context_compass/tasks/2026-02-07_codegen_fast_transient_task.md`
- `context_compass/artifacts/phase12_precompute_meld_runtime/phase12_precompute_audit.md`

## Milestones (Track Progress)
- [x] Milestone 1: Phases 1-11 emit stable Codegen IR artifacts required by Phase 12.
- [x] Milestone 2: Phase 12 no-overrides artifact contract + compiler integrated in SpellCrafter.
- [x] Milestone 3: MeldRuntime no-overrides routes use Phase 12 only and no fallback branches.
- [x] Milestone 4: `MeldEngine` execution integration removed from meld runtime.
- [x] Milestone 5: Override runtime codegen strategy implemented and overrides re-enabled.

## Stories (Required to Complete)
- [x] Story: STORY-2026-02-07-phase11-ir-data-harvest - Augment phases 1-11 to produce spell-scoped Codegen IR.
- [x] Story: STORY-2026-02-07-phase12-no-overrides-executor - Compile and execute spell-scoped no-overrides executors.
- [x] Story: STORY-2026-02-07-phase12-codegen-only-cutover - Remove engine execution path and disable overrides/mutations.
- [x] Story: STORY-2026-02-07-phase12-override-shape-specialization - Add runtime specialization cache for recurring override shapes.

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: Complete story STORY-2026-02-07-phase11-ir-data-harvest
- [x] Task: Complete story STORY-2026-02-07-phase12-no-overrides-executor
- [x] Task: Complete story STORY-2026-02-07-phase12-codegen-only-cutover
- [x] Task: Complete story STORY-2026-02-07-phase12-override-shape-specialization
- [x] Task: TASK-2026-02-07-phase12-cutover-validation - Run cutover validation + benchmark deltas.

## Acceptance Criteria (Epic Done)
- No no-overrides runtime path depends on `MeldEngine`.
- Spell-scoped no-overrides executor path is active and validated.
- Overrides/mutations are explicitly unsupported until override runtime codegen story is complete.
- Override specialization path has explicit gates and cache bounds.

## Risks / Mitigations
- Risk: immediate override behavior break after cutover.
- Mitigation: explicit hard-fail messaging and dedicated override codegen story.
- Risk: codegen artifact drift from phase semantics.
- Mitigation: deterministic IR signatures and phase-to-IR contract tests.
- Risk: specialization cache growth for overrides.
- Mitigation: bounded cache and deterministic eviction.

## Validation / Test Approach
- Targeted unit coverage for SpellCrafter artifact compilation and runtime dispatch.
- Focused integration tests for no-overrides execution parity and deterministic override hard-fails.
- Benchmark comparison before/after cutover.

## Rollout / Adoption Plan
- Ship no-overrides executor path as the only runtime path.
- Remove engine execution integration in the same cutover track.
- Re-introduce override support only through runtime override codegen story.

## Open Questions
- What cache key granularity for override-shape specialization gives best reuse without overfitting?
- Should specialization be per spell id only or include plan variant signature and conduit state?

## Decision Log
- 2026-02-07: Runtime-generalized codegen deemed too coupled; move to spell-scoped exact artifacts.
- 2026-02-07: No backward compatibility fallback is required for this migration branch.
- 2026-02-07: Overrides/mutations are disabled until runtime override codegen path is implemented.
- 2026-02-07: Phase 12 compiler input contract must be produced incrementally by phases 1-11 before cutover.

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Epic is now scoped to a strict no-backcompat cutover: codegen-only no-overrides
execution, engine-path removal, override/mutation temporary disablement, then
future override runtime codegen with existing TargetSpec/SocketRef frontend.

