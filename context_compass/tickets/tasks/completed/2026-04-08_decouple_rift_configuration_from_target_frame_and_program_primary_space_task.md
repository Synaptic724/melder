# Task: Decouple Rift Configuration From Target Frame And Program Primary Space
- Completed: 2026-04-09T11:31:39Z
- Summary: Split bare Rift creation from frame targeting and primary-space programming.


## Metadata
- Task ID: TASK-2026-04-08-decouple-rift-configuration-from-target-frame-and-program-primary-space
- Story: STORY-2026-04-08-split-rift-creation-from-frame-targeting-and-program-primary-space
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-08T11:35:38Z
- Updated: 2026-04-09T11:31:39Z

## Objective
Remove target-frame selection from `RiftConfiguration`, make `Nexus.create_rift(...)`
build a bare Rift, instantiate the primary space from `space_type`, and make
frame targeting the separate Rift action that validates legality and refreshes
the space-attached viewer.

## Ticket Contract
- ENTRY_GATE: the user explicitly approved the Rift lifecycle split and the
  current code evidence shows that target-frame selection is still coupled to
  Rift creation.
- EXECUTION_BOUNDARY: first implementation cut for Rift config cleanup,
  primary-space programming, and explicit frame targeting only.
- DEPENDENCIES:
  - tickets/epics/2026-04-08_rift_creation_frame_targeting_and_primary_space_split_epic.md
  - tickets/stories/2026-04-08_split_rift_creation_from_frame_targeting_and_program_primary_space_story.md
  - src/melder/aether/nexus/nexus.py
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/configuration/rift_configuration.py
  - src/melder/aether/nexus/rift/rift_space/
  - tests/unit/melder/aether/test_nexus.py
  - system_docs/patches/active/rift_creation_targeting_primary_space_split/architecture_patch.md
  - system_docs/patches/active/rift_creation_targeting_primary_space_split/component_patch_nexus.md
  - system_docs/patches/active/rift_creation_targeting_primary_space_split/component_patch_rift.md
  - system_docs/patches/active/rift_creation_targeting_primary_space_split/component_patch_rift_configuration.md
  - system_docs/patches/active/rift_creation_targeting_primary_space_split/component_patch_rift_space.md
  - system_docs/patches/active/rift_creation_targeting_primary_space_split/code_description_patch_rift_programming_flow.md
- EXIT_GATE: the focused Rift/Nexus tests reflect the split and the new
  primary-space/viewer programming flow passes.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if one-primary-space semantics
  force a larger redesign than this first cut can safely carry.

## Scope Boundaries
- In scope:
  - `RiftConfiguration` target-frame removal
  - bare Rift creation
  - primary-space construction from `space_type`
  - explicit target-frame method on `Rift`
  - viewer refresh after targeting
  - focused unit-test updates
- Out of scope:
  - broad multi-space deletion unless required
  - new workspace-history/event features
  - ACL rule-shape changes

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user approved immediate implementation of the Rift
  lifecycle split.

## Steps / Checklist
- [x] Create patch docs for the lifecycle split.
- [x] Remove `target_frame_name` from `RiftConfiguration` and interface contracts.
- [x] Make `Nexus.create_rift(...)` produce a bare Rift.
- [x] Instantiate the primary concrete space from `space_type`.
- [x] Rework target-frame attachment into an explicit Rift action that refreshes the viewer.
- [x] Update focused Rift/Nexus/viewer tests.
- [x] Record findings, implementation, and validation in `## Notes`.

## Deliverables
- bare Rift creation path
- primary space programming path
- explicit target-frame attachment path
- updated tests

## Files / Paths Impacted
- src/melder/aether/nexus/
- src/melder/aether/nexus/rift/
- src/melder/utilities/interfaces/interfaces.py
- tests/unit/melder/aether/
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md

## Validation
- `python -m pytest -q tests/unit/melder/aether/test_nexus.py`

## Risks / Rollback Notes
- Risk: test and interface churn around current target-frame assumptions.
  Rollback: keep the first cut constrained to the Rift/Nexus lifecycle and
  preserve viewer semantics through the existing descriptor + ACL projection path.

## Applicable Anti-Patterns
- [ ] No implementation/validation before required patch docs exist and are linked.
- [ ] No implementation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No widening into unrelated workspace redesign.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/rift_creation_targeting_primary_space_split/architecture_patch.md
  - system_docs/patches/active/rift_creation_targeting_primary_space_split/component_patch_nexus.md
  - system_docs/patches/active/rift_creation_targeting_primary_space_split/component_patch_rift.md
  - system_docs/patches/active/rift_creation_targeting_primary_space_split/component_patch_rift_configuration.md
  - system_docs/patches/active/rift_creation_targeting_primary_space_split/component_patch_rift_space.md
  - system_docs/patches/active/rift_creation_targeting_primary_space_split/code_description_patch_rift_programming_flow.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: merge into canonical docs or explicitly retire after the Rift lifecycle split settles.

## Notes
- DATETIME: 2026-04-08T11:35:38Z
  TYPE: FACT
  CLAIM: The current implementation is still collapsed. `RiftConfiguration`
    owns `target_frame_name`, `Nexus.create_rift(...)` validates the target
    frame during Rift creation, and the created `Rift` is born with
    `target_frame_names` already populated. Primary-space creation and
    `auto_create_space` are not part of that flow yet.
  EVIDENCE:
  - src/melder/aether/nexus/configuration/rift_configuration.py:58-62
  - src/melder/aether/nexus/configuration/rift_configuration.py:214-218
  - src/melder/aether/nexus/nexus.py:611-699
  - src/melder/aether/nexus/rift/rift.py:148-168
  IMPACT: We need a real lifecycle split instead of another helper around the
    current collapsed model.
  NEXT: write the patch docs and then implement the first cut against the
    Rift/Nexus lifecycle.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-08T11:35:38Z
  TYPE: PLAN
  CLAIM: Patch-to-implementation mapping for the first cut is:
    - `component_patch_rift_configuration.md` -> remove `target_frame_name`
      from `RiftConfiguration` and `IRiftConfiguration`
    - `component_patch_nexus.md` -> make `Nexus.create_rift(...)` build a bare
      Rift and stop validating target-frame selection there
    - `component_patch_rift.md` + `component_patch_rift_space.md` -> let
      `Rift` create one primary concrete space from `space_type`, keep viewer
      attachment on the space, and move frame legality checks into the explicit
      targeting path
    - `code_description_patch_rift_programming_flow.md` -> targeting refreshes
      the attached viewer from descriptor + current ACL
  EVIDENCE:
  - codex/context_compass/system_docs/patches/active/rift_creation_targeting_primary_space_split/architecture_patch.md:1-15
  - codex/context_compass/system_docs/patches/active/rift_creation_targeting_primary_space_split/component_patch_nexus.md:1-9
  - codex/context_compass/system_docs/patches/active/rift_creation_targeting_primary_space_split/component_patch_rift.md:1-10
  - codex/context_compass/system_docs/patches/active/rift_creation_targeting_primary_space_split/component_patch_rift_configuration.md:1-8
  - codex/context_compass/system_docs/patches/active/rift_creation_targeting_primary_space_split/component_patch_rift_space.md:1-8
  - codex/context_compass/system_docs/patches/active/rift_creation_targeting_primary_space_split/code_description_patch_rift_programming_flow.md:1-8
  IMPACT: The upcoming code changes now have an explicit contract-to-edit map
    instead of drifting from the patch docs.
  NEXT: edit the configuration, Nexus, Rift, and focused tests to match the
    first-cut lifecycle split.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-08T11:46:11Z
  TYPE: MEASURE
  CLAIM: The first Rift lifecycle split cut is landed and green. `RiftConfiguration`
    no longer carries target-frame selection, `Nexus.create_rift(...)` now
    creates a bare Rift, `Rift` now programs one primary concrete space from
    `space_type`, and explicit `target_frame(...)` now performs the target
    legality check and refreshes the active-space viewer only when descriptor
    truth is available. The old config-level target-frame validator was removed.
  EVIDENCE:
  - src/melder/utilities/interfaces/interfaces.py:5897-5928
  - src/melder/utilities/interfaces/interfaces.py:6143-6240
  - src/melder/aether/nexus/configuration/rift_configuration.py:57-61
  - src/melder/aether/nexus/configuration/rift_configuration.py:197-215
  - src/melder/aether/nexus/nexus.py:524-570
  - src/melder/aether/nexus/nexus.py:611-699
  - src/melder/aether/nexus/rift/rift.py:82-181
  - src/melder/aether/nexus/rift/rift.py:405-483
  - src/melder/aether/nexus/rift/rift.py:796-891
  - tests/unit/melder/aether/test_nexus.py:366-384
  - tests/unit/melder/aether/test_nexus.py:521-556
  - tests/unit/melder/aether/test_nexus.py:687-1077
  - tests/unit/melder/aether/test_nexus.py:1262-1341
  - validation_result: "python -m pytest -q tests/unit/melder/aether/test_nexus.py" -> 46 passed
  - validation_result: "python -m pytest -q tests/unit/melder/aether/test_frame_viewer_projection.py" -> 64 passed
  IMPACT: Rift lifecycle is now staged correctly enough for the next step:
    decide whether to harden one-primary-space semantics further or keep the
    current multi-space registry while using the primary-space path by default.
  NEXT: review this first lifecycle split cut and decide whether the next step
    should enforce one-primary-space more strictly or move into richer
    space/viewer programming behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-08T11:46:11Z
  TYPE: DECISION
  CLAIM: Targeting is now stricter. A frame cannot be engaged by a Rift unless
    descriptor truth already exists for that frame. This makes
    `FrameLinkContract` contain only viewer-projectable frames and removes the
    earlier softer "legal but not yet projectable" state.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:405-456
  - tests/unit/melder/aether/test_nexus.py:1080-1102
  - validation_result: "python -m pytest -q tests/unit/melder/aether/test_nexus.py" -> 47 passed
  IMPACT: Targeting now means "fully usable by the Rift viewer path", not just
    "runtime-legal in principle".
  NEXT: review the stricter target contract and decide whether the next step
    should enforce one-primary-space semantics or deepen the explicit space
    programming path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-08T11:46:11Z
  TYPE: DECISION
  CLAIM: The target-frame contract is being tightened immediately. A frame
    should not be targetable by a Rift unless descriptor truth already exists
    for that frame. This removes the softer "legal but not yet projectable"
    state and makes `FrameLinkContract` contain only viewer-projectable frames.
  EVIDENCE:
  - user_instruction: "we could just ensure that you cannot register a frame unless the descriptor exists"
  - src/melder/aether/nexus/rift/rift.py:405-456
  - src/melder/aether/nexus/nexus.py:1505-1546
  IMPACT: `Rift.target_frame(...)` should fail before contract mutation when
    the descriptor is absent, and the viewer refresh path can become stricter.
  NEXT: update `Rift.target_frame(...)` and the focused Nexus tests to require
    descriptor presence before frame registration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task implements the first cut of the Rift lifecycle split. The target
result is a bare Rift plus a primary space selected by `space_type`, with frame
targeting moved onto the Rift as the separate validated action that refreshes
the attached viewer.

