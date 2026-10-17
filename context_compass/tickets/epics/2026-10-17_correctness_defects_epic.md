# Epic: correctness_defects - structure Melder records wrong or leaves stuck

## Metadata
- Epic ID: EPIC-2026-10-17-correctness_defects
- Status: in_progress
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-17T20:11:34Z
- Updated: 2026-10-17T21:01:21Z
- Target Window: 2026-Q4
- Related Program/Initiative: Melder runtime correctness (the owner's direction, chat 2026-10-17)

## Problem / Opportunity
The owner asked for a hunt for correctness defects (chat 2026-10-17): "start looking up for more correctness stuff
but remember melder_1 is active in the system and please keep the understanding of what we talked about earlier
front and center and if you find a bug just make a generic epic to cover this and add a story for each one please".
This epic is that generic container: the sweep is recorded here, and every confirmed defect gets its own story with
a reproducer and the source range of the failing logic. Fixes are separate lanes the owner schedules.

## MRP Alignment (Most Reasonable Product)
Melder is a runtime agents live and build in, not a DI container, and its structure is the contract: bindings,
spell indexes and their versions, which conduit owns which spell, contracts and links, lineage and clusters,
verdicts, and the record the Crystallizer keeps of them. A defect is structure that is wrong or stuck. Finding
those, and only those, keeps the core trustworthy without judging Melder by rules it does not follow.

## Ticket Contract
- ENTRY_GATE: the owner's direction and the rulings that define a defect recorded (DECISION note); the active board
  row; the sweep plan (PLAN note); melder_1's open lane named and excluded.
- EXECUTION_BOUNDARY: read-only on src/ and tests/; probes and runs under artifacts/correctness_defects_20261017/;
  one story per confirmed defect in tickets/stories/ (ready; the owner schedules its fix). No src/ edit here: a fix
  opens its own lane on the owner's word, with the patch gate. Nothing in melder_1's lane
  (TASK-2026-10-16-recheck_contract_consumers_when_provider_changes): the spell_id -> index -> active-spell swap and
  its six origins, contracts versus transfers, the binding-key gap on the transfer flip, the contract notification
  route; nor the backlog tasks already filed (TASK-2026-10-16-investigate_lent_consumer_provider_loss,
  TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout,
  TASK-2026-10-16-notch_seam_checks_incoming_before_parking).
- DEPENDENCIES: src_architecture "What Melder Is" and "Runtime Model: Structure Is the Contract"; the owner's rulings
  recorded in melder_1's ticket (the spell_id lookup rule, the sharing rule, the notification model).
- EXIT_GATE: every planned area swept and recorded (a defect filed, or checked with the reason it is not one); each
  defect story carries a reproducer run with the GIL off and on and the source range of the failing logic; the
  owner's disposition of the epic; board sync.
- FAILURE_ESCALATION: DECISION_REQUEST when the intended behaviour is unclear - asked, never called a bug; CONFLICT
  when a finding falls in melder_1's lane - sent to melder_1 by mailbox, not filed here.

## Goals (Outcomes)
- Defects where structure is wrong or stuck, each a story the owner can schedule.
- A record of what was swept and why the rest is not a defect, so the next hunt starts past it.

## Non-Goals (Explicit Exclusions)
- DI-container judgments: one live instance per type, every object torn down with its scope, the newest version
  replacing the old. Old versions alive, objects left pending after a transfer or a contract change, and borrowers
  rebuilding after a notch are features.
- Userland objects: Melder does not dispose an object because something else changed.
- Fixes, and any src/ edit.
- Doc-versus-source polish (EPIC-2026-09-27-defect-hunting).
- melder_1's lane and the backlog tasks named in the Ticket Contract.

## Scope Boundaries
- In scope: the structure the runtime records and gates - bind and bind_inactive, the notch, the index moves,
  cleanup_spell, owner stamps, links and contracts outside melder_1's lane, lineage and clusters, verdicts
  (SpellSystemStates, RiskManager), the Crystallizer record and its restore, MutationResearch residency, Nexus
  publication of that structure.
- Out of scope: everything under Non-Goals.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the owner's direction (chat 2026-10-17); the sweep starts with its plan recorded (PLAN note).

## Success Metrics
- Each defect reproduces on the current tree from a probe in the artifacts folder.
- No story files behaviour the rulings call a feature.

## Requirements (Functional + Non-Functional)
- Every claim cites the source range covering the logic it describes, read whole; a search hit is not evidence.
- Each defect names the ruling or contract it breaks and what the structure should be instead.
- Probes import src/ read-only, write only under the artifacts folder, and run with the GIL off and on.

## Constraints / Assumptions
- melder_1 is active and holds its rule-2 files; nothing here writes them.
- Device runs: `. ~/.melder_env`, TMPDIR under /tmp, each call under 180 s.

## Dependencies / External References
- context_compass/system_docs/src_architecture.md (What Melder Is; Runtime Model; Operational Invariants)
- context_compass/tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md

## Milestones (Track Progress)
- [x] Milestone 1: sweep plan recorded - areas, order, exclusions (PLAN note).
- [x] Milestone 2: areas swept - each recorded as a defect or as checked with its reason.
- [ ] Milestone 3: a story per confirmed defect; the owner told what was found.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-10-17-staged_version_releases_active_signature - staging, moving or
  disposing a parked version drops the binding signature of the active spell keyed like it (sweep A1).
- [ ] Story: STORY-2026-10-17-notch_moves_signature_by_incoming_key_only - a notch moves signatures by the
  incoming key alone: a parked version keeps its claim, or an active spell's key is taken (sweep A1).
- [ ] Story: STORY-2026-10-17-parked_cleanup_leaves_borrower_copies - cleanup_spell of a parked version leaves
  its copy and id with index-link borrowers, past their own unlink (sweep A2).
- [ ] Story: STORY-2026-10-17-minted_index_missing_from_frame_registry - the index remove_from_spell_index
  mints is missing from the frame's spell registry, so its version is unknown by spell_id (sweep A3).
- [ ] Story: STORY-2026-10-17-restore_drops_separated_parked_version - a restore drops a parked version
  alone in its own index and still reports complete (sweep A5).

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- The planned areas are swept and recorded; every confirmed defect has a story with its evidence; the owner has
  dispositioned the epic.

## Risks / Mitigations
- Calling a feature a bug: each finding is checked against the rulings and its code path read whole; unclear intent
  goes to the owner as a question.
- Overlap with melder_1: its ticket is read before each filing; a finding in its lane goes to it by mailbox.
- A probe that writes outside its folder: probes run from the artifacts folder with src/ on sys.path only.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Each probe runs with `-X gil=0` and `-X gil=1`; each story's validation plan names a symptom-named regression test.

## Rollout / Adoption Plan
- Stories go to the owner; each fix is its own lane with the patch gate, its notch and the rebuild.

## Open Questions
- none yet.

## Decision Log
- 2026-10-17T20:11:34Z: opened on the owner's direction (DECISION note).
- 2026-10-17T20:24:15Z: sweep A1 filed STORY-2026-10-17-staged_version_releases_active_signature and
  STORY-2026-10-17-notch_moves_signature_by_incoming_key_only (MEASURE note).
- 2026-10-17T20:29:03Z: sweep A2 filed STORY-2026-10-17-parked_cleanup_leaves_borrower_copies (MEASURE note).
- 2026-10-17T20:32:42Z: sweep A3 filed STORY-2026-10-17-minted_index_missing_from_frame_registry (MEASURE note).
- 2026-10-17T20:36:54Z: sweep A4 checked, no story; sweep A5 filed
  STORY-2026-10-17-restore_drops_separated_parked_version (MEASURE note).

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/correctness_defects_20261017/ (probes, runs, notes, scripts)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: at closure the folder stays as the sweep's evidence; each defect's reproducer is rowed under its
  story as well

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - correctness defects in the structure Melder records and gates
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose; created 2026-10-17T20:11:34Z; evidence in Notes.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-17T20:11:34Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's direction (chat 2026-10-17), quoted under Problem / Opportunity: hunt for correctness defects,
    remember melder_1 is active, keep the earlier understanding front and center, one generic epic and a story per
    bug. What counts as a defect is the owner's: Melder is a runtime agents live and build in; structure is the
    contract; versions coexist and a notch only moves which one is active; borrowers follow; objects keep what
    they were built with; a transfer hands over stewardship; Melder does not police userland objects; a defect is
    structure that is wrong or stuck; read the code path before calling a bug and ask when the intent is unclear;
    bind_inactive behaves the same before and after conjure. Recorded in melder_1's ticket on 2026-10-17: a lookup
    by spell_id returns the spell that owns it, active or parked, or nothing - never the index's active spell;
    sharing an index follows its active spell, sharing a spell by id is exactly that spell; contract rows carry no
    active/inactive state; SpellSystemStates has nothing to do with contracts - a contract change notifies the
    impacted spells, which then run their resolution. melder_1 owns the swap's fix and the contract and transfer
    items; this epic files nothing there.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:3-54
  - context_compass/system_docs/src_architecture.md:1195-1215
  - context_compass/tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md:1854-1881
  - context_compass/tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md:1988-2010
  - context_compass/tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md:2063-2083
  - context_compass/tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md:2085-2112
  IMPACT: A finding is filed only when it breaks one of these; a finding inside melder_1's lane goes to melder_1.
  NEXT: Sweep A1 (PLAN note).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-17T20:11:34Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: The sweep, in this order; each area read whole from its public verb down to every structure it writes,
    then probed where reading leaves a doubt:
    A1 bind_inactive before and after conjure - does a version staged before conjure end in the same structure as
       one staged after (lineage state and verdicts, the owner stamp, the Crystallizer record, MutationResearch's
       staged event, Nexus publication, index-link borrowers)? By the owner's rule any difference is a defect.
    A2 cleanup_spell of a parked version - does every structure that holds it let it go (the Book's maps, its
       index, SpellSystemStates, the record, research residency, a borrower's copy through an index link)?
    A3 the index moves - add_to_spell_index, remove_from_spell_index and the fresh index remove mints: do the
       record, the registry and every index-link borrower follow the member?
    A4 the notch's records - the Crystallizer's selection, MutationResearch's promoted event, Nexus's published
       active version.
    A5 restore and graft of a world with parked versions and index moves - does the rebuilt structure equal the
       recorded one?
    Out: melder_1's lane and the three backlog tasks the Ticket Contract names.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:948-1011
  - context_compass/system_docs/src_architecture.md:1195-1215
  IMPACT: The sweep starts where the owner's rulings are sharpest (staged versions, removal, index moves).
  NEXT: Read Spellbook.bind_inactive and SpellbookCreationSystem.define_conduit_into_spells whole, then every
    structure each writes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-17T20:18:06Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: HYPOTHESIS
  CLAIM: Sweep A1, read whole: staging a version can strip the binding signature of the active spell that shares
    its key. `bind_inactive` lets Bind mint a throwaway index for the new version, then folds the version onto the
    caller's index with `_apply_add_to_index`, which destroys the emptied throwaway through `_destroy_spell_index`
    with the staged version's key. That seam pops `_lookup_spells[key]` and calls `release_lookup(key)`, both by
    key, whoever holds it - and a parked version shares its key with its active sibling (the comment in
    `cleanup_and_remove_spell` says so, and releases by spell_id for that reason). Same seam, same key: an index
    move that empties a parked-only index (one `remove_from_spell_index` minted) and `cleanup_spell` of a parked
    version whose index empties. Expected effect: the frame's one-active-spell-per-signature claim is gone while
    the active version still serves, so another bind of the signature anywhere in the frame is accepted, and the
    Book's address lookups (`meld(spellframe=..., binding_name=...)`, `find_spell_index`) miss the active version.
    Second seam: `_apply_notch` repoints only the incoming version's key (`update_lookup`, unconditional), so
    versions with different keys leave the outgoing key claimed by a parked spell, and the incoming key is taken
    even when another active spell holds it. To be proven on the running code before anything is filed.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:5243-5498
  - src/melder/aether/spellbook/spellbook.py:4096-4237
  - src/melder/aether/spellbook/spellbook.py:4422-4563
  - src/melder/aether/spellbook/spellbook.py:716-729
  - src/melder/aether/spellbook/spellbook.py:1500-1621
  - src/melder/aether/spellbook/spellbook.py:3906-4061
  - src/melder/aether/spellbook/spellbook.py:5766-5782
  - src/melder/aether/aetheric_frame/lookup_container.py:5-274
  - src/melder/aether/aetheric_frame/aetheric_frame.py:1064-1112
  - src/melder/aether/conduit/meld/meld.py:303-303
  - src/melder/aether/conduit/meld/meld.py:2188-2270
  - src/melder/aether/spellbook/spellbook.py:2334-2384
  IMPACT: If it holds, it is structure wrong - a signature claim lost, or kept by a parked spell - on the loop the
    owner describes: stage a version, try it, notch.
  NEXT: Probe it in fresh worlds with the GIL off and on: the claim and the address lookups before and after
    bind_inactive (after and before conjure), an index move, a parked cleanup_spell and a notch across keys.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-17T20:20:59Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The hypothesis holds on 0.2.8251, proven in fresh worlds (seven cases, identical with the GIL off and on,
    ids masked). C1: after `bind_inactive(French)` keyed like the active English, the frame holds no claim for
    ('greeter', 'greeter'), the Book's address map no longer routes it, `find_spell_index` raises "Spell not found
    in the spellbook.", and another Book's `bind` of the same signature is ACCEPTED while English stays active - two
    active spells with one signature in the frame (a meld by address made before the staging still served English).
    C2, the same before conjure: after conjure the first `meld(spellframe=Greeter, binding_name='greeter')` raises
    KeyError "[MELD] No spell found ...". C3: `remove_from_spell_index` keeps the claim; `add_to_spell_index` back
    drops it. C4: `cleanup_spell` of the version alone in its minted index drops it. C6: staging in Book L a version
    keyed like Book O's active spell drops O's claim, and a third Book binds that signature. Second seam: C5, after
    a notch from English to a version under another key, the parked English still holds ('greeter', 'greeter'), so
    a new bind of it is refused naming English; C7, a notch inside the index `remove_from_spell_index` minted gives
    French the signature English still holds active, and the next meld by address raises SpellbookValidationError
    [DUPLICATE_SPELL_NAME].
  EVIDENCE:
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_signature_claims.py:1-278
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_signature_claims_gil0.txt:1-91
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_signature_claims_gil1.txt:1-91
  - src/melder/aether/spellbook/spellbook.py:4192-4237
  - src/melder/aether/spellbook/spellbook.py:3966-3978
  IMPACT: Two defects by the owner's definition (structure wrong or stuck): one seam (`_destroy_spell_index`)
    drops a claim it never held, the other (`_apply_notch` step 4) moves claims by the incoming key alone. Neither
    is in melder_1's lane; both fixes sit in spellbook.py, which melder_1 holds.
  NEXT: File one story for each seam under this epic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-17T20:24:49Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Sweep A1 is done. Apart from the signature defects (the same before and after conjure, now two stories), a
    version staged before conjure ends in the structure one staged after gets: the owner stamp (conjure walks
    `_inactive_spells` with the stamp a post-conjure `bind_inactive` gives, 0.2.8248), no lineage registration or
    verdict (neither path calls `register_index` for a parked version), the same record and research entries (one
    code path in `bind_inactive`, gated only on the roots being active), no Nexus record (parked versions are never
    published). One surface difference is not filed here: after conjure, `Conduit.bind_inactive` sends the new member
    to index-link borrowers (`_emit_index_member_added`) and a direct `Spellbook.bind_inactive` does not, as a direct
    `Spellbook.cleanup_spell` skips the index-destroy emission `Conduit.cleanup_spell` sends. Whether a borrower
    needs those copies is the index-link design melder_1 is reworking on the owner's sharing rule (an index link
    follows the index's active spell), so it goes to melder_1 by mailbox with the next message.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook_creation_system.py:1332-1421
  - src/melder/aether/spellbook/spellbook.py:5243-5498
  - src/melder/aether/conduit/conduit.py:4010-4126
  - src/melder/aether/spellbook/spellbook.py:4358-4421
  IMPACT: A1 adds no third story; the borrower question stays with its owner's lane.
  NEXT: Sweep A2: read the parked branch of `_dispose_spell` against every structure that holds a parked version.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-17T20:28:16Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Sweep A2, read whole and proven (identical with the GIL off and on): `Conduit.cleanup_spell` of a parked
    version whose index survives tells index-link borrowers nothing. `_dispose_spell` returns None when other members
    keep the index, and the conduit then emits only on a destroyed index (`_emit_index_destroy`); the member removal
    `remove_from_spell_index` sends (`_emit_index_member_removed`, whose docstring names `Conduit.cleanup_spell` as
    one of its callers) is never sent. Probe: with English active and French parked on an index a borrower contracts
    whole, `remove_from_spell_index(French)` drops the borrower's parked copy and borrowed id (P1), while
    `cleanup_spell(French)` leaves the borrower a parked copy holding the cleaned French Spell and French's id (P2) -
    and the borrower's own `remove_index_from_contract` then removes English and keeps French's copy and id for good.
    The rest of A2 holds: the lender drops French from `_inactive_spells`, `_spell_ids` and the index, and from the
    record (`emit_spell_removed`); research residency is a query-time join over custody; a parked version has no
    Nexus record and no lineage state. Not filed: the verdicts a once-active parked version keeps in each conduit's
    resolution state outlive its disposal, but nothing reads a verdict for an id no state selects.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:6182-6234
  - src/melder/aether/conduit/conduit.py:6092-6180
  - src/melder/aether/spellbook/spellbook.py:4422-4563
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2557-2589
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_parked_cleanup_borrowers.py:1-149
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_parked_cleanup_borrowers_gil0.txt:1-29
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_parked_cleanup_borrowers_gil1.txt:1-29
  IMPACT: A borrower keeps a record of a version that no longer exists, and no later call removes it - structure
    stuck. Contract side, but none of melder_1's named items; filed here, and melder_1 told (it holds conduit.py).
  NEXT: File the story; NOTICE melder_1 with this and the A1 surface note.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-17T20:31:54Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Sweep A3, read whole and proven (identical with the GIL off and on): the index `remove_from_spell_index`
    mints is never registered in the frame's spell registry. `_apply_remove_from_index` builds
    `SpellIndex(initial_id=spell_id)` and repoints the spell, with no `_register_single_spell_index` call - the call
    a post-conjure `bind` makes for its new index - while `_destroy_spell_index` does unregister an index it
    destroys. The frame resolves a spell_id to its conduit by walking that registry (`find_conduit_id_for_spell`),
    so a version in a minted index is unknown to every frame-level lookup. Probe: M1 (control, French parked in
    English's index) - the frame finds French's index and conduit; M2 (French alone, parked, in the minted index) -
    `find_index_for_spell` answers None, `get_spell_by_id` and `get_conduit_by_spell_id` raise "Spell version <id>
    not found in any conduit."; M3 (French notched active inside the minted index) - the same, though
    `meld(spell_id=French)` builds French, and a borrower's `add_spell_to_contract(spell_id=French)` raises the
    same ValueError: an active spell its own frame cannot find or share. The rest of A3 holds: the moves keep the
    spell's id-keyed state, the record gets both index snapshots, and borrowers get the member added or removed
    (`Conduit.add_to_spell_index` / `remove_from_spell_index`).
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:4271-4356
  - src/melder/aether/spellbook/spellbook.py:5883-5888
  - src/melder/aether/spellbook/spellbook.py:4192-4237
  - src/melder/aether/aetheric_frame/aetheric_frame.py:1288-1307
  - src/melder/aether/aetheric_frame/aetheric_frame.py:943-970
  - src/melder/aether/conduit/conduit.py:5979-6180
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_minted_index_registry.py:1-149
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_minted_index_registry_gil0.txt:1-26
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_minted_index_registry_gil1.txt:1-26
  IMPACT: Structure wrong: the frame's record of which conduit holds which index misses an index a Book owns. It
    stays wrong after melder_1's spell_id lookup fix, because the frame step comes before the Book's.
  NEXT: File the story; tell melder_1 (its lookup fix meets this).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-17T20:35:54Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Sweep A4 is done with no story beyond STORY-2026-10-17-notch_moves_signature_by_incoming_key_only (its
    step 4). The notch's other records follow the active version: the parked and promoted versions' custody moves
    through `emit_spell_activity` in the park and promote tails, the index crystal is emitted after the repoint (the
    one truthful selection snapshot), MutationResearch journals the promotion, and Nexus replaces the outgoing
    version's record with the incoming one's (a plain publish when the index had no active version); a world notched
    inside a minted index restores with both versions active (probe R3, sweep A5).
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:3906-4061
  - src/melder/aether/spellbook/spellbook.py:1500-1621
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_restore_staged_structure_gil0.txt:13-17
  IMPACT: A4 adds no story.
  NEXT: Record sweep A5's restore results.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-17T20:35:54Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Sweep A5, read whole and proven (each case records with the Crystallizer active, seals and flushes a
    checkpoint into a scratch cache, boots fresh and restores; identical with the GIL off and on, ids masked). R1:
    a world with French staged under English's signature restores "complete" with English active, French parked -
    and the frame claim for the signature released: the restore replays staging through `Conduit.bind_inactive`, so
    STORY-2026-10-17-staged_version_releases_active_signature hits every such restore. R2: French parked alone in
    the index `remove_from_spell_index` minted is not rebuilt - `_bind_one_staged` finds no live anchor, because
    `_live_index_for` translates an index only after one of its members was bound active, and a parked-only index
    has none - so the report says "complete" with the shortfall "staged_member_anchor_index_not_rebuilt: <index>"
    and the rebuilt Book has no French, although the record captured the minted index (`_apply_remove_from_index`
    emits both snapshots). R3: the same world after French was notched active in its index restores whole.
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1915-2003
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2201-2269
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2400-2441
  - src/melder/aether/spellbook/spellbook.py:4271-4356
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_restore_staged_structure.py:1-160
  - context_compass/artifacts/correctness_defects_20261017/probes/restore_targets.py:1-24
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_restore_staged_structure_gil0.txt:1-18
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_restore_staged_structure_gil1.txt:1-18
  IMPACT: One more defect: the record keeps a separated parked version that the restore drops while reporting the
    restore complete - structure wrong after a restore. R1 widens the first story's impact to restores.
  NEXT: File the restore story; add R1 to the first story's Notes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-17T20:37:46Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: The planned sweep A1-A5 is done (five stories; the owner told, chat 2026-10-17). Tranche 2, same rules
    (read whole, then probe; melder_1's lane excluded), in this order:
    A6 managed pools across a version's life - notch away and back, disposal of an active or parked managed
       version, `ReleaseManagedSpell.release` of an object whose version was notched away or disposed, index moves
       of a parked managed version: do the pool, its registration and the owner stamp stay right?
    A7 Book teardown with parked versions - does `Spellbook.cleanup` let every structure holding a parked version
       go (the version, its index, its pool registration, its record), as it does for active ones?
    A8 the views of moved and separated versions - MutationResearch residency and Nexus publication after index
       moves, a separation and a notch inside a minted index.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:1300-1316
  - context_compass/system_docs/src_architecture.md:1055-1063
  IMPACT: Keeps the hunt on version lifecycle, where the first pass found every defect so far.
  NEXT: Read `ReleaseManagedSpell` and the managed pool's registration paths whole for A6.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.

## Context / Handoff Summary
- Scope: correctness defects - structure Melder records wrong or leaves stuck - by the owner's rulings (DECISION
  note); read-only; one story per confirmed defect; melder_1's lane excluded.
- State: in_progress (melder_0), discovery. The planned sweep A1-A5 is done; five stories filed (ready,
  unassigned): STORY-2026-10-17-staged_version_releases_active_signature (p1),
  STORY-2026-10-17-notch_moves_signature_by_incoming_key_only (p2, open question),
  STORY-2026-10-17-parked_cleanup_leaves_borrower_copies (p2),
  STORY-2026-10-17-minted_index_missing_from_frame_registry (p2) and
  STORY-2026-10-17-restore_drops_separated_parked_version (p2, open question). The first four fixes
  sit in spellbook.py and conduit.py, which melder_1 holds; the fifth in restore_engine.py (free).
- Done since: the owner told what was filed and the two open questions (chat); melder_1 told of the four
  stories whose fixes sit in its files (M0-181, M0-182; it carries them to the owner with its fix #1).
- Next: tranche 2 (PLAN 20:37:46Z): (1) A6 managed pools across a version's life; (2) A7 Book teardown
  with parked versions; (3) A8 the views of moved and separated versions.

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
