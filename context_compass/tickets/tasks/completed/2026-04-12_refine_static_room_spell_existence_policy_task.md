# Task: Refine Static Room Spell Existence Policy
- Completed: 2026-04-13T11:20:06Z
- Summary: Closed the final static existence-policy cleanup after the later static-room slices confirmed the settled spell-facing policy.

## Metadata
- Task ID: TASK-2026-04-12-refine-static-room-spell-existence-policy
- Story: STORY-2026-04-11-precision-acl-target-model-and-descriptor-validation
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-12T17:25:00Z
- Updated: 2026-04-13T11:20:06Z

## Objective
Finish the last static-room semantics pass by making static viewer and static
command agree on unsupported spell existences.

## Ticket Contract
- ENTRY_GATE: the user explicitly approved one final static pass and called out
  that `.many` should not be usable in static, while
  `unique_per_spell_space` is not a stable visible static surface.
- EXECUTION_BOUNDARY: `StaticFrameViewer`, `StaticCommandSystem`, focused
  static tests, patch docs, and board/artifact sync only.
- DEPENDENCIES:
  - src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py
  - src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py
  - tests/unit/melder/aether/test_nexus.py
- EXIT_GATE: static viewer and static command both exclude
  `Existence.many` and `Existence.unique_per_spell_space`, and the focused
  static/runtime ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the existence-policy cleanup
  requires a broader static room redesign.

## Scope Boundaries
- In scope:
  - static viewer spell existence filtering
  - static command spell existence filtering
  - focused tests
- Out of scope:
  - capability mode
  - descriptor publication changes
  - broader static status/helper expansion

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested one more static pass to
  finish the last semantics gap before moving to capability.

## Steps / Checklist
- [x] Stage patch docs and route the task from the board.
- [x] Exclude unsupported spell existences from `StaticFrameViewer`.
- [x] Exclude unsupported spell existences from `StaticCommandSystem`.
- [x] Update focused static tests.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- static existence-policy alignment on viewer and command
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py
- src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py
- tests/unit/melder/aether/test_nexus.py
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md

## Validation
- Ran:
  - `python -m py_compile src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py tests/unit/melder/aether/test_nexus.py`
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_rift_runtime_contracts.py`

## Risks / Rollback Notes
- Risk: static viewer and static command drift again on existence semantics.
  Rollback: keep the policy explicit and duplicated in the two static-only
  surfaces rather than relying on implicit runtime behavior.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

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
  - system_docs/patches/active/static_room_spell_existence_policy/architecture_patch.md
  - system_docs/patches/active/static_room_spell_existence_policy/component_patch_static_frame_viewer.md
  - system_docs/patches/active/static_room_spell_existence_policy/component_patch_static_command_system.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until the static existence policy is merged into
  canonical runtime docs or intentionally retired.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-12T17:25:00Z
  TYPE: FACT
  CLAIM: Static still had one final semantics gap. `StaticCommandSystem`
    already rejects `Existence.many` through `meld_existing_spell(...)`, and
    the user explicitly confirmed `.many` should not be usable in static.
    The user also called out that `unique_per_spell_space` is not a stable
    visible static surface because spellspaces are local. `StaticFrameViewer`
    was still only filtering by liveness, so viewer and command could drift on
    these existence modes.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:397-537
  - src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py:214-337
  - src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py:41-155
  - user_direction: "you cannot use .many"
  - user_direction: "I don't think we can properly see unique_per_spell_space because spellspaces are local"
  IMPACT: The final static cleanup is existence-policy alignment, not another
    viewer/command redesign.
  NEXT: exclude `many` and `unique_per_spell_space` in both static surfaces and
    update the focused tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T17:32:00Z
  TYPE: FACT
  CLAIM: The final static existence-policy pass is now landed in source.
    `StaticFrameViewer` now excludes both `Existence.many` and
    `Existence.unique_per_spell_space` even if a live probe would otherwise
    succeed, and `StaticCommandSystem` now rejects those same existences
    explicitly instead of relying only on downstream `meld_existing_spell(...)`
    behavior.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py:1-337
  - src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py:1-175
  - tests/unit/melder/aether/test_nexus.py:2133-2308
  IMPACT: Static viewer and static command now expose the same final spell
    existence policy instead of drifting on `many` or spellspace-local cases.
  NEXT: run the focused static/runtime ring and decide whether static is now
    fully done.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T17:32:00Z
  TYPE: MEASURE
  CLAIM: The final static refinement is green on the focused and nearby
    static/Rift runtime ring.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py tests/unit/melder/aether/test_nexus.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_rift_runtime_contracts.py` -> 108 passed
  IMPACT: Static is now consistent enough to stop and move to capability.
  NEXT: summarize the final static room contract and shift the next room lane
    to capability.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T11:20:06Z
  TYPE: DECISION
  CLAIM: The static existence-policy cleanup is complete and can move to the
    completed lane. The later static-room testbench and status-helper slices
    already build on this final policy, and the user explicitly asked for old
    finished tickets to be cleaned up.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py:1-337
  - src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py:1-301
  - codex/context_compass/system_docs/src_architecture.md:479-486
  IMPACT: This static semantics cleanup no longer needs to remain in active
    review state.
  NEXT: none.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task is the last static semantics cleanup before capability: align viewer
and command on unsupported spell existences.
