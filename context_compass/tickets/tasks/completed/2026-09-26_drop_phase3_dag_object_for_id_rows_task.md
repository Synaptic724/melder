# Task: Phase 3 emits id and edge rows instead of a DirectedAcyclicWorkGraph (C-C)

- Completed: 2026-09-26T16:58:29Z
- Summary: Phase 3 computes the local frame as id rows (sorted distinct dependencies, root last) without a
  per-spell DirectedAcyclicWorkGraph; `Spell.dependency_graph` is a None tombstone; MISSING_DEPENDENCY_GRAPH
  retired; a self-resolution is recorded for Phase 4 (owner option A). Owner-run spellbook suites green
  (3532 passed) before the self-dependency delta; the delta is worktree-verified (unit+component 2947,
  integration 579) and byte-identical on the device tree. Owner turned it in ("turn it all in").
  Record note: this ticket was reconstructed at 2026-09-26T16:58:29Z from commit 86993dce8 plus a replay of the four
  post-commit note scripts after a closure-script fault deleted the working copy (fable_0, disclosed).

## Metadata
- Task ID: TASK-2026-09-26-drop-phase3-dag-object-for-id-rows
- Story: STORY-2026-09-26-structural-snapshot
- Status: done
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-09-26T16:12:08Z
- Updated: 2026-09-26T16:58:29Z

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
- from_state: in_progress
- to_state: review
- transition_reason: Edits landed on the device tree after a green worktree run (2026-09-26T16:40:10Z); owner-run suites and
  harness (B6) plus acceptance remain.
- from_state: review
- to_state: done
- transition_reason: Owner turned the lane in (2026-09-26T16:58:29Z); closure sync run; the capture task is the successor row.

## Steps / Checklist
- [x] B1: read `compiler_phase_3.py` `_build_local_frame_dag` and its helpers whole, the `dag/` package
      (`directed_acyclic_work_graph.py`, `dag_node.py`) for the ordering rule, `spell.py`
      (`dependency_graph`, `_add_build_details`, cleanup), the presence strategy, and every test that reads
      `dependency_graph` or builds the DAG; note the findings.
- [x] B2: Propose->Confirm (goal, constraints, exact files/symbols, test plan); wait for the owner's go.
- [x] B3: implement the rows-only build, the tombstone and the strategy repoint (CRLF preserved; rich
      docstrings; no module constants; `Optional`/`Union`).
- [x] B4: tests: unit tests for the row builder (ordering, edge rows, no DAG); update the eight files;
      density per overlay.
- [x] B5: align the component patch "After (phase 3)" wording with the landed code; note the harness command.
- [x] B6 (owner-run suites green, 3532 passed, on the pre-delta tree; the self-dependency delta is worktree-verified; the harness run was unusable, machine loaded): owner-run suites and the breakdown harness `local_frame` row before/after; "Not run." until then.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Phase 3 without the DAG object; `Spell.dependency_graph` tombstone; presence strategy repointed; tests.

## Files / Paths Impacted
- src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py
- src/melder/aether/spellbook/spell.py
- src/melder/aether/spellbook/spell_compiler/validation/strategies/resolution_frame_presence_strategy.py
- tests (eight files per candidates.md C-C; exact list after B1)

## Validation
- Not run on the device tree. Worktree (VM, 3.14.7t): tests/unit/melder 8215 passed (3 pre-existing
  asset-stamp failures), tests/component 2146 passed, tests/integration 1930 passed; local_frame -31..-34%.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/spellbook/spell_compiler tests/component/melder/spellbook`
  - `python benchmarks/testing_other_di/profile_phase_scheduler_breakdown.py` (workers=1; `local_frame` row)

## Risks / Rollback Notes
- `Spell.dependency_graph` is a documented owned field and a test surface; keeping the attribute as a
  documented `None` tombstone preserves shape. Rollback: restore the DAG build and the strategy's read (one
  file each); the rows are additive.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without acceptance confirmation and board-sync completion.
- [x] No src edit before the owner confirms the exact file/symbol list.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

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

- DATETIME: 2026-09-26T16:38:34Z
  TYPE: DECISION
  CLAIM: Owner go for the C-C edit set ("ok sure"), conditioned on testing in a worktree first ("test it in your
    worktree in your harness first and see what happens"). Harness: a VM copy of src/tests/benchmarks under the
    session home (device tree untouched), CPython 3.14.7t installed with uv, pytest 9.1.1; the same anchored edit
    scripts (cc_edits/*.py, one per file) are applied to the copy first and to the device tree only after the
    suites pass there. Owner-run suites on the Windows tree remain the acceptance gate.
  EVIDENCE:
  - tickets/tasks/2026-09-26_drop_phase3_dag_object_for_id_rows_task.md
  IMPACT: B3/B4 execute in the worktree; B6 stays owner-run.
  NEXT: Apply the edits in the worktree and run the affected suites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T16:38:34Z
  TYPE: FACT
  CLAIM: B3/B4 done in the worktree (3.14.7t, gil disabled). Src: `_build_local_frame_dag` returns
    `(ordered_node_ids, dependency_spell_ids)`, order = sorted distinct dependency ids + root, self-dependency
    raises ValueError before any registry write, `return_dependencies` and the DAG import are gone; `run` keeps
    the frame/registry/Spell writes and calls `_add_build_details(dependencies=...)`; `Spell.dependency_graph` is a
    documented None tombstone (cleanup cascade removed, `del` kept), `_add_build_details(dependencies)`; the
    presence strategy checks the frame only (MISSING_DEPENDENCY_GRAPH retired). Tests: 9 files edited per the
    proposal plus 2 new unit tests (frame order law with a duplicate socket; self-dependency refusal) and one new
    component test (real Phase-3 frame -> no issue); 5 warning tests and 10 inert `dependency_graph = object()`
    lines removed. Worktree results: tests/unit/melder 8215 passed / 3 failed (pre-existing: build assets
    stamped 0.2.56 vs package 0.2.58 - the owner's asset rebuild, not C-C), tests/component 2146 passed,
    tests/integration 1930 passed (2 skipped, 6 xfailed, 2 xpassed). tests/unit/llm_support not collectable in
    the copy (repo dir absent) - unrelated.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:780-1060
  - src/melder/aether/spellbook/spell.py:466-478
  - src/melder/aether/spellbook/spell.py:1470-1508
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/resolution_frame_presence_strategy.py:1-88
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_3.py:832-1100
  IMPACT: The edit set is proven in the harness; the device tree receives the identical scripted edits next.
  NEXT: Apply the scripts to the device tree; re-run the affected suites against it read-only.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T16:38:34Z
  TYPE: MEASURE
  CLAIM: Breakdown harness in the VM (3.14.7t, gil disabled, 29 spells, workers=1, repeats 7 and 15, three
    runs each, medians): `local_frame` wall 1.150-1.160ms before -> 0.761-0.801ms after (-31% to -34%), busy
    1.05-1.11ms -> 0.68-0.74ms; requirements_symbolic, validation, root_blueprints, system_validation,
    change_control and plan_group within run noise. Method: identical interpreter and harness over two trees
    (device-tree src copy vs the edited worktree). Caveat: VM numbers, not the owner's machine; absolute values
    differ from the 2026-09-26 owner baseline (local_frame 1.528ms), the ratio is the finding.
  EVIDENCE:
  - benchmarks/testing_other_di/profile_phase_scheduler_breakdown.py:1-40
  - artifacts/ir_phase_improvement_20260926/cost_model.md:47-60
  IMPACT: C-C removes roughly a third of phase 3 on the warm and cold paths at 29 spells (~0.35-0.4ms per conjure
    here); the owner's before/after on the Windows tree confirms the number for the record.
  NEXT: Owner runs the harness before/after on their machine (B6).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T16:40:10Z
  TYPE: FACT
  CLAIM: Device tree updated: the nine scripted edits applied to the Windows tree (every anchor unique; all twelve
    touched files byte-identical to the tested worktree copies, verified with cmp). B5 done: the three patch docs
    now describe the landed shape (no `dag_edges` field - the edge rows are a projection of the topology
    sockets; `_add_build_details(dependencies)`; the `Spell.dependency_graph` reader UNKNOWN resolved; nine test
    files). Not run on the device tree (VM-only harness); owner-run suites and the breakdown harness are B6.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:780-1060
  - system_docs/patches/active/structural_snapshot_2026_09_26/architecture_patch.md:26-60
  - system_docs/patches/active/structural_snapshot_2026_09_26/component_patch_spell_compiler.md:30-40
  IMPACT: C-C is complete pending the owner's validation; the capture task can start from these rows.
  NEXT: Owner runs `python -m pytest -q tests/unit/melder/spellbook tests/component/melder/spellbook
    tests/integration/melder/spellbook` and the breakdown harness (workers=1) before/after; then review/accept.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T16:40:36Z
  TYPE: FACT
  CLAIM: Mailbox M0-32 (melder_0, 16:28:28Z) consumed: the owner notched `src/melder/__version__.py` to 0.2.59 and
    the release-note header with it; melder_0 retired the obsolete "One path still renders values the old way"
    bullet in the T1 section (as F0-14 anticipated) and added two override bullets; creation caches rebuild once
    under 0.2.59 with no generation change. Consequence for this lane: the I-1 release-note section (when the
    snapshot ships) goes under the 0.2.59 header; C-C itself is a no-behaviour-change internal edit and gets a
    one-line internal note at most. The 3 worktree failures (assets stamped 0.2.56) are the owner's asset rebuild.
  EVIDENCE:
  - release_docs/next_version_release.md
  - tickets/tasks/2026-09-26_build_site_plan_lowering_task.md
  IMPACT: No action now; the release note is melder_0's file this hour - coordinate before editing it.
  NEXT: Nothing until the owner reports B6.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T16:46:41Z
  TYPE: MEASURE
  CLAIM: Owner-run (Windows, .venv_new, 3.14t): `python -m pytest -q tests/unit/melder/spellbook
    tests/component/melder/spellbook tests/integration/melder/spellbook` -> 3532 passed, 2 skipped, 2 xfailed,
    2 xpassed in 18.38s on the C-C tree. Breakdown harness run with the default sweep (workers 1,2,5; repeats=5):
    workers=1 local_frame 3.433ms, requirements_symbolic 5.387ms, validation 3.747ms, plan_group 21.150ms - every
    phase 2-4x above the 15:18Z baseline (1.528 / 1.307 / 1.050 / 10.543ms), so the machine was loaded (another
    lane runs gauntlets on it) and this run is NOT a usable before/after; the VM ratio (-31..-34% on local_frame)
    stands as the indicative number. Correctness gate: green.
  EVIDENCE:
  - benchmarks/testing_other_di/profile_phase_scheduler_breakdown.py:1-40
  - tickets/stories/2026-09-26_structural_snapshot_story.md
  IMPACT: C-C accepted on correctness; the harness number is optional (a quiet rerun with
    BENCH_BREAKDOWN_WORKERS=1 BENCH_BREAKDOWN_REPEATS=15 would put it on record).
  NEXT: Consume M1-15 (self-dependency follow-up) before closing.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T16:46:41Z
  TYPE: FACT
  CLAIM: Mailbox M1-15 (melder_1, 16:42:46Z) consumed: the owner chose (melder_1's task, DECISION 16:39:36Z, option
    A) that a constructor taking its own class is refused through the readable SpellbookValidationError report
    (SELF_DEPENDENCY) instead of Phase 3's abort. Applied inside C-C (my files, lane in review): the rows-only
    `_build_local_frame_dag` now RECORDS a self-resolution (dependency ids, socket target, registry,
    `Spell.dependencies`) and keeps it out of `ordered_node_ids` (`sorted(set(ids) - {root}) + [root]`); the
    ValueError branch and its docstring clause are gone; the unit test asserts recording. Worktree: unit+component
    2947 passed, integration 579 passed; probe `Node(parent: Node)` conjure -> SpellbookValidationError listing
    SELF_DEPENDENCY and CIRCULAR_DEPENDENCY (melder_1 hides the second behind the first in their lane). Device tree
    updated (both files byte-identical to the worktree). melder_1 owns self_validation_strategy.py and
    spellbook_validation_error.py on top; ACK sent (F0-16).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:925-962
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_3.py:1075-1120
  - tickets/tasks/2026-09-26_report_self_referencing_constructor_as_validation_error_task.md:216-232
  IMPACT: The owner's green run predates this delta: one rerun of the same command is needed before closure.
  NEXT: Owner reruns the spellbook suites; then task 2 closes and the capture task opens.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
STATE 2026-09-26T16:12:08Z: IN_PROGRESS. B1 reads not started. Next: read compiler_phase_3.py `_build_local_frame_dag`
STATE 2026-09-26T16:19:33Z: IN_PROGRESS. B1 done (FACT note). Waiting on the owner's go for the B2 Propose->Confirm;
STATE 2026-09-26T16:38:34Z: IN_PROGRESS. Edits proven in the VM worktree (suites green, local_frame -31..-34%). Next: apply the
scripted edits to the device tree, re-verify, align the patch docs (B5), report; B6 owner-run.
STATE 2026-09-26T16:40:10Z: REVIEW. Edits on the device tree (12 files, byte-identical to the tested worktree); patch docs
aligned. Waiting on owner-run suites/harness (B6) and acceptance; then the capture task opens.
STATE 2026-09-26T16:46:41Z: REVIEW. Owner-run suites green on the first C-C tree; self-dependency follow-up (M1-15, option A)
applied on top in both trees; owner rerun of the spellbook suites pending, then closure and the capture task.
STATE 2026-09-26T16:58:29Z: DONE. Turned in by the owner; moved to completed/; release note bullet added under
"Faster conjure on large books". Successor: tickets/tasks/2026-09-26_capture_structural_payloads_at_conjure_end_task.md.
no src edit yet.
whole, then the dag package, spell.py build details, the presence strategy and the eight tests; then B2.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
