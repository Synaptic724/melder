# Story: staged_version_releases_active_signature - staging, moving or disposing a version keeps other signatures

- Completed: 2026-10-19T14:25:39Z
- Summary: landed and notched 0.2.8263 - staging a version keyed like the active one, an index move back and a
  lone parked `cleanup_spell` keep every other spell's binding signature: `Spellbook._destroy_spell_index` drops
  the Book route only when it routes the key to the destroyed index and releases only the departing member's frame
  claim, by spell_id. Six component tests (five red on 0.2.8262) green with the GIL off and on, the whole tree as
  the MEASURE note records; release-note section "Staging a version keeps the active version's name"; system
  documents and graph; the rebuild comes last in this pass. Turned in on the owner's word (chat 2026-10-19: "Yes
  do your fix", "But finish asap").

## Metadata
- Story ID: STORY-2026-10-17-staged_version_releases_active_signature
- Epic: EPIC-2026-10-17-correctness_defects
- Status: done
- Owner: user
- Agent Name: melder_1
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-17T20:23:51Z
- Updated: 2026-10-19T14:25:39Z

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
- FAILURE_ESCALATION: CONFLICT if the holder of spellbook.py is mid-change in the seam. Staging stays open to any
  key (DECISION note of 2026-10-17T21:55:46Z).

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
- from_state: in_progress
- to_state: done
- transition_reason: landed at 0.2.8263 and turned in on the owner's word (chat 2026-10-19: "Yes do your fix",
  "But finish asap"; MEASURE and FACT notes). Before that, ready -> in_progress on his order (DECISION note).

## Dependencies / Related Work
- STORY-2026-10-17-notch_moves_signature_by_incoming_key_only (the same frame claims; the notch's seam).
- `Spellbook.cleanup_and_remove_spell` already releases by spell_id, for this very reason (spellbook.py:716-729).

## Tasks (Implementation Checklist)
- [x] Task: patch docs for the seam (staged_signature_claims_2026_10_19); the owner's go (chat 2026-10-19:
  "Yes do your fix").
- [x] Task: the fix with symptom-named regression tests (red on 0.2.8262, green at 0.2.8263), docs, notch
  0.2.8263; the rebuild follows the closures of this pass.
- [x] Enforce Ticket Microcycle across all linked tasks.
- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

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
  Settled (2026-10-17T21:55:46Z) by the owner's answer on STORY-2026-10-17-notch_moves_signature_by_incoming_key_only:
  the minimal fix - staging stays open to any key (DECISION note).

## Decision Log
- 2026-10-17T20:23:51Z: filed under EPIC-2026-10-17-correctness_defects from sweep A1 (Notes).
- 2026-10-17T21:55:46Z: the open question settled by the owner's answer on the notch-signature story: the minimal
  fix (DECISION note).
- 2026-10-19T13:40:29Z: scheduled for melder_1 on the owner's order, after S8 (DECISION note).
- 2026-10-19T14:25:39Z: landed at 0.2.8263 and turned in on the owner's word (MEASURE and FACT notes).

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/correctness_defects_20261017/probes/probe_signature_claims.py (cases C1-C4, C6)
  - artifacts/correctness_defects_20261017/runs/probe_signature_claims_gil0.txt
  - artifacts/correctness_defects_20261017/runs/probe_signature_claims_gil1.txt
  - artifacts/correctness_defects_20261017/probes/probe_restore_staged_structure.py (case R1: every restore of a staged world; FACT note)
  - artifacts/correctness_defects_20261017/runs/probe_restore_staged_structure_gil0.txt
  - artifacts/correctness_defects_20261017/runs/probe_restore_staged_structure_gil1.txt
  - artifacts/correctness_defects_20261017/probes/probe_graft_parked_members.py (case G4: every graft of such an index; FACT note)
  - artifacts/correctness_defects_20261017/runs/probe_graft_parked_members_gil0.txt
  - artifacts/correctness_defects_20261017/runs/probe_graft_parked_members_gil1.txt
  - artifacts/staged_signature_claims_20261019/ (melder_1's lane: re-runs, scripts, notes)
  - system_docs/patches/completed/staged_signature_claims_2026_10_19/ (the patch, archived at turn-in)
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

- DATETIME: 2026-10-17T21:47:06Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The defect hits grafts too (sweep A12, probe G4). A graft parks every non-selected member through
    `Conduit.bind_inactive` onto the index its anchor bind created, so grafting an index whose parked member shares
    the active member's signature leaves the host frame with no claim for it: after the graft the host holds English
    active, French parked, and the claim for ('greeter', 'english') is gone. Identical with the GIL off and on.
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader_system/graft_runner.py:432-489
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_graft_parked_members.py:1-152
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_graft_parked_members_gil0.txt:20-25
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_graft_parked_members_gil1.txt:20-25
  IMPACT: The fix's tests should include one graft beside the restore.
  NEXT: The owner schedules the story.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-17T21:55:46Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The open question follows from the owner's answer on
    STORY-2026-10-17-notch_moves_signature_by_incoming_key_only (chat 2026-10-17: one SpellIndex can hold versions
    with different binding signatures). A parked version claims no signature, so staging stays allowed for any key,
    C6 included, and this story takes the minimal fix: stop releasing claims that belong to other spells. If C6's
    version is later notched active while Book O's spell holds the key, that story's notch refusal stops it. Drawn
    by melder_0 from the owner's answer and told to him; his word overrides.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-17_staged_version_releases_active_signature_story.md:97-101
  - context_compass/tickets/stories/2026-10-17_notch_moves_signature_by_incoming_key_only_story.md:40-46
  - src/melder/aether/spellbook/spellbook.py:4192-4237
  IMPACT: No open question remains here; the execution boundary stays `_destroy_spell_index` and its callers.
  NEXT: The owner's scheduling, after melder_1 releases spellbook.py.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-19T13:40:29Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's order puts this story with melder_1 now. He lifted S8's hold with "melder_1 fixes S8, then S1,
    S2 and S5, one at a time" (M1-45, M1-46), and after S8 landed and was turned in he said "So if you know how to
    implement try doing a few small ones you have space" (chat 2026-10-19). S1 is the smallest: one seam,
    `Spellbook._destroy_spell_index`, and the arguments its two callers pass. melder_0 has departed and handed
    every file to melder_1 (M0-211), so spellbook.py needs no claim. Before any src edit: the defect is re-verified
    on 0.2.8262 (the probe of 2026-10-17 calls `find_spell_by_id`, gone since 0.2.8253, so it is rewritten for the
    current names), the seam is re-read whole, the patch is written and linked, and the regression tests are red.
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-17_correctness_defects_epic.md:1147-1169
  - context_compass/tickets/epics/2026-10-17_correctness_defects_epic.md:1223-1239
  - src/melder/aether/spellbook/spellbook.py:4654-4699
  IMPACT: The ENTRY_GATE's scheduling and assignment are met and the board row exists; the patch and the red tests
    remain before the first src edit.
  NEXT: Re-run the claims cases (C1-C4, C6, rewritten for 0.2.8262) with the GIL off and on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-19T14:25:39Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Re-verified, fixed and proven. On 0.2.8262 the claims cases, rewritten for the current names, reproduce
    every one with the GIL off and on: after `bind_inactive` (after and before conjure), an index move back and a
    lone parked `cleanup_spell` the active English holds no frame claim and no Book route, a meld by address raises
    KeyError, `find_spell_index` raises and another Book's bind of the signature is accepted; Book L's staging
    releases Book O's claim (C6). The six component tests are red on 0.2.8262 (5 failed, 1 passed, both modes). The
    fix (patch staged_signature_claims_2026_10_19): `_destroy_spell_index` takes the departing member's spell_id,
    pops `_lookup_spells[key]` only when it is the destroyed index and calls `release_lookup_by_spell_id` instead of
    `release_lookup`; `_apply_add_to_index` and `_dispose_spell` pass it. At the fix: 6 passed with the GIL off and
    on; the cases keep English's claim, route and address melds and refuse the other Book's bind; the release-note
    example runs OK in both modes and raises KeyError on 0.2.8262. Whole tree on 0.2.8263, both modes: unit
    4553 + 2899 + 610 + 537 passed and 1102 passed with one expected failure (assets stamped 0.2.8260 until the
    rebuild); component 2412 passed, 23 skipped, 1 xfailed; integration 846 + 1031 (3 xpassed: a non-strict race
    marker) + 398 passed; experimentation 250 passed. One gil1 failure in the spellbook unit shard was the two
    modes racing on one conjure-cache file in the shared tree (run concurrently); its file re-run alone passes.
    Not run: melder_0's restore (R1) and graft (G4) probes at the fix - both stage through `bind_inactive`, the
    path the tests cover.
  EVIDENCE:
  - context_compass/artifacts/staged_signature_claims_20261019/probes/probe_claims_current.py:1-224
  - context_compass/artifacts/staged_signature_claims_20261019/runs/probe_claims_0_2_8262_gil0.txt:1-26
  - context_compass/artifacts/staged_signature_claims_20261019/runs/probe_claims_fix_0_2_8263_gil0.txt:1-26
  - context_compass/artifacts/staged_signature_claims_20261019/runs/s1_red_0_2_8262_gil0.txt:1-12
  - context_compass/artifacts/staged_signature_claims_20261019/runs/s1_green_gil0.txt:1-2
  - src/melder/aether/spellbook/spellbook.py:4655-4732
  - src/melder/aether/spellbook/spellbook.py:4558-4653
  - src/melder/aether/spellbook/spellbook.py:4964-5132
  - tests/component/melder/spellbook/test_spellbook_component_staged_version_keeps_active_signature.py:1-380
  - context_compass/artifacts/staged_signature_claims_20261019/runs/release_note_probe_s1_gil0.txt:1-1
  - context_compass/artifacts/staged_signature_claims_20261019/runs/release_note_probe_s1_on_0_2_8262_gil0.txt:1-2
  IMPACT: Every acceptance criterion holds on the tree: the active version keeps its claim and route through
    staging, a move back and a lone parked disposal, and another Book's claim survives a staging under its key.
  NEXT: The FACT note on the landing; then the turn-in and the rebuild last.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-19T14:25:39Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Landed and turned in at 0.2.8263 (`__version__` read 0.2.8262). The patch (architecture and Spellbook
    component docs) was written and linked before the src edit and is archived with the completed patches. The four
    system documents carry it - src_architecture an operational invariant, a fixed failure mode, the spellbook.py
    code map (8378 lines) and a handoff entry; src_components Spellbook Core's invariant and failure, the code map
    and a handoff entry; tests_components the cluster's key file, a code-map record and the counts (component 169
    of 171, 861 test modules, core union 279); tests_architecture the inventory - with their indexes regenerated
    and checked OK, and eight numeric citations into spellbook.py remapped line by line (the citation check finds
    only its two pre-existing misses). The graph: Spellbook gains a responsibility and is accepted after reading;
    re-extracted after the notch and reassembled (593 sections, check OK). The running release note gains "Staging
    a version keeps the active version's name" and a packaging bullet; the attention board a notch notice.
  EVIDENCE:
  - context_compass/artifacts/staged_signature_claims_20261019/runs/land_s1_docs_apply.txt:1-6
  - context_compass/artifacts/staged_signature_claims_20261019/runs/remap_s1_citations_apply.txt:1-40
  - context_compass/artifacts/staged_signature_claims_20261019/runs/index_check_src_architecture.txt:1-1
  - context_compass/artifacts/staged_signature_claims_20261019/runs/citation_bounds_s1.txt:1-2
  - context_compass/artifacts/staged_signature_claims_20261019/runs/graph_accept_0_2_8263.txt:1-5
  - context_compass/artifacts/staged_signature_claims_20261019/runs/graph_assemble_check_after_notch_0_2_8263.txt:1-3
  - context_compass/artifacts/staged_signature_claims_20261019/runs/notch_0_2_8263.txt:1-2
  - release_docs/next_version_release.md:1-1
  IMPACT: S1 is done; the rebuild (assets and bundles for 0.2.8263) is the pass's last write.
  NEXT: none for S1; S2 and S5 on the owner's word.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-19T14:29:14Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Rebuilt last for 0.2.8263, for this pass (S3 at 0.2.8261, S8 at 0.2.8262, S1 at 0.2.8263; the assets were
    stamped 0.2.8260). The asset runner ran in a /tmp mirror (it unlinks payloads, which the connected folder
    refuses) - agent documentation, bind guard (630 entries) and system documents at v0.2.8263 - and the eight
    changed files were copied back byte-equal; the mirror's src/ and documents equal the repository's. In the
    repository: the runner's --check OK for all three assets; llm_support/_builder.py --include-untracked rewrote
    src (585 files), tests (1143) and other (409), its --check OK for all three; the runner's --check OK again;
    `test_package_version_metadata.py` passes (4). No .git/index.lock.
  EVIDENCE:
  - context_compass/artifacts/staged_signature_claims_20261019/runs/rebuild_assets_0_2_8263_mirror.txt:1-15
  - context_compass/artifacts/staged_signature_claims_20261019/runs/rebuild_asset_check_0_2_8263.txt:1-3
  - context_compass/artifacts/staged_signature_claims_20261019/runs/rebuild_llm_0_2_8263.txt:1-4
  - context_compass/artifacts/staged_signature_claims_20261019/runs/rebuild_llm_check_0_2_8263.txt:1-3
  - context_compass/artifacts/staged_signature_claims_20261019/runs/rebuild_asset_check_after_llm_0_2_8263.txt:1-3
  IMPACT: Nothing is owed for S1, S8 or S3 but the owner's signed commit.
  NEXT: none.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Closure Confirmation
- [x] Work walkthrough shared with user (the landing report, chat 2026-10-19, sent with this turn-in)
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
- Scope: staging, moving or disposing a parked version leaves every other spell's binding signature and Book route
  in place (Requirements). Defect proven on 0.2.8251 (Notes); probe and runs in Artifact Links.
- State: done (melder_1): landed at 0.2.8263 and turned in on the owner's word (MEASURE and FACT notes); in
  tickets/stories/completed/. The rebuild for 0.2.8263 is the pass's last write.
- Next: none. Related, open: STORY-2026-10-17-notch_moves_signature_by_incoming_key_only (the notch's own
  signature handling) and STORY-2026-10-17-restore_drops_separated_parked_version.

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
