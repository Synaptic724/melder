# Story: Audit DevOps scoping and coupling

- Completed: 2026-02-03
- Summary: DevOps scoping audit completed with evidence map and docs updates.

## Metadata
- Story ID: STORY-2026-02-01-devops-scope-audit
- Epic: EPIC-2026-02-01-conduit-scoped-devops-phase5-7
- Status: done
- Owner:
- Priority: p1
- Created: 2026-02-01
- Updated: 2026-02-03

## User Narrative
As a Melder maintainer, I want a complete audit of DevOps scoping (frame vs conduit) so that we can eliminate cross-conduit coupling in Phase 5-7.

## Value / MRP Alignment
This audit ensures the core DevOps control-plane is coherent and trustworthy in multi-conduit frames, which is essential for reliable validation and change-control behavior.

## Requirements (Functional)
- Identify all DevOps data structures and flows that are frame-scoped vs conduit-scoped.
- Map the call chain from Phase 5-7 into DevOps state with evidence references.
- Identify race/coupling surfaces where conduit actions overwrite shared state.

## Requirements (Non-Functional)
- Evidence-first; no assumptions.
- Findings must cite file+symbol references.

## Scope Boundaries
- In scope:
  - DevOpsManager, RiskManager, ChangeControlManager, SpellSystemStates, ConduitResolutionState.
  - Phase 5-7 entrypoints and wiring.
- Out of scope:
  - Implementation changes; this is audit-only.

## Dependencies / Related Work
- Epic: EPIC-2026-02-01-conduit-scoped-devops-phase5-7

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-02-01-devops-scope-audit - Produce scoping map and coupling analysis.
- [x] Task: TASK-2026-02-01-devops-scope-docs - Update docs to reflect scoping model (if needed).

## Acceptance Criteria
- A written evidence-backed scoping map exists for DevOps and Phase 5-7.
- All coupling/race surfaces are identified with file+symbol evidence.

## Validation / Test Plan
- Not applicable (audit/documentation only).

## UX / API / Data Notes
- None.

## Risks / Mitigations
- Risk: Missing a coupling surface due to incomplete scan.
  Mitigation: Cross-check all DevOps managers and SpellSystemStates flow paths.

## Open Questions
- Should contracted spells be included in conduit-scoped component_of maps?
- Should component_of be keyed by conduit_id or root conduit_id?

## Decision Log
- 2026-02-01: Story created under conduit-scoped DevOps epic.

## Audit Findings (Evidence Map)

### DevOps scoping map
Frame-scoped (AethericFrame-level intent):
- DevOpsManager is an "Aetheric Frame DevOps hub" and owns ChangeControlManager and RiskManager tied to SpellSystemStates. EVIDENCE: src/melder/aether/dev_ops/dev_ops_manager.py:DevOpsManager docstring + __init__.
- AethericFrame constructs DevOpsManager and SpellSystemStates per frame. EVIDENCE: src/melder/aether/aetheric_frame.py:__init__.
- SpellSystemStates is a per-frame registry for structural state (lineages, dirty sets, topologies). EVIDENCE: src/melder/aether/dev_ops/spell_system_states/spell_system_states.py:SpellSystemStates docstring + __init__.

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
- Phase 6 writes per-conduit resolution validity and diagnostics when conduit_id is provided. EVIDENCE: src/melder/spellbook/spell_crafter/system/spell_system_validation_system.py:validate + _record_conduit_resolution_state.
- Aether resolves ChangeControlManager through per-frame DevOpsManager. EVIDENCE: src/melder/aether/aether.py:_get_change_control_manager + _get_devops_manager.

### Coupling / race surfaces
- ChangeControlManager.component_of is a single frame-level map (spell_id -> roots). Rebuilt from Phase-5 root_blueprints filtered to a spellbook's visible spells; last run overwrites prior mappings across conduits. EVIDENCE: src/melder/aether/dev_ops/change_control_manager/change_control_manager.py:rebuild_component_of + src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_root_blueprints.
- ChangeControlManager.revalidate_fn is a single frame-level callback. Phase 5 sets it unconditionally with a closure capturing the current conduit_id and spellbook._spell_id_pool; this is last-writer-wins across conduits. EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_root_blueprints.
- Dirty tracking (dirty_spells/dirty_roots/monitor_active) is frame-global. notify_spell_changed uses component_of to mark dirty roots; revalidate_dirty_roots uses the single revalidator. EVIDENCE: src/melder/aether/dev_ops/change_control_manager/change_control_manager.py:notify_spell_changed + revalidate_dirty_roots + is_root_dirty.
- Phase 7 repeats rebuild_component_of after Phase 5, reinforcing the same coupling surface. EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:_ensure_change_control_ready.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
Audit completed with an evidence-backed scoping map and coupling surfaces. Prior unknowns are resolved with evidence for AethericFrame DevOpsManager ownership, Aether change-control retrieval, and SpellSystemValidationSystem per-conduit writes; see TASK-2026-02-01-devops-scope-audit.
