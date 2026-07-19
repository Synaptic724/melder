# Task: Implement RiftSpace Frame Surface Delegation
- Completed: 2026-04-09T11:31:39Z
- Summary: Exposed the hosted frame-surface chain directly through RiftSpace delegation.


## Metadata
- Task ID: TASK-2026-04-06-implement-rift-space-frame-surface-delegation
- Story: STORY-2026-04-06-contract-backed-assigned-frame-views
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-06T15:44:32Z
- Updated: 2026-04-09T11:31:39Z

## Objective
Make `RiftSpace` delegate the hosted frame-surface path directly so callers can
use the attached viewer through the space boundary instead of reaching into
`space.frame_viewer` and re-stitching the chain themselves.

## Ticket Contract
- ENTRY_GATE: the workspace-facing host seam is landed and the next bounded
  gap is making that host directly usable.
- EXECUTION_BOUNDARY: `RiftSpace` delegation plus the smallest interface/test
  updates needed to expose it cleanly.
- DEPENDENCIES:
  - codex/context_compass/tickets/tasks/2026-04-06_implement_workspace_facing_rift_frame_surface_host.md
  - src/melder/aether/nexus/rift/rift_space/rift_space.py
  - src/melder/utilities/interfaces/interfaces.py
  - tests/unit/melder/aether/test_nexus.py
- EXIT_GATE: `RiftSpace` exposes the hosted frame-surface chain directly and
  focused tests pass.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the clean delegation path
  requires a broader workspace API redesign in the same slice.

## Scope Boundaries
- In scope:
  - `RiftSpace` viewer delegation methods
  - `IRiftSpace` interface updates
  - focused unit tests
- Out of scope:
  - codegen runtime
  - broader workspace redesign
  - ACL changes

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the `RiftSpace` delegation slice is implemented, the
  focused tests passed, and the task is ready for review.

## Steps / Checklist
- [ ] Add `RiftSpace` delegation over the attached frame viewer.
- [ ] Update the exposed interface contract.
- [ ] Add/update focused tests.
- [ ] Document findings, implementation, and validation in `## Notes`.

## Deliverables
- direct `RiftSpace` frame-surface delegation
- interface updates
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/rift/rift_space/rift_space.py
- src/melder/utilities/interfaces/interfaces.py
- tests/unit/melder/aether/
- codex/context_compass/attention_board.md

## Validation
- Completed:
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py`

## Risks / Rollback Notes
- Risk: the slice drifts into a broad workspace API redesign.
  Rollback: keep the cut to basic delegation only.

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
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-06T15:44:32Z
  TYPE: PLAN
  CLAIM: The smallest useful next cut is direct `RiftSpace` delegation. The
    host seam is landed, but callers still have to reach through
    `space.frame_viewer` manually. The next bounded step is to expose the
    obvious viewer-facing calls directly on `RiftSpace` and keep the interface
    contract in lockstep.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:18-208
  - src/melder/utilities/interfaces/interfaces.py:5942-5989
  - codex/context_compass/tickets/tasks/2026-04-06_implement_workspace_facing_rift_frame_surface_host.md:1-123
  IMPACT: This makes the current host seam directly usable without widening
    into codegen or a larger workspace redesign.
  NEXT: add the smallest delegation methods on `RiftSpace` and mirror them in
    `IRiftSpace`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T15:44:32Z
  TYPE: FACT
  CLAIM: The delegation layer is now in code. `RiftSpace` now directly exposes:
    - `get_required_frame_viewer()`
    - `list_frame_names()`
    - `list_available_targets(...)`
    - `describe_available_targets(...)`
    and `IRiftSpace` now mirrors those host-facing methods. That means the
    current frame-surface chain is now reachable from the space boundary itself
    instead of only through `space.frame_viewer`.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:18-245
  - src/melder/utilities/interfaces/interfaces.py:5942-6020
  IMPACT: The host seam is now directly usable through the workspace boundary.
  NEXT: run the focused delegation slice and confirm the new host-facing calls
    hold.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T15:44:32Z
  TYPE: MEASURE
  CLAIM: The focused `RiftSpace` delegation slice is green. The targeted
    unit/integration surface covering `RiftSpace`, `Rift`, `FrameViewer`, and
    the Nexus projection path passed cleanly.
  EVIDENCE:
  - tests/unit/melder/aether/test_nexus.py:513-613
  - command:python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py
  IMPACT: The workspace-facing host seam is stable enough to review as the next
    bounded frame-surface slice.
  NEXT: review whether the next cut should start the codegen-facing workspace
    use path or deepen host-side state/selection behavior further.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

