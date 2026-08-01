# Story: Build the standalone AethericMediator core plane

## Metadata
- Story ID: STORY-2026-07-31-aetheric-mediator-core
- Epic ID: EPIC-2026-07-31-aetheric-mediator-subsystem
- Status: in_progress
- Owner: cowork
- Agent Name: helper_f
- Priority: p1
- Created: 2026-07-31T23:00:41Z
- Updated: 2026-07-31T23:00:41Z

## Problem / Opportunity
The plane must exist and be trustworthy STANDALONE before any subsystem is wired
to it. Ship it as an isolated, independently testable package.

## Ticket Contract
- ENTRY_GATE: epic open, owner directive given.
- EXECUTION_BOUNDARY: `src/melder/aether/aetheric_mediator/` ONLY. No edits to
  Aether, MR, Nexus, or Crystallizer under this story.
- DEPENDENCIES: `melder.utilities` only.
- EXIT_GATE: core vocabulary + claim table + session + mediator exist, tested,
  with a test proving zero `melder.aether` imports.
- FAILURE_ESCALATION: BLOCKER if a core component cannot be built without
  reaching into Aether - that would invalidate constraint 4.

## Goals
- Claim vocabulary (modes + compatibility matrix) that all three subsystems share.
- Atomic all-or-nothing multi-scope acquisition with blocking evidence.
- Sessions carrying status, rollback actions, and the two-outcome failure policy.
- A mediator front door with per-identity root sessions and same-thread joins.

## Non-Goals
- Wiring anything. Separate story.
- Strategy families for MR/Nexus/Crystallizer - only the ABC + registry seam.

## Naming (owner ruling 2026-07-31)
NO `Aetheric` PREFIX AND NO `Change` PREFIX on class names. The PACKAGE is
`aetheric_mediator/`; the classes inside are plain: `Mediator`, `Identity`,
`ClaimTable`, `TransactionType`, `TransactionRequest`, `AdmissionResult`. Do not
re-theme them. `AethericIdentity` and `AethericClaimTable` were renamed to
`Identity` and `ClaimTable` (files `identity.py`, `claim_table.py`) under this
ruling.

## Build Order (tranches)
- [x] T1: claim modes + compatibility matrix (verified against DevOps embargo)
- [x] T2: claimant identity
- [x] T3: claim table (atomic acquire / release / blocking evidence)
- [x] T4: transaction vocabulary + frozen request + admission verdict
- [ ] T5: admission orchestrator (one acquisition under the admission lock)
- [ ] T6: session (status, join/leave, rollback actions, abort pipeline,
      OUTCOME POLICY: unwind | leave_broken)
- [ ] T7: mediator front door + transaction manager (ingress, per-identity root
      sessions, same-thread joins, bounded wait)
- [ ] T8: strategy ABC + registry + staged transaction
- [ ] T9: information registry + information strategies (fact baselines + live
      activity indexes - the reporting half)
- [ ] T10: root wiring (the object Aether holds)
- [ ] T11: unit tests incl. the no-melder.aether-import test and a concurrency
      proof

## Deliberate Divergences From DevOps (each with a reason)
- `scope_claims` IS COMPLETE AND EXPLICIT - every scope key carries its own
  mode, with NO implicit default. DevOps defaults absent keys to exclusive at
  admission. Implicit defaulting is how a caller silently takes a whole-world
  exclusive claim it never requested, which is the exact failure this plane
  exists to end. Cost: one tuple entry. Benefit: a class of accident removed.
- NO SCOPE HASHES. DevOps carries them as advisory identity evidence that
  explicitly "carry no claims". With no consumer here they are dead weight; add
  them back only when something reads them.
  *** PROVISIONAL - COUPLED TO EPIC-2026-08-01-conflict-manager-zombie. ***
  The retired DevOps conflict scan matched on HASHES while the claim table
  matches on KEYS, which are different notions of overlap. If that epic finds
  hash-overlap detection was load-bearing, this plane inherits the same gap by
  construction and the decision must be reopened BEFORE wiring.
- `ChangeControlConflictManager` NOT PORTED. CORRECTION: it is not "retired" in
  DevOps - it is a ZOMBIE. Still constructed, slotted, cleaned, publicly exposed
  and threaded into the orchestrator and mediator, but `find_conflicts` has ZERO
  call sites and the orchestrator accepts it "for signature compatibility only".
  Not porting it is still correct; the reason is just different from the one
  originally recorded here.

## Notes
- DATETIME: 2026-07-31T23:00:41Z
  TYPE: PLAN
  CLAIM: Tranches T1-T3 bootstrapped in this pass; T4-T8 remain.
  EVIDENCE:
  - src/melder/aether/aetheric_mediator/claim_mode.py
  - src/melder/aether/aetheric_mediator/identity.py
  - src/melder/aether/aetheric_mediator/claim_table.py
  IMPACT: The claim vocabulary is the foundation every other tranche sits on, so
    it is deliberately first and deliberately small.
  NEXT: T4 - transaction request + outcome policy.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7
- DATETIME: 2026-07-31T23:00:41Z
  TYPE: FACT
  CLAIM: T4 landed - `TransactionType` (closed StrEnum, 6 provisional members
    each traceable to a real operation), `TransactionRequest` (frozen, value-only,
    complete explicit scope claims, sorted at the construction boundary), and
    `AdmissionResult` + `AdmissionReason` (evidence-not-a-bool, fully detached
    strings). Package compiles; the only external import across all six modules
    is `melder.utilities.general_base.cleanable`.
  EVIDENCE:
  - src/melder/aether/aetheric_mediator/transaction_type.py
  - src/melder/aether/aetheric_mediator/transaction_request.py
  - src/melder/aether/aetheric_mediator/admission_result.py
  IMPACT: The three value-layer pieces are in place, so T5 admission has a
    request to adjudicate and a verdict shape to return.
  NEXT: T5 - the admission orchestrator.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Acceptance Criteria
- Zero imports of `melder.aether` anywhere in the package, enforced by test.
- Mode compatibility matrix tested directly (s/s and ix/ix coexist; x excludes).
- Concurrent acquisition proven all-or-nothing (no partial claim sets survive).
- Every public class and method carries a rich docstring per repo standard.
- Cleanup is idempotent and deletes owned fields.

## Applicable Anti-Patterns
- [ ] No `melder.aether` import inside the package.
- [ ] No module-level mutable state or module-level constants.
- [ ] No PEP 604 unions; Optional/Union only.
- [ ] No dataclasses holding object references.

## Validation / Test Approach
Not run. `pytest tests/unit/melder/aether/aetheric_mediator -q` once tests exist.

## Notes
- DATETIME: 2026-07-31T23:00:41Z
  TYPE: PLAN
  CLAIM: Tranches T1-T3 bootstrapped in this pass; T4-T8 remain.
  EVIDENCE:
  - src/melder/aether/aetheric_mediator/claim_mode.py
  - src/melder/aether/aetheric_mediator/aetheric_identity.py
  - src/melder/aether/aetheric_mediator/aetheric_claim_table.py
  IMPACT: The claim vocabulary is the foundation every other tranche sits on, so
    it is deliberately first and deliberately small.
  NEXT: T4 - transaction request + outcome policy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Standalone package. The one rule that matters: it must not import
`melder.aether`. Everything else follows from that.
