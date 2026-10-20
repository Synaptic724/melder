"""Open EPIC-2026-10-17-correctness_defects: the epic file, its board row and detail, its artifact row.

Run from context_compass/:  python3 artifacts/correctness_defects_20261017/scripts/open_lane.py <NOW>
"""
import pathlib
import sys

NOW = sys.argv[1]
EPIC = "tickets/epics/2026-10-17_correctness_defects_epic.md"
TEMPLATE = pathlib.Path("templates/epic_template.md").read_text(encoding="utf-8")


def block(start: str, end: str) -> str:
    """Verbatim template text from the heading `start` up to (not including) the heading `end`."""
    i = TEMPLATE.index(start)
    return TEMPLATE[i:TEMPLATE.index(end, i)]


BODY = """# Epic: correctness_defects - structure Melder records wrong or leaves stuck

## Metadata
- Epic ID: EPIC-2026-10-17-correctness_defects
- Status: in_progress
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: @@NOW@@
- Updated: @@NOW@@
- Target Window: 2026-Q4
- Related Program/Initiative: Melder runtime correctness (the owner's direction, chat 2026-10-17)

## Problem / Opportunity
The owner asked for a hunt for correctness defects (chat 2026-10-17): "start looking up for more correctness stuff
but remember melder_1 is active in the system and please keep the understanding of what we talked about earlier
front and center and if you find a bug just make a generic epic to cover this and add a story for each one please".
This epic is that generic container: the sweep is recorded here, and every confirmed defect gets its own story with
a reproducer and the source range of the failing logic. Fixes are separate lanes the owner schedules.

## MRP Alignment (Most Reasonable Product)
Melder is a runtime agents live and build in, not a DI container, and its structure is the contract: bindings,
spell indexes and their versions, which conduit owns which spell, contracts and links, lineage and clusters,
verdicts, and the record the Crystallizer keeps of them. A defect is structure that is wrong or stuck. Finding
those, and only those, keeps the core trustworthy without judging Melder by rules it does not follow.

## Ticket Contract
- ENTRY_GATE: the owner's direction and the rulings that define a defect recorded (DECISION note); the active board
  row; the sweep plan (PLAN note); melder_1's open lane named and excluded.
- EXECUTION_BOUNDARY: read-only on src/ and tests/; probes and runs under artifacts/correctness_defects_20261017/;
  one story per confirmed defect in tickets/stories/ (ready; the owner schedules its fix). No src/ edit here: a fix
  opens its own lane on the owner's word, with the patch gate. Nothing in melder_1's lane
  (TASK-2026-10-16-recheck_contract_consumers_when_provider_changes): the spell_id -> index -> active-spell swap and
  its six origins, contracts versus transfers, the binding-key gap on the transfer flip, the contract notification
  route; nor the backlog tasks already filed (TASK-2026-10-16-investigate_lent_consumer_provider_loss,
  TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout,
  TASK-2026-10-16-notch_seam_checks_incoming_before_parking).
- DEPENDENCIES: src_architecture "What Melder Is" and "Runtime Model: Structure Is the Contract"; the owner's rulings
  recorded in melder_1's ticket (the spell_id lookup rule, the sharing rule, the notification model).
- EXIT_GATE: every planned area swept and recorded (a defect filed, or checked with the reason it is not one); each
  defect story carries a reproducer run with the GIL off and on and the source range of the failing logic; the
  owner's disposition of the epic; board sync.
- FAILURE_ESCALATION: DECISION_REQUEST when the intended behaviour is unclear - asked, never called a bug; CONFLICT
  when a finding falls in melder_1's lane - sent to melder_1 by mailbox, not filed here.

## Goals (Outcomes)
- Defects where structure is wrong or stuck, each a story the owner can schedule.
- A record of what was swept and why the rest is not a defect, so the next hunt starts past it.

## Non-Goals (Explicit Exclusions)
- DI-container judgments: one live instance per type, every object torn down with its scope, the newest version
  replacing the old. Old versions alive, objects left pending after a transfer or a contract change, and borrowers
  rebuilding after a notch are features.
- Userland objects: Melder does not dispose an object because something else changed.
- Fixes, and any src/ edit.
- Doc-versus-source polish (EPIC-2026-09-27-defect-hunting).
- melder_1's lane and the backlog tasks named in the Ticket Contract.

## Scope Boundaries
- In scope: the structure the runtime records and gates - bind and bind_inactive, the notch, the index moves,
  cleanup_spell, owner stamps, links and contracts outside melder_1's lane, lineage and clusters, verdicts
  (SpellSystemStates, RiskManager), the Crystallizer record and its restore, MutationResearch residency, Nexus
  publication of that structure.
- Out of scope: everything under Non-Goals.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the owner's direction (chat 2026-10-17); the sweep starts with its plan recorded (PLAN note).

## Success Metrics
- Each defect reproduces on the current tree from a probe in the artifacts folder.
- No story files behaviour the rulings call a feature.

## Requirements (Functional + Non-Functional)
- Every claim cites the source range covering the logic it describes, read whole; a search hit is not evidence.
- Each defect names the ruling or contract it breaks and what the structure should be instead.
- Probes import src/ read-only, write only under the artifacts folder, and run with the GIL off and on.

## Constraints / Assumptions
- melder_1 is active and holds its rule-2 files; nothing here writes them.
- Device runs: `. ~/.melder_env`, TMPDIR under /tmp, each call under 180 s.

## Dependencies / External References
- context_compass/system_docs/src_architecture.md (What Melder Is; Runtime Model; Operational Invariants)
- context_compass/tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md

## Milestones (Track Progress)
- [x] Milestone 1: sweep plan recorded - areas, order, exclusions (PLAN note).
- [ ] Milestone 2: areas swept - each recorded as a defect or as checked with its reason.
- [ ] Milestone 3: a story per confirmed defect; the owner told what was found.

## Stories (Required to Complete)
- none yet; one per confirmed defect.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- The planned areas are swept and recorded; every confirmed defect has a story with its evidence; the owner has
  dispositioned the epic.

## Risks / Mitigations
- Calling a feature a bug: each finding is checked against the rulings and its code path read whole; unclear intent
  goes to the owner as a question.
- Overlap with melder_1: its ticket is read before each filing; a finding in its lane goes to it by mailbox.
- A probe that writes outside its folder: probes run from the artifacts folder with src/ on sys.path only.

@@ANTI@@
## Validation / Test Approach
- Each probe runs with `-X gil=0` and `-X gil=1`; each story's validation plan names a symptom-named regression test.

## Rollout / Adoption Plan
- Stories go to the owner; each fix is its own lane with the patch gate, its notch and the rebuild.

## Open Questions
- none yet.

## Decision Log
- @@NOW@@: opened on the owner's direction (DECISION note).

@@ARTIFACT_HEAD@@- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/correctness_defects_20261017/ (probes, runs, notes, scripts)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: at closure the folder stays as the sweep's evidence; each defect's reproducer is rowed under its
  story as well

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - correctness defects in the structure Melder records and gates
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose; created @@NOW@@; evidence in Notes.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: @@NOW@@
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's direction (chat 2026-10-17), quoted under Problem / Opportunity: hunt for correctness defects,
    remember melder_1 is active, keep the earlier understanding front and center, one generic epic and a story per
    bug. What counts as a defect is the owner's: Melder is a runtime agents live and build in; structure is the
    contract; versions coexist and a notch only moves which one is active; borrowers follow; objects keep what
    they were built with; a transfer hands over stewardship; Melder does not police userland objects; a defect is
    structure that is wrong or stuck; read the code path before calling a bug and ask when the intent is unclear;
    bind_inactive behaves the same before and after conjure. Recorded in melder_1's ticket on 2026-10-17: a lookup
    by spell_id returns the spell that owns it, active or parked, or nothing - never the index's active spell;
    sharing an index follows its active spell, sharing a spell by id is exactly that spell; contract rows carry no
    active/inactive state; SpellSystemStates has nothing to do with contracts - a contract change notifies the
    impacted spells, which then run their resolution. melder_1 owns the swap's fix and the contract and transfer
    items; this epic files nothing there.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:3-54
  - context_compass/system_docs/src_architecture.md:1195-1215
  - context_compass/tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md:1854-1881
  - context_compass/tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md:1988-2010
  - context_compass/tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md:2063-2083
  - context_compass/tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md:2085-2112
  IMPACT: A finding is filed only when it breaks one of these; a finding inside melder_1's lane goes to melder_1.
  NEXT: Sweep A1 (PLAN note).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: @@NOW@@
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: The sweep, in this order; each area read whole from its public verb down to every structure it writes,
    then probed where reading leaves a doubt:
    A1 bind_inactive before and after conjure - does a version staged before conjure end in the same structure as
       one staged after (lineage state and verdicts, the owner stamp, the Crystallizer record, MutationResearch's
       staged event, Nexus publication, index-link borrowers)? By the owner's rule any difference is a defect.
    A2 cleanup_spell of a parked version - does every structure that holds it let it go (the Book's maps, its
       index, SpellSystemStates, the record, research residency, a borrower's copy through an index link)?
    A3 the index moves - add_to_spell_index, remove_from_spell_index and the fresh index remove mints: do the
       record, the registry and every index-link borrower follow the member?
    A4 the notch's records - the Crystallizer's selection, MutationResearch's promoted event, Nexus's published
       active version.
    A5 restore and graft of a world with parked versions and index moves - does the rebuilt structure equal the
       recorded one?
    Out: melder_1's lane and the three backlog tasks the Ticket Contract names.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:948-1011
  - context_compass/system_docs/src_architecture.md:1195-1215
  IMPACT: The sweep starts where the owner's rulings are sharpest (staged versions, removal, index moves).
  NEXT: Read Spellbook.bind_inactive and SpellbookCreationSystem.define_conduit_into_spells whole, then every
    structure each writes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

@@CLOSURE@@@@NOTING@@## Context / Handoff Summary
- Scope: correctness defects - structure Melder records wrong or leaves stuck - by the owner's rulings (DECISION
  note); read-only; one story per confirmed defect; melder_1's lane excluded.
- State: in_progress (melder_0), discovery since @@NOW@@. Stories: none yet.
- Next: (1) sweep A1, bind_inactive before and after conjure; (2) A2-A5 in order (PLAN note); (3) a story per
  confirmed defect, then tell the owner.

@@TAIL@@"""

text = (BODY.replace("@@ANTI@@\n", block("## Applicable Anti-Patterns", "## Validation / Test Approach"))
        .replace("@@ARTIFACT_HEAD@@", block("## Artifact Links (Optional)", "- ARTIFACTS_REQUIRED:"))
        .replace("@@CLOSURE@@", block("## Closure Confirmation", "## Noting Behavior"))
        .replace("@@NOTING@@", block("## Noting Behavior", "## Context / Handoff Summary"))
        .replace("@@TAIL@@", TEMPLATE[TEMPLATE.index("## Project-Specific Additions"):])
        .replace("@@NOW@@", NOW))
assert "@@" not in text
long = [line for line in text.splitlines() if len(line) > 120 and "context_compass/" not in line]
assert not long, long
path = pathlib.Path(EPIC)
assert not path.exists()
path.write_text(text, encoding="utf-8")

board = pathlib.Path("attention_board.md")
b = board.read_text(encoding="utf-8")
assert "| correctness_defects |" not in b and "WORK_ITEM: correctness_defects" not in b
row = ("| correctness_defects | in_progress | discovery | claude | melder_0 | none | Sweep A1: bind_inactive before and "
       "after conjure - every structure it writes, read whole. | Defects where Melder's structure is wrong or stuck, a "
       "story each with a reproducer; the rest recorded as checked. | Every planned area swept and its defects filed as "
       "stories, or the owner redirects. | " + EPIC + " | " + NOW + " | REQUIRED |\n")
end_rows = "<!-- END USER-DEFINED: active_items -->"
assert b.count(end_rows) == 1
b = b.replace(end_rows, row + end_rows, 1)
detail = ("- WORK_ITEM: correctness_defects\n  SWITCH_TRIGGER: Every planned area swept and its defects filed as stories, "
          "or the owner redirects.\n  RESUME_HIERARCHY:\n    - " + EPIC + "\n")
end_details = "<!-- END USER-DEFINED: active_attention_details -->"
assert b.count(end_details) == 1
b = b.replace(end_details, detail + end_details, 1)
board.write_text(b, encoding="utf-8")

art = pathlib.Path("artifact_board.md")
a = art.read_text(encoding="utf-8")
arow = ("| " + EPIC + " | artifacts/correctness_defects_20261017/ | investigation_evidence | active | retain_as_reference | "
        "Probes, runs, notes and scripts of the correctness sweep; each confirmed defect's reproducer is rowed under "
        "its story too. | " + NOW + " | REQUIRED |\n")
end_art = "<!-- END USER-DEFINED: active_artifacts -->"
assert a.count(end_art) == 1 and EPIC not in a
art.write_text(a.replace(end_art, arow + end_art, 1), encoding="utf-8")
print("opened", EPIC, NOW, len(text.splitlines()), "lines")
