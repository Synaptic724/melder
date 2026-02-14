# Story: Compile execution plans during conjure (Phase 8)

## Metadata
- Story ID: STORY-2026-01-25-plan-compilation-phase8
- Epic: EPIC-2026-01-25-fast-path-meld-compiled-plans
- Status: draft
- Owner:
- Priority: p1
- Created: 2026-01-25
- Updated: 2026-01-27

## User Narrative
As a spellbook owner, I want conjure to compile execution plans so that meld
can run without rebuilding occurrence graphs and kwargs on each call.

## Value / MRP Alignment
Moves runtime graph work into conjure, making the optimistic meld path fast and
predictable while preserving existing correctness.

## Requirements (Functional)
- Compile occurrence plan and execution order from RootResolutionBlueprint.
- Compile argument binding recipes from SpellRequirements and DAG data.
- Pre-resolve contract sockets when wiring is stable, otherwise mark plan
  ineligible for fast path.
- Integrate plan compilation into conjure as a new phase.

## Requirements (Non-Functional)
- Plan compilation must be deterministic and reproducible.
- No mutation or override work should occur when inputs are empty.

## Scope Boundaries
- In scope:
  - Occurrence expansion, arg plan compilation, contract wiring checks.
  - Phase 8 integration into SpellCrafter and conjure.
- Out of scope:
  - Fast-path executor and runtime gating.
  - Codegen or Cython work.

## Dependencies / Related Work
- RootResolutionBlueprint from Phase 5
  (src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_root_blueprints).
- Occurrence graph logic in MeldEngine
  (src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_build_occurrence_graph).

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-01-25-plan-compilation-research - Research plan compilation inputs.
- [ ] Task: TASK-2026-01-25-occurrence-plan-compilation - Compile occurrence graph and order.
- [ ] Task: TASK-2026-01-25-arg-plan-compilation - Build arg binding recipes per step.
- [ ] Task: TASK-2026-01-25-contract-resolution-plan - Resolve contract sockets or mark ineligible.
- [ ] Task: TASK-2026-01-25-conjure-phase8-integration - Wire Phase 8 into conjure.
- [ ] Task: TASK-2026-01-25-plan-compilation-tests - Add unit tests for plan compilation.
- [ ] Task: TASK-2026-01-27-phase-8-occurrence-plan-implementation - Implement Phase 8 OccurrencePlan wiring + tests.
- [ ] Task: TASK-2026-01-27-phase-8-runtime-integration - Wire Phase 8 OccurrencePlan into Meld runtime.

## Acceptance Criteria
- Conjure produces RootExecutionPlan for eligible roots.
- Contract sockets that are late-bound mark the plan as fast-path ineligible.
- Plan compilation tests cover occurrence expansion and arg binding.

## Validation / Test Plan
- Not run.
- Recommended: pytest tests/unit/melder/aether/conduit/meld -k plan

## UX / API / Data Notes
- Internal data only; no public API changes.

## Risks / Mitigations
- Risk: plan compilation re-implements MeldEngine incorrectly.
  Mitigation: base plan compiler on existing occurrence and kwargs logic.

## Open Questions
- Should plan compilation run after Phase 6 validation or after Phase 7 wiring?

## Decision Log
- TBD.

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Story created; plan compilation and Phase 8 integration pending.
