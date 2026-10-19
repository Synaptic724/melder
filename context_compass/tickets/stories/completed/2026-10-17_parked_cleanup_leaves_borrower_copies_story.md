# Story: parked_cleanup_leaves_borrower_copies - disposing a parked version removes its copy from index-link borrowers

- Completed: 2026-10-19T13:26:06Z
- Summary: landed and notched 0.2.8261 by melder_0 - every `cleanup_spell` door takes a version out of every
  contract of its Book's root conduit (index-link members and version grants, with the borrower's entry and
  borrowed id) before it disposes it, and the Spellbook's own door goes through the root conduit once
  conjured. 13 tests red on 0.2.8260 and green with the GIL off and on, and the whole tree with S8 applied on
  this tree; release-note section "Cleaning up a spell takes it out of every contract first"; system
  documents and graph; the rebuild comes last in this pass, with S8's 0.2.8262. Turned in by melder_1 on the
  owner's word (chat 2026-10-19: "turn in tickets that you can").

## Metadata
- Story ID: STORY-2026-10-17-parked_cleanup_leaves_borrower_copies
- Epic: EPIC-2026-10-17-correctness_defects
- Status: done
- Owner: user
- Agent Name: melder_1
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-10-17T20:29:03Z
- Updated: 2026-10-19T13:26:06Z

## User Narrative
As an agent sharing a SpellIndex with other conduits through an index link, I want `cleanup_spell` of a parked
version to remove that version from every borrower, as `remove_from_spell_index` does, so that no borrower keeps a
copy of a version that no longer exists.

## Value / MRP Alignment
Contracts and links are structure. A borrower's copy of a disposed version is a record naming something that is
gone, and today nothing removes it - not even the borrower's own unlink of the index - so the structure is stuck.

## Ticket Contract
- ENTRY_GATE: the owner schedules the story and assigns an agent; conduit.py's holder releases it or carries the fix
  (melder_1 holds it and is reworking the contract side on the owner's sharing rule, so it may fold this in); an
  active board row; a component patch for `Conduit.cleanup_spell`'s owner-side emissions.
- EXECUTION_BOUNDARY: `Conduit.cleanup_spell`, `Spellbook.cleanup_spell` and `_dispose_spell`, and
  `ConduitWard._emit_spell_disposed` (patch cleanup_releases_contracts_2026_10_19); regression tests; system
  docs with their indexes and the graph; the release note; one notch (no rebuild: the owner, 2026-10-19).
- DEPENDENCIES: EPIC-2026-10-17-correctness_defects; the probe and its runs (Artifact Links);
  TASK-2026-10-16-recheck_contract_consumers_when_provider_changes (melder_1's contract work).
- EXIT_GATE: the probe's P2 shows the borrower dropping the disposed version's copy and id, as P1 shows after
  `remove_from_spell_index`; regression tests pass with the GIL off and on; docs and the notch; the rebuild with
  both checks OK comes with melder_1's S8 landing (the owner, 2026-10-19).
- FAILURE_ESCALATION: CONFLICT if melder_1's rework changes whether index-link borrowers hold parked copies at all
  (the story is then re-scoped to that design); DECISION_REQUEST if a direct `Spellbook.cleanup_spell`, which has no
  ward, should reach borrowers too.

## Requirements (Functional)
- `Conduit.cleanup_spell` of a parked version whose index survives removes that version's per-member contract, the
  borrower's entry and its borrowed id on every index-link contract covering the index - the emission
  `remove_from_spell_index` already sends, and the one whose docstring already names `Conduit.cleanup_spell` as a
  caller (`ConduitWard._emit_index_member_removed`).
- After it, a borrower's unlink of the index leaves no entry or id of the lender's versions behind.
- `remove_index_from_contract` removes every record the index link filed in the borrower for the index's
  versions - each version's entry, active or parked, its borrowed id and its member detail - a version the
  lender disposed meanwhile included (the owner, 2026-10-19: "removing the index from contract should remove
  all the spells that index shared").
- Every `cleanup_spell` door - a root conduit's, a lesser conduit's, the Spellbook's own - takes the version
  out of every contract its Book's root conduit holds before it disposes it, version grants included, and
  drops the index links when the index goes with it (the owner's go, 2026-10-19: "check for active
  contracts and then cleanup").

## Requirements (Non-Functional)
- No new lock or lock-order edge: the emission runs where the destroy emission runs - after the Book's locked
  decision and before the disposal, with no Book lock held, outside any transaction, under the ward lock - as
  the index emissions run.

## Scope Boundaries
- In scope: the contract release of every `cleanup_spell` door - index-link members, parked or active, and
  version grants - before the disposal (patch cleanup_releases_contracts_2026_10_19).
- Out of scope: what index-link borrowers hold in general; the binding-signature stories of this epic; the
  direct `Spell.cleanup()` and `cleanup_and_remove_spell` doors (probe K6, recorded for the owner).

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: landed at 0.2.8261 by melder_0, handed to melder_1 (DECISION note of 2026-10-19T12:35:35Z) and
  turned in on the owner's word (chat 2026-10-19: "turn in tickets that you can"; the epic's DECISION note).
  Before that, ready -> in_progress: the owner's go (chat 2026-10-19); melder_0 took the fix (DECISION note).

## Dependencies / Related Work
- TASK-2026-10-16-recheck_contract_consumers_when_provider_changes (melder_1; conduit.py and conduit_ward.py).
- 0.2.8251 (one version, one copy): the borrower removes a copy by its own spell_id, so the removal needs no new
  lookup.

## Tasks (Implementation Checklist)
- [x] Task: patch docs (cleanup_releases_contracts_2026_10_19); the owner's go (chat 2026-10-19).
- [x] Task: the fix with symptom-named regression tests, docs and the notch; the rebuild rides melder_1's S8
  landing (the owner, 2026-10-19).
- [x] Enforce Ticket Microcycle across all linked tasks.
- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- After `cleanup_spell` of a parked member while another member keeps the index: no borrower holds an entry for
  it, active or parked, no member detail names it, and no borrower's borrowed ids list it.
- `remove_index_from_contract` afterwards leaves the borrower with no entry or id of the lender's versions.
- After the lender disposes a parked version and stages the same class again, a notch to it completes on both
  sides and the borrower melds it (probe U3; today the notch raises AttributeError in the borrower fan-out and
  the borrower is left with no active version).
- After a lender's cleanup of a granted version, parked or active, the borrower holds no entry, id or Detail
  of it, and its meld of it fails as for a version it never held (probes K2, K3).
- `Spellbook.cleanup_spell` and a lesser conduit's `cleanup_spell` release the contracts as the root
  conduit's does (probes K4, K5, K7); a refused cleanup touches no contract.

## Validation / Test Plan
- Regression tests named for the symptom, e.g. `test_cleanup_of_a_parked_member_drops_it_from_index_link_borrowers`,
  `test_unlink_after_a_parked_cleanup_leaves_no_borrowed_ids`; GIL off and on; the probe re-run.

## UX / API / Data Notes
- No public signature changes. Visible today (probe P2): after the disposal the borrower Book still holds the
  cleaned Spell as a parked copy and lists its id among the lender's borrowed ids, before and after its unlink.

## Risks / Mitigations
- The emission walks every contract of the ward; it is the walk `remove_from_spell_index` already pays.

## Applicable Anti-Patterns
- [x] No story-state transition without linked task-state evidence.
- [x] No closure while required tasks remain active or un-routed.
- [x] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Should a direct `Spellbook.cleanup_spell` (no conduit, so no ward) reach borrowers too, or is
  `Conduit.cleanup_spell` the only surface that must? The A1 note on the epic records the same gap for a direct
  `Spellbook.bind_inactive`.
  Answered in part (owner, 2026-10-19): cleaning up a spell updates the contracts (DECISION note);
  routing the direct door through the conduit once conjured is proposed in the patch docs for his approval.
- (2026-10-19) Asked of the owner after his correction that no copy or object is involved: is a
  borrowing Book's contract entry left pointing at a version the lender cleaned up a defect at all? If
  yes, the question above stands (FACT note).
  Answered (owner, 2026-10-19): yes - a bookkeeping problem; an index removed from a contract takes every
  version it shared, active and parked (DECISION note).

## Decision Log
- 2026-10-17T20:29:03Z: filed under EPIC-2026-10-17-correctness_defects from sweep A2 (Notes).
- 2026-10-19T10:17:01Z: confirmed by the owner - an index removed from a contract takes every version it shared,
  active and parked; re-tested on 0.2.8260, GIL off and on (MEASURE and DECISION notes).
- 2026-10-19T10:41:53Z: the owner named the root cause - cleaning up a spell must update the contracts, through
  the removal code that exists, no custom rig (DECISION note).
- 2026-10-19T10:50:30Z: the owner's go; melder_0 takes the fix - the contracts that hold the version first, then
  the disposal (DECISION note).
- 2026-10-19T11:48:58Z: the src edits and 13 tests, red on 0.2.8260 and green (FACT note); no rebuild by melder_0 -
  melder_1's S8 landing, notched above 0.2.8261, rebuilds for both (the owner; DECISION note).
- 2026-10-19T12:30:04Z: docs, indexes, graph, the release-note section and the notch 0.2.8261 (FACT note).
- 2026-10-19T12:35:35Z: handed to melder_1 with every ticket melder_0 held, on the owner's word (DECISION note).
- 2026-10-19T13:26:06Z: turned in by melder_1 on the owner's word, after S8 landed on this tree (0.2.8262); the
  rebuild for both comes last in this pass (FACT notes).

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/correctness_defects_20261017/probes/probe_parked_cleanup_borrowers.py (cases P1, P2)
  - artifacts/correctness_defects_20261017/runs/probe_parked_cleanup_borrowers_gil0.txt
  - artifacts/correctness_defects_20261017/runs/probe_parked_cleanup_borrowers_gil1.txt
  - artifacts/correctness_defects_20261017/probes/probe_index_unlink_leftovers.py (cases U1-U3, 0.2.8260)
  - artifacts/correctness_defects_20261017/runs/probe_index_unlink_leftovers_gil0.txt
  - artifacts/correctness_defects_20261017/runs/probe_index_unlink_leftovers_gil1.txt
  - artifacts/correctness_defects_20261017/probes/probe_index_unlink_leftovers_u3_trace.py (U3's traceback)
  - artifacts/correctness_defects_20261017/runs/probe_index_unlink_leftovers_u3_trace_gil0.txt
  - artifacts/correctness_defects_20261017/probes/probe_cleanup_contract_doors.py (cases K1-K7, 0.2.8260)
  - artifacts/correctness_defects_20261017/runs/probe_cleanup_contract_doors_gil0.txt
  - artifacts/correctness_defects_20261017/runs/probe_cleanup_contract_doors_gil1.txt
  - system_docs/patches/completed/cleanup_releases_contracts_2026_10_19/ (the patch, five docs; promoted at
    landing, archived at turn-in)
  - artifacts/correctness_defects_20261017/runs/s3_fix/ (red, green, probes at the fix, the whole tree)
  - artifacts/correctness_defects_20261017/scripts/s3_fix/ (the src apply script and the record passes)
  - artifacts/correctness_defects_20261017/probes/probe_release_note_s3.py (the note's example, as written)
- DISPOSITION: retain_as_reference (the probes, their runs, the fix's runs and scripts); promote_to_documentation
  (the patch)
- CLEANUP_TRIGGER: the probes were re-run at the fix and are kept as the defect's reproducers

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - index-link borrowers after the lender disposes a parked version
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose and evidence (the probe); filed 2026-10-17T20:29:03Z.
- Contributions: melder_0 (synaptic_python_developer) - the probes, the patch docs
  cleanup_releases_contracts_2026_10_19, the src edits and 13 tests, the system documents, the graph prose, the
  release note and the notch 0.2.8261 (2026-10-19; Notes); melder_1 (synaptic_python_developer) - the whole tree
  with S8 applied on this tree and the turn-in (2026-10-19; Notes).
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none (self-checks only; closure on the owner's word, chat 2026-10-19)

## Notes
- DATETIME: 2026-10-17T20:29:03Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The defect, read whole and proven on 0.2.8251. `Spellbook._dispose_spell` returns None when other members
    keep the index alive, and `Conduit.cleanup_spell` then sends index-link borrowers nothing: it emits only on a
    destroyed index (`_emit_index_destroy`). `remove_from_spell_index` sends `_emit_index_member_removed`, which
    removes the member's per-member contract and the borrower's copy. Probe, English active and French parked on an
    index the borrower contracts whole: P1, `remove_from_spell_index(French)` - the borrower drops French's parked
    copy and borrowed id; P2, `cleanup_spell(French)` - the borrower keeps a parked copy holding the cleaned French
    Spell and French's id, and its own `remove_index_from_contract` then removes English and keeps French's copy
    and id. Identical with the GIL off and on.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:6182-6234
  - src/melder/aether/conduit/conduit.py:6092-6180
  - src/melder/aether/spellbook/spellbook.py:4422-4563
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2557-2589
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_parked_cleanup_borrowers.py:1-149
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_parked_cleanup_borrowers_gil0.txt:1-29
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_parked_cleanup_borrowers_gil1.txt:1-29
  IMPACT: A borrower holds a record of a version that no longer exists, and nothing removes it.
  NEXT: The owner schedules the story (or melder_1 folds it into its contract work); patch docs first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-19T01:26:09Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: "Copy" in this story is the borrowing Spellbook's contract entry - not a second spell and not an
    object the spell built. `Spellbook._add_contracted_spell` files the lender's own Spell object by
    reference (`spell_map[spell_index] = spell`) with its key and adds the index's member ids to the
    borrowed ids; `_add_inactive_contracted_spell` files a parked version the same way in the parked map.
    The finding is that entry and id staying in the borrowing Book after the lender's `cleanup_spell` of
    the version, the entry pointing at the cleaned Spell, past the borrower's own unlink (probe P2). No
    object is involved: the owner's rule (chat 2026-10-19) is that cleaning up a spell never disposes what
    it built - "only when we cleanup the scope do we clear objects they made". The owner was asked
    whether such a leftover entry is a defect, and if so whether a direct `Spellbook.cleanup_spell` must
    clear it too.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:3274-3343
  - src/melder/aether/spellbook/spellbook.py:3345-3387
  - src/melder/aether/conduit/conduit.py:6212-6264
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_parked_cleanup_borrowers_gil0.txt:12-28
  IMPACT: The story's wording read as a duplicated spell or as objects; it is Melder's own record in the
    borrowing Book.
  NEXT: Record the owner's answers here; re-scope or withdraw the story by them.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-19T01:32:16Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Correction, read in source on the owner's question (chat 2026-10-19). What stays behind is two entries
    in the borrowing conduit's Spellbook: `_inactive_contracted_spells[<lender conduit id>][<version id>]`,
    holding the lender's own Spell object for the version, already cleaned; and the version id in
    `_contracted_spell_ids[<lender conduit id>]`. No object a spell built, no Creations entry. They are not
    stuck - this story's "nothing removes it" is wrong: a sever of the link (`ConduitWard._remove_contract`
    -> `Spellbook._detach_link_contract`, which pops the borrower's whole bucket for that lender, the parked
    map and the id set included), a remove-all (`_clear_contracted_spells_for_conduit`, which clears them
    too) and the borrowing Book's teardown remove them; only the index unlink (`remove_index_from_contract`)
    leaves them. No meld reads them (`find_contracted_spell` answers None, P2). Whether the stale id
    disturbs a later grant of the same spell_id is UNKNOWN (not probed).
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:3661-3726
  - src/melder/aether/spellbook/spellbook.py:3569-3641
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1078-1233
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_parked_cleanup_borrowers_gil0.txt:12-28
  IMPACT: By the owner's rule that leftovers are the owning agent's to clean up, and with a sever clearing these,
    S3 is a tidy-up of Melder's own record at most; withdrawal is recommended to the owner.
  NEXT: The owner's word: withdraw S3, or keep it as a tidy-up of the index unlink.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-19T10:17:01Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Re-tested on 0.2.8260 at the owner's request (probe_index_unlink_leftovers.py), GIL off and on, the same
    output. U1, control: `remove_index_from_contract` with nothing disposed removes every borrower record for
    the index - English's active entry, French's parked entry, both borrowed ids, the tracked index, the ward
    contract's index and member details. U2: after the lender's `cleanup_spell(French)` (English keeps the
    index), the borrower keeps French's parked entry holding the cleaned Spell, French's borrowed id and the
    ward contract's member detail for French, which the public listing and `find_contracted_spell` no longer
    show; `remove_index_from_contract` then removes English's records and leaves those three; `sever_link`
    removes them. U3: after that cleanup the lender stages French again (the same spell_id) and notches to it;
    the lender's switch completes (French active, its meld returns 'bonjour'), but `notch_spell` raises
    AttributeError in the borrower fan-out (`Conduit._activate_borrowed_spell` ->
    `Spellbook._activate_contract_spell` -> `_reactivate_contracted_spell` reads `spell_index` on the stale
    cleaned Spell), and the borrower is left with no active version (English parked; a meld of French raises
    KeyError). No existing test covers a borrower after a lender's parked cleanup, or an unlink after one: the
    unlink tests cover live members, the destroy test the sole member, the parked-cleanup tests no borrower.
  EVIDENCE:
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_index_unlink_leftovers.py:1-202
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_index_unlink_leftovers_gil0.txt:1-93
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_index_unlink_leftovers_gil1.txt:1-97
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_index_unlink_leftovers_u3_trace_gil0.txt:1-31
  - src/melder/aether/conduit/conduit.py:6297-6340
  - src/melder/aether/spellbook/spellbook.py:1774-1846
  - tests/integration/melder/aether/conduit/test_index_link_notch_follow_integration.py:188-196
  - tests/integration/melder/aether/conduit/test_spell_index_meld_and_contract_lifecycle.py:165-175
  - tests/integration/melder/aether/conduit/test_index_lifecycle_and_depth_integration.py:129-137
  IMPACT: The leftover is real, and not only bookkeeping: it makes a later notch of the same class raise after the
    lender's switch, and the borrower loses its active version.
  NEXT: The owner's rule as requirements (DECISION note); then the owner's go for the fix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-19T10:17:01Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner (chat 2026-10-19): "inactive contracted spells that belong to another conduit should indeed be
    removed this is a book keeping problem"; "removing the index from contract should remove all the spells
    that index shared"; "all active and inactive spells properly should be removed if they are part of the
    index and were added by the borrowed conduit spells". So S3 is a defect: when an index leaves a contract,
    every record the link filed in the borrower for its versions goes - active and parked, a version the
    lender disposed meanwhile included - and the lender's cleanup of a parked version leaves none behind. A
    sever already removes them all (U2).
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-17_parked_cleanup_leaves_borrower_copies_story.md:39-48
  - context_compass/tickets/stories/2026-10-17_parked_cleanup_leaves_borrower_copies_story.md:75-81
  IMPACT: The requirements and acceptance carry the rule; the story stays ready for the owner's go.
  NEXT: The owner's go; then the patch docs with the exact edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-19T10:41:53Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner (chat 2026-10-19): "cleaning up a spell should update the [...] contracts [...] isn't that
    the issue?" - yes, it is the root cause; "you better not [...] custom rig this [...], if you cleanup a
    spell you just remove the spell from the contract"; "the code exists for all this [...] the cleanup
    should go to conduit.remove spell from contract or whatever and properly do it, or if its one of many
    in the index you want to make sure you notch it and remove the spell"; "generally you wouldn't
    randomly cleanup some [...] object on an index". Read in source: `Conduit.cleanup_spell` tells
    borrowers only when the index dies (`_emit_index_destroy`); `remove_from_spell_index` tells them after
    its move with `ConduitWard._emit_index_member_removed`, whose `_uncontract_member_spell` drops the
    member detail, the borrower's entry and its borrowed id, and whose docstring already lists
    `Conduit.cleanup_spell` as a caller. `_dispose_spell` reads the index id under the Book lock and hands
    it back only when the index went. `remove_spell_from_contract` cannot serve: it is the borrower's verb,
    needs a link transaction and refuses an index-link member. The active member of a multi-member index
    is already refused with the notch-first remedy (0.2.8256). The direct `Spellbook.cleanup_spell` emits
    nothing, not even the destroy.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:6122-6210
  - src/melder/aether/conduit/conduit.py:6212-6264
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2491-2517
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2557-2589
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:3209-3251
  - src/melder/aether/spellbook/spellbook.py:4481-4546
  - src/melder/aether/spellbook/spellbook.py:4548-4690
  - context_compass/tickets/stories/2026-10-17_parked_cleanup_leaves_borrower_copies_story.md:224-256
  IMPACT: The fix is code that exists: `cleanup_spell` sends the member removal `remove_from_spell_index` sends
    when the index survives. With that, `remove_index_from_contract` already takes every version the index
    holds, active and parked (probe U1), so the unlink needs no change.
  NEXT: The owner's go to take S3; then the patch docs with the exact edits - the surviving index id out of
    `_dispose_spell`, the emission in `cleanup_spell`, the direct door routed through the conduit once
    conjured - for his approval.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-19T10:50:30Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's go (chat 2026-10-19): "sure go ahead and fix this [...] at least you can check for active
    contracts and then cleanup". melder_0 takes S3. The fix in his order: `Conduit.cleanup_spell` finds the
    contracts that hold the version and removes it from them through the removal that exists
    (`ConduitWard._emit_index_member_removed` -> `_uncontract_member_spell`, the call `remove_from_spell_index`
    makes), then the Book disposes it; when the index goes with it, the destroy as today. The direct
    `Spellbook.cleanup_spell` takes the same path through its root conduit once conjured (proposed in the reply
    the go answered). Open before the patch: what a borrower's removal reads from the version (the destroy
    runs it after the disposal today); a version grant (`add_spell_to_contract`) of a version the lender
    disposes; the direct `Spell.cleanup()`.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-17_parked_cleanup_leaves_borrower_copies_story.md:279-313
  - src/melder/aether/conduit/conduit.py:6212-6264
  IMPACT: S3 is in progress with melder_0; the patch gate applies (the cleanup's contract emissions are a
    cross-component contract).
  NEXT: Read `Spellbook._remove_contracted_spell` and the grant path, probe a disposed version's grant, then
    write the patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-19T11:02:08Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Probe K1-K7 on 0.2.8260, the GIL off and on, the same output: which contracts keep a version its lender
    cleans up. K1, an index link, `Conduit.cleanup_spell` of parked French: the borrower keeps French's parked
    entry (cleaned), its borrowed id and the lender-side Detail. K2, a version grant of parked French: the
    same. K3, a version grant of Solo, the sole active member of its index: the borrower keeps an active entry
    holding the cleaned Solo, its id and the Detail, and its meld of Solo raises AttributeError ('Spell' object
    has no attribute '_resolvable'). K4, the direct `Spellbook.cleanup_spell` of French under an index link: as
    K1. K5, the direct door on Solo under an index link on Solo's index: the borrower keeps the cleaned active
    entry, the id, its tracked index of the destroyed index and both Details - that door sends not even the
    destroy. K6, a direct `French.cleanup()`: refused, RuntimeError "Spellbook could not resolve the requested
    local spell." (`cleanup_and_remove_spell` resolves active versions only), nothing changed - outside S3,
    recorded for the owner. K7, `cleanup_spell` through a lesser conduit: as K1 - the emission runs on the
    calling conduit's ward, which holds no contracts.
  EVIDENCE:
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_cleanup_contract_doors.py:1-229
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_cleanup_contract_doors_gil0.txt:1-85
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_cleanup_contract_doors_gil1.txt:1-89
  - src/melder/aether/conduit/conduit.py:6212-6264
  - src/melder/aether/spellbook/spellbook.py:4481-4546
  - src/melder/aether/spellbook/spellbook.py:718-737
  IMPACT: The fix covers every cleanup_spell door and both contract kinds (patch
    cleanup_releases_contracts_2026_10_19); K6's door stays as it is.
  NEXT: The tests, red on 0.2.8260.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-19T11:02:08Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Patch cleanup_releases_contracts_2026_10_19 consumed - architecture, the Conduit, Spellbook and ConduitWard
    component patches, the code-description patch - section -> implementation -> validation: (1) ConduitWard
    `_emit_spell_disposed`: the walk over the root ward's contracts with `_uncontract_member_spell` -> tests for
    a parked index-link member and a parked and an active grant; (2) Spellbook `_dispose_spell(release_contracts=
    ...)`, called after the decision and refusals, inside the try -> unit tests: called between the decision
    and the disposal, not on a refusal, the mark cleared when it raises; (3) Conduit `cleanup_spell` through
    the Book's root ward, `_emit_index_destroy(index_id, ())` after a destroy -> tests for a sole member's
    index link and a lesser conduit's call; (4) Spellbook `cleanup_spell` through the root conduit when
    conjured -> tests for the direct door, parked and sole; (5) the invariants (contracts first; a refusal
    touches none) -> the order and refusal tests; (6) migration -> red on 0.2.8260, green with the GIL off and
    on, probes K1-K7 and U1-U3, the related suites, the whole tree; docs, graph, release note, notch, rebuild.
  EVIDENCE:
  - context_compass/system_docs/patches/active/cleanup_releases_contracts_2026_10_19/architecture_patch.md:1-67
  - context_compass/system_docs/patches/active/cleanup_releases_contracts_2026_10_19/component_patch_conduit_cleanup_spell.md:1-26
  - context_compass/system_docs/patches/active/cleanup_releases_contracts_2026_10_19/component_patch_spellbook_dispose_spell.md:1-27
  - context_compass/system_docs/patches/active/cleanup_releases_contracts_2026_10_19/component_patch_conduit_ward_spell_disposed.md:1-25
  - context_compass/system_docs/patches/active/cleanup_releases_contracts_2026_10_19/code_description_patch_cleanup_spell.md:1-51
  IMPACT: Implementation may start: the patch docs exist and are linked, and the owner gave the go.
  NEXT: Write the tests and run them red on 0.2.8260.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-19T11:48:58Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The fix is in src on 0.2.8260, by patch cleanup_releases_contracts_2026_10_19 - contracts first, then the
    disposal. `ConduitWard._emit_spell_disposed(spell_id)` (new) walks the ward's contracts under the ward lock
    and, for each whose owner-side Detail map holds the version (read under the contract lock), calls
    `_uncontract_member_spell` - the Detail, the borrower's entry, active or parked, and its borrowed id go,
    an index link's member and a version grant alike - then re-emits each changed contract's record.
    `Spellbook._dispose_spell` takes `release_contracts=` (keyword, default None) and calls it with the
    spell_id first inside its try, after the decision and the refusals and before anything is invalidated; a
    raise disposes nothing and the finally clears the in-flight mark. `Conduit.cleanup_spell` passes the
    Book's ROOT conduit ward's `_emit_spell_disposed` (a lesser conduit's ward holds no contracts) and sends
    `_emit_index_destroy(index_id, ())` after a destroy. `Spellbook.cleanup_spell` goes through its root
    conduit's `cleanup_spell` once conjured. Tests: 10 integration (a parked index-link member, the unlink
    after it, a notch to the version staged again, a parked and a sole granted version, the direct door
    parked and sole, a lesser conduit's call, the borrower dropping the version while it is still live, a
    refused cleanup) and 3 component (`release_contracts` runs between the decision and the disposal, never
    on a refusal; a raising hook disposes nothing and a retry completes). On 0.2.8260: 12 failed, 1 passed
    (the refusal), GIL off and on; with the fix: 13 passed, GIL off and on.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2597-2652
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2494-2523
  - src/melder/aether/spellbook/spellbook.py:4565-4732
  - src/melder/aether/spellbook/spellbook.py:4481-4563
  - src/melder/aether/conduit/conduit.py:6212-6289
  - tests/integration/melder/aether/conduit/test_cleanup_releases_contracts_integration.py:1-307
  - tests/component/melder/spellbook/test_spellbook_component_dispose_spell_releases_contracts_first.py:1-115
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/red_0_2_8260_gil0.txt:1-261
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/red_0_2_8260_gil1.txt:1-269
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/green_gil0.txt:1-2
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/green_gil1.txt:1-10
  IMPACT: Every `cleanup_spell` door releases the version from every contract its Book's root conduit holds
    before the disposal; the direct `Spell.cleanup()` / `cleanup_and_remove_spell` doors are unchanged (K6,
    out of scope).
  NEXT: The whole tree with the GIL on against the 0.2.8260 baseline, then the validation note.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-19T11:48:58Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner (chat 2026-10-19), seeing a rebuild planned for S3: "why are you rebuilding you got melder 1
    doing [...]". melder_0 does not rebuild for S3: it lands the src, the tests, the docs, the graph, the
    release-note entry and the notch to 0.2.8261, and melder_1's S8 landing - applied onto S3 and notched
    above it (M1-46) - rebuilds the assets and bundles for both; a NOTICE tells melder_1 when S3 lands. The
    contribution guide's rebuild-last step is waived for S3 alone, by the owner.
  EVIDENCE:
  - context_compass/special_instructions/agent_contribution_guide.md:75-86
  - context_compass/tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md:3-12
  IMPACT: S3's exit gate is its tests, docs and notch; the assets stay stamped 0.2.8260 until melder_1's landing.
  NEXT: The validation note; then the docs, the release note and the notch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-19T12:00:59Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: S3's fix validated. Probes at the fix, the GIL off and on, the same output: after K1, K2, K4, K5 and K7 the
    borrower holds no entry, borrowed id or Detail of the cleaned version (K5 also drops the destroyed index's
    link); after K3 the borrower's meld of the cleaned Solo raises KeyError "[MELD] No spell found with
    spell_id", as for a version it never held; K6 (a direct `Spell.cleanup()`) is unchanged, out of scope. U1
    is unchanged; after U2's cleanup no French record is left, and the unlink and the sever leave nothing; U3's
    notch to French staged again completes on both sides and the borrower melds it ('bonjour'). The whole tree
    with the GIL off and on, against melder_1's 0.2.8260 runs: unit 9691 passed, 7 failed, 3 skipped, 7
    xfailed (the 7 are S8's red preface tests, failing in the baseline too); component 2406 passed, 23
    skipped, 1 xfailed (2403 + this lane's 3); integration aether with the GIL on 833 passed, 13 failed, 5
    xfailed (823 + this lane's 10; the 13 are melder_1's S8 red tests - 11 in the baseline, 13 with today's
    test file on 0.2.8260 too), with the GIL off 832 passed and one failure more,
    `test_concurrent_adds_of_same_conduit_admit_exactly_one`: timing-dependent, it fails on 0.2.8260 as well
    (1 of 10 reruns there, 3 of 15 here, the same assertion) and calls no cleanup_spell; integration conduit
    and spellbook 1031 passed; integration crystallizer, live_sim, multithreading and mutation_research 398
    passed, 4 xfailed; experimentation 250 passed, 4 skipped. That last integration shard timed out on the
    mounted folder at `test_pod_death_rebuilds_the_world_from_sqlite`, whose call takes 7.86 s there and
    1.31 s in a /tmp mirror on 0.2.8260 and with S3 alike - the mount, not the change - so it ran in the
    mirror. Seen, pre-existing and not S3's: a grant of a parked version adds every member id of its index to
    the borrower's borrowed ids (`_add_inactive_contracted_spell`) and its removal drops only its own, so
    after K2 English's id stays with no English entry.
  EVIDENCE:
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/probe_cleanup_contract_doors_fix_gil0.txt:1-86
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/probe_cleanup_contract_doors_fix_gil1.txt:1-90
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/probe_index_unlink_leftovers_fix_gil0.txt:1-94
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/probe_index_unlink_leftovers_fix_gil1.txt:1-98
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/full_tree/unit_aether_gil0.txt:1-65
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/full_tree/unit_spellbook_gil0.txt:1-38
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/full_tree/unit_rest_gil0.txt:1-140
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/full_tree_mirror/unit_aether_gil1.txt:1-73
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/full_tree_mirror/unit_spellbook_gil1.txt:1-46
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/full_tree/unit_rest_melder_gil1.txt:1-140
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/full_tree/unit_rest_other_gil1.txt:1-9
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/full_tree/component_gil0.txt:1-35
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/full_tree_mirror/component_gil1.txt:1-43
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/full_tree/component_agent_text_reader_gil1.txt:1-5
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/full_tree/integ_aether_gil0.txt:1-622
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/full_tree_mirror/integ_aether_gil1.txt:1-594
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/full_tree/integ_conduit_spellbook_gil0.txt:1-16
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/full_tree_mirror/integ_conduit_spellbook_gil1.txt:1-24
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/full_tree_mirror/integ_rest_gil0.txt:1-7
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/full_tree_mirror/integ_rest_gil1.txt:1-15
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/full_tree/exp_and_misc_gil0.txt:1-5
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/full_tree/exp_and_misc_gil1.txt:1-13
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/full_tree_mirror/cluster_concurrency_flake_reruns_gil0.txt:1-15
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/full_tree_mirror/cluster_concurrency_flake_reruns_pre_s3_gil0.txt:1-10
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/full_tree/integ_crystallizer_gil0_verbose.txt:1-71
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/full_tree_mirror/pod_death_mount_vs_mirror_gil0.txt:1-9
  - context_compass/artifacts/book_teardown_parked_20261019/runs/full_tree_0_2_8260/integ_aether_gil1.txt:1-79
  - context_compass/artifacts/book_teardown_parked_20261019/runs/full_tree_0_2_8260/unit_gil1.txt:1-176
  - src/melder/aether/spellbook/spellbook.py:3345-3387
  IMPACT: No regression against 0.2.8260 in either GIL mode; the acceptance criteria hold (probes K and U). The
    flaky cluster test and the borrowed-ids leftover are for the owner.
  NEXT: The system documents, their indexes and the graph; the release note; the notch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-19T12:30:04Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: S3's docs, graph, release note and notch are in. System documents (land_s3_docs_20261019.py):
    src_architecture gains a first operational invariant (a disposed version leaves every contract first)
    and a fixed failure mode, marks the 0.2.8256 invariant's gap fixed, adds the release-first clause to the
    0.2.8231 entry and remeasures three code-map extents; src_components carries the Spellbook Core, Conduit
    Runtime and ConduitWard contracts and a new flow (Conduit.cleanup_spell -> Contracts Released ->
    Spellbook._dispose_spell); tests_components and tests_architecture carry the two test files; nine numeric
    citations moved by the edits are remapped (remap_s3_citations.py); all four indexes are regenerated and
    --check OK; the bounds recipe flags 2 of 1419 citations, bare file names in an older handoff entry present
    at HEAD. Graph: extracted with --strict (0 skipped), prose re-authored for Conduit (31 responsibilities),
    Spellbook (29) and ConduitWard (13) (graph_prose_s3.py), Spellbook accepted after its source was read,
    assembled and --check OK (593 sections). Conduit and ConduitWard stay SEMANTICS_STALE: they were stale at
    HEAD before this lane, and accepting them needs their whole source re-read, which this lane did not do.
    Release note: the section "Cleaning up a spell takes it out of every contract first" - its example run
    as written prints OK on the fixed tree with the GIL off and on, and on 0.2.8260 its notch raises
    AttributeError "... object has no attribute 'spell_index'" in the borrower fan-out - and one Packaging
    bullet; the header reads 0.2.8261 and the rebuild line stays 0.2.8260 for melder_1's S8 landing to set.
    Notch: `__version__` read at the notch as 0.2.8260 and set to 0.2.8261; no rebuild (DECISION note of
    2026-10-19T11:48:58Z).
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:1159-1185
  - context_compass/system_docs/src_architecture.md:2443-2453
  - context_compass/system_docs/src_components.md:8574-8591
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/docs_index_regen.txt:1-36
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/docs_citation_bounds.txt:1-3
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/graph_extract_0_2_8261.txt:1-46
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/graph_prose_0_2_8261.txt:1-4
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/graph_accept_0_2_8261.txt:1-3
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/graph_assemble_check_0_2_8261.txt:1-4
  - context_compass/artifacts/correctness_defects_20261017/scripts/s3_fix/land_s3_docs_20261019.py:1-465
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_release_note_s3.py:1-51
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/release_note_probe_s3_gil0.txt:1-1
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/release_note_probe_s3_gil1.txt:1-5
  - context_compass/artifacts/correctness_defects_20261017/runs/s3_fix/release_note_probe_pre_s3_0_2_8260_gil0.txt:1-17
  - release_docs/next_version_release.md:1083-1143
  - release_docs/next_version_release.md:1203-1206
  - src/melder/__version__.py:12-12
  IMPACT: S3's change is landed but for the rebuild, which rides melder_1's S8 landing (the owner); the turn-in -
    the patch docs archived, the story closed - waits for the owner's word.
  NEXT: M0-211 hands spellbook.py, conduit.py and conduit_ward.py to melder_1.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-19T12:35:35Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner (chat 2026-10-19), after S3's change: "After you finish your change hand all your tickets to
    melder1 your competing for the same resources and document them". melder_0 hands S3 to melder_1, landed
    but for the rebuild and the turn-in: src, 13 tests, docs, indexes, graph, the release-note section and the
    notch 0.2.8261 (FACT notes of 2026-10-19T11:48:58Z and 12:30:04Z; MEASURE note of 12:00:59Z). conduit.py,
    spellbook.py and conduit_ward.py are melder_1's (M0-211); S3's hunks sit in `Conduit.cleanup_spell`,
    `Spellbook.cleanup_spell`, `Spellbook._dispose_spell` and `ConduitWard._emit_spell_disposed`, not in the
    notch path S8 edits. Left for melder_1: S8 applied on S3's tree and the whole tree run there (the S8
    mirror lacked S3's 13 tests); the rebuild for both, which sets the release note's rebuild line (it reads
    0.2.8260); the turn-in on the owner's word - the completion summary names 0.2.8261 and the section
    "Cleaning up a spell takes it out of every contract first", the patch docs go to
    system_docs/patches/completed/cleanup_releases_contracts_2026_10_19/, the story to completed/, and both
    boards sync. Seen and not S3's, for the owner: the direct doors (`cleanup_and_remove_spell`, a direct
    `Spell.cleanup()`) release no contract (K6); a grant of a parked version adds every member id of its
    index to the borrower's borrowed ids and its removal drops only its own (`_add_inactive_contracted_spell`,
    K2); `test_concurrent_adds_of_same_conduit_admit_exactly_one` is timing-dependent (1 of 10 reruns fail
    on 0.2.8260); the graph nodes Conduit and ConduitWard stay SEMANTICS_STALE.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-17_parked_cleanup_leaves_borrower_copies_story.md:413-450
  - context_compass/tickets/stories/2026-10-17_parked_cleanup_leaves_borrower_copies_story.md:469-527
  - context_compass/tickets/stories/2026-10-17_parked_cleanup_leaves_borrower_copies_story.md:529-573
  - src/melder/aether/conduit/conduit.py:6212-6289
  - src/melder/aether/spellbook/spellbook.py:4481-4563
  - src/melder/aether/spellbook/spellbook.py:4565-4732
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2597-2652
  - context_compass/system_docs/patches/active/cleanup_releases_contracts_2026_10_19/architecture_patch.md:1-67
  IMPACT: S3's holder is melder_1; melder_0 holds no file and no ticket.
  NEXT: melder_1 applies S8 on S3's tree (M0-211).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-19T13:07:30Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M0-212 from melder_0 (2026-10-19T12:46:59Z; the owner's word "Ok pass all that info to m1"), consumed:
    the full report behind M0-211, which the DECISION note of 2026-10-19T12:35:35Z above already carries - S3
    landed at 0.2.8261 with its release-note section, whose example runs OK on S3 with the GIL off and on and
    raises AttributeError on 0.2.8260. Left for melder_1: S8 on S3's tree with the whole tree run there (done:
    S8's MEASURE note of 2026-10-19T12:55:50Z), the rebuild for both setting the release note's rebuild line,
    and the turn-in - the patch docs to the completed folder cleanup_releases_contracts_2026_10_19, the story
    to completed/, both boards synced. Open for the owner, not S3's: K6 (the direct doors release no contract),
    K2 (a parked grant's borrowed ids), the timing-dependent test
    `test_concurrent_adds_of_same_conduit_admit_exactly_one`, and the SEMANTICS_STALE graph nodes Conduit and
    ConduitWard.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-17_parked_cleanup_leaves_borrower_copies_story.md:577-609
  - context_compass/tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md:948-992
  IMPACT: Nothing beyond this story's Next; the owner's "turn in tickets that you can" (epic DECISION note of
    this pass) covers the turn-in.
  NEXT: S3's turn-in after S8's documents, notch and release note; the rebuild last.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Closure Confirmation
- [x] Work walkthrough shared with user (the turn-in report, chat 2026-10-19, with S8's)
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
- Scope: a borrower keeps no record of a lender's version that is gone or unlinked (Requirements; the owner's
  rule, 2026-10-19). Probes and runs in Artifact Links.
- State: done (melder_1; turned in 2026-10-19T13:26:06Z). Landed at 0.2.8261 by melder_0: every `cleanup_spell`
  door takes the version out of every contract of its Book's root conduit before it disposes it (FACT and
  MEASURE notes); handed to melder_1 (DECISION note of 2026-10-19T12:35:35Z), which ran the whole tree with S8
  applied on this tree and turned the story in on the owner's word; the rebuild for both comes last in this pass.
- Open for the owner, not this story's: K6 (the direct doors release no contract), K2 (a parked grant's borrowed
  ids), the timing-dependent `test_concurrent_adds_of_same_conduit_admit_exactly_one`, and the SEMANTICS_STALE
  graph nodes Conduit and ConduitWard (FACT note of the M0-212 consumption).
- Next: none here.

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
