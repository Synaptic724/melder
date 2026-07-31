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

## Build Order (tranches)
- [x] T1: claim modes + compatibility matrix
- [x] T2: claimant identity
- [x] T3: claim table (atomic acquire / release / blocking evidence)
- [ ] T4: transaction request + outcome policy
- [ ] T5: session (status, join/leave, rollback actions, abort pipeline)
- [ ] T6: mediator front door (ingress, root sessions, joins, bounded wait)
- [ ] T7: strategy ABC + registry seam
- [ ] T8: unit tests incl. the no-Aether-import test and a concurrency proof

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
