# Task: Add Workstation Reference Modes To Rift Space
- Completed: 2026-04-13T11:34:18Z
- Summary: Closed the workstation strong/weak reference-mode slice after the later room/runtime work confirmed it as part of the settled workstation model.

## Metadata
- Task ID: TASK-2026-04-11-add-workstation-reference-modes-to-rift-space
- Story: STORY-2026-04-11-add-workstation-to-rift-space
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-11T18:19:07Z
- Updated: 2026-04-13T11:34:18Z

## Objective
Extend the room-local workstation so bindings can be stored explicitly as
strong or weak references, and make `weak_ref=None` resolve through the
owning room mode.

## Ticket Contract
- ENTRY_GATE: the workstation and command-system slices are already landed, the
  user explicitly approved a new workstation binding-reference slice, and the
  weak data-structure package has been re-opened as direct source evidence.
- EXECUTION_BOUNDARY: workstation binding storage, `RiftSpace` room-mode
  default resolution, interface updates, focused tests, and ticket/board/
  artifact sync only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-11_add_workstation_to_rift_space_task.md
  - tickets/tasks/2026-04-11_add_command_system_to_rift_space_task.md
  - src/melder/utilities/data_structures/weak_data_structures/weak_ref_node.py
  - src/melder/utilities/data_structures/weak_data_structures/weak_concurrent_dict.py
  - src/melder/aether/nexus/rift/rift_space/workstation.py
  - src/melder/aether/nexus/rift/rift_space/rift_space.py
  - src/melder/aether/nexus/configuration/rift_space_type.py
  - src/melder/utilities/interfaces/interfaces.py
  - tests/unit/melder/aether/test_nexus.py
- EXIT_GATE: workstation binding APIs accept explicit strong/weak choice,
  `weak_ref=None` resolves through room mode, and the focused test slice is
  green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the change requires an event
  queue or deeper command ACL work in the same tranche.

## Scope Boundaries
- In scope:
  - strong and weak workstation binding storage
  - `weak_ref: Optional[bool]` on workstation bind APIs
  - room-mode default resolution for `weak_ref=None`
  - static -> weak default
  - capability/dynamic/base -> strong default
  - focused unit tests
- Out of scope:
  - event queue ownership/consumption
  - command ACL enforcement
  - richer stale-binding recovery behavior

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly approved implementing room-mode-aware
  workstation strong/weak binding behavior now.

## Steps / Checklist
- [ ] Record the workstation/weak-structure findings.
- [ ] Create patch docs for the reference-mode slice.
- [ ] Add strong/weak binding support to workstation storage.
- [ ] Wire room-mode default resolution through `RiftSpace`.
- [ ] Update interfaces and focused tests.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- workstation strong/weak binding support
- room-mode-aware `weak_ref=None` resolution
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/rift/rift_space/workstation.py
- src/melder/aether/nexus/rift/rift_space/rift_space.py
- src/melder/utilities/interfaces/interfaces.py
- tests/unit/melder/aether/test_nexus.py
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py`

## Risks / Rollback Notes
- Risk: weak binding silently degrades to strong for unsupported objects.
  Rollback: treat explicit weak binding as a hard contract and raise on
  unsupported weak targets instead of downgrading.

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
  - system_docs/patches/active/rift_space_workstation_reference_modes/architecture_patch.md
  - system_docs/patches/active/rift_space_workstation_reference_modes/component_patch_workstation.md
  - system_docs/patches/active/rift_space_workstation_reference_modes/component_patch_rift_space.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until the reference-mode model is merged into canonical
  docs or intentionally retired.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-11T18:25:05Z
  TYPE: FACT
  CLAIM: The workstation reference-mode slice is now landed in source.
    Workstation storage is split into strong and weak backing stores per
    logical binding category, all three bind APIs now accept
    `weak_ref: Optional[bool]`, and `weak_ref=None` resolves through the
    room-kind default captured by `RiftSpace` at workstation creation time.
    Static rooms now default binds to weak when `weak_ref` is omitted, while
    capability, dynamic, and current base rooms default omitted binds to
    strong. Explicit weak binding still fails fast when the value cannot be
    weak-referenced.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/workstation.py:1-489
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:1-106
  - src/melder/utilities/interfaces/interfaces.py:6154-6210
  IMPACT: The room-local canvas now has explicit ownership semantics for saved
    bindings without dragging ACL or event-queue work into the same tranche.
  NEXT: run the focused Rift/Nexus unit slice and confirm the new reference
    modes stay green.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T18:25:05Z
  TYPE: MEASURE
  CLAIM: The focused Rift/Nexus unit slice is green after the reference-mode
    retrofit. The new tests covering explicit strong bind, explicit weak bind,
    `weak_ref=None` room-mode defaulting, and explicit weak-bind failure all
    pass together with the earlier workstation and command-system tests.
  EVIDENCE:
  - tests/unit/melder/aether/test_nexus.py:759-907
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus.py` -> 71 passed
  IMPACT: The workstation reference-mode model is ready for review before we
    widen into event-queue or ACL work.
  NEXT: review the new binding-reference model and decide whether the next
    slice should return to ACL enforcement or continue the workstation/runtime
    lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T18:19:07Z
  TYPE: FACT
  CLAIM: The current workstation is strong-reference-only, while the weak data
    structure package already provides the right weak-object substrate for
    named bindings. `WeakConcurrentDict` gives strong-key/weak-value storage
    with `WeakRefNode` collection callbacks and optional auto-prune, while the
    current workstation only owns three strong dict stores with no reference
    mode metadata or room-policy defaulting.
  EVIDENCE:
  - src/melder/utilities/data_structures/weak_data_structures/weak_ref_node.py:1-366
  - src/melder/utilities/data_structures/weak_data_structures/weak_concurrent_dict.py:1-1152
  - src/melder/aether/nexus/rift/rift_space/workstation.py:1-428
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:1-484
  IMPACT: The missing slice is not a new weak-reference subsystem. It is
    workstation storage and room-mode resolution logic.
  NEXT: add a dedicated reference-mode task and patch docs, then retrofit the
    workstation stores and bind APIs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T18:19:07Z
  TYPE: PLAN
  CLAIM: The clean first implementation keeps the public bind surface simple:
    `weak_ref=True` forces weak storage, `weak_ref=False` forces strong
    storage, and `weak_ref=None` resolves through room kind on the owning
    `RiftSpace`. Static rooms default `None` to weak, while capability,
    dynamic, and current base rooms default `None` to strong. Explicit weak
    binding must raise when the object cannot be weak-referenced rather than
    silently downgrading to strong.
  EVIDENCE:
  - user_instruction: "we keep weakref=None, and if its none do nothing but if we're in static mode do weakref if we're in capability and other we just do the normal strong ref on none"
  - src/melder/aether/nexus/configuration/rift_space_type.py:1-26
  - src/melder/aether/nexus/rift/rift_space/workstation.py:1-428
  IMPACT: We can keep the public API small while still making room mode matter
    for default binding behavior.
  NEXT: patch workstation storage plus `RiftSpace` room-mode defaulting and
    then update the focused tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T11:34:18Z
  TYPE: DECISION
  CLAIM: The workstation reference-mode slice is complete and can move to the
    completed lane. The later queue and lock-hardening work assumes the strong/
    weak binding model is already settled, and the user explicitly asked to
    clean up older finished tickets.
  EVIDENCE:
  - tickets/tasks/2026-04-11_add_rift_space_event_queue_and_weak_binding_events_task.md:1-162
  - tickets/tasks/2026-04-11_harden_rift_space_and_workstation_locking_task.md:1-157
  - codex/context_compass/system_docs/src_components.md:699-756
  IMPACT: This reference-mode task no longer needs to remain in active review
    state.
  NEXT: none.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task extends workstation binding semantics only. The runtime is now green
on the focused `test_nexus.py` slice and is ready for review before we widen
back into ACL or event-queue work.
