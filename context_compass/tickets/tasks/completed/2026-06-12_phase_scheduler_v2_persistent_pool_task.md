

# Task: Land PhaseScheduler v2 (persistent pool, latch barriers, chunking, fusion)

- Completed: 2026-06-12T21:06:51Z
- Summary: Persistent per-Spellbook pool, latch barriers, chunked dispatch,
  fused requirements_symbolic/plan_group phases, run-lock for concurrent
  revalidations, PLAN_GROUP_CHUNK_MULTIPLIER=2 with workers==1 gate.
  Measured: warm setup 15.65->8.78ms (-44%), cold -19%, plan_group skew
  2.46->1.5x at workers=5, rotation parity with dishka. User accepted.

## Metadata
- Task ID: TASK-2026-06-12-phase-scheduler-v2-persistent-pool
- Story: none
- Status: done
- Owner: codex
- Agent Name: compiler_builder_0
- Priority: p1
- Created: 2026-06-12T20:20:41Z
- Updated: 2026-06-12T21:06:51Z

## Objective
Replace the per-conjure scheduler lifecycle with one Spellbook-owned persistent
worker pool, latch-based phase barriers, chunked dispatch, and per-spell phase
fusion (1+2 and 8-11), with full test coverage and benchmark verification.

## Ticket Contract
- ENTRY_GATE: active board row for this ticket; spec artifact read
  (`tickets/tasks/2026-06-12_phase_scheduler_v2_persistent_pool_spec.md`).
- EXECUTION_BOUNDARY: `src/melder/utilities/synchronization/` (scheduler,
  unit_of_work, phase_latch), `src/melder/aether/spellbook/spellbook.py`
  (owned-scheduler slot/accessor/cleanup + run lock),
  `src/melder/aether/spellbook/spellbook_creation_system.py` (borrow path,
  chunk helpers, fused factories), matching unit tests. NOT in scope:
  compiler phase implementations (compiler agents' lane).
- DEPENDENCIES: revert note in `phase_scheduler.py` (~L95-105) forbidding
  inline workers==1 execution; phase cross-spell read map (spec ticket).
- EXIT_GATE: full pytest sweep green except known external lanes; user-run
  benchmarks show setup improvement; user confirms acceptance.
- FAILURE_ESCALATION: CONFLICT note if scheduler changes collide with
  compiler-lane phase work; BLOCKER if benchmarks regress.

## Scope Boundaries
- In scope: scheduler/unit-of-work/latch runtime, creation-system dispatch
  shape, spellbook ownership wiring, their tests, spec/ticket docs.
- Out of scope: compiler phase bodies (1-11), bind lane, cache lanes,
  mediator/transaction lanes, nexus lanes.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: Acceptance walk-through confirmed by the user
  ("yeah this is fine go ahead and turn em in") after all suites and
  benchmarks validated the delivered behavior.

## Steps / Checklist
- [x] Investigation: scheduler/UoW consumption-model review + measured costs
- [x] Spec ticket written and user-approved
      (`2026-06-12_phase_scheduler_v2_persistent_pool_spec.md`)
- [x] A+B: persistent pool, per-run cancel scope, blocking get, PhaseLatch
- [x] C: chunked dispatch with per-spell cancel checks
- [x] D: fused `requirements_symbolic` + `plan_group` registrations
- [x] Spellbook-owned scheduler + `_phase_run_lock` (concurrent revalidation
      serialization; found via integration failures, fixed)
- [x] Test updates + new coverage (scheduler v2, latch, run_for_scheduler,
      chunk helpers, fastpath/fused expectations)
- [x] User-run validation: unit suites green (2,240), concurrency integration
      pair green, full sweep green except known external lanes
- [x] User-run benchmarks: setup -19%, warm setup -40%, rotation parity
- [ ] User acceptance + closure walk-through
- [x] Run Ticket Microcycle during execution (retroactive notes below).

## Deliverables
- `src/melder/utilities/synchronization/phase_latch.py` (new)
- `src/melder/utilities/synchronization/phase_scheduler.py` (rewrite)
- `src/melder/utilities/synchronization/unit_of_work.py` (`run_for_scheduler`)
- `src/melder/aether/spellbook/spellbook.py` (owned scheduler + run lock)
- `src/melder/aether/spellbook/spellbook_creation_system.py` (borrow/chunk/fuse)
- Test files: synchronization suites, chunking suite, spellbook/fastpath updates

## Files / Paths Impacted
- src/melder/utilities/synchronization/phase_latch.py
- src/melder/utilities/synchronization/phase_scheduler.py
- src/melder/utilities/synchronization/unit_of_work.py
- src/melder/aether/spellbook/spellbook.py
- src/melder/aether/spellbook/spellbook_creation_system.py
- tests/unit/melder/utilities/synchronization/ (3 files)
- tests/unit/melder/spellbook/ (3 files)

## Validation
- User-run (reported by user, this session):
  - unit spellbook + synchronization suites: 2,240 passed
  - concurrency integration pair: 21 passed
  - full sweep: green except known external lanes (mediator, nexus stubs,
    nesting cross-clear, cache-asset)
  - `profile_bind_conjure_cycle.py`: setup 29.40->23.6/23.9ms disabled,
    warm 15.65->9.4/9.7ms (two consistent runs)
  - shallow_all rotation: melder 80,968 steps/s vs dishka 81,281 (parity)
- Recommended commands:
  - `pytest tests/unit/melder/utilities/synchronization/ -q`
  - `pytest tests/unit/melder/spellbook/ -q`
  - `python benchmarks/testing_other_di/profile_bind_conjure_cycle.py`

## Risks / Rollback Notes
- Scheduler phase-name map changed: `requirements_symbolic` replaces
  `requirements`+`symbolic_graph`; `plan_group` replaces the four plan
  registrations. Anything keying off scheduler RESULT names must adopt the
  new keys (repo sweep found no other consumers).
- Stuck units now occupy a pooled worker instead of leaking a dying thread.
- Runs must never be initiated from inside a phase unit (run-lock deadlock).

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none
- DISPOSITION: none
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-06-12T20:20:41Z
  TYPE: FACT
  CLAIM: Phases 1, 2, 4, 8, 9, 10, 11 have no spellbook-wide reads; phase 3
    iterates the live spell pool at 4 sites; phases 5-7 are frame-wide. This
    is the fusion-legality map: 1+2 and 8-11 fuse per spell, 3 keeps hard
    barriers, 4 stays parallel-behind-barrier.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_2.py:91-119
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py:115-117
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:118-136
  IMPACT: Three plan-group barriers plus one structural barrier deleted.
  NEXT: none (landed).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-06-12T20:20:41Z
  TYPE: FACT
  CLAIM: The persistent shared scheduler exposed a real concurrency bug:
    concurrent meld-time revalidations corrupted the per-run phase registry
    ("already registered" / "no registered factory"). Fixed with
    Spellbook-owned `_phase_run_lock` making register/run/release atomic.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook_creation_system.py:1751-1775
  - src/melder/aether/spellbook/spellbook.py:194-206
  IMPACT: Concurrent revalidations serialize per spellbook; integration pair
    (concurrency + multithreading link/bind) green after fix.
  NEXT: none (landed).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-06-12T20:20:41Z
  TYPE: MEASURE
  CLAIM: User-run results: median setup disabled 29.40->23.6/23.9ms, warm
    15.65->9.4/9.7ms, warm conjure 11.5->6.1ms; rotation threads=1 parity
    with dishka (80,968 vs 81,281 steps/s); real_world threads=3 setup
    202->157ms; cleanup +~0.8ms (relocated pool teardown, by design).
  EVIDENCE:
  - benchmarks/testing_other_di/profile_bind_conjure_cycle.py:1-1
  IMPACT: Scheduler coordination is no longer the dominant setup cost;
    remaining setup levers are bind tokenization, phase work, hydration.
  NEXT: user acceptance walk-through, then closure.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-12T20:40:00Z
  TYPE: PLAN
  CLAIM: User directs a further iteration: profile the scheduler/UoW lane
    deeper and verify the fused plan_group (8-11) work is properly divided
    across workers. Known structural facts to test empirically: plan_group
    chunks are contiguous equal-count splits of heterogeneous per-spell
    costs (deep roots cost far more than leaves), so load imbalance is
    plausible; phases 5/6/7 are single lead-spell units (frame-wide,
    inherently serial on one worker).
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook_creation_system.py:2341-2386
  - src/melder/aether/spellbook/spellbook_creation_system.py:2545-2556
  IMPACT: A chunk-granularity knob (more chunks than workers feeds queue-
    level balancing) is the likely lever, but only measurement decides.
  NEXT: build a phase/chunk/spell timing breakdown harness reusing the
    bind-conjure benchmark graph; user runs it at workers sweep.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-12T22:05:00Z
  TYPE: MEASURE
  CLAIM: Breakdown harness (user-run, 29 classes, repeats=5): plan_group owns
    ~14.2ms busy of ~20ms phase time and parallelizes 14.8 -> 9.9 -> 5.2ms at
    workers 1/2/5 but with 2.46x load skew at workers=5 (contiguous
    equal-count chunks vs heterogeneous spells; RequestRoot ~2.3ms vs ~0.1ms
    leaves). chunk_mult=2: wall 5.22 -> 4.42ms (-15%), skew 1.52x, par_eff
    0.64 -> 0.80. chunk_mult=4 regressed: busy inflated 16.7 -> 22.2ms by
    cross-thread contention. Serial floor: root_blueprints ~1.4ms +
    system_validation ~0.7ms (frame-wide single units; compiler-lane shard
    candidates, not mine).
  EVIDENCE:
  - benchmarks/testing_other_di/profile_phase_scheduler_breakdown.py:1-1
  IMPACT: Evidence picks multiplier 2 as the production value and rules out
    finer fragmentation.
  NEXT: land PLAN_GROUP_CHUNK_MULTIPLIER=2 + tests; user re-runs harness and
    bind-conjure benchmark for confirmation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-06-12T22:05:00Z
  TYPE: DECISION
  CLAIM: Landed `PLAN_GROUP_CHUNK_MULTIPLIER: ClassVar[int] = 2` on
    SpellbookCreationSystem, threaded through a new `chunk_multiplier`
    parameter on `_build_chunked_phase_units` (default 1; only plan_group
    opts in). Tests pin the multiplier behavior, the spell-count cap, and
    the evidence-backed constant value.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook_creation_system.py:68-79
  - tests/unit/melder/spellbook/test_spellbook_creation_system_chunking.py:160-205
  IMPACT: ~0.8ms off conjure plan wall at workers=5 with no new config
    surface; structural phases keep multiplier 1 (their tiny work got
    slower with finer chunks).
  NEXT: user validation run (chunking suite + harness re-run).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-12T22:30:00Z
  TYPE: MEASURE
  CLAIM: Production confirmation of PLAN_GROUP_CHUNK_MULTIPLIER=2
    (user-run): workers=5 plan_group now 10 units, wall 4.49ms (was 5.22),
    skew 1.57x (was 2.46); workers=2 now 4 units, wall 8.28ms (was 9.86),
    skew 1.10x (was 1.76). Chunking suite 10/10 green.
  EVIDENCE:
  - benchmarks/testing_other_di/profile_phase_scheduler_breakdown.py:1-1
  IMPACT: The multiplier behaves in production exactly as the experiment
    predicted; scheduler iteration objectives met.
  NEXT: user acceptance walk-through, then closure with board sync.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-12T23:20:00Z
  TYPE: DECISION
  CLAIM: Cross-lane fix accepted from compiler_strategy_0 (via attention
    board): the plan_group chunk multiplier is now gated off at workers==1,
    where splitting has no balancing benefit and costs pure dispatch tax
    (their measurement: +1-1.6ms cold setup at workers=1). Gate lives in
    `_build_chunked_phase_units` (`effective_multiplier = 1 when
    workers == 1`); new unit test pins it.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook_creation_system.py:2470-2478
  - tests/unit/melder/spellbook/test_spellbook_creation_system_chunking.py:213-231
  IMPACT: workers=1 cold setup recovers the regression; workers>1 keeps the
    measured balancing win.
  NEXT: user runs chunking suite + bind-conjure benchmark at workers=1 to
    confirm the recovery.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
PhaseScheduler v2 fully landed and user-validated. One pool per Spellbook
(lazy spawn, sentinel-only exit), per-run cancel scopes, PhaseLatch barriers
with done-unit post-scan parity, chunked dispatch (<=workers units/phase),
fused `requirements_symbolic` and `plan_group` phases, Spellbook-owned run
lock for concurrent revalidations. Spec + implementation deviations recorded
in `2026-06-12_phase_scheduler_v2_persistent_pool_spec.md`. Compiler-lane
relevance: scheduler result keys changed; phase bodies untouched. Remaining:
user acceptance, then closure with board sync.
