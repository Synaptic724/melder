

# Epic: Give host integrations a public, noncreating read surface over Melder frames and configuration

## Metadata
- Epic ID: EPIC-2026-09-29-host-integration-read-surface
- Status: done
- Owner: user
- Agent Name: melder_0
- Priority: p2
- Created: 2026-09-29T21:20:43Z
- Updated: 2026-09-29T22:28:56Z

- Completed: 2026-09-29T22:28:56Z
- Summary: Milestone 1 delivered (lookups, accessors, 27 tests, notch 0.2.8208, release note; the wheel installed in
  MelderOps' env, floor raised). Closed by owner directive; the backlog story (atomic retirement, creation
  attribution) and the system-doc promotion task stay parked for the owner.
- Target Window: 2026-Q4
- Related Program/Initiative: MelderOps (priv_commandops) native Aether access

## Problem / Opportunity
MelderOps (priv_commandops, `melder_setup`) creates frames by constructing Spellbooks, records the frames it
created, and at teardown retires a recorded frame only when the name still maps to the same object and the frame
has no root conduits. Melder offers no public call that returns a frame without creating it: its frame-scoped
public calls create "default" when it is missing, and none hands back the frame. So MelderOps reads six private
surfaces: `Aether._instance/_initialized/_lock`, `Aether._aetheric_frames` under `Aether._lock`,
`AethericFrame._configuration`, `_frozen` on frame and book configurations, `Conduit._spellbook` and
`SpellbookConfiguration._aether_frame`. Melder itself reads the frame registry privately in four subsystems.

## MRP Alignment (Most Reasonable Product)
A host that creates frames needs to find and manage them through the library's own contracts. Noncreating
lookups and read-only accessors are the smallest coherent surface that removes private reads without changing
how frames are born, owned or retired.

## Ticket Contract
- ENTRY_GATE: owner direction in chat (2026-09-29): "ok lets do it go ahead and add this make an epic and implement
  and notch the version go ahead"; board row routed to the implementation task.
- EXECUTION_BOUNDARY: Melder source only (melder_private); the MelderOps switch-over belongs to command_0's paused
  priv_commandops ticket. Atomic retirement and creation attribution are parked in a backlog story.
- DEPENDENCIES: STORY-2026-09-29-frame-lookups-and-read-accessors; special_instructions/agent_contribution_guide.md.
- EXIT_GATE: the story accepted; one notch; docs, graph, release note, assets and bundles current; boards synced.
- FAILURE_ESCALATION: DECISION_REQUEST if an accessor's natural semantics differ from what MelderOps reads today.

## Goals (Outcomes)
- Aether answers "which frames exist" and "give me this frame" without creating any frame, "default" included.
- Read-only accessors cover the other private reads MelderOps needs (Aether itself is reached with `Aether()`).

## Non-Goals (Explicit Exclusions)
- No change to how frames are created, owned or cleaned; no lazy-default change to the existing conduit lookups.
- No atomic retire-if-idle or creation-reporting API in this epic's first story (backlog story).
- No edits to priv_commandops.

## Scope Boundaries
- In scope: Aether frame lookups; read-only accessors on AethericFrame, AethericFrameConfiguration,
  SpellbookConfiguration and Conduit; tests; system docs; graph; release note; notch; assets and bundles.
- Out of scope: migrating Melder's own private frame-registry readers (separate lane if wanted).

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: Owner directive in chat (2026-09-29) to turn in after the release note.

## Success Metrics
- MelderOps' six private reads each have a public replacement (or `Aether()`), documented and tested.

## Requirements (Functional + Non-Functional)
- Lookups never create a frame, take no plane claim and never freeze the Aether configuration.
- Accessors are read-only, add no lock or cost to any meld path, and change no existing behaviour.

## Constraints / Assumptions
- One notch for the landed change set (read `__version__` at landing).

## Dependencies / External References
- priv_commandops: src/melder_ops/command_center/spectrum/melder_setup/inspection.py and runtime.py (read only).

## Milestones (Track Progress)
- [x] Milestone 1: lookups and accessors landed with tests, release note and notch (docs and graph parked).
- [ ] Milestone 2: owner decision on the backlog story (atomic retirement, creation attribution).

## Stories (Required to Complete)
- [x] Story: STORY-2026-09-29-frame-lookups-and-read-accessors - lookups and read-only accessors
- [ ] Story: STORY-2026-09-29-atomic-frame-retirement-and-creation-attribution - backlog, owner decides

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: Complete story STORY-2026-09-29-frame-lookups-and-read-accessors
- [x] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- The first story is accepted by the owner; the backlog story is either scheduled or retired by the owner.

## Risks / Mitigations
- Returned frames are borrowed and unleased: documented on every lookup; nothing pins a frame.

## Applicable Anti-Patterns
- [x] No epic-state transition without story-level evidence.
- [x] No closure while required stories are incomplete or unaccepted (closed by owner directive).
- [x] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Unit tests per accessor and lookup; the meld and conduit suites; asset and bundle checks after the rebuild.

## Rollout / Adoption Plan
- MelderOps adopts the public calls in command_0's priv_commandops lane once a wheel with this notch is installed.

## Open Questions
- Backlog story: does MelderOps share its frames with other code? If so, retire-if-idle belongs in Melder.

## Decision Log
- 2026-09-29: names follow Aether's verb grammar (`get_*` raises, `find_*` returns None, `list_*` returns a tuple).

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/host_read_surface_20260929/
  - system_docs/patches/completed/host_read_surface_2026_09_29/
- DISPOSITION: retain_as_reference (artifacts); promote_to_documentation (patch lane)
- CLEANUP_TRIGGER: epic closure

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-29T21:20:43Z
  TYPE: DECISION
  CLAIM: Epic opened on the owner's direction (chat, 2026-09-29) after reviewing MelderOps' melder_setup: add
    noncreating frame lookups plus the read-only accessors that retire MelderOps' other private reads, as one
    change set with one notch. Atomic retirement and creation attribution are parked for an owner decision.
  EVIDENCE:
  - context_compass/tickets/stories/2026-09-29_frame_lookups_and_read_accessors_story.md
  - context_compass/tickets/tasks/2026-09-29_implement_frame_lookups_and_read_accessors_task.md
  IMPACT: One implementation story routes the work; the backlog story keeps the harder design visible.
  NEXT: Work the implementation task (investigation notes, patch docs, then code).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-29T22:28:56Z
  TYPE: DECISION
  CLAIM: Closed by owner directive after the release note (chat, 2026-09-29). Milestone 1 delivered: the read
    surface at 0.2.8208 and its rollout step (wheel in MelderOps' env, melder>=0.2.8208). Milestone 2 is not
    decided: the atomic-retirement story stays in stories/backlog, and the system-doc promotion is parked in
    tasks/backlog. Asset rebuild waived by the owner; the LLM bundles are stale until the next rebuild.
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-09-29_implement_frame_lookups_and_read_accessors_task.md
  - context_compass/tickets/tasks/completed/2026-09-29_build_0_2_8208_wheel_into_melderops_env_task.md
  - context_compass/tickets/tasks/backlog/2026-09-29_promote_host_read_surface_into_system_docs_task.md
  IMPACT: The owner's tranche is closed; the two open decisions remain visible in the backlog.
  NEXT: none.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user (turn-in directive)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
Closed 2026-09-29T22:28:56Z. Delivered at 0.2.8208; parked: the atomic-retirement story (owner decision) and
the system-doc promotion task. MelderOps' switch to the public calls belongs to command_0's paused
priv_commandops ticket.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
