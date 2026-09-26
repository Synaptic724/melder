

# Task: Investigate Melder's long-run gauntlet slowdown and possible retained growth

## Metadata
- Task ID: TASK-2026-09-26-investigate-melder-long-run-growth
- Epic: EPIC-2026-09-26-melder-long-run-throughput-truth
- Status: in_progress
- Owner: user
- Agent Name: melder_1
- Priority: p1
- Created: 2026-09-26T00:24:13Z
- Updated: 2026-09-26T00:35:00Z

## Objective
Find out why Melder's gauntlet throughput held from 5k to 50k iterations but fell 12.5% at 100k,
decide from source whether Melder retains memory or per-thread state across short-lived threads,
and add diagnostic tests under benchmarks/testing_other_di that detect the mechanism.

## Ticket Contract
- ENTRY_GATE: Owner direction 2026-09-26 ("go investigate", "add any important tests ... in
  benchmarks/testing_other_di"); active attention-board row routes here.
- EXECUTION_BOUNDARY: Read src/ and benchmarks/. Write new test files under
  benchmarks/testing_other_di/, this ticket, and board/mailbox rows. No src/ edits; any fix needs a
  separate owner-approved ticket.
- DEPENDENCIES: owner-run gauntlet output (5k/50k/100k, recorded in Notes);
  tickets/tasks/completed/2026-09-25_implement_creation_slot_build_guards_task.md (creations.py
  changed 2026-09-25T23:23Z, before the 50k and 100k runs).
- EXIT_GATE: Retained-growth mechanism is FACT or ruled out with source evidence; diagnostic tests
  are added and runnable by the owner; status review.
- FAILURE_ESCALATION: BLOCKER if a claim needs execution and no CPython 3.14 is available (this
  shell has 3.10); DECISION_REQUEST before any src fix; CONFLICT if docs contradict source.

## Scope Boundaries
- In scope: Melder per-thread state, scope pools (lesser conduit, SpellSpace), creation slot
  guards, Creations stores touched per gauntlet cycle; the gauntlet's Melder lane code.
- Out of scope: src/ fixes; changing the shared gauntlet's measurement method; dishka and
  dependency-injector internals.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner directed the investigation and test additions on 2026-09-26.

## Steps / Checklist
- [ ] Record the three gauntlet runs and the questions they raise.
- [ ] Read the gauntlet's Melder lane code to know which Melder paths each cycle exercises.
- [ ] Read Melder per-thread state, scope pooling and slot-guard code on those paths.
- [ ] Decide retained growth: FACT or ruled out, with the growing structure named.
- [ ] Add diagnostic tests under benchmarks/testing_other_di (thread churn vs retained state).
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Source-backed verdict in Notes.
- New diagnostic test file(s) in benchmarks/testing_other_di/.

## Files / Paths Impacted
- benchmarks/testing_other_di/ (new test files only)

## Validation
- Not run.
- Recommended commands:
  - Owner-run with CPython 3.14 free-threaded (-X gil=0), from PyCharm or the repo venv.

## Risks / Rollback Notes
- One run per length; a 12.5% change may include machine noise (hybrid P/E cores, Melder runs last).
- New tests are additive files; rollback is deleting them.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No behavior claim cited only to a document or a one-line search hit.

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
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - Melder retained state under thread churn in the shared gauntlet.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T00:24:13Z
  TYPE: MEASURE
  CLAIM: Owner-run shared gauntlet (free-threaded, 3 threads, same process, order DI/dishka/Melder),
    hot scopes/s at 5k/50k/100k: dependency-injector 37,125/23,519/22,514; dishka
    29,311/22,002/21,799; Melder 23,787/23,200/20,304. Non-library time per iteration (threaded
    phase minus busiest lane's outer_total sum): DI 0.88/1.67/1.87 ms, dishka 1.60/2.18/2.21 ms,
    Melder 1.93/1.88/2.18 ms. Library-only rates moved <=8% between 50k and 100k. Cleanup (ends in
    gc.collect) ~1.9x from 50k to 100k for all three. New at 100k only: Melder outer-scope create
    max 10.9 ms and request-scope create max 7.0 ms (50k: <0.4 ms). One run per length.
  EVIDENCE:
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1186-1285
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1318-1345
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1580-1600
  IMPACT: Melder is the only library that degrades between 50k and 100k; the benchmark starts three
    new threads per iteration (300k over 100k iterations), so per-thread retained state is a lead.
  NEXT: Read the gauntlet's Melder lane (lines 945-1136) to list the Melder paths each cycle uses.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-26T00:24:13Z
  TYPE: ALIGNMENT_CHECK
  CLAIM: Consumed melder_0 notices on lane open. M0-7 (relabel matrix R5d to CONFIRM) and M0-11
    (owner turn-in: contract task and story closed; item 4 = (a), item 5 = (c); R5d probe carried to
    the override lane) need no action here. M0-10 is relevant: slotted door routes now hold
    store.slot_guard(spell_id) across the executor (creations.py modified 2026-09-25T23:23Z), which
    predates the 50k run start (23:46Z per the PyCharm header), so 50k and 100k both ran slot guards.
  EVIDENCE: tickets/tasks/completed/2026-09-25_implement_creation_slot_build_guards_task.md:1-20
  IMPACT: The 50k->100k Melder drop is not explained by the slot-guard change landing between runs;
    the new guards are still in scope as possible per-slot growth.
  NEXT: Include creations.py slot-guard lifecycle in the Melder path read.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7
- DATETIME: 2026-09-26T00:40:00Z
  TYPE: ASSUMPTION_CHALLENGE
  CLAIM: The shared gauntlet does NOT run its in-file Melder lane. _build_ops("melder") imports
    test_melder_gauntlet and calls its _build_runtime_melder (phase_scheduler_workers_per_spellbook=1,
    no configure_aether_frame, request roots bound unique_per_spell_space). The in-file lane
    (workers=3, configure_aether_frame, roots bound many) is dead code for the owner's runs. The cycle
    shape is the same: create_lesser_conduit -> lesser.meld outer x2 -> enter_spellspace/__enter__ ->
    space.meld marker x2 + outer + variant roots -> __exit__ -> lesser.cleanup().
  EVIDENCE:
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1149-1158
  - benchmarks/testing_other_di/test_melder_gauntlet.py:72-305
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:945-1136
  IMPACT: The earlier summary described the in-file lane; read paths and probes must use the
    test_melder_gauntlet builder. Per iteration: 65 cycles over 3 fresh threads (10/25/30).
  NEXT: Read the Melder cycle path in source, starting at Conduit.create_lesser_conduit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-26T01:05:00Z
  TYPE: FACT
  CLAIM: Every per-cycle structure on the gauntlet's Melder path is bounded or symmetric in source.
    (1) Lesser pool: create_object pops the root-owned deque; return appends and destroys the
    overflow above target_idle; root pools are built with baseline_idle=max_idle=20. (2) Ward link
    adds _lesser_conduits[id]; _detach_for_pool pops the same id from the parent and clears the
    parent pointer. (3) Each lesser owns one SpellSpacePool (also 20/20); enter_spellspace pops or
    creates, __exit__ pop_expected()s the thread stack and releases to the pool. (4) Stores reset on
    return (reset_for_pool / reset_for_pool_unlocked clear the live dict); _slot_guards grows only
    per spell id per store and is kept by design. (5) SpellSpaceThreadState keeps one
    threading.local per conduit; per-thread stacks are released by CPython when a thread exits
    (interpreter behaviour, not Melder source; confirmed by the T2 30k-thread measurement).
  EVIDENCE:
  - src/melder/aether/conduit/conduit_pool.py:106-161
  - src/melder/aether/conduit/conduit.py:347-360
  - src/melder/aether/conduit/conduit.py:566-705
  - src/melder/aether/conduit/conduit.py:1201-1234
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:381-422
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1175-1214
  - src/melder/aether/conduit/spell_space/spell_space.py:233-364
  - src/melder/aether/conduit/spell_space/spell_space_pool.py:184-288
  - src/melder/aether/conduit/creations/creations.py:124-181
  - src/melder/aether/conduit/creations/creations.py:356-406
  - src/melder/aether/conduit/creations/creations.py:1009-1106
  - src/melder/aether/conduit/spell_space/spell_space_thread_state.py:10-302
  IMPACT: Retained growth per cycle or per thread is ruled out in source for this lane, matching
    the T2 measurement (flat objects and allocator blocks over 650k cycles and 30k threads). The
    100k drop has to come from outside Melder's retained state.
  NEXT: Wait for T2's full-harness per-window run, then write the diagnostic tests around the
    verdict (bounded growth under churn, per-window throughput).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Opened 2026-09-26T00:24:13Z on owner direction. Resume from the latest Notes NEXT. Validation: Not run.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
