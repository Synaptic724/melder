"""File sweep A12's story (the minted index selects its parked version); widen S1 and S5; sync epic and boards.

Everything is rendered and checked in memory first, then written. Run from context_compass/ with <NOW>.
The S1 and S5 FACT notes are appended separately with append_note.py before this runs.
"""
import pathlib
import re
import sys

NOW = sys.argv[1]
EPIC = pathlib.Path("tickets/epics/2026-10-17_correctness_defects_epic.md")
S10 = "tickets/stories/2026-10-17_minted_index_selects_its_parked_version_story.md"
S10_ID = "STORY-2026-10-17-minted_index_selects_its_parked_version"
S9_ID = "STORY-2026-10-17-direct_cleanup_of_active_member_orphans_parked_versions"
S1 = "tickets/stories/2026-10-17_staged_version_releases_active_signature_story.md"
S5 = "tickets/stories/2026-10-17_restore_drops_separated_parked_version_story.md"
TEMPLATE = pathlib.Path("templates/story_template.md").read_text(encoding="utf-8")
ART = "artifacts/correctness_defects_20261017/"
PROBE = ART + "probes/probe_graft_parked_members.py"
RUN0 = ART + "runs/probe_graft_parked_members_gil0.txt"
RUN1 = ART + "runs/probe_graft_parked_members_gil1.txt"
SB = "src/melder/aether/spellbook/spellbook.py"
SI = "src/melder/aether/spellbook/bind/spell_index.py"
GR = "src/melder/crystallizer/crystal_loader_system/graft_runner.py"
PP = "src/melder/crystallizer/persistence/persistence_profile.py"


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


BODY = """# Story: minted_index_selects_its_parked_version - an index never names a parked version as its active one

## Metadata
- Story ID: """ + S10_ID + """
- Epic: EPIC-2026-10-17-correctness_defects
- Status: ready
- Owner: user
- Agent Name: unassigned
- Agent Role: UNKNOWN
- Priority: p3
- Created: @@NOW@@
- Updated: @@NOW@@

## User Narrative
As an agent who separates a parked version into its own index and later records or grafts that index, I want the
index to say that its version is parked, so that the record and a graft bring the version back parked, as it was,
instead of active.

## Value / MRP Alignment
Which version of a lineage is active is structure (owner ruling: a notch only moves which version is active). The
index `remove_from_spell_index` mints names its parked member as its selection, so the index and the Book disagree;
the Crystallizer record keeps the index's answer and a graft acts on it, turning a parked version into an active one.

## Ticket Contract
- ENTRY_GATE: the owner's answer to the open question below and to the open question of
  STORY-2026-10-17-restore_drops_separated_parked_version (what a restore or a graft of a parked-only index should
  produce); the owner schedules the story and assigns an agent; melder_1 has released spellbook.py; an active board
  row; patch docs for the seam (and for SpellIndex when the answer is (a)).
- EXECUTION_BOUNDARY: `Spellbook._apply_remove_from_index` and, per the answer, `SpellIndex` (an index whose
  members are all parked selects nothing) with the readers of `selected_spell_id` that assume an active version -
  or those readers alone (the record's index crystal, the graft runner, `_is_selected_unless_cleaned`); regression
  tests; the system documents (the SpellIndex Mutation Surface, a failure mode) with their indexes and the graph;
  the release note; one notch; the rebuild last.
- DEPENDENCIES: EPIC-2026-10-17-correctness_defects; the probe and its runs (Artifact Links);
  STORY-2026-10-17-minted_index_missing_from_frame_registry (the same seam: one patch can carry both);
  STORY-2026-10-17-restore_drops_separated_parked_version (the restore and graft lanes for a parked-only index).
- EXIT_GATE: probe G2 no longer brings French back active (it comes back parked, or the graft refuses with a reason,
  per S5's answer), and the live minted index no longer names French as selected (or no reader treats that as
  active, per the answer); G1, G3 and G4 unchanged; regression tests pass with the GIL off and on; docs, notch and
  the rebuild with both checks OK.
- FAILURE_ESCALATION: DECISION_REQUEST for the open question; CONFLICT while spellbook.py is held, or if the S4 fix
  lands first with another shape for the minted index.

## Requirements (Functional)
- No index names a parked version as the version it selects: after `remove_from_spell_index`, the minted index's
  selection does not make its parked member read as active to any reader (the record, a graft,
  `_is_selected_unless_cleaned`, which is documented to answer False for a parked member).
- A notch inside the minted index still makes its member active, and from then on the index selects it.
- A graft of the minted index's record never binds the parked member active.

## Requirements (Non-Functional)
- `selected_spell_id` is the compiler's hottest fingerprint read; answer (a) must keep that read lock-free and cheap,
  and the patch must enumerate its readers before changing what it may return.

## Scope Boundaries
- In scope: the selection of the index `remove_from_spell_index` mints, and what readers make of it.
- Out of scope: the frame registration of that index (S4); rebuilding it parked through restore or graft (S5); the
  throwaway index Bind mints inside `bind_inactive`, which never outlives the call.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: the defect is proven on 0.2.8252 by a probe with the GIL off and on (Notes); one open question
  for the owner.

## Dependencies / Related Work
- STORY-2026-10-17-minted_index_missing_from_frame_registry (same seam).
- STORY-2026-10-17-restore_drops_separated_parked_version (restore drops the version; graft activates it).

## Tasks (Implementation Checklist)
- [ ] Task: the owner's answer on the open question (and S5's).
- [ ] Task: patch docs for the seam; the owner's approval.
- [ ] Task: the fix with symptom-named regression tests, docs, notch and the rebuild last.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- After `remove_from_spell_index(spell_id=French)`: the minted index does not report French as active - to the
  record, to `_is_selected_unless_cleaned(French)` (False) and to a graft.
- Grafting that index's record into a host never makes French active there.
- After a notch to French inside the minted index, the index selects French as today.

## Validation / Test Plan
- Regression tests named for the symptom, e.g. `test_a_minted_index_does_not_select_its_parked_version` and
  `test_graft_of_a_parked_only_index_does_not_activate_its_version`; GIL off and on; the probe re-run. Not run: no
  fix exists yet.

## UX / API / Data Notes
- Visible today: `minted_index.selected_spell_id` returns the parked version's spell_id, the captured graft record's
  `index_payload["selected_spell_id"]` names it while its member's `custody_state` is "inactive", and
  `graft_index` reports `members_bound: 1, members_parked: 0` with the version active in the host.

## Risks / Mitigations
- Answer (a) changes what `selected_spell_id` may return; every reader must be checked, the compiler's included.
  Answer (b) keeps the field and moves the truth to the readers, which can drift again.

@@ANTI@@
## Open Questions
- Should the index `remove_from_spell_index` mints (a) select nothing until a notch makes its member active
  (recommended: the index then says what is true, and the notch already handles an index with no active version),
  or (b) keep naming its member while the record, the graft and the release resolver check the Book's active map
  instead of trusting the selection?

## Decision Log
- @@NOW@@: filed under EPIC-2026-10-17-correctness_defects from sweep A12 (Notes).

@@ARTIFACT_HEAD@@- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - """ + PROBE + """ (case G2, with G1 and G3 as controls)
  - """ + RUN0 + """
  - """ + RUN1 + """
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: the probe is re-run at the fix and kept as the defect's reproducer

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - the selection of the index remove_from_spell_index mints
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
  CLAIM: The defect, read whole and proven on 0.2.8252. `_apply_remove_from_index` mints `SpellIndex(initial_id=
    spell_id)`, whose constructor makes its one member the selection, and leaves it so while the member stays parked
    in the Book. `selected_spell_id` is documented as "the active spell's id" and `_is_selected_unless_cleaned` as
    answering False for a parked member; for the minted index both name the parked version. The record's index
    crystal captures that selection, and `GraftRunner.run` (fresh-index mode) binds the selected member active and
    parks only the others. Probe G2: French separated into the minted index (parked in the Book); the live index
    selects French; the record says selected French with French's custody "inactive"; the graft reports one bound,
    none parked, and the host holds French active. G1 and G3 graft members of a registered index right. Identical
    with the GIL off and on.
  EVIDENCE:
  - """ + SB + """:4271-4356
  - """ + SI + """:83-116
  - """ + SI + """:143-164
  - """ + SI + """:358-388
  - """ + PP + """:900-969
  - """ + GR + """:230-330
  - """ + GR + """:375-489
  - context_compass/""" + PROBE + """:1-152
  - context_compass/""" + RUN0 + """:1-26
  - context_compass/""" + RUN1 + """:1-26
  IMPACT: A parked version comes back active from a graft; the index and the Book disagree on what is active.
  NEXT: The owner's answer on the open question (and S5's), then patch docs for the seam.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

@@CLOSURE@@@@NOTING@@## Context / Handoff Summary
- Scope: the index `remove_from_spell_index` mints never names its parked version as active (Requirements). Defect
  proven on 0.2.8252 (Notes); probe and runs in Artifact Links.
- State: ready, unassigned; filed by melder_0 under EPIC-2026-10-17-correctness_defects; one open question for the
  owner. The fix sits in spellbook.py (S4's seam), which melder_1 holds.
- Next: (1) the owner's answers (this story's and S5's) and scheduling; (2) patch docs; (3) the fix, its tests,
  docs, notch and the rebuild.

@@TAIL@@"""

story = check(BODY.replace("@@ANTI@@\n", block("## Applicable Anti-Patterns", "## Open Questions"))
              .replace("@@ARTIFACT_HEAD@@", block("## Artifact Links (Optional)", "- ARTIFACTS_REQUIRED:"))
              .replace("@@CLOSURE@@", block("## Closure Confirmation", "## Noting Behavior"))
              .replace("@@NOTING@@", block("## Noting Behavior", "## Context / Handoff Summary"))
              .replace("@@TAIL@@", TEMPLATE[TEMPLATE.index("## Project-Specific Additions"):])
              .replace("@@NOW@@", NOW))


def link_probe(path: str, after: str, lines: str) -> str:
    """Add artifact paths to a story's Artifact Links after the line `after`; set Updated."""
    text = pathlib.Path(path).read_text(encoding="utf-8")
    assert text.count(after) == 1
    text = text.replace(after, after + lines, 1)
    text, count = re.subn(r"(?m)^- Updated: \S+$", "- Updated: " + NOW, text, count=1)
    assert count == 1
    return check(text)


s1 = link_probe(S1, "  - " + ART + "runs/probe_restore_staged_structure_gil1.txt\n",
                "  - " + PROBE + " (case G4: every graft of such an index; FACT note)\n"
                "  - " + RUN0 + "\n  - " + RUN1 + "\n")
s5 = link_probe(S5, "  - " + ART + "runs/probe_restore_staged_structure_gil1.txt\n",
                "  - " + PROBE + " (case G2: the graft activates the separated version; FACT note)\n"
                "  - " + RUN0 + "\n  - " + RUN1 + "\n")

epic = EPIC.read_text(encoding="utf-8")
anchor = "  of an index's active member leaves its parked versions on a cleaned index (sweep A10).\n"
assert epic.count(anchor) == 1
epic = epic.replace(anchor, anchor + "- [ ] Story: " + S10_ID + " - the index\n"
                    "  remove_from_spell_index mints selects its parked version, so a graft activates it (sweep A12).\n", 1)
log_anchor = "  (FACT notes).\n"
assert epic.count(log_anchor) == 1
epic = epic.replace(log_anchor, log_anchor + "- " + NOW + ": sweep A12 filed\n  " + S10_ID + " and widened\n"
                    "  STORY-2026-10-17-staged_version_releases_active_signature and\n"
                    "  STORY-2026-10-17-restore_drops_separated_parked_version (graft side; MEASURE note).\n", 1)
old_view = re.search(r"(?ms)^- State: in_progress \(melder_0\), discovery\. A1-A11 are done.*?\(S6\) are free\.\n",
                     epic).group(0)
new_view = old_view.replace("A1-A11 are done; nine stories filed", "A1-A12 are done; ten stories filed")
new_view = new_view.replace("  STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers (p2, open question) and\n",
                            "  STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers (p2, open question),\n")
new_view = new_view.replace("  " + S9_ID + " (p2).\n", "  " + S9_ID + " (p2) and\n  " + S10_ID + " (p3, open question).\n")
new_view = new_view.replace("(S1-S4, S7-S9)", "(S1-S4, S7-S10)")
new_view = new_view.replace("  STORY-2026-10-17-restore_drops_separated_parked_version (p2, open question),\n",
                            "  STORY-2026-10-17-restore_drops_separated_parked_version (p2, open question; a graft activates\n"
                            "  the version instead, A12),\n")
assert new_view != old_view and S10_ID in new_view and "A12)," in new_view
epic = epic.replace(old_view, new_view, 1)
old_next = ("- Next: tranche 3 (PLAN note): (1) A12 graft of an index with parked versions; (2) NOTICE\n"
            "  melder_1 of S9 and tell the owner (S9; S8's bind precedent).\n")
assert epic.count(old_next) == 1
epic = epic.replace(old_next, "- Next: (1) NOTICE melder_1 (M0-185) of S9, S10 and the S1/S5 widenings; (2) tell the owner of\n"
                    "  S9-S10, S10's question and S8's bind precedent; (3) the owner's answers on the open questions.\n", 1)
epic, count = re.subn(r"(?m)^- Updated: \S+$", "- Updated: " + NOW, epic, count=1)
assert count == 1
check(epic)

art = pathlib.Path("artifact_board.md")
a = art.read_text(encoding="utf-8")
end_art = "<!-- END USER-DEFINED: active_artifacts -->"
assert a.count(end_art) == 1 and S10 not in a
rows = ("| " + S10 + " | " + PROBE + " | defect_reproducer | ready | retain_as_reference | Case G2 (with G1, G3 as "
        "controls) and its runs (runs/probe_graft_parked_members_gil0.txt, _gil1.txt); re-run at the fix. | " + NOW
        + " | HELPFUL |\n"
        "| " + S5 + " | " + PROBE + " | defect_reproducer | ready | retain_as_reference | Case G2 (the graft side: the "
        "separated version comes back active) with its runs (runs/probe_graft_parked_members_gil0.txt, _gil1.txt). | "
        + NOW + " | HELPFUL |\n"
        "| " + S1 + " | " + PROBE + " | defect_reproducer | ready | retain_as_reference | Case G4 (every graft of a "
        "staged index under one signature) with its runs (runs/probe_graft_parked_members_gil0.txt, _gil1.txt). | "
        + NOW + " | HELPFUL |\n")

board = pathlib.Path("attention_board.md")
b = board.read_text(encoding="utf-8")
old_row_next = ("| Sweep A12: read GraftRunner whole for an index whose members include parked versions, "
                "then probe. |")
assert b.count(old_row_next) == 1
b = b.replace(old_row_next, "| NOTICE melder_1 (M0-185) of S9, S10 and the S1/S5 widenings, then tell the owner of "
              "S9-S10 and S10's question. |", 1)
row_re = re.compile(r"^(\| correctness_defects \|.*\| tickets/epics/2026-10-17_correctness_defects_epic\.md \| )\S+( \| REQUIRED \|)$", re.M)
assert len(row_re.findall(b)) == 1
b = row_re.sub(lambda m: m.group(1) + NOW + m.group(2), b, count=1)

if "--dry-run" in sys.argv:
    print(new_view)
    print("dry run OK")
    sys.exit(0)
target = pathlib.Path(S10)
assert not target.exists()
target.write_text(story, encoding="utf-8")
pathlib.Path(S1).write_text(s1, encoding="utf-8")
pathlib.Path(S5).write_text(s5, encoding="utf-8")
EPIC.write_text(epic, encoding="utf-8")
art.write_text(a.replace(end_art, rows + end_art, 1), encoding="utf-8")
board.write_text(b, encoding="utf-8")
print("filed", S10, NOW)
