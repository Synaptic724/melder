"""File sweep A1's two stories under EPIC-2026-10-17-correctness_defects and sync the epic and the artifact board.

Run from context_compass/:  python3 artifacts/correctness_defects_20261017/scripts/file_stories_a1.py <NOW>
"""
import pathlib
import re
import sys

NOW = sys.argv[1]
EPIC = pathlib.Path("tickets/epics/2026-10-17_correctness_defects_epic.md")
S1 = "tickets/stories/2026-10-17_staged_version_releases_active_signature_story.md"
S2 = "tickets/stories/2026-10-17_notch_moves_signature_by_incoming_key_only_story.md"
S1_ID = "STORY-2026-10-17-staged_version_releases_active_signature"
S2_ID = "STORY-2026-10-17-notch_moves_signature_by_incoming_key_only"
TEMPLATE = pathlib.Path("templates/story_template.md").read_text(encoding="utf-8")
PROBE = "artifacts/correctness_defects_20261017/probes/probe_signature_claims.py"
RUN0 = "artifacts/correctness_defects_20261017/runs/probe_signature_claims_gil0.txt"
RUN1 = "artifacts/correctness_defects_20261017/runs/probe_signature_claims_gil1.txt"


def block(start: str, end: str) -> str:
    """Verbatim template text from heading `start` up to (not including) `end`."""
    i = TEMPLATE.index(start)
    return TEMPLATE[i:TEMPLATE.index(end, i)]


def render(body: str) -> str:
    """Fill the template blocks and NOW; refuse long lines that hold no path."""
    text = (body.replace("@@ANTI@@\n", block("## Applicable Anti-Patterns", "## Open Questions"))
            .replace("@@ARTIFACT_HEAD@@", block("## Artifact Links (Optional)", "- ARTIFACTS_REQUIRED:"))
            .replace("@@CLOSURE@@", block("## Closure Confirmation", "## Noting Behavior"))
            .replace("@@NOTING@@", block("## Noting Behavior", "## Context / Handoff Summary"))
            .replace("@@TAIL@@", TEMPLATE[TEMPLATE.index("## Project-Specific Additions"):])
            .replace("@@NOW@@", NOW))
    assert "@@" not in text
    long = [line for line in text.splitlines() if len(line) > 120 and "/" not in line]
    assert not long, long
    return text


STORY1 = """# Story: staged_version_releases_active_signature - staging, moving or disposing a version keeps other signatures

## Metadata
- Story ID: """ + S1_ID + """
- Epic: EPIC-2026-10-17-correctness_defects
- Status: ready
- Owner: user
- Agent Name: unassigned
- Agent Role: UNKNOWN
- Priority: p1
- Created: @@NOW@@
- Updated: @@NOW@@

## User Narrative
As an agent iterating on a spell in a live world, I want staging a new version with `bind_inactive`, moving a parked
version between indexes and disposing a parked version to leave the active version's binding signature where it is,
so that the version I am still running stays addressable by its name and no other bind can take its signature.

## Value / MRP Alignment
The frame's one-active-spell-per-signature claim (`LookupContainer`) and a Book's address map (`_lookup_spells`) are
binding structure. Staging versions and notching between them is the loop the owner describes Melder for; today the
first step of that loop drops the claim of the version still serving, so the structure is wrong until a notch
happens to repair it.

## Ticket Contract
- ENTRY_GATE: the owner schedules the story and assigns an agent; spellbook.py's holder releases it (melder_1 until
  its rule-2 closure) or carries the fix; an active board row; a component patch for the seam (it changes how a
  structural invariant is enforced).
- EXECUTION_BOUNDARY: `Spellbook._destroy_spell_index` (what it releases and pops) and, if the patch says so, the
  arguments its two callers pass (`_apply_add_to_index`, `_dispose_spell`); regression tests; system docs with their
  indexes and the graph; the release note; one notch; the rebuild last.
- DEPENDENCIES: EPIC-2026-10-17-correctness_defects; the probe and its runs (Artifact Links).
- EXIT_GATE: the probe's C1, C2, C3, C4 and C6 show every other spell's claim and route unchanged; the regression
  tests pass with the GIL off and on; docs, notch and the rebuild with both checks OK.
- FAILURE_ESCALATION: DECISION_REQUEST if the fix should make staging refuse a version keyed like another active
  spell (C6) instead of only not releasing it; CONFLICT if the holder of spellbook.py is mid-change in the seam.

## Requirements (Functional)
- Destroying an emptied index releases a frame claim and drops a Book route only when they belong to that index: the
  claim held by a spell of that index (released by spell_id, as `cleanup_and_remove_spell` already does), the route
  `_lookup_spells[key]` only when it points at that index. Every index `_destroy_spell_index` is handed today holds
  parked members only, so it holds no claim and no route.
- `bind_inactive` (before and after conjure), `add_to_spell_index` emptying its source, and `cleanup_spell` of a
  parked version emptying its index change no other spell's claim or route, in this Book or another Book of the
  frame.

## Requirements (Non-Functional)
- No new lock or lock-order edge; the warm meld path untouched.

## Scope Boundaries
- In scope: the claim and route handling of `_destroy_spell_index` and its two callers.
- Out of scope: the notch's own signature handling
  (""" + S2_ID + """); spell_id lookups and contracts (melder_1's lane).

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: the defect is proven on 0.2.8251 by a probe in fresh worlds, GIL off and on (Notes).

## Dependencies / Related Work
- """ + S2_ID + """ (the same frame claims; the notch's seam).
- `Spellbook.cleanup_and_remove_spell` already releases by spell_id, for this very reason (spellbook.py:716-729).

## Tasks (Implementation Checklist)
- [ ] Task: patch docs for the seam; the owner's approval.
- [ ] Task: the fix with symptom-named regression tests, docs, notch and the rebuild last.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- After `bind_inactive` of a version keyed like the active version, before or after conjure: the frame claim still
  names the active version; `meld(spellframe=..., binding_name=...)` returns it; `find_spell_index` returns its
  index; another bind of the signature anywhere in the frame is refused.
- The same after `remove_from_spell_index` then `add_to_spell_index` back, and after `cleanup_spell` of a parked
  version alone in its index.
- Staging in one Book a version keyed like another Book's active spell leaves that spell's claim in place.

## Validation / Test Plan
- Regression tests named for the symptom, e.g. `test_bind_inactive_keeps_the_active_versions_binding_signature`,
  `test_index_move_back_keeps_the_active_versions_binding_signature`,
  `test_cleanup_of_a_lone_parked_version_keeps_the_siblings_binding_signature`,
  `test_staging_does_not_release_another_books_binding_signature`; GIL off and on; the probe re-run.

## UX / API / Data Notes
- No public signature changes. Visible today: `find_spell_index` raises "Spell not found in the spellbook." and a
  meld by address raises KeyError "[MELD] No spell found ..." for a spell that is active, and a second spell can
  bind a signature an active spell holds.

## Risks / Mitigations
- A caller that relies on the release: none found - both callers hand the seam an index of parked members only.

@@ANTI@@
## Open Questions
- Should staging also refuse a version whose key another Book's active spell holds (C6), or only stop releasing that
  claim? The owner's call; the minimal fix is the latter.

## Decision Log
- @@NOW@@: filed under EPIC-2026-10-17-correctness_defects from sweep A1 (Notes).

@@ARTIFACT_HEAD@@- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - """ + PROBE + """ (cases C1-C4, C6)
  - """ + RUN0 + """
  - """ + RUN1 + """
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: the probe is re-run at the fix and kept as the defect's reproducer

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - binding-signature claims and Book address routes around parked versions
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
  CLAIM: The defect, read whole and proven on 0.2.8251. `_destroy_spell_index` pops the Book's
    `_lookup_spells[binding_key]` and calls the frame's `release_lookup(binding_key)` - both by key, whoever holds it -
    with the key of a parked version. Its callers hand it an index of parked members only: `_apply_add_to_index` when
    the moved version emptied its source - which `bind_inactive` does every time, folding the new version off the
    throwaway index Bind minted - and `_dispose_spell` when a parked version was its index's last member. A parked
    version shares its key with its active sibling, so the release lands on the sibling, or on any active spell of
    the frame keyed the same. Probe: after `bind_inactive` the frame claim is gone, `find_spell_index` raises, a meld
    by address raises KeyError when no meld warmed it before, and another Book binds the signature while the version
    still serves (C1, C2); the same after an index move back (C3), a lone parked `cleanup_spell` (C4) and across
    Books (C6). Identical with the GIL off and on.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:4192-4237
  - src/melder/aether/spellbook/spellbook.py:4096-4190
  - src/melder/aether/spellbook/spellbook.py:5243-5498
  - src/melder/aether/spellbook/spellbook.py:4422-4563
  - src/melder/aether/spellbook/spellbook.py:716-729
  - src/melder/aether/aetheric_frame/lookup_container.py:5-274
  - context_compass/""" + PROBE + """:1-278
  - context_compass/""" + RUN0 + """:1-91
  - context_compass/""" + RUN1 + """:1-91
  IMPACT: The structure is wrong from a staging until the next notch: the signature an active version holds is free
    for any bind in the frame, and the Book cannot address that version by name.
  NEXT: The owner schedules the story; patch docs for `_destroy_spell_index` first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

@@CLOSURE@@@@NOTING@@## Context / Handoff Summary
- Scope: staging, moving or disposing a parked version leaves every other spell's binding signature and Book route
  in place (Requirements). Defect proven on 0.2.8251 (Notes); probe and runs in Artifact Links.
- State: ready, unassigned; filed by melder_0 under EPIC-2026-10-17-correctness_defects. The fix sits in
  spellbook.py, which melder_1 holds until its rule-2 closure.
- Next: (1) the owner schedules it; (2) patch docs for `_destroy_spell_index`; (3) the fix, its tests, docs, notch
  and the rebuild.

@@TAIL@@"""

STORY2 = """# Story: notch_moves_signature_by_incoming_key_only - a notch moves the signature with the active version

## Metadata
- Story ID: """ + S2_ID + """
- Epic: EPIC-2026-10-17-correctness_defects
- Status: ready
- Owner: user
- Agent Name: unassigned
- Agent Role: UNKNOWN
- Priority: p2
- Created: @@NOW@@
- Updated: @@NOW@@

## User Narrative
As an agent notching between versions, I want the frame's signature claims to follow the active version - the
outgoing version's claim released, the incoming version's key taken only when no other active spell holds it - so
that no parked spell keeps a signature and no two active spells share one address.

## Value / MRP Alignment
A notch only moves which version is active (owner ruling); the binding signature belongs with the active version.
Today a notch across keys leaves a parked version holding a signature nobody can bind again (stuck), and a notch
inside an index `remove_from_spell_index` minted puts a second active spell at an address an active spell already
holds (wrong: the next meld by address is refused).

## Ticket Contract
- ENTRY_GATE: the owner's answer to the open question below; the owner schedules the story and assigns an agent;
  spellbook.py's holder releases it or carries the fix; an active board row; a component patch for the seam.
- EXECUTION_BOUNDARY: step 4 of `Spellbook._apply_notch` (the signature repoint) and, if the owner rules that one
  index holds one signature, the admission checks of `bind_inactive` and `add_to_spell_index`; regression tests;
  system docs with their indexes and the graph; the release note; one notch; the rebuild last.
- DEPENDENCIES: EPIC-2026-10-17-correctness_defects; """ + S1_ID + """ (the same
  claims; staging disturbs them until it lands, so this story's tests heal or avoid that first);
  TASK-2026-10-16-notch_seam_checks_incoming_before_parking (the same seam: a check moved ahead of the park); the
  probe and its runs.
- EXIT_GATE: the probe's C5 and C7 show the claims following the active version, or the notch refused before
  anything moved; regression tests pass with the GIL off and on; docs, notch and the rebuild with both checks OK.
- FAILURE_ESCALATION: DECISION_REQUEST for the open question; CONFLICT if the notch-seam backlog task lands first
  with another order of checks.

## Requirements (Functional)
- After a notch the frame claims the incoming version's key for it, and the outgoing version's claim is released
  when its key differs (released by spell_id, so a sibling's claim is never touched).
- A notch whose incoming key is held by another active spell of the frame - not the outgoing version - is refused
  before anything is parked, as `bind` refuses ("Binding signature already active in this frame ...").
- The Book's address map follows: the outgoing key no longer routes to the index, the incoming key does, and it
  never overwrites another index's route.

## Requirements (Non-Functional)
- No new lock or lock-order edge (the frame's lookup container lock is a leaf); the refusal runs inside the held
  notch window before the park, so a refused notch changes nothing.

## Scope Boundaries
- In scope: the notch's signature handling; the staging admission only if the owner rules one signature per index.
- Out of scope: `_destroy_spell_index` (""" + S1_ID + """); spell_id lookups and
  contracts (melder_1's lane).

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: the defect is proven on 0.2.8251 by a probe in fresh worlds, GIL off and on (Notes); one open
  question for the owner.

## Dependencies / Related Work
- """ + S1_ID + """.
- TASK-2026-10-16-notch_seam_checks_incoming_before_parking (backlog).

## Tasks (Implementation Checklist)
- [ ] Task: the owner's answer on one signature per index.
- [ ] Task: patch docs for the seam; the owner's approval.
- [ ] Task: the fix with symptom-named regression tests, docs, notch and the rebuild last.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- After a notch from a version keyed K1 to one keyed K2, K1 is free in the frame (a bind of it succeeds) and K2
  names the incoming version; a notch back restores K1 and frees K2.
- A notch that would give the incoming version a key another active spell holds raises before anything moves, and
  both indexes stay as they were.
- Or, if the owner rules one signature per index: staging or adding a version keyed differently from its index's
  signature is refused, so C5's world cannot be built; C7's refusal holds either way.

## Validation / Test Plan
- Regression tests named for the symptom, e.g. `test_notch_across_keys_frees_the_outgoing_signature`,
  `test_notch_refuses_a_signature_another_active_spell_holds`; GIL off and on; the probe re-run (C5, C7).

## UX / API / Data Notes
- Visible today: after a notch across keys, a bind of the old signature raises "Binding signature already active in
  this frame ... held by spell_id='<the parked version>'"; after C7's notch, `meld(spellframe=..., binding_name=...)`
  raises SpellbookValidationError [DUPLICATE_SPELL_NAME]. A refused notch is a new error for C7's call sequence.

## Risks / Mitigations
- The notch-seam backlog task also moves a check ahead of the park: whichever lands second rebases on the first.

@@ANTI@@
## Open Questions
- May one SpellIndex hold versions under different binding signatures? If yes, the notch moves the claim (above); if
  no, staging refuses a differently keyed version and C5 cannot occur. C7 needs the notch refusal either way.

## Decision Log
- @@NOW@@: filed under EPIC-2026-10-17-correctness_defects from sweep A1 (Notes).

@@ARTIFACT_HEAD@@- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - """ + PROBE + """ (cases C5, C7)
  - """ + RUN0 + """
  - """ + RUN1 + """
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: the probe is re-run at the fix and kept as the defect's reproducer

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - binding-signature claims across a notch
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
  CLAIM: The defect, read whole and proven on 0.2.8251. Step 4 of `_apply_notch` calls the frame's
    `update_lookup(spell._key, new_id)`: `LookupContainer.update` sets the incoming version's key unconditionally - no
    uniqueness check, it only drops that key's previous holder from the reverse map - and the outgoing version's own
    key is never released: `_deactivate_owned_spell` leaves the frame lookup to its caller, and the caller repoints
    the incoming key only. C5: after a notch from English ('greeter') to a version under ('greeter', 'spanish') the
    parked English still holds ('greeter', 'greeter'), so a new bind of that signature is refused naming English. C7:
    French, moved by `remove_from_spell_index` into the index it mints and notched active there, takes the signature
    English still holds active in its own index; the Book then has two active spells at one address, and the next
    `meld(spellframe=Greeter, binding_name='greeter')` raises SpellbookValidationError [DUPLICATE_SPELL_NAME].
    Identical with the GIL off and on.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:3906-4061
  - src/melder/aether/spellbook/spellbook.py:1500-1621
  - src/melder/aether/aetheric_frame/lookup_container.py:5-274
  - src/melder/aether/spellbook/spellbook.py:4271-4356
  - context_compass/""" + PROBE + """:1-278
  - context_compass/""" + RUN0 + """:1-91
  - context_compass/""" + RUN1 + """:1-91
  IMPACT: A notch can leave a signature claimed by a parked version (stuck) or give an active spell's signature to a
    second one (wrong), against the frame's one-active-spell-per-signature rule.
  NEXT: The owner's answer on one signature per index, then patch docs for the notch's step 4.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

@@CLOSURE@@@@NOTING@@## Context / Handoff Summary
- Scope: a notch hands the binding signature to the incoming version, frees the outgoing one, and refuses a key
  another active spell holds (Requirements). Defect proven on 0.2.8251 (Notes); probe and runs in Artifact Links.
- State: ready, unassigned; filed by melder_0 under EPIC-2026-10-17-correctness_defects; one open question for the
  owner (one signature per index?). The fix sits in spellbook.py, which melder_1 holds until its rule-2 closure.
- Next: (1) the owner's answer and scheduling; (2) patch docs for `_apply_notch` step 4; (3) the fix, its tests,
  docs, notch and the rebuild.

@@TAIL@@"""

for path, body in ((S1, STORY1), (S2, STORY2)):
    target = pathlib.Path(path)
    assert not target.exists(), path
    target.write_text(render(body), encoding="utf-8")

epic = EPIC.read_text(encoding="utf-8")
old_stories = "## Stories (Required to Complete)\n- none yet; one per confirmed defect.\n"
assert epic.count(old_stories) == 1
epic = epic.replace(old_stories, "## Stories (Required to Complete)\n- [ ] Story: " + S1_ID + " - staging, moving or\n"
                    "  disposing a parked version drops the binding signature of the active spell keyed like it (sweep A1).\n"
                    "- [ ] Story: " + S2_ID + " - a notch moves signatures by the\n"
                    "  incoming key alone: a parked version keeps its claim, or an active spell's key is taken (sweep A1).\n", 1)
old_log = "- " + re.search(r"(?m)^- (\S+): opened on the owner's direction \(DECISION note\)\.$", epic).group(1)
log_line = re.search(r"(?m)^- \S+: opened on the owner's direction \(DECISION note\)\.\n", epic).group(0)
epic = epic.replace(log_line, log_line + "- " + NOW + ": sweep A1 filed " + S1_ID + " and\n  " + S2_ID
                    + " (MEASURE note).\n", 1)
start = epic.index("## Context / Handoff Summary\n") + len("## Context / Handoff Summary\n")
end = epic.index("\n## Project-Specific Additions", start)
view = ("- Scope: correctness defects - structure Melder records wrong or leaves stuck - by the owner's rulings (DECISION\n"
        "  note); read-only; one story per confirmed defect; melder_1's lane excluded.\n"
        "- State: in_progress (melder_0), discovery. Sweep A1 done: two defects filed, both binding-signature claims -\n"
        "  " + S1_ID + " (p1) and " + S2_ID + "\n  (p2, one open question). Their fixes sit in spellbook.py (melder_1's until its rule-2 closure).\n"
        "- Next: (1) sweep A2, cleanup_spell of a parked version (PLAN note); (2) A3-A5 in order; (3) tell the owner\n"
        "  what was filed.\n")
epic = epic[:start] + view + epic[end:]
long = [line for line in epic.splitlines() if len(line) > 120 and "/" not in line]
assert not long, long
EPIC.write_text(epic, encoding="utf-8")

art = pathlib.Path("artifact_board.md")
a = art.read_text(encoding="utf-8")
end_art = "<!-- END USER-DEFINED: active_artifacts -->"
rows = ""
for path, cases in ((S1, "C1-C4, C6"), (S2, "C5, C7")):
    rows += ("| " + path + " | " + PROBE + " | defect_reproducer | ready | retain_as_reference | Cases " + cases
             + " with their runs (runs/probe_signature_claims_gil0.txt, _gil1.txt); re-run at the fix. | " + NOW
             + " | HELPFUL |\n")
assert a.count(end_art) == 1 and S1 not in a and S2 not in a
art.write_text(a.replace(end_art, rows + end_art, 1), encoding="utf-8")
print("filed", S1, S2)
