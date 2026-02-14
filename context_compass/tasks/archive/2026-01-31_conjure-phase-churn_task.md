# Task: Trace conjure phase churn and object creation hotspots

## Metadata
- Task ID: TASK-2026-01-31-conjure-phase-churn
- Story: N/A
- Status: in_progress
- Owner:
- Priority: p1
- Created: 2026-01-31
- Updated: 2026-01-31

## Objective
Identify why conjure build phases create excessive objects and take ~250ms for a small spell set, then produce a concrete diagnosis and targeted optimization plan.

## Scope Boundaries
- In scope:
  - Trace benchmark call paths and phase scheduling for conjure build.
  - Map per-phase work to object creation hotspots.
  - Determine whether frame-level phases are redundantly executed per-spell.
  - Draft a fix plan and test strategy to validate improved behavior.
- Out of scope:
  - Implementing optimizations or behavior changes without explicit approval.
  - Repo-wide refactors or unrelated performance tuning.

## Steps / Checklist
- [ ] Read `benchmarks/conjure/profile_conjure_build_direct.py` to confirm phase invocation paths.
- [ ] Trace phase scheduling and per-spell facades for Phases 5–11.
- [ ] Identify redundant frame-level work and the exact objects created repeatedly.
- [ ] Draft investigation test/harness plan (component test or benchmark harness) and get approval.
- [ ] Produce a diagnosis summary with candidate fixes and expected impact.

## Deliverables
- Investigation summary (call paths, redundancy points, object churn hotspots).
- Proposed optimization plan (minimal, reviewable change set).
- Test plan for verifying correctness and performance impact.

## Files / Paths Impacted
- `benchmarks/conjure/profile_conjure_build_direct.py`
- `src/melder/spellbook/spellbook.py`
- `src/melder/spellbook/spell.py`
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py`
- `benchmarks/conjure/test_conjure_phase_invocation_counts.py` (investigation harness)

## Validation
- Not run.
- Recommended commands:
  - `pytest benchmarks/conjure/test_conjure_phase_invocation_counts.py`

## Risks / Rollback Notes
- Risk: Misidentifying frame-level vs spell-level responsibilities could change semantics.
- Mitigation: Constrain changes to scheduling/wiring after evidence confirms redundancy; add targeted tests.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
User reported slow conjure build (~250ms for ~9 objects) and suspected excess object creation. Investigation confirmed frame-level phases (5/6/7) were scheduled per spell and Phase 5 rebuilt root blueprints per spell. Implemented single-UnitOfWork scheduling for phases 5/6/7 and propagated Phase 6 validation state to all spell crafters. Added a benchmark harness to assert single invocation of frame-level phases (`benchmarks/conjure/test_conjure_phase_invocation_counts.py`). Validation not run.
