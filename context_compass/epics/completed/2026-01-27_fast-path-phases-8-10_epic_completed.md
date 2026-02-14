# Epic: Fast-path phases 8-10 (occurrence, injection, patch maps)

- Completed: 2026-01-27
- Summary: Archived Phase 8-10 epic per user direction; Phase 9/10 planning
  tickets completed and Phase 8 tickets archived as recorded.

## Metadata
- Epic ID: EPIC-2026-01-27-fast-path-phases-8-10
- Status: complete
- Owner:
- Priority: p1
- Created: 2026-01-27
- Updated: 2026-01-27
- Target Window: 2026-Q1
- Related Program/Initiative: Fast-path meld plan

## Problem / Opportunity
Phases 8-10 are defined in the fast-path tickets as the compilation steps that
remove per-call occurrence/injection/override work from meld. We need a concrete
implementation plan and tickets for those phases so the runtime can execute
precompiled plans with minimal branching.

Evidence and references:
- context_compass/artifacts/fast_path_meld_plan/ticket_fast_path_github.md
- context_compass/artifacts/fast_path_meld_plan/ticket2_fast_path_github.md
- context_compass/artifacts/fast_path_meld_plan/ticket3_fast_path_github.md
- context_compass/artifacts/fast_path_meld_plan/codex_exploration/meld_route_matrix_2026-01-26.md

## MRP Alignment (Most Reasonable Product)
Define and implement durable Phase 8-10 artifacts (occurrence plan, injection
plan, patch maps) so meld executes precompiled plans without rebuilding graphs
or override structures per call, while preserving correctness via fallback.

## Goals (Outcomes)
- Phase 8: Occurrence plan compiled at conjure from existing blueprints.
- Phase 9: Injection plan compiled at conjure with stable argument wiring.
- Phase 10: Override and mutation patch maps compiled for fast-path patching.
- Clear storage, invalidation, and lifecycle rules for all three artifacts.

## Non-Goals (Explicit Exclusions)
- Phase 11 codegen executor (explicitly deferred).
- Lock policy redesign for Creations.
- Changes to public APIs for Meld/Conduit/Spellbook beyond plan wiring.

## Scope Boundaries
- In scope:
  - Investigation and implementation plan for phases 8-10.
  - Tickets for Phase 8-10 design, compilation, and tests.
  - Updates to fast-path artifacts where needed.
- Out of scope:
  - Phase 11 codegen implementation.
  - Override-heavy runtime redesign outside patch-map approach.

## Success Metrics
- Phase 8-10 tickets exist with clear deliverables and validation steps.
- Each phase has an implementation plan grounded in current code paths.
- Phase 8-10 artifacts are defined with storage + invalidation rules.

## Requirements (Functional + Non-Functional)
- Functional:
  - OccurrencePlan, InjectionPlan, and PatchMap artifacts are defined.
  - Compilers consume Phase 1-7 outputs and emit Phase 8-10 artifacts.
  - Fast-path gating can use Phase 8-10 outputs with fallback.
- Non-functional:
  - No new module-level mutable state.
  - Cleanup and invalidation rules are explicit and testable.

## Constraints / Assumptions
- Phase 1-7 artifacts already exist and remain the source of truth.
- Fast-path gates and fallback remain in meld runtime.

## Dependencies / External References
- src/melder/spellbook/spell_crafter/spell_crafter.py
- src/melder/spellbook/spell_crafter/blueprints/root_resolution_blueprint.py
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py
- src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py
- context_compass/artifacts/fast_path_meld_plan/

## Milestones (Track Progress)
- [ ] Milestone 1: Phase 8 occurrence plan investigation and schema defined.
- [ ] Milestone 2: Phase 9 injection plan investigation and schema defined.
- [ ] Milestone 3: Phase 10 patch map investigation and schema defined.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-01-27-phase-8-occurrence-plan - Compile occurrence plan.
- [ ] Story: STORY-2026-01-27-phase-9-injection-plan - Compile injection plan.
- [ ] Story: STORY-2026-01-27-phase-10-patch-maps - Compile override/mutation patch maps.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete story STORY-2026-01-27-phase-8-occurrence-plan
- [ ] Task: Complete story STORY-2026-01-27-phase-9-injection-plan
- [ ] Task: Complete story STORY-2026-01-27-phase-10-patch-maps

## Acceptance Criteria (Epic Done)
- Phase 8-10 stories and tasks are defined with clear scope and validation.
- Implementation plan explicitly references current code and artifacts.
- Open questions and risks are documented for each phase.

## Risks / Mitigations
- Risk: missing invalidation inputs leads to stale plan reuse.
  Mitigation: define plan signatures and invalidation hooks early.
- Risk: patch maps add complexity without real coverage.
  Mitigation: scope patch maps to explicit override/mutation cases first.

## Validation / Test Approach
- Not run (planning only).
- Each story includes validation criteria and recommended tests.

## Rollout / Adoption Plan
- Land Phase 8-10 artifacts behind fast-path gates.
- Enable in benchmarks first; expand once validated.

## Open Questions
- Where should Phase 8-10 artifacts live (spell vs spellcrafter vs conduit)?
- What signature/epoch fields are required for safe invalidation?
- Which override/mutation cases are patchable without graph rebuild?

## Decision Log
- TBD.

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Epic created to scope and plan phases 8-10 only. Phase 11 is explicitly deferred.
