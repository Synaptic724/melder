

# Task: Identify the rare multi-millisecond events in Melder's gauntlet scope cycles

## Metadata
- Task ID: TASK-2026-09-26-attribute-gauntlet-tail-spikes
- Story: STORY-2026-09-26-gauntlet-runtime-speed
- Status: in_progress
- Owner: user
- Agent Name: melder_2
- Priority: p1
- Created: 2026-09-26T19:43:02Z
- Updated: 2026-09-26T19:50:01Z

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
- from_state: draft
- to_state: in_progress
- transition_reason: The owner's runs show the Melder-specific tail, and the owner asked for it to be investigated
  before the averages.

## Steps / Checklist
- [x] VM: harness GC instruments (probe, per-turn slowest turns with gc_during, GC disabled A/B).
- [x] VM: probe for the non-GC candidates (audit-hook compile/exec events, cache-emit calls, root-lock waits) with
      per-cycle timestamps, correlated with the slow cycles.
- [ ] Owner run on Windows with the harness instruments; compare with the VM.
- [ ] Attribution note plus ranked fix candidates; DECISION_REQUEST.
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

## Context / Handoff Summary
VM attribution done. Melder's big cycle spikes are the one-time lazy hydration and compilation of executors at
first meld in turn 0 (a warm-up removes them). No GC fires in the gauntlet loop. A collection, when an application
triggers one, costs about 2x dishka's, because importing melder pulls in ~576 modules. The DECISION_REQUEST lists
the fix candidates. Waiting on the owner's Windows run with the harness instruments and the owner's pick.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
