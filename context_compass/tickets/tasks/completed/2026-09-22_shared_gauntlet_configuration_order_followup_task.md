# Task: Recheck the shared DI gauntlet's configuration order

- Completed: 2026-10-24T21:57:09Z
- Summary: Obsolete: the shared gauntlet's Melder lane no longer calls configure_aether_frame before it sets
  phase_scheduler_workers_per_spellbook (f1cd22a22, 2026-09-26), and the lane-parity guard builds that lane - 5 passed
  with the GIL off and with it on at 3cf114b9d. Closed on the owner's word by melder_2
  (TASK-2026-10-24-ci_lane_loose_ends); nothing to repair.

## Metadata
- Task ID: TASK-2026-09-22-shared-gauntlet-configuration-order-followup
- Status: done
- Owner: unassigned
- Agent Name: melder_2
- Created: 2026-09-22T19:39:53Z
- Updated: 2026-10-24T21:57:09Z
- Disposition: closed as obsolete with evidence on 2026-10-24 (Notes); it was a backlog finding, implementation
  not selected

## Objective
Preserve the distinct shared-gauntlet setup failure found during the completed spell-ID selector
repair. Reproduce against current source before deciding whether a configuration-order edit is needed.

## Ticket Contract
- ENTRY_GATE: Owner selects this separate follow-up; reopen the retained failure and current adapter.
- EXECUTION_BOUNDARY: Shared benchmark setup and narrowly necessary example compatibility checks.
- DEPENDENCIES: Completed selector repair and its fresh-process setup-failure evidence.
- EXIT_GATE: Current failure is either repaired and verified or shown obsolete with evidence.
- FAILURE_ESCALATION: Keep runtime redesign and benchmark workload changes outside this repair.

## State Transition Event
- from_state: ready
- to_state: done
- transition_reason: shown obsolete with evidence, the exit gate's second branch (Notes, 2026-10-24); closed on the
  owner's word (chat 2026-10-24, 15:07 MDT: "yeah so get t hose loose ends fixed up") by melder_2 for
  TASK-2026-10-24-ci_lane_loose_ends.

## Scope / Known State
The 2026-09-20 run failed while setting the scheduler-worker configuration after
configure_aether_frame, before any Meld lookup. The 134 ID-selector replacements and standalone
gauntlet repair are complete. This later backlog entry does not claim the separate setup issue is fixed.
Current reproducibility is UNKNOWN; no new investigation or runtime execution was done during closure.

## Work
- [x] Read the retained isolated failure and current adapter setup.
- [ ] Reproduce the setup failure independently of selector resolution.
- [ ] Repair only if still present and qualify the benchmark's existing workload.

## Validation
2026-09-22: Not run in this follow-up. Prior evidence is retained below.
2026-10-24 (melder_2): `python -X gil=0 -m pytest benchmarks/testing_other_di/test_gauntlet_melder_lane_parity.py
-q -p no:cacheprovider` 5 passed (3.14.7t), and with `-X gil=1` 5 passed, at 3cf114b9d. Hosted CI: Not run.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS (deleted with the 2026-10-24 board cleanup; in git at 72b712179^):
  - artifacts/benchmark_spell_id_repair_20260919/validation.md
  - artifacts/benchmark_spell_id_repair_20260919/shared_gauntlet_isolated.log
- DISPOSITION: retain_as_reference (no artifact left on disk to dispose at closure)

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false

## Notes
- DATETIME: 2026-09-22T19:39:53Z
  TYPE: DECISION
  CLAIM: Owner asks to turn in completed recent work. Preserve this out-of-scope finding as a
    separate backlog task rather than leaving the completed selector repair open indefinitely.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-19_repair_benchmark_spell_id_lookup_task.md
  - artifacts/benchmark_spell_id_repair_20260919/shared_gauntlet_isolated.log:1-8
  IMPACT: Completed selector work can close without losing the unresolved setup finding.
  NEXT: Reproduce only when the owner selects this follow-up.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-24T21:57:09Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Obsolete. The retained failure (validation.md lines 43-49 of the 2026-09-19 lane, deleted with its
    artifacts in the 2026-10-24 cleanup, kept in git at 72b712179^) was the shared gauntlet's Melder adapter calling
    configure_aether_frame, which freezes the configuration, before it set phase_scheduler_workers_per_spellbook
    ("Cannot modify configuration after it is frozen."). Since f1cd22a22 (2026-09-26) `_build_runtime_melder` sets
    the property on a fresh configuration with no frame call before it, and test_gauntlet_melder_lane_parity.py
    builds that lane with the Melder-only builder refused: 5 passed with the GIL off and 5 with it on at 3cf114b9d
    (3.14.7t). The failure was not re-run as it was: its cause is gone from the adapter.
  EVIDENCE:
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1066-1106
  - benchmarks/testing_other_di/test_gauntlet_melder_lane_parity.py:429-451
  IMPACT: The exit gate's second branch holds (shown obsolete with evidence); nothing to repair, no benchmark
    workload touched.
  NEXT: None (closed).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
DONE 2026-10-24T21:57:09Z: obsolete - the setup order was fixed in f1cd22a22 and the lane-parity guard passes in
both GIL modes (Notes). Closed on the owner's word by melder_2; nothing remains.
