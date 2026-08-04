# Task: Add Capability Rift Space Placeholder
- Completed: 2026-04-09T11:31:39Z
- Summary: Added `capability` as a placeholder Rift space type and wired primary-space creation to it.


## Metadata
- Task ID: TASK-2026-04-09-add-capability-rift-space-placeholder
- Story: STORY-2026-04-08-split-rift-creation-from-frame-targeting-and-program-primary-space
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-04-09T11:04:56Z
- Updated: 2026-04-09T11:31:39Z

## Objective
Add `capability` as a first-class `RiftSpaceType` plus a placeholder concrete
`CapabilityRiftSpace`, wire Rift primary-space creation to understand it, and
cover the placeholder with focused Nexus unit tests.

## Ticket Contract
- ENTRY_GATE: the user explicitly wants the placeholder next and the current
  Rift lifecycle split already programs the primary space from `space_type`.
- EXECUTION_BOUNDARY: placeholder only. Add the enum value, protocol, concrete
  room class, Rift creation wiring, and focused tests. Do not implement the
  actual capability execution layer yet.
- DEPENDENCIES:
  - tickets/epics/2026-04-08_rift_creation_frame_targeting_and_primary_space_split_epic.md
  - tickets/artifacts/2026-04-08_rift_access_modes_static_capability_dynamic_model.md
  - src/melder/aether/nexus/configuration/rift_space_type.py
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/rift/rift_space/
  - src/melder/utilities/interfaces/interfaces.py
  - tests/unit/melder/aether/test_nexus.py
  - system_docs/patches/active/capability_rift_space_placeholder/architecture_patch.md
  - system_docs/patches/active/capability_rift_space_placeholder/component_patch_rift_space_type.md
  - system_docs/patches/active/capability_rift_space_placeholder/component_patch_rift_space.md
  - system_docs/patches/active/capability_rift_space_placeholder/component_patch_rift.md
- EXIT_GATE: the placeholder `capability` space type is real in runtime and
  focused Nexus tests pass.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if placeholder-only support
  unexpectedly forces immediate capability-layer semantics.

## Scope Boundaries
- In scope:
  - `RiftSpaceType.capability`
  - `ICapabilityRiftSpace`
  - `CapabilityRiftSpace`
  - Rift primary-space creation support
  - focused tests
- Out of scope:
  - capability ACL semantics
  - capability execution handles
  - static/dynamic semantic rewrites

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested the capability-space placeholder next.

## Steps / Checklist
- [x] Create patch docs for the placeholder.
- [x] Add the new enum value and protocol.
- [x] Add the placeholder `CapabilityRiftSpace` class.
- [x] Wire Rift primary-space creation to instantiate it.
- [x] Extend focused Nexus unit tests.
- [x] Record findings, implementation, and validation in `## Notes`.

## Deliverables
- `RiftSpaceType.capability`
- `CapabilityRiftSpace`
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/configuration/rift_space_type.py
- src/melder/aether/nexus/rift/rift.py
- src/melder/aether/nexus/rift/rift_space/
- src/melder/utilities/interfaces/interfaces.py
- tests/unit/melder/aether/test_nexus.py

## Validation
- `python -m pytest -q tests/unit/melder/aether/test_nexus.py`

## Risks / Rollback Notes
- Risk: placeholder introduces implied semantics that are not implemented yet.
  Rollback: keep docs and class docstrings explicit that this is placeholder-only.

## Applicable Anti-Patterns
- [ ] No implementation/validation before required patch docs exist and are linked.
- [ ] No widening into actual capability-mode runtime semantics.
- [ ] No silent semantic claims beyond placeholder support.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/capability_rift_space_placeholder/architecture_patch.md
  - system_docs/patches/active/capability_rift_space_placeholder/component_patch_rift_space_type.md
  - system_docs/patches/active/capability_rift_space_placeholder/component_patch_rift_space.md
  - system_docs/patches/active/capability_rift_space_placeholder/component_patch_rift.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: merge into canonical docs or explicitly retire after capability space stops being placeholder-only.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-09T11:04:56Z
  TYPE: PLAN
  CLAIM: The next slice is intentionally small. We only want the third space
    type to exist in the runtime now; the actual capability semantics can come
    later.
  EVIDENCE:
  - user_instruction: "ok cool go ahead next steps add the capability space object"
  IMPACT: This keeps the access-mode architecture moving without pretending the
    capability execution layer is finished.
  NEXT: add the placeholder enum/protocol/class and wire Rift creation to it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-09T11:06:49Z
  TYPE: MEASURE
  CLAIM: The placeholder third space type is landed and green. `RiftSpaceType`
    now includes `capability`, `ICapabilityRiftSpace` now exists,
    `CapabilityRiftSpace` is a concrete room class, and Rift primary-space
    creation now instantiates it when `space_type == capability`. Focused Nexus
    unit coverage now proves that the third room type is a real selectable
    placeholder.
  EVIDENCE:
  - src/melder/aether/nexus/configuration/rift_space_type.py:15-26
  - src/melder/utilities/interfaces/interfaces.py:6198-6200
  - src/melder/aether/nexus/rift/capability_rift_space.py:1-51
  - src/melder/aether/nexus/rift/rift.py:9-12
  - src/melder/aether/nexus/rift/rift.py:846-852
  - tests/unit/melder/aether/test_nexus.py:22-25
  - tests/unit/melder/aether/test_nexus.py:567-600
  - validation_result: "python -m pytest -q tests/unit/melder/aether/test_nexus.py" -> 47 passed
  IMPACT: The access-mode architecture now has a real third room type in
    runtime, which unblocks later capability-mode semantics without forcing
    them into this cut.
  NEXT: review the placeholder and, if accepted, move next into the real
    capability execution/access semantics.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-09T11:11:14Z
  TYPE: FACT
  CLAIM: The earlier close-out note about the file path was wrong. The
    placeholder class already lives in the correct package beside
    `StaticRiftSpace` and `DynamicRiftSpace` under
    `src/melder/aether/nexus/rift/rift_space/`, and the runtime imports/tests
    are already using that location.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/capability_rift_space.py:1-51
  - src/melder/aether/nexus/rift/rift.py:1-12
  - tests/unit/melder/aether/test_nexus.py:18-24
  IMPACT: No runtime/file move is needed. Only the stale note needed repair so
    future re-entry is not confused by a false layout problem.
  NEXT: leave the runtime file layout as-is and continue from the current
    capability placeholder state.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task adds the placeholder third Rift space type only. It does not build
the capability execution layer yet.

