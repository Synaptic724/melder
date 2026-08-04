

# Task: Trim shared-object traffic in the compiled executor construction lane

## Metadata
- Task ID: TASK-2026-06-13-executor-construction-lane-trim
- Story: none (handoff from compiler_builder_0's closed warm-meld lane)
- Status: closed (orphan sweep 2026-07-11, melder_0, owner-directed:
  compiler_strategy_0 does not exist; trim #1 landed emitter-only June
  13 and every full-tree green since covers the suites leg; RESIDUE:
  trim #2 (warm-tail singleton specialization) was design-gated for a
  fresh session and never started - re-ticket from its spec here if
  wanted; the contention-sweep/gauntlet perf evidence was never run)
- Owner: claude
- Agent Name: compiler_strategy_0
- Priority: p1
- Created: 2026-06-13T06:30:00Z
- Updated: 2026-06-13T22:13:34Z

## Objective
Pick up the construction-lane handoff: meld#1 of each existence per recycled
scope runs the compiled no-overrides executor body at ~2.7-3.1us (76% of
per-cycle meld cost at t1) and inflates +52% (t3) / +94% (t5) from
shared-object reads inside the executor (spell/creations/lock traffic).
Door lane is at dishka parity (287ns); this is the remaining competitive
gap at threads>=3. Reduce per-step shared touches in the EMITTED body
without changing meld semantics.

## Ticket Contract
- ENTRY_GATE: handoff RAISE anchor + closed-ticket final note
  (2026-06-12_warm_meld_fixed_cost_trim_task.md:278-302).
- EXECUTION_BOUNDARY: codegen_creation_system emitters/compilers + runtime
  helpers the emitted body calls (`_construct_spell_instance`,
  `_register_spell_instance_prebound`), executor namespace assembly in
  spell_codegen_creation_cache.py / spellbook_creation_system.py:560-640.
  NOT: conduit doors (epoch contract is compiler_builder_0's landed work),
  ward semantics, meld signature, scheduler, dev_ops.
- DEPENDENCIES: profile_scope_cycle_contention.py meld#1 rows +
  BENCH_CONTENTION_MICRO=1 baseline (compiler_builder_0's harness).
- EXIT_GATE: measured meld#1 per-op drop and/or t3/t5 inflation cut on the
  harness, no gauntlet ratio regression, suites green, user accepts.
- FAILURE_ESCALATION: BLOCKER if inflation is dominated by CPython
  free-threaded refcount traffic on instances themselves (no code-level
  mitigation in our surfaces); CONFLICT if a trim would change observable
  construction semantics (lock disciplines, registration order, disposal
  bookkeeping).

## Scope Boundaries
- In scope: emitted-source shape (locks taken, shared reads per step),
  executor namespace binding choices, registration-block cost, per-step
  alias elision.
- Out of scope: existence semantics, disposal contract, door lanes.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: user redirected the compiler lane to this handoff;
  overrides-plan lane parked (see its DECISION note).

## Steps / Checklist
- [ ] Research read: emitted body anatomy end-to-end (DONE for the
      generalized no-overrides emitter; remaining: `_emit_construct_instance`,
      `_append_register_source`, `_append_creations_target_source`,
      namespace assembly, `_construct_spell_instance` generic path).
- [x] Baseline: user re-ran contention harness (sweep + micro) post-epoch
      trim; meld#1 numbers current (see MEASURE note).
- [ ] User runs profile_construction_lane.py; rank the 4 suspects from the
      report.
- [ ] Rank per-step shared touches; propose trim #1; implement with tests.
- [ ] Validate on harness + gauntlet; iterate or close.

## Validation
- 2026-06-13 trim #1 user-run validation: unit 2010 + component 391 green,
  ZERO test drift (the exploding-lock hit-path test held by design).
  Cycle sweep vs same-session baseline: t1 meld#1 2.69->2.54us outer /
  2.96->2.78us request (-5.6/-6.1%), cycles/s 87.3k->91.1k; t3 meld#1
  4.34->4.12 / 4.65->4.33us, cycles/s 165.6k->179.7k (+8.5%); t5 meld#1
  6.26->5.11 / 6.46->5.48us, cycles/s 187.4k->232.6k (+24%, partially
  confounded by a much quieter t5 run -- stalls fell 22->1 -- so claim
  t1/t3 only). Gauntlet: melder 23,456 hot_scopes/s (was ~22.0k),
  melder/dishka 0.746, no regression; doors unchanged (untouched lane).
  Honest attribution: ~5-6% meld#1 from emitter slimming, consistent at
  t1/t3; remaining gap is trim #2 territory.
- Original commands:
  - `python benchmarks/testing_other_di/profile_scope_cycle_contention.py`
  - `$env:BENCH_CONTENTION_MICRO="1"; python benchmarks/testing_other_di/profile_scope_cycle_contention.py`
  - `pytest benchmarks/testing_other_di/test_real_world_gauntlet.py -q -s`

## Applicable Anti-Patterns
- [ ] No trim from HYPOTHESIS: measurement ranks before any edit.
- [ ] No semantic drift in lock disciplines or registration order.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: true (long session; this ticket is the
  resume root).

## Noting Behavior
- Note focus: per-step touch inventory, measured rankings, one trim at a time.

## Notes
- DATETIME: 2026-06-13T06:30:00Z
  TYPE: FACT
  CLAIM: Emitted-body anatomy (generalized no-overrides lane). The source
    is identity-free and shape-cached process-wide
    (executor_code_cache.py, sha256-keyed, lock-free hits); ALL identity
    arrives as function DEFAULT PARAMETERS (steps, step_spells,
    step_spell_ids, step_disposal_methods, step_existences,
    step_instance_keys, step_dep_keys, root_instance_key + helper refs),
    so per-call reads are frame-local loads, not dict lookups. LOCALS MODE
    (all steps inlinable + all deps emitted) keeps step results in plain
    locals - no instance_results dict, no tuple hashing. Per-step shared
    touches by existence: many w/o disposal = constructor call only (zero
    locks, spell_N read only if owner-targeted); many w/ disposal =
    creations lock + register block; unique-likes = lock-free
    `_creations.get` hit, double-checked creations-lock miss; spell-lock-
    hint path adds `spell_N._lock` (SHARED across all threads) nested over
    the creations lock on miss. Inflation suspects, in rank order
    (HYPOTHESIS, unmeasured): (1) `step_spells[N]` tuple reads = refcount
    traffic on shared Spell objects per step per scope cycle; (2) shared
    `creations._creations` dict reads + `_lock` words for outer-scoped
    deps inside request cycles; (3) register-block work for
    disposal-tracked request instances per recycle; (4) helper-call
    overhead in the generic `_construct_spell_instance` path (dict-mode
    spells only).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:186-280
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:336-475
  - src/melder/aether/spellbook/spell_compiler/executor_code_cache.py:1-43
  - tickets/tasks/completed/2026-06-12_warm_meld_fixed_cost_trim_task.md:278-302
  IMPACT: trim surface is concrete; measurement must rank (1)-(4) before
    any edit because refcount traffic (1) may have no code-level fix in
    our lane (escalation path documented in contract).
  NEXT: finish the research read (construct/register/target emitters +
    namespace assembly), then have the user run the fresh meld#1 baseline.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-13T07:05:00Z
  TYPE: MEASURE
  CLAIM: Fresh post-epoch baseline (user-run, gil=disabled, 29-class
    gauntlet). Cycle sweep t1: outer_meld1 2.69us / request_meld1 2.96us
    (5.65us of 7.31us total melds = 77%); doors 0.51/0.47us; space_exit
    0.59us; cleanup 1.26us; create 0.97us. t3: meld1 4.34/4.65us (+61/+57%).
    t5: meld1 6.26/6.46us (+133/+118%). Micro doors: t1 334.9/289.5ns
    (matches the epoch-trim numbers), t3 952/1247ns, t5 1393/1414ns.
    Handoff numbers CONFIRMED current. Built the discriminator:
    benchmarks/testing_other_di/profile_construction_lane.py -- standalone
    (does not touch compiler_builder_0's live harness), single-threaded
    construction-only cycles (no repeat melds, so every profiled meld is a
    meld#1), re-execs PYTHON_GIL=1, ranks tottime + lane attribution
    (gauntlet __init__ floor vs _construct_spell_instance vs registration
    vs lock traffic vs create/cleanup machinery). The t1 report separates
    the raw constructor floor from melder overhead; the t3/t5 refcount
    mechanism stays with the harness micro mode (invisible to cProfile).
  EVIDENCE:
  - benchmarks/testing_other_di/profile_construction_lane.py:1-1
  IMPACT: trim ranking becomes evidence instead of the 4-way hypothesis;
    if the constructor floor dominates t1, the lane's value is entirely in
    contended-touch reduction, which changes which trims are worth landing.
  NEXT: user runs the profiler; rank suspects from
    construction_lane_profile.txt; propose trim #1.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-13T07:30:00Z
  TYPE: MEASURE
  CLAIM: t1 decomposition (user-run, 20k cycles, profiled 0.515s, 29.22us/
    cycle under profiler vs ~9.6us native = ~3.05x inflation; ranking
    valid, absolutes inflated). RANKING: (1) EMITTED-BODY OWN BYTECODE is
    the biggest block: step-factory self 0.087s + door-template self
    0.039s = 24% of profiled time (~1.5us native/cycle) -- the executor's
    alias loads, branches, and per-step plumbing, NOT helpers; (2) LOCKS:
    200k RLock enter + 200k exit = TEN lock pairs per cycle, 0.041s
    combined self (~8%); (3) DICT TRAFFIC: 440k dict.get = 22/cycle
    (0.039s) + get_creation 80k = 4/cycle; (4) CONSTRUCTOR FLOOR IS SMALL:
    all gauntlet __init__s sum ~0.031s self (~6%, ~0.5us native/cycle) --
    melder overhead dominates meld#1 ~4:1 over user code, so the trim
    headroom is real (dishka comparison says the floor is not the gap).
    Shape facts: door template runs 2x/cycle (both families) but the
    separate step-factory frame runs only 1x/cycle (the other family's
    steps execute inline in the template frame); many-existence transients
    construct 2x/cycle (once per family subtree -- correct semantics).
    Machinery (create_lesser 0.059 cum, cleanup->prepare_for_pool 0.089/
    0.075, ward link/detach, pool+thread-state) is the remaining ~35-40%
    and is NOT this lane's boundary (conduit-side, compiler_builder_0
    adjacent).
  EVIDENCE:
  - benchmarks/testing_other_di/construction_lane_profile.txt:1-1
  IMPACT: trim #1 candidate is emitted-source slimming (fewer per-step
    aliases/branches/locals in the hot shapes) + lock-pair count reduction
    inside the emitted body; both also cut shared touches, which is the
    t3/t5 mechanism. Constructor-floor pessimism is retired.
  NEXT: dump the actual emitted source for the outer + request shapes
    (count instructions and locks per step against the manifest rows),
    then propose trim #1 concretely.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-13T08:10:00Z
  TYPE: FACT
  CLAIM: Full emitted bodies captured (emitted_executor_sources.txt, via
    builtins.compile hook after the cache chokepoint provably did not see
    them). FINDINGS: (A) CACHE BYPASS -- the runtime step factory compiles
    through a `__melder_executor_factory__(bindings)` wrapper shape that
    appears in NO emitter I read and never passes executor_code_cache:
    there is a second runtime emission path (suspect:
    spellbook_creation_system.py:560-640 / shared_compiler_executions
    hydration lane) doing raw compile() -- same-shape spells repay
    compile() per conjure, and the process-wide dedupe the cache module
    documents is dead code on this path. (B) SINGLETON PREFIX WASTE -- the
    outer factory's steps 0-4 are unique-existence hits after cycle #1
    forever, yet every meld#1 re-walks them: per step it loads the shared
    Spell, reads spell._owner_creations (2nd shared touch), computes
    use_spell_lock_N BEFORE the hit check (only needed on miss), then
    does the shared dict get. 5 steps x 2 families x every cycle = the
    bulk of the shared-object traffic the t3/t5 inflation rides on.
    (C) PER-STEP REDUNDANCY -- `if caller_creations is None: raise`
    repeats per caller-lane step (6-7x per body) and many-no-disposal
    steps assign a DEAD `creations_N = caller_creations` local.
    (D) The overrides shape factory (534/573 lines, also compiled raw,
    also bypassing cache, embedding instance-key hash literals) is built
    per spell on override-free graphs -- more parked-ticket evidence.
  EVIDENCE:
  - benchmarks/testing_other_di/emitted_executor_sources.txt:1-1
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:236-280
  IMPACT: trim plan -- #1 mechanical emitter slimming (hoist the None
    check, delete dead locals, move use_spell_lock under the miss branch):
    zero semantic change, modest t1 win. #2 warm-tail specialization
    (post-first-run executor closing over resolved singleton instances,
    epoch-invalidated): kills 10-15 shared touches per meld#1, the direct
    t3/t5 lever, needs design + user decision. #A cache-bypass fix:
    cold-lane dedupe win at scale. Locate the wrapper emitter first.
  NEXT: find the `__melder_executor_factory__` emission site, then
    propose trim #1 + #A as one bounded patch; #2 as a design note.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-13T08:50:00Z
  TYPE: DECISION
  CLAIM: TRIM #1 LANDED (emitter slimming, zero semantic change), and
    finding (A) is RETIRED: `__melder_executor_factory__` is the
    executor_factory_cache second tier (sha256-keyed compile+exec dedupe
    per shape, lock-free hits) -- my "cache bypass" was its one-time miss
    build; no fix needed and the correction is recorded. Edits, all in
    generalized_manifest_no_overrides_compiler.py: (1) the
    caller_creations None guard is HOISTED to one check per body (emitted
    only when any row targets CALLER/SPELLSPACE; replaces 6-7 per-step
    re-checks); (2) per-step CALLER guard removed and the dead
    `creations_N` alias suppressed for many-without-disposal steps via
    `needs_creations_alias` (OWNER routing untouched -- its branch is a
    real guard); (3) `use_spell_lock_N` computation moved INSIDE the miss
    branch, so warm singleton hits skip two reads + compare per step per
    meld#1. Cache safety: both executor cache tiers key on source hash, so
    the new emission rebuilds cleanly; staged bundles with old source stay
    valid. Behavioral lock test (test_codegen_creation_compilers_core.py:
    950-973, exploding locks on the hit path) pins exactly the contract
    these edits strengthen.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:236-260
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:501-545
  - src/melder/aether/spellbook/spell_compiler/executor_factory_cache.py:104-165
  IMPACT: hot meld#1 bodies lose ~15-25 bytecode ops + the per-step guard
    branches; modest t1 win, small t3/t5 contribution. The BIG t3/t5
    lever remains trim #2 (warm-tail executor closing over resolved
    singletons, epoch-invalidated) -- design-gated, NOT started: it adds
    executor state to the door contract and deserves a fresh session with
    compiler_builder_0's epoch chokepoints read end-to-end.
  NEXT: user validation (suites + contention sweep + micro + gauntlet);
    then trim #2 design as its own microcycle.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-13T20:36:24Z
  TYPE: PLAN
  CLAIM: Trim #2 (warm-tail singleton specialization, epoch-invalidated) IS the
    adaptive PGO DI optimizer, and its full design is now persisted durably so it
    survives compaction. Added to the design artifact: §11 storage mechanism --
    a physically separate `__optimizations__` cache as a SECOND CachingSystem
    instance (one bundle per conduit, static bundle untouched, two-tier lookup),
    nested `spell_id -> variation_sha256 -> speculative_manifest` polymorphic
    keying (sha256 over the specialization signature), per-spell polymorphism cap
    K with generalized-pin fallback, in-memory `(spell_id, variation_sha256)`
    marker as the dedup/"already-done" check, and a flush cadence that writes
    in-memory per NEW specialization (lock-guarded) but flushes to disk only on
    `dirty_count >= flush_every_n` OR shutdown/atexit OR T-seconds-dirty (counts
    specializations not melds, self-quiescing), with cache writes isolated OFF
    the meld read path and OUT of the Transaction Admission Plane; plus §12, a
    consolidated build checklist + current status. Locked door decision recorded:
    new `optimizer_conduit_meld` + `optimizer_spellspace_meld`, construction-time
    selection, default doors untouched, OFF = zero added cost.
  EVIDENCE:
  - artifacts/2026-06-13_adaptive_pgo_di_optimizer_design.md:284-391
  - tickets/stories/backlog/2026-06-13_adaptive_pgo_di_optimizer_future_direction_story.md
  IMPACT: trim #2 is design-complete and durable; no chat-memory dependence. The
    next concrete move is Stage 0 (the decider micro-bench) on the 3.14t target,
    which gates whether any staged build proceeds. No source edits until that
    number clears warmup amortization and the §4 guard policy is signed off.
  NEXT: owner runs/approves the Stage 0 decider micro-bench (hand-rolled
    singleton-guarded body + epoch guard vs generalized resolve, threads 1/3/5).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-13T22:13:34Z
  TYPE: MEASURE
  CLAIM: STAGE 0 DECIDER = GO (mechanism confirmed; end-to-end magnitude TBD).
    User-run on 3.14t via
    tests/experimentation/stage0_singleton_specialization_decider.py (isolated
    dep-acquisition + root-construct, 3 arms over REAL melder objects, threads
    1/3/5, widths 5/12). NOGIL (gil=disabled): speculated/generic ratio width5
    0.74/0.73/0.73 (saved 269/1009/1658ns at t1/t3/t5); width12 0.72/0.61/0.64
    (saved 599/3179/4188ns). Ratio FALLS into t3/t5 and the win SCALES with dep
    count -> the predicted nogil shared-line contention relief is real. GIL
    CONTROL (gil=enabled): ratio FLAT ~0.71-0.75 (width5) / ~0.70-0.72 (width12)
    -> with the GIL there is no contention to relieve, so the flatness isolates a
    ~25-29% pure-shape win and proves the nogil ratio-fall is genuinely contention,
    not artifact. Real meld#1 anchor reproduces the ticket's t3/t5 inflation
    (+79/+107% width5, +83/+181% width12), so the synthetic graph sits in the right
    regime.
  EVIDENCE:
  - tests/experimentation/stage0_singleton_specialization_decider.py
  - artifacts/2026-06-13_adaptive_pgo_di_optimizer_design.md:177-391
  IMPACT: GO to Stage 1. HONEST CAVEATS: (a) the isolated arm OVERSTATES the
    end-to-end win -- it removes ONLY dep acquisition while real meld#1 keeps the
    door + root construct + register + gate; the RATIO is the trustworthy signal,
    the absolute saved_ns is an upper bound on meld#1 reduction. (b) the generic
    arm models the singleton read as `spell._owner_creations` per dep (ticket FACT
    note); if the live emitted body uses the frame-local `owner_creations` param
    instead, the win shrinks -- Stage 1 must confirm against the dumped emitted
    source. (c) dep-acquisition's true FRACTION of meld#1 is the number that sets
    the real payoff; Stage 1 (instrument the real body) quantifies it.
  NEXT: build Stage 1 (record + optimizer doors, observe-only) on user signoff;
    first sub-step confirms the `_owner_creations`-per-dep faithfulness against the
    live emitted body.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-13T22:13:34Z
  TYPE: FACT
  CLAIM: Existence->creations routing VERIFIED in code; Stage 0 generic arm
    confirmed FAITHFUL (MEASURE-note caveat (b) RESOLVED).
    `_creation_target_for_existence` (spell_generalized_codegen_lane_plan.py):
    unique_per_conduit -> CALLER, many -> CALLER, unique_per_spell_space ->
    SPELLSPACE, ELSE -> OWNER. So the OWNER / `_owner_creations` (speculatable
    shared-singleton) set is EXACTLY {unique, unique_per_conduit_cluster,
    unique_per_conduit_lineage} (matches `_lock_hint_for_existence` = spell_lock
    for those three). The OWNER step (`_append_creations_target_source`) reads
    `spell_N._owner_creations` PER DEP (preferred; the bound `owner_creations`
    param is only a None-fallback), then `creations_N._creations.get(spell_id_N)`
    -- the exact 3-shared-touch warm-hit shape (step_spells[N] load,
    _owner_creations attr, dict get) the Stage 0 generic arm modeled. So the
    experiment was faithful and the nogil ratios stand as measured.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:2211-2235
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:524-566
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation_cache.py:240-290
  IMPACT: speculatable set = the 3 OWNER existences. `unique` = SAFEST first
    target (frame-stable instance; Stage 0 measured this). cluster/lineage share
    the same per-step READ shape (so Stage 0's `unique` covers the cost) BUT carry
    more invalidation surfaces (cluster join/leave, lineage transfer) -> their
    guards must bump `_door_epoch` on membership change; harder, later. `many` =
    the separate "always-construct" sound slice. unique_per_conduit /
    unique_per_spell_space are caller/spellspace-scoped -> not cross-recycle
    singletons, not close-over-able.
  NEXT: Stage 1 targets `unique` deps first; cluster/lineage gated on the §4 guard
    extension for membership-change invalidation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Successor to compiler_builder_0's warm-meld lane (door at dishka parity).
This lane owns the executor BODY. Overrides-plan lane is parked, not dead:
tickets/tasks/2026-06-13_skip_dead_overrides_plan_build_task.md.
