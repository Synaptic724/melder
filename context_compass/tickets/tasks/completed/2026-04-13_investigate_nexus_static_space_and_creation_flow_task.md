# Task: Investigate Nexus Static Space And Creation Flow
- Completed: 2026-04-26T11:39:24Z
- Summary: Closed after the Nexus, static-room, descriptor, ACL, and lower
  creation-flow boundaries were reconstructed with source-backed evidence.

## Metadata
- Task ID: TASK-2026-04-13-investigate-nexus-static-space-and-creation-flow
- Epic: EPIC-2026-04-13-investigate-april-11-12-aethericrift-history-and-next-steps
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-13T23:35:43Z
- Updated: 2026-04-26T11:39:24Z

## Objective
Investigate how `Nexus`, `Rift`, `RiftSpace`, and the static room actually
compose and create runtime state today, then capture the findings in one
durable ticket with source evidence.

## Ticket Contract
- ENTRY_GATE: the user explicitly asked for a Nexus/static-space investigation
  and said the answer should be documented in a ticket.
- EXECUTION_BOUNDARY: investigation and ticket documentation only.
- DEPENDENCIES:
  - codex/context_compass/system_docs/src_architecture.md
  - codex/context_compass/system_docs/src_components.md
  - src/melder/aether/nexus/nexus.py
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/rift/rift_space/rift_space.py
  - src/melder/aether/nexus/rift/rift_space/static_rift_space.py
  - src/melder/aether/nexus/configuration/rift_configuration.py
  - src/melder/aether/nexus/configuration/rift_space_type.py
- EXIT_GATE: the ticket captures the current Nexus/static-space creation model,
  the role of static space, and where creation is or is not allowed.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the docs and source disagree
  materially about how room creation or static behavior works.

## Scope Boundaries
- In scope:
  - Nexus-to-Rift creation flow
  - room selection and `RiftSpace` composition
  - static room behavior and creation boundaries
  - how existing runtime objects are surfaced versus created
- Out of scope:
  - implementing new dynamic/codegen behavior
  - ticket cleanup unrelated to this investigation
  - MutationResearch behavior

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a Nexus/static-space
  investigation and ticket documentation before continuing the runtime lane.

## Steps / Checklist
- [ ] Read current source docs for Nexus/Rift/room architecture.
- [ ] Read the relevant Nexus/Rift/room code paths in bounded chunks.
- [ ] Record how static space works today with evidence.
- [ ] Record where creation is routed and denied with evidence.
- [ ] Summarize the current model and open questions in `## Notes`.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- evidence-backed Nexus/static-space investigation notes
- one durable summary of current room and creation behavior

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-04-13_investigate_nexus_static_space_and_creation_flow_task.md
- codex/context_compass/attention_board.md

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py`

## Risks / Rollback Notes
- Risk: older docs describe superseded room semantics and blur the current
  source of truth.
  Rollback: keep every claim tied to current source lines and mark conflicts
  explicitly.

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
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-13T23:35:43Z
  TYPE: PLAN
  CLAIM: The next useful investigation is not another abstract room-mode
    discussion. It is a concrete reconstruction of how `Nexus`, `Rift`, and
    static space actually work today, especially where object creation is
    routed or denied. The user explicitly wants that grounded in source and
    captured in a ticket.
  EVIDENCE:
  - user_instruction: "do you know about the static space too and how things are created?"
  - user_instruction: "go investigate nexus and understand how it all works and document it in a ticket"
  IMPACT: We need one bounded source-backed pass over the current Nexus/Rift
    creation and static-space paths before continuing the runtime lane.
  NEXT: read the relevant docs and source files in bounded chunks, then append
    findings here before widening scope.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T23:35:43Z
  TYPE: FACT
  CLAIM: The current Nexus/Rift creation flow is room-first, target-frame
    second. `Nexus.create_rift_configuration(...)` produces a bare per-Rift
    config with room posture only. `Nexus.create_rift(...)` then creates a bare
    `Rift` without validating or selecting a target frame. Inside `Rift.__init__`,
    the Rift immediately programs one primary room from `space_type`, and
    `Rift.target_frame(...)` is the later explicit attachment step. Static space
    therefore does not create runtime objects itself. It composes a static
    command surface and static viewer posture over the same lower Melder truth.
    Static denies topology mutation and direct `meld(...)`, but its live-only
    spell getters resolve already-live objects through the owning conduit using
    `meld_existing_spell(...)`.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:543-590
  - src/melder/aether/nexus/nexus.py:630-718
  - src/melder/aether/nexus/rift/rift.py:153-160
  - src/melder/aether/nexus/rift/rift.py:212-214
  - src/melder/aether/nexus/rift/rift.py:606-703
  - src/melder/aether/nexus/rift/rift.py:1067-1118
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:31-64
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:150-157
  - src/melder/aether/nexus/rift/rift_space/static_rift_space.py:24-35
  - src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py:46-69
  - src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py:71-95
  - src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py:327-416
  IMPACT: The design boundary is cleaner than "static creates less." Static
    does not own creation at all. Creation remains a lower Conduit/Meld/
    CreationContext concern, while static is a restrictive room surface over
    already-live and already-published runtime truth.
  NEXT: inspect the lower `Conduit` / `Meld` creation paths and the static room's
    spell-status/getter seams together so the ticket can say exactly where
    creation still lives and how static reaches live objects without creating.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T23:35:43Z
  TYPE: FACT
  CLAIM: The descriptor and ACL layers are now more explicit than the old file
    assumptions suggested. `FrameDescriptorManager` owns publication into one
    `FrameDescriptor`, and that descriptor owns:
    - one `frame_overview`
    - conduit records by id
    - spell records by key
    The ACL side is separate but layered over that descriptor truth. One
    `FrameACLContainer` exists per frame, and it owns separate family chains
    for view, command, and codegen plus two different validator services:
    1) `FrameACLValidator`, which validates assembled ACL snapshots against
       descriptor truth and record contracts
    2) `FrameACLSetCompatibilityValidator`, which validates cross-child/family
       compatibility
    So the validation split is not "one validator for ACLs and one random
    overview validator." It is descriptor publication first, then a
    frame-overview/record-contract-aware ACL validator, plus a sibling
    compatibility validator for the container's multi-family model.
  EVIDENCE:
  - src/melder\aether\nexus\frame_descriptor\frame_descriptor.py:49-84
  - src/melder\aether\nexus\frame_descriptor\frame_descriptor.py:189-202
  - src/melder\aether\nexus\frame_descriptor\frame_descriptor.py:336-356
  - src/melder\aether\nexus\frame_descriptor_manager.py:237-304
  - src/melder\aether\nexus\acl\frame_acl_container.py:29-43
  - src/melder\aether\nexus\acl\frame_acl_container.py:95-114
  - src/melder\aether\nexus\acl\frame_acl_container.py:219-242
  - src/melder\aether\nexus\acl\validator\frame_acl_validator.py:476-485
  - src/melder\aether\nexus\rift\frame_viewer\profiles\frame_viewer_profile.py:818-828
  IMPACT: The live architecture is "publish descriptor truth -> validate ACL
    snapshots against it -> compile access surface -> let viewer/command/codegen
    consume that compiled truth." That is the real current stack to reason about,
    not the older flatter notes.
  NEXT: read the publication methods in `FrameDescriptorManager`, the compiler,
    and the frame-viewer/command consumers so the ticket can explain the full
    descriptor -> validation -> consumer flow.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T23:35:43Z
  TYPE: FACT
  CLAIM: The live consumer flow is:
    descriptor publication -> assembled ACL bundle -> validation ->
    compiled access surface -> viewer and command consumption.
    `FrameDescriptorManager` publishes `frame_overview`, conduit records, and
    spell records into `FrameDescriptor`. `FrameACLManager` assembles one
    selected ACL bundle per frame from separate view/command/codegen family
    chains. `FrameACLValidator` validates that bundle against descriptor truth,
    including frame-overview record contracts and spell payload floors.
    `FrameACLSetCompatibilityValidator` separately checks cross-family coherence.
    `FrameACLCompiler` then compiles one `CompiledFrameACLAccessSurface`.
    The viewer side binds to that compiled surface by reference through
    `FrameViewerProfile.bind_to_frame(...)`, while the command side enforces
    `command_frame_enabled`, `enabled_conduit_ids`, and
    `enabled_spell_index_ids` from the same compiled surface.
    Codegen is present in the selected-contract and compiled-ACL model
    (`codegen_contract_name`, codegen configuration/profile selection, and
    `allowed_commands` in the compiled surface), but I do not see a first-class
    AR runtime codegen consumer in these current `Nexus` / `Rift` /
    `RiftSpace` paths yet. It looks more like prepared policy state than a
    fully surfaced room/runtime execution path.
  EVIDENCE:
  - src/melder\aether\nexus\frame_descriptor_manager.py:226-305
  - src/melder\aether\nexus\frame_descriptor_manager.py:307-378
  - src/melder\aether\nexus\frame_descriptor_manager.py:457-525
  - src/melder\aether\nexus\frame_acl_manager.py:221-256
  - src/melder\aether\nexus\frame_acl_manager.py:320-352
  - src/melder\aether\nexus\frame_acl_manager.py:559-584
  - src/melder\aether\nexus\acl\validator\frame_acl_validator.py:459-520
  - src/melder\aether\nexus\acl\validator\compatibility\frame_acl_set_compatibility_validator.py:24-37
  - src/melder\aether\nexus\acl\validator\compatibility\frame_acl_set_compatibility_validator.py:133-197
  - src/melder\aether\nexus\acl\frame_acl_compiler.py:25-38
  - src/melder\aether\nexus\acl\frame_acl_compiler.py:77-221
  - src/melder\aether\nexus\rift\frame_viewer\profiles\frame_viewer_profile.py:573-699
  - src/melder\aether\nexus\rift\frame_viewer\profiles\frame_viewer_profile.py:799-840
  - src/melder\aether\nexus\rift\rift_space\command_system\command_system.py:1791-1876
  - src/melder\aether\nexus\rift\rift_space\command_system\command_system.py:1878-1905
  - src/melder\aether\nexus\rift\frame_link\frame_link_contract.py:219-260
  - src/melder\aether\nexus\acl\frame_acl_compiled_access_surface.py:32-36
  - src/melder\aether\nexus\acl\frame_acl_compiled_access_surface.py:262-292
  IMPACT: The current AR stack already has one shared published truth for
    viewer and command. The next dynamic/codegen lane should probably consume
    the existing codegen-selected and compiled ACL state rather than inventing a
    second policy system.
  NEXT: inspect the lower Conduit/Meld/CreationContext path and the room-local
    command/viewer seams together so the ticket can explain exactly how static
    reaches live runtime objects without creation, and where creation still
    happens when allowed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T23:35:43Z
  TYPE: FACT
  CLAIM: Creation still lives entirely below the AR room layer in the
    Conduit/Meld/CreationContext stack. `Conduit.meld(...)` delegates to
    `Meld.meld(...)`, which resolves spell identity, enforces validity/change-
    control gates, and then enters the spell's `CreationContext` compiled
    execution lanes for reuse or creation. `CreationContext` holds the
    spell-static executors and override-specialization machinery. Static does
    not enter that creation path directly. Instead, `StaticCommandSystem`
    denies direct `meld(...)`, allows `meld_existing_spell(...)`, and its live-
    only spell getters resolve a published `spell_index_id`, fetch the owner
    conduit, and call `owner_conduit.meld_existing_spell(...)`. The live probe
    (`has_live_creation(...)` / `describe_live_creation_status(...)`) uses the
    same spell-resolution path as `meld(...)` but stops before creation and
    only inspects current runtime storage.
  EVIDENCE:
  - src/melder\aether\conduit\conduit.py:2440-2555
  - src/melder\aether\conduit\conduit.py:2557-2632
  - src/melder\aether\conduit\conduit.py:2634-2697
  - src/melder\aether\conduit\meld\meld.py:217-395
  - src/melder\aether\conduit\meld\meld.py:397-540
  - src/melder\aether\conduit\meld\meld.py:542-645
  - src/melder\aether\conduit\meld\meld.py:770-907
  - src/melder\aether\conduit\meld\creation_context\creation_context.py:110-129
  - src/melder\aether\conduit\meld\creation_context\creation_context.py:531-537
  - src/melder\aether\conduit\meld\creation_context\creation_context.py:565-716
  - src/melder\aether\nexus\rift\rift_space\command_system\static_command_system.py:71-95
  - src/melder\aether\nexus\rift\rift_space\command_system\static_command_system.py:327-416
  IMPACT: Static is not a separate creation system and not a fake dynamic mode.
    It is a restrictive room surface over published descriptor truth plus the
    reuse-only lower-runtime seam. That makes the next dynamic/codegen question
    clearer: dynamic should own the richer execution path above the same lower
    runtime, not duplicate the lower creation machinery.
  NEXT: keep this ticket open for any remaining Nexus/static clarifications,
    but the core room/descriptor/validation/creation model is now explicit
    enough to discuss next-step DynamicSpace work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T23:35:43Z
  TYPE: FACT
  CLAIM: The viewer/command split is now concrete and shared by the same
    compiled ACL truth. `FrameViewer` clones a `FrameViewerProfile` already
    bound to:
    - one `FrameDescriptor`
    - one assembled `FrameACLConfiguration`
    - one `CompiledFrameACLAccessSurface`
    The general view profile uses that compiled surface to decide which frame,
    conduit, and spell links are emitted and which payload fields/sections are
    visible. `CommandSystem` then resolves selected targets back through the
    viewer and descriptor records and separately enforces command enablement
    through the same compiled surface. So viewer is the filtered publication
    surface, and command is the filtered action surface over that same compiled
    state.
  EVIDENCE:
  - src/melder\aether\nexus\rift\frame_viewer\frame_viewer.py:3270-3280
  - src/melder\aether\nexus\rift\frame_viewer\frame_viewer.py:3282-3324
  - src/melder\aether\nexus\rift\frame_viewer\profiles\frame_viewer_profile.py:573-699
  - src/melder\aether\nexus\rift\frame_viewer\profiles\frame_viewer_profile.py:799-840
  - src/melder\aether\nexus\rift\frame_viewer\profiles\general\view_frame.py:1527-1640
  - src/melder\aether\nexus\rift\rift_space\command_system\command_system.py:191-250
  - src/melder\aether\nexus\rift\rift_space\command_system\command_system.py:1791-1876
  IMPACT: The runtime already has one shared source of truth for "what is
    visible" and "what is executable." That means dynamic/codegen should be
    built as the next consumer of the existing compiled codegen-side contract,
    not by inventing a parallel visibility/permission system.
  NEXT: use this ticket as the grounded explanation of the current AR stack and
    stage DynamicSpace/codegen work on top of it rather than reopening static
    or capability fundamentals.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-14T11:33:56Z
  TYPE: CONFLICT
  CLAIM: The live Rift stack mostly has explicit cleanup contracts, but the
    ownership teardown is not fully coherent yet. `Nexus`, `RiftSpace`,
    `Workstation`, `CommandSystem`, `FrameViewer`, `FrameLinkContract`,
    `FrameDescriptorManager`, and `FrameACLManager` all implement explicit
    cleanup methods with deterministic local teardown. The hole is
    `Rift.cleanup()`: it clears the space registries and drops the owned
    `RiftConfiguration` reference, but it does not iterate and cleanup the
    registered spaces and it does not cleanup the owned configuration snapshot.
    Since `Rift` is the owner of those rooms and the per-Rift config snapshot,
    that means a top-level Rift teardown can leak room-local objects and their
    viewer/workstation/command/event cleanup chains.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:219-289
  - src/melder/aether/nexus/rift/rift.py:256-303
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:162-205
  - src/melder/aether/nexus/rift/rift_space/workstation.py:121-161
  - src/melder/aether/nexus/rift/rift_space/command_system/command_system.py:81-106
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:207-242
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:463-488
  - src/melder/aether/nexus/frame_descriptor_manager.py:111-142
  - src/melder/aether/nexus/frame_acl_manager.py:104-135
  IMPACT: The cleanup model is not "everything in Rift is fully safe" yet.
    The top-level ownership chain needs one fix in `Rift.cleanup()` for the
    local stack to teardown cleanly end to end.
  NEXT: answer the user with the nuanced state: most objects are cleanup-aware,
    but `Rift.cleanup()` is currently incomplete for what it owns.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the current Nexus/static-space creation-flow investigation.
