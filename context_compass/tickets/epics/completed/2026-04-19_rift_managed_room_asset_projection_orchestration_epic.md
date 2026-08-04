# Epic: Rift-Managed Room Asset Projection Orchestration
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Epic ID: EPIC-2026-04-19-rift-managed-room-asset-projection-orchestration
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-19T12:16:10Z
- Updated: 2026-04-19T16:37:39Z
- Target Window: 2026-04-19
- Related Program/Initiative: AetherRift projection ownership cleanup

## Problem / Opportunity
The runtime now has a durable room-owned viewer asset, but projection state and
projection application are still too room-centric.

Current wrong shape:
- `Nexus` compiles projections
- `Rift` orchestrates refresh
- `RiftSpace` still stores projection state
- `RiftSpace` still exposes projection accessors and projection-application
  helpers
- `CommandSystem` still reads command projection state through `RiftSpace`

That means the wrong object still "manages" projection-derived asset state.

The intended model is:
- `Nexus` owns projection creation
- `Rift` owns contract lifecycle and projection application orchestration
- `RiftSpace` hosts assets only
- room assets start empty
- when a frame contract forms or ACL changes, `Rift` gets projections from
  `Nexus` and applies them to the hosted assets automatically
- the agent never touches projections

## MRP Alignment (Most Reasonable Product)
The most reasonable product is:
- move projection registry ownership from `RiftSpace` to `Rift`
- remove projection accessors and projection-management seams from `RiftSpace`
- make `Rift` the single owner of projection application to hosted assets
- make `CommandSystem` read current projection truth from `Rift`, not `space`
- keep projections hidden implementation detail rather than part of the room
  surface

## Ticket Contract
- ENTRY_GATE: the user explicitly rejected room-owned projection management and
  clarified that `Rift` must own asset/projection orchestration.
- EXECUTION_BOUNDARY: `Rift`, `RiftSpace`, `CommandSystem`, focused tests, and
  matching AR docs only.
- DEPENDENCIES:
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/rift/rift_space/rift_space.py
  - src/melder/aether/nexus/rift/command_system/command_system.py
  - src/melder/aether/nexus/rift/command_system/static_command_system.py
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
  - src/melder/utilities/interfaces/interfaces.py
- EXIT_GATE: `Rift` owns projection registry + application, `RiftSpace` stops
  exposing projection management seams, command projection access is Rift-owned,
  and focused tests/docs are green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the lane exposes a real
  codegen-asset requirement rather than the current codegen-projection-only
  state.

## Goals (Outcomes)
- Make `Rift` the owner of applied projection state.
- Keep room assets durable but projection-blind.
- Remove projection-management responsibility from `RiftSpace`.
- Route command projection access through `Rift`.
- Keep projections hidden from the agent-facing room surface.

## Non-Goals (Explicit Exclusions)
- Do not redesign `Nexus` projection compilation.
- Do not redesign viewer helper APIs.
- Do not invent a fake codegen asset if one does not yet exist.
- Do not reopen the full explicit `frame_name` enforcement lane here.

## Scope Boundaries
- In scope:
  - Rift-owned projection registry
  - Rift-owned projection application to viewer + command assets
  - removal of room projection accessors
  - command-system projection lookup rebasing
  - focused tests/docs
- Out of scope:
  - command vocabulary redesign
  - codegen execution system design
  - broader ACL model work

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the implementation story/task landed and the broader
  AR/command/viewer ring is green.

## Success Metrics
- `RiftSpace` no longer stores or exposes projection state.
- `Rift` stores current projections internally.
- `CommandSystem` gets command projection truth from `Rift`, not `space`.
- Viewer sync is triggered from `Rift`.
- Agent-facing room surface no longer exposes projections.

## Requirements (Functional + Non-Functional)
- `Rift` must own the current frame projection registry.
- `Rift` must merge/replace projection updates and then apply them to assets.
- `RiftSpace` must stop exposing projection management methods.
- `CommandSystem` must stop calling `self._space.get_required_command_projection(...)`.
- Command runtime-frame fallback, where still used, must resolve through `Rift`
  rather than through a room projection/default shim.
- The implementation must stay honest about current codegen reality: if no
  durable codegen asset exists yet, codegen projections remain Rift-owned
  internal state for now.

## Constraints / Assumptions
- Room assets still live on `RiftSpace`.
- Projections still come from `Nexus`.
- `CommandSystem` currently depends on `space` for memory system and gate access
  and can keep those room-hosting references while projection lookup moves to
  `Rift`.

## Dependencies / External References
- codex/context_compass/system_docs/src_architecture.md
- codex/context_compass/system_docs/src_components.md
- durable-viewer lifecycle epic
- atomic ACL batch refresh epic

## Milestones (Track Progress)
- [ ] Milestone 1: Ownership redesign staged
      The Rift-vs-room projection ownership boundary is explicit and approved.
- [x] Milestone 2: Rift owns projection registry
      Room no longer stores projection sets.
- [x] Milestone 3: Command projection access is Rift-owned
      CommandSystem no longer reads projections from space.
- [x] Milestone 4: Room surface is projection-blind
      Projection accessors and management seams are removed from RiftSpace.

## Stories (Required to Complete)
- [x] Story: STORY-2026-04-19-implement-rift-managed-room-asset-projection-orchestration -
      implement Rift-managed room asset projection orchestration

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: TASK-2026-04-19-implement-rift-managed-room-asset-projection-orchestration
- [ ] Task: Verify Ticket Microcycle enforcement across staged tickets.

## Acceptance Criteria (Epic Done)
- `Rift` owns current applied projection state.
- `RiftSpace` no longer owns projection registry or projection accessors.
- `CommandSystem` and viewer asset updates are driven by `Rift`.
- Focused tests and AR docs reflect the new ownership split.

## Risks / Mitigations
- Risk: command-system direct tests rely on room-owned projection shims.
  Mitigation: update direct tests to use Rift-owned fake projection providers.
- Risk: codegen projection ownership may be ambiguous without a real codegen
  asset.
  Mitigation: keep codegen projections Rift-internal for now and document that
  explicitly.

## Applicable Anti-Patterns
- [ ] No projection-management API remains on `RiftSpace` after this lane.
- [ ] No claim that `RiftSpace` manages contracts or projection lifecycles.
- [ ] No fake codegen asset is invented just to satisfy symmetry.

## Validation / Test Approach
- Focused room/rift tests for asset orchestration.
- Focused command-system tests for Rift-owned projection access.
- Focused AR integration ring for target/refresh behavior.

## Rollout / Adoption Plan
- Stage the implementation story/task and patch docs.
- Move projection registry/apply logic into `Rift`.
- Rebase `CommandSystem` onto Rift-owned projection access.
- Remove room projection seams.
- Update focused tests/docs.

## Open Questions
- Whether `CommandSystem` should hold a direct Rift reference or a narrower
  internal projection provider contract.

## Decision Log
- Pending implementation.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-04-19T12:16:10Z
  TYPE: FACT
  CLAIM: The runtime is still too room-centric. `RiftSpace` still owns
    `_projection_sets_by_frame_name`, still exposes projection accessors, and
    `CommandSystem` still pulls command projection truth through `space`.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:157-158
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:485-586
  - src/melder/aether/nexus/rift/command_system/command_system.py:242-2666
  IMPACT: The durable-viewer slice improved asset lifecycle, but not ownership
    of projection orchestration.
  NEXT: implement the Rift-owned projection registry and remove room seams.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T12:39:30Z
  TYPE: FACT
  CLAIM: The ownership correction is landed. `Rift` now owns the projection
    registry and asset application path, `RiftSpace` no longer exposes
    projection seams, and `CommandSystem` now follows the same Rift-owned
    projection model.
  EVIDENCE:
  - tickets/tasks/2026-04-19_implement_rift_managed_room_asset_projection_orchestration_task.md:1-170
  - src/melder/aether/nexus/rift/rift.py:87-88
  - src/melder/aether/nexus/rift/rift.py:490-667
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:35-84
  - src/melder/aether/nexus/rift/command_system/command_system.py:21-39
  IMPACT: The epic is back in review and no longer needs active implementation
    work unless a follow-on is requested.
  NEXT: hold for review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level ownership direction, cross-story sequencing, and
  boundary cleanup.
- Add notes when projection ownership, command access, or codegen handling
  changes.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This epic corrects the remaining ownership bug after the durable-viewer slice:
`Rift` should manage projection-driven asset updates, not `RiftSpace`.