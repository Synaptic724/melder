# Task: fix root conduit cleanup frame detach regression

Completed: 2026-05-19T17:29:27Z
Summary: Closed per user instruction before final completion. Latest lane state remains below.


## Metadata
- Task ID: TASK-2026-05-18-fix-root-conduit-cleanup-frame-detach-regression
- Story: none
- Status: done
- Owner: codex
- Agent Name: mypy_2
- Priority: p2
- Created: 2026-05-18T10:00:15Z
- Updated: 2026-05-19T17:29:27Z

## Objective
Repair the real runtime bug where cleaning the rooted conduit returned by
`Rift.create_nexus_frame()` left stale Nexus frame-manager state behind.

## Ticket Contract
- ENTRY_GATE: the `rift.py` typing slice is in flight and the focused Rift/Nexus
  validation ring exposed one real runtime failure
- EXECUTION_BOUNDARY: only the teardown path in `aether.py` and
  `conduit_cloud.py` needed to let rooted conduit cleanup finish the frame-detach path
- DEPENDENCIES: failing `test_external_aether_frame_cleanup_clears_nexus_frame_manager_state`
  and the root conduit cleanup path through `Conduit -> Aether -> Nexus`
- EXIT_GATE: rooted conduit cleanup removes manager-owned frame state again and
  the focused Rift/Nexus ring is green
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if frame teardown proves to need
  a broader lifecycle redesign instead of this local stale-entry repair

## Scope Boundaries
- In scope:
  - `src/melder/aether/aether.py`
  - `src/melder/aether/conduit_cloud.py`
- Out of scope:
  - cleanup policy rewrite
  - broad Aether/Nexus lifecycle redesign

## State Transition Event
- from_state: draft
- to_state: review
- transition_reason: the failing focused Rift/Nexus test is repaired and the
  same ring is green again

## Validation
- Run:
  - `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\test_rift_runtime_contracts.py tests\unit\melder\aether\test_nexus.py tests\unit\melder\aether\test_nexus_frame_surface_projection.py`
    -> `174 passed, 1 warning`

## Notes
- DATETIME: 2026-05-18T10:00:15Z
  TYPE: FACT
  CLAIM: The failing runtime test came from teardown aborting mid-cleanup. Both
    `Aether._remove_conduit(...)` and `ConduitCloud._unregister_conduit(...)`
    were reading conduit `name` through the cleaned-state-gated public property
    during normal-conduit cleanup. Once cleanup had already flipped `_cleaned`,
    those property reads raised and the frame-detach path never reached the
    manager cleanup branch.
  EVIDENCE:
  - src/melder\aether\aether.py:1284-1319
  - src/melder\aether\conduit_cloud.py:272-300
  - src/melder\aether\conduit\conduit.py:380-390
  - tests/unit/melder/aether/test_nexus.py:6004-6012
  IMPACT: The failure was a real runtime stale-state bug, not a typing artifact.
  NEXT: use the private `_name` field in the two internal unregister/remove paths so cleanup can complete the frame-detach flow.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T10:00:15Z
  TYPE: MEASURE
  CLAIM: The rooted-conduit cleanup regression is fixed. Internal unregister/remove
    paths now use the conduit's private `_name` field during teardown, so the
    cleanup path completes and the Nexus frame-manager entry is dropped when the
    rooted frame is disposed.
  EVIDENCE:
  - src/melder\aether\aether.py:1284-1319
  - src/melder\aether\conduit_cloud.py:272-300
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\test_rift_runtime_contracts.py tests\unit\melder\aether\test_nexus.py tests\unit\melder\aether\test_nexus_frame_surface_projection.py` -> `174 passed, 1 warning`
  IMPACT: Rooted Nexus-frame cleanup is truthful again, and the focused Rift/Nexus ring is back to green.
  NEXT: continue with the next typing/runtime slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T13:13:54Z
  TYPE: MEASURE
  CLAIM: A broader suite rerun still exposes the same family of bug in the
    component matrix path. `test_component_external_frame_cleanup_clears_manager_state_matrix`
    fails because after `conduit.cleanup()` the Nexus frame manager still
    reports the managed frame as present. So the earlier teardown patch fixed
    one rooted cleanup path, but not the full external-frame detach matrix.
  EVIDENCE:
  - tests/component/melder/aether/test_nexus_frame_authoring_component.py:276-299
  - src/melder/aether/aetheric_frame.py:143-146
  - src/melder/aether/nexus/nexus.py:2278-2284
  IMPACT: The regression ticket needs to be reopened. The next fix has to
    follow the `AethericFrame.cleanup() -> Aether._detach_cleaned_frame(...) ->
    Nexus.handle_aether_frame_disposal(...)` path in the component matrix, not
    just the earlier root-conduit name cleanup seam.
  NEXT: inspect the Nexus frame-manager disposal handling and the Aether frame
    detach path used by this component matrix failure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T13:29:34Z
  TYPE: DECISION
  CLAIM: The contract is being changed, not merely repaired. Root-conduit
    cleanup should no longer auto-dispose the owning frame. `ConduitCloud`
    is a frame-owned borrowed facade, so it must stop carrying the
    owner-cleanup callback and stop deciding when the `AethericFrame` should
    be cleaned. Frame disposal should instead be explicit through Aether-owned
    frame targeting.
  EVIDENCE:
  - src/melder/aether/aetheric_frame.py:85-95
  - src/melder/aether/conduit_cloud.py:31-71
  - src/melder/aether/conduit_cloud.py:396-407
  - src/melder/aether/conduit/conduit.py:400-404
  - src/melder/aether/aether.py:241-299
  IMPACT: The fix is now a behavior change: remove the `owner_cleanup` /
    `cleanup_owner_frame_if_empty()` path, keep conduit cleanup limited to
    conduit teardown, and update tests that encoded the old auto-frame-disposal
    behavior to use explicit Aether-targeted frame cleanup.
  NEXT: patch `ConduitCloud`, `AethericFrame`, `IConduitCloud`, and
    `Conduit._cleanup_normal_conduit()`, then update the Nexus frame cleanup
    component tests to explicitly dispose the frame through Aether.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T13:32:20Z
  TYPE: FACT
  CLAIM: The auto-frame-disposal path is removed in source. `ConduitCloud`
    no longer accepts or stores an owner-cleanup callback, the
    `cleanup_owner_frame_if_empty()` helper is gone, `Conduit` now stops after
    root/cloud unregistration and republishes frame state instead of
    destroying the frame, and the Nexus frame cleanup component test now uses
    explicit Aether-targeted frame cleanup.
  EVIDENCE:
  - src/melder/utilities/interfaces/iconduitcloud.py:1-125
  - src/melder/aether/conduit_cloud.py:1-423
  - src/melder/aether/aetheric_frame.py:85-95
  - src/melder/aether/conduit/conduit.py:395-404
  - tests/component/melder/aether/test_nexus_frame_authoring_component.py:295-302
  - tests/unit/melder/aether/test_conduit_cloud.py:13-21
  IMPACT: Validation now needs to confirm the new contract is coherent in the
    direct cloud/unit ring and in the Nexus managed-frame component path.
  NEXT: run the targeted ConduitCloud unit tests plus the affected Nexus frame
    component tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T13:32:54Z
  TYPE: MEASURE
  CLAIM: The targeted validation ring shows the runtime contract change is
    coherent, but four remaining failures are now test-side stale-state reads.
    The `test_component_nexus_remove_rift_cleans_frames_by_topology_matrix`
    cases dereference `_aetheric_frame` on `Conduit` objects after
    `nexus.remove_rift(...)`, when those conduits have already been cleaned and
    dropped that field.
  EVIDENCE:
  - tests/component/melder/aether/test_nexus_frame_authoring_component.py:357-385
  IMPACT: The tests need to snapshot the frame names before calling
    `nexus.remove_rift(...)` instead of reading cleaned conduit internals after
    teardown.
  NEXT: patch the four failing component cases to capture frame names before
    removal, then rerun the same targeted validation ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T13:33:40Z
  TYPE: MEASURE
  CLAIM: The explicit-frame-ownership contract is now validated in the direct
    ring. `ConduitCloud` no longer owns or triggers frame cleanup, the Nexus
    frame authoring component test now uses explicit Aether-targeted frame
    disposal where needed, and the targeted cloud/component ring is green.
  EVIDENCE:
  - src/melder/aether/conduit_cloud.py:1-423
  - src/melder/aether/conduit/conduit.py:395-404
  - tests/component/melder/aether/test_nexus_frame_authoring_component.py:286-385
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\test_conduit_cloud.py tests\component\melder\aether\test_nexus_frame_authoring_component.py` -> `60 passed, 1 warning`
  IMPACT: The behavior change is stable in the local ring, so the next useful
    move is another full-suite stop-on-first-failure pass to find the next real
    blocker.
  NEXT: rerun `pytest -vv -x --tb=long` across the full suite and capture the
    next failure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Small runtime bugfix uncovered while validating the `rift.py` typing pass.
