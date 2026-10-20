# Task: Make the queue deadline regression reliable across wakeups

- Completed: 2026-10-20T00:39:01Z
- Summary: Replaced the scheduling-sensitive elapsed-time assertion with two controlled-clock
  deadline cases. Full local runtime: 14399 passed, zero failures; 400 repeated cases and three
  mutation controls verify the oracle. Test-map extent and generated test bundles are current.

## Metadata
- Task ID: TASK-2026-10-19-fix_queue_deadline_wakeup_test
- Story: none (standalone owner-directed CI repair)
- Status: done
- Owner: Mark
- Agent Name: expert_1
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-20T00:07:04Z
- Updated: 2026-10-20T00:39:01Z

## Objective
Diagnose and repair the reported queue-deadline failure while preserving the contract that
wakeups without available capacity never restart a caller's timeout.

## Problem / Context / MRP
The owner supplied one macOS Python 3.14.3 failure from run 39343965856. The waiter raised
ManagedSpellExhaustedError as expected, but elapsed time was 0.758850458 seconds against a
0.75-second assertion. The job reported 14397 passed, 28 skipped, 18 xfailed and 2 xpassed.
This is reported evidence; the elapsed value does not establish whether the deadline restarted.
The smallest trustworthy repair must discriminate a restarted deadline from scheduling delay.

## Ticket Contract
- ENTRY_GATE: Retained owner-assigned expert_1 identity and synaptic_python_developer role;
  required recovery reads and attestation complete, own roster active, matching attention route.
- EXECUTION_BOUNDARY: ManagedSpellQuantity.reserve and its queue waiting/cleanup collaborators;
  test_managed_spell_quantity.py and direct fixtures; required evidence, test documentation and
  generated bundles. Select exact edits after reading and diagnosis.
- DEPENDENCIES: Existing managed-pool contract and current clean source base
  70ea25d23394f939bc75337e232a0e598d402ac4. Preserve the two previously completed repairs.
- EXIT_GATE: Source-backed cause, a deterministic regression oracle with a failing negative
  control, focused checks and the required runtime suite passing, distinct author self-review,
  relevant generated-asset checks and synchronized closure records.
- FAILURE_ESCALATION: Record an actual source-custody collision, unresolved consequential
  contract choice, unavailable required check or tool denial. Hold only dependent actions.

## Scope Boundaries
- In scope: Trace timeout ownership, reproduce the reported failure mechanism, repair the test
  or runtime according to evidence, and validate the final candidate locally on Mark's machine.
- Out of scope: Other correctness stories, dependency/CI policy changes, agents/subagents,
  commits, pushes, merges, releases, hosted runs and unrelated coroutine-warning repairs.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: Full-suite qualification, deterministic controls, input-integrity checks and
  distinct author self-review satisfy the repair criteria under retained owner authority.

## Steps / Checklist
- [x] Read the relevant component context, full source and affected tests; classify the cause.
- [x] Record the exact repair and acceptance oracle before implementation.
- [x] Implement a narrow repair with truthful contracts and deterministic evidence.
- [x] Validate focused cases, negative control, repeats and the required runtime tiers.
- [x] Perform distinct self-review, close records and verify generated assets last.
- [x] Run the Ticket Microcycle and record meaningful findings before dependent work.

## Deliverables
- Reviewable repair preserving the original timeout across wakeups.
- Reproducible validation evidence with explicit platform/interpreter limits.

## Files / Paths Impacted
- tests/unit/melder/aether/conduit/creations/test_managed_spell_quantity.py
- src/melder/aether/conduit/creations/managed_spell_quantity.py (investigation; edit only if warranted)
- Context Compass task, routing and evidence; test-map updates only where this repair changes them.
- llm_support generated bundles affected by changed tests/docs.

## Validation
- Focused module: 75 passed. Managed selection: 217 passed, 894 deselected.
- Deadline repeats: 200 passed per GIL mode; 400 cases total. Python 3.14.2: both cases passed.
- Three mutation controls: both cases reject each mutant; six expected assertion failures.
- Full runtime: 14399 passed, 28 skipped, 17 xfailed, 3 xpassed, no failures/errors in 1318.09 s.
  The official driver returned 0 after its in-process GIL checks; both new cases executed.
- All 1802 tracked qualification input hashes and the base revision match the pre-run capture.
- Source-asset and LLM checks passed for this candidate; final delivery receipts are
  final_asset_check.log, final_bundle_check.log and final_verification.json in the evidence folder.
- Final runtime qualification uses the repository driver with the GIL disabled.
- Hosted macOS Python 3.14.3: Not run; no hosted execution is authorized by this task.
- Coverage: Not run; no measured-coverage claim will be made.

## Risks / Rollback Notes
- A broader timing threshold can hide a restarted deadline; preserve a strict logical oracle.
- Global clock patches can affect other code; isolate the pool's time boundary and undo patches.
- Preserve existing thread-based release, exhaustion and teardown checks.
- Roll back only this task's changed lines and regenerated outputs if qualification fails.

## Applicable Anti-Patterns
- [x] No source-behavior claim from a search hit or a prior receipt.
- [x] No implementation from UNKNOWN or HYPOTHESIS without an evidence-backed decision.
- [x] No weakened timeout check or removed required failure to claim a pass.
- [x] No closure before criteria, required checks, self-review and board synchronization.

## Done Checklist
- [x] Steps complete and checked off.
- [x] Deliverables and evidence linked.
- [x] Documentation updated where needed.
- [x] Validation and unavailable matrix cells recorded accurately.
- [x] Notes meet configured usefulness score and preserve prior findings.
- [x] Acceptance, review and artifact disposition recorded.
- [x] Own attention route replaced by closure anchor.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/queue_deadline_wakeups_20261019/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Applied at closure: qualification evidence and before-copy retained; eleven
  verified task-owned temporary/cache directories removed (cleanup_receipt.json).

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: queue deadline across spurious wakeups
- IF_UNKNOWN: none

## Noting Behavior
- Tactical findings, concrete impact and one next action with exact evidence ranges.
- Preserve historical Notes; current resume view is updated in place.

## Contribution Attribution
- Ticket/Work Author(s): expert_1, synaptic_python_developer; diagnosis, test repair,
  documentation, controls and qualification of test SHA256
  936bb6ec9f93698baf48c85d7ca44110897106709ad0ac8ab589c30127b11d7c.
- Published By: local workspace files through Codex; no remote publication.
- Independent Review: none; expert_1 performed distinct author self-review, recorded below.

## Notes
- DATETIME: 2026-10-20T00:09:50Z
  AUTHOR: expert_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The runtime already takes deadline = monotonic() + timeout once, before acquiring the
    condition, and each loop waits deadline - monotonic(). The test starts its stopwatch before
    spawning the worker and measures through exception creation and the worker's finally block;
    it can fail after scheduler delay without a restarted deadline. Repair only the test's oracle.
  EVIDENCE:
  - src/melder/aether/conduit/creations/managed_spell_quantity.py:510-550
  - tests/unit/melder/aether/conduit/creations/test_managed_spell_quantity.py:157-176
  - tests/unit/melder/aether/conduit/creations/test_managed_spell_quantity.py:773-795
  IMPACT: No runtime, API, source graph, version or release-note change is warranted. A test-only
    change does not trigger the system-impacting source patch framework.
  NEXT: Demonstrate the old test's false failure under a delayed worker, then replace its clock
    and wait boundaries while retaining the actual reserve loop and exhaustion checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-20T00:07:04Z
  AUTHOR: expert_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The owner requested this repair in the existing local-only scope. The prior repairs are
    completed and committed in the clean base; no deadline-specific ticket was found.
  EVIDENCE:
  - tickets/tasks/completed/2026-10-19_fix_cluster_duplicate_add_concurrency_task.md:1-24
  - mailbox_board.md:86-103
  IMPACT: This distinct failure gets one new task without reopening completed work or other lanes.
  NEXT: Read the managed-pool component and full implementation/test units.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-20T00:11:00Z
  AUTHOR: expert_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The unchanged test passed locally once. Delaying only the worker's start by 0.6 seconds
    made the same test fail at line 795 with the production deadline logic untouched. This proves
    a false-failure mechanism; it does not establish the exact macOS scheduling event.
  EVIDENCE:
  - artifacts/queue_deadline_wakeups_20261019/baseline.log:1-3
  - artifacts/queue_deadline_wakeups_20261019/delayed_worker_control.log:1-3
  - artifacts/queue_deadline_wakeups_20261019/reproduce_delayed_worker.py:9-39
  IMPACT: Replace only this test's real-time/thread measurement with a module-local clock and
    a condition-wait double. Keep production reserve/count/error logic and existing real-thread
    tests. Assert decreasing wait budgets and timeout at or after the original logical deadline;
    bound the double's wakeups so a deadline-reset mutant fails promptly instead of hanging.
  NEXT: Implement two deterministic cases (wake at deadline and wake beyond it), then run
    deadline-reset, full-timeout-wait and early-expiry controls against the revised oracle.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-20T00:13:14Z
  AUTHOR: expert_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The revised module passes 75 tests; the managed selection passes 217 tests. Both deadline
    cases pass 100 repetitions in each GIL mode (400 cases total), and reject all three transient
    mutants (deadline restart, full timeout passed to every wait, early expiry): six expected
    assertion failures. The first control-report validator wrongly expected a JUnit type attribute;
    its three runs ended with KeyError after the expected failures. The validator was corrected to
    inspect the saved assertion trace and all three complete controls then exited successfully.
  EVIDENCE:
  - artifacts/queue_deadline_wakeups_20261019/focused.log:1-4
  - artifacts/queue_deadline_wakeups_20261019/managed.log:1-5
  - artifacts/queue_deadline_wakeups_20261019/repeat_gil0.xml:1-1
  - artifacts/queue_deadline_wakeups_20261019/repeat_gil1.xml:1-1
  - artifacts/queue_deadline_wakeups_20261019/run_deadline_mutant.py:14-64
  IMPACT: The regression oracle discriminates real timeout bugs while retaining real-thread pool
    tests. The test map's recorded 1040-line extent is now stale (actual 1070), so refresh only its
    managed-pool claim, C1 entry and handoff, preserving prior content and rebuilding its index.
  NEXT: Verify the narrow test-map update, rebuild candidate assets and qualify the full runtime.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-20T00:16:21Z
  AUTHOR: expert_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Distinct author self-review inspected the exact test/doc/index diff and the production
    reserve loop after implementation stopped. Clock substitution is local to the production
    module; fixture restoration and finally cleanup are explicit. Binary-exact wake intervals
    avoid clock-origin rounding, expected budgets catch overlong waits, finite wake counts catch
    deadline resets, and the second case covers delayed wakes beyond the deadline. No source
    file changed. Existing real-thread tests and their helpers are unchanged. No review defect
    remains in this candidate; full-suite acceptance is pending.
  EVIDENCE:
  - tests/unit/melder/aether/conduit/creations/test_managed_spell_quantity.py:776-826
  - src/melder/aether/conduit/creations/managed_spell_quantity.py:510-550
  - artifacts/queue_deadline_wakeups_20261019/qualification_inputs.json:1-22
  - artifacts/queue_deadline_wakeups_20261019/documentation_verification.json:1-16
  IMPACT: Candidate inputs are bound to 1802 tracked files by one path-aware SHA256 aggregate;
    production is unchanged against the base, all nine CI dependency pins match, and the original
    control's AST matches the base. The test-map preservation check accounts for only four
    replaced metadata lines, its index is current and its updated extent is 1070. This is scoped
    verification of the changed entry, not a new whole-document semantic certification.
  NEXT: Follow the local full-runtime process to completion and recheck all input hashes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-20T00:39:01Z
  AUTHOR: expert_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Accept and close the complete authorized repair after distinct author self-review.
    The official full runtime passed 14399 tests with zero failures/errors (28 skipped,
    17 xfailed, 3 xpassed), driver exit 0, GIL verified off before and after. Both deadline
    cases executed. All 1802 tracked input hashes and the base revision are unchanged.
  EVIDENCE:
  - artifacts/queue_deadline_wakeups_20261019/verification_receipt.json:1-102
  - artifacts/queue_deadline_wakeups_20261019/full_runtime_exit.json:1-4
  - artifacts/queue_deadline_wakeups_20261019/documentation_verification.json:1-16
  - artifacts/queue_deadline_wakeups_20261019/cleanup_receipt.json:1-17
  IMPACT: Every scoped criterion passes: source-backed diagnosis, old-test false-failure
    reproduction, deterministic contract checks with negative controls, focused/repeated/full
    validation, preserved test-map content and current index, honest self-review and artifact
    disposition. Hosted macOS 3.14.3 and coverage were not run. The existing coroutine shutdown
    warning remains a separate issue; no production file changed. Eleven temporary directories
    were removed after validating each absolute target under this task's evidence root.
  NEXT: Run the final asset/bundle rebuild and checks after closure, then return the result.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Completed test-only repair. The original test can fail after a delayed worker start even with
correct timeout logic. Two controlled-clock cases now verify decreasing remaining budgets and
exhaustion at/beyond the original deadline, and all three deliberate timeout mutants fail them.
Full local Windows Python 3.14.7 GIL-off qualification passed 14399 tests; 75 focused checks,
217 managed checks, 400 repeated cases and both Python 3.14.2 cases also passed. Production
files and all qualification inputs stayed unchanged. The test-map update is narrow and its
index/preservation checks pass. Reports and controls are retained; temporary directories are
removed. Final generated-asset receipts are linked above. Hosted macOS 3.14.3, coverage and the
separate coroutine shutdown warning remain explicit limits. No active work remains in this lane.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
