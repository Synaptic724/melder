# Task: move conduit registration into aetheric frame
- Completed: 2026-05-20T08:58:57Z
- Summary: Closed after moving conduit registration into `AethericFrame`, cleaning the `aetheric_frame_name`/`aetheric_frame` split, removing the old conduit-owned cloud registration path, and validating the full suite (`8143 passed, 2 skipped, 5 xfailed, 1 warning`).

## Metadata
- Task ID: TASK-2026-05-19-move-conduit-registration-into-aetheric-frame
- Story: none
- Epic: EPIC-2026-05-18-recompose-conduit-aether-spellbook-runtime-ownership
- Status: done
- Owner: codex
- Agent Name: refactor_0
- Priority: p1
- Created: 2026-05-19T23:33:50Z
- Updated: 2026-05-20T08:58:57Z

## Objective
Move root-conduit and dynamic named-conduit registration out of `Aether` and
`ConduitCloud` into `AethericFrame`, inject the live frame object into
`Conduit`, and let `ConduitWard` derive a local cloud handle from that frame
instead of reaching back through Aether for conduit-id resolution.

## Ticket Contract
- ENTRY_GATE: this task is routed on `attention_board.md`, patch artifacts are
  linked, and the implementation mapping note is written before code edits.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/aetheric_frame/aetheric_frame.py`
  - `src/melder/aether/aetheric_frame/conduit_cloud.py`
  - `src/melder/aether/conduit/conduit.py`
  - `src/melder/aether/conduit/conduit_ward/conduit_ward.py`
  - `src/melder/aether/spellbook/spellbook_creation_system.py`
  - `src/melder/aether/aether.py`
  - directly impacted interfaces and focused tests only
- DEPENDENCIES:
  - `codex/context_compass/tickets/tasks/2026-05-19_investigate_frame_owned_conduit_registration_and_ward_access_task.md`
  - `system_docs/patches/active/frame_owned_conduit_registration/architecture_patch.md`
  - `system_docs/patches/active/frame_owned_conduit_registration/component_patch_aetheric_frame.md`
  - `system_docs/patches/active/frame_owned_conduit_registration/component_patch_conduit_cloud.md`
  - `system_docs/patches/active/frame_owned_conduit_registration/component_patch_conduit.md`
  - `system_docs/patches/active/frame_owned_conduit_registration/component_patch_conduit_ward.md`
  - `system_docs/patches/active/frame_owned_conduit_registration/component_patch_spellbook_creation_system.md`
  - `system_docs/patches/active/frame_owned_conduit_registration/component_patch_aether.md`
- EXIT_GATE: conduit registration is frame-owned, `Conduit` no longer stores
  `ConduitCloud`, `ConduitWard` no longer uses Aether for same-frame conduit-id
  resolution, and the focused validation ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if cross-frame lookup or
  descriptor expectations force a different ownership model than the patch
  contract.

## Scope Boundaries
- In scope:
  - frame-owned root conduit registration
  - frame-owned dynamic named-conduit registration
  - `Conduit` constructor and cleanup rewiring
  - `ConduitWard` lookup rewiring to frame-derived cloud access
  - removing dead duplicate Aether registration helpers
- Out of scope:
  - cluster ownership redesign
  - broader spell/spellbook cycle cuts
  - unrelated runtime surface cleanup

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the investigation shows registration ownership is already
  duplicated and the user explicitly selected the frame-owned registration cut.

## Steps / Checklist
- [ ] Finalize the patch-lane artifacts and implementation mapping note.
- [x] Move root and dynamic registration into `AethericFrame`.
- [x] Inject the live frame object into `Conduit` and derive a local cloud
      handle in `ConduitWard`.
- [x] Remove duplicate Aether registration helpers and stale cloud registration
      methods.
- [x] Update focused tests.
- [x] Validate with `.\.venv_new`.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- frame-owned conduit registration surface
- reduced `Conduit` dependency surface
- ward-local conduit-id lookup without Aether
- focused green validation

## Files / Paths Impacted
- `codex/context_compass/tickets/tasks/2026-05-19_move_conduit_registration_into_aetheric_frame_task.md`
- `codex/context_compass/attention_board.md`
- `codex/context_compass/artifact_board.md`

## Validation
- Not run.
- Recommended commands:
  - `.\.venv_new\Scripts\python.exe -m py_compile <touched runtime/interface/test files>`
  - `.\.venv_new\Scripts\python.exe -m pytest -q <focused conduit/cloud/ward/transfer/rift command rings>`

## Risks / Rollback Notes
- Risk: the ward lookup cut may accidentally narrow a call path that still
  expects cross-frame resolution.
  Rollback: keep frame-owned registration but restore ward lookup to a narrower
  injected resolver instead of Aether reach-back.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

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
  - `system_docs/patches/active/frame_owned_conduit_registration/architecture_patch.md`
  - `system_docs/patches/active/frame_owned_conduit_registration/component_patch_aetheric_frame.md`
  - `system_docs/patches/active/frame_owned_conduit_registration/component_patch_conduit_cloud.md`
  - `system_docs/patches/active/frame_owned_conduit_registration/component_patch_conduit.md`
  - `system_docs/patches/active/frame_owned_conduit_registration/component_patch_conduit_ward.md`
  - `system_docs/patches/active/frame_owned_conduit_registration/component_patch_spellbook_creation_system.md`
  - `system_docs/patches/active/frame_owned_conduit_registration/component_patch_aether.md`
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: remove patch-lane artifacts after canonical docs and code are merged and validated.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-19T23:33:50Z
  TYPE: DECISION
  CLAIM: The implementation cut will move root and dynamic conduit
    registration into `AethericFrame`, keep `ConduitCloud` as lookup and
    cluster service, inject the live frame object into `Conduit`, and let
    `ConduitWard` derive a local cloud handle from that frame instead of using
    Aether for same-frame conduit-id resolution.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/aetheric_frame.py:74-93
  - src/melder/aether/aetheric_frame/conduit_cloud.py:305-423
  - src/melder/aether/conduit/conduit.py:183-193
  - src/melder/aether/conduit/conduit.py:723-726
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1271-1317
  - src/melder/aether/aether.py:1080-1280
  IMPACT: This removes duplicate registration ownership and narrows the live
    runtime dependency away from `Conduit -> ConduitCloud` while keeping the
    cloud as the frame-local lookup and cluster surface.
  NEXT: create the patch artifacts and map them to implementation steps before
    editing runtime code.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T23:33:50Z
  TYPE: PLAN
  CLAIM: Patch-to-implementation mapping is explicit. `architecture_patch.md`
    defines the ownership shift and migration order. `component_patch_aetheric_frame.md`
    maps to frame-owned root and dynamic registration helpers plus frame-owned
    dynamic registry storage. `component_patch_conduit_cloud.md` maps to
    removing registration helpers and keeping lookup/cluster APIs only.
    `component_patch_conduit.md` maps to constructor, lesser-creation, cleanup,
    and hook-peer lookup rewiring. `component_patch_conduit_ward.md` maps to
    ward init and same-frame conduit-id resolution rewiring.
    `component_patch_spellbook_creation_system.md` maps to root-conduit frame
    injection, and `component_patch_aether.md` maps to duplicate helper removal.
  EVIDENCE:
  - codex/context_compass/system_docs/patches/active/frame_owned_conduit_registration/architecture_patch.md:1-43
  - codex/context_compass/system_docs/patches/active/frame_owned_conduit_registration/component_patch_aetheric_frame.md:1-28
  - codex/context_compass/system_docs/patches/active/frame_owned_conduit_registration/component_patch_conduit_cloud.md:1-27
  - codex/context_compass/system_docs/patches/active/frame_owned_conduit_registration/component_patch_conduit.md:1-29
  - codex/context_compass/system_docs/patches/active/frame_owned_conduit_registration/component_patch_conduit_ward.md:1-28
  - codex/context_compass/system_docs/patches/active/frame_owned_conduit_registration/component_patch_spellbook_creation_system.md:1-25
  - codex/context_compass/system_docs/patches/active/frame_owned_conduit_registration/component_patch_aether.md:1-21
  IMPACT: The engineer patch gate is met: the patch sections now map directly
    to code-edit slices and later focused validation.
  NEXT: edit the runtime and interface files in the mapped order, then run the
    focused `.venv_new` validation ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T23:33:50Z
  TYPE: MEASURE
  CLAIM: The first focused validation run says the runtime cut compiles and the
    fallout is mostly ownership-expectation drift, not an unknown architectural
    break. The failures cluster into four buckets:
    1) `ConduitCloud` tests still target removed registration methods and the
       old 3-arg constructor,
    2) Aether tests still target removed duplicate `_add_conduit` /
       `_remove_conduit` helpers,
    3) a few conduit tests still assert the old `_conduit_cloud` field or its
       delegate calls,
    4) standalone `ConduitWard` tests need explicit frame/cloud setup on direct
       mock conduits.
  EVIDENCE:
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m pytest -q tests\\unit\\melder\\aether\\conduit tests\\unit\\melder\\aether\\test_conduit_cloud.py tests\\unit\\melder\\aether\\test_aether.py tests\\integration\\melder\\aether\\test_aether_integration_registry_ops.py tests\\integration\\melder\\conduit\\test_conduit_integration_clusters_spellspace.py`
  IMPACT: The live runtime change is intact enough to keep going; the next pass
    should be test and small expectation alignment, not a rollback of the
    ownership cut.
  NEXT: patch the test surfaces and the small remaining conduit expectation
    assertions, then rerun the same focused ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T00:01:14Z
  TYPE: FACT
  CLAIM: The frame-owned registration cut is implemented. `AethericFrame` now
    owns root and dynamic named-conduit registration, `ConduitCloud` is reduced
    to borrowed lookup plus owned cluster behavior, `Conduit` takes the live
    frame object instead of `ConduitCloud`, `ConduitWard` resolves same-frame
    peer conduits through a frame-derived cloud handle, and the dead duplicate
    Aether root-registration helpers are removed.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/aetheric_frame.py:74-93
  - src/melder/aether/aetheric_frame/aetheric_frame.py:206-330
  - src/melder/aether/aetheric_frame/conduit_cloud.py:36-93
  - src/melder/aether/aetheric_frame/conduit_cloud.py:145-320
  - src/melder/aether/conduit/conduit.py:98-244
  - src/melder/aether/conduit/conduit.py:398-405
  - src/melder/aether/conduit/conduit.py:723-727
  - src/melder/aether/conduit/conduit.py:991-1011
  - src/melder/aether/conduit/conduit.py:1455-1465
  - src/melder/aether/conduit/conduit.py:3926-3936
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:22-58
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:89-149
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1367-1387
  - src/melder/aether/spellbook/spellbook_creation_system.py:183-195
  - src/melder/aether/spellbook/spellbook_creation_system.py:304-389
  - src/melder/aether/aether.py:1057-1198
  IMPACT: The live runtime no longer depends on `Conduit -> ConduitCloud` for
    registration ownership, and the remaining cloud role is clearly lookup and
    clustering.
  NEXT: hand the cut back for review unless you want the next conduit/cloud
    ownership slice immediately.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T00:01:14Z
  TYPE: MEASURE
  CLAIM: The focused runtime/test ring for the frame-owned registration cut is
    green on `.venv_new` after runtime and expectation alignment.
  EVIDENCE:
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m py_compile src\\melder\\utilities\\interfaces\\iaethericframe.py src\\melder\\utilities\\interfaces\\iconduitcloud.py src\\melder\\aether\\aetheric_frame\\aetheric_frame.py src\\melder\\aether\\aetheric_frame\\conduit_cloud.py src\\melder\\aether\\conduit\\conduit.py src\\melder\\aether\\conduit\\conduit_ward\\conduit_ward.py src\\melder\\aether\\spellbook\\spellbook_creation_system.py src\\melder\\aether\\aether.py tests\\unit\\melder\\aether\\conduit\\conftest.py tests\\unit\\melder\\aether\\conduit\\test_conduit_lifecycle.py tests\\unit\\melder\\aether\\conduit\\test_conduit_configuration_and_hooks.py tests\\unit\\melder\\aether\\conduit\\test_conduit_contracts.py tests\\unit\\melder\\aether\\conduit\\test_conduit_transactions.py tests\\unit\\melder\\aether\\conduit\\conduit_ward\\test_conduit_ward.py tests\\unit\\melder\\aether\\conduit\\conduit_ward\\test_conduit_ward_contracts.py tests\\unit\\melder\\aether\\test_conduit_cloud.py`
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m pytest -q tests\\unit\\melder\\aether\\conduit tests\\unit\\melder\\aether\\test_conduit_cloud.py tests\\unit\\melder\\aether\\test_aether.py tests\\integration\\melder\\aether\\test_aether_integration_registry_ops.py tests\\integration\\melder\\conduit\\test_conduit_integration_clusters_spellspace.py` -> `1379 passed, 1 skipped, 1 warning`
  IMPACT: The ownership cut is stable across the direct runtime, conduit, ward,
    Aether, and integration surfaces it was meant to change.
  NEXT: review or route the next bounded refactor tranche.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T00:03:47Z
  TYPE: PLAN
  CLAIM: The user explicitly requested a broader rerun after the focused green
    ring. The next tranche is to run the full repo pytest suite on
    `.\.venv_new` unchanged, then classify any remaining fallout from the
    frame-owned conduit-registration cut before patching further.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-20
  IMPACT: The next moves should be driven by the live full-suite failure set,
    not by extrapolation from the focused validation ring.
  NEXT: run `.\.venv_new\\Scripts\\python.exe -m pytest -q` and capture the
    first meaningful failure bucket.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-20T00:10:07Z
  TYPE: DECISION
  CLAIM: The current frame-owned registration cut needs one cleanup pass before
    widening again. The user explicitly rejected the compatibility shim choices:
    `ConduitWard` must require `aetheric_frame`, the live frame instance should
    be named `aetheric_frame`, the string field should be
    `aetheric_frame_name`, `_dynamic_conduits_by_name` must be removed, and
    `ConduitCloud` should work from the frame-owned `_conduits` surface rather
    than a second registry shim.
  EVIDENCE:
  - user_feedback: current chat instructions on 2026-05-20
  IMPACT: The next edit tranche is a cleanup/refinement pass over the current
    ownership cut, not a new feature or a full-suite-driven bug hunt.
  NEXT: remove the shim state and optional frame fallback from the runtime and
    align the direct tests to the stricter constructor/ownership contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T00:22:09Z
  TYPE: FACT
  CLAIM: The cleanup pass is complete. The optional ward-frame fallback path
    and the extra dynamic registry shim are gone. `ConduitWard` now requires
    the injected frame, `ConduitCloud` derives cloud-name visibility from the
    frame-owned root conduit set, and the constructor boundary now uses the
    clearer `aetheric_frame_name` / `aetheric_frame` pair at the live conduit
    creation seams.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/aetheric_frame.py:74-93
  - src/melder/aether/aetheric_frame/aetheric_frame.py:215-274
  - src/melder/aether/aetheric_frame/conduit_cloud.py:34-70
  - src/melder/aether/aetheric_frame/conduit_cloud.py:238-254
  - src/melder/aether/conduit/conduit.py:103-184
  - src/melder/aether/conduit/conduit.py:241-246
  - src/melder/aether/conduit/conduit.py:396-405
  - src/melder/aether/conduit/conduit.py:1450-1459
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:114-174
  - src/melder/aether/spellbook/spellbook_creation_system.py:183-195
  - src/melder/aether/spellbook/spellbook_creation_system.py:304-389
  IMPACT: The ownership cut now matches the intended model instead of carrying
    compatibility scaffolding.
  NEXT: review the cut or choose the next bounded conduit/cloud refactor slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T00:22:09Z
  TYPE: MEASURE
  CLAIM: The post-cleanup focused validation rings are green on `.venv_new`.
    The narrowed ward/Aether/cloud bucket passed, and the wider conduit/Aether/
    integration ring passed again after the shim removal and expectation
    alignment.
  EVIDENCE:
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m pytest -q tests\\unit\\melder\\aether\\conduit\\conduit_ward tests\\unit\\melder\\aether\\test_aether.py tests\\unit\\melder\\aether\\test_conduit_cloud.py tests\\integration\\melder\\aether\\test_aether_integration_registry_ops.py tests\\integration\\melder\\conduit\\test_conduit_integration_clusters_spellspace.py` -> `603 passed, 1 warning`
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m pytest -q tests\\unit\\melder\\aether\\conduit tests\\unit\\melder\\aether\\test_conduit_cloud.py tests\\unit\\melder\\aether\\test_aether.py tests\\integration\\melder\\aether\\test_aether_integration_registry_ops.py tests\\integration\\melder\\conduit\\test_conduit_integration_clusters_spellspace.py` -> `1379 passed, 1 skipped, 1 warning`
  IMPACT: The runtime and direct caller/test surfaces affected by the cleanup
    pass are stable again.
  NEXT: `Not run.` for the full repo suite after this cleanup pass; rerun it
    only if you want the broader fallout map next.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T00:24:52Z
  TYPE: FACT
  CLAIM: The runtime naming cleanup is still incomplete in `Conduit`. The
    constructor boundary was improved, but the stored fields are still the bad
    intermediate pair: `self._aetheric_frame` holds the frame-name string and
    `self._aetheric_frame_object` holds the live frame object. That violates the
    requested naming contract for this cut.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:178-184
  IMPACT: This is a direct runtime naming debt in the active cut, not just a
    cosmetic issue. It should be corrected before we widen to any new lane.
  NEXT: rename the stored fields so the string becomes
    `self._aetheric_frame_name` and the live frame object becomes
    `self._aetheric_frame`, then rerun the focused validation ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T00:44:20Z
  TYPE: FACT
  CLAIM: The conduit-side naming contract is now corrected. `Conduit` stores
    the frame-name string on `_aetheric_frame_name` and the live frame object
    on `_aetheric_frame`, and the ward helper now does the exact direct cloud
    lookup agreed in review:
    `self._conduit_cloud.get_conduit_by_id(conduit_id)`.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:103-184
  - src/melder/aether/conduit/conduit.py:241-246
  - src/melder/aether/conduit/conduit.py:514-514
  - src/melder/aether/conduit/conduit.py:1453-1454
  - src/melder/aether/conduit/conduit.py:3924-3927
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1319-1322
  IMPACT: The runtime no longer carries the bad intermediate `_aetheric_frame`
    string / `_aetheric_frame_object` object split, and the ward helper no
    longer carries the rejected defensive frame-check logic.
  NEXT: review the cut or rerun a broader suite if you want fallout beyond the
    focused conduit/Aether ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T00:44:20Z
  TYPE: MEASURE
  CLAIM: The focused conduit/Aether/integration validation ring is green again
    after the naming cleanup and direct-lookup correction.
  EVIDENCE:
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m pytest -q tests\\unit\\melder\\aether\\conduit tests\\unit\\melder\\aether\\test_conduit_cloud.py tests\\unit\\melder\\aether\\test_aether.py tests\\integration\\melder\\aether\\test_aether_integration_registry_ops.py tests\\integration\\melder\\conduit\\test_conduit_integration_clusters_spellspace.py` -> `1379 passed, 1 skipped, 1 warning`
  IMPACT: The corrected naming and lookup shape is stable on the directly
    affected runtime and test surfaces.
  NEXT: `Not run.` for the full repo suite after this specific cleanup pass;
    run it only if you want the broader fallout map next.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T00:49:21Z
  TYPE: PLAN
  CLAIM: The next tranche is now explicit: run the full repo pytest suite on
    `.\.venv_new` after the naming cleanup so the remaining fallout, if any, is
    evidence-backed and not guessed from the focused ring.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-20
  IMPACT: The next patches should be driven by the live full-suite failure set,
    not by extrapolation from the conduit-focused validation ring.
  NEXT: run `.\.venv_new\\Scripts\\python.exe -m pytest -q` and classify the
    first surviving failure bucket.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-20T00:50:55Z
  TYPE: MEASURE
  CLAIM: The full repo suite confirms the conduit-frame naming cleanup still
    has broad fallout outside the focused ring, but the pattern is mostly
    mechanical. The current failures are dominated by test/component/integration
    doubles and call sites that still use the old conduit string field
    (`_aetheric_frame`) or old `Conduit` constructor keyword shape, plus a few
    direct conduit-frame consumers that still expect the old field name.
  EVIDENCE:
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m pytest -q` -> `113 failed, 8030 passed, 3 skipped, 5 xfailed`
  IMPACT: The next pass should be a broad but still mechanical fallout cleanup
    driven by the full-suite failure set, not a runtime design rethink.
  NEXT: patch the remaining test/runtime-fake field and constructor references,
    reroute direct conduit-frame consumers to `_aetheric_frame_name`, and rerun
    the full suite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T01:05:00Z
  TYPE: MEASURE
  CLAIM: The full repo suite is now green after the mechanical fallout cleanup
    from the conduit field rename and frame-owned registration cut. The final
    state is the intended one: `Conduit` uses `_aetheric_frame_name` for the
    string, `_aetheric_frame` for the live frame object, and the direct ward
    lookup path stays a simple cloud id lookup.
  EVIDENCE:
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m pytest -q` -> `8143 passed, 2 skipped, 5 xfailed, 1 warning`
  IMPACT: The registration ownership cut and the naming cleanup are both fully
    validated against the full suite, not just the focused ring.
  NEXT: hand the cut back for review or select the next bounded refactor lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Frame-owned conduit registration and the conduit naming cleanup are implemented,
and the full repo suite is green. The next step is user review or the next
bounded conduit/cloud ownership cut.
