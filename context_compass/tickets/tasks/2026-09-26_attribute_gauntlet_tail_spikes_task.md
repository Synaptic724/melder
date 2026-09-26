

# Task: Identify the rare multi-millisecond events in Melder's gauntlet scope cycles

## Metadata
- Task ID: TASK-2026-09-26-attribute-gauntlet-tail-spikes
- Story: STORY-2026-09-26-gauntlet-runtime-speed
- Status: review
- Owner: user
- Agent Name: melder_2
- Priority: p1
- Created: 2026-09-26T19:43:02Z
- Updated: 2026-09-26T20:35:11Z

## Objective
Name the event behind Melder's rare scope-cycle spikes in the gauntlet, and prove it with measurements. In
every owner run, Melder's single-cycle maxima are 4-10x dishka's and dependency-injector's (outer cycle 6-10 ms,
request window 4-7 ms), while the p99s are equal. Candidates the owner named: GC, cache rebuild, lock
contention, lazy compilation, allocator, OS scheduling, deferred-refcount collection. The output is an attribution
with evidence and a fix candidate for each confirmed cause. Fixes are their own tasks.

## Ticket Contract
- ENTRY_GATE: the owner's 19:31Z / 19:34Z runs, filed with same-run ratios; the owner asked for the tail first.
- EXECUTION_BOUNDARY: read-only on src/ and benchmarks/. Probes and runs happen on the VM copy and in artifacts.
  The harness's own opt-in instruments are used first (GAUNTLET_GC_PROBE, GAUNTLET_PER_TURN_GC,
  GAUNTLET_PER_TURN_CSV, GAUNTLET_GC_MODE, GAUNTLET_TREND_WINDOWS). Owner runs on Windows decide.
- DEPENDENCIES: VM copy of the device tree; the owner's Windows runs; melder_0 owns code emission and the meld
  doors, if the cause lands there.
- EXIT_GATE: each spike class is attributed with evidence, or marked UNKNOWN with what would settle it; fix
  candidates are ranked; DECISION_REQUEST to the owner.
- FAILURE_ESCALATION: BLOCKER if the tail cannot be reproduced anywhere measurable; CONFLICT if the fix sits in
  another lane's files.

## Scope Boundaries
- In scope: the Melder lane of the gauntlet harness and the runtime paths its cycles run (lesser and SpellSpace
  lifecycle, melds, creations disposal, pools, locks), the process GC, compilation and file I/O on the loop.
- Out of scope: changing the harness or src in this task; the average-cost levers (measure task).

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: The tail is attributed on the VM and confirmed on Windows (turn-0 first use, no GC in the
  loop); the fix candidates went to the owner as a DECISION_REQUEST, and the owner's picks remain.

## Steps / Checklist
- [x] VM: harness GC instruments (probe, per-turn slowest turns with gc_during, GC disabled A/B).
- [x] VM: probe for the non-GC candidates (audit-hook compile/exec events, cache-emit calls, root-lock waits) with
      per-cycle timestamps, correlated with the slow cycles.
- [x] Owner run on Windows with the harness instruments; compare with the VM.
- [x] Attribution note plus ranked fix candidates; DECISION_REQUEST.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- artifacts/gauntlet_runtime_speed_20260926/tail/ (runs, probes, attribution)

## Files / Paths Impacted
- context_compass/ tickets, boards and artifacts only.

## Validation
- Not run yet.
- Recommended commands (owner, Windows, free-threaded venv):
  - GAUNTLET_GC_PROBE=1 GAUNTLET_PER_TURN_GC=1 python benchmarks/testing_other_di/real_world_gauntlet_gil_runner.py

## Risks / Rollback Notes
- The VM has 2 vCPUs, so three threads are oversubscribed and scheduling spikes dominate there. VM runs attribute
  mechanisms (GC pauses, compile events, lock waits); only owner runs size the Windows tail.
- Instrumentation can move the tail; each instrument is compared against an uninstrumented run.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No cause named from a single max value; slow turns are attributed individually.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/gauntlet_runtime_speed_20260926/tail/
  - artifacts/gauntlet_runtime_speed_20260926/owner_run_20260926_1931_10k_30k.txt
  - artifacts/gauntlet_runtime_speed_20260926/owner_run_20260926_ratios.txt
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: task closure; the owner confirms retention.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T19:43:02Z
  TYPE: PLAN
  CLAIM: Order of work:
    1. The harness already carries opt-in tail instruments (_GcPauseProbe via gc.callbacks, per-turn gc_during and
       gen0 live counts, slowest-N turns in time order, a GC-disabled or frozen mode, trend windows). Run them on
       the VM copy first to test GC.
    2. Probe the remaining candidates: lazy compile/exec (sys audit hook), cache-file emission
       (Spellbook._emit_cache_file_if_required), waits on the root conduit lock shared by every thread.
    3. Ask the owner for one Windows run with the instruments.
    The spikes sit in single cycles (p99 unchanged), so each slow turn is attributed individually.
  EVIDENCE:
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1406-1512
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1541-1745
  - tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md:793-816
  IMPACT: The owner's own instruments come first, so the attribution uses tools the owner already trusts.
  NEXT: VM run: GAUNTLET_GC_PROBE=1 GAUNTLET_PER_TURN_GC=1 DI_GAUNTLET_ITERS=10000 on the 0.2.68 copy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T19:47:37Z
  TYPE: MEASURE
  CLAIM: VM (combined 0.2.68 copy, 3.14.7t, 10k iterations, the harness's own instruments GAUNTLET_GC_PROBE=1 and
    GAUNTLET_PER_TURN_GC=1). No collection fired in any library's measured loop: collections=0, gc.get_stats
    delta +0, gen0 live flat at 7770 (DI), 10943 (dishka) and 6112 (melder). The Melder-only tail still shows
    without GC: outer-cycle max 7.35 ms against DI 1.61 and dishka 1.48; request-window max 5.76 against 1.60
    and 1.06. Melder's slowest turn is turn 0 (11.8 ms against dishka's 3.4 ms). The other slow Melder turns are
    4.8-7.0 ms clusters with no collection. On this 2-vCPU VM, DI and dishka show 2.5-4.7 ms clusters too.
  EVIDENCE:
  - artifacts/gauntlet_runtime_speed_20260926/tail/vm_harness_gcprobe_10k.txt:1-96
  IMPACT: GC does not trigger in the gauntlet loop on the VM, so it cannot explain the steady-state tail here.
    The owner's machine still needs the same probe to confirm.
  NEXT: Attribute the slow cycles one by one with probe_tail.py (per-turn cycle maxima plus compile/exec/open audit
    events).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T19:47:37Z
  TYPE: FACT
  CLAIM: Melder's largest single cycles are first-use compilation inside turn 0. probe_tail.py ran the harness's
    _run_gauntlet_once for 10k turns with a sys audit hook; the run was repeated twice with the same result.
    - The six slowest cycles are the FIRST cycle of each lane in turn 0: outer 3.7-7.1 ms, request window
      2.0-3.9 ms.
    - Turn 0 carries all 30 compile/exec events of the loop, all "<melder_site_plan_executor>": the site-plan
      executors are compiled at first meld. No open() fires on the loop, so there is no cache-file I/O.
    - Outside turn 0, 2-3 of 10k turns have a cycle over 2 ms, and about 3% have one over 1 ms (VM
      oversubscription).
    - The probe's own retained rows triggered one gen-0 collection at turn 308. It paused the process for
      8.6-9.5 ms: the cost of one stop-the-world collection with Melder's world loaded. The harness alone
      triggers none.
  EVIDENCE:
  - artifacts/gauntlet_runtime_speed_20260926/tail/probe_tail_melder_10k.txt:1-33
  - artifacts/gauntlet_runtime_speed_20260926/tail/probe_tail.py:1-92
  IMPACT: Two Melder-specific tail mechanisms are identified. (1) Lazy compilation of executors at first meld: a
    one-time cost per process, which the gauntlet times because it has no warm-up. (2) The size of a GC pause:
    a collection costs roughly 9 ms with Melder loaded, whenever an application triggers one. Candidates not
    seen on the VM loop: cache rebuild or I/O, and deferred-refcount collection (P3 is not in the code).
  NEXT: Split turn 0 into compile and other first-use costs; measure tracked-object counts and full-collection
    time per library world; then ask the owner for the same instruments on Windows.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T19:49:27Z
  TYPE: MEASURE
  CLAIM: What turn 0 pays, per library (VM, probe_firstuse.py, the harness's own _run_gauntlet_once, two runs).
    - Melder, cold: the first cycle of each lane costs 2.9-9.8 ms (outer) and 2.1-3.9 ms (request window).
      Across the lanes, turn 0 runs 17 generalized hydrations, 15.5-16.7 ms of work in total: site-plan runtime
      builds 11.7-14.1 ms, of which executor compile is 7.7-8.1 ms.
    - Melder, warm (every lane run once on a throwaway thread before timing): first cycles fall to 0.03-0.04 ms
      and turn 0 to 2.4-2.6 ms, the same as later turns.
    - dishka's first cycles: 0.8-4.1 ms. DI's: 0.05-0.73 ms.
    - One full gc.collect() of the loaded world: Melder 5.3-6.0 ms (95k tracked objects), dishka 2.1-3.2 ms
      (49k), DI 1.9 ms (45k).
  EVIDENCE:
  - artifacts/gauntlet_runtime_speed_20260926/tail/probe_firstuse_vm.txt:1-22
  - artifacts/gauntlet_runtime_speed_20260926/tail/probe_firstuse.py:1-68
  IMPACT: Confirmed on the VM: Melder's biggest cycle spikes are the one-time lazy hydration and compilation of
    executors at first meld (by design since S2b: "Hydration builds the normal inner executor at first meld").
    The gauntlet times turn 0, so it counts them.
  NEXT: Find what makes Melder's world 2x the tracked objects, since that sets every GC pause.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T19:49:27Z
  TYPE: FACT
  CLAIM: Melder's larger GC pause comes from its import footprint, not its runtime objects.
    - After setup and 2 turns, Melder's world holds 96k tracked objects to dishka's 49k. The additions are mostly
      code objects (20.3k), functions (20.2k), tuples (13.2k) and dicts (7.9k). Only about 2.0k objects are
      instances of melder classes.
    - "import melder" alone: 100 ms, 576 melder modules, +56k tracked objects. Nexus (the AR runtime) is 155 of
      those modules, the crystallizer 35 and mutation_research 27. A plain DI user touches none of these.
    - A full collection right after "import melder" takes 2.5 ms on the VM.
  EVIDENCE:
  - artifacts/gauntlet_runtime_speed_20260926/tail/probe_heap_vm.txt:1-6
  - artifacts/gauntlet_runtime_speed_20260926/tail/probe_heap.py:1-26
  IMPACT: No collection fires in the gauntlet loop, but any collection an application triggers pauses every thread
    for about twice as long as with dishka. The same footprint is the parked setup gap (D3: setup 272-282 ms
    against 38-42 ms). Lazy imports of subsystems a DI user does not touch would shrink both.
  NEXT: DECISION_REQUEST to the owner with the fix candidates; ask for one Windows run with GAUNTLET_GC_PROBE=1 and
    GAUNTLET_PER_TURN_GC=1 to confirm turn 0 there.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T19:50:01Z
  TYPE: DECISION_REQUEST
  CLAIM: Candidate fixes for the tail, for the owner.
    (1) Turn-0 hydration, the observed spikes:
        (a) An explicit prewarm: a public call, or a SpellbookConfiguration flag, that hydrates every resolvable
            spell's executors at conjure. The harness would call it in Melder's setup, which is timed separately
            and honestly, the way dishka builds its factories at container creation. The cost moves into setup
            (about 15 ms on the VM for this world). Needs patch docs, since it changes when hydration happens.
            The hydration code is melder_0's.
        (b) Persist compiled executor code in the creation cache, so a warm process skips compile, about half
            of the cost. melder_0's caching and emission lane; a new cache generation.
        (c) A warm-up for every library in the harness before timing. It changes what the benchmark measures,
            so it is the owner's call only.
        Recommendation: (a). It is honest: the first request stops paying, and setup shows the cost.
    (2) GC pause size, a latent tail for applications: import the subsystems a DI user never touches (Nexus,
        crystallizer, mutation_research) lazily. That shrinks the tracked world, and with it import and setup
        time (the parked D3). It reverses the eager-boot ruling of 2026-08-03, so it stays parked unless the
        owner reopens it.
    (3) Confirm on Windows before acting: one run with GAUNTLET_GC_PROBE=1 and GAUNTLET_PER_TURN_GC=1. If turn 0
        heads the slowest turns and no collection fires, the attribution holds there too.
  EVIDENCE:
  - tickets/tasks/2026-09-26_attribute_gauntlet_tail_spikes_task.md:133-215
  - artifacts/gauntlet_runtime_speed_20260926/tail/probe_firstuse_vm.txt:1-22
  - src/melder/aether/spellbook/spell_compiler/executor_code_cache.py:1-177
  IMPACT: The owner picks (1a/b/c) and whether (2) reopens. The Windows run confirms the attribution first.
  NEXT: Report to the owner; wait for the Windows run and the pick.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T20:22:10Z
  TYPE: MEASURE
  CLAIM: Two owner Windows runs, filed verbatim, confirm the VM attribution.
    - 30k with GAUNTLET_GC_PROBE=1 and GAUNTLET_PER_TURN_GC=1 (20:05Z, tree 0.2.70). No collection fired in any
      library: collections=0, gc.get_stats delta +0, turns_with_collection 0/30000. gen0_live stayed flat: DI 17312,
      dishka 11006, melder 2547 (2498 at turn 0). Melder's slowest turn is turn 0: 10.172 ms total, 8.818 ms
      threaded, gc_during no. Its other 14 slowest turns are 2.90-3.78 ms, the same band as DI (2.90-3.55) and
      dishka (2.57-4.90). Melder's cycle maxima (outer 6.444, request window 4.775 ms) are therefore turn-0 first
      cycles, as on the VM.
    - 200k, no instruments (19:40Z, tree 0.2.69). Every library ran slower than in the 30k runs: iteration avg DI
      1.315 -> 1.603 ms, dishka 1.226 -> 1.604, melder 1.431 -> 1.836. The maxima hit all three: iteration max DI
      234.0, dishka 188.4, melder 99.4 ms; outer-cycle max 72.1 / 83.3 / 24.2 ms. In this run Melder's tail was the
      smallest.
    - Same-run ratios hold: hot_scopes/s melder/dishka 0.873 (200k) and 0.857 (30k); melder/DI 0.873 and 0.919.
      Active cycles/s melder/dishka: request 0.995 / 1.035, worker_a 0.858 / 0.905, worker_b 1.009 / 1.073.
    - Where the average gap sits. Per iteration, melder minus dishka is +0.232 ms (200k) and +0.205 ms (30k). The
      threaded phase carries +0.204 and +0.179 ms of it, bootstrap +0.005. Each iteration runs 10 request, 25
      worker_a and 30 worker_b cycles. Lane outer-cycle averages at 200k are melder 0.020 / 0.015 / 0.015 ms and
      dishka 0.018 / 0.012 / 0.012 ms (30k: melder 0.020 / 0.015 / 0.014). The longest lane, worker_b, accounts
      for about +0.06 to +0.09 ms. The remaining ~+0.11 to +0.12 ms of the threaded gap, in both runs, falls
      outside the timed cycles: thread wake, the lane loop, thread exit and join. The averages are printed to
      1 us, so each lane figure is uncertain by about +-0.015 ms on worker_b.
  EVIDENCE:
  - artifacts/gauntlet_runtime_speed_20260926/tail/owner_run_20260926_2005_30k_gcprobe.txt:1-113
  - artifacts/gauntlet_runtime_speed_20260926/tail/owner_run_20260926_1940_200k.txt:1-59
  - artifacts/gauntlet_runtime_speed_20260926/tail/owner_runs_1940_2005_ratios.txt:1-22
  IMPACT: The tail question is answered on Windows. GC never fires; the only Melder-specific spike is turn 0's
    first-use hydration and compile. The 200k maxima are machine events shared by all three libraries. The
    persistent average gap is ~0.2 ms per iteration: roughly half is inside worker_b's cycles and half lies
    outside the timed cycles.
  NEXT: Read the harness's trend-window instrument and the threaded-phase boundaries.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T20:22:10Z
  TYPE: FACT
  CLAIM: What the harness already measures.
    - GAUNTLET_TREND_WINDOWS=N splits a run into N equal windows. For each window it prints the iteration median,
      p99 and max, the threaded p99 and max, collections fired, gc.get_count() and the window's wall time. That is
      throughput per window, the slope question. It has no RSS column.
    - Per-turn gen0_live is gc.get_count()[0], i.e. tracked objects created minus freed since the last
      collection. Flat means no net growth during the loop; it is not heap size.
    - The threaded phase runs from start_event.set() to the last join(). Beyond the timed cycles it includes each
      thread's wake-up, the lane loop (rng, six list appends per cycle), thread exit and join. Each iteration
      spawns 3 new threads.
  EVIDENCE:
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1561-1566
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1621-1667
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1679-1713
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1244-1345
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1040-1092
  IMPACT: The long-run slope question needs no harness change: one 200k run with GAUNTLET_TREND_WINDOWS=20
    answers it within a single machine state. Only RSS would need an addition. The ~0.11 ms outside the cycles is
    per-iteration thread overhead, which a server with a thread pool would not pay per request.
  NEXT: VM test of one mechanism for that overhead: thread start, first use and exit cost after `import melder`
    against a bare interpreter and against dishka and dependency_injector.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T20:27:51Z
  TYPE: MEASURE
  CLAIM: Thread exit cost on free-threaded CPython accounts for most of the threaded phase beyond the timed cycles,
    and it is larger in Melder's world. VM runs of probe_threads*.py (3.14.7t -X gil=0, no src change, 1500
    iterations per process, medians):
    - A short-lived thread's exit+join slows down as live objects allocated by already-exited threads accumulate.
      Bare interpreter: 98-100 us. With 100k or 300k live instances created on the main thread: unchanged. When a
      worker thread creates 100k live instances and exits, every later thread takes 650-654 us; at 300k, 4.2 ms.
    - After each library's gauntlet world is built (setup plus 2 threaded turns), one short-lived thread's
      exit+join takes: DI 338-347 us, dishka 500-514 us, Melder 659-677 us. `import melder` alone changes
      nothing (103-113 us).
    - Running every lane and variant once on the main thread first lowers it: Melder 372-486 us, dishka 342-355,
      DI 324-328.
    - Gauntlet shape (3 threads per iteration, trivial work), threaded phase: bare 324 us, DI 411, dishka 571,
      Melder 745, and 544 for Melder with first use on the main thread.
  EVIDENCE:
  - artifacts/gauntlet_runtime_speed_20260926/tail/probe_threads_vm.txt:1-22
  - artifacts/gauntlet_runtime_speed_20260926/tail/probe_threads.py:1-90
  - artifacts/gauntlet_runtime_speed_20260926/tail/probe_threads2.py:1-87
  IMPACT: The gauntlet starts 3 new threads per iteration, so each iteration pays this exit cost. The cost grows
    with how much of a library's long-lived state was built on worker threads. Melder builds its executors at
    first meld and its pooled shells on whichever thread needs one, so in the gauntlet these objects outlive the
    turn-0 threads. This fits Windows in direction and size: +0.11 to +0.12 ms of Melder's threaded gap lies
    outside the timed cycles, against +174 us over dishka in the VM's 3-thread shape. It is a cost of the benchmark's
    shape (a thread pool pays it rarely), but it is real on 3.14t. Doing first use on the owning thread removes
    much of it, which strengthens candidate 1a (hydrate at conjure). The CPython mechanism is UNKNOWN; mimalloc's
    handling of abandoned pages at thread exit is the likely path. On Windows the effect is UNKNOWN until an owner
    run of probe_threads.py.
  NEXT: DECISION_REQUEST to the owner with the updated candidates and the Windows probe commands.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T20:28:34Z
  TYPE: DECISION_REQUEST
  CLAIM: Updated owner decisions. This supersedes the 19:50:01Z request, whose item 3 (the Windows run) is done.
    (1) One lever for the turn-0 spike and the thread-exit cost: hydrate every resolvable spell's executors at
        conjure, on the conjuring thread, behind a SpellbookConfiguration flag or a public call (recommended).
        - It removes the turn-0 spike (VM warm-up: first cycles 0.03-0.04 ms).
        - The executors stop living in memory owned by exited worker threads. On the VM, first use on the main
          thread cut Melder's thread exit+join from 659-677 us to 372-486 us.
        - The cost moves into setup, about 15 ms on the VM.
        - Next step: a VM prototype with no tree edit to size it, then patch docs and a NOTICE to melder_0, whose
          lane owns hydration.
        Alternatives:
        (b) Persist compiled code in the creation cache. This cuts compile time only, not the thread-exit part.
        (c) Warm up every library in the harness. That is the owner's call, because it changes what the benchmark
            measures.
    (2) Long-run slope: one 200k run with GAUNTLET_TREND_WINDOWS=20. No harness change is needed. An RSS column
        would be a harness change, the owner's call.
    (3) Windows check of the thread-exit mechanism: probe_threads.py with world_dishka, world_melder and
        mainwarm_melder, 3 threads each.
    (4) Import footprint (D3, which sets the GC pause size): stays parked unless the owner reopens it.
    Still pending from earlier:
    - P1 closure (R2 has landed).
    - P4 acceptance.
    - The SpellSpace active-scope RISK.
    - Who fixes the system_document_view race.
  EVIDENCE:
  - tickets/tasks/2026-09-26_attribute_gauntlet_tail_spikes_task.md:175-194
  - tickets/tasks/2026-09-26_attribute_gauntlet_tail_spikes_task.md:245-334
  - artifacts/gauntlet_runtime_speed_20260926/tail/probe_threads_vm.txt:1-22
  IMPACT: The owner's picks set the next task. (1) needs a prototype before any patch docs. (2) and (3) are owner
    runs.
  NEXT: Report to the owner. On a yes to (1), prototype conjure-time hydration on the VM copy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T20:35:11Z
  TYPE: DECISION
  CLAIM: Owner direction, replying to the DECISION_REQUEST: "we're not trying to win a benchmark here we're literally
    just trying to optimize code, and my pools should exist when the root makes them and not any other time".
    Consequences:
    - Candidate (1a), hydrating executors at conjure, is withdrawn. It removes no work: it moves the same code
      generation and compile from the first meld to conjure, and would also run for spells that are never melded.
      Lazy hydration is the documented design (zero hydration work at build time; hydrate once at first meld).
    - Pools: the ConduitPool is built in the normal root's constructor, and a SpellSpacePool in every conduit's
      constructor. The shells inside them are built on demand by the thread that needs one when none is idle, then
      reused. Read as a rule: no lever changes when pools or their shells are created, so no prewarming.
      prewarm_spellspaces stays an owner-chosen public call; the harness does not use it.
    - The thread-exit cost is a CPython 3.14t effect that the gauntlet's three new threads per iteration amplify.
      It is not per-request work in Melder, so it gets no fix.
    - Levers that remove work stay:
      - the worker lanes' in-cycle cost (+2-3 us per cycle), starting with worker_a's mix;
      - compile at first meld, through a compiled-code cache that works across processes (melder_0's lane, a
        handoff if the owner wants it);
      - import size (parked).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:161-258
  - src/melder/aether/conduit/conduit.py:347-361
  - src/melder/aether/conduit/conduit_pool.py:106-121
  - src/melder/aether/conduit/conduit.py:2643-2652
  - src/melder/aether/conduit/spell_space/spell_space_pool.py:118-145
  - src/melder/aether/conduit/conduit.py:1236-1262
  IMPACT: Supersedes items (1) and (3) of the 20:28:34Z DECISION_REQUEST. The tail work ends with the attribution;
    what remains open for the owner is (2), the 200k trend run, if wanted. The next lever is real per-cycle work in
    the scope lifecycle.
  NEXT: Once the owner agrees, break down the worker_a cycle step by step against dishka on the VM (no tree edit).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Attribution is done and confirmed on Windows. No collection fires in the gauntlet loop, and Melder's only specific
spike is turn 0's first-use hydration and compile (10.2 ms); its other slow turns match DI and dishka. Side
finding: on 3.14t a thread's exit cost grows with live objects left by exited threads, which the gauntlet's three
new threads per iteration amplify. Owner direction (last note): optimize code, not the benchmark; pools and their
shells are created when they are today. Conjure-time hydration is withdrawn. Open for the owner: an optional 200k
run with GAUNTLET_TREND_WINDOWS=20. Next lever (measure task): the worker lanes' per-cycle cost.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
