# Task: fix frame viewer and acl return contract cluster

Completed: 2026-05-19T17:29:27Z
Summary: Closed per user instruction after validation handoff. Latest lane state and validation notes remain below.


## Metadata
- Task ID: TASK-2026-05-19-fix-frame-viewer-and-acl-return-contract-cluster
- Story: none
- Status: done
- Owner: codex
- Agent Name: mypy_2
- Priority: p1
- Created: 2026-05-19T11:28:53Z
- Updated: 2026-05-19T17:29:27Z

## Objective
Fix the current `frame_viewer.py` and `frame_acl_container.py` mypy cluster by
correcting override/return contracts and tightening any stale public interface
surfaces that are causing `Any` to leak through.

## Ticket Contract
- ENTRY_GATE: the user supplied a bounded AR viewer + ACL return-contract mypy
  cluster and explicitly asked to tackle it next.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py`
  - `src/melder\aether\nexus\acl\frame_acl_container.py`
  - directly implicated public interfaces only where the surface is real:
    - `src/melder\utilities\interfaces\iframeviewer.py`
    - `src/melder\utilities\interfaces\iframeaclcontainer.py`
    - `src/melder\utilities\interfaces\iframeaclviewconfiguration.py`
    - `src/melder\utilities\interfaces\iframeaclcommandconfiguration.py`
    - `src/melder\utilities\interfaces\iframeaclcodegenconfiguration.py`
  - directly implicated concrete helper/model files only if interface truth
    requires them
- DEPENDENCIES:
  - current Rift-backed frame viewer ownership model
  - current frame-local ACL container/profile chain model
  - no casts, no shims, no fake local protocols
- EXIT_GATE:
  - the targeted `frame_viewer.py` and `frame_acl_container.py` cluster is gone
  - override/return contracts are truthful at the public interface boundary
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the correct public contract
  shape is ambiguous between generic viewer/ACL interfaces and the concrete AR
  runtime objects

## Scope Boundaries
- In scope:
  - `frame_viewer` override mismatches
  - `frame_acl_container` `no-any-return` cluster
  - truthful interface updates for those return surfaces
- Out of scope:
  - unrelated AR viewer or ACL redesign
  - repo-wide mypy debt outside this exact lane

## Steps / Checklist
- [ ] inspect the concrete return surfaces around the reported lines
- [ ] patch public interfaces first where they are lying
- [ ] patch local concrete return annotations/narrowings
- [ ] rerun targeted mypy on the bounded cluster
- [ ] continue only after documenting the result
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- a bounded frame-viewer/ACL return-contract fix

## Files / Paths Impacted
- `src/melder\aether\nexus\rift\frame_viewer\frame_viewer.py`
- `src/melder\aether\nexus\acl\frame_acl_container.py`
- `src/melder\utilities\interfaces\iframeviewer.py`
- `src/melder\utilities\interfaces\iframeaclcontainer.py`
- `src/melder\utilities\interfaces\iframeaclviewconfiguration.py`
- `src/melder\utilities\interfaces\iframeaclcommandconfiguration.py`
- `src/melder\utilities\interfaces\iframeaclcodegenconfiguration.py`
- only if required by truthful fix:
  - directly implicated concrete ACL/viewer helper or projection files

## Validation
- Not run.
- Recommended commands:
  - `.\.venv_new\Scripts\python.exe -m mypy --show-error-codes --show-column-numbers --no-error-summary src\melder\aether\nexus\rift\frame_viewer\frame_viewer.py src\melder\aether\nexus\acl\frame_acl_container.py`

## Risks / Rollback Notes
- Medium risk. The likely fix is interface truth plus local narrowing, but the
  wrong move would be widening viewer or ACL interfaces in a way that hides
  real AR runtime distinctions.

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
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-19T11:28:53Z
  TYPE: FACT
  CLAIM: The new viewer/ACL cluster looks like interface truth first, not
    local hacks first. `frame_viewer.py` shows one override mismatch
    (`list_frame_names`, `get_view_frame`) and several `no-any-return` sites,
    while `frame_acl_container.py` is a large `no-any-return` block that
    usually means the interface/property chain is still leaking `Any`.
  EVIDENCE:
  - user_error_report: `frame_viewer.py:150`, `frame_viewer.py:1350`,
    `frame_viewer.py:3966-4035`
  - user_error_report: `frame_acl_container.py:300-711`
  - codex/context_compass/tickets/tasks/2026-05-18_fix_frame_acl_container_interface_alignment_task.md:1-170
  IMPACT: We should inspect the concrete return/property surfaces and patch the
    public contracts if they are stale before touching the big local files.
  NEXT: read the implicated chunks of `frame_viewer.py`,
    `frame_acl_container.py`, and the related interfaces in bounded chunks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T11:28:53Z
  TYPE: FACT
  CLAIM: The core contract fixes are now explicit. `IRift` needed the real
    `_get_required_view_projection(...)` surface, `ViewProjection` needed real
    descriptor/config/compiled-surface property types instead of `Any`, and the
    ACL family chain needed a truthful union return contract so the container
    could narrow family-specific results without casts.
  EVIDENCE:
  - src/melder/utilities/interfaces/irift.py:1-220
  - src/melder/utilities/interfaces/iframeviewer.py:1-91
  - src/melder/aether/nexus/rift/projection/view_projection.py:1-95
  - src/melder/aether/nexus/acl/frame_acl_configuration_chain.py:1-377
  - src/melder/aether/nexus/acl/frame_acl_container.py:284-813
  IMPACT: The `Any` leaks are now fixed at the source instead of being patched
    around in the two large concrete files.
  NEXT: record the bounded validation result and move the lane to review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T11:28:53Z
  TYPE: FACT
  CLAIM: One surfaced test failure proved the real public contract for the
    viewer host: `list_frame_names()` is list-shaped in runtime and tests, so
    the interface was stale. The correct fix was to align `IFrameViewer` to
    the real list return instead of forcing a tuple retrofit through the viewer
    layer.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:150-160
  - src/melder/utilities/interfaces/iframeviewer.py:1-24
  - tests/unit/melder/aether/test_frame_viewer_projection.py:399-399
  - tests/unit/melder/aether/test_nexus.py:5607-5607
  - tests/unit/melder/aether/test_nexus.py:6162-6162
  IMPACT: The viewer interface now matches the live runtime and the existing
    tests instead of encoding the wrong shape.
  NEXT: report the bounded fix and wait for the next exact bucket.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T11:28:53Z
  TYPE: MEASURE
  CLAIM: The bounded viewer/ACL cluster is green. The targeted mypy slice shows
    no file-local output for `frame_viewer.py` or `frame_acl_container.py`, and
    the selected unit/component/integration bundle passes after the interface
    and local return-surface fixes.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:1-4060
  - src/melder/aether/nexus/acl/frame_acl_container.py:1-952
  - src/melder/utilities/interfaces/iframeviewer.py:1-91
  - src/melder/utilities/interfaces/irift.py:1-220
  - src/melder/aether/nexus/rift/projection/view_projection.py:1-95
  - src/melder/aether/nexus/acl/frame_acl_configuration_chain.py:1-377
  - validation_result: `.\.venv_new\Scripts\python.exe -m mypy --show-error-codes --show-column-numbers --no-error-summary src\melder\aether\nexus\rift\frame_viewer\frame_viewer.py src\melder\aether\nexus\acl\frame_acl_container.py 2>&1 | Select-String 'src\\melder\\aether\\nexus\\rift\\frame_viewer\\frame_viewer.py:|src\\melder\\aether\\nexus\\acl\\frame_acl_container.py:'` -> no output
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\test_frame_viewer_projection.py tests\unit\melder\aether\test_nexus.py tests\component\melder\aether\test_frame_acl_component.py tests\integration\melder\aether\test_frame_acl_compiler_integration.py` -> `233 passed, 1 warning`
  IMPACT: The user-supplied viewer/ACL cluster is fixed without casts or
    shims.
  NEXT: report the bounded fix and wait for the next exact mypy/runtime lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Active AR viewer + ACL return-contract lane. Current evidence says the first
pass should be interface truth and bounded return-surface narrowing.
