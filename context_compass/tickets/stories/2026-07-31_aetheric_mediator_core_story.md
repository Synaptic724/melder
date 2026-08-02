# Story: Build the standalone AethericMediator core plane

## Metadata
- Story ID: STORY-2026-07-31-aetheric-mediator-core
- Epic ID: EPIC-2026-07-31-aetheric-mediator-subsystem
- Status: in_progress
- Owner: cowork
- Agent Name: UNASSIGNED (helper_f departed 2026-08-02, owner-directed; lane left ACTIVE)
- Priority: p1
- Created: 2026-07-31T23:00:41Z
- Updated: 2026-08-01T13:20:00Z

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
- [x] T5: admission orchestrator (one acquisition under the admission lock)
- [x] T6: session (status, join/leave, rollback actions, abort pipeline,
      OUTCOME POLICY: unwind | leave_broken)
- [x] T7: mediator front door + scope-key helper. NOTE: no separate
      `TransactionManager` - DevOps splits request-building and in-flight
      tracking across the manager, but in-flight lives on the orchestrator here
      and request building is a static factory on the request itself. A third
      class would only forward.
- [x] T8: strategy ABC + registry + staged transaction
- [x] T9: information registry (fact baselines + activity indexes by scope,
      submitter, and type). Concrete information STRATEGIES (the catalog) are
      deferred - the registry is the mechanism, the catalog is content.
- [x] T10: root wiring - `Mediator` IS the root Aether holds. DevOps splits
      `ChangeControlManager` (owner) from `TransactionMediator` (front door)
      because its root carries frame duties (dirty roots, revalidation, risk)
      with no counterpart here; splitting would leave a root that only forwards.
- [x] T11: unit tests incl. the no-melder.aether-import test and a concurrency
      proof. OWNER-RUN GREEN on 3.14t. The standalone 3.10 harnesses referenced
      in the RISK note below are SUPERSEDED by those runs and are logic evidence
      only - do not cite them as coverage.

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

- DATETIME: 2026-08-01T12:05:00Z
  TYPE: FACT
  CLAIM: POST-COMPACTION REPAIR + the deterministic-deallocation pass that landed
    after the last note. THREE ticket defects fixed, then the substantive work
    recorded. Ticket defects: (1) this file carried TWO `## Notes` headings and the
    second held a stale copy of the T1-T3 note citing `aetheric_identity.py` /
    `aetheric_claim_table.py` - files renamed away by THIS TICKET'S OWN ruling at
    its Naming section; a future reader repairing from that note would have written
    the pre-rename paths, which is exactly the failure mode that produced the
    bind-guard manifest-path error on 2026-07-27. (2) T11 read `[ ]` after the
    owner ran the suite green. (3) Validation read "Not run" against six recorded
    owner runs.
  EVIDENCE:
  - src/melder/aether/aetheric_mediator/transaction_session.py
  - src/melder/aether/aetheric_mediator/mediator.py
  - src/melder/aether/aetheric_mediator/transaction_request.py
  IMPACT: SUBSTANTIVE WORK THIS LANE, all owner-run green (88 passed):
    (a) REFERENCE CYCLE CLOSED. A rollback inverse is a closure and a useful one
    captures the session, giving `session -> _rollback_actions -> _RollbackAction
    -> closure -> session`. Refcounting cannot see through that, so EVERY finished
    transaction survived to an unrelated collector pass. `discard_inverses()`
    (terminal-only, idempotent) is now called from `_finalize`, so the thread that
    finishes the transaction cuts the edge. Deliberately NOT a full `cleanup()` -
    every accessor is guarded by `check_cleaned()`, so cleaning there would stop a
    caller reading the outcome of its own transaction. `begin`'s failure path DOES
    clean fully: that session never escaped, so nobody is owed a readable outcome.
    (b) `_RollbackAction` is now `Cleanable`. It owns a `Callable`, the one complex
    type in the package, and per banned_patterns.md:78-81 a record holding an
    object reference must be a normal class with cleanup. Precedent is direct:
    `ChangeControlManager.cleanup` explicitly `del`s `_commit_hook`, `_abort_hook`,
    `_commit_validator`, `_structural_validator`, `_dirty_marker`.
    (c) `_run_inverses` releases each record in a `finally` AS IT RUNS, not in a
    batch. A raising inverse produces a caught exception whose traceback references
    the unwind frame and therefore every closure still pending in it.
    (d) `fail` empties `_rollback_actions` when handing them to the unwind, so
    exactly one place owns the release.
    (e) `ClaimTable.cleanup` now clears `Dict[str, List[_GrantedClaim]]`
    NESTED-FIRST. This matters concretely: `release` REBUILDS those lists, so a
    concurrent reader can hold an older one that outer-only clearing would miss.
    (f) THREE ALLOCATIONS -> ONE. `StagedTransaction.from_request` ran 3x per
    transaction and `admitted_at=time.time()` in commit/fail RESTAMPED the field
    with the commit time - it was reporting the wrong moment. Built once at
    admission now. `MetadataPolicy.normalize` returns a DEEPLY frozen structure
    (proxy mappings + tuples at every depth), which is what made the copies
    removable: `frozen=True` only blocks rebinding, so the old `Dict` field left
    both records advertising themselves as detached while any holder could edit
    them.
  NEXT: Owner rulings on the two open questions (does the top plane claim FRAME
    scope keys; do inner frame transactions JOIN or stay siblings), then the three
    subsystem surveys. NOT wiring anything until both land.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-01T12:05:00Z
  TYPE: DECISION_REQUEST
  CLAIM: TWO POLICY ITEMS NEED AN OWNER RULING BEFORE THIS STORY CAN CLOSE.
    (1) PATCH-FRAMEWORK GATE possibly skipped. `patch_framework_gating.md:11-18`
    triggers on work that "changes architecture/component boundaries" and on work
    requiring `src_architecture.md` / `src_components.md` updates. A new top-level
    subsystem under `src/melder/aether/` is both. No `system_docs/patches/active/`
    dir exists for it and `artifact_board.md` carries zero rows for this lane. The
    entry gate says implementation should not have started without those artifacts.
    I am not going to quietly backfill patch docs to paper over the gate - that is
    the box-checking the policy exists to prevent.
    (2) DATACLASS RULE CONFLICT, surfaced not resolved. synaptic `AGENTS.MD` 5.15
    allows only `None/bool/int/float/str` as dataclass fields; `banned_patterns.md`
    line 80 allows "value types AND CONTAINERS of those value types". The three
    remaining dataclasses (`AdmissionResult`, `TransactionRequest`,
    `StagedTransaction`) hold tuples and a frozen mapping - legal under the skill
    doc, illegal under a literal reading of AGENTS.MD. They hold NO object
    references either way, so the underlying intent is satisfied. AGENTS.MD 5.4
    says stop and ask when repo docs conflict.
  EVIDENCE:
  - context_compass/agent_onboarding/default/engineer/skills/patch_framework_gating.md:11-26
  - context_compass/agent_onboarding/user_defined/synaptic_python_developer/skills/python/banned_patterns.md:78-81
  IMPACT: (1) decides whether this lane is gate-compliant or needs a documented
    owner waiver before closure. (2) decides whether three dataclasses stay as-is
    or become normal classes with cleanup - a real refactor, not a doc nit.
  NEXT: Owner rules both; I act on neither until then.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-01T12:40:00Z
  TYPE: UNKNOWN
  CORRECTED 2026-08-01T13:20:00Z - THIS NOTE WAS FILED AS `FACT` AND SHOULD NOT
  HAVE BEEN. Its conclusions came from grep and AST walks over the source, not
  from reading it. The Unknowns Gate forbids promoting inference from naming or
  structure. The lock claims were later CONFIRMED by reading both modules in
  full (see the 13:20 note), but the method was wrong and the type is corrected
  here rather than quietly left standing.
  CLAIM: LOCK-ORDER AUDIT. The plane owns SIX lock-bearing objects and has never
    had its lock order established. It has EXACTLY ONE cross-object nesting and
    that nesting is ONE-WAY, so the plane is deadlock-free - but by an accident of
    construction that nothing documents and no test guards.
    THE ONE NESTING: `AdmissionOrchestrator.admit` holds `orchestrator._lock` and
    calls `claim_table.try_acquire(...)`, which takes `claim_table._condition`.
    ORDER: orchestrator._lock -> claim_table._condition.
    NO REVERSE EDGE: `ClaimTable` is a leaf. It never calls the orchestrator, the
    mediator, the registry, or a session.
    WHY IT IS SAFE: `try_acquire` is NON-BLOCKING - it returns blocking evidence
    or `()` and never parks - so the nesting is bounded. And
    `AdmissionOrchestrator.release` deliberately does the opposite: it takes its
    own lock, mutates `_in_flight`, RELEASES, and only then calls
    `claim_table.release_holder(...)`. So release never nests at all.
    METHOD CORRECTION, recorded because it nearly produced a false clean bill:
    my first AST probe reported "no cross-object calls under lock" and I almost
    promoted that to FACT. It was a FALSE NEGATIVE - the probe matched only
    `self._collaborator.method()` and the real call is on a PARAMETER
    (`claim_table.try_acquire`). Re-running against parameter receivers found it.
    Naming-shaped probes are exactly what the Unknowns Gate forbids inferring from.
  EVIDENCE:
  - src/melder/aether/aetheric_mediator/admission_orchestrator.py:169-190
  - src/melder/aether/aetheric_mediator/admission_orchestrator.py:222-227
  - src/melder/aether/aetheric_mediator/mediator.py:_admit_with_wait
  IMPACT: THE LOAD-BEARING LAW IS "ADMIT MUST NEVER WAIT". `_admit_with_wait`
    parks on `claim_table.wait_for_change(...)` only AFTER `admit` has fully
    returned and dropped the orchestrator lock. If the wait ever moved inside
    admit, a parked thread would hold the very lock `release` must take to free
    the claims it is waiting for - the plane would deadlock on the first real
    contention, which is precisely the workload it exists for. Nothing currently
    states this law or tests it.
  NEXT: State the lock order in the two class docstrings and add a test that
    fails if `admit` ever becomes blocking.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-01T12:40:00Z
  TYPE: RISK
  CLAIM: `ClaimTable.acquire(...)` - the BLOCKING variant carrying
    `self._condition.wait(timeout=remaining)` - has ZERO production call sites.
    Four test call sites only. The mediator does not use it; it implements its own
    bounded retry loop over the non-blocking `try_acquire` instead.
  EVIDENCE:
  - src/melder/aether/aetheric_mediator/claim_table.py:acquire
  - src/melder/aether/aetheric_mediator/mediator.py:_admit_with_wait
  IMPACT: THIS IS A LOADED GUN AIMED AT THE WIRING LANE, not dead weight. It is
    public, it is the obvious-looking name, and it blocks. A future agent wiring
    MR / Nexus / Crystallizer who reaches for `acquire` instead of `try_acquire`
    from inside the orchestrator lock deadlocks the plane instantly - and the
    method's own name invites exactly that. The failure would appear under
    contention only, which is the hardest kind to reproduce.
  NEXT: Owner ruling - delete it (public-API change, so I will not do it
    unilaterally per refactor_limits.md), or keep it with a docstring that refuses
    the unsafe usage in words. I am adding the lock-order law either way.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-01T12:55:00Z
  TYPE: IMPLEMENT
  CLAIM: Lock order is now STATED and GUARDED. Three changes, no behaviour change.
    (1) `AdmissionOrchestrator` class docstring now carries the plane-wide lock
    order (`orchestrator._lock` -> `claim_table._condition`), names it the ONLY
    cross-object nesting, states why it is one-way (the table is a leaf), and
    states the law ADMIT MUST NEVER WAIT with the deadlock it prevents.
    (2) `ClaimTable.acquire` docstring opens with a refusal: THIS METHOD BLOCKS,
    never call it holding another plane lock, and it names the trap explicitly -
    `acquire` reads like the default while `try_acquire` reads like the special
    case, when the reverse is true for every in-package caller.
    (3) Three static tests added.
    DOCSTRING CORRECTION, not an addition: the old `Threading:` section asserted
    "No foreign code is invoked while holding it." That was FACTUALLY FALSE -
    `admit` invokes `claim_table.try_acquire` under the lock at line 179. Fixed
    per comments.md (a comment conflicting with behaviour is repaired, not
    deleted); a reader trusting the old text would have concluded no nesting
    existed and could safely add a blocking call.
  EVIDENCE:
  - src/melder/aether/aetheric_mediator/admission_orchestrator.py:68-99
  - src/melder/aether/aetheric_mediator/claim_table.py:287-305
  - tests/unit/melder/aether/aetheric_mediator/test_aetheric_mediator_unit.py
  IMPACT: The three tests are STATIC BY DESIGN and that is the point. Breaking
    this law produces a DEADLOCK, and a deadlocked test reports as a hang or a
    timeout - it never tells the next reader which rule was broken. Parsing the
    source names the rule at the moment it is violated:
    - `test_admit_never_makes_a_blocking_call_while_holding_the_admission_lock`
      fails the instant a blocking name appears under that lock, AND asserts
      `try_acquire` is still the acquisition path so the docstring cannot quietly
      start describing something else.
    - `test_release_does_not_touch_the_table_while_holding_the_admission_lock`
      preserves the asymmetry that makes the order provably one-way rather than
      merely currently-true.
    - `test_claim_table_is_a_leaf_so_the_lock_order_cannot_reverse` fails if the
      table ever imports another plane component, which is the only way a reverse
      edge could appear.
  NEXT: Owner runs the suite; then the owner ruling on whether
    `ClaimTable.acquire` is deleted or kept behind its new refusal docstring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-01T13:20:00Z
  TYPE: FACT
  CLAIM: LOST WAKEUP IN `Mediator._admit_with_wait`, found by READING the module
    end to end after the owner called out that I was inferring from AST scans
    instead of reading code. The check and the park are TWO separate
    acquisitions of the claim table's condition: `_orchestrator.admit(...)`
    takes and releases it inside `try_acquire`, then `wait_for_change(...)`
    takes it again to park. A `release_holder` landing between them calls
    `notify_all` while this thread is NOT yet parked, so the notification is
    missed and nothing notifies again until the NEXT release. If the blocker
    was the last holder there is no next release, and the transaction slept the
    FULL `max_wait_seconds` (default 30s) with its scope already free.
    THE EXISTING TEST COULD NOT CATCH IT: `test_release_wakes_a_waiter_rather_
    than_leaving_it_to_time_out` sleeps to let the waiter park before releasing,
    which is precisely the ordering that dodges the window.
  EVIDENCE:
  - src/melder/aether/aetheric_mediator/mediator.py:_admit_with_wait
  - src/melder/aether/aetheric_mediator/claim_table.py:release_holder
  IMPACT: Latency only, never a deadlock - but it bites exclusively under
    contention, which is the only workload this plane exists for. Also RETIRES
    my own earlier proposal to "restructure the loop to hold the condition
    across check-and-wait, or call ClaimTable.acquire directly". Both were
    inventions and both are wrong: admission runs THROUGH the orchestrator,
    which owns its own lock, the in-flight registry, and the identity check.
    Holding the table condition across that call nests the two locks in the
    opposite order from `admit` - the exact AB-BA this design avoids. And
    `acquire` can only do check-and-wait under one acquisition because it
    BYPASSES admission entirely, which would lose all three of those things.
    The two-acquisition structure is forced, not sloppy.
  NEXT: Port the DevOps answer rather than inventing a third one.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-01T13:20:00Z
  TYPE: DECISION
  CLAIM: FIXED BY PORTING, NOT BY INVENTING. `TransactionMediator._admit_with_
    scope_wait` hit this identical race first and answered it with SLICED
    WAITING - `wait_for_release(timeout=min(remaining, 1.0))` - carrying a
    comment that names the window explicitly. DevOps did not restructure the
    loop either; it accepted the forced two-acquisition shape and BOUNDED the
    cost. Three changes, all copied:
    (1) `mediator.py` parks for `min(remaining, self._WAIT_SLICE_SECONDS)`,
    capping a missed notification at one second per retry instead of the whole
    budget. `_WAIT_SLICE_SECONDS` is a CLASS attribute, not a module constant,
    per module_scope.md.
    (2) `claim_table.wait_for_change` now calls `check_cleaned()` on BOTH sides
    of the park, mirroring `ChangeControlEmbargoManager.wait_for_release`.
    `cleanup` notifies every waiter before dropping state, so a thread parked
    when the plane dies previously woke with `notified=True` and reported an
    ordinary wakeup; the teardown now surfaces here, naming this table, instead
    of one hop later inside the caller's next acquisition.
    (3) Two regression tests, both single-threaded and deterministic - the
    release is forced into the window by a patched `wait_for_change` rather
    than by timing luck, so neither can pass or fail on scheduling.
    ALSO REVERTED IN THIS PASS: the three static AST tests I added earlier.
    They asserted source SHAPE, not behaviour, and would fail for a rename or
    an extracted helper - Rank F under testing_overview.md and exactly what
    synaptic 6.3 forbids. Filing them was rationalising a bad test, and the
    docstring lock-order law they were meant to guard stands on its own.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:1256-1260
  - src/melder/aether/aetheric_mediator/mediator.py:_admit_with_wait
  - src/melder/aether/aetheric_mediator/claim_table.py:wait_for_change
  IMPACT: The plane's admission latency now matches the working system's under
    contention. The broader lesson is recorded because it caused three wrong
    turns in one session: this package was built by porting NAMES from DevOps
    while reimplementing the MECHANISMS, and every defect found today lives in
    a mechanism I wrote myself rather than one I copied.
  NEXT: Owner runs the suite. Then audit the REMAINING hand-written mechanisms
    against their DevOps counterparts on the same suspicion - the session join
    and depth model, and the strategy commit-delta ordering, are the two that
    were reimplemented rather than ported.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-02T18:35:00Z
  TYPE: RISK
  CLAIM: PRESERVED FROM AN UNDELIVERABLE MAILBOX MESSAGE. bootstrap_0 sent
    helper_f a NOTICE at 2026-08-02T17:55:00Z that was never consumed, because
    helper_f was retired by owner directive on 2026-08-02 before reading it. The
    content is copied here by tester_0 and the message then deleted, per
    `mailbox_protocol.md:59-61` - durable history lives in tickets, never in the
    mailbox - because deleting it unread would have destroyed the only copy.
    THE SUBSTANCE: bootstrap_0 AUTHORED GRAPH SEMANTICS FOR ALL 38 NODES of
    `src/melder/aether/aetheric_mediator` under EPIC-2026-08-02-author-graph-semantics,
    having first parked the story at 16:35Z out of deference to this being an
    active build lane, then reversed at 17:55Z on the reasoning that a
    per-node staleness stamp makes wrong prose self-announcing (SEMANTICS_STALE)
    while UNSEMANTIC is simply absent and announces nothing. They wrote the prose
    FROM THIS PACKAGE'S DOCSTRINGS ALONE, never from the design intent, and asked
    the lane owner to correct anything that reads wrong. THREE ASSERTIONS THEY
    EXPLICITLY FLAGGED FOR A SECOND PAIR OF EYES, none of them yet verified by
    anyone who built this package: (1) that INTENT (`ix`) is the HIERARCHICAL
    PARENT-SCOPE MARKER rather than an escalation marker; (2) that refusal leaves
    NO TRACE; (3) that `BROKEN` is deliberately a distinct terminal state from
    `ABORTED` because a half-built world is a work surface rather than debris.
    Nothing of this lane's source was touched - descriptors are a separate tree.
    TO CORRECT A NODE: edit the descriptor under
    `system_docs/graph/melder/aether/aetheric_mediator/`, then
    `graph_walker.py --accept <node_id> --apply` and reassemble. No ack was
    requested and none can now be given.
  EVIDENCE:
  - tickets/stories/completed/2026-08-02_src-melder-aether-aetheric-mediator_graph_semantics_story.md
  - tickets/epics/completed/2026-08-02_author-graph-semantics_epic.md
  - system_docs/graph/melder/aether/aetheric_mediator/
  IMPACT: 38 nodes of published graph prose describe THIS story's design intent
    and were written by someone who did not hold it, from docstrings that this
    repo has independently found to be wrong elsewhere (see
    TASK-2026-08-02-stale-source-docstrings, which found at least six false
    docstring claims in adjacent Conduit code). The reviewer bootstrap_0 was
    counting on has departed, so the review debt now sits with whoever takes this
    lane. Authored graph prose reads as verified whether or not anyone verified it.
  NEXT: Whoever claims this lane reads the three flagged assertions against
    `claim_mode.py`, `claim_table.py` and `transaction_session.py` and either
    re-stamps or corrects the descriptors.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

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
OWNER-RUN on 3.14t, green. Command:
`pytest tests/unit/melder/aether/aetheric_mediator tests/component/melder/aether/aetheric_mediator -q`

Run history (owner-executed; NOT run by any agent):
- run 1: 35 unit passed; 1 component failed (namespace-package `__file__` is None)
- run 2: 3 failed / 56 passed (two `__file__`, one wrong starvation assertion)
- run 3: 71 passed
- run 4: 5 failed / 78 passed - ALL FIVE were MY test bug: a root session opens at
  depth 1, so `begin`/`leave` must balance before `commit`, and only `commit`
  enforces it
- run 5: 2 failed / 86 passed - again MY test bug, and the failure SHAPE was the
  tell: a `def` inside a test body binds the closure to a local name the test
  frame keeps alive, so a loop leaves exactly the LAST closure looking leaked
- run 6: 88 passed

Coverage: Not run. No agent has executed `pytest --cov`; density is the standard
applied here per testing_overview.md:123-135.

- DATETIME: 2026-08-01T00:05:04Z
  TYPE: MEASURE
  CLAIM: T5-T10 COMPLETE. 14 modules, 3,679 LOC, all compiling, and the ONLY
    external import across the whole package is
    `melder.utilities.general_base.cleanable`. End-to-end behaviour proven with
    two real strategies (whole-world `CheckpointLoad` claiming world=x, and
    frame-scoped `FormationLoad` claiming world=ix + frame=x):
    1. `missing_types()` reports the 4 unregistered vocabulary members at boot.
    2. Two DISJOINT formation loads admit CONCURRENTLY on one world via ix.
    3. A whole-world load correctly BLOCKS behind them and times out with
       `wait_timeout` after the configured bound.
    4. Reporting answers by scope and by type while transactions are in flight.
    5. Same identity on the same thread JOINS (same object, depth 2) rather
       than opening a second root.
    6. Commit releases claims AND stamps a freshness baseline; `stale_regions`
       correctly reports both a stale region and a never-reported one.
    7. LEAVE_BROKEN terminates BROKEN, runs NOTHING, and returns the residue
       ledger.
    8. Claims are RELEASED even under LEAVE_BROKEN.
    9. The whole-world load admits once the frames clear.
    10. Plane drains to zero claims and zero in-flight.
  EVIDENCE:
  - src/melder/aether/aetheric_mediator/mediator.py
  - src/melder/aether/aetheric_mediator/transaction_session.py
  - src/melder/aether/aetheric_mediator/information_registry.py
  IMPACT: The LoadGate re-expression is DEMONSTRATED, not just argued: whole-world
    exclusivity and disjoint frame parallelism coexist under one claim table with
    no new mechanism. The owner's two-outcome policy works end to end.
  NEXT: T11 - real tests on 3.14t (owner-run), then the three subsystem surveys.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-08-01T00:05:04Z
  TYPE: RISK
  CLAIM: ALL harness evidence to date ran on PYTHON 3.10 against COPIES with
    `StrEnum` and `Cleanable` SHIMMED and imports rewritten. It proves the
    ALGORITHM. It does NOT prove the shipped wiring, `__slots__` behaviour
    against the real `Cleanable`, or anything under free-threaded 3.14t.
  EVIDENCE:
  - src/melder/aether/aetheric_mediator/mediator.py
  IMPACT: Nobody should read "10/10 checks pass" as "this is tested". T11 is
    real work, not a formality.
  NEXT: Owner runs the suite on 3.14t once T11 tests exist.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Standalone package, 14 modules. The one rule that matters: it must not import
`melder.aether`. Everything else follows from that.

Core is COMPLETE through T10 and demonstrated end to end. What remains before
this is trustworthy: T11 real tests on 3.14t, the three subsystem surveys, and
owner rulings on the epic's open questions - especially whether the top plane
claims FRAME scope keys (it currently does, via `ScopeKey.frame`) and whether
inner frame transactions JOIN the top session or stay siblings.
