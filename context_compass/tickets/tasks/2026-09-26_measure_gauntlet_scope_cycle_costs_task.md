

# Task: Reproduce the real-world gauntlet and attribute Melder's per-scope-cycle cost

## Metadata
- Task ID: TASK-2026-09-26-measure-gauntlet-scope-cycle-costs
- Story: STORY-2026-09-26-gauntlet-runtime-speed
- Status: in_progress
- Owner: user
- Agent Name: melder_2
- Priority: p1
- Created: 2026-09-26T15:43:24Z
- Updated: 2026-09-26T23:01:16Z

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
- [x] Build the VM copy: CPython 3.14t via uv, Melder's runtime dependencies, dishka, dependency-injector and
      pytest; copy src/, benchmarks/ and pyproject.toml; smoke-run the gauntlet at reduced iterations.
- [x] Read the gauntlet harness (the Melder lane and the shared driver) in full; record what each reported metric
      measures (wall versus active cycles, the scope create and cleanup windows).
- [x] Run the gauntlet on the VM copy (threads 1, 2 and 3, repeated) and compare same-run ratios with the owner's.
- [ ] Attribute the Melder scope cycle: call counts and time per sub-step, single-threaded first; run the existing
      probes (profile_scope_cycle_contention.py, test_melder_gauntlet_gc_probe.py) once each.
- [x] Read the attributed runtime code in full (pooled lesser and SpellSpace acquire and return, creations
      disposal, ID minting, per-cycle locks); record the per-cycle cost map.
- [x] Rank candidates with expected gain, risk, files and owning lane; DECISION_REQUEST to the owner.
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
  - artifacts/gauntlet_runtime_speed_20260926/lever1/
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

- DATETIME: 2026-09-26T19:42:21Z
  TYPE: MEASURE
  CLAIM: Owner-run Windows gauntlet on the 0.2.68 tree (melder_0 S2-S5 + R1, P4), 10k and 30k iterations, all
    three libraries in each run. Same-run ratios against the morning 30k baseline:
    - hot_scopes/s, melder/dishka: 0.875 (10k), 0.859 (30k); was 0.779. melder/DI: 1.016, 0.929; was 0.976.
    - active cycles/s (the SpellSpace window), melder/dishka at 30k: request 0.997, worker_a 0.852, worker_b
      1.012; was 0.551, 0.634, 0.769. The 10k run: 1.071, 0.920, 1.094.
    - wall cycles/s: 0.84 on every lane in both runs; was 0.74.
    - Remaining average gap: outside the SpellSpace window (lesser create, lesser melds, cleanup, thread
      spawn). Melder's outer cycle averages 2-3 us more than dishka's while the request windows are equal.
    - Tail: Melder's single-cycle maxima stay 4-10x the competitors' in every run. Outer cycle max 9.61 / 6.11
      ms against dishka 1.71 / 1.41 and DI 0.88 / 1.12; request window max 7.08 / 4.38 against 0.67 / 1.05 and
      0.87 / 0.71. The p99s are equal (0.018 to 0.039 ms), so these are rare events. The iteration-level max is
      noisier: DI also hit 14.87 ms in the 10k run.
  EVIDENCE:
  - artifacts/gauntlet_runtime_speed_20260926/owner_run_20260926_1931_10k_30k.txt:1-115
  - artifacts/gauntlet_runtime_speed_20260926/owner_run_20260926_ratios.txt:1-44
  - artifacts/gauntlet_runtime_speed_20260926/owner_run_20260926.txt:1-92
  IMPACT: The active-window gap is closed on two lanes, and hot_scopes/s moved from 0.78x to 0.86x dishka.
    Two targets remain: the per-cycle scope lifecycle (average) and a rare multi-millisecond event unique to
    Melder (tail). The owner points at the tail first.
  NEXT: Open the tail task; run the harness's own per-turn GC attribution on the VM copy to test the GC hypothesis.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-26T20:28:57Z
  TYPE: FACT
  CLAIM: The average gap after P4, from the owner's 19:40Z (200k) and 20:05Z (30k) runs, is about 0.2 ms per
    iteration against dishka (hot_scopes/s 0.86-0.87x). About half of it sits in the worker lanes' outer cycles,
    at +2 to +3 us per cycle. worker_a is the only lane below dishka inside the SpellSpace window (0.86-0.91x). The
    other half lies outside the timed cycles. There the tail task measured a thread-exit cost that grows with state
    built on worker threads: Melder's world has the largest on the VM, and first use on the main thread cuts it.
    Evidence and numbers are in the tail task.
  EVIDENCE:
  - tickets/tasks/2026-09-26_attribute_gauntlet_tail_spikes_task.md:245-334
  - tickets/tasks/2026-09-26_attribute_gauntlet_tail_spikes_task.md:336-369
  IMPACT: Two levers for the average gap: conjure-time hydration, which it shares with the tail fix, and the
    worker lanes' in-cycle cost, starting with worker_a's operation mix.
  NEXT: The owner picks. Then either prototype conjure-time hydration on the VM, or break down worker_a's cycle
    step by step against dishka, as was done for the request lane at 15:50Z.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T20:38:41Z
  TYPE: DECISION
  CLAIM: Owner (~20:37Z): "well you can look into 1 because the other guy has been working on that shit for like 2
    hours". melder_2 takes lever 1: the worker lanes' per-cycle cost. Compile caching (lever 2) stays in melder_0's
    area. Plan:
    - Take a fresh VM copy of the device tree at 0.2.70 (tree_0270, caches excluded).
    - Step-by-step breakdown of the worker_a and worker_b cycles for Melder and dishka on one worker thread, with the
      root build separated from the group build.
    - Find which step carries the gap, read that path in full, then prototype and A/B.
    Gates, as before: VM A/B, suites on 3.14t and GIL, a 30k soak, a NOTICE to the file owner, patch docs if the
    change is system-impacting. Also the owner's rules: a lever must remove work, and pools and their shells stay
    created when they are today.
  EVIDENCE:
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:261-311
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:824-926
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1040-1165
  IMPACT: Work stays in melder_2's lane (scope lifecycle and SpellSpace path). No tree edit until a measured win.
  NEXT: Run the step breakdown on tree_0270.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T20:39:53Z
  TYPE: MEASURE
  CLAIM: Step breakdown of the worker lanes. VM, tree_0270 (0.2.70), one worker thread, 4000 cycles, two
    interleaved rounds, medians. Per cycle, worker_a: Melder 6.9-7.1 us, dishka 5.9 us. worker_b: Melder 6.7 us,
    dishka 6.2 us.
    - Melder builds objects faster than dishka:
      - root build: worker_a 1.30-1.31 us vs 1.83-1.84; worker_b 1.22-1.24 vs 2.23-2.25;
      - group build: 0.59-0.60 vs 0.72 (a), 0.48 vs 0.56 (b);
      - session build: 0.85-0.88 vs 0.99-1.00.
    - Melder loses on the scope lifecycle: lesser create 0.78-0.81 us vs 0.39-0.40; lesser cleanup 0.85-0.87 vs
      0.10; spellspace exit 0.54-0.58 vs 0.27-0.31; spellspace enter 0.23-0.24 vs 0.34. The lifecycle totals about
      2.4-2.5 us against 1.1-1.2 us, i.e. +1.3 us per cycle.
    - Smaller losses:
      - first build of the one-object scoped marker: 0.65-0.66 vs 0.40 us;
      - each cached meld: 0.25-0.35 vs 0.18-0.20 us (three per cycle).
  EVIDENCE:
  - artifacts/gauntlet_runtime_speed_20260926/lever1/steps_worker_lanes_vm.txt:1-9
  - artifacts/gauntlet_runtime_speed_20260926/lever1/probe_steps2.py:1-84
  IMPACT: On one thread, Melder already wins on object construction. Per cycle it loses +1.3 us in the lifecycle,
    +0.26 us on the first meld in a fresh scope, and about +0.25 us on cached melds. The lifecycle is in melder_2's
    lane and is the largest target, starting with cleanup (0.86 vs 0.10 us). This does not reproduce the Windows
    in-window loss on worker_a (0.86-0.91x): on the VM, Melder is slightly faster inside the window. Whether the
    Windows loss comes from three threads on separate cores is UNKNOWN.
  NEXT: Profile lesser cleanup, lesser create and spellspace exit on a worker thread (calls and time per function),
    then read those paths in full.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T20:41:53Z
  TYPE: FACT
  CLAIM: The scope-lifecycle path on tree_0270 was re-read in full. It is unchanged since the 16:33:35Z FACT, and
    alone it costs 1.88 us per cycle on a worker thread. Per anonymous cycle it does:
    - five RLock pairs: the root Conduit lock and the root ward lock on link, which every thread shares; then the
      lesser's Conduit lock, its Creations lock and its ward lock on cleanup;
    - three threading.local reads: stack push, pop_expected and drain;
    - two deque pops and two appends, on the lesser pool and the spellspace pool;
    - one insert and one pop on the root ward's _lesser_conduits dict. The pop runs under the child's ward lock.
    Redundant work in the root case: create_lesser_conduit checks root_conduit for None and normal state when the
    root is self, and _link_lesser_conduit resolves and checks the root again. Under cProfile (inflated), the
    cumulative time per cycle is cleanup 4.3 us, create 3.2, spellspace exit 2.1 and enter 1.1.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:566-643
  - src/melder/aether/conduit/conduit.py:672-705
  - src/melder/aether/conduit/conduit.py:1201-1234
  - src/melder/aether/conduit/conduit.py:2539-2792
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:382-424
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1176-1218
  - src/melder/aether/conduit/creations/creations.py:1046-1104
  - src/melder/aether/conduit/spell_space/spell_space.py:233-363
  - src/melder/aether/conduit/spell_space/spell_space_pool.py:185-288
  - src/melder/aether/conduit/spell_space/spell_space_thread_state.py:187-289
  - artifacts/gauntlet_runtime_speed_20260926/lever1/lifecycle_cprofile_vm.txt:1-47
  IMPACT: The lifecycle's cost is bookkeeping that other contracts depend on: pooling, the parent registry for
    cleanup cascades, locks for shared lessers, and per-thread scope stacks. conduit.py is melder_0's file (NOTICE
    first). Which pieces can shrink without a contract change is UNKNOWN until each is sized.
  NEXT: Time each lifecycle piece and the primitives (RLock pair, threading.local read, deque, dict) on a worker
    thread to size what a contract-preserving trim can reach.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T20:45:59Z
  TYPE: MEASURE
  CLAIM: What each piece of the anonymous scope lifecycle costs, and whether concurrency widens the gap. VM,
    tree_0270, worker thread, empty stores, ns, two runs each.
    - Lesser create, 718-753 ns total:
      - link under lock 429-431 (root Conduit lock, root ward lock, dict insert, child-ward fields, logger
        check);
      - pool pop 72-75, state sets 76-88, check_cleaned 30.
    - Lesser cleanup, 726 ns total:
      - detach 206-211, spellspaces-for-pool 103-107, pool return 101-103, creations reset 87-90;
      - state and hooks 63-64, the lesser's lock 56-59.
    - Spellspace enter plus exit, about 330 ns: push 85-91, pop_expected 88-91, acquire 54-59, release 55-56,
      reset 39-44.
    - Primitives: RLock pair 64, threading.local read 35, method call 28, deque pop+append 53, dict set+pop
      67-72, logger.is_attached property 46.
    - Two concurrent threads (probe_contention.py) raise per-cycle CPU for both libraries alike: Melder 7.1 ->
      10.0-10.2 us, dishka 5.8-6.0 -> 9.0-9.1 us. On the VM the gap does not grow with concurrency (+1.2 ->
      +1.0-1.1 us).
  EVIDENCE:
  - artifacts/gauntlet_runtime_speed_20260926/lever1/lifecycle_parts_vm.txt:1-51
  - artifacts/gauntlet_runtime_speed_20260926/lever1/probe_parts.py:1-113
  - artifacts/gauntlet_runtime_speed_20260926/lever1/contention_worker_a_vm.txt:1-9
  - artifacts/gauntlet_runtime_speed_20260926/lever1/probe_contention.py:1-75
  IMPACT: Nearly every piece carries a contract: pooling, the parent registry that lets a root clean its active
    scopes, the locks that keep a shared lesser safe, and the per-thread scope stacks. Removing redundant checks
    and one duplicate root lookup would save about 50-150 ns per cycle (1-2%) with no contract change. The larger
    step is the lock structure of anonymous link and detach: 3 lock pairs, 2 of them on shared root objects. That
    needs a design change with patch docs. The Windows in-window loss on worker_a does not reproduce on the VM
    with 1 or 2 threads; only a Windows run of the step probes can locate it.
  NEXT: DECISION_REQUEST to the owner: Windows step runs first, then decide on the lock change.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T20:45:59Z
  TYPE: DECISION_REQUEST
  CLAIM: Lever 1 options for the owner.
    (1) Windows step runs, recommended first: probe_steps2.py (melder and dishka, worker_a) and probe_contention.py
        (worker_a, 1 and 3 threads). They show whether worker_a's Windows loss sits in one step or appears only
        under concurrency.
    (2) Lock simplification for anonymous scopes. Link and detach would run under the root ward's lock only, with
        a closed flag that root cleanup sets under that same lock. That takes the root Conduit lock off the
        per-cycle path, and the parent's _lesser_conduits dict would no longer be mutated under the child's lock.
        Estimated -60 to -130 ns per cycle single-threaded; the effect under multi-core contention is UNKNOWN.
        Needs patch docs, a NOTICE to melder_0 (conduit.py) and the full suites.
    (3) Contract-free trims: redundant root checks and the duplicate root resolution, 1-2%. Low value, not
        recommended on its own.
  EVIDENCE:
  - tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md:885-948
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:306-330
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:382-424
  - src/melder/aether/conduit/conduit.py:2723-2792
  IMPACT: The owner picks. No tree edit happens before a pick and a measured win.
  NEXT: Report to the owner with the Windows commands.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T20:54:48Z
  TYPE: MEASURE
  CLAIM: Owner Windows runs of the step probes (tree 0.2.70, ~20:50Z).
    - One worker thread, worker_a, medians in ns. Windows perf_counter ticks every 100 ns, so every value is a
      multiple of 100. Melder / dishka:
      - root build 1800 / 2700, group 800 / 1000, session 1100 / 1400;
      - lesser create 1000 / 500, cleanup 1100 / 200, spellspace exit 700 / 400, enter 300 / 500;
      - first marker 900 / 600;
      - cycle sum 9.2 / 8.6 us.
      This is the VM's pattern: Melder builds faster and loses on lifecycle bookkeeping. Inside the request window
      Melder is faster on one thread (about 5.6 vs 6.2 us).
    - The 3-thread contention runs have no usable resolution. On Windows thread_time advances in 15.625 ms ticks,
      so each 3000-cycle block reads as 2 or 3 ticks (10,417 or 15,625 ns per cycle).
  EVIDENCE: artifacts/gauntlet_runtime_speed_20260926/lever1/owner_windows_steps_contention_20260926_2050.txt:1-16
  IMPACT: On one thread Melder wins inside the request window on Windows too, while the gauntlet's 3-thread worker_a
    window loses (0.86-0.91x dishka). The loss therefore appears with concurrency. Which steps inflate under 3
    threads is UNKNOWN until a probe with Windows-usable timing runs.
  NEXT: Write probe_steps3.py: T concurrent threads, per-step trimmed means (quantization averages out) and wall
    time per cycle, then validate it on the VM with 1 and 2 threads.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T20:56:57Z
  TYPE: MEASURE
  CLAIM: With two concurrent threads, Melder's request window goes from faster than dishka's to slower, and the
    extra cost sits in the steps that touch shared root objects. VM, probe_steps3.py, worker_a, 2 vCPUs, 95%
    trimmed means per step, two rounds.
    - Request window: 1 thread Melder 4.26 us vs dishka 4.35-4.39 us; 2 threads 5.67-5.98 vs 5.50-5.59 us.
    - Lifecycle: 1 thread 2.58-2.65 vs 1.17-1.18 us; 2 threads 3.43-3.58 vs 1.46-1.49 us.
    - Growth from 1 to 2 threads per step, Melder vs dishka (ns):
      - lesser cleanup +440 vs +48; first marker meld +356 vs +208; spellspace exit +158 vs +30;
      - lesser create +212 vs +130; cached melds +93 to +120 vs +38 to +106;
      - construction steps grow alike: root +462 vs +489, session +493 vs +530, group +174 vs +158.
      In total Melder grows about 0.84 us more per cycle than dishka, so the per-cycle gap nearly doubles (+0.97
      -> +1.81 us).
  EVIDENCE:
  - artifacts/gauntlet_runtime_speed_20260926/lever1/steps_concurrency_worker_a_vm.txt:1-9
  - artifacts/gauntlet_runtime_speed_20260926/lever1/probe_steps3.py:1-105
  IMPACT: This matches the Windows picture: Melder wins inside the window on one thread (VM and Windows) and loses
    it under concurrency (gauntlet, 3 threads). The Melder-specific growth is in the lifecycle, which touches the
    root's shared locks, children dict and pool deque every cycle. It also writes shared ConduitState enum members
    into state fields, so every thread does atomic refcount traffic on the same few objects; that part is a
    HYPOTHESIS, not measured separately. Cached and first melds also grow more; they read shared kernel objects
    (spells, contexts, the spellbook). Candidate structural levers, all needing a design and the owner's pick: a
    sharded root pool created with the root, a single lock for anonymous link/detach, a sharded children registry.
    The owner's Windows run with 1 and 3 threads decides which steps matter there.
  NEXT: Owner runs probe_steps3.py on Windows (melder and dishka, worker_a, 1 and 3 threads).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T20:57:15Z
  TYPE: FACT
  CLAIM: Consumed M0-46 (melder_0, 20:47:28Z). melder_0's S6 moves __version__ from 0.2.70 to 0.2.71 and rebuilds
    the assets (_agent_documentation, _bind_guard, _system_documents manifests). Its src edits are docstring-only,
    in its own lane's files (site-plan modules, site-graph analysis and processor, both family hydrators), with
    graph descriptors re-authored. Any melder_2 change that lands after this notches above 0.2.71.
  EVIDENCE: tickets/tasks/2026-09-26_build_site_plan_lowering_task.md:2888-2925
  IMPACT: tree_0270 differs from the device only by docstrings and assets in melder_0's files, so lever-1
    measurements on it stand. A future lever-1 apply takes the next notch after 0.2.71.
  NEXT: Owner runs probe_steps3.py on Windows (1 and 3 threads).
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T21:06:36Z
  TYPE: MEASURE
  CLAIM: Owner Windows run of probe_steps3.py (~21:05Z, worker_a, 1 and 3 threads, 95% trimmed means). It
    overturns the VM's contention reading.
    - On Windows Melder's lifecycle does not grow with 3 threads (4,524 -> 4,563 ns); dishka's grows 1,481 -> 1,824.
      With threads the window grows +983 ns for Melder and +1,662 for dishka.
    - Windows' problem is single-thread cost. One thread, Melder / dishka:
      - wall 14.5 / 9.7 us per cycle; lifecycle 4.52 / 1.48 us (create 1,478 / 489, cleanup 1,587 / 144, exit
        1,020 / 406);
      - first marker meld 1,111 / 569; cached melds 402-454 / 273-279;
      - root build 2,246 / 2,617.
      At 3 threads: window 8,089 / 7,667 ns (Melder +5.5%), wall 15.3-15.9 / 13.2-13.7 us.
    - Melder's lifecycle steps carry a heavy tail on Windows: these means are about 1.45x the 20:50Z medians (create
      1,000, cleanup 1,100, exit 700). dishka's means match its medians.
  EVIDENCE:
  - artifacts/gauntlet_runtime_speed_20260926/lever1/owner_windows_steps3_20260926_2105.txt:1-12
  - artifacts/gauntlet_runtime_speed_20260926/lever1/owner_windows_steps_contention_20260926_2050.txt:1-16
  IMPACT: The Windows target is Melder's single-thread lifecycle: about +3 us per cycle, half of it a frequent
    slow tail. It is not contention, so the sharded pool and the single lock are not supported by Windows data. What
    makes the lifecycle slow and heavy-tailed on Windows is UNKNOWN. HYPOTHESES: the elastic pool policy
    occasionally evicting or rebuilding shells; delayed frees of dict tables in stores that other threads have
    touched; OS memory calls.
  NEXT: Read AbstractElasticPool (the pool policy behind create and cleanup), then build a Windows parts probe that
    reports p50/p90/mean per lifecycle piece.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T21:08:15Z
  TYPE: FACT
  CLAIM: The elastic pool policy cannot explain a steady-state tail. AbstractElasticPool.release evicts only when
    the idle deque exceeds _target_idle. The target starts at baseline_idle=20 and changes only after a miss
    (stretch) or an overflow (decay). A single-thread cycle keeps at most one idle shell, so nothing is evicted or
    rebuilt. probe_parts2.py times every lifecycle piece with p50, p90 and mean, with the stores populated. On the
    VM the distributions are tight (p90/p50 about 1.1-1.2):
    - public calls: create 813, enter 238, exit 345, cleanup 838 ns (p50);
    - heaviest pieces: link under lock 519, detach 254, creations reset with entries 190, spaces-for-pool 149,
      pool return 136 ns (p50, timer included).
  EVIDENCE:
  - src/melder/utilities/general_base/abstract_elastic_pool.py:290-345
  - artifacts/gauntlet_runtime_speed_20260926/lever1/parts2_vm.txt:1-21
  - artifacts/gauntlet_runtime_speed_20260926/lever1/probe_parts2.py:1-107
  IMPACT: Whether Windows has a real heavy tail in one piece, or the 21:05Z means caught machine noise (the Melder
    runs rewrite the creation cache after the 0.2.71 notch, which the dishka runs do not), is UNKNOWN until
    probe_parts2.py runs on Windows. That same run gives the Windows per-piece costs.
  NEXT: Ask the owner for two Windows runs of probe_parts2.py.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T21:12:27Z
  TYPE: MEASURE
  CLAIM: Owner Windows runs of probe_parts2.py (~21:10Z, tree 0.2.71): no piece of the lifecycle has a Windows-only
    slow path.
    - Run 1: every piece had a similar tail (p90 about 2x p50, e.g. create 1,200/2,700, cleanup 1,300/2,800),
      which is machine-wide noise, not one piece.
    - Run 2, warm cache: tight (p90/p50 about 1.1). Means: create 1,006, enter 257, exit 423, cleanup 1,103 ns.
      Pieces, timer included: link under lock 641, detach 344, creations reset 251, spaces-for-pool 178,
      pop_expected 170, pool return 166, push 148, store reset 140, pool pop 136, state/hooks 133, state sets
      128, lock pair 125, acquire 120, release 118, check_cleaned 81.
    - Windows runs about 1.2-1.3x the VM, uniformly. The heavy tails in the 21:05Z means were noise.
    - The lifecycle is about 2.8 us per cycle against dishka's 1.5 us, so about +1.3 us. It is spread over
      roughly 15 pieces of 80-640 ns, each doing contract work: two root locks and the children-dict insert on
      link, three lesser locks on cleanup, pool reuse, per-thread stack push/pop and drain, state flags.
    - Each first build takes two lock pairs: 9 RLock pairs per cycle with two builds against 5 for the lifecycle
      alone. A gauntlet cycle has three first builds (session, marker, root), so about six pairs, roughly 0.5 us
      on Windows. (Corrected 21:32Z: the two pairs are the same slot guard taken twice, by the door and then the
      site plan, not the slot guard plus the store lock. Objects without disposal methods publish without the
      store lock. See tickets/tasks/2026-09-26_spellspace_build_locks_task.md:235-281.)
  EVIDENCE:
  - artifacts/gauntlet_runtime_speed_20260926/lever1/owner_windows_parts2_20260926_2110.txt:1-46
  - artifacts/gauntlet_runtime_speed_20260926/lever1/lifecycle_cprofile_vm.txt:6-7
  - tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md:346-378
  IMPACT: Lever 1 holds no contract-preserving big win. Trims that change nothing (redundant root checks, the
    duplicate root lookup on link) save about 0.1 us per cycle. The larger pieces each need a guarantee or protocol
    redesign:
    - skip build locks for spellspace-scoped builds in a thread-confined managed spellspace (about 0.3 us per
      cycle; melder_0's emission lane and a concurrency-contract question);
    - one lock for anonymous link (about 0.1 us);
    - a cheaper fast-door check (about 0.1-0.2 us per cycle; melder_0's guard ladder, four readers).
  NEXT: DECISION_REQUEST to the owner: close lever 1 as measured, or pursue one of the redesigns.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T21:12:27Z
  TYPE: DECISION_REQUEST
  CLAIM: Lever 1 outcome for the owner.
    (1) Recommended: close lever 1 as measured. Melder builds objects faster than dishka. Its extra ~1.3 us per
        scope pays for guarantees dishka's scopes do not carry: thread-safe shared scopes, cascade cleanup through
        the children registry, pooled shells, per-thread spellspace stacks. No single piece is waste.
    (2) Pursue the largest redesign: skip the two build locks for spellspace-scoped objects when the spellspace is
        a thread-confined managed one. About 0.3 us per cycle on Windows. It needs the owner to confirm the
        confinement contract covers melds, a design with melder_0 (emission and Creations slot_guard), and patch
        docs.
    (3) Smaller redesigns: one lock for anonymous link (~0.1 us); a single-check fast door (~0.1-0.2 us, melder_0).
    (4) Contract-free trims (~0.1 us): only if bundled with another change to conduit.py.
  EVIDENCE: tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md:1085-1117
  IMPACT: The owner decides whether lever 1 closes or one redesign opens as its own task.
  NEXT: Report to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T21:15:35Z
  TYPE: DECISION
  CLAIM: Owner (~21:15Z), answering the lever-1 DECISION_REQUEST: "ok cool so lets move on then and look at those".
    - The lifecycle part of lever 1 closes as measured: no contract-free win beyond about 0.1 us, and no redesign
      of scope linking now.
    - The spellspace build locks move to their own discovery task: whether first builds of spellspace-scoped
      objects can skip the slot guard and store lock when the spellspace is thread-confined.
    - Discovery only: read, VM prototype, then a DECISION_REQUEST with a design and the file owners. No tree edit.
  EVIDENCE: tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md:1085-1135
  IMPACT: The measure task keeps the cost map. The lock question gets its own ticket and board row.
  NEXT: Open TASK-2026-09-26-spellspace-build-locks (ticket, board row, story line, artifact row).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T23:01:16Z
  TYPE: FACT
  CLAIM: The owner turned in P1, P4, the tail attribution, the build-locks discovery and the nested slot-guard
    removal after the 22:47Z Windows run (hot_scopes/s 0.919x dishka on 0.2.74). In that run most of the
    per-iteration gap sits outside the measured cycles, and inside them in the outer scope's create and cleanup,
    which lever 1 closed as measured.
  EVIDENCE:
  - artifacts/gauntlet_runtime_speed_20260926/owner_run_20260926_2247_ratios.txt:1-63
  - tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md:1119-1149
  IMPACT: This task keeps the cost map; the open levers wait for the owner's pick.
  NEXT: Owner decides whether thread-affine pools or a small redesign is worth a task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Attribution is done: the cost map is in Notes, from 15:50Z to 16:43Z. Levers, in order:
- P1, positional constructor calls: turned in; the site-plan lowering carries the rule (P5).
- P3, deferred refcounting through ctypes: dropped by the owner; the research stays in artifacts.
- Lever 1, interning: no gain, dropped.
- Lever 2, thread-affine pools: -6% to -7% per cycle on Linux, effect on Windows unknown, needs a design.
- P4, SpellSpace.meld warm id lane: in the tree at 0.2.68, turned in.
Open owner decisions:
- The SpellSpace active-scope RISK: enforce the check, or correct the documents.
- The system_document_view lazy-index race (RISK in the P4 task): which lane fixes it.
Levers must remove work, and pools and shells are created when they are today (owner, 2026-09-26). Lever 1's
lifecycle is closed as measured (owner, 21:15Z; about 15 contract-bearing pieces, trims worth about 0.1 us). The
spellspace build locks led to the nested slot-guard removal (0.2.73); both turned in. Thread-affine pools need the owner's view under the
rule. Conjure-time hydration is withdrawn (tail task).

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
