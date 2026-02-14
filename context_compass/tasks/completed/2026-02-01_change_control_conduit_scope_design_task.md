# Task: Design conduit-scoped change-control behavior

- Completed: 2026-02-03
- Summary: Defined conduit-scoped change-control semantics with scoping key,
  contracted-spell inclusion rules, and an impacted call-site map.

## Metadata
- Task ID: TASK-2026-02-01-change-control-conduit-scope-design
- Story: STORY-2026-02-01-change-control-conduit-scope
- Status: done
- Owner:
- Priority: p1
- Created: 2026-02-01
- Updated: 2026-02-03

## Objective
Define the conduit-scoped component_of and revalidator semantics, including keying strategy and contracted-spell inclusion rules, with evidence-backed call-site impact.

## Scope Boundaries
- In scope:
  - ChangeControlManager data structures and API impacts.
  - Phase 5/7 call site requirements.
- Out of scope:
  - Implementation and tests.

## Steps / Checklist
- [x] Decide scoping key (conduit_id vs root conduit_id) with evidence and rationale.
- [x] Define contracted-spell inclusion rules for component_of and dirty tracking.
- [x] Identify required API changes and all call sites.

## Deliverables
- Written design with decisions and impacted file/symbol list.

## Design Summary (Evidence-Based)

### Recommended scoping key
Use the **resolution conduit id** (root conduit id for lesser conduits).

Rationale (evidence):
- Per-conduit resolution validity is keyed by `conduit_id` and uses root conduit id for lesser conduits. EVIDENCE: src/melder/aether/conduit/meld/meld.py:_get_resolution_conduit_id.
- Phase 6 writes per-conduit resolution validity and diagnostics keyed by conduit_id. EVIDENCE: src/melder/spellbook/spell_crafter/system/spell_system_validation_system.py:_record_conduit_resolution_state.

This aligns change-control scoping with the same conduit id used for resolution gating and diagnostics.

### Contracted-spell inclusion
Include contracted spells visible to the Spellbook for the conduit being validated.

Rationale (evidence):
- Phase 5 builds root blueprints and system index from the Spellbook-visible spell pool (`spellbook._spell_id_pool`), which includes local + contracted spells. EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_root_blueprints.

### Data model changes (ChangeControlManager)
Introduce per-resolution-conduit maps keyed by conduit_id (root for lessers):
- `component_of_by_conduit_id: Dict[str, Dict[str, Set[str]]]`
- `dirty_roots_by_conduit_id: Dict[str, Set[str]]`
- `dirty_spells_by_conduit_id: Dict[str, Set[str]]`
- `monitor_active_by_conduit_id: Dict[str, bool]`
- `revalidate_fn_by_conduit_id: Dict[str, Callable[[Set[str], Optional[CancellationEvent]], Optional[Set[str]]]]`

### API changes (proposed)
ChangeControlManager methods to accept `conduit_id`:
- `rebuild_component_of(conduit_id, root_blueprints)`
- `set_revalidator(conduit_id, fn)`
- `notify_spell_changed(conduit_id, spell_id)`
- `revalidate_dirty_roots(conduit_id, cancel_event)`
- `is_root_dirty(conduit_id, root_id)`
- `describe(conduit_id=None)` (optional: per-conduit view or aggregated)

### Call sites impacted (evidence map)
Phase 5/7 wiring:
- `SpellCrafter.run_phase_root_blueprints` sets component_of and revalidator. EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_root_blueprints.
- `SpellCrafter.run_phase_change_control` rebuilds component_of and revalidator. EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:_ensure_change_control_ready.

Meld gating:
- `Meld._gated_validation_required` checks `ccm.is_root_dirty` without conduit id. EVIDENCE: src/melder/aether/conduit/meld/meld.py:_gated_validation_required.
- `MeldRuntime.execute` checks `manager.is_root_dirty` without conduit id. EVIDENCE: src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py:execute.

Aether/DevOps access:
- `Aether._revalidate_dirty_roots` uses frame-level ChangeControlManager. EVIDENCE: src/melder/aether/aether.py:_revalidate_dirty_roots.
- `DevOpsManager.revalidate_dirty_roots` delegates to ChangeControlManager. EVIDENCE: src/melder/aether/dev_ops/dev_ops_manager.py:revalidate_dirty_roots.

Ownership transfer incident path:
- TransferOfOwnership checks `change_control_manager._revalidate_fn is None`; needs per-conduit equivalent. EVIDENCE: src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:_record_incident.

### Open design questions (explicit)
- Should `notify_spell_changed` fan out across **all** conduit component_of maps, or only a specified conduit? (Currently no call sites for notify_spell_changed; evidence: rg results show no external uses.)
- Do we want per-conduit dirty roots to block meld for lesser conduits when the root conduit is dirty? Current resolution conduit id logic suggests "yes." EVIDENCE: src/melder/aether/conduit/meld/meld.py:_get_resolution_conduit_id.


## Files / Paths Impacted
- `context_compass/tasks/2026-02-01_change_control_conduit_scope_design_task.md`
- `context_compass/stories/2026-02-01_change_control_conduit_scope_story.md`

## Validation
- Not run.
- Recommended commands:
  - N/A (design only)

## Risks / Rollback Notes
- Risk: changing scoping keys impacts cross-conduit contract behavior.
  Mitigation: include contracted-spell scenarios in the design and test plan.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Design completed with a recommended conduit-scoped model aligned to resolution conduit id, plus impacted API/call-site map. User acceptance confirmed for closure.
