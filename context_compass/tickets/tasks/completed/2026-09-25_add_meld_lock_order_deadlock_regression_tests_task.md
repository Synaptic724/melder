

# Task: Add regression tests that pin the meld store/Spell lock-order deadlock

## Metadata
- Completed: 2026-09-25T23:47:39Z
- Summary: Lock-order regression file now guards the fix: 8 formerly deadlocking + 4 safe shapes must complete on
  3.14t and GIL.
- Task ID: TASK-2026-09-25-add-meld-lock-order-deadlock-regression-tests
- Story: STORY-2026-09-25-verify-override-writer-and-contract
- Status: done
- Owner: user
- Agent Name: melder_0
- Priority: p1
- Created: 2026-09-25T21:29:48Z
- Updated: 2026-09-25T23:47:39Z

## Objective
Encode the reproduced deadlocks as integration tests with a hard timeout, so the defect is remembered,
cannot silently return, and flips loudly when a fix lands. No production source change in this task.

## Ticket Contract
- ENTRY_GATE: Owner confirms the proposed test plan; board row routes here.
- EXECUTION_BOUNDARY: One new file,
  tests/integration/melder/multithreading/test_multithreading_meld_lock_order_deadlock.py.
  No src/ edits, no changes to existing tests, no new dependencies.
- DEPENDENCIES: TASK-2026-09-25-verify-native-writer-lock-order evidence (rows 1, 2, 4 reproduced).
- EXIT_GATE: File written to repo conventions; run on CPython 3.14.7t and GIL with results recorded;
  deadlock cases report XFAIL, control reports PASS.
- FAILURE_ESCALATION: BLOCKER if a scenario cannot be forced deterministically through public behavior;
  DECISION_REQUEST for any seam that would require internal instrumentation.

## Scope Boundaries
- In scope: Row 4 (per-conduit and lineage), row 4b (disposal-bearing many), row 1 (purge), and a
  many-consumer control.
- Out of scope: The fix itself (C vs E), cluster row 3, SpellSpace variants.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: Owner accepted the delivered fix on 2026-09-25 and directed closure.

## Steps / Checklist
- [x] Owner confirms plan (subprocess isolation, constructor gates, xfail strict, timeouts).
- [x] Write the test file to repo conventions (docstrings, typing, no __future__ import, no PEP 604).
- [x] Run in the VM source copy on 3.14.7t and 3.14.7 GIL; record outcomes as MEASURE notes.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- tests/integration/melder/multithreading/test_multithreading_meld_lock_order_deadlock.py

## Files / Paths Impacted
- tests/integration/melder/multithreading/test_multithreading_meld_lock_order_deadlock.py (new)

## Validation
- Run in VM source copy: 3.14.7t and 3.14.7 GIL -> 4 passed, 7 xfailed (each xfail a deadlock verdict).
- Recommended commands:
  - python -m pytest tests/integration/melder/multithreading/test_multithreading_meld_lock_order_deadlock.py -rxX

## Risks / Rollback Notes
- Constructor-gate ordering relies on the plan building the `many` leaf before the unique's own check.
  If a precondition is not observed, the child reports it and the test FAILS (never a false pass).
- Rollback: delete the one new file.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No test that can pass while the deadlock is present (every gate has a precondition check).

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >= `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: Deadlock regression tests.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-25T21:29:48Z
  TYPE: PLAN
  CLAIM: Each scenario runs in a child Python process (subprocess.run with a hard timeout), so a real
    deadlock can never hang or poison the pytest process. The interleaving is forced through public
    behavior only: user constructors act as gates (thread A's many-leaf constructor runs while A's meld
    holds the store, and waits for thread C to be inside its unique build). Deadlock cases are
    xfail(strict=True) with a reason naming this story; the many-consumer control must pass.
  EVIDENCE:
  - context_compass/artifacts/melder_writer_lock_order_20260925/meld_only_lock_results_py314t.json:1-540
  - tests/component/melder/aether/test_aether_component_process_wide_spell_id_regime.py:199-212
  - tests/component/melder/spellbook/test_ordered_disposal_binding.py:356-361
  IMPACT: Gives the fix a red-to-green signal and keeps the defect documented in the suite.
  NEXT: Owner confirmation, then write the file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-25T21:38:27Z
  TYPE: MEASURE
  CLAIM: Test file written (test 1 + control). Run in the VM source copy: free-threaded CPython 3.14.7t
    and 3.14.7 GIL both give "1 passed, 1 xfailed" in about 22s. --runxfail verdict: outcome deadlock,
    stuck_threads [meld-A, meld-C], neither meld returned, after both ordering gates were reached. The
    xfail accepts only MeldDeadlockDetected, so a missed gate or crash fails outright. mypy: 0 errors in
    the file. ruff 0.16.9 defaults (no repo ruff config, not in CI): fixed PLW1510 and ISC004; remaining
    UP035/UP006/UP045 conflict with the repo's Optional/typing.List policy, BLE001 is the documented
    outcome capture, EXE002 is a VM mount artifact.
  EVIDENCE:
  - tests/integration/melder/multithreading/test_multithreading_meld_lock_order_deadlock.py:1-334 (superseded by 2026-09-25T21:48:12Z note)
  IMPACT: The meld-only deadlock is pinned in the suite and flips to a strict-xfail failure when fixed.
  NEXT: Owner review of the file; lineage, 4b and purge variants remain deferred by owner scope.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-25T21:48:12Z
  TYPE: MEASURE
  CLAIM: Owner widened scope ("cover more tests, find other ways it can break"; mypy/ruff not used by
    the project). File rewritten as one parameterized runner. VM source copy, 3.14.7t and GIL: 4 passed,
    7 xfailed on both. CONFIRMED deadlocks (xfail on MeldDeadlockDetected): per-conduit on root; lineage
    on root; lineage on TWO DIFFERENT LESSERS of one root (per-request pattern); per-conduit melded with an
    override; purge of the not-yet-built unique; a constructor that melds the unique itself with no DI edge
    (service-locator); disposal-bearing many under the unique (4b). SAFE today: many consumer; per-conduit
    on two lessers; shared manual SpellSpace with and without a disposal leaf. The space+disposal case was
    predicted to deadlock and did not; which store receives that many is UNKNOWN (tripwire kept).
  EVIDENCE:
  - tests/integration/melder/multithreading/test_multithreading_meld_lock_order_deadlock.py:1-482
  IMPACT: The defect reaches ordinary request-scoped lessers and nested melds, not only root-level races.
    4b stays in the matrix as the discriminator between fix options C and E.
  NEXT: Owner review; then code reading toward the fix (meld.py lock scope, SpellSpace unique routing).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-25T23:28:41Z
  TYPE: MEASURE
  CLAIM: Fix landed (implementation task). All 7 former DEADLOCK_CASES moved into
    FORMERLY_DEADLOCKING_CASES (plain test, must complete; MeldDeadlockDetected now means the defect is
    back); new case unique -> many -> unique_per_conduit added; strict xfail removed. 12 passed on
    3.14.7t (3 runs) and GIL. Against the pre-fix source the same file gives 8 failed, 4 passed.
  EVIDENCE: tests/integration/melder/multithreading/test_multithreading_meld_lock_order_deadlock.py:1-540
  IMPACT: The suite now guards the fix instead of documenting the defect.
  NEXT: Owner review together with the implementation task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-25T23:47:39Z
  TYPE: DECISION
  CLAIM: Owner accepted the implementation and its tests; this task closes with the flipped matrix.
  EVIDENCE: tests/integration/melder/multithreading/test_multithreading_meld_lock_order_deadlock.py:1-540
  IMPACT: None further.
  NEXT: none.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
Done 2026-09-25T23:47:39Z (owner accepted the implemented fix). State 2026-09-25T23:28:41Z: review. The deadlock fix landed (TASK-2026-09-25-implement-creation-slot-build-guards).
One parameterized file: 8 FORMERLY_DEADLOCKING_CASES and 4 SAFE_CASES, all must complete; a
MeldDeadlockDetected failure means the store lock is again held across a build. Child-process isolation,
constructor gates, purge gate via stack inspection of Creations._detach_purge_entries; timeouts 10s gate,
5s shared join deadline, 120s child. Not covered: cluster, dynamic-mode transfer or upgrade, hooks that meld.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
