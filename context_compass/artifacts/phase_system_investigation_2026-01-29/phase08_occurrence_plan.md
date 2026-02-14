# Phase 8 Investigation (Occurrence Plan)

## Metadata
- Created: 2026-01-29
- Updated: 2026-01-29
- Task: TASK-2026-01-29-phase08-occurrence-plan-investigation

## Scope
Analyze occurrence plan compilation, root-only behavior, and runtime selection rules.

## Key Questions
- What artifacts are required to build an occurrence plan?
- How are SpellContract overrides recorded?
- When is an occurrence plan considered usable at runtime?

## Evidence
- src/melder/spellbook/spell_crafter/spell_crafter.py: SpellCrafter.run_phase_occurrence_plan
- src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py: OccurrencePlan
- src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py: OccurrencePlanBuilder.build
- src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py: select_occurrence_plan
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py: MeldEngine.run

## Findings
- Phase 8 requires Phase 5 artifacts. If entire_dag_blueprint_phase5 is missing, it raises RuntimeError.
- Phase 8 is root-only. If root_blueprint_phase5 is None and the spell is a root (present in _entire_dag_blueprint_phase5), it raises; otherwise it returns without creating a plan.
- OccurrencePlanBuilder builds a path-aware occurrence_graph, execution_order, instance_keys_by_spell_id, canonical_occurrences_by_spell_id, root_instance_key, and shared_spell_ids for a single root blueprint.
- OccurrencePlanBuilder attempts to compile SpellContract override payloads. Missing providers or invalid overrides mark contract_dependencies_complete False, rather than raising.
- select_occurrence_plan returns None when the plan root mismatches or contract_dependencies_complete is False.
- MeldEngine.run requires a usable Phase 8 plan when a deep blueprint is present; if select_occurrence_plan returns None, it raises MeldExecutionError and instructs revalidation.

## Risks / Concerns
- Root-only plan compilation means non-root spells do not get occurrence plans.
- Contract dependency completeness gates plan selection; missing providers make the plan unusable even if the blueprint exists.

## Unknowns
- How contract dependency completeness should be interpreted for dynamic linking scenarios (design decision).
- Whether occurrence plan reuse should be allowed when contract overrides change at runtime.

## Next Steps
- Confirm how contract completeness is updated after dynamic linking.
- Decide whether to compile occurrence plans for non-root spells or adjust runtime expectations.
