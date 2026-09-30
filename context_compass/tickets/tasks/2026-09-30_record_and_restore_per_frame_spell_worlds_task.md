

# Task: Record and restore per-frame spell-id worlds intact (regime in the Aether record, custody per Book)

## Metadata
- Task ID: TASK-2026-09-30-record-and-restore-per-frame-spell-worlds
- Story: none; implements options A + B of tickets/tasks/2026-09-30_investigate_aether_record_spell_id_regime_task.md
- Status: in_progress
- Owner: user
- Agent Name: melder_0
- Priority: p1
- Created: 2026-09-30T16:46:28Z
- Updated: 2026-09-30T18:28:19Z

## Objective
Owner pick (chat, 2026-09-30): "yeah ok so give me the best fix we can do go ahead and notch whatever versions you
want", after agreeing that the full fix is A + B. A world recorded under per-frame spell ids must come back as it
was: (A) the Aether record carries the spell-id regime and restore installs it before any frame is born, with an
honest shortfall or refusal when the live world holds another regime; (B) the record keeps one spell crystal per
Book instead of one per spell_id, so the same class bound in several frames survives recording, and every
spell_id-keyed record path (journal, removal, activity, fold, bind order, graft, reads) follows. Process-wide worlds
keep their behaviour; the record version moves to a new major so older readers refuse instead of merging copies.

## Ticket Contract
- ENTRY_GATE: the owner's pick; this board row; the survey of every spell_id-keyed record path noted before patch
  docs; patch docs and the mailbox NOTICE before any src edit.
- EXECUTION_BOUNDARY: src/melder/aether (Aether configuration twin and its emission seams),
  src/melder/crystallizer (persistence record, crystals, emit verbs, restore engine, graft, analysis reads), the
  emission call sites that must pass the owning Book, their tests, system docs, graph descriptors, the release note
  and __version__. The exact file list is fixed by the survey note and the patch docs.
- DEPENDENCIES: the investigation ticket above (findings, probes, DECISION_REQUEST); the 0.2.8209 sealed-regime
  guard (Aether.configure/activate refuse another regime while frames exist).
- EXIT_GATE: a per-frame world with one class in two frames records both crystals and restores both bindings under
  per-frame ids in a fresh process; the distinct-class per-frame world restores per-frame; process-wide worlds and
  existing 3.x records restore as before; new records carry the new major; red-to-green tests plus the crystallizer
  and affected suites; docs, graph, release note, notches, assets and LLM bundles with --check OK.
- FAILURE_ESCALATION: a DECISION_REQUEST before widening beyond the record (for example MutationResearch stores);
  BLOCKER if the VM cannot run the suites.

## Scope Boundaries
- In scope: options A and B as agreed; the probes rerun as acceptance.
- Out of scope: option C (unnecessary once nothing is overwritten); the injected-provider epic (parked by the owner).

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: (2026-09-30T16:46:28Z) owner pick in chat; ticket, board row and artifact row created
  before the survey.

## Steps / Checklist
- [x] Survey every spell_id-keyed record path (read-only) and note the file list.
- [x] Patch docs (architecture, per-component, code description) and the mailbox NOTICE.
- [x] Red tests for A and B (unit and integration, fresh-process restore included).
- [x] Implement A (regime in the Aether twin; stage 1 installs or reports it).
- [x] Implement B (custody per Book; every record path follows; record major).
- [x] Green: new tests, crystallizer tree, affected suites; rerun the investigation probes.
- [ ] System docs, graph descriptors, release note, one notch per change, assets and LLM bundles last.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Source change A and source change B with tests; patch docs promoted into the system docs; release note; notches.

## Files / Paths Impacted
- A (0.2.8213): src/melder/aether/aether.py, src/melder/aether/aether_configuration.py,
  src/melder/aether/aether_utility_system.py, src/melder/crystallizer/crystal_loader_system/restore_engine.py (stage 1).
- B (0.2.8214): src/melder/crystallizer/crystals/spell_crystal.py, src/melder/crystallizer/persistence/
  persistence_profile.py, persistence_system.py, record_version.py, src/melder/crystallizer/crystallizer.py,
  src/melder/crystallizer/crystal_loader_system/restore_engine.py, load_admission.py,
  src/melder/crystallizer/crystal_analysis/impact_engine.py, src/melder/aether/spellbook/spellbook.py (emit sites).
- src/melder/__version__.py; tests (new and updated doubles), system docs, graph descriptors, release note.

## Validation
- Not run.
- Recommended commands:
  - recorded in the MEASURE notes as they run

## Risks / Rollback Notes
- Record format change: a new major makes older Melder builds refuse new records by design; rollback is reverting
  the change set before release.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No src edit before the patch docs and the NOTICE.

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
  - artifacts/per_frame_spell_worlds_20260930/
  - system_docs/patches/active/per_frame_spell_worlds_2026_09_30/architecture_patch.md
  - system_docs/patches/active/per_frame_spell_worlds_2026_09_30/component_patch_aether_root_configuration.md
  - system_docs/patches/active/per_frame_spell_worlds_2026_09_30/component_patch_crystallizer_record.md
  - system_docs/patches/active/per_frame_spell_worlds_2026_09_30/component_patch_crystallizer_restore.md
  - system_docs/patches/active/per_frame_spell_worlds_2026_09_30/code_description_patch_restore_regime_and_custody.md
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
- DATETIME: 2026-09-30T16:46:28Z
  TYPE: DECISION
  CLAIM: Owner pick: the full fix, options A + B of the investigation's DECISION_REQUEST, with notches as needed
    ("give me the best fix we can do go ahead and notch whatever versions you want"). Option C is dropped because
    B leaves nothing to overwrite. The injected-provider epic stays parked until this lands.
  EVIDENCE:
  - tickets/tasks/2026-09-30_investigate_aether_record_spell_id_regime_task.md:245-275
  - tickets/tasks/2026-09-30_investigate_aether_record_spell_id_regime_task.md:277-296
  IMPACT: Two source changes (A, B), so two notches above 0.2.8212 at landing, plus a new record major for B.
  NEXT: Survey every spell_id-keyed record path, starting with the persistence profile and the emit verbs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-30T16:56:01Z
  TYPE: FACT
  CLAIM: Survey of every spell_id-keyed record path (read-only). Custody: PersistenceProfile keeps two maps keyed by
    spell_id; record, activity flips and removals address that key, and the journal and captured payloads for the
    spell_crystal / spell_activity / spell_removed kinds use it too; get_spell_crystal, describe_spell_crystals and
    capture_index_graft read by it. Emitters: two bind sites, two removal sites and two park/promote sites in
    spellbook.py, plus the transfer re-emission, which relies on replace-on-emit to displace the source Book's copy.
    Readers: the restore fold is key-agnostic, but its bind order, index-member lookup and recorded-to-live
    translation assume one copy per spell_id; the impact engine's per-spell lookup and the formation retarget
    (rewrites Book frame names only) do too. Preflight strategies use keys for display only; the synthetic and user
    module rebuild lanes are idempotent across copies. Frame-local facts that fix the key: a link to another frame
    is refused and a transfer runs inside its source frame, so (frame, spell_id) is unique under both regimes.
    MutationResearch reads custody by spell_id for source views and keys its own residence by spell_id - research is
    about code identity, which both frames' copies share. For A: the Aether twin is built in two places (the
    configuration seam and the utility system's logger re-emission, which would erase a regime field it does not
    carry), stage 1 skips a configured live Aether, and before the first frame the regime in force is the installed
    configuration's value (Aether exposes no public read of it).
  EVIDENCE:
  - src/melder/crystallizer/persistence/persistence_profile.py:334-434
  - src/melder/crystallizer/persistence/persistence_profile.py:744-926
  - src/melder/crystallizer/persistence/persistence_profile.py:1051-1191
  - src/melder/crystallizer/crystallizer.py:829-865
  - src/melder/crystallizer/crystallizer.py:1082-1141
  - src/melder/crystallizer/crystallizer.py:1471-1545
  - src/melder/crystallizer/crystallizer.py:1596-1640
  - src/melder/aether/spellbook/spellbook.py:649-658
  - src/melder/aether/spellbook/spellbook.py:1514-1518
  - src/melder/aether/spellbook/spellbook.py:1573-1576
  - src/melder/aether/spellbook/spellbook.py:4216-4220
  - src/melder/aether/spellbook/spellbook.py:5067-5075
  - src/melder/aether/spellbook/spellbook.py:5419-5429
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:447-477
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:801-815
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1101-1240
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1956-2203
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2462-2532
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1339-1393
  - src/melder/crystallizer/crystal_loader_system/load_admission.py:274-333
  - src/melder/crystallizer/crystal_analysis/impact_engine.py:281-317
  - src/melder/mutation_research/mutation_research.py:1819-1850
  - src/melder/aether/aether_configuration.py:421-485
  - src/melder/aether/aether_configuration.py:872-920
  - src/melder/aether/aether_utility_system.py:204-256
  - src/melder/aether/aether.py:970-1072
  IMPACT: The change set is bounded to the Aether root twin, the record's custody key and the readers that assume one
    copy per spell_id; MutationResearch needs no change.
  NEXT: Record the design decisions, then the patch docs and the NOTICE.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-30T16:56:01Z
  TYPE: DECISION
  CLAIM: Design, within the owner's A + B pick. (A) The Aether twin carries process_wide_unique_spell_ids from both
    emission places; a new read-only Aether.process_wide_unique_spell_ids reports the regime in force (sealed after
    the first frame, else the installed configuration's value, else True); from_recorded_payload applies the value or
    lists it as missing. Stage 1 installs the recorded regime before any frame is born; when the live regime cannot
    change (a configured Aether or existing frames) and differs, the restore refuses before building anything if the
    record holds one spell_id in two frames, and otherwise continues with a named shortfall. (B) Custody is keyed by
    the spell_id's uniqueness scope: the bare spell_id under process-wide ids (records of default worlds keep their
    shape) and "spell_id@frame" under per-frame ids; the crystal carries frame_name and custody_key; emitters pass
    their frame; removal and activity address the key; reads by spell_id without a frame pick the lowest key; restore
    derives spell ids from payloads, finds a member's index within its own Book and keeps recorded-to-live spell
    translation per Book (selections, anchors, contract grants); retargeting rewrites custody frame names; the impact
    engine finds a spell by payload id. RecordVersion goes to 4.0.0. Notches: A 0.2.8213, B 0.2.8214.
  EVIDENCE:
  - src/melder/crystallizer/persistence/record_version.py:78-78
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1745-1858
  IMPACT: Default-world records keep their keys (only the version and the additive Aether field change); per-frame
    records change shape, which the major bump fences from older readers.
  NEXT: Write the patch docs under system_docs/patches/active/per_frame_spell_worlds_2026_09_30/ and send the NOTICE.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-30T17:16:10Z
  TYPE: FACT
  CLAIM: Re-read after compaction, refining the survey before the patch docs. (1) A Spell carries its frame as the
    public attribute aetheric_frame and the Crystallizer holds its hosting Aether, so a crystal can take its frame
    from the spell and the facade can read the regime; crystal creation needs no call-site change, only the two
    spell-id emit verbs need the frame (four spellbook sites). (2) Aether seals the regime before it inserts the
    first frame, both under its class lock, and its frame reads deliberately take no lock, so a regime read can be
    lock-free. (3) Aether.cleanup marks the root cleaned before frames and the crystallizer are torn down and Aether()
    keeps returning that husk until its finally, so the utility system may read the regime only from an initialized,
    uncleaned Aether. (4) Stage 1 activates the rebuilt configuration whenever Aether is not configured, frames or
    not, so a sealed different regime fails the restore at stage aether_configuration (the 0.2.8209 guard).
    (5) _book_bind_order matches the book's bind_order (spell ids) against custody keys, so frame-scoped keys would
    drop the recorded order; _index_id_for_member scans every book's indexes; recorded-to-live spell translation is
    one global map. (6) A formation's journal is minted from payload keys after retarget, so retarget may re-key
    custody. (7) Eight test stubs expose exactly what the profile reads (no custody key), two spell doubles lack
    aetheric_frame, and two reload-lane tests pin the missing list to the logger key.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:430-443
  - src/melder/crystallizer/crystallizer.py:224-245
  - src/melder/aether/aether.py:1208-1259
  - src/melder/aether/aether.py:1756-1793
  - src/melder/aether/aether.py:278-337
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1339-1393
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1956-2202
  - src/melder/crystallizer/crystal_loader_system/load_admission.py:244-271
  - tests/unit/melder/crystallizer/persistence/test_persistence_profile.py:28-48
  - tests/mocks/crystallizer/spell_crystal_harness.py:17-39
  - tests/unit/melder/aether/test_configuration_reload_lanes.py:201-230
  IMPACT: The key scheme needs no new crystal-creation plumbing; the regime read must stay lock-free and tolerate a
    cleaned root; restore needs per-Book bind order, index lookup and translation; tests need stub/double updates.
  NEXT: Record the refined design split by notch, then write the patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-30T17:16:10Z
  TYPE: DECISION
  CLAIM: Refined design, one notch per change. A (0.2.8213): read-only Aether.process_wide_unique_spell_ids, lock-free
    (sealed value once a frame exists, else the installed configuration's, else True); both Aether twin emitters
    carry the regime (the utility system only from an initialized, uncleaned Aether); from_recorded_payload applies it
    or lists it missing. Stage 1: nothing fixed (unconfigured, no frame) installs the recorded regime; a fixed live
    regime (configured, or frames) that differs files a named shortfall, and an unconfigured world with frames
    installs the recorded logger policy under the live regime instead of failing the sealed-regime guard.
    B (0.2.8214): SpellCrystal gains frame_name (from the spell) and custody_key (per-frame flag from the facade;
    compose/split statics); the profile keys custody by it; emit_spell_removed, emit_spell_activity and
    get_spell_crystal take frame_name=None (required under per-frame ids); activity/removed payloads carry spell_id and
    custody_key; index grafts find a member's custody in the index's own Book; restore maps bind order and member
    index per Book, translates spell ids per Book (selections, anchors, contract grants by the granter's recorded
    Book) and refuses before building when the record holds one spell id in two frames under a process-wide live
    regime; retarget rewrites custody frame names and re-keys frame-scoped keys; the impact engine falls back to the
    payload id; RecordVersion 4.0.0. The custody maps keep their names (comments say what keys them); MutationResearch
    is unchanged (a per-frame record answers a bare spell id with its lowest key).
  EVIDENCE:
  - src/melder/crystallizer/persistence/persistence_profile.py:744-926
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1745-1858
  IMPACT: Fixes both measured defects; default worlds keep their record shape apart from the version and the additive
    regime field; test doubles grow by the one field each now reads.
  NEXT: Write the patch docs under system_docs/patches/active/per_frame_spell_worlds_2026_09_30/.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-30T17:19:01Z
  TYPE: PLAN
  CLAIM: Patch docs written and read in order (architecture, the three component patches, the code description);
    NOTICE M0-132..134 sent to fable_0, muse_0 and melder_2 (sole-writer claim on the A + B files). Mapping, patch
    section -> implementation -> validation: "Aether: regime in force" -> Aether property -> new component test file;
    "AetherConfiguration: twin and reload" -> payload key + reload -> reload-lane unit tests (two updated) and the twin
    integration test; "AetherUtilitySystem: root twin re-emission" -> guarded regime read -> twin integration test;
    "stage 1 decision table" -> _replay_aether_configuration + helpers -> new stage 1 unit tests (A branches, then the
    B refusal); "SpellCrystal", "PersistenceProfile...", "Crystallizer facade", "ImpactEngine", "RecordVersion" ->
    record B -> unit tests in test_spell_crystal, test_persistence_profile, test_crystallizer_record_sinks,
    test_impact_engine (stubs and doubles updated); "stage 6 per-Book custody replay" and "retarget" -> restore B ->
    per-frame restore integration tests and a retarget unit test; acceptance: the investigation probes rerun.
  EVIDENCE:
  - context_compass/system_docs/patches/active/per_frame_spell_worlds_2026_09_30/architecture_patch.md:10-70
  - context_compass/system_docs/patches/active/per_frame_spell_worlds_2026_09_30/component_patch_crystallizer_restore.md:9-64
  - context_compass/system_docs/patches/active/per_frame_spell_worlds_2026_09_30/code_description_patch_restore_regime_and_custody.md:9-57
  IMPACT: Entry gate satisfied (docs linked, read order done, mapping written); implementation may start with red
    tests.
  NEXT: Write the red tests for A (reload lanes, Aether property, twin, stage 1), run them red in the VM mirror.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-30T17:30:14Z
  TYPE: MEASURE
  CLAIM: Part A landed on the device tree and the VM mirror, __version__ 0.2.8212 -> 0.2.8213 (read at landing). Red
    first (VM mirror, 3.14.7t, GIL off): 14 of 31 new or updated tests failed for the expected reasons (no Aether
    property; KeyError on the twin's regime key; the reload lane's missing list; stage 1 filing no regime shortfall).
    Green after apply_a_src.py: 31/31; unit crystallizer tree 570 passed; component and integration crystallizer
    plus unit and component aether 5796 passed, 4 xfailed (pre-existing). One correction found while writing the
    tests: on 0.2.8212 a per-frame payload restored into a sealed process-wide frame did not fail - the reload dropped
    the regime, so the mismatch passed silently; the fix installs the logger policy under the live regime because a
    reload that now carries the regime would trip the sealed-regime guard.
  EVIDENCE:
  - src/melder/aether/aether.py:761-802
  - src/melder/aether/aether_configuration.py:421-497
  - src/melder/aether/aether_configuration.py:884-937
  - src/melder/aether/aether_utility_system.py:204-291
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1339-1448
  - context_compass/artifacts/per_frame_spell_worlds_20260930/runs/a_red.txt:1-28
  - context_compass/artifacts/per_frame_spell_worlds_20260930/runs/a_green_unit_crystallizer.txt:1-9
  - context_compass/artifacts/per_frame_spell_worlds_20260930/runs/a_green_crystallizer_aether_suites.txt:1-82
  - context_compass/artifacts/per_frame_spell_worlds_20260930/apply/apply_a_src.py:1-287
  IMPACT: Every Aether twin now records the regime and stage 1 installs or reports it; B (custody per frame) is next.
  NEXT: Write the B red tests (crystal key, record, facade verbs, impact, retarget, restore helpers, integration).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-30T18:02:37Z
  TYPE: MEASURE
  CLAIM: B red tests written and run red (VM mirror, 3.14.7t, GIL off, 0.2.8213): 24 of the 25 new or updated tests
    fail for the expected reasons - no frame_name on the profile, system and facade lookups and emit verbs; no
    custody_key, frame_name, statics or per_frame_custody on SpellCrystal; the retarget leaves "<id>@alpha" keys and
    payload frames; stage 1 does not refuse a two-frame record under a process-wide host; no per-Book translation
    helpers; a per-frame world records one custody entry per spell id; a one-frame removal empties the record. The
    graft test was pointed at tenant_a's index (the copy today's record displaces), so it fails on today's code too.
    The distinct-class per-frame integration test passes already (A covers it). The other 200 tests in the touched
    files pass with the doubles' new aetheric_frame and custody_key fields.
  EVIDENCE:
  - context_compass/artifacts/per_frame_spell_worlds_20260930/runs/b_red.txt:1-103
  - context_compass/artifacts/per_frame_spell_worlds_20260930/apply/apply_b_tests_unit.py:1-677
  - context_compass/artifacts/per_frame_spell_worlds_20260930/apply/apply_b_tests_integration.py:1-309
  - context_compass/artifacts/per_frame_spell_worlds_20260930/apply/apply_b_tests_fix1.py:1-44
  IMPACT: B's behaviour is pinned before any source edit; the implementation follows the 17:19:01Z patch mapping.
  NEXT: Write apply_b_src.py (SpellCrystal, record, facade, spellbook call sites, restore, retarget, impact,
    RecordVersion 4.0.0, notch 0.2.8214) and run the B tests green.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-30T18:16:21Z
  TYPE: MEASURE
  CLAIM: Part B landed on the VM mirror, then the device tree; __version__ 0.2.8213 -> 0.2.8214 (read at landing).
    Green in the mirror (3.14.7t, GIL off): the 224 tests of the red selection; unit crystallizer tree 589; component
    and integration crystallizer plus unit and component aether 5801 passed, 4 xfailed; MutationResearch, spellbook
    and aether integration 4724 passed, 2 skipped, 2 xpassed (all three pre-existing). Conduit integration and package
    checks: 304 passed, 1 failed - the build-asset version stamp (0.2.8212 vs 0.2.8214), expected until the final
    rebuild. Acceptance, the investigation probe rerun in fresh processes: S1 (one class in two frames, per-frame
    ids) records 2 spell crystals keyed "<sha>@tenant_a" and "<sha>@tenant_b" and an Aether twin with the regime
    False; a plain restore is complete with spell_active 2 and per-frame ids, and binding the class into either
    tenant afterwards collides because both tenants hold it again (on 0.2.8212 tenant_a came back empty). S3
    (distinct classes) records frame-scoped keys and restores per-frame (tenant_b accepts tenant_a's class). S2
    (process-wide) keeps bare keys and restores process-wide as before.
  EVIDENCE:
  - src/melder/crystallizer/crystals/spell_crystal.py:150-528
  - src/melder/crystallizer/persistence/persistence_profile.py:372-446
  - src/melder/crystallizer/persistence/persistence_profile.py:756-1014
  - src/melder/crystallizer/persistence/persistence_profile.py:1139-1283
  - src/melder/crystallizer/persistence/persistence_system.py:299-507
  - src/melder/crystallizer/crystallizer.py:829-876
  - src/melder/crystallizer/crystallizer.py:1124-1166
  - src/melder/crystallizer/crystallizer.py:1496-1719
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1349-1538
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1915-2435
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2696-2833
  - src/melder/crystallizer/crystal_loader_system/load_admission.py:275-347
  - src/melder/crystallizer/crystal_analysis/impact_engine.py:282-331
  - src/melder/crystallizer/persistence/record_version.py:76-80
  - src/melder/aether/spellbook/spellbook.py:652-656
  - src/melder/aether/spellbook/spellbook.py:1520-1522
  - src/melder/aether/spellbook/spellbook.py:1580-1582
  - src/melder/aether/spellbook/spellbook.py:4226-4228
  - context_compass/artifacts/per_frame_spell_worlds_20260930/runs/b_green_new_and_touched.txt:1-5
  - context_compass/artifacts/per_frame_spell_worlds_20260930/runs/b_green_unit_crystallizer.txt:1-10
  - context_compass/artifacts/per_frame_spell_worlds_20260930/runs/b_green_crystallizer_aether_suites.txt:1-82
  - context_compass/artifacts/per_frame_spell_worlds_20260930/runs/b_green_mr_spellbook_aether_integration_suites.txt:1-67
  - context_compass/artifacts/per_frame_spell_worlds_20260930/runs/b_conduit_integration_and_package_checks.txt:1-14
  - context_compass/artifacts/per_frame_spell_worlds_20260930/runs/probe_rerun/s1_record.txt:1-1
  - context_compass/artifacts/per_frame_spell_worlds_20260930/runs/probe_rerun/s1_restore_plain.txt:1-3
  - context_compass/artifacts/per_frame_spell_worlds_20260930/runs/probe_rerun/s1_restore_perframe_first.txt:1-3
  - context_compass/artifacts/per_frame_spell_worlds_20260930/runs/probe_rerun/s3_restore_plain.txt:1-3
  - context_compass/artifacts/per_frame_spell_worlds_20260930/runs/probe_rerun/s2_restore_plain.txt:1-3
  - context_compass/artifacts/per_frame_spell_worlds_20260930/apply/apply_b_src_record.py:1-891
  - context_compass/artifacts/per_frame_spell_worlds_20260930/apply/apply_b_src_restore.py:1-565
  IMPACT: Both measured defects are fixed and the exit gate's behaviour holds; docs, graph, release note and the
    rebuild remain.
  NEXT: Promote the patch docs into src_architecture, src_components and tests_components (indexes regenerated),
    then the graph descriptors, the release note (header 0.2.8214), the NOTICE, and the rebuild last.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-30T18:24:10Z
  TYPE: PLAN
  CLAIM: Owner direction (chat, after the 18:16Z note): "yeah don't do it now just finish what your doing please
    before you alternate to this validation thing" - the injected-provider (validation) discussion waits until this
    lane is in review. REONBOARD ran after the compaction (attestation and self-certification 18:22Z); the 18:16:21Z
    MEASURE note and step checks were written before it, were re-read during it, and stand. Board row and NOTICE
    M0-136..138 (0.2.8213 and 0.2.8214 landed) sent 18:23:27Z. Remaining, in order: (1) re-read the landed A and B
    methods the docs describe; (2) src_architecture - boundary list, the root-guards invariant's known gap replaced,
    failure modes, record-version lines, code map extents, handoff - and its index; (3) src_components - Aether
    Singleton, Aether Root Configuration Assembly, AetherUtilitySystem Provider Host, the Crystallizer component,
    Crystallizer Root, SpellCrystal Manifest, the restore detail, code map, handoff - and its index; (4)
    tests_components for the new tests; (5) graph descriptors of the changed files (extract, re-read and accept,
    assemble); (6) release note under "# Melder 0.2.8214" (A and B, Breaking for record major 4 and the custody keys);
    (7) Validation section, patch docs archived, artifact board, status review, board sync; (8) assets and LLM
    bundles rebuilt with --check, last.
  EVIDENCE:
  - context_compass/system_docs/patches/active/per_frame_spell_worlds_2026_09_30/architecture_patch.md:1-69
  - context_compass/mailbox_board.md:861-897
  - context_compass/attention_board.md:161-161
  IMPACT: The lane closes in the contribution guide's turn-in order; nothing else is opened meanwhile.
  NEXT: Re-read the landed methods (aether.py property, twin and reload, utility re-emission, SpellCrystal key,
    profile custody, facade verbs, stage 1 and stage 6 helpers, retarget, impact) before editing the docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-30T18:25:52Z
  TYPE: FACT
  CLAIM: Re-read of the landed A and B code after REONBOARD, as the docs' source: it matches the patch docs with one
    refinement the docs must carry - emit_spell_removed and emit_spell_activity return before computing a key while
    the crystallizer is inactive, so their frameless ValueError under per-frame ids fires only while recording. The
    stage-1 refusal surfaces as "restore failed at stage 'aether_configuration'" (the all-or-nothing wrapper) with
    the regime message chained. Measured extents for the code maps: aether.py 2954, aether_configuration.py 937,
    aether_utility_system.py 495, crystallizer.py 3089, spell_crystal.py 1280, spellbook.py 7335,
    persistence_profile.py 1636, persistence_system.py 1437, record_version.py 184, restore_engine.py 3021,
    load_admission.py 633, impact_engine.py 421.
  EVIDENCE:
  - src/melder/aether/aether.py:761-802
  - src/melder/aether/aether_configuration.py:421-497
  - src/melder/aether/aether_configuration.py:884-937
  - src/melder/aether/aether_utility_system.py:204-291
  - src/melder/crystallizer/crystals/spell_crystal.py:150-528
  - src/melder/crystallizer/persistence/persistence_profile.py:372-446
  - src/melder/crystallizer/persistence/persistence_profile.py:756-1014
  - src/melder/crystallizer/persistence/persistence_profile.py:1139-1283
  - src/melder/crystallizer/persistence/persistence_system.py:299-337
  - src/melder/crystallizer/persistence/persistence_system.py:481-507
  - src/melder/crystallizer/crystallizer.py:829-876
  - src/melder/crystallizer/crystallizer.py:1124-1166
  - src/melder/crystallizer/crystallizer.py:1496-1719
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:776-784
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1349-1538
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1915-2003
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2101-2435
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2696-2833
  - src/melder/crystallizer/crystal_loader_system/load_admission.py:275-347
  - src/melder/crystallizer/crystal_analysis/impact_engine.py:282-331
  - src/melder/crystallizer/persistence/record_version.py:76-80
  IMPACT: The docs state the verbs' refusal as "while recording" and the refusal's surfaced message; code-map extents
    are measured, not estimated.
  NEXT: Edit src_architecture (boundary list, glossary, invariants, failure modes, record-version lines, code map,
    sources, handoff) and regenerate its index.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-30T18:28:19Z
  TYPE: MEASURE
  CLAIM: src_architecture promoted (apply_docs_architecture.py): glossary "Custody key"; boundary list gains
    Aether.process_wide_unique_spell_ids and the frame-aware record verbs; the root-guards invariant's known gap is
    closed and a new invariant "Per-frame spell worlds record and restore intact" carries A and B; two failure modes
    (the stage-1 refusal as surfaced, the frameless emit ValueError while recording); record-version lines at 4.0.0;
    six code-map extents remeasured plus persistence_profile.py and restore_engine.py entries; six information
    sources; a handoff entry closing the root-guards "still open" item. Index regenerated, --check OK (57 sections,
    3378 lines); no added line over 120 characters; no package path in the document.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:291-293
  - context_compass/system_docs/src_architecture.md:312-313
  - context_compass/system_docs/src_architecture.md:924-946
  - context_compass/system_docs/src_architecture.md:1384-1397
  - context_compass/system_docs/src_architecture.md:3082-3089
  - context_compass/artifacts/per_frame_spell_worlds_20260930/apply/apply_docs_architecture.py:1-205
  IMPACT: The architecture narrative no longer claims the per-frame gap; the component map is next.
  NEXT: Verify the src_components index, slice the Aether, Crystallizer and restore sections, then edit them.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Opened 2026-09-30T16:46:28Z on the owner's pick (A + B). A landed at 0.2.8213 (17:30:14Z): the Aether twin
records the spell-id regime and restore stage 1 installs or reports it. B landed at 0.2.8214 (18:16:21Z): custody
per frame under per-frame ids, RecordVersion 4.0.0. Both green in the VM mirror; the investigation probes confirm
both defects fixed. Remaining: system docs, graph descriptors, release note, rebuild last, then status review for
the owner's turn-in (with the investigation ticket). The injected-provider discussion waits until then (owner,
chat). Patch docs, design and mapping are in the notes above.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
