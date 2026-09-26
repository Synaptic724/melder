

# Task: Measure what causes Melder's long-run gauntlet drop (retained state vs process effects)

## Metadata
- Task ID: TASK-2026-09-26-measure-melder-long-run-attribution
- Epic: EPIC-2026-09-26-melder-long-run-throughput-truth
- Status: in_progress
- Owner: user
- Agent Name: melder_1
- Priority: p1
- Created: 2026-09-26T00:34:00Z
- Updated: 2026-09-26T00:34:00Z

## Objective
Run the gauntlet's Melder cycle under controlled conditions in a CPython 3.14 free-threaded sandbox
copy of the current working tree, and attribute the long-run drop: retained objects/memory per cycle,
fresh-thread churn vs persistent threads, GC pause growth, and the effect of running after the other
two libraries in the same process.

## Ticket Contract
- ENTRY_GATE: Owner direction 2026-09-26 ("Make an epic and hunt down the truth"); board row routes here.
- EXECUTION_BOUNDARY: Sandbox copy of src/ and benchmarks/testing_other_di (snapshot taken
  2026-09-26T00:31Z); probe scripts and results under artifacts/melder_long_run_growth_20260926/.
  No src/ edits.
- DEPENDENCIES: T1 source reads (which structures to count); 3.14.0rc2 free-threaded sandbox.
- EXIT_GATE: Each measured cause recorded as MEASURE with method and caveats; attribution stated.
- FAILURE_ESCALATION: BLOCKER if the sandbox cannot run the gauntlet; DECISION_REQUEST if the
  verdict needs owner-machine runs.

## Scope Boundaries
- In scope: object counts, tracemalloc, gc callbacks, per-thread state counts, pool sizes, timing shape.
- Out of scope: absolute throughput claims for the owner's machine; src fixes.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Opened under the epic on owner direction 2026-09-26.

## Steps / Checklist
- [ ] Confirm the sandbox runs the Melder gauntlet lane on the snapshot.
- [ ] Measure retained objects per cycle under fresh-thread churn and under persistent threads.
- [ ] Measure GC collections/pauses over a long run and whether pauses grow with iterations.
- [ ] Measure Melder alone vs Melder after dependency-injector and dishka in one process.
- [ ] Record attribution and hand exact owner-run commands over.
- [ ] Run Ticket Microcycle during execution.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- MEASURE notes with method, interpreter, cores and caveats.
- Probe scripts and outputs under artifacts/melder_long_run_growth_20260926/.

## Files / Paths Impacted
- artifacts/melder_long_run_growth_20260926/ (new)

## Validation
- Sandbox runs are recorded as they happen; owner-machine runs: Not run.

## Risks / Rollback Notes
- 3.14.0rc2 on 2 cores differs from the owner's 3.14 on an i9-13900K; counts transfer, speed does not.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No behavior claim cited only to a document or a one-line search hit.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/melder_long_run_growth_20260926/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: owner acceptance of the epic verdict

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - Long-run attribution of Melder's gauntlet drop.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T00:34:00Z
  TYPE: FACT
  CLAIM: Sandbox ready: CPython 3.14.0rc2 free-threading build, 2 cores, 7 GB, with pytest 9.1.1,
    dishka 1.10.1, dependency-injector 4.49.1. Snapshot of src/, benchmarks/testing_other_di and
    pyproject.toml taken from the working tree at 2026-09-26T00:31Z (includes uncommitted slot-guard
    changes). The tarball was left at Claude outputs/melder_1_scratch/ in the repo (owner may delete).
  EVIDENCE: pyproject.toml:10-10
  IMPACT: Object-growth measurements can run now; timing is shape-only.
  NEXT: Run the Melder gauntlet lane on the snapshot to confirm it executes.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7
- DATETIME: 2026-09-26T00:40:00Z
  TYPE: MEASURE
  CLAIM: The gauntlet's real Melder lane (test_melder_gauntlet._build_runtime_melder driven by
    test_real_world_gauntlet._run_gauntlet_once, 3 fresh threads per iteration) runs on the sandbox
    snapshot: setup 1.98 s, 200 iterations in 0.89 s (~14.6k scope cycles/s on 2 cores, -X gil=0).
  EVIDENCE:
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1186-1285
  - benchmarks/testing_other_di/test_melder_gauntlet.py:72-305
  IMPACT: Growth probes can reuse the exact harness functions instead of a re-implementation.
  NEXT: Probe retained objects per iteration under fresh-thread churn vs persistent threads.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7
- DATETIME: 2026-09-26T00:52:00Z
  TYPE: MEASURE
  CLAIM: No retained growth in the gauntlet's Melder lane. Probe (warm 500 iterations, then gc.collect
    and a full gc.get_objects() type census every 2,000 iterations, 10,000 iterations = 650k scope
    cycles): fresh-thread churn (30k threads) GC-tracked objects 98,721 -> 97,226 (flat after 6k),
    sys.getallocatedblocks +314..+332 (flat), RSS flat; persistent 3 threads: objects 98,869 ->
    97,377, blocks +293..+310, RSS flat. Throughput per window flat in both modes (churn 13.8-14.0k
    cycles/s; persistent 30.7-32.3k cycles/s). Only probe-owned objects (Counter, list) grew.
  EVIDENCE:
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1186-1285
  - benchmarks/testing_other_di/test_melder_gauntlet.py:146-205
  IMPACT: A Melder memory leak is ruled out for this lane at the object and allocator level; the
    long-run drop must come from something that grows with iterations outside Melder. Separate
    finding: the same cycles run 2.3x faster on persistent threads than with 3 new threads per
    iteration, so thread churn dominates the harness cost on this box.
  NEXT: Run the full three-library harness long enough to see per-window drift, with the GC probe on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Opened 2026-09-26 under EPIC-2026-09-26-melder-long-run-throughput-truth. Resume from latest NEXT.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
