"""File sweep A6's story under EPIC-2026-10-17-correctness_defects; sync the epic, the artifact board and the row.

Everything is rendered and checked in memory first, then written. Run from context_compass/ with <NOW>.
"""
import pathlib
import re
import sys

NOW = sys.argv[1]
EPIC = pathlib.Path("tickets/epics/2026-10-17_correctness_defects_epic.md")
S6 = "tickets/stories/2026-10-17_release_routes_parked_version_objects_to_active_pool_story.md"
S6_ID = "STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool"
S5_ID = "STORY-2026-10-17-restore_drops_separated_parked_version"
TEMPLATE = pathlib.Path("templates/story_template.md").read_text(encoding="utf-8")
PROBE = "artifacts/correctness_defects_20261017/probes/probe_managed_release_routing.py"
RUN0 = "artifacts/correctness_defects_20261017/runs/probe_managed_release_routing_gil0.txt"
RUN1 = "artifacts/correctness_defects_20261017/runs/probe_managed_release_routing_gil1.txt"
RMS = "src/melder/aether/conduit/creations/release_managed_spell.py"
MSQ = "src/melder/aether/conduit/creations/managed_spell_quantity.py"
MEPIC = "context_compass/tickets/epics/completed/2026-10-14_managed_spell_quantity_epic.md"


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


BODY = """# Story: release_routes_parked_version_objects_to_active_pool - a release after a notch strands a version's pool

## Metadata
- Story ID: """ + S6_ID + """
- Epic: EPIC-2026-10-17-correctness_defects
- Status: ready
- Owner: user
- Agent Name: unassigned
- Agent Role: UNKNOWN
- Priority: p2
- Created: @@NOW@@
- Updated: @@NOW@@

## User Narrative
As an agent iterating on a managed class through versions of one index - the same class bound again with other
managed options, then notched in - I want an object I leased before the notch to go back to the pool of the
version that leased it when I release it, so that each version's pool keeps a true count and the old version
leases again after a notch back.

## Value / MRP Alignment
A pool's count is structure Melder keeps (owner ruling: structure is the contract). Today a release can leave the
count of a limited_quantity or queue pool naming an object out that the pool will never get back, so that version
refuses every lease after a notch back while nothing is out - state an agent cannot get past without knowing where
the object went.

## Ticket Contract
- ENTRY_GATE: the owner's answer to the open question below; the owner schedules the story and assigns an agent; an
  active board row; a component patch for `ReleaseManagedSpell`'s resolver.
- EXECUTION_BOUNDARY: `ReleaseManagedSpell._resolve_pool` (with `release`, `managed` and `release_all`, which share
  it) and, only if the answer needs one, a record on `ManagedSpellQuantity`; regression tests; the system documents
  (the Managed Spell Pools component, the ReleaseManagedSpell invariant and its failure mode) with their indexes and
  the graph; the release note; one notch; the rebuild last.
- DEPENDENCIES: EPIC-2026-10-17-correctness_defects; the probe and its runs (Artifact Links); the managed epic's
  rulings (owner, 2026-10-14: notch and cleanup_spell destroy nothing; identity is not tracked).
- EXIT_GATE: probe Q2 no longer leaves A's object in B's pool silently (it returns to A, or the release refuses and
  names `spell_id=`, per the answer), and A leases after the notch back; Q1, Q3, Q4, Q5 and Q6 unchanged; regression
  tests pass with the GIL off and on; docs, notch and the rebuild with both checks OK.
- FAILURE_ESCALATION: DECISION_REQUEST for the open question; CONFLICT if the fix needs a file another lane holds.

## Requirements (Functional)
- An object released with no filter, of a class whose live pools belong to two or more versions of one index, never
  lands silently in the pool of a version that did not lease it: it goes back to the version that leased it, or
  the release raises ValueError naming each version's spell_id and the keyword that picks one (the owner's choice).
- A one-pool release keeps its fast path; releases with `spell_id=` or `conduit=`, pools of different indexes or
  roots, and leases from `Conduit.managed_spell_meld` (which carry their pool) keep today's rules.

## Requirements (Non-Functional)
- The warm release (one pool, no filter) keeps its cost: one dict get and the pool's put-back, no lock.
- No identity tracking unless the owner chooses it (his 2026-10-14 ruling: "we don't care about identity").

## Scope Boundaries
- In scope: the cold resolver's choice among pools of one class that belong to versions of one index.
- Out of scope: pools of a disposed version (kept by the 2026-10-14 ruling); releases that name their pool; elastic
  pools' retention.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: the defect is proven on 0.2.8252 by a probe with the GIL off and on (Notes); one open question
  for the owner, because the preference that causes it is an accepted design.

## Dependencies / Related Work
- The managed epic (EPIC-2026-10-14-managed_spell_quantity, completed): its lifecycle table chose "resolver prefers
  the active version" for notch and cleanup_spell.

## Tasks (Implementation Checklist)
- [ ] Task: the owner's answer on the open question.
- [ ] Task: patch docs for the resolver; the owner's approval.
- [ ] Task: the fix with symptom-named regression tests, docs, notch and the rebuild last.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- With A (limited_quantity, limit 1) and B (the same class, limit 2) on one index, an object leased from A, a notch
  to B and a release with no filter: A's count and B's idle count stay true, and after a notch back A leases.
- The cases the probe uses as controls (one version; a release naming its version; a disposed version; a rebind
  under the same spell_id; versions that are two classes) behave as today.

## Validation / Test Plan
- Regression tests named for the symptom, e.g.
  `test_release_after_a_notch_does_not_strand_the_parked_versions_limited_pool`; GIL off and on; the probe re-run.

## UX / API / Data Notes
- Visible today: after a notch back, `managed_spell_meld` or `meld` of the old version raises
  ManagedSpellExhaustedError "Managed spell '<name>' (limited_quantity, limit <N>) has all <N> objects out." while
  `ReleaseManagedSpell().describe(cls)` shows the object idle in the other version's pool. A refusing resolver would
  be a **Breaking change:** for code that releases such objects with no filter.

## Risks / Mitigations
- Routing to the leasing version needs to know which version leased an object, which the ruling declined to track;
  refusing the ambiguous release needs none and matches how two roots or two binding names are handled today.

@@ANTI@@
## Open Questions
- When two versions of one index share a class, should a release with no filter (a) raise ValueError naming each
  version's spell_id, as two roots or two binding names do today (recommended: no identity record, no silent
  count drift), (b) keep preferring the active version and document the drift with its remedy (`spell_id=`), or
  (c) record which version leased each object (the identity tracking ruled out on 2026-10-14)?

## Decision Log
- @@NOW@@: filed under EPIC-2026-10-17-correctness_defects from sweep A6 (Notes).

@@ARTIFACT_HEAD@@- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - """ + PROBE + """ (cases Q1-Q6)
  - """ + RUN0 + """
  - """ + RUN1 + """
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: the probe is re-run at the fix and kept as the defect's reproducer

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - which pool a released managed object goes back to when versions of one index share a class
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
  CLAIM: The defect, read whole and proven on 0.2.8252. `ReleaseManagedSpell.release` takes its fast path only for
    a class with one pool; otherwise `_resolve_pool` keeps the pools matching the filters and, when several remain,
    the one whose version its index selects (`_is_selected_version`). Two versions of one index that bind the same
    class have one pool each, so after a notch every unfiltered release of the class goes to the new active version.
    `put_back` pools any object without counting it, and the count of the pool that leased it - raised by its own
    `reserve()` - never comes down. Probe Q2 (A limited_quantity limit 1, B the same class limit 2): Worker #2
    leased from A, B staged and notched in, `release(obj)`: B count 0 idle 1, A count 1 idle 0; B serves #2 next;
    after a notch back A raises ManagedSpellExhaustedError "has all 1 objects out" with nothing out. Q3 (the same
    with `spell_id=A`) stays right; Q6 (versions that are two classes) routes by class. Identical with the GIL off
    and on (ids masked).
  EVIDENCE:
  - """ + RMS + """:357-399
  - """ + RMS + """:515-580
  - """ + RMS + """:625-645
  - """ + MSQ + """:474-545
  - """ + MSQ + """:548-606
  - """ + MEPIC + """:401-412
  - context_compass/""" + PROBE + """:1-205
  - context_compass/""" + RUN0 + """:1-64
  - context_compass/""" + RUN1 + """:1-64
  IMPACT: A limited_quantity or queue version can refuse every lease after a notch back while nothing is out.
  NEXT: The owner's answer on the open question, then patch docs for the resolver.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

@@CLOSURE@@@@NOTING@@## Context / Handoff Summary
- Scope: a release with no filter among versions of one index that share a class (Requirements). Defect proven on
  0.2.8252 (Notes); probe and runs in Artifact Links.
- State: ready, unassigned; filed by melder_0 under EPIC-2026-10-17-correctness_defects; one open question for the
  owner. The fix sits in release_managed_spell.py, which no other lane holds.
- Next: (1) the owner's answer and scheduling; (2) patch docs; (3) the fix, its tests, docs, notch and the rebuild.

@@TAIL@@"""

story = check(BODY.replace("@@ANTI@@\n", block("## Applicable Anti-Patterns", "## Open Questions"))
              .replace("@@ARTIFACT_HEAD@@", block("## Artifact Links (Optional)", "- ARTIFACTS_REQUIRED:"))
              .replace("@@CLOSURE@@", block("## Closure Confirmation", "## Noting Behavior"))
              .replace("@@NOTING@@", block("## Noting Behavior", "## Context / Handoff Summary"))
              .replace("@@TAIL@@", TEMPLATE[TEMPLATE.index("## Project-Specific Additions"):])
              .replace("@@NOW@@", NOW))

epic = EPIC.read_text(encoding="utf-8")
anchor = "  alone in its own index and still reports complete (sweep A5).\n"
assert epic.count(anchor) == 1
epic = epic.replace(anchor, anchor + "- [ ] Story: " + S6_ID + " - a release with no filter\n"
                    "  sends a parked version's object to the active version's pool and strands its count (sweep A6).\n", 1)
log_anchor = re.search(r"(?m)^  " + re.escape(S5_ID) + r" \(MEASURE note\)\.\n", epic).group(0)
epic = epic.replace(log_anchor, log_anchor + "- " + NOW + ": sweep A6 filed\n  " + S6_ID + " (MEASURE note).\n", 1)
old_view = re.search(r"(?ms)^- State: in_progress \(melder_0\), discovery\. The planned sweep A1-A5 is done.*?"
                     r"\(free\)\.\n", epic).group(0)
new_view = ("- State: in_progress (melder_0), discovery. A1-A5 and A6 are done; six stories filed (ready, unassigned):\n"
            "  STORY-2026-10-17-staged_version_releases_active_signature (p1),\n"
            "  STORY-2026-10-17-notch_moves_signature_by_incoming_key_only (p2, open question),\n"
            "  STORY-2026-10-17-parked_cleanup_leaves_borrower_copies (p2),\n"
            "  STORY-2026-10-17-minted_index_missing_from_frame_registry (p2),\n"
            "  " + S5_ID + " (p2, open question) and\n"
            "  " + S6_ID + " (p2, open question).\n"
            "  The first four fixes sit in spellbook.py and conduit.py, which melder_1 holds; the fifth in\n"
            "  restore_engine.py and the sixth in release_managed_spell.py (free).\n")
epic = epic.replace(old_view, new_view, 1)
old_next = ("- Next: tranche 2 (PLAN 20:37:46Z): (1) A6 managed pools across a version's life; (2) A7 Book teardown\n"
            "  with parked versions; (3) A8 the views of moved and separated versions.\n")
assert epic.count(old_next) == 1
epic = epic.replace(old_next, "- Next: tranche 2 (PLAN 20:37:46Z): (1) A7 Book teardown with parked versions; (2) A8 the views\n"
                    "  of moved and separated versions; (3) tell the owner of the sixth story and its question.\n", 1)
epic, count = re.subn(r"(?m)^- Updated: \S+$", "- Updated: " + NOW, epic, count=1)
assert count == 1
check(epic)

art = pathlib.Path("artifact_board.md")
a = art.read_text(encoding="utf-8")
end_art = "<!-- END USER-DEFINED: active_artifacts -->"
assert a.count(end_art) == 1 and S6 not in a
row = ("| " + S6 + " | " + PROBE + " | defect_reproducer | ready | retain_as_reference | Cases Q1-Q6 with their runs "
       "(runs/probe_managed_release_routing_gil0.txt, _gil1.txt); re-run at the fix. | " + NOW + " | HELPFUL |\n")

board = pathlib.Path("attention_board.md")
b = board.read_text(encoding="utf-8")
old_row_next = ("| Sweep A6: read ReleaseManagedSpell, the managed pool and the Creations pool paths whole, then probe a "
                "managed version across notch, disposal and release. |")
assert b.count(old_row_next) == 1
b = b.replace(old_row_next, "| Sweep A7: read Spellbook.cleanup and Book teardown whole for parked versions (their index, pool "
              "registration and record), then probe. |", 1)
row_re = re.compile(r"^(\| correctness_defects \|.*\| tickets/epics/2026-10-17_correctness_defects_epic\.md \| )\S+( \| REQUIRED \|)$", re.M)
assert len(row_re.findall(b)) == 1
b = row_re.sub(lambda m: m.group(1) + NOW + m.group(2), b, count=1)

target = pathlib.Path(S6)
assert not target.exists()
target.write_text(story, encoding="utf-8")
EPIC.write_text(epic, encoding="utf-8")
art.write_text(a.replace(end_art, row + end_art, 1), encoding="utf-8")
board.write_text(b, encoding="utf-8")
print("filed", S6, NOW)
