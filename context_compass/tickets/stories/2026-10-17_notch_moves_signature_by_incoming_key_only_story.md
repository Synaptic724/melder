# Story: notch_moves_signature_by_incoming_key_only - a notch moves the signature with the active version

## Metadata
- Story ID: STORY-2026-10-17-notch_moves_signature_by_incoming_key_only
- Epic: EPIC-2026-10-17-correctness_defects
- Status: ready
- Owner: user
- Agent Name: unassigned
- Agent Role: UNKNOWN
- Priority: p2
- Created: 2026-10-17T20:23:51Z
- Updated: 2026-10-17T21:55:46Z

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
- ENTRY_GATE: the owner schedules the story and assigns an agent (the open question was answered on 2026-10-17);
  spellbook.py's holder releases it or carries the fix; an active board row; a component patch for the seam.
- EXECUTION_BOUNDARY: step 4 of `Spellbook._apply_notch` (the signature repoint and the refusal of a key another
  active spell holds); regression tests; system docs with their indexes and the graph; the release note; one notch;
  the rebuild last. Staging stays open to any key (owner, 2026-10-17).
- DEPENDENCIES: EPIC-2026-10-17-correctness_defects; STORY-2026-10-17-staged_version_releases_active_signature (the same
  claims; staging disturbs them until it lands, so this story's tests heal or avoid that first);
  TASK-2026-10-16-notch_seam_checks_incoming_before_parking (the same seam: a check moved ahead of the park); the
  probe and its runs.
- EXIT_GATE: the probe's C5 and C7 show the claims following the active version, or the notch refused before
  anything moved; regression tests pass with the GIL off and on; docs, notch and the rebuild with both checks OK.
- FAILURE_ESCALATION: CONFLICT if the notch-seam backlog task lands first with another order of checks, or while
  spellbook.py is held.

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
- In scope: the notch's signature handling. One index may hold versions under different signatures (owner,
  2026-10-17), so staging and index moves keep their admission.
- Out of scope: `_destroy_spell_index` (STORY-2026-10-17-staged_version_releases_active_signature); spell_id lookups and
  contracts (melder_1's lane).

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: the defect is proven on 0.2.8251 by a probe in fresh worlds, GIL off and on (Notes); one open
  question for the owner.

## Dependencies / Related Work
- STORY-2026-10-17-staged_version_releases_active_signature.
- TASK-2026-10-16-notch_seam_checks_incoming_before_parking (backlog).

## Tasks (Implementation Checklist)
- [x] Task: the owner's answer on one signature per index (2026-10-17: one index may hold several; DECISION note).
- [ ] Task: patch docs for the seam; the owner's approval.
- [ ] Task: the fix with symptom-named regression tests, docs, notch and the rebuild last.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- After a notch from a version keyed K1 to one keyed K2, K1 is free in the frame (a bind of it succeeds) and K2
  names the incoming version; a notch back restores K1 and frees K2.
- A notch that would give the incoming version a key another active spell holds raises before anything moves, and
  both indexes stay as they were.
- Staging or adding a version keyed differently from its index's other versions stays allowed (owner, 2026-10-17).

## Validation / Test Plan
- Regression tests named for the symptom, e.g. `test_notch_across_keys_frees_the_outgoing_signature`,
  `test_notch_refuses_a_signature_another_active_spell_holds`; GIL off and on; the probe re-run (C5, C7).

## UX / API / Data Notes
- Visible today: after a notch across keys, a bind of the old signature raises "Binding signature already active in
  this frame ... held by spell_id='<the parked version>'"; after C7's notch, `meld(spellframe=..., binding_name=...)`
  raises SpellbookValidationError [DUPLICATE_SPELL_NAME]. A refused notch is a new error for C7's call sequence.

## Risks / Mitigations
- The notch-seam backlog task also moves a check ahead of the park: whichever lands second rebases on the first.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- May one SpellIndex hold versions under different binding signatures? If yes, the notch moves the claim (above); if
  no, staging refuses a differently keyed version and C5 cannot occur. C7 needs the notch refusal either way.
  Answered (owner, 2026-10-17T21:55:46Z): yes - "1 spellindex can hold versions with different binding
  signatures, this is why revalidation happens" (DECISION note).

## Decision Log
- 2026-10-17T20:23:51Z: filed under EPIC-2026-10-17-correctness_defects from sweep A1 (Notes).
- 2026-10-17T21:55:46Z: the owner answered the open question - one index may hold versions under different
  signatures, so the notch moves the claim (DECISION note).

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/correctness_defects_20261017/probes/probe_signature_claims.py (cases C5, C7)
  - artifacts/correctness_defects_20261017/runs/probe_signature_claims_gil0.txt
  - artifacts/correctness_defects_20261017/runs/probe_signature_claims_gil1.txt
  - artifacts/correctness_defects_20261017/probes/probe_book_teardown_parked.py (case T4: the claim outlives the Book; FACT note)
  - artifacts/correctness_defects_20261017/runs/probe_book_teardown_parked_gil0.txt
  - artifacts/correctness_defects_20261017/runs/probe_book_teardown_parked_gil1.txt
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
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose and evidence (the probe); filed 2026-10-17T20:23:51Z.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-17T20:23:51Z
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
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_signature_claims.py:1-278
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_signature_claims_gil0.txt:1-91
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_signature_claims_gil1.txt:1-91
  IMPACT: A notch can leave a signature claimed by a parked version (stuck) or give an active spell's signature to a
    second one (wrong), against the frame's one-active-spell-per-signature rule.
  NEXT: The owner's answer on one signature per index, then patch docs for the notch's step 4.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-17T21:12:09Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The leaked claim outlives the Book (sweep A7, probe T4). After a notch from English ('greeter') to Spanish
    ('spanish') the parked English still holds ('greeter', 'greeter') frame-wide; the park popped English's key from
    the Book's `_lookup_spells` (`_deactivate_owned_spell`), and Book teardown releases only the keys left in that
    map, so tearing the Book down through its root leaves the claim held by a spell of a dead Book: every later bind
    of the signature in that frame is refused ("Binding signature already active in this frame ... held by
    spell_id=<English>") until the frame itself ends. Identical with the GIL off and on.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:1500-1561
  - src/melder/aether/spellbook/spellbook.py:405-556
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_book_teardown_parked.py:1-231
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_book_teardown_parked_gil0.txt:20-24
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_book_teardown_parked_gil1.txt:20-24
  IMPACT: The stuck claim is not bounded by the Book's life; the regression tests should also tear the Book down and
    bind the old signature again.
  NEXT: The owner's answer on this story's open question.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-17T21:55:46Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The open question is answered (owner, chat 2026-10-17): "Yes 1 spellindex can hold versions with different
    binding signatures, this is why revalidation happens". The story takes its first branch: after a notch the frame
    claims the incoming version's key for it and releases the outgoing version's claim by spell_id when the keys
    differ (C5); a notch whose incoming key another active spell of the frame holds is refused before anything is
    parked (C7); staging or adding a differently keyed version stays allowed. The one-signature-per-index branch is
    out of scope.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-17_notch_moves_signature_by_incoming_key_only_story.md:40-46
  - src/melder/aether/spellbook/spellbook.py:3906-4061
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_signature_claims_gil0.txt:1-91
  IMPACT: The ENTRY_GATE's question is met; the fix is the notch's step 4 alone (no staging admission change).
  NEXT: The owner's scheduling, after melder_1 releases spellbook.py; then patch docs for `_apply_notch` step 4.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

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
- Scope: a notch hands the binding signature to the incoming version, frees the outgoing one, and refuses a key
  another active spell holds (Requirements). Defect proven on 0.2.8251 (Notes); probe and runs in Artifact Links.
- State: ready, unassigned; filed by melder_0 under EPIC-2026-10-17-correctness_defects; the owner answered its
  question (one index may hold several signatures; the notch moves the claim). The fix sits in spellbook.py, which
  melder_1 holds until its rule-2 closure.
- Next: (1) the owner's scheduling; (2) patch docs for `_apply_notch` step 4; (3) the fix, its tests, docs, notch
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
