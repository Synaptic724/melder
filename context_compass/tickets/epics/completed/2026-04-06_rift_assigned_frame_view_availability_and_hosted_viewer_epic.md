# Epic: Rift Assigned Frame View Availability And Hosted Viewer
- Completed: 2026-04-09T21:59:36Z
- Summary: Closed the downstream assigned-frame-view epic after the implementation lane was already completed.


## Metadata
- Epic ID: EPIC-2026-04-06-rift-assigned-frame-view-availability-and-hosted-viewer
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-06T14:31:44Z
- Updated: 2026-04-09T21:59:36Z

## Objective
Implement the Nexus/Rift frame-surface chain so registered Rift frames become
contract-backed available views, each available view owns the full filtered
target surface for its frame, and hosted viewer/profile commands operate only
over those assigned views.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested implementation of the Nexus frame
  surface without backward-compat shims and confirmed the target chain:
  Rift registration -> contract-backed frame availability -> assigned views ->
  viewer/profile command surface.
- EXECUTION_BOUNDARY: Nexus/Rift frame-surface behavior only.
- DEPENDENCIES:
  - codex/context_compass/tickets/tasks/2026-04-03_design_frameinfolink_hld_task.md
  - codex/context_compass/tickets/tasks/2026-04-02_design_profile_contracts_and_access_boundaries_task.md
  - src/melder/aether/nexus/
  - src/melder/aether/nexus/rift/
- EXIT_GATE: Rift-assigned frame availability is real in runtime code, the
  viewer only sees assigned views, and focused tests cover the chain.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the implementation forces a
  larger ACL ownership redesign in the same tranche.

## Scope Boundaries
- In scope:
  - contract-backed frame availability
  - assigned/available view hosting
  - frame-local filtered target surfaces
  - hosted viewer/profile command routing
- Out of scope:
  - mutation work
  - unrelated Nexus subsystems
  - broad workspace UI/runtime exposure beyond the frame-surface chain

## Deliverables
- implemented frame-availability chain
- focused tests
- cleanup of stale frame-surface leftovers

## Notes
- DATETIME: 2026-04-06T14:31:44Z
  TYPE: PLAN
  CLAIM: The current frame-surface code has the lower pieces landed but not the
    final chain. We have descriptor truth, projection, and profile-owned tools,
    but not yet the runtime behavior where Rift frame registration drives
    contract-backed available views and the viewer only sees assigned views.
  EVIDENCE:
  - user_instruction: "the rift then targets the frame, nexus sets up a contract and then we permit availability"
  - user_instruction: "you want to have available_views inside the FrameViewer object, that get added when you assign a frame"
  - user_instruction: "the view should bring in all descriptors for that frame in 1 shot, and then apply the ACLs to them too"
  IMPACT: The next implementation work should stop polishing isolated classes
    and instead wire the actual frame-assignment chain end to end.
  NEXT: create the first bounded story/task for contract-backed assigned views
    and frame-local available targets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

