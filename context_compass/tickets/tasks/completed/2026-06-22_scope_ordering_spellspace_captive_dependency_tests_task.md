<!-- CLOSED 2026-06-30T23:04:50Z (departed-agent cleanup) -->
- Completed: 2026-06-30T23:04:50Z
- Summary: Turned in during departed-agent cleanup (owner optimizer_0 departed); closed via tickets/tasks/completed/2026-06-30_turn_in_departed_agents_optimizer0_hope0_task.md. Prior in-file Notes preserved as the durable record; acceptance not re-verified.

# Task: Integration tests for the spellspace captive-dependency invariant

## Metadata
- Task ID: TASK-2026-06-22-scope-ordering-spellspace-captive-dep-tests
- Story: UNKNOWN (feeds the meld/existence bug-fix program)
- Status: in_progress
- Owner: cowork
- Agent Name: optimizer_0
- Priority: p1
- Created: 2026-06-22T12:40:00Z
- Updated: 2026-06-22T12:40:00Z

## Objective
Author integration tests that pin the invariant: a longer-lived spell
(`unique`, `unique_per_conduit`, `unique_per_conduit_lineage`,
`unique_per_conduit_cluster`) must NOT be allowed to depend on a request-local
`unique_per_spell_space` spell (captive dependency). The bad edge must be
rejected at build (conjure) time.

## Ticket Contract
- ENTRY_GATE: active board row routing optimizer_0; this ticket read.
- EXECUTION_BOUNDARY: create one new integration test file under
  tests/integration/melder/conduit/. No src/ changes in this task.
- DEPENDENCIES: ScopeOrderingStrategy (system/validation/scope_ordering_strategy.py)
  is the intended enforcer; the lineage-store fix lane is a sibling.
- EXIT_GATE: test file authored; run attempted; result recorded truthfully
  ("Not run" here because the sandbox is Py3.10 and melder is 3.14t-only).
- FAILURE_ESCALATION: if the invariant should be enforced at meld rather than
  conjure, record a DECISION_REQUEST before changing the assertion site.

## Scope Boundaries
- In scope: author the integration tests; characterize expected vs current
  behavior from static evidence.
- Out of scope: implementing the conjure-time rejection (separate fix); the
  lineage-store threading fix.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: user directed authoring of these tests now.

## Steps / Checklist
- [x] Confirm the enforcer + current behavior (ScopeOrderingStrategy ranks
      scopes; experiment shows conjure currently succeeds for unique->spellspace
      and only a meld-time spellspace-request RuntimeError fires).
- [x] Write tests/integration/melder/conduit/test_conduit_integration_scope_ordering_spellspace.py.
- [ ] Run on 3.14t (user) and record pass/fail; the strict tests are EXPECTED
      to fail on current code (guard not enforced at conjure).
- [ ] Decide enforcement point (conjure vs meld) and open the fix ticket.

## Deliverables
- test_conduit_integration_scope_ordering_spellspace.py: 4 rejection tests
  (unique / upc / lineage / cluster -> spellspace) + 1 positive control.
- EXPANSION (user directed "make ~30 more, cover all angles"): two matrix files.
  - test_conduit_integration_scope_ordering_matrix.py (BUILD lane, 29 cases):
    full scope truth table -- 10 rejection edges (every broad->strictly-narrower
    pair) + 17 allowed edges (equal-or-broader, or `many` either side) + 2 sanity.
  - test_conduit_integration_scope_resolution_alignment.py (RUNTIME lane, 22):
    each existence resolving from its correct store -- direct, as-dependency,
    across lessers/nested lessers, and under 8-thread concurrency (3.14t no-GIL).
    Includes the lineage-as-dependency BUG pins and cluster leader-store PROBES.

## Files / Paths Impacted
- tests/integration/melder/conduit/test_conduit_integration_scope_ordering_spellspace.py (new)
- tests/integration/melder/conduit/test_conduit_integration_scope_ordering_matrix.py (new)
- tests/integration/melder/conduit/test_conduit_integration_scope_resolution_alignment.py (new)
- tests/integration/melder/conduit/test_conduit_integration_scope_structural_resolution.py (new)
- tests/integration/melder/conduit/test_conduit_integration_spellspace_scope_safety.py (new)

## Validation
- Sandbox cannot run melder (Python 3.10.12; melder is 3.14t-only). Run on the
  user's 3.14t venv, from repo root:
  - python -m pytest tests/integration/melder/conduit/test_conduit_integration_scope_ordering_spellspace.py -q
  - Bare `pytest <file>` fails collection (ModuleNotFoundError: tests._frame_posture_test_support):
    `tests` is a namespace package (no __init__) and there is no pythonpath /
    root conftest, so the repo root must be on sys.path. `python -m pytest`
    adds CWD; equivalently set `$env:PYTHONPATH="."` before `pytest`.
- RUN 1 (2026-06-22, user, 3.14t): 5 failed -- but ALL at the same site,
  `_book()` -> `Spellbook(...)` construction, NOT at the invariant assertion:
  `RuntimeError: SpellbookConfiguration name does not match the aetheric frame`
  (spellbook.py:3467). Cause: TEST-FIXTURE BUG -- `_book` built
  `SpellbookConfiguration()` (frame "default") while passing
  `aetheric_frame="scope-spellspace-{tag}"`, so the frame-name match guard in
  `_initialize_configuration` fired before conjure. None of the 5 tests reached
  conjure; the invariant was NOT actually exercised. Fix: construct
  `SpellbookConfiguration(frame)` with the same name passed to the Spellbook
  (matches the working experiment pattern). Awaiting RUN 2.
- RUN 2 (2026-06-22, user, 3.14t): 4 failed, 1 passed -- the REAL signal.
  All four rejection tests failed with `Failed: DID NOT RAISE
  SpellbookValidationError` (conjure SUCCEEDED for unique/upc/lineage/cluster ->
  spellspace). `test_spellspace_may_depend_on_unique_positive_control` PASSED.
  CONCLUSION (confirmed, not predicted): the captive-dependency invariant is NOT
  enforced at conjure for ANY of the four broad scopes. The only existing guard
  is the meld-time spellspace-request RuntimeError, which does not prevent the
  bad binding. Gap is real; tests are correct and now pin it.
- RUN 3 (2026-06-23, user, 3.14t): full matrix, 51 tests -> 16 failed, 35 passed.
  14 are GENUINE findings; 2 are a repeat of the config frame-name setup bug.
  BUILD lane: all 10 broad->strictly-narrower rejection edges FAILED with DID NOT
  RAISE -> the ENTIRE scope-ordering gate is absent at conjure (not just
  spellspace). All 17 allowed + 2 sanity PASSED -> legal graphs still build.
  RUNTIME lane PASSED: unique x3, upc x3, lineage direct (root/lesser/nested/
  cross-root) x3, lineage-holder-on-unique, many x2, spellspace direct x3,
  concurrent-unique. RUNTIME lane FAILED (wrong instance): lineage AS DEPENDENCY
  into a many holder, into a upc holder, into a spellspace holder entered on a
  LESSER, and the same under 8 threads. So direct lineage + lineage-as-holder are
  aligned; lineage-as-a-dependency-through-a-lesser resolves a lesser-local
  instance -- exactly the `root_creations = caller_creations` door defect. Also
  learned: enter_spellspace() works on a lesser; the concurrency failure is
  deterministic wrong-store, not a race. The 2 cluster PROBES errored at Spellbook
  construction (frame-name mismatch -- setup bug, fixed to a default-frame shared
  config per the proven cluster pattern); cluster meld-path result PENDING re-run.
- RUN 3b (2026-06-23, user, 3.14t, alignment file only): 6 failed, 16 passed.
  The 4 lineage-as-dependency reds reproduced identically (stable, not flaky).
  The 2 cluster probes reached the REAL runtime and revealed the cluster store is
  inert until a leader is explicitly elected: membership + refresh != election.
  Error surfaces differed by graph (resolved_store() RuntimeError vs the
  resolution-validity gate's SpellbookValidationError, which subclasses
  RuntimeError). FIX: election API is `cloud.get_cluster(name).elect_leader(
  conduit.id)` (conduit_cluster.py:676); a cluster spell resolves into the
  leader's own `_creations` (component test asserts
  `member._cluster_creations.resolved_store() is leader._creations`). Rewrote the
  2 fragile cluster probes into 3 grounded tests: no-leader-raises (the discovered
  invariant), elected-leader stable-in-leader-store, and member-facade-resolves-
  to-leader-store (mirrors the proven component pattern). Re-run PENDING.
- RUN 4 (2026-06-23, user, 3.14t): cluster trio in alignment file now all PASS.
  New STRUCTURAL file (test_..._scope_structural_resolution.py): 1 pass, 7 fail
  exactly as designed. KEY EVIDENCE:
  * COUNT: root + 5 lessers yield SIX distinct lineage instances (saw 6, want 1)
    -> the lineage store fragments one-per-caller; this is a store-identity defect,
    not random per-meld allocation.
  * MASKING CONTROL passes: the same broken path on the ROOT resolves correctly
    because caller==root -> proves root-only coverage gives false comfort.
  * PATH AGREEMENT fails: on a lesser the DIRECT meld is correct but the
    DEPENDENCY-injected instance differs -> defect localized to the dependency path.
  * DEDUP refinement: `a.dep is b.dep` PASSES (two holders on one lesser share),
    but `a.dep is root_leaf` FAILS -> each caller store dedups internally; it is
    simply the WRONG store. Pins it to per-caller-store identity.
  * TRANSITIVE (2 hops) and LIFETIME (across sibling churn) also fail -> the defect
    survives depth and is not a transient.
  FINDING (API): cluster membership is normal-conduits-only; a lesser is rejected
  at the cloud boundary (conduit_cloud.py:193 "requires a normal conduit"). So the
  cluster dependency analog cannot use a lesser-member; rewrote it to two normal
  conduits in one frame (shared config), member binds the holder. Cluster-dep
  result PENDING that re-run.
  NOTE: sandbox bash mount lagged on the last write (py_compile saw a truncated
  361-line copy); the on-disk file is complete and valid -- user pytest is the
  real check.
- RUN 4b (2026-06-23, user, 3.14t): rewritten cluster-dependency probe (two
  normal conduits, leader elected, member melds the holder) FAILS on the real
  assertion -- member_holder.dep != leader's instance. CLUSTER dependency path
  confirmed to share the lineage defect.
- BLAST RADIUS (source-grounded, ground truth = the door compiler + meld store
  selection). Per leaf-door store read:
  * unique -> `_spell._owner_creations` (door_compiler.py:602): caller-independent
    -> SAFE.
  * unique_per_conduit -> `caller_creations` (door_compiler.py:544): caller IS its
    store -> SAFE.
  * many -> no persistent store -> SAFE.
  * lineage -> `root_creations = caller_creations` (door_compiler.py:636): trusts
    caller==lineage-root -> AFFECTED.
  * cluster -> `leader_creations = caller_creations` (door_compiler.py:672): trusts
    caller==leader -> AFFECTED.
  * spellspace -> `caller_creations` (door_compiler.py:571): DIRECT meld is
    correctly per-scope, BUT the DEPENDENCY path is BROKEN -> AFFECTED. The source
    argument that it was safe was WRONG; RUN 5 falsified it.
  CRUX: conduit_meld.py:344-349 swaps in a SEPARATE scope store only for lineage
  (_root_creations) and cluster (resolved_store()); all others use self._creations.
  The DEPENDENCY path never re-selects the child's scope store, so every existence
  whose true store is not the plain caller store breaks: lineage and cluster
  resolve into the caller store; spellspace into a persistent non-scope store.
  unique reads owner (safe), upc's store IS the caller (safe), many has no store
  (safe) -- all three confirmed by PASSING dependency tests, not just source.
  CONCLUSION: 3 of 6 existences affected (lineage, cluster, spellspace), one
  dependency-step root cause; the fix re-selects the child's scope store per
  existence. unique/upc/many unchanged.
- RUN 5 (2026-06-23, user, 3.14t): spellspace safety suite (10 tests) -> 6 failed,
  4 passed. PASS = all DIRECT-meld tests: same-in-scope, distinct-across-scopes,
  lesser/root scope isolation, concurrent scopes isolated. FAIL = all DEPENDENCY-
  path tests: within-scope count saw 2 not 1; many-holder dep != direct scope
  instance; transitive dep != direct; two holders share a dep but != direct; lesser
  dependency != lesser scope instance; and RE-ENTRY: holder.dep in scope1 IS
  holder.dep in scope2 (same object across two scopes). CHARACTERIZATION: the
  spellspace DEPENDENCY path resolves a SINGLE PERSISTENT instance (shared across
  holders AND across scopes) -- it degrades unique_per_spell_space to unique-like
  frame-singleton behavior and LEAKS past scope close (captive-dependency hazard,
  live). Direct meld is correctly scoped. spellspace is a THIRD lane-1 casualty;
  the "make sure it is for a fact safe" call was correct, the SAFE claim was not.

## Risks / Rollback Notes
- The strict tests assert conjure rejection; if the project chooses meld-time
  enforcement instead, the assertion site must change. Flagged as a decision.

## Applicable Anti-Patterns
- [ ] No claim that tests ran when they did not (reported "Not run").
- [ ] No assertion of a contract not grounded in the existence/scope rules.

## Notes
- DATETIME: 2026-06-22T12:40:00Z
  TYPE: FACT
  CLAIM: ScopeOrderingStrategy ranks unique=0, cluster=1, lineage=2,
    unique_per_conduit=3, unique_per_spell_space=4, many=5, and emits a
    `scope_ordering_violation` ERROR when a node depends on a strictly narrower
    scope (node_rank < dep_rank), skipping `many` on both sides. So all four
    broad->spellspace edges SHOULD be flagged. But the existing experiment shows
    `unique`->spellspace conjure SUCCEEDS and only a conduit-meld-time
    spellspace-request RuntimeError fires -- so the Phase-6 violation is NOT
    enforced as a conjure failure today.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/system/validation/scope_ordering_strategy.py:79-129
  - tests/experimentation/test_unique_depends_on_spellspace_experiment.py:111-145
  IMPACT: the captive dependency is not prevented at build; a broad spell built
    inside a spellspace would capture a request-local instance and dangle on
    spellspace close.
  NEXT: user runs the tests on 3.14t; decide conjure-vs-meld enforcement.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Tests encode the captive-dependency invariant for spellspace. Authored against
the documented scope rule; could not be run on the 3.10 sandbox. Per the prior
experiment, the 4 rejection tests are expected to FAIL on current code (conjure
does not reject; only a meld-time spellspace gate exists), which is the gap to
fix. Positive control (spellspace -> unique) should pass. Next: user runs on
3.14t, then we choose the enforcement point and open the fix ticket.
