# Task: Investigate the Spellbook.find_spell_by_id race blocking the MelderOps lane

## Metadata
- Task ID: TASK-2026-10-10-investigate-spell-lookup-by-id-race
- Story: none (standalone; owner-assigned investigation)
- Status: review
- Owner: claude (assigned by the owner 2026-10-10; investigation and isolated diagnostic tests only)
- Agent Name: melder_1
- Priority: p1
- Created: 2026-10-10T18:18:25Z
- Updated: 2026-10-11T08:49:47Z

## Objective
Investigate the reported race between `Spellbook.find_spell_by_id` and concurrent changes to the collection it
searches, which blocks the MelderOps lane. Pin the exact source, check whether the failure still exists, build a
deterministic reproduction with explicit synchronization and meaningful assertions (no sleeps), separate a current
reproduced defect from historical evidence, and return the smallest proposed repair with its locking, ownership and
reentrancy implications, compatibility risks and regression tests - before any implementation.

## Owner Direction
Owner, chat 2026-10-10 (message for Melder One): investigate the spell-lookup-by-ID race starting with
`Spellbook.find_spell_by_id` and concurrent changes to the collection it searches; pin branch, commit, package
version and relevant uncommitted source changes; check whether the reported failure still exists; preserve the
completed scan/bind work; deterministic reproduction with explicit synchronization, not sleeps; use the MelderOps
failure report if available and distinguish a current reproduced defect from historical evidence; if not reproduced,
report the conditions tested and what remains unknown. Before implementation return the smallest proposed repair,
its locking/ownership/reentrancy implications, compatibility risks and regression tests. Keep failing evidence
intact. Isolated diagnostic tests are fine; no production source change, commit or push. D-10, D-11 and D-20 stay
separate and open; this assignment approves none of their security or architecture decisions.

Owner, chat 2026-10-10 (after Note 12; replaces an earlier brief - Book lock plus R1's snapshot - before any
work on it, and clarified in a follow-up message): a reviewer's comparison recommends reusing the EXISTING
Spellbook._lock in two places - held across find_spell_by_id's existing live traversal, and taken briefly around
bind's active-map insertion - with no new lock, no snapshot, no new index helper and SpellIndex.has_spell and the
index-level locking unchanged; document that returned Spells remain borrowed references. Reviewer audit: nine live
mutation statements of the map, eight already under the Book lock, normal bind publication the missing one;
restore/graft use the ordinary bind/stage/notch paths. Reviewer evidence (isolated 8227, CPython 3.14.8t, both GIL
modes): 66 fair-matrix checks plus 10 focused checks passed; registration callbacks could join foreign-thread
lookups (the publication lock does not enclose hooks); reader locking alone failed the dict-change negative
control. It fixes the target lookup, not every consumer: permissions lookup, command-system lookup, foreign-Book
inspection and contract-proxy iteration need separate review. Asked of melder_1: verify the access inventory,
adapt the patch on current 8228, return the diff and regression evidence before landing. Outstanding: full suite,
performance, opposite-direction transfer, forced rollback. Do not advance MelderOps' baseline; R2/R3 stay separate.

Owner, chat 2026-10-10/11 (after Note 21): challenged R4's stall ("a mediator is used for bind and conjure";
prove it on the entire system, not in isolation), then stopped the full-tree rerun to save usage and asked what
0.2.8224 changed. find_spell_by_id was added for MelderOps and a meld fast path; notch is ordered by the mediator,
every version of a spell stays in the Book under an active or inactive spell id, and a better way to reach a
spell should be used. After Note 25: R6 seems reasonable - send the fix if it holds, otherwise propose the next.

## Ticket Contract
- ENTRY_GATE: owner assignment (chat, 2026-10-10); this ticket and its attention_board.md row exist before any
  diagnostic test runs.
- EXECUTION_BOUNDARY: read src/melder (find_spell_by_id, the collection it iterates, every writer and reader of it);
  diagnostic tests and probes only under artifacts/spell_lookup_race_20261010/ or /tmp scratch; read-only use of the
  MelderOps report. No change under src/, tests/, docs/ or release_docs/; no notch, commit or push.
  AMENDED (owner approval, Note 29): the R6 landing - src, tests, docs, release note, notch, graph, assets and
  llm_support - through the patch lane; still no commit or push.
- DEPENDENCIES: HEAD 3d184cac (0.2.8228, scan/bind work committed); the MelderOps report (priv_commandops).
- EXIT_GATE: source identity pinned; reproduction and test results recorded (or the conditions tested and the
  remaining unknowns, if not reproduced); proposed patch scope with locking/ownership/reentrancy implications,
  compatibility risks and regression tests written here; the owner reviews. Implementation needs separate approval.
- FAILURE_ESCALATION: DECISION_REQUEST if the repair needs a lock-order change or a public contract change; BLOCKER
  if neither the report nor the source explains the reported failure.

## Scope Boundaries
- In scope: find_spell_by_id and the `_spells` map it walks; the writers that change that map; other readers that
  walk it without the Spellbook lock (to size the repair); SpellIndex membership reads used by the lookup.
- Out of scope: implementation; MelderOps code; D-10, D-11 and D-20; the scan/bind work (committed at 3d184cac).

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: opened and started on the owner's assignment (chat, 2026-10-10); investigation and isolated
  diagnostic tests only.
- from_state: in_progress
- to_state: review
- transition_reason: (2026-10-10T19:22:24Z) investigation complete - defect reproduced on 3d184cac, repair
  R1 measured in scratch exports and proposed (Note 12); implementation waits for the owner's decision.
- from_state: review
- to_state: in_progress
- transition_reason: (2026-10-10T21:09:45Z) the owner redirected to the reviewer's Book-lock design (Owner
  Direction, second paragraph): verify the access inventory, adapt the patch on 3d184cac and return diff and
  evidence; no landing.
- from_state: in_progress
- to_state: review
- transition_reason: (2026-10-10T22:20:00Z) inventory verified; R4 as written regresses conjure (Notes
  15-16); adapted repair R5 measured and proposed with the R4' alternative (Notes 17-21); the owner decides,
  nothing landed.
- from_state: review
- to_state: in_progress
- transition_reason: (2026-10-11T00:51:22Z) the owner chose R6 if it holds (Owner Direction, third paragraph): verify it
  from source, build and test it in scratch; landing only after that, through the patch lane.
- from_state: in_progress
- to_state: review
- transition_reason: (2026-10-11T00:56:46Z) pure R6 failed its source check on two points (Note 26); R7 proposed
  (Note 27), nothing built or landed.
- from_state: review
- to_state: in_progress
- transition_reason: (2026-10-11T01:07:38Z) owner go for R6 as amended (Note 29): patch lane, scratch tests,
  then landing.
- from_state: in_progress
- to_state: review
- transition_reason: (2026-10-11T08:49:47Z) R6 landed as 0.2.8229 with its tests, docs, graph, release note and rebuilt
  assets (Notes 31-33); the owner accepts or redirects. No commit or push.

## Steps / Checklist
- [x] Pin branch, commit, version and uncommitted changes.
- [x] Locate and read the MelderOps failure report; record its version and symptom. (Note 2)
- [x] Read find_spell_by_id, the `_spells` writers and readers, and SpellIndex membership reads. (Notes 3-6)
- [x] Deterministic reproduction with explicit synchronization (red on the current code if the defect exists). (Note 7)
- [x] Characterize each failure mode; uninstrumented stress run as supplementary evidence. (Notes 7-8)
- [x] Propose the smallest repair with implications, risks and regression tests. (Notes 9-12)
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.
- [x] Owner review of the proposal (decisions 1-3 in Note 12): redirected to the Book-lock design.
- [x] Verify the `_spells` access inventory and the lock order of the Book-lock design on 3d184cac. (Notes
      14-16: inventory holds; R4's reader lock deadlocks against conjure)
- [x] Adapt the patch (R5); run fair-matrix, negative-control, suite, performance, transfer and rollback
      checks. (Notes 17-20)
- [x] Return the R5 diff and evidence, with the R4' alternative, for the owner's review before landing. (Note 21)
- [x] Owner decision: R6 if it holds (owner, 2026-10-11); R5 and R4' stay as measured alternatives.
- [x] Verify R6 from source (Note 26: the premise holds per Book, except that transfer leaves parked versions
      behind; the parked branch reintroduces a cleanup race).
- [x] Owner go for R6 as amended (Note 29); orientation slices read (src_components, graph).
- [x] Patch docs written and linked; R6 built in scratch with its tests and the full tree (Notes 30-31;
      single-thread cost not re-measured).
- [x] If it holds: land R6 through the patch lane (patch docs, src, tests, docs, notch, release note, graph,
      assets and llm_support last); otherwise propose the next design.

## Deliverables
- Source identity, reproduction and test results, the proposed patch scope, and any decision or blocker.

## Files / Paths Impacted
- context_compass/artifacts/spell_lookup_race_20261010/ (evidence and diagnostic tests, new; r4/ for the R4/R5
  review, proposal/repair_proposal_r5.md and proposal/proposed_patch_r5.diff)
- this ticket; context_compass/attention_board.md; context_compass/artifact_board.md
- Landing (0.2.8229): src/melder/aether/spellbook/spellbook.py, src/melder/aether/spellbook/spell.py,
  src/melder/__version__.py, tests/component/melder/spellbook/test_spellbook_component_find_spell_by_id.py (new),
  tests/unit/melder/spellbook/test_spell_cleanup_safe_index_read.py (new), release_docs/next_version_release.md,
  context_compass/system_docs (src_architecture, src_components, their indexes, graph descriptors, src_graph),
  the rebuilt src/melder/_build_assets and llm_support; artifacts/spell_lookup_race_20261010/r6/ (evidence).

## Validation
- Run (device VM, CPython 3.14.7 free-threaded, -X gil=0 and -X gil=1, pytest 9.1.1, git-archive exports of
  3d184cac; the candidate only in scratch exports): the forced diagnostics (13 tests, 10 runs per tree and GIL
  mode), the uninstrumented stress, single-thread and contended benchmarks, and 6,388 existing tests in the
  directories covering every caller (identical on 3d184cac and R1). Logs: artifacts/spell_lookup_race_20261010/runs/.
- Run for the R4/R5 review (Notes 15-20; logs under artifacts/spell_lookup_race_20261010/r4/runs/): the 17-test
  fair matrix over 3d184cac, R1, R4, R4', R5 and three negative controls (3 reps x gil=0/1), the full test tree
  on full exports of 3d184cac and of the exact R5 source (gil=0), R4' on the caller directories, single-thread
  and contended benchmarks, opposite-direction transfers with forced rollback and a watchdog (gil=0/1), and the
  forced post-publication bind failure.
- Not run: the full tree under -X gil=1, the owner's Windows tiers, hosted CI, the gauntlet, MelderOps' x40
  closure run, coverage.
- Run for the R6 landing (Notes 31-33; logs under artifacts/spell_lookup_race_20261010/r6/runs/): the 14 new
  tests on 3d184cac and R6 (gil=0/1), the full test tree on R6 (gil=0), the index, graph, asset and llm_support
  checks. Not run: the full tree under -X gil=1, a single-thread cost re-measure, the owner's Windows tiers,
  hosted CI, the gauntlet, MelderOps' x40 closure run, coverage.

## Risks / Rollback Notes
- Diagnostic tests stay outside tests/ so the suite is unchanged; nothing to roll back in src/.

## Applicable Anti-Patterns
- [x] No production change without the owner's approval of the proposed repair.
- [x] No sleep-based reproduction presented as deterministic.
- [x] No historical report presented as a current defect without a current reproduction.

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
  - artifacts/spell_lookup_race_20261010/
  - system_docs/patches/completed/find_spell_by_id_id_maps_2026_10_11/
- DISPOSITION: retain_as_reference (evidence); promote_to_documentation (patch docs, at landing)
- CLEANUP_TRIGGER: decided at turn-in (the diagnostic tests may become the repair's regression tests).

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: free-threaded dict iteration; Spellbook registry locking
- IF_UNKNOWN: ask user before implementation

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-10-10T18:18:25Z
  TYPE: FACT
  CLAIM: Source pinned. Branch codex_features2 at 3d184cac699dfb5981449e8b841624e2eea59276 ("Add scan_bind option
    parity and update version to 0.2.8228", 2026-10-10T18:11:19Z), equal to the local origin/codex_features2 ref
    (0 ahead, 0 behind; no fetch made). Melder 0.2.8228. The working tree equals HEAD in content: no modified,
    added or untracked non-ignored file; 1753 files differ only in CRLF endings. So there are no uncommitted source
    changes, and the scan/bind work and the review's hand-back are committed in 3d184cac.
  EVIDENCE:
  - context_compass/artifacts/spell_lookup_race_20261010/source_identity.txt:1-12
  - src/melder/__version__.py:12-12
  IMPACT: Every result in this ticket is against exactly this tree; nothing of the scan/bind work is at risk.
  NEXT: Read find_spell_by_id and the writers of the map it iterates.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-10T18:32:49Z
  TYPE: FACT
  CLAIM: HISTORICAL evidence, not a current reproduction. The MelderOps report records MissionBuilder
    test_concurrent_operations failing 5 of 40 runs on CPython 3.14.8t, melder 0.2.8226, 2 vCPU: three
    RuntimeError('dictionary changed size during iteration') at the find_spell_by_id loop and two AttributeError
    ('SpellIndex' object has no attribute '_spells_in_index') inside has_spell. An earlier 30-round probe failed 3
    times with the same two signatures on the path Conduit.get_spell_by_id -> _get_spell_by_id_via_aether ->
    find_spell_by_id, reached from the builder's unregister lookup while 8 threads bind, meld and unregister. The
    code it ran is HEAD's: find_spell_by_id, _get_spell_by_id_via_aether, bind, cleanup_and_remove_spell,
    _destroy_spell_index, the park/unpark writers, transaction, has_spell and SpellIndex.cleanup hash identically
    at 0.2.8226, 0.2.8227 and 0.2.8228, and the traceback lines (2036, 2038, 2805, 315) are HEAD's lines.
    probe_for_loop_race.* is a separate MelderOps race (unguarded += in ConcurrentTools.for_loop), out of scope.
  EVIDENCE:
  - priv_commandops: context_compass/artifacts/2026-10-10_melder_find_spell_race/mission_race_final_tree_x40.txt:1-25
  - priv_commandops: context_compass/artifacts/2026-10-10_full_suite_failures/mission_builder_race_repro.txt:1-88
  - priv_commandops: context_compass/artifacts/2026-10-10_full_suite_failures/repro_mission.py:22-44
  - context_compass/artifacts/spell_lookup_race_20261010/code_identity_since_0.2.8226.txt:1-27
  IMPACT: The report applies to HEAD's code unchanged, but it is a stress result from another machine and
    interpreter patch; whether HEAD fails here is UNKNOWN until reproduced.
  NEXT: Record the failure modes from the source, then force each with Event handshakes on HEAD.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-10T18:32:50Z
  TYPE: FACT
  CLAIM: Three failure modes, read from HEAD source; in each the searched spell is stable and only another spell
    changes. (a) find_spell_by_id walks self._spells.items() with no lock (its docstring says so); bind inserts
    into _spells inside its mediator transaction window, not under self._lock, and the remove and park paths pop
    under self._lock, which the walk never takes, so an insert or pop between two steps of the walk raises
    RuntimeError('dictionary changed size during iteration'). (b) cleanup_and_remove_spell and
    _destroy_spell_index pop the index under the lock but clean it after releasing it, and has_spell runs
    check_cleaned() before taking the index RLock while cleanup deletes _spells_in_index under that RLock: a walk
    holding the popped index raises AttributeError when cleanup lands between the check and the lock, or (c)
    RuntimeError('SpellIndex has already been cleaned. ') when it lands before the check. The docstring's Raises
    names only a cleaned Spellbook.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:1990-2041
  - src/melder/aether/spellbook/spellbook.py:5176-5471
  - src/melder/aether/spellbook/spellbook.py:4476-4551
  - src/melder/aether/spellbook/spellbook.py:591-709
  - src/melder/aether/spellbook/spellbook.py:3972-4017
  - src/melder/aether/spellbook/spellbook.py:1461-1522
  - src/melder/aether/spellbook/bind/spell_index.py:118-138
  - src/melder/aether/spellbook/bind/spell_index.py:288-315
  - src/melder/utilities/general_base/cleanable.py:129-144
  IMPACT: (a) needs a stable view of _spells for the walk; (b) and (c) need the membership probe to treat a
    concurrently cleaned index as a non-owner instead of raising. Whether either needs the free-threaded build is
    UNKNOWN; the forced reproductions do not depend on it and the stress run covers gil=0 and gil=1.
  NEXT: Size the other _spells readers, then write the Event-synchronized diagnostics.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-10T18:32:51Z
  TYPE: FACT
  CLAIM: Sizing. Writes to _spells use two exclusion mechanisms: bind writes in its transaction window without
    self._lock, the remove/park/unpark/destroy writers hold self._lock. So the readers that walk under self._lock
    (index-id lookup, inspect_spell, _check_all_spells) are excluded from pops but not from a concurrent bind
    insert, and find_spell_by_id and the conjure-tail Nexus walk hold neither. The public `spells` property
    returns a live MappingProxyType over the same dict; Meld holds that dict as _owned_spells and only calls .get.
    The walk-plus-has_spell shape recurs: _find_contracted_spell_by_id walks a contracted map unlocked, and search
    finds has_spell walks in aetheric_frame.py:1178, conduit.py:4048, conduit_ward.py:2547/2550/3537,
    contract.py:484, transfer_of_ownership.py:607 and command_system.py:885 - located, not read, so their locking
    is UNKNOWN.
  EVIDENCE:
  - context_compass/artifacts/spell_lookup_race_20261010/spells_map_access_sites.txt:1-35
  - src/melder/aether/spellbook/spellbook.py:1880-1899
  - src/melder/aether/spellbook/spellbook.py:6082-6107
  - src/melder/aether/spellbook/spellbook.py:2914-2940
  - src/melder/aether/conduit/meld/meld.py:284-284
  - src/melder/aether/conduit/meld/meld.py:1993-1998
  IMPACT: Locking the walk alone does not exclude bind's insert; a one-call dict.copy() does. A has_spell-level
    repair would also cover the sibling walks for (b) and (c), not their own (a) exposure.
  NEXT: Read the archived prior-art epic (the rolled-back locked reader) before writing the diagnostics.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-10T18:34:01Z
  TYPE: FACT
  CLAIM: Prior art and the other half of the reported path. The archived 2026-06-14 frame spell-registry epic hit
    the same iterate-while-insert race; its lock-serialized fix was correct but the owner rolled it back for a
    gauntlet regression (~820 ms vs ~650 ms), and the accepted design kept the writers free of a wide lock and
    accepted a cold-reader residual pending a reader-plus-writer stress test. On HEAD the frame half of the
    MelderOps path is locked on both sides: Aether._get_conduit_by_spell_id calls
    AethericFrame.find_conduit_id_for_spell, which walks _spell_registry under frame._lock, and every frame
    registry mutator takes that lock; both removal paths unregister the index from the frame before cleaning it,
    so that walk never meets a cleaned index. The race is in the second half, Spellbook.find_spell_by_id.
  EVIDENCE:
  - context_compass/tickets/epics/archive/2026-06-14_aether_frame_spell_registry_concurrent_access_race_epic.md:200-256
  - context_compass/tickets/epics/archive/2026-06-14_aether_frame_spell_registry_concurrent_access_race_epic.md:257-312
  - src/melder/aether/spellbook/spellbook.py:2778-2805
  - src/melder/aether/aether.py:2478-2517
  - src/melder/aether/aether.py:2680-2760
  - src/melder/aether/aetheric_frame/aetheric_frame.py:1060-1180
  - src/melder/aether/spellbook/spellbook.py:667-702
  - src/melder/aether/spellbook/spellbook.py:4002-4017
  IMPACT: The repair should add no lock to bind's or removal's write path (owner precedent) and keep the lookup
    lock-free: one-call snapshot of the map for (a), a per-index probe that is safe against a concurrent cleanup
    for (b) and (c). Its cost must be measured before it is proposed.
  NEXT: Write the Event-synchronized diagnostics (red on HEAD), then measure the candidate in a scratch copy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-10T18:38:10Z
  TYPE: FACT
  CLAIM: Callers, for the cost of any repair. Melder reaches find_spell_by_id from the Phase-4 ambiguity report
    (only when a spell is refused), restore and graft binds, and through Conduit.get_spell_by_id from ward link,
    contract and transfer resolution and Conduit._resolve_transfer_spell. Search finds no caller in conduit/meld,
    conduit/creations, conduit/spell_space or the codegen creation runtime, so the warm meld door does not run
    it. MelderOps calls it after every builder bind and unregister (its report). A per-call O(n) snapshot
    therefore lands on cold Melder paths and on MelderOps registration; whether any gauntlet scope cycle reaches
    a ward caller is UNKNOWN (the gauntlet is owner-run).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/ambiguous_provider_strategy.py:163-172
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2191-2191
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2431-2431
  - src/melder/crystallizer/crystal_loader_system/graft_runner.py:423-423
  - src/melder/aether/conduit/conduit.py:3097-3131
  - src/melder/aether/conduit/conduit.py:4414-4447
  IMPACT: The snapshot's cost needs a micro-benchmark at realistic book sizes, not a gauntlet claim.
  NEXT: Write the Event-synchronized diagnostics and run them on a git-archive export of HEAD.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-10T18:41:46Z
  TYPE: MEASURE
  CLAIM: CURRENT defect, reproduced deterministically on HEAD 3d184cac (0.2.8228, git archive export) with CPython
    3.14.7 (free-threaded build) under both -X gil=0 and -X gil=1. The diagnostics pause the lookup thread with
    Event handshakes inside the find_spell_by_id walk and change a DIFFERENT spell from the test thread. All six
    contract tests fail and all five characterization tests pass, identically in 10 of 10 runs per GIL mode: a
    bind or a removal during the walk raises RuntimeError('dictionary changed size during iteration'), also through
    Conduit.get_spell_by_id on a dynamic root (the MelderOps path); a cleanup between has_spell's check and lock
    raises the MelderOps AttributeError verbatim; a cleanup before the check raises RuntimeError('SpellIndex has
    already been cleaned. '). Removing the searched spell itself mid-walk raises the AttributeError too.
  EVIDENCE:
  - context_compass/artifacts/spell_lookup_race_20261010/diagnostics/test_find_spell_by_id_race.py:1-468
  - context_compass/artifacts/spell_lookup_race_20261010/runs/head_gil0.log:1-177
  - context_compass/artifacts/spell_lookup_race_20261010/runs/head_gil1.log:1-185
  - context_compass/artifacts/spell_lookup_race_20261010/runs/head_repeat_10x_per_gil.log:1-21
  IMPACT: The reported failure exists on HEAD, needs no free-threaded build and is not an artefact of the MelderOps
    test. The six contract tests are the proposed regression tests.
  NEXT: Run the uninstrumented Barrier-started stress for rates, then try the candidate repair in a scratch copy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-10-10T18:45:15Z
  TYPE: MEASURE
  CLAIM: A fourth failure mode, worse than the exceptions: a SILENT MISS. A removal plus a bind between two steps of
    the walk leave the dict's size unchanged but resize it, and CPython's iterator then skips the searched entry
    without raising, so find_spell_by_id answers None for a spell that is still registered (forced as mode d,
    plain-dict form in dict_skip_probe; both GIL modes). The diagnostics file v2 adds it: 7 contract tests red, 6
    characterization tests green, identically in 10 of 10 runs per GIL mode. The uninstrumented Barrier-started
    stress on a dynamic root (4 writers binding and removing their own spells, 4 readers calling
    Conduit.get_spell_by_id on a stable spell, 40 rounds, nproc 2) failed every round under -X gil=0 (1650 size-change
    RuntimeErrors and 4 wrong None results in 4,111,061 lookups) and no round under -X gil=1 (0 in 6,756,101).
  EVIDENCE:
  - context_compass/artifacts/spell_lookup_race_20261010/diagnostics/test_find_spell_by_id_race.py:1-548
  - context_compass/artifacts/spell_lookup_race_20261010/runs/head_v2_gil0.log:1-204
  - context_compass/artifacts/spell_lookup_race_20261010/runs/head_v2_gil1.log:1-212
  - context_compass/artifacts/spell_lookup_race_20261010/runs/head_v2_repeat_10x_per_gil.log:1-21
  - context_compass/artifacts/spell_lookup_race_20261010/runs/dict_skip_probe.log:1-5
  - context_compass/artifacts/spell_lookup_race_20261010/runs/stress_head_gil0.log:1-48
  - context_compass/artifacts/spell_lookup_race_20261010/runs/stress_head_gil1.log:1-46
  IMPACT: Catching the exception at the caller (a retry around the lookup) would not cover this mode; the walk
    itself must read a stable view. Under the GIL the race is reachable (forced tests) but was not observed in the
    stress, which matches the MelderOps report coming from a free-threaded run.
  NEXT: Apply the candidate repair to a second scratch export and run the diagnostics and the stress against it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-10-10T19:11:59Z
  TYPE: MEASURE
  CLAIM: First candidate, R1a (walk self._spells.copy() and probe each index with a new non-raising
    SpellIndex._has_spell_unless_cleaned), applied only to a scratch export: the 7 contract tests turn green and
    the 6 characterization tests red in 10 of 10 runs per GIL mode, and the stress drops to 0 failures. But with
    2 readers and 2 writers on 2 vCPU its reader throughput fell to about half (gil=0, ~700k -> ~370k lookups/s)
    and a third (gil=1, ~320k -> ~110k). A dict-level probe isolates it: under concurrent writers, a live loop
    raised 1033 RuntimeErrors and missed a never-touched key 23 times, tuple(d.items()) is not atomic either
    (1291 / 25), while dict.copy() and list(d.items()) stayed exact, list(d.items()) at 955 ns per read against
    2622 ns for dict.copy() (gil=0). CPython 3.14's list_extend takes the dict's critical section around
    list_extend_dictitems for a dict items view, which builds the pairs in C with no Python code in between.
  EVIDENCE:
  - context_compass/artifacts/spell_lookup_race_20261010/proposal/variant_r1a_dict_copy.diff:1-110
  - context_compass/artifacts/spell_lookup_race_20261010/runs/cand_v3_gil0.log:1-125
  - context_compass/artifacts/spell_lookup_race_20261010/runs/v3_repeat_10x.log:1-42
  - context_compass/artifacts/spell_lookup_race_20261010/runs/stress_cand_gil0.log:1-46
  - context_compass/artifacts/spell_lookup_race_20261010/runs/contended_throughput.log:1-13
  - context_compass/artifacts/spell_lookup_race_20261010/runs/dict_snapshot_probe.log:1-13
  - https://raw.githubusercontent.com/python/cpython/3.14/Objects/listobject.c (_list_extend, list_extend_dictitems)
  IMPACT: The snapshot must be list(self._spells.items()), not dict.copy() and not tuple(...); R1a is kept as a
    measured, rejected variant.
  NEXT: Measure R1 with list(items()) the same way, plus a keys-only variant for the latency trade-off.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-10T19:11:59Z
  TYPE: MEASURE
  CLAIM: R1 (walk list(self._spells.items()) and probe with _has_spell_unless_cleaned), scratch export only: the 7
    contract tests pass and the 6 characterization tests fail in 10 of 10 runs per GIL mode; the stress shows 0
    failures in 3,978,741 (gil=0) and 5,818,337 (gil=1) lookups; contended reader and writer throughput match
    HEAD within run-to-run noise. Single-thread cost against HEAD (median of two alternated runs): an early hit
    pays the snapshot, +20..50 ns at 1 spell, +0.1 us at 8, +0.75..0.9 us at 64, +5.5..5.7 us at 512; a full walk
    or a miss is within -4%..+2% (the cheaper probe offsets the copy). A keys-only variant (list(self._spells)
    plus one .get on the hit) costs +1.3 us for an early hit at 512 and walks about 15% faster, at about 5-8%
    lower contended reader throughput and one more read of the live map.
  EVIDENCE:
  - context_compass/artifacts/spell_lookup_race_20261010/proposal/proposed_patch_r1.diff:1-111
  - context_compass/artifacts/spell_lookup_race_20261010/runs/cand_r1_v3_gil0.log:1-125
  - context_compass/artifacts/spell_lookup_race_20261010/runs/cand_r1_v3_gil1.log:1-133
  - context_compass/artifacts/spell_lookup_race_20261010/runs/cand_r1_v3_repeat_10x.log:1-21
  - context_compass/artifacts/spell_lookup_race_20261010/runs/stress_cand_r1_gil0.log:1-46
  - context_compass/artifacts/spell_lookup_race_20261010/runs/stress_cand_r1_gil1.log:1-46
  - context_compass/artifacts/spell_lookup_race_20261010/runs/contended_throughput_r1.log:1-13
  - context_compass/artifacts/spell_lookup_race_20261010/runs/bench_r1_gil0.log:1-53
  - context_compass/artifacts/spell_lookup_race_20261010/runs/bench_r1_gil1.log:1-53
  - context_compass/artifacts/spell_lookup_race_20261010/runs/bench_variant_keys_gil0.log:1-28
  IMPACT: R1 fixes all four modes with no contended slowdown and a bounded single-call cost on cold paths;
    the keys-only variant is the option if early-hit latency on large books matters more than simplicity.
  NEXT: Compare the existing unit, component and integration directories on head and R1, then write the proposal.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-10T19:22:05Z
  TYPE: MEASURE
  CLAIM: R1 changes nothing else that the existing tests see: the directories covering every caller of
    find_spell_by_id and SpellIndex (unit spellbook 2343, unit aether/conduit 1205, component spellbook 799,
    component aether/conduit 763, integration spellbook 617, aether/conduit 110, conduit 275, crystallizer 276;
    6,388 tests) give identical results on 3d184cac and on R1 under -X gil=0: all passed, plus the same 2
    skipped, 2 xpassed and 3 xfailed. A same-session contended comparison repeats the R1a finding (dict.copy
    readers ~320-330k/s at gil=0 and ~150k/s at gil=1 against ~610k and ~400k for 3d184cac and R1); over six
    alternated windows at gil=0, R1's median writer throughput is 1404 pairs/s against 1348 for 3d184cac and its
    median reader throughput is 2.6% lower, inside the run-to-run spread.
  EVIDENCE:
  - context_compass/artifacts/spell_lookup_race_20261010/runs/suite_dirs_head_vs_r1.log:1-19
  - context_compass/artifacts/spell_lookup_race_20261010/runs/contended_copy_vs_list.log:1-13
  - context_compass/artifacts/spell_lookup_race_20261010/runs/contended_writer_check_gil0.log:1-13
  - context_compass/artifacts/spell_lookup_race_20261010/runs/README.txt:1-25
  IMPACT: No regression found in the touched area; the full tree, the Windows tiers, hosted CI and the gauntlet
    are Not run (owner-owed).
  NEXT: Write the repair proposal with its decisions and hand the lane to the owner for review.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-10T19:22:05Z
  TYPE: DECISION_REQUEST
  CLAIM: Proposed repair R1, not implemented. find_spell_by_id walks list(self._spells.items()), a one-call
    snapshot, and probes each index with a new internal SpellIndex._has_spell_unless_cleaned that reads the
    cleaned flag and the member set under the index lock and answers False for a cleaned index. It fixes all four
    modes; it adds no lock, holds none across the walk and adds no lock-order edge (each index RLock is taken
    alone, as has_spell takes it today); bind, removal and park paths are untouched; has_spell keeps its contract.
    Semantics become those of the snapshot instant (a later bind is not seen; a concurrently removed searched spell
    answers None or the spell; a racing notch can return the outgoing spell), all within the documented contract.
    Cost: early hits +0.1 us at 8 spells to +5.7 us at 512, full walks and misses within -4%..+2%, contended
    throughput equal to today. Regression tests: the 7 forced contract tests as a component test file and unit
    tests for the new probe. Decisions: (1) approve R1, or R1c (keys-only snapshot: faster early hits, one more
    read of the live map); (2) R2 (SpellIndex check-then-lock pattern) and R3 (the other _spells walkers, same
    mechanism by reading, not reproduced) as follow-up tasks, recommended, or folded in; (3) on approval the
    landing is a source change: patch lane (architecture, component and code-description docs), the next notch
    above 0.2.8228, a release-note entry, system docs and graph, then assets and llm_support last. D-10, D-11 and
    D-20 stay separate, open and untouched.
  EVIDENCE:
  - context_compass/artifacts/spell_lookup_race_20261010/proposal/repair_proposal.md:1-144
  - context_compass/artifacts/spell_lookup_race_20261010/proposal/proposed_patch_r1.diff:1-111
  - context_compass/artifacts/spell_lookup_race_20261010/diagnostics/test_find_spell_by_id_race.py:1-591
  - src/melder/aether/spellbook/spellbook.py:1990-2041
  - src/melder/aether/spellbook/bind/spell_index.py:288-315
  IMPACT: The MelderOps lane stays blocked until a Melder release carries a repair; nothing is implemented until
    the owner chooses.
  NEXT: Owner reviews the proposal and answers decisions 1-3; on approval, open the patch lane before any code.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-10-10T21:10:16Z
  TYPE: DECISION
  CLAIM: Owner redirect after Note 12: instead of R1, the reviewer's design R4 reuses the existing Spellbook._lock in
    two places - held across find_spell_by_id's existing live traversal, and taken briefly around bind's
    active-map insertion - with no new lock, no snapshot, no new index helper and has_spell unchanged; returned
    Spells are documented as borrowed references. melder_1 is to verify the reviewer's access inventory (nine live
    mutation statements, eight already under the Book lock), adapt R4 on 3d184cac in scratch, and return the diff
    with regression evidence before landing. PLAN: (1) inventory every mutation and walk of Spellbook._spells in
    src/, aliases included, with the lock each holds; (2) map the lock order the two new acquisitions create - what
    callers of find_spell_by_id hold, what bind holds at publication, what the Book lock already nests; (3) build R4
    and a fair harness whose writers may block on the Book lock, with the reader-lock-only negative control; (4)
    suites, single-thread and contended performance, opposite-direction transfer and forced bind rollback.
  EVIDENCE: context_compass/tickets/tasks/2026-10-10_investigate_spell_lookup_by_id_race_task.md:31-44
  IMPACT: R1 is no longer the proposal; its evidence stays as the comparison. R4 adds lock edges, so the lock-order
    review is the gate before any regression run means anything.
  NEXT: Inventory the _spells mutations and walks across src/, with the lock held at each.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-10T21:25:13Z
  TYPE: FACT
  CLAIM: The reviewer's mutation inventory holds on 3d184cac. Nine live statements change Spellbook._spells: four
    in spellbook.py under self._lock (removal pop 662, notch park pop 1510, notch promote insert 1572, index
    destroy pop 4003), the transfer flip (pop 1448, insert 1456) and its rollback (pop 954, insert 960) under
    SafeGuard over both Book locks, and bind's publication insert 5358, which holds no Book lock (its
    _register_owned_spell_id takes it at the next line). Book teardown clears and deletes the map under the lock
    after setting _cleaned (444, 448 via cleanup 387-391). No alias mutates it: Meld._owned_spells is read with
    .get only. Every path cleans a SpellIndex only after popping it under the Book lock (702, 4017) or inside
    teardown under the lock. So a walk that holds the lock, with bind publishing under it, meets no size change,
    no resize and no cleaned index (modes a-d). One gap stays: a teardown between the walk's unlocked
    check_cleaned and its lock acquisition leaves _spells deleted, an AttributeError.
  EVIDENCE:
  - context_compass/artifacts/spell_lookup_race_20261010/r4/spells_access_inventory.txt:1-56
  - src/melder/aether/spellbook/spellbook.py:365-392
  - src/melder/aether/spellbook/spellbook.py:400-449
  - src/melder/aether/spellbook/spellbook.py:591-709
  - src/melder/aether/spellbook/spellbook.py:1461-1583
  - src/melder/aether/spellbook/spellbook.py:3972-4017
  - src/melder/aether/spellbook/spellbook.py:5291-5471
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:929-975
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1376-1475
  - src/melder/aether/conduit/meld/meld.py:1993-1998
  IMPACT: R4's two acquisitions cover every live writer of the map. Re-checking _cleaned inside the lock (the
    repository's check-before-and-after-locking cleanup rule) turns the teardown gap into the documented
    RuntimeError for one attribute read. Walks outside the target keep today's exposure (inventory, WALKS).
  NEXT: Map the lock order R4 adds, first whether conjure holds the Book lock while Phase 4 runs on scheduler
    workers, since Phase 4's ambiguity report calls find_spell_by_id.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-10T21:28:36Z
  TYPE: MEASURE
  CLAIM: R4 as specified regresses the conjure-time ambiguity report (0.2.8224). Conjure holds the Book lock
    across the whole creation pipeline (_conjure_within_transaction_window), phase 4 runs on scheduler worker
    threads only, and AmbiguousProviderStrategy._describe_candidates calls find_spell_by_id on that Book. With
    the walk under the Book lock, the worker blocks on the lock the conjuring thread holds while that thread
    waits on the phase latch. Forced on a scratch export of 3d184cac with R4 applied literally (CPython 3.14.7t,
    -X gil=0): test_two_same_named_classes_in_two_categories_are_reported_with_both_addresses hangs the full
    60000 ms barrier and fails with PhaseTimeoutError("Phase 'validation' exceeded barrier timeout (60000 ms)")
    instead of SpellbookValidationError [AMBIGUOUS_PROVIDER]; on 3d184cac it passes in 0.58 s. A late bind in
    a dynamic world (test_guard_two_providers_of_the_annotated_type_still_raise_ambiguity) still passes,
    because post-conjure phase 4 runs inline on the binding thread.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:7012-7112
  - src/melder/aether/spellbook/spellbook_creation_system.py:2084-2169
  - src/melder/utilities/synchronization/phase_scheduler.py:758-906
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/ambiguous_provider_strategy.py:144-178
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:668-668
  - context_compass/artifacts/spell_lookup_race_20261010/r4/r4_literal.diff:1-56
  - context_compass/artifacts/spell_lookup_race_20261010/r4/runs/r4_literal_ambiguous_conjure_gil0.log:170-187
  - context_compass/artifacts/spell_lookup_race_20261010/r4/runs/head_ambiguous_conjure_and_late_bind_gil0.log:1-2
  IMPACT: R4 cannot land as written. Every refused conjure with an ambiguous provider becomes a 60 s stall and
    an opaque timeout, the exact report the 0.2.8224 lane added. The reviewer's 66+10 checks did not include the
    existing suite, which carries this test. The general rule it breaks: a Book-lock holder that waits on
    another thread excludes that thread from find_spell_by_id.
  NEXT: List every place the Book lock is held while the holder waits on another thread or another lock that a
    find_spell_by_id caller can hold, then decide whether R4 can be adapted or R1 stays the proposal.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-10-10T21:34:54Z
  TYPE: MEASURE
  CLAIM: Any reader-side Book lock fails the same way, and the failure is not limited to Melder's own phase 4.
    Conjure fires the conduit lifecycle hooks inside the same Book-lock region (SpellbookCreationSystem.conjure:
    pre-created, then activation and post-created), so a user hook that waits for a lookup made on another
    thread cannot complete. probe_conjure_hook_foreign_lookup (post-created hook starts a thread that calls
    find_spell_by_id and waits on its Event, bounded at 5 s only as a deadlock detector): 3d184cac and R1 finish
    inside the hook (0.0 s), R4 and R4b (lock held only around a one-call snapshot) do not (5.0 s wait; the
    lookup completes only after conjure releases the lock), identically under -X gil=0 and gil=1; an unbounded
    join would hang for ever. R4b also fails the conjure-time ambiguity test with the same 60000 ms
    PhaseTimeoutError, while R1 passes it in 0.59 s. Meld-time structural reruns call phase 4 inline under the
    spell's rebuild window and spell._lock, so a reader lock would add those two edges into the Book lock too.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook_creation_system.py:210-300
  - src/melder/aether/conduit/meld/meld.py:922-948
  - context_compass/artifacts/spell_lookup_race_20261010/r4/diagnostics/probe_conjure_hook_foreign_lookup.py:1-70
  - context_compass/artifacts/spell_lookup_race_20261010/r4/runs/probe_conjure_hook_foreign_lookup.log:1-8
  - context_compass/artifacts/spell_lookup_race_20261010/r4/runs/r4b_ambiguous_conjure_gil0.log:1-186
  - context_compass/artifacts/spell_lookup_race_20261010/r4/runs/r1_ambiguous_conjure_gil0.log:1-2
  - context_compass/artifacts/spell_lookup_race_20261010/r4/scripts/apply_r4b_brief_reader_lock.py:1-27
  IMPACT: find_spell_by_id must stay lock-free on the reader side: conjure holds the Book lock while it waits on
    phase workers and runs user callbacks, and both can call the lookup from another thread. R4's writer half is
    different: bind's next statement (_register_owned_spell_id) already takes the same lock with the same locks
    and claims held, so locking the two insertions adds no lock-order edge.
  NEXT: Build R5 in scratch - R1's lock-free reader (one-call snapshot, cleanup-safe probe) plus R4's narrow
    publication lock in bind - and run the fair matrix, suites, performance, transfer and rollback checks on it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-10-10T21:41:26Z
  TYPE: PLAN
  CLAIM: Two adaptations of R4 are measurable, and they trade differently. R5 (built in scratch): R1's lock-free
    reader - list(self._spells.items()) and SpellIndex._has_spell_unless_cleaned - plus R4's bind publication
    lock, widened to _register_owned_spell_id so the four active maps publish together as the notch promote path
    does; it adds no lock-order edge. R4': R4 with phase 4's ambiguity report resolving candidates through
    _spell_id_pool.get instead of find_spell_by_id (a second file); it keeps linearizable lookups but leaves the
    conjure-hook constraint and reader serialization. HYPOTHESIS to force: a lock-free reader can see a notch's
    intermediate state - _apply_notch pops the index (_deactivate_owned_spell) and re-inserts it
    (_reactivate_owned_spell) inside one Book-lock region with _cleanup_creation_context between - so R5, R1 and
    3d184cac answer None for that lineage there, where R4 and R4' block and return the incoming spell. Program:
    a fair matrix whose writers run on their own threads and may block on an instrumented Book lock (modes a1,
    a2, b, c, p, d, self-removal, notch, notch with resize, notch gap, transfer, transfer with forced rollback,
    membership move, bind-hook and conjure-hook foreign lookups, a Book-locked walker against a bind) over
    3d184cac, R1, R4, R4', R5 and three negative controls (R5 without the snapshot, R5 without the probe, R4's
    reader lock without the writer lock), both GIL modes, repeated; then the suites, single-thread and contended
    performance, opposite-direction transfers with a watchdog, and forced rollback with a lock-leak check.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:3701-3841
  - src/melder/aether/spellbook/spellbook.py:1266-1323
  - src/melder/aether/spellbook/spellbook.py:5176-5471
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:380-447
  - context_compass/artifacts/spell_lookup_race_20261010/proposal/proposed_patch_r1.diff:1-111
  IMPACT: The owner's choice between lock-free snapshot semantics (R5) and guarded selection (R4') needs the
    notch-gap result and the contended reader cost side by side; nothing lands either way.
  NEXT: Write the fair-matrix test file under artifacts/.../r4/diagnostics/ and the R4' and control trees.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-10T21:50:43Z
  TYPE: MEASURE
  CLAIM: Fair matrix (17 tests; probe and writer on their own threads, Book locks watched; Event handshakes,
    watchdogs only), 3 repetitions x -X gil=0/1 per tree, every cell identical in all 6 runs. 3d184cac fails 14
    (passes n1, h1, h2). R4 and R4' fail only h2 (a conduit post-created hook waiting on a foreign-thread
    lookup). R5 fails only g1 (a lookup inside a notch, between its pop and its insert, answers None) and m1 (a
    lookup racing a membership move of its id answers None) - both also fail on 3d184cac, so R5 leaves them as
    they are; a reader holding the Book lock closes both. R1 fails g1, m1 and l1 (a Book-locked index-id walk
    breaks when a bind past its earlier locking publishes into it; R5's publication lock closes that). Negative
    controls: R5 without the snapshot fails 13, R5 without the cleanup-safe probe fails b, c and self-removal,
    and R4's reader lock without the publication lock fails a3 and l1 - the reviewer's control, reproduced. The
    forced transfer rollback (t2) resizes the owner map on 3d184cac and silently hides the searched spell; every
    candidate passes it and releases both Book locks. R4' also breaks 3 unit tests that stub find_spell_by_id.
  EVIDENCE:
  - context_compass/artifacts/spell_lookup_race_20261010/r4/diagnostics/test_lookup_fair_matrix.py:1-818
  - context_compass/artifacts/spell_lookup_race_20261010/r4/runs/matrix_table.txt:1-21
  - context_compass/artifacts/spell_lookup_race_20261010/r4/runs/r4p_ambiguity_files_gil0.log:150-157
  - context_compass/artifacts/spell_lookup_race_20261010/r4/scripts/make_variants.py:1-58
  IMPACT: The choice is lock-freedom (R5: never blocks, fixes every reported mode, no new lock edge, leaves the
    notch and membership-move gaps 3d184cac already has) against linearizable lookups (R4': closes those gaps,
    keeps the conduit-hook deadlock class, touches phase 4 and its unit tests, serializes readers).
  NEXT: Measure single-thread and contended cost of R5 and R4' against 3d184cac, then the suites and the
    opposite-direction transfer watchdog.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-10-10T21:57:21Z
  TYPE: MEASURE
  CLAIM: Cost, device VM (nproc 2, CPython 3.14.7t), same session, trees alternated. Contended, 3 s windows x3,
    Conduit.get_spell_by_id readers on a dynamic root: gil=0 with 2 readers and 2 bind/remove writers - 3d184cac
    696-731k lookups/s with 768-814 reader failures per window, R5 688-735k with none, R4' 610-650k with none
    (about -10%), writers 1785-1816, 1786-1839 and 1728-1751 pairs/s; gil=0 readers only - 648-666k, R5 554-583k
    (-12..15%: two readers contend on the dict's critical section in list(items())), R4' 610-628k (-5%); gil=1 -
    all three inside run-to-run noise (284-353k). Single thread (median ns): R5 adds 15-22 ns at 1 spell and an
    O(n) snapshot to an early hit (+90 ns at 8, +0.6 us at 64, +5.1-5.3 us at 512), full walks and misses within
    -1..+3%; R4' adds a flat 48-60 ns (the RLock) and walks within +0.1..2% (one gil=1 outlier, +443 ns at 8).
  EVIDENCE:
  - context_compass/artifacts/spell_lookup_race_20261010/r4/runs/contended_r5_r4p_gil0.log:1-9
  - context_compass/artifacts/spell_lookup_race_20261010/r4/runs/contended_r5_r4p_gil1.log:1-9
  - context_compass/artifacts/spell_lookup_race_20261010/r4/runs/contended_readers_only_gil0.log:1-9
  - context_compass/artifacts/spell_lookup_race_20261010/r4/runs/bench_table_gil0.txt:1-14
  - context_compass/artifacts/spell_lookup_race_20261010/r4/runs/bench_table_gil1.txt:1-14
  - context_compass/artifacts/spell_lookup_race_20261010/diagnostics/contended_throughput.py:1-60
  IMPACT: Neither candidate is free and neither is costly on these cold paths (no meld door calls the lookup).
    R5 pays per call in proportion to the Book's size on an early hit; R4' pays a flat lock and loses about a
    tenth of contended reader throughput on two cores, more as readers grow. Cost does not decide between them.
  NEXT: Run the existing suites on R5 (and R4' on the directories that cover the lookup's callers) against
    3d184cac, then the opposite-direction transfer watchdog.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-10T22:12:02Z
  TYPE: MEASURE
  CLAIM: Regressions. Full test tree (23 chunks, every directory under tests/, full git-archive exports of
    3d184cac with and without R5, -X gil=0): 13,640 passed, 31 skipped, 17 xfailed, 2 xpassed on both, nothing
    else. R4' on the directories covering the lookup's callers: identical to 3d184cac except the 3 unit tests of
    the ambiguity strategy, which stub find_spell_by_id. Opposite-direction transfers (two dynamic roots, 6 movers
    each way, 2 readers, 60 s watchdog, 3 rounds per row, gil=0/1, with and without every 2nd transfer forced to
    fail after its flip): no deadlock in any row for 3d184cac, R5 or R4'; every forced failure rolled back,
    every mover ends owned by exactly one Book and both Book locks are free afterwards; stable-spell lookups never
    fail on R5 or R4', while 3d184cac raises the size-change RuntimeError at gil=0. In every tree, looking up a
    spell that is between owners through Conduit.get_spell_by_id raises ValueError("Spell version ... not found
    in any conduit.") from Aether._get_conduit_by_spell_id - a separate, pre-existing contract gap: that method's
    Spellbook wrapper and Conduit.get_spell_by_id document None for a miss.
  EVIDENCE:
  - context_compass/artifacts/spell_lookup_race_20261010/r4/runs/suites/summary_full_tree_gil0.txt:1-46
  - context_compass/artifacts/spell_lookup_race_20261010/r4/runs/suites/summary_r4p_caller_dirs_gil0.txt:1-8
  - context_compass/artifacts/spell_lookup_race_20261010/r4/runs/opposite_transfer_table.txt:1-14
  - context_compass/artifacts/spell_lookup_race_20261010/r4/diagnostics/opposite_transfer_watchdog.py:1-182
  - src/melder/aether/aether.py:2478-2517
  - src/melder/aether/spellbook/spellbook.py:2584-2610
  - src/melder/aether/conduit/conduit.py:3097-3131
  IMPACT: R5 changes nothing the suite sees and holds up under opposite transfers and forced rollback. The
    ValueError on a between-owners lookup reaches MelderOps' path too; it needs its own decision (None or a
    documented raise) and stays out of this repair.
  NEXT: Write the R5 proposal and diff (with the R4' alternative and the decision), sync the ticket summary,
    boards and artifact index, and return it to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-10T22:19:40Z
  TYPE: DECISION_REQUEST
  CLAIM: R4 as written is not landable (Notes 15-16). Proposed instead: R5 - R1's lock-free reader (one-call
    list(items()) snapshot, SpellIndex._has_spell_unless_cleaned) plus R4's narrow publication lock in bind over
    the four active maps; 2 files, 3 methods, no new lock, no lock-order edge, has_spell unchanged, returned Spells
    documented as borrowed references. Evidence: fair matrix 15/17 (the two misses, a lookup overlapping a notch
    or a membership move of its own lineage, fail identically on 3d184cac and are documented as the residual);
    full test tree identical to 3d184cac on the exact proposed source; opposite transfers and forced rollbacks
    without deadlock or leaked lock; cost +15-22 ns per call, O(n) on an early hit (+5 us at 512 spells), equal
    contended throughput with writers. Decisions: (1) R5, or R4' (linearizable; keeps a conduit-hook deadlock
    class, changes phase 4 and 3 unit tests, about -10% contended reader throughput); (2) follow-ups kept separate -
    Conduit.get_spell_by_id's undocumented ValueError for an id no conduit claims, R2, and the reviewer's list
    (permissions, command-system, foreign-Book, contract-proxy) plus the other unlocked walkers; (3) on approval,
    the landing order of proposal section 8. MelderOps' baseline, D-10, D-11 and D-20 untouched.
  EVIDENCE:
  - context_compass/artifacts/spell_lookup_race_20261010/proposal/repair_proposal_r5.md:1-149
  - context_compass/artifacts/spell_lookup_race_20261010/proposal/proposed_patch_r5.diff:1-142
  - context_compass/artifacts/spell_lookup_race_20261010/r4/README.txt:1-36
  IMPACT: Nothing lands until the owner chooses; the MelderOps lane stays blocked until a Melder release carries
    a repair.
  NEXT: Owner answers decisions 1-3; on approval open the patch lane before any source edit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-10-10T23:53:50Z
  TYPE: FACT
  CLAIM: Owner challenge after Note 21 (is R4's stall real in the whole, mediated system?) and its origin. Public
    Spellbook.conjure() opens the mediator's CONJURE transaction, then _conjure_within_transaction_window holds
    Spellbook._lock across the creation pipeline; the mediator orders transactions, not lookups, so it does not
    change Note 15. The conflict comes from e8b888745 (0.2.8224, 2026-10-04), which added
    ambiguous_provider_strategy.py (196 new lines; validation_system.py +4): its _describe_candidates calls
    spellbook.find_spell_by_id per candidate to print addresses in the [AMBIGUOUS_PROVIDER] report, in phase 4
    on a phase worker while the conjure thread holds the Book lock. find_spell_by_id itself exists since at least
    2026-04-12; 8224 added this caller. Unlocked (today) the call is harmless; R4's lock turns it into a
    self-wait until the 60 s phase timeout. Scope correction: the evidence covers this report path and a
    constructed hook, not conjure in general. The full-tree R4 rerun was dropped at the owner's request (usage);
    this note rests on git history and source reads only.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:6753-6782
  - src/melder/aether/spellbook/spellbook.py:7012-7106
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/ambiguous_provider_strategy.py:163-166
  - tests/integration/melder/aether/conduit/test_annotation_category_collision_integration.py:418-440
  IMPACT: Narrows Note 21's objection to R4 to one caller added in 8224; R5, or R4' (phase 4 reads
    _spell_id_pool), removes it. Note 21's decisions are unchanged.
  NEXT: Owner answers Note 21.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-11T00:02:49Z
  TYPE: FACT
  CLAIM: Why find_spell_by_id walks (owner question: why not index directly). Its contract resolves ANY id in a
    spell's version lineage, superseded and parked ids included, to the live spell; old ids live only in each
    SpellIndex's member set (_spells_in_index; select_new_id keeps the old id a member). The Book's id maps hold
    current ids only: a notch pops the old id and inserts the new one in _spells_by_id and _spell_id_pool, and
    _spell_id_pool also holds contracted spells, which this lookup excludes. A direct index is possible two ways:
    (a) fast path - _spells_by_id.get(spell_id) first (one atomic get, every current id), walking a snapshot
    only for old ids; (b) a Book-level member-id -> SpellIndex map kept by every membership writer, so the
    lookup is two atomic gets, no loop and no lock; (b) also closes the membership-move gap (m1), not the notch
    gap (g1). Not yet inventoried: every writer of SpellIndex membership.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:1990-2041
  - src/melder/aether/spellbook/spellbook.py:1196-1207
  - src/melder/aether/spellbook/spellbook.py:1711-1712
  - src/melder/aether/spellbook/bind/spell_index.py:180-185
  IMPACT: A candidate that removes the walk instead of making it safe; the owner decides whether to pursue it.
  NEXT: Owner decides; if yes, inventory the membership writers (read-only) before any design.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-11T00:10:46Z
  TYPE: DECISION_REQUEST
  CLAIM: R6 - answer find_spell_by_id from the Book's id maps instead of walking (owner: use the existing
    spell_id access; notch is ordered by the mediator). Every owned version is in _spells_by_id (ACTIVE,
    "meld-by-id") or _inactive_spells (parked by _deactivate_owned_spell and bind_inactive), and each Spell
    carries spell.spell_index, which add-to-index repoints (it only moves parked spells). Lookup:
    _spells_by_id.get(id), else _inactive_spells.get(id) -> spell_index -> _spells.get(index). O(1), no lock, no
    iteration: no size-change error, no skipped entry, no R4 lock question, and the membership-move gap (m1)
    closes. A lookup overlapping a notch can still briefly miss, as today. _update_owned_spell_id, the re-key
    that drops an old id, has no caller. The index-id walk and R5's bind lock for it stay a separate item.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:332-337
  - src/melder/aether/spellbook/spellbook.py:1461-1583
  - src/melder/aether/spellbook/spellbook.py:3876-3950
  - src/melder/aether/spellbook/spellbook.py:5042
  - src/melder/aether/spellbook/spell.py:408
  IMPACT: Removes the walk instead of guarding it; supersedes R5 and R4' for this method if the owner agrees.
  NEXT: Owner approves R6; then the patch lane, the change and its race tests (fair-matrix modes, a cleaned
    parked spell mid-lookup).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-11T00:19:55Z
  TYPE: ASSUMPTION_CHALLENGE
  CLAIM: Correction to Notes 23-24, which were written after the context compaction but before the REONBOARD (skipped,
    then completed on the owner's challenge). Note 23's "a notch pops the old id and inserts the new one" cites
    _update_owned_spell_id, which has no caller in src, so it describes no live path; the owner's premise that
    every version stays in the Book under an active or inactive id stands until the live path is read. Note 24's
    behaviour claims rest on search hits, not reads (its two single-line pointers are the tell): that
    _deactivate_owned_spell and bind_inactive park versions in _inactive_spells, that add-to-index moves only
    parked spells and repoints spell.spell_index, and that the lookup never misses a version are UNKNOWN. Its
    sketch used getattr(parked, "spell_index", None), which the overlay's attribute rule bans for owned
    attributes: R6 reads spell.spell_index directly, and a parked spell cleaned mid-lookup (spell.py deletes
    spell_index at 648, enclosing method unread) is handled only if the removal path shows the case is real.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:1144-1211
  - src/melder/aether/spellbook/spell.py:648-648
  - context_compass/agent_onboarding/user_defined/synaptic_python_developer/AGENTS.MD:138-168
  - context_compass/agent_onboarding/default/general/skills/unknowns_gate_reference.md:56-76
  IMPACT: R6 stays the owner's direction but is unverified; nothing in Notes 23-24 is promoted without the reads.
  NEXT: Read _deactivate_owned_spell and _reactivate_owned_spell, bind_inactive's parking, _apply_add_to_index and
    cleanup_spell's parked branch, then confirm or correct R6 in one note.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-11T00:56:46Z
  TYPE: FACT
  CLAIM: R6 source check. Per Book the owner's premise holds: a notch parks the outgoing version in
    _inactive_spells and promotes the incoming one under the Book lock (the index keeps both ids);
    add/remove-from-index move only parked members and repoint spell.spell_index under the lock; cleanup_spell
    drops a parked version from _inactive_spells and from the member set together under the lock; SpellIndex
    hash and equality survive cleanup. Two findings stop pure R6. (1) An ownership transfer moves only the
    active spell's four maps to the target Book; its parked versions stay in the source Book's _inactive_spells
    while the index, member set included, moves - so today the target resolves those ids and R6 would answer
    None. (2) R6's parked branch reads parked.spell_index, which Spell.cleanup deletes under the spell's lock
    after cleanup_spell has popped it outside the Book lock: a lock-free reader holding a parked spell meets the
    MelderOps AttributeError shape again. Handling it needs the spell's lock, which is not a leaf (meld-time
    reruns run phase 4 under it), or an exception handler.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:1461-1583
  - src/melder/aether/spellbook/spellbook.py:3701-3841
  - src/melder/aether/spellbook/spellbook.py:3876-3970
  - src/melder/aether/spellbook/spellbook.py:4051-4136
  - src/melder/aether/spellbook/spellbook.py:4138-4250
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1376-1503
  - src/melder/aether/spellbook/spell.py:550-648
  - src/melder/aether/spellbook/bind/spell_index.py:118-138
  - src/melder/aether/spellbook/bind/spell_index.py:397-439
  - src/melder/aether/conduit/meld/meld.py:922-948
  IMPACT: Pure R6 changes the lineage contract after a transfer and reintroduces a cleanup race; it is not
    landable as sketched.
  NEXT: Propose R7 (id-map fast path for current ids, R5's lineage walk for every other id).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-11T00:56:46Z
  TYPE: DECISION_REQUEST
  CLAIM: R7 in place of pure R6: find_spell_by_id answers a current version id from _spells_by_id (one atomic
    dict read, O(1), no lock); only an id that is not current - a superseded or parked lineage member, or an id
    this Book does not own - falls through to R5's walk (one-call list(self._spells.items()) snapshot probed
    with SpellIndex._has_spell_unless_cleaned), and R5's narrow bind publication lock stays. R7 = R5 + the fast
    path: the lineage contract (transfer included), a lock-free reader and every R5 result carry over, and the
    fast path only shortcuts ids the walk answers with the same spell, because _spells_by_id holds exactly the
    current ids and moves with _spells under the Book lock. Which ids MelderOps passes is UNKNOWN; the ambiguity
    report's own-Book candidates are current ids. Residuals as R5: a lookup inside a notch or a membership move
    of its own lineage can briefly miss. Pure O(1) for lineage ids first needs transfer to move parked versions
    with their index (separate change). On the owner's go: scratch build, the matrix retargeted so walk cases
    use lineage ids, a fast-path race test, single-thread cost, the full tree; then the patch lane and landing.
  EVIDENCE:
  - context_compass/artifacts/spell_lookup_race_20261010/proposal/proposed_patch_r5.diff:1-142
  - src/melder/aether/spellbook/spellbook.py:1100-1143
  - src/melder/aether/spellbook/spellbook.py:1461-1583
  - src/melder/aether/spellbook/spellbook.py:1990-2041
  IMPACT: Takes the O(n) walk off every current-id lookup without changing what any lookup answers.
  NEXT: Owner says go for R7, or redirects.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-11T01:02:30Z
  TYPE: ASSUMPTION_CHALLENGE
  CLAIM: Correction to Note 26 finding (1), raised by the owner: a transfer moves the whole lineage. execute() runs
    _flip_registry_and_spellbooks and then _migrate_inactive_members inside the same conduit-lock section, and
    the second moves every parked member src._inactive_spells -> tgt._inactive_spells (with _spell_ids and the
    member's book, states and owner pointers) under both Book locks, with its own rollback; its docstring says
    transfer of ownership moves an index. Note 26 had read only the flip. So the Book's id maps cover every
    lineage id after a transfer too; the only gap is the instant between flip and migration, while the lineage
    is disabled. Finding (2), the parked-branch cleanup race, stands. R6 is the proposal again, its parked branch
    reading the index through a new Spell._spell_index_unless_cleaned that takes the spell's own lock (the lock
    Spell.cleanup deletes spell_index under) and answers None once cleaned. That lock is taken only for a parked
    id and held for one read; parked spells are off every active map meld resolves through, so the only long
    holder found is a unique build already running when a notch parked its spell (search, not a full survey).
    Supersedes Note 27; R7 stays the fallback if the owner wants no new lock edge.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:361-447
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1575-1660
  - src/melder/aether/spellbook/spell.py:402-402
  - src/melder/aether/spellbook/spell.py:550-648
  - src/melder/aether/spellbook/spellbook.py:1461-1522
  - src/melder/aether/conduit/meld/meld.py:922-948
  IMPACT: R6 keeps every lookup O(1) and its answers equal to today's, apart from the transient windows R5 had.
  NEXT: Owner says go for R6 as amended (scratch build and tests, then the patch lane) or picks R7.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-11T01:07:16Z
  TYPE: DECISION
  CLAIM: Owner go for R6 as amended (chat 2026-10-11). Landing plan, patch id find_spell_by_id_id_maps_2026_10_11:
    src - Spellbook.find_spell_by_id (spellbook.py: body and docstring) answers from _spells_by_id, then
    _inactive_spells and the parked spell's index; Spell._spell_index_unless_cleaned (spell.py, new internal)
    reads spell_index under the spell's lock. Tests - a new component test file (lineage contract across notch,
    add/remove-from-index, transfer, parked disposal, contracted and unknown ids; the parked-disposal window
    forced; no iteration of the live map) and unit tests for the accessor. Docs - src_architecture and
    src_components entries with their indexes, graph descriptors reassembled, release note, notch 0.2.8229;
    assets and llm_support rebuilt last. The investigation contract's no-src boundary is lifted for this
    landing only, by this approval. Orientation first: src_components (Spellbook Core, Binding Pipeline,
    SpellIndex Mutation Surface, Ownership Transfer) and the graph sections of spellbook.py and spell.py.
  EVIDENCE:
  - context_compass/system_docs/src_components.md:341-848
  - context_compass/system_docs/src_components.md:5560-5620
  - context_compass/system_docs/src_components.md:5946-5963
  - context_compass/system_docs/src_graph.md:6207-6290
  - context_compass/system_docs/src_graph.md:15420-15520
  IMPACT: Moves the lane from proposal to landing; nothing lands before the scratch tests pass.
  NEXT: Write the three patch docs and link them, then build R6 in scratch with its tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-11T01:08:58Z
  TYPE: PLAN
  CLAIM: Patch docs written and consumed (architecture, component, code description). Mapping: invariants and
    control flow 1-5 -> find_spell_by_id body and docstring -> component tests (lineage contract, no iteration
    of the live map, forced parked-disposal window); accessor delta -> Spell._spell_index_unless_cleaned ->
    unit tests (index, None after cleanup, waits for the spell lock); failure deltas -> docstring Raises and
    Threading -> the no-raise window test under gil=0 and gil=1; dependency and ordering -> no lock held while
    the spell lock is taken -> full tree, conjure ambiguity path included; migration order -> tests, src, docs
    and indexes, graph, notch and release note, assets last. No unknown left open in the patch docs.
  EVIDENCE:
  - system_docs/patches/active/find_spell_by_id_id_maps_2026_10_11/architecture_patch.md:1-47
  - system_docs/patches/active/find_spell_by_id_id_maps_2026_10_11/component_patch_spellbook_core.md:1-32
  - system_docs/patches/active/find_spell_by_id_id_maps_2026_10_11/code_description_patch_find_spell_by_id.md:1-20
  IMPACT: The implementation and its tests are fixed before any code is written.
  NEXT: Build R6 in a scratch export with the new tests; red on 3d184cac where they pin the walk, green on R6.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-11T08:49:47Z
  TYPE: MEASURE
  CLAIM: R6 built and tested in scratch (git-archive exports of 3d184cac plus apply_r6.py; CPython 3.14.7t). The
    14 new tests - 10 component (lineage contract across notch, add/remove-from-index, transfer, parked disposal,
    unknown and foreign ids; no iteration of the live map; the parked-disposal window forced by an Event pause) and
    4 unit tests of Spell._spell_index_unless_cleaned - pass on R6 under -X gil=0 and gil=1. On 3d184cac 6 fail in
    both modes (the no-walk and mid-lookup-disposal tests and the four accessor tests: the method is new) and the 8
    contract tests pass, so R6 keeps every answer the walk gave. Full test tree on R6 (-X gil=0, the 23 chunks of
    the R5 baseline): 13,654 passed, 31 skipped, 17 xfailed, 2 xpassed - the 3d184cac baseline of 13,640 plus the
    14 new tests, nothing else. The crystallizer integration chunk first failed with ENOSPC (the VM's /sessions
    volume, pytest's temp root, was full from other sessions); rerun with TMPDIR on /tmp it matched the baseline,
    273 passed and 3 xfailed. Spell.cleanup never deleted _lock although its docstring said it did; the docstring is
    corrected, since the accessor's never-raises contract relies on the lock surviving cleanup.
  EVIDENCE:
  - context_compass/artifacts/spell_lookup_race_20261010/r6/runs/new_tests_head_gil0.log:1-150
  - context_compass/artifacts/spell_lookup_race_20261010/r6/runs/new_tests_head_gil1.log:1-150
  - context_compass/artifacts/spell_lookup_race_20261010/r6/runs/new_tests_cand_r6_gil0.log:1-2
  - context_compass/artifacts/spell_lookup_race_20261010/r6/runs/new_tests_cand_r6_gil1.log:1-2
  - context_compass/artifacts/spell_lookup_race_20261010/r6/runs/summary_full_r6_gil0.txt:1-25
  - context_compass/artifacts/spell_lookup_race_20261010/r4/runs/suites/summary_full_tree_gil0.txt:1-46
  - src/melder/aether/spellbook/spell.py:550-655
  IMPACT: The gate for landing (Note 29: nothing lands before the scratch tests pass) is met.
  NEXT: Land R6 through the patch lane: src, tests, notch, release note, docs, graph, then assets last.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-11T08:49:47Z
  TYPE: FACT
  CLAIM: R6 landed on the working tree as 0.2.8229 (no commit or push). find_spell_by_id answers from
    _spells_by_id, then _inactive_spells and the parked spell's index read through the new
    Spell._spell_index_unless_cleaned, then _spells.get(index); the Spell.cleanup docstring says _lock is kept. After
    the tree run one docstring sentence was made exact - an index move has no None window, a lookup racing it
    answers as before or as after the move - code unchanged. Tests: the component and unit files below.
    __version__ 0.2.8228 -> 0.2.8229; release note header, a user-facing section and the rebuild line.
    src_architecture (operational invariant, failure mode, code map, handoff) and src_components (Spellbook Core
    threading and failure modes, Binding Pipeline threading, code map, handoff), both indexes regenerated and
    checked. Graph: extract --strict, the Spell node re-read against its prose and accepted (it went stale only
    through this change; Spellbook was already stale at 3d184cac and is left so), reassembled; extract --check
    reports what 3d184cac reports (10 unsemantic, 208 stale) and assemble --check is OK. Patch docs promoted and
    archived to system_docs/patches/completed/find_spell_by_id_id_maps_2026_10_11/.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:1990-2069
  - src/melder/aether/spellbook/spell.py:720-753
  - src/melder/__version__.py:12-12
  - tests/component/melder/spellbook/test_spellbook_component_find_spell_by_id.py:1-303
  - tests/unit/melder/spellbook/test_spell_cleanup_safe_index_read.py:1-145
  - release_docs/next_version_release.md:1-65
  - context_compass/artifacts/spell_lookup_race_20261010/r6/scripts/land_docs_r6.py:1-164
  - context_compass/artifacts/spell_lookup_race_20261010/r6/runs/extract_check2.log:1-46
  IMPACT: The MelderOps lane can move once a Melder build carries 0.2.8229; the owner commits and pushes.
  NEXT: Rebuild the assets and llm_support bundles, then both --check.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-11T08:52:27Z
  TYPE: MEASURE
  CLAIM: Rebuilt last, from the repository root on CPython 3.14.7t with GIT_OPTIONAL_LOCKS=0: the build assets
    (agent documentation 462 entries, bind guard 622, system documents 4, all stamped v0.2.8229) and their --check
    print only OK lines; llm_support/_builder.py --include-untracked rewrote the bundles and its --check prints only
    OK lines (src, tests, other). No .git/index.lock was left. Ticket and board files are outside both bundles.
  EVIDENCE:
  - context_compass/artifacts/spell_lookup_race_20261010/r6/runs/assets_build.log:1-3
  - context_compass/artifacts/spell_lookup_race_20261010/r6/runs/assets_check.log:1-3
  - context_compass/artifacts/spell_lookup_race_20261010/r6/runs/llm_build.log:1-4
  - context_compass/artifacts/spell_lookup_race_20261010/r6/runs/llm_check.log:1-3
  IMPACT: The 0.2.8229 change set is complete on the working tree; nothing is committed or pushed.
  NEXT: Owner commits and pushes (git add -A for the two new test files and the archived patch folder), then
    accepts or redirects; closure is the owner's.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
REVIEW (melder_1), 2026-10-11T08:49:47Z: R6 LANDED as 0.2.8229 on the working tree, not committed - find_spell_by_id
answers from the Book's id maps, the parked branch reads its index through Spell._spell_index_unless_cleaned; 14
new tests; full tree identical to 3d184cac plus those tests (Notes 31-32). Owner: commit and push, accept or
redirect; Windows tiers, hosted CI, the gauntlet and MelderOps' x40 run are the owner's. Earlier state follows.
REVIEW (melder_1), updated: R4's conjure stall traces to one caller added in 8224 (Note 22). At the owner's
direction, R6 - find_spell_by_id answered from the Book's id maps, no walk - is the direction over R5 and R4'
(Notes 23-24). Its source check (Note 26) wrongly said transfer leaves parked versions behind - transfer moves
the whole lineage (Note 28); the real gap was the parked branch racing Spell.cleanup, closed by reading the
index under the spell's own lock. R6 as amended waits for the owner's go; R7 (Note 27) is the fallback. The
REONBOARD after the last compaction was late and was completed on the owner's challenge (Note 25). Earlier
state follows.
REVIEW (melder_1). The find_spell_by_id race is a current defect on 3d184cac (0.2.8228), reproduced in four modes
(Notes 7-8). The reviewer's Book-lock design R4 was checked on 3d184cac: its mutation inventory holds (Note 14),
but its reader lock makes a conjure with an ambiguous provider stall 60 s into PhaseTimeoutError and blocks
conduit hooks that wait on foreign-thread lookups (Notes 15-16). PROPOSED, not implemented: R5 = R1's lock-free
reader + R4's bind publication lock (proposal/repair_proposal_r5.md, proposal/proposed_patch_r5.diff), with R4'
as the linearizable alternative; evidence in Notes 18-20 and artifacts/.../r4/. Next: the owner answers Note 21's
decisions; on approval, open the patch lane before any code. No production change, notch, commit or push;
MelderOps' baseline, D-10, D-11 and D-20 untouched.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
