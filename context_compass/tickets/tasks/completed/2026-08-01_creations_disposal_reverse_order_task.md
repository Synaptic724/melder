

- Completed: 2026-08-01T19:40:00Z
- Summary: Scoped disposal now runs in reverse creation order, across keys and
  inside `Existence.many` buckets - two `reversed(...)` calls, no new machinery,
  since the dict already was the creation-order record. Owner ran the new unit
  regression and all four integration tests GREEN on 3.14t.
- CLOSED WITH ONE NAMED GAP, not a clean claim: the owner's run also surfaced a
  pre-existing red, `test_component_conduit_cleanup_disposes_lifo`, which
  asserted forward order while being NAMED `..._disposes_lifo` with a `Raises:`
  clause reading "If disposal order is not LIFO". That test had capitulated to
  the bug; its assertion was corrected to `[2, 1, 0]` and its contradictory
  docstring repaired. THAT CORRECTION HAS NOT BEEN RUN by anyone. Closed on
  owner instruction to turn the task in. If
  `pytest tests/component/melder/aether/conduit/test_conduit_component_creations.py -q`
  reds, this closure reopens.
- Two limitations recorded as owner decisions rather than fixed: disposal-method
  -name semantics (first name only, first failure rejects the rest) accepted
  as-is, and reverse-insertion stops equalling reverse-creation after an
  ownership transfer.

# Task: Dispose scoped creations in reverse creation order

## Metadata
- Task ID: TASK-2026-08-01-creations-disposal-reverse-order
- Story: none (standalone task)
- Status: done (owner-verified green on 3.14t, 2026-08-02)
- Owner: cowork
- Agent Name: bootstrap_0
- Priority: p2
- Created: 2026-08-01T16:29:03Z
- Updated: 2026-08-01T16:29:03Z

## Objective
Make `Creations` tear down its scoped entries in REVERSE creation order so a
dependency is never disposed before the dependent that holds it. Ordering only;
disposal-method-name semantics are explicitly out of scope by owner ruling.

## Ticket Contract
- ENTRY_GATE: owner ruled "implement the ordering" 2026-08-01 after a source read
  established the current walk is forward. Board row routes this task.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/conduit/creations/creations.py`
    (`_dispose_disposable_registry`, class docstring Lifecycle/Cleanup section)
  - one new regression test under `tests/unit/melder/aether/conduit/creations/`
  - `context_compass/system_docs/src_components.md` (Creations component entry)
- DEPENDENCIES: none blocking.
- EXIT_GATE: reverse order implemented for BOTH the unique walk and the `many`
  bucket walk, regression test added, canonical component doc states the
  ordering invariant, owner-run suite green on 3.14t.
- FAILURE_ESCALATION: RAISE if any existing test asserts forward disposal order,
  because that would mean forward order was an intended contract rather than an
  unstated default.

## Scope Boundaries
- In scope: iteration direction of disposal, its docstring contract, one
  regression test, the canonical doc line.
- Out of scope (OWNER-RULED 2026-08-01): `_attempt_cleanup` calling only the
  first declared disposal method, and the `List[str]` vs first-wins mismatch.
  Owner accepted current behaviour, including first-failure rejecting the rest
  of that object's names. Do not touch that method.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: owner gave an explicit implement instruction and the
  investigation that justifies it is source-backed, not hypothesised.

## Steps / Checklist
- [x] Establish current order from source rather than from docs
- [x] Confirm the ordering data already exists (dict insertion order)
- [x] Reverse the unique walk
- [x] Reverse the `many` bucket walk
- [x] Add regression test naming the symptom
- [x] Update canonical component doc with the ordering invariant
- [ ] Owner runs the suite on 3.14t
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Reverse-order disposal in `Creations._dispose_disposable_registry`.
- `tests/unit/melder/aether/conduit/creations/test_creations_disposal_reverse_order_regression.py`
- `tests/integration/melder/conduit/test_conduit_integration_disposal_ordering.py`
- Ordering invariant recorded in `system_docs/src_components.md`.

## Files / Paths Impacted
- src/melder/aether/conduit/creations/creations.py
- tests/unit/melder/aether/conduit/creations/test_creations_disposal_reverse_order_regression.py
- tests/integration/melder/conduit/test_conduit_integration_disposal_ordering.py
- context_compass/system_docs/src_components.md

## Validation
- GAP DISCHARGED 2026-08-02 by the OWNER, not by me. The owner reports the suite
  green on 3.14t, including `test_component_conduit_cleanup_disposes_lifo` - the
  test whose assertion I corrected from `[0, 1, 2]` to `[2, 1, 0]` and which was
  the one thing this ticket closed without verifying. Recording it as an owner
  observation and attributing it, because I did not run it and this repo's rule
  is that a test result is only ever claimed by whoever actually ran it.
- Not run BY ME. The sandbox is Python 3.10.12 and melder targets 3.14t, so the
  suite cannot import the package here. `py_compile` was run on all touched
  Python files and all compile clean.
- Recommended commands:
  - `pytest tests/integration/melder/conduit/test_conduit_integration_disposal_ordering.py -q`
  - `pytest tests/unit/melder/aether/conduit/creations -q`
  - `pytest tests/integration/melder/conduit -q`

## Risks / Rollback Notes
- RISK: some object's teardown may have silently depended on forward order.
  Reversal is a behaviour change even though it is the more defensible one.
  MITIGATION: single-call change, trivially revertible; the regression test
  documents the intended direction so a revert is a deliberate act.
- RISK: reversal fixes WITHIN one store only. It does not order teardown across
  different `Creations` instances; that axis belongs to the scope cascade.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [x] No claiming tests ran that did not run.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed
- [x] Notes quality maintained
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.

## Notes
- DATETIME: 2026-08-01T16:29:03Z
  TYPE: FACT
  CLAIM: Disposal ran FORWARD, in creation order. `_dispose_disposable_registry`
    walks `disposable_registry.values()` on a plain dict, and dict iteration is
    insertion-ordered by language guarantee since 3.7. Insertion happens at
    creation time, so a dependency resolved first was also disposed first -
    ahead of the dependent that holds it.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:229-241
  - src/melder/aether/conduit/creations/creations.py:268-273
  - src/melder/aether/conduit/creations/creations.py:286-292
  IMPACT: Same defect class as python-dependency-injector issue #432, where a
    session was closed before the token whose teardown still needed it. Latent
    here, not observed: it only bites when a disposal method reaches into an
    injected dependency.
  NEXT: Reverse both walks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-01T16:29:03Z
  TYPE: DECISION
  CLAIM: Reverse the walk in place rather than introducing any order-tracking
    structure. The ordering data already exists - the dict IS the creation-order
    record - so this is an iteration-direction change, not new machinery. Dict
    views have been reversible since 3.8 and the package floor is 3.14.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:229-241
  IMPACT: Keeps the fix to one method and adds zero per-creation cost to the
    resolution hot path, which the class docstring explicitly protects.
  NEXT: Apply to the unique walk and the `many` bucket walk together; a `many`
    bucket is also creation-ordered and needs the same treatment.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-08-01T16:29:03Z
  TYPE: DECISION
  CLAIM: OWNER RULING - disposal-method-name semantics are ACCEPTED AS-IS and
    excluded from this task. `_attempt_cleanup` processes only the first
    declared name and returns on both success and failure; owner confirmed
    first-failure rejecting the rest is intended. The `List[str]` type and the
    plural class-docstring wording remain in tension with that, and were NOT
    corrected here because the owner scoped this task to ordering only.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:190-212
  - src/melder/aether/conduit/creations/creations.py:39-43
  IMPACT: Anyone later mirroring this class for boot methods inherits the same
    first-name-only behaviour. That is now a recorded owner decision rather than
    an undiscovered quirk.
  NEXT: If the plural/singular mismatch is ever revisited, it is a separate
    ticket - do not fold it into ordering work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-08-01T16:35:00Z
  TYPE: MEASURE
  CLAIM: Implementation landed. Both disposal walks now run under `reversed(...)`,
    the method and class docstrings state the ordering invariant, one regression
    test asserts strict reverse order across unique entries and within a `many`
    bucket, and the canonical component doc records the invariant. Both touched
    Python files compile clean under py_compile.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:214-253
  - tests/unit/melder/aether/conduit/creations/test_creations_disposal_reverse_order_regression.py:1-118
  - context_compass/system_docs/src_components.md:1511-1519
  IMPACT: Within-store teardown is now dependency-safe. Combined with the
    existing scope cascade for between-store ordering, teardown is correct on
    both axes without a graph walk.
  NEXT: Owner runs `pytest tests/unit/melder/aether/conduit/creations -q` on
    3.14t; green closes this task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-01T16:52:00Z
  TYPE: MEASURE
  CLAIM: `reversed()` on a dict view is NOT a snapshot, so the fix costs
    effectively nothing. It returns `dict_reversevalueiterator`, a lazy iterator
    of the same 72 bytes as the forward iterator. Consuming 200,000 entries
    peaked at 584 bytes reversed vs 512 forward; a real snapshot
    (`list(d.values())[::-1]`) peaked at 3,200,472 bytes. Timing best-of-5 over
    the same 200,000: forward 1.53 ms, reversed 1.99 ms, snapshot 3.26 ms.
    Reverse iteration IS about 30% slower per element (~10 ns vs ~7.6 ns) due to
    backwards traversal of the entries array, but teardown runs once per scope
    over disposal-declaring entries only, so a 50-object scope pays roughly 500
    nanoseconds total while already invoking arbitrary user teardown code.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:234-247
  IMPACT: Settles the "isn't reversed slow because it snapshots" objection with
    numbers instead of assertion, and rules out replacing the dict with a
    parallel order list - that would move cost onto the per-meld creation path
    to save nanoseconds on a once-per-scope teardown path, which is the trade
    backwards and contradicts the class docstring's own hot-path principle.
  NEXT: None. Recorded so the question is not re-derived.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-08-01T16:52:00Z
  TYPE: RISK
  CLAIM: OWNER-ACCEPTED LIMITATION - reverse INSERTION order stops equalling
    reverse CREATION order once entries move between stores. `restore_spell_creations`
    inserts into `_disposable_creations` fresh, and a dict insert appends, so a
    transferred object arrives as the apparent newest entry in its destination
    and disposes first there regardless of when it was built. The same applies
    to a restore into the SAME store: the method pops the key and re-inserts it,
    moving it to the end, so transfer preflight/rollback reorders an entry even
    when no ownership actually changed. For `Existence.many`, bucket members are
    siblings of one spell and hold no references to each other, so intra-bucket
    order is nearly irrelevant; the imprecise part is that a bucket's position is
    pinned at FIRST insertion, so instance 50 disposes at instance 1's slot.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:428-478
  - src/melder/aether/conduit/creations/creations.py:348-404
  IMPACT: Correctness is "right in the common case, degrades under ownership
    transfer" rather than "right everywhere". Owner ruled this acceptable
    2026-08-01: transfer is an explicit dynamic-mode-only administrative act that
    already marks the lineage dirty and gated for revalidation, and the fix - a
    monotonic sequence stamped per disposal entry, carried through
    extract/restore, plus an O(n log n) sort at teardown - would pay on the
    per-meld creation path forever to buy correctness for a rare act.
  NEXT: None. Do not "fix" this without a fresh owner ruling; it is a recorded
    decision, not an oversight.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-01T17:08:00Z
  TYPE: FACT
  CLAIM: Coverage confirmed for the single-site fix. Only TWO classes actually
    store creations - `Creations` (used directly by `SpellSpace`, parameterized
    with the spellspace id) and `ConduitCreations(Creations)` (conduit/root).
    `ClusterCreations` extends `Cleanable`, NOT `Creations`: it is a facade that
    references the elected leader's store and its own docstring states it
    "never cleans the underlying store". So cluster-scoped objects are disposed
    by the leader's `Creations`, and conduit, root, lineage, cluster and
    spellspace teardown all funnel through the one walk that was changed. No
    second disposal site exists.
  EVIDENCE:
  - src/melder/aether/conduit/creations/cluster_creations.py:9-42
  - src/melder/aether/conduit/spell_space/spell_space.py:174
  - src/melder/aether/conduit/conduit.py:326
  IMPACT: Satisfies the EXIT_GATE question "did one edit actually cover every
    scope" without assuming it from the class docstring.
  NEXT: None.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-08-01T17:08:00Z
  TYPE: MEASURE
  CLAIM: Integration coverage added at owner request, because the unit
    regression hand-inserts entries in an order the TEST chooses and therefore
    assumes the very thing under test - that real resolution registers a
    dependency ahead of its dependent. Four integration tests now build a real
    Spellbook, conjure a real Conduit, and let constructor DI decide insertion
    order: a three-deep chain asserting exact reverse build order; a behavioural
    case asserting each dependent observes its dependency still open during its
    own teardown; a spellspace-scope case covering the plain `Creations` path;
    and an `Existence.many` case using per-instance ordinals so the bucket
    assertion proves sequence rather than merely proving three disposals ran.
  EVIDENCE:
  - tests/integration/melder/conduit/test_conduit_integration_disposal_ordering.py:1-300
  IMPACT: The ordering claim is now falsifiable against the real runtime. If
    resolution order ever stops matching insertion order, these fail rather than
    the fix silently becoming wrong.
  NEXT: Owner runs the integration file on 3.14t.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-01T17:20:00Z
  TYPE: MEASURE
  CLAIM: OWNER RAN THE SUITE ON 3.14t - ALL GREEN. Both the unit regression and
    the four integration tests pass, so the EXIT_GATE condition "owner-run suite
    green" is satisfied by evidence rather than by agent assertion. The agent did
    NOT run these; the sandbox is Python 3.10.12 and cannot import melder.
  EVIDENCE:
  - tests/integration/melder/conduit/test_conduit_integration_disposal_ordering.py:1-300
  - tests/unit/melder/aether/conduit/creations/test_creations_disposal_reverse_order_regression.py:1-190
  IMPACT: Confirms real resolution order matches insertion order in the live
    runtime - the assumption the whole fix rests on is now evidenced end to end,
    not inferred. Ready for acceptance walkthrough and closure.
  NEXT: Owner confirms acceptance criteria -> move to completed + board sync.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-01T17:41:00Z
  TYPE: CONFLICT
  CLAIM: FAILURE_ESCALATION CONDITION FIRED, and it resolves to "not an intended
    contract". Owner's 3.14t run surfaced one red:
    `test_component_conduit_cleanup_disposes_lifo` asserted `[0, 1, 2]`. That
    test is internally contradictory and the contradiction is the evidence: it
    is NAMED `..._disposes_lifo`, its `Raises:` clause reads "If disposal order
    is not LIFO", and its Purpose says "the CURRENT RETAINED order" - while its
    Contract line said "insertion order" and its assertion said `[0, 1, 2]`. The
    name and failure clause preserve an original LIFO intent; the assertion and
    Contract line were amended at some point to match what the forward walk
    actually did. So forward order was a capitulation recorded in a test, not a
    designed contract. Assertion corrected to `[2, 1, 0]` and the Contract line
    repaired so name, contract, failure clause and assertion finally agree.
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_conduit_component_creations.py:439-476
  IMPACT: The EXIT_GATE question is answered with evidence rather than assumed.
    It also means the forward walk had already been noticed by someone who chose
    to encode it instead of fix it.
  NEXT: Owner re-runs the component lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-01T17:41:00Z
  TYPE: FACT
  CLAIM: AGENT ERROR, recorded so the process gap is visible. The earlier
    EXIT_GATE check was reported as "no pre-existing test asserts forward order",
    but the grep only covered `tests/unit/melder/aether/conduit/creations/`. It
    never touched `tests/component/` or `tests/integration/`, so the claim was
    stated with more confidence than the search supported and the owner found
    the red instead of the agent. A full sweep across all three tiers has now
    been run: `test_component_conduit_cleanup_disposes_lifo` was the ONLY
    forward-order assertion in the suite. `test_dev_ops_manager.py:534
    test_cleanup_order` matched the grep but concerns DevOpsManager child
    teardown, not `Creations`, and is unaffected.
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_conduit_component_creations.py:466
  - tests/unit/melder/aether/dev_ops/test_dev_ops_manager.py:534
  IMPACT: Scope a behaviour-change EXIT_GATE sweep across every test tier, not
    the directory nearest the edited file.
  NEXT: None.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Ordering-only fix, owner-ruled and owner-scoped. Disposal within one `Creations`
store now runs newest-first so dependents tear down before their dependencies.
The scope cascade already handled ordering BETWEEN stores, so the two axes now
compose. Disposal-method-name semantics were explicitly excluded by the owner
and are unchanged. Tests not run by the agent - the sandbox is 3.10 and cannot
import melder; the suite needs an owner run on 3.14t.
