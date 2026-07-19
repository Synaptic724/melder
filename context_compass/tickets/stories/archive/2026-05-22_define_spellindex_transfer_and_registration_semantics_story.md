# Story: Define SpellIndex, Transfer, and Registration Semantics

## Metadata
- Story ID: STORY-2026-05-22-define-spellindex-transfer-and-registration-semantics
- Epic: EPIC-2026-05-22-pin-down-spellindex-transfer-and-version-semantics
- Status: in_progress
- Owner: codex
- Agent Name: mutres_0
- Priority: p0
- Created: 2026-05-22T10:17:21Z
- Updated: 2026-05-22T10:17:21Z

## User Narrative
As the project owner, I want the current SpellIndex, transfer, and
version-related semantics investigated and defined cleanly, so later runtime
cleanup stops guessing what identity, registration, ownership, and mutation
state are supposed to mean.

## Value / MRP Alignment
This story keeps the next cleanup honest. It avoids rewriting runtime code from
an imprecise mental model and forces the semantic split to be explicit before
any implementation cut starts.

## Ticket Contract
- ENTRY_GATE: the new epic is active and the current source seams are pinned to
  exact files and methods.
- EXECUTION_BOUNDARY: investigation and semantic definition only; no runtime
  cleanup patch in this story.
- DEPENDENCIES:
  - TASK-2026-05-22-investigate-spellindex-transfer-semantic-drift
  - EPIC-2026-05-22-pin-down-spellindex-transfer-and-version-semantics
- EXIT_GATE: current semantics and target semantic split are both written down
  clearly enough to cut bounded implementation tasks.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` when the current runtime and the
  desired semantic model cannot be reconciled without a broader redesign.

## Requirements (Functional)
- Map current `SpellIndex` runtime fields and behaviors.
- Map current `Spellbook` registration semantics.
- Map current `Spell` runtime stewardship semantics.
- Map transfer-of-ownership updates across those layers.
- Define the target split between:
  - identification
  - registration
  - runtime stewardship
  - mutation/version semantics

## Requirements (Non-Functional)
- Keep claims source-backed.
- Keep the story investigation-first.
- Preserve UNKNOWN-first discipline where the target model still needs a user
  decision.

## Scope Boundaries
- In scope:
  - current source semantics
  - target semantic model
  - implementation-slice planning
- Out of scope:
  - actual runtime cleanup edits
  - unrelated mutation socket implementation work
  - unrelated Crystallizer runtime work

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested an investigation-first lane
  and a real epic instead of more speculative semantic talk.

## Dependencies / Related Work
- EPIC-2026-05-22-pin-down-spellindex-transfer-and-version-semantics
- TASK-2026-05-22-investigate-spellindex-transfer-semantic-drift
- TASK-2026-05-10-investigate-spell-index-runtime-grouping-semantics

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-05-22-investigate-spellindex-transfer-semantic-drift - map the current semantic drift and define the target split
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- Current runtime semantics are documented in evidence-backed terms.
- Target semantic split is explicit.
- Follow-up runtime cleanup tasks can be cut without semantic ambiguity.

## Validation / Test Plan
- Investigation only in this story.
- No runtime validation claims until the later cleanup tasks land.

## UX / API / Data Notes
- This story is about semantic contracts, not public API polish.

## Risks / Mitigations
- Risk: the target model keeps moving mid-investigation.
  Mitigation: keep the first task focused on current source truth and escalate
  explicit conflicts early.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- What should replace `SpellIndex.current` if `SpellIndex` becomes pure
  identification only?
- Which runtime object should own transfer-time stewardship semantics after the
  cleanup?

## Decision Log
- 2026-05-22T10:17:21Z: Story opened to force a proper investigation and
  target semantic definition before runtime cleanup.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-05-22T10:17:21Z
  TYPE: PLAN
  CLAIM: The first story slice is intentionally narrow: read current source,
    classify the current semantic drift, and define the target split before
    code changes start. That keeps the next implementation tranche from
    pretending the model is already obvious.
  EVIDENCE:
  - user_instruction: "make a dam epic like I asked we're going to investigate this first"
  - src/melder/aether/spellbook/bind/spell_index.py:32-41
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1223-1342
  IMPACT: The story can now route directly into one investigation task instead
    of stalling in chat.
  NEXT: open and route the dedicated investigation task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This story owns the investigation and definition lane for SpellIndex,
Spellbook, transfer, and version semantics before the runtime cleanup starts.
