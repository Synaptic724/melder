# Task: Slot conjure-path classes and dataclasses for lower overhead

## Metadata
- Task ID: TASK-2026-02-01-slot-conjure-classes
- Story: N/A
- Status: in_progress
- Owner:
- Priority: p0
- Created: 2026-02-01
- Updated: 2026-02-01

## Objective
Add __slots__ (or dataclass slots) to conjure-path classes to reduce per-instance
memory and attribute lookup overhead without changing behavior or public API.

## Scope Boundaries
- In scope:
  - Add __slots__ to normal classes on the conjure path.
  - Add slots=True to existing dataclasses on the conjure path.
  - Keep docstrings and behavior unchanged.
- Out of scope:
  - Refactors, behavior changes, or API changes.
  - Converting dataclasses to normal classes.
  - Any meld/runtime changes outside conjure phases.

## Steps / Checklist
- [x] Identify conjure-path classes without slots.
- [x] Add __slots__ to normal classes.
- [x] Add slots=True to dataclasses.
- [x] Record validation status.

## Deliverables
- Slot additions in the conjure pipeline classes listed below.

## Files / Paths Impacted
- src/melder/spellbook/bind/bind.py
- src/melder/spellbook/bind/scan.py
- src/melder/spellbook/configuration/configuration.py
- src/melder/spellbook/spell_crafter/blueprints/execution_plan.py
- src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py
- src/melder/spellbook/spell_crafter/blueprints/patch_maps.py
- src/melder/spellbook/spell_crafter/dag/dag_index.py
- src/melder/spellbook/spell_crafter/dag/dag_node.py
- src/melder/spellbook/spell_crafter/dag/directed_acyclic_work_graph.py
- src/melder/spellbook/spell_crafter/dag/resolution_frame/resolution_frame.py
- src/melder/spellbook/spell_crafter/dag/target_spec.py
- src/melder/spellbook/spell_crafter/topology/spell_local_topology.py
- src/melder/spellbook/spell_crafter/spell_examiner/inspectors/class_inspector.py
- src/melder/spellbook/spell_crafter/spell_examiner/inspectors/inspector_utility.py
- src/melder/spellbook/spell_crafter/spell_examiner/inspectors/method_inspector.py
- src/melder/spellbook/spell_crafter/system/validation/socket_ref_sanity_strategy.py
- src/melder/spellbook/spell_crafter/system/validation/strategy_base.py

## Validation
- Not run.
- Recommended commands:
  - pytest -q

## Risks / Rollback Notes
- Risk: Missing slot entries could raise AttributeError at runtime.
- Mitigation: Audit __init__ assignments and keep __slots__ aligned.

## Done Checklist
- [x] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Added __slots__ to conjure-path classes and slots=True to dataclasses across
binding, configuration, blueprint, DAG, topology, inspectors, and system
validation strategy modules. Loosened DagNode to allow instance attribute
override in tests and removed MethodInspector slots. Validation not run.
