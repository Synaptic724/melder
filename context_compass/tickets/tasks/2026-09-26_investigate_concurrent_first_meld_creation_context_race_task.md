

# Task: Investigate the concurrent first-meld "Cannot build CreationContext" flake

## Metadata
- Task ID: TASK-2026-09-26-investigate-concurrent-first-meld-creation-context-race
- Story: none (RISK recorded in TASK-2026-09-26-align-annotation-shape-guard-with-phase1-caller-inputs)
- Status: in_progress
- Owner: user
- Agent Name: melder_1
- Priority: p1
- Created: 2026-09-26T12:29:46Z
- Updated: 2026-09-26T12:36:50Z

## Objective
tests/integration/melder/conduit/test_conduit_integration_concurrency.py fails intermittently on unmodified
source with RuntimeError "Cannot build CreationContext before spell_codegen_creation exists. Run analyzer ->
processor -> planner -> codegen creation first." (5 of 6 file runs in a 2-core VM, several tests). Earlier
lanes saw only the cluster test fail occasionally. Establish from source the exact race (which threads, which
state, which ordering), whether it is a production defect or a test artifact, and propose a fix.

## Ticket Contract
- ENTRY_GATE: Owner direction 2026-09-26 ("concurrency flake sure lets look into that next go ahead and
  investigate it").
- EXECUTION_BOUNDARY: Investigation reads src/ and tests, runs probes and repeated test runs on VM copies. No
  src edits before owner confirmation of a DECISION_REQUEST.
- DEPENDENCIES: Meld / CreationContext / codegen-creation publication, conduit contract and cluster paths,
  per-slot build guards (2026-09-25).
- EXIT_GATE: Root cause evidenced with a reproduction; fix proposal approved; implementation with a
  deterministic regression; suites green.
- FAILURE_ESCALATION: DECISION_REQUEST for the fix; BLOCKER if the race cannot be reproduced reliably enough to
  prove a fix.

## Scope Boundaries
- In scope: the CreationContext / spell_codegen_creation publication path under concurrent first melds.
- Out of scope: unrelated flakes; the paused class-annotation lane; the guard lane (in review).

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner directed the investigation (2026-09-26T12:29:46Z).

## Steps / Checklist
- [x] Measure failure rates per test and read the failing tests.
- [x] Read the raising code and every writer of the state it checks.
- [x] Reproduce deterministically (probe or instrumented run) and name the race.
- [x] Propose the fix (DECISION_REQUEST).
- [ ] Implement with a deterministic regression after approval; validate; docs.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Evidence and probes under artifacts/creation_context_race_20260926/; root cause; a fix proposal.

## Files / Paths Impacted
- UNKNOWN until the root cause is established.

## Validation
- Not run.

## Risks / Rollback Notes
- Concurrency fixes can move the race rather than remove it; the regression must force the interleaving.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No behavior claim cited only to a document or a one-line search hit.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/creation_context_race_20260926/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: ticket closure

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - Concurrent first melds and codegen-creation publication.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.

## Notes
- DATETIME: 2026-09-26T12:34:28Z
  TYPE: MEASURE
  CLAIM: Rate on the VM copy (2-core, 3.14.7t, -X gil=0), 40 separate runs of the concurrency file: 7 runs
    failed, 9 failures - cluster_unique_per_conduit_cluster_shared_instance 4, unique_across_multiple_borrowers
    2, many_across_borrowers 2, across_linked_conduits_isolated_per_conduit 1 - all with RuntimeError
    "Cannot build CreationContext before spell_codegen_creation exists". Every failing test melds one spell
    from several conduits (owner + borrowers, linked conduits, clusters) at once.
  EVIDENCE:
  - context_compass/artifacts/creation_context_race_20260926/results/file_runs_40.txt:1-49
  - tests/integration/melder/conduit/test_conduit_integration_concurrency.py:1188-1274
  IMPACT: The race is not confined to the one test an earlier lane skipped; it reaches every cross-conduit
    first-meld test in the file.
  NEXT: Read the raising builder, the factory and the Phase-5 writers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T12:34:28Z
  TYPE: FACT
  CLAIM: Root cause was already proven on 2026-09-05 (epic shared_context_rebuild_publication, closed
    cancelled_deferred) and still matches current source. A spell's CreationContext and compiled codegen are
    SPELL-owned, shared by every conduit. A conduit whose resolution for the spell is unknown/gated (a
    borrower's first meld after a contract) reruns phases 5-11 under spell._lock
    (Meld._ensure_resolution_resolvable); Phase 5 calls artifact._cleanup_codegen_outputs() and
    spell._cleanup_creation_context() (context None, CounterSwitch reset to 0) at four sites, and Phase 11
    republishes codegen later. A conduit whose resolution is already valid returns before that lock and
    CreationContextFactory.get_or_build_for_spell elects a builder from state 0 without the spell lock;
    CreationContextBuilder.build then raises because _spell_codegen_creation is None. The 2026-09-05 lane
    reproduced it with debugger-controlled pauses (no object cleaned). Owner then rejected the broad repair
    (gate freeze/drain rebuild, CreationContextRebuild - left in src, never wired), skipped the original
    two-cluster test and the deterministic component reproduction, and deferred the repair.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:991-1049
  - src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:293-339
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:103-146
  - src/melder/aether/spellbook/spell.py:686-714
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:185-217
  - tickets/tasks/completed/2026-09-05_shared_context_rebuild_race_task.md:255-420
  - tests/component/melder/aether/conduit/test_shared_context_rebuild_publication.py:60-80
  IMPACT: No new root-cause hunt is needed; the open question is a fix the owner accepts, given the earlier
    rejection (owner protects the warm fast path and wanted proof before code). The skipped component test is
    a ready deterministic regression.
  NEXT: Read the four Phase-5 clear sites and the dependency-closure handling to scope a narrow fix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-26T12:36:50Z
  TYPE: MEASURE
  CLAIM: Sequential probe (no threads, cold cache, 3.14.7t): owner + 2 borrowers sharing one Existence.many
    spell by contract, set up exactly like the concurrency tests. The owner's first meld builds the context
    from the conjure plan. Each borrower's FIRST meld runs Phase5.run_local for that borrower's conduit, which
    discards the shared SpellCodegenCreation and CreationContext (new object ids after every borrower) and
    rebuilds them; the rebuilt no-overrides executor signature is identical to the one it replaced
    (e3d84d965e6266c0 in all three). Second melds rebuild nothing. With a warm cache the owner hydrates a
    context without any codegen object (cache runs must be cleared for this probe). Also read: the local rerun
    holds spell._lock across phases 5-11 (Meld._ensure_resolution_resolvable), while a conduit already valid
    for the spell never takes that lock before get_or_build_for_spell.
  EVIDENCE:
  - context_compass/artifacts/creation_context_race_20260926/results/borrower_rebuild_trace.txt:1-12
  - context_compass/artifacts/creation_context_race_20260926/probes/probe_borrower_rebuild.py:1-97
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:617-713
  - src/melder/aether/conduit/meld/meld.py:1020-1049
  IMPACT: In these tests the destructive window exists only to rebuild an identical plan for a new
    conduit's validity record; every concurrent meld from an already-valid conduit can fall into it.
  NEXT: Record fix options (DECISION_REQUEST) and discuss with the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-26T12:36:50Z
  TYPE: DECISION_REQUEST
  CLAIM: Fix options (no code yet). (1) Cold-path wait: when get_or_build_for_spell elects a builder
    (switch 0, the rare path) and the compiled plan is absent, take spell._lock - held by the rebuilding
    conduit across 5-11 - and build after it; the warm path (switch >= 2) is untouched. Needs pending
    followers woken by a mid-election reset to re-elect instead of raising, and does not address a reader
    already executing an old context that Phase 5 cleans. (2) Skip the no-op teardown: when a conduit's local
    Phase 5 produces the same root blueprint as the spell's current plan and the plan is present, record the
    conduit's validity and keep the published plan/context (no clear, no 8-11). Removes the window and the
    wasted rebuild for the common "new conduit validates an unchanged spell" case; a genuine change still
    rebuilds. (3) Build-then-swap publication with reader draining - the broad design the owner rejected on
    2026-09-05. Recommendation: (2) as the main fix plus (1) as the safety net for genuine changes; the
    skipped deterministic component test and the skipped two-cluster test become the regressions.
  EVIDENCE:
  - context_compass/artifacts/creation_context_race_20260926/results/borrower_rebuild_trace.txt:1-12
  - src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:293-339
  - tickets/tasks/completed/2026-09-05_shared_context_rebuild_race_task.md:369-386
  IMPACT: Implementation waits for the owner; (2) needs a blueprint-equality check verified against Phase 8's
    existing fingerprint skips before it is designed in detail.
  NEXT: Explain the findings and options to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T12:41:08Z
  TYPE: ALIGNMENT_CHECK
  CLAIM: Owner constraint on the DECISION_REQUEST: "revalidation happens because spells can change over time,
    thats the point". Revalidation must keep running and keep its effect; option (2) (skip the teardown when
    the plan is unchanged) is withdrawn as the main fix because it adds a second path deciding whether a
    revalidation's result counts. Remaining direction: leave revalidation untouched and make readers safe
    during it - a meld that finds the context gone and the plan absent waits for the in-flight rebuild (which
    holds spell._lock across phases 5-11) and builds from the fresh plan, instead of raising. Open, not yet
    evidenced: a reader already executing the old context while Phase 5 cleans it (not observed in 40 runs).
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:1020-1049
  - src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:293-339
  IMPACT: Fix scope narrows to the reader/cold path; the warm path and revalidation are unchanged.
  NEXT: Confirm the direction with the owner, then design the cold-path wait against CounterSwitch's
    pending/reset behaviour before any code.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T12:42:29Z
  TYPE: DECISION
  CLAIM: Owner approves the reader-side direction instead of the September design ("I'm ok with this, we can
    do this instead its fine"): revalidation unchanged; a meld that finds the context gone and the plan absent
    waits for the in-flight rebuild and builds from the fresh plan. Owner asked why the September repair was
    rejected, recalling performance. The record does not state the reason: the rejection note (2026-09-05
    22:17Z) says only that the owner rejected and rolled back the broad repair and returned to discovery. The
    recorded constraints are consistent with a performance concern - "Preserve automatic-mode warm doors and
    lock-free ready reads", "No blanket Spell lock", "Stop before adding unsupported fast-path locking",
    "Keep steady-state performance protected by measurements" - and that design moved the dynamic index
    admission ahead of context acquisition, i.e. onto every dynamic meld.
  EVIDENCE:
  - tickets/epics/completed/2026-09-05_shared_context_rebuild_publication_epic.md:505-520
  - tickets/epics/completed/2026-09-05_shared_context_rebuild_publication_epic.md:455-473
  - tickets/epics/completed/2026-09-05_shared_context_rebuild_publication_epic.md:160-175
  - tickets/tasks/completed/2026-09-05_shared_context_protocol_repair_task.md:150-158
  IMPACT: Design must keep the ready path lock-free and ticket-free; the wait lives only on the cold build path.
  NEXT: Design the cold-path wait against CounterSwitch pending/reset semantics and check the old-context
    reader hazard, then present the exact change.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T12:56:07Z
  TYPE: FACT
  CLAIM: Cold-path design facts, read in full. (a) Spell._get_or_build_creation_context has promised a cold-path
    spell RLock since 0.2.0 but never took it (working tree == HEAD apart from CRLF). (b) Every reset relevant to
    the flake happens while the meld thread holds spell._lock: the local 5-11 rerun and the deferred 8-11 run
    execute on PhaseScheduler workers while the meld thread holds the lock and waits; ownership restamps
    (_add_owned_conduit, _add_build_details, invalidate_spell) reset under the lock themselves. The Phase-11
    facade republishes codegen and then resets the context again, so a finished rebuild leaves codegen present,
    context None, switch 0; contexts are built only at the four meld doors. (c) The leader in
    get_or_build_for_spell never releases its claim if the build raises: the switch stays at 1 and later callers
    wait on the event with no timeout until some reset. (d) A warm door can read fast_state 2 and then the slot
    after _cleanup_creation_context set it to None ("Spell returned no live CreationContext"), or read the old
    context while it is being cleaned (cleanup deletes the three executor slots). (e) Lock order: cache staging
    after publish takes spellbook._lock (_get_or_create_caching_system), and _add_hooks_to_spell holds
    spellbook._lock while _set_hooks takes spell._lock on a live spell, so staging must NOT run under
    spell._lock. (f) Resets outside the spell lock remain: frame-wide Phase 5 at conjure, notch outgoing,
    cleanup/transfer teardown, explicit dirty-root revalidation (no caller in src/); load_cached(publish=True) is
    conjure-time only.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:777-818
  - src/melder/aether/spellbook/spell.py:686-714
  - src/melder/aether/spellbook/spell.py:638-685
  - src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:294-339
  - src/melder/utilities/synchronization/counter_switch.py:255-342
  - src/melder/aether/conduit/meld/meld.py:818-863
  - src/melder/aether/conduit/meld/meld.py:991-1049
  - src/melder/aether/spellbook/spellbook_creation_system.py:1968-2010
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_system.py:414-438
  - src/melder/aether/spellbook/spellbook.py:908-945
  - src/melder/aether/spellbook/spellbook.py:5536-5584
  - src/melder/aether/conduit/meld/conduit_meld.py:487-556
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:170-188
  IMPACT: The lock closes the observed race only if build and publish run under spell._lock, cache staging runs
    after the lock is released, a failed leader releases its claim, and a warm read that finds None falls
    into the cold path instead of raising. The in-flight old-context hazard is not closed by this and stays
    UNKNOWN until probed.
  NEXT: Prototype the change on the VM copy, unskip the two September regressions, probe the in-flight hazard,
    run the 40-run loop.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-26T13:03:32Z
  TYPE: MEASURE
  CLAIM: VM prototype (3.14.7t, -X gil=0) of the reader-side fix, applied by scripts/apply_fix.py (factory cold path
    under spell._lock with a recheck, build+publish+open inside, cache staging after release, no selector election;
    Spell and the four meld doors send an open-switch/empty-slot read to the cold path). Tests applied by
    scripts/apply_tests.py: both September regressions unskipped (the component one now also observes the reader
    entering the cold path, its new waiting point), one component test for the open-switch/empty-slot instant, five
    factory tests (lock-before-build, queued caller returns the published context, open switch with empty slot,
    failed build leaves nothing published, staging outside the lock), one Spell test, and the leader test's expected
    advance changed from [1] to [2]. Result: 138 passed with a cold and with a warm creation cache; the same 9 new or
    changed tests fail on unpatched source (September regression fails with the exact flake error). Finding along the
    way: a full cache hit publishes a context with no phase-11 plan behind it, so a slot emptied without a rerun
    cannot be rebuilt; in real flows every reset is followed by a rerun that recompiles, and the new component test
    lets the peer's first meld do that rerun.
  EVIDENCE:
  - context_compass/artifacts/creation_context_race_20260926/scripts/apply_fix.py:1-282
  - context_compass/artifacts/creation_context_race_20260926/scripts/apply_tests.py:1-361
  - tests/component/melder/aether/conduit/test_shared_context_rebuild_publication.py:60-162
  IMPACT: The deterministic reproduction is closed by the reader-side change; no revalidation behaviour changed.
  NEXT: Run the concurrency file 40 times plus the unskipped two-cluster test on the patched VM copy, then the
    broader suites, then probe the in-flight old-context hazard.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T13:10:12Z
  TYPE: MEASURE
  CLAIM: 40 runs of the concurrency file (19 tests incl. the unskipped two-cluster test) on the patched VM copy: 6
    failing runs (baseline 7/40), 2 cluster_shared, 3 many_across_borrowers, 1 unique_across_borrowers; the
    two-cluster test never failed. "Cannot build CreationContext" is gone. Every remaining failure (9 of 9 sampled)
    is AttributeError "'CreationContext' object has no attribute '_dynamic_environment'": a meld read the published
    context on the lock-free path, then the peer's Phase-5 reset called cleanup() on that same object (deletes its
    slots) while the meld was still using it. The lock cannot cover this because warm readers never take it.
    Phase 5 also calls SpellCodegenCreation.cleanup() (deletes its executor references and clears metadata), which
    an in-flight first execution may depend on (executors hydrate on first run and hot-swap context slots; whether
    that path reads codegen metadata is UNKNOWN).
  EVIDENCE:
  - context_compass/artifacts/creation_context_race_20260926/results/file_runs_40_after_lock.txt:1-46
  - context_compass/artifacts/creation_context_race_20260926/results/errors_after_lock.txt:1-9
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:170-188
  - src/melder/aether/spellbook/spell.py:686-714
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:365-395
  - src/melder/aether/conduit/meld/conduit_meld.py:494-514
  IMPACT: The lock fixes the builder race (deterministic regression green) but not the flake rate: a second race,
    tearing down a context lock-free readers still hold, was co-present and now dominates. Closing it needs either
    reader tracking (the September design, rejected for cost on every meld) or revalidation releasing the superseded
    context/plan instead of destroying it while readers may hold it.
  NEXT: Prototype "release, do not destroy, on revalidation resets" on the VM copy and rerun the 40-run loop, then
    bring the owner the evidence and the cleanup-posture question.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-26T13:12:13Z
  TYPE: DECISION_REQUEST
  CLAIM: Probe V1 on the VM copy (spell-lock cold path plus Spell._cleanup_creation_context releasing the reference
    instead of calling cleanup() on the old context): 40 of 40 runs green (baseline 7/40 failing, lock alone 6/40).
    At a 15% per-run failure rate, 40 clean runs by chance is about 0.15%. Codegen cleanup was left as is: in-flight
    executors hold their own function objects, and the only live artifact read found in hydration is many_only
    override hydration reading the Phase-5 root blueprint, not codegen metadata. Proposed change for the owner:
    (1) keep the spell-lock cold path; (2) resets release the superseded CreationContext and only terminal
    Spell.cleanup destroys it, because any reset can race a lock-free reader. Warm path unchanged, revalidation
    unchanged (the old context is never served again: slot and switch are reset). This departs from the profile
    rule "we cleanup everything; do not leave it to the GC" for one object type: the context holds only references,
    and the rule's own premise (not used after cleanup) is false here. The alternative that keeps eager destruction
    is reader tracking on every meld (September design, rejected for cost).
  EVIDENCE:
  - context_compass/artifacts/creation_context_race_20260926/results/file_runs_40_lock_plus_release_probe.txt:1-40
  - context_compass/artifacts/creation_context_race_20260926/results/file_runs_40_after_lock.txt:1-46
  - src/melder/aether/spellbook/spell.py:686-714
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:170-188
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/hydration/many_only_hydrator.py:374-388
  IMPACT: Implementation waits for the owner. RISK noted, not observed: an old plan's first override execution that
    overlaps a rerun reads the new Phase-5 path registry.
  NEXT: Explain the two-race finding and the proposal to the owner; implement on approval.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-26T13:17:29Z
  TYPE: CONFLICT
  CLAIM: Correction to the 12:42:29Z DECISION: that note misread the owner. "I'm ok with this, we can do this
    instead" approved the September plan (freeze the affected index gates, drain admitted readers, rebuild,
    publish, reopen), not melder_1's reader-side direction. Everything built since (spell-lock cold path, release
    probe) was built on the misread. Facts on the September plan, read in full: it was an approved attempt that
    the owner rolled back about an hour later, mid-implementation; no working code, fix results or performance
    numbers exist. What remains is the unwired CreationContextRebuild (144 lines) plus archived patch contracts.
    It moves the existing dynamic index-gate ticket ahead of context acquisition rather than adding a second
    one; the earlier claim that it put admission "onto every dynamic meld" overstated it, since dynamic melds
    already take that ticket during execution. Freeze plus drain covers both races found today.
  EVIDENCE:
  - tickets/epics/completed/2026-09-05_shared_context_rebuild_publication_epic.md:453-520
  - tickets/tasks/completed/2026-09-05_shared_context_protocol_repair_task.md:106-160
  - src/melder/aether/conduit/meld/creation_context/creation_context_rebuild.py:1-144
  IMPACT: Direction reopens: the owner chooses between finishing the September design and the measured
    lock-plus-release change. No device source was changed under the misread.
  NEXT: Explain plainly and take the owner's choice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-26T13:18:51Z
  TYPE: DECISION
  CLAIM: Owner: "yeah run with the september plan", with the constraint that several agents share the worktree, so
    nothing is unwound: fix forward with anchored edits, never revert or restore files. Direction: finish the
    September freeze/drain design (producer closes the affected spell-index gates, drains admitted melds, rebuilds,
    publishes, reopens; the dynamic ticket is taken before context acquisition). The lock-plus-release prototype
    (scripts/apply_fix.py, scripts/apply_tests.py) is superseded and kept only as evidence; its unskip and
    open-switch/empty-slot tests may be reused where they still hold. Work happens on the VM copy first; device
    source changes wait for patch docs, measurements and the owner's confirmation of the exact change. All
    target files were clean in the worktree at this time (no uncommitted edits by any agent).
  EVIDENCE:
  - tickets/epics/completed/2026-09-05_shared_context_rebuild_publication_epic.md:453-520
  - src/melder/aether/conduit/meld/creation_context/creation_context_rebuild.py:1-144
  IMPACT: Next reads are the archived September patch contracts and the CreationGate ticket/drain mechanics.
  NEXT: Read system_docs/patches/completed/shared_context_rebuild_2026_09_05/ in patch order.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Opened 2026-09-26T12:29:46Z on owner direction. Investigation first; no src edits until the owner approves a plan.
Resume from the latest Notes NEXT.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
