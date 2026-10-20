"""Open TASK-2026-10-16-spell_id_wording_near_spell_index: the ticket, its board rows and the question to melder_1.

Run from context_compass/:  python open_lane.py <NOW>
Writes the new ticket (refuses an existing file), adds the attention board row and detail, the artifact board row,
and appends QUESTION M0-178 to melder_1 with its alert. Every insertion point must exist exactly once; files keep LF.
"""
import pathlib
import sys

NOW = sys.argv[1]
TICKET = pathlib.Path("tickets/tasks/2026-10-16_spell_id_wording_near_spell_index_task.md")
TICKET_REL = "tickets/tasks/2026-10-16_spell_id_wording_near_spell_index_task.md"

TICKET_TEXT = """# Task: spell_id_wording_near_spell_index - name the id where "version id" meets the spell index

## Metadata
- Task ID: TASK-2026-10-16-spell_id_wording_near_spell_index
- Story: none (standalone; the owner's direction after TASK-2026-10-16-public_notch_target_for_staged_versions)
- Status: in_progress
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: <NOW>
- Updated: <NOW>

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
- from_state: draft
- to_state: in_progress
- transition_reason: opened in progress on the owner's direction (chat 2026-10-16, quoted in the DECISION note);
  melder_0 is assigned and its previous lane is closed.

## Steps / Checklist
- [ ] Inventory every live occurrence with its context; the decision for each, by hand.
- [ ] Apply the decisions in files nobody else holds; compile; the touched tests with the GIL off and on.
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
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose; created <NOW>; evidence in Notes.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: <NOW>
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

- DATETIME: <NOW>
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

## Context / Handoff Summary
- Scope: replace "version id" by hand where it relates to a spell index (owner, 2026-10-16); wording only, no
  identifier renamed, no blanket rename.
- State: in_progress (melder_0), discovery; inventory next.
- Owners: melder_1 holds five src files with 61 occurrences, its test files, the system docs, graph descriptors and
  the release note until its rule-2 closure (QUESTION M0-178).
- Next: the inventory with context; the decisions; the edits in files nobody holds.

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
"""


def insert_before(path: pathlib.Path, marker: str, text: str) -> None:
    """
    Insert text before a marker that occurs exactly once in an LF file.

    Args:
        path: The file.
        marker: The marker line.
        text: The text to insert (ends with a newline).
    """
    content = path.read_text(encoding="utf-8")
    assert "\r\n" not in content and content.count(marker) == 1, (str(path), content.count(marker))
    path.write_text(content.replace(marker, text + marker, 1), encoding="utf-8")


def main() -> None:
    """Write the ticket, the board rows and the question."""
    assert not TICKET.exists()
    body = TICKET_TEXT.replace("<NOW>", NOW)
    long_lines = [line for line in body.split("\n") if len(line) > 120]
    assert not long_lines, long_lines
    TICKET.write_text(body, encoding="utf-8")
    row = ("| spell_id_wording | in_progress | discovery | claude | melder_0 | melder_1 holds five src files, its tests, the "
           "system docs, graph and release note until its closure (M0-178) | Inventory every live 'version id' with "
           "its context and decide each by hand. | Every 'version id' that relates to a spell index names spell_id or "
           "the spell index id, by hand; the rest listed with reasons. | The wording lands with its notch, release note "
           "and rebuild, or the owner redirects. | " + TICKET_REL + " | " + NOW + " | REQUIRED |\n")
    insert_before(pathlib.Path("attention_board.md"), "<!-- END USER-DEFINED: active_items -->", row)
    detail = ("- WORK_ITEM: spell_id_wording\n"
              "  SWITCH_TRIGGER: The wording lands with its notch, release note and rebuild, or the owner redirects.\n"
              "  RESUME_HIERARCHY:\n"
              "    - " + TICKET_REL + "\n")
    insert_before(pathlib.Path("attention_board.md"), "<!-- END USER-DEFINED: active_attention_details -->", detail)
    art = ("| " + TICKET_REL + " | artifacts/spell_id_wording_20261016/ | investigation_evidence | active | "
           "retain_as_reference | The inventory of every live occurrence with its context, the per-occurrence "
           "decisions, the apply scripts and runs, the notes. | " + NOW + " | REQUIRED |\n")
    insert_before(pathlib.Path("artifact_board.md"), "<!-- END USER-DEFINED: active_artifacts -->", art)
    message = """- TO: melder_1
  FROM: melder_0
  DATETIME: """ + NOW + """
  TYPE: QUESTION
  CLAIM: M0-178. Owner (chat 2026-10-16): where "version id" relates to a spell index, replace it by hand with
    spell_id or the spell index id; no blanket rename, wording only. Of your rule-2 set it touches docstrings and
    comments in spellbook.py (28), spell_system_states.py (12), conduit_ward.py (9), conduit.py (8), meld.py (4),
    some test files, src_architecture / src_components / tests_components, graph descriptors and the release note.
    I edit none of them until you release them: please list what you hold and tell me when it is free.
  EVIDENCE: context_compass/""" + TICKET_REL + """
  ACK_REQUESTED: true
"""
    insert_before(pathlib.Path("mailbox_board.md"), "<!-- END USER-DEFINED: messages -->", message)
    insert_before(pathlib.Path("attention_board.md"), "<!-- END USER-DEFINED: alerts -->",
                  "- NEW MESSAGE for melder_1 (from melder_0, " + NOW + ")\n")
    print("opened:", TICKET)


if __name__ == "__main__":
    main()
