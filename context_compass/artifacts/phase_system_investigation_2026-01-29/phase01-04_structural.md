# Phase 1-4 Investigation (Requirements, Symbolic Graph, Local Frame, Validation)

## Metadata
- Created: 2026-01-29
- Updated: 2026-01-29
- Task: TASK-2026-01-29-phase01-04-structural-investigation

## Summary
Phases 1-4 are per-spell structural phases. They produce requirements, a symbolic graph,
a local DAG and topology, and a validation result. They are prerequisites for Phase 5.

## Phase 1 - Requirements (SpellRequirements)
Inputs:
- Bound Spell with SpellIndex and spell_type.

Outputs/Storage:
- SpellRequirements stored on SpellCrafter._requirements (spell_id = SpellIndex.current).
- Requirements are built by SpellRequirementsFinder and returned on repeat calls (idempotent).

Key contracts:
- Existing-creation spells produce no parameter requirements.
- No Spellbook or SpellSystemStates updates in Phase 1.

Evidence:
- src/melder/spellbook/spell_crafter/spell_crafter.py: SpellCrafter.run_phase_requirements
- src/melder/spellbook/spell_crafter/spell_examiner/spell_requirements_finder/spell_requirements_finder.py: SpellRequirementsFinder.build_requirements

## Phase 2 - Symbolic Graph (SpellSymbolicGraph)
Inputs:
- Phase 1 SpellRequirements.

Outputs/Storage:
- SpellSymbolicGraph stored on SpellCrafter._symbolic_graph.
- Symbolic dependencies include ParameterDIShape shapes for normal DI, SpellMap, SpellContract,
  MutationContract, and plain parameters.

Key contracts:
- Raises if requirements are missing; does not run Phase 1 automatically.
- No SpellSystemStates updates.

Evidence:
- src/melder/spellbook/spell_crafter/spell_crafter.py: SpellCrafter.run_phase_symbolic_graph
- src/melder/spellbook/spell_crafter/spell_examiner/profiles/resolution_profile.py: SpellSymbolicGraph

## Phase 3 - Local Frame / DAG (SpellResolutionFrame + topology)
Inputs:
- Phase 1 requirements and Phase 2 symbolic graph.
- SpellbookScanner for spell resolution.

Outputs/Storage:
- DirectedAcyclicWorkGraph for local frame (root + direct dependency nodes).
- SpellResolutionFrame stored on SpellCrafter._resolution_frame (ordered_node_ids).
- Spell._add_build_details called with dag and unique dependencies.
- SpellSystemStates updated with:
  - update_dependencies(spell_index, dependency_spell_ids)
  - register_local_topology(spell_index, topology)

Key contracts:
- Only normal DI shapes (single/collection/SpellMap) produce DAG edges.
- SpellContract, MutationContract, and plain params are metadata-only at this phase.
- Raises if requirements or symbolic graph are missing.

Evidence:
- src/melder/spellbook/spell_crafter/spell_crafter.py: SpellCrafter.run_phase_local_frame, _build_local_frame_dag
- src/melder/aether/dev_ops/spell_system_states/spell_system_states.py: SpellSystemStates.update_dependencies, register_local_topology
- src/melder/spellbook/spell_crafter/spell_examiner/profiles/resolution_profile.py: SpellResolutionFrame

## Phase 4 - Validation (SpellValidationSystem)
Inputs:
- Phase 1 requirements, Phase 2 symbolic graph, Phase 3 resolution frame.

Outputs/Storage:
- SpellValidationResult stored on SpellCrafter._validation_result_phase4.
- Flags: _validated_phase4 and _is_broken.
- SpellSystemState validity set to valid or invalid based on result.

Key contracts:
- Returns early if already validated and SpellSystemState validity is valid.
- Raises if any Phase 1-3 artifact is missing.

Evidence:
- src/melder/spellbook/spell_crafter/spell_crafter.py: SpellCrafter.run_phase_validation
- src/melder/spellbook/spell_crafter/validation/validation_system.py: SpellValidationSystem and built-in strategies

## Cleanup behavior
- SpellCrafter.cleanup_phase_artifacts clears requirements, symbolic graph, resolution frame,
  and Phase 4/6 validation results; keeps Phase 5+ artifacts.

Evidence:
- src/melder/spellbook/spell_crafter/spell_crafter.py: SpellCrafter._cleanup_phase_artifacts_locked

## Risks / Concerns
- Phase 3 writes dependencies into SpellSystemStates; root selection in Phase 5 depends on these edges.
- Any change to dependency recording changes root detection downstream.

## Unknowns
- SpellSystemStates.update_dependencies accepts dependency ids described as version or lineage ids.
  Phase 3 currently passes version ids (SpellIndex.current), but other callers may differ.
  Evidence: src/melder/aether/dev_ops/spell_system_states/spell_system_states.py: update_dependencies docstring.
