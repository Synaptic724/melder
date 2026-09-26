

# Story: Melder wins the real-world gauntlet hot path (scope-cycle runtime speed)

## Metadata
- Story ID: STORY-2026-09-26-gauntlet-runtime-speed
- Epic: none (standalone; outside the IR epic's boundary and separate from the override performance epic)
- Status: draft
- Owner: user
- Agent Name: melder_2
- Priority: p1
- Created: 2026-09-26T15:43:24Z
- Updated: 2026-09-26T15:43:24Z

## User Narrative
As the Melder owner, I want Melder's per-scope-cycle runtime on the real-world gauntlet (free-threaded, three
threads) to match or beat dishka and dependency-injector, so that Melder wins the benchmark it is compared on
without changing any public behavior.

## Value / MRP Alignment
The gauntlet exercises what every user pays per request: scope create, warm melds, scope cleanup. A faster core
with unchanged contracts (existence semantics, cleanup ordering, thread-safety) is MRP work. A speedup that
weakens a cleanup or concurrency guarantee is out.

## Ticket Contract
- ENTRY_GATE: board row routes to the active child task; owner decisions D1-D3 recorded in that task.
- EXECUTION_BOUNDARY: measurement and attribution first, read-only on src/ and benchmarks/; each code change is
  its own task behind patch docs and names its files; no public API change.
- DEPENDENCIES: melder_0's override performance lane (owns the warm meld call); fable_0's 2026-09-25 per-cycle
  counts and the deferred door-diet request on the IR epic; owner-run numbers for every accepted gain.
- EXIT_GATE: owner-run gauntlet meets the agreed target in the same run as the competitors; suites green on
  3.14t and GIL for every change; the owner accepts.
- FAILURE_ESCALATION: CONFLICT when a candidate needs another agent's files; DECISION_REQUEST for the target and
  candidate selection; BLOCKER when no comparable measurement is possible.

## Requirements (Functional)
- No change to meld results, existence semantics, cleanup and disposal ordering, or error behavior.

## Requirements (Non-Functional)
- Every claimed gain is measured: same-run comparison with dishka and dependency-injector, repeated runs,
  dispersion reported; VM numbers are relative only and owner-run numbers are authoritative.
- No new lock on a warm path; suites green on 3.14t and GIL.

## Scope Boundaries
- In scope: gauntlet measurement protocol; per-scope-cycle attribution (outer and request scope create and
  cleanup, pooled lesser and SpellSpace acquire and return, creations disposal, ID minting, per-cycle locks);
  candidate changes in that lifecycle.
- Out of scope: the warm meld call and override plans (melder_0) unless the owner reassigns them; import/boot
  setup (parked by the owner on 2026-09-25) unless reopened; compiler phases (IR epic); changing what the
  gauntlet measures without owner approval.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: Story opened from the owner's 2026-09-26 request; child task waits on D1-D3.

## Dependencies / Related Work
- tickets/tasks/2026-09-26_build_site_plan_lowering_task.md (melder_0; warm meld call, cross-thread refcounts)
- tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md:825-865 (door-diet request, owner deferral)
- tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md:594-624 (2026-09-25 cProfile counts)

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-09-26-measure-gauntlet-scope-cycle-costs - reproduce, attribute, rank candidates (no code).
- [ ] Task: one task per candidate the owner picks, each behind patch docs and a gauntlet gate.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- The target is set by the owner after the attribution task; the natural candidate is melder hot_scopes/s at or
  above dishka's in the same owner run.
- Each change: owner-run before and after, suites green on 3.14t and GIL, system docs updated.

## Validation / Test Plan
- Owner-run gauntlet before and after each change; VM-copy runs for attribution and A/B.

## UX / API / Data Notes
- None; no public surface change is planned.

## Risks / Mitigations
- 2-vCPU VM cannot reproduce three-thread scaling -> VM numbers are relative; owner-run confirms.
- Overlap with melder_0's warm-meld work -> file ownership named per task; mailbox notice before a shared file.
- Cross-day variance on the owner machine (competitors moved 1.28x-1.79x between the 09-25 and 09-26 runs) ->
  ratios within one run only.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- D1-D3, in the child task's DECISION_REQUEST.

## Decision Log
- none yet

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/gauntlet_runtime_speed_20260926/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: story closure; the owner confirms retention.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-26T15:43:24Z
  TYPE: PLAN
  CLAIM: Story shape: one attribution task first (no code), then one gauntlet-gated task per candidate the owner
    picks. The child task carries the baseline, the environment facts and the D1-D3 request.
  EVIDENCE: tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md:1-40
  IMPACT: No code changes until the per-cycle cost map exists and the owner picks.
  NEXT: Owner answers D1-D3 in the child task.
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
Opened 2026-09-26 on the owner's request. First task measures and attributes; no code changes until the owner
picks candidates.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
