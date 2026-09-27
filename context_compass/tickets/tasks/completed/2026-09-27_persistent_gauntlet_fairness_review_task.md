# Task: Fairness review of the persistent runtime gauntlet (melder vs dependency-injector vs dishka)

## Metadata
- Task ID: TASK-2026-09-27-persistent-gauntlet-fairness-review
- Story: none (owner-directed review)
- Status: done
- Owner: cowork
- Agent Name: fable_0
- Priority: p2
- Created: 2026-09-27T11:19:40Z
- Updated: 2026-09-27T12:37:00Z
- Completed: 2026-09-27T12:37:00Z
- Summary: Harness judged symmetric with source evidence; the per-cycle work was proven identical across the three
  libraries by constructor counts; the disclosure recommendations (environment line, identity and scope-semantics
  checks, honest labels) landed through the follow-up dishka/parity task. Closed at the owner's turn-in.

## Objective
Owner asked ("make sure it's fair and there's no bullshit gaming the results") for a review of
`benchmarks/testing_other_di/test_persistent_runtime_gauntlet.py` after his 6-run, 300 s/run, 10-thread,
`-X gil=0` session (melder 210,654 cycles/s wall vs dishka 107,653 vs dependency-injector 23,404 on
fastapi_steady). Read the harness whole, the three lane builders it reuses from `test_real_world_gauntlet.py`,
and the class graph; verify the per-cycle work is identical across libraries by instrumenting constructors;
characterize what the numbers measure (single-thread, GIL on/off) so the claim is stated fairly.

## Ticket Contract
- ENTRY_GATE: owner request 2026-09-27.
- EXECUTION_BOUNDARY: reads only under benchmarks/; a scratch probe outside the repo (VM home); no edits.
- DEPENDENCIES: dependency-injector 4.49.1 and dishka 1.10.1 installed into the VM venv for the probe.
- EXIT_GATE: findings reported with evidence; owner decides on harness changes.
- FAILURE_ESCALATION: none.

## Scope Boundaries
- In scope: harness symmetry, per-cycle work equivalence, disclosure of what is measured.
- Out of scope: changing the harness (recommendations only).

## State Transition Event
- from_state: draft
- to_state: review
- transition_reason: Review executed and reported in one pass (2026-09-27T11:19:40Z).
- from_state: review
- to_state: done
- transition_reason: Owner turn-in directive (2026-09-27T12:37:00Z); verdict acknowledged, recommendations landed
  elsewhere.

## Steps / Checklist
- [x] R1: read the harness whole and the lane builders, wiring, existence partition, timers.
- [x] R2: instrumented-constructor probe over the unmodified lane builders (all three libraries).
- [x] R3: single-thread and 4-thread runs with `-X gil=1` and `-X gil=0` on the VM (2 cores).
- [x] R4: report.
- [x] Run Ticket Microcycle during execution.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Findings (Notes) and the owner report; probe script kept in the VM home (not in the repo).

## Files / Paths Impacted
- none (review only)

## Validation
- Probe and short runs executed on the VM venv (CPython 3.14.7t) against the device tree's benchmarks/ and src/.

## Risks / Rollback Notes
- none

## Applicable Anti-Patterns
- [x] No claim of unfairness or fairness without source evidence.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed (owner turn-in 2026-09-27)
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none
- DISPOSITION: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: benchmark fairness; free-threaded scaling.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-27T11:19:40Z
  TYPE: FACT
  CLAIM: Harness symmetry. `test_persistent_runtime_gauntlet.py` is library-agnostic: one worker loop, one
    lane-choice RNG (per-library seeds differ only to decorrelate; weights 60/25/15 and three variants are
    shared), the same warmup, sampling rate, timers and idle handling; `cycle_total` wraps the whole lane call
    (scope create, resolves, identity asserts, scope cleanup) for every library; `objects_min` is a per-lane
    constant times cycles, the same constant for every library. The lane builders in
    `test_real_world_gauntlet.py` wire one class graph from constructor annotations for all three, with the
    same existence partition (singletons; outer-scoped RequestSession/Worker*Session; request-scoped markers
    and roots; transient leaves/groups; transient Layer chain and Bootstrap objects). Melder's outer scope is a
    real lesser conduit (create + cleanup measured, ~0.02 ms) where dependency-injector's is a bare
    `contextvars.Context()` with no teardown - melder pays more scope machinery per cycle, not less.
  EVIDENCE:
  - benchmarks/testing_other_di/test_persistent_runtime_gauntlet.py:455-566
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:362-441
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:592-1186
  IMPACT: No structural bias toward melder in the harness or the wiring.
  NEXT: prove the per-cycle work is identical by counting constructions.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T11:19:40Z
  TYPE: MEASURE
  CLAIM: Constructor-counting probe over the UNMODIFIED lane builders (VM venv, 3.14.7t, `-X gil=0`; each
    library: spawn_singletons, bootstrap_fanout, then request lane variants 0/1/2): identical counts for
    melder, dependency-injector and dishka - variant 0 and 2: 63 constructions (RequestSession 1, Layer1-4 4,
    BootstrapAObject 1, RequestScopeMarker 1, RequestRoot 1, RequestGroup 5, RequestLeaf 50); variant 1: 74
    (+1 group, +10 leaves). No library pools transients or skips work; `objects_min` = 63 is exact for two of
    three variants and a lower bound for the third.
  EVIDENCE:
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:426-433
  - (probe: VM home work/bench/fair/freshness_probe.py; output recorded in this note)
  IMPACT: The "same work per cycle" premise of the comparison holds, class by class.
  NEXT: characterize what the 10-thread no-GIL numbers measure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T11:19:40Z
  TYPE: MEASURE
  CLAIM: Short runs on the VM (2 cores; 8 s measured, 2 s warmup, fastapi_steady). threads=1: melder 0.010 ms
    per cycle, dishka 0.010 ms, dependency-injector 0.021 ms - identical with `-X gil=1` and `-X gil=0`.
    threads=4 (oversubscribed on 2 cores): gil=1 melder 74.8k cycles/s, dishka 85.2k, DI 42.7k; gil=0 melder
    123.9k, dishka 143.0k, DI 57.3k. So single-threaded melder ties dishka and beats DI 2x; under threads the
    ranking depends on the machine (dishka led on this 2-core VM at 4 threads; the owner's box at 10 threads
    gave melder 2x dishka and 9x DI). The owner's per-cycle costs at 10 threads (melder 0.044 ms, dishka 0.089,
    DI 0.422) versus 1-thread costs show the comparison is dominated by free-threaded scaling behavior, which
    is what the harness sets out to measure, not by per-object resolution cost.
  EVIDENCE:
  - benchmarks/testing_other_di/test_persistent_runtime_gauntlet.py:8-27
  - (runs recorded in this note; owner log of 2026-09-27 04:38 in the conversation)
  IMPACT: Fair to publish only with the environment stated: core count, thread count, `-X gil` flag, and a
    threads=1 row; dependency-injector and dishka do not target free-threaded Python.
  NEXT: report with recommendations (labels, single-thread row, freshness assert, one seed).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T11:22:41Z
  TYPE: DECISION
  CLAIM: Owner's correction accepted: the VM has 2 cores, so its 4-thread rows are an oversubscribed regime and
    say nothing about 10-thread scaling; the only VM evidence that stands is the threads=1 per-cycle cost
    (melder 0.010 ms = dishka 0.010 ms, DI 0.021 ms) and the constructor-count parity. The 10-thread ranking is
    the owner's hardware result and is the scaling claim; presenting it next to a threads=1 row and the core
    count is what makes it fair, not a change to the harness.
  EVIDENCE:
  - tickets/tasks/2026-09-27_persistent_gauntlet_fairness_review_task.md (MEASURE notes above)
  IMPACT: Recommendation 1 (environment line + threads=1 row) is the substantive one; a threads sweep
    (1,2,4,8,10) on the owner's box would show the scaling curve per library.
  NEXT: owner decides.
  REREAD: OPTIONAL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T12:37:00Z
  TYPE: DECISION
  CLAIM: Closed by owner directive at turn-in. The verdict stands as reported (symmetric harness; identical per-cycle
    work by constructor count; the 10-thread ranking is the owner's hardware result and is fair to publish beside
    the core count, the GIL flag and a threads=1 row). Every harness recommendation from this review was
    implemented in the follow-up task rather than here: the environment/version line and the untimed
    scope-semantics parity phase (D2/D3), the inner-object rate label, the dependency-injector cleanup label, the
    deadline ordering with validation, the minimal instrumentation mode and the variant-2 identity checks (D6).
  EVIDENCE:
  - tickets/tasks/completed/2026-09-27_dishka_scope_placement_and_parity_phase_task.md (notes 11:44:54Z, 11:54:31Z)
  IMPACT: Nothing open; the audit trail for the fairness claim is this ticket plus the follow-up task.
  NEXT: none.
  REREAD: OPTIONAL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
STATE 2026-09-27T11:19:40Z: REVIEW. Verdict: symmetric harness, identical per-cycle work proven; recommendations are
disclosure and guard-rails, not fixes. Owner decides whether to amend the harness.
STATE 2026-09-27T12:37:00Z: DONE. Closed at the owner's turn-in; recommendations landed in the dishka/parity task;
board synced.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
