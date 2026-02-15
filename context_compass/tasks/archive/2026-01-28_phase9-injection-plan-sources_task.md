# Task: Expand Phase 9 InjectionPlan to encode overrides and contracts

## Metadata
- Task ID: TASK-2026-01-28-phase9-injection-plan-sources
- Story: STORY-2026-01-28-meld-runtime-phase-artifacts
- Status: completed
- Owner: codex
- Priority: p1
- Created: 2026-01-28
- Updated: 2026-01-28

## Objective
Extend Phase 9 InjectionPlan so it fully describes dependency, override, and
SpellContract sources, allowing MeldEngine to build kwargs without runtime
merge logic while preserving existing behavior.

## Scope Boundaries
- In scope:
  - Update InjectionPlanBuilder to include ParamSource kinds for overrides and
    SpellContract payloads.
  - Update MeldEngine to consume the enriched InjectionPlan for kwargs building.
- Out of scope:
  - Any semantic changes to override precedence or contract behavior.
  - Changes outside meld runtime/engine and SpellCrafter Phase 9.

## Steps / Checklist
- [x] Map current override/contract precedence in MeldEngine (evidence-based).
- [x] Define InjectionPlan param source kinds and fields needed to encode precedence.
- [x] Update InjectionPlanBuilder to emit those sources from OccurrencePlan data.
- [x] Update MeldEngine to rely on InjectionPlan for full kwargs assembly.
- [x] Add/adjust tests to confirm behavior parity.

## Deliverables
- InjectionPlan encodes override and contract sources with precedence preserved.
- MeldEngine uses InjectionPlan without runtime merging for those sources.

## Files / Paths Impacted
- src/melder/spellbook/spell_crafter/blueprints/injection_plan.py
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py
- tests/unit/melder/aether/conduit/meld/
- tests/unit/melder/spellbook/spell_crafter/

## Validation
- PYTHONPATH=/workspace/melder_private pytest -q

## Risks / Rollback Notes
- Risk: subtle precedence drift between overrides and contract payloads.
- Rollback: revert InjectionPlan changes and restore MeldEngine merge path.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Created to extend Phase 9 InjectionPlan with override/contract sourcing so runtime
behavior can migrate out of MeldEngine without semantic changes.
