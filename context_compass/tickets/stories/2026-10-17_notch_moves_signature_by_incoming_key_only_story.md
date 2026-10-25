# Story: notch_moves_signature_by_incoming_key_only - a notch moves the signature with the active version

## Metadata
- Story ID: STORY-2026-10-17-notch_moves_signature_by_incoming_key_only
- Epic: EPIC-2026-10-17-correctness_defects
- Status: in_progress
- Owner: user
- Agent Name: melder_1
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-10-17T20:23:51Z
- Updated: 2026-10-25T01:25:13Z

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
- from_state: ready
- to_state: in_progress
- transition_reason: the owner's direction (chat 2026-10-24): the index is the representation of the binding
  signature, validated on the way in, and the overlapping signature defenses are researched first (DECISION note).
  Before that, draft -> ready: the defect proven on 0.2.8251 (Notes), with one open question for the owner.

## Dependencies / Related Work
- STORY-2026-10-17-staged_version_releases_active_signature.
- TASK-2026-10-16-notch_seam_checks_incoming_before_parking (backlog).

## Tasks (Implementation Checklist)
- [x] Task: the owner's answer on one signature per index (2026-10-17: one index may hold several; DECISION note).
- [x] Task: research the binding-signature defenses for the index-owns-the-signature model (owner, 2026-10-24);
  the findings in Notes, for the owner's review.
- [ ] Task: the owner's three calls (DECISION_REQUEST note of 2026-10-25T01:25:13Z).
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
- 2026-10-25T00:39:06Z: superseded by the owner's direction (chat 2026-10-24): the index is the representation of
  the binding signature, validated on the way in; research the overlapping defenses first; melder_1 assigned
  (DECISION note).

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
  - artifacts/correctness_defects_20261017/probes/diag_notch_takes_other_books_address.py (the cross-Book case)
  - artifacts/correctness_defects_20261017/runs/diag_notch_takes_other_books_address_0_2_8267.txt
  - artifacts/correctness_defects_20261017/probes/probe_how_melds_follow_a_notch.py (what follows a notch)
  - artifacts/correctness_defects_20261017/runs/probe_how_melds_follow_a_notch_0_2_8267.txt
  - artifacts/correctness_defects_20261017/scripts/option_a_experiment/ (option (A)'s scratch patches and runners)
  - artifacts/correctness_defects_20261017/runs/option_a_blast_radius_0_2_8267.txt
  - artifacts/correctness_defects_20261017/probes/probe_mixed_record_under_option_a.py (a record of a mixed index)
  - artifacts/correctness_defects_20261017/runs/probe_mixed_record_under_option_a_0_2_8267.txt
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

- DATETIME: 2026-10-24T23:31:58Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Rechecked on 0.2.8267 through public calls, the GIL off and on. C5 and T4 unchanged. C7 reproduces only
    when the incoming version was compiled before (French notched to and back first): the notch in its minted index
    then stands and every meld at 'greeter' - by address, and English's and French's by spell_id - raises
    SpellbookValidationError "Broken spells: ...". A French never compiled is refused by the 0.2.8262 check
    (`_check_notched_version` runs phases 1-4, whose DUPLICATE_SPELL_NAME fails it): nothing moves and English stays
    served, but the refusal names a failed structural check, not the taken signature.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:4270-4311
  - src/melder/aether/spellbook/spellbook.py:4107-4268
  - context_compass/artifacts/correctness_defects_20261017/runs/recheck_open_stories_public_calls_0_2_8267.txt:6-35
  - context_compass/artifacts/correctness_defects_20261017/runs/recheck_open_stories_public_calls_0_2_8267.txt:71-100
  IMPACT: The C7 regression test must compile the incoming version first, or the 0.2.8262 check hides the defect;
    the refusal this story adds runs before that check and names the signature, as `bind` does.
  NEXT: Patch docs for `_apply_notch` step 4 on the owner's go.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T23:38:22Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The incoming-key half also reproduces across Books, with a version never compiled (0.2.8267, public calls,
    the GIL off and on): Book O holds Spanish active at (Greeter, 'spanish'); Book L stages French at 'spanish' on
    English's index and notches to it. The notch stands (Phase 4 sees no duplicate: Book O's spell is not in Book
    L's pool), French takes the frame claim from Spanish, and both Books meld their own spell at 'spanish'. A third
    Book's bind of 'spanish' is refused naming French; once Book L's root is torn down its teardown releases
    'spanish' by key, the frame holds no claim while Spanish is still active, and the third Book's bind of 'spanish'
    succeeds - two active spells at one address, against the frame's one-active-spell-per-signature rule. Only bind
    reads the frame claims (`claim_lookup`); melds resolve through the Book's own maps.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:4107-4268
  - src/melder/aether/aetheric_frame/lookup_container.py:129-152
  - src/melder/aether/spellbook/spellbook.py:472-484
  - src/melder/aether/conduit/meld/meld.py:2187-2237
  - context_compass/artifacts/correctness_defects_20261017/probes/diag_notch_takes_other_books_address.py:1-69
  - context_compass/artifacts/correctness_defects_20261017/runs/diag_notch_takes_other_books_address_0_2_8267.txt:1-46
  IMPACT: The refusal of an incoming key another active spell holds is not a same-Book corner case: any Book's notch
    can take another Book's address, and that Book's teardown then frees it for a third bind.
  NEXT: The owner's call on the outgoing address (freed, as Requirements say, or kept for the index), then patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T00:16:21Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: What follows a notch (0.2.8267, public calls, the GIL off and on; the owner's point in chat 2026-10-24: "per
    notch you lose the metadata binding name should match and spellframe otherwise you fail ... melding via spell_id
    is always off the table during notches"). English -> French at one address: every way of reaching the index
    follows - a meld by address, a consumer injected by its Protocol annotation, a consumer whose SpellMap names the
    address, a linked borrower's meld by address and its injected consumer; only a meld by spell_id stays on the
    version it names. English ('greeter') -> Spanish ('spanish'): only the injected consumers follow; a meld at the
    old address raises KeyError in the lender and the borrower, and the SpellMap consumer raises RuntimeError
    "SpellMap default could not be resolved". A SpellIndex keeps no address of its own (its id, its selection and
    its members); its address is its active version's.
  EVIDENCE:
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_how_melds_follow_a_notch.py:1-115
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_how_melds_follow_a_notch_0_2_8267.txt:4-30
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_how_melds_follow_a_notch_0_2_8267.txt:31-60
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_how_melds_follow_a_notch_0_2_8267.txt:62-118
  - src/melder/aether/spellbook/bind/spell_index.py:83-116
  IMPACT: With versions at different addresses, every caller that names an address breaks at each notch that moves
    it; the owner's point holds, so the address rule is a design decision before S2's fix, not part of it.
  NEXT: The owner's choice between the options in the next note.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T00:16:21Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION_REQUEST
  CLAIM: What is the stable handle of an index across notches? (A) One address per index: a version staged or added
    onto an index takes the index's spellframe and binding name (a different one is refused), so a notch never moves
    the address, the notch's frame write is right as it is, and S2 shrinks to refusing a notch whose address another
    active spell holds (the minted-index case C7 and the cross-Book case); this walks back the 2026-10-17 answer, while
    a notch still revalidates because the code changed. (B) Keep the 2026-10-17 answer: S2 as written (free the old
    address, refuse a taken new one), and a caller that names the old address gets a clear error at the next notch
    that moves it. (C) Give the index a handle that follows notches (a meld or SpellMap by index): new API surface.
    melder_1 recommends (A): agents iterate on one object and its borrowers follow a notch, and the address is how
    every caller but an injected one reaches it.
  EVIDENCE:
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_how_melds_follow_a_notch_0_2_8267.txt:31-60
  - context_compass/tickets/stories/2026-10-17_notch_moves_signature_by_incoming_key_only_story.md:99-108
  - src/melder/aether/aetheric_frame/lookup_container.py:129-152
  IMPACT: (A) changes bind_inactive's and add_to_spell_index's admission and needs a rule for records that hold a
    mixed index; (B) keeps the story as written; (C) is a new feature lane.
  NEXT: The owner's choice; then patch docs for the chosen option.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T00:33:43Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: For option (A), on the owner's question (chat 2026-10-24: "right now we're binding a spell now we'd be
    binding a spellindex so like what are the dynamics there"): a meld by address already goes through the index.
    The Book's address map holds address -> SpellIndex and `_spells` holds SpellIndex -> its active version; Meld's
    local lookup reads the two in turn, and a borrower's contracted maps have the same two layers per lender. What
    moves today is the map's key: bind writes the new version's address, a notch's park pops the outgoing
    version's address and its promotion writes the incoming one. So (A) keeps the lookup and pins the key: the
    index owns its address, which no notch rewrites.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:2239-2272
  - src/melder/aether/conduit/meld/meld.py:2274-2320
  - src/melder/aether/spellbook/spellbook.py:6380-6386
  - src/melder/aether/spellbook/spellbook.py:1594-1656
  - src/melder/aether/spellbook/spellbook.py:1657-1716
  IMPACT: (A) changes who owns the address, not how a meld finds a spell; the open design points are the split
    (`remove_from_spell_index`) and records holding a mixed index.
  NEXT: The owner's answer on (A)'s split and record rules.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T00:39:06Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's direction (chat 2026-10-24): "defining an index to be the representation of the binding
    signature makes sense and you can validate it on the way in", with "this also implies we can have the same
    binding signatures and this means bind_inactive should bypass specific checks on demand like theres some
    overlapping defenses since we overlooked notch" and "look into this part and add your research to your ticket".
    Option (A) of the DECISION_REQUEST note is the direction; the 2026-10-17 answer (one index may hold several
    signatures) is superseded. First a read-only research pass: every check that guards a binding signature, what
    it guards today, which of them refuse or must admit a version staged at its index's signature, which overlap,
    and what (A) keeps, changes or removes. No src edit before the owner reviews it.
  EVIDENCE: context_compass/tickets/stories/2026-10-17_notch_moves_signature_by_incoming_key_only_story.md:99-108
  IMPACT: The story moves from "the notch moves the claim" to "the index owns the claim"; its Requirements and
    acceptance are rewritten after the research.
  NEXT: Inventory the signature checks in bind, bind_inactive, the index moves, the notch, cleanup, teardown,
    transfer, contracts, Phase 4, conjure, restore, graft and scan, reading each in full.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T00:40:05Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M0-222 consumed (melder_0, 2026-10-25T00:16:54Z): on the owner's ask melder_0 took
    TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout under EPIC-2026-10-25-notch_fanout_inflight_
    melds, investigation only, and asks for custody before editing conduit.py, conduit_ward.py, meld.py or the
    hydrators. This story's research is read-only; its fix under (A) may need conduit.py (the split verb
    `remove_from_spell_index` taking a new address) besides spellbook.py and spell_index.py.
  EVIDENCE: context_compass/tickets/epics/2026-10-25_notch_fanout_inflight_melds_epic.md:1-16
  IMPACT: Both lanes work around the notch; edits to conduit.py wait for custody from whichever lane holds it.
  NEXT: Reply M1-61 to melder_0; ask for conduit.py custody before any edit there.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-25T01:25:13Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The binding-signature checks on 0.2.8267, each read in full. Guards: (1) the frame claim - `bind` claims its
    new spell's address (`AethericFrame.claim_lookup` -> `LookupContainer.claim`, which refuses an address another
    spell_id holds); the only frame-wide uniqueness gate. (2) `_assert_lookup_key_available`, run with the local maps
    skipped: a borrower refuses a second lender's copy at one address (`_add_contracted_spell`, a grant and its
    dependency preflight). (3) Phase 4 DUPLICATE_SPELL_NAME over the Book's `_spell_id_pool` - the same invariant
    again, so it also catches a local and a borrowed spell at one address. (4) The 0.2.8262 notch check runs (3) only
    for a version never compiled - why a same-Book C7 is refused only then, and as a failed structural check. (5) S1's
    care: `_destroy_spell_index` and `cleanup_and_remove_spell` drop a route only when it routes to their index and
    release a claim by spell_id. (6) S8's `_restore_binding_key` sets a refused version's own address back when it
    differs from the restored version's. What (1)-(3) read holds ACTIVE spells only: a parked version never claims,
    a park takes a version out of `_lookup_spells` and `_spell_id_pool`, and a parked borrowed copy writes no lookup
    (`_add_inactive_contracted_spell`). Unchecked writers: the notch (step 4 re-points the incoming address with
    `LookupContainer.update`, which sets it unconditionally, and the park drops the outgoing route while nothing
    releases its claim); a borrower's `_reactivate_contracted_spell` (writes its lender's map unconditionally); the
    transfer flip (moves the route; the claim stays with the spell_id); and bind_inactive, add_to_spell_index and
    remove_from_spell_index, which carry no address logic at all. Book teardown releases by key the routes it still
    holds (`_cleanup_components`), the one release not by spell_id.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/lookup_container.py:92-193
  - src/melder/aether/spellbook/spellbook.py:6167-6499
  - src/melder/aether/spellbook/spellbook.py:2503-2557
  - src/melder/aether/spellbook/spellbook.py:3296-3409
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1844-2091
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:3064-3208
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/duplicate_spell_name_strategy.py:71-166
  - src/melder/aether/spellbook/spellbook.py:4270-4310
  - src/melder/aether/spellbook/spellbook.py:4675-4752
  - src/melder/aether/spellbook/spellbook.py:649-822
  - src/melder/aether/spellbook/spellbook.py:4342-4543
  - src/melder/aether/spellbook/spellbook.py:4107-4268
  - src/melder/aether/spellbook/spellbook.py:1594-1868
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1429-1553
  - src/melder/aether/spellbook/spellbook.py:5836-6096
  - src/melder/aether/spellbook/spellbook.py:4578-4673
  - src/melder/aether/spellbook/spellbook.py:4788-4898
  - src/melder/aether/spellbook/spellbook.py:407-559
  IMPACT: The owner's question ("bind_inactive should bypass specific checks"): it has none to bypass - no check reads a
    parked version, so the versions of one index can share an address today without tripping one. What (A) needs is
    the check nobody makes: the version's address against its index's, at the way in.
  NEXT: The experiment of (A) on scratch copies (MEASURE below).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T01:25:13Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Option (A) tried on scratch copies of 0.2.8267 (option_a_patches.diff, never in the repository): A -
    bind_inactive and `_apply_add_to_index` refuse a version whose address differs from its index's (the active
    member's, else the selected parked member's); B - `_apply_notch` refuses, before the park, an address the frame
    claim gives to a spell outside the index. Over the 895 tests of the 62 files that stage, move, notch or graft, the
    GIL off and on: B alone fails none; A fails 169 tests in 35 files, the same set in both modes, all at bind_inactive.
    They stage versions under another binding name ('french' on 'english'), or bind the version classes bare, so the
    class name is the frame ('restorebeta' on 'restorealpha'), or both. 161 stage in test code; 8
    (test_ordered_disposal_replay) through the graft merge lane, which replays recorded members at their recorded
    addresses. A record made on 0.2.8267 holding such an index (English at 'english', French parked on its index at
    'french') restores and grafts there; under A its restore fails whole ("restore failed at stage 'level_1'; the
    partially built world was torn down (all-or-nothing)") and its graft raises, the GIL off and on.
  EVIDENCE:
  - context_compass/artifacts/correctness_defects_20261017/scripts/option_a_experiment/option_a_patches.diff:1-44
  - context_compass/artifacts/correctness_defects_20261017/runs/option_a_blast_radius_0_2_8267.txt:1-101
  - context_compass/artifacts/correctness_defects_20261017/runs/option_a_blast_radius_0_2_8267.txt:102-335
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_mixed_record_under_option_a.py:1-146
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_mixed_record_under_option_a_0_2_8267.txt:1-65
  IMPACT: The notch refusal is free; the way-in check rewrites 169 tests' staging calls (their classes stay) and,
    without a rule for records made before it, refuses every restore and graft of a record that holds such an index.
  NEXT: The plan for (A) and the owner's three calls (next notes).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T01:25:13Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: (A) mapped to the code, for the owner's review. Changes: (a) bind_inactive and `_apply_add_to_index` refuse a
    version whose address is not its index's - any member's, since (A) keeps them equal - before anything registers,
    the message naming the spellframe and binding name to pass; a parked version still claims nothing, so no check
    needs a bypass. (b) `_apply_notch` refuses, before the park, an address the frame claim gives to a spell outside
    the index: the one door (a) leaves open - an index `remove_from_spell_index` minted keeps its version's address,
    which its source index still serves, or another Book binds the address after it was freed. (c) Records made
    before (A): restore's `_bind_one_staged` and the graft's `_park_members` and `_merge_members` stage a member the
    record put at another address at its index's address and list it in `binding_changes`, the spell_id kept (the
    owner's call 1). (d) Book teardown releases claims by spell_id like every other path (hardening; the same result
    under (A)). (e) bind_inactive's stale docstring ("all four are part of a managed spell's id"). Kept: the frame
    claim at bind, the contract-key assertion, Phase 4, the 0.2.8262 check and S1's by-spell_id care - every parked
    version now shares its active version's key. Goes: the different-key branch of S8's `_restore_binding_key` call,
    dead once a refused and a restored version share the key (its no-active-version branch stays). Follows: C5, T4
    and the cross-Book case cannot occur, and step 4's `update_lookup` is right as it is (its docstring already says
    the index keeps the signature). The split keeps its version's address - corrected: the M0-222 note's "taking a
    new address" cannot be done, since an address is part of a Spell's binding manifest and a new address is a new
    Spell (`cleanup_spell` and `bind` again, the spell_id kept); its index goes active only once no other index holds
    the address (call 2), and `add_to_spell_index` then moves a version only between an index and the ones split from
    it. Tests: the 169 stage at their index's address; new symptom tests for (a)-(c), the GIL off and on. Docs:
    README's stage -> notch -> meld example and the `notch_spell` and `add_to_spell_index` docstring examples stage a
    renamed class bare, so they change; the system docs; a Breaking release-note entry. Files: spellbook.py,
    restore_engine.py, graft_runner.py, conduit.py (docstrings; custody asked of melder_0 first) and the tests; one
    notch, 0.2.8268 unless another lane lands first.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:4107-4268
  - src/melder/aether/spellbook/spellbook.py:4342-4543
  - src/melder/aether/spellbook/spellbook.py:4788-4898
  - src/melder/aether/spellbook/spell.py:322-610
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2262-2334
  - src/melder/crystallizer/crystal_loader_system/graft_runner.py:375-584
  - src/melder/aether/conduit/conduit.py:5652-5804
  - src/melder/aether/conduit/conduit.py:6026-6137
  - README.md:1396-1426
  IMPACT: The fix is the way-in check, one notch refusal and a replay rule; the rest of the defenses stand as they are.
  NEXT: The owner's three calls (DECISION_REQUEST below); then the Requirements and Acceptance rewritten and patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T01:25:13Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION_REQUEST
  CLAIM: Three calls before patch docs, each with melder_1's recommendation. (1) A record made before (A) whose index
    holds versions at different addresses: restore and graft stage each such version at its index's address and
    list it in `binding_changes` (recommended: every version comes back, as under a changed receiving policy), or
    skip it with a named shortfall. (2) A version split off with `remove_from_spell_index` keeps its address, and its
    index can be notched active only once no other index holds that address (recommended), or the split is refused
    under (A). (3) A version staged at another address than its index's is refused, the message naming the
    spellframe and binding name to pass (recommended: the call says what it means), or it takes its index's address
    when the caller passes neither - for a class bound bare that address is its class's name, which a renamed
    version can take only as a string spellframe or through a new internal key parameter.
  EVIDENCE:
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_mixed_record_under_option_a_0_2_8267.txt:25-35
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2262-2334
  - src/melder/crystallizer/crystal_loader_system/graft_runner.py:375-584
  - src/melder/aether/spellbook/spellbook.py:4788-4898
  - src/melder/utilities/helpers/general_helpers.py:365-401
  IMPACT: (1) decides whether records made before the change restore; (2) and (3) set what the split and bind_inactive
    do from the fix on.
  NEXT: The owner's answers; then patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T01:26:52Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M3-7 consumed (melder_3, 2026-10-25T01:13:45Z): src_components is at its spec (11,874 lines). A change landed
    there puts a file a C2 entry names in Key Files (C1) into its parent C3 entry's list and the C1 map; states
    today's rule with its version tag, no "before" or CORRECTED history; adds one dated handoff entry per lane, at the
    top, with the contracts changed, the unknowns and what to verify next; and names no path into context_compass.
    melder_3 is rebuilding the assets now.
  EVIDENCE: context_compass/tickets/stories/completed/2026-10-24_src_components_to_spec_story.md:1-12
  IMPACT: S2's docs step follows these rules; the src_components index read at re-entry predates the trim, so it is
    read again before any slice.
  NEXT: The owner's three calls.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

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
- Scope: the binding signature (address) belongs to the SpellIndex - a version is staged at its index's address
  and a notch never moves it (the owner's direction of 2026-10-24, option A; the 2026-10-17 answer is
  superseded). The Requirements and Acceptance above are option B's and are rewritten after the owner's calls.
  Filed by melder_0 under EPIC-2026-10-17-correctness_defects; proven on 0.2.8251, rechecked on 0.2.8267 (Notes).
- State: in_progress with melder_1, handoff. The research is done (FACT, MEASURE and PLAN notes of
  2026-10-25T01:25:13Z): no existing check needs a bypass; (A) adds a way-in check and a notch refusal; the
  refusal fails no test, the way-in check 169 that stage at other addresses; records made before (A) need a rule.
- Next: (1) the owner's three calls (DECISION_REQUEST note of 2026-10-25T01:25:13Z); (2) the Requirements and
  Acceptance rewritten, patch docs for (a)-(e) of the PLAN note and his approval; (3) red tests, the fix, docs,
  notch 0.2.8268 and the rebuild last, with conduit.py custody from melder_0 before its docstrings change.

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
