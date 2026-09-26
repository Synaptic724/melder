

# Story: Unresolved input sockets - typed parameters with no provider are supplied at meld, not refused at conjure

## Metadata
- Story ID: STORY-2026-09-26-unresolved-input-sockets
- Epic: EPIC-2026-09-24-override-execution-performance
- Status: in_progress
- Owner: user
- Agent Name: melder_0
- Lead Agent: melder_0
- Priority: p1
- Created: 2026-09-26T01:10:07Z
- Updated: 2026-09-26T01:16:08Z

## User Narrative
As a Melder user, I want a constructor parameter whose type nothing registered can provide (Package,
Conduit, greenlet, Spectrum) to compile anyway, be filled by my meld override, and fail with an error that
names exactly what is missing when I do not supply it, so that I never register objects Melder must not own.

## Value / MRP Alignment
Unblocks CommandOps' area bootstraps without weakening kernel guards or changing application constructors.
Introduces the "value comes from the call" concept the demand-driven override rewrite (design S2-S5) builds on.

## Ticket Contract
- ENTRY_GATE: Owner approved the UNRESOLVED_INPUT strategy on 2026-09-26 and asked for deep investigation
  before implementation.
- EXECUTION_BOUNDARY: Investigation and patch docs first; src/ and tests/ edits only after the owner reviews
  the patch docs and confirms the file list.
- DEPENDENCIES: trace task (review), design task (review), completed 2026-09-19 resolvable=False work.
- EXIT_GATE: Implemented, tested on 3.14t and GIL, docs promoted, owner accepts.
- FAILURE_ESCALATION: DECISION_REQUEST for policy choices; BLOCKER if a consumer cannot tolerate the new kind.

## Requirements (Functional)
- New SocketKind.UNRESOLVED_INPUT assigned in resolution only for a single typed parameter with zero providers.
- Conjure succeeds and reports each unresolved input.
- Meld uses a supplied override value by identity; a missing value raises UnresolvedInputError naming the
  consumer, parameter, expected type and override key, only when that object is constructed.
- Registering a matching provider later re-resolves the consumer into a normal edge.
- resolvable=False, OVERRIDE_REQUIRED, collections, SpellMap, SpellContract, PLAIN and ambiguity unchanged.

## Requirements (Non-Functional)
- No added work on successful melds; cache generation advanced so stale executors regenerate.

## Scope Boundaries
- In scope: compiler Phases 3-11 consumers of the socket, the error class and wiring, cache generation, tests, docs.
- Out of scope: Nexus publication of unresolved inputs (follow-up), the override build-order rewrite (S2-S5),
  a strict-mode setting, type checking of supplied values.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner approved strategy and directed deep investigation first, 2026-09-26T01:10:07Z.

## Dependencies / Related Work
- tickets/tasks/2026-09-26_trace_caller_input_conjure_strictness_regression_task.md
- tickets/tasks/2026-09-26_design_override_and_caller_input_execution_task.md
- tickets/tasks/2026-09-24_investigate_required_caller_inputs_task.md (workflows_0)

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-09-26-implement-missing-dependency-sockets - investigate, patch docs, implement, qualify
  tickets/tasks/2026-09-26_implement_missing_dependency_sockets_task.md
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- CommandOps' five reported failures conjure; supplied inputs work; missing inputs raise UnresolvedInputError.
- Existing resolvable=False behavior and tests unchanged.
- Regression suite shows no attributable failures on 3.14t and GIL.

## Validation / Test Plan
- Unit (Phase 3, injection rows, error helper), component (families, nested, reuse, late provider, cache).

## UX / API / Data Notes
- New public exception UnresolvedInputError (subclass of MeldExecutionError), exported at the package root.

## Risks / Mitigations
- Forgotten registrations surface at first meld instead of conjure: conjure warning lists unresolved inputs.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Nexus visibility of unresolved inputs (deferred follow-up).

## Decision Log
- 2026-09-26T01:10:07Z: Owner approved UNRESOLVED_INPUT with UnresolvedInputError; resolvable=False stays a separate Nexus feature.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/missing_dependency_sockets_20260926/
  - system_docs/patches/active/unresolved_input_sockets_2026_09_26/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Patch docs promoted and archived at story closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: Unresolved input sockets.
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-26T01:10:07Z
  TYPE: DECISION
  CLAIM: Owner approved the strategy and asked to reuse the override epic, investigate deeply and document every
    finding before implementation. This story owns the S1 lane of the design; the implementation task carries
    the investigation notes and patch docs.
  EVIDENCE: tickets/tasks/2026-09-26_implement_missing_dependency_sockets_task.md
  IMPACT: One story routes S1; S2-S5 get their own stories later.
  NEXT: Investigation tranche per pipeline stage, notes in the task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T01:16:08Z
  TYPE: FACT
  CLAIM: Investigation complete across Phases 3-11, validation, the watcher, exporters and every executor family;
    no consumer blocks the new kind. Patch docs written for owner review; six old-contract tests identified.
  EVIDENCE:
  - tickets/tasks/2026-09-26_implement_missing_dependency_sockets_task.md
  - system_docs/patches/active/unresolved_input_sockets_2026_09_26/architecture_patch.md:1-80
  IMPACT: Implementation can start on approval, in the patch rollout order.
  NEXT: Owner reviews the patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.

## Context / Handoff Summary
Opened on owner approval. Investigation proceeds in the implementation task. No src/ edits yet.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
