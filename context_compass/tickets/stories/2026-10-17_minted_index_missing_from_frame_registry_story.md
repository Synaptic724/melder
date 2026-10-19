# Story: minted_index_missing_from_frame_registry - the index remove_from_spell_index mints is known to the frame

## Metadata
- Story ID: STORY-2026-10-17-minted_index_missing_from_frame_registry
- Epic: EPIC-2026-10-17-correctness_defects
- Status: in_progress
- Owner: user
- Agent Name: melder_1
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-10-17T20:32:42Z
- Updated: 2026-10-19T00:00:59Z

## User Narrative
As an agent who separates a version into its own index with `remove_from_spell_index` - to keep it, try it on its
own or share it - I want the frame to know that index belongs to my conduit, so that the version's spell_id is found
by the frame-level lookups and other conduits can be granted it, parked or after a notch makes it active.

## Value / MRP Alignment
Which conduit owns which index is structure the frame records (its spell registry). An index a Book owns but the
frame does not list makes a live version - even an active one - unreachable by spell_id from the frame and
unshareable by spell_id, while the Book itself melds it.

## Ticket Contract
- ENTRY_GATE: the owner schedules the story and assigns an agent (2026-10-18: melder_1 - DECISION note); the
  owner's word on the edits (2026-10-18: A registers the minted index as `bind` registers the index it creates,
  with B and C - DECISION note); spellbook.py claimed back from melder_0 by message once S1 and S2 of
  EPIC-2026-10-18-spell_identity_is_the_code land (M1-38), mutation_research.py claimed by message; an active
  board row; patch docs for the seam, the teardown and residency before the first src edit.
- EXECUTION_BOUNDARY (widened on the owner's word, 2026-10-18): (A) `Spellbook._apply_remove_from_index`
  registers the index it mints in the frame's spell registry as a post-conjure `bind` registers the index it
  creates - bind's guard and call, the Book's root conduit; (B) `Spellbook._unregister_conduit_spells_from_aether`,
  which only the root's teardown calls, also unregisters the indexes that hold only parked versions; (C)
  `MutationResearch._locate_live_membership` calls a version active only when the frame's lineage registry tracks
  it as its index's current version; their docstrings and their entries' (`_remove_from_spell_index`,
  `residency_view`); regression tests; system docs with their indexes and the graph; the release note; one notch;
  the rebuild last.
- DEPENDENCIES: EPIC-2026-10-17-correctness_defects; the probe and its runs (Artifact Links);
  TASK-2026-10-16-recheck_contract_consumers_when_provider_changes (melder_1's spell_id lookup fix, landed at
  0.2.8253: the frame step this story repairs comes before the Book step that fix changed); S1 and S2 of
  EPIC-2026-10-18-spell_identity_is_the_code, whose landing holds spellbook.py (M1-38).
- EXIT_GATE: on the fixed tree the probes read right - M2 and M3: the frame finds the minted index and its conduit,
  `get_spell_by_spell_id` and `get_conduit_by_spell_id` answer, the grant is accepted; M4b and M5b: the second
  bind is refused; M6: nothing is left for the torn-down root; M7: the transfer by spell_id is accepted; V2 parked
  and V3 active - and the regression tests pass with the GIL off and on, the whole tree in a mirror; docs, notch
  and the rebuild with both checks OK.
- FAILURE_ESCALATION: CONFLICT if melder_0's S1 and S2 landing changes the seam, the teardown or bind's
  registration; DECISION_REQUEST if a test shows a case the three edits do not cover.

## Requirements (Functional)
- After `remove_from_spell_index` on a conjured Book, the frame's spell registry lists the minted index under the
  Book's root conduit, registered as `bind` registers the index it creates, so `find_index_for_spell` and
  `find_conduit_id_for_spell` find the separated version - and so do the lookups, grants and transfers by
  spell_id and bind's collision guard, which walk that registry.
- That holds while the version stays parked and after a notch makes it active in the minted index; the existing
  destroy path keeps unregistering the index when it empties (`_destroy_spell_index`), and the root's teardown
  unregisters it with the root's other indexes.
- `residency_view` reads the version parked in the minted index, and active once a notch makes it active there.

## Requirements (Non-Functional)
- No new lock or lock-order edge: the registration takes the frame lock alone, after the seam's Book-locked section,
  as bind's registration and the destroy path's unregistration do; the teardown reads each parked version's index
  under the Book lock (Book -> spell, the order Book teardown takes) and unregisters with the frame lock alone after
  it; residency's lineage read takes the registry lock, then the state's lock, each alone, with no other lock held.

## Scope Boundaries
- In scope: the frame registration of the minted index, its unregistration at the root's teardown, and residency's
  verdict for a version in it.
- Out of scope: the binding signature an active version in a minted index takes
  (STORY-2026-10-17-notch_moves_signature_by_incoming_key_only); the parked versions Book teardown leaves uncleaned
  (STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned); a restore or graft of a separated version
  (STORY-2026-10-17-restore_drops_separated_parked_version); a new index state (withdrawn by the owner,
  ALIGNMENT_CHECK note).

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: the owner scheduled the story for melder_1 (chat 2026-10-18; DECISION note); the defect
  is re-verified on the current tree before any change.

## Dependencies / Related Work
- melder_1's spell_id lookup fix (the owner's rule: a lookup by spell_id returns that spell or nothing).
- STORY-2026-10-17-parked_cleanup_leaves_borrower_copies (the same family of index-membership records).

## Tasks (Implementation Checklist)
- [x] Task: the owner's word on the edits (2026-10-18; DECISION note).
- [x] Task: patch docs for the seam, the teardown and residency (linked; PLAN note).
- [ ] Task: the fix with symptom-named regression tests (written: red on 0.2.8256, green with A-D; MEASURE
  note), docs, notch and the rebuild last.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- After `remove_from_spell_index(spell_id=X)`: `frame.find_index_for_spell(X)` returns the minted index,
  `get_conduit_by_spell_id(X)` returns the owning root, `get_spell_by_spell_id(X)` returns X, and `residency_view`
  reads X parked.
- After a notch makes X active in the minted index: the same, `residency_view` reads X active, a borrower's
  `add_spell_to_contract(spell_id=X)` is accepted, and a transfer by spell_id moves X to its target.
- While X is in the minted index, a bind of X's spell_id by another Book - of the frame, or of another frame under
  process-wide spell ids - is refused, as it is for a version in any registered index.
- After X moves back with `add_to_spell_index`, the emptied minted index is gone from the registry; after the root's
  teardown the frame holds no entry for the root.

## Validation / Test Plan
- Regression tests named for the symptom, e.g. `test_a_version_separated_into_its_own_index_is_found_by_spell_id`,
  `test_a_version_notched_active_in_its_own_index_can_be_granted_by_spell_id`,
  `test_a_version_in_its_own_index_cannot_be_bound_again_by_another_book` and
  `test_a_torn_down_root_leaves_no_registry_entry_for_a_separated_version`; red on 0.2.8256 and green with the
  three edits, GIL off and on; the probes M1-M7 and V1-V4 re-run; the whole tree in a mirror.

## UX / API / Data Notes
- No public signature changes. Visible today: `get_spell_by_spell_id` and `get_conduit_by_spell_id` raise
  ValueError for a version the conduit's own Book owns in a minted index (parked or active), a grant or a transfer
  of it by spell_id raises the same error, another Book may bind its spell_id, and `residency_view` reads it
  `declared_only`. After the fix all four answer as they do for a version in any other index.

## Risks / Mitigations
- A walk over the frame registry now sees one more index per separated version; the walks are the existing ones.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- none.

## Decision Log
- 2026-10-17T20:32:42Z: filed under EPIC-2026-10-17-correctness_defects from sweep A3 (Notes).
- 2026-10-18T17:35:35Z: the boundary's widening asked of the owner - B (the root's teardown) and C (residency)
  (DECISION_REQUEST note).
- 2026-10-18T18:00:11Z: the owner's word - A registers the minted index as `bind` registers the index it creates,
  with B and C; no new index state (DECISION and ALIGNMENT_CHECK notes).

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/correctness_defects_20261017/probes/probe_minted_index_registry.py (cases M1-M3)
  - artifacts/correctness_defects_20261017/runs/probe_minted_index_registry_gil0.txt
  - artifacts/correctness_defects_20261017/runs/probe_minted_index_registry_gil1.txt
  - artifacts/correctness_defects_20261017/probes/probe_research_residency_moves.py (cases V2-V3: residency_view; FACT note)
  - artifacts/correctness_defects_20261017/runs/probe_research_residency_moves_gil0.txt
  - artifacts/correctness_defects_20261017/runs/probe_research_residency_moves_gil1.txt
  - artifacts/minted_index_registry_20261018/ (melder_1's lane: re-runs, scripts, notes)
  - system_docs/patches/active/minted_index_registry_2026_10_18/ (the three patch docs)
  - artifacts/minted_index_registry_20261018/probes/probe_minted_index_fix_cases.py (cases M4-M7)
  - artifacts/minted_index_registry_20261018/runs/s4_preview_0_2_8256_abcd.diff (edits A-D to land)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: the probe is re-run at the fix and kept as the defect's reproducer

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - the frame's spell registry and the index remove_from_spell_index mints
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose and evidence (the probe); filed 2026-10-17T20:32:42Z.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-17T20:32:42Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The defect, read whole and proven on 0.2.8251. `_apply_remove_from_index` mints `SpellIndex(initial_id=
    spell_id)` and repoints the spell without registering the new index in the frame's spell registry - the
    registration a post-conjure `bind` makes for its new index (`_register_single_spell_index`) - so
    `find_conduit_id_for_spell`, which walks that registry, cannot find the version. Probe: M1 (control) - French
    parked in English's index is found; M2 - French alone and parked in the minted index: `find_index_for_spell`
    None, `get_spell_by_id` and `get_conduit_by_spell_id` raise "Spell version <id> not found in any conduit."; M3 -
    French notched active there: the same, `meld(spell_id=French)` builds French, and a borrower's
    `add_spell_to_contract(spell_id=French)` raises that ValueError. Identical with the GIL off and on.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:4271-4356
  - src/melder/aether/spellbook/spellbook.py:5883-5888
  - src/melder/aether/spellbook/spellbook.py:4192-4237
  - src/melder/aether/aetheric_frame/aetheric_frame.py:1288-1307
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_minted_index_registry.py:1-149
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_minted_index_registry_gil0.txt:1-26
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_minted_index_registry_gil1.txt:1-26
  IMPACT: A live version its Book owns - active or parked - is unknown to its frame by spell_id and cannot be shared
    by spell_id.
  NEXT: The owner schedules the story; patch docs for the seam first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-17T21:16:07Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: MutationResearch loses the version too (sweep A8, probe V2-V3). `residency_view` reads runtime truth from the
    frames' spell registry (`_locate_live_membership` -> `AethericFrame.find_index_for_spell`), so a version in the
    minted index reads `declared_only` with no index - parked there (V2) and after a notch made it active there
    (V3) - while members of a registered index read right (V1, V4). Identical with the GIL off and on.
  EVIDENCE:
  - src/melder/mutation_research/mutation_research.py:1485-1525
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_research_residency_moves.py:1-110
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_research_residency_moves_gil0.txt:1-13
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_research_residency_moves_gil1.txt:1-13
  IMPACT: The record agents read to see where their versions live misses every version in a minted index; the
    regression tests should read `residency_view` too.
  NEXT: The owner's scheduling.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T17:10:56Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's order puts this story with melder_1 after S9 (chat 2026-10-18): parallel - melder_0 keeps
    EPIC-2026-10-18-spell_identity_is_the_code, melder_1 takes the correctness fixes one at a time; of the stories
    after S8 he said "do the ones without open questions please" - S9, S4 and S7 - with "go over them again before
    you make changes and let him know". S8 is on hold and S9 landed at 0.2.8256, so S4 is next. The defect is
    re-verified on 0.2.8256 and its code path re-read whole before any change; the exact edits go to the owner
    before the first one; melder_0 was told (M1-38). The fix sits in spellbook.py, which melder_0 holds for S1 and
    S2 until they land, so it is claimed back by message before any edit.
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-17_correctness_defects_epic.md:915-930
  - context_compass/tickets/stories/completed/2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md:198-215
  - context_compass/tickets/stories/completed/2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md:777-803
  IMPACT: The ENTRY_GATE's scheduling and assignment are met; the patch, the owner's word on the edits and the file
    claim remain before any src edit.
  NEXT: Re-run probe M1-M3 and V1-V4 on 0.2.8256 with the GIL off and on; re-read the minting seam and the frame
    registry whole.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T17:17:12Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The defect holds on 0.2.8256, re-verified before any change as the owner asked. melder_0's two probes,
    copied with the 0.2.8253 renames (`find_spell_by_id` -> `find_spell_by_spell_id`, `get_spell_by_id` ->
    `get_spell_by_spell_id`), ran on Python 3.14.7t; with the GIL on each output equals the GIL-off run apart from
    the GIL-mode warning. M1 (control): the frame finds French parked in English's index, and
    `get_spell_by_spell_id` now answers French itself, by the 0.2.8253 rule (it answered English). M2 (French alone
    and parked in the minted index) and M3 (French notched active there): `find_index_for_spell` answers None,
    `find_conduit_id_for_spell` not the lender, `get_spell_by_spell_id` and `get_conduit_by_spell_id` raise "Spell
    version <id> not found in any conduit."; in M3 `meld(spell_id=French)` builds French while a borrower's
    `add_spell_to_contract(spell_id=French)` raises the same ValueError. V1-V4: `residency_view` reads French
    `declared_only in none` in the minted index, parked (V2) and active (V3); members of English's index read right.
  EVIDENCE:
  - context_compass/artifacts/minted_index_registry_20261018/probes/probe_minted_index_registry_0_2_8256.py:1-152
  - context_compass/artifacts/minted_index_registry_20261018/runs/probe_minted_index_registry_0_2_8256_gil0.txt:1-26
  - context_compass/artifacts/minted_index_registry_20261018/runs/probe_minted_index_registry_0_2_8256_gil1.txt:1-30
  - context_compass/artifacts/minted_index_registry_20261018/probes/probe_research_residency_moves_0_2_8256.py:1-113
  - context_compass/artifacts/minted_index_registry_20261018/runs/probe_research_residency_moves_0_2_8256_gil0.txt:1-13
  - context_compass/artifacts/minted_index_registry_20261018/runs/probe_research_residency_moves_0_2_8256_gil1.txt:1-17
  IMPACT: Nothing landed since 0.2.8251 changed the failure; only M1's answer moved, as the 0.2.8253 rule says.
  NEXT: Read the minting seam, the frame registry and its readers whole (FACT note).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T17:17:12Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The minting seam, the frame's spell registry and every reader of it, read whole on 0.2.8256. The registry
    maps a conduit id to a set of SpellIndex (`_spell_registry`) beside the Book's live `_spell_ids`
    (`_selected_spell_registry`). Conjure registers the indexes that hold an active spell (`set(_spells.keys())`), a
    post-conjure `bind` its new index (`_register_single_spell_index`: the frame lock alone, after the Book lock),
    and `_destroy_spell_index` unregisters an emptied index under the spell's owner id; `_apply_remove_from_index`
    mints `SpellIndex(initial_id=spell_id)` and registers nothing, so every walk of `_spell_registry` misses it -
    `find_index_for_spell`, `find_conduit_id_for_spell` (so `Aether._get_conduit_by_spell_id`, the spell_id lookups,
    a grant and a transfer by spell_id), `_find_index_for_spell_unless_cleaned`, MutationResearch's
    `_locate_live_membership`, graft's resident check and the transfer's `_spell_in_registry`. Three readers shape
    the fix. (1) `Aether._check_for_spell`, bind's collision guard, asks `has_spell` (the live `_spell_ids`, which
    hold French) and then returns `find_index_for_spell` - None for French - so another Book of the frame, or of
    another frame under process-wide ids, may bind French's spell_id while it lives in the minted index (to be
    probed). (2) Root teardown unregisters only `set(_spells.keys())`, before the Book is cleaned
    (`_cleanup_normal_conduit` step 4), and the frame drops a conduit's entry only when its set empties, so a minted
    index registered while its version stays parked would outlive the root in the registry: the fix must unregister
    it at teardown too. (3) `_locate_live_membership` calls a version active when its index selects it
    (`index.selected_spell_id == spell_id`), and the minted index selects its parked member (S10, withdrawn by the
    owner: activation takes a notch), so once registered, a parked French there would read `active`, not `parked`.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:4303-4388
  - src/melder/aether/spellbook/spellbook.py:4224-4269
  - src/melder/aether/spellbook/spellbook.py:4128-4222
  - src/melder/aether/spellbook/spellbook.py:5919-5924
  - src/melder/aether/spellbook/spellbook.py:2672-2716
  - src/melder/aether/aether.py:2505-2544
  - src/melder/aether/aether.py:2550-2624
  - src/melder/aether/aether.py:2744-2800
  - src/melder/aether/aetheric_frame/aetheric_frame.py:873-976
  - src/melder/aether/aetheric_frame/aetheric_frame.py:1010-1038
  - src/melder/aether/aetheric_frame/aetheric_frame.py:1187-1307
  - src/melder/aether/conduit/conduit.py:1034-1178
  - src/melder/mutation_research/mutation_research.py:1374-1525
  - src/melder/crystallizer/crystal_loader_system/graft_runner.py:332-373
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1173-1200
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1429-1487
  IMPACT: The fix is three edits, not one: register the minted index at the seam, unregister every index the root
    registered at its teardown, and let residency call a version active only when its Book holds it active. The
    third reaches mutation_research.py, outside the story's EXECUTION_BOUNDARY, so it goes to the owner.
  NEXT: Prove (1)-(3) in a /tmp mirror: the duplicate binds on the tree, then the seam's registration alone (teardown
    and V2), then all three edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T17:35:35Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The three readers the FACT note named, probed on 0.2.8256 (new probe M4-M7, Python 3.14.7t; the GIL-on
    output equals the GIL-off one apart from the GIL-mode warning). M4: another Book of the frame binds French
    (same class, address and existence, so French's spell_id). Control (a), French parked in English's index: both
    binds refused, "Spell ID collision detected". (b), French alone in the minted index: a conjured Book's
    post-conjure bind is ACCEPTED - two Books of one frame hold French's spell_id - and an unconjured Book's bind is
    accepted too, its conjure then refused ("Conjure refused: 1 spell(s) owned by this ..."). M5: a Book of another
    frame under process-wide spell ids (the default) - the same answers as M4. M6: root 'lender' torn down with
    French parked alone in the minted index - nothing was ever registered for it, so nothing is left behind. M7: a
    transfer by spell_id of French, notched active in the minted index, is refused: ValueError "Spell version <id>
    not found in any conduit.".
  EVIDENCE:
  - context_compass/artifacts/minted_index_registry_20261018/probes/probe_minted_index_fix_cases.py:1-198
  - context_compass/artifacts/minted_index_registry_20261018/runs/probe_minted_index_fix_cases_0_2_8256_gil0.txt:1-32
  - context_compass/artifacts/minted_index_registry_20261018/runs/probe_minted_index_fix_cases_0_2_8256_gil1.txt:1-36
  IMPACT: The defect is wider than lookups: bind's collision guard (`Aether._check_for_spell`) misses a version in a
    minted index, so its spell_id can be bound again in the frame and in other frames, and an ownership transfer by
    spell_id is refused. The regression tests take M4b, M5b and M7 as acceptance cases.
  NEXT: Record the prototypes of the three edits (MEASURE note).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T17:35:35Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The fix proven in /tmp copies of the 0.2.8256 src, one edit at a time, applied by the lane's script
    (`apply_s4.py --edits`; the copies differ from the tree in those files only); all three probes run, GIL off, and
    with all three edits GIL on too (equal apart from the warning). A - `_apply_remove_from_index` registers the
    minted index under the spell's owner, frame lock alone after the Book lock: M2 and M3 found, both lookups
    answer, the grant is accepted, M4b and M5b refused, M7's transfer accepted; but V2 reads French "active in
    index2" while the Book holds it parked (the minted index selects its parked member; activation takes a notch,
    the owner's S10 ruling), and M6 leaves the dead root a registry entry (1 index) and an id-set entry, so
    `find_index_for_spell` and `find_conduit_id_for_spell` answer the dead root. A+B - the root's teardown
    (`_unregister_conduit_spells_from_aether`) also unregisters each parked version's index: M6 clean; V2 still
    "active". A+B+C - `_locate_live_membership` calls a version active only when the index selects it and the
    frame's lineage registry tracks it as that index's current version (`get_by_index_id(index.id)
    .current_spell_id`): every case right - V2 parked, V3 active, M1-M7 as above. The preview diff is 161 lines;
    re-run on the final preview, the A+B+C outputs are byte-equal to the recorded ones.
  EVIDENCE:
  - context_compass/artifacts/minted_index_registry_20261018/scripts/apply_s4.py:1-235
  - context_compass/artifacts/minted_index_registry_20261018/runs/s4_preview_0_2_8256.diff:1-161
  - context_compass/artifacts/minted_index_registry_20261018/runs/prototype_A_probe_minted_index_fix_cases_gil0.txt:1-30
  - context_compass/artifacts/minted_index_registry_20261018/runs/prototype_A_probe_research_residency_moves_0_2_8256_gil0.txt:1-13
  - context_compass/artifacts/minted_index_registry_20261018/runs/prototype_AB_probe_minted_index_fix_cases_gil0.txt:1-30
  - context_compass/artifacts/minted_index_registry_20261018/runs/prototype_AB_probe_research_residency_moves_0_2_8256_gil0.txt:1-13
  - context_compass/artifacts/minted_index_registry_20261018/runs/prototype_ABC_probe_minted_index_fix_cases_gil0.txt:1-30
  - context_compass/artifacts/minted_index_registry_20261018/runs/prototype_ABC_probe_minted_index_fix_cases_gil1.txt:1-34
  - context_compass/artifacts/minted_index_registry_20261018/runs/prototype_ABC_probe_minted_index_registry_0_2_8256_gil0.txt:1-26
  - context_compass/artifacts/minted_index_registry_20261018/runs/prototype_ABC_probe_minted_index_registry_0_2_8256_gil1.txt:1-30
  - context_compass/artifacts/minted_index_registry_20261018/runs/prototype_ABC_probe_research_residency_moves_0_2_8256_gil0.txt:1-13
  - context_compass/artifacts/minted_index_registry_20261018/runs/prototype_ABC_probe_research_residency_moves_0_2_8256_gil1.txt:1-17
  IMPACT: The seam's registration alone (A) fixes the lookups but makes residency wrong in a new way and leaves a
    torn-down root in the registry; A+B+C is the smallest set with every case right. B sits outside the story's
    EXECUTION_BOUNDARY in spellbook.py (the root's teardown) and C in mutation_research.py (DECISION_REQUEST note).
  NEXT: The owner's word on the three edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T17:35:35Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION_REQUEST
  CLAIM: The fix needs the story's EXECUTION_BOUNDARY widened, which is the owner's call (the synaptic overlay: no
    scope expansion without his word). The boundary names the seam only. Edit B is in the same file but in the root's
    teardown (`Spellbook._unregister_conduit_spells_from_aether`), and edit C is in another subsystem's file
    (`MutationResearch._locate_live_membership` and the `residency_view` contract, mutation_research.py, CRLF in the
    working tree). Asked of the owner with the three edits: A + B + C as previewed (recommended: the only set with
    every probe case right), or another shape. No src edit before his word; spellbook.py is melder_0's until S1 and
    S2 of EPIC-2026-10-18-spell_identity_is_the_code land, and mutation_research.py is on no lane's list.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-17_minted_index_missing_from_frame_registry_story.md:25-32
  - context_compass/artifacts/minted_index_registry_20261018/runs/s4_preview_0_2_8256.diff:1-161
  - context_compass/tickets/epics/2026-10-17_correctness_defects_epic.md:981-1002
  IMPACT: On his yes the boundary, requirements and acceptance take B, C and the M4-M7 cases, and the patch docs,
    the red tests and the claim of both files follow; on another answer the fix is re-shaped first.
  NEXT: Ask the owner; then tell melder_0 (M1-39).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T17:39:55Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: ALIGNMENT_CHECK
  CLAIM: The owner did not take the three edits (chat 2026-10-18): "lets talk please you can't just unregister
    indexes without an active version". Edit B was read as unregistering live indexes that hold no active version.
    It does not: `_unregister_conduit_spells_from_aether` has one caller, the root's permanent teardown
    (`Conduit._cleanup_normal_conduit` step 4, reached from `_permanent_cleanup` for a normal conduit only), which
    already removes every index of the dying root that holds an active version, just before the Book is cleaned.
    B adds the indexes holding only parked versions to that same teardown. While the root lives nothing is
    unregistered: with A the minted index stays registered whether its version is parked or active, and leaves only
    when it empties (`_destroy_spell_index`, as today) or its root is torn down. Without B, A leaves the dead root's
    entry, because the frame drops a conduit's entry only once its set is empty (prototype A, M6). Explained to the
    owner; his word is awaited, and nothing changes meanwhile.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:805-860
  - src/melder/aether/conduit/conduit.py:1034-1178
  - src/melder/aether/spellbook/spellbook.py:2695-2716
  - src/melder/aether/aetheric_frame/aetheric_frame.py:1216-1240
  - context_compass/artifacts/minted_index_registry_20261018/runs/prototype_A_probe_minted_index_fix_cases_gil0.txt:19-26
  - context_compass/artifacts/minted_index_registry_20261018/runs/prototype_AB_probe_minted_index_fix_cases_gil0.txt:19-26
  IMPACT: The scope question stays open; the boundary, patch docs and tests wait for the owner's answer.
  NEXT: The owner's answer on B (and on A + C).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T17:45:20Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: ALIGNMENT_CHECK
  CLAIM: The owner's question and direction (chat 2026-10-18): "so why would we ever have an index without a spell in
    it? ... by default we should have one, and our mechanisms are trying to enforce at least 1 active spell", then
    "we probably do need to have a way to have a hole available with no_active_spell and a way to manage this state
    and notify all dependencies and reliances so they revalidate ... cleaning up a spell thats actively relied on
    could then be reasonable instead of just refusing it so that is the right approach to all your issues I think
    but we need a new spellsystemstate for it and various other concepts need to overlap with this". The code's
    answer: every path keeps one active spell per index - `bind` makes its new index's spell active,
    `bind_inactive` and `add_to_spell_index` only park versions in an existing index (an emptied source is
    destroyed), a notch swaps which version is active, the three cleanup calls refuse the active member while
    parked versions remain (0.2.8256), and an index goes with its last member - except `remove_from_spell_index`,
    whose contract is that the separated version "becomes the only member of a fresh index and stays parked" (kept
    by the owner's S10 ruling: activation takes a notch). So Melder already has an index with no active spell, and
    nothing manages it: S4, S5, S7, S9 and S10 of the correctness epic are its symptoms, S1 (C4), S2 (C7) and S8 (its
    minted-index branch) in part.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:5806-5822
  - src/melder/aether/spellbook/spellbook.py:5279-5300
  - src/melder/aether/spellbook/spellbook.py:4095-4269
  - src/melder/aether/spellbook/spellbook.py:1590-1649
  - src/melder/aether/spellbook/spellbook.py:4271-4388
  - src/melder/aether/spellbook/spellbook.py:4390-4456
  - src/melder/aether/spellbook/spellbook.py:700-713
  - src/melder/aether/conduit/conduit.py:6122-6210
  - context_compass/tickets/epics/2026-10-17_correctness_defects_epic.md:94-123
  IMPACT: A managed no_active_spell state makes S4's registration (A) and teardown (B) part of one design, makes C
    unnecessary if such an index selects nothing, and replaces S9's refusal; it is an epic (the owner's rule: an
    epic and its stories before implementing) reaching SpellIndex, SpellSystemStates, the meld gate, contracts and
    index links, the record, Nexus and residency.
  NEXT: Ask the owner to open that epic, a design story first (no src); S4 waits for its outcome.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T17:54:06Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: ALIGNMENT_CHECK
  CLAIM: The owner turned the hole route down (chat 2026-10-18): "an index with no spell should only happen when you
    make it and add a spell to it on the spot so its not an issue ... I'm not exactly sure why this is a problem
    your also forgetting what melder is ... its an agentic AI runtime most things are managed by agents as inventory
    not as objects in a program". So no no_active_spell state and no epic; the previous note's NEXT is withdrawn.
    The index `remove_from_spell_index` mints is created with its version in it (`SpellIndex(initial_id=...)`), and a
    version an agent parks there is inventory it holds, active only when it notches it - nothing to manage. What S4
    is about stays: the frame's catalog of which conduit holds which index misses that index, so the agent's own
    inventory is unknown to the frame by spell_id - the conduit's spell_id lookups raise "not found in any conduit",
    a grant or a transfer by spell_id is refused, another Book may bind the same spell_id (against the identity
    epic's strict refusal of duplicates) and residency loses the version (MEASURE notes). Re-explained to the owner
    in those terms; his word is asked: fix it as A + B + C (no new state), or drop S4.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:3-54
  - src/melder/aether/spellbook/spellbook.py:4303-4388
  - context_compass/artifacts/minted_index_registry_20261018/runs/probe_minted_index_fix_cases_0_2_8256_gil0.txt:1-32
  - context_compass/artifacts/minted_index_registry_20261018/runs/probe_minted_index_registry_0_2_8256_gil0.txt:1-26
  - context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md:709-733
  IMPACT: S4 stays the narrow fix it was filed as, or is dropped on the owner's word; nothing else changes.
  NEXT: The owner's word: A + B + C, or drop S4.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T18:00:11Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's word (chat 2026-10-18). Shown the defect in one example - the conduit finds French until
    `remove_from_spell_index` moves it into an index of its own, then `get_spell_by_spell_id` raises "not found in
    any conduit" - he put it as "we're not updating the dam spellbook registry objects properly then is this the
    issue?" (yes: the frame's registry, not the Book's maps, which still answer), then: "it should properly follow
    the general spell index creation and registry binding processes the same way it does during bind yeah". So S4
    is fixed as filed, its boundary widened on his word: A - the seam registers its new index the way a
    post-conjure `bind` registers the index it creates, with bind's guard (`self._conjured and self._conduit is not
    None`) and call (`_register_single_spell_index(self._get_required_conduit_surface()._id, ...)`) - the index is
    already created as bind creates one (`SpellIndex(initial_id=...)`); B - the root's teardown unregisters it with
    the rest; C - residency reports a parked version as parked. A's draft keyed the registration on the spell's
    owner stamp; it is re-shaped to bind's guard and conduit. No new state (ALIGNMENT_CHECK notes).
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:5919-5925
  - src/melder/aether/spellbook/bind/bind.py:795-804
  - src/melder/aether/spellbook/spellbook.py:4372-4375
  - src/melder/aether/spellbook/spellbook.py:924-931
  IMPACT: The ENTRY_GATE's word on the edits is given; before the first src edit remain the patch docs, the red
    tests, spellbook.py back from melder_0 after S1 and S2 land, and mutation_research.py claimed by message.
  NEXT: Re-shape A in the lane's script, re-run the probes on the new A+B+C copy (GIL off and on), update the
    story's contract, then the patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T18:02:27Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Edit A re-shaped to the owner's word in the lane's script: the seam registers its new index with bind's
    guard (`self._conjured and self._conduit is not None`) and call (`_register_single_spell_index` under
    `self._get_required_conduit_surface()._id`), and its docstrings say so; B and C unchanged. The three probes
    re-run on fresh /tmp copies of the 0.2.8256 src with A, A+B and A+B+C (GIL off; A+B+C GIL on too): every output
    is byte-equal to the run the prototypes' MEASURE note recorded, so the re-shape changes nothing the probes see
    (in their worlds the spell's owner stamp and the Book's root conduit are one id). The preview of the three
    edits against 0.2.8256 is now 162 lines.
  EVIDENCE:
  - context_compass/artifacts/minted_index_registry_20261018/scripts/apply_s4.py:1-237
  - context_compass/artifacts/minted_index_registry_20261018/runs/s4_preview_0_2_8256_bind_guard.diff:1-162
  IMPACT: The edits to land are this preview's; the earlier preview stays as the record of the first draft.
  NEXT: Update the story's contract to the owner's word; then the patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T18:16:36Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M0-199 from melder_0 (2026-10-18T18:08:26Z, the ACK of M1-39), consumed after the re-onboarding.
    mutation_research.py is melder_1's for S4: S1 and S2 do not touch it, and melder_0 claims it back by message if
    S5's research-history step needs it. spellbook.py comes back by message the moment S1 and S2 land - notched,
    documented and rebuilt - and S4 notches above them. melder_0 recorded the bind-guard gap (M4b, M5b) as a Risk
    of EPIC-2026-10-18-spell_identity_is_the_code until edit A lands; that epic's S4 takes M4b and M5b as
    acceptance cases after this fix. M1-39 did not name spell.py, which edit D touches (a docstring), so it is
    claimed in M1-40.
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md:100-107
  - context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md:163-165
  - context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md:700-724
  IMPACT: The fix lands as one change set once spellbook.py (A, B) and spell.py (D) are handed back with S1 and
    S2's landing; mutation_research.py (C) is held meanwhile. Patch-doc links, the PLAN note and the red tests do
    not wait.
  NEXT: Send M1-40 claiming spell.py with spellbook.py; then the patch-doc links and the PLAN note.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T18:19:28Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: The patch read in the required order (architecture, Spellbook component, MutationResearch component) and
    mapped patch section -> implementation step -> validation step. No code-description patch: no state machine,
    gate pipeline, rollback or concurrency semantics change. (1) Changed components (the seam) and the Spellbook
    patch's Before/after -> edit A in `_apply_remove_from_index`: after the Book-locked move and with bind's guard,
    `Spellbook._aether._register_single_spell_index(self._get_required_conduit_surface()._id, new_index,
    self._aetheric_frame_name)`; the entry's Contract, the seam's summary, step 4 and Threading -> tests: the version
    is found by spell_id parked and notched active (frame index and conduit, both Conduit lookups), a grant and a
    transfer by spell_id proceed, a second bind of its spell_id is refused (another Book of the frame, conjured and
    not; a Book of another frame under process-wide ids), the move back drops the minted index; probes M2-M5, M7.
    (2) The teardown invariant and the Spellbook patch's teardown half -> edit B in
    `_unregister_conduit_spells_from_aether`: each parked version's index joins the set under the Book lock, read
    through `_spell_index_unless_cleaned`; Contract and Threading -> test: a torn-down root leaves no registry or
    id-set entry and its separated version's index is not found; probe M6. (3) The residency component patch ->
    edit C in `_locate_live_membership` (CRLF kept): active only when the index selects the version and
    `get_by_index_id(index.id).current_spell_id` is it (None for an index no lineage registered); the verdict text
    and the method's Contract -> tests: V2 parked, V3 active, V1 and V4 as before; two unit tests whose frame
    doubles leave the lineage unset would read parked under C and get doubles whose lineage tracks the selected
    id (`test_root_residency_view_reports_runtime_and_custody_join`,
    `test_residency_view_prefers_selected_membership_in_later_frame`), and a new unit test reads a selected version
    no lineage tracks as parked; probe V1-V4. (4) Docstrings -> edit D in `Spell._spell_index_unless_cleaned` ->
    the documentation ritual. (5) No new lock edge -> registration after the Book lock, teardown reads Book ->
    spell -> the whole tree in a /tmp mirror by shards, GIL off and on. (6) Migration 5-7 and Rollback -> system
    documents, indexes and graph, the release note, the next free notch, closure, the rebuild last; no cache
    generation or record version moves.
  EVIDENCE:
  - context_compass/system_docs/patches/active/minted_index_registry_2026_10_18/architecture_patch.md:1-72
  - context_compass/system_docs/patches/active/minted_index_registry_2026_10_18/component_patch_spellbook_minted_index_registration.md:1-60
  - context_compass/system_docs/patches/active/minted_index_registry_2026_10_18/component_patch_mutation_research_residency.md:1-36
  - context_compass/artifacts/minted_index_registry_20261018/scripts/apply_s4.py:1-258
  - tests/unit/melder/mutation_research/test_mutation_research_root.py:361-397
  - tests/unit/melder/mutation_research/test_mutation_research_root.py:439-482
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:560-576
  IMPACT: The patch gate's mapping is recorded; tests may be written now, src edits wait for the files (M1-40).
  NEXT: Read S9's integration test and the three probes for conventions, then write the red tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T18:47:35Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The regression tests, written to the PLAN note, red on 0.2.8256 and green with A-D (Python 3.14.7t, the same
    with the GIL off and on). New integration file, 12 cases: the version found by spell_id parked and notched
    active, granted by spell_id parked and active (the borrower's copy parked or active as on the lender),
    transferred by spell_id, a second bind of its spell_id refused (another Book of the frame, conjured or not; a
    Book of another frame, conjured or not), registered under its root until the root's teardown, then gone and
    bindable anew, moved back with no registered index left behind (a control), and read by residency parked, then
    active. Residency unit file: two frame doubles now track the selected id as bind and a notch register it, and one
    new case reads a selected version no lineage tracks as parked. In the repository: 11 failed, 1 passed (the
    control); the unit file 1 failed (the new case), 37 passed. In a /tmp mirror of the repository with A-D applied
    by the lane's script (byte-equal to the preview's files): both files 50 passed; the whole tree by shards - unit
    9648 passed, 3 skipped, 7 xfailed; component 2396 passed, 23 skipped, 1 xfailed; integration spellbook 669
    passed, 2 skipped, 2 xpassed; aether 823 passed, 5 xfailed; conduit 353 passed, 1 xpassed; crystallizer,
    multithreading, mutation_research and live_sim 398 passed, 4 xfailed; experimentation, experiments, tests and
    mocks 250 passed, 4 skipped - the only failures the 18 red tests held for
    STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers (7 unit, 11 integration), as at 0.2.8256. Probes at
    A-D: M1-M7 and V1-V4 byte-equal to the A+B+C prototype runs; new probe G1-G3 - a grant by spell_id of French in
    its own index gives a parked copy while French is parked and an active one once notched (the tree raises "not
    found in any conduit" for both).
  EVIDENCE:
  - tests/integration/melder/spellbook/test_separated_version_is_known_to_its_frame_integration.py:1-411
  - tests/unit/melder/mutation_research/test_mutation_research_root.py:361-403
  - tests/unit/melder/mutation_research/test_mutation_research_root.py:444-553
  - context_compass/artifacts/minted_index_registry_20261018/runs/red_tests_0_2_8256_gil0.txt:1-48
  - context_compass/artifacts/minted_index_registry_20261018/runs/red_tests_0_2_8256_gil1.txt:1-56
  - context_compass/artifacts/minted_index_registry_20261018/runs/red_unit_residency_0_2_8256_gil0.txt:1-10
  - context_compass/artifacts/minted_index_registry_20261018/runs/red_unit_residency_0_2_8256_gil1.txt:1-18
  - context_compass/artifacts/minted_index_registry_20261018/runs/full_tree_abcd/green_tests_gil0.txt:1-2
  - context_compass/artifacts/minted_index_registry_20261018/runs/full_tree_abcd/green_tests_gil1.txt:1-10
  - context_compass/artifacts/minted_index_registry_20261018/runs/full_tree_abcd/unit_gil0.txt:1-168
  - context_compass/artifacts/minted_index_registry_20261018/runs/full_tree_abcd/integ_aether_gil0.txt:1-71
  - context_compass/artifacts/minted_index_registry_20261018/probes/probe_minted_index_grants.py:1-106
  - context_compass/artifacts/minted_index_registry_20261018/runs/abcd_probe_minted_index_grants_gil0.txt:1-6
  - context_compass/artifacts/minted_index_registry_20261018/runs/abcd_probe_minted_index_fix_cases_gil0.txt:1-30
  IMPACT: The fix is proven red to green on the repository's own tests, with nothing else in the tree moving. The new
    tests stay red in the repository until A-D land with spellbook.py and spell.py back (M1-40); S1 and S2 land
    first, so the tests and the four anchors are re-checked on that tree (the collision message the rebind case
    matches, the seams' text).
  NEXT: melder_0's handover after S1 and S2 land; then re-check the anchors and apply A-D.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T18:52:07Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Prepared while spellbook.py and spell.py wait for S1 and S2's landing. (1) melder_0's S1+S2 src diff (his
    lane, 17:48Z) changes spellbook.py in seven hunks (2564-2576, 2605-2618, 2635-2643, 2851-2868, 5443-5453,
    5557-5563, 5792-5802 of 0.2.8256) and spell.py in eighteen, the nearest ending at 865; none reaches the text A,
    B or D anchor on (spellbook.py 2695-2716 and 4271-4388, spell.py 911-924), so the edits should apply unchanged.
    They are re-checked on the landed tree before applying, since the landing may differ from that diff. (2) The
    documentation is drafted - the architecture's invariant, failure mode, sequence, code map and handoff entries,
    the component entries, the tests map and the release note - to be applied after the edits, against the landed
    documents. (3) The release note's example runs as written: on 0.2.8256 the lookup of French's spell_id after
    the move raises ValueError "Spell version ... not found in any conduit."; with A-D every assert holds, GIL off
    and on.
  EVIDENCE:
  - context_compass/artifacts/spell_identity_20261018/staged/runs/mirror_s1s2_src.diff:693-916
  - context_compass/artifacts/spell_identity_20261018/staged/runs/mirror_s1s2_src.diff:1391-1529
  - src/melder/aether/spellbook/spellbook.py:2695-2716
  - src/melder/aether/spellbook/spellbook.py:4271-4388
  - src/melder/aether/spellbook/spell.py:911-924
  - context_compass/artifacts/minted_index_registry_20261018/notes/s4_docs_draft.md:1-157
  - context_compass/artifacts/minted_index_registry_20261018/probes/probe_release_note_s4.py:1-36
  - context_compass/artifacts/minted_index_registry_20261018/runs/probe_release_note_s4_repo_and_abcd.txt:1-4
  IMPACT: The landing pass is mechanical once the files come back: re-check the anchors, apply, run, docs, notch,
    closure, rebuild.
  NEXT: melder_0's handover message (the mailbox read every 30 seconds while blocked).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T18:53:03Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M0-200 from melder_0 (2026-10-18T18:40:11Z, the ACK of M1-40), consumed. spell.py comes back with
    spellbook.py in one NOTICE once S1 and S2 land - notched, documented and rebuilt. By melder_0's edit list S1 and
    S2 change spell.py in 19 places (the binding manifest and `binding_hash` on the Spell, its spell_id statements)
    and none in `_spell_index_unless_cleaned`, so edit D's anchor survives and only its line moves, as the S1+S2
    diff showed (FACT note above). mutation_research.py stays with melder_1.
  EVIDENCE: context_compass/artifacts/spell_identity_20261018/scripts/edits_spell.py:1-118
  IMPACT: Every file S4 edits has its route back; nothing more is owed to melder_0 before the handover.
  NEXT: melder_0's handover NOTICE (the mailbox read every 30 seconds while blocked).
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-18T19:12:43Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The landing pass is scripted, each part checked against the 0.2.8256 tree and documents (--check, with
    0.2.8257 standing in for the notch S4 takes). apply_s4.py now takes the notch (--notch) and writes it beside the
    patch id where its comments and docstrings named the patch alone, as S9's do ("(direct_cleanup_refusal,
    0.2.8256)"); its anchors still hold. land_s4_docs.py writes the documentation draft into the four system
    documents: section headers or short phrases melder_0's S1/S2 documentation does not reach anchor the edits,
    code-map records are found by path and remeasured from disk, and the counts S4 moves are recounted from disk
    (integration 176 of 183, spellbook tree 53, 852 in the three tiers; the S4 test file is on disk already). It
    also corrects tests_components' core count: the key-file union is 265, not the 264 it states, since S9
    (0.2.8256) added a key file without updating it - 266 with S4's. graph_prose_s4.py adds the Spellbook node's
    registration responsibility and the lineage condition to MutationResearch's residency one; release_note_s4.py
    adds the section, the packaging bullet and the rebuild line, its example run as written by
    run_release_note_block_s4.py (it raises on 0.2.8256 and holds with A-D, GIL off and on).
  EVIDENCE:
  - context_compass/artifacts/minted_index_registry_20261018/scripts/apply_s4.py:1-265
  - context_compass/artifacts/minted_index_registry_20261018/scripts/land_s4_docs.py:1-474
  - context_compass/artifacts/minted_index_registry_20261018/scripts/graph_prose_s4.py:1-69
  - context_compass/artifacts/minted_index_registry_20261018/scripts/release_note_s4.py:1-113
  - context_compass/artifacts/minted_index_registry_20261018/probes/run_release_note_block_s4.py:1-18
  - context_compass/artifacts/minted_index_registry_20261018/runs/release_note_block_s4_repo_and_abcd.txt:1-4
  - context_compass/system_docs/tests_components.md:2025-2027
  IMPACT: After the handover the pass is mechanical: re-check every anchor on the landed tree, apply A-D with the
    notch, run the tests, the whole tree and the probes, then the documents, graph, release note, notch, closure
    and the rebuild in a mirror.
  NEXT: melder_0's handover NOTICE (the mailbox read every 30 seconds while blocked).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T19:40:31Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: remap_s4_citations.py runs after A-D are applied: it rebuilds each file's pre-edit text by undoing the
    edits it reads from apply_s4.py, then maps old line numbers to new. Since apply_s4.py fills a `{notch}` placeholder
    in its new texts, the remap could no longer find the applied texts; it now takes --notch and fills the
    placeholder the same way before undoing. Checked on a /tmp root holding the three files with A-D at 0.2.8259 and
    today's two documents: spellbook.py 7802 -> 7848 lines, spell.py 1972 -> 1975, mutation_research.py 3990 -> 4005;
    9 citation lines in src_architecture and 14 in src_components remap. The landing scripts write no numeric
    citation into these three files, so the remap can run before or after land_s4_docs.py without shifting a line
    twice.
  EVIDENCE:
  - context_compass/artifacts/minted_index_registry_20261018/scripts/remap_s4_citations.py:1-133
  - context_compass/artifacts/minted_index_registry_20261018/scripts/apply_s4.py:225-265
  IMPACT: The citation step of the landing pass runs as scripted, with the notch passed as apply_s4.py takes it.
  NEXT: melder_0's handover NOTICE (the mailbox read every 30 seconds while blocked).
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-18T19:46:10Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The rebuild step is scripted too (rebuild_s4_assets.py, S9's procedure). It copies src/ and the system
    documents into a /tmp mirror, runs the asset runner there whole (its system-documents writer unlinks its
    payloads, which the connected folder refuses), and lists every file the run changed under
    src/melder/_build_assets; with --apply it writes each over its original, reads it back byte-equal and compares
    the mirror's src/ and the runner's documents with the repository's. Tried on 0.2.8256 (28 and 40 s): the runner
    reproduces the committed assets byte for byte - nothing to copy - and the trees compare equal, so the mirror
    holds everything the three builders read. The checks still run in the repository afterwards: the runner's
    --check, the LLM bundles (--include-untracked, then --check) and the runner's --check again.
  EVIDENCE:
  - context_compass/artifacts/minted_index_registry_20261018/scripts/rebuild_s4_assets.py:1-122
  - context_compass/artifacts/minted_index_registry_20261018/runs/rebuild_trial_dryrun_0_2_8256.txt:1-4
  - context_compass/artifacts/minted_index_registry_20261018/runs/rebuild_trial_apply_0_2_8256.txt:1-5
  - src/melder/_build_assets/_system_documents/_builder.py:542-626
  IMPACT: The landing's last step needs no hand copying; a run that removes a file, or a mirror gone stale, stops it.
  NEXT: melder_0's handover NOTICE (the mailbox read every 30 seconds while blocked).
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-18T23:45:34Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M0-204 from melder_0 (2026-10-18T23:43:33Z, the handover NOTICE answering M1-40), consumed. S1 and S2 of
    EPIC-2026-10-18-spell_identity_is_the_code landed and are turned in at 0.2.8257 and 0.2.8258 (`__version__`
    0.2.8258): their release-note sections, the system documents, the graph and the rebuild, both checks OK.
    spellbook.py and spell.py are melder_1's again and melder_0 holds no src file, so every file S4 edits is free;
    S4 notches above 0.2.8258. For S4's tests: one object is one spell now, so a test that needs a second
    registration of a class binds a version of it (`version_of` in tests/_spell_identity_test_support.py) or a
    class of its own. melder_0 rebuilt in a /tmp mirror and copied back byte for byte, its LLM bundles too (the
    mirror must carry the tracked src/melder/__melder_cache__/__melder_cache__.py).
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md:882-914
  - src/melder/__version__.py:12-12
  - tests/_spell_identity_test_support.py:18-21
  IMPACT: The ENTRY_GATE's last condition is met; the landing pass starts on the landed tree: re-check every
    script's anchors and the S4 tests, tell the owner, then apply A-D.
  NEXT: Re-sync the /tmp mirror to 0.2.8258, re-check the landing scripts and run the S4 tests on the tree (red).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T23:50:10Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Edits A-D are in the repository, on the 0.2.8258 tree melder_0 handed back (M0-204), as the owner approved
    them (owner told first, chat): apply_s4.py with the notch S4 takes, 0.2.8259, written beside the patch id in the
    comments and docstrings; every anchor found once; spellbook.py and spell.py LF, mutation_research.py CRLF kept
    (4005 lines, all CRLF); the three files byte-equal to the /tmp mirror's. The landed diff is 182 lines. Before it,
    every landing script was re-checked on 0.2.8258: apply_s4.py, land_s4_docs.py (counts from disk: integration 176
    of 183, the spellbook tree 53, the three tiers 857), release_note_s4.py, graph_prose_s4.py and close_s4.py
    --check, and remap_s4_citations.py on a /tmp root (9 and 14 citation lines). The S4 tests on the 0.2.8258 tree
    before A-D: 12 failed, 38 passed, GIL off and on - the same cases and reasons as on 0.2.8256; in the mirror with
    A-D: 50 passed, GIL off and on.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:2695-2736
  - src/melder/aether/spellbook/spellbook.py:4290-4435
  - src/melder/aether/spellbook/spell.py:963-1004
  - src/melder/mutation_research/mutation_research.py:1374-1541
  - context_compass/artifacts/minted_index_registry_20261018/runs/apply_s4_repo_0_2_8259.txt:1-4
  - context_compass/artifacts/minted_index_registry_20261018/runs/s4_landed_0_2_8258_abcd.diff:1-182
  - context_compass/artifacts/minted_index_registry_20261018/runs/red_s4_0_2_8258_gil0.txt:1-54
  - context_compass/artifacts/minted_index_registry_20261018/runs/red_s4_0_2_8258_gil1.txt:1-62
  - context_compass/artifacts/minted_index_registry_20261018/runs/green_s4_mirror_0_2_8259_gil0.txt:1-2
  - context_compass/artifacts/minted_index_registry_20261018/runs/green_s4_mirror_0_2_8259_gil1.txt:1-10
  IMPACT: The fix is in src; the version is still 0.2.8258 until the notch, which follows the validation and the
    documents in the contribution guide's turn-in order.
  NEXT: The whole tree by shards in the mirror, GIL off and on; then the probes M1-M7, V1-V4, G1-G3 and the release
    note's block.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-19T00:00:59Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Validated with A-D on the 0.2.8258 tree (Python 3.14.7t; the /tmp mirror byte-equal to the repository's
    src/ and tests/; the same counts with the GIL off and on). The S4 tests: 50 passed. The whole tree by shards:
    unit 9691 passed, 3 skipped, 7 xfailed; component 2403 passed, 23 skipped, 1 xfailed; integration spellbook 670
    passed, 2 skipped, 2 xpassed; aether 823 passed, 5 xfailed; conduit 353 passed (its open notch-race test,
    marked intermittent, xfailed in one run and xpassed in the others); crystallizer, multithreading,
    mutation_research and live_sim 398 passed, 4 xfailed; experimentation, experiments, tests and mocks 250 passed,
    4 skipped - the only failures the 18 red tests held for
    STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers (7 unit, 11 integration), as at 0.2.8256. Probes on
    the repository: M1-M3, V1-V4 and G1-G3 byte-equal to the A-D runs at 0.2.8256; M4-M7 equal but for its eight
    refusals, which now carry S1's wording ("Spell ID collision detected: this object is already registered as
    spell_id ...") and are refused all the same. The release note's example: every assert holds, GIL off and on.
  EVIDENCE:
  - context_compass/artifacts/minted_index_registry_20261018/runs/full_tree_0_2_8259/unit_gil0.txt:1-168
  - context_compass/artifacts/minted_index_registry_20261018/runs/full_tree_0_2_8259/unit_gil1.txt:1-176
  - context_compass/artifacts/minted_index_registry_20261018/runs/full_tree_0_2_8259/integ_aether_gil0.txt:1-71
  - context_compass/artifacts/minted_index_registry_20261018/runs/full_tree_0_2_8259/integ_aether_gil1.txt:1-79
  - context_compass/artifacts/minted_index_registry_20261018/runs/full_tree_0_2_8259/integ_conduit_gil0.txt:1-6
  - context_compass/artifacts/minted_index_registry_20261018/runs/full_tree_0_2_8259/integ_rest_gil1.txt:1-15
  - context_compass/artifacts/minted_index_registry_20261018/runs/landed_0_2_8259_probe_minted_index_fix_cases_gil0.txt:1-30
  - context_compass/artifacts/minted_index_registry_20261018/runs/landed_0_2_8259_probe_minted_index_registry_0_2_8256_gil0.txt:1-26
  - context_compass/artifacts/minted_index_registry_20261018/runs/landed_0_2_8259_probe_research_residency_moves_0_2_8256_gil0.txt:1-13
  - context_compass/artifacts/minted_index_registry_20261018/runs/landed_0_2_8259_probe_minted_index_grants_gil0.txt:1-6
  - context_compass/artifacts/minted_index_registry_20261018/runs/release_note_block_s4_landed_0_2_8259.txt:1-2
  IMPACT: The exit gate's tests and probes hold on the landed tree; what remains is documentation, the notch, the
    closure and the rebuild.
  NEXT: The system documents (land_s4_docs.py, the citation remap, the four indexes), then the graph.
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
- Scope: the index `remove_from_spell_index` mints is registered in the frame's spell registry as `bind` registers
  the index it creates, unregistered at the root's teardown with the rest, and residency reads its version parked
  (Requirements; widened on the owner's word). Defect proven on 0.2.8251 and re-verified on 0.2.8256 (Notes);
  probes and runs in Artifact Links.
- State: in_progress (melder_1), implementation. The owner's word is given (DECISION note of
  2026-10-18T18:00:11Z): A follows bind's registration (guard and call), with B and C, and D a docstring; no new
  index state (ALIGNMENT_CHECK notes). The patch docs are linked (Artifact Links) and mapped to steps and tests
  (PLAN note). The regression tests are in the repository: red on 0.2.8256, green with A-D in a /tmp mirror whose
  whole tree passes but for S8's 18 held red tests, GIL off and on (MEASURE note); the edits to land are
  runs/s4_preview_0_2_8256_abcd.diff in the lane folder. No src edit yet: spellbook.py and spell.py come back
  from melder_0 when S1 and S2 of EPIC-2026-10-18-spell_identity_is_the_code land (M0-199, M1-40);
  mutation_research.py is held.
- Next: (1) melder_0's handover; then re-check A-D's anchors and the tests on the landed tree and apply A-D;
  (2) the tests green in the repository, the whole tree in a mirror and the probes, GIL off and on; (3) system
  documents with their indexes and the graph, the release note, the next free notch, closure, the rebuild last,
  the files handed back. Steps (1) and (3) are scripted in the lane folder (apply_s4.py, land_s4_docs.py,
  graph_prose_s4.py, release_note_s4.py, remap_s4_citations.py, close_s4.py, rebuild_s4_assets.py; FACT notes
  of the landing scripts, the remap's notch and the rebuild script).

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
