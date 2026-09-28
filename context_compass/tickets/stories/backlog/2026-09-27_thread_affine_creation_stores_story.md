# Story: Thread-affine creation stores - per-thread registration when the profile shows one creator thread

## Metadata
- Story ID: STORY-2026-09-27-thread-affine-creation-stores
- Epic: EPIC-2026-09-27-adaptive-creation-contexts
- Status: draft
- Owner: cowork
- Agent Name: fable_0
- Priority: p2
- Created: 2026-09-27T23:42:45Z
- Updated: 2026-09-28T00:57:27Z

## User Narrative
As the Melder owner, I want a scope whose `many` creations the profile shows are built by one thread to
register them into a thread-affine bucket without taking the store lock, so that the lock and its contention
at threads > 1 stop being paid where the data says they are never contended.

## Value / MRP Alignment
Turns the thread context the owner asked for into a lever: registration without a lock measured 62-63 ns
against 103-120 locked and 305-384 today, and melder_2 measured -6..-7% per gauntlet cycle for thread-affine
shell pools on Linux. It is a guarded version, not a global change: a creation from a second thread deopts the
scope to the shared store.

## Ticket Contract
- ENTRY_GATE: owner's pick; the registration trim shipped; the capture story providing creator threads;
  patch docs before src.
- EXECUTION_BOUNDARY: `creations.py` (thread-affine buckets and their merge at cleanup/purge), the
  regenerated registration line, the guard (creator thread check), tests.
- DEPENDENCIES: STORY-2026-09-27-many-registration-trim; STORY-2026-09-27-creator-thread-context-capture;
  STORY-2026-09-27-creation-context-versioning.
- EXIT_GATE: single-thread scopes register lock-free with a measured win; a second creator thread deopts
  safely; cleanup/purge dispose everything in order; Windows measured before shipping.
- FAILURE_ESCALATION: DECISION_REQUEST if the Windows measurement disagrees with Linux; BLOCKER if the
  cleanup merge cannot be made race-free.

## Requirements (Functional)
- A per-scope thread-affine bucket keyed by creator thread, selected by a version guard on the thread ident.
- Deopt: a creation from another thread falls back to the shared, locked bucket for that scope.
- Cleanup, clear_all and purge merge the affine buckets into the disposal order newest-first.

## Requirements (Non-Functional)
- No change for scopes whose profile shows more than one creator thread.
- Measured on Linux and Windows before shipping.

## Scope Boundaries
- In scope: the affine bucket, the guard, the merge, tests, measurement.
- Out of scope: thread-affine pools (melder_2's lever) - linked, not duplicated.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: Drafted from the owner's idea list (2026-09-27T23:42:45Z); opens when the owner picks it.

## Dependencies / Related Work
- melder_2's lever 2 measurement:
  tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md:1160-1175
- Registration split: artifacts/pgo_strategies_20260927/vm_many_registration_split_gil0_20260927.md
- STORY-2026-09-27-many-registration-trim

## Tasks (Implementation Checklist)
- [ ] Task: INVESTIGATE how this idea lands in the `CreationContext` object (slot, executor variant, guard,
      cleanup ordering) before anything else; its finding is the story's first note (owner, 2026-09-27T23:54Z).
- [ ] Task: TASK design the affine bucket, the guard and the merge; the race argument for cleanup; patch docs.
- [ ] Task: TASK implement as a regenerated version behind the profile; tests with two creator threads.
- [ ] Task: TASK measure on the VM (GIL 0/1) and hand Windows and the gauntlet to the owner.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- A single-thread scope registers without the store lock and disposes in order; a second thread never loses
  an object; measured win at threads > 1 owner-run.

## Validation / Test Plan
- Unit tests on buckets and merge; component tests with a second creator thread; the deopt matrix; owner-run
  gauntlet on both platforms.

## UX / API / Data Notes
- No public API change.

## Risks / Mitigations
- OS-thread ownership on Windows -> measured; the version is per platform if needed.
- Merge at cleanup while another thread still appends -> the refusal contract, decided in the trim story.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.
- [ ] No perf claim from agent-side runs; ranking numbers are owner-run.

## Open Questions
- Is the affinity per scope (conduit/space) or per spell within a scope?

## Decision Log
- 2026-09-27T23:42:45Z (owner): idea collected into the epic; one story per idea. Collected from the owner's
  thread-context idea and melder_2's measured lever.

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
  - thread affinity; lock-free registration; cleanup merge
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-27T23:42:45Z
  TYPE: HYPOTHESIS
  CLAIM: Lock-free append after a double-checked first use measured 62-63 ns against 103-120 with the RLock
    (VM); contention at threads > 1 is unmeasured here and is what the gauntlet would show.
  EVIDENCE:
  - artifacts/pgo_strategies_20260927/vm_many_registration_split_gil0_20260927.md
  - tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md:1160-1175
  IMPACT: Worth its story only if the capture shows single-thread creators in the owner's apps.
  NEXT: owner picks; wait for the capture data.
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
STATE 2026-09-27T23:42:45Z: DRAFT. Collected from the owner's direction; not routed. Opens when the owner
picks it; its first
task is the measurement plan and the patch docs.

STATE 2026-09-28T00:57:27Z: PARKED (backlog_by_owner) with the epic; reopen on the owner's word.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
