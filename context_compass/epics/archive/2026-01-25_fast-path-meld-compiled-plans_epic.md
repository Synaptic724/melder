# Epic: Fast-path meld compiled execution plans

## Metadata
- Epic ID: EPIC-2026-01-25-fast-path-meld-compiled-plans
- Status: draft
- Owner:
- Priority: p0
- Created: 2026-01-25
- Updated: 2026-01-25
- Target Window: 2026-Q1
- Related Program/Initiative: Performance / meld hot path

## Problem / Opportunity
Meld runtime still builds execution structures per call even when no overrides or
mutations are present. Evidence:
- MeldRuntime.execute constructs a ResolutionFrame, applies GraphMutator and
  SpellOverrider when a RootResolutionBlueprint is present, and runs MeldEngine
  (src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py).
- MeldEngine builds a path-aware occurrence graph and per-call instance plan
  (src/melder/aether/conduit/meld/meld_engine/meld_engine.py).
- Conjure Phase 5 already builds RootResolutionBlueprints and a SpellSystemIndex
  (src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_root_blueprints).

User-reported benchmarks indicate large gaps versus other DI containers.
UNKNOWN: confirm with benchmarks after fast-path work.

## MRP Alignment (Most Reasonable Product)
Deliver a trustworthy fast path that preserves correctness while frontloading
graph work into conjure. The core experience is predictable, fast resolution
with explicit fallback to existing runtime behavior.

## Goals (Outcomes)
- Compile per-root execution plans during conjure to avoid runtime graph work.
- Provide a fast-path executor that skips overrides and mutation work when absent.
- Preserve existing behavior via clean fallback to MeldRuntime and MeldEngine.

## Non-Goals (Explicit Exclusions)
- Full optimization of override-heavy or mutation-heavy workloads in v1.
- Removing all locks in the system.
- Changing public API semantics for Meld, Conduit, or Spellbook.

## Scope Boundaries
- In scope:
  - RootExecutionPlan data model and plan cache lifecycle.
  - Conjure-time compilation from RootResolutionBlueprints.
  - Fast-path gating and execution in meld runtime.
  - Override and mutation patch maps for fast-path variants.
  - Observability and benchmark instrumentation.
  - Optional codegen or Cython feasibility work.
- Out of scope:
  - New configuration properties beyond what is required for gating.
  - Mutation pipeline redesign.
  - Contract or ACL behavior changes.

## Success Metrics
- Fast-path hit rate and fallback reasons are observable.
- Warm root resolves are microsecond-scale in the optimistic case.
- Cold root resolves are sub-millisecond for typical deep graphs.

## Requirements (Functional + Non-Functional)
- Functional:
  - RootExecutionPlan compiled per root and per conduit.
  - Fast path executes without GraphMutator or SpellOverrider when no overrides.
  - Fallback to current runtime path when gating fails.
- Non-functional:
  - Plan invalidation is correct when wiring or validity changes.
  - No new module-level mutable state.
  - Cleanup is deterministic and preserves existing semantics.

## Constraints / Assumptions
- Conjure can increase in cost if meld hot path improves.
- Plan signature must include conduit wiring state to avoid stale reuse.
- Change-control dirty roots must still block fast path.

## Dependencies / External References
- src/melder/spellbook/spell_crafter/spell_crafter.py
- src/melder/spellbook/spell_crafter/blueprints/root_resolution_blueprint.py
- src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py
- src/melder/aether/conduit/meld/overrides/graph_mutator.py
- src/melder/aether/conduit/meld/overrides/spell_overrider.py
- src/melder/aether/dev_ops/change_control_manager/change_control_manager.py
- context_compass/artifacts/fast_path_meld_plan/

## Milestones (Track Progress)
- [ ] Milestone 1: Plan model and compilation pipeline defined and wired into conjure.
- [ ] Milestone 2: Fast-path executor and gating logic integrated with fallback.
- [ ] Milestone 3: Observability and optional codegen feasibility complete.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-01-25-compiled-plan-model - Define plan model and lifecycle.
- [ ] Story: STORY-2026-01-25-plan-compilation-phase8 - Compile plans during conjure.
- [ ] Story: STORY-2026-01-25-fast-path-runtime - Fast-path executor and gating.
- [ ] Story: STORY-2026-01-25-override-mutation-fast-path - Patch maps and override fast path.
- [ ] Story: STORY-2026-01-25-fast-path-observability - Metrics and benchmark harness.
- [ ] Story: STORY-2026-01-25-fast-path-codegen - Optional codegen and Cython spike.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete story STORY-2026-01-25-compiled-plan-model
- [ ] Task: Complete story STORY-2026-01-25-plan-compilation-phase8
- [ ] Task: Complete story STORY-2026-01-25-fast-path-runtime
- [ ] Task: Complete story STORY-2026-01-25-override-mutation-fast-path
- [ ] Task: Complete story STORY-2026-01-25-fast-path-observability
- [ ] Task: Complete story STORY-2026-01-25-fast-path-codegen

## Acceptance Criteria (Epic Done)
- Compiled plans are produced at conjure and used by a fast-path executor.
- Gating is correct and fallbacks preserve existing behavior.
- Observability captures fast-path hit rate and fallback reasons.
- Optional codegen feasibility is evaluated and documented.

## Risks / Mitigations
- Risk: stale plan use due to missing invalidation inputs.
  Mitigation: define plan signature and invalidate on wiring or validity changes.
- Risk: conjure time increases significantly.
  Mitigation: quantify and document cost; cache plans per conduit.
- Risk: codegen adds complexity.
  Mitigation: keep optional and gated behind configuration.

## Validation / Test Approach
- Not run.
- Targeted unit and integration tests per story.
- Benchmarks in benchmarks/testing_other_di for comparison once implemented.

## Rollout / Adoption Plan
- Land plan model and compiler behind fast-path gating flag.
- Enable fast path for benchmark harness first, then broader usage.

## Open Questions
- What exact contract wiring signature is required to invalidate a plan safely?
- Do we need plan variants for hooks enabled or disabled?
- Should the optimistic cache hit avoid locks for shared existences?
- Where should plan storage live (blueprint, spell, or conduit)?

## Decision Log
- TBD.

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Epic created from the user request to frontload meld runtime work into conjure
via compiled execution plans and fast-path execution.
Artifacts folder created at context_compass/artifacts/fast_path_meld_plan/ for
research notes and evidence snapshots.
