

# Epic: Establish why Melder's gauntlet throughput falls on long runs, from evidence

## Metadata
- Epic ID: EPIC-2026-09-26-melder-long-run-throughput-truth
- Status: review
- Owner: user
- Agent Name: melder_1
- Priority: p1
- Created: 2026-09-26T00:33:00Z
- Updated: 2026-09-26T08:05:49Z
- Target Window: 2026-09
- Related Program/Initiative: benchmarks/testing_other_di shared gauntlet; free-threaded performance

## Problem / Opportunity
The owner's shared gauntlet (free-threaded CPython 3.14, 3 threads, one process, order
dependency-injector -> dishka -> Melder) shows Melder holding 23,787 -> 23,200 hot scopes/s from 5k to
50k iterations, then falling to 20,304 at 100k (-12.5%), with outer/request create max rising from
<0.4 ms to 10.9/7.0 ms. The other two libraries drop early (5k -> 50k) and then hold. The owner asked
whether Melder leaks. The answer must come from source reads and measurements, not inference.

## MRP Alignment (Most Reasonable Product)
A dependency graph runtime that loses throughput or retains memory in proportion to request count or
thread count is a trap for long-lived services. The core claim to verify is that a lesser-conduit and
SpellSpace cycle returns the runtime to the state it was in before the cycle, whichever thread ran it.

## Ticket Contract
- ENTRY_GATE: Owner direction 2026-09-26 ("Make an epic and hunt down the truth"); board row routes
  the child tasks.
- EXECUTION_BOUNDARY: Read src/ and benchmarks/. Write only child tickets, board/mailbox rows, new
  test files under benchmarks/testing_other_di/, and evidence under artifacts/. No src/ edits; any
  fix is a separate owner-approved ticket.
- DEPENDENCIES: owner gauntlet output (recorded in the task notes); a CPython 3.14 free-threaded
  interpreter for measurements (the device shell has 3.10; a 3.14.0rc2t sandbox copy is used for
  shape, not absolute speed).
- EXIT_GATE: Each candidate cause is FACT or ruled out with source or measurement evidence;
  diagnostic tests are added; owner reviews the verdict.
- FAILURE_ESCALATION: DECISION_REQUEST before any src fix; BLOCKER if a verdict needs the owner's
  machine; CONFLICT if docs contradict source.

## Goals (Outcomes)
- A per-cycle retained-state verdict for the gauntlet's Melder path (lesser conduit + SpellSpace).
- An attribution of the 50k -> 100k drop between Melder-owned growth and harness/process effects
  (retained samples, GC with a larger heap, run order, CPU scheduling).
- Diagnostic tests the owner can run on his machine to detect regression of the verdict.

## Non-Goals (Explicit Exclusions)
- Fixing Melder source in this epic.
- Changing the shared gauntlet's reported metrics.
- Tuning dishka or dependency-injector.

## Scope Boundaries
- In scope: Melder per-thread state, lesser-conduit and SpellSpace pools, creation slot guards,
  Creations stores, ward links, registries touched per cycle; gauntlet harness memory/GC behaviour.
- Out of scope: persistence (Crystallizer), Nexus/Rift, override execution work in other lanes.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner directed the epic on 2026-09-26; T1 already in progress.
- from_state: in_progress
- to_state: review
- transition_reason: Both tasks in review with evidence; owner acceptance and harness decision pending.

## Success Metrics
- Every candidate cause listed in Notes carries FACT or ruled-out status with evidence ranges.
- Retained Python objects per Melder cycle measured under fresh-thread churn and persistent threads.

## Requirements (Functional + Non-Functional)
- Measurements state interpreter version, core count and caveats.
- Tests are deterministic in outcome (growth thresholds, not wall-clock thresholds).

## Constraints / Assumptions
- Sandbox runs use 3.14.0rc2 free-threaded on 2 cores: valid for object/memory growth, not for
  absolute throughput on the owner's i9-13900K.

## Dependencies / External References
- benchmarks/testing_other_di/test_real_world_gauntlet.py
- benchmarks/testing_other_di/real_world_gauntlet_gil_runner.py

## Milestones (Track Progress)
- [x] Milestone 1: Source verdict on per-cycle retained state (T1).
- [x] Milestone 2: Measured attribution of the long-run drop (T2).
- [x] Milestone 3: Diagnostic tests added and handed to the owner (T1).

## Stories (Required to Complete)
- [ ] none - tasks attach directly to this epic (repository pattern for investigation epics).

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: TASK-2026-09-26-investigate-melder-long-run-growth - source verdict and diagnostic tests.
- [ ] Task: TASK-2026-09-26-measure-melder-long-run-attribution - controlled runs and attribution.
- [ ] Task: TASK-2026-09-26-fix-gauntlet-sample-storage-and-melder-lane-isolation - harness fix
  and lane parity (owner-approved).
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- Owner accepts the verdict and the added tests.

## Risks / Mitigations
- Sandbox timing is not the owner's machine -> use object counts and memory, report timing as shape
  only, hand exact commands to the owner.
- One owner run per length -> ask for a repeat or a Melder-only run before any fix decision.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Sandbox: 3.14.0rc2 free-threaded probes (object counts, tracemalloc, gc callbacks).
- Owner: pytest on the new diagnostic tests; optional Melder-only gauntlet repeat.

## Rollout / Adoption Plan
- None; investigation plus additive benchmark tests.

## Open Questions
- UNKNOWN: why the owner-machine shape differs by library (DI/dishka early, Melder late); the
  opt-in attribution test answers it on that machine.
- UNKNOWN: the CPython-internal mechanism (hypothesis: allocator pages left by exited threads).

## Decision Log
- 2026-09-26: Owner opened the epic; T1 attached; T2 added for measured attribution.
- 2026-09-26: Verdict - no Melder leak; long-run drop attributed to the harness retaining
  worker-thread-allocated samples. Harness fix options raised as DECISION_REQUEST in T2.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/melder_long_run_growth_20260926/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: owner acceptance of the verdict

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - Melder retained state under thread churn; gauntlet long-run attribution.
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-26T00:33:00Z
  TYPE: PLAN
  CLAIM: T1 reads the Melder cycle path in source (lesser create/return, SpellSpace enter/exit,
    per-thread state, slot guards) and adds diagnostic tests. T2 runs the same cycle in a 3.14t
    sandbox copy of the current working tree to count retained objects per cycle under fresh-thread
    churn versus persistent threads, and measures GC pause growth and run-order effects.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-09-26_investigate_melder_long_run_growth_task.md:120-232
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:945-1136
  IMPACT: Separates "Melder retains state" from "the process got bigger/slower" before any fix talk.
  NEXT: Create T2 and route both tasks on the attention board.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T08:05:49Z
  TYPE: DECISION
  CLAIM: Epic verdict. (1) Melder has no retained growth on the gauntlet path: source bounded/symmetric,
    flat objects and blocks over 650k cycles / 30k threads, zero collections (T1). (2) The long-run
    drop belongs to the harness: keeping ints allocated by exited worker threads makes later cycles
    2-2.5x costlier for Melder and dishka alike, with zero GC; discard, main-thread copies and
    persistent threads each remove it (T2 2x2). (3) Guard tests and a 3-mode attribution test are in
    benchmarks/testing_other_di/test_melder_long_run_retention.py.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-09-26_investigate_melder_long_run_growth_task.md:120-232
  - context_compass/tickets/tasks/2026-09-26_measure_melder_long_run_attribution_task.md:105-288
  - context_compass/artifacts/melder_long_run_growth_20260926/README.md:1-40
  IMPACT: No Melder source change indicated; the harness needs a storage fix before long-run numbers
    compare libraries fairly.
  NEXT: Owner reviews; picks a harness option (T2 DECISION_REQUEST); runs the tests on his machine.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T08:27:30Z
  TYPE: DECISION
  CLAIM: Owner approved the fixes and widened scope: harness storage fixed in both gauntlet harnesses,
    shared gauntlet's broken Melder builder repaired to the Melder-only settings and made independent,
    parity guarded by test_gauntlet_melder_lane_parity.py (TASK-2026-09-26-fix-gauntlet-sample-storage-
    and-melder-lane-isolation). Sandbox long runs are flat after the fix.
  EVIDENCE: context_compass/tickets/tasks/2026-09-26_fix_gauntlet_sample_storage_and_melder_lane_isolation_task.md:1-30
  IMPACT: Epic boundary now includes benchmark harness edits (owner-approved); still no src changes.
  NEXT: Owner review of all three tasks; closure only on explicit turn-in.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

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
In review since 2026-09-26T08:05:49Z: no Melder leak; harness attributed; tests delivered. Resume from the task notes.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
