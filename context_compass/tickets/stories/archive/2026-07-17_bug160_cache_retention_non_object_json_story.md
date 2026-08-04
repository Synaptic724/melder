# Story: BUG-160 - Valid non-object JSON aborts cache retention instead of being reclaimed

## Metadata
- Story ID: STORY-2026-07-17-bug160-cache-retention-non-object-json
- Epic: EPIC-2026-07-17-bugfix-crystallizer-persistence
- Status: review
- Owner: cowork
- Agent Name: helper_0
- Priority: p2
- Severity: Medium
- Created: 2026-07-18T16:09:15Z
- Updated: 2026-07-18T16:09:15Z

## Root Cause (verified against current source + runtime repro)
CrystallizerCache.enforce_cache_retention sorts cached files by a _creation_order key that
does json.loads(...).get('checkpoint_number'). It catches only (OSError, ValueError), so a
file whose JSON parses cleanly but is NOT an object - a list, null, or scalar (e.g. '[]') -
reaches .get() and raises AttributeError. Because _creation_order is the sorted() key, the
whole retention pass aborts and NOTHING is reclaimed: one structurally invalid file
permanently blocks FIFO cleanup for its profile (audit BUG-160, crystallizer_cache.py:201-220).

## Fix (root cause)
Guard the payload shape: only a dict payload can carry a checkpoint_number, so wrap the
.get() in `if isinstance(payload, dict):`. Any non-object JSON falls through to the dead-weight
key (0, 0, name) and reclaims first - exactly the audit's expected behavior. No broadening of
the except clause (that would be defensive-guard sprawl masking the real contract).

## Scope Boundaries
- In scope: crystallizer_cache.py enforce_cache_retention/_creation_order + a regression.
- Out of scope: other cache verbs; unrelated bugs.

## Tasks (Implementation Checklist)
- [x] Re-verify BUG-160 against current source (except misses AttributeError on non-dict JSON).
- [x] Guard payload with isinstance(dict) so non-object JSON sorts as dead weight.
- [x] Run a real before/after cache-retention repro.
- [x] Add a regression (a '[]' file beside a valid checkpoint, cap 1).
- [ ] User runs the crystallizer-cache suite on 3.14t and accepts.

## Acceptance Criteria
- A non-object JSON file is reclaimed as dead weight (retention no longer raises); valid
  checkpoints are retained by recorded number; the suite is green on the user's 3.14t run.

## Validation / Test Plan
- VERIFIED with the REAL CrystallizerCache in-container (stdlib-only deps: Cleanable): a before/
  after repro over a temp cache dir with a valid checkpoint + a '[]' file at cap 1.
    - ORIGINAL: enforce_cache_retention raised AttributeError: 'list' object has no attribute 'get'.
    - FIXED: removed=['01AAA','BAD'] (dead weight + oldest), remaining=['01BBB.json']; no error.
- py_compile OK. Regression added to test_crystallizer_cache.py (uses the cache_root tmp fixture).
- Full pytest module Not run in-container (the test file imports AetherCrystal/PersistenceSystem
  at module load, which need 3.14t). Agent test-run status: real cache repro PASSED; pytest suite Not run.

## Risks / Mitigations
- Risk: a dict payload without checkpoint_number now still sorts as dead weight (unchanged from
  before). Mitigation: pre-existing behavior; only the non-object crash path changed.

## Applicable Anti-Patterns
- [x] Reproduced before fixing (real runtime repro).
- [x] Root-cause (shape guard), not a broadened blanket except.
- [ ] No closure before the user's suite run.

## Decision Log
- DATETIME: 2026-07-18T16:09:15Z
  TYPE: DECISION
  CLAIM: Guard the payload shape with isinstance(dict) rather than adding AttributeError to the except; the type check states the real contract (a checkpoint payload is an object) instead of swallowing a class of programming errors.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Notes
- DATETIME: 2026-07-18T16:09:15Z
  TYPE: MEASURE
  CLAIM: Real before/after repro: original raises AttributeError; fixed reclaims the non-object file as dead weight and keeps the newest valid checkpoint.
  EVIDENCE:
  - src/melder/crystallizer/asset_management/crystallizer_cache.py:201-224
  - codex/2026-07-17_melder_bug_audit_persistence_profile_cache_appendix.md:50-68
  IMPACT: One malformed-but-parseable JSON file can no longer wedge a profile's cache cleanup.
  NEXT: User runs the cache suite on 3.14t; then close.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
BUG-160 fixed at root cause with a payload-shape guard; a non-object JSON file now reclaims as
dead weight instead of crashing retention. Verified with the real cache in-container. Status
review; only BUG-163 (Medium) remains in story 06.
