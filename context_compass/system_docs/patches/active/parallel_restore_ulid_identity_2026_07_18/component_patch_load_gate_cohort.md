# Component Patch: cohort-aware LoadGate (S3)

Lane: parallel_restore_ulid_identity_2026_07_18. Ticket: STORY-2026-07-18-cohort-aware-load-gate.
GATE NOTE: implementation additionally requires code_description_patch_load_gate_cohort.md
(control flow, edge/error semantics, idempotency, non-goals) authored at story start -
concurrency-sensitive trigger per patch_framework_gating.md.

## Before
- Load authority is thread-keyed: "while a crystallizer load holds system authority, the
  loading thread passes free and all other threads park until release"
  (transaction_mediator.py:140-143). The loader claims the span in load_checkpoint /
  restore_formation_record (crystal_loader_system.py:166-187). A parallel restore's own
  worker threads would therefore park at the gate their restore claimed - the direct
  blocker for scheduler-driven replay.

## After
- The span holds a cohort: the loading thread plus threads explicitly enrolled for that
  span token. Passage check: cohort member -> pass; foreign -> park (identical park
  semantics and wait bound as today). Default span with no enrollments is a cohort of one -
  byte-identical to current behavior.
- Aether authority surface gains enroll_load_worker(thread_ident) /
  withdraw_load_worker(thread_ident), legal only while the span is held by the calling
  loader; release clears the cohort unconditionally (no membership survives a span).
- The loader enrolls its scheduler pool threads after span acquisition and withdraws in
  finally; abandoned spans (holder dies) release cohort + authority together.

## Interface Deltas
- LoadGate: span token carries a member set; membership verbs; passage consults membership.
- Aether: enroll/withdraw verbs delegating to the gate (borrowed, never cleaned here).
- TransactionMediator: passage check callsite only; NO change to scope-claim admission,
  nested-join law, or wait bounds.

## State / Failure Deltas
- New failure: enroll outside an active span -> RuntimeError (fail-fast, loud message).
- Lock-order law preserved: the gate condition is never awaited while holding the mediator
  lock; membership reads are gate-local.

## Dependency / Ordering
- Depends on S2 (pool thread identities); consumed by S4. Foreign-thread semantics are a
  frozen contract: any change is a DECISION_REQUEST, not a story-local call.

## Validation Expectations
- Adversarial suite (>= 20 tests/100 LOC): foreign thread never passes an active cohort
  span; member passes without re-entrant deadlock; withdraw mid-span parks that thread;
  release restores single-thread law; abandoned-span recovery; nested same-thread joins
  never consult the gate (existing law). Owner-run 3.14t.
