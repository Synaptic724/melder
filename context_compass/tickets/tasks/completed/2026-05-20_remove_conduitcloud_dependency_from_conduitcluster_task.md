# Task: remove conduitcloud dependency from conduitcluster
- Completed: 2026-05-20T09:32:43Z
- Summary: Closed after removing the method-time `ConduitCloud` dependency from `ConduitCluster`, injecting only the borrowed conduit registry plus `aetheric_frame_name`, and validating the focused cluster/cloud ring (`199 passed, 1 warning`).

## Metadata
- Task ID: TASK-2026-05-20-remove-conduitcloud-dependency-from-conduitcluster
- Story: none
- Epic: EPIC-2026-05-18-recompose-conduit-aether-spellbook-runtime-ownership
- Status: done
- Owner: codex
- Agent Name: refactor_0
- Priority: p1
- Created: 2026-05-20T09:15:54Z
- Updated: 2026-05-20T09:32:43Z

## Objective
Remove the method-time `ConduitCloud` dependency from `ConduitCluster` by
injecting only the borrowed conduit registry and `aetheric_frame_name`, then
rewire the cloud, interface, and focused tests to that narrower contract.

## Ticket Contract
- ENTRY_GATE: this task is routed on `attention_board.md`, the patch artifacts
  are linked, and the implementation mapping note is written before code edits.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/conduit/conduit_cluster.py`
  - `src/melder/aether/aetheric_frame/conduit_cloud.py`
  - `src/melder/utilities/interfaces/iconduitcluster.py`
  - focused cluster/cloud tests only
- DEPENDENCIES:
  - `tickets/tasks/2026-05-20_investigate_conduit_cluster_registry_decoupling_task.md`
  - `system_docs/patches/active/conduit_cluster_registry_decoupling/architecture_patch.md`
  - `system_docs/patches/active/conduit_cluster_registry_decoupling/component_patch_conduit_cluster.md`
  - `system_docs/patches/active/conduit_cluster_registry_decoupling/component_patch_conduit_cloud.md`
  - `system_docs/patches/active/conduit_cluster_registry_decoupling/component_patch_iconduitcluster.md`
- EXIT_GATE: `ConduitCluster` no longer takes `ConduitCloud` as a runtime
  collaborator, the cloud constructs it with borrowed registry +
  `aetheric_frame_name`, and the focused validation ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the raw registry contract
  proves insufficient and a wider resolver abstraction is required.

## Scope Boundaries
- In scope:
  - cluster constructor and local resolver
  - cloud method-call rewiring
  - cluster protocol signature rewiring
  - focused unit/component test fallout
- Out of scope:
  - broader cluster ownership redesign
  - Aether/frame API redesign
  - unrelated conduit/cloud cleanup

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user approved the narrow registry + frame-name cut and
  explicitly rejected shims, defensive fallback logic, and broader redesign.

## Steps / Checklist
- [ ] Finalize patch artifacts and map them to code slices.
- [ ] Patch `ConduitCluster` to store borrowed registry +
      `aetheric_frame_name` and resolve peers locally.
- [ ] Patch `ConduitCloud` and `IConduitCluster` to the new constructor and
      cloud-free method signatures.
- [ ] Update focused unit/component tests.
- [ ] Validate with `.\.venv_new`.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- cloud-free `ConduitCluster` runtime contract
- cloud constructor/call-site rewiring
- focused green validation

## Files / Paths Impacted
- `codex/context_compass/tickets/tasks/2026-05-20_remove_conduitcloud_dependency_from_conduitcluster_task.md`
- `codex/context_compass/attention_board.md`
- `codex/context_compass/artifact_board.md`

## Validation
- Not run.
- Recommended commands:
  - `.\.venv_new\Scripts\python.exe -m py_compile src\melder\aether\conduit\conduit_cluster.py src\melder\aether\aetheric_frame\conduit_cloud.py src\melder\utilities\interfaces\iconduitcluster.py tests\unit\melder\aether\conduit\test_conduit_cluster.py tests\component\melder\aether\conduit\test_conduit_component_cluster.py tests\unit\melder\aether\test_conduit_cloud.py tests\unit\melder\aether\test_aether.py`
  - `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\test_conduit_cluster.py tests\component\melder\aether\conduit\test_conduit_component_cluster.py tests\unit\melder\aether\test_conduit_cloud.py tests\unit\melder\aether\test_aether.py`

## Risks / Rollback Notes
- Risk: stale tests or fakes may still expect cloud-parameter method calls and
  the old one-arg cluster constructor.
  Rollback: restore the old constructor/signatures only if the focused ring
  shows the registry contract is actually insufficient.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
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
  - `system_docs/patches/active/conduit_cluster_registry_decoupling/architecture_patch.md`
  - `system_docs/patches/active/conduit_cluster_registry_decoupling/component_patch_conduit_cluster.md`
  - `system_docs/patches/active/conduit_cluster_registry_decoupling/component_patch_conduit_cloud.md`
  - `system_docs/patches/active/conduit_cluster_registry_decoupling/component_patch_iconduitcluster.md`
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: remove patch-lane artifacts after the code/test deltas are
  merged and validated.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-20T09:15:54Z
  TYPE: DECISION
  CLAIM: The implementation cut is intentionally narrow. `ConduitCluster` will
    take only the borrowed conduit registry and `aetheric_frame_name`, own a
    local `resolve_conduit_by_id(...)`, drop the `ConduitCloud` method
    parameter surface, and explicitly delete the borrowed registry reference on
    cleanup. No compatibility shim or broader resolver abstraction is allowed
    in this slice.
  EVIDENCE:
  - tickets/tasks/2026-05-20_investigate_conduit_cluster_registry_decoupling_task.md:69-103
  - src/melder/aether/conduit/conduit_cluster.py:172-458
  - src/melder/aether/aetheric_frame/conduit_cloud.py:300-396
  IMPACT: The next implementation pass can stay local to cluster/cloud/interface
    and the focused test ring.
  NEXT: map the patch sections to exact code/test edits, then patch the runtime
    files in that order.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T09:15:54Z
  TYPE: PLAN
  CLAIM: Patch-to-implementation mapping is explicit. `architecture_patch.md`
    defines the narrow registry-backed boundary. `component_patch_conduit_cluster.md`
    maps to constructor/state/signature changes plus the local
    `resolve_conduit_by_id(...)` helper and cleanup deletion. 
    `component_patch_conduit_cloud.md` maps to the new cluster constructor and
    cloud-free method calls. `component_patch_iconduitcluster.md` maps to the
    protocol signature cleanup. The edit order is: interface -> cluster ->
    cloud -> focused tests -> validation.
  EVIDENCE:
  - codex/context_compass/system_docs/patches/active/conduit_cluster_registry_decoupling/architecture_patch.md:1-41
  - codex/context_compass/system_docs/patches/active/conduit_cluster_registry_decoupling/component_patch_conduit_cluster.md:1-35
  - codex/context_compass/system_docs/patches/active/conduit_cluster_registry_decoupling/component_patch_conduit_cloud.md:1-31
  - codex/context_compass/system_docs/patches/active/conduit_cluster_registry_decoupling/component_patch_iconduitcluster.md:1-28
  IMPACT: The patch gate is satisfied and the implementation scope is concrete.
  NEXT: patch the runtime and focused tests, then run the declared validation ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T09:26:41Z
  TYPE: MEASURE
  CLAIM: The runtime cut compiles and most of the focused pytest ring is green.
    The remaining failures are stale `test_aether.py` expectations only:
    the frame-cloud stub tests still assert the old one-arg cluster
    constructor and the old `handle_join` / `handle_leave` /
    `refresh_member_shares` cloud-parameter calls.
  EVIDENCE:
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m py_compile src\\melder\\aether\\conduit\\conduit_cluster.py src\\melder\\aether\\aetheric_frame\\conduit_cloud.py src\\melder\\utilities\\interfaces\\iconduitcluster.py tests\\unit\\melder\\aether\\conduit\\test_conduit_cluster.py tests\\component\\melder\\aether\\conduit\\test_conduit_component_cluster.py tests\\unit\\melder\\aether\\test_aether.py`
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m pytest -q tests\\unit\\melder\\aether\\conduit\\test_conduit_cluster.py tests\\component\\melder\\aether\\conduit\\test_conduit_component_cluster.py tests\\unit\\melder\\aether\\test_conduit_cloud.py tests\\unit\\melder\\aether\\test_aether.py` -> `4 failed, 195 passed`
  - tests/unit/melder/aether/test_aether.py:1170-1178
  - tests/unit/melder/aether/test_aether.py:1234-1245
  - tests/unit/melder/aether/test_aether.py:1264-1272
  - tests/unit/melder/aether/test_aether.py:1362-1370
  IMPACT: The remaining fallout is stale focused-test expectation drift, not a
    new runtime design problem.
  NEXT: patch those four `test_aether.py` expectations, then rerun the same
    focused validation ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T09:28:06Z
  TYPE: BLOCKER
  CLAIM: The second focused pytest pass stopped in collection because my last
    `test_aether.py` expectation patch introduced one indentation error. This
    is syntax fallout in the test file, not a runtime or contract problem.
  EVIDENCE:
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m pytest -q tests\\unit\\melder\\aether\\conduit\\test_conduit_cluster.py tests\\component\\melder\\aether\\conduit\\test_conduit_component_cluster.py tests\\unit\\melder\\aether\\test_conduit_cloud.py tests\\unit\\melder\\aether\\test_aether.py` -> `IndentationError` at `tests/unit/melder/aether/test_aether.py:1245`
  IMPACT: Validation is temporarily blocked by one malformed assertion line in
    the focused test file.
  NEXT: fix the indentation at `tests/unit/melder/aether/test_aether.py:1245`
    and rerun the same focused validation ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-20T09:29:34Z
  TYPE: FACT
  CLAIM: The runtime cut is landed. `ConduitCluster` now takes only the
    borrowed conduit registry and `aetheric_frame_name`, stores a local
    `_resolve_conduit_by_id(...)` helper, drops the `ConduitCloud` method
    parameter surface, and explicitly deletes the borrowed registry on cleanup.
    `ConduitCloud` now constructs the cluster with those two values and calls
    the cloud-free cluster methods directly. `IConduitCluster` matches the new
    signatures.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_cluster.py:1-64
  - src/melder/aether/conduit/conduit_cluster.py:172-458
  - src/melder/aether/conduit/conduit_cluster.py:487-500
  - src/melder/aether/aetheric_frame/conduit_cloud.py:300-396
  - src/melder/utilities/interfaces/iconduitcluster.py:1-94
  IMPACT: The cluster no longer needs the cloud object as a runtime
    collaborator, only the borrowed registry and frame-name context chosen at
    cloud construction time.
  NEXT: keep the lane in review unless you want a broader suite run or the next
    cluster/cloud follow-up cut.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T09:29:34Z
  TYPE: MEASURE
  CLAIM: The focused validation ring for the cluster/cloud decoupling cut is
    green on `.\.venv_new` after aligning the cluster unit/component tests and
    the `test_aether.py` cloud stub expectations.
  EVIDENCE:
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m py_compile src\\melder\\aether\\conduit\\conduit_cluster.py src\\melder\\aether\\aetheric_frame\\conduit_cloud.py src\\melder\\utilities\\interfaces\\iconduitcluster.py tests\\unit\\melder\\aether\\conduit\\test_conduit_cluster.py tests\\component\\melder\\aether\\conduit\\test_conduit_component_cluster.py tests\\unit\\melder\\aether\\test_aether.py`
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m pytest -q tests\\unit\\melder\\aether\\conduit\\test_conduit_cluster.py tests\\component\\melder\\aether\\conduit\\test_conduit_component_cluster.py tests\\unit\\melder\\aether\\test_conduit_cloud.py tests\\unit\\melder\\aether\\test_aether.py` -> `199 passed, 1 warning`
  IMPACT: The narrowed registry-backed contract is stable across the direct
    runtime and focused test surfaces it changed.
  NEXT: `Not run.` for the broader suite; only widen validation if you want the
    larger fallout map next.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Active implementation lane for removing the method-time `ConduitCloud`
dependency from `ConduitCluster`.
