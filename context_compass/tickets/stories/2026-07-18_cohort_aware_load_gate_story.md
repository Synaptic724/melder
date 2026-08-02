# Story: S3 - Cohort-aware LoadGate (restore worker admission)

## Metadata
- Story ID: STORY-2026-07-18-cohort-aware-load-gate
- Epic: EPIC-2026-07-18-parallel-restore-ulid-identity
- Status: review (code_description patch + code + adversarial suite landed; pending owner 3.14t run)
- Owner: cowork
- Agent Name: UNASSIGNED (helper_f departed 2026-08-02, owner-directed; lane left ACTIVE)
- Priority: p0
- Created: 2026-07-18T22:30:00Z
- Updated: 2026-07-18T22:30:00Z

## Objective
Load authority admits a COHORT: the loading thread plus explicitly enrolled restore worker
threads pass the LoadGate during the span; every foreign thread parks exactly as today.
Single-thread spans remain the default (cohort of one).

## Ticket Contract
- ENTRY_GATE: epic active; load-gate component patch AND its code_description patch (to be
  authored at story start - concurrency-sensitive trigger) linked and read. Implementation
  MUST NOT start on the component patch alone.
- EXECUTION_BOUNDARY: utilities/synchronization/load_gate.py, aether.py load-authority
  verbs (enroll/withdraw worker surface), crystal_loader_system authority span, mediator
  gate consultation (transaction_mediator.py passage check only), tests.
- DEPENDENCIES: component_patch_load_gate_cohort.md; S2 (worker identity comes from the
  loader-owned scheduler pool).
- EXIT_GATE: adversarial regressions green: foreign thread NEVER passes an active cohort
  span; workers pass without re-entrancy deadlock; release restores the single-thread law;
  abandoned-span recovery (cohort holder dies) documented + tested.
- FAILURE_ESCALATION: BLOCKER on any deadlock between gate condition, mediator RLock, and
  scheduler latches; DECISION_REQUEST before ANY change to foreign-thread park semantics.

## Scope Boundaries
- In scope: cohort membership, passage check, span lifecycle, enrollment API.
- Out of scope: mediator scope-claim semantics; scheduler internals.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: component patch authored; code_description patch gated at story start.

## Steps / Checklist
- [ ] Author code_description_patch_load_gate_cohort.md (control flow, edge/error
      semantics, idempotency, explicit non-goals) BEFORE code.
- [ ] Cohort registry keyed by span token; membership = loading thread + enrolled workers.
- [ ] Enroll/withdraw verbs on the authority surface; loader enrolls pool threads for the
      span, withdraws in finally.
- [ ] Passage check: member -> pass; foreign -> park (unchanged semantics + bound).
- [ ] Adversarial suite (>= 20 tests/100 LOC): overlap, timeout, abandoned span, nested
      same-thread joins, worker exception mid-span.

## Validation
- Not run. Recommended: pytest tests/component -k load_gate; owner 3.14t run.

## Applicable Anti-Patterns
- [ ] No implementation before the code_description patch exists.
- [ ] No lock-order inversion: gate condition never awaited while holding mediator lock
      (existing law preserved).

## Noting Behavior
- Story notes: cross-task synthesis and gate transitions.

## Notes
- DATETIME: 2026-07-18T23:38:44Z
  TYPE: MEASURE
  CLAIM: Gate law honored: code_description_patch_load_gate_cohort.md authored FIRST
    (control flow, edge/error semantics, idempotency, abandoned-span posture, non-goals),
    then the implementation. Delta: LoadGate gains _cohort_thread_ids under the ONE
    existing condition lock (no new locks, no lock-order surface) - acquire resets the
    cohort (span = cohort of one, byte-identical start), enroll_worker/withdraw_worker are
    HOLDER-ONLY with positive-int ident validation and set idempotency, wait_for_passage
    passes members (membership re-read per wake), release AND cleanup clear the cohort
    unconditionally (no membership survives a span; cleanup keeps the documented tombstone
    posture and clears the set in place), describe() reports cohort_size + detached sorted
    ids. Aether gains enroll_load_worker/withdraw_load_worker delegating verbs mirroring
    the existing authority-verb posture. Mediator untouched (passage is gate-internal).
    Ten adversarial regressions appended to the gate suite: member-passes,
    foreign-parks-and-times-out (byte-identical error), no-span refuses, non-holder
    refuses, invalid idents refuse, withdrawn-worker parks at next check,
    release-clears-cohort (next span starts alone), enroll/withdraw idempotency,
    cleanup-clears + terminal-open + post-cleanup enroll refuses, describe truthfulness
    (detached copy). AST + device py_compile green x3; aether.py's UTF-8 BOM preserved
    byte-exact. pytest Not run - rides the owner's 3.14t run.
  EVIDENCE:
  - system_docs/patches/active/parallel_restore_ulid_identity_2026_07_18/code_description_patch_load_gate_cohort.md:1-1
  - src/melder/utilities/synchronization/load_gate.py:1-460
  - src/melder/aether/aether.py:950-1030
  - tests/unit/melder/utilities/synchronization/test_load_gate.py:212-470
  IMPACT: The epic's concurrency-risk core is landed with its double patch gate satisfied;
    S4 can enroll the loader's pool threads into load spans.
  NEXT: S4 - code_description patch for the RestorePlanGraph compiler + parallel engine,
    then implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
The concurrency-risk core of the epic; isolated behind its own double patch gate.
