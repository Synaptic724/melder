# Phase 8 OccurrencePlan Compiler Plan (2026-01-27)

## Purpose
Define where Phase 8 compiles OccurrencePlan inside the SpellCrafter pipeline,
what inputs it consumes, and how it integrates with revalidation and cleanup.

## Evidence Anchors
- `src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_root_blueprints`
- `src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_system_validation`
- `src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_change_control`
- `src/melder/spellbook/spell_crafter/spell_crafter.py:run_all_phases`
- `src/melder/spellbook/spell.py:run_all_phases`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:MeldEngine.run`

## Phase 8 Insertion Point (Draft)
Phase 8 depends on Phase 5 artifacts (RootResolutionBlueprint, DagIndex,
ordered_node_ids) and on topology from Phase 3. Evidence for Phase 5 output
availability is `run_phase_root_blueprints`.

Candidate insertion point:
- After Phase 5 (root blueprints) and before Phase 6.

Rationale:
- Phase 8 uses Phase 5 outputs directly; Phase 6 validates them but does not
  materially change them.
- If Phase 6 fails, we can still drop the fast plan; no need to block Phase 8
  compilation.

UNKNOWN:
- Whether Phase 8 should be gated by Phase 6 validity to avoid compiling for
  invalid roots.

## Compiler Responsibilities (Phase 8)
Derived from `MeldEngine.run`:
- Build occurrence graph for the root blueprint DAG.
- Extend occurrence graph using ordered_node_ids.
- Compute execution order from occurrence dependencies.
- Build instance plan (instance keys + canonical occurrences + root key).

These are the direct replacements for the per-call planning steps.

## Proposed SpellCrafter API
Add new methods (SpellCrafter):
- `run_phase_occurrence_plan(conduit_id, cancel_event=None)`
  - Requires Phase 5 artifacts on the root spell crafter.
  - Stores OccurrencePlan on the root crafter (or blueprint).

Add new facades (Spell):
- `run_phase_occurrence_plan(conduit_id, cancel_event=None)`
  - Delegates to SpellCrafter method above.

Update `Spell.run_all_phases` to include Phase 8 when enabled, so that
ChangeControl revalidation can rerun Phase 8 as part of the existing pipeline.

Evidence for phase facade pattern: `Spell.run_all_phases` and
`SpellCrafter.run_all_phases`.

## Compiler Data Flow (Draft)
Inputs:
- RootResolutionBlueprint.dag
- RootResolutionBlueprint.ordered_node_ids
- RootResolutionBlueprint.dag_index (for mutation targeting in dependencies)
- SpellSystemStates local topology (for dependency collection)
- Spell lookup map (for contract sockets + existence)

Outputs:
- OccurrencePlan (as defined in `phase8_occurrence_plan_schema.md`)

## Storage Location (Draft)
Option A: store on root SpellCrafter
- Mirrors Phase 5 storage pattern (`_root_blueprint_phase5`).
Option B: store on RootResolutionBlueprint
- Keeps plan with the root blueprint artifact.

UNKNOWN: cleanup responsibilities and where plan is best invalidated.

## Revalidation / Change-Control Integration
`run_phase_root_blueprints` installs a change-control revalidator that calls
`crafter.run_all_phases` for dirty roots. Evidence: `_revalidate_dirty_roots`
inside `run_phase_root_blueprints`.

Therefore:
- Extend `run_all_phases` to include Phase 8 so revalidation regenerates the plan.
- Or add a new revalidator path for Phase 8 if Phase 8 is excluded from
  `run_all_phases`.

## Minimal Migration Steps (Compiler Plan)
1) Add OccurrencePlan storage to SpellCrafter (new field).
2) Implement `run_phase_occurrence_plan` in SpellCrafter:
   - Validate Phase 5 artifacts exist.
   - Compile plan using logic from `MeldEngine.run`.
   - Store plan on root crafter (or blueprint).
3) Add Spell facade and include in `run_all_phases` when enabled.
4) Update meld runtime to consume OccurrencePlan when present and gates allow.

## Tests (Draft)
- Unit: plan matches current runtime outputs for a known blueprint (compare
  occurrence_graph, execution_order, instance plan).
- Integration: revalidation reruns Phase 8 (dirty root) and replaces plan.
- Fallback: missing/stale plan -> runtime planning path still works.

## Open Questions
- Is Phase 8 gated by Phase 6 validity or can it compile even if invalid?
- Where should the plan be stored to align with cleanup semantics?
