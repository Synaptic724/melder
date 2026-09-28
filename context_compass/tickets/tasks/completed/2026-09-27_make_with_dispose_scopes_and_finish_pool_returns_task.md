

# Task: Make `with` a dispose scope and finish every scope exit and pool return

## Metadata
- Task ID: TASK-2026-09-27-make-with-dispose-scopes-and-finish-pool-returns
- Story: none
- Status: done
- Owner: user
- Agent Name: melder_0
- Priority: p1
- Created: 2026-09-27T21:34:16Z
- Updated: 2026-09-28T00:20:38Z
- Completed: 2026-09-28T00:20:38Z
- Closure Basis: owner turn-in in chat (2026-09-28): "ok cool yeah fix the problem you have yourself and
  send it, finish off your fixes and turn in the remaining things please go ahead".
- Summary: `with conduit:` disposes (Breaking), `Conduit.enter_lesser_conduit()`, every scope exit finishes and then
  raises its disposal failures, children-first pool return, idempotent soft cleanup, a SpellSpace lease flag
  (released spaces refuse meld and purge), `using_cleanup()` propagates; no hot-path cost. Notched 0.2.8203;
  release note section "`with` releases a Conduit, and every scope exit finishes its cleanup".

## Objective
Build the package the owner approved from the scope-exit investigation (question card, 2026-09-27):
1. `with conduit:` disposes like a .NET `using`: at block exit a lesser returns to its pool and a root is torn
   down. `Conduit.enter_lesser_conduit(name=None)` makes a lesser for use in `with` (plain, no per-thread stack).
2. Every exit finishes its cleanup when a disposal method fails, then raises every failure as one group:
   SpellSpaces reset and go back to their pool, lessers finish their pool return, permanent teardown raises after
   finishing instead of only logging.
3. Lesser pool return disposes descendants first, then its Spaces, then its own store.
4. Soft cleanup of a scope that is already pooled or released is a no-op (no double pooling).
5. A released SpellSpace refuses meld and purge (one flag); an owner cleaned inside its own managed Space no longer
   makes the block exit raise.
6. `Cleanable.using_cleanup()` stops swallowing cleanup errors.
7. The SpellSpace documents stop promising reset, version and active-scope checks the source never had.
Hot paths are benchmarked before and after on 3.14t (owner constraint).

## Ticket Contract
- ENTRY_GATE: owner decisions recorded in the investigation ticket; this board row; patch docs written, linked and
  mapped in Notes before any src edit (lifecycle and error-contract change).
- EXECUTION_BOUNDARY: src/melder/aether/conduit/conduit.py (context manager, cleanup and pool-return paths, lesser
  creation), src/melder/aether/conduit/spell_space/, conduit_ward pool cleanup, conduit_pool.py,
  src/melder/aether/conduit/meld/spellspace_meld.py, src/melder/utilities/general_base/cleanable.py, the frame
  teardown in aetheric_frame.py, and any direct caller the reading shows must change; their tests; src and tests
  system documents, indexes and graph descriptors; the release note; `__version__`; assets and bundles last.
- DEPENDENCIES:
  - tickets/tasks/2026-09-27_investigate_scope_exit_and_pool_return_cleanup_task.md (findings, probes, decisions).
- EXIT_GATE: new tests red before the change and green after; conduit, SpellSpace, creations and cleanable suites
  and the whole tree green on 3.14t, affected subsets with the GIL on and on the GIL build; benchmarks before and
  after with no hot-path regression beyond noise; docs, indexes and graph current; notch and a Breaking release-note
  entry; NOTICEs; asset and bundle checks OK; owner acceptance.
- FAILURE_ESCALATION: DECISION_REQUEST for a contract choice outside the recorded decisions or a measured hot-path
  regression; BLOCKER when a path cannot be exercised.

## Scope Boundaries
- In scope: the seven items of the Objective, their tests, docs and benchmarks.
- Out of scope: disposal order (fixed at bind); purge authority; `with` on Spellbook, Aether, AethericFrame,
  ConduitWard and SpellIndex (they stay lock contexts); the 33 test copies of `_CoordinatedLock`.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner approved the package (question card, 2026-09-27): `with conduit:` disposes,
  enter_lesser_conduit plain, using_cleanup raises; the rest was settled earlier in the investigation ticket.
- from_state: in_progress
- to_state: blocked
- transition_reason: Built and validated on the VM copy; the released-space flag measures about 20 ns per managed
  space cycle on 3.14t (same-process A/B), a hot-path cost beyond noise, so the owner decides before the device
  landing (DECISION_REQUEST note, 2026-09-27T22:33:48Z).
- from_state: blocked
- to_state: in_progress
- transition_reason: Owner kept the refusal on condition that SpellSpace use gets no more expensive; the offsets
  measured at or below the old cost (2026-09-27T22:54:34Z MEASURE note).
- from_state: in_progress
- to_state: review
- transition_reason: Landed at 0.2.8203 with docs, graph, release note, assets and bundles; final suites green on
  three interpreters (MEASURE note of this datetime). Owner acceptance is the remaining exit-gate item.
- from_state: review
- to_state: done
- transition_reason: Owner turn-in in chat (2026-09-28); patch lane archived to completed, artifacts retained.

## Steps / Checklist
- [x] Re-read every path whole at today's line numbers: Conduit context manager, cleanup, pool return, lesser
      creation and enter_spellspace; SpellSpace, its pool and thread state; ward pool cleanup; ConduitPool;
      SpellSpaceMeld meld/purge; Cleanable; the frame teardown.
- [x] Patch docs (architecture, component, code description); linked; patch-to-implementation mapping note.
- [x] Red tests for every behaviour change, run red on the current tree.
- [x] Baseline benchmarks on 3.14t (gauntlet per-step: space enter/meld/exit, lesser create/cleanup, warm melds).
- [x] NOTICE the active agents, implement, then red tests green, suites, whole tree.
- [x] Benchmarks after, same harness and machine.
- [x] Docs, indexes, graph descriptors; release note (Breaking change); notch.
- [x] Asset and LLM-bundle rebuild last; both checks OK.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- The behaviour package, its tests, before/after benchmarks, docs, release note and notch.

## Files / Paths Impacted
- src: conduit.py, conduit_ward.py, spell_space.py, spell_space_pool.py, spell_space_thread_state.py,
  spellspace_meld.py (docstrings), aetheric_frame.py, cleanable.py, __version__.py (0.2.8203).
- tests: 3 new (component scope exit, component SpellSpace lease, unit cleanup contexts); rewritten tests in
  test_conduit_lifecycle.py, test_conduit_integration_public_api.py, test_conduit_integration_disposal_failures.py
  and the named-lesser retry test.
- docs: src_architecture, src_components, tests_components (+ indexes), graph descriptors and src_graph, the
  running release note; build assets and LLM bundles regenerated.

## Validation
- Red before / green after: 31 new tests red on the old tree (4 guards green), 37 new and rewritten green after
  (artifacts red_before_change_gil0.txt, green_resynced_gil0.txt).
- Whole tree green on the re-synced VM copy, 3.14.7t GIL off (PyYAML collection error = environment); conduit,
  cleanable, multithreading and aether-integration subsets green with the GIL on and on the GIL build
  (suites_post_change_vm.txt).
- Final at 0.2.8203: version/asset/system-document set 288 passed, 1 skipped; lane suites 2207 passed; GIL 0,
  GIL 1 and the GIL build (suites_final_08203_vm.txt). Asset --check OK; LLM --check OK with --include-untracked.
- Benchmarks: same-process A/B at or below the old cost on every measured fast path (ab_*_resynced*.txt).
- Coverage: Not run.

## Risks / Rollback Notes
- Breaking: code using `with conduit:` as a lock now disposes the scope (no in-repo user besides two tests).
- Teardown paths that only logged will raise after finishing; the frame teardown that swallows conduit errors with
  a bare `pass` must log instead.
- New checks on hot paths (released flag in meld, idempotence in soft cleanup) are measured, not assumed free.
- Rollback is a revert of one change set.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without acceptance confirmation and board-sync completion.
- [x] No behaviour claim cited to a search hit; every range covers the logic that was read.
- [x] No hot-path change landed without before/after numbers.

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
  - system_docs/patches/completed/scope_exit_dispose_2026_09_27/
  - artifacts/scope_exit_dispose_20260927/
- DISPOSITION: promote_to_documentation (patch lane); retain_as_reference (tests, benchmarks, apply scripts)
- CLEANUP_TRIGGER: task closure

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
- DATETIME: 2026-09-27T21:34:16Z
  TYPE: DECISION
  CLAIM: Lane opened on the owner's approval of the package (question card, 2026-09-27). Decisions carried from
    the investigation: `with conduit:` disposes; enter_lesser_conduit plain; using_cleanup raises; finish-then-raise
    on every exit with lessers re-pooled; children before parents; idempotent soft cleanup; released-space refusal
    by one flag; Python's exception chaining when block and cleanup both fail; SpellSpace docs corrected;
    benchmarks before and after. One notch above 0.2.82 at landing, release note entry led by Breaking change.
  EVIDENCE: context_compass/tickets/tasks/2026-09-27_investigate_scope_exit_and_pool_return_cleanup_task.md:245-420
  IMPACT: Scope and contract choices are fixed; this task builds, measures and documents them.
  NEXT: Re-read the exit and pool-return code whole at today's line numbers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T21:41:29Z
  TYPE: FACT
  CLAIM: Re-read whole at today's line numbers; the investigation's map still holds. Conduit: `cleanup()` never
    checks for the pooled state (a second soft cleanup re-pools); `_prepare_for_pool` disposes Spaces, then its
    own store, then children (named or unnamed detach), then re-pools; `_cleanup_spellspaces_for_pool`,
    `_cleanup_spellspaces` and both permanent paths log every failure; `__enter__`/`__exit__` are the bare lock.
    SpellSpace: managed exit and manual cleanup skip hook reset and pool release when disposal raises; `meld` (warm
    id lane first) and `purge` have no lease check; the pool sets no lease state on acquire or release; prewarm
    releases through the pool directly. Creations swaps its maps empty before any disposal method runs. New: the
    async `using_cleanup` twin swallows the same way; SpellSpaceScopeError (a RuntimeError) already documents "used
    after it has been closed", so it is the error for a released space; a pooled lesser handle still melds into
    its idle shell (the P3 leak class) through Conduit.meld, the hottest door, and stays out of scope; an elastic
    pool's release after its own cleanup appends to the retired deque though its docstring says it destroys.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:566-705
  - src/melder/aether/conduit/conduit.py:722-985
  - src/melder/aether/conduit/conduit.py:1074-1117
  - src/melder/aether/conduit/conduit.py:1201-1285
  - src/melder/aether/conduit/conduit.py:1561-1616
  - src/melder/aether/conduit/conduit.py:2539-2792
  - src/melder/aether/conduit/spell_space/spell_space.py:213-411
  - src/melder/aether/conduit/spell_space/spell_space.py:455-647
  - src/melder/aether/conduit/spell_space/spell_space_pool.py:118-288
  - src/melder/aether/conduit/spell_space/spell_space_thread_state.py:219-289
  - src/melder/aether/conduit/conduit_pool.py:106-161
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:251-462
  - src/melder/aether/conduit/creations/creations.py:1073-1168
  - src/melder/utilities/general_base/cleanable.py:187-420
  - src/melder/aether/aetheric_frame/aetheric_frame.py:274-337
  - src/melder/utilities/general_base/abstract_elastic_pool.py:192-345
  - src/melder/utilities/custom_exceptions/spell_space_scope_error.py:5-17
  IMPACT: The design needs no new mechanism beyond one lease flag on SpellSpace; every other change reorders or
    finishes existing steps. The pooled-lesser handle and the retired-pool release are flagged, not changed.
  NEXT: Record the PLAN (per-item design, files and symbols, tests, benchmarks).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T21:43:14Z
  TYPE: PLAN
  CLAIM: Design, files and symbols. conduit.py - `__enter__` returns self (no lock), `__exit__` calls cleanup()
    and never suppresses (annotations fixed to Optional[Type[...]]); new `enter_lesser_conduit(logger=None, *,
    name=None)` returns create_lesser_conduit(...); `cleanup()` makes soft cleanup of a pooled lesser a no-op;
    `_prepare_for_pool` runs children, Spaces, own store, then named retirement or detach, hooks, pool, and raises
    one ExceptionGroup of collected disposal failures last (a child still attached after failing keeps the retry
    rule; a retirement failure raises together with any collected failures); `_cleanup_spellspaces_for_pool`,
    `_cleanup_spellspaces`, `_cleanup_lesser_conduit` and `_cleanup_normal_conduit` collect disposal failures
    (infrastructure errors stay logged) and `_permanent_cleanup` raises them after the logger and deletes.
    conduit_ward.py - `_cleanup_children_for_pool(finished_failures=None)` keeps a finished child's failure (the
    child is no longer in the map) and raises only for children still attached; `cleanup()` raises its children's
    permanent-cleanup failures after finishing. spell_space.py - a `_released` lease flag (a documented tombstone,
    True once released or destroyed); `__exit__` of a released or destroyed space discards itself from the stack
    top and returns; recycle, manual cleanup and destroy finish hook reset, registry discard and pool release in
    `finally`; `meld` and `purge` refuse a released space with SpellSpaceScopeError (RuntimeError after destroy).
    spell_space_pool.py - release sets the flag, acquire paths clear it. spell_space_thread_state.py - a
    `discard_expected` helper. cleanable.py - both cleanup contexts stop swallowing. aetheric_frame.py - the
    bare `pass` logs through the Aether logger. Docs: SpellSpace, pool and SpellSpaceMeld docstrings; src
    architecture and components plus indexes; graph for conduit.py; release note led by Breaking change; 0.2.8201.
    Tests: component files for conduit exit and SpellSpace release, unit for the cleanup contexts; the two lock
    tests and the 0.2.80 no-raise test are rewritten. Benchmarks: melder_2's per-step probe, A/B on 3.14t.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-09-27_make_with_dispose_scopes_and_finish_pool_returns_task.md:145-180
  - src/melder/aether/conduit/conduit.py:566-705
  - src/melder/aether/conduit/spell_space/spell_space.py:213-411
  - context_compass/artifacts/gauntlet_runtime_speed_20260926/probes/probe_steps.py:1-44
  IMPACT: One lease flag and one bool per hot call are the only new per-cycle work; everything else reorders or
    finishes existing steps. Deleting the lock-context behaviour of `with conduit:` is the Breaking change.
  NEXT: Write the patch docs under system_docs/patches/active/scope_exit_dispose_2026_09_27/.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T21:45:02Z
  TYPE: PLAN
  CLAIM: Patch docs written and linked (read order: architecture, three component patches, code description).
    Mapping - patch section -> implementation -> validation:
    architecture "Interface deltas" (Breaking `with`) -> Conduit.__enter__/__exit__ -> component test exit
    disposes lesser and root, block error kept; rewrite the two lock tests.
    conduit_runtime "After" (pooled no-op, children first, finish-then-raise, ward, frame log) -> cleanup,
    _prepare_for_pool, _cleanup_spellspaces_for_pool, permanent paths, ConduitWard, AethericFrame -> component
    tests: double cleanup, disposal order, lesser and root failure paths; rewrite the 0.2.80 no-raise test.
    spellspace "After" (lease flag, refusal, finished exits, discard) -> SpellSpace, SpellSpacePool,
    SpellSpaceThreadState -> component tests: kept handle, double cleanup, failing managed/manual/permanent exits,
    owner cleaned inside its space.
    cleanable_contexts -> Cleanable._CleanupContext/_AsyncCleanupContext -> unit tests.
    code description "Invariants" -> per-step benchmarks A/B (space enter/meld/exit, lesser create/cleanup).
  EVIDENCE:
  - context_compass/system_docs/patches/active/scope_exit_dispose_2026_09_27/architecture_patch.md:1-86
  - context_compass/system_docs/patches/active/scope_exit_dispose_2026_09_27/component_patch_conduit_runtime.md:1-48
  - context_compass/system_docs/patches/active/scope_exit_dispose_2026_09_27/component_patch_spellspace.md:1-37
  - context_compass/system_docs/patches/active/scope_exit_dispose_2026_09_27/component_patch_cleanable_contexts.md:1-16
  - context_compass/system_docs/patches/active/scope_exit_dispose_2026_09_27/code_description_patch_scope_exit_paths.md:1-73
  IMPACT: The patch gate is met; implementation may start after the red tests and baselines.
  NEXT: Write the red tests in the VM worktree and run them on the current tree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T21:48:49Z
  TYPE: MEASURE
  CLAIM: Red tests written in the VM worktree (equal to the device tree for src/ and tests/, rsync -c dry run):
    15 component tests for conduit exits, 11 for SpellSpace leases and 5 unit tests for the cleanup contexts.
    On the unchanged tree (3.14.7t, GIL off) 27 fail and 4 pass; the 4 are guards that must stay green: an
    explicit cleanup inside `with lesser:` (passes today only because `with` does not dispose), a re-acquired or
    prewarmed shell melding again, a block error through a clean managed exit, and a block error kept by
    using_cleanup when cleanup succeeds.
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_conduit_component_scope_exit_dispose.py:1-394
  - tests/component/melder/aether/conduit/test_spellspace_component_lease_release.py:1-301
  - tests/unit/melder/utilities/general_base/test_cleanable_cleanup_contexts.py:1-114
  - context_compass/artifacts/scope_exit_dispose_20260927/red_before_change_gil0.txt:1-33
  IMPACT: Every behaviour change has a failing test; the guards pin what must not regress.
  NEXT: Baseline per-step benchmarks on the unchanged worktree.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T22:03:24Z
  TYPE: MEASURE
  CLAIM: Baseline per-step times on the unchanged worktree (wt; 3.14.7t, GIL off, request lane, worker thread,
    800 warm-up cycles, then 3 runs x 4000 cycles): sum of step medians 8,006-8,082 ns. Medians: lesser_create
    802-820, lesser_meld_2nd 310-311, space_enter 229-231, space_meld_marker_2nd 283-286, space_meld_outer
    289-292, space_exit 806-811, lesser_cleanup 1,100-1,115 ns. An earlier run of the same harness, not saved,
    summed 7,976 ns. The after-change A/B interleaves wt and wt_new on this harness and must match within noise.
  EVIDENCE:
  - context_compass/artifacts/scope_exit_dispose_20260927/baseline_wt_gil0.txt:1-34
  - context_compass/artifacts/scope_exit_dispose_20260927/bench_scope_cycle_steps.py:1-93
  IMPACT: The hot steps the change touches (space exit, lesser cleanup, warm space meld) have a recorded floor.
  NEXT: Read the diffs of apply parts 1-2 on wt_new and record them as implemented.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T22:05:28Z
  TYPE: DECISION
  CLAIM: Apply parts 1-2 read back from the wt/wt_new diffs. Part 1 (cleanable.py, spell_space_thread_state.py,
    spell_space_pool.py): both cleanup contexts drop the owner first, call cleanup once and let its error propagate;
    `discard_expected` pops only its own top entry; release sets `_released`, prepare_object and acquire_untracked
    clear it. Part 2 (spell_space.py) matches the PLAN, with one gap against the patch: a space destroyed inside its
    own block (a direct permanent_cleanup(), or an idle-overflow eviction after an explicit cleanup) deletes its
    thread-state reference, so its exit cannot leave the stack and later scopes on that thread would fail
    "stack corruption". Decision: `_cleanup_for_destroy` calls `discard_expected(self)` in its `finally`, before
    the deletes (safe: the conduit never cleans its SpellSpaceThreadState, it only drops the reference); the exit of
    a destroyed space only returns. Patch docs updated first; part 2 is re-applied from the unchanged wt copy.
  EVIDENCE:
  - src/melder/utilities/general_base/cleanable.py:187-420
  - src/melder/aether/conduit/spell_space/spell_space_thread_state.py:219-289
  - src/melder/aether/conduit/spell_space/spell_space_pool.py:146-288
  - src/melder/aether/conduit/spell_space/spell_space.py:233-411
  - src/melder/aether/conduit/conduit.py:840-860
  - src/melder/aether/conduit/conduit.py:965-985
  - context_compass/system_docs/patches/active/scope_exit_dispose_2026_09_27/component_patch_spellspace.md:14-24
  IMPACT: Every exit of a destroyed or released managed space leaves the thread stack consistent.
  NEXT: Update the SpellSpace patch sections, amend and re-run part 2, then write part 3.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T22:08:45Z
  TYPE: FACT
  CLAIM: Implemented on the VM copy wt_new (device src untouched): part 2 re-applied from the unchanged wt copy with
    the destroy-time stack discard; part 3 applied. ConduitWard.cleanup() collects the ExceptionGroup each child's
    permanent teardown raises (other child errors stay logged) and raises them after its own teardown, logger
    last; `_cleanup_children_for_pool(collect_finished=False)` treats a raising child that is no longer attached
    as finished (returned when collect_finished, else logged) and raises "Cannot pool..." with unfinished and
    finished failures only when a child is still attached. AethericFrame logs a raising conduit through the Aether
    logger ("Error cleaning conduit during frame teardown") instead of `pass`. Every apply script is AST-anchored
    and re-parses the file before writing, so the device run fails loudly on any drift.
  EVIDENCE:
  - context_compass/artifacts/scope_exit_dispose_20260927/apply/apply_2_spell_space.py:1-411
  - context_compass/artifacts/scope_exit_dispose_20260927/apply/apply_3_ward_and_frame.py:1-213
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:251-462
  - src/melder/aether/aetheric_frame/aetheric_frame.py:274-337
  IMPACT: Parts 1-3 are in place on wt_new; part 4 (conduit.py) is the last source edit before the red tests run.
  NEXT: Write apply part 4 (conduit.py) from the PLAN note and run it on wt_new.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T22:16:29Z
  TYPE: MEASURE
  CLAIM: Part 4 (conduit.py) applied on wt_new: `with` returns self and exit calls cleanup(); enter_lesser_conduit;
    soft cleanup of a pooled lesser is a no-op; children, then Spaces, then own store on pool return, failures
    raised after re-pooling; permanent paths collect and raise after the logger. The 31 red tests plus one added
    for a space destroyed inside its own block (red on the old src: its exit hit a deleted attribute) pass: 32 green
    on 3.14.7t GIL off. A first suite pass (unit/component aether, integration conduit+aether, utilities) found 4
    tests pinning the old behaviour: the lock test (it still passed, for the wrong reason: cleanup takes the lock),
    the root `with` meld test, the 0.2.80 no-raise teardown test and the named-lesser retry-after-failure test; plus
    one unit test whose MagicMock ward returned a truthy MagicMock child map (setup drift, fixed to an empty map).
    Part 5 rewrites them for the owner's contract; 5 of the 6 are red on the unchanged src, all 37 green on wt_new.
  EVIDENCE:
  - context_compass/artifacts/scope_exit_dispose_20260927/apply/apply_4_conduit.py:1-613
  - context_compass/artifacts/scope_exit_dispose_20260927/apply/apply_5_existing_tests.py:1-284
  - context_compass/artifacts/scope_exit_dispose_20260927/green_new_tests_gil0.txt:1-39
  - context_compass/artifacts/scope_exit_dispose_20260927/red_rewritten_tests_gil0.txt:1-9
  - context_compass/artifacts/scope_exit_dispose_20260927/suites_post_change_vm.txt:1-10
  IMPACT: The behaviour package is complete on the VM copy; the whole tree and the benchmarks decide if it lands.
  NEXT: Run the whole tree on 3.14t GIL off, then the conduit subsets with the GIL on and on the GIL build.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T22:22:40Z
  TYPE: MEASURE
  CLAIM: Whole tree green on wt_new (parts 1-5) on 3.14.7t with the GIL off: aether unit 4113, integration 729,
    component 1242 (+1 xfail); spellbook 2194/776/583; conduit integration 275; multithreading 42; utilities 807
    and 41; metadata and build assets 260; crystallizer 565/258/110; mutation research 277/66/40; llm_support 28;
    architecture 18; github_workflows 385 plus the known PyYAML collection error (environment, as at 13:23Z);
    experimentation 250. wt_new lacked the repository-root files some groups read (.github, llm_support, docs,
    README); they were linked read-only from wt and those groups rerun green. The conduit, cleanable, multithreading
    and aether integration subsets are green with the GIL on (1197/715/317/729) and on the 3.14.7 GIL build (same).
  EVIDENCE: context_compass/artifacts/scope_exit_dispose_20260927/suites_post_change_vm.txt:1-116
  IMPACT: No regression outside the rewritten tests; the change is ready for the benchmark gate.
  NEXT: Interleaved A/B benchmarks, wt vs wt_new, on the per-step harness; then with_lesser mode on wt_new.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T22:33:48Z
  TYPE: MEASURE
  CLAIM: Benchmarks, 3.14.7t GIL off. Separate-process runs vary about +-3% per process (memory layout), more than
    the change, so the decisive harness runs OLD and NEW method versions in ABBA blocks inside one process.
    Same-process A/B: managed space enter+exit +18 to +21 ns (340 -> 358-362 ns, +5-6%), every run; lesser
    create+cleanup +24/+20/-8 ns (about +1%, noise band) after an amendment that reads the conduit state, ward and
    pooled member once in `_prepare_for_pool` (it was +53 ns with an extra enum check in cleanup()). Warm
    SpellSpace.meld with the released check: +0.5/-0.1 ns (none). Control (warm lesser meld): none. On the GIL build
    the space cycle is unchanged (+1.7/-0.9 ns). Cause: the lease flag's two stores per cycle; STORE_ATTR is not
    specialized on the free-threaded build (about 10-12 ns per store, measured in isolation; a list slot is no
    cheaper), and any lease flag needs one write at release and one at acquisition. Full gauntlet request cycle,
    per-step harness: sum of step medians 8,170 -> 8,232 ns (+0.8%, inside the +-4% run-to-run range).
  EVIDENCE:
  - context_compass/artifacts/scope_exit_dispose_20260927/ab_same_process_gil0.txt:1-9
  - context_compass/artifacts/scope_exit_dispose_20260927/ab_same_process_gilbuild.txt:1-14
  - context_compass/artifacts/scope_exit_dispose_20260927/ab_micro_gil0_amended.txt:1-18
  - context_compass/artifacts/scope_exit_dispose_20260927/ab_steps_amended_gil0.txt:1-134
  - context_compass/artifacts/scope_exit_dispose_20260927/bench_same_process_ab.py:1-128
  IMPACT: The released flag the owner chose costs about 20 ns per managed space cycle on 3.14t; nothing else
    measurable. That is a hot-path cost beyond noise in isolation, so the FAILURE_ESCALATION rule applies.
  NEXT: Put the cost to the owner (DECISION_REQUEST) before the device landing.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T22:33:48Z
  TYPE: DECISION_REQUEST
  CLAIM: The released-space refusal costs about 20 ns per managed SpellSpace enter+exit on 3.14t (+5-6% of an
    empty scope, +0.25% of the gauntlet request cycle) and nothing on the GIL build. Options: (A, recommended)
    accept it: it is the cheapest form of the one-bool flag decided on 2026-09-27, and warm melds pay nothing;
    (B) drop the refusal and keep the rest of the package: no cost, but a handle kept past its block melds into
    the idle shell again and the next lease is served that object (P3). Everything else lands either way.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-09-27_investigate_scope_exit_and_pool_return_cleanup_task.md:278-292
  - context_compass/artifacts/scope_exit_dispose_20260927/ab_same_process_gil0.txt:1-9
  IMPACT: The device landing waits for this answer; docs and the release note depend on it.
  NEXT: Ask the owner; land on the device with the chosen option.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T22:54:34Z
  TYPE: DECISION
  CLAIM: Owner answer (question card, then chat "ok cool lets keep moving"): the flag's purpose was unclear ("if you
    cleanup a spellspace you should be done using it, same with a conduit"); keep going on one condition: "make
    sure the price doesn't go up on using spellspace entirely", and explain it better. So the refusal stays and its
    two per-cycle writes are paid back inside the same scope path, verified with the same-process A/B, before the
    device landing. The explanation goes to the owner with the numbers.
  EVIDENCE: context_compass/tickets/tasks/2026-09-27_make_with_dispose_scopes_and_finish_pool_returns_task.md:1-40
  IMPACT: Option A with a zero-net-cost condition; no other contract changes.
  NEXT: Trim the managed enter/exit and lesser return paths, then re-measure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T22:54:34Z
  TYPE: MEASURE
  CLAIM: Cost offsets applied on wt_new and measured (3.14.7t GIL off, same-process ABBA, 3 runs): managed space
    enter+exit -5.4/-7.5/-3.9 ns and lesser create+cleanup -24/-20/-9 ns against the old code; separate-process
    micro: space cycle 338 -> 325 ns (-4%, ranges apart), warm space meld and the control unchanged; GIL build
    same-process: lesser -25/-21 ns, space -7/-17 ns; gauntlet per-step sum 8,058 -> 8,043 ns. Offsets: the managed
    lane of recycle_from_managed_context runs inline in SpellSpace.__exit__ (one call and one flag read fewer),
    SpellSpacePool.release reads its deque once, Conduit.enter_spellspace pushes onto its owned thread stack inline,
    and Conduit._cleanup_spellspaces_for_pool returns before the drain call when nothing is open or registered (the
    common case; that call alone was about 45 ns). Variant runs showed the children-first check costs about 15 ns
    and the flag writes about 20 ns; the offsets more than cover both. Conduit subsets green after the offsets.
  EVIDENCE:
  - context_compass/artifacts/scope_exit_dispose_20260927/ab_same_process_gil0_final.txt:1-10
  - context_compass/artifacts/scope_exit_dispose_20260927/ab_micro_gil0_final.txt:1-18
  - context_compass/artifacts/scope_exit_dispose_20260927/ab_same_process_gilbuild_final.txt:1-6
  - context_compass/artifacts/scope_exit_dispose_20260927/ab_steps_final_gil0.txt:1-134
  - context_compass/artifacts/scope_exit_dispose_20260927/apply/apply_4_conduit.py:1-646
  - context_compass/artifacts/scope_exit_dispose_20260927/apply/apply_2_spell_space.py:1-427
  IMPACT: Using a SpellSpace, and a lesser, costs no more than before on 3.14t or the GIL build; the owner's
    condition is met, so the landing is unblocked.
  NEXT: Rerun the whole tree and the GIL subsets on the final wt_new, then land on the device.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T22:56:25Z
  TYPE: FACT
  CLAIM: Mailbox F0-1 and F0-5 (fable_0) consumed. fable_0 landed the name/class meld entry cache on the device
    tree at 21:54:42Z, before reading M0-63: `Conduit.meld` in conduit.py and `SpellSpace.meld` in spell_space.py,
    plus meld.py, conduit_meld.py, spellspace_meld.py, spellbook.py and one new component test; notched 0.2.8201.
    The device now differs from this lane's wt baseline in conduit.py, spell_space.py, meld.py, spellspace_meld.py
    and __version__.py. `__version__` reads 0.2.8202 (file written 22:06:38Z); fable_0 attributes that bump to
    melder_0, but melder_0 wrote no device source this session (only artifacts, tickets and boards) - not mine.
    The running note header reads 0.2.8202 with fable_0's section first; this lane's section goes after it,
    before Packaging. Owner ruled the collision fine for fable_0 ("notch this as you want").
  EVIDENCE:
  - context_compass/mailbox_board.md:243-320
  - src/melder/__version__.py:1-20
  - release_docs/next_version_release.md:1-28
  IMPACT: The apply scripts must run against the current device files: re-sync the baseline, re-apply, re-test and
    re-measure before landing; the notch is read from `__version__` at landing (0.2.8203 if it still reads 0.2.8202).
  NEXT: ACK F0-5, then rebuild the VM baseline from the device tree and re-apply parts 1-5.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T23:07:47Z
  TYPE: MEASURE
  CLAIM: Re-synced from the device tree (wt2, with fable_0's meld entry cache and 0.2.8202) and re-applied parts 1-5
    (wt2_new); part 2's meld anchor moved to fable_0's new warm-lanes comment, every other edit applied unchanged,
    and the diff of this lane's edits equals the pre-sync one. 37 new and rewritten tests green; whole tree green
    on 3.14.7t GIL off (aether component now 1262 with fable_0's tests), the PyYAML collection error aside; the
    conduit, cleanable, multithreading and aether-integration subsets green with the GIL on and on the GIL build.
    Same-process A/B against the re-synced baseline: space enter+exit -9 to -19 ns, lesser create+cleanup -7 to
    -20 ns, warm SpellSpace.meld with the released check -2 to -5 ns; per-step gauntlet sum 8,055 -> 7,976 ns.
  EVIDENCE:
  - artifacts/scope_exit_dispose_20260927/green_resynced_gil0.txt:1-39
  - artifacts/scope_exit_dispose_20260927/suites_post_change_vm.txt:1-166
  - artifacts/scope_exit_dispose_20260927/ab_same_process_gil0_resynced_meld.txt:1-13
  - artifacts/scope_exit_dispose_20260927/ab_steps_resynced_gil0.txt:1-90
  - artifacts/scope_exit_dispose_20260927/ab_micro_gil0_resynced.txt:1-14
  IMPACT: The package is validated against the tree as it is now and costs less than the tree on every measured
    fast path; the device landing can proceed.
  NEXT: cmp the device files against wt2, apply parts 1-5 on the device, copy the new tests, verify byte equality.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T23:09:03Z
  TYPE: FACT
  CLAIM: Landed on the device tree at 23:08:24Z: the eleven touched files matched wt2 byte for byte and src/ and
    tests/ matched as a whole (rsync -c), apply parts 1-5 ran on the tree, and the three new test files were copied.
    The tree's src/ and tests/ now equal wt2_new apart from test-run cache files other lanes left under tests/.
    Notch: `__version__` read 0.2.8202 at landing and is now 0.2.8203 (23:08:38Z). NOTICEs M0-67 (fable_0), M0-68
    (muse_0), M0-69 (melder_2) sent with alert lines.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - context_compass/artifacts/scope_exit_dispose_20260927/apply/apply_1_cleanable_and_space_support.py:1-297
  - context_compass/artifacts/scope_exit_dispose_20260927/apply/apply_2_spell_space.py:1-427
  - context_compass/artifacts/scope_exit_dispose_20260927/apply/apply_3_ward_and_frame.py:1-213
  - context_compass/artifacts/scope_exit_dispose_20260927/apply/apply_4_conduit.py:1-646
  - context_compass/artifacts/scope_exit_dispose_20260927/apply/apply_5_existing_tests.py:1-284
  - context_compass/mailbox_board.md:285-330
  IMPACT: The behaviour is live on the tree; docs, release note, graph and assets remain.
  NEXT: Correct the SpellSpaceMeld docstrings, then promote the patch docs into src_architecture and src_components.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T23:30:55Z
  TYPE: FACT
  CLAIM: Part 6 landed on the tree and on wt2_new (docstrings only): SpellSpaceMeld's class Lifecycle and System
    Context no longer promise `reset()`, a version bump or an ACTIVE-scope check, and its `meld` contract no longer
    routes `many` to the owner conduit. Verified against the emitted solo executor: a `many` object with disposal
    methods goes to the resolving door's `_spellspace_creations` (the space store) and falls back to the conduit
    store only on a ConduitMeld; without disposal methods it is not stored.
  EVIDENCE:
  - src/melder/aether/conduit/meld/spellspace_meld.py:41-74
  - src/melder/aether/conduit/meld/spellspace_meld.py:292-312
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:80-122
  - context_compass/artifacts/scope_exit_dispose_20260927/apply/apply_6_spellspace_meld_docs.py:1-48
  IMPACT: The last stale SpellSpace document claims in src are corrected; the system documents follow.
  NEXT: Promote the patch docs into src_architecture and src_components and regenerate their indexes.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T23:30:55Z
  TYPE: RISK
  CLAIM: Out of scope, flagged: `SpellSpaceMeld._describe_spell_live_creation_status` reads `many` from the owner
    conduit store, but a `many` object with disposal methods melded through a space lives in the space store, so a
    live-creation probe through a space can report 0 while the space holds one. A probe inaccuracy, not a lifetime
    bug; the fix is a small code change for its own ticket.
  EVIDENCE:
  - src/melder/aether/conduit/meld/spellspace_meld.py:886-953
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:98-122
  IMPACT: Reported to the owner at hand-off; nothing in this lane depends on it.
  NEXT: Name it in the owner report as a follow-up candidate.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-27T23:38:18Z
  TYPE: FACT
  CLAIM: REONBOARD after compaction done (self-certified melder_0). Re-read the landed source behind every claim the
    system docs will carry: Conduit cleanup/_prepare_for_pool/_cleanup_spellspaces_for_pool/_permanent_cleanup/
    _cleanup_lesser_conduit/_cleanup_normal_conduit/_cleanup_spellspaces/enter_spellspace/__enter__/__exit__/
    enter_lesser_conduit; SpellSpace whole; SpellSpacePool; SpellSpaceThreadState.discard_expected; ConduitWard
    cleanup/_clean_up_lesser_conduits_links/_cleanup_children_for_pool; AethericFrame._cleanup_data_structures;
    Cleanable._CleanupContext/_AsyncCleanupContext. They match the patch docs. One factual error found: seven
    docstrings name the landing version as 0.2.8201, written before fable_0 took that notch; the change landed at
    0.2.8203 (conduit.py x2, cleanable.py x2, three rewritten tests).
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:568-616
  - src/melder/aether/conduit/conduit.py:617-800
  - src/melder/aether/conduit/conduit.py:801-1100
  - src/melder/aether/conduit/conduit.py:1193-1255
  - src/melder/aether/conduit/conduit.py:1697-1760
  - src/melder/aether/conduit/conduit.py:2867-2911
  - src/melder/aether/conduit/spell_space/spell_space.py:1-792
  - src/melder/aether/conduit/spell_space/spell_space_pool.py:1-301
  - src/melder/aether/conduit/spell_space/spell_space_thread_state.py:250-274
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:251-527
  - src/melder/aether/aetheric_frame/aetheric_frame.py:274-341
  - src/melder/utilities/general_base/cleanable.py:187-429
  IMPACT: The docs can be promoted as the patch describes; the version text in the landed docstrings is wrong.
  NEXT: Correct the seven version references (part 7, docstring-only, same change set), then promote the docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T23:38:18Z
  TYPE: PLAN
  CLAIM: Doc promotion tranche, after part 7. src_architecture: boundary list (`with conduit` disposes,
    enter_lesser_conduit), Create Lesser Conduit step 5 (children first, finish then raise), SpellSpace Usage
    (no reset/version/active-scope; lease flag), Cleanup item 1, one Operational Invariant (scope exits), the stale
    "SpellSpace can only meld when it is the active spellspace" line, Failure Modes (SpellSpaceScopeError, cleanup
    errors raise after finishing), a Scope Exit diagram (ASCII + Mermaid), Information Sources, C1 remeasure,
    handoff. src_components: Conduit Runtime, ConduitWard, Creations and SpellSpace entries; C2 Lesser Conduit
    Creation, SpellSpace Scope Gate, SpellSpace Thread State; flows Create Lesser Conduit and SpellSpace Scoped
    Meld; C1 remeasure; handoff. tests_components: the three new test files in their clusters and the C1 map, the
    disposal-failures test's new meaning. Content-preservation multisets are captured before the first edit;
    indexes rebuilt in the same pass. Pre-existing and out of scope: both src docs' `## Indexing` and handoff
    sections name package tool paths (the portability check fails before this lane); flagged, not changed.
  EVIDENCE:
  - context_compass/system_docs/patches/active/scope_exit_dispose_2026_09_27/architecture_patch.md:1-88
  - context_compass/system_docs/src_architecture_index.md:31-85
  - context_compass/system_docs/src_components_index.md:31-176
  - context_compass/system_docs/tests_components_index.md:29-99
  - context_compass/system_docs/src_architecture.md:33-114
  - context_compass/system_docs/src_components.md:22-60
  IMPACT: Every doc edit maps to a patch section; the portability leak is recorded for the owner, not fixed here.
  NEXT: Apply part 7, then capture the preservation baselines and edit src_architecture.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T23:39:18Z
  TYPE: FACT
  CLAIM: Part 7 landed on the tree and on wt2_new (23:38:45Z, docstring text only, same 0.2.8203 change set, no
    new notch): the seven version references now read 0.2.8203. Each edit is anchored on its full context string
    and must match once; the script refuses a file that still names 0.2.8201 and compiles each file before writing.
    The six touched test files pass on wt2_new (79 passed, 3.14.7t GIL off); device src/ equals wt2_new src/
    (rsync -c dry run, caches excluded).
  EVIDENCE:
  - context_compass/artifacts/scope_exit_dispose_20260927/apply/apply_7_version_text.py:1-52
  - context_compass/artifacts/scope_exit_dispose_20260927/part7_touched_tests_gil0.txt:1-4
  - src/melder/aether/conduit/conduit.py:590-596
  - src/melder/aether/conduit/conduit.py:1707-1713
  - src/melder/utilities/general_base/cleanable.py:262-268
  - src/melder/utilities/general_base/cleanable.py:368-374
  IMPACT: The landed docstrings name the version the change shipped in; C1 ranges are measured after this edit.
  NEXT: Capture the content-preservation baselines, then edit src_architecture.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-27T23:51:11Z
  TYPE: FACT
  CLAIM: Patch promoted into the three system docs; indexes rebuilt and --check OK (src_architecture 57 sections /
    3228 lines, src_components 147 / 10140, tests_components 65 / 2565). src_architecture: boundary list, Create
    Lesser Conduit step 5, SpellSpace Usage (reset/version/active-scope removed), Cleanup items 1 and 7, a new
    scope-exit invariant, the stale active-spellspace invariant corrected, three failure modes, a Scope Exit and
    Pool Return diagram (ASCII + Mermaid), sources, C1 remeasured (+ spell_space_pool/thread_state), handoff.
    src_components: Conduit Runtime ("Scope exits"), ConduitWard, Creations and SpellSpace ("Scope lease and
    finished exits"; the folded "reset/versioning" line kept and flagged CORRECTED), AethericFrame Services
    (two log calls now), three C2 entries, two flows, C1 remeasured, sources, handoff; the RISK probe gap is a
    known Failure Mode. tests_components: the three new test files in their clusters and the C1 map (core now
    186 paths), the disposal-failures test remeasured (142), handoff. Line citations into the files this change
    set grew were re-found by symbol (a second pass for src_architecture): conduit.py 10 lines, conduit_ward.py 11,
    aetheric_frame.py 5. Some already pointed elsewhere before this lane and were corrected on the way: the
    conduit.py ones since fable_0's 0.2.8201 edit; ward 799/973 (now the SafeGuard lines 893/1067), 708-721,
    527-580, 572-579, 565-567 (docstring lines, now the code); frame 463, 841, 209 -> 208 and 645-694 (now the
    unfrozen branch, 691-752, whose copy count is recounted as fourteen values, not twelve). Preservation: every
    lost line is a replaced stale claim, a remapped citation or a remeasured C1 field (report written). Join:
    every Key Files / C1 path in src_components resolves in src_graph_index. No new portability hits (9 and 11
    pre-existing, 0 in tests_components); no new line over 120.
  EVIDENCE:
  - context_compass/artifacts/scope_exit_dispose_20260927/docs/edit_src_architecture.py:1-246
  - context_compass/artifacts/scope_exit_dispose_20260927/docs/edit_src_architecture_citations.py:1-50
  - context_compass/artifacts/scope_exit_dispose_20260927/docs/edit_src_components.py:1-455
  - context_compass/artifacts/scope_exit_dispose_20260927/docs/edit_tests_components.py:1-130
  - context_compass/artifacts/scope_exit_dispose_20260927/doc_preservation/preservation_report.md:1-130
  - context_compass/system_docs/src_architecture_index.md:1-86
  - context_compass/system_docs/src_components_index.md:1-176
  - context_compass/system_docs/tests_components_index.md:1-94
  IMPACT: The canonical docs describe the landed behaviour; graph, release note and assets remain.
  NEXT: Extract and assemble the graph for the changed src files, review stale authored prose, then accept.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T23:59:50Z
  TYPE: FACT
  CLAIM: Graph refreshed. extract_graph.py --strict (3.14.7t, skipped=0) rewrote the mechanical tier of 21
    descriptors (this lane's 8 files; fable_0's meld.py, conduit_meld.py, spellbook.py, __version__ and 8 asset
    manifests/payloads, none re-extracted since their changes; creations.json only re-indented); authored tiers
    compared equal before and after. The authored prose of the 18 nodes in this lane's files was read against the
    source: stale lines fixed (SpellSpace "active scope" and "reset" -> lease flag and finished exits; ConduitWard
    descendant retention; Conduit gains `with` dispose, enter_lesser_conduit, children-first return,
    finish-then-raise, and the name/class warm lane fable_0 added; Cleanable contexts propagate;
    _AsyncCleanupContext authored), then each node accepted. A second extraction only re-indented the
    walker-written files (indent 2 -> 1, same content); assemble_graph.py then wrote src_graph.md (27539 lines)
    and its index (all 584 ranges verified); 0 package paths. Census 1050 -> 1060 AUTHORED, 151 -> 142 stale. Left
    stale, not this lane's to accept: Meld, ConduitMeld and Spellbook (fable_0's 0.2.8201 source), plus the 139
    pre-existing stale nodes.
  EVIDENCE:
  - context_compass/artifacts/scope_exit_dispose_20260927/docs/edit_graph_descriptors.py:1-124
  - context_compass/artifacts/scope_exit_dispose_20260927/docs/graph_walker_report_after.txt:1-8
  - context_compass/system_docs/src_graph_index.md:133-133
  - context_compass/system_docs/src_graph_index.md:157-157
  - context_compass/system_docs/src_graph_index.md:586-586
  IMPACT: The graph describes the landed source for every file this lane changed; release note and assets remain.
  NEXT: Write the release-note section after fable_0's and update the header and packaging line to 0.2.8203.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-28T00:02:01Z
  TYPE: FACT
  CLAIM: Release note written (CRLF kept): header 0.2.8202 -> 0.2.8203; section "`with` releases a Conduit, and
    every scope exit finishes its cleanup" after fable_0's and before Packaging, with two Breaking change leads
    (`with conduit:` disposes; disposal failures are raised after finishing, using_cleanup propagates), a short
    enter_lesser_conduit example, the four fixes, what stays the same and the VM numbers; one Packaging bullet
    for the corrected system documents; rebuild line at 0.2.8203. Asset inputs checked before rebuilding: the
    system-document assets read only src_architecture, src_components and src_graph (+ indexes), the agent
    documentation reads src/*.py, and the LLM bundles exclude context_compass/, so the later ticket closure,
    board sync and patch-lane archive cannot stale them.
  EVIDENCE:
  - release_docs/next_version_release.md:1-77
  - src/melder/_build_assets/_system_documents/_builder.py:110-180
  - src/melder/_build_assets/_agent_documentation/_builder.py:185-195
  - llm_support/README.md:1-60
  IMPACT: Everything the rebuild reads is final; the rebuild can run now and stays current through closure.
  NEXT: Rebuild assets and LLM bundles, then both --check runs, then the version/asset/system-doc tests.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-28T00:14:51Z
  TYPE: MEASURE
  CLAIM: Assets and bundles at 0.2.8203. The asset runner on the device wrote the agent-documentation and
    bind-guard manifests, then stopped: the system-document builder unlinks old payloads and the connected folder
    refuses deletes. As in the 0.2.80 lane, the assets were rebuilt in the VM copy (inputs equal to the device:
    src/ and the three system docs + indexes, rsync -c / cmp), --check OK there, and the five system-document
    outputs copied over the device files (backup of the old ones in VM scratch); the two manifests already on the
    device equalled the VM build. Device --check: OK for all three (v0.2.8203). LLM bundles rebuilt on the device
    with --include-untracked (src 576, tests 1032, other 379; the untracked inputs are this lane's three tests,
    fable_0's input-fast-door test and seven experimentation modules, reviewed, no secrets); --check with the
    flag prints only OK; tracked-only reads tests STALE until the owner commits the untracked tests, as at 0.2.80.
    Final pass on a synced VM copy: the version/asset/system-document set 288 passed, 1 skipped and the lane
    suites (unit+component aether/conduit, integration conduit, general_base) 2207 passed, on 3.14.7t GIL 0 and 1
    and on the 3.14.7 GIL build.
  EVIDENCE:
  - context_compass/artifacts/scope_exit_dispose_20260927/suites_final_08203_vm.txt:1-7
  - src/melder/_build_assets/_system_documents/_builder.py:575-578
  - src/melder/_build_assets/_system_documents/manifest/system_documents_manifest.py:1-82
  - llm_support/manifest.json:1-20
  IMPACT: Every EXIT_GATE item except owner acceptance is met.
  NEXT: Move the task to review, sync the board, NOTICE the active agents, report to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-28T00:16:25Z
  TYPE: MEASURE
  CLAIM: Quality rubric, self-scored from the files on disk after the index rebuilds (scope: the sections and
    entries this pass touched; the rest was not re-scored). src_architecture 75/100 (B): Fidelity 4 (touched
    sections checked against source, 30 citations re-found by symbol; untouched claims not re-verified, and this
    pass found drift there, e.g. the twelve-value copy), Completeness 5 (17 contract sections in order), Depth 4
    (older one-clause invariants remain), Addressability 3 (container H2s with no own text, e.g. Data Flows and
    Sequences), Join 3 (every C1 path resolves; only the 7 files this lane touched were remeasured), Mirror 3
    (tests_architecture not re-read this pass). src_components 75/100 (B): Fidelity 4, Completeness 5 (all twelve
    fields in the four touched entries), Depth 4 (the four touched entries), Addressability 3 (the C3 catalog
    container), Join 3 (Key Files join verified; ranges remeasured for touched files only), Mirror 3
    (tests_components updated for the new tests only).
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:1223-1223
  - context_compass/system_docs/src_architecture.md:633-634
  - context_compass/system_docs/src_architecture.md:1250-1255
  - context_compass/system_docs/src_components.md:206-208
  IMPACT: Both documents stay above the 60 threshold; the weak criteria are pre-existing and recorded here.
  NEXT: Report to the owner and ask for acceptance.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-28T00:19:49Z
  TYPE: DECISION
  CLAIM: Owner accepted the lane (chat, 2026-09-28: "ok cool yeah fix the problem you have yourself and send it,
    finish off your fixes and turn in the remaining things please go ahead"). Read as: (1) this task and the
    investigation task are accepted and turned in now; (2) the follow-up this lane found in its own area - the
    SpellSpaceMeld live-creation probe missing a space-held `many` (RISK note) - is fixed in its own task, landed
    with its own notch, then turned in by the same directive. The doc portability leak and fable_0's stale graph
    nodes are not this lane's and stay recorded follow-ups.
  EVIDENCE: context_compass/tickets/tasks/2026-09-27_make_with_dispose_scopes_and_finish_pool_returns_task.md:1-40
  IMPACT: Closure proceeds; a new task carries the probe fix.
  NEXT: Turn in both scope-exit tickets (summaries, completed lanes, boards, patch lane), then open the probe task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-28T00:20:38Z
  TYPE: FACT
  CLAIM: Turned in on the owner's directive: moved to tasks/completed, board row removed and anchored, attention
    details pruned, patch lane moved to patches/completed (promoted), artifacts retained as reference.
  EVIDENCE: context_compass/attention_board.md:1-60
  IMPACT: The lane is closed; nothing here is routed any more.
  NEXT: none.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
State (2026-09-28): in review. The package is live at 0.2.8203: `with conduit:` disposes (Breaking),
`Conduit.enter_lesser_conduit()`, finish-then-raise on every scope exit, children-first pool return, idempotent
soft cleanup, the SpellSpace lease flag (released spaces refuse meld and purge), `using_cleanup()` propagates,
frame teardown logs. Measured at or below the old cost on every fast path. Docs, graph, release note, assets and
bundles are current; final suites green on three interpreters. Remaining: owner acceptance, then close this task
together with the investigation task (patch lane -> completed, artifacts retained, board anchors).
Follow-ups for the owner, not done here: the SpellSpaceMeld live-creation probe misses space-held `many` (RISK
note); both src system docs still name tool paths in `## Indexing` (portability, pre-existing); fable_0's Meld,
ConduitMeld and Spellbook graph nodes are SEMANTICS_STALE since 0.2.8201.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->

<!--
Anything this project needs on every ticket of this kind goes in the region
above: extra fields, a compliance checklist, a link to a local convention.

The region is yours. An upgrade replaces every other line of this template with
the new version's text and carries this region across untouched, so a local
addition here is not a divergence you re-resolve on every upgrade - which is
what editing the rest of the template would cost you.
-->
