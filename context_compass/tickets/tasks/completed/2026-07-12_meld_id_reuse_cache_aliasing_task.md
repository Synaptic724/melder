- Completed: 2026-07-12T21:00:00Z
- Summary: All four cache lanes (conduit_meld x2, spellspace_meld x2) now
  SKIP the input-resolution cache for unhashable inputs (TypeError ->
  cache_key None; store guarded) - raw id() keys no longer outlive their
  objects. Old id-fallback unit rewritten to the skip-cache law + 2-test
  integration regression (poisoned key never served; skip lane writes
  nothing). Closed on owner directive; pytest Not run by agent - reopen
  on red.

# Task: meld input-resolution cache id()-reuse aliasing fix

## Metadata
- Task ID: TASK-2026-07-12-meld-id-reuse-cache-aliasing
- Parent: none (owner-directed fix, 2026-07-12)
- Status: in_progress
- Owner: cowork
- Agent Name: melder_0
- Priority: p1
- Created: 2026-07-12T16:50:00Z
- Updated: 2026-07-12T16:50:00Z

## Problem / Opportunity
Owner finding: both meld doors' input-resolution caches fall back to
`(spell_name, id(spell), id(spellframe), binding_name)` keys when the
inputs are unhashable, and the cache stores those raw integers. id()
values outlive their objects: CPython reuses a dead object's address,
so a LATER unhashable object can hit the DEAD object's cache entry and
meld the wrong spell. Four sites: conduit_meld.py:263-270 + :460-467,
spellspace_meld.py:285-292 + :475-482.

## Ticket Contract
- ENTRY_GATE: owner directive ("look into this next"); routed on
  attention_board.md.
- EXECUTION_BOUNDARY: the four unhashable-fallback blocks + their store
  guards; NO change to the hashable-key hot path, the fast door, or
  resolution semantics.
- DEPENDENCIES: none.
- EXIT_GATE: unhashable inputs bypass the cache entirely (resolve
  every call); hashable caching byte-identical; regression test proves
  no stale hit across id reuse; owner-run green.
- FAILURE_ESCALATION: BLOCKER note if any caller depends on the id()
  fallback for correctness (none expected - it was a best-effort lane).

## Acceptance Criteria
- TypeError fallback sets cache_key None (skip-cache lane) at all four
  sites; the store is guarded on cache_key presence.
- Hashable-input caching behavior unchanged.
- Regression test: two distinct unhashable inputs never alias.

## Applicable Anti-Patterns
- [ ] No hot-path cost added to the hashable lane.
- [ ] No claim that pytest ran (owner runs; agent reports "Not run.").

## Noting Behavior
- Task notes: tactical findings, immediate impacts, one-step
  continuation.

## Notes
- DATETIME: 2026-07-12T16:50:00Z
  TYPE: FACT
  CLAIM: Owner finding source-verified at all four sites: the
    unhashable fallback builds id()-keyed entries and the shared store
    line caches them like any key (e.g. conduit_meld.py:261-290 -
    fallback :263-270, store :285-290). Unhashable meld inputs are the
    rare/exotic lane (classes, strings, Protocols - the dominant inputs
    - are all hashable), so skip-cache is strictly safer with no
    hot-path cost: the TypeError branch only fires for inputs that
    could alias.
  EVIDENCE:
  - src/melder/aether/conduit/meld/conduit_meld.py:261-290
  - src/melder/aether/conduit/meld/conduit_meld.py:458-487
  - src/melder/aether/conduit/meld/spellspace_meld.py:283-312
  - src/melder/aether/conduit/meld/spellspace_meld.py:473-502
  IMPACT: a freed unhashable input's address reuse can currently serve
    a stale spell resolution - a real wrong-object bug under allocation
    churn on 3.14t.
  NEXT: apply the skip-cache fallback at all four sites + regression
    test.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-12T17:15:00Z
  TYPE: FACT
  CLAIM: FIX LANDED at all four sites: the TypeError fallback now sets
    cache_key=None + cached_spell_id=None (skip-cache lane; teach-grade
    comment records the id-reuse hazard) and the store is guarded
    `if cache_key is not None:` - unhashable inputs resolve uncached
    every call; the hashable hot path is byte-identical. Grep-clean: no
    raw id(spell)/id(spellframe) keys remain in meld/. REGRESSION TEST
    (integration, world-reset fixture): (1) seeds the EXACT poisoned
    id-shaped entry the removed fallback would have read (pointing at a
    real bound spell) and proves an unhashable meld can never serve it
    (belt-and-braces isinstance trap surfaces a poisoned serve loudly);
    (2) proves the skip lane leaves no id-shaped cache rows while
    hashable class inputs still cache one entry (parity). AST floor OK
    on the test; the two src files hit the standing bash replica rot
    (phantom brace error at a stale :755) - real disk verified via
    file-tool (the :755 dict closes at :765; edited regions read back
    clean). pytest: Not run (owner-run 3.14t).
  EVIDENCE:
  - src/melder/aether/conduit/meld/conduit_meld.py:258-300,463-500
  - src/melder/aether/conduit/meld/spellspace_meld.py:280-320,470-510
  - tests/integration/melder/aether/conduit/test_meld_unhashable_input_cache_aliasing.py
  IMPACT: a freed unhashable input's address can no longer resurrect a
    dead cache entry; wrong-spell resolution via id reuse is closed.
  NEXT: owner-run (new regression + meld unit/integration trees);
    green -> closure walk.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-12T19:05:00Z
  TYPE: FACT
  CLAIM: OWNER-RUN FALLOUT RESOLVED: test_meld.py carried
    test_meld_non_string_unhashable_input_uses_identity_fallback_cache_
    key, which asserted the REMOVED id-fallback behavior (id-shaped key
    stored + reused, resolve-once). Rewritten as ..._skips_the_
    resolution_cache asserting the new law: no cache entry ever
    (cache == {} after both calls), _resolve_spell runs on EVERY call
    (call_count == 2), execute lane unchanged. History block records
    the aliasing rationale. Sweep: no other old-contract fallback
    tests remain (grep clean).
  EVIDENCE:
  - tests/unit/melder/aether/conduit/meld/test_meld.py:1026-1082
  IMPACT: the unit suite now asserts the fix instead of the bug.
  NEXT: owner re-run of test_meld.py; then closure walk.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Owner-found id-reuse aliasing in the meld doors' unhashable-input cache
fallback. Fix LANDED = never cache by raw id(): TypeError -> cache_key
None -> resolve uncached; store guarded. Four sites + one two-test
regression file + the old-contract unit test rewritten to the new law.
Awaiting owner run.
