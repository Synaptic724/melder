# Epic: Cleanup Stale Fallout From Rooted Nexus Creation Refactor
- Completed: 2026-04-22T11:14:18Z
- Summary: Closed during the 2026-04-22 rebaseline after the first bounded fallout pass cleaned the direct stale aftermath from the rooted Nexus creation refactor.

## Metadata
- Epic ID: EPIC-2026-04-22-cleanup-stale-fallout-from-rooted-nexus-creation-refactor
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-22T00:40:58Z
- Updated: 2026-04-22T11:14:18Z
- Target Window: 2026-Q2
- Related Program/Initiative: Nexus frame-manager rooted conduit refactor cleanup

## Problem / Opportunity
The Nexus frame-manager creation refactor changed the creation contract in a
big way:
- Nexus/Rift-facing creation is now Spellbook-mediated
- creation is rooted by default
- the public result is the conduit, not the frame

That kind of contract cut always leaves stale fallout around it:
- tests still assuming frame returns in edge cases we did not touch yet
- docs still describing frame-first or frame-returning behavior in corners
- manager/builder/configuration APIs that may still encode older assumptions
- downstream Nexus/Rift helpers that may still treat the Nexus-created object
  as “the frame” rather than “the rooted conduit that anchors the frame”

This epic exists to isolate that fallout cleanup as a deliberate lane instead
of letting it smear into unrelated Nexus/Rift work.

## MRP Alignment (Most Reasonable Product)
The MRP is not just “the main path works.”
The MRP is “the Nexus rooted-creation contract is coherent across the nearby
system and does not leave contradictory stale seams that make the next agent
or user trip over mixed assumptions.”

If we stop at the first working green ring and leave stale frame-returning
assumptions around the surrounding APIs/docs/tests, we have not actually
landed a trustworthy foundation.

## Ticket Contract
- ENTRY_GATE: the rooted Spellbook-mediated creation lane is implemented and
  validated strongly enough that fallout cleanup can now target the aftermath
  instead of the core creation behavior itself.
- EXECUTION_BOUNDARY: stale fallout caused by the rooted Nexus creation
  contract change only.
- DEPENDENCIES:
  - tickets/epics/2026-04-21_refactor_nexus_frame_realization_into_spellbook_mediated_rooted_creation_epic.md
  - tickets/tasks/2026-04-22_implement_rooted_spellbook_mediated_nexus_creation_task.md
- EXIT_GATE: the surrounding stale fallout is identified, triaged, and
  cleaned through explicit story/task lanes instead of ad hoc edits.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the fallout crosses into a
  broader AR/Nexus public-surface redesign instead of bounded cleanup.

## Goals (Outcomes)
- Identify the stale code/docs/tests directly caused by the rooted Nexus
  creation refactor.
- Separate “real fallout” from unrelated old debt.
- Stage follow-on cleanup slices that are bounded and evidence-backed.

## Non-Goals (Explicit Exclusions)
- Broad AR/Nexus redesign unrelated to this creation contract cut.
- Reopening the core rooted-creation implementation unless a true regression is found.
- General repo-wide cleanup.

## Scope Boundaries
- In scope:
  - stale fallout from the Nexus rooted-creation refactor
  - code, tests, docs, and interfaces directly affected by that contract cut
- Out of scope:
  - unrelated viewer/command/runtime cleanup
  - unrelated Nexus topology work
  - non-Nexus creation systems

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly asked for an epic dedicated to stale
  fallout from the just-landed Nexus frame-manager change.

## Success Metrics
- One explicit epic owns the stale fallout from the rooted Nexus creation lane.
- Follow-on cleanup work can be routed without re-explaining the contract change each time.

## Requirements (Functional + Non-Functional)
- Functional:
  - identify stale assumptions introduced or exposed by the new conduit-returning contract
  - stage bounded story/task follow-ons
- Non-functional:
  - do not widen into unrelated cleanup
  - preserve source-backed, evidence-first triage

## Constraints / Assumptions
- The epic is about consequences of the rooted Nexus creation change, not
  every stale seam in Rift/Nexus.
- Any follow-on lane should prove that the stale issue is downstream of this
  contract cut.

## Dependencies / External References
- `src/melder/aether/nexus/nexus_frame_manager.py`
- `src/melder/aether/nexus/nexus.py`
- `src/melder/aether/nexus/rift/rift.py`
- `src/melder/utilities/interfaces/interfaces.py`

## Milestones (Track Progress)
- [x] Milestone 1: Enumerate and classify stale fallout from the rooted creation cut
- [x] Milestone 2: Stage the first bounded cleanup story/task

## Stories (Required to Complete)
- [x] Story: STORY-2026-04-22-audit-rooted-nexus-creation-fallout

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- The stale fallout from the rooted Nexus creation refactor is owned by this
  epic and decomposed into explicit, bounded follow-on work.

## Risks / Mitigations
- Risk: this epic turns into a vague “clean stuff up later” bucket.
  Mitigation: require every follow-on claim to point back to the rooted Nexus
  creation contract cut directly.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Discovery and classification first.
- Later follow-on tasks own the actual code/test validation for each stale
  fallout slice.

## Rollout / Adoption Plan
- Audit the fallout.
- Stage the first cleanup story/task.
- Execute cleanup in bounded slices.

## Open Questions
- Which remaining frame-returning or root-optional seams are real fallout from
  the creation change versus unrelated older debt?
- Does `get_nexus_frame(...)` need a second pass after the creation contract cut,
  or is the current conduit-returning path sufficient?

## Decision Log
- 2026-04-22: Epic created at user request to isolate stale fallout from the
  Nexus frame-manager rooted creation refactor.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Notes
- DATETIME: 2026-04-22T00:40:58Z
  TYPE: PLAN
  CLAIM: This epic is intentionally narrow. It is only about stale fallout
    caused by the rooted Nexus creation refactor, not general Rift/Nexus debt.
  EVIDENCE:
  - tickets/tasks/2026-04-22_implement_rooted_spellbook_mediated_nexus_creation_task.md:1-145
  - user_instruction: "make an epic to properly go cleanup all the stale shit as a concequence of that"
  IMPACT: Follow-on work can stay bounded to actual fallout from this contract
    change instead of diffusing into broad cleanup.
  NEXT: stage the first audit story under this epic and route the fallout review there.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-22T10:41:57Z
  TYPE: FACT
  CLAIM: The first bounded fallout pass is complete and did not uncover a second
    hidden code-path regression. The real fallout was the expected stale source,
    test, doc, and retained patch-doc wording around frame-returning or root-optional
    assumptions, and that bounded set has now been cleaned.
  EVIDENCE:
  - tickets/tasks/2026-04-22_cleanup_rooted_nexus_creation_fallout_task.md:1-76
  - tickets/tasks/2026-04-22_implement_rooted_spellbook_mediated_nexus_creation_task.md:144-210
  IMPACT: This epic can move to review and wait for acceptance instead of staying
    open as if the fallout were still unclassified discovery work.
  NEXT: review whether this first fallout pass is sufficient to accept the epic
    or whether another direct downstream cleanup seam needs its own ticket.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This epic owns the cleanup fallout caused specifically by the rooted
Spellbook-mediated Nexus creation contract cut. The first bounded fallout pass
is now complete and review-ready.
