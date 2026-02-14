# Phase 9 InjectionPlan Compiler Plan (2026-01-27)

## Purpose
Define where Phase 9 compiles the InjectionPlan in the SpellCrafter pipeline
and how the runtime will consume it.

## Evidence Anchors
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_build_kwargs_for_instance`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_build_instance_override_map`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_build_kwargs_for_instance_from_plan`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_select_injection_plan`
- `src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py:execute`
- `src/melder/spellbook/spell_crafter/spell_crafter.py:run_all_phases`
- `src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_injection_plan`

## Phase 9 Insertion Point (Draft)
Phase 9 depends on Phase 8 outputs (OccurrencePlan). Therefore:
- Insert Phase 9 after Phase 8 in SpellCrafter.

Rationale:
- InjectionPlan uses occurrence graph + instance plan.
- It can be compiled from Phase 8 outputs without additional graph work.

## Compiler Responsibilities
Derived from `_build_kwargs_for_instance`:
- Precompute dependency wiring per instance key.
- Record override precedence rules (override > contract > deps).
- Record positional override handling (`__args__`).

## Proposed SpellCrafter API
Add:
- `run_phase_injection_plan(conduit_id, cancel_event=None)`
Store:
- `_injection_plan_phase9` on SpellCrafter (draft field).

Add Spell facade:
- `Spell.run_phase_injection_plan(conduit_id, cancel_event=None)`

## Data Flow
Inputs:
- OccurrencePlan (Phase 8 output).
- Spell requirements / resolution frame (parameter names).
- Contract socket metadata (from local topology / requirements).

Outputs:
- InjectionPlan artifact (see `phase9_injection_plan_schema.md`).

## Revalidation Integration
Update `SpellCrafter.run_all_phases` to include Phase 9 after Phase 8 when
fast-path compilation is enabled, so change-control revalidation refreshes
InjectionPlan along with Phase 8.

## Runtime Gating
- Only reuse the InjectionPlan when the Phase 8 OccurrencePlan is accepted.
- Disable plan reuse when mutation overrides are present to avoid stale wiring.

## Tests (Draft)
- Unit: compare InjectionPlan-generated kwargs vs runtime kwargs for a known
  blueprint (no overrides).
- Integration: Phase 9 outputs remain aligned when Phase 8 is regenerated.
- Unit: ensure InjectionPlan is ignored when OccurrencePlan is rejected.

## Open Questions
- Should override handling be excluded from Phase 9 and deferred to Phase 10?
- Where should contract override payloads live (Phase 9 vs Phase 10)?
