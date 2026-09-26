

# Task: Phase 5 reads a stable copy of the spell pool, so concurrent binds cannot abort revalidation

## Metadata
- Completed: 2026-09-26T21:59:01Z
- Closure Basis: owner turn-in in chat (2026-09-26T21:59Z): "I accept your 2/3 continue working on the last part"
  (the Phase-5 pool fix and the guard-test fix; the tests docs task stays open).
- Summary: Compiler passes on the meld-time path (Phases 3, 4 strategies, 5, 6 frame-wide, the Phase-8 walk) iterate
  a copy of the spell pool, and Phase 5 admits only ids with a registered state, so a concurrent bind cannot
  abort revalidation; regression test red before, green after; 0.2.72 docs, graph, assets, LLM bundles and
  release note current. Raised, not changed: conjure-time sweeps and the Nexus publisher's pool tuple.
- Task ID: TASK-2026-09-26-snapshot-phase5-live-spell-pool
- Story: none
- Status: done
- Owner: user
- Agent Name: melder_0
- Priority: p0
- Created: 2026-09-26T21:12:25Z
- Updated: 2026-09-26T21:59:01Z

## Objective
Conjure-time and meld-time Phase 5 build their visible-spell set by iterating `spellbook._spell_id_pool` live.
A bind or removal on another thread in that window raises "dictionary changed size during iteration" and aborts
the resolution run (seen once in the 3.14t multithreading suite). Phase 5 must read a consistent snapshot, and
every other live iteration of the pool on the same revalidation path must be checked.

## Ticket Contract
- ENTRY_GATE: owner approval (Notes); code read and the fix decided in Notes; patch docs written and linked (the
  change is concurrency-sensitive); file list in Notes before code.
- EXECUTION_BOUNDARY: `compiler_phase_5.py` and any other src file named in the PLAN note; a regression test; the
  canonical docs, graph descriptor, assets, release note and version notch for 0.2.72.
- DEPENDENCIES: none open; NOTICEs to fable_0, melder_1 and melder_2 before the notch.
- EXIT_GATE: deterministic regression test fails before and passes after; spellbook, multithreading and compiler
  suites on 3.14t and GIL; assets and LLM bundles current at 0.2.72.
- FAILURE_ESCALATION: DECISION_REQUEST if the fix needs a lock or changes which spells Phase 5 sees.

## Scope Boundaries
- In scope: every live iteration of the spell pool on the Phase 5 path; the regression test.
- Out of scope: other pools and registries unless the same hazard is on the Phase 5 path.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner instruction to fix the reported follow-ups, 2026-09-26T21:12:25Z.
- from_state: review
- to_state: done
- transition_reason: Owner turn-in, 2026-09-26T21:59:01Z; see the Closure Basis.

## Steps / Checklist
- [x] Read Phase 5 and the pool writers; decide the snapshot form (free-threaded atomicity).
- [x] Patch docs (architecture, component, code description) and file list.
- [x] Regression test red, fix, test green; suites on 3.14t and GIL.
- [x] Docs, graph, notch 0.2.72, release entry, assets, LLM bundles.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Fix, regression test, patch docs promoted, release entry.

## Files / Paths Impacted
- src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py (more in the PLAN note if found)

## Validation
- Regression test 5/5 red on unfixed src, 5/5 green with the fix on 3.14t and GIL; suites in the 21:35:35Z
  note; asset and document tests 21:45:09Z. Nothing was rerun at closure.

## Risks / Rollback Notes
- A snapshot can include a spell removed a moment later; the removal path must still gate it (verify).

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without acceptance confirmation and board-sync completion.

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
  - system_docs/patches/completed/compiler_pool_snapshot_2026_09_26/
  - artifacts/compiler_pool_snapshot_20260926/
- DISPOSITION: promote_to_documentation (patch docs); retain_as_reference (probes)
- CLEANUP_TRIGGER: Task closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - Phase 5 visible-spell set, spell pool writers, free-threaded dict iteration
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T21:12:25Z
  TYPE: DECISION
  CLAIM: Owner, after the override lane turn-in: "yeah go ahead and fix all that shit and finish up all those things,
    ok fix the rare crash bro thats a correctness issue". This task is one of the three follow-ups melder_0 reported
    (Phase-5 pool race, order-dependent guard test, weak tests system docs); the deleted unroll benchmarks need no
    action (they measured the retired emitter's dict-vs-unroll choice).
  EVIDENCE:
  - tickets/tasks/completed/2026-09-26_build_site_plan_lowering_task.md
  IMPACT: Work is owner-approved; file lists are recorded here before any edit.
  NEXT: Read compiler_phase_5.py run_local/run_frame_wide and the spell pool writers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T21:18:17Z
  TYPE: FACT
  CLAIM: The hazard is wider than Phase 5. Pool writers (bind, notch, contract grants, transfer) change
    `spellbook._spell_id_pool` under the Spellbook RLock, while compiler passes iterate it with no lock. Meld-time
    revalidation (structural 1-4, resolution 5-11, deferred 8-11) runs outside any transaction, so these live
    iterations can raise "dictionary changed size during iteration": Phase 3 `_iter_all_spells` (a generator used by
    five candidate scans, held open across user `__eq__` calls), the Phase-4 binding-resolution-cycle (two sweeps),
    circular-dependency and duplicate-name strategies, Phase 5 frame-wide and local, Phase 6 frame-wide (its pool
    is also iterated by two Phase-6 system strategies), and the Phase-8 pool walk. The Phase-8 walk catches the error
    and returns None, so a race there silently drops the existence-occurrence analysis that family discovery reads.
    Second race in Phase 5: bind publishes the pool entry before `register_index`, so a pass in that gap sees a
    visible spell with no SpellSystemState and raises "requires a live SpellSystemState". Lookups (`get`, `[]`,
    `in`) are safe. Conjure-time sweeps in spellbook_creation_system.py and structural_snapshot.py run inside the
    CONJURE transaction; the Nexus relationship publisher takes `tuple(pool.values())` (another subsystem).
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:1098-1140
  - src/melder/aether/spellbook/spellbook.py:5341-5402
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:115-134
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/binding_resolution_cycle_strategy.py:136-146
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/binding_resolution_cycle_strategy.py:204-214
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/circular_dependency_strategy.py:100-112
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/duplicate_spell_name_strategy.py:100-115
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:473-560
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:617-713
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_6.py:330-391
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:531-561
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:634-662
  - src/melder/aether/spellbook/spell_compiler/system/spell_system_adjacency_builder.py:30-96
  - src/melder/nexus/frame_descriptor_manager.py:619-628
  IMPACT: Fixing Phase 5 alone would leave the same crash in Phases 3, 4, 6 and a silent wrong family choice in 8.
  NEXT: PLAN below, then an atomicity probe of dict.copy() on 3.14t.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T21:18:17Z
  TYPE: PLAN
  CLAIM: One rule for every compiler pass on the meld-time path: iterate a copy of the pool taken in one call
    (`pool.copy()`; the dict's own lock makes it atomic on free-threaded builds, the GIL on others), never the live
    dict, and never take the Spellbook lock (writers hold it across user-visible work; no new lock, no lock-order
    risk). Phase 5 uses its copy for both the visible set and every lookup in the pass, and admits only ids present
    in the pass's adjacency snapshot, so a spell whose state is not registered yet is left to the revalidation its
    bind schedules. Today any such id makes the pass raise, so this only changes passes that would have failed.
    Phase 6 frame-wide copies once and uses the copy for all its stages and strategies. Out of scope, raised to the
    owner: the conjure-time sweeps (inside the CONJURE transaction; fable_0's files) and the Nexus publisher.
    Lane id compiler_pool_snapshot_2026_09_26 (patch docs); probes under artifacts/compiler_pool_snapshot_20260926/.
    FILES:
    - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py (_iter_all_spells)
    - src/melder/aether/spellbook/spell_compiler/validation/strategies/binding_resolution_cycle_strategy.py
    - src/melder/aether/spellbook/spell_compiler/validation/strategies/circular_dependency_strategy.py
    - src/melder/aether/spellbook/spell_compiler/validation/strategies/duplicate_spell_name_strategy.py
    - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py (run_frame_wide, run_local)
    - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_6.py (run_frame_wide)
    - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py
    - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_pool_snapshot_reads.py (new)
    - src/melder/__version__.py, release_docs/next_version_release.md, canonical docs, graph, assets, LLM bundles
  EVIDENCE: src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:514-545
  IMPACT: Closes the observed crash and its siblings with no lock and no steady-state behavior change.
  NEXT: Probe dict.copy() atomicity under a writer thread on 3.14t (and PYTHON_GIL=1).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T21:19:05Z
  TYPE: MEASURE
  CLAIM: probe_dict_copy_atomicity.py (a writer thread inserting and popping keys; 20,000 reader rounds over a
    300-key dict), Python 3.14.7: free-threaded, iterating the live dict raised RuntimeError in 19,981 rounds and
    `dict.copy()` in 0; with PYTHON_GIL=1 both 0 (the switch interval rarely lands inside so short a loop; the
    compiler loops are longer and call user code). A first run also saw one live read return an empty list,
    not reproduced in the second (0 short reads).
  EVIDENCE:
  - context_compass/artifacts/compiler_pool_snapshot_20260926/probe_dict_copy_atomicity.py:1-51
  - context_compass/artifacts/compiler_pool_snapshot_20260926/probe_ft.txt:1-2
  IMPACT: `pool.copy()` is the safe read on both builds; no lock is needed.
  NEXT: Patch docs, then the regression test on the current tree (expected red).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T21:24:00Z
  TYPE: MEASURE
  CLAIM: Implemented on the work copy (apply_pool_snapshot_edits.py: 7 files, 15 anchored line edits, each region
    keeps its own line ending; --check clean on the work copy and the device). New
    test_compiler_pool_snapshot_reads.py (5 tests, real Spellbook and conjured graph; a pool that grows while
    iterated stands in for a concurrent bind): on the unfixed device src all 5 fail with the reported symptoms
    ("dictionary changed size during iteration" in Phase 3 `_iter_all_spells` via `_resolve_single_by_annotation`,
    in Phase 5 local and frame-wide; "requires a live SpellSystemState" for the unregistered entry; the Phase-8 walk
    returns None); with the fix 5 passed on 3.14t and with PYTHON_GIL=1. The test double's first version let
    dict.copy() run through its overridden iteration (a subclass overriding __iter__ loses the fast copy); it now
    defines copy() as a plain dict of its entries, as a real pool's copy is.
  EVIDENCE:
  - context_compass/artifacts/compiler_pool_snapshot_20260926/apply_pool_snapshot_edits.py:1-144
  - context_compass/artifacts/compiler_pool_snapshot_20260926/test_compiler_pool_snapshot_reads.py:1-235
  IMPACT: The crash and its siblings are closed on the work copy; broader suites are running.
  NEXT: Read the suite logs (~/work/s7_ft.log, ~/work/s7_gil.log); then apply to the device.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T21:35:35Z
  TYPE: MEASURE
  CLAIM: Suites on the work copy with the fix (3.14.7). Free-threaded: unit spellbook 2179, component spellbook
    776, integration spellbook 583+2s+2xf+2xp, multithreading 42, component aether 1215+1xf, integration aether
    716, unit aether 4053, integration conduit 268, crystallizer unit 565 / integration 258+3xf, mutation_research
    unit 277 / component 40 / integration 66, utilities unit 802+2s+7xf / component 41+23s, live_sim 1+1xf,
    package-root unit files 58, experimentation 250+4s: all pass except the known crystallizer file_backed_morph
    x4. PYTHON_GIL=1: the first seven suites pass with the same counts. The multithreading race is rare and was
    not reproducible before either (37 runs), so the deterministic tests are the evidence, not the suite.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_pool_snapshot_reads.py:1-235
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:514-560
  IMPACT: The fix is qualified; device apply next.
  NEXT: Apply src edits, the new test and the test-order edits to the device; verify against the work copy.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T21:45:09Z
  TYPE: MEASURE
  CLAIM: Device done for 0.2.72. (1) src edits and the new test applied; device src/tests byte-identical to the
    qualified work copy (backup ~/work/s7/device_before/files.tgz). (2) NOTICEs M0-47 (fable_0, before the Phase-8
    edit), M0-48 (melder_1), M0-49 (melder_2); __version__ 0.2.71 -> 0.2.72, release header and asset line, a release
    section "A bind during a meld's revalidation no longer fails it", packaging bullet extended. (3) Promoted:
    src_components "Compiler pool reads" block under the SpellCompiler entry, src_architecture operational invariant,
    both handoff summaries; C1 entries of compiler_phase_5.py re-measured (729) and the one drifted citation into
    the Phase-8 file remapped (1085-1127, same symbol); both indexes --check clean. (4) Graph: extract --strict rc 0;
    the 7 changed class nodes re-read and accepted with a copy-read responsibility each; CompilerPhase3's false DAG
    responsibility corrected and its false "creates DirectedAcyclicWorkGraph" edge retired to the lane's
    retired_edges.json (Phase 3 builds id rows since C-C); assemble and --check clean, census stale 203 -> 196.
    (5) Assets: work copy then device, byte-equal, CRLF kept, --check OK at v0.2.72 (bind guard unchanged at 619);
    the combined system-document selection 255 passed, 1 skipped. (6) LLM bundles with --include-untracked (the only
    untracked file outside context_compass is the new test): --check OK; a tracked-only check stays stale until
    that file is committed.
  EVIDENCE:
  - context_compass/system_docs/src_components.md:3398-3416
  - context_compass/system_docs/src_architecture.md:869-874
  - context_compass/system_docs/patches/active/compiler_pool_snapshot_2026_09_26/retired_edges.json:1-17
  - release_docs/next_version_release.md:376-391
  IMPACT: The fix is complete end to end; the task moves to review for the owner's turn-in.
  NEXT: Owner acceptance; at turn-in move the patch lane to patches/completed and close.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T21:49:31Z
  TYPE: FACT
  CLAIM: M2-8 from melder_2 (21:47:18Z, consumed): an owner-approved change notched above 0.2.72 stops the normal
    site plan re-taking its root's slot guard when the calling door already holds it (unique_per_conduit and
    spellspace routes) in site_plan_lowering.py, site_plan_override_runtime.py and generalized_hydrator.py; its
    device apply waited for this task's 0.2.72 docs and assets. Those are done, and no edit of this lane touches
    those files, so M0-50 tells melder_2 to proceed. Their change will move line citations into those files and
    needs its own asset and LLM-bundle rebuild at their notch.
  EVIDENCE: tickets/tasks/2026-09-26_remove_nested_slot_guard_take_task.md
  IMPACT: No conflict; melder_2 is unblocked.
  NEXT: Continue the tests docs refresh.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T21:59:01Z
  TYPE: DECISION
  CLAIM: Closed on the owner's turn-in (see the Closure Basis); acceptance given.
  EVIDENCE: tickets/tasks/completed/2026-09-26_snapshot_phase5_live_spell_pool_task.md
  IMPACT: The ticket moves to its completed folder; board and artifact rows are synced in the same pass.
  NEXT: none.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
Review. Compiler passes on the meld-time path iterate a copy of the spell pool (Phases 3, 4 strategies, 5, 6
frame-wide, the Phase-8 walk); Phase 5 admits only ids with a registered state. 0.2.72: docs, graph, assets, LLM
bundles and release note current. Open items raised, not changed: conjure-time sweeps in the creation system and
structural snapshot (inside the CONJURE transaction), and the Nexus publisher's tuple(pool.values()).
Closed 2026-09-26T21:59:01Z on the owner's turn-in. Patch lane archived to
system_docs/patches/completed/compiler_pool_snapshot_2026_09_26/ (retired_edges.json inside).

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
