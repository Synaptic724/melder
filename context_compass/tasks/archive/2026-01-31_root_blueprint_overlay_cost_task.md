# Task: Reduce Phase 5 root blueprint overlay cost

## Metadata
- Task ID: TASK-2026-01-31-root-blueprint-overlay-cost
- Story:
- Status: draft
- Owner:
- Priority: p1
- Created: 2026-01-31
- Updated: 2026-01-31

## Objective
Reduce Phase 5 build time by trimming the socket overlay/indexing work in `SpellSystemRootBlueprintBuilder`.

## Problem / Opportunity
Phase 5 root blueprint construction is the second largest contributor in the full conjure build profile. The profile shows `SpellSystemRootBlueprintBuilder._overlay_sockets_and_index` and `root_resolution_blueprint.add_socket_ref` dominating this phase, indicating heavy repeated socket indexing.

## Context
Evidence from the user's `profile_conjure_build_direct.py` run on 2026-01-31:
- `SpellCrafter.run_phase_root_blueprints` ~0.147s cumulative.
- `_overlay_sockets_and_index` ~0.108s cumulative.
- `RootResolutionBlueprint.add_socket_ref` and `DagIndex.add_socket` are high-call hotspots.

## MRP Alignment
Root blueprint generation must remain correct and deterministic. Any optimizations should preserve the observable DAG and socket reference structures while improving build latency.

## Goals
- Identify redundant socket indexing or repeated traversal patterns.
- Reduce CPU time in `_overlay_sockets_and_index` without changing blueprint outputs.
- Maintain deterministic ordering and index correctness.

## Non-Goals
- Do not change DAG semantics or socket reference contracts.
- Do not alter public APIs.
- Do not add global caches or non-deterministic behavior.

## Scope Boundaries
- In scope: `SpellSystemRootBlueprintBuilder` and `RootResolutionBlueprint` socket handling.
- Out of scope: changes to unrelated phases or scheduler behavior.

## Requirements
- Preserve existing blueprint output shapes and ordering.
- Keep changes localized and documented.
- Add/adjust tests to protect against regressions in socket overlay behavior.

## Acceptance Criteria
- Phase 5 cumulative time decreases on the deep_layers direct benchmark.
- Root blueprint outputs remain identical for existing tests.
- New tests cover any optimized path or new helper introduced.

## Steps / Checklist
- [ ] Inspect `_overlay_sockets_and_index` algorithm and identify repeated work.
- [ ] Propose minimal optimization and get user approval.
- [ ] Implement optimization with docstring/comment updates.
- [ ] Add or update tests for socket overlay correctness.
- [ ] Validate with direct conjure benchmark (user-run).

## Deliverables
- Optimized root blueprint overlay/indexing logic.
- Regression tests for socket overlay behavior.
- Benchmark comparison notes.

## Files / Paths Impacted
- src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py
- src/melder/spellbook/spell_crafter/blueprints/root_resolution_blueprint.py
- src/melder/spellbook/spell_crafter/dag/dag_index.py
- tests/unit/melder/spellbook/spell_crafter/system (new or updated tests)

## Validation
- Not run.
- Recommended commands:
  - `<local-workspace>\.venv_new\Scripts\python.exe benchmarks\conjure\profile_conjure_build_direct.py`
  - `pytest -q tests\unit\melder\spellbook\spell_crafter\system`

## Risks / Rollback Notes
- Risk: subtle socket reference ordering drift.
- Mitigation: assertions in tests on socket ordering and index contents.

## Decision Log
- Baseline hotspots recorded from profile run provided by user (2026-01-31).

## Context / Handoff Summary
Phase 5 is dominated by socket overlay/indexing in `SpellSystemRootBlueprintBuilder._overlay_sockets_and_index` and related `add_socket_ref`/`DagIndex.add_socket` calls. Focus on reducing redundant work while preserving blueprint semantics.
