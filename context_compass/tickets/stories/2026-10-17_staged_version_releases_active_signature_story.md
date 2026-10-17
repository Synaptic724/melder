# Story: staged_version_releases_active_signature - staging, moving or disposing a version keeps other signatures

## Metadata
- Story ID: STORY-2026-10-17-staged_version_releases_active_signature
- Epic: EPIC-2026-10-17-correctness_defects
- Status: ready
- Owner: user
- Agent Name: unassigned
- Agent Role: UNKNOWN
- Priority: p1
- Created: 2026-10-17T20:23:51Z
- Updated: 2026-10-17T20:35:54Z

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
  (STORY-2026-10-17-notch_moves_signature_by_incoming_key_only); spell_id lookups and contracts (melder_1's lane).

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: the defect is proven on 0.2.8251 by a probe in fresh worlds, GIL off and on (Notes).

## Dependencies / Related Work
- STORY-2026-10-17-notch_moves_signature_by_incoming_key_only (the same frame claims; the notch's seam).
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

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Should staging also refuse a version whose key another Book's active spell holds (C6), or only stop releasing that
  claim? The owner's call; the minimal fix is the latter.

## Decision Log
- 2026-10-17T20:23:51Z: filed under EPIC-2026-10-17-correctness_defects from sweep A1 (Notes).

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/correctness_defects_20261017/probes/probe_signature_claims.py (cases C1-C4, C6)
  - artifacts/correctness_defects_20261017/runs/probe_signature_claims_gil0.txt
  - artifacts/correctness_defects_20261017/runs/probe_signature_claims_gil1.txt
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
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose and evidence (the probe); filed 2026-10-17T20:23:51Z.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-17T20:23:51Z
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
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_signature_claims.py:1-278
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_signature_claims_gil0.txt:1-91
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_signature_claims_gil1.txt:1-91
  IMPACT: The structure is wrong from a staging until the next notch: the signature an active version holds is free
    for any bind in the frame, and the Book cannot address that version by name.
  NEXT: The owner schedules the story; patch docs for `_destroy_spell_index` first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-17T20:35:54Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The defect hits restores too. The restore engine replays every staged member through
    `Conduit.bind_inactive` onto its live anchor, so a recorded world with a staged version under its active
    sibling's signature comes back "complete" with the active version's frame claim released (probe R1, sweep A5 of
    the epic; identical with the GIL off and on).
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2201-2269
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_restore_staged_structure.py:1-160
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_restore_staged_structure_gil0.txt:1-4
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_restore_staged_structure_gil1.txt:1-4
  IMPACT: The acceptance criteria hold for a restored world too; the fix's tests should include one restore.
  NEXT: The owner schedules the story.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.

## Context / Handoff Summary
- Scope: staging, moving or disposing a parked version leaves every other spell's binding signature and Book route
  in place (Requirements). Defect proven on 0.2.8251 (Notes); probe and runs in Artifact Links.
- State: ready, unassigned; filed by melder_0 under EPIC-2026-10-17-correctness_defects. The fix sits in
  spellbook.py, which melder_1 holds until its rule-2 closure.
- Next: (1) the owner schedules it; (2) patch docs for `_destroy_spell_index`; (3) the fix, its tests, docs, notch
  and the rebuild.

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
