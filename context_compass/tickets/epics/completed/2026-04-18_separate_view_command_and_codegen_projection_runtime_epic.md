# Epic: Separate View Command And Codegen Projection Runtime
- Completed: 2026-04-19T16:54:36Z
- Summary: Closed during the 2026-04-19 cleanup pass after the projection-split implementation landed.

## Metadata
- Epic ID: EPIC-2026-04-18-separate-view-command-and-codegen-projection-runtime
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-18T18:20:00Z
- Updated: 2026-04-19T16:54:36Z
- Target Window: 2026-04
- Related Program/Initiative: Rift runtime decoupling and synchronized ACL refresh

## Problem / Opportunity
The current runtime still couples command access to the viewer. `FrameLinkContract`
already stores separate selected ACL family names for `view`, `command`, and
`codegen`, but the runtime only materializes a viewer projection and lets
`CommandSystem` read through it. That means:
- command availability is partially hosted by view state
- view and command are not truly separate
- ACL refresh is viewer-centric instead of a real multi-surface update protocol

## MRP Alignment (Most Reasonable Product)
The next MRP is:
- split the runtime into separate view/command/codegen projections
- let `RiftSpace` own the live projection set
- let `Nexus` coordinate synchronized ACL refresh across impacted Rifts using
  `RiftGate`
- decouple `CommandSystem` from `FrameViewer`

That gives us the correct runtime substrate before later codegen-specific work.

## Ticket Contract
- ENTRY_GATE: the live ACL propagation investigation is complete and the user
  explicitly approved implementing the projection split.
- EXECUTION_BOUNDARY: projection objects, Nexus build/refresh flow, Rift/RiftSpace
  projection ownership, command decoupling, and direct tests/docs.
- DEPENDENCIES:
  - tickets/tasks/2026-04-18_investigate_frame_viewer_acl_propagation_and_refresh_task.md
  - tickets/tasks/2026-04-18_implement_rift_gate_and_rift_gate_controller_task.md
- EXIT_GATE: separate projections exist, command no longer reads the viewer
  directly, and Nexus performs synchronized ACL refresh through the gate controller.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the selected-target bridge
  requires a larger API redesign than this epic should absorb in the first cut.

## Goals (Outcomes)
- Separate view, command, and codegen runtime projections.
- Decouple command from viewer.
- Make Nexus the owner of synchronized ACL refresh across affected Rifts.

## Non-Goals (Explicit Exclusions)
- full codegen-system implementation
- workstation redesign
- deferred action model

## Scope Boundaries
- In scope:
  - projection objects
  - `FrameProjectionSet`
  - `RiftSpace` projection ownership
  - `Nexus` refresh orchestration
  - command decoupling from viewer
- Out of scope:
  - unrelated ACL authoring redesign
  - non-Rift thread orchestration

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly approved implementing the separated
  projection runtime and synchronized Nexus refresh path.

## Success Metrics
- one code-grounded split between view, command, and codegen projections
- one synchronized Nexus refresh path using `RiftGate`
- command explicit-id paths no longer depend on `FrameViewer`

## Requirements (Functional + Non-Functional)
- `Nexus` must build separate `ViewProjection`, `CommandProjection`, and
  `CodegenProjection` objects from descriptor truth plus selected ACL names.
- `RiftSpace` must own the live projection set by frame.
- `Nexus` must provide a synchronized refresh method that:
  1. identifies impacted Rifts
  2. closes their gates
  3. waits for drain
  4. rebuilds projections
  5. swaps them into the space
  6. reopens the gates
- `CommandSystem` must stop reading `FrameViewer` directly.
- No backward-compat compatibility shim is required.

## Milestones (Track Progress)
- [ ] Milestone 1: epic/story/task planning aligned and routed
- [ ] Milestone 2: projection objects and ownership landed
- [ ] Milestone 3: synchronized Nexus refresh and command decoupling landed

## Stories (Required to Complete)
- [ ] Story: STORY-2026-04-18-separate-view-command-codegen-projections
      - implement the projection split and synchronized refresh path

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: complete the projection implementation task
- [ ] Task: keep ticket notes and board routing synchronized during the split

## Acceptance Criteria (Epic Done)
- The view/command/codegen split is real in code.
- Nexus owns synchronized refresh across impacted Rifts.
- Command explicit-id paths no longer depend on the viewer.
- The focused validation ring is green.

## Risks / Mitigations
- Risk: selected-target APIs currently assume viewer state.
  Mitigation: allow a bounded room-level bridge in the first cut if needed,
  while keeping explicit-id command paths fully decoupled.

## Validation / Test Approach
- focused unit ring for:
  - frame/viewer projection behavior
  - command-system behavior
  - Nexus refresh coordination
  - Rift runtime contracts

## Open Questions
- Whether selected-target convenience should survive in `CommandSystem` via a
  room-level bridge in the first cut, or be removed entirely at once.
- Whether codegen projection should remain a stored substrate only until a real
  codegen system is implemented.

## Decision Log
- 2026-04-18T18:20:00Z: stage the separated projection runtime as the next
  Rift epic and keep the first codegen part substrate-only if needed.

## Notes
- DATETIME: 2026-04-18T18:20:00Z
  TYPE: PLAN
  CLAIM: The next runtime cut is no longer conceptual. The user explicitly
    asked to implement the separated projection model plus synchronized Nexus
    refresh, so this epic stages the code change lane around that split.
  EVIDENCE:
  - user_instruction: "Implement this!"
  - tickets/tasks/2026-04-18_investigate_frame_viewer_acl_propagation_and_refresh_task.md:92-140
  IMPACT: We can now implement the projection split under one explicit epic
    instead of drifting between investigation and gate work.
  NEXT: wire the existing story/task under this epic and start the code patch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Context / Handoff Summary
This epic owns the projection split: separate view/command/codegen projections
plus Nexus-owned synchronized ACL refresh.
