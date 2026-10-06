# Task: Run the real-world gauntlet in Melder CI with arbitrary thread counts

## Metadata
- Task ID: TASK-2026-10-03-real_world_gauntlet_ci
- Status: done
- Owner: codex
- Agent Name: command_0
- Created: 2026-10-03T14:14:45Z

- Completed: 2026-10-03T19:01:36Z
- Summary: Delivered 2026-10-03 (command_0): the real-world gauntlet runs in Melder CI on validated
  dev-to-preprod PRs (other routes skip; the manual run stays), the benchmark forces GIL-off in the measured
  child and takes arbitrary thread counts and an editable iteration list, printing both lists at startup; 279
  CI policy cases and 71 benchmark contracts green; bundles regenerated with --check OK; no src change. The
  hosted three-OS matrix remains for the owner. Closed by owner directive 2026-10-03.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: (2026-10-03T19:01:36Z) owner directive in chat, 2026-10-03: every active ticket in review
  is done; turned in by fable_1 under TASK-2026-10-03-turn-in-review-tickets.

## Objective and authority
Owner explicitly requests adapting Downloads/real-world-gauntlet.yml into Melder CI on feature
pull requests into dev, including codex_features2. Owner waived Melder onboarding for this task.
After a brief cancellation, owner resumed and expanded the task: the benchmark Python code must
force GIL-off in the process that measures the workload and support arbitrary positive thread counts.

## Contract and boundary
Work only in melder_private: the supplied workflow adaptation, ci.yml, ci_policy.py, directly
related CI tests and branch guide; the existing real-world benchmark and child runner, their focused
contracts, and required repository bundles. No Melder runtime implementation, package installs,
publishing, pushes, PR creation or changes to MelderOps. Preserve unrelated staged deletions.
Existing full-CI routes gain the gauntlet; lightweight promotions retain their current selection.
Keep one isolated process per library/round and comparable existing 1-3-thread behavior.

## Initial workload question (resolved below)
Optional owner clarification asks whether extra threads alternate worker A/B behind one request
thread, or repeat the request/A/B trio. Recommended assumption: one request thread, then alternating
A/B workers with independent per-thread metrics. Preserve existing defaults until clarified.

## Acceptance
- GIL-off is requested and verified in the actual measured child process.
- Positive N is supported; barriers, seeds, per-lane counters and throughput include every thread.
- Existing 1-3-thread work distribution stays compatible.
- CI runs on the existing full PR/manual profile, requires success and returns per-OS summaries,
  JUnit/log/provenance artifacts. Python setup helpers do not inherit PYTHON_GIL=0.
- Focused CI/benchmark contracts and small real runs pass; no unperformed hosted matrix is claimed.

## Evidence and notes
- CI routes: .github/workflows/ci.yml and .github/scripts/ci_policy.py.
- Supplied workflow: C:/Users/Mark/Downloads/real-world-gauntlet.yml, 179 lines.
- Benchmark before: 08CFC9C02384E9A204BF5E992D5C82E371CD75AFB08E316C02051E7A70392CC7.
- Runner before: BC008FB77BA8FDE065FECB26DC6580A97E4852086F55F53DC906738BD59A387F.
- Existing wrapper isolates each library in a subprocess with conditional -X gil=0. Configuration
  currently refuses more than 3 threads, and lane allocation/reporting has three fixed entries.
- NEXT: finish the actual workload/metrics trace, record thread expansion choice, then implement.

## Artifacts
- artifacts/2026-10-03_real_world_gauntlet_ci/; retain_as_reference.
- CONTEXT_MANAGEMENT_REQUIRED: false.

## Workload decision and implementation
Owner selected repetition of the full request/A/B workload cycle, with C, D, E, F, G
and onward as distinct additional thread lanes. No producer/consumer queue is added.
Every lane owns its metrics and counter slots; the existing readiness/start/join pattern
is preserved. The launcher now forces child PYTHON_GIL=0 and -X gil=0; the measured
entry point checks GIL state before setup, after imports and after measurement.
The owner additionally requests an editable [3,5,7,9] thread-count list in the
benchmark configuration section. The wrapper executes each library/count/round in
its own child and separates summaries and per-turn CSV by thread count.
Next: add focused N-thread/GIL contracts, then wire the workflow and validate.

## CI and easy pytest configuration
The top-of-file block now exposes iterations, the [3,5,7,9] list and rounds.
Workflow full-CI wiring is implemented with the existing route, merge gate and
source-qualification contract. Manual input can override the list; default CI
uses the file configuration. Logs validate every library/count/round, with no-GIL
provenance and artifacts. First benchmark selection passed 33 tests before these
three scalar default knobs were exposed; final focused validation is next.

## Validation checkpoint
- Combined focused.xml: 460 passing cases, no failures/errors/skips. This contains 427 CI cases
  and the then-current 33 benchmark contracts.
- Final benchmark_final.xml: 34 passing cases after exposing the editable defaults and improving
  the child-environment contract. CI files are unchanged from their passing run.
- The workflow's actual pytest/report Python step also ran locally with only output-path redirection,
  iterations=2, counts=[3,5,7,9], rounds=1. All three libraries verified, exit 0; summaries, full log,
  outcome.json and JUnit are saved in workflow_results/. This is a Windows correctness smoke,
  not a hosted three-OS run or a performance ranking.
- No runtime source under src/ changed. Required repository bundles are the remaining generated step;
  stage only the two new workflow/benchmark test files so the tracked-input builder can include them.

## Delivery
Implemented and verified: 427 CI contract cases and 34 final benchmark
cases pass, with zero errors/skips. The real workflow report step passes its 2-iteration Windows
smoke for all three libraries across 3/5/7/9 threads. Required repository bundles are regenerated
and --check reports OK for src/tests/other. delivery.json records final hashes.

Run test_real_world_gauntlet through pytest normally. Edit the three top-of-file settings:
REAL_WORLD_GAUNTLET_ITERATIONS, REAL_WORLD_GAUNTLET_THREAD_COUNTS and REAL_WORLD_GAUNTLET_ROUNDS.
Fresh no-GIL child processes are automatic for every library/count/round. CI uses the same file
defaults and publishes summaries/artifacts on the existing full PR/manual route.

No hosted matrix, commit, push or publication was performed. Only the two newly created workflow
and benchmark-contract files were staged for the tracked-input bundle builder; unrelated staged
deletions were preserved. No src runtime file or package version changed. Await owner acceptance.

## Iteration relay extension
Owner adds editable iteration counts [5000,10000,15000,25000,50000]. Every Cartesian
iteration/thread/library/round combination gets a fresh child. Payload checks, medians,
CSV and CI validation now include both dimensions. The larger default is 60 child runs
per round/OS; existing execution ceilings extend to six hours, with upload headroom.
Next: validate the expanded relay at small counts, then regenerate repository bundles.

## Startup configuration output
Owner requests the selected thread list and iteration list at the top of the run.
The pytest wrapper now flushes both effective lists before starting any benchmark child;
environment overrides are reflected. CI summaries preserve these two header lines.
Iteration relay validation before this output edit: 71 passed, 4 subprocess cases deselected;
required source/test/other bundles passed --check. Full benchmark remains for the owner to run.

## Final iteration-list and startup-output handoff
Both owner-requested startup lists are implemented. Defaults and explicit overrides were
verified at the first child launch boundary without running benchmark children; workflow
embedded Python compiles. startup_output.txt records the observed headers.
Latest focused run: startup_contracts.xml, 71 passed, 4 real-subprocess cases deselected.
Earlier 427-case CI and 34-case benchmark checkpoints predate the iteration-list extension;
the earlier real smoke covered one iteration count across four thread counts. The new full
iteration/thread matrix has not been executed by this agent; the owner will run it.
The editable settings are REAL_WORLD_GAUNTLET_ITERATION_COUNTS,
REAL_WORLD_GAUNTLET_THREAD_COUNTS, and REAL_WORLD_GAUNTLET_ROUNDS.
Owner confirmed there is no second requested change. No commit or push performed.
Final repository bundles regenerated; --check reports OK for src/tests/other.
Final git diff --check passes; delivery.json contains current file hashes and separated historical results.

## Owner revision: promotion-only CI budget
Automatically run the gauntlet only for validated dev-to-preprod PRs. Require its success
there and accept intentional skips on other CI routes. Keep the standalone manual gauntlet
for one-off checks. YAML iteration input defaults become [500,1000,2500,5000,10000];
local benchmark defaults and thread counts remain unchanged. Update route flags, merge
checks, source qualification consumers, workflow contracts and branch documentation together.

## Promotion-only delivery
Implemented the validated dev-to-preprod-only gauntlet requirement through the branch
outputs, workflow condition, final merge gate and source-proof producer. Other CI routes
accept an intentional skip; a failed/cancelled run is never accepted. Manual gauntlet remains
available. Both workflow input defaults select [500,1000,2500,5000,10000].
Validation: 279 CI policy/workflow/source-qualification cases passed, zero failures/errors/skips
(promotion_contracts.xml). Required bundles regenerated and --check passed for src/tests/other;
git diff --check passed. The local benchmark file SHA is unchanged from the prior delivery.
No hosted run, commit, push or publication performed. delivery.json contains current evidence
and file hashes; the first hosted promotion run remains to be observed after these edits land.
