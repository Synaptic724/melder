

# Task: Map where Melder can still gain on the shared gauntlet

## Metadata
- Task ID: TASK-2026-09-30-map-remaining-melder-gauntlet-gains
- Story: none; discovery for the owner (read, measure, recommend; no tree edit without the owner's pick)
- Related: tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md (melder_2's cost map and levers),
  tickets/tasks/completed/2026-09-30_investigate_gauntlet_order_dependence_task.md (the isolated harness)
- Status: done
- Owner: user
- Agent Name: melder_0
- Priority: p2
- Created: 2026-09-30T14:02:49Z
- Updated: 2026-09-30T15:27:09Z
- Completed: 2026-09-30T15:27:09Z
- Closure Basis: owner turn-in in chat (2026-09-30), answering "Want me to close this ticket out?": "ok
  yeah lets drop the change, go ahead and drop it and lets move on".
- Summary: Mapped Melder's remaining loop gap to dishka on the isolated gauntlet. No regression across the four
  releases compared; GC is about 0.2% of the loop; about 80% of the Windows gap is thread start/exit outside
  the timed cycles, with no single Melder cause. Option A (top-level creation-context doors) was prototyped as
  a VM-only overlay: about -2% CPU per scope cycle in the VM, +8-11% per cycle on the owner's Windows machine
  (the caller loses CALL_PY_EXACT_ARGS). Dropped by the owner; no source changed.

## Objective
Owner question (chat, 2026-09-30), after the first one-process-per-library run at 30000 iterations: "how can we
improve this? like its pretty fast but melder can get a bit quicker, what other things can we do I feel like we've
kinda milked it already" - and "ignore setup cost, we milked that too most of it is module imports". Find where
Melder's remaining loop gap to dishka sits now, check whether any of it is a regression since the last measured
state, and rank the levers left, excluding what the owner already dropped (deferred refcounting through ctypes,
conjure-time hydration, prewarming pools) and keeping the owner's rules (a lever removes work; pools and shells
are created when they are today; no unstable-API tricks; correctness first).

## Ticket Contract
- ENTRY_GATE: this board row routes here; the owner's run and the prior cost map are noted before any probe.
- EXECUTION_BOUNDARY: read-only in src/ and benchmarks/; probes and logs under
  artifacts/melder_gauntlet_gap_20260930/; runs in VM trees (the current mirror and older versions extracted with
  read-only git). No tree edit without the owner's pick, a NOTICE to the file owner and patch docs when
  system-impacting.
- DEPENDENCIES: melder_2's lane (cost map, dropped levers, open levers); the isolated harness (0.2.8212).
- EXIT_GATE: a ranked lever list with sizes and evidence, any regression located to a version range, and a
  DECISION_REQUEST; status review.
- FAILURE_ESCALATION: BLOCKER if older trees cannot run the current harness; DECISION_REQUEST before any edit.

## Scope Boundaries
- In scope: the loop only (setup excluded by the owner); per-version A/B of Melder on the current harness; the
  scope lifecycle, meld doors and thread-lifecycle costs; levers that remove work.
- Out of scope: setup and imports; dropped levers; changing the benchmark to favour Melder.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: owner asked in chat (2026-09-30T14:02:49Z); ticket and board row created before any probe.
- from_state: in_progress
- to_state: review
- transition_reason: (2026-09-30T14:40:56Z) exit gate met - no regression (0.2.74 to 0.2.8212 flat), GC ruled out,
  the gap located (mostly thread start/exit outside the cycles), the one clean in-cycle lever named, and
  the ranked DECISION_REQUEST filed; the owner picks A, B, C or D.
- from_state: review
- to_state: in_progress
- transition_reason: (2026-09-30T14:51:49Z) the owner picked option A in chat; the prototype runs as a VM-only overlay
  (DECISION and PLAN notes), no tree edit.
- from_state: in_progress
- to_state: review
- transition_reason: (2026-09-30T15:08:06Z) prototype built, tests pass under it (two introspection asserts aside), VM
  per-cycle A/B shows about -2% CPU per scope cycle and no resolvable gauntlet change; the owner runs the
  Windows A/B and decides whether to land it.
- from_state: review
- to_state: done
- transition_reason: (2026-09-30T15:27:09Z) owner turn-in in chat: option A dropped ("go ahead and drop it and lets move
  on"); nothing reached the tree, so the lane closes on its findings (option C in effect).

## Steps / Checklist
- [x] Note the owner's 30k run and the prior lever inventory.
- [x] A/B Melder across versions on the current harness (0.2.74, 0.2.82, 0.2.8207, 0.2.8212), dishka as control.
- [x] If a version range regressed, narrow it and read the change (none regressed).
- [x] Size the open levers that fit the owner's rules (GC, thread lifecycle, shell origin, hot functions).
- [x] DECISION_REQUEST with the ranked list.
- [x] Option A (owner's pick): build the top-level door overlay; check the doors are deferred and not nested.
- [x] Run the door-related tests under the overlay (full unit, component and integration suites).
- [x] Interleaved A/B in fresh processes (VM); hand the A/B driver to the owner for Windows.
- [x] Owner's Windows run of door_proto_cycles.py (door_proto_ab.py did not run): a loss, drop recommended.
- [x] Owner confirms dropping option A and closing the lane (turn-in).
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Evidence-backed notes and a ranked lever list for the owner.
- Probes and run logs under `artifacts/melder_gauntlet_gap_20260930/`.

## Files / Paths Impacted
- None in the repository tree (discovery); artifacts only.

## Validation
- Not run (nothing changed to validate). VM measurements only; every number is in the Notes and the
  artifacts.
- Recommended commands:
  - `pytest benchmarks/testing_other_di/test_real_world_gauntlet.py -s` with REAL_WORLD_GAUNTLET_ROUNDS=3

## Risks / Rollback Notes
- The VM has 2 cores; Windows decides. Old trees run the current harness, which must stay API-compatible with them.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without acceptance confirmation and board-sync completion.
- [x] No lever the owner already dropped comes back without a new reason.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/melder_gauntlet_gap_20260930/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: the owner's turn-in of this ticket.

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
- DATETIME: 2026-09-30T14:02:49Z
  TYPE: MEASURE
  CLAIM: Owner's first isolated run (Windows, 0.2.8212, 30000 iterations, one process per library): Melder
    36,608 ms, dishka 31,965 (Melder +14.5%, hot_scopes/s 0.873x), dependency-injector 38,350. Per iteration
    Melder is +0.154 ms: threaded phase +0.119, bootstrap +0.005, the rest (thread creation and start before the
    barrier) +0.030. Inside the request window Melder leads dishka on the request and worker_b lanes (active
    cycles/s 1.087x and 1.116x) and trails on worker_a (0.956x). Melder's outer scope costs about 1-2 us more per
    cycle (create 0.002 vs 0.001 ms, cleanup 0.002 vs 0.000 ms, 3-decimal resolution), and summing cycles per lane
    gives about +0.09 ms of lane time per iteration, of which the longest lane carries +0.03 ms; the rest of the
    threaded gap lies outside the timed cycles (thread start, exit and join).
  EVIDENCE: context_compass/artifacts/melder_gauntlet_gap_20260930/owner_run_30k_isolated_20260930.md:1-28
  IMPACT: The meld work inside the scopes is at or ahead of dishka; the gap is scope open/close plus the thread
    lifecycle, which is where levers have to come from.
  NEXT: Record the prior lever inventory, then check for a regression since 0.2.74.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-30T14:02:49Z
  TYPE: FACT
  CLAIM: Lever inventory from melder_2's lane (2026-09-26), with the owner's rulings:
    - done: P1 positional constructor calls; P4 SpellSpace.meld warm id lane (0.2.68); the nested slot-guard
      removal (0.2.73);
    - dropped by the owner: P3 deferred refcounting through ctypes (-23 to -36% per scope cycle on worker threads
      on the VM, but an unstable C API and "not a play"); spell-id interning (no gain); conjure-time hydration
      (moves work instead of removing it); prewarming pools or shells;
    - closed as measured: the scope lifecycle's contract-free trims (about 0.1 us per cycle);
    - open, never decided: thread-affine shell pools (-6 to -7% per cycle on Linux, Windows unknown); one lock for
      anonymous link (about 0.1 us); a single-check fast door (0.1-0.2 us); fewer shared-object hops per warm
      meld (never sized); a compiled-code cache across processes (melder_0's area; turn 0 only).
    Owner rules: a lever must remove work; pools and shells are created when they are today; correctness first.
    The last owner run in that lane (0.2.74, 22:47Z, all three in one process) put Melder at 0.919x dishka; today's
    same-layout runs gave 0.839-0.872x, so part of the gap may be new.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md:578-614
  - context_compass/tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md:1085-1164
  - context_compass/tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md:1165-1179
  - context_compass/artifacts/gauntlet_order_dependence_20260930/owner_runs_20260930.md:10-20
  IMPACT: The next answer must come from the open levers or from a regression, not from repeating dropped ones.
    The 0.919 -> 0.84-0.87 drop mixes harness changes (the 09-27 fairness review) with Melder changes, so only an
    A/B on one harness can say whether Melder got slower.
  NEXT: A/B Melder 0.2.74 / 0.2.82 / 0.2.8207 / 0.2.8212 on the current harness in the VM, dishka as control.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-30T14:16:00Z
  TYPE: MEASURE
  CLAIM: No Melder regression since 0.2.74 on one harness. VM, 3.14.7t with -X gil=0, 3000 iterations, the
    current harness copied into each tree, one process per run, two shuffled rounds (seed 31). Melder total ms:
    0.2.74 5207.7 / 5095.5, 0.2.82 5186.3 / 5086.2, 0.2.8207 5253.5 / 5113.3, 0.2.8212 5165.6 / 5170.9; dishka
    control 4398.0 / 4391.8. The spread between versions (at most 3%) is no larger than one version's
    round-to-round spread (0.2.74: 2.2%), so no version is measurably slower. All four trees recompiled Melder from
    source in every process (no usable .pyc; setup 566-602 ms), so they ran on equal footing, about 5% above the
    working mirror's level (next note).
  EVIDENCE: context_compass/artifacts/melder_gauntlet_gap_20260930/runs/version_and_tree_ab_summary.md:10-23
  IMPACT: The move from 0.919x dishka (0.2.74, 2026-09-26) to 0.84-0.87x today is not Melder getting slower. What
    remains is the harness (the 2026-09-27 fairness review) and Windows run-to-run variation; which of the two is
    UNKNOWN and does not change the lever list.
  NEXT: Settle the copied-tree discrepancy (fresh .pyc in both trees), then decompose the loop gap outside the timed
    cycles.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-30T14:16:00Z
  TYPE: MEASURE
  CLAIM: The same 0.2.8212 source ran slower from a copied tree than from the working mirror, and the setup half of
    that is stale bytecode. Tree A/B (seed 41, three rounds): wt2_new Melder 4604.5 / 4870.8 / 4879.1 ms, setup
    120-128 ms; trees/v08212 (a cp -r of wt2_new) 4995.1 / 4993.5 / 5024.2 ms, setup 569-573 ms; dishka 4458.2 /
    4313.0 / 4090.9. cp -r gave every .py a new mtime, so each copied .pyc was stale, and PYTHONDONTWRITEBYTECODE=1
    kept imports from rewriting it: every process recompiled Melder from source (about 450 ms). After compileall
    wrote fresh .pyc into the four trees (14:06Z; VM scratch only, run before this session's re-onboarding), a
    30-iteration v08212 run set up in 116.9 ms. Whether the 3-8% loop difference has the same cause is UNKNOWN.
  EVIDENCE:
  - context_compass/artifacts/melder_gauntlet_gap_20260930/runs/version_and_tree_ab_summary.md:25-37
  - context_compass/artifacts/melder_gauntlet_gap_20260930/runs/pyc_check_v08212_30it.jsonl:1-1
  IMPACT: If compiling in-process also slows the loop, Melder's process state after setup (heap size, allocator
    pages) is a loop lever - the mechanism the order-dependence lane measured for thread start/exit - and not only a
    setup cost.
  NEXT: Re-run the tree A/B with fresh .pyc in both trees, dishka as control.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-30T14:18:50Z
  TYPE: MEASURE
  CLAIM: With fresh .pyc in both trees the copied-tree slowdown is gone, so compiling Melder from source inside the
    process was what slowed the loop too. Tree A/B again (seed 51, three rounds, 3000 iterations): trees/v08212
    4585.0 / 4556.0 / 4595.2 ms, setup 119-124 ms; wt2_new 4516.5 / 4560.7 / 4626.5 ms, setup 121-126 ms; dishka
    4439.3 / 4365.8 / 4380.3 ms. The two trees now agree within 1%; before the recompile fix v08212 ran 3-8% slower
    in the loop, not only in setup. In this VM (2 vCPU) Melder sits about 4% behind dishka, against 14.5% on the
    owner's Windows machine (many cores), so the VM under-reproduces the contention part of the gap.
  EVIDENCE: context_compass/artifacts/melder_gauntlet_gap_20260930/runs/tree_ab_fresh_pyc.jsonl:1-9
  IMPACT: Work done in the process before the loop (compiling, allocating) changes the loop's speed afterwards. The
    same can hold for Melder's own setup work (runtime codegen compile, conjure garbage), so process state is a real
    loop lever. VM sizes of contention levers must be read as lower bounds; Windows decides.
  NEXT: Read how emitted executors are materialized (top-level functions or nested closures), since 3.14t gives
    top-level functions deferred refcounting and executors are shared by all worker threads.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-30T14:21:58Z
  TYPE: FACT
  CLAIM: What the harness puts inside and outside the timed cycles (read from the code). Each iteration: bootstrap
    fan-out on the main thread, then 3 new threads that wait on a barrier and an event; the threaded window runs
    from the event to the last join. A lane's timed cycle (outer_total) spans scope create -> melds -> cleanup;
    the harness closure, the metrics object, six list appends, the rng draw, thread wake-up, thread exit and join
    fall outside it, and that code is the same for every library. "active cycles/s" uses request_total (the
    inner scope only); "wall cycles/s" divides cycles by the threaded window. So Melder's +0.09 ms outside the
    cycles on Windows is not Melder code: it is the state Melder leaves in the process (GC heap, allocator
    pages, object ownership), which the same identical code then pays for. The harness can already report GC
    pauses (GAUNTLET_GC_PROBE=1) and run the loop with GC disabled or with the setup heap frozen
    (GAUNTLET_GC_MODE=disabled|frozen). Separately: site plans are exec'd as top-level defs in a fresh namespace,
    and melder_2 recorded (2026-09-26, before the site-plan lowering) that on 3.14.7t module-level functions and
    classes are already deferred while runtime closures, instances and dicts are not.
  EVIDENCE:
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1527-1626
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1659-1686
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1124-1176
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1824-1880
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_override_runtime.py:337-405
  - context_compass/tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md:435-452
  IMPACT: The biggest part of the gap (about 0.12 of 0.154 ms per iteration on Windows) sits in process-state
    costs, so the levers to size first are GC load and cross-thread object ownership, not the meld path.
  NEXT: Run the harness per library with GAUNTLET_GC_PROBE=1 in normal, disabled and frozen GC modes (VM, 3000
    iterations, interleaved) to size GC's share of each library's loop.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-30T14:24:06Z
  TYPE: MEASURE
  CLAIM: Garbage collection is not where the gap is. Harness runner per library, VM, 3000 iterations, GC probe on,
    two shuffled rounds of three modes (normal, disabled, frozen). During the loop Melder triggers one collection
    in 3000 iterations (8.4-10.2 ms pause, about 0.2% of its loop) and dishka none; frozen mode's one collection
    is the harness's own gc.collect() before the freeze. Loop totals (ms): Melder normal 4415.9 / 4744.9,
    disabled 4742.3 / 4683.7, frozen 4637.2 / 4730.0; dishka normal 4332.9 / 4385.1, disabled 4403.8 / 4382.4,
    frozen 4274.1 / 4144.3. Turning GC off or freezing the setup heap does not move Melder beyond the noise (about
    +-4% here).
  EVIDENCE:
  - context_compass/artifacts/melder_gauntlet_gap_20260930/runs/gc_modes_3000.log:1-48
  - context_compass/artifacts/melder_gauntlet_gap_20260930/probes/gc_modes.py:1-71
  IMPACT: A GC lever (fewer tracked allocations, a smaller live heap) cannot buy more than a few tenths of a
    percent. What remains outside the cycles is allocator and ownership state and the thread lifecycle.
  NEXT: Time the parts of one iteration outside the cycles (thread start, wake-up, per-cycle bookkeeping, exit and
    join) per library with a probe that mirrors _run_gauntlet_once.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-30T14:29:17Z
  TYPE: MEASURE
  CLAIM: In the VM, starting and joining threads is most of a gauntlet iteration, and it gets about three times
    slower once the workload has run, for both libraries, with Melder's process about 100-150 us per thread slower
    than dishka's. (1) Gap probe smoke (Melder, 200 iterations, a line-for-line copy of _run_gauntlet_once with
    timestamps): iteration 1763 us = bootstrap 18 + thread create/start 263 + barrier 27 + threaded window 1455;
    lanes wake 73-188 us after the start event, their cycles take 269-425 us, and the window closes 875-1027 us
    after a lane's last cycle (thread exit and join). (2) Sequential start+join of a no-op thread, by setup stage
    in one process: bare 206-239 us; after the harness import, the library import and bind + conjure still 172-231
    us; after singletons + 50 iterations Melder 756 / dishka 603 us; after 1000 more 729 / 635 us; after
    gc.collect() 708 / 598 us. (3) Not the per-thread refcount arrays of 3.14t (unique ids of heap types, code
    objects and globals dicts, pycore_object.h): growing a bare interpreter by 150,000 such objects adds about
    50-100 us, and imports did not move the cost at all.
  EVIDENCE:
  - context_compass/artifacts/melder_gauntlet_gap_20260930/runs/gap_probe_smoke_melder_200it.jsonl:1-1
  - context_compass/artifacts/melder_gauntlet_gap_20260930/runs/thread_stages_s1.jsonl:1-14
  - context_compass/artifacts/melder_gauntlet_gap_20260930/runs/uid_pool_probe_vm.txt:1-15
  - context_compass/artifacts/melder_gauntlet_gap_20260930/probes/gap_probe.py:74-171
  - context_compass/artifacts/melder_gauntlet_gap_20260930/probes/thread_state_probe.py:60-110
  IMPACT: The state that slows thread start/exit is created by the running workload (what worker threads allocate
    and leave behind), not by imports or conjure. Melder leaves more of it than dishka, which fits the owner's
    +0.03 ms before the barrier and most of the +0.09 ms outside the cycles on Windows.
  NEXT: Find what holds that state: add stages after the library's cleanup and a null-library run (harness only)
    to the thread-state probe.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-30T14:39:55Z
  TYPE: MEASURE
  CLAIM: The thread start/exit cost has no single Melder cause I could find. (1) Stages v2: the harness alone
    (scope cycles that do nothing) raises a no-op thread start+join from 211 to 377-407 us; dishka's workload to
    589-648; Melder's to 722-743, and Melder's own cleanup brings it back to 609 (dishka's level). (2) Survivor
    census after 50 iterations: no GC-tracked object from a gauntlet worker thread is left alive; Melder's only
    foreign-owned objects (1,317 compile artifacts: DagNodes, blueprints, sets, dicts) belong to its live daemon
    phase worker (MelderPhaseWorker-0), which stops at conduit cleanup. (3) Operation residue with an empty pool
    (shells built by worker threads): idle 236 us, lesser create+cleanup 403, + outer melds 433, + SpellSpace
    472, + request melds 487, full harness cycles 530; with shells prebuilt on the main thread the lesser cycle
    left 238-274 (noise +-60 us). (4) On the real harness loop (2000 iterations, three rounds) prebuilding six
    shells on the main thread changed the loop by -0.2%, +0.8% and +3.8% (3181.7 / 3099.8 / 3151.2 against
    3174.6 / 3125.9 / 3274.6 ms), within noise; the start+join cost stayed about 700 us either way.
  EVIDENCE:
  - context_compass/artifacts/melder_gauntlet_gap_20260930/runs/thread_stages_s2.jsonl:1-24
  - context_compass/artifacts/melder_gauntlet_gap_20260930/runs/worker_owned_census_50it.txt:1-18
  - context_compass/artifacts/melder_gauntlet_gap_20260930/runs/op_residue_r1_worker_built_shells.txt:1-6
  - context_compass/artifacts/melder_gauntlet_gap_20260930/runs/op_residue_r2_main_built_shells.txt:1-8
  - context_compass/artifacts/melder_gauntlet_gap_20260930/runs/prebuild_ab_2000it.jsonl:1-6
  - src/melder/aether/conduit/conduit.py:617-705
  IMPACT: The biggest bucket of the gap (thread start/exit under free-threading) grows with any workload and
    with what the process keeps alive, dishka included; who builds the pooled shells does not change the loop,
    so prewarming (already dropped) would not have bought anything either. No clean Melder lever here.
  NEXT: Check which functions of a warm scope cycle miss 3.14t's automatic deferred refcounting.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-30T14:39:55Z
  TYPE: MEASURE
  CLAIM: The per-spell creation-context doors are the only hot functions left without deferred refcounting.
    sys.setprofile over 150 warm scope cycles (Melder lane, harness code excluded): 39.7 Python-level calls per
    cycle; every method (Conduit, SpellSpace, pools, ward, Creations) and every site-plan executor and _miss
    function is a top-level function and already deferred. 6.7 calls per cycle go to
    `_creation_context_execute_no_overrides_only` closures (spellspace route 3.32, unique_per_conduit 3.00, many
    0.34), none deferred, each with cells. They are nested by construction: a template function takes the spell's
    values and returns the nested door, so every call pays atomic refcounts on a shared function object and its
    cells.
  EVIDENCE:
  - context_compass/artifacts/melder_gauntlet_gap_20260930/runs/hot_function_census_50cycles.txt:1-46
  - context_compass/artifacts/melder_gauntlet_gap_20260930/probes/hot_function_census.py:57-111
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:56-99
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:358-391
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:416-438
  IMPACT: This is the one clean piece of the dropped P3 idea left: emitting the doors as top-level functions
    lets CPython defer them itself (no ctypes, no unstable API). melder_2's P3 split (2026-09-26) put functions
    plus cells at 3-9 points of the worker-thread cycle when the executors were closures too; the executors are
    top-level now, so the door share is smaller. UNKNOWN until prototyped; it touches only the in-cycle part.
  NEXT: File the ranked lever list for the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-30T14:39:55Z
  TYPE: DECISION_REQUEST
  CLAIM: Where Melder can still gain on the shared gauntlet, ranked. Known: no regression since 0.2.74; GC is
    about 0.2% of the loop; inside the scopes Melder matches or beats dishka on two of three lanes; about 80% of
    the Windows gap (0.12 of 0.154 ms per iteration) sits outside the timed cycles, in thread start/exit costs
    that grow with any workload under free-threading and have no Melder cause found. Options:
    (A) Prototype top-level door functions in a VM copy (no tree edit): per-cycle A/B, then a Windows run decides;
        expected a few percent of the scope cycle, i.e. about 1-2% of the iteration at best (UNKNOWN).
    (B) Thread-affine shell pools (melder_2, 2026-09-26): -6 to -7% per cycle on Linux, Windows UNKNOWN, changes
        pool semantics and needs patch docs.
    (C) Stop here: the loop is tight; record the findings and close (recommended).
    (D) Benchmark only, opt-in: a thread-reuse layout of the gauntlet so it can report DI work without thread
        churn; the default layout stays.
    Not options: prewarming (dropped, and measured no gain), GC tuning (nothing to gain), P3 via ctypes (dropped).
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-09-30_map_remaining_melder_gauntlet_gains_task.md:187-237
  - context_compass/tickets/tasks/completed/2026-09-30_map_remaining_melder_gauntlet_gains_task.md:238-308
  - context_compass/artifacts/melder_gauntlet_gap_20260930/owner_run_30k_isolated_20260930.md:1-28
  - context_compass/tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md:631-652
  IMPACT: Each of A, B and D is its own task with a NOTICE to the file owner; C closes this lane. Nothing is edited
    until the owner picks.
  NEXT: Owner picks A, B, C or D.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-30T14:51:27Z
  TYPE: DECISION
  CLAIM: Owner picked option A (chat, 2026-09-30, after the 14:40Z DECISION_REQUEST): "yeah prototype that change
    go ahead and lets see what it does". The prototype stays in this ticket because it is VM-only work inside the
    EXECUTION_BOUNDARY (runs in VM trees, code under artifacts/, no tree edit). This corrects the request's
    IMPACT line, which said every option would open its own task: only landing the change in src/ does (a
    NOTICE to the file owner, patch docs, tests, a notch).
  EVIDENCE: context_compass/tickets/tasks/completed/2026-09-30_map_remaining_melder_gauntlet_gains_task.md:358-381
  IMPACT: Status returns to in_progress for the prototype; nothing in src/ changes.
  NEXT: Write the prototype PLAN, then build it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-30T14:51:27Z
  TYPE: PLAN
  CLAIM: Prototype A as a runtime overlay, tree untouched. (1) door_proto.py (artifacts/.../prototype/) rebuilds
    the four door-template families of creation_runtime_door_compiler from the module's own route bodies
    (_build_no_overrides_lines, _build_with_overrides_lines), emitted as a top-level `def` with no template
    wrapper and compiled once per route. Per spell it builds FunctionType(code.replace(), a globals dict of that
    spell's bindings, name): no cells, no CO_NESTED (so 3.14t defers the function), and one code copy per spell
    so each LOAD_GLOBAL specializes to its own dict. On 3.14t a slot load of a deferred function pushes a borrowed
    stackref (include/internal/pycore_stackref.h:369-380 of the installed CPython), so a door read from
    CreationContext._no_overrides_instance_executor and called costs no refcount at all. install() swaps the
    entries of the four template dicts before any Spellbook is built; the three hydrators reach the templates
    only through the module's compile functions, which read those dicts per call. (2) Checks: the hot-function
    census under the overlay (expect 0 non-deferred door calls); the door-related unit, component and
    integration tests under the overlay through a pytest plugin. (3) Measure: interleaved A/B in fresh
    processes (harness Melder lane, 3000 iterations, at least four rounds): iteration and threaded totals,
    per-lane outer_total and active cycles/s. (4) Hand the same A/B driver to the owner for a Windows run.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:358-438
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:498-896
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:1160-1227
  - src/melder/aether/conduit/spell_space/spell_space.py:577-685
  IMPACT: Sizes the last clean in-cycle lever with no change to the tree; if it pays, the same code shape moves
    into the compiler in its own task.
  NEXT: Write door_proto.py and check that the doors it builds are deferred and not nested.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-30T14:53:51Z
  TYPE: MEASURE
  CLAIM: The overlay builds the hot doors as deferred top-level functions with no cells. door_proto.py
    (TopLevelDoorTemplate, build_templates, install) swaps the four template dicts; on the harness Melder lane
    after 20 iterations, the 58 executors found in CreationContext slots go from 58 nested closures with cells
    and 0 deferred (tree) to 27 deferred top-level doors plus 31 nested ones (overlay). The 31 are the
    hydrators' lazy cold doors (build_lazy_creation_executors, build_solo_lazy_creation_executors,
    _build_lazy_overrides_door), which a first meld swaps out, and they are off the warm path. The hot-function
    census under the overlay: 39.7 Python-level calls per warm scope cycle as before, 0.0 to non-deferred functions
    (tree: 6.7).
  EVIDENCE:
  - context_compass/artifacts/melder_gauntlet_gap_20260930/prototype/door_proto.py:31-196
  - context_compass/artifacts/melder_gauntlet_gap_20260930/runs/door_proto_check.txt:1-4
  - context_compass/artifacts/melder_gauntlet_gap_20260930/runs/hot_function_census_proto_50cycles.txt:1-46
  IMPACT: The overlay reaches exactly the calls the lever targets and nothing else, so an A/B isolates it.
  NEXT: Run the door-related tests under the overlay.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-30T15:02:56Z
  TYPE: MEASURE
  CLAIM: The suites pass under the overlay except two introspection asserts. VM mirror, 3.14.7t -X gil=0, overlay
    installed at pytest_configure: tests/unit 8716 passed, 3 skipped, 7 xfailed; tests/integration 2001 passed, 2
    skipped, 4 xfailed, 2 xpassed (the two known XPASS); tests/component 2252 passed, 23 skipped, 1 xfailed and 2
    failed (2254 passed without the overlay). Both failures are the singleton-specialization tests' helper
    _door_binds_executor_named, which finds the inner executor through a door's defaults, kwdefaults and closure
    cells; the overlay keeps it in the door's globals. With the helper also reading
    __globals__["_no_overrides_executor"] (temporary patch in the VM mirror, restored identical to the device copy)
    all 7 tests of that file pass under the overlay; they pass without it too.
  EVIDENCE:
  - context_compass/artifacts/melder_gauntlet_gap_20260930/prototype/logs/overlay_unit.log:124-125
  - context_compass/artifacts/melder_gauntlet_gap_20260930/prototype/logs/overlay_component.log:80-87
  - context_compass/artifacts/melder_gauntlet_gap_20260930/prototype/logs/overlay_integration.log:29-30
  - context_compass/artifacts/melder_gauntlet_gap_20260930/prototype/logs/overlay_specialization_globals_helper.log:1-3
  - context_compass/artifacts/melder_gauntlet_gap_20260930/prototype/patch_spec_test_helper.py:17-35
  - tests/component/melder/aether/conduit/test_conduit_component_singleton_specialization.py:128-155
  IMPACT: No behaviour change shows up across 12,971 tests; landing the change would also update that one test
    helper. The prototype is fit to measure.
  NEXT: Write the interleaved A/B driver and run it in the VM.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-30T15:05:01Z
  TYPE: MEASURE
  CLAIM: On the VM gauntlet the overlay does not measurably change Melder. door_proto_ab.py, four shuffled rounds,
    3000 iterations, fresh -X gil=0 process per run: totals base 5607.8 / 5665.9 / 5844.7 / 5743.4 ms, proto
    5556.7 / 5864.7 / 5922.5 / 6128.5 ms (medians 5704.6 vs 5893.6, ratio 1.033, within the run-to-run spread;
    the host drifted slower over the four rounds, and the whole VM ran about 25% slower than at 14:10Z). In-cycle
    medians proto/base: outer_total request 0.990, worker_a 1.005, worker_b 1.005; active cycles/s 0.995, 1.011,
    1.036. The expected saving is about 20 uncontended atomic pairs per scope cycle (function plus two cells on
    6.7 door calls), well under the noise of a 2-vCPU VM.
  EVIDENCE:
  - context_compass/artifacts/melder_gauntlet_gap_20260930/prototype/logs/door_proto_ab_vm_r1-4_3000it.jsonl:1-8
  - context_compass/artifacts/melder_gauntlet_gap_20260930/prototype/door_proto_ab.py:31-80
  IMPACT: The VM gauntlet cannot resolve a lever this size; a per-cycle CPU A/B on worker threads is the only VM
    measurement that can, and the owner's Windows run decides.
  NEXT: Per-cycle CPU A/B (thread_time on fresh worker threads, one lane per thread and three lanes at once).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-30T15:08:06Z
  TYPE: MEASURE
  CLAIM: Per scope cycle the overlay saves about 2% of worker-thread CPU in the VM. door_proto_cycles.py, 32
    paired rounds (base and proto back to back in fresh -X gil=0 processes, order shuffled), 3000 warm cycles per
    lane on fresh threads after the harness's own warm-up. Median proto/base CPU ratio: solo request 0.972,
    worker_a 0.930, worker_b 0.986; three lanes at once 1.001, 0.992, 0.963. Over all 192 comparisons: median
    0.977, mean 0.979, proto faster in 122. The per-round spread is wide (quartiles about 6-12% either side), and a
    cycle costs about 10.4-15.4 us. In gauntlet terms that is about 2% of the longest lane's roughly 0.39 ms of
    cycles, some 8 us of a 1.2-1.5 ms iteration: about 0.5-1% of the total, which the VM gauntlet A/B could not
    resolve.
  EVIDENCE:
  - context_compass/artifacts/melder_gauntlet_gap_20260930/prototype/logs/door_proto_cycles_vm_32rounds_paired.txt:1-16
  - context_compass/artifacts/melder_gauntlet_gap_20260930/prototype/logs/door_proto_cycles_vm_32rounds.jsonl:1-64
  - context_compass/artifacts/melder_gauntlet_gap_20260930/prototype/door_proto_cycles.py:34-105
  IMPACT: The lever is real and small, as sized in the DECISION_REQUEST. Whether to land it turns on the Windows
    run, where the threads run on separate cores and atomics cost more.
  NEXT: Hand the owner the two Windows commands (per-cycle and gauntlet A/B); land only on the owner's word, in its
    own task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-30T15:11:30Z
  TYPE: RISK
  CLAIM: The owner reports about ten agents working in the background on the machine (chat, 2026-09-30, after
    the option-A handoff). The device VM runs on that machine, so every VM number today was taken under that load;
    it fits the VM running about 25% slower during the overlay A/B than at 14:10Z. Paired and interleaved ratios
    (door_proto_cycles, door_proto_ab, version and tree A/Bs) stay usable because both sides of each pair saw the
    same load, but bursts can swamp a 2% effect, and absolute levels are not comparable across the session.
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-09-30_map_remaining_melder_gauntlet_gains_task.md:460-476
  - context_compass/artifacts/melder_gauntlet_gap_20260930/prototype/logs/door_proto_cycles_vm_32rounds_paired.txt:1-16
  IMPACT: The Windows A/B should run with the agents idle; if it runs under load, use more rounds (32 for
    door_proto_cycles.py) and read the paired ratios (door_proto_cycles_paired.py, wall_ns on Windows).
  NEXT: Owner runs the Windows A/B when the machine is quiet; melder_0 can repeat the VM per-cycle A/B then too.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-30T15:14:16Z
  TYPE: MEASURE
  CLAIM: On the owner's Windows machine option A is a loss: every scope cycle got slower. Owner's run of
    door_proto_cycles.py (free-threaded CPython 3.14 from uv, .venv_new; 16 paired rounds, 30,000 cycles per
    lane; about ten agents working in the background): median proto/base wall ratio solo request 1.090,
    worker_a 1.112, worker_b 1.123; three lanes at once 1.074, 1.047, 1.054; proto faster in 11 of 96 wall
    comparisons and 3 of 96 CPU comparisons (CPU median 1.108). In the VM the same overlay measured about 0.98. The
    owner's second command (door_proto_ab.py) did not run: the pasted line began with the prompt text.
  EVIDENCE:
  - context_compass/artifacts/melder_gauntlet_gap_20260930/prototype/logs/door_proto_cycles_win.jsonl:1-32
  - context_compass/artifacts/melder_gauntlet_gap_20260930/prototype/logs/door_proto_cycles_win_paired.txt:1-16
  IMPACT: Option A as built costs about 1-2 us per scope cycle on Windows, far more than the refcounts it saves;
    it must not land in this shape.
  NEXT: Find why (suspect: each door's own code copy gives every door its own function version, so the shared
    call sites in SpellSpace.meld and Conduit.meld stop specializing).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-30T15:15:25Z
  TYPE: FACT
  CLAIM: Why option A loses: the door's own code copy breaks the caller's call specialization. After warm cycles
    (VM, 3.14.7t), the door call in SpellSpace.meld's warm lane (`instance = fast_executor(meld_door)`) is
    specialized to CALL_PY_EXACT_ARGS on the tree and falls back to the generic CALL under the overlay. The overlay
    gives each spell's door its own code object so that its LOAD_GLOBALs specialize (they do: LOAD_GLOBAL_MODULE),
    but a function's version comes from its code, so one call site now sees a different version for every spell
    and cannot stay specialized. The closures share one code object per route, which keeps the caller specialized
    and gives each spell its values through cells. The two alternatives fail the same trade: one shared code object
    with per-spell globals would thrash LOAD_GLOBAL's keys-version guard inside the door, and per-spell defaults
    rule out CALL_PY_EXACT_ARGS (the call no longer passes every positional argument). The generic call cost more
    on the owner's Windows build than the three atomic refcount pairs per door call it saved; on the Linux VM the
    two roughly cancelled.
  EVIDENCE:
  - context_compass/artifacts/melder_gauntlet_gap_20260930/prototype/logs/door_proto_specialization_vm.txt:1-14
  - context_compass/artifacts/melder_gauntlet_gap_20260930/prototype/door_proto_specialization.py:24-92
  - src/melder/aether/conduit/spell_space/spell_space.py:662-685
  - context_compass/artifacts/melder_gauntlet_gap_20260930/prototype/door_proto.py:61-74
  IMPACT: The closure is already the best shape for these doors; option A has no clean variant that keeps both
    specializations, so it is dropped unless the owner says otherwise. This closes the last in-cycle lever.
  NEXT: Recommend closing the lane (option C); keep the prototype and its logs as reference.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-30T15:27:09Z
  TYPE: DECISION
  CLAIM: The owner dropped option A and closed the lane (chat, 2026-09-30, answering "Want me to close this ticket
    out?"): "ok yeah lets drop the change, go ahead and drop it and lets move on". There is nothing to revert:
    the overlay only ever ran in VM trees and lives under artifacts/.../prototype/. The prototype, its A/B
    drivers and every log stay as reference, with the specialization finding that rules the top-level door
    shape out; the prototype/__pycache__ left by the owner's Windows run is git-ignored and stays.
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-09-30_map_remaining_melder_gauntlet_gains_task.md:512-551
  - .gitignore:2-2
  IMPACT: Option C is in effect: no src change, no release-note entry, no rebuild. The remaining Windows gap
    stays where these notes put it (thread start/exit under free-threading, outside the timed cycles), with no
    open Melder lever left in this lane.
  NEXT: Turn in: completion summary, move to tickets/tasks/completed/, attention and artifact board sync.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Closed 2026-09-30T15:27:09Z on the owner's turn-in: option A dropped, lane closed (option C in effect). No
regression across the Melder releases compared; GC is about 0.2% of the loop; about 80% of the Windows gap
sits in thread start/exit costs outside the timed cycles, with no single Melder cause. Option A (top-level
doors, a VM-only overlay under artifacts/.../prototype/) saved about 2% CPU per scope cycle in the VM and cost
8-11% per cycle on the owner's Windows machine, because a per-spell code copy costs the caller
(SpellSpace.meld) its CALL_PY_EXACT_ARGS specialization; the closure shape stays. No tree edit. Artifacts
retained as reference.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
