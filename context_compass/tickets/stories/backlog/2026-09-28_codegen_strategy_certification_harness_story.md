# Story: Strategy certification harness - measure every concrete strategy on the emitted bodies before building

## Metadata
- Story ID: STORY-2026-09-28-codegen-strategy-certification-harness
- Epic: EPIC-2026-09-27-adaptive-creation-contexts
- Status: draft
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-09-28T00:57:27Z
- Updated: 2026-09-28T00:57:27Z

## User Narrative
As the Melder owner, I want one experiment module that captures the plain emitted body for a set of
representative shapes, applies each concrete strategy (S1-S7 in the epic) as a source transform of that body,
executes it and times plain against each and all combined, so that the 5-10% question is answered by numbers
before a multi-thousand-line lane is opened.

## Value / MRP Alignment
The cheapest possible proof: no src change, the real emitter's output, the real runtime objects, and a table
that says which strategies are certified. It reuses the capture trick of the probe prototype
(`SitePlanLowering.emit` wrapped) and the store stand-ins of the registration experiment.

## Ticket Contract
- ENTRY_GATE: owner's word to reopen; no patch docs (experimentation only).
- EXECUTION_BOUNDARY: `tests/experimentation/codegen_strategy_certification.py` (new), prototype store
  classes inside it, runs under artifacts/pgo_strategies_20260927/.
- DEPENDENCIES: the Concrete Strategies section of the epic; the probe prototype and the registration
  experiment.
- EXIT_GATE: a table of plain vs each strategy vs all combined for Worker, ContextRoot, wide8 over uniques,
  wide8 over existing objects and chain8, VM-directional, with the certified set named; owner-run
  confirmation on the gauntlet shapes.
- FAILURE_ESCALATION: DECISION_REQUEST if no strategy clears 5% on any shape the owner's applications have.

## Requirements (Functional)
- Capture the plain normal plan per shape through a `SitePlanLowering.emit` wrapper.
- Transforms: S1 (one-append registration against a stand-in store), S2a (existing-object constants), S2b
  (epoch-guarded unique constants), S4 (single-door prologue), S5 (batched registration, lazy index), S6
  (thread-affine append); each a deterministic edit of the captured source.
- Timing: median of batches after warm-up, plain vs each vs all combined; Python/C call counts per body.
- Output: one markdown table per shape plus the certified set (a strategy is certified when it wins on every
  shape it applies to and never loses).

## Requirements (Non-Functional)
- No src change; 3.14t GIL off; directional numbers labelled as such.

## Scope Boundaries
- In scope: the harness, the transforms, the runs, the table.
- Out of scope: implementing any strategy.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: Drafted from the owner's direction (2026-09-28T00:57:27Z); parked with the epic.

## Dependencies / Related Work
- tests/experimentation/probe_creation_context_prototype.py:1-136
- tests/experimentation/many_registration_split_experiment.py:1-142
- tickets/epics/backlog/2026-09-27_adaptive_creation_contexts_epic.md (Concrete Strategies)

## Tasks (Implementation Checklist)
- [ ] Task: INVESTIGATE how this idea lands in the `CreationContext` object (slot, executor variant, guard,
      cleanup ordering) before anything else; its finding is the story's first note.
- [ ] Task: TASK build the harness with the S1-S6 transforms over the five shapes; run on the VM; land the table.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- The table exists in the artifacts with the certified set named and the owner has the gauntlet numbers.

## Validation / Test Plan
- The harness itself (VM runs); owner-run gauntlet on the same shapes.

## UX / API / Data Notes
- None.

## Risks / Mitigations
- Source transforms drift from what an emitter would produce -> keep transforms minimal and quote the
  emitted lines in the table.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.
- [ ] No perf claim from agent-side runs; ranking numbers are owner-run.

## Open Questions
- Which shapes from the owner's other applications should join the five?

## Decision Log
- 2026-09-28T00:57:27Z (owner): define concrete, well-defined strategies and test them before implementing
  the ~5k-LOC system.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/pgo_strategies_20260927/ (proof and runs shared by the epic; new runs land here)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: promoted into the canonical maps when the story ships.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - certification harness; strategy transforms; emitted bodies
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-28T00:57:27Z
  TYPE: PLAN
  CLAIM: Predicted from the price model: Worker -50..-60%, ContextRoot -55%, wide8 over uniques -12%, wide8
    over existing objects -33%, singleton warm melds 0; the harness turns these into measurements.
  EVIDENCE:
  - tickets/epics/backlog/2026-09-27_adaptive_creation_contexts_epic.md:150-215
  - artifacts/pgo_strategies_20260927/vm_commandops_shapes_gil0_20260927.md
  IMPACT: The one experiment that decides whether the epic reopens.
  NEXT: parked with the epic; reopen on the owner's word.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

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
STATE 2026-09-28T00:57:27Z: DRAFT, PARKED. Collected from the owner's direction and shelved with the epic; not routed.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
