

# Task: Reproduce the real-world gauntlet and attribute Melder's per-scope-cycle cost

## Metadata
- Task ID: TASK-2026-09-26-measure-gauntlet-scope-cycle-costs
- Story: STORY-2026-09-26-gauntlet-runtime-speed
- Status: ready
- Owner: user
- Agent Name: melder_2
- Priority: p1
- Created: 2026-09-26T15:43:24Z
- Updated: 2026-09-26T15:43:24Z

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
- from_state: draft
- to_state: ready
- transition_reason: Ticket written from the owner's 2026-09-26 request; measurement starts once D1-D3 are
  answered.

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

## Context / Handoff Summary
Opened 2026-09-26 on the owner's request to run the benchmarks and speed up the library. Baseline filed (owner
runs, same-run ratios); no runs by melder_2 yet. Waiting on D1-D3; next is the 3.14t VM copy and a reduced-
iteration smoke run, then the harness read and the per-cycle attribution.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
