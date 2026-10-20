# Task: Make the FrameLink cleanup guard regression deterministic

- Completed: 2026-10-20T10:16:36Z
- Summary: Replaced the timed two-worker fixture with a deterministic real-cleanup acquisition
  boundary. Full local runtime: 14399 passed, zero failures or unhandled-worker warnings;
  400 repeated cases and both removed-guard controls verify the regression's detection.

## Metadata
- Task ID: TASK-2026-10-19-fix_frame_link_cleanup_guard_test
- Story: none (standalone owner-directed CI repair)
- Status: done
- Owner: Mark
- Agent Name: expert_1
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-20T02:16:03Z
- Updated: 2026-10-20T10:16:36Z

## Objective
Repair the reported FrameLink cleanup regression test so it deterministically detects a missing
inside-lock cleaned-state check and cannot leave a test worker hanging at process shutdown.

## Problem / Context / MRP
The owner reports one Windows free-threaded Python 3.14.3 failure in run 39354429351:
test_frame_link_cleanup_rechecks_cleaned_inside_lock. Its coordinated lock raises while waiting
one second for a second worker. The test then reads cleaned=False; a worker warning and a
shutdown join remain, and the CI tests job is cancelled. Merge-ready correctly refuses that
cancelled required job; the owner supplied its gate output too. The job reported 14398 passed,
28 skipped, 17 xfailed and 3 xpassed. These are reported results, not local qualification.

## Ticket Contract
- ENTRY_GATE: Retained expert_1 identity and synaptic_python_developer role; applicable guidance
  remains in context and the resumed source is rechecked. Own roster is active with a matching route.
- EXECUTION_BOUNDARY: test_frame_link_runtime_contracts.py, FrameLink.cleanup and its direct
  Cleanable contract; narrow test-map/extent updates, controlled reproductions, qualification
  and generated test bundles. Select exact changes from the diagnosis before implementation.
- DEPENDENCIES: Base e6b41f3220082ac604c42839d26bbca21336bf41. Preserve the owner's existing
  attention-board edit removing old muse_0 alerts. Prior repairs stay completed.
- EXIT_GATE: Reproduce the fixture's failure/shutdown mechanism in a bounded child process;
  a deterministic guard regression passes on production and fails for a removed guard;
  focused/repeated/full runtime checks pass, distinct author self-review and current asset
  checks are recorded, and closure/artifact state is synchronized.
- FAILURE_ESCALATION: Record actual source-custody collisions, required-check failures or access
  denials. Preserve the merge-ready gate and stop only the dependent scope on a genuine blocker.

## Scope Boundaries
- In scope: Diagnose and repair the supplied fixture failure and its inability to finish cleanly;
  preserve cleanup idempotence and meaningful detection of the inside-lock guard.
- Out of scope: CI gate changes, new dependencies, public API changes, unrelated runtime defects,
  commits, pushes, merges, hosted CI invocations, agents/subagents and remote execution.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: The complete repair meets its criteria after deterministic controls,
  focused/repeated/full qualification, input-integrity checks and distinct author self-review.

## Steps / Checklist
- [x] Verify the source contract and reproduce the fixture failure in a bounded process.
- [x] Record the minimal repair and its guard-detection oracle before editing.
- [x] Implement the deterministic stand-in and verify failing mutation controls.
- [x] Run focused, repeated and full runtime checks on the final candidate.
- [x] Perform distinct self-review, update the test map, close records and rebuild assets last.
- [x] Record meaningful findings before dependent work under the Ticket Microcycle.

## Deliverables
- A regression check that detects a missing cleanup guard without scheduler timing assumptions.
- Reproducible failure, mutation and qualification evidence with explicit limits.

## Files / Paths Impacted
- tests/unit/melder/aether/test_frame_link_runtime_contracts.py
- src/melder/nexus/rift/frame_link/frame_link.py (investigation; no change without a proven cause)
- context_compass/system_docs/tests_components.md and its index where the test extent/flow changes
- This task's Context Compass routing/evidence and affected generated test bundles

## Validation
- Affected module: 7 passed, with unhandled-thread warnings treated as errors.
- Repeated regression: 200 passed per GIL mode, 400 total; both background commands exited 0.
- Both removed-guard mutation controls produce the expected direct failure and exit normally.
- Bounded original-fixture control reproduced the failed assertion and stranded worker.
- Adjacent selection: 25 passed. Local Python 3.14.2 affected module: 7 passed.
- Candidate asset/bundle checks and document preservation/index checks pass.
- Full local Windows Python 3.14.7 runtime: 14399 passed, 28 skipped, 17 xfailed, 3 xpassed
  in 752.40 seconds. The driver exited 0 after verifying the GIL remained off.
- The repaired case executed and no PytestUnhandledThreadExceptionWarning appeared.
- All 1802 tracked input hashes and the base revision match the pre-run capture.
- Final delivery receipts: final_asset_check.log, final_bundle_check.log and
  final_verification.json in the linked evidence directory.
- Hosted Windows Python 3.14.3 and coverage: Not run.
- The separate coroutine-coro-never-awaited shutdown warning remains.

## Risks / Rollback Notes
- The old fixture can strand a non-daemon worker after __enter__ raises with its RLock held.
  Reproduce it only inside a child process with a parent-enforced timeout and complete cleanup.
- Raising a timeout alone does not establish reliable scheduling or guard detection.
- Avoid a stand-in that merely sets cleaned=True and then asserts that same value.
- Roll back only this task's changes and generated outputs if qualification fails.

## Applicable Anti-Patterns
- [x] No implementation from UNKNOWN or HYPOTHESIS without an evidence-backed decision.
- [x] No unhandled worker failures or unbounded test-process shutdown.
- [x] No weakened assertion, skipped test or relaxed required CI gate to get green results.
- [x] No closure before required checks, distinct self-review and board synchronization.

## Done Checklist
- [x] Steps and deliverables complete.
- [x] Source-backed cause and deterministic invalid controls recorded.
- [x] Validation and unavailable matrix cells recorded honestly.
- [x] Relevant documentation/extent and index current; prior claims preserved.
- [x] Acceptance and truthful self-review recorded.
- [x] Artifact disposition and closure route synchronized.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/frame_link_cleanup_guard_20261019/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Applied at closure: reports, controls and before-copies retained; nine verified
  task-owned temporary directories and one navigation reading cache removed (cleanup_receipt.json).

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: FrameLink cleanup guard and deterministic acquisition boundary
- IF_UNKNOWN: none

## Noting Behavior
- Tactical findings, exact evidence ranges and one concrete next action; preserve historical Notes.
- Keep one current resume view below rather than a separate tracker.

## Contribution Attribution
- Ticket/Work Author(s): expert_1, synaptic_python_developer; diagnosis, test repair,
  documentation and qualification of test SHA256
  25ea402517ea879a0ab76ed779c2a0bf898626528e5271eeb21fe6d88bdb9c72.
- Published By: local workspace files through Codex; no remote publication.
- Independent Review: none; expert_1 performed distinct author self-review, recorded below.

## Notes
- DATETIME: 2026-10-20T02:16:03Z
  AUTHOR: expert_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: FrameLink.cleanup already rechecks _cleaned inside its lock. The test lock acquires an
    RLock, then asserts a one-second Event wait in __enter__; an assertion there prevents
    __exit__ from releasing it. The final assertion checks only the flag the stand-in sets and
    does not explicitly propagate worker errors or require the workers to finish.
  EVIDENCE:
  - src/melder/nexus/rift/frame_link/frame_link.py:116-145
  - tests/unit/melder/aether/test_frame_link_runtime_contracts.py:142-176
  - src/melder/utilities/general_base/cleanable.py:26-44
  IMPACT: A test-only coordination defect is evidenced; production timeout/cleanup policy and
    merge-ready must remain intact. A bounded reproduction will distinguish the fixture's own
    failure/shutdown behavior before replacing the scheduling assumptions.
  NEXT: Capture the original test and reproduce a delayed worker without leaving a live child.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-20T02:19:22Z
  AUTHOR: expert_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The bounded control reproduced the original assertion and a live non-daemon cleanup
    worker at interpreter shutdown by delaying only that worker's target by 1.5 seconds. The
    parent timeout killed and joined its own child. Production cleanup was unchanged. Replace
    this fixture's two threads and Events with a synchronous lock-acquisition stand-in that
    completes an actual recursive cleanup once before the outer acquisition proceeds.
  EVIDENCE:
  - artifacts/frame_link_cleanup_guard_20261019/original_shutdown_control.log:1-3
  - artifacts/frame_link_cleanup_guard_20261019/original_shutdown_child.stderr.log:1-50
  - artifacts/frame_link_cleanup_guard_20261019/reproduce_original_shutdown.py:13-67
  - src/melder/nexus/rift/frame_link/frame_link.py:116-145
  IMPACT: The stand-in controls precisely the transition between the outer check and inside-lock
    recheck, uses the real cleanup body, and needs no scheduler wait or worker thread. Missing
    the inner guard must raise in the test thread when the outer call touches already-deleted
    fields; missing the outer guard must fail the final repeated cleanup. No runtime patch,
    source version change or CI gate change is needed.
  NEXT: Implement this test-only boundary stand-in and prove both removed-guard variants fail.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-20T02:21:03Z
  AUTHOR: expert_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: All seven affected-module tests pass with unhandled-thread warnings treated as errors.
    Removing either cleanup guard in separate transient processes makes the revised regression
    fail directly with AttributeError; both negative-control runners finish normally. The
    fixture invokes actual cleanup from a one-shot acquisition boundary instead of setting the
    cleaned flag itself, creating threads or waiting for scheduler progress.
  EVIDENCE:
  - artifacts/frame_link_cleanup_guard_20261019/focused.log:1-3
  - artifacts/frame_link_cleanup_guard_20261019/mutant_inner.log:1-80
  - artifacts/frame_link_cleanup_guard_20261019/mutant_outer.log:1-80
  - tests/unit/melder/aether/test_frame_link_runtime_contracts.py:145-191
  IMPACT: The missing-guard detection is now explicit and cannot be relegated to a worker warning.
    Update only the test map's relevant C2 claim, a focused call flow and its handoff; this file
    was not in the C1 core inventory, so no existing C1 extent or core count changes.
  NEXT: Run focused repetitions and adjacent runtime contracts, then qualify the full runtime.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-20T09:55:52Z
  AUTHOR: expert_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: After the owner resumed the interrupted turn, both earlier repeat commands completed
    with exit 0: 200 passes each, 400 total. The source base and full FrameLink implementation
    are unchanged; its hash remains 2164bb2822f89f7073c74d5b7f3ff26311ea18c8fb88e1697e2d55862b6d8e0f.
    The first adjacent command used a nonexistent filename and exited 4 with no tests run;
    resolve it to the existing test_frame_link_contract_profiles.py before counting validation.
  EVIDENCE:
  - artifacts/frame_link_cleanup_guard_20261019/repeat_gil0.log:1-5
  - artifacts/frame_link_cleanup_guard_20261019/repeat_gil1.log:1-20
  - artifacts/frame_link_cleanup_guard_20261019/adjacent_initial_selection.log:1-6
  - src/melder/nexus/rift/frame_link/frame_link.py:1-231
  IMPACT: Completed repeats are retained rather than restarted. The full source and current
    191-line test were read again. Correct one joined documentation evidence line, regenerate
    the index, then finish adjacent checks and qualify the full runtime on the final input hashes.
  NEXT: Run the corrected adjacent-file selection and verify the test-map index/preservation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-20T10:00:15Z
  AUTHOR: expert_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The corrected adjacent selection passes 25 tests and the affected module passes all
    seven tests on local Python 3.14.2. Candidate source-asset and LLM checks pass. The input
    verifier refused an off-by-one new documentation citation (146 rather than the actual
    function definition at 145); correct that citation and rebuild the index before capture.
  EVIDENCE:
  - artifacts/frame_link_cleanup_guard_20261019/adjacent.log:1-3
  - artifacts/frame_link_cleanup_guard_20261019/python3142.log:1-3
  - artifacts/frame_link_cleanup_guard_20261019/candidate_asset_check.log:1-4
  - artifacts/frame_link_cleanup_guard_20261019/candidate_bundle_check.log:1-4
  - tests/unit/melder/aether/test_frame_link_runtime_contracts.py:145-191
  IMPACT: No executable check failed; capture was correctly withheld until the new citation
    covered the complete function. Full-suite acceptance remains pending and will use a fresh
    aggregate over the final candidate, not the earlier repair's result.
  NEXT: Capture the corrected final inputs and run the complete local runtime driver.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-20T10:01:11Z
  AUTHOR: expert_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Distinct author self-review inspected the complete changed test, production cleanup,
    exact test/document diff and mutation failures. The one-shot trigger clears before recursive
    cleanup, so recursion is bounded; each acquired RLock is released by its context manager.
    The real cleanup retires state, and the outer call must return before reading deleted fields.
    Assertions also verify the cleaned-state access refusal and repeated cleanup. No production
    behavior or required CI gate changes; no material review concern remains in this candidate.
  EVIDENCE:
  - tests/unit/melder/aether/test_frame_link_runtime_contracts.py:145-191
  - src/melder/nexus/rift/frame_link/frame_link.py:116-145
  - artifacts/frame_link_cleanup_guard_20261019/qualification_inputs.json:1-22
  - artifacts/frame_link_cleanup_guard_20261019/documentation_verification.json:1-16
  IMPACT: Qualification is bound to test SHA256
    25ea402517ea879a0ab76ed779c2a0bf898626528e5271eeb21fe6d88bdb9c72 and the recorded aggregate
    over 1802 tracked inputs. Nine dependency pins match both the available 3.14.7 cell and the
    reported 3.14.3 cell. The index validates all 70 ranges; only the prior metadata timestamp
    is replaced in the document baseline, with all prior claims preserved. This is scoped
    verification of the changed entry/flow, not a new whole-document semantic certification.
  NEXT: Run the official full-runtime driver on this candidate and verify the inputs afterward.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-20T10:16:36Z
  AUTHOR: expert_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Accept and close the complete local repair after distinct author self-review. The
    official runtime driver passed 14399 tests with zero failures/errors and no unhandled-thread
    exception warning, then returned 0 with the GIL verified off before and after. The repaired
    test executed. All 1802 tracked input hashes and the source base remain unchanged.
  EVIDENCE:
  - artifacts/frame_link_cleanup_guard_20261019/verification_receipt.json:1-88
  - artifacts/frame_link_cleanup_guard_20261019/full_runtime_exit.json:1-4
  - artifacts/frame_link_cleanup_guard_20261019/documentation_verification.json:1-14
  - artifacts/frame_link_cleanup_guard_20261019/cleanup_receipt.json:1-16
  IMPACT: Every scoped criterion passes: bounded old-fixture/shutdown reproduction, meaningful
    guard detection with two negative controls, focused/adjacent/repeated/full checks, preserved
    documentation with a current index, and truthful author self-review. The prior bad adjacent
    filename and citation verification error were corrected and their history is recorded.
    Nine task-owned directories and one reading cache were removed after absolute-path and
    reparse-point checks. The owner's existing attention-board edits are preserved. Hosted
    Windows 3.14.3 and coverage remain unrun; the separate coroutine shutdown warning persists.
    Merge-ready was correctly refusing a cancelled required test job; it needs a successful
    hosted rerun after this repair is published, not a gate change.
  NEXT: Run the final asset/bundle rebuild and checks after closure, then return the verified result.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Completed test-only repair on base e6b41f3220082ac604c42839d26bbca21336bf41. The old fixture's
timed wait could fail with its RLock held and strand a non-daemon worker; a bounded child
reproduces that. The regression now completes an actual cleanup before the outer acquisition
and requires the outer call to recheck cleaned state, with no worker threads or timing deadline.
Both removed-guard variants fail directly. Full local Windows Python 3.14.7 GIL-off runtime:
14399 passed, zero failures/errors or unhandled-thread warnings. Seven module tests, 25 adjacent
tests, 400 repeats and all seven cases on Python 3.14.2 pass. Production and qualified inputs
stay unchanged; test-map content is preserved and its index is current. Final asset receipts
are linked above. Temporary outputs are removed and evidence retained. Hosted Windows 3.14.3,
coverage and the separate coroutine shutdown warning remain explicit limits. The hosted
merge-ready result awaits a successful CI rerun after publication; no active local work remains.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
