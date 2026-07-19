# Task: Owner-run red triage - fix the 9 failures from the 2026-07-18 full-suite run

## Metadata
- Task ID: TASK-2026-07-18-owner-run-red-triage
- Status: in_progress
- Owner: cowork
- Agent Name: helper_f
- Priority: p0
- Created: 2026-07-18T19:35:00Z
- Updated: 2026-07-18T20:15:00Z
- Related: EPIC-2026-07-17-bugfix-aether-core-logging (BUG-005/BUG-007 families),
  EPIC-2026-07-17-bugfix-conduit-binding-meld (link guardrails), the turned-in MR audit
  epic (BUG-045/046), and helper_1's departed link-guardrail+counter_switch lane.

## Problem / Opportunity
The owner's full 3.14t pytest run went red with 9 failures across four families. Source
tracing proved every family is HALF-LANDED prior-session work (drift between tests and
production), not new defects: (1) BUG-005 two-phase sever existed only in tests - the
production spellbook/ward halves were never on disk; (2) CounterSwitch cleanup contradicted
its own documented retained-terminal-surface contract with a del block (BUG-007 family,
helper_1's departed lane); (3) Conduit.link ran its self-link guard AFTER transaction
admission, so the admission plane raised the wrong error first; (4) two MR group-diff tests
still encoded the pre-BUG-046 lane-only pairing contract that helper_f2's landed fix
deliberately tightened.

## MRP Alignment
Split-brain sever state, waiter crashes on torn slots, and wrong-error guardrails are
correctness-of-core defects; the fix restores the audited contracts at root cause.

## Ticket Contract
- ENTRY_GATE: Owner directive ("fix all this shit, probably mostly drift") + the pasted
  failure output; all touched sources md5-verified staged==device before edit.
- EXECUTION_BOUNDARY: Exactly the 9 failures' root causes; no drive-by refactors.
- DEPENDENCIES: BUG-005/007/045/046 regression suites as the contract spec;
  ticketing/technical_expertise laws (test-drift correction is outcome 3).
- EXIT_GATE: Owner 3.14t run green over the touched suites; REOPEN on red.
- FAILURE_ESCALATION: CONFLICT note if any fixed contract contradicts live source on re-read.

## Scope Boundaries
- In scope: counter_switch.py + its 2 suites; conduit.py link() guards; spellbook.py
  detach/reattach/destroy seams; conduit_ward.py _remove_contract; member_diff_strategy.py
  docstring; 2 stale MR group-diff tests.
- Out of scope: sever_link/unlink mirror of the guard-order defect (flagged below), dead
  `_sever_link_contract` retirement (still used by passing component/unit suites).

## Validation / Test Approach
Sandbox harness (CPython 3.12, pytest-shim runner): 23/23 green - full
test_counter_switch.py (15, incl. the 3 rewritten), full BUG-007 regression suite (5),
full test_group_diff_engine.py (3). py_compile green on all 8 files sandbox-side AND
device-side. Ward/conduit/spellbook suites and the MR compositions e2e: Not run (import
closure too heavy for the sandbox) - they ride the owner's next 3.14t run.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: All 9 root causes fixed and committed mtime-guarded; validation
  pending the owner run.

## Applicable Anti-Patterns
- [x] No fix from UNKNOWN: every family re-verified against live source before editing.
- [x] No defensive-guard sprawl: guards hoisted/removed per documented contracts only.

## Noting Behavior
- Task grain: tactical findings, immediate impacts, one-step continuation.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-07-18T19:50:00Z
  TYPE: FACT
  CLAIM: Family diagnoses, all source-verified. (1) BUG-005: tests + fakes (mtimes
    2026-07-18) specify detach/reattach/destroy seams that existed NOWHERE in production
    (grep: only tests) - the prior session's production half never landed on disk.
    (2) CounterSwitch.cleanup dels all four slots directly under a docstring that mandates
    retaining them (LoadGate tombstone law); the old suite still asserted the del posture -
    both sides of a half-landed helper_1 change. (3) Conduit.link opens the LINK transaction
    before the ward's self-link guard; the strategy's >=2-distinct-participants rule fires
    first with the admission-plane error. (4) BUG-046's version-truth pairing (strategy +
    resolver ancestor_spell_ids, both landed) is contradicted only by two stale pre-fix
    tests; the BUG-046 regression suite in test_mutation_research_root.py pins the
    tightened contract and passes.
  EVIDENCE:
  - tests/unit/melder/aether/conduit/conduit_ward/test_conduit_ward_sever_failure_atomicity_regression.py:82-214
  - src/melder/utilities/synchronization/counter_switch.py:87-126
  - src/melder/aether/conduit/conduit.py:3994-4000
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/link_transaction_strategy.py:165-187
  - src/melder/mutation_research/mutation_research.py:2696-2739
  - tests/unit/melder/mutation_research/test_mutation_research_root.py:730-780
  IMPACT: Direction settled per family: implement production (1), remove dels + update old
    suite (2), hoist guards (3), update stale tests to the landed contract (4).
  NEXT: Implement in that order; sandbox-run what the import closure allows.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-18T20:15:00Z
  TYPE: DECISION
  CLAIM: IMPLEMENTED + COMMITTED (8 files, mtime-guarded, CRLF/LF byte-fidelity verified
    per file, device py_compile green). (1) Spellbook gained _detach_link_contract
    (reversible five-map pop, None on residue, lockstep guard), _reattach_link_contract
    (exact restore, refuses overwrite), _destroy_detached_link_contract (pool release +
    staged-key refresh + risk-manager unregister over the DETACHED payload);
    ConduitWard._remove_contract rewritten to the three-phase protocol: detach A then B
    with exact-restore rollback on the second failure, residue-tolerant commit pops
    (registries AND direction indices), per-side loud best-effort destroy LAST;
    _sever_link_contract retained (still used by component/unit suites + line-3145 bulk
    teardown). (2) CounterSwitch.cleanup del block removed with a contract comment; the
    3 del-posture tests rewritten to the retained-terminal contract (renames:
    post_cleanup_usage_breaks_fast -> post_cleanup_reads_serve_terminal_idle_state,
    cleanup_drops_fast_state_mirror -> cleanup_zeroes_fast_state_mirror). (3) link() now
    guards self-link and lesser-target BEFORE transaction admission with the ward's exact
    messages; docstring Raises updated; ward guards stay as mutation-site defense.
    (4) Engine-test _material grew ancestor_spell_ids (sha-a2 -> [sha-a1]); e2e fixture
    registers sha-a2 with parent_spell_ids=["sha-a1"] (matching its own "two versions of
    one object" docstring); MemberDiffStrategy class Contract now states the BUG-046
    double-evidence law. VALIDATION: sandbox 23/23 green (both counter_switch suites +
    group_diff engine suite); ward/conduit/spellbook/e2e suites Not run here - owner run.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:2951-3131
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:941-1100
  - src/melder/aether/conduit/conduit.py:3997-4014
  - src/melder/utilities/synchronization/counter_switch.py:113-128
  - tests/unit/melder/utilities/synchronization/test_counter_switch.py:182-240
  - tests/unit/melder/mutation_research/test_mutation_research_compositions.py:52-80
  IMPACT: All 9 owner-run failures addressed at root cause; zero contested directions.
  NEXT: Owner reruns the full 3.14t suite; green -> close this task, red -> REOPEN with
    the failing row.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-18T20:15:00Z
  TYPE: RISK
  CLAIM: Mirror defect flagged, not fixed (scope law): sever_link/unlink shares the
    guard-after-admission shape - a self-sever would surface the admission-plane error
    before any ward guard, same as the fixed link case. No test currently demands it.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:4310-4360
  IMPACT: Same wrong-error class remains reachable on the sever door.
  NEXT: Owner decides whether to hoist the sever-door guards in a follow-up slice.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-07-18T20:45:00Z
  TYPE: DECISION
  CLAIM: REOPEN FALLOUT FIXED. The owner's rerun surfaced 2 new failures caused by the
    hoisted lesser-target guard: test_link_delegates_to_ward_and_fires_hook and
    test_link_false_does_not_fire_hook both passed LESSER-state targets as cheap fixture
    stand-ins for contracts that are actually about ward delegation and hook behavior -
    they only ever passed because the mocked ward swallowed the lesser semantics the
    integration guardrail test explicitly demands. The guard stands (right per the ward
    contract + the integration test); both tests repointed to NORMAL-built targets via the
    same _build_conduit helper. Reachability proof: the neighboring
    test_link_publishes_peer_record_when_target_participates_in_nexus builds a normal
    target with the identical helper, drives the full link() success path, and PASSED in
    the owner's run. The file has MIXED CRLF/LF line endings (150 lone-LF lines), so the
    whole-file conversion lane was refused by its roundtrip guard; edits were applied
    byte-exact per line with each line's own ending preserved, py_compile green sandbox +
    device. Suite itself: Not run (import closure) - rides the owner rerun.
  EVIDENCE:
  - tests/unit/melder/aether/conduit/test_conduit_contracts.py:232-238
  - tests/unit/melder/aether/conduit/test_conduit_contracts.py:295-360
  - tests/unit/melder/aether/conduit/test_conduit_contracts.py:268-292
  IMPACT: The guardrail contract and the delegation contracts no longer collide; no
    production change was needed for the fallout.
  NEXT: Owner reruns the suite; green -> close, red -> REOPEN with the failing row.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Closure Confirmation
- [ ] Owner 3.14t run green over the touched suites
- [ ] Acceptance confirmed by owner

## Context / Handoff Summary
All 9 failures from the owner's 2026-07-18 red run fixed at root cause and committed:
BUG-005 two-phase sever production halves implemented (spellbook seams + ward rewrite),
CounterSwitch retained-terminal cleanup enforced (dels removed, old suite modernized),
link() identity guardrails hoisted pre-admission, and the two stale pre-BUG-046 group-diff
tests updated to the landed version-truth contract. Sandbox 23/23 green where importable;
the rest rides the owner run. One flagged follow-up: the sever door shares the
guard-after-admission shape.
