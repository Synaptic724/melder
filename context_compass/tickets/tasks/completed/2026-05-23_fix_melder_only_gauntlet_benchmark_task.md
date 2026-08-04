# Task: Fix Melder-only gauntlet benchmark

## Metadata
- Task ID: TASK-2026-05-23-fix-melder-only-gauntlet-benchmark
- Story: none
- Status: done
- Owner: codex
- Agent Name: mutres_0
- Priority: p1
- Created: 2026-05-23T20:16:41Z
- Updated: 2026-06-01T11:05:49Z

## Objective
Remake `test_melder_gauntlet.py` as a dedicated Melder-only benchmark that
follows the proven `test_real_world_gauntlet.py` workload model without
carrying a second drift-prone full benchmark copy.

## Ticket Contract
- ENTRY_GATE: the user explicitly asked for a Melder-only version of the real
  world gauntlet and identified the current `test_melder_gauntlet.py` as
  stalled/useless.
- EXECUTION_BOUNDARY:
  - `benchmarks/testing_other_di/test_real_world_gauntlet.py`
  - `benchmarks/testing_other_di/test_melder_gauntlet.py`
  - `benchmarks/testing_other_di/test_melder_gauntlet_cprofile.py`
  - `benchmarks/testing_other_di/melder_gauntlet_cprofile_runner.py`
  - `benchmarks/testing_other_di/melder_gauntlet_support.py`
  - `codex/context_compass/attention_board.md`
  - this task ticket
- DEPENDENCIES:
  - `tickets/tasks/2026-05-23_run_real_world_gauntlet_benchmark_and_cprofile_task.md`
- EXIT_GATE: the Melder-only benchmark is a dedicated Melder-only entrypoint
  aligned to the real-world gauntlet's workload semantics, low-iteration
  validation completes, and the file no longer carries a second large drifted
  benchmark implementation.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the real-world Melder path
  itself reproduces the stall and the fix therefore requires runtime changes
  instead of benchmark-file cleanup.

## Scope Boundaries
- In scope:
  - benchmark drift analysis between the shared and Melder-only files
  - reproducing the current Melder-only runner with bounded env overrides
  - remaking the Melder-only file so it follows the shared workload model
    without remaining a second large stale copy
  - fixing the Melder-only cProfile wrapper/runner to the new standalone
    benchmark API
  - focused benchmark validation
- Out of scope:
  - runtime performance fixes in `src/`
  - cProfile analysis
  - changes to the cross-library shared benchmark semantics

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a benchmark-file fix and a
  Melder-only real-world gauntlet variant.

## Steps / Checklist
- [ ] Compare the shared gauntlet and Melder-only file to identify drift.
- [ ] Reproduce the current Melder-only behavior with bounded env overrides.
- [ ] Remake the Melder-only benchmark around the proven real-world workload
      model without leaving a second large drifted implementation in place.
- [ ] Run focused validation on the Melder-only benchmark.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- one evidence-backed diagnosis of the Melder-only benchmark drift/stall
- one dedicated Melder-only benchmark file aligned to the shared workload model
- one working Melder-only cProfile wrapper/runner pair aligned to that file
- one focused validation result

## Files / Paths Impacted
- `codex/context_compass/tickets/tasks/2026-05-23_fix_melder_only_gauntlet_benchmark_task.md`
- `codex/context_compass/attention_board.md`
- `benchmarks/testing_other_di/test_melder_gauntlet.py`
- `benchmarks/testing_other_di/test_melder_gauntlet_cprofile.py`
- `benchmarks/testing_other_di/melder_gauntlet_cprofile_runner.py`
- `benchmarks/testing_other_di/melder_gauntlet_support.py`
- `benchmarks/testing_other_di/test_real_world_gauntlet.py` (read-only unless a
  small shared export seam is required)

## Validation
- Not run.
- Recommended commands:
  - `.\.venv_new\Scripts\python.exe -m pytest -q -s benchmarks\testing_other_di\test_melder_gauntlet.py`

## Risks / Rollback Notes
- Risk: the separate benchmark file may be exposing a real Melder runtime
  concurrency stall that the shared three-library run masks with different
  environment settings or execution order.
- Rollback: if the shared Melder path reproduces the same stall under the same
  bounded settings, stop after diagnosis and raise the runtime boundary to the
  user instead of pretending a wrapper fix solves it.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No widening into runtime performance fixes without first proving the
      benchmark file itself is not the problem.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: ticket closure

## Noting Behavior
- Note focus: benchmark drift, stall evidence, and one-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-06-01T11:05:49Z
  TYPE: DECISION
  CLAIM: The user explicitly accepted this lane as complete and requested that
    it be turned in and moved out of active routing.
  EVIDENCE:
  - user_instruction
  IMPACT: This ticket is now closed and should no longer appear in active
    board routing.
  NEXT: none
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-23T20:16:41Z
  TYPE: PLAN
  CLAIM: The current ask is a benchmark-file repair, not a runtime performance
    redesign. The file still needs a bounded reproduce/compare pass first so
    we do not handwave the stall, but the end goal is a proper Melder-only
    benchmark aligned to the real-world workload, not another stale fork and
    not a superficial one-line wrapper.
  EVIDENCE:
  - user_instruction
  IMPACT: The next step is to compare the two files and run the current
    Melder-only benchmark with tiny env overrides before touching the file.
  NEXT: reproduce the current Melder-only runner and record whether it stalls
    under bounded iteration/thread counts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-23T20:20:00Z
  TYPE: FACT
  CLAIM: The immediate defect is drift, not total non-functionality. Under
    bounded settings (`1` iteration, `1` thread, `10` request scopes), both
    the current `test_melder_gauntlet.py` and the Melder leg inside
    `test_real_world_gauntlet.py` complete and print results. The real problem
    is that `test_melder_gauntlet.py` is still a separate large implementation
    with its own env surface and runner body, so it can diverge from the
    shared real-world benchmark independently.
  EVIDENCE:
  - benchmarks/testing_other_di/test_melder_gauntlet.py:395-410
  - benchmarks/testing_other_di/test_melder_gauntlet.py:512-897
  - benchmarks/testing_other_di/test_melder_gauntlet.py:1105-1118
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:425-440
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:916-1311
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1520-1539
  - validation_result: `MELDER_GAUNTLET_ITERS=1 MELDER_GAUNTLET_THREADS=1 MELDER_GAUNTLET_REQUEST_SCOPES=10 .\\.venv_new\\Scripts\\python.exe -m pytest -q -s benchmarks\\testing_other_di\\test_melder_gauntlet.py`
  - validation_result: `DI_GAUNTLET_ITERS=1 DI_GAUNTLET_THREADS=1 DI_GAUNTLET_REQUEST_SCOPES=10 .\\.venv_new\\Scripts\\python.exe -m pytest -q -s benchmarks\\testing_other_di\\test_real_world_gauntlet.py -k melder`
  IMPACT: The repair should focus on removing the second large drift surface
    while keeping a dedicated Melder-only entrypoint.
  NEXT: remake `test_melder_gauntlet.py` so it follows the real-world gauntlet
    workload model with only the Melder runtime path and Melder-specific env
    handling.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-23T20:20:00Z
  TYPE: DECISION
  CLAIM: A thin wrapper over `_run_gauntlet_benchmark("melder", ...)` is the
    wrong cut for this ask. The file should stay as a dedicated Melder-only
    benchmark entrypoint, but it should stop carrying a second full benchmark
    implementation. The correct remake is to align it to the shared workload
    model and helper surfaces while keeping its own Melder-only entry surface.
  EVIDENCE:
  - user_instruction
  - benchmarks/testing_other_di/test_melder_gauntlet.py:1-1118
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1-1539
  IMPACT: The next edit should rebuild the file around the shared workload
    model instead of either leaving the drifted copy or collapsing it to a
    trivial one-line shim.
  NEXT: patch `test_melder_gauntlet.py` into a real Melder-only benchmark with
    shared workload semantics and focused validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-23T20:28:00Z
  TYPE: FACT
  CLAIM: The remake is now in place. `test_melder_gauntlet.py` is no longer a
    second giant fork of the benchmark. It now owns only the Melder-specific
    env surface, Melder runtime construction, and the Melder-only benchmark
    entrypoint, while it reuses the shared real-world workload model and
    generic per-iteration harness from `test_real_world_gauntlet.py`.
  EVIDENCE:
  - benchmarks/testing_other_di/test_melder_gauntlet.py:1-423
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:35-440
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:916-1311
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1520-1539
  IMPACT: The Melder-only benchmark now stays aligned to the real-world
    workload without carrying a second full benchmark body that can silently
    drift into a different or broken test.
  NEXT: run focused validation on the remade Melder-only benchmark.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-23T20:52:00Z
  TYPE: MEASURE
  CLAIM: The remade benchmark is now validated at a realistic threaded shape
    after the runtime deadlock fix. The dedicated Melder-only file completes
    cleanly at `1` iteration, `3` threads, `10` request scopes, `5` worker-A
    jobs, and `5` worker-B jobs, which is the exact shape that previously sat
    hung until interrupted.
  EVIDENCE:
  - benchmarks/testing_other_di/test_melder_gauntlet.py:1-491
  - src/melder/aether/aetheric_frame/dev_ops/devops_identity.py:106-151
  - validation_result: `MELDER_GAUNTLET_ITERS=1 MELDER_GAUNTLET_THREADS=3 MELDER_GAUNTLET_REQUEST_SCOPES=10 MELDER_GAUNTLET_WORKER_A_JOBS=5 MELDER_GAUNTLET_WORKER_B_JOBS=5 .\\.venv_new\\Scripts\\python.exe -m pytest -q -s benchmarks\\testing_other_di\\test_melder_gauntlet.py`
  IMPACT: The file remake is now proven against the threaded shape that was
    failing in practice, not just against a trivial single-thread smoke run.
  NEXT: present the file remake plus the runtime deadlock fix together so the
    user can decide whether to push validation harder or close the lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-23T20:58:00Z
  TYPE: FACT
  CLAIM: The benchmark-file remake is still not clean enough for the user's
    ask. Even after the runtime deadlock fix, `test_melder_gauntlet.py` still
    imports `test_real_world_gauntlet` directly and still accepts
    `DI_GAUNTLET_*` fallback env names. That means the file is still coupled to
    the cross-library benchmark module and still carries leftover non-Melder
    benchmark surface area.
  EVIDENCE:
  - benchmarks/testing_other_di/test_melder_gauntlet.py:31-31
  - benchmarks/testing_other_di/test_melder_gauntlet.py:54-93
  - source_scan: `rg -n "DI_GAUNTLET|test_real_world_gauntlet|_shared\\." benchmarks/testing_other_di/test_melder_gauntlet.py`
  IMPACT: The next edit is not optional polish. The file needs one more pass to
    become a true standalone Melder-only benchmark with no shared benchmark
    import and no dependency-injector/dishka env leftovers.
  NEXT: extract the neutral workload/harness pieces into a Melder-only support
    module or inline them locally, then remove all `_shared` and
    `DI_GAUNTLET_*` references from `test_melder_gauntlet.py`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-23T21:05:00Z
  TYPE: FACT
  CLAIM: The file is now clean on the specific boundary the user asked for.
    `test_melder_gauntlet.py` no longer imports `test_real_world_gauntlet`,
    no longer references `_shared`, and no longer accepts `DI_GAUNTLET_*`,
    `dishka`, or `dependency-injector` benchmark surface area. The remaining
    issue after that cleanup was only a local bootstrap regression: the file
    needed `src/` back on `sys.path` so `melder` could import in standalone
    mode.
  EVIDENCE:
  - benchmarks/testing_other_di/test_melder_gauntlet.py:1-313
  - benchmarks/testing_other_di/melder_gauntlet_support.py:1-623
  - validation_result: `rg -n "DI_GAUNTLET|dependency-injector|dishka|test_real_world_gauntlet|_shared\\." benchmarks/testing_other_di/test_melder_gauntlet.py benchmarks/testing_other_di/melder_gauntlet_support.py` -> no matches
  IMPACT: The benchmark file is now structurally standalone and Melder-only.
    The next step is just the focused gauntlet rerun after restoring the `src/`
    bootstrap path.
  NEXT: rerun the 3-thread / 5-job Melder-only gauntlet and capture the
    post-cleanup validation result.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-23T21:09:47Z
  TYPE: FACT
  CLAIM: The Melder-only cProfile path drifted too. The runner and pytest
    wrapper were still shaped around the old benchmark API and old execution
    assumptions. The concrete failures are:
    - the runner was still expecting deleted benchmark helpers from the old
      file shape
    - the pytest wrapper was still launching the subprocess without `gil=1`
      even though the user explicitly wants cProfile through the GIL-enabled
      path
  EVIDENCE:
  - benchmarks/testing_other_di/melder_gauntlet_cprofile_runner.py:128-165
  - benchmarks/testing_other_di/test_melder_gauntlet_cprofile.py:33-58
  - user_instruction
  IMPACT: The next edit is straightforward and bounded: align the runner to
    the current standalone benchmark API and make the wrapper launch the child
    with `-X gil=1`.
  NEXT: patch the two cProfile files, then validate the cProfile runner with
    low profile iteration counts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-23T21:12:00Z
  TYPE: MEASURE
  CLAIM: The Melder-only cProfile path is now working again on the bounded
    `gil=1` path. The pytest wrapper now launches the standalone runner with
    `-X gil=1`, the runner uses the current standalone Melder benchmark API,
    and a low-iteration validation run completes cleanly with `.prof` output
    written plus printed pstats blocks.
  EVIDENCE:
  - benchmarks/testing_other_di/test_melder_gauntlet_cprofile.py:33-58
  - benchmarks/testing_other_di/melder_gauntlet_cprofile_runner.py:128-170
  - validation_result: `MELDER_GAUNTLET_PROFILE_ITERS=1 MELDER_GAUNTLET_PROFILE_TOP=10 MELDER_GAUNTLET_ITERS=1 MELDER_GAUNTLET_THREADS=1 MELDER_GAUNTLET_REQUEST_SCOPES=10 MELDER_GAUNTLET_WORKER_A_JOBS=1 MELDER_GAUNTLET_WORKER_B_JOBS=1 .\\.venv_new\\Scripts\\python.exe -m pytest -q -s benchmarks\\testing_other_di\\test_melder_gauntlet_cprofile.py`
  IMPACT: The Melder-only benchmark lane now has both the standalone timing
    benchmark and the standalone cProfile wrapper/runner working against the
    cleaned Melder-only benchmark surface.
  NEXT: surface the final benchmark/cProfile repair state to the user and let
    them decide whether to push the profiled workload harder than this bounded
    validation shape.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the benchmark-file fix for `test_melder_gauntlet.py`. The goal
is to remake it as a dedicated Melder-only benchmark aligned to the shared
real-world workload instead of leaving a second large drifted copy in place.

