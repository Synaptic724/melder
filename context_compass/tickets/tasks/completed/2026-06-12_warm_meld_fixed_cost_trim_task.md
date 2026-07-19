

# Task: Trim warm-meld / spellspace-exit fixed cost and shared-surface inflation

## Metadata
- Task ID: TASK-2026-06-12-warm-meld-fixed-cost-trim
- Story: none
- Status: done
- Owner: claude
- Agent Name: compiler_builder_0
- Priority: p1
- Created: 2026-06-12T22:05:01Z
- Updated: 2026-06-12T22:32:25Z

## Objective
Close the cached-meld fixed-cost gap (melder 0.44us vs dishka 0.29us per
cached meld; spellspace exit 0.45us vs 0.23us) and reduce the cross-thread
meld inflation (+59-65% per meld at threads=3, equal across outer and
request families => shared-surface mechanism). Melds are ~68% of every hot
scope cycle; this is the remaining competitive gap vs dishka at threads>=3
(melder ~22.0k vs dishka ~29.2k hot scopes/s, quiet-machine baseline).

## Ticket Contract
- ENTRY_GATE: active board row; fresh research read of the current cached
  meld warm path (conduit front door -> creations lookup; spellspace meld;
  spellspace exit/recycle) - other lanes changed src this session.
- EXECUTION_BOUNDARY: meld warm/cached paths in
  `src/melder/aether/conduit/` (conduit meld front door, creations
  storage, spell_space meld + exit lanes) and directly-supporting
  utilities. NOT in scope: bind pipeline/compiler phases, phase
  scheduler, transaction mediator, ward lineage semantics, public meld
  signature (settled: spell positional, spell_name keyword-only).
- DEPENDENCIES: profile_scope_cycle_contention.py (sub-attributed meld
  segments) from the closed contention lane; real_world gauntlet.
- EXIT_GATE: each landed trim shows a measured improvement (per-meld ns
  and/or t3 inflation) on the harness AND no gauntlet ratio regression;
  user accepts closure.
- FAILURE_ESCALATION: CONFLICT note if a trim requires changing observable
  meld semantics (permissions, existence resolution, ward bookkeeping);
  BLOCKER if inflation traces to non-owned lanes or to CPython-level
  free-threading costs with no code-level mitigation.

## Scope Boundaries
- In scope: per-meld instruction-path attribution; attribute-hop and
  shared-object-touch reduction; pre-bound hot references; per-meld
  micro-benchmark additions to the existing harness; exit/recycle trim.
- Out of scope: meld signature changes; caching semantics changes;
  bind/conjure surfaces; ward-link retention.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: User accepted closure ("yeah sure") with the door
  target met (request door at dishka parity) and the construction-lane
  finding recorded as a compiler-lane handoff.

## Steps / Checklist
- [x] Research read: current cached-meld warm path end-to-end (conduit
      front door, creations lookup, spellspace meld, spellspace exit)
- [x] Attribute per-meld cost: instruction-path walk + harness extension
      (per-segment ns inside one cached meld; shared-object touch count)
- [x] User runs attribution; rank trims by ns and shared-touch count
- [x] Land trim #1 with tests; re-measure pending (harness + gauntlet ratios)
- [x] Repeat or close per evidence (closed: door target met; construction
      lane handed to the compiler lane)
- [x] Run Ticket Microcycle during execution.

## Deliverables
- Measured per-meld attribution (harness extension or new micro-harness)
- Evidence-ranked trim(s) in the meld warm path with tests

## Files / Paths Impacted
- src/melder/aether/conduit/ (meld warm path; exact targets UNKNOWN until
  attributed)
- benchmarks/testing_other_di/profile_scope_cycle_contention.py (possible
  extension)

## Validation
- Not run.
- Recommended commands:
  - `python benchmarks/testing_other_di/profile_scope_cycle_contention.py`
  - `pytest benchmarks/testing_other_di/test_real_world_gauntlet.py -q -s`

## Risks / Rollback Notes
- Micro-trims can silently change error surfaces; every trim lands with
  tests pinning the touched contract.
- Free-threaded inflation may be partly CPython refcount traffic;
  mitigation is touch reduction, not elimination - rank by measured ns.
- Cython-backed dependency-injector is not a parity target; dishka is.

## Applicable Anti-Patterns
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without acceptance confirmation and board-sync completion.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-06-12T22:05:01Z
  TYPE: PLAN
  CLAIM: Baselines carried from the closed contention lane: cached meld
    0.44us vs dishka 0.29us; spellspace exit 0.45us vs 0.23us; melds
    ~68% of hot cycle; cross-thread inflation +59-65% per meld at t3
    (equal across outer/request families; space_enter flat at 0.10us =>
    the shared surface is in the meld body, not scope entry); gauntlet
    melder ~22.0k vs dishka ~29.2k hot scopes/s (quiet baseline).
    Measurement-first: attribute inside one cached meld before any trim.
  EVIDENCE:
  - tickets/tasks/completed/2026-06-12_threads_contention_scope_cycle_breakdown_task.md:1-1
  IMPACT: Last competitive surface vs dishka at threads>=3; expected
    value +10-25% hot throughput if attribution finds avoidable touches.
  NEXT: research-read the cached-meld warm path end-to-end.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-12T22:20:00Z
  TYPE: FACT
  CLAIM: Fast-meld-door anatomy (conduit lane; spellspace lane is
    parallel-shaped): one cached HIT pays (a) isinstance + override-None
    checks, (b) `_fast_meld_doors.get` dict read (per-conduit dict,
    survives pool recycle - only permanent cleanup deletes it, and
    `reset_for_pool` preserves the captured creations object identity),
    (c) a guard ladder of ~6 SHARED-object attribute reads per hit:
    `self._meld_hooks`, `spell._hooks_enabled`,
    `spell._creation_context_switch.fast_state`,
    `spell._creation_context is captured_context`,
    `spellbook._spellbook_validation_required`,
    `spell.resolution_required`, (d) executor slot read through the live
    context (`captured_context._no_overrides_executor`), (e)
    `fast_executor(fast_creations)[0]` - tuple alloc + index per meld,
    (f) `spellbook._cache_emit_required` read. Spell, spellbook, and
    context objects are shared across ALL threads => per-hit atomic
    refcount/cache traffic on shared lines; this matches the equal
    inflation across meld families. ALSO: in scope-cycle workloads the
    FIRST meld of each existence per recycled scope runs the executor's
    construction body (storage was reset), so per-cycle meld cost =
    construction lane + repeat-door lane; the 0.44us-vs-0.29us gap is
    the repeat lane.
  EVIDENCE:
  - src/melder/aether/conduit/meld/conduit_meld.py:190-247
  - src/melder/aether/conduit/meld/meld.py:105-261
  - src/melder/aether/conduit/meld/spellspace_meld.py:214-349
  IMPACT: Preliminary trim candidates (UNVERIFIED ranking, attribution
    must confirm): (1) collapse the guard ladder into one precomputed
    fast-state slot maintained by the existing invalidation chokepoints
    (6 shared reads -> 1); (2) mirror the two spellbook flags into
    conduit-local slots; (3) avoid the per-hit tuple alloc - executor
    contract is shared with the compiler lane, needs coordination.
  NEXT: extend the harness to time meld#1 (construction lane) vs meld#2
    (pure door) separately per family, plus a tight repeat-meld
    micro-loop for the 0.44us decomposition; user runs; rank trims.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-12T22:35:00Z
  TYPE: MEASURE
  CLAIM: Attribution harness landed in
    profile_scope_cycle_contention.py: (1) cycle sweeps now time meld#1
    (construction lane) vs meld#2 (pure repeat door) separately for both
    families; (2) new BENCH_CONTENTION_MICRO=1 mode runs tight
    repeat-meld loops (default 200k iters, warmup 1000) on per-thread
    private lessers with barrier-synchronized start - pure fast-door
    per-op ns for outer and request melds at each thread count,
    isolating door cost + cross-thread guard inflation from all cycle
    machinery. Not run (user executes).
  EVIDENCE:
  - benchmarks/testing_other_di/profile_scope_cycle_contention.py:1-1
  IMPACT: Micro t1 number should reproduce ~0.44us cached meld; t3/t5
    deltas isolate the shared-guard inflation; meld#1-vs-#2 split shows
    whether construction or door dominates per-cycle cost.
  NEXT: user runs sweep + micro modes; rank trims from the numbers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-12T22:50:00Z
  TYPE: MEASURE
  CLAIM: Attribution run (user, gil=disabled). MICRO (pure door, private
    lessers, barrier start, 200k iters): outer 382ns / request 353ns at
    t1; ~1,001ns at t3 (2.6x); ~1,620ns at t5 (4.2x). The pure door
    inflates massively with zero shared STORAGE - the shared reads are
    the guard ladder itself (spell flags, context identity, spellbook
    flags, shared meld-hooks dict, executor slot) => atomic
    refcount/cache-line ping-pong on shared objects is CONFIRMED as the
    inflation mechanism. CYCLE sweeps: meld#1 construction lane owns
    ~76% of per-cycle meld cost at t1 (outer 2.84us / request 3.10us vs
    door 0.56/0.54us) and inflates +52% (t3) / +94% (t5); door-in-cycle
    inflates less (1.4x t3) because cycle machinery spaces out hits.
  EVIDENCE:
  - benchmarks/testing_other_di/profile_scope_cycle_contention.py:1-1
  IMPACT: Trim #1 target = guard-ladder shared-touch count. Design:
    consolidate the 5-6 live guards into ONE epoch integer compare -
    add a door-epoch slot bumped at the existing invalidation
    chokepoints (hook toggle, context swap/cleanup, validation flag,
    resolution flag, meld-hooks registration via spellbook-wide epoch,
    phase-11 executor hot-swap). Door entry captures (spell, epoch,
    executor, creations); hit = dict get + one int compare + executor
    call. Epoch-bump on hot-swap lets the entry capture the executor
    directly (one extra normal-lane rebuild per spell after hydration).
    Expected: t1 380ns -> ~300ns; t3/t5 inflation cut by the removed
    shared touches. Construction-lane trim is fix #2 (executor body is
    compiler-lane-owned; needs coordination).
  NEXT: propose trim #1 to user; on approval implement epoch slot +
    chokepoint bumps + door rebuild, with tests pinning every
    invalidation path (hooks, context swap, validation, resolution,
    hot-swap, meld-hooks registration).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-12T23:10:00Z
  TYPE: DECISION
  CLAIM: Trim #1 LANDED - epoch-consolidated door guard. `Spell` gains
    `_door_epoch` (slot + init 0); bumps at: `_set_hooks` (hook gate
    change), `_cleanup_creation_context` (covers context clear AND switch
    reset; also covers `_invalidate_for_revalidation` which calls it),
    meld.py deferred-resolution failure regating, and
    spellbook_creation_system cache-rehydration regating
    (`resolution_required = True` sites). Becoming-VALID transitions
    (resolution_required=False) intentionally do not bump - stale-pass
    is impossible because entries are rebuilt on the post-valid normal
    pass. Door entries are now 4-tuples `(spell, context, creations,
    captured_epoch)` with the epoch read BEFORE the building meld
    executes (mid-meld bumps invalidate the new entry). Hit ladder in
    BOTH doors is now: meld-hooks truthiness + epoch compare + context
    identity + spellbook validation flag (drops `_hooks_enabled`,
    `_creation_context_switch.fast_state` object hop, and
    `resolution_required` reads). Executor still read per hit through
    the live context (phase-11 hot-swap preserved; zero compiler-lane
    edits). Tests: `_poison_entry` seam updated to 4-tuple; new
    `test_component_fast_door_epoch_invalidates_on_hook_attach` pins the
    chokepoint->miss->hook-lane path. Door registry docs updated.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:209-215,360-370,560-590
  - src/melder/aether/conduit/meld/conduit_meld.py:200-260,300-360
  - src/melder/aether/conduit/meld/spellspace_meld.py:214-260,316-370
  - src/melder/aether/conduit/meld/meld.py:66-82,211-214,620-630
  - tests/component/melder/aether/conduit/test_conduit_component_fast_meld_door.py:465-502
  IMPACT: Per-hit shared-object hops cut from ~8 to ~5; expected t1
    380->~320ns and a material cut to the 2.6x/4.2x t3/t5 inflation.
    RISK note: direct writes to `resolution_required`/hook lists that
    bypass the chokepoint methods will NOT invalidate doors - the
    chokepoint contract is now load-bearing (documented at the slot).
  NEXT: user runs door component suite + micro + sweep + gauntlet; then
    decide trim #2 (construction lane, compiler-lane coordination).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-12T23:30:00Z
  TYPE: MEASURE
  CLAIM: Trim #1 validated on the micro harness (user-run): pure door t1
    outer 382->336ns (-12%), request 353->287ns (-19%, now AT dishka's
    0.29us cached-meld parity); t3 ~1001->900ns (-10%); t5
    1620/1536->1405/1428ns. Cycle-sweep t1 door lanes improved
    (outer_meld2 0.56->0.51us, request_meld2 0.54->0.47us). The t5 sweep
    and gauntlet runs were swarm-contaminated (create stalls up to
    4.3ms, melder max 70ms, dishka max 10.5ms - all frameworks noisy);
    gauntlet ratios melder/DI 0.553, melder/dishka 0.772, within the
    loaded-machine noise band. Tests: 2027 passed incl. the new epoch
    test; 3 failures were one stub drift (_RecordingSpell lacked
    _door_epoch) - stub updated to mirror the live contract.
  EVIDENCE:
  - tests/unit/melder/spellbook/test_cache_runtime_verification.py:42-60
  IMPACT: Fixed-cost goal of the lane is met for the repeat-door lane
    (request at dishka parity, outer within 15%). Remaining inflation is
    the residual ~5 shared hops (spell, context, spellbook, executor,
    instance refcounts) - diminishing room without structural change.
    Construction lane (meld#1, ~3us, 76% of cycle melds) is the
    remaining big slice and is compiler-lane-owned.
  NEXT: stub re-run GREEN (50/50, user-run 2026-06-12). Decision
    pending: close lane (micro goal met; construction-lane finding
    handed to the compiler lane) or keep open for construction-lane
    coordination.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-12T22:32:25Z
  TYPE: DECISION
  CLAIM: CLOSURE. Delivered: epoch-consolidated fast-door guard (Spell
    `_door_epoch` + 4 chokepoint bumps; 4-tuple entries; both doors),
    meld#1/#2 + micro attribution modes in the contention harness, stub
    fix, epoch invalidation test. Measured: pure door t1 request
    353->287ns (dishka parity), outer 382->336ns; t3/t5 contended door
    -10-13%; suites green (2027 + 50 after stub fix).
    HANDOFF (compiler lane, compiler_strategy_0): the remaining warm-meld
    slice is the CONSTRUCTION lane - meld#1 of each existence per
    recycled scope runs the compiled executor body at ~2.7-3.1us (76% of
    per-cycle meld cost at t1) and inflates +52% (t3) / +94% (t5) from
    shared-object traffic inside the executor (spell/blueprint/dep
    reads). Reproduce with profile_scope_cycle_contention.py (meld#1
    rows; BENCH_CONTENTION_MICRO=1 for the door-only baseline).
    Executor body is codegen-owned; touch-reduction there is the next
    evidence-backed cut.
  EVIDENCE:
  - benchmarks/testing_other_di/profile_scope_cycle_contention.py:1-1
  IMPACT: Lane target met for the repeat lane; remaining competitive
    melders gap at threads>=3 now lives in executor construction, owned
    by the compiler lane.
  NEXT: none (lane closed).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Successor to the contention lane (fix #1 landed there: narrowed parent
lock). This lane owns the per-meld fixed cost and the deferred fix #2
shared-surface inflation. Attribution first (instruction-path walk +
harness extension), then trims land one at a time with tests, validated
on the harness and gauntlet ratios.
