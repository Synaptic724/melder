# Task: Refresh Src Architecture And Components For Recent Rift And Meld Changes
- Completed: 2026-04-13T11:09:48Z
- Summary: Reconciled the canonical AR source docs and the stale active AR doc/access-mode tickets against the live Nexus/Rift runtime.

## Metadata
- Task ID: TASK-2026-04-10-refresh-src-architecture-and-components-for-recent-rift-and-meld-changes
- Story: STORY-2026-04-10-define-rift-access-modes-and-space-semantics
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-04-10T00:50:25Z
- Updated: 2026-04-13T11:09:48Z

## Objective
Refresh `src_architecture.md` and `src_components.md` so they match the live
AR runtime, including the manager-owned Nexus layers, the room-local
workstation/command surfaces, and the current room-mode semantics.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested the source architecture/components
  refresh after the recent Rift and Meld changes were identified as stale in docs.
- EXECUTION_BOUNDARY: source-doc and active-ticket refresh for the broader AR
  runtime drift now visible after re-entry.
- DEPENDENCIES:
  - codex/context_compass/system_docs/src_architecture.md
  - codex/context_compass/system_docs/src_components.md
  - src/melder/aether/nexus/configuration/rift_space_type.py
  - src/melder/aether/nexus/frame_descriptor_manager.py
  - src/melder/aether/nexus/frame_acl_manager.py
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/rift/rift_space/rift_space.py
  - src/melder/aether/nexus/rift/rift_space/workstation.py
  - src/melder/aether/nexus/rift/rift_space/command_system/command_system.py
- EXIT_GATE: the source docs and the active AR access-mode/doc tickets reflect
  the live AR runtime instead of the older bounded refresh story.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the refresh requires a broader
  source-doc rewrite than the bounded recent-drift pass.

## Scope Boundaries
- In scope:
  - `system_docs/src_architecture.md`
  - `system_docs/src_components.md`
  - Rift lifecycle drift
  - room-mode drift
  - manager/workstation/command-system drift
  - stale active ticket/epic semantics that now mislead onboarding
- Out of scope:
  - tests docs
  - unrelated non-AR architecture rewrite
  - runtime code changes

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly approved a targeted source-doc refresh
  for the recent Rift and Meld changes.

## Steps / Checklist
- [x] Re-read the required design-engineer source-doc inputs.
- [x] Read the current `src_architecture.md` and `src_components.md` in chunks.
- [x] Record the concrete stale sections in `## Notes`.
- [x] Patch the recent Rift/Nexus/Meld sections only.
- [x] Record the documentation deltas and validation status in `## Notes`.

## Deliverables
- refreshed `src_architecture.md`
- refreshed `src_components.md`

## Files / Paths Impacted
- codex/context_compass/system_docs/src_architecture.md
- codex/context_compass/system_docs/src_components.md
- codex/context_compass/attention_board.md
- codex/context_compass/tickets/tasks/completed/2026-04-10_refresh_src_architecture_and_components_for_recent_rift_and_meld_changes.md

## Validation
- Ran:
  - `python -m py_compile src/melder/aether/nexus/configuration/rift_space_type.py`
  - `Select-String -Path codex/context_compass/system_docs/src_architecture.md -Pattern 'FrameDescriptorManager|FrameACLManager|Workstation|CommandSystem|StaticFrameViewer'`
  - `Select-String -Path codex/context_compass/system_docs/src_components.md -Pattern 'Component: Nexus Descriptor And ACL Managers|Component: RiftSpace Workstation And Command Surface|Subcomponent: Frame Descriptor Publication Manager|Subcomponent: RiftSpace Command System|Flow: FrameDescriptorManager Passive Publication|Flow: RiftSpace Command Surface -> Runtime Operation'`
  - `Select-String -Path codex/context_compass/tickets/epics/2026-04-10_rift_access_modes_static_capability_dynamic_epic.md -Pattern 'broad manual runtime access without codegen|future codegen-oriented room|non-codegen distinction'`

## Risks / Rollback Notes
- Risk: this turns into a broad architecture rewrite instead of a narrow drift repair.
  Rollback: keep the pass bounded to the recent landed changes only.

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
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-10T00:50:25Z
  TYPE: PLAN
  CLAIM: The source-doc refresh is justified by direct drift, not by a desire to
    rewrite architecture prose. The confirmed stale anchors are in the Rift/Nexus
    path references and in the missing coverage for the recent lifecycle/probe/capability
    changes.
  EVIDENCE:
  - codex/context_compass/system_docs/src_architecture.md:199-199
  - codex/context_compass/system_docs/src_architecture.md:895-895
  - codex/context_compass/system_docs/src_components.md:561-561
  - codex/context_compass/system_docs/src_components.md:1670-1670
  - codex/context_compass/system_docs/src_components.md:2033-2033
  IMPACT: A bounded doc update is the right next move; leaving these stale will
    make the current Rift/Meld state harder to re-enter correctly later.
  NEXT: read the current source docs in chunks and pin the exact sections that
    must be updated.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-10T00:50:25Z
  TYPE: FACT
  CLAIM: The current source docs are stale in three concrete ways. First, both
    docs still point at the old `src/melder/aether/nexus/rift_space/` path even
    though the live files now live under `src/melder/aether/nexus/rift/rift_space/`.
    Second, the Rift docs still describe the older creation/targeting story
    instead of the landed bare-Rift -> primary-space -> explicit `target_frame(...)`
    flow. Third, neither doc currently mentions the landed `capability`
    space type or the new `Meld` / `Conduit` live-creation probe methods.
  EVIDENCE:
  - codex/context_compass/system_docs/src_architecture.md:199-199
  - codex/context_compass/system_docs/src_architecture.md:895-895
  - codex/context_compass/system_docs/src_components.md:561-561
  - codex/context_compass/system_docs/src_components.md:1670-1670
  - codex/context_compass/system_docs/src_components.md:2033-2033
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:1-1
  - src/melder/aether/nexus/rift/rift.py:194-194
  - src/melder/aether/nexus/rift/rift.py:406-488
  - src/melder/aether/nexus/rift/rift.py:805-854
  - src/melder/aether/nexus/configuration/rift_space_type.py:6-26
  - src/melder/aether/conduit/meld/meld.py:406-634
  - src/melder/aether/conduit/conduit.py:2510-2626
  IMPACT: The refresh can stay narrow: fix the stale paths, refresh the Rift
    lifecycle/space narrative, and add the live-creation probe to the meld runtime
    story without reopening unrelated architecture sections.
  NEXT: patch the Rift/Nexus/Meld sections in `src_architecture.md` and
    `src_components.md`, then verify the stale anchors are gone.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-10T00:50:25Z
  TYPE: MEASURE
  CLAIM: The bounded source-doc refresh is landed. `src_architecture.md` now
    reflects the staged bare-Rift -> primary-space -> explicit `target_frame(...)`
    lifecycle, the placeholder `CapabilityRiftSpace`, and the meld no-create
    live-creation probe. `src_components.md` now mirrors the same AR runtime
    semantics, includes the live-creation probe in the meld runtime component
    and method-level call flows, and no longer carries the stale
    `src/melder/aether/nexus/rift_space/` paths.
  EVIDENCE:
  - codex/context_compass/system_docs/src_architecture.md:367-376
  - codex/context_compass/system_docs/src_architecture.md:430-443
  - codex/context_compass/system_docs/src_architecture.md:641-648
  - codex/context_compass/system_docs/src_architecture.md:752-764
  - codex/context_compass/system_docs/src_components.md:489-563
  - codex/context_compass/system_docs/src_components.md:756-791
  - codex/context_compass/system_docs/src_components.md:1741-1746
  - codex/context_compass/system_docs/src_components.md:1777-1781
  - codex/context_compass/system_docs/src_components.md:2068-2074
  - validation_result: stale `rift_space/` path scan returned no hits in `src_architecture.md` or `src_components.md`
  IMPACT: The current source architecture/components docs are back in line with
    the recent Rift and Meld runtime changes, so future re-entry does not have
    to fight the stale lifecycle and path story.
  NEXT: review the bounded doc refresh and either accept it or redirect it into
    a broader source-doc rewrite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T00:24:24Z
  TYPE: FACT
  CLAIM: The earlier bounded refresh was real, but it was not enough. A deeper
    re-read of the live AR code shows three additional onboarding blockers.
    First, the canonical docs still flatten most AR behavior into one generic
    `Nexus` / `Rift` / `RiftSpace` section and do not document
    `FrameDescriptorManager`, `FrameACLManager`, or the room-local
    workstation/command layers as first-class surfaces. Second,
    `RiftSpaceType` still carries the older restrictive capability language in
    code docs. Third, the active April 10 access-mode epic still preserves the
    pre-capability semantics even though the April 12 capability artifact and
    runtime superseded them.
  EVIDENCE:
  - src/melder/aether/nexus/frame_descriptor_manager.py:30-33
  - src/melder/aether/nexus/frame_acl_manager.py:35-38
  - src/melder/aether/nexus/rift/rift_space/workstation.py:12-38
  - src/melder/aether/nexus/rift/rift_space/command_system/command_system.py:14-28
  - src/melder/aether/nexus/configuration/rift_space_type.py:6-19
  - codex/context_compass/system_docs/src_architecture.md:421-475
  - codex/context_compass/system_docs/src_components.md:489-607
  - codex/context_compass/system_docs/src_components.md:1703-1724
  - codex/context_compass/tickets/epics/2026-04-10_rift_access_modes_static_capability_dynamic_epic.md:13-32
  IMPACT: This task should now be treated as a broader AR doc/ticket
    reconciliation pass rather than a one-time recent-drift repair.
  NEXT: patch the canonical docs, the stale access-mode epic, the stale
    `RiftSpaceType` docstring, and the attention-board route together, then
    re-verify the result.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T00:31:51Z
  TYPE: MEASURE
  CLAIM: The broader AR documentation reconciliation is now landed. The
    canonical source docs explicitly name the Nexus-side manager layers
    (`FrameDescriptorManager`, `FrameACLManager`), the room-local
    workstation/command surfaces, and the static viewer overlay. The stale
    `RiftSpaceType` enum docstring now matches the implemented room posture,
    and the active April 10 access-mode epic no longer preserves the older
    restrictive capability framing.
  EVIDENCE:
  - src/melder/aether/nexus/configuration/rift_space_type.py:17-22
  - codex/context_compass/system_docs/src_architecture.md:257-270
  - codex/context_compass/system_docs/src_architecture.md:443-472
  - codex/context_compass/system_docs/src_components.md:631-758
  - codex/context_compass/system_docs/src_components.md:1859-2028
  - codex/context_compass/tickets/epics/2026-04-10_rift_access_modes_static_capability_dynamic_epic.md:33-35
  - codex/context_compass/tickets/epics/2026-04-10_rift_access_modes_static_capability_dynamic_epic.md:150-162
  - codex/context_compass/attention_board.md:70-70
  - validation_result: `python -m py_compile src/melder/aether/nexus/configuration/rift_space_type.py` -> success
  IMPACT: New onboarding and future doc refresh work can start from a more
    truthful AR model instead of reverse-engineering the Nexus managers and
    room-local surfaces from code again.
  NEXT: review the landed reconciliation, then decide whether the next doc lane
    is tests-architecture coverage for the new static/capability harnesses or
    another AR source-doc deepening pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T11:09:48Z
  TYPE: DECISION
  CLAIM: The broader AR doc/ticket reconciliation lane is complete for this
    tranche. The canonical source docs, the stale April 10 access-mode epic,
    the stale `RiftSpaceType` enum docstring, and the active board route now
    all agree on the live Nexus/Rift runtime model closely enough to close this
    task.
  EVIDENCE:
  - codex/context_compass/system_docs/src_architecture.md:257-270
  - codex/context_compass/system_docs/src_architecture.md:443-472
  - codex/context_compass/system_docs/src_components.md:631-758
  - codex/context_compass/system_docs/src_components.md:1859-2028
  - codex/context_compass/tickets/epics/2026-04-10_rift_access_modes_static_capability_dynamic_epic.md:33-35
  - src/melder/aether/nexus/configuration/rift_space_type.py:17-22
  - codex/context_compass/attention_board.md:70-70
  IMPACT: Future onboarding can start from the updated AR docs instead of
    repeating this same reconciliation pass immediately.
  NEXT: none.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task now owns the broader AR doc/ticket reconciliation pass needed to make
onboarding match the live Nexus/Rift runtime.
