

# Task: Fix gauntlet sample storage and isolate the shared gauntlet's Melder lane

## Metadata
- Task ID: TASK-2026-09-26-fix-gauntlet-sample-storage-and-melder-lane-isolation
- Epic: EPIC-2026-09-26-melder-long-run-throughput-truth
- Status: review
- Owner: user
- Agent Name: melder_1
- Priority: p1
- Created: 2026-09-26T08:10:44Z
- Updated: 2026-09-26T08:27:30Z

## Objective
Stop the gauntlet harnesses from keeping worker-thread-allocated ints for a whole leg, and make the
shared real-world gauntlet build Melder from its own lane with a configuration that matches the
Melder-only gauntlet, so the two benchmarks are isolated in code but comparable in results.

## Ticket Contract
- ENTRY_GATE: Owner direction 2026-09-26 ("yeah fix everything"; "make sure the configurations
  match too when its run in the real world gauntlet, the melder gauntlet should be isolated, like I
  don't want to skew my results"). T2 DECISION_REQUEST option (a) accepted.
- EXECUTION_BOUNDARY: benchmarks/testing_other_di/ only: test_real_world_gauntlet.py,
  melder_gauntlet_support.py, test_melder_long_run_retention.py (and one new parity test if needed).
  No src/ edits. Reported metrics keep their meaning and values.
- DEPENDENCIES: TASK-2026-09-26-measure-melder-long-run-attribution (evidence and options).
- EXIT_GATE: Harness long runs flat in the sandbox; parity between the two Melder lanes enforced by a
  test; owner review.
- FAILURE_ESCALATION: DECISION_REQUEST if aligning configurations requires choosing between two
  owner-visible settings; BLOCKER if the sandbox cannot validate.

## Scope Boundaries
- In scope: sample storage in both harnesses; shared gauntlet Melder builder; config parity test.
- Out of scope: Melder runtime changes; DI/dishka lane definitions.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner approved the fixes on 2026-09-26.
- from_state: in_progress
- to_state: review
- transition_reason: Fix applied byte-identically to the sandbox-validated files; tests and long
  runs pass in the sandbox; owner-machine run pending.

## Steps / Checklist
- [x] Record the owner decision and the two lanes' configuration differences with evidence.
- [x] Store lane samples in array('q') in both harnesses (worker ints no longer outlive threads).
- [x] Shared gauntlet builds Melder from its own lane; configuration equal to the Melder-only lane.
- [x] Parity test: both builders produce the same Melder configuration and existence map.
- [x] Update test_melder_long_run_retention.py attribution modes for the fixed harness.
- [x] Validate in the sandbox (tests + long harness trend run); record MEASURE notes.
- [ ] Run Ticket Microcycle; document each meaningful finding before continuing.

## Deliverables
- Edited: test_real_world_gauntlet.py, melder_gauntlet_support.py, test_melder_long_run_retention.py.
- New: test_gauntlet_melder_lane_parity.py.
- Patch record: artifacts/melder_long_run_growth_20260926/patch_gauntlet_harness.py.

## Files / Paths Impacted
- benchmarks/testing_other_di/test_real_world_gauntlet.py
- benchmarks/testing_other_di/melder_gauntlet_support.py
- benchmarks/testing_other_di/test_melder_long_run_retention.py
- benchmarks/testing_other_di/test_gauntlet_melder_lane_parity.py (new)

## Validation
- Sandbox (3.14.0rc2 free-threaded): parity + retention files 7 passed, 1 skipped (opt-in);
  parity negative control (workers 3 in the Melder-only lane) failed with a readable diff;
  test_melder_gauntlet 500-iteration smoke run OK; fixed harness 40k runs flat (Notes).
- Device files hash-identical to the validated sandbox files; CRLF preserved.
- Owner machine: Not run. Commands (repo root):
  - python -X gil=0 -m pytest benchmarks/testing_other_di/test_gauntlet_melder_lane_parity.py -q
  - python -X gil=0 -m pytest benchmarks/testing_other_di/test_melder_long_run_retention.py -q -s

## Risks / Rollback Notes
- New numbers after the fix are not comparable to earlier long-run numbers (the earlier ones carried
  the harness penalty). Rollback: revert the three files.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No behavior claim cited only to a document or a one-line search hit.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - Gauntlet harness fairness on free-threaded CPython.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Keep notes append-only; promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T08:10:44Z
  TYPE: ALIGNMENT_CHECK
  CLAIM: Owner approved "fix everything" (T2 option (a): array('q') sample storage) and added: the
    shared gauntlet must run Melder with a configuration matching the Melder-only gauntlet, with the
    Melder-only gauntlet isolated so it cannot skew shared results.
  EVIDENCE:
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1149-1158
  - benchmarks/testing_other_di/test_melder_gauntlet.py:72-127
  IMPACT: Scope now includes the shared gauntlet's Melder builder and a parity guard.
  NEXT: Compare the two builders' configuration calls against Spellbook defaults.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-26T08:13:01Z
  TYPE: FACT
  CLAIM: The shared gauntlet's in-file Melder builder cannot run: it calls configure_aether_frame
    (which validates and freezes the Spellbook configuration) and then set_property("phase_scheduler_
    workers_per_spellbook", 3), which raises "Cannot modify configuration after it is frozen." That is
    why _build_ops("melder") borrows test_melder_gauntlet's builder. Differences between the two
    builders: workers 3 vs 1; configure_aether_frame(system_caching_enabled=True) vs no call (the
    frame default is already True, so only the early freeze differs); class graph from the shared
    module vs melder_gauntlet_support copies (constructor parameters identical, only __slots__ order
    differs). Existence per class is the same (roots unique_per_spell_space in both).
  EVIDENCE:
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:945-1146
  - benchmarks/testing_other_di/test_melder_gauntlet.py:72-127
  - src/melder/aether/spellbook/spellbook.py:6200-6387
  - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:115-125
  IMPACT: Isolation plus matched configuration means: repair the in-file builder with exactly the
    Melder-only lane's settings (workers=1, no configure_aether_frame), route _build_ops to it, and
    guard the match with a test that records both builders' setup calls. This keeps the owner's
    recorded Melder configuration, so no skew is introduced.
  NEXT: Implement array sample storage in both harnesses and the builder repair; validate in sandbox.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T08:19:22Z
  TYPE: DECISION
  CLAIM: Implementation shape (sandbox copy first, then byte-identical on the device via one patch
    script with exact-once anchors and CRLF preserved). Both harnesses: per-iteration samples stay
    plain lists (safe for concurrent worker appends when lanes share workers); the run-long
    accumulation and the combined lists become array('q') via new _new_lane_metric_storage /
    new_lane_metric_storage, so worker-created ints die with their iteration. Shared gauntlet:
    in-file Melder builder repaired to the Melder-only settings (workers=1, no configure_aether_frame)
    and _build_ops("melder") routed to it. New test_gauntlet_melder_lane_parity.py guards setup-call,
    spell, class-graph, per-variant meld and isolation parity. Retention test attribution modes are
    now discard / harness / worker_objects.
  EVIDENCE:
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:945-1200
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1545-1600
  - benchmarks/testing_other_di/melder_gauntlet_support.py:449-560
  IMPACT: Arrays alone in the worker path were avoided because the Melder-only harness shares lane
    storage across workers when threads > 3; list appends are the thread-safe choice there.
  NEXT: Sandbox validation (parity + retention tests, negative controls, 40k-iteration trend runs).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-26T08:27:30Z
  TYPE: MEASURE
  CLAIM: Fixed harness validated in the sandbox. _run_gauntlet_benchmark, 40k iterations, 8 trend
    windows, GC probe: Melder 23.5/23.8/22.9/21.4/22.2/21.4/21.9/23.0 s per 5k iterations, 14,945 hot
    scopes/s, 0 collections, cleanup 48.9 ms; dishka 18.4/17.2/17.0/16.8/16.4/17.2/16.6/17.1 s,
    19,827 hot scopes/s, 0 collections. Pre-fix storage fell to ~4.4k cycles/s for both over the same
    length. Tests: 7 passed + 1 opt-in skipped; parity negative control caught a workers=3 change.
    Device files are hash-identical to the validated files (9032128a, d36a87b7, 5d2a6fe3, e4f58f8b).
  EVIDENCE:
  - context_compass/artifacts/melder_long_run_growth_20260926/runs/runD_fixed_melder.log:1-12
  - context_compass/artifacts/melder_long_run_growth_20260926/runs/runD_fixed_dishka.log:1-12
  - benchmarks/testing_other_di/test_gauntlet_melder_lane_parity.py:1-40
  IMPACT: The shared and Melder-only gauntlets no longer penalize long runs, and their Melder setup is
    now guarded equal. Numbers taken before the fix are not comparable with numbers after it.
  NEXT: Owner runs both test files and a fresh gauntlet on his machine; review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T08:27:30Z
  TYPE: RISK
  CLAIM: Found incidentally, not changed (src out of scope): inspect.signature(Aether.get_conduit_by_name)
    raises NameError on 3.14 because its return annotation Conduit is imported only under
    TYPE_CHECKING and inspect evaluates annotations. Any tool that introspects public Melder
    signatures (IDEs, DI frameworks, docs generators) can hit this.
  EVIDENCE: src/melder/aether/aether.py:1842-1861
  IMPACT: Possible user-facing introspection failures across TYPE_CHECKING-annotated public APIs.
  NEXT: Owner decides whether to open a separate investigation ticket.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
Opened 2026-09-26T08:10:44Z; review since 08:27:30Z. Harness storage fixed in both harnesses, shared
Melder lane repaired and isolated, parity test added; sandbox-validated. Owner-machine run: Not run.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
