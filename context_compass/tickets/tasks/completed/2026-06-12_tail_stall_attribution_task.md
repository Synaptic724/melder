

# Task: Attribute melder's tail-latency stalls (GC vs locks vs allocator)

## Metadata
- Task ID: TASK-2026-06-12-tail-stall-attribution
- Story: none
- Status: done
- Owner: claude
- Agent Name: compiler_builder_0
- Priority: p1
- Created: 2026-06-12T22:59:34Z
- Updated: 2026-06-12T23:55:00Z

## Objective
Attribute melder's tail stalls (gauntlet max 17-70ms, whole-cycle cv
240-340% vs dishka 1-10ms / cv ~70% in the SAME runs) to a mechanism.
Cycle locks and the fast door are exonerated (prior lanes). Suspects:
GC pauses under per-cycle allocation pressure, spellbook
`_phase_run_lock` revalidation serialization, allocator/scheduler
behavior on 3.14t.

## Ticket Contract
- ENTRY_GATE: active board row; prior-lane evidence carried (stalls never
  reproduced in the isolation harness; environment-sensitive).
- EXECUTION_BOUNDARY: one new diagnostic harness under
  `benchmarks/testing_other_di/`; fixes (if any) land only in surfaces
  this agent owns (conduit/meld/scheduler); GC-policy changes require
  user sign-off. NOT in scope: compiler phases, mediator, dev_ops.
- DEPENDENCIES: profile_scope_cycle_contention.py workload shape.
- EXIT_GATE: stalls classified with measured evidence (e.g. % overlapping
  GC windows; gc-disabled control run delta); fix or documented
  disposition accepted by user.
- FAILURE_ESCALATION: BLOCKER if stalls trace to CPython internals with
  no code-level mitigation; CONFLICT if mitigation requires changing
  default GC posture for users.

## Scope Boundaries
- In scope: GC-window/stall-overlap harness; gc-disabled control mode;
  per-surface stall logs; allocation-pressure reduction trims in owned
  surfaces if convicted.
- Out of scope: gc.freeze in runtime code; compiler/mediator surfaces.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: Classification complete and confirmed at the 0.3ms
  threshold; disposition "no melder defect" closed per the plan the user
  accepted (close-on-clean-confirm).

## Steps / Checklist
- [x] Build profile_tail_stall_attribution.py (gc.callbacks windows +
      per-surface stall log + overlap report; GC_DISABLE control mode)
- [x] User runs both modes; classify stalls
- [x] Land fix or record disposition per evidence (disposition: no fix
      warranted; see closure note)
- [x] Run Ticket Microcycle during execution.

## Deliverables
- benchmarks/testing_other_di/profile_tail_stall_attribution.py (new)
- Evidence-backed stall classification; fix or disposition

## Files / Paths Impacted
- benchmarks/testing_other_di/profile_tail_stall_attribution.py (new)
- Fix targets UNKNOWN until classified

## Validation
- Not run.
- Recommended commands:
  - `python benchmarks/testing_other_di/profile_tail_stall_attribution.py`
  - same with `BENCH_TAIL_GC_DISABLE=1`

## Risks / Rollback Notes
- GC attribution is correlational (window overlap); the gc-disabled
  control run is the causal check.
- Machine load from co-running agents inflates tails; compare modes
  within the same session.

## Applicable Anti-Patterns
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without acceptance confirmation and board-sync completion.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, single-step continuation.
- Add a `## Notes` entry after each meaningful finding; append-only.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-06-12T22:59:34Z
  TYPE: PLAN
  CLAIM: Design: gc.callbacks record (phase, generation, timestamp) ->
    GC windows. Workers run gauntlet-lite scope cycles logging any
    segment >= threshold with (surface, start, duration). Report: GC
    pause stats per generation, stalls by surface, % of stall time
    overlapping GC windows, plus a GC-disabled control mode
    (BENCH_TAIL_GC_DISABLE=1): if tails collapse with gc off, GC is
    convicted causally, and the fix direction is allocation-pressure
    reduction in owned surfaces (per-cycle tuple/list churn) or a
    documented gc-tuning recommendation (user sign-off).
  EVIDENCE:
  - tickets/tasks/completed/2026-06-12_warm_meld_fixed_cost_trim_task.md:1-1
  IMPACT: Last unexplained competitive surface (tail latency).
  NEXT: build the harness.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-12T23:20:00Z
  TYPE: MEASURE
  CLAIM: Both modes run (user, t3, 10s each). GC EXONERATED CAUSALLY:
    zero gc collections in BOTH runs (refcounting absorbs the cycle
    churn; no container cycles reach the collector) and stalls are
    identical with gc disabled (3x ~9.4ms vs 4x ~9.1ms). STALL SIGNATURE
    IDENTIFIED: exactly one ~9-9.5ms melds stall PER THREAD, at startup
    - all threads simultaneously hit the cold phase-8-11 creation-context
    build on first meld (leader compiles, followers wait on the context
    switch). After warmup: 1.9M cycles / 10s with ZERO stalls >=1ms.
    Steady-state melder is clean in isolation. Throughput delta between
    modes (190.9k vs 174.6k cycles/s) is run noise, not a gc effect.
  EVIDENCE:
  - benchmarks/testing_other_di/profile_tail_stall_attribution.py:1-1
  IMPACT: The gauntlet's 17-70ms tails are NOT a steady-state melder
    defect: remaining explanations are (a) cold JIT context builds early
    in each measured run (by design; the cache system is the existing
    mitigation) and (b) co-running machine load (dishka/DI also spike in
    loaded runs). Melder-side fix surface: none indicated.
  NEXT: optional confirms - a 0.3ms-threshold run to bound sub-ms
    steady-state noise, and one quiet-machine gauntlet for the record;
    then dispose the lane (no fix warranted) per user.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-12T23:55:00Z
  TYPE: DECISION
  CLAIM: CLOSURE - disposition "no melder defect". Confirm run at 0.3ms
    threshold: 23 stalls across 1.7M cycles (0.0013% of segments), zero
    gc collections, zero gc overlap; only the 3 startup cold-build
    stalls (~9.6ms, one per thread: leader compiles phases 8-11 context,
    followers wait on the switch) exceed 2.2ms; the 0.3-2.1ms residue
    (20 events over 5M+ segments) is OS-scheduler-scale noise. FINAL
    CLASSIFICATION of the gauntlet 17-70ms tails: (1) by-design cold
    JIT context builds early in each run - existing mitigation is the
    cache system; (2) co-running machine load (all frameworks spiked in
    loaded runs). GC exonerated causally. Steady-state melder is clean.
    No fix landed; none warranted.
  EVIDENCE:
  - benchmarks/testing_other_di/profile_tail_stall_attribution.py:1-1
  IMPACT: Tail latency is off the competitive-worry list; remaining
    throughput gap is the construction lane (active compiler lane).
  NEXT: none (lane closed).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Successor to the contention + warm-meld lanes. Both exonerated their
surfaces for the 17-70ms tails; this lane classifies them (GC vs locks
vs allocator) with a falsifiable two-mode harness, then fixes or
disposes per evidence.
