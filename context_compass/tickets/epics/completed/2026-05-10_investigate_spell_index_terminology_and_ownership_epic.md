# Completed: 2026-05-10T12:04:09Z
# Summary: The staged SpellIndex investigation lane reduced into completed rename and wording-cleanup slices across the runtime and outward AR surfaces without touching real conduit lineage systems.
# Epic: Investigate SpellIndex Terminology And Ownership

## Metadata
- Epic ID: EPIC-2026-05-10-investigate-spell-index-terminology-and-ownership
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-10T10:14:03Z
- Updated: 2026-05-10T10:14:03Z
- Target Window: 2026-Q2
- Related Program/Initiative: Spell identity, mutation authority, and runtime selection cleanup

## Problem / Opportunity
The current runtime uses the word `lineage` in many places. Some of those uses
are legitimate and should stay:
- conduit lineage
- conduit lineage gates
- conduit lineage ownership trees

But the `SpellIndex` side is now under real design pressure. The user wants to
preserve the useful notch-forward-and-resolve mechanic while questioning the
ownership assumptions and terminology drift that make `SpellIndex` feel like a
spellbook-owned lineage authority instead of a runtime spell container or
selection structure.

This epic exists to isolate that work:
- investigate where `SpellIndex` is acting like lineage authority
- investigate where `SpellIndex` is acting like a runtime selection/index slot
- identify the places where raw `lineage` wording is really describing
  SpellIndex-adjacent semantics and may later need to become `index` or a more
  precise spell-index term
- keep conduit-lineage semantics explicitly out of scope

## MRP Alignment (Most Reasonable Product)
The MRP is not a blind repo-wide rename. The MRP is:
- one evidence-backed map of SpellIndex-related ownership and terminology
- one clean separation between real conduit lineage and spell-index semantics
- enough clarity to stage a future rename/refactor without damaging runtime
  behavior or mutation design

## Ticket Contract
- ENTRY_GATE: the user explicitly directed a raw `lineage` keyword
  investigation with a SpellIndex focus and explicitly said to keep clear of
  conduit lineage changes.
- EXECUTION_BOUNDARY: discovery only for SpellIndex-adjacent lineage wording,
  ownership, and dependent spell-index surfaces across `src/` and `tests/`.
- DEPENDENCIES:
  - `src/melder/spellbook/bind/spell_index.py`
  - `src/melder/spellbook/spellbook.py`
  - `src/melder/aether/dev_ops/spell_system_states/spell_system_states.py`
  - `src/melder/aether/aether.py`
  - `src/melder/aether/aetheric_frame.py`
  - `src/melder/spellbook/mutations/`
  - `src/melder/utilities/interfaces/`
  - spellbook/spell-crafter/viewer test surfaces that expose spell-index
    semantics
- EXIT_GATE: the repo has one explicit investigation lane for SpellIndex
  terminology/ownership, and each high-signal search space has its own task.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if a supposed SpellIndex
  cleanup requires changing real conduit-lineage semantics or other genuinely
  separate lineage systems.

## Goals (Outcomes)
- Separate legitimate conduit-lineage semantics from SpellIndex semantics.
- Identify where `SpellIndex` is being treated as lineage authority.
- Identify where `SpellIndex` is being treated as a runtime slot/container.
- Stage investigation tasks for each high-signal SpellIndex search space.

## Non-Goals (Explicit Exclusions)
- No runtime code changes yet.
- No conduit-lineage renaming.
- No broad mutation design rewrite in this epic.
- No blind search-and-replace of `lineage` strings.

## Scope Boundaries
- In scope:
  - SpellIndex semantics
  - raw `lineage` wording when it is really about SpellIndex
  - spellbook ownership language around SpellIndex
  - SpellSystemStates coupling to SpellIndex
  - Aether/AethericFrame registry wording around SpellIndex
  - MutationResearch wording around SpellIndex
  - interface contracts for SpellIndex
  - SpellIndex exposure in spell-crafter, validation, descriptor, viewer, and
    test surfaces
- Out of scope:
  - conduit lineage trees
  - conduit lineage gates as a concept
  - ConduitWard lineage semantics
  - module-lineage design

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a dedicated spell-index
  investigation lane and said to keep it separate from conduit-lineage work.

## Success Metrics
- One durable epic owns the SpellIndex terminology/ownership cleanup lane.
- Each high-signal SpellIndex search space has a dedicated investigation task.
- The distinction between real lineage and spell-index semantics is explicit in
  the ticket stack.

## Requirements (Functional + Non-Functional)
- Functional:
  - identify high-signal SpellIndex search spaces
  - create one task per search space
  - keep conduit-lineage changes out of scope
- Non-functional:
  - evidence-first
  - no terminology collapse across unrelated systems
  - durable enough to guide later refactor work

## Constraints / Assumptions
- `SpellIndex` may still be salvageable as a useful runtime container/index.
- Some uses of “lineage” in the system are real and should not be touched.
- The investigation must distinguish ownership semantics from runtime-selection
  semantics.

## Dependencies / External References
- recent spell-index / lineage discussion in this thread
- focused `SpellIndex` search pass across `src/` and `tests/`

## Milestones (Track Progress)
- [x] Milestone 1: identify and stage all high-signal SpellIndex search spaces
- [x] Milestone 2: investigate each search space and record whether
      terminology/ownership should change later

## Stories (Required to Complete)
- [x] Story: STORY-2026-05-10-investigate-spell-index-terminology-and-ownership

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: investigate `spell_index.py` as the core object
- [x] Task: investigate `spellbook.py` ownership and registration semantics
- [x] Task: investigate `spell_system_states.py` coupling to SpellIndex
- [x] Task: investigate `aether.py` / `aetheric_frame.py` SpellIndex registry wording
- [x] Task: investigate MutationResearch SpellIndex lineage wording
- [x] Task: investigate SpellIndex-related interfaces
- [x] Task: investigate spell-crafter and validation SpellIndex usage
- [x] Task: investigate viewer/descriptor/static-command SpellIndex exposure
- [x] Task: investigate tests and support surfaces that encode SpellIndex semantics
- [x] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- The SpellIndex investigation surfaces are all staged explicitly.
- Conduit-lineage semantics remain out of scope and untouched.
- The lane is clear enough to drive a later rename/refactor discussion without
  mixing unrelated lineage systems together.

## Risks / Mitigations
- Risk: the lane drifts into broad lineage cleanup.
  Mitigation: explicitly keep conduit lineage out of scope.
- Risk: terminology cleanup is treated as a blind text rewrite.
  Mitigation: force each search space through an evidence-backed task first.

## Applicable Anti-Patterns
- [ ] No epic-state transition without evidence-backed scope.
- [ ] No fake global “lineage cleanup” that mixes SpellIndex and conduit lineage.
- [ ] No rename proposals without search-space-level evidence.

## Validation / Test Approach
- Investigation only in this epic.
- Validation is clarity of search-space decomposition and scope discipline.

## Rollout / Adoption Plan
- Stage the story and tasks now.
- Investigate each search space separately.
- Use the investigation results to decide later whether a rename/refactor is
  warranted and how narrow it should be.

## Open Questions
- Is `SpellIndex` best understood as lineage authority, a selection container,
  or both in different places?
- Which call sites really require lineage language versus index/slot language?
- Which AR/viewer surfaces are depending on lineage wording only because the
  underlying spellbook contract does?

## Decision Log
- 2026-05-10T10:14:03Z: Opened after the user explicitly requested a
  SpellIndex-focused investigation and clarified that conduit-lineage semantics
  are not the target.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-05-10T10:14:03Z
  TYPE: FACT
  CLAIM: The prior broad lineage search mixed two different semantic classes:
    real conduit lineage on one side and SpellIndex terminology/ownership drift
    on the other. The user explicitly corrected that and narrowed the target to
    the raw `lineage` keyword only where it is actually talking about
    SpellIndex or spell-index-adjacent semantics.
  EVIDENCE:
  - user_instruction: "actually look for the keywords lineage"
  - user_instruction: "sometimes called it lineage when talking about spell_index"
  - user_instruction: "keep clear of conduit changes and its lineage"
  IMPACT: This epic must stay tightly bounded to SpellIndex semantics and avoid
    turning into a generic lineage cleanup lane.
  NEXT: stage one story and one task per high-signal SpellIndex-adjacent raw
    lineage search space.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-task tradeoffs, and scope
  discipline.
- Add notes when the investigation boundary shifts or a search space is split
  further.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This epic exists to isolate SpellIndex terminology/ownership cleanup from
other legitimate lineage systems such as conduit lineage.
