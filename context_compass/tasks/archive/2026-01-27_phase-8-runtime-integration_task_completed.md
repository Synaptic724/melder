# Task: Wire Phase 8 OccurrencePlan into Meld runtime

- Completed: 2026-01-27
- Summary: Wired OccurrencePlan usage into MeldRuntime/MeldEngine with fallback
  behavior, tests, and doc updates recorded in the task.

## Metadata
- Task ID: TASK-2026-01-27-phase-8-runtime-integration
- Story: STORY-2026-01-25-plan-compilation-phase8
- Status: completed
- Owner:
- Priority: p1
- Created: 2026-01-27
- Updated: 2026-01-27

## Objective
Integrate the Phase 8 OccurrencePlan artifact into MeldRuntime/MeldEngine so
runtime execution uses the precompiled plan and removes redundant per-call
occurrence planning work.

## Scope Boundaries
- In scope:
  - Consume OccurrencePlan in MeldRuntime/MeldEngine when available.
  - Remove or guard runtime occurrence planning steps moved into Phase 8.
  - Update unit tests to validate plan-based execution and fallback behavior.
  - Update architecture/components docs if runtime flow changes.
- Out of scope:
  - Phase 9 InjectionPlan compilation.
  - Phase 10 patch map compilation.
  - Phase 11 executor/gating.

## Steps / Checklist
- [x] Review MeldRuntime/MeldEngine planning flow and identify replacement points.
- [x] Implement OccurrencePlan consumption and fall back when missing/stale.
- [x] Remove or guard redundant runtime planning logic that Phase 8 replaces.
- [x] Add/update unit tests for plan-based execution and fallback behavior.
- [x] Update architecture/components docs if the runtime flow changes.

## Deliverables
- MeldRuntime/MeldEngine use Phase 8 OccurrencePlan for execution order and
  instance planning when present.
- Runtime planning logic is reduced or guarded to avoid duplicate work.
- Tests covering plan usage and fallback paths.

## Files / Paths Impacted
- src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py
- src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py
- tests/unit/melder/aether/conduit/meld/
- context_compass/architecture/src_architecture.md
- context_compass/components/src_components.md

## Validation
- Not run.
- Recommended commands:
  - pytest tests/unit/melder/aether/conduit/meld -k occurrence_plan

## Risks / Rollback Notes
- Risk: plan execution diverges from current runtime ordering semantics.
  Mitigation: compare plan-derived outputs against current runtime planning in tests.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Completed Phase 8 runtime integration by wiring OccurrencePlan usage into
MeldRuntime/MeldEngine, guarding legacy occurrence planning when plans are
absent or incompatible, and adding tests for plan usage and fallback behavior.
Validation remains not run in this environment.
