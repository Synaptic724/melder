Completed: 2026-02-08
Summary: Completed deterministic ordering audit with follow-on hardening and regression validation.

# Task: Audit Phase5-8 Deterministic Ordering for Codegen Contracts

## Metadata
- Task ID: TASK-2026-02-07-phase5-8-deterministic-ordering-audit
- Story: STORY-2026-02-07-phase-contract-codegen-completeness
- Status: done
- Owner:
- Priority: p0
- Created: 2026-02-07
- Updated: 2026-02-08

## Objective
Identify all nondeterministic iteration paths in Phase5-8 builders that can
change exported ordering, signatures, or generated source across equivalent
graphs.

## Scope Boundaries
- In scope:
- Audit set/dict iteration in root-blueprint DAG assembly and topo ordering.
- Audit occurrence-plan execution-order build and cycle fallback ordering.
- Audit any root-id selection that depends on unordered collections.
- Define canonical tie-break rules for each ordered artifact.
- Out of scope:
- Implementing ordering changes.

## Steps / Checklist
- [x] Build a field-level map of ordered outputs and their upstream iterators.
- [x] Confirm nondeterministic branches in:
  - `SpellSystemRootBlueprintBuilder`
  - `DirectedAcyclicWorkGraph.topological_sort`
  - `OccurrencePlanBuilder._build_execution_order`
- [x] Define deterministic ordering rules per structure (nodes, edges, roots).
- [x] Produce regression test scenarios for multi-root and tie cases.

## Deliverables
- Evidence matrix: output field -> iterator source -> deterministic risk.
- Canonical ordering spec for Phase5/8 outputs.
- Follow-on implementation checklist.

### Evidence Matrix (Summary)
- `occurrence_graph` expansion queue -> `dependencies.values()` / child list insertion:
  queue ordering could diverge across equivalent map/set iteration.
- DAG fallback dependency collection -> `node.dependencies` (`set[DagNode]`):
  parent traversal could diverge and perturb path-id creation order.
- Shared canonical occurrence selection -> first entry in unsorted occurrence list:
  canonical shared occurrence could drift by map insertion order.
- Contract override compilation rows -> `occurrence_graph.items()`:
  grouped override row order could diverge across equivalent occurrence maps.

### Canonical Ordering Rules Applied
- Occurrence keys are sorted by `(spell_id, path_id)` with `None` path ids first.
- Queue expansion over dependency maps uses sorted param names and sorted occurrence keys.
- DAG fallback edges are traversed by `(param_name, parent_spell_id)`.
- Shared canonical occurrence is the minimum occurrence key, not first-seen.
- Contract override compilation iterates sorted occurrence keys.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py`
- `src/melder/spellbook/spell_crafter/dag/directed_acyclic_work_graph.py`
- `src/melder/spellbook/spell_crafter/dag/dag_node.py`
- `src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py`
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `tests/`

## Validation
- Ran:
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/blueprints/test_occurrence_plan.py`
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py`
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py tests/unit/melder/aether/conduit/meld/meld_engine/test_meld_engine_2.py tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_occurrence_plan.py`
- Result:
  - 218 passed.

## Risks / Rollback Notes
- Risk: unstable ordering causes signature churn or stale cache acceptance.
- Mitigation: canonical tie-break keys with explicit tests for ties/cycles.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Audit identified additional deterministic-risk paths beyond initial Phase5/8
hardening and landed follow-on fixes in `occurrence_plan.py`: deterministic
queue expansion, deterministic DAG fallback dependency traversal, canonical
shared occurrence selection, sorted contract override compilation, and stable
mutation-override map iteration for string keys. Added regression tests proving
stable instance-plan and contract-override outputs across equivalent occurrence
map insertion orders.


