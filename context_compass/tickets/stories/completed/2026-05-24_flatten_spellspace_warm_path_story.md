# Story: Flatten Spellspace Warm Path
- Completed: 2026-05-30T15:06:13Z
- Summary: Closed by explicit user instruction during the 2026-05-30 compiler-strategy lane reset. This ticket is superseded as an active route by the new execution-strategy compiler direction.


## Metadata
- Story ID: STORY-2026-05-24-flatten-spellspace-warm-path
- Epic: EPIC-2026-05-24-melder-runtime-performance-optimization
- Status: done
- Owner: codex
- Agent Name: mutres_0
- Priority: p1
- Created: 2026-05-24T18:22:04Z
- Updated: 2026-05-30T15:06:13Z

## User Narrative
As a Melder runtime owner, I want spellspace-scoped warm resolves to stop
repeating obvious scope lookups, so that the common spellspace path is flatter
before we widen into a full warm-hit seal.

## Value / MRP Alignment
This story targets the hottest remaining spellspace-specific tax without
mixing in broader architecture work. It keeps the runtime honest and moves the
common scoped path toward a faster, simpler shape before we add bigger caching
machinery.

## Ticket Contract
- ENTRY_GATE: the performance epic is active and the top-5 ranking has already
  identified spellspace lookup churn as a first-pass optimization target.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py`
  - tightly related spellspace/runtime helpers only if required
  - focused tests/benchmarks directly proving the hoist
- DEPENDENCIES:
  - `tickets/epics/2026-05-24_melder_runtime_performance_optimization_epic.md`
  - `tickets/tasks/2026-05-24_investigate_performance_roadmap_claims_task.md`
  - `tickets/tasks/2026-05-23_investigate_single_meld_lock_and_check_cleaned_paths_task.md`
- EXIT_GATE: the spellspace active-lookup hoist lands, direct validation is
  green, and the story notes explicitly state whether the next step should be
  the warm-hit seal.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the hoist is not actually
  isolated from the larger seal work.

## Requirements (Functional)
- Hoist spellspace active-scope lookup once per generated executor run.
- Reuse the hoisted `spellspace_id` through subsequent spellspace storage probes in that run.
- Preserve existing spellspace error semantics when no active spellspace exists.

## Requirements (Non-Functional)
- No behavioral drift on warm or cold spellspace resolution semantics.
- Keep the codegen templates readable and reviewable.

## Scope Boundaries
- In scope:
  - spellspace route generation for no-overrides and override-capable paths
  - focused test and/or benchmark validation for that route
- Out of scope:
  - full warm-hit seal implementation
  - broader creations fast-path changes
  - pool reset/return optimization

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly narrowed the next optimization cut to spellspace work and item #2 first.

## Dependencies / Related Work
- `tickets/tasks/2026-05-24_hoist_spellspace_active_lookup_once_per_executor_run_task.md`

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-05-24-hoist-spellspace-active-lookup-once-per-executor-run - Implement and validate the hoist.
- [ ] Task: evaluate whether the next slice should move directly into the warm-hit seal.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- Generated spellspace executor paths stop re-reading active spellspace more than once per run.
- Focused validation is green.
- The next step toward the spellspace warm-hit seal is explicit.

## Validation / Test Plan
- Focused unit/component tests touching spellspace creation routes.
- Focused single-meld or spellspace microbench when needed.

## UX / API / Data Notes
- No public API change expected in this slice.

## Risks / Mitigations
- Risk: the hoist helps less than expected if repeated creation-store probing dominates.
  Mitigation: measure directly after the cut before widening.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Is the next best step after the hoist the full warm-hit seal, or a smaller creations-hit-path cleanup?

## Decision Log
- Decision: execute item #2 before the larger warm-hit seal.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: ticket closure

## Notes
- DATETIME: 2026-05-24T18:22:04Z
  TYPE: PLAN
  CLAIM: The user explicitly narrowed the next optimization slice to spellspace
    work and item #2 first. The smallest coherent cut is to hoist
    `get_active_spellspace()` once per executor run and carry `spellspace_id`
    through the spellspace route before we widen into the seal.
  EVIDENCE:
  - user_instruction
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:568-571
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:758-805
  IMPACT: This gives us one measurable spellspace-path improvement without
    mixing in broader caching or invalidation machinery yet.
  NEXT: create the focused task and route the board to it.
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
This story narrows the performance lane to spellspace-specific warm-path work.
The first task is the active-spellspace lookup hoist; the warm-hit seal remains
the likely next slice after that.
