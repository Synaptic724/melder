# Task: spell_id_wording_near_spell_index - name the id where "version id" meets the spell index

- Completed: 2026-10-17T20:49:39Z
- Summary: notched 0.2.8252 - "version id" named by hand as the `spell_id` in 214 docstring, comment and
  test lines of 113 files nobody else held; IdentityMixingStrategy's diagnostic ends "instead of a
  spell_id."; the owner's double check found no "version id" meaning another id. Release-note bullet in
  "Packaging and documentation". The 127 held rewrites, 5 kept lines and the tests_components entry
  moved to TASK-2026-10-17-spell_id_wording_in_held_files (backlog, blocked on melder_1's release).
  Turned in on the owner's word (chat 2026-10-17); rebuilt last.

## Metadata
- Task ID: TASK-2026-10-16-spell_id_wording_near_spell_index
- Story: none (standalone; the owner's direction after TASK-2026-10-16-public_notch_target_for_staged_versions)
- Status: done
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-10-16T18:37:02Z
- Updated: 2026-10-17T21:00:59Z

## Objective
Where the term "version id" relates to a spell index, replace it with the id it means - `spell_id` (the id `bind`
and `bind_inactive` generate) or the spell index id (`spell_index_id`) - so no reader has to guess which of the two
is meant. Every occurrence is found and decided by hand; nothing is renamed in bulk.

## Ticket Contract
- ENTRY_GATE: the owner's direction recorded (DECISION note); the active board row; an inventory of every live
  occurrence with its context in the artifacts folder; the decision for each occurrence written before any edit.
- EXECUTION_BOUNDARY: wording only - docstrings and comments in src/ and tests/, the system documents (with their
  indexes), the authored prose of the graph descriptors (with the reassembled graph), the running release note.
  No code identifier is renamed and no behaviour changes. Files melder_1 holds for its rule-2 lane (TASK-2026-10-16-
  recheck_contract_consumers_when_provider_changes: 7 src, 11 test files, the system docs, the graph descriptors of
  its files and the release note) are edited only after melder_1 releases them.
- DEPENDENCIES: melder_1's rule-2 closure for the files it holds (QUESTION M0-178).
- EXIT_GATE: no live occurrence relating to a spell index left; every occurrence kept is listed with its reason; the
  touched files compile and their tests pass with the GIL off and on; indexes and graph regenerated with their
  checks OK; the notch (src docstrings ship) and a release-note bullet; the rebuild last with both checks OK.
- FAILURE_ESCALATION: DECISION_REQUEST when the code cannot settle which id an occurrence names, or when a fix
  would need an identifier renamed; CONFLICT when melder_1 needs a file this lane is editing.

## Scope Boundaries
- In scope: every live "version id" / "version ids" / "version ID" / "version-id" in prose, read in context.
- Out of scope: code identifiers (the test helpers `_get_spell_by_version_id`, `get_spell_by_version_id` and
  `_get_local_spell_by_version_id` in 44 test files; the local `version_id` / `version_ids` names in
  spell_system_root_blueprint_builder.py and spell_system_adjacency_snapshot.py) - renames, which the owner ruled out
  as a blanket change; history (completed tickets, archived patch docs, artifacts, Plans/, benchmark plan notes);
  generated output (build/, docs/_build, _readthedocs, llm_support, the asset payloads - rebuilt); third-party code.

## State Transition Event
- from_state: blocked
- to_state: done
- transition_reason: turned in on the owner's word (chat 2026-10-17, "turn in your old tickets"):
  notched 0.2.8252 for the landed free scope; the held scope moved to a backlog successor.

## Steps / Checklist
- [x] Inventory every live occurrence with its context; the decision for each, by hand.
- [x] Apply the decisions in files nobody else holds; compile; the touched tests with the GIL off and on.
- [x] After melder_1 releases its files: the same for them, the system docs, the graph and the release note
      (handed to TASK-2026-10-17-spell_id_wording_in_held_files at turn-in).
- [x] Notch, release-note bullet, closure, the rebuild last.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.

## Deliverables
- The reworded occurrences; the inventory with each decision and the list of occurrences kept, with reasons.

## Files / Paths Impacted
- src/ docstrings and comments (63 files hold the term; the ones relating to a spell index are edited)
- tests/ docstrings and comments (61 files hold the term)
- context_compass/system_docs/ (src_architecture, src_components, tests_components, their indexes; graph
  descriptors and the assembled graph)
- release_docs/next_version_release.md; src/melder/__version__.py (the notch)

## Validation
- Run on the landed scope (MEASURE notes 2026-10-16T18:56:42Z, 19:11:31Z, 20:06:44Z): py_compile of every
  touched file; the touched files' unit, component and integration tests with the GIL off and on, green but
  for a pre-existing order dependence (fixed by TASK-2026-10-16-stamp_test_boots_its_own_aether). At turn-in:
  the asset and LLM bundle rebuilds, each with its --check. Not run: the whole test tree.
- Commands used:
  - python -m py_compile <every touched .py>
  - python -X gil=0 -m pytest -q -p no:cacheprovider <the touched test files>; the same with -X gil=1

## Risks / Rollback Notes
- A wrong replacement names the wrong id; each decision is made from the surrounding code, and an unclear one is
  asked, not guessed.
- Rollback: the edits are wording only; reverting the touched lines restores the old text.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without delegated acceptance or reserved-owner disposition and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/spell_id_wording_20261016/ (inventory, decisions, scripts, runs, notes)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: at closure the folder stays as the lane's evidence

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - which id "version id" names where it relates to a spell index
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Multiple meaningful comments or authorized documents may hold findings directly; no forced
  body copy of every finding is required before ordinary continuation.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose; created 2026-10-16T18:37:02Z; evidence in Notes.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-16T18:37:02Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's direction (chat 2026-10-16). First: "yeah version id can go its not necessary those can be
    removed because version id might mean spell_id or spell_index_id idk". Asked how far to go (every live
    occurrence with the test helpers renamed, wording only, or only the four named), he answered: "no not everywhere
    in the places where you think version id is related to spell index because thats the only location not do a
    blanket rename properly find all the spots and rename them by hand". So: every live occurrence is read in its
    context; where it relates to a spell index it is replaced by hand with the id it means - `spell_id` or the spell
    index id (`spell_index_id`); an occurrence with no relation to a spell index is kept and listed with its reason;
    code identifiers are not renamed (that is the blanket rename he declined); no patch lane, because nothing
    changes behaviour, a boundary or a contract - only words.
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-10-16_public_notch_target_for_staged_versions_task.md:809-811
  - src/melder/aether/spellbook/spellbook.py:2268-2285
  IMPACT: The lane is wording only; the src docstrings ship, so it takes one notch and the rebuild last.
  NEXT: Inventory every live occurrence with its context.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-16T18:37:02Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Where the term lives (grep, case-insensitive, `version[ _-]ids?`, live trees only): src 177 prose
    occurrences in 63 files plus 9 identifier uses in 2 files; tests 119 prose occurrences in 61 files plus 321
    identifier uses in 44 files (the three test helpers and local names); src_architecture 9, src_components 5,
    tests_components 2, tests_architecture 0; 16 in 9 graph descriptors (and so in the assembled graph); the
    release note 3; README, docs/ and the UX lessons none. 61 of the src occurrences sit in five files melder_1
    holds for its rule-2 lane until its closure: spellbook.py 28, spell_system_states.py 12, conduit_ward.py 9,
    conduit.py 8, meld.py 4; its lane also holds two new and nine changed test files, the system docs, the graph
    descriptors of its files and the release note (its turn-in waits on the owner's two questions).
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md:1135-1160
  - context_compass/tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md:1459-1491
  IMPACT: Most of the work is in files nobody holds; melder_1's files wait for its release (QUESTION M0-178).
  NEXT: Write the inventory with context and decide each occurrence.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-16T18:48:31Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Every occurrence is decided, by hand, before any edit. The inventory holds 330 lines with the term (src 177,
    tests 118 - in docstrings, comments and one test literal -, the system docs 16, graph descriptors 16, the
    release note 3, as `str.splitlines` numbers them), each with two lines of context. Read in context, every use
    names the id of a spell in an index lineage - a spell_id: the index's selected, current, parked or member
    spell's id, a lookup that answers through the index, a key set beside index ids - so 328 are rewritten by hand
    with the precise name (spell_id, spell_ids, "the selected spell_id of its index", "spell index id" where the
    index is meant), each as an exact old/new pair checked against its inventoried line; none means the index id.
    Two are kept: the 0.2.8249 handoff entries of src_architecture and src_components quote the retired term ("not
    'version id'") - a mention, not a use. One runtime text changes: IdentityMixingStrategy's diagnostic now ends
    "instead of a spell_id." (no test asserts the old text); one test literal becomes "updated-spell-id" (used only
    through its variable). Code names stay: the three test helpers, the local `version_id` names and parameters
    such as `version_id` in stubs (their descriptions are reworded). 204 decisions in 113 files nobody holds apply
    now; 124 in 24 files - melder_1's rule-2 files, the system docs, the graph descriptors and the release note -
    apply after melder_1 releases them (M0-178). The apply script refuses a moved line or an `old` that is not
    found exactly once, and keeps each line's own terminator (95 files are CRLF, 8 of them mixed).
  EVIDENCE:
  - context_compass/artifacts/spell_id_wording_20261016/inventory/occurrences.txt:1-2309
  - context_compass/artifacts/spell_id_wording_20261016/inventory/decisions_001_100.json:1-102
  - context_compass/artifacts/spell_id_wording_20261016/inventory/decisions_101_154.json:1-56
  - context_compass/artifacts/spell_id_wording_20261016/inventory/decisions_155_209.json:1-57
  - context_compass/artifacts/spell_id_wording_20261016/inventory/decisions_210_330.json:1-123
  - context_compass/artifacts/spell_id_wording_20261016/scripts/apply_decisions.py:1-160
  - src/melder/aether/spellbook/spell_compiler/system/validation/identity_mixing_strategy.py:90-100
  IMPACT: The edit is reviewable line by line; the held quarter waits without blocking the rest.
  NEXT: Apply the 204 free decisions, compile the touched files and run their tests with the GIL off and on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T18:56:42Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The decisions for files nobody holds are applied and checked. 204 applied in 113 files, then one undone:
    transfer_of_ownership.py:1798 is back to its text (equal to HEAD), because melder_1 holds that file (M1-22,
    below) and this lane's held list had missed it; that decision (V086) joins the held scope, which now holds 125
    decisions in 25 files. On the 112 files: compared with HEAD after normalising line endings, exactly the
    inventoried lines changed (204 lines, V139 being two); no "version id" is left in them; all compile. Tests of
    the 55 touched test files: unit 674 passed with the GIL on and 677 passed with it off, with one failure there
    that is an order dependence, not this change - test_aetheric_frame.py's fixture resets the Aether singleton
    after each test without booting it again, so test_spell_managed_quantity_stamp.py::test_stamping_into_a_real_
    root_store_creates_the_pool_there, which needs the hosted ReleaseManagedSpell, fails when it runs right after;
    alone that file passes (4 passed, GIL off and on) and the two files together reproduce it (1 failed, 39 passed);
    filed as TASK-2026-10-16-stamp_test_boots_its_own_aether (backlog). Component 220 passed and integration 87
    passed, GIL off and on.
  EVIDENCE:
  - context_compass/artifacts/spell_id_wording_20261016/runs/apply_free.txt:1-1
  - context_compass/artifacts/spell_id_wording_20261016/runs/apply_free_verify.txt:1-1
  - context_compass/artifacts/spell_id_wording_20261016/runs/free_rescan_compile.txt:1-1
  - context_compass/artifacts/spell_id_wording_20261016/runs/free_unit_gil0.txt:1-78
  - context_compass/artifacts/spell_id_wording_20261016/runs/free_unit_gil1.txt:1-11
  - context_compass/artifacts/spell_id_wording_20261016/runs/free_unit_stamp_alone_gil0.txt:1-2
  - context_compass/artifacts/spell_id_wording_20261016/runs/free_unit_stamp_alone_gil1.txt:1-2
  - context_compass/artifacts/spell_id_wording_20261016/runs/order_dependence_probe_gil0.txt:1-69
  - context_compass/artifacts/spell_id_wording_20261016/runs/free_component_gil0.txt:1-5
  - context_compass/artifacts/spell_id_wording_20261016/runs/free_component_gil1.txt:1-5
  - context_compass/artifacts/spell_id_wording_20261016/runs/free_integration_gil0.txt:1-3
  - context_compass/artifacts/spell_id_wording_20261016/runs/free_integration_gil1.txt:1-3
  - tests/unit/melder/aether/test_aetheric_frame.py:13-23
  - tests/unit/melder/spellbook/test_spell_managed_quantity_stamp.py:87-131
  IMPACT: Three quarters of the wording is done and green; the rest waits for melder_1's release.
  NEXT: Wait for melder_1's NOTICE; then apply the held scope, the system docs' indexes, the graph, the notch,
    the release-note bullet, closure and the rebuild.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T18:56:42Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Consumed M1-22 (melder_1's ACK of M0-178, 18:46:51Z): nothing it holds is free until rule 2's closure and
    rebuild - __version__.py, spellbook.py, spell_system_states.py, meld.py, conduit.py, conduit_ward.py,
    transfer_of_ownership.py, contract_provider_presence_strategy.py, spellbook_validation_error.py, rule 2's 11 test
    files, the four system docs and indexes, the graph and the release note; its closure waits on the owner's
    direction on three findings that may add edits to spellbook.py, conduit_ward.py and transfer_of_ownership.py; a
    NOTICE follows each release. This lane's held list now carries transfer_of_ownership.py and __version__.py too;
    the one line edited there was put back (NOTICE M0-179 tells melder_1).
  EVIDENCE: context_compass/tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md:1459-1491
  IMPACT: The notch, the system docs, the graph, the release note and 125 decisions wait for melder_1's release.
  NEXT: Wait for melder_1's NOTICE.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-16T19:11:31Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The order dependence holds with the GIL on too, and the GIL-on unit figure recorded at 18:56:42Z needs one
    precision. The frame file then the stamp file: 1 failed, 39 passed with the GIL off and with it on; the 23
    touched unit files with the GIL on: 1 failed, 677 passed, the same test (both modes collect 678 tests there).
    The "674 passed" with the GIL on was those files without the stamp file's 4 tests, which ran alone (4 passed).
    Filed as TASK-2026-10-16-stamp_test_boots_its_own_aether (backlog, test-only): the stamp test installs a fresh
    Aether around each test, as the managed store tests do.
  EVIDENCE:
  - context_compass/artifacts/spell_id_wording_20261016/runs/order_dependence_probe_gil1.txt:1-69
  - context_compass/artifacts/spell_id_wording_20261016/runs/free_unit_gil1_with_stamp.txt:1-78
  - context_compass/artifacts/spell_id_wording_20261016/runs/free_unit_gil1.txt:1-11
  - context_compass/tickets/tasks/backlog/2026-10-16_stamp_test_boots_its_own_aether_task.md:1-175
  IMPACT: No failure in this lane's runs comes from its edits; the one failure is pre-existing and now ticketed.
  NEXT: Hold for melder_1's release NOTICE.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-16T19:11:31Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: BLOCKER
  CLAIM: The rest of the lane is blocked on melder_1's release: 125 decisions in 25 files it holds - its rule-2 src
    (spellbook.py, spell_system_states.py, conduit_ward.py, conduit.py, meld.py, transfer_of_ownership.py,
    contract_provider_presence_strategy.py, spellbook_validation_error.py) and tests, the four system docs and their
    indexes, the graph descriptors and the release note - and the notch, since __version__.py is held too. melder_1
    releases them with a NOTICE after its closure and rebuild, and its closure waits on the owner's direction on its
    open findings (which copy an unlink removes after a notch, how transfers and contracts affect each other, rule
    2's binding-key gap on the transfer path). Unblock: that NOTICE; starting earlier would break one writer per file.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md:1502-1524
  - context_compass/tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md:1526-1558
  IMPACT: The notch, the release-note bullet, the system docs, the graph and closure wait; the free scope stays
    applied and green meanwhile.
  NEXT: On the NOTICE, recheck the held decisions against the files (re-inventory any moved line), then apply them.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-16T20:03:17Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The owner asked (chat 2026-10-16): "double check if we're not using a real version id somewhere else for
    something else". Audit of every live term of the family - version id / version_id / version-id / versionid
    and plurals, "version identifier", "version identity" - in src, tests, the system docs, graph descriptors,
    release note, README, docs/, agents/, architecture_and_design/, benchmarks/ and .github/, each hit classified
    by the token it sits in (492 hits). Every "version id" names a spell's own id, a spell_id: no src code
    identifier holds the term; the 310 test identifiers (the three helpers, `version_id` parameters, test names)
    all carry spell_ids (`spell_id: str` signatures, passed on as `spell_id=`); none of the 330 inventoried lines
    names another id (the six with the thinnest context re-read against their code - AethericFrame.spells_in_index
    returns each Book's `_spell_ids`). Real ids for other things exist and none was touched: the distribution
    version (verify_distributions.py, site_package_custody_strategy.py "name/version identity"), Nexus's published
    source id `spellbook_id:spell_id` ("book/version identity" in frame_viewer.py and view_spell.py) and a Phase-11
    `plan_version_id` in old benchmark plan notes (never implemented under that name). The other versions in src
    are format versions (RecordVersion, payload, nexus and profile versions, the cache generation, the package
    version), none called a version id; MutationResearch's "version identity" is the spell_id by contract.
  EVIDENCE:
  - context_compass/artifacts/spell_id_wording_20261016/runs/version_term_audit.txt:1-512
  - context_compass/artifacts/spell_id_wording_20261016/inventory/supplement_after_audit/other_version_terms.json:1-142
  - src/melder/mutation_research/research_set/research_node.py:20-23
  - src/melder/nexus/rift/command_system/command_system.py:1527-1551
  - src/melder/aether/aetheric_frame/aetheric_frame.py:906-940
  - src/melder/crystallizer/crystal_analysis/custody/site_package_custody_strategy.py:46-53
  - .github/scripts/verify_distributions.py:1-1
  - benchmarks/competitors/melder_implementation_plan/melder_system_maps/melder_override_codegen_supporting_notes.md:37-38
  IMPACT: Nothing renamed so far meant another id; the term had no second meaning in the code to protect.
  NEXT: Apply the lines the first inventory missed (DECISION below).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T20:03:17Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The first inventory missed 17 lines: its prose pattern did not take "version_id" written in docstrings or
    the spelled-out "version identifier", and it set every `version_id` aside as a code name. 12 are reworded by
    hand (V331-V340, V343-V344): SpellSystemAdjacencySnapshot's docstrings (3 lines) and
    SpellSystemRootBlueprintBuilder's (5), MeldExecutionError's `spell_id` argument, a test helper's Args line, and
    two lines of Conduit.get_spell_by_id (held: conduit.py). 5 stay (V341, V342, V345-V347): they name a stub
    parameter literally called `version_id` or `_version_id`, a code name the ruling keeps, and must match it.
    "version identity" is another phrase and is not changed: in MutationResearch, the Nexus diff commands,
    SpellCrystal.id, two system-doc lines and one graph descriptor it means the spell_id by contract (the owner's
    call whether to reword those); in the distribution check and the custody strategy it is the package version,
    and in the frame viewer the `spellbook_id:spell_id` source id - neither may become spell_id.
  EVIDENCE:
  - context_compass/artifacts/spell_id_wording_20261016/inventory/supplement_after_audit/occurrences.json:1-121
  - context_compass/artifacts/spell_id_wording_20261016/inventory/supplement_after_audit/decisions_331_347.json:1-87
  IMPACT: 10 apply now in four files nobody holds; 2 join the held scope (127 rewrites, 5 kept, in 25 files).
  NEXT: Apply the 10, compare with HEAD, compile, and run the touched tests with the GIL off and on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T20:06:44Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The 10 free lines are applied. Compared with HEAD (192482b4c, the owner's commit of 19:47Z, which already
    carries the first 204), exactly the inventoried lines changed in four files - the adjacency snapshot 84, 96 and
    108, the root blueprint builder 74, 75, 77, 81 and 334, MeldExecutionError 117 and the facade test 24 - and the
    fifth file (two kept lines) is byte-identical. The five files compile; their tests (5 files) passed, 55 with the
    GIL off and 55 with it on. The audit rerun finds no "version id" or "version identifier" left in prose outside
    the held files, apart from the two kept parameter descriptions and the benchmark notes' plan version id.
  EVIDENCE:
  - context_compass/artifacts/spell_id_wording_20261016/runs/apply_supplement_free.txt:1-3
  - context_compass/artifacts/spell_id_wording_20261016/runs/supplement_tests_gil0.txt:1-2
  - context_compass/artifacts/spell_id_wording_20261016/runs/supplement_tests_gil1.txt:1-2
  - context_compass/artifacts/spell_id_wording_20261016/runs/version_term_audit_after_supplement.txt:1-499
  IMPACT: The free scope is complete; the held scope is 127 rewrites and 5 kept lines in 25 files.
  NEXT: Hold for melder_1's release NOTICE.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-16T20:24:14Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: This lane carries one system-doc item for TASK-2026-10-16-stamp_test_boots_its_own_aether (closed,
    tests only): after melder_1 releases tests_components.md, its code-map entry for
    tests/unit/melder/spellbook/test_spell_managed_quantity_stamp.py moves to end_line and loc 185 (the file gained
    the 33-line fresh-Aether fixture) and its note names the fixture; the document's index is regenerated with the
    wording edits, in the same pass.
  EVIDENCE:
  - context_compass/system_docs/tests_components.md:3194-3199
  - context_compass/tickets/tasks/completed/2026-10-16_stamp_test_boots_its_own_aether_task.md:1-8
  IMPACT: One more held edit, in a document this lane edits anyway; no notch of its own (tests only).
  NEXT: Hold for melder_1's release NOTICE.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-17T19:50:33Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Consumed M1-23 (melder_1, 2026-10-16T22:01:54Z): it notched 0.2.8251 for the removal fix
    (`Spellbook._remove_contracted_spell` removes exactly the copy of the spell_id it is given); spellbook.py grew
    7 lines inside that method; every held file stays melder_1's until rule 2's closure and its rebuild. Rechecked
    against the files: of the 132 held records (127 rewrites, 5 kept) 113 sit where inventoried and 19 have moved
    with their text intact (the system docs, the release note, spellbook.py); none is gone. melder_1 now also sweeps
    the origins of the spell_id -> index -> active-spell swap on the owner's rule of 2026-10-17 (a lookup by
    spell_id returns that spell or nothing), which will rewrite docstrings these records reword.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md:1988-2009
  - src/melder/__version__.py:12-12
  IMPACT: The held rewording cannot be applied as inventoried; it is re-inventoried when the files are released.
  NEXT: Turn in this ticket (the owner, chat 2026-10-17); QUESTION M0-180 asks melder_1 for __version__.py and the
    release note for this ticket's notch and bullet.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-17T20:47:41Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Consumed M1-24 (melder_1's ACK of M0-180, 2026-10-17T20:38:54Z), copied before deletion: "Yes: write
    src/melder/__version__.py (one notch above what it reads), your one bullet in the release note's 'Packaging and
    documentation' section, then rebuild. I write neither file until your NOTICE says you are done; my next landing
    (the spell_id lookup fix, origin 1 only, owner-approved) takes the number above yours. The rest of my hold
    (M1-22) stands." melder_1 recorded the grant as a DECISION in its ticket. M0-181 and M0-182 are noted there; the
    conduit.py story and the minted-index registry go to the owner with its fix #1 report.
  EVIDENCE: context_compass/tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md:2115-2140
  IMPACT: The turn-in is unblocked: __version__ reads 0.2.8251, so this ticket notches 0.2.8252; the held rewording
    (127 rewrites, 5 kept lines, the tests_components entry) moves to the backlog successor, as M1-22 still holds.
  NEXT: Notch, the release-note bullet before the rebuild line, closure with board sync and NOTICE M0-183, then the
    rebuild last with both checks OK.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-17T21:00:59Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Turned in and rebuilt last at 0.2.8252, from the repository root on Python 3.14.7t. The first asset run
    on the connected folder wrote the agent-documentation and bind-guard manifests and the system-documents index,
    then stopped with PermissionError: the system-documents builder deletes its three payload modules before
    writing them again, and the folder refuses deletes. The runner was then run whole in a mirror under /tmp (src/,
    the system docs, pyproject, README, docs): all three assets at v0.2.8252 (468 agent-documentation entries, 628
    bind-guard entries, 4 system documents). The five files it changed beyond the real tree - the three payloads,
    the system-documents manifest and the graph adjacency manifest - were copied back over their originals
    (nothing deleted; byte-equal after copy), and the asset --check on the real tree printed only OK lines. The LLM
    bundles (--include-untracked) rewrote src (583 files), tests (1125) and other (404) and the manifest; their
    --check printed only OK lines.
  EVIDENCE:
  - context_compass/artifacts/spell_id_wording_20261016/runs/rebuild_0_2_8252_assets.txt:1-28
  - context_compass/artifacts/spell_id_wording_20261016/runs/rebuild_0_2_8252_assets_mirror.txt:1-7
  - context_compass/artifacts/spell_id_wording_20261016/runs/rebuild_0_2_8252_assets_check.txt:1-7
  - context_compass/artifacts/spell_id_wording_20261016/runs/rebuild_0_2_8252_llm.txt:1-8
  - context_compass/artifacts/spell_id_wording_20261016/runs/rebuild_0_2_8252_llm_check.txt:1-7
  - src/melder/_build_assets/_system_documents/_builder.py:575-578
  IMPACT: Code, docstrings, release note, notch and generated assets agree at 0.2.8252; __version__.py and the
    release note go back to melder_1 (NOTICE M0-183).
  NEXT: NOTICE M0-183 to melder_1; then EPIC-2026-10-17-correctness_defects sweep A6.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
- Scope: "version id" named by hand where it relates to a spell index (owner, 2026-10-16); wording only.
- State: done (melder_0), 2026-10-17T20:49:39Z, notched 0.2.8252. Landed: 214 lines in 113 files (the owner's
  commits 192482b4c and 5ac69ab51). Handed over: 127 rewrites, 5 kept lines and the tests_components
  entry, to TASK-2026-10-17-spell_id_wording_in_held_files (backlog, blocked on melder_1's release).
- Open for the owner: whether "version identity" is reworded too (DECISION, 2026-10-16T20:03:17Z).
- Evidence: the Notes; artifacts/spell_id_wording_20261016/.
- Next: none in this ticket.

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
