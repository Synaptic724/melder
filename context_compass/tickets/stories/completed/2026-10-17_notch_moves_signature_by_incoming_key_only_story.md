# Story: notch_moves_signature_by_incoming_key_only - a notch moves the signature with the active version

- Completed: 2026-10-25T12:26:46Z
- Summary: every version of a SpellIndex is bound the way its first version was - the kind of spellframe and the
  address - so `bind_inactive` and `add_to_spell_index` refuse another binding before anything is registered or
  moved, a notch keeps the index's address and refuses one another spell holds, records below 5.0.0 are refused,
  the creation cache is generation 24 and a graft merge files a member bound another way as a shortfall. Notched
  0.2.8273; release-note section "Every version of a SpellIndex is bound the way its first version was". The red
  tests are green and the full suites ran green, the GIL off and on. Rebuild last, after the closure.

## Metadata
- Story ID: STORY-2026-10-17-notch_moves_signature_by_incoming_key_only
- Epic: EPIC-2026-10-17-correctness_defects
- Status: done
- Owner: user
- Agent Name: melder_1
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-10-17T20:23:51Z
- Updated: 2026-10-25T12:26:46Z

## User Narrative
As an agent iterating on one object through versions, I want every version of an index bound the way its first
version was, so that a notch never moves the index's address, every caller that names the address follows the
notch, and no two active spells ever share an address.

## Value / MRP Alignment
The address is how every caller but an injected one reaches an index. While a version could be staged at any
address, a notch across addresses broke those callers, left the parked version holding the old address (stuck) and
could give the incoming version an address another index's active version held (wrong: two active spells at one
address). The owner's rule closes all three at the way in: the index keeps its first version's binding, a version
bound any other way is a new spell, and a notch only moves which version serves the address.

## Ticket Contract
- ENTRY_GATE: the owner's go (chat 2026-10-25: "if you want to use notch you gotta use the signature that was used
  originally and spell_index would retain that validation check ... go ahead and implement it") and his call 1
  ("notch the cache version and invalidate all the records"); the board row; the patch docs linked; the red tests
  recorded before any src edit.
- EXECUTION_BOUNDARY: `SpellIndex` (the binding and its check), `Bind._bind_logic` (records it), `Spellbook`
  (`bind_inactive`'s way-in checks, `_apply_add_to_index`, `_apply_notch`'s claim move, `_apply_remove_from_index`,
  `_revert_refused_notch`), `LookupContainer` and `AethericFrame` (`repoint`), `RecordVersion` (5.0.0 and the older-
  major refusal), `CachingSystem` (generation 24), `GraftRunner._merge_members` (the per-member shortfall), the
  Conduit's docstrings, README; the tests; the system docs with their indexes and the graph; the release note; one
  notch; the rebuild last.
- DEPENDENCIES: EPIC-2026-10-17-correctness_defects; STORY-2026-10-25-probe_and_purge_reach_every_version (turned
  in at 0.2.8269); melder_0's D-10 (lands 0.2.8270 first; this lane notches above it and edits the docs and the
  graph after it); melder_3's rebind tests task (tests_components waits for its turn-in).
- EXIT_GATE: the red tests green the GIL off and on; the full suite green both ways with the staging tests rewritten;
  docs, notch, release-note entry and closure; the rebuild last with both checks OK.
- FAILURE_ESCALATION: CONFLICT when another lane holds a file in the boundary; DECISION_REQUEST when a refusal's
  wording or reach needs the owner.

## Requirements (Functional)
- R1. A SpellIndex records the binding of the version it is created for - its spellframe's kind (none, a string
  category, a Protocol) and the address that gives (frame key and binding key, case-insensitive) - for its life;
  `SpellIndex.binding_signature` reads it. Bind records it for the index it creates; `remove_from_spell_index`
  records the moved version's.
- R2. `bind_inactive` stages a version only on an index this Book owns that keeps the version's binding, and checks
  both before anything is registered: a binding mismatch raises ValueError naming the index's binding, the
  version's and the remedy; another Book's index raises RuntimeError; either way nothing stays registered, so a
  retry with the right arguments is not refused as a spell_id collision.
- R3. `add_to_spell_index` refuses a parked version bound another way than its target index (ValueError) before
  anything moves.
- R4. A notch never moves an index's address. It moves the address's frame claim from the outgoing version to the
  incoming one in one atomic step, before the park, and refuses - RuntimeError naming the holder and the remedy,
  nothing moved - when another spell holds the address: another index's active version in this Book (a split
  version's index notched active while its source still serves it) or another Book's spell.
- R5. A version split off with `remove_from_spell_index` keeps its binding; its index can be notched active once no
  other spell holds the address, and `add_to_spell_index` moves it back.
- R6. Records: RecordVersion 5.0.0, and `check_readable` refuses every older major - pre-versioning ones included -
  naming why and the remedy (record the world again). The creation cache moves to generation 24.
- R7. Graft, merge lane: a recorded member bound another way than the merge target is a per-member shortfall.
- R8. C5 and T4 cannot occur (every version of an index shares its address), so `_revert_refused_notch`'s
  different-key branch goes.

## Requirements (Non-Functional)
- No new lock-order edge: the binding is immutable on the index and read without a lock; the claim move is one call
  into the frame container's leaf lock, under the Book lock, where the notch's unconditional update ran.
- No meld path changes; no new verb on Conduit or Spellbook; SpellIndex gains `binding_signature` (a read),
  `signature_of`, `for_binding` and `check_admits`.

## Scope Boundaries
- In scope: R1-R8; the tests that stage versions under another binding, rewritten to stage at their index's binding;
  README, docstrings, system docs, a Breaking release-note entry.
- Out of scope: EPIC-2026-10-25-dependency_watchers_listen_for_names (the stuck consumer); the meld naming rules of
  the identity map (gap 2 and gap 3); S3 (a changed binding revalidates).

## State Transition Event
- from_state: in_progress (implementation)
- to_state: done
- transition_reason: the EXIT_GATE is met but for its last item, the rebuild, which the turn-in order runs after
  this closure: the red tests and the full suites green, the GIL off and on; the docs, the graph, the notch
  (0.2.8273) and the release-note entry written. Opened for implementation on the owner's go and his call 1 (chat
  2026-10-25; DECISION notes of 08:39 and 08:51).

## Dependencies / Related Work
- STORY-2026-10-17-staged_version_releases_active_signature.
- TASK-2026-10-16-notch_seam_checks_incoming_before_parking (backlog).

## Tasks (Implementation Checklist)
- [x] Task: the owner's answer on one signature per index (2026-10-17: one index may hold several; DECISION note).
- [x] Task: research the binding-signature defenses for the index-owns-the-signature model (owner, 2026-10-24);
  the findings in Notes, for the owner's review.
- [x] Task: the owner's three calls and the rename rule (DECISION notes of 2026-10-25: call 3 and (A)'s go;
  the strict rule and call 2; call 1, the record and cache versions).
- [x] Task: red tests (MEASURE note), the GIL off and on.
- [x] Task: map every meld identity across a notch (the owner, chat 2026-10-25; notes of 2026-10-25T02:01:57Z).
- [x] Task: the owner's parked-door call (yes, 2026-10-25; its own lane,
  STORY-2026-10-25-probe_and_purge_reach_every_version).
- [x] Task: patch docs and the mapping note (PLAN note); the owner's go of 2026-10-25 covers the implementation.
- [x] Task: the fix with symptom-named regression tests, docs, notch and the rebuild last (it runs after this
  closure).
- [x] Enforce Ticket Microcycle across all linked tasks.
- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- The new symptom tests pass the GIL off and on, and the full suite passes both ways with the staging tests rewritten.
- A record of an older major is refused at the version gate with the message; the creation cache is generation 24.
- The docs and the release note say how a version of an index is bound and what a notch refuses.

## Validation / Test Plan
- tests/component/melder/spellbook/test_spellbook_component_index_keeps_its_first_binding.py (the binding, the
  way-in refusals, the foreign-index leak, the add refusal, the notch refusals C7 and cross-Book, the controls);
  tests/unit/melder/aether/test_lookup_container_repoint.py; tests/unit/melder/spellbook/bind/
  test_spell_index_binding_signature.py; a record-version unit test; a graft-merge shortfall test; the full suite,
  the GIL off and on.

## UX / API / Data Notes
- Breaking: `bind_inactive` and `add_to_spell_index` refuse a version bound another way than its index (stage an
  edited class under its index's spellframe and binding name; a renamed class or a new binding name is a new spell);
  a notch refuses an address another spell holds; records made before are refused (record the world again).

## Risks / Mitigations
- Agent code that stages renamed classes breaks at its next run: the release note's Breaking entry gives the remedy,
  and the refusal message names both bindings.
- Saved records stop loading: the owner's call; the refusal names the remedy.

## Applicable Anti-Patterns
- [x] No story-state transition without linked task-state evidence.
- [x] No closure while required tasks remain active or un-routed.
- [x] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- None: the rename rule, calls 1 and 2 and the version bumps are answered (DECISION notes of 2026-10-25).

## Decision Log
- 2026-10-17T20:23:51Z: filed under EPIC-2026-10-17-correctness_defects from sweep A1 (Notes).
- 2026-10-17T21:55:46Z: the owner answered the open question - one index may hold versions under different
  signatures, so the notch moves the claim (DECISION note).
- 2026-10-25T00:39:06Z: superseded by the owner's direction (chat 2026-10-24): the index is the representation of
  the binding signature, validated on the way in; research the overlapping defenses first; melder_1 assigned
  (DECISION note).
- 2026-10-25: the owner's go for (A) with the strict rule, then call 1: the record version to 5.0.0, older records
  refused, the creation cache to generation 24 (DECISION notes).
- 2026-10-25T12:26:46Z: closure under the owner's go; no independent review requested (DECISION note).

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
  - artifacts/correctness_defects_20261017/probes/probe_meld_identities_across_a_notch.py (every meld form)
  - artifacts/correctness_defects_20261017/runs/probe_meld_identities_across_a_notch_0_2_8267.txt
  - artifacts/correctness_defects_20261017/probes/diag_class_annotated_consumer_after_notch_back.py (stuck consumer)
  - artifacts/correctness_defects_20261017/runs/diag_class_annotated_consumer_after_notch_back_0_2_8267.txt
  - system_docs/patches/active/index_keeps_its_first_binding_2026_10_25/ (the patch: architecture, four component
    patches, the Spellbook Core code description, their indexes; promote_to_documentation)
  - artifacts/index_keeps_its_binding_20261025/runs/red_gil0.txt (the red run; delete_on_close)
  - artifacts/index_keeps_its_binding_20261025/runs/red_gil1.txt
  - artifacts/index_keeps_its_binding_20261025/scripts/run_tree.sh (the lane's runner)
- DISPOSITION: retain_as_reference for the probes and runs of artifacts/correctness_defects_20261017/;
  promote_to_documentation for the patch folder; delete_on_close for artifacts/index_keeps_its_binding_20261025/
- CLEANUP_TRIGGER: the probes are re-run at the fix and kept as the defects' reproducers; the patch merges into the
  system docs and its folder goes at closure; the lane's runs are summarized in Notes and deleted at closure
- APPLIED (2026-10-25T12:26:46Z): the patch deltas are in src_architecture and src_components, and the patch folder and
  artifacts/index_keeps_its_binding_20261025/ are deleted at this closure (their committed files stay in git
  history); the probes ran again at the fix and stay as the defects' reproducers:
  artifacts/correctness_defects_20261017/runs/*_0_2_8273*.txt.

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
- Independent Review: none requested (routine closure under the owner's go)

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

- DATETIME: 2026-10-25T02:01:57Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: How every meld names a spell, read in full on 0.2.8267 (the owner's question, chat 2026-10-25: does an index
    owning the signature work "for all melds or just some", since "you can meld using spell_id and other things").
    Three identities. (1) A spell_id - meld(spell_id), meld_existing_spell, has_live_creation and purge given one,
    SpellSpace.meld, a capability room's meld - goes to `_resolve_spell_by_id`, which reads the active pool, the
    active local versions and each lender's active copies and never the parked versions: that exact version, only
    while it is active. (2) Every other form - a SpellName string, a class object, spellframe and binding name, and
    purge or a probe given those - normalizes to an address (a class or a name keys by its lowercased name with the
    default binding) and resolves address -> SpellIndex -> the index's active version, in the Book, then in each
    lender's contracted maps: it follows the index. managed_spell_meld takes both forms and resolves them the same
    way. (3) Injection: a class annotation selects spells whose class name matches; a Protocol annotation, spells
    that recorded that Protocol; a SpellMap(spellframe=, binding_name=) compares the recorded spellframe object and
    the binding; a SpellMap(spell=Cls) compares the class object by identity; a SpellContract resolves by address
    through the contracted maps. Also following a notch: the input cache (each hit re-reads the active pool and
    falls back to the address lookup), a compiled plan's recorded ids (taken to the index's current version) and an
    index link; a version grant stays with its version. The fast doors are built on the non-dynamic lane only, and
    a notch needs a dynamic world.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:2067-2322
  - src/melder/utilities/helpers/general_helpers.py:404-456
  - src/melder/aether/conduit/meld/conduit_meld.py:282-732
  - src/melder/aether/conduit/meld/conduit_meld.py:733-956
  - src/melder/aether/conduit/meld/conduit_meld.py:150-210
  - src/melder/aether/conduit/meld/meld.py:605-730
  - src/melder/aether/conduit/meld/spellspace_meld.py:241-678
  - src/melder/nexus/rift/command_system/capability_command_system.py:1026-1090
  - src/melder/aether/conduit/conduit.py:5097-5209
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:206-446
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:771-881
  - src/melder/aether/conduit/meld/meld.py:1484-1585
  - src/melder/aether/conduit/conduit.py:5652-5805
  - src/melder/aether/conduit/conduit.py:6308-6383
  IMPACT: (A) changes none of these lookups: a spell_id stays exact (the owner's rule of 2026-10-17), and every
    address form already goes through the index, so pinning the index's address makes all of them follow a notch.
  NEXT: The MEASURE below.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T02:01:57Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The forms across a notch (probe_meld_identities_across_a_notch.py, public calls, 0.2.8267; the GIL off and on
    identical apart from object ids). Protocol case, English -> French at (Greeter, 'greeter'): after the notch the
    address, the Protocol-annotated consumer, the SpellMap by address and the index-link borrower give French; by
    spell_id French's works and English's raises KeyError "No spell found with spell_id", as do
    meld_existing_spell, has_live_creation and purge of English while it is parked; the class-annotated consumer
    raises UnresolvedInputError, the SpellMap(spell=English) consumer RuntimeError "SpellMap default could not be
    resolved", and the version-grant borrower KeyError at the address. After the notch back every form gives
    English's own `unique` object again, the one built before the notch - except the class-annotated consumer,
    still refused (FACT below). meld(spell=English) and meld('English') raise KeyError in every state: English is
    at (greeter, greeter), and a class or a name looks up (english, __default__). Bare cases: an edited class that
    keeps its name is followed by every form, the class annotation included; a renamed version bound bare (allowed
    today) loses the old name's forms and the consumer; a renamed version staged at the old address, as (A) stages
    it, answers meld(spell=ReportService) and meld('ReportService') with a ReportServiceV2 object, while
    meld(spell=ReportServiceV2) raises KeyError.
  EVIDENCE:
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_meld_identities_across_a_notch.py:1-225
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_meld_identities_across_a_notch_0_2_8267.txt:3-57
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_meld_identities_across_a_notch_0_2_8267.txt:59-123
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_meld_identities_across_a_notch_0_2_8267.txt:125-128
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_meld_identities_across_a_notch_0_2_8267.txt:130-255
  IMPACT: The answer to the owner: (A) holds for every meld that names the index; a spell_id names one version and is
    refused while that version is parked, by design; three door rules sit outside (A) (next note).
  NEXT: The gaps note.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T02:01:57Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Three gaps the map shows, none caused or fixed by (A). (1) A parked version keeps its objects (the notch back
    returns the same object), but no door reaches them while it is parked: has_live_creation and purge resolve
    active versions only (`_resolve_purge_spell`, `describe_live_creation_status`), so checking or retiring an old
    version's object takes a notch back first. (2) meld(spell=Cls) and meld('Name') are address lookups keyed by
    the class's name, not type lookups: a version bound under a spellframe is never reached that way, and under (A)
    a renamed version at the old address answers the old class's meld with an object of the new class. (3) Four
    identity rules: a spell_id is the version, an address is the index, a class annotation is the class name and a
    SpellMap(spell=Cls) is the class object, which never follows a notch, even to an edited class of the same name.
    A SpellMap(spellframe=...) compares the recorded spellframe, None for a bare binding, so it never selects a
    version bound bare (`_spellmap_frame_matches`): under (A) a bare first version and a renamed one staged with
    spellframe='ReportService' share the address, but such a SpellMap selects only the second.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:605-730
  - src/melder/aether/conduit/meld/conduit_meld.py:150-210
  - src/melder/aether/conduit/meld/conduit_meld.py:892-956
  - src/melder/utilities/helpers/general_helpers.py:241-275
  - src/melder/utilities/helpers/general_helpers.py:404-456
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:261-280
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:771-881
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_meld_identities_across_a_notch_0_2_8267.txt:38-42
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_meld_identities_across_a_notch_0_2_8267.txt:118-119
  IMPACT: (1) is a missing door; (2) and (3) are naming rules; each is the owner's call and separate from S2's fix.
  NEXT: The side defect below, then the owner's answer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T02:01:57Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Side defect, pre-existing on 0.2.8267 in both address models (the diag_class_annotated_consumer_after_notch_
    back.py runs, the GIL off and on identical): a consumer injected by a class annotation that compiled without its
    provider stays refused when the provider comes back under a spellframe. Phase 3 records the parameter as an
    UNRESOLVED_INPUT socket, with no dependency edge, keyed by the annotation (('english', '__default__')), and
    SpellSystemStates watches it under that key's frame, 'english'; bind and notch stage the incoming spell's
    address, and the commit's dirty marker marks only the watchers of those frame keys. A class bound bare has the
    frame 'english', so a notch back or a later bind marks the consumer and its next meld resolves. Bound under
    Greeter its frame is 'greeter': nothing marks the consumer, which stays `valid` with its unresolved socket, and
    every meld raises UnresolvedInputError - after a notch away and back (two Protocol versions at one address), and
    after a later bind of the provider. cleanup_spell and bind of the consumer (the same spell_id) recover it. The
    0.2.8222 kind-matching task left "the watcher ... name keying" out of scope for a follow-up ticket; none exists.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:1023-1220
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:883-926
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1889-1929
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1625-1696
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:841-877
  - src/melder/aether/spellbook/spellbook.py:5526-5598
  - src/melder/aether/conduit/conduit.py:5652-5805
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/notch_transaction_strategy.py:113-221
  - context_compass/artifacts/correctness_defects_20261017/probes/diag_class_annotated_consumer_after_notch_back.py:1-129
  - context_compass/artifacts/correctness_defects_20261017/runs/diag_class_annotated_consumer_after_notch_back_0_2_8267.txt:3-53
  - context_compass/artifacts/correctness_defects_20261017/runs/diag_class_annotated_consumer_after_notch_back_0_2_8267.txt:55-105
  - context_compass/tickets/tasks/completed/2026-10-04_repair_annotation_kind_matching_task.md:57-61
  IMPACT: Stuck structure under the owner's runtime model, outside S2's scope and unchanged by (A): the watcher and
    the staged key spell one provider two ways. A story under the epic on the owner's word (epic FACT note).
  NEXT: The owner's answer on the call below and on filing it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T02:01:57Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION_REQUEST
  CLAIM: One call beside the three of 2026-10-25T01:25:13Z: should the two doors that build nothing - has_live_creation
    and purge - reach a parked version by its spell_id, so an agent can check or retire an old version's object
    without notching back (melder_1 recommends yes: they build nothing, so serving a parked version breaks no rule,
    and a meld by spell_id stays active-only), or stay active-only as today. melder_1 also recommends a spell_id
    stays exact (the owner's 2026-10-17 rule; the one handle no notch moves), (A) goes ahead for the address forms,
    and the stuck consumer is filed as its own story under the epic.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:605-730
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_meld_identities_across_a_notch_0_2_8267.txt:38-42
  IMPACT: A yes adds a parked-version branch to those two doors, a change separate from S2's fix; a no leaves them.
  NEXT: The owner's answers; then the Requirements rewritten and patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T02:47:38Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's answers (chat 2026-10-25): "ok yeah lets do it, this makes sense to me and yeah has_live_creation
    and purge should be able to target the parked version ... go ahead and d othis ... make tests please before you
    implement this"; on the address, "Spellindex hosts a bind frame and if your using notch adhere to it ... if you
    change the name you clearly got a new spell". So (A) goes ahead for every address form, a spell_id stays exact,
    and call 3 is answered: a version not at its index's address is refused. The parked-door call is yes and is its
    own lane, STORY-2026-10-25-probe_and_purge_reach_every_version, which lands first (one lane at a time); the stuck
    consumer is EPIC-2026-10-25-dependency_watchers_listen_for_names. Open before patch docs: calls 1 (records made
    before (A)) and 2 (the split), and the rule his words imply for a rename: a version must carry its index's
    recorded spellframe and binding name - for a class bound bare, no spellframe and its own class name - not only
    the same normalized key. Today's (A) plan would still let ReportServiceV2 join a bare ReportService index by
    passing spellframe='ReportService' (the bare_renamed_a run); the stricter rule makes that a new spell, and it
    also closes gap 3's SpellMap(spellframe=...) mismatch between a bare version and one staged under a spellframe.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-17_notch_moves_signature_by_incoming_key_only_story.md:497-537
  - context_compass/tickets/stories/2026-10-17_notch_moves_signature_by_incoming_key_only_story.md:673-690
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_meld_identities_across_a_notch_0_2_8267.txt:103-123
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:771-794
  IMPACT: The Requirements rewrite waits for calls 1-2 and the rename rule; nothing in S2's code moves before the
    probe-and-purge lane lands.
  NEXT: The owner's answers on the rename rule and calls 1-2.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T08:40:04Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's go (chat 2026-10-25): "if you want to use notch you gotta use the signature that was used
    originally and spell_index would retain that validation check ... I think your spell_index idea fits, go ahead
    and implement it". The rename rule is the strict one: a SpellIndex records the signature its first version was
    bound with - the spellframe's kind (none, a string category, a Protocol) and the normalized address (frame key,
    binding key) - and admits only a version bound the same way, so bind_inactive and add_to_spell_index refuse any
    other before anything registers or moves, and a renamed class or a new binding name is a new spell. A notch never
    moves the address, and it refuses one the frame claim gives to another index's version (C7, the cross-Book case)
    before anything moves. A spell_id stays exact; the owner counts the spell_id gaps as resolved by
    STORY-2026-10-25-probe_and_purge_reach_every_version ("now you can target any id so thats resolved"). Call 2
    (the split) is taken as recommended; call 1 (records made before the rule) is asked of the owner in chat - bring
    such a version back parked in an index of its own (needs `bind_inactive(..., spell_index=None)`), or skip it with
    a report entry - and the core proceeds meanwhile.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-17_notch_moves_signature_by_incoming_key_only_story.md:457-523
  - src/melder/aether/spellbook/bind/spell_index.py:12-118
  - src/melder/aether/spellbook/spellbook.py:5896-6170
  - src/melder/aether/spellbook/spellbook.py:4029-4328
  - src/melder/aether/spellbook/spellbook.py:4638-4733
  - src/melder/aether/aetheric_frame/lookup_container.py:92-152
  IMPACT: The Requirements and Acceptance are rewritten for (A) with the strict rule; then the patch docs, the red
    tests and the fix.
  NEXT: Custody NOTICEs, the Requirements rewrite, the patch docs, the red tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T08:49:58Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Call 1, the owner's answer (chat 2026-10-25): "we gotta just notch the cache version and invalidate all the
    records bro and keep moving", then, on the plain restatement, "yeah your right now we basically are saying they
    all must have the same name yep like this is the right spot to land on anyways". So no replay rule for records
    holding a mixed index and no `bind_inactive(spell_index=None)`: RecordVersion moves to a new major (5.0.0) and
    `check_readable` refuses every record of an older major - pre-versioning ones included - with a message naming
    why and the remedy (record the world again); the creation cache moves to generation 24, so bundles written
    before are cold once. A record made after the rule cannot hold a mixed index. The graft's merge lane can still
    meet a recorded member bound another way than the merge target: that member becomes a per-member shortfall, the
    graft's rule for per-member problems.
  EVIDENCE:
  - src/melder/crystallizer/persistence/record_version.py:17-194
  - src/melder/utilities/caching_system/caching_system.py:200-256
  - src/melder/crystallizer/crystal_loader_system/graft_runner.py:492-584
  IMPACT: The restore engine needs no change beyond the version gate; the 8 graft-merge tests stage at the merge
    target's binding or assert the shortfall; tests pinning record 4.x readability move to 5.0.0.
  NEXT: The Requirements rewrite and the patch docs, then the red tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T08:52:07Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The red run on 0.2.8269 (the working tree; melder_0's uncommitted D-10 edits in it), the GIL off and on
    identical: 27 failed, 5 passed over the three new files. Failing for the reason this story fixes: the API is
    missing (SpellIndex.binding_signature, signature_of, for_binding, check_admits; LookupContainer.repoint); the
    three way-in refusals and the add refusal did not raise; the foreign-index staging raised "not owned" but left
    FrenchGreeter registered in Book B (`find_spell_by_spell_id` returned it), so a retry would be refused as a
    collision; the compiled C7 and the cross-Book notches stood; the uncompiled C7 was refused as a failed structural
    check, not for the taken address. Passing, the controls: the three admitted stagings, a notch keeping its
    address, and a split version notched active once its address is free.
  EVIDENCE:
  - tests/component/melder/spellbook/test_spellbook_component_index_keeps_its_first_binding.py:1-547
  - tests/unit/melder/aether/test_lookup_container_repoint.py:1-82
  - tests/unit/melder/spellbook/bind/test_spell_index_binding_signature.py:1-145
  - context_compass/artifacts/index_keeps_its_binding_20261025/runs/red_gil0.txt
  - context_compass/artifacts/index_keeps_its_binding_20261025/runs/red_gil1.txt
  IMPACT: The tests pin R1-R5 before any src edit; the foreign-index leak is a pre-existing defect R2 fixes.
  NEXT: The patch docs and the mapping note, then the implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T09:02:41Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Three messages consumed. M3-14 (melder_3, 08:37:18Z): melder_3 added the rebind module
    test_conduit_component_rebind_while_old_objects_are_alive.py under tests/component (tests only; untracked
    until the owner commits, so the LLM bundles are built and checked with --include-untracked) and moved the tests
    pair, both indexes regenerated: re-read tests_components and tests_architecture before editing them, and check
    the module against the strict rule with the other staging tests. M0-225 (melder_0, 08:38:33Z): D-10 took
    0.2.8270 and closed at 08:42:12Z, so S2 notches above it and its system-doc and graph edits may start - after
    melder_0's rebuild, which is not recorded yet: the bind-guard and agent-documentation manifests read 0.2.8270,
    the system-documents manifest still 0.2.8269. M3-16 (melder_3, 08:47:37Z, re M1-69): tests_components is no
    longer melder_3's; melder_3 re-reads it and tells this lane before any edit if the owner changes the module.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - src/melder/_build_assets/_bind_guard/manifest/bind_guard_manifest.py:17-17
  - src/melder/_build_assets/_system_documents/manifest/system_documents_manifest.py:22-22
  - context_compass/tickets/tasks/completed/2026-10-10_deny_file_access_under_safe_codegen_task.md:3-8
  - context_compass/tickets/tasks/2026-10-25_rebind_while_old_objects_are_alive_tests_task.md:1-16
  IMPACT: The notch is 0.2.8271 unless another lane lands first; the docs pair and tests_components are this lane's
    at landing, melder_0's rebuild state checked first.
  NEXT: The patch docs, then the mapping note.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T09:17:53Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: The patch is written and linked (architecture_patch, component patches for the Binding Pipeline, Spellbook
    Core, AethericFrame Services and the Crystallizer, and the Spellbook Core code description, each indexed). The
    mapping, patch section -> code -> test: (1) binding_pipeline: SpellIndex keeps `_binding_signature` and
    `_binding_text` (kept after cleanup, like `_id`), `signature_of`, `for_binding`, `binding_signature`,
    `check_admits`; Bind builds its index with `for_binding` -> the unit file test_spell_index_binding_signature.py and
    the component test of the recorded binding. (2) aetheric_frame_services: `LookupContainer.repoint` and
    `AethericFrame.repoint_lookup` -> test_lookup_container_repoint.py. (3) spellbook_core and its code description:
    `bind_inactive` runs `check_admits` and the ownership check after the collision check, before the hooks and
    registration; `_apply_add_to_index` runs `check_admits` before the move; `_apply_notch` reads the claim's holder,
    repoints by compare-and-set before the park, refuses a holder (RuntimeError naming it, two remedies), puts the claim
    back if the park or promotion raises and no longer calls `update_lookup`; `_apply_remove_from_index` mints with
    `for_binding`; the different-key branch of `_revert_refused_notch` goes -> the component file's staging, add, notch
    and split tests, and the 0.2.8262 refusal tests unchanged. (4) The cache: generation 24 -> the cache-version tests.
    (5) crystallizer: RecordVersion 5.0.0 with `OLDEST_READABLE_MAJOR = 5` -> a new unit test; GraftRunner's merge
    lane checks each member's signature before `bind_inactive` -> a new graft-merge test. (6) The Conduit docstrings,
    README and the UX examples -> the example runs. Then the suites, the GIL off and on.
  EVIDENCE:
  - context_compass/system_docs/patches/active/index_keeps_its_first_binding_2026_10_25/architecture_patch.md:1-119
  - context_compass/system_docs/patches/active/index_keeps_its_first_binding_2026_10_25/component_patch_spellbook_core.md:1-100
  - context_compass/system_docs/patches/active/index_keeps_its_first_binding_2026_10_25/code_description_patch_spellbook_core.md:1-88
  - context_compass/system_docs/patches/active/index_keeps_its_first_binding_2026_10_25/component_patch_crystallizer.md:1-73
  - src/melder/aether/spellbook/bind/spell_index.py:75-118
  - src/melder/aether/spellbook/bind/bind.py:808-809
  - src/melder/aether/aetheric_frame/lookup_container.py:92-152
  - src/melder/aether/spellbook/spellbook.py:6053-6075
  - src/melder/aether/spellbook/spellbook.py:4167-4328
  - src/melder/aether/spellbook/spellbook.py:4402-4507
  - src/melder/crystallizer/persistence/record_version.py:80-194
  - src/melder/crystallizer/crystal_loader_system/graft_runner.py:492-584
  IMPACT: The patch gate is met; each code step has the test that pins it, and the notch's park-before-check order
    for a target that is not parked stays with its backlog task (the claim is put back on that path).
  NEXT: SpellIndex and Bind, then the frame's repoint, then the Book.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T09:29:58Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The patch is implemented as mapped. SpellIndex keeps `_binding_signature` and `_binding_text` (kept after
    cleanup, like `_id`) and gains `for_binding`, `signature_of`, `_describe_binding`, `binding_signature` and
    `check_admits`; Bind builds every index with `for_binding`. `LookupContainer.repoint` is the claim's
    compare-and-set and `AethericFrame.repoint_lookup` wraps it (both files CRLF, kept). In the Book: `bind_inactive`
    runs `check_admits` and the ownership check right after the collision check, before the hooks and registration;
    `_apply_add_to_index` runs `check_admits` before the move; `_apply_notch` reads the claim's holder, repoints from
    the outgoing version (or from no one) before the park, refuses another holder through the new
    `_refuse_taken_address` (RuntimeError naming the holder; one remedy for this Book's other index, one for another
    Book's spell), gives the claim back if the park or promotion raises, and no longer calls `update_lookup`;
    `_apply_remove_from_index` mints with `for_binding`; `_revert_refused_notch` lost its different-key branch.
    RecordVersion is 5.0.0 with `OLDEST_READABLE_MAJOR = 5` and refuses older majors with the reason and remedy; the
    cache is generation 24; the graft's merge lane files `member_binding_differs_from_merge_target` before
    `bind_inactive`. Docstrings: the Conduit's `bind_inactive`, `notch_spell` (its example stages an edited
    ReportService) and `add_to_spell_index` (its example moves a split version back), and the stale managed-options
    line of `bind` and `bind_inactive` ("part of a managed spell's id").
  EVIDENCE:
  - src/melder/aether/spellbook/bind/spell_index.py:156-298
  - src/melder/aether/spellbook/bind/spell_index.py:631-720
  - src/melder/aether/spellbook/bind/bind.py:811-820
  - src/melder/aether/aetheric_frame/lookup_container.py:157-202
  - src/melder/aether/aetheric_frame/aetheric_frame.py:1134-1157
  - src/melder/aether/spellbook/spellbook.py:6213-6232
  - src/melder/aether/spellbook/spellbook.py:4810-4818
  - src/melder/aether/spellbook/spellbook.py:4169-4367
  - src/melder/aether/spellbook/spellbook.py:4368-4431
  - src/melder/aether/spellbook/spellbook.py:4504-4607
  - src/melder/aether/spellbook/spellbook.py:5049-5058
  - src/melder/crystallizer/persistence/record_version.py:90-217
  - src/melder/utilities/caching_system/caching_system.py:231-263
  - src/melder/crystallizer/crystal_loader_system/graft_runner.py:492-618
  IMPACT: R1-R6 and R8 are in the code, R7 in the graft; the docs and the release note follow the suites.
  NEXT: Rewrite the failing tests (MEASURE below).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T09:29:58Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The three red files pass, 32 of 32, the GIL off and on. The suites, the GIL off, first pass: unit 2 failed of
    10013, component 29 of 2508 (11 files), integration 181 of 2327 (26 files). By cause: 157 staging refusals
    ("bind_inactive refused: SpellIndex <id> keeps the binding its first version was bound with", tests that stage a
    renamed class or another binding name - 137 bare, 20 under a Protocol); 23 in the cache-schema test, which pins
    the version history (generation 24 is new); 3 record-version tests (two units pin 4.3.0 or read an unstamped
    record; one integration graft hand-builds a record at 1.0.0). No failure points elsewhere.
  EVIDENCE:
  - context_compass/artifacts/index_keeps_its_binding_20261025/runs/green1_gil0.txt
  - context_compass/artifacts/index_keeps_its_binding_20261025/runs/green1_gil1.txt
  - context_compass/artifacts/index_keeps_its_binding_20261025/runs/suites_first_pass_gil0_summary.txt
  - context_compass/artifacts/index_keeps_its_binding_20261025/runs/suites_first_pass_gil0_failures.tsv
  IMPACT: The rewrite is the staging tests (stage each version at its index's binding, keeping what each test
    proves), the cache-history pin and the record-version tests; then the GIL-on pass and the UX examples.
  NEXT: Rewrite the 37 failing files, file by file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T09:44:14Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M0-228 consumed (melder_0, 09:08:41Z, re M1-67). D-10 landed and was rebuilt at 0.2.8270, with the asset
    and bundle `--check` runs OK; the system-documents manifest reads 0.2.8270. So src_architecture, src_components
    and the graph are free for this lane at its landing. The notch-fanout race task needs none of this lane's files
    now and waits on the owner's design choice. Both designs change when `Conduit.notch_spell` runs its borrower
    fan-out, so its fix agrees conduit.py custody with this lane before its first edit.
  EVIDENCE:
  - src/melder/_build_assets/_system_documents/manifest/system_documents_manifest.py:22-22
  - context_compass/tickets/tasks/completed/2026-10-10_deny_file_access_under_safe_codegen_task.md:706-714
  - context_compass/tickets/tasks/2026-10-16_order_inflight_borrower_melds_against_notch_fanout_task.md:419-429
  IMPACT: The docs pair and the graph wait only on this lane's own order (suites, then docs). conduit.py stays this
    lane's (docstrings) until it lands, and the race fix asks first.
  NEXT: Rewrite the parked-member test of test_conduit_component_lock_residuals.py (lock_gaps is green, 5 passed).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T10:33:23Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Every test the first suite pass failed is rewritten (27 files and 2 unit tests, listed in rewritten_tests.txt):
    a staging test stages each version at its index's binding - the first version bound under a string category
    named like it, or both under one Protocol and binding name - and keeps what it proves; a test whose scenario the
    rule forbids now asserts the refusal (staging at another address, a notch onto an address another spell holds,
    a move onto an index bound another way, a 1.0.0 graft record at the version gate); notching a split version
    first frees its address. Each file passed alone, the GIL off. R7's test is new,
    test_graft_merge_keeps_the_target_binding_integration.py: a (Greeter, 'english') index (EnglishGreeter active,
    EnglishGreeterNext parked) merged into an index at the same binding, the binding name in any case, parks both, and
    a notch then serves the address; merged into (Greeter, 'french') or the category 'Greeter' at 'english' it files
    one shortfall per member and registers nothing, so the same record then grafts into an index of its own; a
    refused selection is not adopted. 6 passed, the GIL off and on; with the check removed (a copy of the tree) the 4
    refusing tests fail on bind_inactive's ValueError. The shortfall now names the target's binding in the words
    bind_inactive's refusal uses, not a tuple, and the remedy; the crystallizer patch says so (index regenerated).
  EVIDENCE:
  - context_compass/artifacts/index_keeps_its_binding_20261025/runs/rewritten_tests.txt:1-47
  - tests/integration/melder/crystallizer/test_graft_merge_keeps_the_target_binding_integration.py:1-313
  - context_compass/artifacts/index_keeps_its_binding_20261025/runs/r7_graft_merge_gil0.txt:1-2
  - context_compass/artifacts/index_keeps_its_binding_20261025/runs/r7_graft_merge_gil1.txt:1-10
  - src/melder/crystallizer/crystal_loader_system/graft_runner.py:492-624
  - context_compass/system_docs/patches/active/index_keeps_its_first_binding_2026_10_25/component_patch_crystallizer.md:30-39
  IMPACT: R7 is pinned by a test that fails without it; the suites can run whole.
  NEXT: The full suites, the GIL off and on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T10:33:23Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The owner's commit d8938890b (2026-10-25T09:52:06Z) holds this lane's src as of that time - spell_index.py,
    bind.py, spellbook.py, lookup_container.py, aetheric_frame.py, conduit.py, graft_runner.py, record_version.py and
    caching_system.py - with the component rewrites, the lane's new component and unit tests and two integration
    edits. Not in it: the 24 integration and 2 unit rewrites made after it, the graft-merge test and the shortfall
    wording in graft_runner.py, uncommitted. melder_0's D-11 has src_architecture, src_components and their indexes
    modified now, uncommitted.
  EVIDENCE:
  - context_compass/artifacts/index_keeps_its_binding_20261025/runs/rewritten_tests.txt:1-47
  - src/melder/crystallizer/crystal_loader_system/graft_runner.py:545-578
  IMPACT: The landing's change set is the commit plus what is uncommitted; the system docs wait on an order agreed
    with melder_0.
  NEXT: The full suites, the GIL off and on.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T10:47:30Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The full suites pass, the GIL off and on, on the tree as it stands (this lane's work, the owner's commit and
    melder_0's D-11 in flight): unit 10019 passed, 3 skipped, 7 xfailed; component 2480 passed, 23 skipped, 5
    xfailed; integration 2332 passed, 6 skipped, 4 xfailed, 3 xpassed (the 3 xpasses are the first pass's; 4 xfails
    of the first pass now pass, D-11's dynamic-import tests). The UX examples, the GIL off: 10 failed of 627. Six are
    this lane's - expert 17, 23, 26, 28, 29 and 31 stage a renamed class (or rebind the same one) bare at the default
    binding onto an index whose first version has a binding name, which bind_inactive refuses. Four fail as they did
    on 0.2.8256 (the identity lane's run): beginner 39 counts 9 errors where the root exports 11, expert 37's header
    lacks VERIFY:, the probes test_probe_two_visible_spells_may_not_share_a_name (DID NOT RAISE) and
    test_probe_upgrade_to_normal_keeps_creations_and_registers (KeyError for 'payload'). Not this lane's.
  EVIDENCE:
  - context_compass/artifacts/index_keeps_its_binding_20261025/runs/suites_green_summary.txt:1-24
  - context_compass/artifacts/index_keeps_its_binding_20261025/runs/ux_examples_red_gil0.txt:83-94
  - context_compass/artifacts/spell_identity_20261018/runs/ux_examples/ux_rewrite_gil0.txt:207-213
  IMPACT: The exit gate's suites are met; the six examples and the docs that stage under another binding come next.
    Custody: M1-70 (melder_0, the docs-pair order asked), M1-71 and M1-72 add the UX examples,
    agents/MELDER_AGENT_OPERATIONS.md, docs/expert/governed-change.md and docs/reference/glossary.md.
  NEXT: Rewrite expert 17, 23, 26, 28, 29 and 31 to stage at their index's binding, then rerun the UX examples.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T11:15:02Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The six expert examples stage at their index's binding, and the UX examples pass except the four that
    failed on 0.2.8256 already (623 passed of 627, the GIL off and on). Expert 17 binds both versions under the
    category 'pricing' and melds by it, so the address follows the notch, and shows a bare staging refused, then
    retried; 23 binds both under ('rule', 'branch'); 26, 28 and 31 bind under a category named like the first
    class, with its binding name (the address a bare bind of that class gives, so melds by name still resolve);
    29 stages under the first version's binding name. The expert concept map, the UX AGENTS.md (a new law
    bullet), README's stage -> notch -> meld (the edited ReportService from its own module; a meld by name
    follows the notch), docs/expert/governed-change.md, docs/reference/glossary.md and
    agents/MELDER_AGENT_OPERATIONS.md section 13 (its example now runs, the GIL off and on; its fingerprint
    bullet, wrong since 0.2.8257, corrected) state the rule. docs/tests: 39 passed, 5 need sphinx or files
    outside this checkout; the docs build: Not run (no sphinx on the device).
  EVIDENCE:
  - context_compass/artifacts/index_keeps_its_binding_20261025/runs/ux_examples_green_gil0.txt:1-31
  - context_compass/artifacts/index_keeps_its_binding_20261025/runs/ux_examples_green_gil1.txt:1-39
  - UX_and_AIX_experiences/04_expert/17_notch_swapping_a_live_object.py:1-216
  - README.md:1401-1438
  - agents/MELDER_AGENT_OPERATIONS.md:456-518
  IMPACT: Every example and user doc that staged a version another way is rewritten; the system docs come next.
  NEXT: Merge the patch into src_architecture and src_components.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T11:15:02Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Three messages consumed. M0-227 (melder_0, 10:52:15Z): D-11 took 0.2.8271 and closed, its docs, graph and
    release-note section in. M0-230 (11:03:20Z) answers M1-70: D-11 is rebuilt (the asset build and the bundle
    --check green at 0.2.8271), so S2 edits src_architecture, src_components and their indexes on top of it and
    takes 0.2.8272; D-11 remeasured six C1 loc entries (nexus.py, static_frame_viewer.py, codegen_system.py,
    codegen_namespace_configuration.py, frame_acl_compiled_access_surface.py, frame_acl_compiler.py), extended
    Codegen Internal Engine and Nexus Descriptor And ACL Managers and prepended a handoff entry to each doc and
    src_graph, so S2 re-reads those regions and recomputes each index's proof before slicing. M3-17 (melder_3,
    11:01:25Z, STORY-2026-10-25-creations_store_slots_by_binding, the owner's go) asked to edit conduit.py
    (`_register_to_creations`) and caching_system.py (generation 25) now: answered yes (M1-73) - S2's code there
    is committed (d8938890b; both files clean against it) and S2 writes neither again; melder_3 adds 25 to the
    cache-schema test and remaps, at its landing, the conduit.py citations its edit moves.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - src/melder/_build_assets/_system_documents/manifest/system_documents_manifest.py:22-22
  - tests/integration/melder/spellbook/test_cache_schema_version_integration.py:36-36
  - context_compass/tickets/stories/2026-10-25_creations_store_slots_by_binding_story.md:1-16
  IMPACT: S2 lands at 0.2.8272 unless another lane lands first. melder_3 may move conduit.py lines while S2's docs
    are written, so S2 measures its conduit.py citations at write time and melder_3 remaps them past its edit.
  NEXT: Merge the patch into src_architecture and src_components.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T11:57:21Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The patch is merged into the four system docs, the version written as a token the notch replaces.
    src_architecture (30 edits, 5108 lines, 11:29:20Z): a new first Operational Invariant, five Failure Modes, the
    SpellIndex Mutation Entry, the bind and notch sequences, record versioning. src_components (55 edits, 12281
    lines, 11:32:52Z): Spellbook Core, Binding Pipeline, AethericFrame Services, Crystallizer, Conduit Runtime
    (docstrings), the SpellIndex subcomponents and the flows. Citations into spellbook.py, bind.py and conduit.py
    were measured at write time, conduit.py with melder_3's in-progress edit in it (one line more, above S2's
    code), and the code maps remeasure the seven changed files. tests_components (51 edits, 4657 lines) and
    tests_architecture (6 edits, 1168 lines), 11:55:34Z: the four new modules and the record-version test are key
    files with code-map records, the 17 rewritten files' records are re-stamped, the catalog entries the rule
    changed are rewritten, an operational invariant covers the 36 restaged modules, the key-file union is
    recounted (292; it read 284) and the inventory is 873 test modules - the 869 of the last recount and this
    lane's four; five untracked modules of two lanes in progress are left out. All four indexes regenerated;
    --check OK.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:1066-1110
  - context_compass/system_docs/src_components.md:327-359
  - context_compass/system_docs/tests_architecture.md:455-467
  - context_compass/system_docs/tests_components.md:4185-4204
  IMPACT: The docs say what the code does; the graph, the release note, the notch and the rebuild remain.
  NEXT: The graph: the S2 nodes' descriptors, the extract, assemble and the walker; then the release note.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T12:15:04Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The graph follows the rule. Authored fields updated, re-read against source and accepted: SpellIndex (role,
    the binding responsibility, `_binding_signature` and `_binding_text`), Bind (mints with `for_binding`; its
    creates edge), Spellbook (the bind_inactive checks, the notch's claim move and refusal, the reversal without its
    key restore), LookupContainer (`repoint`), AethericFrame (`repoint_lookup`, `_lookup_container`), RecordVersion
    (5.0.0, OLDEST_READABLE_MAJOR 5, the 4.x bullet) and GraftRunner (the merge shortfall; a new borrows edge to
    SpellIndex). CachingSystem gains the generation-24 bullet but stays SEMANTICS_STALE with Conduit, since melder_3's
    edits are in both spans; melder_3 accepts them at its landing. The extract covered all of src, other lanes'
    edits in progress included; melder_0 re-assembled at 12:08:54Z with both sets in. Four messages consumed: M3-20
    and M3-21 (melder_3 edited test_spellbook_integration_parked_before_conjure.py on the owner's word, counting the
    store by spell id), M0-231 and M0-233 (D-20 applied its doc edits on top of S2's at 12:03:26Z and holds
    0.2.8272); answered M1-74 and M1-75. The expert examples 02, 09, 24 and 27 that melder_0 saw fail pass on a copy
    without the device's gitignored crystallizer cache folder and fail with it copied in.
  EVIDENCE:
  - context_compass/system_docs/src_graph.md:6353-6406
  - context_compass/system_docs/src_graph.md:15836-15955
  - context_compass/system_docs/src_graph.md:18729-18773
  - src/melder/crystallizer/asset_management/crystallizer_cache.py:176-215
  IMPACT: S2's docs and graph are complete; it notches above D-20 once D-20 has closed and rebuilt.
  NEXT: The release-note section; then the notch, closure and the rebuild last.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T12:22:05Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Notched 0.2.8273: D-20 took 0.2.8272 and rebuilt (the asset and bundle --check runs OK at 12:20Z on that
    tree). The version token is replaced in src_architecture (24), src_components (38), tests_architecture (2) and
    tests_components (38), each index regenerated and --check OK; no token is left in a tracked file but the build
    payloads the rebuild regenerates. The release note reads 0.2.8273: the section "Every version of a SpellIndex is
    bound the way its first version was" (four Breaking changes, the cross-Book staging fix, and an example that ran
    green on the device tree), a Packaging bullet, and the rebuild line. M0-235 consumed (D-20 closed at 0.2.8272);
    NOTICEs M1-76 to M1-78 sent with their alerts.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - release_docs/next_version_release.md:269-348
  - release_docs/next_version_release.md:410-419
  IMPACT: S2 holds 0.2.8273; the closure and the rebuild remain.
  NEXT: Re-run the probes at the fix, close the story and both boards, then rebuild last.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T12:26:46Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Closure. The EXIT_GATE is met but for the rebuild, which runs after this pass: the red tests (27 failed, 5
    passed on 0.2.8269) pass with the change, the GIL off and on, and the full suites ran green both ways with the
    staging tests rewritten (MEASURE note of 10:47:30Z); the UX examples and the user docs follow the rule (FACT of
    11:15:02Z); the patch is promoted into the four system docs and the graph (FACT notes of 11:57:21Z and
    12:15:04Z); notched 0.2.8273 with its release-note section (FACT of 12:22:05Z). The probes ran again at the
    fix: C5, C6 and T4 are refused at the way in, C7 by the notch, the cross-Book diagnostic at its staging and the
    meld-identity probe's renamed bare stagings too, and a mixed index can no longer be recorded; C1-C4 keep the
    claims as at 0.2.8263. Two probes predate the 0.2.8253 rename of find_spell_by_id, so they ran through
    scripts/run_with_alias.py, which aliases it. Acceptance: routine completion under the owner's go; no
    independent review was requested. Board row and detail removed, closed anchor added; the patch folder (merged)
    and the lane's runs folder deleted per their dispositions; the probes' rows kept with their new runs. Not run:
    the owner's own checks; the docs build (no sphinx on the device).
  EVIDENCE:
  - release_docs/next_version_release.md:269-348
  - src/melder/__version__.py:12-12
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_signature_claims_0_2_8273_gil0.txt:1-72
  IMPACT: The story is turned in.
  NEXT: Rebuild last and record it here as a MEASURE; tell the owner.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T12:30:58Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Rebuilt last at 0.2.8273 on Python 3.14: the asset runner wrote the agent documentation (469 entries), bind
    guard (629) and system documents (4) manifests, and its --check printed OK for all three; the bundle builder
    with --include-untracked rewrote src (585 files) and other (418), tests unchanged, and its --check printed OK
    for src, tests and other. No version token is left in src. M3-22 consumed (melder_3 takes the docs for its
    landing); M1-79 and M1-80 say S2 is landed and rebuilt.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - src/melder/_build_assets/_system_documents/manifest/system_documents_manifest.py:22-22
  IMPACT: S2 is landed and rebuilt.
  NEXT: Tell the owner.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Closure Confirmation
- [x] Work walkthrough shared with user (melder_1's chat reports to the owner, 2026-10-25, and the report
  after the rebuild)
- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.

## Context / Handoff Summary
- Scope: a SpellIndex keeps its first version's binding - the kind of spellframe and the address - and admits only a
  version bound the same way; a notch never moves the address and refuses one another spell holds; records older than
  5.0.0 are refused, the creation cache is generation 24, and the graft's merge lane files a member bound another way
  as a shortfall (R1-R8; the owner's go and call 1).
- State: done (2026-10-25T12:26:46Z), melder_1. src (seven files and the Conduit's docstrings), four new test
  modules and the 36 restaged ones, README, docs, six expert examples, the four system docs, the graph and the
  release note carry it; notched 0.2.8273; the patch folder and the lane's runs deleted; the probes ran again at
  the fix and are kept.
- Next: none in this story - the rebuild runs last (its MEASURE note follows). melder_3 accepts the graph's
  CachingSystem and Conduit nodes and remaps its conduit.py citations at its landing (M1-73, M1-75); the epic's
  open stories wait for the owner.

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
