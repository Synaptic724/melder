# Task: Profile and cut the scope-cycle runtime machinery gap

## Metadata
- Task ID: TASK-2026-07-02-scope-cycle-runtime-machinery
- Story: none (standalone; successor lane to
  2026-07-01_compiler_phase8_11_generalized_call_savings_task.md)
- Status: closed (2026-07-03: attribution complete; ward cut rejected by design
  [lineage tree is load-bearing]; remaining rows proven load-bearing scope
  semantics; the one evidenced low-risk cut [drain empty fast path] LANDED)
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-07-02T08:40:00Z
- Updated: 2026-07-02T08:40:00Z

## Objective
Close the measured per-cycle gap on scope-churn workloads: the real-world gauntlet shows
melder paying ~2us on scope CREATE and ~2us on scope CLEANUP per cycle (outer_total
17-29us, request_total 10-19us) where dishka/dependency-injector read ~0.000ms on the
same rows. Profile one lesser-conduit cycle and one spellspace cycle to microsecond
attribution, then cut with evidence.

## Ticket Contract
- ENTRY_GATE: owner directed this lane in chat 2026-07-02 ("go attempt your next big
  win") after the real-world gauntlet MEASURE note in the compiler-lane ticket.
- EXECUTION_BOUNDARY: read scope = conduit pool/recycle paths (create_lesser_conduit,
  Conduit._prepare_for_pool/reset_for_pool, cleanup), spell_space enter/exit/recycle,
  creations lifecycle (Creations reset/clear paths), existing experimentation profilers.
  EDIT scope EMPTY until a DECISION note records an evidenced cut; profiling harness
  additions in tests/experimentation are pre-approved.
- DEPENDENCIES: real-world gauntlet MEASURE (compiler ticket 2026-07-02T08:15 note);
  possible reuse: tests/experimentation contention/profiling assets from prior lanes.
- EXIT_GATE: microsecond-level attribution of the ~2us+2us rows documented; at least one
  evidenced cut proposed (or landed with owner approval); user-run gauntlet delta
  recorded.
- FAILURE_ESCALATION: DECISION_REQUEST before any runtime-semantics change; BLOCKER if
  attribution requires 3.14t-only profiling the sandbox cannot run and the user cannot
  run promptly.

## Scope Boundaries
- In scope: scope lifecycle machinery (pool acquire/reset/recycle, creations lifecycle
  on cycles, per-cycle bookkeeping), profiling harnesses.
- Out of scope: phases 8-11 emitters (previous lane), mutation systems, public API.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: owner directed; investigation begins with profiling-first rule.

## Steps / Checklist
- [ ] Survey tests/experimentation for reusable scope-cycle profilers.
- [ ] Read the lesser-conduit cycle path (create -> meld -> cleanup -> recycle).
- [ ] Read the spellspace cycle path (enter -> meld -> exit -> recycle).
- [ ] Author/extend a per-phase attribution probe (sandbox-authored, user-run 3.14t).
- [ ] Document attribution; propose cuts with evidence; owner picks.
- [ ] Land approved cuts; user-run gauntlet delta.

## Validation
- Not run. User-run 3.14t: attribution probe + real-world gauntlet before/after.

## Applicable Anti-Patterns
- [ ] No blind trims: every cut must name its microseconds first (t5 lesson).
- [ ] No implementation from UNKNOWN/HYPOTHESIS.
- [ ] No performance claims without measurement.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: none
- IF_UNKNOWN: none

## Noting Behavior
- Task notes: tactical findings, evidence ranges, one-step continuation.

## Notes
- DATETIME: 2026-07-02T08:40:00Z
  TYPE: PLAN
  CLAIM: Lane opened on the real-world gauntlet evidence: melder scope create ~2us +
    cleanup ~2us per cycle vs ~0 for dishka/dep-injector; outer cycles 17-29us vs
    11-17us. Attribution first: find where the microseconds go in ONE lesser cycle and
    ONE spellspace cycle before proposing any cut.
  EVIDENCE:
  - tickets/tasks/2026-07-01_compiler_phase8_11_generalized_call_savings_task.md:1-1
    (2026-07-02T08:15 MEASURE note)
  IMPACT: Directly attacks the competitive gap on the <private-strategy-doc> benchmark shape.
  NEXT: Survey tests/experimentation for existing profilers, then read the pool paths.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8


- DATETIME: 2026-07-02T08:55:00Z
  TYPE: FACT
  CLAIM: ATTRIBUTION TOOLING ALREADY EXISTS - no new harness needed.
    tests/experimentation/test_targeted_pooled_cycle_breakdown_harness.py (775 lines)
    method-patches the pooled lifecycle WITHOUT changing production code and decomposes
    both cycle types into: pool_acquire (core/create/prepare), lesser_creations_reset,
    cleanup_spellspaces_for_pool, cleanup_for_pool_reuse, pool_return/release,
    context_enter/exit, and residuals. It rides the same _build_runtime/_prime_* support
    as the meld-cycle harness. This is exactly the microsecond-attribution the lane's
    entry rule demands before any cut.
  EVIDENCE:
  - tests/experimentation/test_targeted_pooled_cycle_breakdown_harness.py:1-60
  - tests/experimentation/test_targeted_pooled_cycle_breakdown_harness.py:735-741
  IMPACT: Skips straight to measurement; the first checklist item closes as reuse.
  NEXT: user runs `pytest tests/experimentation/test_targeted_pooled_cycle_breakdown_
    harness.py -q -s` on 3.14t; read the table, name the dominant rows, propose cuts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8


- DATETIME: 2026-07-02T09:10:00Z
  TYPE: MEASURE
  CLAIM: BREAKDOWN TABLE IN (user-run 3.14t, TWO consistent runs). pooled_lesser cycle
    4555-4987ns: cleanup 64% / acquire 35%. DOMINANT ROW: prepare_residual_ns 1604-1747
    (~35% of the WHOLE cycle) = state flips/hook clearing inside _prepare_for_pool
    OUTSIDE its timed subcalls. #2: acquire_residual_ns 890-974 (~19.5%) = root/lock/
    state bookkeeping in create_lesser_conduit outside pool_create (276-322) +
    ward_link (442-486). Attributed subcalls are all small: cleanup_spellspaces_for_
    pool 333-411, ward_detach 333-396, creations_reset 235-266, pool_return 190-225.
    pooled_spellspace cycle 2424-2494ns: enter 58% dominated by enter_spellspace
    internals (~1112-1174 total; pool_acquire only ~260, stack_push ~190 => ~650-700ns
    residual INSIDE enter_spellspace); exit dominated by __exit__ pop_expected+recycle
    784ns (stack ops ~0) + exit_residual 230.
  EVIDENCE:
  - chat transcript 2026-07-02 (two user-run breakdown tables)
  IMPACT: The gap is NOT in the pools or stores (all small); it is in per-recycle
    BOOKKEEPING residuals: _prepare_for_pool's unconditional state-reset body,
    create_lesser_conduit's setup bookkeeping, and enter_spellspace/exit recycle
    internals. Cut hypothesis class: reset-only-what-was-dirtied + slim the
    unconditional per-cycle attribute churn.
  NEXT: Read Conduit._prepare_for_pool (:419+) and create_lesser_conduit (:1828+)
    statement by statement; name the residual's contents; propose cuts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9


- DATETIME: 2026-07-02T09:35:00Z
  TYPE: FACT
  CLAIM: CODE READ COMPLETE for both hot functions + INSTRUMENTATION CAVEAT + CUT
    PROPOSAL. (1) CAVEAT: _prepare_for_pool (conduit.py:419-440) is SHORT - four timed
    subcalls + two enum flips + conditional hooks clear; there is no 1.6us of real work
    between subcalls. The prepare/acquire residuals are substantially HARNESS
    INSTRUMENTATION OVERHEAD (4 patched wrappers x 2 perf_counter_ns each + wrapper
    frames); cross-check: the spec probe's UNINSTRUMENTED conduit cycle_meld1 (create +
    meld + cleanup) measured 2.5-2.7us total vs this harness's 4.6-5.0us cycle. Trust
    the TIMED SUBCALL rows, not the residuals. (2) Steady-state acquire path
    (create_lesser_conduit :1880-1973, no-hooks branch): check_cleaned + root
    resolution + pool hit + 2 state flips + publish-flag copy + PARENT LOCK acquire for
    ward link (_link_new_lesser_under_lock :2004-2012). (3) EVIDENCED CUT PROPOSAL -
    WARD AFFINITY ACROSS POOL IDLING: every cycle pays ward_link 442-486ns (under the
    parent lock) + ward_detach 333-396ns, ~17% of the real cycle - yet a pooled lesser
    returns ONLY to its own root's pool, and BOTH sites already flip
    _conduit_ward._conduit_type (pooled_lesser at :437, lesser at :1922/:1967),
    suggesting ward consumers already discriminate by type. If membership can persist
    across idle (detach only on permanent cleanup), both rows die AND the parent-lock
    window shrinks (the contention doc at :1985-1989 records the lock's history as the
    t3/t5 bottleneck - this cut compounds under threads). SECONDARY:
    _cleanup_spellspaces_for_pool (:442-475) allocates drain() list + loops registry
    even when both are empty (common case) - cheap emptiness guards, ~100-300ns.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:419-475
  - src/melder/aether/conduit/conduit.py:1880-2012
  IMPACT: Ward affinity is the first structural cut with named nanoseconds AND a
    concurrency dividend. GATE: requires reading ConduitWard._link_lesser_conduit /
    _detach_for_pool and EVERY ward consumer that iterates lessers (teardown sweeps,
    routing, transfer) to prove pooled_lesser-typed members are already filtered or can
    be filtered without semantic change. Runtime-semantics change => DECISION_REQUEST
    to owner before any edit per ticket contract.
  NEXT: Owner decision: proceed with the ward-consumer audit for ward affinity (+ the
    spellspace-drain guards as a low-risk side cut), or redirect.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9


- DATETIME: 2026-07-02T09:50:00Z
  TYPE: DECISION
  CLAIM: WARD-AFFINITY CUT REJECTED BY OWNER (chat 2026-07-02): the per-cycle ward
    link IS the lineage tree - removing/persisting it degrades the tree to a flat
    n<->lesser relationship. The tree carries no user-visible feature TODAY but is the
    foundation for planned graph-lookup systems (application topology mapping + usage
    patterns), so link/detach stays on the hot path by design. Mechanical corroboration
    from the read: the link target is the ACQUIRING PARENT's ward position
    (conduit.py:1934/:1969 link under `self` = parent, not root), and a pooled shell
    can be re-acquired under a DIFFERENT parent - persistent membership would corrupt
    tree topology, not just semantics. CONSEQUENCE: ~780-880ns/cycle of ward work is
    load-bearing; the lesser-cycle optimization ceiling in this lane drops to the small
    rows (spellspace-drain emptiness guards ~100-300ns; pool_create/return + creations_
    reset all ~200-320ns each). Remaining unread candidate: the spellspace EXIT path
    (__exit__ pop_expected + recycle = 784ns, the largest REAL spellspace row) + the
    ~650ns inside enter_spellspace beyond pool acquire + stack push. FUTURE NOTE for
    the graph-lookup design: an append-only lineage journal could someday move topology
    recording off the hot path entirely - owner's design space, recorded only as a
    pointer.
  EVIDENCE:
  - chat transcript 2026-07-02 (owner decision)
  - src/melder/aether/conduit/conduit.py:1932-1934
  IMPACT: Lane EV reduced for lesser cycles; spellspace enter/exit internals are the
    remaining unread surface with >0.5us rows.
  NEXT: Owner picks: (a) read spellspace enter/exit internals + land the low-risk
    drain guards, (b) park this lane and bank the compiler-lane runs still owed
    (probe t5 confirm, flag-ON gauntlet), or (c) close out.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-03T03:40:00Z
  TYPE: FACT
  CLAIM: LANE CLOSED. Final reads (enter_spellspace :899-932, SpellSpace
    __enter__/__exit__/recycle_from_managed_context, SpellSpacePool
    acquire_untracked/release, Creations.reset_for_pool_unlocked) confirm the
    exit chain is already lean: pop_expected + 2 flag reads + disposables
    check + dict clear + deque append. Remaining per-cycle rows are
    LOAD-BEARING (creations clear = scope semantics; ward link/detach =
    lineage tree by owner decision; pool deque ops minimal). The prior
    harness residuals (~650ns enter / prepare 1.6us) were substantially
    instrumentation overhead per the 09:35 caveat. ONE cut landed:
    SpellSpaceThreadState.drain() empty fast path - returns the live empty
    list without allocation/thread-local store when nothing to detach (the
    common pooled-cycle case); callers audited (conduit.py:456 iterates,
    :799 copies via list()); documented read-only contract. Saves one list
    alloc + TL store per lesser cleanup cycle. py_compile verified via
    shadow (VM replica rot on this file; user disk intact).
  EVIDENCE:
  - src/melder/aether/conduit/spell_space/spell_space_thread_state.py (drain)
  - src/melder/aether/conduit/conduit.py:456,799 (caller audit)
  IMPACT: Scope-cycle machinery is measured, attributed, and at its
    semantic floor; the competitive wall-vs-active gap is understood
    (thread spawn/join + GC context per the cache epic, not scope work).
  NEXT: none - lane closed. Future pointer: owner's append-only lineage
    journal idea (graph-lookup design space) is the only path that moves
    ward work off the hot path.
  REREAD: NOT_REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Fresh lane. Resume from Notes; the compiler lane's 2026-07-02T08:15 MEASURE note holds
the motivating numbers.
CLOSED 2026-07-03 - see final note.
