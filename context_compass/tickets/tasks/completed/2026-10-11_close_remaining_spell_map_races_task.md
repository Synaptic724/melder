# Task: Close the remaining Spellbook spell-map races and the mid-transfer lookup error

## Metadata
- Task ID: TASK-2026-10-11-close-remaining-spell-map-races
- Story: none (standalone; follow-ups R2/R3 and the transfer-lookup gap from TASK-2026-10-10-investigate-spell-lookup-by-id-race)
- Status: done
- Owner: claude (assigned by the owner 2026-10-11)
- Agent Name: melder_1
- Priority: p1
- Created: 2026-10-11T11:49:06Z
- Updated: 2026-10-12T21:14:45Z

- Completed: 2026-10-12T21:14:45Z
- Summary: Landed, notched 0.2.8230: bind publishes the spell maps under the Book lock, unlocked walks take snapshots,
  has_spell and contract details survive a racing cleanup, the Conduit spell lookups document their ValueError;
  release note 'Spell lookups and validation no longer fail while other spells change'. Turned in 2026-10-12.

## Objective
Close the races the find_spell_by_id lane left open and the contract gap it found: (1) bind publishes into
Spellbook._spells without the Book lock, so every other walker of that map can meet a size change or a resize -
Book-locked walkers included - and several walkers hold no Book lock at all; (2) SpellIndex.has_spell checks
cleaned before taking its lock, so a concurrent cleanup surfaces as AttributeError; (3) Conduit.get_spell_by_id
raises ValueError for a spell between owners although it documents None for a miss. Reproduce each, fix it with the
smallest change that holds, test it, and land it through the patch lane.

## Owner Direction
Owner, chat 2026-10-11, after the 0.2.8229 landing and the list of open items: "ok go investigate those things
please and iterate on fixes". Items in scope are 1-3 of that list. D-10, D-11 and D-20 stay separate and untouched
(owner-assigned backlog); MelderOps' baseline is not advanced.

## Ticket Contract
- ENTRY_GATE: owner direction (chat, 2026-10-11); this ticket and its attention_board.md row exist before any
  investigation tranche.
- EXECUTION_BOUNDARY: read src/melder for items 1-3; reproduce and fix in scratch copies under /tmp first; land each
  fix through the patch lane (patch docs, src, tests, docs, notch, release note, graph, assets and llm_support last)
  only after its tests and the full tree pass. No commit or push.
- DEPENDENCIES: working tree = 3d184cac plus the uncommitted 0.2.8229 landing
  (tickets/tasks/2026-10-10_investigate_spell_lookup_by_id_race_task.md, in review).
- EXIT_GATE: each item reproduced (or shown unreachable) with evidence, fixed with regression tests, landed with
  the checks green; anything needing an owner choice is a DECISION_REQUEST before it lands.
- FAILURE_ESCALATION: DECISION_REQUEST for a lock-order change or a public contract change; BLOCKER if the VM disk
  (attention_board.md, Device VM disk) stops validation.

## Scope Boundaries
- In scope: writers and walkers of Spellbook._spells (inventory:
  artifacts/spell_lookup_race_20261010/r4/spells_access_inventory.txt); SpellIndex.has_spell and its walking
  callers; Conduit.get_spell_by_id, Spellbook._get_spell_by_id_via_aether, Aether._get_conduit_by_spell_id.
- Out of scope: D-10, D-11, D-20; MelderOps code; behaviour unrelated to these maps.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: items 1-3 landed as 0.2.8230 with checks green; acceptance, commit and push are the owner's.
- from_state: review
- to_state: done
- transition_reason: (2026-10-12T21:14:45Z) the owner turned in every finished melder_1 ticket (chat 2026-10-12: "just close everything you finished");
  git add -A, commit, push, the Windows tiers and hosted CI remain the owner's.

## Steps / Checklist
- [x] Item 1: read every writer and walker of _spells; reproduce the reachable races; fix and test in scratch.
- [x] Item 2: read has_spell and its walking callers; reproduce; fix and test in scratch.
- [x] Item 3: read the get_spell_by_id chain; reproduce; decide None vs documented raise; fix and test.
- [x] Patch docs written and linked; full tree on the fixed scratch tree.
- [x] Land through the patch lane; assets and llm_support rebuilt last.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Reproductions, fixes with regression tests, landed change set, and any owner decision request.

## Files / Paths Impacted
- src/melder/aether/spellbook/spellbook.py, spellbook_creation_system.py, bind/spell_index.py
- src/melder/aether/conduit/conduit.py, conduit_ward/contract/details.py,
  conduit_ward/transfer/transfer_of_ownership.py; src/melder/nexus/rift/command_system/command_system.py
- src/melder/__version__.py (0.2.8230), release_docs/next_version_release.md, rebuilt _build_assets and llm_support
- tests: 3 new files (unit spell_index race, unit detail probe, component spell-map races); 5 unit files' stubs
- context_compass/system_docs: src_architecture, src_components (+ indexes), graph descriptors and src_graph
- context_compass/artifacts/spell_lookup_race_20261010/followups/ (evidence)

## Validation
- New tests red/green and the full tree (gil=0) on the scratch tree; post-landing unit_arch/llm/build/
  top/gh on the landed version; graph, assets and llm_support checks OK (Note 12). Not run: gil=1 full tree,
  Windows tiers, hosted CI, coverage.

## Risks / Rollback Notes
- A Book-lock acquisition added to bind must not add a lock-order edge (R5 measured it does not; re-verify).

## Applicable Anti-Patterns
- [x] No sleep-based reproduction presented as deterministic.
- [x] No behaviour claim from a search hit alone.
- [x] No defensive guard without contract evidence.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed (owner turn-in, 2026-10-12)
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/spell_lookup_race_20261010/followups/
  - system_docs/patches/completed/spell_map_races_2026_10_11/ (five patch docs, archived at landing)
- DISPOSITION: retain_as_reference (evidence); promote_to_documentation (patch docs, at landing)
- CLEANUP_TRIGGER: decided at turn-in; the patch docs were promoted and archived at the 0.2.8230 landing.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: free-threaded dict iteration; Spellbook and SpellIndex locking; transfer windows
- IF_UNKNOWN: ask user before implementation

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes

- DATETIME: 2026-10-11T11:56:58Z
  TYPE: FACT
  CLAIM: Item 1 read through. Every writer of Spellbook._spells holds the Book lock except bind's publication insert,
    so the Book-locked walkers (group A, 20 sites) are exposed only to that insert. Group C walks the live map with
    no Book lock: Conduit.get_spell_permissions and CommandSystem.get_spell_by_id (items() + has_spell, the same
    lineage lookup find_spell_by_id now answers from the id maps), inspect_spell over another conduit's Book,
    TransferOfOwnership._conduit_has_impacted_lineage (also the contracted maps), and the creation system's
    book-wide phase factories, which public Conduit.validate_resolution runs with no Book lock (live loops at 1534
    and 2643, next(iter(values())) at 3108/3429/3470, comprehensions at 3147-3368). Meld-time reruns use the
    compiler's per-spell and target-single phases, not these factories.
  EVIDENCE:
  - context_compass/artifacts/spell_lookup_race_20261010/followups/spells_walkers_0.2.8229.txt:1-33
  - src/melder/aether/spellbook/spellbook.py:5348-5388
  - src/melder/aether/conduit/conduit.py:4013-4057
  - src/melder/aether/conduit/conduit.py:5862-5929
  - src/melder/nexus/rift/command_system/command_system.py:835-889
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:818-846
  - src/melder/aether/spellbook/spellbook_creation_system.py:1501-1545
  - src/melder/aether/spellbook/spellbook_creation_system.py:3403-3480
  IMPACT: One bind-side lock covers group A; group C needs one-call snapshots or the id maps, not reader locks
    (a reader-side Book lock deadlocks conjure, Note 15 of the find_spell_by_id ticket).
  NEXT: Measure which one-call forms are exact under concurrent writers, then read item 2.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-11T11:56:58Z
  TYPE: MEASURE
  CLAIM: On CPython 3.14.7t (-X gil=0), 2 writers inserting/removing and 2 readers for 2 s each: list(d.values()),
    list(d), lst.extend(d.values()) and list(d.items()) are exact (0 errors, 0 missed stable keys); a comprehension
    over d.values() raised 1,488,820 size-change errors, and next(iter(d.values())) raised in 126,678 of ~3.4M
    reads - the lead-spell pattern fails too, not just full walks.
  EVIDENCE:
  - context_compass/artifacts/spell_lookup_race_20261010/followups/snap_probe.py:1-42
  - context_compass/artifacts/spell_lookup_race_20261010/followups/snap_probe_gil0.log:1-7
  IMPACT: The fix for group C is list(...) taken in one call (the 0.2.72 precedent for the spell pool);
    risk_manager.py:487 and the factories at 2697/2982 are already exact and stay as they are.
  NEXT: Read SpellIndex.has_spell and the walkers that still call it (item 2).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-11T12:05:09Z
  TYPE: FACT
  CLAIM: Item 2 read through. SpellIndex.has_spell runs check_cleaned() before taking its lock while cleanup() sets
    _cleaned and deletes _spells_in_index under that lock, so a cleanup landing between the two raises
    AttributeError; IndexDetail.has_spell reads spell_index._spells_in_index with no lock and no check of the
    index, the same shape. Walkers that probe indexes they do not lock: Spellbook._find_contracted_spell_by_id
    (live walk of a contracted map + has_spell), TransferOfOwnership._enumerate_borrowers (cluster-shared
    indexes), ConduitWard._find_governing_index_link and _get_spell_in_contracts (IndexDetail.has_spell);
    get_spell_permissions and CommandSystem.get_spell_by_id leave has_spell once they read the id maps.
    AethericFrame.find_conduit_id_for_spell is safe (frame lock, and indexes leave the frame before cleanup);
    Contract._grant has no caller in src.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/spell_index.py:288-315
  - src/melder/aether/spellbook/bind/spell_index.py:118-138
  - src/melder/aether/conduit/conduit_ward/contract/details.py:425-439
  - src/melder/aether/spellbook/spellbook.py:2942-2968
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:561-618
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2525-2552
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:3504-3561
  IMPACT: has_spell needs the check repeated under its lock (the documented RuntimeError instead of
    AttributeError); walkers over indexes they do not own need a probe that answers False for a cleaned index.
  NEXT: Read the get_spell_by_id chain (item 3).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-11T12:05:09Z
  TYPE: FACT
  CLAIM: Item 3 read through. Conduit.get_spell_by_id, Conduit.get_conduit_by_spell_id and
    Spellbook._get_conduit_by_spell_id all document None for an id no conduit claims, and every internal caller
    checks for None and raises its own error (ward link and contract resolution, transfer, Conduit 4443); but the
    chain ends in Aether._get_conduit_by_spell_id, which documents and raises ValueError("Spell version ... not
    found in any conduit.") - so the None branches are dead and the documented contract is never honoured.
    Aether._get_conduit_by_spell_id keeps a raising caller of its own (CommandSystem.get_spell_by_id).
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:3036-3066
  - src/melder/aether/conduit/conduit.py:3097-3131
  - src/melder/aether/spellbook/spellbook.py:2612-2638
  - src/melder/aether/spellbook/spellbook.py:2806-2833
  - src/melder/aether/aether.py:2478-2517
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1515-1522
  IMPACT: Returning None from the Spellbook wrapper honours three docstrings and the internal callers; code outside
    Melder that caught ValueError to detect a missing spell would need to check for None.
  NEXT: Decide the item-3 semantics, then write the patch docs and the implementation mapping.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-11T12:05:09Z
  TYPE: DECISION
  CLAIM: Item 3 follows the documented contract: a new Aether._find_conduit_by_spell_id returns None for an id no
    conduit claims (or whose owner root is gone), Aether._get_conduit_by_spell_id keeps raising through it, and
    Spellbook._get_conduit_by_spell_id uses the non-raising lookup - so Conduit.get_spell_by_id and
    get_conduit_by_spell_id return None as documented; an unknown frame still raises ValueError. Taken under the
    owner's "iterate on fixes" (Owner Direction) after the evidence above; flagged in the release note as a change a
    caller who caught ValueError must adapt to, and in the hand-back so the owner can redirect before committing.
  EVIDENCE: context_compass/tickets/tasks/2026-10-11_close_remaining_spell_map_races_task.md:19-23
  IMPACT: One public behaviour change, in the documented direction.
  NEXT: Write the patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-11T12:06:16Z
  TYPE: PLAN
  CLAIM: Patch docs written and consumed (architecture, three component patches, code description). Mapping:
    invariant 1 -> bind publishes its three maps under one Book-lock block -> a Book-locked walk paused mid-walk
    while another thread binds; invariant 2 -> list(...) snapshots in the group-C walkers -> a creation-system loop
    paused in its body while another thread binds; invariant 3 -> has_spell re-check, the new probe and
    IndexDetail -> unit tests with a cleanup forced between check and lock; invariant 4 -> Aether find + the
    Spellbook wrapper -> unknown id answers None from both Conduit lookups, unknown frame still ValueError.
    Order: scratch copy of the working tree, tests red where deterministic, src, tests green, full tree, then
    landing as 0.2.8230 (one change set: these walkers and lookups are one contract).
  EVIDENCE:
  - context_compass/system_docs/patches/active/spell_map_races_2026_10_11/architecture_patch.md:1-55
  - context_compass/system_docs/patches/active/spell_map_races_2026_10_11/code_description_patch_spell_map_walks.md:1-22
  IMPACT: Implementation and tests are fixed before code is written.
  NEXT: Copy the working tree to scratch and write the tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-11T12:33:00Z
  TYPE: FACT
  CLAIM: Correction to the item-2 note: ConduitWard._get_spell_in_contracts probes Detail.has_spell (the per-spell
    detail map), not IndexDetail.has_spell. Detail.has_spell reads spell_index._spells_in_index unlocked exactly as
    IndexDetail.has_spell does, so both detail classes take the cleanup-safe probe.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/contract/details.py:193-207
  - src/melder/aether/conduit/conduit_ward/contract/details.py:425-439
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:3504-3561
  IMPACT: The scratch change set edits both has_spell bodies; the new unit test runs over Detail and IndexDetail.
  NEXT: Record the scratch red/green, then run the full tree on both trees.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-11T12:33:00Z
  TYPE: MEASURE
  CLAIM: Scratch change set applied to a copy of the working tree (/tmp/cc_follow/cand; 8 src files, the edits of
    the patch docs plus public docstrings for the item-3 None and the aether log/doc names). 9 new tests in 3 files
    are red on the unpatched copy for the intended reasons - has_spell raised AttributeError under a forced
    cleanup, the probe was missing, details raised AttributeError, the Book-locked walk and the validate_resolution
    cleanup pass raised "dictionary changed size during iteration", get_spell_permissions walked items(), and the
    unclaimed id raised ValueError - on -X gil=0 and gil=1; green on the patched copy on both, 15 of 15 repeats.
    Six existing unit files whose stubs modelled the old walk (Book _spells stubs, a has_spell-only index stub, a
    MagicMock index) were updated to stub find_spell_by_id or the probe; with 4 added unit tests they pass (563).
  EVIDENCE:
  - context_compass/artifacts/spell_lookup_race_20261010/followups/scratch_0.2.8230/src_0.2.8230.diff:1-551
  - context_compass/artifacts/spell_lookup_race_20261010/followups/scratch_0.2.8230/tests_0.2.8230.diff:1-669
  - context_compass/artifacts/spell_lookup_race_20261010/followups/scratch_0.2.8230/runs/new_tests_base_gil0.log:1-37
  - context_compass/artifacts/spell_lookup_race_20261010/followups/scratch_0.2.8230/runs/new_tests_cand_gil0.log:1-13
  - context_compass/artifacts/spell_lookup_race_20261010/followups/scratch_0.2.8230/runs/new_tests_cand_gil1.log:1-21
  - context_compass/artifacts/spell_lookup_race_20261010/followups/scratch_0.2.8230/runs/updated_unit_files_cand_gil0.log:1-9
  IMPACT: Every invariant in the patch has a forced regression; the remaining gate before landing is the full tree.
  NEXT: Run the full tree on the unpatched and patched copies (gil=0) and compare.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-11T12:39:19Z
  TYPE: CONFLICT
  CLAIM: Full tree on the patched copy (gil=0): every chunk green except two integration tests that pin the old
    item-3 behaviour - test_aether_integration_frames.py::test_aether_frame_isolation_for_conduit_and_spell_lookup
    (an id bound in another frame, looked up in the default frame) and
    test_conduit_integration_lifecycle.py::test_conduit_cleanup_unregisters_from_aether_and_cloud (an id whose owner
    was cleaned; its docstring says "after cleanup, lookups raise") both expect ValueError("Spell version ...") from
    Conduit.get_conduit_by_spell_id. So the raise is tested behaviour, not only undocumented behaviour, and returning
    None is a public semantic change - this ticket's FAILURE_ESCALATION and engineer AGENTS 7.10 make it the
    owner's call; the Note 5 DECISION is suspended until then. No MelderOps source calls get_spell_by_id or
    get_conduit_by_spell_id (grep of priv_commandops, caches and venvs excluded). Items 1-2 change no public result.
  EVIDENCE:
  - tests/integration/melder/aether/test_aether_integration_frames.py:69-127
  - tests/integration/melder/conduit/test_conduit_integration_lifecycle.py:124-170
  - src/melder/aether/conduit/conduit.py:3036-3066
  IMPACT: Item 3 cannot land without the owner choosing None (docs and internal callers) or ValueError (tests).
  NEXT: DECISION_REQUEST to the owner; items 1-2 are independent of the answer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-11T12:39:19Z
  TYPE: DECISION_REQUEST
  CLAIM: Owner: should Conduit.get_spell_by_id and Conduit.get_conduit_by_spell_id return None for an id no conduit
    claims (what their docstrings and every internal caller expect; the two integration tests change to expect
    None; release note flags it for callers that caught ValueError), or keep raising ValueError (the docstrings
    change to document it; the internal None branches stay dead)? Recommendation: None. Items 1-2 land either way.
  EVIDENCE:
  - context_compass/system_docs/patches/active/spell_map_races_2026_10_11/architecture_patch.md:1-55
  - src/melder/aether/aether.py:2478-2517
  IMPACT: Decides whether 0.2.8230 carries item 3 or only items 1-2.
  NEXT: Wait for the owner's answer; land accordingly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-11T15:12:40Z
  TYPE: DECISION
  CLAIM: Owner, chat 2026-10-11, answering Note 10 after the case for each side: keep ValueError. Conduit.get_spell_by_id
    and get_conduit_by_spell_id keep raising for an id no conduit claims - the get_* raises / find_* returns None
    convention of the 0.2.79 lookup API and 0.2.8208 frame lookups, fail-fast, and the precedent of
    get_spell_permissions, whose docs were corrected to its raise. The docstrings (which promised None) and
    get_conduit_by_spell_id's Optional annotation are corrected instead; Aether is unchanged; the two integration
    tests stay. Supersedes the Note 5 DECISION. Items 1-3 land together as 0.2.8230. Patch docs updated first.
  EVIDENCE:
  - context_compass/system_docs/patches/active/spell_map_races_2026_10_11/architecture_patch.md:1-55
  - context_compass/system_docs/patches/active/spell_map_races_2026_10_11/component_patch_conduit_runtime.md:1-20
  - src/melder/aether/conduit/conduit.py:3036-3131
  IMPACT: No public behaviour change in the landing; item 3 becomes documentation of the existing raise.
  NEXT: Re-cut the scratch change set (items 1-2 + the item-3 docs), rerun the new tests and the full tree, land.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-11T15:56:27Z
  TYPE: MEASURE
  CLAIM: Landed as 0.2.8230 (notched from 0.2.8229). The change set was re-cut after the Note 11 decision
    (apply_0_2_8230.py: items 1-2 unchanged, item 3 as docstrings and the get_conduit_by_spell_id annotation; Aether
    untouched) and applied to the working tree, which was byte-identical to the scratch base for every touched file
    and all of src/. New tests: 9 in 3 files - 8 red on the 0.2.8229 tree for the intended reasons and 1 contract
    lock (the documented ValueError) green on both, all 9 green on 0.2.8230 under -X gil=0 and gil=1, 15 of 15
    repeats. Full tree on the scratch tree (gil=0): every chunk green; against the 0.2.8229 run unit_aether +2,
    unit_sb +4, comp_sb +4, nothing else moved; after the notch and the rebuild unit_arch/llm/build/top/gh pass on
    the landed version. Docs: src_architecture (invariant, two failure modes, code map, handoff), src_components
    (Spellbook Core, Binding Pipeline, Conduit Runtime, ConduitWard, command surface, code map, handoff), both
    indexes current. Graph: extract --strict rc=0; five nodes went stale from this change (SpellbookCreationSystem,
    SpellIndex, TransferOfOwnership, Detail, IndexDetail) - prose re-read, SpellIndex's corrected (it claimed owner
    and contract metadata the class does not hold), the others extended, all five accepted; census back to 10
    unsemantic / 208 stale (unchanged); assemble --check OK. Release note section extended; patch folder archived.
    Assets and llm_support (--include-untracked) rebuilt, both checks OK.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:5403-5412
  - src/melder/aether/spellbook/bind/spell_index.py:288-357
  - context_compass/system_docs/src_architecture.md:923-939
  - tests/component/melder/spellbook/test_spellbook_component_spell_map_races.py:109-317
  - context_compass/artifacts/spell_lookup_race_20261010/followups/scratch_0.2.8230/runs/summary_full_cand_0_2_8230_gil0.txt:1-31
  - context_compass/artifacts/spell_lookup_race_20261010/followups/scratch_0.2.8230/runs/new_tests_base_gil0.log:1-36
  - context_compass/artifacts/spell_lookup_race_20261010/followups/scratch_0.2.8230/runs/new_tests_cand_gil1.log:1-21
  - context_compass/artifacts/spell_lookup_race_20261010/followups/scratch_0.2.8230/runs/assets_check.log:1-3
  - context_compass/artifacts/spell_lookup_race_20261010/followups/scratch_0.2.8230/runs/llm_check.log:1-3
  IMPACT: Items 1-3 are closed in the working tree; nothing is committed. Residuals, not changed here: Aether's frame
    sweep in _check_for_spell walks _aetheric_frames live; ConduitWard._get_spell_in_contracts walks contract detail
    maps live under the ward lock only; TransferOfOwnership._enumerate_borrowers keeps has_spell (now always the
    documented RuntimeError for a cleaned shared index); the public Spellbook.spells property is a live read-only view
    that a caller iterating it during concurrent binds can still meet resizing; the None checks of the callers of
    Spellbook._get_conduit_by_spell_id are dead; Contract._grant has no caller.
  NEXT: Owner: commit and push (git add -A: three new test files, the archived patch folder, followups evidence),
    then accept or redirect; Windows tiers and hosted CI are the owner's.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-11T16:05:18Z
  TYPE: FACT
  CLAIM: Owner asked whether the Note 12 residuals matter in the architecture or only in isolation; read each
    reader against its writers' locks and callers. Reachable through public operations in a multithreaded dynamic
    world: (a) Conduit.cleanup_spell runs with no lock or transaction and, after the Spellbook has already removed
    the spell, ConduitWard._emit_index_destroy walks the ward's live _contracts while link/sever write that map
    under SafeGuard(ward locks) - a resize aborts the emission midway and borrowers keep subscriptions to a dead
    lineage (the only one that leaves state inconsistent); (b) the borrower's contract inspection
    (Conduit.get_spell_in_contracts -> ConduitWard._get_spell_in_contracts) walks contract._get_detail_map(owner)
    live under its own ward lock while the owner's index moves and destroys write the same dict under the contract
    lock - a spurious RuntimeError, read-only; (c) Aether._check_for_spell and _get_all_spell_ids (bind's collision
    guard, inspect_spell, check_spell_id) sweep _aetheric_frames live while frame birth and detach write it under
    the Aether lock, and AethericFrame.has_spell raises for a cleaned frame not yet detached - a spurious bind
    failure while frames are born or collapse, only with two or more frames under process-wide ids; fails clean.
    Consistency, not races: (d) link dependency contracting, transfer by id and _check_spell_id_and_spell turn a
    None from the Conduit lookups into RuntimeError with their own message, but the lookups raise ValueError first,
    so those operations surface ValueError for an unknown id; (e) Spellbook.spells documents an "immutable map" for
    "safe introspection" but returns a live view - no Melder code iterates it (single-key gets only) and MelderOps
    does not use it. Benign: (f) _enumerate_borrowers runs in transfer preflight, so a cleaned shared index fails
    the transfer before any mutation; (g) Contract._grant is dead code. None of these is on the meld path.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:5551-5584
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2369-2405
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:765-951
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1051-1146
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:3504-3561
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2451-2477
  - src/melder/aether/conduit/conduit_ward/contract/contract.py:237-300
  - src/melder/aether/aether.py:2523-2583
  - src/melder/aether/aether.py:2762-2808
  - src/melder/aether/aether.py:405-460
  - src/melder/aether/aether.py:1251-1300
  - src/melder/aether/aetheric_frame/aetheric_frame.py:853-878
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2866-2889
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:3714-3728
  - src/melder/aether/spellbook/spellbook.py:1880-1899
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:282-360
  IMPACT: (a)-(c) are architecture-level (cross-object lock gaps of the same family as 0.2.8230: a reader and a
    writer guarded by different locks); none is reproduced yet. (d)-(e) are contract wording/type issues; (f)-(g)
    need nothing. Fixes would follow the existing patterns (one-call snapshots; skip frames that read cleaned).
  NEXT: Owner decides whether (a)-(e) get a follow-up lane; nothing changes until then.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
IN REVIEW (melder_1, 2026-10-11T15:56:27Z): items 1-3 landed as 0.2.8230 in the working tree (not committed). Item 1: bind
publishes its four spell maps under the Book lock; unlocked walks (validate_resolution's phases and cleanup pass,
inspect_spell over another Book, contracted lookups, the transfer impact walk) take one-call snapshots;
get_spell_permissions and CommandSystem.get_spell_by_id use find_spell_by_id. Item 2: SpellIndex.has_spell re-checks
cleaned under its lock; new SpellIndex._has_spell_unless_cleaned backs Detail/IndexDetail.has_spell and the
contracted lookup. Item 3 (owner decision, Note 11): Conduit.get_spell_by_id and get_conduit_by_spell_id keep raising
ValueError for an unclaimed id and now document it. Evidence: Notes 7-12 and context_compass/artifacts/spell_lookup_race_20261010/followups/scratch_0.2.8230/. Open for the owner: commit/push,
Windows tiers, hosted CI, acceptance. Residuals are listed in Note 12's IMPACT.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
