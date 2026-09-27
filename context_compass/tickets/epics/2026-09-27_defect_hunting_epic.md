# Epic: defect_hunting

## Metadata
- Epic ID: EPIC-2026-09-27-defect-hunting
- Status: in_progress
- Owner: user
- Agent Name: muse_0
- Priority: p2
- Created: 2026-09-27T15:56:49Z
- Updated: 2026-09-27T15:56:49Z
- Target Window: 2026-Q4
- Related Program/Initiative: Melder correctness review

## Problem / Opportunity
Melder is a large fast-moving runtime (593 modules, ~319k lines) whose docs
and signatures drift as code moves. A standing high-level sweep for
correctness issues — stale docstrings, signature/contract mismatches, and
doc-vs-source diffs — catches cheap defects early and surfaces any meaty
findings before they harden.

## MRP Alignment (Most Reasonable Product)
Correctness of the core experience first: contracts users and agents rely on
must say what the code does. This epic changes no behavior; it records
evidence and proposes fixes.

## Ticket Contract
- ENTRY_GATE: epic routed from the board; each sweep tranche runs under a
  child task with its own notes.
- EXECUTION_BOUNDARY: read-only review plus reported findings. No `src/` or
  `system_docs/` edits in this epic without a separate owner-approved fix lane.
- DEPENDENCIES: `src_architecture.md`, `src_components.md` plus their
  indexes; the components audit lane as method reference.
- EXIT_GATE: sweep tasks accepted, contradiction list triaged with owner,
  board sync complete.
- FAILURE_ESCALATION: record BLOCKER when a claim cannot be resolved to
  document or source; DECISION_REQUEST for fix dispositions.

## Goals (Outcomes)
- High-level superficial sweep across hot areas, starting with spellbook.
- Docstring, signature, and doc-vs-source diffs recorded with evidence.
- Meaty correctness issues called out separately from polish.

## Non-Goals (Explicit Exclusions)
- No behavior changes, refactors, or doc rewrites in this epic.
- No exhaustive per-line audit; sampling with evidence over coverage theater.

## Scope Boundaries
- In scope:
  - spellbook, conduit/meld surface, plus src_arch vs src_comp diffs.
  - Docstring accuracy, signature honesty, stale cross-references.
- Out of scope:
  - Fixes (follow-up lanes).
  - Performance benchmarking beyond noting hot-path smells.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: owner-directed defect-hunting program opened; first sweep
  task routes this epic.

## Success Metrics
- Findings recorded with `path:start-end` evidence and triage disposition.
- Zero edits outside ticket/board/notes surfaces in this epic.

## Requirements (Functional + Non-Functional)
- Every finding carries evidence and a concrete next step.
- UNKNOWN stays UNKNOWN until source is read.

## Constraints / Assumptions
- Read-only posture assumed until owner approves a fix lane.

## Dependencies / External References
- context_compass/system_docs/src_architecture.md
- context_compass/system_docs/src_components.md

## Milestones (Track Progress)
- [ ] Milestone 1: spellbook sweep - first contradiction list with evidence.
- [ ] Milestone 2: conduit/meld surface sweep.
- [ ] Milestone 3: src_arch vs src_comp diff pass with dispositions.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-09-27-spellbook-sweep - Spellbook sweep findings.
- [ ] Story: <next sweep round> - one story per round per owner direction.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: TASK-2026-09-27-spellbook-sweep - Sweep spellbook surface.
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- Sweep findings triaged with owner and follow-up lanes opened as directed.

## Risks / Mitigations
- Risk: sweep sprawls into full audit; mitigated by per-tranche task notes
  and explicit next single steps.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Not run. Review-only epic; validation belongs to follow-up fix lanes.

## Rollout / Adoption Plan
- Findings turn into owner-approved fix lanes; nothing rolls out from here.

## Open Questions
- Which area after spellbook: conduit/meld or arch-vs-comp diffs?

## Decision Log
- 2026-09-27T15:56:49Z: epic opened read-only per owner direction.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: on ticket close

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
  - defect sweep findings with evidence
- IF_UNKNOWN: ask user before implementation

## Notes
- DATETIME: 2026-09-27T15:56:49Z
  TYPE: PLAN
  CLAIM: defect_hunting epic opened read-only; spellbook sweep first.
  EVIDENCE:
  - context_compass/tickets/epics/2026-09-27_defect_hunting_epic.md:1-10
  IMPACT: Gives the cost-playground sweep a durable home without authorizing
    any behavior or doc edits.
  NEXT: Route the board to the spellbook sweep task and start reading.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

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
Epic opened per owner request as a read-only defect-hunting program. Next:
sweep task for spellbook, then conduit/meld and arch-vs-comp diffs.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
