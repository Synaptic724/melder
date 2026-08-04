# Story: BUG-159 - Checkpoint retention drops a baseline the integrity gate still certifies restorable

## Metadata
- Story ID: STORY-2026-07-17-bug159-checkpoint-retention-restorability
- Epic: EPIC-2026-07-17-bugfix-crystallizer-persistence
- Status: review
- Owner: cowork
- Agent Name: helper_0
- Priority: p0
- Severity: Critical
- Created: 2026-07-18T13:55:19Z
- Updated: 2026-07-18T13:55:19Z

## User Narrative
As an operator who relies on the crystallizer checkpoint ledger for disaster
recovery, I need the chain-integrity gate to tell the truth about whether a
retained chain can still be folded back to the live world, so I never restore a
world that is silently missing state retention evicted.

## Root Cause (verified against current source)
Checkpoints are INCREMENTAL: each PersistenceCrystal captures only what changed
in its window; composing the world at checkpoint K folds the profile chain 1..K,
later payloads winning per (kind, key) (persistence_crystal.py class contract).
`create_checkpoint` runs a FIFO dropout (persistence_system.py:958-965) that
evicts the oldest crystal outright when the ledger exceeds the retention cap - it
does NOT compact the evicted payloads forward into the surviving baseline. When
the evicted head uniquely held some live unit (e.g. Nexus state) that no later
incremental re-captures, that state is gone from every surviving crystal.
`verify_checkpoint_chain` (persistence_system.py:1120-1258) meanwhile classified
the truncated survivor as verdict 'truncated_prefix', documented as 'a fold
yields the post-prefix world' and treated as usable - so the integrity gate
declared a chain restorable that could only rebuild a world MISSING the evicted
state. That is the Critical data-loss path (audit: persistence_profile_cache_appendix BUG-159).

## Fix (owner-directed: fail-closed classification)
Per the owner's direction, remediate via the audit's sanctioned option 'the
surviving chain must be classified unrestorable/incomplete' rather than changing
retention. `verify_checkpoint_chain` now returns an explicit `restorable` boolean
that is True ONLY for a fully intact chain (baseline retained: first checkpoint
number 1 AND first window sequence 1, contiguous, no breaks). A 'truncated_prefix',
'broken', or 'empty' report is restorable=False. The verb sees only structure,
never payloads, so once the prefix is dropped it CANNOT prove the evicted baseline
carried no unsuperseded state - therefore it fails closed and refuses to certify.
The verdict strings are unchanged (backward compatible); `restorable` is an
additive key and the docstring redefines 'truncated_prefix' as not restorable.

## Scope Boundaries
- In scope: src/melder/crystallizer/persistence/persistence_system.py
  (verify_checkpoint_chain only) + tests/unit/melder/crystallizer/persistence/
  test_checkpoint_chain_integrity.py (guards + BUG-159 regression).
- Deliberately OUT of scope (residual, flagged below): retention still evicts
  (no compaction), and the restore engine is not re-wired to consult the gate.

## Residual / Follow-ups (flagged for owner)
- This fix makes the integrity gate HONEST (detects + refuses to certify). It does
  NOT by itself prevent the eviction, nor auto-refuse a restore: the restore engine
  (crystal_loader_system) runs its OWN S4 preflight admission verdict
  (clean/warnings/blockers) and does not currently consult verify_checkpoint_chain.
  Grep confirms NO code consumes the chain verdict, so nothing regresses; but full
  fail-closed-on-restore requires a separate DECISION: either (B) compact evicted
  payloads into the surviving baseline on eviction (prevents the loss; needs a
  PersistenceCrystal baseline marker + serialization change + RecordVersion major
  bump), or wire the loader admission to gate on `restorable`. Recommended next.

## Tasks (Implementation Checklist)
- [x] Re-verify BUG-159 against current source (retention FIFO + verdict logic).
- [x] Add fail-closed `restorable` to verify_checkpoint_chain (intact-only True).
- [x] Redocument the verdict contract (truncated_prefix = not restorable).
- [x] Update existing integrity tests to guard `restorable`.
- [x] Add symptom-named BUG-159 regression (Nexus then unrelated MutationResearch, cap 1).
- [ ] User runs the persistence suite on 3.14t (existing + new) and accepts.
- [ ] Owner decision on loss-prevention follow-up (compaction / restore-gate wiring).

## Acceptance Criteria
- verify_checkpoint_chain reports restorable=False for any retention-truncated or
  broken chain and True only for an intact baseline chain; the persistence suite
  (existing 9-plus integrity tests + the BUG-159 regression) is green on the user's 3.14t run.

## Validation / Test Plan
- Logic verified IN-CONTAINER (CPython 3.11) by executing a faithful transcription
  of the fixed decision core across 7 scenarios - intact, empty, BUG-159 dropped
  baseline (different state), same-state dropout, full-dropout restart, broken gap,
  and empty-window marker - all produced the expected (verdict, restorable) pair.
- py_compile OK on both changed files.
- Full pytest NOT run in-container: the test imports the melder package root chain
  (PersistenceProfile/SpellCrystal/...), which targets 3.14t; no package index here.
  Agent test-run status: Not run under pytest - the user runs the suite on 3.14t.

## Risks / Mitigations
- Risk: additive return-shape change (`restorable` key). Mitigation: purely additive;
  verdict strings unchanged; grep shows no external consumer of the report.
- Risk: detection without prevention could read as 'fixed' while a naive caller still
  restores. Mitigation: explicitly flagged as residual; no current caller consults the
  verdict; loss-prevention follow-up recommended for owner decision.

## Applicable Anti-Patterns
- [x] Reproduced/verified before fixing (source re-verify + logic simulation); no fix from HYPOTHESIS.
- [x] Root-cause classification, not defensive-guard sprawl.
- [ ] No closure before the user's suite run confirms green.

## Decision Log
- DATETIME: 2026-07-18T13:55:19Z
  TYPE: DECISION
  CLAIM: Fix BUG-159 by making verify_checkpoint_chain fail closed (explicit restorable, intact-only True) - the audit-sanctioned 'classify unrestorable/incomplete' remedy, chosen by the owner over compaction (record-format bump) and baseline-pinning (soft cap). Loss-prevention (compaction / restore-gate wiring) deferred to a flagged follow-up.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Notes
- DATETIME: 2026-07-18T13:55:19Z
  TYPE: MEASURE
  CLAIM: Fixed verdict core exercised across 7 scenarios; the BUG-159 dropped-baseline case flips from certified-usable to restorable=False, intact stays True.
  EVIDENCE:
  - src/melder/crystallizer/persistence/persistence_system.py:1120-1266
  - tests/unit/melder/crystallizer/persistence/test_checkpoint_chain_integrity.py:BUG-159 regression
  - codex/2026-07-17_melder_bug_audit_persistence_profile_cache_appendix.md:30-48
  IMPACT: Integrity gate no longer certifies a chain it cannot fold to the true world.
  NEXT: User runs the persistence suite on 3.14t; owner decides on loss-prevention follow-up.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
BUG-159 (Critical) fixed at the integrity gate: verify_checkpoint_chain now fails
closed with an explicit restorable flag (intact-only). Retention still evicts and
the restore engine is not re-wired - loss-prevention is a flagged owner follow-up.
Status review, pending the user's 3.14t suite run.
