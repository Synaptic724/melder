"""File sweep A9's story (a notch whose commit fails); sync epic and boards.

Everything is rendered and checked in memory first, then written. Run from context_compass/ with <NOW>.
"""
import pathlib
import re
import sys

NOW = sys.argv[1]
EPIC = pathlib.Path("tickets/epics/2026-10-17_correctness_defects_epic.md")
S8 = "tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md"
S8_ID = "STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers"
S7_ID = "STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned"
TEMPLATE = pathlib.Path("templates/story_template.md").read_text(encoding="utf-8")
ART = "artifacts/correctness_defects_20261017/"
PROBE = ART + "probes/probe_failed_notch_commit.py"
RUN0 = ART + "runs/probe_failed_notch_commit_gil0.txt"
RUN1 = ART + "runs/probe_failed_notch_commit_gil1.txt"
CD = "src/melder/aether/conduit/conduit.py"
SB = "src/melder/aether/spellbook/spellbook.py"
CCM = "src/melder/aether/aetheric_frame/dev_ops/change_control_manager/"
MED = CCM + "transaction_manager/transaction_mediator.py"
SES = CCM + "transaction_manager/transaction_session.py"
ORC = CCM + "orchestrator/orchestrator.py"
CCMF = CCM + "change_control_manager.py"


def block(start: str, end: str) -> str:
    """Verbatim template text from heading `start` up to (not including) `end`."""
    i = TEMPLATE.index(start)
    return TEMPLATE[i:TEMPLATE.index(end, i)]


def check(text: str) -> str:
    """Refuse placeholders left and long lines that hold no path."""
    assert "@@" not in text
    long = [line for line in text.splitlines() if len(line) > 120 and "/" not in line]
    assert not long, long
    return text


BODY = """# Story: failed_notch_keeps_switch_without_borrowers - a notch that fails its commit leaves no half-made switch

## Metadata
- Story ID: """ + S8_ID + """
- Epic: EPIC-2026-10-17-correctness_defects
- Status: ready
- Owner: user
- Agent Name: unassigned
- Agent Role: UNKNOWN
- Priority: p2
- Created: @@NOW@@
- Updated: @@NOW@@

## User Narrative
As an agent notching to a version I staged, I want a notch that raises to leave the structure the way the exception
says it is - the lender and every borrower on one version - so that a failed notch never leaves the lender on the
new version and its borrowers on the old one.

## Value / MRP Alignment
Which version an index selects, and that its borrowers follow a notch, are structure (owner rulings: a notch only
moves which version is active; borrowers follow). Today a notch whose commit validation fails raises
SpellbookValidationError after the switch was made and before the borrowers were told: the lender's index selects
the broken version, the borrowers keep the old one, and the lender can meld neither by address nor the old version
by its spell_id until someone notches back. The structure is wrong after an operation that reported failure.

## Ticket Contract
- ENTRY_GATE: the owner's answer to the open question below; the owner schedules the story and assigns an agent;
  the holder of conduit.py and spellbook.py (melder_1, until its rule-2 closure) releases them or carries the fix;
  an active board row; patch docs for the notch's commit path (architecture, component and code-description: the
  change is in error and rollback semantics).
- EXECUTION_BOUNDARY: `Conduit.notch_spell` (its commit and its fan-out) and whatever the answer needs around the
  seam - a structural check of the incoming version before `_apply_notch` runs, rollback actions that undo the seam
  when the commit fails, or a fan-out that runs whatever the commit raises; regression tests; the system documents
  (the SpellIndex Mutation Entry sequence, a failure mode) with their indexes and the graph; the release note; one
  notch; the rebuild last.
- DEPENDENCIES: EPIC-2026-10-17-correctness_defects; the probe and its runs (Artifact Links);
  TASK-2026-10-16-notch_seam_checks_incoming_before_parking (the seam's own failure, inside the window);
  STORY-2026-10-17-notch_moves_signature_by_incoming_key_only (the frame claim an undo must give back).
- EXIT_GATE: probe N2 ends with the lender and its borrower on one version, as the answer says, and the exception
  saying which; N1 and N3 unchanged; regression tests pass with the GIL off and on; docs, notch and the rebuild with
  both checks OK.
- FAILURE_ESCALATION: DECISION_REQUEST for the open question; CONFLICT while conduit.py or spellbook.py is held, or
  if the seam task lands first with another order of checks.

## Requirements (Functional)
- A notch that raises from its commit leaves the lender and every linked borrower selecting the same version.
- Answer (a): nothing moves - the index still selects the outgoing version, the incoming one stays parked, the frame
  claim and the Nexus record name the outgoing version, the lender melds it by address and by spell_id, and the
  borrowers are untouched; the error says the notch did not happen and names the broken version.
- Answer (b): the switch stands and the borrower fan-out runs before the error propagates, so the borrowers follow
  the lender; the error says the broken version is now active and that a notch back restores the previous one.

## Requirements (Non-Functional)
- No new lock or lock-order edge; the warm meld path untouched. A notch whose commit succeeds pays nothing new
  beyond what the answer needs (under (a), a check that runs only for a version never compiled - the case the
  commit validator already compiles today).

## Scope Boundaries
- In scope: a notch whose transaction commit raises (phases 1-4 of a never-compiled incoming version failing in the
  change-control structural validator).
- Out of scope: a seam that raises inside the window (TASK-2026-10-16-notch_seam_checks_incoming_before_parking);
  melds in flight while a notch fans out (TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout); a
  bind whose commit fails (the same validator; not probed here).

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: the defect is proven on 0.2.8252 by a probe with the GIL off and on (Notes); one open question
  for the owner.

## Dependencies / Related Work
- TASK-2026-10-16-notch_seam_checks_incoming_before_parking (backlog): the same seam; a check moved ahead of the park
  there and a structural check ahead of the switch here would sit side by side.
- STORY-2026-10-17-notch_moves_signature_by_incoming_key_only: the seam's frame-claim step, which an undo reverses.

## Tasks (Implementation Checklist)
- [ ] Task: the owner's answer on the open question.
- [ ] Task: patch docs for the notch's commit path; the owner's approval.
- [ ] Task: the fix with symptom-named regression tests, docs, notch and the rebuild last.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- With English active, a borrower index-linked to its index and a staged version whose structure is broken (a
  constructor that takes its own class): `notch_spell` to it raises, and afterwards the lender's index and the
  borrower select the same version - English under (a), the broken version under (b); under (a) the lender melds
  English by address and by its spell_id.
- A notch to a sound version (N1) and a notch back (N3) behave as today.

## Validation / Test Plan
- Regression tests named for the symptom, e.g. `test_a_notch_refused_at_commit_leaves_the_old_version_active` and
  `test_a_notch_refused_at_commit_leaves_borrowers_on_the_lenders_version`; GIL off and on; the probe re-run. Not
  run: no fix exists yet.

## UX / API / Data Notes
- Visible today: `notch_spell` raises SpellbookValidationError "Spellbook validation failed. Broken spells: <name>.",
  then the lender's `meld(spellframe=..., binding_name=...)` raises the same error and `meld(spell_id=<old>)` raises
  KeyError "[MELD] No spell found with spell_id: ..." while the borrower holds the old version active. Under (a) the
  exception keeps its meaning and the world keeps working; under (b) the exception reports a notch that happened.

## Risks / Mitigations
- An undo after the seam must reverse every step `_apply_notch` takes (park, promote, index pointer, frame claim,
  lineage registration and verdicts, Nexus record); a check before the seam needs none, but must run phases 1-4 on a
  version that is still parked - UNKNOWN until the patch reads the phase runner for a parked spell.
- The seam journals the promotion and emits the index crystal inside the window; whichever answer is chosen, the
  research journal and the record should end up telling what happened.

@@ANTI@@
## Open Questions
- When a notch's commit validation fails, should the notch (a) be refused with nothing moved - the incoming version
  checked before the switch, or the switch undone; the patch picks the mechanism - so the error means it did not
  happen (recommended: the structural validator fails "instead of accepting a broken staged mutation", and
  notch_spell's other refusals change nothing), or (b) stand, with the borrowers moved to the broken version before
  the error propagates?

## Decision Log
- @@NOW@@: filed under EPIC-2026-10-17-correctness_defects from sweep A9 (Notes).

@@ARTIFACT_HEAD@@- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - """ + PROBE + """ (cases N1-N3)
  - """ + RUN0 + """
  - """ + RUN1 + """
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: the probe is re-run at the fix and kept as the defect's reproducer

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - a notch whose transaction commit fails after its seam ran
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose and evidence (the probe); filed @@NOW@@.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: @@NOW@@
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The defect, read whole and proven on 0.2.8252. `Conduit.notch_spell` runs the seam inside its transaction
    (`_notch_spell` -> `_apply_notch`: park the outgoing version and clean its creation context, promote the incoming
    one, repoint the index and the frame claim, emit the index crystal, journal the promotion, re-register the lineage
    gated, mark its dependents, publish the incoming version to Nexus, gate its verdicts), then calls
    `end_transaction(success=True)` outside its `try`. The commit runs the change-control commit validator: for a
    notch to a version never compiled, phases 1-4 (`_default_structural_validator`, which fails "instead of accepting
    a broken staged mutation"). When they fail, the orchestrator's abort hook is unset, the session holds no abort
    hook or rollback action (no caller of `register_rollback_action`, `register_abort_hook` or
    `ChangeControlManager.set_abort_hook` exists in src/melder), and the mediator re-raises: every change of the seam
    stays, and `notch_spell` exits before its borrower fan-out (`_deactivate_borrowed_spell`,
    `_activate_borrowed_spell`, `_emit_index_notch`). Probe N2 (English active, an index-linked borrower, SelfMade
    staged with a constructor that takes its own class): `notch_spell` raises SpellbookValidationError "Broken
    spells: SelfMade.", yet the lender's index selects SelfMade, active, with English parked; the borrower holds
    English active and SelfMade parked; the lender's meld by address raises that error and `meld(spell_id=English)`
    KeyError. N3: a notch back to English restores both sides. N1 (a sound version): owner and borrower follow.
    Identical with the GIL off and on.
  EVIDENCE:
  - """ + CD + """:5622-5759
  - """ + SB + """:3851-3904
  - """ + SB + """:3906-4061
  - """ + MED + """:1043-1091
  - """ + ORC + """:452-530
  - """ + CCMF + """:562-586
  - """ + CCMF + """:614-641
  - """ + CCMF + """:783-835
  - """ + SES + """:463-526
  - context_compass/""" + PROBE + """:1-171
  - context_compass/""" + RUN0 + """:1-34
  - context_compass/""" + RUN1 + """:1-34
  IMPACT: After an operation that reported failure the lender selects the new version and its borrowers the old one,
    against "borrowers follow", and the lender cannot meld the index by address until a notch back.
  NEXT: The owner's answer on the open question, then patch docs for the notch's commit path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

@@CLOSURE@@@@NOTING@@## Context / Handoff Summary
- Scope: a notch whose commit fails leaves the lender and its borrowers on one version (Requirements). Defect proven
  on 0.2.8252 (Notes); probe and runs in Artifact Links.
- State: ready, unassigned; filed by melder_0 under EPIC-2026-10-17-correctness_defects; one open question for the
  owner. The fix sits in conduit.py and spellbook.py, which melder_1 holds.
- Next: (1) the owner's answer and scheduling; (2) patch docs; (3) the fix, its tests, docs, notch and the rebuild.

@@TAIL@@"""

story = check(BODY.replace("@@ANTI@@\n", block("## Applicable Anti-Patterns", "## Open Questions"))
              .replace("@@ARTIFACT_HEAD@@", block("## Artifact Links (Optional)", "- ARTIFACTS_REQUIRED:"))
              .replace("@@CLOSURE@@", block("## Closure Confirmation", "## Noting Behavior"))
              .replace("@@NOTING@@", block("## Noting Behavior", "## Context / Handoff Summary"))
              .replace("@@TAIL@@", TEMPLATE[TEMPLATE.index("## Project-Specific Additions"):])
              .replace("@@NOW@@", NOW))

epic = EPIC.read_text(encoding="utf-8")
anchor = "  its parked versions and parked-only indexes uncleaned, beyond any cleanup (sweep A7).\n"
assert epic.count(anchor) == 1
epic = epic.replace(anchor, anchor + "- [ ] Story: " + S8_ID + " - a notch whose commit\n"
                    "  validation fails keeps its switch and leaves its borrowers behind (sweep A9).\n", 1)
log_anchor = ("  STORY-2026-10-17-minted_index_missing_from_frame_registry (residency_view; MEASURE note).\n")
assert epic.count(log_anchor) == 1
epic = epic.replace(log_anchor, log_anchor + "- " + NOW + ": sweep A9 filed\n  " + S8_ID + " (MEASURE note).\n", 1)
old_view = re.search(r"(?ms)^- State: in_progress \(melder_0\), discovery\. A1-A8 are done.*?\(S6\) are free\.\n",
                     epic).group(0)
new_view = ("- State: in_progress (melder_0), discovery. A1-A9 are done; eight stories filed (ready, unassigned):\n"
            "  STORY-2026-10-17-staged_version_releases_active_signature (p1),\n"
            "  STORY-2026-10-17-notch_moves_signature_by_incoming_key_only (p2, open question; its leaked claim\n"
            "  outlives the Book, A7),\n"
            "  STORY-2026-10-17-parked_cleanup_leaves_borrower_copies (p2),\n"
            "  STORY-2026-10-17-minted_index_missing_from_frame_registry (p2; MutationResearch residency\n"
            "  misses the version too, A8),\n"
            "  STORY-2026-10-17-restore_drops_separated_parked_version (p2, open question),\n"
            "  STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool (p2, open question),\n"
            "  " + S7_ID + " (p3) and\n"
            "  " + S8_ID + " (p2, open question).\n"
            "  Fixes in spellbook.py and conduit.py (S1-S4, S7, S8) wait for melder_1's release; restore_engine.py\n"
            "  (S5) and release_managed_spell.py (S6) are free.\n")
epic = epic.replace(old_view, new_view, 1)
old_next = ("- Next: (1) A9 what a notch whose commit validation fails leaves behind (A8 MEASURE note);\n"
            "  (2) tell the owner of the sixth and seventh stories, the sixth's question and the A7/A8 widenings.\n")
assert epic.count(old_next) == 1
epic = epic.replace(old_next, "- Next: (1) NOTICE melder_1 (M0-184) of S7, S8 and the A7/A8 widenings; (2) tell the owner of\n"
                    "  S6-S8, their open questions and the widenings; (3) plan the next tranche (PLAN note).\n", 1)
epic, count = re.subn(r"(?m)^- Updated: \S+$", "- Updated: " + NOW, epic, count=1)
assert count == 1
check(epic)

art = pathlib.Path("artifact_board.md")
a = art.read_text(encoding="utf-8")
end_art = "<!-- END USER-DEFINED: active_artifacts -->"
assert a.count(end_art) == 1 and S8 not in a
rows = ("| " + S8 + " | " + PROBE + " | defect_reproducer | ready | retain_as_reference | Cases N1 (control), N2 and N3 "
        "with their runs (runs/probe_failed_notch_commit_gil0.txt, _gil1.txt); re-run at the fix. | " + NOW
        + " | HELPFUL |\n")

board = pathlib.Path("attention_board.md")
b = board.read_text(encoding="utf-8")
old_row_next = ("| Sweep A9: read the notch transaction's commit path whole and probe what a notch whose commit "
                "validation fails leaves behind. |")
assert b.count(old_row_next) == 1
b = b.replace(old_row_next, "| NOTICE melder_1 (M0-184) of the teardown and failed-notch stories and the two widenings, "
              "then tell the owner of S6-S8 and their questions. |", 1)
row_re = re.compile(r"^(\| correctness_defects \|.*\| tickets/epics/2026-10-17_correctness_defects_epic\.md \| )\S+( \| REQUIRED \|)$", re.M)
assert len(row_re.findall(b)) == 1
b = row_re.sub(lambda m: m.group(1) + NOW + m.group(2), b, count=1)

if "--dry-run" in sys.argv:
    print(story[:300])
    print("dry run OK")
    sys.exit(0)
target = pathlib.Path(S8)
assert not target.exists()
target.write_text(story, encoding="utf-8")
EPIC.write_text(epic, encoding="utf-8")
art.write_text(a.replace(end_art, rows + end_art, 1), encoding="utf-8")
board.write_text(b, encoding="utf-8")
print("filed", S8, NOW)
