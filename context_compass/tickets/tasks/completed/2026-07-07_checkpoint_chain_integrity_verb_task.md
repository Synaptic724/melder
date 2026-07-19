# Task: Checkpoint chain-integrity verb (verify_checkpoint_chain)

## Metadata
- Task ID: TASK-2026-07-07-checkpoint-chain-integrity-verb
- Parent Epic: EPIC-2026-07-03-crystallizer-bootstrap-checkpoint
- Status: closed
- Owner: cowork
- Agent Name: melder_0
- Priority: p3
- Created: 2026-07-07T04:50:00Z
- Updated: 2026-07-07T13:00:00Z

## Problem / Opportunity
The restore engine folds a profile's checkpoint chain trusting its shape.
Nothing today can ANSWER whether a chain is fold-safe: retention dropout
truncates the prefix silently, and a damaged ledger (missing middle crystal,
overlapping windows) would fold into a wrong world. One read-only verb closes
B4's residue: report chain health BEFORE anyone folds it.

## MRP Alignment
Diagnostic honesty for the restore lane: cheap, read-only, no new state.

## Ticket Contract
- ENTRY_GATE: bootstrap epic active; rides patch lane
  restore_engine_2026_07_07 (additive verb on the same component).
- EXECUTION_BOUNDARY: PersistenceSystem.verify_checkpoint_chain + the
  Crystallizer facade passthrough + unit tests. Read-only; no ledger
  mutation; no runtime surfaces.
- DEPENDENCIES: sealed-ledger semantics (checkpoint_number per profile,
  sequence_range windows, insertion-order FIFO dropout).
- EXIT_GATE: verb reports intact / truncated_prefix / broken with break
  evidence; tests authored; owner-run 3.14t green.
- FAILURE_ESCALATION: DECISION_REQUEST if verdict vocabulary needs owner
  taste; CONFLICT if persistence/** is edited concurrently by another agent.

## Goals
- verify_checkpoint_chain(profile_name=None -> active profile): detached
  report {profile_name, ledger_count, first/last checkpoint numbers,
  dropped_prefix_count, breaks[], empty_windows[], verdict}.
- Verdicts: "intact" (contiguous from 1), "truncated_prefix" (contiguous but
  retention dropped the head - fold yields a POST-PREFIX world), "broken"
  (number gap, duplicate number, or non-contiguous windows - fold unsafe).

## Non-Goals
- Repairing chains; cache-side verification (adapter lane); restore changes.

## Acceptance Criteria
- Intact, truncated, and broken chains classify correctly with evidence
  rows; empty windows report without breaking the verdict; unknown profile
  raises the standard KeyError; owner accepts.

## Applicable Anti-Patterns
- [ ] No ledger mutation from a diagnostic verb.
- [ ] No verdict without break evidence rows.

## Noting Behavior
- Task notes: tactical findings, immediate impacts, one-step continuation.

## Notes
- DATETIME: 2026-07-07T04:50:00Z
  TYPE: PLAN
  CLAIM: Implement PersistenceSystem.verify_checkpoint_chain (creation-order
    walk of one profile's ledger run; number contiguity, window contiguity
    range[i].first == range[i-1].last + 1, empty-window tolerance
    first == last + 1) + Crystallizer facade + unit suite.
  EVIDENCE:
  - src/melder/crystallizer/persistence/persistence_system.py:702-773
  IMPACT: Fold-safety becomes checkable before restore.
  NEXT: Implement + tests, then note results.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-07-07T05:15:00Z
  TYPE: FACT
  CLAIM: LANDED. verify_checkpoint_chain on PersistenceSystem (+ Crystallizer
    facade): creation-order run walk, duplicate/gap/window-discontinuity/
    inverted-window break rows, empty-window tolerance, verdicts intact/
    truncated_prefix/broken/empty; full-dropout restarts caught via the first
    retained window starting past sequence 1. BONUS BUG the verb's design
    exposed and fixed: _next_checkpoint_number minted from the retained COUNT
    - once FIFO dropout engages the count stalls and numbers DUPLICATE (drop
    #1 of a full cap, next mint re-issues the tail number). Now mints
    highest-retained + 1 (monotonic under retention). 8 unit tests authored
    (intact, empty ledger, empty windows, retention truncation + no-dup mint,
    full-dropout restart, missing-middle broken evidence, forged duplicate,
    guards); one self-caught assertion fix (restart numbering is 1, not 2).
    VALIDATION: test file py_compile OK in-sandbox; persistence_system/
    crystallizer compile Not run (replica rot; disk verified via file-tool
    reads). Owner runs 3.14t.
  EVIDENCE:
  - src/melder/crystallizer/persistence/persistence_system.py:945-1085
  - src/melder/crystallizer/persistence/persistence_system.py:1087-1120
  - src/melder/crystallizer/crystallizer.py:1235-1263
  - tests/unit/melder/crystallizer/persistence/test_checkpoint_chain_integrity.py:1-186
  IMPACT: B4 residue closed on disk; the restore lane can gate folds on the
    verdict later if the owner wants belt-and-suspenders.
  NEXT: Owner-run 3.14t; on green, walk acceptance criteria for closure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-07T13:00:00Z
  TYPE: FACT
  CLAIM: CLOSED - acceptance walk on owner-run GREEN (all suites passed
    across runs 3-6). Criteria: (1) verify_checkpoint_chain reports
    intact/truncated_prefix/broken/empty with break evidence rows - PROVEN
    by 8 unit tests incl. forged duplicates, popped middles, full-dropout
    restart detection; (2) Crystallizer facade passthrough activation-gated
    - LANDED; (3) the latent count-based numbering duplicate under
    retention dropout - FIXED (highest+1) and regression-tested; (4) empty
    windows tolerated and listed - PROVEN. The verb also became the kit
    export gate design input (epic design note). Closure per owner-run
    green + owner "keep going" directive.
  EVIDENCE:
  - src/melder/crystallizer/persistence/persistence_system.py
    (verify_checkpoint_chain + _next_checkpoint_number)
  - tests/unit/melder/crystallizer/persistence/test_checkpoint_chain_integrity.py
  IMPACT: B4 residue closed; fold-safety checkable before any restore.
  NEXT: none (closed).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Small read-only diagnostic verb under the bootstrap epic, riding the
restore_engine_2026_07_07 patch lane. Reports chain fold-safety.
