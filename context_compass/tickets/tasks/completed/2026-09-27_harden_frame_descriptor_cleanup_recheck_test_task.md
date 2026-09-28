

# Task: Harden the Windows-flaky FrameDescriptor cleanup recheck test

## Metadata
- Task ID: TASK-2026-09-27-harden-frame-descriptor-cleanup-recheck-test
- Story: none
- Status: done
- Owner: user
- Agent Name: melder_0
- Priority: p1
- Created: 2026-09-27T20:17:43Z
- Updated: 2026-09-27T21:26:35Z
- Completed: 2026-09-27T21:26:35Z
- Closure Basis: owner acceptance in chat (2026-09-27), answering "Can I close this one out?": "ok cool lets
  keep moving".
- Summary: The Windows CI flake was the test's lock stand-in losing a signal and dying with its lock held. The
  test now uses one descriptor: frame_name checked, cleaned once, check_cleaned() must raise; no threads and no
  use after cleanup. No source change; the 33 sibling copies of the old helper stay unless the owner asks.

## Objective
The owner's Windows CI run (windows-latest, CPython 3.14.7 free-threaded; 1 failed, 12806 passed) failed
`tests/unit/melder/aether/test_aetheric_frame_descriptor.py::test_descriptor_exposes_frame_name_and_cleanup_rechecks_cleaned_inside_lock`: the first cleanup thread's
coordinated lock timed out waiting for the second thread and died inside `__enter__` holding its RLock, the second
thread blocked on it for good, `cleaned` was still False, and the interpreter's shutdown join then hung until it was
interrupted. Find the cause, prove it, and harden the test - and the code, if the fault is there.

## Ticket Contract
- ENTRY_GATE: owner direction in chat (2026-09-27); this board row.
- EXECUTION_BOUNDARY: the failing test in tests/unit/melder/aether/test_aetheric_frame_descriptor.py;
  FrameDescriptor.cleanup read-only unless the fault is there; probes under
  artifacts/frame_descriptor_test_race_20260927/; LLM bundles rebuilt if the tests corpus goes stale. No notch and no
  release-note entry: a tests-only change (special_instructions/agent_contribution_guide.md). Sibling tests that copy
  the same coordination helper are listed, not edited, until the owner approves a sweep.
- DEPENDENCIES: none.
- EXIT_GATE: cause evidenced from source and a forced reproduction; the hardened test passes stress runs on 3.14t
  (GIL off and on) and the GIL build and survives the adversarial interleaving; the file's suite green; asset and
  LLM-bundle checks OK; owner acceptance.
- FAILURE_ESCALATION: DECISION_REQUEST for a production-code change or a many-file sweep; BLOCKER if the failure
  cannot be explained from source.

## Scope Boundaries
- In scope: the one failing test, its coordination helper, the cleanup method it exercises.
- Out of scope without approval: the sibling copies of the helper; production cleanup posture changes.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner instruction in chat, 2026-09-27 ("figure it out and harden it if we can").
- from_state: in_progress
- to_state: review
- transition_reason: Cause proven (forced and natural reproduction), hardened test live in the device tree and
  green under stress on three interpreters, asset and LLM-bundle checks OK. Awaiting owner acceptance.
- from_state: review
- to_state: in_progress
- transition_reason: Owner redirected the test to the simple form (tolerate the use-after-clean AttributeError,
  verify with check_cleaned()).
- from_state: in_progress
- to_state: review
- transition_reason: Simple form live in the device tree, green under stress on three interpreters; checks OK.
- from_state: review
- to_state: in_progress
- transition_reason: Owner directed (chat) that the test must not use a cleaned descriptor: take the race out.
- from_state: in_progress
- to_state: review
- transition_reason: No-race test live in the device tree, 11 passed on three interpreters; checks OK.
- from_state: review
- to_state: done
- transition_reason: Owner turn-in (chat, 2026-09-27T21:26:35Z): "ok cool lets keep moving".

## Steps / Checklist
- [x] Read the test and FrameDescriptor.cleanup in full; record the cause.
- [x] Reproduce: stress the original on 3.14t and force the bad interleaving deterministically.
- [x] Harden the test in the VM worktree; stress it and run the adversarial interleaving.
- [x] NOTICEs, copy to the device, file suite on 3.14t (GIL 0/1) and the GIL build.
- [x] Asset and LLM-bundle checks OK (tests-only change: no notch, no release-note entry).
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- A deterministic test, reproduction evidence, and the list of sibling copies with a sweep proposal.

## Files / Paths Impacted
- tests/unit/melder/aether/test_aetheric_frame_descriptor.py; llm_support (rebuilt, if its tests corpus goes stale).

## Validation
- Final (no race: one descriptor, cleaned once, `check_cleaned()` raises), worktree equal to the device tree:
  the file under pytest with thread-exception warnings as errors, 11 passed on 3.14.7t GIL off and on and the
  3.14.7 GIL build, and 11 passed from the device tree (suite_file_worktree_no_race.txt).
- Before it, the simple form: 11 passed on all three, 20,000-run stress on each, race outcome tally; against a
  cleanup without its inner recheck it still passed 200 of 200 (simple_vs_mutant_gil0.txt).
- Earlier: forced interleaving and stress of the original (fails as on CI, 3 in 20,000 with the GIL off).
- Device: file byte-equal to the validated copy; build assets `--check` OK; LLM bundles (tests) rebuilt, all `--check` OK.
- Coverage: Not run.

## Risks / Rollback Notes
- Test-only change; rollback is a revert of one file.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without acceptance confirmation and board-sync completion.
- [x] No behaviour claim cited to a search hit; every range covers the logic that was read.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/frame_descriptor_test_race_20260927/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: task closure

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-27T20:21:12Z
  TYPE: DECISION
  CLAIM: The owner-ruled contribution guide added to special_instructions today governs this lane: tickets that touch
    only tests do not notch and add nothing to the running release note; generated assets and bundles are rebuilt
    last and both checks must be OK at hand-off. The device tree moved since the last lane (0.2.82 cut by fable_0,
    release_docs/0.2.82.md, empty next_version_release.md); the test file and FrameDescriptor are unchanged.
  EVIDENCE:
  - context_compass/special_instructions/agent_contribution_guide.md:14-97
  - context_compass/attention_board.md:107-107
  IMPACT: This lane edits one test file and, if needed, regenerates llm_support; no version or release-note work.
  NEXT: Record the cause from the full read of the test and FrameDescriptor.cleanup.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T20:21:12Z
  TYPE: FACT
  CLAIM: The fault is the test's coordination helper, not FrameDescriptor. `_CoordinatedLock.__enter__` decides
    first versus second by reading `_entered_first.is_set()` BEFORE taking its RLock, and the first entrant sets
    that event only AFTER taking it. When both threads read the event before the first sets it - they start
    together and free-threaded Windows runs them in parallel - the second never signals `_second_attempted` and
    blocks in `acquire()`. The first then waits 1.0 s for a signal that cannot come, and its `assert` fails inside
    `__enter__` while it holds the RLock (no `__exit__` runs): the second thread is blocked for good on a lock whose
    owner died, `_cleaned` is never set because the assert comes first, the main thread's `cleaned is True` fails
    after its two 1 s joins, and the stuck non-daemon thread holds up interpreter shutdown. The CI log shows each
    step: Thread-377's AssertionError at the wait, `cleaned` False, KeyboardInterrupt in `_thread._shutdown()`.
    FrameDescriptor.cleanup does recheck `_cleaned` inside its lock, which is the property the test is after.
  EVIDENCE:
  - tests/unit/melder/aether/test_aetheric_frame_descriptor.py:388-450
  - src/melder/nexus/frame_descriptor/frame_descriptor.py:116-161
  IMPACT: A deterministic coordination (the second entrant identified by a failed non-blocking acquire, the lock
    released if the first entrant fails, daemon threads with liveness asserts) removes the flake without touching
    the code under test.
  NEXT: Record the sibling copies and the production lock-deletion risk, then reproduce.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T20:21:12Z
  TYPE: FACT
  CLAIM: The same helper, with the same event checks, acquire and 1.0 s wait, is copied 34 times across 32 test files
    (AST scan; one hash for every copy): 10 dev_ops files (change-control, incident, risk, spell system states,
    DevOps manager), 18 aether files (ACL, frame descriptor, frame links, Nexus and Rift configuration) and 5
    spell-compiler files. Every copy can flake the same way; only this one has failed so far.
  EVIDENCE:
  - tests/unit/melder/aether/dev_ops/change_control_manager/test_conflict_manager.py:47-66
  - tests/unit/melder/aether/test_frame_acl_profile.py:202-221
  - tests/unit/melder/spellbook/spell_crafter/symbolic_graph/test_spell_symbolic_graph.py:123-142
  IMPACT: Fixing one copy leaves 33 identical latent flakes; a shared helper under tests/ plus a mechanical sweep
    is the durable fix, and it needs the owner's approval (many files).
  NEXT: Record the production lock-deletion risk.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T20:21:12Z
  TYPE: RISK
  CLAIM: Separate from the flake: FrameDescriptor.cleanup deletes `_lock` after leaving its `with` block. A second
    cleanup that passed the unlocked `_cleaned` check but reads `self._lock` after the first finished gets
    AttributeError instead of returning. The test cannot see this (its stand-in marks the descriptor cleaned before
    the body runs). Deleting the lock after guarded teardown is the documented default of the cleanup skill, so
    whether to keep locks as post-cleanup tombstones (as Creations does) is a codebase-wide owner decision.
  EVIDENCE:
  - src/melder/nexus/frame_descriptor/frame_descriptor.py:136-161
  - src/melder/aether/conduit/creations/creations.py:186-243
  - context_compass/agent_onboarding/user_defined/synaptic_python_developer/skills/python/cleanup_and_disposal.md:51-64
  IMPACT: Not the cause of this failure; flagged, not changed.
  NEXT: Stress the original test on 3.14t and force the bad interleaving.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T20:24:59Z
  TYPE: MEASURE
  CLAIM: Reproduced on the VM (3.14.7t, GIL off, 2 CPUs; worktree synced to the device tree). Forced: the helper
    copied verbatim, with only its inner RLock gated so the first acquirer waits until the second calls acquire(),
    gives the CI failure exactly - the first thread dies with AssertionError at the wait, the second stays blocked,
    `cleaned` is False. Unforced: 20,000 calls of the original test in 11.4 s failed 3 times (AssertionError), each
    leaving one thread blocked for good. The repo's pytest settings have no `filterwarnings = error`, so an
    exception inside a cleanup thread is only a warning: the original test would pass a FrameDescriptor.cleanup
    that lost its inner recheck.
  EVIDENCE:
  - context_compass/artifacts/frame_descriptor_test_race_20260927/probe_forced_interleaving.py:1-92
  - context_compass/artifacts/frame_descriptor_test_race_20260927/probe_forced_interleaving_gil0.txt:1-5
  - context_compass/artifacts/frame_descriptor_test_race_20260927/probe_stress.py:1-46
  - context_compass/artifacts/frame_descriptor_test_race_20260927/stress_original_gil0.txt:1-1
  - pyproject.toml:210-229
  IMPACT: The failure is the lost-signal race in the helper, reproducible on demand; the fix must also make a
    missing recheck fail the test rather than warn.
  NEXT: Rewrite the helper and thread handling in the worktree per the PLAN note.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T20:24:59Z
  TYPE: PLAN
  CLAIM: Test-only change to the one test: the first entrant is the thread whose non-blocking acquire succeeds,
    the other sets `_waiter_blocked` and blocks, so the descriptor is marked cleaned only after the waiter has
    passed the unlocked check; a failing first entrant releases the lock before raising; the wait is 10 s and the
    joins 15 s (no timing on the success path); both threads are daemons wrapped to record exceptions, and the test
    asserts neither is alive, no exception was raised in either, and `cleaned` is True; docstrings added; imports
    gain List, Self, Type and TracebackType. Validation: forced delays (waiter 0.5 s late; waiter started first), a
    mutant cleanup without the inner recheck (must fail cleanly, not hang), 20,000-run stress on 3.14t GIL 0/1
    and the GIL build, then the whole file under pytest on all three.
  EVIDENCE:
  - tests/unit/melder/aether/test_aetheric_frame_descriptor.py:388-450
  - src/melder/nexus/frame_descriptor/frame_descriptor.py:116-161
  IMPACT: One file changes; FrameDescriptor and the 33 sibling copies do not.
  NEXT: Apply in the worktree and run the validation list.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T20:29:26Z
  TYPE: MEASURE
  CLAIM: Hardened test applied in the worktree (BOM and CRLF kept; longest line 111). Validation: the waiter
    arriving 0.5 s late passes; 300 runs with a random 0-20 ms delay before each cleanup all pass; against a
    mutant cleanup without the inner recheck the hardened test fails at once, while the ORIGINAL test passes it
    (the AttributeError stays inside a thread); 20,000 stress runs each on 3.14.7t GIL off (8.3 s), GIL on
    (12.3 s) and the 3.14.7 GIL build (3.7 s): no failure, thread error or stuck thread. The original, same
    stress: 3 failures with the GIL off, none with it on - the race needs parallel threads, as on the
    free-threaded Windows runner. The file under pytest, with thread-exception warnings made errors: 11 passed
    on all three interpreters (the one warning is melder's GIL-enabled notice).
  EVIDENCE:
  - context_compass/artifacts/frame_descriptor_test_race_20260927/apply/apply_hardened_test.py:1-160
  - context_compass/artifacts/frame_descriptor_test_race_20260927/validate_hardened_gil0.txt:1-6
  - context_compass/artifacts/frame_descriptor_test_race_20260927/stress_hardened_314t.txt:1-2
  - context_compass/artifacts/frame_descriptor_test_race_20260927/stress_hardened_314gil.txt:1-1
  - context_compass/artifacts/frame_descriptor_test_race_20260927/stress_original.txt:1-3
  - context_compass/artifacts/frame_descriptor_test_race_20260927/suite_file_worktree.txt:1-9
  IMPACT: The test is deterministic on every interpreter and now catches the regression it is named for.
  NEXT: NOTICE the agents active today, then apply the same script to the device tree.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T20:35:00Z
  TYPE: MEASURE
  CLAIM: Landed in the device tree: the device file equalled the pre-change copy, the same apply script ran on it,
    and the result is byte-equal to the validated worktree file (git shows the file's only other difference from
    HEAD is line endings, as for the rest of the tree). NOTICEs M0-61 (fable_0) and M0-62 (muse_0). Checks from
    the repository root on 3.14.7t: build assets `--check` OK (v0.2.82, untouched); LLM bundles were stale for
    `tests` (this change) and `other` (drift outside src/tests since the 0.2.82 build, not this lane), rebuilt
    tracked-only (the README's normal path) and `--check` now OK for src, tests and other. No notch and no
    release-note entry: tests-only change.
  EVIDENCE:
  - tests/unit/melder/aether/test_aetheric_frame_descriptor.py:388-503
  - context_compass/artifacts/frame_descriptor_test_race_20260927/apply/apply_hardened_test.py:1-160
  - llm_support/manifest.json:1-20
  IMPACT: The fix is live in the owner's tree; the only generated files touched are the tests and other bundles.
  NEXT: Ask the owner to accept, and whether to sweep the 33 sibling copies onto one shared helper.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T20:35:00Z
  TYPE: DECISION_REQUEST
  CLAIM: Two follow-ups, neither started. (1) Sweep: move the hardened helper into one shared test-support module
    and replace the 33 racy copies in the 31 other files with it, mechanically (one codemod, same assertions per
    test), then stress each affected test; every copy can fail the same way on free-threaded runners. (2) The
    production RISK note: FrameDescriptor.cleanup (and every class following the delete-the-lock-after-teardown
    default) can raise AttributeError in a second concurrent cleanup; keeping the lock as a post-cleanup tombstone,
    as Creations does, would close it, but it is a codebase-wide posture change.
  EVIDENCE:
  - tests/unit/melder/aether/dev_ops/change_control_manager/test_conflict_manager.py:47-66
  - src/melder/nexus/frame_descriptor/frame_descriptor.py:136-161
  IMPACT: This task closes on acceptance either way; each follow-up would be its own ticket.
  NEXT: Owner accepts this task and decides (1) and (2).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T20:39:15Z
  TYPE: DECISION
  CLAIM: Owner (chat) on the follow-ups: no production change for the lock-deletion race - calling cleanup on an
    object that is being or has been cleaned is the caller's problem, not something to harden the source for; the
    test is a test, keep it simple and move on. Item (2) is dropped. Item (1), the 33 sibling copies, is left as is
    unless the owner asks for the sweep. The test change already landed is kept: a bare try/except in the test body
    would not have stopped the failure, which was a thread stuck on a lock whose owner died, not an exception the
    test could catch.
  EVIDENCE: context_compass/tickets/tasks/2026-09-27_harden_frame_descriptor_cleanup_recheck_test_task.md:264-278
  IMPACT: Scope stays one test file; no source change in this lane.
  NEXT: Owner confirms turn-in of this task.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-27T20:42:03Z
  TYPE: DECISION
  CLAIM: Owner (chat), overruling the landed rewrite: fix the test the simple way. A cleanup that reaches the
    lock after the other cleanup deleted it raises AttributeError, and that is legitimate - the object must not be
    used any more; the test should tolerate it (the try/except the owner asked for) and verify the outcome with
    `check_cleaned()` in that spot, instead of a lock stand-in that pokes `_cleaned` and a no-errors assertion.
    Plan: drop the stand-in; two daemon threads start on a Barrier and call the real cleanup(); AttributeError is
    caught and ignored with a comment, any other exception or a thread still alive fails; finally
    `check_cleaned()` must raise RuntimeError. Imports go back to the original set plus List. The test no longer
    asserts the inner recheck itself (the owner's call). Tests-only: no notch.
  EVIDENCE:
  - tests/unit/melder/aether/test_aetheric_frame_descriptor.py:388-503
  - src/melder/utilities/general_base/cleanable.py:129-144
  IMPACT: The Windows failure mode (a stand-in dying with the lock held) disappears with the stand-in.
  NEXT: Apply in the worktree, stress on three interpreters, then land on the device and rebuild the bundles.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T20:45:01Z
  TYPE: MEASURE
  CLAIM: The owner's simple form is live in the device tree (byte-equal to the validated worktree file; the device
    file still matched the stand-in version before the swap). The test now races two real cleanups on a Barrier,
    ignores the use-after-clean AttributeError, fails on any other error or a live thread, and ends with
    `check_cleaned()` raising. Worktree: the file 11 passed on 3.14.7t GIL off and on and the 3.14.7 GIL build
    (thread-exception warnings as errors); 20,000 stress runs on each, no failure or stuck thread. Race tally,
    20,000 races each: GIL off 19,999 both-returned and 1 AttributeError-plus-returned, GIL on none - the case the
    owner described is real and now tolerated. LLM bundles rebuilt (tests corpus); asset and bundle checks OK.
  EVIDENCE:
  - tests/unit/melder/aether/test_aetheric_frame_descriptor.py:388-457
  - context_compass/artifacts/frame_descriptor_test_race_20260927/apply/apply_simple_test.py:1-101
  - context_compass/artifacts/frame_descriptor_test_race_20260927/suite_file_worktree_simple.txt:1-6
  - context_compass/artifacts/frame_descriptor_test_race_20260927/stress_simple.txt:1-3
  - context_compass/artifacts/frame_descriptor_test_race_20260927/probe_race_outcomes.py:1-51
  - context_compass/artifacts/frame_descriptor_test_race_20260927/race_outcomes.txt:1-3
  IMPACT: No stand-in lock is left to die holding a lock, so the Windows hang cannot recur in this test.
  NEXT: Owner confirms turn-in.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T21:04:04Z
  TYPE: FACT
  CLAIM: Owner (chat, after the simple form landed): the AttributeError from the deleted lock is real, but the
    point is that nothing should use a descriptor once it is cleaned. Source agrees: FrameDescriptor.cleanup has one
    caller in src, FrameDescriptorManager.cleanup, which runs once under the manager lock (outer and inner
    `_cleaned` checks), cleans each descriptor once and clears and deletes the registry holding them; its one
    caller is Nexus.cleanup, double-checked under the Nexus lock; the manager's descriptor lookups call
    `check_cleaned()` first. No src path cleans a descriptor twice or reaches one through the manager after
    cleanup; the only caller racing a second cleanup in is this test's second thread, on purpose. The supported
    post-cleanup contract (getters raise RuntimeError through check_cleaned) is already covered by
    test_descriptor_properties_raise_after_cleanup.
  EVIDENCE:
  - src/melder/nexus/frame_descriptor/frame_descriptor.py:116-161
  - src/melder/nexus/frame_descriptor_manager.py:144-175
  - src/melder/nexus/frame_descriptor_manager.py:667-747
  - src/melder/nexus/nexus.py:304-379
  - tests/unit/melder/aether/test_aetheric_frame_descriptor.py:367-385
  - tests/unit/melder/aether/test_aetheric_frame_descriptor.py:388-457
  IMPACT: The race half of the test exists only to use a descriptor while or after it is cleaned - the case the
    owner rules out - and with the AttributeError tolerated it may no longer fail for any real regression.
  NEXT: Measure the current test against a mutant cleanup without the inner recheck (VM worktree only).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T21:05:43Z
  TYPE: MEASURE
  CLAIM: The simple-form test cannot tell a working inner recheck from a missing one, and its race mostly
    exercises use-after-clean. Probe (3.14.7t, GIL off, VM worktree equal to the device tree): a Barrier right
    after the outer `_cleaned` check makes both cleanups reach the lock on every run. Recheck kept: 200 of 200
    passed; the second cleanup reached the inner recheck in 4 runs and hit the deleted `_lock` (AttributeError)
    in 196. Recheck removed: 200 of 200 still passed, including the 2 runs where the second cleanup re-ran the
    teardown and failed on the deleted `_frame_overview` - the test swallows both AttributeErrors alike.
  EVIDENCE:
  - context_compass/artifacts/frame_descriptor_test_race_20260927/probe_simple_vs_mutant.py:1-102
  - context_compass/artifacts/frame_descriptor_test_race_20260927/simple_vs_mutant_gil0.txt:1-3
  - tests/unit/melder/aether/test_aetheric_frame_descriptor.py:388-457
  IMPACT: The race half only exercises the use the owner rules out and cannot fail for the regression its name
    promises. Proposal: one descriptor - check frame_name, clean it once, `check_cleaned()` raises - with no
    threads and no AttributeError to catch, renamed ..._reports_cleaned_after_cleanup (no recheck is tested).
  NEXT: Owner picks: take the racing second cleanup out as proposed, or close with the current form.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T21:20:48Z
  TYPE: DECISION
  CLAIM: Owner (chat): fix the test so it does not use a cleaned descriptor. Plan: one descriptor holds the two
    records, `frame_name` is asserted, `cleanup()` runs once, then `check_cleaned()` must raise; the racing second
    cleanup, the threads, the Barrier and the AttributeError catch go, and `threading` and `List` leave the imports
    (nothing else in the file uses them). The test is renamed
    test_descriptor_exposes_frame_name_and_reports_cleaned_after_cleanup, since it no longer tests a recheck; no doc,
    release note, CI file or system document cites the old name. Tests-only: no notch, no release-note entry.
  EVIDENCE:
  - tests/unit/melder/aether/test_aetheric_frame_descriptor.py:1-5
  - tests/unit/melder/aether/test_aetheric_frame_descriptor.py:388-457
  IMPACT: The test calls nothing on the descriptor after cleanup but `check_cleaned()` and starts no threads, so the
    Windows hang cannot come back through it.
  NEXT: Apply in the worktree, run the file on three interpreters, land on the device, then rebuild the bundles.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T21:23:38Z
  TYPE: MEASURE
  CLAIM: The no-race test is live in the device tree, byte-equal to the validated worktree file (the device file
    matched the simple-form copy before the swap). test_descriptor_exposes_frame_name_and_reports_cleaned_after_cleanup
    holds the two records, asserts `frame_name`, cleans the descriptor once and asserts `check_cleaned()` raises:
    no threads, Barrier or AttributeError catch; the `threading` and `List` imports are gone; BOM and CRLF kept,
    longest line 109. The file: 11 passed on 3.14.7t GIL off and on and on the 3.14.7 GIL build (worktree, thread
    exceptions as errors) and 11 passed from the device tree. LLM bundles: tests corpus rebuilt; bundle `--check`
    OK for src, tests and other; build assets `--check` OK (v0.2.82, untouched). No source change, no notch.
  EVIDENCE:
  - tests/unit/melder/aether/test_aetheric_frame_descriptor.py:1-5
  - tests/unit/melder/aether/test_aetheric_frame_descriptor.py:387-433
  - context_compass/artifacts/frame_descriptor_test_race_20260927/apply/apply_no_race_test.py:1-97
  - context_compass/artifacts/frame_descriptor_test_race_20260927/suite_file_worktree_no_race.txt:1-9
  IMPACT: The test no longer uses a descriptor after cleanup and runs no threads; the Windows hang cannot recur here.
  NEXT: Owner confirms turn-in.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Turned in on owner acceptance (2026-09-27T21:26:35Z); in the device tree, not committed; tests-only. The Windows failure was the test's lock stand-in
losing a signal when both cleanup threads started together: its first thread asserted while holding the lock,
the second blocked forever, and shutdown hung. On the owner's direction the test no longer uses a cleaned
descriptor at all: it is now test_descriptor_exposes_frame_name_and_reports_cleaned_after_cleanup - one
descriptor, `frame_name` checked, cleaned once, `check_cleaned()` must raise - with no threads. Nothing in src
cleans a descriptor twice (Nexus.cleanup -> FrameDescriptorManager.cleanup, once, under locks). No source change;
the 33 sibling copies of the old helper, which race a second cleanup the same way, stay unless the owner asks.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->

<!--
Anything this project needs on every ticket of this kind goes in the region
above: extra fields, a compliance checklist, a link to a local convention.

The region is yours. An upgrade replaces every other line of this template with
the new version's text and carries this region across untouched, so a local
addition here is not a divergence you re-resolve on every upgrade - which is
what editing the rest of the template would cost you.
-->
