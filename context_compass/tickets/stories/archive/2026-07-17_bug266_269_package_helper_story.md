# Story: BUG-266..269 - Package/Pack helper contract fixes

## Metadata
- Story ID: STORY-2026-07-17-bug266-269-package-helper
- Epic: EPIC-2026-07-17-bugfix-package-python-compat
- Status: review
- Owner: cowork
- Agent Name: helper_0
- Priority: p2
- Created: 2026-07-18T13:31:38Z
- Updated: 2026-07-18T13:31:38Z

## User Narrative
As a caller of the `Package`/`Pack` callable wrapper, I want its hash, normalization,
freeze, and post-cleanup contracts to hold, so it behaves correctly in sets/dicts, batch
normalization, frozen use, and after disposal.

## Value / MRP Alignment
These are public utility-contract violations in a shared helper. Even with no current
production caller, correct hash/lifecycle/immutability contracts are foundational MRP
hygiene for a public library.

## Ticket Contract
- ENTRY_GATE: Package epic in_progress (helper_0); BUG-001 already handled.
- EXECUTION_BOUNDARY: src/melder/utilities/helpers/package.py only, plus a regression test.
- DEPENDENCIES: audit report codex/2026-07-17_melder_bug_audit_package_helper_appendix.md.
- EXIT_GATE: each of BUG-266..269 fixed at root cause with a passing regression assertion; user suite green on 3.14t.
- FAILURE_ESCALATION: BUG-266 changes the public hashing contract (freeze-on-hash) - raise if the owner wants different semantics.

## Scope Boundaries
- In scope: package.py __hash__, _normalize_many, kwargs accessor, __getattr__.
- Out of scope: functional redesign of Package; other subsystems.

## State Transition Event
- from_state: ready
- to_state: review
- transition_reason: All four fixes applied at root cause and verified with a before/after repro; awaiting the user's full-suite run on 3.14t for acceptance.

## Tasks (Implementation Checklist)
- [x] Task: BUG-267 - _normalize_many preserves an existing Package (no double-wrap).
- [x] Task: BUG-268 - kwargs accessor returns a copy (mirrors args), keeping freeze/signature consistent.
- [x] Task: BUG-266 - freeze-on-hash keeps hash/membership stable for the object's lifetime.
- [x] Task: BUG-269 - __getattr__ raises the canonical cleaned RuntimeError instead of recursing.
- [x] Task: Add symptom-named regression test.
- [ ] Task: User runs the package suite on 3.14t (existing 15 tests + the new regression) and accepts.

## Acceptance Criteria
- All four repros show corrected behavior; the 15 existing package tests still pass on the user's 3.14t run.

## Validation / Test Plan
- Verified in-container (CPython 3.11; version-independent logic bugs) with a before/after repro:
  - BUG-266 original: mutate-after-set -> not in set; fixed: mutation blocked (frozen-on-hash), still in set.
  - BUG-267 original: TypeError (bindings lost); fixed: same object returned, invocation yields 3.
  - BUG-268 original: invoke=9 vs signature b=2; fixed: invoke=3, signature b=2 (consistent).
  - BUG-269 original: RecursionError x3; fixed: canonical RuntimeError x3.
- New pytest guard: tests/unit/melder/utilities/helpers/test_package_helper_bug266_269_regression.py.
- pytest is not installable in this cloud container (no index); the user runs the suite on 3.14t. Agent test-run status: Not run under pytest (logic verified via plain-python repro).

## Risks / Mitigations
- Risk: BUG-266 freeze-on-hash changes public hashing semantics (hashing now freezes bindings). Mitigation: it matches the audit's expected contract and reuses the existing freeze mechanism; flagged for owner review. If undesired, alternative is making Package unhashable-until-frozen.
- Risk: BUG-269 __getattr__ guard also makes describe() raise on a cleaned package instead of returning "Package(cleaned)". Mitigation: consistent with the canonical raise-on-cleaned contract the audit requests.

## Applicable Anti-Patterns
- [ ] No story-state transition without task evidence.
- [ ] No closure before the user's suite run confirms no regression.

## Decision Log
- DATETIME: 2026-07-18T13:31:38Z
  TYPE: DECISION
  CLAIM: BUG-266 fixed by freeze-on-hash (equality/hash derive from mutable bindings; freezing on first hash keeps membership stable). Chosen over unhashable-until-frozen to preserve current hashability. Flagged for owner review.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Notes
- DATETIME: 2026-07-18T13:31:38Z
  TYPE: MEASURE
  CLAIM: All four fixes verified by running the reported repros against original vs fixed package.py; every symptom flipped to corrected behavior.
  EVIDENCE:
  - src/melder/utilities/helpers/package.py:446-495
  - src/melder/utilities/helpers/package.py:636-678
  - src/melder/utilities/helpers/package.py:820-849
  - src/melder/utilities/helpers/package.py:866-895
  IMPACT: Closes BUG-266..269 pending the user's 3.14t suite run.
  NEXT: User runs pytest on 3.14t; then close.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
BUG-266..269 fixed in package.py at root cause and verified with a before/after repro; a symptom-named
regression test was added. Status review, pending the user's full package-suite run on 3.14t for acceptance.
