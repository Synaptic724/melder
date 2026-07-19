- Completed: 2026-07-12T21:00:00Z
- Summary: Closed under the 20:40Z re-measure ruling + owner turn-in
  directive. Revert verified faithful; every raising wait excluded by the
  pass; tree has since absorbed four concurrency fixes touching this
  neighborhood. Watch item: if the next full run burns minutes again,
  REOPEN and run the two-flag diagnostic (--durations=0 -vv
  --faulthandler-timeout=45) - triage resumes on the dump.

# Task: restore link round-trip test 2-3 minute slowness triage

## Metadata
- Task ID: TASK-2026-07-12-restore-link-test-slowness-triage
- Parent: none (owner-directed triage, 2026-07-12)
- Status: in_progress
- Owner: cowork
- Agent Name: melder_0
- Priority: p1
- Created: 2026-07-12T11:30:00Z
- Updated: 2026-07-12T11:30:00Z

## Problem / Opportunity
Owner report: `test_round_trip_restores_links_between_conduits`
(tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py)
appeared to stall, then PASSED after ~2-3 minutes. A passing test that
burns minutes means a bounded wait is being consumed and released (or an
expire-and-proceed path), not a deadlock and not a hard timeout (those
raise). Find the burn, fix it.

## Ticket Contract
- ENTRY_GATE: owner directive ("Focus on this... can you fix it?");
  routed on attention_board.md.
- EXECUTION_BOUNDARY: diagnosis first (no code edits until the burn is
  named with evidence); the eventual fix stays inside whatever component
  the evidence names. Root-cause law applies - no speculative timeout
  tuning.
- DEPENDENCIES: owner runs 3.14t (sandbox cannot import melder).
- EXIT_GATE: the test completes in normal integration time on an
  owner run, with the cause named and fixed (or ruled expected with
  evidence).
- FAILURE_ESCALATION: BLOCKER note if the burn lands in another
  agent's active lane (mutation_0); DECISION_REQUEST if the fix would
  change a public wait contract.

## Goals / Non-goals
- Goal: name the exact wait (file:line) consuming the minutes; fix it.
- Non-goal: re-litigating the reverted remediation mediation (owner
  adjudicated; commit 7abb39e62).

## Acceptance Criteria
- Cause named with `path:line` evidence from a thread-stack dump or
  equivalent.
- Fix lands with a test-time regression guard where sensible.
- Owner-run confirms normal duration. (Agent: "Not run.")

## Applicable Anti-Patterns
- [ ] No blanket timeout increases/decreases without traced cause.
- [ ] No claim that pytest ran (owner runs; agent reports "Not run.").

## State Transition Event
- from_state: (none)
- to_state: in_progress
- transition_reason: owner-directed triage of the slow restore test.

## Noting Behavior
- Task notes: tactical findings, immediate impacts, one-step
  continuation.

## Notes
- DATETIME: 2026-07-12T11:30:00Z
  TYPE: FACT
  CLAIM: Revert verified FAITHFUL before triage - commit 7abb39e62
    removed every remediation element (strategy file, enum, builder row,
    make_scope_key_lineage, notch lineage claim, meld.py wiring incl.
    both helpers + import); meld.py's gated branches are byte-shaped
    back to the pre-change form (locked structural rerun; inlined
    resolution rerun with early returns). Zero remediation/lineage-scope
    tokens remain in the transaction plane. The runtime is the green
    9702 baseline plus mutation_0's research_recent commits (MR is
    inactive in this test - not on its path).
  EVIDENCE:
  - git show 7abb39e62 (10 files; meld.py -177 net)
  - src/melder/aether/conduit/meld/meld.py:572-590 (restored shape)
  IMPACT: the slowness is NOT leftover mediation; static suspects
    narrow to the wait surfaces on the restore path.
  NEXT: wait-surface audit note below.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-12T11:40:00Z
  TYPE: FACT
  CLAIM: Wait-surface audit over this test's exact path - every bounded
    wait either RAISES on expiry (test passed, so none expired) or is
    instant here: LoadGate.wait_for_passage 30s raises (load_gate.py
    :193,:227,:240); acquire_load_authority drain 30s raises
    (aether.py:790-845); mediator scope-wait 30s raises (bounded by
    max_transaction_wait_time_in_seconds, default 30.0,
    aetheric_frame_configuration.py:91); CreationGate
    close_and_wait_until_free polls only while tickets exist - this
    test never melds, so zero tickets = instant (creation_gate.py
    :328-380); PhaseScheduler cleanup thread.join(timeout=5.0) is the
    only expire-AND-PROCEED wait found (phase_scheduler.py:259) but
    would slow every conjure test suite-wide if workers lingered.
    Static analysis cannot pick the culprit; an empirical thread-stack
    dump during the burn is the correct next step (pytest builtin
    faulthandler names the exact file:line without altering pass/fail).
  EVIDENCE:
  - src/melder/utilities/synchronization/load_gate.py:193-240
  - src/melder/aether/aether.py:790-845
  - src/melder/utilities/synchronization/creation_gate.py:328-380
  - src/melder/utilities/synchronization/phase_scheduler.py:259-259
  IMPACT: avoids speculative fixes; one owner-run diagnostic yields the
    exact burn line.
  NEXT: owner runs the two-flag diagnostic (durations split +
    faulthandler dump); triage resumes on the dump.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-12T20:40:00Z
  TYPE: DECISION
  CLAIM: RULING (owner-delegated): the faulthandler dump never arrived
    and the tree has since absorbed four concurrency fixes plus the
    retention re-order that touch this test's neighborhood. New path:
    RE-MEASURE on the owner's next full run - if the test completes in
    normal integration time, close this lane as
    unreproducible-post-fixes; if it burns minutes again, the two-flag
    diagnostic (--durations=0 -vv + --faulthandler-timeout=45) remains
    the one-run answer and triage resumes on the dump.
  EVIDENCE:
  - tickets/tasks/2026-07-12_restore_link_test_slowness_triage_task.md:1-120
  IMPACT: the lane stops blocking on a diagnostic nobody ran; one
    ordinary run resolves it either way.
  NEXT: owner's next full-tree run decides close vs resume.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
Owner-reported 2-3 minute pass on the restore link round-trip test.
Revert verified clean; all raising waits excluded by the pass. RULING
2026-07-12: re-measure on the next owner run - normal time closes the
lane as unreproducible-post-fixes; a repeat burn resumes triage via the
two-flag faulthandler diagnostic.
