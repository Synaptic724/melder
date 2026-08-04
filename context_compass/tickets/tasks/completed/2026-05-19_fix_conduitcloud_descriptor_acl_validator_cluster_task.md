# Task: fix conduitcloud descriptor acl validator cluster

Completed: 2026-05-19T17:29:27Z
Summary: Closed per user instruction after validation handoff. Latest lane state and validation notes remain below.


## Metadata
- Task ID: TASK-2026-05-19-fix-conduitcloud-descriptor-acl-validator-cluster
- Story: none
- Status: done
- Owner: codex
- Agent Name: mypy_2
- Priority: p1
- Created: 2026-05-19T14:09:43Z
- Updated: 2026-05-19T17:29:27Z

## Objective
Fix the current bounded mypy cluster spanning `conduit_cloud.py`,
`frame_descriptor_manager.py`, `iframeviewer.py`, and
`frame_acl_validator.py` by separating local annotation debt from stale public
contract drift.

## Ticket Contract
- ENTRY_GATE: the user supplied a bounded mypy error cluster for these four
  surfaces.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/conduit_cloud.py`
  - `src/melder/nexus/frame_descriptor_manager.py`
  - `src/melder/utilities/interfaces/iframeviewer.py`
  - `src/melder/nexus/acl/validator/frame_acl_validator.py`
  - directly implicated support contracts only if the real seam requires them
- DEPENDENCIES:
  - current ConduitCloud public surface
  - current Nexus frame-descriptor and ACL-validator contracts
  - no shims, no fake surfaces, no unrelated refactors
  - raise to Mark directly if the contract is ambiguous or a fix would require
    behavior change
- EXIT_GATE:
  - the targeted file-local mypy errors are gone
  - any interface changes remain truthful and bounded
  - focused validation confirms the lane
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if one of the reported errors
  requires a public-surface decision instead of a local fix

## Scope Boundaries
- In scope:
  - missing local annotation in `conduit_cloud.py`
  - descriptor manager return/assignment typing
  - `iframeviewer.py` missing `IRift` name resolution
  - frame ACL validator missing constant/attribute typing
- Out of scope:
  - broader Nexus architecture redesign
  - unrelated repo-wide mypy debt

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: the user selected this exact bounded mypy cluster as the
  next active lane.

## Steps / Checklist
- [ ] read the exact failing source slices and support interfaces
- [ ] classify each failure as local debt or public contract drift
- [ ] patch the bounded source/interface fixes only
- [ ] rerun focused mypy on the four-file cluster
- [ ] rerun bounded tests if any behavior-sensitive surfaces were touched
- [ ] continue only after documenting the result
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- a bounded conduit-cloud / descriptor-manager / viewer / ACL-validator typing fix

## Files / Paths Impacted
- `src/melder/aether/conduit_cloud.py`
- `src/melder/nexus/frame_descriptor_manager.py`
- `src/melder/utilities/interfaces/iframeviewer.py`
- `src/melder/nexus/acl/validator/frame_acl_validator.py`
- only if required by the truthful fix:
  - directly implicated support interfaces or descriptor payload contracts

## Validation
- Ran:
  - `.\.venv_new\Scripts\python.exe -m mypy --show-error-codes --show-column-numbers --no-error-summary src\melder\aether\conduit_cloud.py src\melder\nexus\frame_descriptor_manager.py src\melder\utilities\interfaces\iframeviewer.py src\melder\nexus\acl\validator\frame_acl_validator.py 2>&1 | Select-String 'src\\melder\\aether\\conduit_cloud.py:|src\\melder\\nexus\\frame_descriptor_manager.py:|src\\melder\\utilities\\interfaces\\iframeviewer.py:|src\\melder\\nexus\\acl\\validator\\frame_acl_validator.py:'`
  - `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\test_conduit_cloud.py tests\unit\melder\aether\test_frame_descriptor_manager.py tests\unit\melder\aether\test_frame_acl_validator.py`
- Results:
  - no output for the targeted four-file mypy slice
  - `53 passed, 1 warning`

## Risks / Rollback Notes
- Medium risk. The likely fixes are mostly local, but the descriptor-manager
  and viewer seams may expose one stale public contract.

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
- DATETIME: 2026-05-19T14:09:43Z
  TYPE: FACT
  CLAIM: The new bounded mypy lane spans one local ConduitCloud annotation,
    three descriptor/viewer typing residuals, and one ACL-validator attribute
    cluster. The first safe step is exact source-slice reading around the
    reported lines plus the directly implicated interfaces before patching.
  EVIDENCE:
  - user_error_report: `src/melder/aether/conduit_cloud.py:119`
  - user_error_report: `src/melder/nexus/frame_descriptor_manager.py:181,218,394,495`
  - user_error_report: `src/melder/utilities/interfaces/iframeviewer.py:35`
  - user_error_report: `src/melder/nexus/acl/validator/frame_acl_validator.py:1259-1295`
  IMPACT: This should stay bounded if the support contracts already tell the
    truth.
  NEXT: read the exact failing slices and classify local debt versus interface drift.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T14:09:43Z
  TYPE: FACT
  CLAIM: The cluster splits cleanly. `conduit_cloud.py` is just missing the
    standard context-manager `__exit__` parameter annotations. In
    `frame_descriptor_manager.py`, the two posture-return methods are typed too
    concretely and should use the already-canonical
    `IAethericFrameConfiguration` contract, `_compute_parent_conduit_id(...)`
    needs a local runtime-safe `str` narrowing, and spell publication should
    stay on `ISpellDescriptorPayload` because `ISpellGeneralProfile` already
    exposes that interface. In `iframeviewer.py`, mypy just needs the missing
    `IRift` name in scope. In `frame_acl_validator.py`, the safe-profile
    override tables exist as imported module constants but were referenced as
    missing class attributes.
  EVIDENCE:
  - src/melder/aether/conduit_cloud.py:119-124
  - src/melder/nexus/frame_descriptor_manager.py:160-218
  - src/melder/nexus/frame_descriptor_manager.py:391-401
  - src/melder/nexus/frame_descriptor_manager.py:492-500
  - src/melder/nexus/frame_descriptor/frame_descriptor.py:166-179
  - src/melder/utilities/interfaces/ispellgeneralprofile.py:1-40
  - src/melder/utilities/interfaces/ispelldescriptorpayload.py:1-18
  - src/melder/utilities/interfaces/iframeviewer.py:1-35
  - src/melder/nexus/acl/validator/frame_acl_validator.py:1254-1297
  - src/melder/nexus/acl/validator/profiles/view/safe_strategy.py:1-24
  - src/melder/nexus/acl/validator/profiles/codegen/safe_strategy.py:1-31
  IMPACT: This can stay a bounded typing/interface lane with no behavior
    change.
  NEXT: patch the four files directly, then run focused mypy and the most
    relevant descriptor/ACL tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T14:09:43Z
  TYPE: FACT
  CLAIM: One attempted interface fix created a real runtime cycle: importing
    `IRift` directly into `iframeviewer.py` causes `irift -> iriftspace ->
    iframeviewer -> irift` during package import. The viewer field `_rift` is a
    private backing field rather than a public API return surface, so the right
    fix is to avoid the direct protocol import and keep that field typed more
    weakly instead of forcing a circular runtime dependency.
  EVIDENCE:
  - src/melder/utilities/interfaces/iframeviewer.py:1-35
  - src/melder/utilities/interfaces/irift.py:1-20
  - src/melder/utilities/interfaces/iriftspace.py:1-10
  - validation_result: focused pytest collection failed with circular import through `iframeviewer.py`
  IMPACT: The lane stays bounded, but `iframeviewer.py` needs a cycle-safe
    typing adjustment before validation can proceed.
  NEXT: remove the direct `IRift` import from `iframeviewer.py`, weaken the
    private `_rift` field type, then rerun the same bounded mypy and test ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T14:09:43Z
  TYPE: MEASURE
  CLAIM: The bounded four-file cluster is green. `ConduitCloud.__exit__` now
    has the missing context-manager annotations, the descriptor manager uses
    the truthful frame-posture and spell-payload interfaces plus a local
    parent-conduit id narrowing, `IFrameViewer` no longer injects a circular
    `IRift` import into runtime package loading, and `FrameACLValidator` now
    references the safe-profile override tables through real imported module
    constants. The focused Nexus/ACL tests pass.
  EVIDENCE:
  - src/melder/aether/conduit_cloud.py:108-124
  - src/melder/nexus/frame_descriptor_manager.py:1-80
  - src/melder/nexus/frame_descriptor_manager.py:160-218
  - src/melder/nexus/frame_descriptor_manager.py:391-401
  - src/melder/nexus/frame_descriptor_manager.py:492-500
  - src/melder/utilities/interfaces/iframeviewer.py:1-35
  - src/melder/nexus/acl/validator/frame_acl_validator.py:1-90
  - src/melder/nexus/acl/validator/frame_acl_validator.py:1254-1297
  - src/melder/utilities/interfaces/iconduitcloud.py:1-176
  - validation_result: filtered four-file mypy command -> no output
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\test_conduit_cloud.py tests\unit\melder\aether\test_frame_descriptor_manager.py tests\unit\melder\aether\test_frame_acl_validator.py` -> `53 passed, 1 warning`
  IMPACT: The user-supplied four-file mypy lane is fixed without shims or
    behavior changes. A raw mypy run on those files still exits nonzero only
    because of imported debt elsewhere in the repo, not because of residual
    errors in this cluster.
  NEXT: report the bounded fix and wait for the next exact mypy/runtime lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Active bounded mypy lane for ConduitCloud, frame descriptor manager, viewer
interface, and frame ACL validator.
