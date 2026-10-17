"""File sweep A7's story; link the restore and teardown probes to the two signature stories; sync epic and boards.

Everything is rendered and checked in memory first, then written. Run from context_compass/ with <NOW>.
"""
import pathlib
import re
import sys

NOW = sys.argv[1]
EPIC = pathlib.Path("tickets/epics/2026-10-17_correctness_defects_epic.md")
S7 = "tickets/stories/2026-10-17_book_teardown_leaves_parked_versions_uncleaned_story.md"
S7_ID = "STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned"
S6_ID = "STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool"
S1 = "tickets/stories/2026-10-17_staged_version_releases_active_signature_story.md"
S2 = "tickets/stories/2026-10-17_notch_moves_signature_by_incoming_key_only_story.md"
TEMPLATE = pathlib.Path("templates/story_template.md").read_text(encoding="utf-8")
ART = "artifacts/correctness_defects_20261017/"
PROBE = ART + "probes/probe_book_teardown_parked.py"
RUN0 = ART + "runs/probe_book_teardown_parked_gil0.txt"
RUN1 = ART + "runs/probe_book_teardown_parked_gil1.txt"
RPROBE = ART + "probes/probe_restore_staged_structure.py"
RRUN0 = ART + "runs/probe_restore_staged_structure_gil0.txt"
RRUN1 = ART + "runs/probe_restore_staged_structure_gil1.txt"
SB = "src/melder/aether/spellbook/spellbook.py"
SP = "src/melder/aether/spellbook/spell.py"


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


BODY = """# Story: book_teardown_leaves_parked_versions_uncleaned - a Book's teardown retires its parked versions too

## Metadata
- Story ID: """ + S7_ID + """
- Epic: EPIC-2026-10-17-correctness_defects
- Status: ready
- Owner: user
- Agent Name: unassigned
- Agent Role: UNKNOWN
- Priority: p3
- Created: @@NOW@@
- Updated: @@NOW@@

## User Narrative
As an agent who staged and separated versions in a Book and then tore the Book down, I want every version the Book
owned - the parked ones and an index only they hold included - retired with it, so that no version of a dead Book
still reads as live or refuses its own cleanup.

## Value / MRP Alignment
Melder's infrastructure cleans up its own state (owner ruling, src_architecture "Runtime Model"); a Spell and its
SpellIndex are Melder's records of a version. Today the parked versions of a torn-down Book stay uncleaned, and
`Spell.cleanup()` on one raises "Spellbook has already been cleaned." - a record that reads as live and can never be
retired.

## Ticket Contract
- ENTRY_GATE: the owner schedules the story and assigns an agent; melder_1 has released spellbook.py (its rule-2
  hold); an active board row; a component patch for the Book teardown.
- EXECUTION_BOUNDARY: `Spellbook._cleanup_spells` (or the step of `_cleanup_components` that clears
  `_inactive_spells`): the local teardown of every parked version, as the parked branch of `_dispose_spell` runs it
  (`_spellbook_cleanup` set, then `Spell.cleanup()`), and `SpellIndex.cleanup()` of every index only parked versions
  hold, best-effort and logged like the active loop; regression tests; the system documents (the cleanup sequence,
  the Spellbook Core component) with their indexes and the graph; the release note; one notch; the rebuild last.
- DEPENDENCIES: EPIC-2026-10-17-correctness_defects; the probe and its runs (Artifact Links); melder_1's release of
  spellbook.py (TASK-2026-10-16-recheck_contract_consumers_when_provider_changes).
- EXIT_GATE: probe T2 and T3 show French and the minted index cleaned after teardown and `French.cleanup()` returning;
  T1, T4 and T5 unchanged; regression tests pass with the GIL off and on; docs, notch and the rebuild with both
  checks OK.
- FAILURE_ESCALATION: CONFLICT while spellbook.py is held; DECISION_REQUEST if retiring a parked version turns out to
  need more than its local teardown.

## Requirements (Functional)
- Book teardown cleans every version the Book owns, active and parked, and every SpellIndex it owns, including an
  index only parked versions hold.
- A parked version's teardown is local: it is on no resolution map, in no lineage registration and in no frame lookup
  of its own, so only `Spell.cleanup()` (with `_spellbook_cleanup` set) and its index's cleanup run.
- After the teardown, `Spell.cleanup()` on any of the Book's versions returns without raising.

## Requirements (Non-Functional)
- The lock order stays: spell locks are taken under the Book lock, as the active loop takes them; nothing new runs
  user code.

## Scope Boundaries
- In scope: parked versions and parked-only indexes at Book teardown.
- Out of scope: frame claims (the two signature stories), borrowers' copies (the ward's teardown), the record (it
  already evicts the Book's custody in both locations and its index crystals).

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: the defect is proven on 0.2.8252 by a probe with the GIL off and on (Notes).

## Dependencies / Related Work
- STORY-2026-10-17-notch_moves_signature_by_incoming_key_only: the same probe's case T4 (a claim that outlives the
  Book) belongs there.

## Tasks (Implementation Checklist)
- [ ] Task: patch docs for the Book teardown; the owner's approval.
- [ ] Task: the fix with symptom-named regression tests, docs, notch and the rebuild last.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- After its root's teardown, a Book's parked version (on a shared index, or alone in a minted one) reads cleaned,
  its parked-only index reads cleaned, and `cleanup()` on the version returns.
- An active-only Book and a Book with managed versions tear down as today.

## Validation / Test Plan
- Regression tests named for the symptom, e.g. `test_book_teardown_cleans_its_parked_versions` and
  `test_book_teardown_cleans_an_index_only_parked_versions_hold`; GIL off and on; the probe re-run.

## UX / API / Data Notes
- No public signature changes. Visible today: `spell.cleaned` is False for a parked version of a torn-down Book, and
  `spell.cleanup()` raises RuntimeError "Spellbook has already been cleaned.".

## Risks / Mitigations
- Cleaning a parked Spell drops its factory and any compiled artifact; nothing can meld it once its Book is gone, so
  nothing is lost.

@@ANTI@@
## Open Questions
- none.

## Decision Log
- @@NOW@@: filed under EPIC-2026-10-17-correctness_defects from sweep A7 (Notes).

@@ARTIFACT_HEAD@@- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - """ + PROBE + """ (cases T1-T3, T5)
  - """ + RUN0 + """
  - """ + RUN1 + """
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: the probe is re-run at the fix and kept as the defect's reproducer

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - parked versions and parked-only indexes at Book teardown
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
  CLAIM: The defect, read whole and proven on 0.2.8252. `Spellbook._cleanup_spells` walks `_spells` - the active
    version of each index - unregistering, cleaning each Spell and its index; `_cleanup_components` then clears
    `_inactive_spells` without cleaning one of them, and an index only parked versions hold is never reached. The
    parked branch of `_dispose_spell` shows the teardown a parked version needs (`_spellbook_cleanup` set, then
    `Spell.cleanup()`). Afterwards a direct `Spell.cleanup()` routes to the Book (`_direct_removal_route`,
    `cleanup_and_remove_spell`), which raises "Spellbook has already been cleaned.". Probe T2: after the root's
    teardown English is cleaned and French, parked on its index, is not; `French.cleanup()` raises. T3: French
    separated into its own minted index - neither French nor that index is cleaned. T1 (active only) and T5 (the
    pools of an active and a parked managed version, both unregistered) are right. Identical with the GIL off and on.
  EVIDENCE:
  - """ + SB + """:405-556
  - """ + SB + """:557-600
  - """ + SB + """:602-748
  - """ + SB + """:4422-4563
  - """ + SP + """:581-723
  - """ + SP + """:725-763
  - context_compass/""" + PROBE + """:1-231
  - context_compass/""" + RUN0 + """:1-30
  - context_compass/""" + RUN1 + """:1-30
  IMPACT: A dead Book's parked versions read as live and can never be retired.
  NEXT: The owner's scheduling, after melder_1 releases spellbook.py; then patch docs for the Book teardown.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

@@CLOSURE@@@@NOTING@@## Context / Handoff Summary
- Scope: Book teardown retires parked versions and parked-only indexes (Requirements). Defect proven on 0.2.8252
  (Notes); probe and runs in Artifact Links.
- State: ready, unassigned; filed by melder_0 under EPIC-2026-10-17-correctness_defects. The fix sits in
  spellbook.py, which melder_1 holds.
- Next: (1) the owner's scheduling; (2) patch docs; (3) the fix, its tests, docs, notch and the rebuild.

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


s1 = link_probe(S1, "  - " + ART + "runs/probe_signature_claims_gil1.txt\n",
                "  - " + RPROBE + " (case R1: every restore of a staged world; FACT note)\n"
                "  - " + RRUN0 + "\n  - " + RRUN1 + "\n")
s2 = link_probe(S2, "  - " + ART + "runs/probe_signature_claims_gil1.txt\n",
                "  - " + PROBE + " (case T4: the claim outlives the Book; FACT note)\n"
                "  - " + RUN0 + "\n  - " + RUN1 + "\n")

epic = EPIC.read_text(encoding="utf-8")
anchor = "  sends a parked version's object to the active version's pool and strands its count (sweep A6).\n"
assert epic.count(anchor) == 1
epic = epic.replace(anchor, anchor + "- [ ] Story: " + S7_ID + " - Book teardown leaves\n"
                    "  its parked versions and parked-only indexes uncleaned, beyond any cleanup (sweep A7).\n", 1)
log_anchor = "  " + S6_ID + " (MEASURE note).\n"
assert epic.count(log_anchor) == 1
epic = epic.replace(log_anchor, log_anchor + "- " + NOW + ": sweep A7 filed\n  " + S7_ID + " and widened\n"
                    "  STORY-2026-10-17-notch_moves_signature_by_incoming_key_only (MEASURE note).\n", 1)
old_view = re.search(r"(?ms)^- State: in_progress \(melder_0\), discovery\. A1-A5 and A6 are done.*?\(free\)\.\n",
                     epic).group(0)
new_view = ("- State: in_progress (melder_0), discovery. A1-A7 are done; seven stories filed (ready, unassigned):\n"
            "  STORY-2026-10-17-staged_version_releases_active_signature (p1),\n"
            "  STORY-2026-10-17-notch_moves_signature_by_incoming_key_only (p2, open question; its leaked claim\n"
            "  outlives the Book, A7),\n"
            "  STORY-2026-10-17-parked_cleanup_leaves_borrower_copies (p2),\n"
            "  STORY-2026-10-17-minted_index_missing_from_frame_registry (p2),\n"
            "  STORY-2026-10-17-restore_drops_separated_parked_version (p2, open question),\n"
            "  " + S6_ID + " (p2, open question) and\n"
            "  " + S7_ID + " (p3).\n"
            "  Fixes in spellbook.py and conduit.py (S1-S4, S7) wait for melder_1's release; restore_engine.py\n"
            "  (S5) and release_managed_spell.py (S6) are free.\n")
epic = epic.replace(old_view, new_view, 1)
old_next = ("- Next: tranche 2 (PLAN 20:37:46Z): (1) A7 Book teardown with parked versions; (2) A8 the views\n"
            "  of moved and separated versions; (3) tell the owner of the sixth story and its question.\n")
assert epic.count(old_next) == 1
epic = epic.replace(old_next, "- Next: (1) A8 the views of moved and separated versions (MutationResearch residency, Nexus);\n"
                    "  (2) tell the owner of the sixth and seventh stories, the sixth's question and the A7 widening.\n", 1)
epic, count = re.subn(r"(?m)^- Updated: \S+$", "- Updated: " + NOW, epic, count=1)
assert count == 1
check(epic)

art = pathlib.Path("artifact_board.md")
a = art.read_text(encoding="utf-8")
end_art = "<!-- END USER-DEFINED: active_artifacts -->"
assert a.count(end_art) == 1 and S7 not in a
rows = ("| " + S7 + " | " + PROBE + " | defect_reproducer | ready | retain_as_reference | Cases T1-T3, T5 with their runs "
        "(runs/probe_book_teardown_parked_gil0.txt, _gil1.txt); re-run at the fix. | " + NOW + " | HELPFUL |\n"
        "| " + S2 + " | " + PROBE + " | defect_reproducer | ready | retain_as_reference | Case T4 (the claim outlives the "
        "Book) with its runs (runs/probe_book_teardown_parked_gil0.txt, _gil1.txt); re-run at the fix. | " + NOW
        + " | HELPFUL |\n"
        "| " + S1 + " | " + RPROBE + " | defect_reproducer | ready | retain_as_reference | Case R1 (every restore of a "
        "staged world) with its runs (runs/probe_restore_staged_structure_gil0.txt, _gil1.txt); re-run at the fix. | "
        + NOW + " | HELPFUL |\n")

board = pathlib.Path("attention_board.md")
b = board.read_text(encoding="utf-8")
old_row_next = ("| Sweep A7: read Spellbook.cleanup and Book teardown whole for parked versions (their index, pool "
                "registration and record), then probe. |")
assert b.count(old_row_next) == 1
b = b.replace(old_row_next, "| Sweep A8: read MutationResearch residency and Nexus publication whole for moved and "
              "separated versions, then probe. |", 1)
row_re = re.compile(r"^(\| correctness_defects \|.*\| tickets/epics/2026-10-17_correctness_defects_epic\.md \| )\S+( \| REQUIRED \|)$", re.M)
assert len(row_re.findall(b)) == 1
b = row_re.sub(lambda m: m.group(1) + NOW + m.group(2), b, count=1)

target = pathlib.Path(S7)
assert not target.exists()
target.write_text(story, encoding="utf-8")
pathlib.Path(S1).write_text(s1, encoding="utf-8")
pathlib.Path(S2).write_text(s2, encoding="utf-8")
EPIC.write_text(epic, encoding="utf-8")
art.write_text(a.replace(end_art, rows + end_art, 1), encoding="utf-8")
board.write_text(b, encoding="utf-8")
print("filed", S7, NOW)
