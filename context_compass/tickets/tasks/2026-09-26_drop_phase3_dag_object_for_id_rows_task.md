# Task: Phase 3 emits id and edge rows instead of a DirectedAcyclicWorkGraph (C-C)

## Metadata
- Task ID: TASK-2026-09-26-drop-phase3-dag-object-for-id-rows
- Story: STORY-2026-09-26-structural-snapshot
- Status: in_progress
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-09-26T16:12:08Z
- Updated: 2026-09-26T16:19:33Z

## Objective
Phase 3 computes `ordered_node_ids`, `dependency_spell_ids` and DAG edge rows
`(parent_id, child_id, param_name, socket_kind)` from the resolved sockets without materializing a
`DirectedAcyclicWorkGraph` (no ULID mint, no RLock, no DagNode containers, no heap sort per spell per
conjure); `Spell.dependency_graph` becomes a documented tombstone; the resolution-frame presence strategy
reads the resolution frame. Every other phase-3 write is unchanged (architecture patch matrix row 1,
component patch "Before/After (phase 3)"). The rows are the phase-3 material the capture task persists.

## Ticket Contract
- ENTRY_GATE: the patch docs under `system_docs/patches/active/structural_snapshot_2026_09_26/` are
  owner-approved (2026-09-26); the active board row routes here; B1 reads and the Propose->Confirm precede
  any edit under `src/`.
- EXECUTION_BOUNDARY: `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py`
  (`_build_local_frame_dag` and its helpers), `src/melder/aether/spellbook/spell.py` (`dependency_graph`,
  `_add_build_details`, cleanup), the resolution-frame presence strategy, the `dag/` package only if a
  rows-only helper lands there, the tests that read `dependency_graph` or the DAG (eight files per the
  candidate record), the component map entries at review. NOT in scope: the envelope, the conjure order,
  capture/hydrate (later tasks), phases 4-11, the meld hot path.
- DEPENDENCIES: patch docs (approved); candidates.md C-C; phase_03.md; the T1 determinism test as the guard
  for any signature-visible change (none expected: the rows are not hashed in this task).
- EXIT_GATE: owner-confirmed file list; edits applied with CRLF preserved; tests updated or added (unit
  first); owner-run compiler suites green; breakdown harness `local_frame` row before/after recorded;
  component patch "After (phase 3)" matches the landed code; task in review.
- FAILURE_ESCALATION: CONFLICT if a production reader of `Spell.dependency_graph` other than the presence
  strategy exists (Nexus, crystallizer); DECISION_REQUEST if the DAG's topological order cannot be
  reproduced from the sockets without the object; BLOCKER if a test suite depends on DAG internals that
  have no row equivalent.

## Scope Boundaries
- In scope: the rows-only phase-3 build, the tombstone, the strategy repoint, the affected tests, the
  harness measurement (owner-run), the component-patch alignment.
- Out of scope: persisting the rows (capture task), the conjure reorder (hydrate task), any `dag/` package
  removal (the package stays for other consumers until proven unused).

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner approved the patch docs and directed the lane to proceed (2026-09-26T16:12:08Z); opened as the
  first implementation task per the story's task order and the migration order in the architecture patch.

## Steps / Checklist
- [x] B1: read `compiler_phase_3.py` `_build_local_frame_dag` and its helpers whole, the `dag/` package
      (`directed_acyclic_work_graph.py`, `dag_node.py`) for the ordering rule, `spell.py`
      (`dependency_graph`, `_add_build_details`, cleanup), the presence strategy, and every test that reads
      `dependency_graph` or builds the DAG; note the findings.
- [ ] B2: Propose->Confirm (goal, constraints, exact files/symbols, test plan); wait for the owner's go.
- [ ] B3: implement the rows-only build, the tombstone and the strategy repoint (CRLF preserved; rich
      docstrings; no module constants; `Optional`/`Union`).
- [ ] B4: tests: unit tests for the row builder (ordering, edge rows, no DAG); update the eight files;
      density per overlay.
- [ ] B5: align the component patch "After (phase 3)" wording with the landed code; note the harness command.
- [ ] B6: owner-run suites and the breakdown harness `local_frame` row before/after; "Not run." until then.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Phase 3 without the DAG object; `Spell.dependency_graph` tombstone; presence strategy repointed; tests.

## Files / Paths Impacted
- src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py
- src/melder/aether/spellbook/spell.py
- src/melder/aether/spellbook/spell_compiler/validation/strategies/resolution_frame_presence_strategy.py
- tests (eight files per candidates.md C-C; exact list after B1)

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/spellbook/spell_compiler tests/component/melder/spellbook`
  - `python benchmarks/testing_other_di/profile_phase_scheduler_breakdown.py` (workers=1; `local_frame` row)

## Risks / Rollback Notes
- `Spell.dependency_graph` is a documented owned field and a test surface; keeping the attribute as a
  documented `None` tombstone preserves shape. Rollback: restore the DAG build and the strategy's read (one
  file each); the rows are additive.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No src edit before the owner confirms the exact file/symbol list.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/structural_snapshot_2026_09_26/architecture_patch.md
  - system_docs/patches/active/structural_snapshot_2026_09_26/component_patch_spell_compiler.md
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: Story closure (the patch folder is shared by the story's tasks).

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: phase 3 DAG rows; Spell.dependency_graph tombstone.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T16:12:08Z
  TYPE: PLAN
  CLAIM: Opened on the owner's approval of the patch docs ("finish off what you gotta do"). Order: B1 reads
    (phase 3 whole around `_build_local_frame_dag`, the dag package's ordering rule, `Spell._add_build_details`
    and cleanup, the presence strategy, the eight tests), then B2 Propose->Confirm with the exact symbol list,
    then B3-B6. Design source: candidates.md C-C and phase_03.md (DAG payloads are live Spells; edges are
    parent=dependency -> child=root tagged param_name and SocketKind; topological ties break on node id).
  EVIDENCE:
  - artifacts/ir_phase_improvement_20260926/candidates.md:72-98
  - artifacts/ir_phase_survey_20260925/phase_03.md:36-60
  - system_docs/patches/active/structural_snapshot_2026_09_26/component_patch_spell_compiler.md:23-33
  IMPACT: No src edit until the owner confirms the file list; the reads decide the exact helper shape.
  NEXT: B1 - read compiler_phase_3.py around `_build_local_frame_dag` (whole method and helpers).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T16:19:33Z
  TYPE: FACT
  CLAIM: B1 reads done. (1) Phase 3's DAG is a STAR: `_build_local_frame_dag` adds the root node, then for every
    resolved dependency `add_node(dep_id)` + `add_dependency(parent=dep_id, child=root_id, param_name,
    socket_kind=NORMAL)`; no edge between dependencies. `topological_sort` heaps indegree-0 nodes by id and pops
    the root last, so `collect_dependency_ids()` == sorted(set(dependency_spell_ids)) + [root_id] exactly.
    `DagNode.add_dependency` ignores a repeated parent (first param wins) and raises ValueError("DagNode cannot
    depend on itself.") when a spell resolves itself; every edge's socket_kind is NORMAL (SPELL_CONTRACT deps
    resolve to {} and produce no edge). (2) The only production reader of `Spell.dependency_graph` is the
    presence strategy's `is None` warning (MISSING_DEPENDENCY_GRAPH); `Spell` cleanup cascades into it and
    `_add_build_details(dag, dependencies)` rejects dag=None. No nexus/crystallizer reader; the build asset
    `src_graph_payload.py` names the field in prose (owner-run regen). (3) `DirectedAcyclicWorkGraph` stays:
    phase 5's root-blueprint builder, the root-scale strategy and the restore engine build their own deep DAGs.
    (4) Edge rows are a projection of the registered topology (socket target_spell_ids + param_name + NORMAL),
    so C-C needs NO new storage: ordered ids and direct ids are derivable; the patch schema's `dag_edges` field
    is redundant (record for the capture task). (5) Test surface: `_build_local_frame_dag` returns the DAG to
    three unit tests; nine test files read `dependency_graph` or the warning code (list in the proposal).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:783-1057
  - src/melder/aether/spellbook/spell_compiler/dag/directed_acyclic_work_graph.py:122-296
  - src/melder/aether/spellbook/spell_compiler/dag/dag_node.py:168-215
  - src/melder/aether/spellbook/spell.py:455-475
  - src/melder/aether/spellbook/spell.py:555-626
  - src/melder/aether/spellbook/spell.py:1472-1510
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/resolution_frame_presence_strategy.py:1-103
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1320-1362
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_3.py:60-125
  - tests/unit/melder/spellbook/spell_crafter/validation/strategies/test_resolution_frame_presence_strategy.py:1-384
  - tests/component/melder/spellbook/spell_crafter/dag/test_spellbook_component_dag_local_frame.py:100-247
  IMPACT: The change is small and exact: compute the order arithmetically, keep the self-dependency refusal,
    tombstone the field, drop the dag parameter, retire the warning code; nine test files follow.
  NEXT: B2 - Propose->Confirm to the owner with the file/symbol list; no edit before the go.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
STATE 2026-09-26T16:12:08Z: IN_PROGRESS. B1 reads not started. Next: read compiler_phase_3.py `_build_local_frame_dag`
STATE 2026-09-26T16:19:33Z: IN_PROGRESS. B1 done (FACT note). Waiting on the owner's go for the B2 Propose->Confirm;
no src edit yet.
whole, then the dag package, spell.py build details, the presence strategy and the eight tests; then B2.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
