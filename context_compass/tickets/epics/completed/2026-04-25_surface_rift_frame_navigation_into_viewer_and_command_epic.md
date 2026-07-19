# Epic: Surface Rift Frame Navigation Into Viewer And Command
- Completed: 2026-04-25T16:08:39Z
- Summary: Closed after the viewer/command frame-navigation slice landed:
  viewer now separates linked, Nexus, and non-Nexus frame names; command now
  wraps frame linking and rooted Nexus-conduit retrieval without exposing raw
  frame objects; focused cross-room validation stayed green.

## Metadata
- Epic ID: EPIC-2026-04-25-surface-rift-frame-navigation-into-viewer-and-command
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-25T15:40:37Z
- Updated: 2026-04-25T16:08:39Z
- Target Window: 2026-Q2
- Related Program/Initiative: Rift room ergonomics and agent frame navigation

## Problem / Opportunity
The codegen-room namespace direction is converging toward:
- `viewer`
- `command`
- `workstation`
- `codegen`

That is cleaner than exposing raw `space`, `frame_name`, or `target`, but it
creates one missing ergonomic seam: agents still need a first-class way to
discover accessible frames and jump into them without reaching through the raw
`Rift` or `RiftSpace` object.

Current source already has the lower runtime contract:
- `Rift.create_frame_link(frame_name)` attaches a frame and refreshes
  projection-backed room assets.
- `Rift.get_nexus_frame(...)` and `Rift.create_nexus_frame(...)` already expose
  rooted Nexus-managed conduit recovery/creation.
- `Rift.list_accessible_nexus_frame_names()` already exposes Nexus-managed
  frame visibility for the requesting Rift.
- `FrameViewer.list_frame_names()` already exposes the currently assigned frame
  set, but only after frames are already linked into the Rift.

So the problem is not missing lower runtime behavior.
The problem is that the useful frame-discovery and frame-navigation methods are
still stranded at the raw `Rift` layer instead of being surfaced through the
room tools the agent is supposed to use directly.

## MRP Alignment (Most Reasonable Product)
The MRP is not exposing raw `space`.

The MRP is:
- keep the namespace/tool surface clean
- surface read-only frame discovery through `viewer`
- surface state-changing frame navigation through `command`
- preserve existing Nexus topology enforcement and frame-link validation
- avoid inventing a second frame-navigation subsystem

That gives agents a clean way to move between frames while keeping the lower
ownership and policy model intact.

## Ticket Contract
- ENTRY_GATE: the user explicitly wants agents to move between frames without
  raw `space` exposure and asked for an epic to stage that work.
- EXECUTION_BOUNDARY: investigation, design, and follow-on implementation
  staging for moving selected Rift frame operations into viewer/command.
- DEPENDENCIES:
  - `src/melder/aether/nexus/rift/rift.py`
  - `src/melder/aether/nexus/nexus.py`
  - `src/melder/aether/nexus/nexus_frame_manager.py`
  - `src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py`
  - `src/melder/aether/nexus/rift/frame_viewer/view_multiframe.py`
  - `src/melder/aether/nexus/rift/command_system/command_system.py`
  - `src/melder/aether/nexus/rift/command_system/capability_command_system.py`
  - `src/melder/aether/nexus/rift/command_system/codegen_command_system.py`
  - `codex/context_compass/system_docs/src_architecture.md`
  - `codex/context_compass/system_docs/src_components.md`
- EXIT_GATE: the exact viewer vs command frame-navigation split is explicit
  enough to implement with bounded tickets and without exposing raw `space`.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the desired surface requires
  bypassing current Nexus topology policy or widening into a broader AR
  redesign.

## Goals (Outcomes)
- Define the exact read-side frame discovery surface that should live on
  `viewer`.
- Define the exact state-changing frame navigation surface that should live on
  `command`.
- Keep raw `Rift` / `RiftSpace` out of the agent-facing namespace.
- Preserve existing Nexus-managed topology enforcement and descriptor/ACL
  validation semantics.
- Make the distinction between:
  - currently linked frames
  - accessible Nexus-managed frames
  explicit in the surfaced APIs.

## Non-Goals (Explicit Exclusions)
- Exposing raw `space` in the codegen namespace.
- Replacing the existing `Rift.create_frame_link(...)` contract.
- Reworking lower `SystemState.dynamic` or lower conduit-link semantics.
- Implementing codegen ACL policy in this epic.

## Scope Boundaries
- In scope:
  - viewer frame-discovery methods
  - command frame-navigation methods
  - Nexus-managed frame visibility semantics
  - frame-link/create/get surfacing strategy
  - implementation decomposition
- Out of scope:
  - raw room-object exposure
  - unrelated codegen execution changes
  - lower Melder topology or conduit runtime refactors

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested an epic to stage frame
  discovery and frame navigation through viewer/command instead of raw
  `space`.

## Success Metrics
- One epic owns the frame-discovery/navigation surfacing lane.
- The viewer vs command split is explicit and source-backed.
- The topology-mode semantics for accessible frames are documented clearly.
- The follow-on implementation can proceed without relitigating namespace
  design.

## Requirements (Functional + Non-Functional)
- Functional:
  - define a viewer-facing accessible-frame discovery API
  - define a command-facing frame-link API
  - define whether rooted Nexus-frame get/create should also be surfaced on
    command
  - preserve lower Nexus topology enforcement and descriptor validation
  - distinguish accessible Nexus frames from already linked frames
- Non-functional:
  - no raw `space` exposure
  - no duplicate subsystem
  - keep methods small and role-appropriate
  - keep namespace/tool ergonomics explicit for agents

## Constraints / Assumptions
- `Rift.create_frame_link(frame_name)` is already the lower runtime contract
  and should remain the owner of actual attachment behavior.
- `FrameViewer.list_frame_names()` already describes the currently assigned
  frame set and should not be redefined to mean accessible-but-unlinked frames.
- `NexusFrameManager.list_accessible_frame_names_for_rift(...)` already defines
  accessible Nexus-managed frames by topology mode:
  - `single`: the shared default frame if it exists
  - `one_per_workspace`: the private frame for that Rift if it exists
  - otherwise: all manager-owned frames in sorted order
- read-only discovery belongs on viewer more naturally than command
- state-changing frame navigation belongs on command more naturally than viewer

## Dependencies / External References
- `src/melder/aether/nexus/rift/rift.py:368-445`
- `src/melder/aether/nexus/rift/rift.py:929-1001`
- `src/melder/aether/nexus/nexus_frame_manager.py:514-588`
- `src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:146-164`
- `src/melder/aether/nexus/rift/frame_viewer/view_multiframe.py:389-408`
- `src/melder/aether/nexus/rift/command_system/capability_command_system.py:57-86`
- `src/melder/aether/nexus/rift/command_system/codegen_command_system.py:398-427`

## Milestones (Track Progress)
- [ ] Milestone 1: Freeze the exact API split.
      Success means the viewer-side and command-side method sets are explicit
      and justified from current runtime ownership.
- [ ] Milestone 2: Define accessible-frame semantics and naming.
      Success means the difference between linked frames and accessible frames
      is explicit enough to document and test.
- [ ] Milestone 3: Stage bounded implementation tickets.
      Success means the surfacing work can be implemented without reopening
      raw-namespace design.

## Stories (Required to Complete)
- [ ] Story: surface topology-aware accessible frame discovery on viewer
- [ ] Story: surface frame attach/get/create operations on command
- [ ] Story: add focused topology/viewer/command tests for the surfaced frame APIs

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: verify exact current viewer frame-discovery behavior
- [ ] Task: verify exact current Rift frame-link/get/create behavior
- [ ] Task: define method names and placement on viewer vs command
- [ ] Task: define expected behavior by Nexus frame mode
- [ ] Task: stage follow-on implementation tickets

## Acceptance Criteria (Epic Done)
- The surfacing plan is explicit and source-backed.
- Viewer and command responsibilities are clearly separated.
- Accessible-frame semantics for `single`, `one_per_workspace`, and `indexed`
  are documented.
- Follow-on implementation work can start without exposing raw `space`.

## Risks / Mitigations
- Risk: viewer methods get overloaded with state-changing behavior.
  Mitigation: keep viewer strictly read-side for this lane.
- Risk: command methods blur currently linked frames with accessible frames.
  Mitigation: document the two concepts separately and test them separately.
- Risk: a convenience surface bypasses current Nexus policy checks.
  Mitigation: wrap the existing `Rift`/`Nexus` methods rather than duplicating
  policy logic.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No implementation before the viewer/command split is explicit.
- [ ] No namespace-expansion drift back toward raw `space`.

## Validation / Test Approach
- Investigation/design first.
- Later focused tests should cover:
  - accessible-frame listing by topology mode
  - linked-frame listing vs accessible-frame listing
  - frame-link success/failure paths
  - Nexus-managed get/create command wrappers

## Rollout / Adoption Plan
1. Freeze the exact surfacing split.
2. Add viewer-side accessible-frame discovery.
3. Add command-side frame-link/get/create wrappers.
4. Add focused tests for topology semantics and wrapper behavior.
5. Revisit the codegen namespace once the viewer/command surface exists.

## Open Questions
- Should the viewer method keep the Nexus-specific name
  `list_accessible_nexus_frame_names()` or add a shorter alias like
  `list_accessible_frames()`?
- Should command expose `create_frame_link(...)` directly or a friendlier alias
  like `link_frame(...)`?
- Should `get_nexus_frame(...)` and `create_nexus_frame(...)` both be surfaced
  on command immediately, or should frame-link come first and rooted
  conduit-get/create come in a second slice?
- Do we also want a read-side “all currently linked frames” method beyond the
  existing `viewer.list_frame_names()` surface, or is the current viewer
  behavior already sufficient there?

## Decision Log
- 2026-04-25: direction set to keep raw `space` out of the namespace and move
  curated frame discovery/navigation operations into `viewer` and `command`
  instead.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-04-25T15:40:37Z
  TYPE: FACT
  CLAIM: The lower runtime frame-navigation contract already exists on `Rift`.
    `create_frame_link(frame_name)` validates policy/runtime posture, requires
    descriptor truth, materializes the selected ACL contract, validates it
    against the descriptor, stores a `FrameLinkContract`, and refreshes
    projection-backed room assets.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:368-445
  IMPACT: We do not need a new frame-link subsystem. We need a higher-level
    surfacing decision.
  NEXT: define where that contract should surface in viewer/command.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T15:40:37Z
  TYPE: FACT
  CLAIM: Accessible Nexus-managed frame discovery is already topology-aware in
    the manager layer. `single` returns the shared default frame when present,
    `one_per_workspace` returns only the requesting Rift's private frame when
    present, and the remaining mode returns all manager-owned frames in sorted
    order.
  EVIDENCE:
  - src/melder/aether/nexus/nexus_frame_manager.py:554-588
  IMPACT: We can surface accessible-frame discovery without inventing new mode
    semantics.
  NEXT: decide whether that read-side discovery belongs on viewer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T15:40:37Z
  TYPE: FACT
  CLAIM: The viewer already exposes the currently linked frame set through
    `list_frame_names()`, but that is not the same thing as "accessible Nexus
    frames." It delegates to `ViewMultiFrame`, which reads
    `Rift.list_assigned_frame_names()`.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:146-164
  - src/melder/aether/nexus/rift/frame_viewer/view_multiframe.py:389-408
  IMPACT: We need two explicit concepts:
    - linked frames
    - accessible frames
  NEXT: keep those semantics separate in the surfacing design.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T16:08:39Z
  TYPE: FACT
  CLAIM: The first implementation slice is now landed. Published non-Nexus
    frame discovery is implemented at the Nexus/Rift layer, viewer now
    exposes explicit linked/Nexus/non-Nexus frame-name surfaces, and the
    shared command surface now exposes `link_frame(...)` plus
    `get_nexus_frame(...)` without exposing raw frame objects.
  EVIDENCE:
  - src/melder/aether/nexus/frame_descriptor_manager.py:639-658
  - src/melder/aether/nexus/nexus.py:2133-2190
  - src/melder/aether/nexus/rift/rift.py:987-1018
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:146-184
  - src/melder/aether/nexus/rift/frame_viewer/view_multiframe.py:389-433
  - src/melder/aether/nexus/rift/command_system/command_system.py:897-934
  IMPACT: Agents can now discover Nexus vs non-Nexus frame names and move into
    frames through room tools instead of a raw `space` object.
  NEXT: return the landed slice for review and decide whether `get_nexus_frame`
    stays on the command surface or gets narrowed further.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T16:08:39Z
  TYPE: MEASURE
  CLAIM: The landed frame-navigation slice is green on syntax plus a focused
    unit ring covering viewer separation, room-posture filtering for non-Nexus
    discovery, and the shared command wrappers.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/frame_descriptor_manager.py src/melder/aether/nexus/nexus.py src/melder/aether/nexus/rift/rift.py src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py src/melder/aether/nexus/rift/frame_viewer/view_multiframe.py src/melder/aether/nexus/rift/command_system/command_system.py src/melder/utilities/interfaces/interfaces.py tests/unit/melder/aether/test_nexus.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus.py -k "supported_command_methods or viewer_lists_linked_nexus or codegen_room_filters_non_nexus or command_system_surfaces_frame_link"` -> `3 passed, 140 deselected`
  IMPACT: The slice is stable enough to review without widening into broader
    Rift or ACL work first.
  NEXT: let the user decide whether to keep iterating this surfacing lane or
    move back to the broader codegen ACL composition work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T16:08:39Z
  TYPE: FACT
  CLAIM: The cross-room inheritance surface is now explicit and green. Static,
    capability, and codegen rooms all expose the shared frame-navigation
    methods on their command or viewer surfaces, while codegen discovery stays
    intentionally slim and advertises only `link_frame(...)`,
    `get_nexus_frame(...)`, its selected runtime helpers, and the codegen
    seams.
  EVIDENCE:
  - src/melder/aether/nexus/rift/command_system/command_system.py:310-338
  - src/melder/aether/nexus/rift/command_system/codegen_command_system.py:748-775
  - tests/unit/melder/aether/test_nexus.py:1857-1959
  - tests/unit/melder/aether/test_nexus.py:4551-4647
  IMPACT: The frame-navigation surface is consistent across static,
    capability, and codegen without reopening raw namespace exposure.
  NEXT: none
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program direction, viewer/command boundary choices, and staging
  of the implementation lane.
- Add notes when the API split changes, mode semantics are clarified, or
  follow-on tickets are staged.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This epic owns the frame-discovery and frame-navigation surfacing lane. The
current direction is to keep raw `space` out of the namespace, put read-side
accessible-frame discovery on viewer, put state-changing frame navigation on
command, and preserve the existing `Rift`/`Nexus` policy and validation
contracts under those higher-level wrappers.
