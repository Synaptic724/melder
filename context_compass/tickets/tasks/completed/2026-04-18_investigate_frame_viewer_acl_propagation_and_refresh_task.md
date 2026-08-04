# Task: Investigate Frame Viewer ACL Propagation And Refresh
- Completed: 2026-04-19T16:54:36Z
- Summary: Closed during the 2026-04-19 cleanup pass after its findings were consumed by the separated-projection implementation lane.

## Metadata
- Task ID: TASK-2026-04-18-investigate-frame-viewer-acl-propagation-and-refresh
- Story:
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-18T17:14:19Z
- Updated: 2026-04-19T16:54:36Z

## Objective
Map the live ACL lifecycle from `Nexus` into `FrameLinkContract`, viewer
projection, and command/codegen access so we can decide what should remain
fluid versus fixed.

## Ticket Contract
- ENTRY_GATE: the event/memory lane is closed and the user explicitly
  redirected to the next viewer/ACL/runtime setup discussion.
- EXECUTION_BOUNDARY: investigation and explanation only across the live
  `Nexus`, `Rift`, `RiftSpace`, frame viewer, ACL, and command/codegen
  surfaces.
- DEPENDENCIES:
  - src/melder/aether/nexus/frame_acl_manager.py
  - src/melder/aether/nexus/nexus.py
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
  - src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py
  - src/melder/aether/nexus/rift/command_system/command_system.py
  - src/melder/aether/nexus/rift/command_system/codegen_command_system.py
- EXIT_GATE: the live ACL mutation/refresh story is explicit enough to discuss
  architecture tradeoffs without guesswork.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the code contradicts the
  intended ownership model strongly enough that we need to choose between
  documenting current behavior and redesigning it immediately.

## Scope Boundaries
- In scope:
  - ACL mutability in Nexus
  - transfer of selected ACL family names into `FrameLinkContract`
  - viewer refresh/invalidation path
  - command/codegen access-surface refresh behavior
- Out of scope:
  - implementing a viewer redesign
  - changing frame-link ownership today

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user asked to work out the next viewer/ACL/runtime
  phase after closing the event lane.

## Steps / Checklist
- [ ] Read the live ACL owner and change callback path.
- [ ] Read the live `FrameLinkContract` and `Rift.target_frame(...)` flow.
- [ ] Read viewer creation/refresh and command/codegen dependency paths.
- [ ] Write the live runtime story into `## Notes`.
- [ ] Return a code-grounded explanation and recommendation.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- evidence-backed explanation of ACL mutability and downstream refresh
- explicit answer about whether the system auto-updates today

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-04-18_investigate_frame_viewer_acl_propagation_and_refresh_task.md

## Validation
- Not run.

## Risks / Rollback Notes
- Risk: the live code may still reflect multiple partially-completed ownership
  models.
- Rollback: keep the outcome descriptive and evidence-first rather than
  pretending the design is already clean.

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
- DATETIME: 2026-04-18T17:14:19Z
  TYPE: PLAN
  CLAIM: This lane is investigation-only and is focused on one concrete
    question: whether ACLs are fixed or fluid after targeting, how the
    selected ACL family names reach `FrameLinkContract`, and how viewer plus
    command/codegen access react when ACL state changes later.
  EVIDENCE:
  - user_instruction: "what happens when nexus sets ACLs are they set in stone or can they be changed"
  - user_instruction: "how do those ACLs transfer to the FrameLinkContract"
  - user_instruction: "how can they update the viewer/commandsystem/codegen system"
  IMPACT: The next response has to be a code-grounded runtime story, not
    architectural handwaving.
  NEXT: read the ACL manager, frame-link contract, viewer refresh path, and
  shared command surface.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T17:14:19Z
  TYPE: FACT
  CLAIM: `FrameLinkContract` does not snapshot a full ACL configuration. It
    only stores the selected per-frame contract names for `view`, `command`,
    and `codegen`. When `Rift.target_frame(...)` runs, `Nexus` resolves the
    current ACL snapshot for those names and validates it, but the contract
    itself retains only the names.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:20-29
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:88-96
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:149-158
  - src/melder/aether/nexus/rift/rift.py:363-409
  IMPACT: The stable thing on the Rift side is the selected contract-name set,
    not the assembled ACL payload. If a named ACL chain changes later, the
    frame link can still resolve to a different current ACL snapshot without
    mutating the stored contract names.
  NEXT: inspect the frame ACL change callback path and how viewer refresh uses
    the selected contract names later.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T17:14:19Z
  TYPE: FACT
  CLAIM: ACL state is fluid after targeting. `FrameACLContainer` fires the
    manager callback whenever one family chain selects a new current revision,
    `Nexus._on_frame_acl_changed(...)` invalidates cached projected viewers,
    and `Nexus._refresh_attached_rift_viewers_for_frame(...)` tells every
    affected Rift to rebuild and reattach its viewer for that frame.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_container.py:580-602
  - src/melder/aether/nexus/acl/frame_acl_container.py:623-640
  - src/melder/aether/nexus/acl/frame_acl_container.py:1028-1036
  - src/melder/aether/nexus/frame_acl_manager.py:73-97
  - src/melder/aether/nexus/frame_acl_manager.py:250-255
  - src/melder/aether/nexus/nexus.py:198-199
  - src/melder/aether/nexus/nexus.py:1958-2035
  IMPACT: ACL revisions are not set in stone once a frame is targeted. The
    current runtime does have an automatic downstream refresh path, but it is
    viewer-rebuild based, not live in-place mutation of one existing viewer
    object.
  NEXT: inspect how the rebuilt viewer feeds command/codegen access so we can
  answer whether those systems update automatically too.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T17:14:19Z
  TYPE: FACT
  CLAIM: The downstream refresh path is viewer-centric. `Nexus` rebuilds a new
    `FrameViewer` from the current selected contract names, including a fresh
    assembled `FrameACLConfiguration` and freshly compiled access surface per
    frame. `Rift.attach_frame_viewer(...)` then swaps that viewer onto the one
    owned `RiftSpace`. The shared `CommandSystem` does not cache ACL state on
    its own; it reads the attached viewer and compiled access surface live on
    each command call. There is no separate implemented `CodegenSystem` yet,
    and `CodegenCommandSystem` currently adds no codegen-specific refresh
    behavior beyond inheriting the shared command surface.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:1491-1521
  - src/melder/aether/nexus/nexus.py:1590-1633
  - src/melder/aether/nexus/nexus.py:1837-1880
  - src/melder/aether/nexus/rift/rift.py:436-436
  - src/melder/aether/nexus/rift/rift.py:552-566
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:131-166
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:2140-2156
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:2630-2685
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:2853-2876
  - src/melder/aether/nexus/rift/command_system/command_system.py:28-35
  - src/melder/aether/nexus/rift/command_system/command_system.py:2002-2230
  - src/melder/aether/nexus/rift/command_system/codegen_command_system.py:1-16
  IMPACT: Viewer and command access do auto-update today, but by replacing the
    attached viewer with a freshly rebuilt one. There is no distinct codegen
    runtime surface yet that independently reacts to codegen ACL changes.
  NEXT: answer the user with the current runtime story and then discuss what
  ownership model we actually want next.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T17:14:19Z
  TYPE: CONFLICT
  CLAIM: The current refresh model is not the right end-state for command and
    codegen. `CommandSystem` still depends on the attached viewer for selected
    target resolution, descriptor access, and compiled command ACL lookup, so
    command availability is still viewer-hosted even though `FrameLinkContract`
    already stores separate selected names for `view`, `command`, and
    `codegen`. That means command and view are not truly separated today.
  EVIDENCE:
  - src/melder/aether/nexus/rift/command_system/command_system.py:20-35
  - src/melder/aether/nexus/rift/command_system/command_system.py:1856-1912
  - src/melder/aether/nexus/rift/command_system/command_system.py:2210-2230
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:24-29
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:149-158
  IMPACT: If we want command-enabled but view-hidden operations to stay
    available, command cannot keep reading the viewer as its substrate.
  NEXT: stage the implementation plan around separate projections for view,
    command, and codegen plus a Nexus-owned ACL refresh protocol.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T17:14:19Z
  TYPE: RISK
  CLAIM: The current viewer-refresh path is not strong enough as the sole ACL
    update mechanism in a no-GIL runtime. `RiftSpace.attach_frame_viewer(...)`
    cleans the old viewer before replacing it, while `CommandSystem` can still
    reach into the current viewer during command execution. That creates a real
    race if ACL change propagation happens concurrently with command calls.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:355-374
  - src/melder/aether/nexus/rift/command_system/command_system.py:1856-1863
  - src/melder/aether/nexus/rift/command_system/command_system.py:1903-1910
  - user_instruction: "nexus should actually force the thread making the ACL change to properly update command system too not just viewer"
  IMPACT: The next implementation needs an explicit projection refresh protocol
    and safer swap semantics, not just "viewer rebuild and hope command reads
    the new one."
  NEXT: propose a Nexus-owned synchronous refresh cascade with separate
  projection hooks for viewer, command, and codegen.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T17:14:19Z
  TYPE: DECISION
  CLAIM: The right next runtime model is not "pause every thread in the
    process." It is a projection gate/state machine attached to each
    projection-dependent surface. `Nexus` remains the authority for ACL change
    propagation, but affected `RiftSpace` instances should expose a gate that:
    1. closes admission for view/command/codegen calls for the affected frame,
    2. waits for in-flight operations to drain with a bounded timeout
       (for example 30 seconds),
    3. atomically swaps in fresh view/command/codegen projections,
    4. reopens admission or enters a failed state if refresh does not complete.
    This should mirror the existing meld-gate idea, but at the projection
    layer instead of at conduit activation.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:50-64
  - src/melder/aether/conduit/conduit.py:2402-2448
  - src/melder/aether/nexus/nexus.py:1993-2035
  - user_instruction: "similar to meld gate"
  - user_instruction: "stop all threads update the state then resume all threads"
  - user_instruction: "we want it on a timer so if something goes wrong we throw after say 30 seconds"
  IMPACT: The next implementation should introduce a projection gate/state
    machine rather than relying on unsafe viewer replacement as the only
    refresh mechanism.
  NEXT: return the recommended gate/projection plan and get approval before
    patching the runtime.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the next investigation lane after the closed event/memory work:
live ACL mutability, frame-link propagation, and viewer/command refresh
behavior.
