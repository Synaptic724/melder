

# Task: Reproduce the real-world gauntlet and attribute Melder's per-scope-cycle cost

## Metadata
- Task ID: TASK-2026-09-26-measure-gauntlet-scope-cycle-costs
- Story: STORY-2026-09-26-gauntlet-runtime-speed
- Status: in_progress
- Owner: user
- Agent Name: melder_2
- Priority: p1
- Created: 2026-09-26T15:43:24Z
- Updated: 2026-09-26T17:36:01Z

## Objective
A per-scope-cycle cost map for Melder on the real-world gauntlet - where the time and the calls go in outer and
request scope create, warm melds and cleanup, set against dishka and dependency-injector in the same run - and a
ranked candidate list (expected gain, risk, files, owning lane). No production or benchmark code changes.

## Ticket Contract
- ENTRY_GATE: board row routes here; owner decisions D1 (lane split with melder_0), D2 (measurement environment)
  and D3 (setup in or out) recorded as DECISION notes.
- EXECUTION_BOUNDARY: read-only on src/ and benchmarks/ in the device tree. Runs happen on a VM copy under the
  session scratch (outside the connected folder), so no cache or result files land in the owner's tree. Outputs go
  to artifacts/gauntlet_runtime_speed_20260926/. Ticket, board and artifact files are the only writes.
- DEPENDENCIES: melder_0 owns the warm meld call (tickets/tasks/2026-09-26_build_site_plan_lowering_task.md);
  fable_0's 2026-09-25 per-cycle counts on the IR epic are prior evidence; owner-run confirmation for any number
  that is claimed as a gain.
- EXIT_GATE: cost map and ranked candidates filed (artifact plus Notes); DECISION_REQUEST to the owner; follow-up
  tasks open only on the owner's pick.
- FAILURE_ESCALATION: BLOCKER if CPython 3.14t or the competitor packages cannot be installed in the VM; CONFLICT
  if a top candidate sits in another agent's files; DECISION_REQUEST for candidate selection and the target.

## Scope Boundaries
- In scope: the gauntlet harness's Melder lane and the runtime code it drives (reading, running, profiling).
- Out of scope: edits to src/ or benchmarks/; the override benchmark and the meld-call trims (melder_0);
  import/boot setup unless D3 brings it in.

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: Owner answered D1-D3 (2026-09-26T15:45:57Z); measurement starts on the VM copy.

## Steps / Checklist
- [x] Record the owner's 2026-09-26 runs (5,000 and 30,000 iterations) verbatim as the baseline artifact.
- [ ] Build the VM copy: CPython 3.14t via uv, Melder's runtime dependencies, dishka, dependency-injector and
      pytest; copy src/, benchmarks/ and pyproject.toml; smoke-run the gauntlet at reduced iterations.
- [ ] Read the gauntlet harness (the Melder lane and the shared driver) in full; record what each reported metric
      measures (wall versus active cycles, the scope create and cleanup windows).
- [ ] Run the gauntlet on the VM copy (threads 1, 2 and 3, repeated) and compare same-run ratios with the owner's.
- [ ] Attribute the Melder scope cycle: call counts and time per sub-step, single-threaded first; run the existing
      probes (profile_scope_cycle_contention.py, test_melder_gauntlet_gc_probe.py) once each.
- [ ] Read the attributed runtime code in full (pooled lesser and SpellSpace acquire and return, creations
      disposal, ID minting, per-cycle locks); record the per-cycle cost map.
- [ ] Rank candidates with expected gain, risk, files and owning lane; DECISION_REQUEST to the owner.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- artifacts/gauntlet_runtime_speed_20260926/owner_run_20260926.txt (owner baseline, verbatim)
- artifacts/gauntlet_runtime_speed_20260926/vm_environment.txt
- VM run outputs and profiles, and cost_map.md with the ranked candidates

## Files / Paths Impacted
- context_compass/tickets/ (this task and its story), attention_board.md, artifact_board.md, mailbox_board.md
- context_compass/artifacts/gauntlet_runtime_speed_20260926/
- No src/ or benchmarks/ files.

## Validation
- Not run.
- Recommended commands:
  - UNKNOWN until the harness is read (the owner's exact command is not in the paste).

## Risks / Rollback Notes
- The VM and the cloud workspace have 2 vCPUs: three worker threads are oversubscribed, so thread scaling and
  cross-thread refcount costs are not reproduced; VM numbers are relative only, and melder_0 has already seen the
  owner machine show a larger Melder gap than the VM.
- cProfile on 3.14t interleaves cumtime across threads (IR epic, 2026-09-25); attribution uses call counts and
  single-threaded timing.
- No rollback needed: no tree edits.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No gain claimed from a VM number alone; the owner-run number decides.
- [ ] No cumtime from a threaded cProfile used as evidence.

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
  - artifacts/gauntlet_runtime_speed_20260926/owner_run_20260926.txt
  - artifacts/gauntlet_runtime_speed_20260926/vm_environment.txt
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
- DATETIME: 2026-09-26T15:43:24Z
  TYPE: MEASURE
  CLAIM: Owner-run gauntlet 2026-09-26 (gil=disabled, 3 threads, 5 singletons), all three libraries in one run.
    30,000 iterations: hot_scopes/s melder 38,175 vs dishka 48,979 (0.78x) vs dependency-injector 39,130 (0.98x);
    total 51.08 s vs 39.81 s vs 49.83 s; setup 187.5 ms vs 42.1 ms vs 45.4 ms; end cleanup 18.7 ms vs 6.0 vs 6.5;
    active cycles/s melder/dishka 0.55 (request lane), 0.63 (worker_a), 0.77 (worker_b), while melder is ~1.6-1.7x
    dependency-injector on the same active metric and below it on wall cycles/s. 5,000 iterations: hot_scopes/s
    0.67x dishka and 0.77x dependency-injector; melder's worst iteration 192.6 ms and worst outer-scope create
    63.1 ms. What wall versus active measure is UNKNOWN until the harness is read. Interpreter build, commit,
    machine and creation-cache state are UNKNOWN.
  EVIDENCE:
  - artifacts/gauntlet_runtime_speed_20260926/owner_run_20260926.txt:51-92
  - artifacts/gauntlet_runtime_speed_20260926/owner_run_20260926.txt:36-46
  IMPACT: The gap is per scope cycle: melder completes a cycle at 55-77% of dishka's active rate. Setup is 4.5x
    and is a separate question (D3).
  NEXT: Owner answers D1-D3; then build the VM copy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T15:43:24Z
  TYPE: FACT
  CLAIM: Absolute numbers do not carry across days on the owner machine: between the 2026-09-25 and 2026-09-26
    owner runs (both 5,000 iterations, gil=disabled, 3 threads) hot_scopes/s moved 1.28x for dependency-injector
    (35,491 -> 45,284), 1.79x for dishka (28,797 -> 51,514) and 1.49x for melder (23,382 -> 34,745). Only ratios
    within one run are comparable.
  EVIDENCE:
  - artifacts/ir_epic_gauntlet_baseline_20260925/owner_run_20260925.txt:18-46
  - artifacts/gauntlet_runtime_speed_20260926/owner_run_20260926.txt:18-46
  IMPACT: Every before/after comparison runs the competitors in the same invocation and reports ratios.
  NEXT: Put same-run ratios in the measurement protocol.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T15:43:24Z
  TYPE: FACT
  CLAIM: No 3.14t interpreter exists in this session yet: the device VM has Python 3.10.12, uv and PyPI access, 2
    vCPUs and 3.9 GB; the cloud workspace has 2 vCPUs as well. The gauntlet's three worker threads would be
    oversubscribed in either.
  EVIDENCE: artifacts/gauntlet_runtime_speed_20260926/vm_environment.txt:1-14
  IMPACT: 3.14t must be installed with uv; VM runs are good for call counts, single-thread attribution and A/B
    ratios, not for thread scaling.
  NEXT: Install CPython 3.14t with uv once D2 is answered.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T15:43:24Z
  TYPE: FACT
  CLAIM: melder_0 is working the warm meld call right now: the Conduit.meld arm and override fast door are
    trimmed, and its next lever is fewer shared-object touches per warm meld because on 3.14t a worker-thread meld
    pays atomic refcounts on main-thread-owned objects (solo 402 vs 188 ns, GIL no difference). The gauntlet runs
    its hot path on worker threads, so that cost is inside the gauntlet's per-cycle number. On the owner machine the
    Melder per-step gap is larger than on melder_0's VM (1.37 vs 0.35 us, VM 0.59 vs 0.29).
  EVIDENCE:
  - tickets/tasks/2026-09-26_build_site_plan_lowering_task.md:984-1011
  - tickets/tasks/2026-09-26_build_site_plan_lowering_task.md:1027-1049
  - attention_board.md:88-88
  IMPACT: The meld call is melder_0's lane; this lane's natural share is the rest of the scope cycle, and VM
    numbers will understate the owner's gap (D1, D2).
  NEXT: Owner decides the split (D1).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T15:43:24Z
  TYPE: FACT
  CLAIM: Prior attribution exists: fable_0's 2026-09-25 cProfile gauntlet (GIL, 25 iterations) counted per scope
    cycle ~16 RLock pairs, 42 dict.get, 29 isinstance and 16.6 ULID-genexpr iterations around ~6 us compiled
    creation bodies, and proposed a scope-cycle "door diet" (lock consolidation, lazy IDs for pooled lessers,
    meld-door check removal); the owner deferred it ("just not yet") because another agent owned hot-path work.
    The counts predate today's fast door and trims.
  EVIDENCE:
  - tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md:594-624
  - tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md:825-865
  IMPACT: Starting hypotheses for the attribution, not facts about today's tree; they are re-measured before use.
  NEXT: Re-count per cycle on the VM copy after D1-D3.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T15:43:24Z
  TYPE: RISK
  CLAIM: Running the benchmarks from the device tree writes creation-cache files into the owner's src/melder
    (melder_0 saw a .melc written by an owner run), and cache state changes what conjure does: a full hit skips
    phases 8-11. A Linux 3.14t run on the shared tree could also leave caches that an owner Windows run then reads.
  EVIDENCE:
  - tickets/tasks/2026-09-26_build_site_plan_lowering_task.md:1013-1025
  - system_docs/src_architecture.md:649-676
  IMPACT: All melder_2 runs use a VM copy; each run records whether the creation cache was cold or warm.
  NEXT: Build the copy under the session scratch, outside the connected folder.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T15:43:24Z
  TYPE: DECISION_REQUEST
  CLAIM: Three owner decisions before measurement starts. D1 lane split - recommended: melder_2 takes the rest of
    the scope cycle (pooled lesser and SpellSpace acquire/return, creations disposal on return, ID minting,
    per-cycle locks) plus the gauntlet measurement, and hands meld-call findings to melder_0, who keeps
    Conduit.meld, the ConduitMeld/SpellSpaceMeld doors, meld.py and override plans. D2 environment - recommended:
    a VM copy with CPython 3.14t for attribution and A/B (relative numbers only), owner-run on Windows for every
    number claimed as a gain. D3 setup (187.5 ms vs 42.1 ms) - parked since 2026-09-25; recommended: stays parked.
  EVIDENCE:
  - tickets/tasks/2026-09-26_build_site_plan_lowering_task.md:984-1011
  - tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md:825-865
  - artifacts/gauntlet_runtime_speed_20260926/vm_environment.txt:1-14
  IMPACT: D1 decides which files melder_2 may later change, D2 whose numbers count, D3 whether import/boot enters
    the story.
  NEXT: Ask the owner; record each answer as a DECISION note.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T15:45:57Z
  TYPE: DECISION
  CLAIM: Owner answers (2026-09-26). D1: "focus on the meld and spellspace hotpath and maybe resolution hotpath,
    I feel like its pretty tight right now but if you got any ideas go ahead and ... send it" - melder_2 owns the
    warm meld and SpellSpace path (and the resolution path if the profile points there). That overlaps melder_0's
    lane, so ownership is settled per file by mailbox notice before any tree edit (M2-4). D2: VM copy with CPython
    3.14t for attribution and A/B; the owner runs Windows for any number claimed as a gain. D3: setup stays parked.
  EVIDENCE: tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md:217-233
  IMPACT: Measurement starts now on the VM copy. Ideas are prototyped on the copy and come back with files and
    measured deltas; tree edits follow the patch gate and the one-writer rule.
  NEXT: Install CPython 3.14t, build the VM copy, smoke-run the gauntlet.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T15:48:42Z
  TYPE: FACT
  CLAIM: Harness semantics (Melder lane, driver and summaries read in full). One scope cycle: create_lesser_conduit,
    two lesser melds of the outer type (unique_per_conduit), enter_spellspace, three space melds (marker twice,
    inherited outer once), one or two root/group melds (a request root builds 63 objects, worker_a 25, worker_b 20),
    spellspace exit, lesser.cleanup. "active cycles/s" divides cycles by the summed request_total (spellspace
    enter to exit only); "wall cycles/s" by the summed threaded-phase wall; hot_scopes/s by the summed iteration
    totals, bootstrap included. The runner runs DI, dishka and melder in turn in one `-X gil=0` process, GC normal.
  EVIDENCE:
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:966-1185
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1244-1345
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1376-1405
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1760-1830
  - benchmarks/testing_other_di/real_world_gauntlet_gil_runner.py:1-38
  IMPACT: Melder's 0.55-0.77x "active" gap sits inside the SpellSpace window (enter/exit, the space melds and the
    root construction); lesser create/cleanup and the lesser melds show only in outer_total, wall and hot_scopes/s.
  NEXT: Smoke-run the runner on the VM copy (CPython 3.14.7t, cold cache) at reduced iterations.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T15:50:52Z
  TYPE: MEASURE
  CLAIM: VM copy (CPython 3.14.7t, -X gil=0, cold cache). Gauntlet smoke run, 300 iterations, 3 threads:
    hot_scopes/s melder 32,796 vs dishka 42,414 (0.77x) vs dependency-injector 36,787 (0.89x), close to the
    owner's 30,000-iteration ratios (0.78x, 0.98x). One worker thread, full scope cycle through the harness's own
    lane callables: request 15.0 us vs dishka 9.7 (1.55x), worker_a 10.2 vs 7.0 (1.47x), worker_b 10.2 vs 7.3
    (1.40x). Request-cycle steps (medians): lesser create 0.84 us, first lesser meld (session plus a 5-object
    chain) 1.78, cached lesser meld 0.32, space enter 0.24, FIRST space meld of the marker (one object, one
    inherited dependency) 1.77, cached space melds 0.34 each, root meld 5.08 (63+ objects, ~80 ns/object),
    space exit 0.88, lesser cleanup 0.96. cProfile: 227 Python calls per request cycle (dishka 234).
  EVIDENCE:
  - artifacts/gauntlet_runtime_speed_20260926/vm_runs/smoke_300_iters_3_threads.txt:1-60
  - artifacts/gauntlet_runtime_speed_20260926/vm_runs/per_cycle_baseline.txt:1-33
  - artifacts/gauntlet_runtime_speed_20260926/probes/probe_steps.py:1-50
  IMPACT: Bulk construction is already cheap (~80 ns/object). The gap is fixed cost: a first build in a fresh
    scope costs ~1.4 us beyond a cache hit even for one object, cached melds ~0.33 us each (4-5 per cycle), and
    the scope lifecycle ~2.9 us per cycle. Those three are the targets.
  NEXT: Read the first-build path of a unique_per_spell_space meld (SpellSpace.meld -> SpellSpaceMeld.meld ->
    creation-context template -> Creations slot guard and publication) in full.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T15:56:49Z
  TYPE: MEASURE
  CLAIM: Generated plans build every dependent object with KEYWORD arguments (`target_N(prior=..., branch=...)`),
    and on 3.14t a keyword class call costs 170 ns vs 77 ns positional (Layer2Scope, worker thread): only the
    positional form gets the interpreter's specialized class-call path. Prototype P1 (VM copy only) emits the
    signature-order prefix of dependency params positionally (Python classes; remaining params stay keyword).
    A/B, 3 interleaved rounds x 7 x 3,000 cycles, one worker thread, median of medians: request 15.04 -> 11.60 us
    (-23%), worker_a 10.28 -> 8.79 (-15%), worker_b 10.00 -> 8.65 (-14%); dishka is 9.67 / 6.99 / 7.29, so the
    gap drops from 1.55x/1.47x/1.37x to 1.20x/1.26x/1.19x. Harness type and caching assertions pass.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:561-661
  - artifacts/gauntlet_runtime_speed_20260926/vm_runs/ab_p1_positional_cycle.txt:1-18
  - artifacts/gauntlet_runtime_speed_20260926/prototypes/p1_positional_constructor_args.diff:1-73
  - artifacts/gauntlet_runtime_speed_20260926/probes/micro_kw.py:1-35
  IMPACT: Largest single lever found so far, mechanical and contract-preserving if positional use is limited to
    params the target provably takes positionally in that order. The emitter is phase-11 code in melder_0's area.
  NEXT: Full gauntlet A/B (3 threads) on the VM; then the safety rule for positional emission.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-26T16:24:09Z
  TYPE: MEASURE
  CLAIM: With P1 in place the request cycle's step medians sum to ~9.6 us (from 12.5): root meld 3.26 us (34%),
    first marker build 1.31 (still rebuilding the session's 5-object chain it never uses), first session build
    1.24, three cached melds ~1.0 together, and the scope lifecycle - lesser create 0.80, space exit 0.84, lesser
    cleanup 0.94, space enter 0.24 - ~2.8 us (29%). Lifecycle alone (no melds) costs 1.88 us per cycle on a worker
    thread with 42 Python calls and 5 RLock enter/exit pairs; worker_b spends 31% of its cycle there.
  EVIDENCE:
  - artifacts/gauntlet_runtime_speed_20260926/vm_runs/post_p1_breakdown.txt:1-60
  - artifacts/gauntlet_runtime_speed_20260926/probes/probe_lifecycle.py:1-55
  IMPACT: Next levers in order of size: the scope lifecycle (~2.8 us), the dominated-chain rebuild (~1 us on
    the request lane), and the per-call cost of cached space melds.
  NEXT: Read the lifecycle path in full: Conduit.create_lesser_conduit/_link_new_lesser_under_lock/cleanup/
    _prepare_for_pool, ConduitWard link/detach, ConduitPool, SpellSpace enter/exit and its pool and thread state.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T16:29:58Z
  TYPE: FACT
  CLAIM: Consumed M0-31 and M0-34 from melder_0. At 16:17Z melder_0 applied the existing-object fast path to
    conduit.py (Conduit.meld), meld/conduit_meld.py, meld/spellspace_meld.py, meld/meld.py and the fast-door
    component test; fast-door entries are now 4-tuples (spell, context, epoch, existing_object_entry), so the VM
    copy is stale for those files. melder_0 is done with them for now (next: S2b in site_plan_lowering.py,
    site_plan_override_runtime.py and the family hydrators) and asks for a NOTICE before any edit to them; it will
    NOTICE before touching them again. Version is now 0.2.59, so the first conjure after it rebuilds the creation
    cache once (release-bound admission): gauntlet runs must be cold/warm labelled.
  EVIDENCE:
  - tickets/tasks/2026-09-26_build_site_plan_lowering_task.md:1257-1284
  - tickets/tasks/2026-09-26_build_site_plan_lowering_task.md:1313-1335
  IMPACT: Refresh the VM copy from the device tree before reading or prototyping the meld and lifecycle paths;
    any trim in conduit.py, meld.py, conduit_meld.py or spellspace_meld.py needs a mailbox NOTICE first.
  NEXT: Refresh the VM copy (src/ and benchmarks/ from the device tree), then read the scope-lifecycle path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T16:33:35Z
  TYPE: FACT
  CLAIM: Scope-lifecycle path read in full on the refreshed copy (conduit.py identical to the device tree). One
    anonymous cycle is 23 Python functions and 19 C calls. Its 5 RLock pairs: root Conduit._lock
    (_link_new_lesser_under_lock) and root ConduitWard._lock (_link_lesser_conduit), both shared by every gauntlet
    thread on every cycle; then the lesser's own Conduit._lock (cleanup), its Creations._lock (reset_for_pool) and
    its ward lock (_detach_for_pool), which are thread-confined. Every cycle also writes the root ward's
    _lesser_conduits dict (insert at link, pop at detach, the pop under the CHILD ward lock) and the root pool
    deque, both shared across threads. Earlier trims are already in place: SpellSpace exit takes no lock
    (reset_for_pool_unlocked), drain() does not allocate, the hook and logger checks are single bools, and there is
    no per-cycle wrapper object. What remains removable without a contract change is call depth: about 8 thin
    helpers (acquire_untracked, push, pop_expected, recycle_from_managed_context, reset_for_pool_unlocked,
    _cleanup_spellspaces_for_pool, drain, return_lesser_conduit). Removing the root lock pair or the shared
    registry write would change the parent-cleanup ordering contract. How much of space-exit and lesser-cleanup
    time with melds is deallocation of the scope's objects when the stores clear is UNKNOWN.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:566-706
  - src/melder/aether/conduit/conduit.py:1201-1235
  - src/melder/aether/conduit/conduit.py:2539-2796
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:382-465
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1176-1219
  - src/melder/aether/conduit/conduit_pool.py:106-161
  - src/melder/aether/conduit/spell_space/spell_space.py:213-408
  - src/melder/aether/conduit/spell_space/spell_space_pool.py:185-288
  - src/melder/aether/conduit/spell_space/spell_space_thread_state.py:187-302
  - src/melder/aether/conduit/creations/creations.py:1009-1105
  IMPACT: Local call flattening can save roughly 0.2-0.4 us of the ~1.9 us lifecycle (an estimate, not yet
    measured). The cross-thread cost of the shared root lock, dict and deque cannot be measured on 2 vCPUs, and
    changing it needs patch docs. The meld path is the larger remaining target: 4-5 cached melds at ~0.32 us each.
  NEXT: Measure the deallocation share of space exit and lesser cleanup, then read the cached-meld path after
    melder_0's 16:17Z change (SpellSpace.meld -> SpellSpaceMeld fast door, Conduit.meld -> ConduitMeld).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T16:43:20Z
  TYPE: MEASURE
  CLAIM: Largest lever so far is cross-thread refcounting, not call count. On 3.14t, a worker-thread load of an
    object owned by a LIVE other thread costs ~9 ns extra (4 loads: 54.6 vs 19.7 ns). An object from an exited
    thread (19.7 ns) or with deferred refcounting (18.1 ns) costs nothing extra. Melder conjures on the main
    thread, so every warm meld and plan step touches main-owned kernel objects: Spells, contexts, the spellbook,
    root meld and store dicts, executor cells and tuples. A pooled shell built by live main costs +19-22% per cycle
    (a cached lesser meld +39-43%); shells built by exited threads cost nothing, and that is the gauntlet's steady
    state. Experiment only (probe_deferred.py, no src change): after warm-up, deferred refcounting via ctypes
    (PyUnstable_Object_EnableDeferredRefcount, CPython 3.14) on the melder-owned graph from the root conduit and
    spellbook, with user instances, types, modules and module globals skipped. Fresh worker threads, 3 x 3,000
    cycles x 3 rounds: request 15.8-16.1 -> 10.8 us (-32%), worker_a 11.8-11.9 -> 8.4 (-29%), worker_b 10.5-10.8
    -> 8.0 (-25%). Two concurrent threads: request 18.8 -> 12.8, worker_a 13.2 -> 9.9. By scope: kernel instances
    alone give -9 to -18%; adding dict/list/tuple/set gives -20 to -23%; adding functions and cells gives the full
    gain. The walk touches ~13k objects, defers ~7.2k, and takes ~18 ms. One 3-thread gauntlet pair on the VM
    (300 iterations, noisy): melder active cycles/s +22-31%.
  EVIDENCE:
  - context_compass/artifacts/gauntlet_runtime_speed_20260926/vm_runs/deferred_refcount_experiment.txt:1-24
  - context_compass/artifacts/gauntlet_runtime_speed_20260926/probes/probe_deferred.py:1-75
  - context_compass/artifacts/gauntlet_runtime_speed_20260926/probes/probe_owner.py:1-52
  - context_compass/artifacts/gauntlet_runtime_speed_20260926/probes/gauntlet_deferred.py:1-47
  IMPACT: This explains most of melder_0's worker-vs-main gap (402 vs 188 ns) and is worth roughly -25 to -32% of
    the scope cycle on worker threads, more than P1. It is also a design decision: ctypes into an unstable CPython
    3.14 API, memory for deferred objects reclaimed only by the GC, a no-op on GIL builds, and chokepoints in
    other lanes' files (conjure, hydration, pooled shells, fast-door entries).
  NEXT: Decision request to the owner: implement free-threaded deferred refcounting behind patch docs (chokepoints
    and files named), or not; meanwhile check the tests for weakref/refcount-release assertions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-26T16:47:32Z
  TYPE: MEASURE
  CLAIM: How much of the deferral gain reaches the gauntlet. (1) Scope, 8 interleaved processes per variant, fresh
    worker thread: kernel instances only -10 to -15%; plus functions, cells and tuples -9 to -20%; plus dicts,
    lists and sets that hold no user object at walk time ("userfree") -21 to -26%; everything -21 to -29%.
    "userfree" keeps nearly all of the gain without deferring containers that already hold user objects.
    (2) Exposure: in the real 3-thread gauntlet, the pooled lesser shell is owned (object-header ob_tid) by
    another thread in 63-71% of cycles, and so is its spellspace. New threads that reuse an exited thread's id
    inherit its objects, which is why exited-thread shells measured "free". (3) Real gauntlet with
    DI_GAUNTLET_THREADS=1 (the shell is effectively always owned, so only the main-owned kernel remains):
    userfree deferral, walked after setup and again after iteration 1, gives active cycles/s +4 to +10%
    (102-106k -> 109-112k). hot_scopes/s is dominated by per-iteration thread spawn and is within noise. The
    3-thread VM gauntlet stays too noisy to judge.
  EVIDENCE:
  - context_compass/artifacts/gauntlet_runtime_speed_20260926/vm_runs/deferred_scope_and_ownership.txt:1-55
  - context_compass/artifacts/gauntlet_runtime_speed_20260926/vm_runs/gauntlet_threads1_deferred_ab.txt:1-7
  - context_compass/artifacts/gauntlet_runtime_speed_20260926/probes/gauntlet_ownership.py:1-51
  IMPACT: Rough gauntlet estimate: about two thirds of cycles gain ~25% and the rest ~5%, so roughly -18% per
    3-thread cycle on the VM. The owner machine runs threads on separate cores, where contended atomics cost more,
    so the gain could be larger; only an owner run can say. The "userfree" rule is the shippable shape.
  NEXT: Check the suites for release-timing assumptions (weakref and getrefcount tests); then write the decision
    request with the chokepoint and file list.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T16:50:28Z
  TYPE: PLAN
  CLAIM: Next is a VM-copy prototype P3 (no tree edit) of deferred refcounting as a library feature, so the owner
    decides from validated numbers and a suite run. Facts on 3.14.7t: module-level functions and classes are
    already deferred; closures built at runtime (every hydrated executor and step function) and all instances
    and dicts are not. sys.intern makes a str immortal in place, which adds ~3-5% on top. Shape:
    (a) new utility melder/utilities/helpers/refcount_deferral.py (RefcountDeferral), free-threaded CPython
    only, resolved once as a class attribute and a no-op elsewhere. defer_graph(*roots) is a breadth-first walk
    with one gc.get_referents call per level, using the "userfree" rule: melder instances, functions, methods and
    cells, plus containers that hold no user object. It never enters modules, code objects, module globals, types
    or user instances, and descends only through roots and newly deferred objects. (b) Chokepoints: end of
    Spellbook conjure and _conjure_existing_conduit (spellbook, conduit), each hydrator's hot-door publication
    (the context), new pooled lesser and spellspace shells, and fast-door entry tuples (a single defer).
    (c) Validate on the VM copy: the full suites on 3.14t and GIL (GIL builds get a no-op), probe_deferred.py
    and probe_steps.py A/B, and the setup-time delta.
  EVIDENCE:
  - context_compass/artifacts/gauntlet_runtime_speed_20260926/vm_runs/deferred_scope_and_ownership.txt:1-55
  - src/melder/aether/conduit/meld/conduit_meld.py:585-620
  - src/melder/aether/conduit/meld/spellspace_meld.py:547-582
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:205-235
  IMPACT: Turns a probe-only win into a candidate with files, tests and costs named. Tree edits still wait for the
    owner's decision, patch docs and NOTICEs to the file owners (melder_0 for the meld files and conduit.py).
  NEXT: Read the hydrator publication sites and Spellbook conjure's tail in full, then write the utility on the
    VM copy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T17:11:10Z
  TYPE: MEASURE
  CLAIM: P3 prototype, library form, VM copy only (device tree at ~17:10Z plus apply_p3.py): the new
    RefcountDeferral utility, called at conjure end, hydrator publication, new lesser and spellspace shells, and
    fast-door entries. A/B against the unmodified tree in interleaved processes, fresh worker thread per lane:
    request 15.55 -> 11.04 us (-29%), worker_a 11.76 -> 8.54 (-27%), worker_b 10.76 -> 8.27 (-23%). Two concurrent
    threads: -33% / -36%. A thread that warmed its own shell: 9.8-9.9 -> 8.6-8.7 us (-11%). Main thread (owns
    everything): -2 to -9%, no regression. Costs: gauntlet setup (bind and conjure, warm cache) 122-128 ->
    137-146 ms (+~17 ms from the conjure walk, ~35 ms on a cold cache). During a whole 3-thread gauntlet run
    defer_graph runs 84 times; everything after conjure totals ~12 ms, all in the first cycles, and there are no
    steady-state walks. With GC disabled, application objects are still released at scope exit and cleanup
    (weakref probe, same on both trees). Suites green on 3.14t -X gil=0 (unit/component/integration spellbook,
    conduit, multithreading, unit/component/integration aether, unit utilities, crystallizer, mutation_research,
    live_sim) and -X gil=1. A standard 3.14 GIL build gives a no-op and ctypes is not loaded. Two known failures
    are unchanged on both trees (build-assets builder x2, asset version stamp). New tests: 13 unit + 4 component.
  EVIDENCE:
  - context_compass/artifacts/gauntlet_runtime_speed_20260926/vm_runs/p3_ab.txt:1-35
  - context_compass/artifacts/gauntlet_runtime_speed_20260926/vm_runs/p3_costs_and_census.txt:1-38
  - context_compass/artifacts/gauntlet_runtime_speed_20260926/p3_deferred_refcount/p3_src.diff:1-273
  - context_compass/artifacts/gauntlet_runtime_speed_20260926/p3_deferred_refcount/refcount_deferral.py:1-372
  IMPACT: Largest validated gain so far and it compounds with P1. What remains is the owner's decision (ctypes
    call into an unstable 3.14 C API; deferred Melder objects reclaimed by the GC; +17 ms conjure; edits in
    melder_0's meld and conduit files), then patch docs and NOTICEs before a tree edit.
  NEXT: DECISION_REQUEST to the owner with the options and the file list.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-26T17:11:21Z
  TYPE: DECISION_REQUEST
  CLAIM: Owner decision on P3 (deferred refcounting of Melder's runtime graph on free-threaded CPython). (A)
    Ship it (recommended): open a P3 task and write patch docs (architecture plus Meld/Conduit/Spellbook
    component patches: memory lifecycle of kernel objects, chokepoints, no-op builds), NOTICE melder_0 before
    touching conduit.py, conduit_meld.py and spellspace_meld.py, apply with --check first, then the owner's
    Windows gauntlet run decides. Files: new melder/utilities/helpers/refcount_deferral.py; spellbook.py (conjure
    and _conjure_existing_conduit tails); conduit.py (new lesser shell); spell_space_pool.py (new spellspace
    shell); conduit_meld.py and spellspace_meld.py (fast-door entries); the generalized, solo and many_only
    hydrators (hot-door publication); plus 2 new test files. (B) Ship it without the fast-door entry sites
    (leaves melder_0's meld doors untouched; that share of the gain is unmeasured). (C) Do not ship: it calls an
    unstable C API through ctypes and GC-reclaims Melder objects. Known costs of A: +~17 ms warm conjure in the
    gauntlet world; Melder objects (not application objects) freed at the next GC collection instead of at
    their last reference; must be re-checked on each CPython minor release (the symbol is PyUnstable).
  EVIDENCE:
  - context_compass/artifacts/gauntlet_runtime_speed_20260926/vm_runs/p3_ab.txt:1-35
  - context_compass/artifacts/gauntlet_runtime_speed_20260926/vm_runs/p3_costs_and_census.txt:1-38
  - context_compass/artifacts/gauntlet_runtime_speed_20260926/p3_deferred_refcount/apply_p3.py:1-218
  IMPACT: Tree edits wait for this answer; A or B opens the P3 task and patch lane.
  NEXT: Ask the owner (A/B/C); record the answer as a DECISION note.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T17:12:06Z
  TYPE: FACT
  CLAIM: Consumed M0-35 (melder_0, 16:31:17Z; owner decision "yeah continue 1"). S2b moves normal melds onto
    melder_0's site-plan lowering, so melder_0 owns code emission for both normal and override melds: the
    generalized and many_only compilers, the hydrators and site_plan_*. P1 will be folded into the lowering and
    kept for the normal lane. melder_2 keeps to meld entry and SpellSpace costs and sends emission levers to
    melder_0 instead of editing those files. generalized_manifest_no_overrides_compiler.py stays as it is until
    S2b lands. For P3, the hydrator chokepoints (the generalized, solo and many_only _hydrate_once and the
    specializer) become a handoff to melder_0. melder_2's own chokepoints stay: the utility, conjure end, new
    lesser and spellspace shells, and fast-door entries in the meld doors (NOTICE first).
  EVIDENCE: tickets/tasks/2026-09-26_build_site_plan_lowering_task.md:1336-1370
  IMPACT: P3 splits by file owner: melder_2 applies the lifecycle and entry sites, melder_0 adds deferral at
    hot-door publication in its emission lane. Walking from each fast-door entry with its context as a root
    still reaches the hydrated executor, so most of the executor share is covered without the hydrators.
  NEXT: ACK M0-35; ask the owner for the P3 decision (A/B/C).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T17:13:19Z
  TYPE: DECISION
  CLAIM: Owner answer (AskUserQuestion, ~17:13Z): "Ship it (Recommended)", i.e. option A. melder_2 opens the P3
    task and patch lane. Per M0-35, melder_2 applies the utility, the conjure-end walk, new lesser and spellspace
    shells, and the fast-door entry sites (walk roots: the entry and its context, which reaches the hydrated
    executor), after NOTICEs. The hydrator and specializer publication lines go to melder_0 as a HANDOFF, not an
    edit. Before any tree edit, re-validate this exact shape (without the hydrator sites) on the VM copy.
  EVIDENCE:
  - tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md:488-509
  - tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md:511-527
  IMPACT: P3 moves from prototype to a patch-gated implementation task.
  NEXT: Open the P3 task (ticket, story checklist, board and artifact rows), then write the patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T17:18:03Z
  TYPE: DECISION
  CLAIM: The owner paused P3 right after answering "Ship it" (~17:15Z): "its not a fix"; the concern is getting
    faster now but slower over time (a pattern the owner has seen with dishka and dependency-injector), plus using
    "frankenstein tech" (ctypes into an unstable C API) to win. P3 is ON HOLD: no P3 task, patch docs or tree
    edits until the discussion ends with a new owner decision. That decision replaces the 17:13:19Z answer.
  EVIDENCE: tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md:529-542
  IMPACT: Prevents a post-compaction resume from shipping P3 on the superseded answer. The long-run question (soak
    and churn behavior) is UNKNOWN: every P3 number so far comes from short runs.
  NEXT: Discuss mechanism, long-run risk and clean alternatives with the owner; record the outcome.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T17:22:58Z
  TYPE: FACT
  CLAIM: Owner proposal under discussion: offer P3 as an opt-in SpellbookConfiguration flag "momentum_mode",
    documented as strictly for short-lived applications and used for benchmarks. Plumbing facts: boolean
    configuration properties already follow one pattern (enforce_priority_disposal_methods: typed schema entry,
    default False, required-property defaults, with_<name>() fluent setter via set_property, freeze at conjure,
    and a restore-compatibility rule for crystallizer records that predate the key). No class in src/melder
    defines __del__, so no Melder teardown depends on deallocation timing. Deferral cannot be undone per object,
    which fits a conjure-frozen setting. The only crash vector is ctypes calling a changed signature on a
    future CPython, fenced by allowing only tested minors (3.14) and falling back to a no-op plus one warning
    elsewhere.
  EVIDENCE:
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:145-149
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:685-695
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:1312-1340
  IMPACT: The flag is a small, patterned change on top of the validated utility; the owner still decides.
  NEXT: Owner answers whether to build momentum_mode (default off, 3.14t-only allowlist, labeled gauntlet lane).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T17:29:58Z
  TYPE: DECISION
  CLAIM: P3 is DROPPED in every form, including the opt-in "momentum_mode"/"haste_mode" flag. Owner (~17:30Z):
    it's clever, but a tactic built on an API that may disappear in future versions "is not really a play", and
    shipping it would look like gaming the benchmark. Nothing goes into src/ or benchmarks/; the prototype and
    measurements stay in artifacts as research (retain_as_reference). The finding stands and drives the plan:
    cross-thread ownership of hot objects dominates the worker-thread cycle on 3.14t. It is to be attacked with
    plain-Python design changes, each gated by a long-run check (30k+ iterations: per-window throughput, RSS,
    GC stats).
  EVIDENCE:
  - tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md:544-575
  - context_compass/artifacts/gauntlet_runtime_speed_20260926/p3_deferred_refcount/apply_p3.py:1-218
  IMPACT: This supersedes the 17:13:19Z "Ship it" answer and the 17:18:03Z hold. The next candidates are the
    clean levers (spell-id interning, thread-affine shell pools, fewer shared hops per meld, SpellSpace.meld entry,
    lifecycle flattening), plus handoffs to melder_0 (module-level executors; P2 via the S2b nested-miss form).
  NEXT: Owner picks the first clean lever; open its task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T17:32:38Z
  TYPE: DECISION
  CLAIM: Owner go-ahead (~17:33Z): "if you think you can improve the speed just don't fuck up the app ... do what
    you think is right just don't break things ... correctness and honesty is the best policy". melder_2 runs
    the clean levers in order of risk, each sized first on the VM copy with no tree edit: (1) spell-id
    interning, (2) thread-affine shell pools (Windows benefit uncertain: ownership follows the OS thread
    identity), (3) a SpellSpace.meld entry fast lane mirroring Conduit.meld, (4) fewer shared-object hops per
    warm meld (NOTICE melder_0). Gates before any tree edit: VM A/B; suites on 3.14t (gil 0 and 1) and the GIL
    build; unchanged behavior and cleanup order; a NOTICE to the file owner; patch docs when system-impacting;
    a 30k-iteration long run. Anything that fails a gate is dropped and recorded.
  EVIDENCE: tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md:577-594
  IMPACT: Sets the order and the gates for the next implementation tasks.
  NEXT: Size lever 1 standalone: intern every string reachable from the kernel after warm-up (no deferral), A/B
    against the tree on fresh worker threads.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T17:33:37Z
  TYPE: MEASURE
  CLAIM: Lever 1 (spell-id interning) on its own gives no gain, so it is DROPPED. Interning in place all 1,281
    strings reachable from the spellbook and root conduit after warm-up (no deferral), 8 interleaved processes,
    fresh worker thread per lane: request 14.69 -> 15.12 us (+3.0%), worker_a 10.81 -> 11.31 (+4.6%), worker_b
    9.73 -> 10.28 (+5.7%), i.e. no improvement (the small slowdown is not explained). The 3-5% seen under P3 existed
    only once the other shared objects were deferred. Strings are not where the cross-thread cost sits.
  EVIDENCE:
  - context_compass/artifacts/gauntlet_runtime_speed_20260926/vm_runs/lever1_intern_ab.txt:1-18
  - context_compass/artifacts/gauntlet_runtime_speed_20260926/probes/probe_intern.py:1-55
  IMPACT: One lever fewer. The shared cost is in object and container loads (spells, contexts, stores, doors,
    shells), which points at levers 2 and 4.
  NEXT: Size lever 2 (thread-affine shell pools) with a gauntlet-shaped probe (new threads per iteration)
    measuring per-thread CPU time per cycle, which removes the VM's preemption noise.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T17:36:01Z
  TYPE: MEASURE
  CLAIM: Lever 2 (thread-affine shell pools), sized with an in-process pool patch (no src change) in a
    gauntlet-shaped probe: 3 new threads per iteration, per-thread CPU time per cycle, 300 iterations, 6
    interleaved pairs. Each thread first reuses shells returned under its own threading.get_ident(), then the
    shared pool. Result: leased lesser shells owned by the running thread rise from 31-34% to 100%. Per-cycle CPU
    request -6.0%, worker_a -7.4%, worker_b -7.1%; wall per iteration -4.5%. The gain is real but much smaller
    than P3, because the kernel (spells, contexts, root objects) stays main-owned. Caveat: on Linux get_ident()
    equals the object-header owner id (pthread_self is the TCB), which the 100% own rate confirms. On Windows
    get_ident() is the thread id while the owner id is the TEB address, so the gain there is UNKNOWN until an
    owner run.
  EVIDENCE:
  - context_compass/artifacts/gauntlet_runtime_speed_20260926/vm_runs/lever2_affine_ab.txt:1-17
  - context_compass/artifacts/gauntlet_runtime_speed_20260926/probes/probe_affine.py:1-94
  IMPACT: A modest, platform-sensitive gain that changes pooling semantics (per-thread idle stacks, sizing,
    cleanup of per-thread lists), so it needs patch docs and care. It ranks after the lower-risk SpellSpace.meld
    entry lane.
  NEXT: Prototype lever 3 on the VM copy: in SpellSpace.meld, inline the warm id fast lane the way melder_0
    inlined Conduit.meld; A/B it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T17:54:14Z
  TYPE: MEASURE
  CLAIM: Lever 3 = P4, a warm id lane in SpellSpace.meld, VM copy only (device tree ~17:37Z plus apply_p4.py,
    CPython 3.14.7t). A `spell_id=` meld with no spell, spellframe or binding_name reads the door's fast-door
    entry and applies SpellSpaceMeld.meld's guard ladder and arms; a miss or any failed guard continues into the
    door. Fresh worker thread, 8 interleaved process pairs, medians: request 12,226 -> 11,784 ns (-3.6%),
    worker_a 10,548 -> 10,141 (-3.9%), worker_b 9,994 -> 9,690 (-3.0%); runs are bimodal (thread-id reuse decides
    shell ownership), so the gain is small against the spread. Gauntlet shape (3 new threads per iteration,
    per-thread CPU per cycle, 5 pairs): -2.4% / -2.6% / -1.9%. 30k-iteration soak (30 windows): medians
    16,548 / 12,305 / 12,534 -> 16,209 / 12,046 / 12,167 ns; last 5 windows vs windows 2-6 flat on both trees
    (within 1.3%); RSS 81.6 -> 83.6 MB on both; GC collections 14 on both. Suites passed on 3.14t (gil 0, and a
    gil 1 subset) and on the 3.14.7 GIL build (subset) during the session; those logs were not retained. The new
    component test (8 cases) fails its 3 lane-specific cases on the base tree and passes on P4.
  EVIDENCE:
  - artifacts/gauntlet_runtime_speed_20260926/vm_runs/p4_ab_fresh_thread.txt:1-16
  - artifacts/gauntlet_runtime_speed_20260926/vm_runs/p4_gauntlet_shape.txt:1-10
  - artifacts/gauntlet_runtime_speed_20260926/vm_runs/soak_base_30k.txt:1-32
  - artifacts/gauntlet_runtime_speed_20260926/vm_runs/soak_p4_30k.txt:1-32
  - artifacts/gauntlet_runtime_speed_20260926/p4_spellspace_warm_lane/p4_src.diff:1-103
  - artifacts/gauntlet_runtime_speed_20260926/p4_spellspace_warm_lane/test_spellspace_component_warm_id_lane.py:1-239
  IMPACT: A modest (~2-4%) per-cycle gain with no drift; not applied. Gates still open before any tree edit: prove
    the lane cannot skip the active-scope check or any other check the door runs before its fast path; re-run the
    suites with saved logs; NOTICE melder_0 (one doc sentence in meld.py, a fourth reader of _fast_meld_doors).
  NEXT: Read SpellSpace.meld and SpellSpaceMeld.meld in full on the device tree and map every check the door
    performs before its fast path against the lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T17:57:01Z
  TYPE: FACT
  CLAIM: P4 skips no check that the door performs. The current SpellSpace.meld checks only that spell and spell_id
    are not both given, then forwards to its own SpellSpaceMeld door. For a str spell the door's first action is
    its fast door, which uses the same guard ladder and arms that the lane copies. Neither method checks that the
    space is the conduit's active spellspace. SpellSpaceScopeError is raised only by pop_expected on LIFO exit.
    The lane calls the same executors with the same door object, so anything an executor raises is unchanged.
    The lane is narrower than the door's fast path: it requires type(spell_id) is str and no spellframe or
    binding_name. Every other call shape reaches the door with the same arguments as before.
  EVIDENCE:
  - src/melder/aether/conduit/spell_space/spell_space.py:455-507
  - src/melder/aether/conduit/meld/spellspace_meld.py:235-627
  - src/melder/aether/conduit/spell_space/spell_space_thread_state.py:219-248
  IMPACT: The equivalence claim holds when checked against the source. The remaining pre-apply gates are a suite
    re-run with saved logs and the NOTICE to melder_0.
  NEXT: Record the stale active-scope documentation as a RISK, then re-run the suites on the refreshed copy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T17:57:01Z
  TYPE: RISK
  CLAIM: Pre-existing and independent of P4: Melder's documents describe an active-scope check on SpellSpace.meld
    that the source does not perform. Places: src_architecture "Sequence: SpellSpace Usage", the invariant "can
    only meld when it is the active spellspace", and the failure mode "SpellSpaceScopeError if a non-active
    SpellSpace is used for meld"; src_components "SpellSpace Scope Gate" and "Flow: SpellSpace Scoped Meld" (the
    flow also says it delegates to Conduit.meld; in the source it goes to its own door); the SpellSpace.__init__
    docstring ("fails its active-scope check") and the SpellSpaceMeld class docstring. In the source, a handle kept
    after its with-block, once the space is back in the pool, can still meld. The scope store is cleared at exit
    (recycle_from_managed_context) and not at acquire, so a unique_per_spell_space object built through a stale
    handle stays in the idle space. The next scope that acquires that space, possibly on another thread, is then
    served it. This takes caller misuse (purge's docstring already calls reuse of an old reference a violation),
    but the documents promise a refusal.
  EVIDENCE:
  - src/melder/aether/conduit/spell_space/spell_space.py:305-363
  - src/melder/aether/conduit/spell_space/spell_space_pool.py:185-211
  - src/melder/aether/conduit/spell_space/spell_space.py:141-156
  - src/melder/aether/conduit/meld/spellspace_meld.py:62-70
  - system_docs/src_architecture.md:787-791
  - system_docs/src_architecture.md:1151-1151
  - system_docs/src_architecture.md:1237-1237
  - system_docs/src_components.md:5587-5599
  - system_docs/src_components.md:6361-6366
  IMPACT: This is an owner decision and outside P4: (a) enforce the check cheaply, e.g. a per-space active flag set
    at enter and cleared at exit with one compare in SpellSpace.meld, turning misuse into SpellSpaceScopeError; or
    (b) correct the documents so reuse after exit is stated as unchecked caller misuse. P4 changes neither.
  NEXT: Put the decision to the owner with the P4 report; do not change behaviour without an answer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T18:04:29Z
  TYPE: MEASURE
  CLAIM: P4 suites re-run with saved logs on a copy refreshed from the device tree at 17:55Z. The only drift since
    the 17:37Z copy was __version__.py. apply_p4.py applied cleanly on the refreshed copy, touching only
    spell_space.py and meld.py. CPython 3.14.7t -X gil=0, all passed: unit/component/integration spellbook
    2227/778/586, conduit 268, multithreading 42, unit/component/integration aether 4145/1214/716, unit and
    component utilities 802/21, crystallizer 565/258/110, mutation_research 277/66/40, live_sim 1. The only failures
    are the 3 pre-existing build-asset and version-stamp cases, identical on the base copy. -X gil=1 and the
    3.14.7 GIL build: spellbook x3, component aether, conduit, multithreading and unit aether all passed. The new
    warm-lane test: 8/8 on P4; on the base copy its 3 lane-specific cases fail and the other 5 pass.
  EVIDENCE:
  - artifacts/gauntlet_runtime_speed_20260926/vm_runs/p4_suites.txt:1-45
  IMPACT: The suite gate is closed with retained logs. Left before the apply: the NOTICE to melder_0, a check that
    meld.py is unchanged at apply time, and the doc decision (patch docs or not) recorded.
  NEXT: Check whether src_components describes the fast-door readers or the SpellSpace.meld call path that P4
    changes, then record the doc decision.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T18:04:52Z
  TYPE: DECISION
  CLAIM: P4 gets no patch docs, by the same test applied to P1. It changes no boundary, lifecycle, policy or
    cross-component contract, and results, errors and cleanup are identical. src_components mentions the fast-door
    memo only in passing (admission and rebuild windows); neither system document lists the fast-door readers or
    the warm id lanes. The code-level contract carries the change: the SpellSpace.meld docstring, and the reader
    list in Meld._fast_meld_doors (one sentence in meld.py, melder_0's file, after a NOTICE). The stale SpellSpace
    scope wording in both system documents waits for the owner's answer on the scope RISK, so it is corrected once.
  EVIDENCE:
  - system_docs/src_components.md:2865-2877
  - system_docs/src_components.md:2913-2920
  - artifacts/gauntlet_runtime_speed_20260926/p4_spellspace_warm_lane/p4_src.diff:1-103
  IMPACT: P4 can go to the device tree once the NOTICE is sent and meld.py is confirmed unchanged at apply time.
  NEXT: Open the P4 task (ticket, story checklist, board and artifact rows), then NOTICE melder_0.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T19:13:01Z
  TYPE: MEASURE
  CLAIM: P4 re-validated on the device tree as of 19:06Z (0.2.66; melder_0's S2-S5 landed since 17:55Z). None of
    P4's files or the doors changed. apply_p4.py applied cleanly and its diff body is byte-identical to the
    validated p4_src.diff. Suites on CPython 3.14.7t -X gil=0 all passed: unit/component/integration spellbook
    2245/790/586, conduit 268, multithreading 42, unit/component/integration aether 4146/1215/716, utilities
    802/21, crystallizer 565/258/110, mutation_research 277/66/40, live_sim 1. The only failures are the 3
    pre-existing build-asset and version-stamp cases, identical on the base copy. -X gil=1 and the 3.14.7 GIL
    build (spellbook x3, component aether, conduit, multithreading, unit aether) all passed. Speed:
    - Cached space meld on a worker thread: 252-263 -> 208-237 ns, close to calling the door directly (~197 ns).
    - Gauntlet shape (3 new threads per iteration, per-thread CPU, 6 pairs): request -2.4%, worker_a -2.6%,
      worker_b -2.7%.
    - Fresh-thread probe: bimodal (thread-id reuse decides shell ownership), so plain medians mislead. Within
      each mode it gives -2% to -5%, except worker_a in the fast mode (~0%).
    probe_deferred.py and probe_cached_meld.py in the artifacts were refreshed to the versions these runs used
    (MELDER_ROOT tree selection; one extra research scope, visible in git diff).
  EVIDENCE:
  - artifacts/gauntlet_runtime_speed_20260926/vm_runs/p4_suites_1906.txt:1-41
  - artifacts/gauntlet_runtime_speed_20260926/vm_runs/p4_cached_meld_1913.txt:1-36
  - artifacts/gauntlet_runtime_speed_20260926/vm_runs/p4_gauntlet_shape_1911.txt:1-12
  - artifacts/gauntlet_runtime_speed_20260926/vm_runs/p4_ab_fresh_thread_1910.txt:1-16
  - artifacts/gauntlet_runtime_speed_20260926/probes/probe_cached_meld.py:1-45
  IMPACT: P4 holds on today's tree: about -17% per cached space meld and -2.5% per gauntlet cycle. Only
    bookkeeping remains before the apply.
  NEXT: Open the P4 task and board rows, send the NOTICE to melder_0, then apply with --check first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Opened 2026-09-26 on the owner's request to run the benchmarks and speed up the library. Baseline filed (owner
runs, same-run ratios); no runs by melder_2 yet. Waiting on D1-D3; next is the 3.14t VM copy and a reduced-
iteration smoke run, then the harness read and the per-cycle attribution.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
