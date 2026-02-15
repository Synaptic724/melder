# Task: Audit DevOps scoping and coupling surfaces

- Completed: 2026-02-03
- Summary: Produced the evidence-backed DevOps scoping map and Phase 5-7 coupling analysis.

## Metadata
- Task ID: TASK-2026-02-01-devops-scope-audit
- Story: STORY-2026-02-01-devops-scope-audit
- Status: done
- Owner:
- Priority: p1
- Created: 2026-02-01
- Updated: 2026-02-03

## Objective
Produce an evidence-backed map of DevOps scoping (frame vs conduit) and identify all coupling surfaces in Phase 5-7 and DevOps managers.

## Scope Boundaries
- In scope:
  - DevOpsManager, RiskManager, ChangeControlManager, SpellSystemStates, ConduitResolutionState.
  - Phase 5-7 call chains and their DevOps touchpoints.
- Out of scope:
  - Implementation changes.

## Steps / Checklist
- [x] Enumerate DevOps data structures and label scope (frame vs conduit) with file+symbol evidence.
- [x] Trace Phase 5-7 call flow into DevOps state with evidence references.
- [x] Identify coupling/race surfaces and record them with evidence.

## Deliverables
- Evidence-backed scoping map with coupling analysis.

## Audit Findings (Evidence Map)

### DevOps scoping map
Frame-scoped (AethericFrame-level intent):
- DevOpsManager is an "Aetheric Frame DevOps hub" and owns ChangeControlManager and RiskManager tied to SpellSystemStates. EVIDENCE: src/melder/aether/dev_ops/dev_ops_manager.py:DevOpsManager docstring + __init__.
- SpellSystemStates is documented as a per-frame registry and stores frame-wide structural state (_states_by_index_id/_states_by_spell_id/_dirty_lineages/_local_topologies). EVIDENCE: src/melder/aether/dev_ops/spell_system_states/spell_system_states.py:SpellSystemStates docstring + __init__.

Spellbook-scoped (within frame):
- Collection and SpellContract dependency indices are keyed by spellbook_id and owned via lineage->spellbook mapping. EVIDENCE: src/melder/aether/dev_ops/spell_system_states/spell_system_states.py:register_lineage + register_local_topology + mark_collection_dependents_dirty + mark_contract_dependents_dirty.

Conduit-scoped (within frame):
- Per-conduit resolution state is keyed by conduit_id in SpellSystemStates._resolution_by_conduit_id. EVIDENCE: src/melder/aether/dev_ops/spell_system_states/spell_system_states.py:get_or_create_conduit_resolution_state.
- ConduitResolutionState stores per-conduit spell/root validity, diagnostics, and dirty flags. EVIDENCE: src/melder/aether/dev_ops/spell_system_states/conduit_resolution_state.py:ConduitResolutionState docstring + __init__.
- RiskManager tracks per-conduit risk state keyed by conduit_id and updates on per-conduit resolution validity changes. EVIDENCE: src/melder/aether/dev_ops/risk_manager/risk_manager.py:register_conduit + on_resolution_validity_change.

### Phase 5-7 call flow (DevOps touchpoints)
- Spellbook._run_resolution_phases_for_conduit registers phases root_blueprints, system_validation, change_control as single lead-spell units with scope="frame". EVIDENCE: src/melder/spellbook/spellbook.py:_run_resolution_phases_for_conduit + _phase_root_blueprints_factory + _phase_system_validation_factory + _phase_change_control_factory.
- Phase 5 (SpellCrafter.run_phase_root_blueprints) builds adjacency from SpellSystemStates, filters to spellbook-visible spells, builds root blueprints, rebuilds ChangeControlManager.component_of, and sets a revalidator closure capturing conduit_id. EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_root_blueprints.
- Phase 7 (SpellCrafter.run_phase_change_control -> _ensure_change_control_ready) rebuilds component_of and conditionally sets the revalidator if missing. EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_change_control + _ensure_change_control_ready.
- Phase 6 passes conduit_id to SpellSystemValidationSystem.validate with spell_system_states. EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_system_validation. UNKNOWN: how validate writes per-conduit validity (requires spell_system_validation_system.py review).

### Coupling / race surfaces
- ChangeControlManager.component_of is a single frame-level map (spell_id -> roots). Rebuilt from Phase-5 root_blueprints filtered to a spellbook's visible spells; last run overwrites prior mappings across conduits. EVIDENCE: src/melder/aether/dev_ops/change_control_manager/change_control_manager.py:rebuild_component_of + src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_root_blueprints.
- ChangeControlManager.revalidate_fn is a single frame-level callback. Phase 5 sets it unconditionally with a closure capturing the current conduit_id and spellbook._spell_id_pool; this is last-writer-wins across conduits. EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_root_blueprints.
- Dirty tracking (dirty_spells/dirty_roots/monitor_active) is frame-global. notify_spell_changed uses component_of to mark dirty roots; revalidate_dirty_roots uses the single revalidator. EVIDENCE: src/melder/aether/dev_ops/change_control_manager/change_control_manager.py:notify_spell_changed + revalidate_dirty_roots + is_root_dirty.
- Phase 7 repeats rebuild_component_of after Phase 5, reinforcing the same coupling surface. EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:_ensure_change_control_ready.

### Evidence closure for prior unknowns
- DevOpsManager is constructed per AethericFrame and holds frame-level DevOps state. EVIDENCE: src/melder/aether/aetheric_frame.py:__init__.
- Aether._get_change_control_manager returns the frame's DevOpsManager.change_control_manager (per-frame). EVIDENCE: src/melder/aether/aether.py:_get_change_control_manager + _get_devops_manager.
- SpellSystemValidationSystem.validate writes per-conduit resolution validity and diagnostics when conduit_id is provided. EVIDENCE: src/melder/spellbook/spell_crafter/system/spell_system_validation_system.py:validate + _record_conduit_resolution_state.

## Files / Paths Impacted
- `context_compass/tasks/completed/2026-02-01_devops_scope_audit_task.md`
- `context_compass/stories/completed/2026-02-01_devops_scope_audit_story.md`

## Validation
- Not run.
- Recommended commands:
  - N/A (audit only)

## Risks / Rollback Notes
- Risk: incomplete audit due to missed entrypoints.
  Mitigation: cross-check all DevOps managers and SpellSystemStates usage.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Audit completed with evidence-backed scoping map and coupling surfaces for Phase 5-7. Remaining gaps are explicit in the Unknowns list (AethericFrame/Aether scoping and SpellSystemValidationSystem write paths).
