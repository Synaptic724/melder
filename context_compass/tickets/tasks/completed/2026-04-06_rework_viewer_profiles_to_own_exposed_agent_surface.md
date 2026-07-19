# Task: Rework Viewer Profiles To Own Exposed Agent Surface
- Completed: 2026-04-06T12:17:44Z
- Summary: Accepted review slice moved out of the active lane during the 2026-04-06 board cleanup after the user advanced to later ACL/frame-surface work.


## Metadata
- Task ID: TASK-2026-04-06-rework-viewer-profiles-to-own-exposed-agent-surface
- Story: STORY-2026-04-03-frameinfolink-hld
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-06T06:00:00Z
- Updated: 2026-04-06T12:17:44Z

## Objective
Rework the viewer profile model so the selected viewer profile owns the
pregenerated command/capability surface exposed to the agent, instead of
treating the agent as the selector of viewer behavior at runtime.

## Ticket Contract
- ENTRY_GATE: the user explicitly clarified that the viewer surface should be
  pregenerated and exposed in the workspace, with profile selection happening
  when the Rift is built rather than by the agent at use time.
- EXECUTION_BOUNDARY: viewer-profile semantics and the smallest runtime wiring
  needed to honor that model.
- DEPENDENCIES:
  - tickets/tasks/2026-04-06_build_frame_view_and_viewer_profile_foundations.md
  - src/melder/aether/nexus/rift/frame_viewer/
  - src/melder/aether/nexus/nexus.py
- EXIT_GATE: the selected viewer profile owns the exposed helper/capability
  surface and focused tests pass.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the clean implementation
  requires the full viewer command catalog in one pass.

## Scope Boundaries
- In scope:
  - `FrameViewerProfile` semantic ownership rework
  - runtime wiring so selected profile drives exposed helper surface
  - focused tests
- Out of scope:
  - full command DSL
  - broad workspace UI changes
  - larger Rift construction redesign

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: the task was turned in during the cleanup pass after the user advanced to later ACL/frame-surface work.
## Steps / Checklist
- [x] Define the smallest semantic rework so profile owns the exposed helper set.
- [x] Implement the runtime/profile wiring changes.
- [x] Add/update focused tests.
- [x] Run focused validation.
- [x] Document findings, implementation, and validation in `## Notes`.

## Deliverables
- reworked viewer profile semantics
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/rift/frame_viewer/
- src/melder/aether/nexus/nexus.py
- tests/unit/melder/aether/
- codex/context_compass/attention_board.md

## Validation
- Completed:
  - `python -m pytest -q tests/unit/melder/aether/test_frame_view_and_viewer_profiles.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py`

## Risks / Rollback Notes
- Risk: we half-shift ownership and leave profile/runtime semantics split.
  Rollback: keep the first cut small and explicit, with the profile clearly
  owning the enabled helper surface.

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
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-06T06:00:00Z
  TYPE: PLAN
  CLAIM: The next bounded frame-surface slice is viewer-profile ownership
    semantics. The user explicitly clarified that the agent does not get to
    select the view surface dynamically. The selected viewer profile is chosen
    as part of Rift construction, the workspace gets a pregenerated exposed
    surface, and the agent only uses what that surface exposes. The first cut
    should therefore make the selected profile the owner of the exposed helper
    set rather than treating the profile as passive metadata.
  EVIDENCE:
  - user_instruction: "put everything in the profile"
  - user_instruction: "it gets selected with everything else whe nthe rift is built"
  - user_instruction: "the agent doesn't get to to select this stuff, its pregenerated and exposed in the workspace"
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py:1-130
  IMPACT: The profile/runtime relationship should be reworked before we add
    more viewer capabilities.
  NEXT: inspect the current viewer profile/runtime wiring and implement the
    smallest cut where the selected profile owns the exposed helper surface.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T06:10:00Z
  TYPE: FACT
  CLAIM: The current runtime already carries the selected viewer profile name,
    version, defaults, and enabled helper ids in the projected viewer metadata,
    but `FrameViewer` itself still exposes every helper method
    unconditionally. That means profile selection is currently descriptive, not
    authoritative. The smallest useful semantic rework is to make helper access
    validate against the selected profile's `enabled_helpers`.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py:1-130
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:1-426
  - src/melder/aether/nexus/nexus.py:1454-1518
  IMPACT: We can make the selected profile actually own the exposed surface
    without building the full command catalog yet.
  NEXT: add viewer-side helper gating against the selected profile and update
    the focused tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T06:12:00Z
  TYPE: FACT
  CLAIM: The selected viewer profile now actually owns the exposed helper
    surface. `FrameViewer` now stores the selected profile's enabled helper
    ids and fails fast when a helper is not enabled by that profile. Nexus
    projection now passes the selected viewer profile's helper set and default
    grouping/detail posture into the concrete `FrameViewer` instance instead of
    leaving the profile as passive metadata only.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:1-507
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py:1-131
  - src/melder/aether/nexus/nexus.py:1461-1519
  - tests/unit/melder/aether/test_frame_viewer_projection.py:1-487
  - tests/unit/melder/aether/test_nexus_frame_surface_projection.py:1-285
  IMPACT: The workspace-exposed viewer surface is now profile-owned in a real
    runtime sense instead of just carrying descriptive profile metadata.
  NEXT: decide whether to build the first explicit viewer capability/command
    catalog next.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T06:12:00Z
  TYPE: MEASURE
  CLAIM: The focused viewer-profile ownership slice is green. The profile
    foundations, viewer helper gating, and Nexus projection tests passed with
    48 tests.
  EVIDENCE:
  - command:python -m pytest -q tests/unit/melder/aether/test_frame_view_and_viewer_profiles.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py
  IMPACT: The semantic rework is stable enough to review as a bounded slice.
  NEXT: decide whether to add the first viewer capability/command catalog.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to align the viewer profile system with the intended
pregenerated workspace-exposed agent surface model.



