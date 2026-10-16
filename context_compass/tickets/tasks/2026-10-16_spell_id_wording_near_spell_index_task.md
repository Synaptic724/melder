# Task: spell_id_wording_near_spell_index - name the id where "version id" meets the spell index

## Metadata
- Task ID: TASK-2026-10-16-spell_id_wording_near_spell_index
- Story: none (standalone; the owner's direction after TASK-2026-10-16-public_notch_target_for_staged_versions)
- Status: blocked
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-10-16T18:37:02Z
- Updated: 2026-10-16T19:11:31Z

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
- from_state: in_progress
- to_state: blocked
- transition_reason: the decisions for files nobody holds are applied and green (MEASURE, 18:56:42Z); the
  125 left sit in files melder_1 holds until its rule-2 closure and rebuild (M1-22), so the lane waits for its
  release NOTICE (BLOCKER, 2026-10-16T19:11:31Z).

## Steps / Checklist
- [x] Inventory every live occurrence with its context; the decision for each, by hand.
- [x] Apply the decisions in files nobody else holds; compile; the touched tests with the GIL off and on.
- [ ] After melder_1 releases its files: the same for them, the system docs, the graph and the release note.
- [ ] Notch, release-note bullet, closure, the rebuild last.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
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
- Not run.
- Recommended commands:
  - python -m py_compile <every touched .py>
  - python -X gil=0 -m pytest -q -p no:cacheprovider <the touched test files>; the same with -X gil=1

## Risks / Rollback Notes
- A wrong replacement names the wrong id; each decision is made from the surrounding code, and an unclear one is
  asked, not guessed.
- Rollback: the edits are wording only; reverting the touched lines restores the old text.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without delegated acceptance or reserved-owner disposition and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Board sync completed for successor routing or closure anchor update.

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

## Context / Handoff Summary
- Scope: replace "version id" by hand where it relates to a spell index (owner, 2026-10-16); wording only, no
  identifier renamed, no blanket rename.
- State: blocked (melder_0) since 2026-10-16T19:11:31Z. 204 decisions applied in 112 files nobody holds (one more, in
  transfer_of_ownership.py, undone), checked against HEAD, compiled, tests green with the GIL off and on apart from
  the pre-existing order dependence filed as TASK-2026-10-16-stamp_test_boots_its_own_aether (backlog).
- Hold: 125 decisions in 25 files melder_1 holds - its rule-2 src and tests, the four system docs and indexes, the
  graph descriptors, the release note and __version__.py - until its closure and rebuild (M1-22); that closure waits
  on the owner's direction on its open findings (BLOCKER note).
- Evidence: inventory, decisions, scripts and runs in artifacts/spell_id_wording_20261016/; Notes 18:37:02Z on.
- Next: (1) on melder_1's NOTICE, recheck the held decisions against the files (re-inventory any moved line) and
  apply them, then py_compile and their tests with the GIL off and on; (2) the system doc indexes, the graph
  descriptors and reassembly, each with its check; (3) the notch above __version__, the release-note bullet under
  Packaging and documentation, closure and board sync, the rebuild last with both checks OK.

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
