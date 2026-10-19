# Epic: correctness_defects - structure Melder records wrong or leaves stuck

## Metadata
- Epic ID: EPIC-2026-10-17-correctness_defects
- Status: in_progress
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-17T20:11:34Z
- Updated: 2026-10-19T01:07:36Z
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
- [x] Milestone 3: a story per confirmed defect; the owner told what was found.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-10-17-staged_version_releases_active_signature - staging, moving or
  disposing a parked version drops the binding signature of the active spell keyed like it (sweep A1).
- [ ] Story: STORY-2026-10-17-notch_moves_signature_by_incoming_key_only - a notch moves signatures by the
  incoming key alone: a parked version keeps its claim, or an active spell's key is taken (sweep A1).
- [ ] Story: STORY-2026-10-17-parked_cleanup_leaves_borrower_copies - cleanup_spell of a parked version leaves
  its copy and id with index-link borrowers, past their own unlink (sweep A2).
- [x] Story: STORY-2026-10-17-minted_index_missing_from_frame_registry - the index remove_from_spell_index
  mints is missing from the frame's spell registry, so its version is unknown by spell_id (sweep A3). Landed
  by melder_1 at 0.2.8259: the minted index is registered with the frame as bind registers its new one and
  leaves with its root, and residency reads its version parked; turned in 2026-10-19 (M1-42), in
  tickets/stories/completed/.
- [ ] Story: STORY-2026-10-17-restore_drops_separated_parked_version - a restore drops a parked version
  alone in its own index and still reports complete (sweep A5).
- [x] Story: STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool - a release with no filter
  sends a parked version's object to the active version's pool and strands its count (sweep A6). Part A landed
  at 0.2.8254 (the managed settings left the spell_id; owner, 2026-10-17); turned in 2026-10-18 on the owner's
  identity direction, part B superseded by EPIC-2026-10-18-spell_identity_is_the_code; in tickets/stories/completed/.
- [ ] Story: STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned - Book teardown leaves
  its parked versions and parked-only indexes uncleaned, beyond any cleanup (sweep A7).
- [ ] Story: STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers - a notch whose commit
  validation fails keeps its switch and leaves its borrowers behind (sweep A9). melder_1's (the owner-approved
  patch failed_notch_refusal_2026_10_18; M1-30, M1-31); on hold by the owner since 2026-10-18T13:38:59Z, no src
  edit made (M1-33).
- [x] Story: STORY-2026-10-17-direct_cleanup_of_active_member_orphans_parked_versions - a direct cleanup
  of an index's active member leaves its parked versions on a cleaned index (sweep A10). Landed by melder_1
  at 0.2.8256 with the refusal the owner chose (M1-37): all three cleanup calls refuse the active member of
  an index that holds parked versions, naming the remedies; turned in 2026-10-18 (M1-38), in
  tickets/stories/completed/. S4 and S7 follow with melder_1, one at a time (M1-32).
- [x] Story: STORY-2026-10-17-minted_index_selects_its_parked_version - the index
  remove_from_spell_index mints selects its parked version, so a graft activates it (sweep A12). Withdrawn on
  the owner's ruling (2026-10-17): not a defect; in tickets/stories/completed/.

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

- None open on the stories. S6's open items - part B's refusal, its legacy record and the rest of the bind call -
  moved with its turn-in (2026-10-18) to EPIC-2026-10-18-spell_identity_is_the_code.

## Decision Log
- 2026-10-17T20:11:34Z: opened on the owner's direction (DECISION note).
- 2026-10-17T20:24:15Z: sweep A1 filed STORY-2026-10-17-staged_version_releases_active_signature and
  STORY-2026-10-17-notch_moves_signature_by_incoming_key_only (MEASURE note).
- 2026-10-17T20:29:03Z: sweep A2 filed STORY-2026-10-17-parked_cleanup_leaves_borrower_copies (MEASURE note).
- 2026-10-17T20:32:42Z: sweep A3 filed STORY-2026-10-17-minted_index_missing_from_frame_registry (MEASURE note).
- 2026-10-17T20:36:54Z: sweep A4 checked, no story; sweep A5 filed
  STORY-2026-10-17-restore_drops_separated_parked_version (MEASURE note).
- 2026-10-17T21:07:53Z: sweep A6 filed
  STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool (MEASURE note).
- 2026-10-17T21:13:35Z: sweep A7 filed
  STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned and widened
  STORY-2026-10-17-notch_moves_signature_by_incoming_key_only (MEASURE note).
- 2026-10-17T21:16:35Z: sweep A8 checked, no story; widened
  STORY-2026-10-17-minted_index_missing_from_frame_registry (residency_view; MEASURE note).
- 2026-10-17T21:32:09Z: sweep A9 filed
  STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers (MEASURE note).
- 2026-10-17T21:38:03Z: sweep A10 filed
  STORY-2026-10-17-direct_cleanup_of_active_member_orphans_parked_versions (MEASURE note).
- 2026-10-17T21:41:33Z: sweep A11 checked, no story (a failed late bind keeps
  its spell by design); its precedent added to STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers
  (FACT notes).
- 2026-10-17T21:47:06Z: sweep A12 filed
  STORY-2026-10-17-minted_index_selects_its_parked_version and widened
  STORY-2026-10-17-staged_version_releases_active_signature and
  STORY-2026-10-17-restore_drops_separated_parked_version (graft side; MEASURE note).
- 2026-10-17T21:55:46Z: the owner answered S2 (one index may hold several signatures) and S5 (restore what should be
  restored: rebuild parked); S1 follows from S2's answer (DECISION notes).
- 2026-10-17T22:12:58Z: the owner answered S8 - (a): a notch whose incoming version fails its commit check is
  refused with nothing moved (DECISION note).
- 2026-10-17T23:25:30Z: the owner ruled S10 not a defect - moving a version is the agent's call and activation takes a
  notch; S10 withdrawn, its graft side stays in S5; S6 reframed to options 1-4 (DECISION note).
- 2026-10-17T23:50:39Z: the owner chose S6's direction - the bind call's settings must not change the
  spell_id, notch for the cache; melder_0 takes S6's fix lane (DECISION note).
- 2026-10-18T00:42:22Z: the owner confirmed S6's scope - the four managed settings only - and gave the go for
  part A (DECISION note).
- 2026-10-18T12:06:53Z: the owner's identity direction: S6 turned in (part A delivered, part B superseded); its open
  items moved to EPIC-2026-10-18-spell_identity_is_the_code (DECISION note).
- 2026-10-18T13:06:51Z: the owner's order (M1-30): parallel - melder_1 takes the stories he fully confirmed, one
  at a time, S8 first; melder_0 runs EPIC-2026-10-18-spell_identity_is_the_code (FACT note).
- 2026-10-18T13:11:35Z: the owner's order for the fixes (melder_1's DECISION note; M1-32): S8, then S4, S7 and S9
  with melder_1; S3 waits for its open question; S1, S2 and S5 wait for EPIC-2026-10-18-spell_identity_is_the_code.
- 2026-10-18T14:14:10Z: S8 on hold by the owner (13:38:59Z); melder_1 started S9 and holds spellbook.py and
  spell.py for it (FACT note).
- 2026-10-18T15:15:34Z: M1-35 - the owner's rule for S9 (an index whose active version is cleaned up keeps its
  parked versions with nothing active; the refusal goes) supersedes sweep A10's "refused by design";
  melder_1 holds spell_index.py too, released by M0-197 (FACT note).
- 2026-10-18T17:23:22Z: M1-38 - S9 landed at 0.2.8256 with the refusal the owner chose (M1-37) and is turned in;
  the hole rule of the 15:15:34Z entry did not land (FACT note).
- 2026-10-19T00:49:20Z: M1-42 - S4 landed at 0.2.8259 and is turned in; S7 is next with melder_1; the identity
  epic is turned in, so S1, S2 and S5 wait for the owner's word (FACT note).
- 2026-10-19T01:07:36Z: M1-43 - S7 is in progress with melder_1; spellbook.py and spell.py go to it for S7
  (M0-208; FACT note).

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

- DATETIME: 2026-10-17T21:06:35Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Sweep A6, read whole and proven (identical with the GIL off and on, ids masked). One defect: when two
    versions of one index bind the same class, a release with no filter sends an object leased from the parked
    version to the active version's pool, and the parked version's limited_quantity or queue pool counts that object
    as out for good. `ReleaseManagedSpell.release` resolves several pools of a class by keeping the one whose version
    its index selects (`_resolve_pool`, `_is_selected_version`; the managed epic's lifecycle table: "resolver
    prefers the active version"), `put_back` pools any object uncounted, and only the leasing pool's `reserve()`
    raised a count. Probe Q2: A (limited_quantity, limit 1) leases Worker #2; B (same class, limit 2) is staged and
    notched in; `release(obj)` puts #2 into B's pool (B count 0, idle 1; A count 1, idle 0); B serves #2 next; after
    a notch back, A refuses with ManagedSpellExhaustedError "has all 1 objects out" while nothing is out - stuck
    until someone leases #2 from B and releases it with spell_id=A. Q3: `release(obj, spell_id=A)` keeps both
    pools right. Q6: versions that are two classes route by class, untouched. The rest of A6 holds by the owner's
    rulings of 2026-10-14 (notch and cleanup_spell destroy nothing; identity is not tracked): a disposed version's
    pool stays registered with its idle objects (Q4); a rebind under the same spell_id meets it, re-pointed, and
    serves its idle object (Q5); index moves leave the pool alone and `_is_selected_version` follows the Spell's
    current index; a lease from `managed_spell_meld` carries its pool, so it never misroutes.
  EVIDENCE:
  - src/melder/aether/conduit/creations/release_managed_spell.py:357-399
  - src/melder/aether/conduit/creations/release_managed_spell.py:515-580
  - src/melder/aether/conduit/creations/release_managed_spell.py:625-645
  - src/melder/aether/conduit/creations/managed_spell_quantity.py:474-545
  - src/melder/aether/conduit/creations/managed_spell_quantity.py:548-606
  - src/melder/aether/conduit/conduit.py:5067-5179
  - context_compass/tickets/epics/completed/2026-10-14_managed_spell_quantity_epic.md:401-412
  - context_compass/tickets/epics/completed/2026-10-14_managed_spell_quantity_epic.md:679-687
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_managed_release_routing.py:1-205
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_managed_release_routing_gil0.txt:1-64
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_managed_release_routing_gil1.txt:1-64
  IMPACT: Structure stuck: a pool's count names an object out that the pool will never get back, so a limited or
    queue version refuses every lease after a notch back. The preference is an accepted design, so the story carries
    the fix direction as the owner's question. The fix sits in release_managed_spell.py, which no lane holds.
  NEXT: File the story; then sweep A7 (Book teardown with parked versions).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-17T21:11:57Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Sweep A7, read whole and proven (identical with the GIL off and on, ids masked). One new defect and one
    wider impact. New: Book teardown never cleans its parked versions or an index only they hold, and nothing can
    clean them afterwards. `Spellbook._cleanup_spells` walks `_spells` (the active version per index) and cleans
    each Spell and its index; `_cleanup_components` then clears `_inactive_spells` without cleaning one, while the
    parked branch of `_dispose_spell` shows the local teardown a parked version needs (`_spellbook_cleanup` set,
    `Spell.cleanup()`). A later direct `Spell.cleanup()` on such a version routes to its Book
    (`_direct_removal_route` -> `cleanup_and_remove_spell`) and raises "Spellbook has already been cleaned.". Probe
    T2: after the root's teardown English is cleaned and French (parked on its index) is not, and
    `French.cleanup()` raises; T3: a parked version separated into its own minted index - neither it nor that index
    is cleaned. Wider: STORY-2026-10-17-notch_moves_signature_by_incoming_key_only outlives the Book. After a notch
    across keys the parked English still holds ('greeter', 'greeter') frame-wide; the notch's park popped that key
    from the Book's `_lookup_spells`, and teardown releases only the keys in that map, so the claim survives the
    Book (T4): every later bind of the signature in that frame is refused, naming a spell of a dead Book. The rest
    holds: the record evicts the Book's custody in both locations and its index crystals by Book id; the root store's
    cleanup unregisters every pool, parked versions' included (T5); the frame drops the conduit's registry entry.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:370-398
  - src/melder/aether/spellbook/spellbook.py:405-556
  - src/melder/aether/spellbook/spellbook.py:557-600
  - src/melder/aether/spellbook/spellbook.py:602-748
  - src/melder/aether/spellbook/spellbook.py:1500-1561
  - src/melder/aether/spellbook/spellbook.py:4422-4563
  - src/melder/aether/spellbook/spell.py:581-723
  - src/melder/aether/spellbook/spell.py:725-763
  - src/melder/crystallizer/persistence/persistence_profile.py:684-754
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_book_teardown_parked.py:1-231
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_book_teardown_parked_gil0.txt:1-30
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_book_teardown_parked_gil1.txt:1-30
  IMPACT: Structure stuck twice over: parked versions of a dead Book stay uncleaned and cannot be cleaned, and a
    signature a notch left claimed stays claimed for the frame's life. Both fixes sit in spellbook.py (melder_1's).
  NEXT: File the teardown story; add T4 to the notch-signature story's Notes; then sweep A8.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-17T21:16:07Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Sweep A8, read whole and proven (identical with the GIL off and on). No new seam; one wider impact of
    STORY-2026-10-17-minted_index_missing_from_frame_registry. `MutationResearch.residency_view` takes runtime truth
    from the frames (`_locate_live_membership` -> `AethericFrame.find_index_for_spell`, the registry the minted index
    is missing from), so a version in the index `remove_from_spell_index` mints reads "declared_only" with no index:
    probe V2 (French parked there) and V3 (French notched active there, under its own binding name) both answer
    `declared_only in none` while the Book holds it parked, then active; V1 and V4 (members of a registered index)
    read right. Nexus holds: it publishes active versions only, each with the index the Spell names
    (`FrameDescriptorManager._publish_spell_record`), a notch inside a minted index publishes the incoming version
    plainly, and its relationships read the Book's active pool; parked versions are never published. Seen on the way,
    to be swept next: with French under English's binding name, the notch inside the minted index raised
    SpellbookValidationError [DUPLICATE_SPELL_NAME] from its commit validation after the seam had run - what such a
    failed notch leaves behind is unchecked.
  EVIDENCE:
  - src/melder/mutation_research/mutation_research.py:1374-1483
  - src/melder/mutation_research/mutation_research.py:1485-1525
  - src/melder/nexus/frame_descriptor_manager.py:512-584
  - src/melder/aether/spellbook/spellbook.py:6533-6582
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_research_residency_moves.py:1-110
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_research_residency_moves_gil0.txt:1-13
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_research_residency_moves_gil1.txt:1-13
  IMPACT: MutationResearch, the record agents read to see where their versions live, loses every version in a
    minted index, active or parked; the S4 fix restores it. A failed notch commit may be a new seam (A9).
  NEXT: Add V2-V3 to S4's Notes and Artifact Links; then sweep A9: what a notch whose commit validation fails
    leaves behind.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-17T21:19:15Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Sweep A9, read whole and proven (identical with the GIL off and on). One defect: a notch whose commit
    validation fails raises but keeps its switch, and its borrowers never follow. `Conduit.notch_spell` runs the seam
    (`Spellbook._notch_spell` -> `_apply_notch`: park, promote, index pointer, frame claim, re-registration, marks,
    research, Nexus) inside the transaction, then `end_transaction(success=True)` commits; for a version never
    compiled the commit runs phases 1-4 (`_default_structural_validator`). When they fail, the mediator runs the
    session's abort pipeline - the notch registered no rollback action - and re-raises, so notch_spell exits before
    its borrower fan-out (`_deactivate_borrowed_spell`, `_activate_borrowed_spell`, `_emit_index_notch`). Probe N2:
    a staged version whose constructor takes its own class (SELF_DEPENDENCY); notch_spell raises
    SpellbookValidationError, yet the lender's index selects it, it is active and English is parked, while the
    index-linked borrower still holds English active and the new version parked; the lender's meld by address
    raises, by English's spell_id KeyError. N3: a notch back to English restores both sides. N1 (a sound version):
    owner and borrower both follow.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:5622-5759
  - src/melder/aether/spellbook/spellbook.py:3851-3904
  - src/melder/aether/spellbook/spellbook.py:3906-4061
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:783-835
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:1043-1091
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_session.py:502-526
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_failed_notch_commit.py:1-171
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_failed_notch_commit_gil0.txt:1-34
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_failed_notch_commit_gil1.txt:1-34
  IMPACT: Structure wrong: after an operation that reported failure, the lender selects the new version and its
    borrowers the old one, against "borrowers follow"; an agent reading the exception believes nothing moved. The
    fix direction (roll the switch back, or let it stand as a failed bind's spell does and complete the fan-out) is
    the owner's. The fix sits in conduit.py and spellbook.py, which melder_1 holds.
  NEXT: File the story; NOTICE melder_1 of this story, the teardown story and the two widenings; tell the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-17T21:33:36Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Tranche 2 (A6-A9) is done: S6-S8 filed, S2 and S4 widened, melder_1 told (M0-184), the owner told of
    S6-S8 with the two new questions (chat). Tranche 3, same rules (read whole, then probe with the GIL off and on;
    melder_1's lane and the backlog tasks excluded), in this order:
    A10 cleanup_spell of an ACTIVE version whose index holds parked versions - the active branch of
        `_dispose_spell`: what becomes of the index, its parked members, the frame claim, the lineage registration,
        the record and index-link borrowers?
    A11 a bind whose commit validation fails - a post-conjure `bind` (dynamic world) of a class whose phases 1-4
        report it broken: what does the raise leave registered (the Book's maps, the frame claim, the lineage, the
        record, research, Nexus), and can the agent bind a fixed version at that address afterwards?
    A12 graft of an index with parked versions - `GraftRunner` over a captured index whose members include parked
        versions, and over one whose members are all parked: does the live Book get every member (S5's restore gap)?
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:758-772
  - context_compass/system_docs/src_architecture.md:948-1011
  - context_compass/system_docs/src_architecture.md:2743-2765
  IMPACT: Keeps the hunt on version lifecycle and on operations that fail part-way, where tranches 1-2 found every
    defect so far.
  NEXT: Read the active branch of `Spellbook._dispose_spell` and `Conduit.cleanup_spell` whole for A10.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-17T21:36:36Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Sweep A10, read whole and proven (identical with the GIL off and on). `cleanup_spell` of the active member
    of an index that also holds parked versions is refused by design ("notch away from it first": it would leave
    the index headless), and D1 shows the refusal changes nothing. One defect: the two other public ways to dispose
    that member skip the rule. A direct `Spell.cleanup()` routes to `Spellbook.cleanup_and_remove_spell`, which
    resolves the active spell and then unregisters its whole index from SpellSystemStates, drops the index from the
    frame registry and the record, and cleans the index - with no check for parked members. Probe D2
    (`English.cleanup()`) and D3 (`cleanup_and_remove_spell(english_id)`), French parked on English's index: the
    index is cleaned, French stays parked in the Book, uncleaned, pointing at the cleaned index and unknown to the
    frame; a notch to it raises AttributeError, `add_to_spell_index` and `cleanup_spell` of it raise "SpellIndex has
    already been cleaned.", the Book's teardown leaves it (S7) and `French.cleanup()` then raises "Spellbook has
    already been cleaned.". The index-linked borrower keeps an active copy of the cleaned English and a parked copy
    of French (the direct path sends no ward emission - the gap already with melder_1, A1 note).
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:4358-4421
  - src/melder/aether/spellbook/spellbook.py:4422-4563
  - src/melder/aether/spellbook/spellbook.py:602-748
  - src/melder/aether/spellbook/spell.py:581-723
  - src/melder/aether/spellbook/spell.py:725-763
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_direct_cleanup_active_member.py:1-186
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_direct_cleanup_active_member_gil0.txt:1-49
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_direct_cleanup_active_member_gil1.txt:1-49
  IMPACT: Structure stuck: a parked version left on a cleaned index can be neither notched, moved, disposed nor
    cleaned by its Book's teardown. The fix sits in spellbook.py (melder_1 holds it): apply cleanup_spell's own rule.
  NEXT: File the story; then sweep A11 (a bind whose commit validation fails).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-17T21:41:15Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Sweep A11, read whole and probed (identical with the GIL off and on): no story. A late `bind` stages its
    spell on the bind transaction (`_stage_spell_for_structural_phases`) and the commit runs phases 1-4 for it; a
    broken class fails there after the bind registered it, and `Spellbook.transaction` re-raises from its commit
    with nothing unregistered. Probe B2: `bind(SelfMade)` raises SpellbookValidationError "Broken spells: SelfMade.",
    and SelfMade stays active, holding its address, its lineage `invalid`, every meld refused - the documented
    behaviour ("refused at that bind and at its melds", Failure Modes, 0.2.8224). Nothing is stuck: staging a fixed
    class on its index and notching to it (B2), or `cleanup_spell` and a fresh bind (B3), gets the agent past it.
    Two things for S8: a failed late bind keeps its spell - the precedent for S8's option (b) - but displaces
    nothing, while a failed notch displaces a working version; and `_stage_spell_for_structural_phases` says notch
    "does NOT stage" and runs the phases directly, which the validator, `_notch_spell` and probe N2 contradict - a
    stale docstring for S8's fix to correct.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:5569-5896
  - src/melder/aether/spellbook/spellbook.py:4788-4864
  - src/melder/aether/spellbook/spellbook.py:4937-4958
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:783-835
  - context_compass/system_docs/src_architecture.md:2490-2502
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_broken_late_bind.py:1-187
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_broken_late_bind_gil0.txt:1-40
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_broken_late_bind_gil1.txt:1-40
  IMPACT: A11 adds no story; it gives S8's open question its bind precedent and its fix a stale docstring to correct.
  NEXT: Add the precedent to S8's Notes; then sweep A12 (graft of an index with parked versions).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-17T21:45:24Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Sweep A12, read whole and proven (each case records with the Crystallizer active, captures one index,
    boots fresh and grafts it into a new host Book; identical with the GIL off and on). One new defect, two wider
    impacts. New: the index `remove_from_spell_index` mints selects the parked version it holds -
    `SpellIndex(initial_id=...)` makes its one member the selection, and `_apply_remove_from_index` leaves it so -
    although `selected_spell_id` is documented as "the active spell's id" and `_is_selected_unless_cleaned` as
    answering False for a parked member. The record captures that selection, and a graft (fresh-index mode) binds the
    selected member ACTIVE: G2, French parked alone in the minted index, comes back active in the host. Wider: G4,
    a graft parks members through `Conduit.bind_inactive`, so a parked member under the active member's signature
    releases the host's claim for it (S1, as the restore did in R1); and the graft side of S5's gap is G2 - the
    graft activates the separated version instead of dropping it. G1 and G3 (members of a registered index) graft
    right: English active, French parked.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:4271-4356
  - src/melder/aether/spellbook/bind/spell_index.py:83-116
  - src/melder/aether/spellbook/bind/spell_index.py:143-164
  - src/melder/aether/spellbook/bind/spell_index.py:358-388
  - src/melder/crystallizer/persistence/persistence_profile.py:900-969
  - src/melder/crystallizer/crystal_loader_system/graft_runner.py:230-330
  - src/melder/crystallizer/crystal_loader_system/graft_runner.py:375-489
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_graft_parked_members.py:1-152
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_graft_parked_members_gil0.txt:1-26
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_graft_parked_members_gil1.txt:1-26
  IMPACT: Structure wrong: the index and the Book disagree on whether its version is active, and the record and
    every graft carry the index's answer. The seam is S4's (`_apply_remove_from_index`, spellbook.py, melder_1's).
  NEXT: File the story; add G2 to S5's Notes and G4 to S1's; then NOTICE melder_1 and tell the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-17T21:55:46Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner answered two open questions (chat 2026-10-17). S2: "Yes 1 spellindex can hold versions with
    different binding signatures, this is why revalidation happens" - a notch moves the frame claim with the active
    version (the outgoing claim released, the incoming key claimed) and refuses a key another active spell holds;
    staging stays open to any key. S5: "I'm not sure whats the most correct thing? I think we restore what should be
    restored" - with melder_0's recommendation given in reply: a version separated into an index of its own is
    structure an agent made with a public verb and the record already holds, so a restore and a graft rebuild it
    parked, in a fresh index of its Book (his word can still override). Follow-ons: S1's side question takes its
    minimal fix (a parked version claims no signature; the one-active-signature rule holds where a version becomes
    active - bind, or S2's notch refusal); S10's graft criterion becomes "comes back parked". Still open: S6, S8, S10.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-17_notch_moves_signature_by_incoming_key_only_story.md:99-103
  - context_compass/tickets/stories/2026-10-17_restore_drops_separated_parked_version_story.md:94-98
  - context_compass/tickets/stories/2026-10-17_staged_version_releases_active_signature_story.md:97-101
  - context_compass/system_docs/src_architecture.md:26-34
  IMPACT: S2, S5 and S1 carry no open question now; S10's acceptance narrows; three questions remain with the owner.
  NEXT: The owner's answers on S6, S8 and S10.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-17T22:12:58Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner answered S8 (chat 2026-10-17): "Yeah sure you can refuse it and throw and move on if you mean it
    couldn't notch that makes sense" - and it is that case: the incoming version failed the structural check the
    notch's commit runs. S8 takes answer (a): a notch whose incoming version fails that check is refused with nothing
    moved, the lender and every borrower stay on the outgoing version, and the error says so. The owner asked for
    plain explanations of S6 and S10 with examples (given in the reply); both questions stay open with him.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md:114-121
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_failed_notch_commit_gil0.txt:10-19
  IMPACT: S8 carries no open question; two remain with the owner (S6, S10).
  NEXT: The owner's answers on S6 and S10.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-17T23:25:30Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner ruled S10 not a defect (chat 2026-10-17: moving a version is the agent's call - "you gotta use
    notch"), so STORY-2026-10-17-minted_index_selects_its_parked_version is withdrawn and moved to completed; its
    graft side stays in S5, whose lanes now decide from each member's recorded custody. On S6 the owner asked to see
    the code and to talk it through properly: the two versions are one class object differing only in
    `managed_spell_limit`, the earlier raise-on-ambiguity recommendation is withdrawn (it would fire on every release
    of the class), and four options are with him, option 3 (one managed version per class per index) recommended.
  EVIDENCE:
  - context_compass/tickets/stories/completed/2026-10-17_minted_index_selects_its_parked_version_story.md:107-112
  - context_compass/tickets/stories/2026-10-17_release_routes_parked_version_objects_to_active_pool_story.md:99-106
  IMPACT: Nine stories remain; one open question (S6) is with the owner.
  NEXT: The owner's choice on S6.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-17T23:27:04Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: melder_1's lookup fix is now in the tree (its board row: "Fix #1's code is in the repo"; the files were
    written at 22:22:06Z, __version__ still 0.2.8252), so this epic's line citations into two of its files moved:
    spellbook.py by +5 to +6 lines after `find_spell_by_spell_id` (`_notch_spell` 3856, `_apply_notch` 3911,
    `_apply_add_to_index` 4101, `_destroy_spell_index` 4197, `_apply_remove_from_index` 4276, `_dispose_spell` 4427,
    `transaction` 4794, `bind_inactive` 5248, `bind` 5574), conduit.py by +8 at `bind_inactive` (4018) and +28 to +30
    from `managed_spell_meld` (5095) on (`notch_spell` 5650, `add_to_spell_index` 6009, `remove_from_spell_index`
    6122, `cleanup_spell` 6212). spell.py, conduit_ward.py, restore_engine.py and graft_runner.py citations hold.
    Notes keep the ranges of their DATETIME; a fix lane re-reads the code it changes.
  EVIDENCE:
  - context_compass/attention_board.md:186-186
  - src/melder/aether/spellbook/spellbook.py:2052-2052
  - src/melder/aether/spellbook/spellbook.py:3911-3911
  - src/melder/aether/conduit/conduit.py:5650-5650
  IMPACT: A reader following an older note into spellbook.py or conduit.py lands a few lines early; the method names
    in each note stay the reliable key.
  NEXT: The owner's choice on S6.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-17T23:50:39Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner chose S6's direction (chat 2026-10-17): "the bind call itself shouldn't impact the actual SHA256
    thats absurd" - a bug - and "you gotta notch the version for the cache". The managed settings leave the spell_id
    (option 2); a same-spell_id rebind re-composes its pool's settings; the notch and a cache generation bump retire
    every bundle. melder_0 takes S6's fix lane (free files) and starts with patch docs; the scope (address, existence,
    disposal names and resolvable stay in the id; a staging refusal for the residual same-class case) is with the
    owner for confirmation (S6's DECISION note).
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-17_release_routes_parked_version_objects_to_active_pool_story.md:99-106
  - src/melder/aether/spellbook/bind/bind.py:1019-1150
  IMPACT: No open question remains on the stories except the scope confirmation; S6 moves from ready to in_progress.
  NEXT: S6's patch docs and the owner's confirmation; then the fix after melder_1's notch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T00:42:22Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner confirmed S6's scope (chat 2026-10-18): only the four managed settings leave the spell_id, the
    rest stays; part A lands now, and part B's refusal, the legacy record and anything more of the bind call are
    talked through after it. melder_1's 0.2.8253 landed (M1-26), so part A notches above it.
  EVIDENCE: context_compass/tickets/stories/2026-10-17_release_routes_parked_version_objects_to_active_pool_story.md:399-419
  IMPACT: S6 moves to implementation; no other story changes.
  NEXT: S6's part A; then report to the owner.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-18T12:06:53Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's direction (chat 2026-10-18) took the spell's identity out of this epic: a spell_id is the
    registered object's code and the bind signature a binding manifest with its own hash, built in a new epic ("if
    your going to implement anything please make an epic, document your stories for it and lets hit that up next
    turn in anything you completed and leave notes on things you left open"). So S6 is turned in - part A delivered
    at 0.2.8254, part B superseded (one registration per object covers its case) - and its open items live in
    EPIC-2026-10-18-spell_identity_is_the_code. Eight stories stay ready (S1-S5, S7-S9), S6 is done, S10 withdrawn.
    melder_1 turned in its lane and handed back spellbook.py and conduit.py (M1-28), so the fixes that waited for
    them (S1-S4, S7-S9) wait only for the owner's scheduling; the new epic touches the same files, and with one
    writer per file the owner's order decides which lane goes first.
  EVIDENCE:
  - context_compass/tickets/stories/completed/2026-10-17_release_routes_parked_version_objects_to_active_pool_story.md:977-996
  - context_compass/tickets/stories/completed/2026-10-17_release_routes_parked_version_objects_to_active_pool_story.md:998-1021
  - context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md:116-126
  IMPACT: This epic keeps its eight ready stories and its sweep record; the identity work runs in its own epic.
  NEXT: The owner's order: the identity epic's calls first, or a correctness fix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T13:06:51Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The owner's order, relayed by melder_1 (M1-30, 2026-10-18T12:30:17Z; consumed): parallel - melder_0 keeps
    EPIC-2026-10-18-spell_identity_is_the_code; melder_1 takes this epic's stories one at a time, only those the
    owner fully confirmed, each re-verified on the current tree before any change. melder_1 started with
    STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers (S8; in_progress, its own board row); the owner
    approved its patch (failed_notch_refusal_2026_10_18, M1-31), and spellbook.py, conduit.py,
    spellbook_validation_error.py and change_control_manager.py are melder_1's until it lands (released, M0-194).
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md:1-12
  - context_compass/system_docs/patches/active/failed_notch_refusal_2026_10_18/architecture_patch.md:1-62
  IMPACT: The handoff's first open item (the owner's order) is answered; each remaining story waits for melder_1's
    next pick or the owner's word.
  NEXT: Keep this epic's record current as melder_1 lands and turns in each story.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-18T13:11:35Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's order for these fixes (chat 2026-10-18). Asked between EPIC-2026-10-18-spell_identity_is_the_code
    and the ready stories, he chose "Parallel (Recommended)": melder_0 keeps the identity epic; melder_1 takes the
    correctness fixes one at a time, S8 first, claiming each file from melder_0 by mailbox; S1, S2 and S5 wait for
    the identity epic. Of the rest he said "do the ones without open questions please": S4, S7 and S9, which carry
    none, are melder_1's after S8; S3 waits for its open question. Each story is re-verified on the current tree
    before any change, and melder_0 is told (M1-30, M1-32).
  EVIDENCE: context_compass/tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md:245-266
  IMPACT: The Handoff's next step (1), the owner's order, is answered: S8 in progress (melder_1), then S4, S7 and S9;
    S3 open; S1, S2 and S5 after the identity epic.
  NEXT: S8's fix, then S4's re-verification.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T14:14:10Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M1-33 and M1-34 from melder_1, consumed. The owner put S8 on hold (chat 2026-10-18; S8's DECISION note of
    2026-10-18T13:38:59Z) with no src edit made: conduit.py, spellbook_validation_error.py and
    change_control_manager.py are free while it waits, and melder_1 claims them again before S8 resumes. On the
    owner's word melder_1 took S9 (STORY-2026-10-17-direct_cleanup_of_active_member_orphans_parked_versions, patch
    direct_cleanup_refusal_2026_10_18) and holds spellbook.py (`cleanup_and_remove_spell`) and, released by
    M0-195, spell.py (`Spell.cleanup`'s Raises entry) until S9 lands; no edit before the owner's word on S9's edits.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md:437-452
  - context_compass/tickets/stories/2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md:1-40
  IMPACT: S9 is the story in progress; S8 waits for the owner; S4 and S7 follow S9 with melder_1.
  NEXT: Keep this record current as melder_1 lands S9.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-18T15:15:34Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M1-35 from melder_1 (2026-10-18T15:04:57Z), consumed. The owner's rule for S9 (chat 2026-10-18; S9's
    DECISION note of 2026-10-18T15:04:57Z): cleaning up an index's active version - `cleanup_spell`,
    `Spell.cleanup()` or `cleanup_and_remove_spell` - marks it invalid and removes it; the index stays with its
    parked versions and nothing active, no version promoted; what resolves through it meets a hole naming the
    index; only an index left without members is destroyed; `cleanup_spell`'s refusal goes. It supersedes
    "refused by design" in sweep A10's MEASURE note: the defect there (two calls skip the refusal) is fixed by
    giving all three calls the new rule. The fix needs a SpellIndex that can hold no selection, so melder_1
    holds spell_index.py beside spellbook.py and spell.py until S9 lands. melder_0 released it (M0-197): S1 and
    S2 of EPIC-2026-10-18-spell_identity_is_the_code edit nothing in it. They plan to edit bind.py,
    binding_profile.py, binding_profile_strategy.py, two new modules, structural_snapshot.py,
    spellbook_creation_system.py and caching_system.py, and docstrings in lookup_container.py, aether.py,
    aether_configuration.py, conduit_meld.py, meld.py, spellspace_meld.py, generalized_manifest.py and
    generalized_manifest_no_overrides_compiler.py; of these only meld.py and generalized_manifest.py read
    `selected_spell_id`, the field S9's inventory starts from.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md:361-389
  - context_compass/tickets/epics/2026-10-17_correctness_defects_epic.md:672-701
  - context_compass/tickets/stories/2026-10-18_spell_id_hashes_the_object_code_story.md:254-278
  IMPACT: S9 now changes SpellIndex's selection contract and its readers, so it holds three files longer and may
    reach a file of the identity epic's plan; S4 and S7 still follow it with melder_1. Sweep A10's record reads
    with this note.
  NEXT: Keep this record current as melder_1 lands S9; take any shared file in turn with melder_1.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T17:23:22Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M1-38 from melder_1 (2026-10-18T17:07:19Z, NOTICE), consumed. S9
    (STORY-2026-10-17-direct_cleanup_of_active_member_orphans_parked_versions) landed at 0.2.8256 and is turned
    in, rebuilt last with both checks OK. It took the refusal, the owner's choice once he reopened the rule
    (M1-36, M1-37): `cleanup_spell`, `Spellbook.cleanup_and_remove_spell` and a direct `Spell.cleanup()` refuse
    the active version of an index that holds parked versions, change nothing and name the remedies (notch to a
    parked version first, dispose the parked versions, or move them out); Book teardown is unaffected. The hole
    rule this epic's FACT note of 2026-10-18T15:15:34Z records (M1-35) did not land: sweep A10's "refused by
    design" stands, now on all three calls. melder_1 takes S4 next; spellbook.py, spell.py and spell_index.py
    are melder_0's again.
  EVIDENCE:
  - context_compass/tickets/stories/completed/2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md:1-9
  - src/melder/aether/spellbook/spellbook.py:602-781
  - context_compass/system_docs/src_architecture.md:1126-1152
  IMPACT: S9 is done; the defects left with melder_1 are S4 and S7 (S8 on hold); the record of sweep A10 reads with
    this note, not the 15:15:34Z one.
  NEXT: Keep this record current as melder_1 lands S4.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T18:08:26Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M1-39 from melder_1 (2026-10-18T18:04:38Z), consumed. S4
    (STORY-2026-10-17-minted_index_missing_from_frame_registry) has the owner's word on edits A-C:
    `remove_from_spell_index` registers the index it mints as a post-conjure `bind` does, the root's
    teardown unregisters it with the rest, and `residency_view` reads its version parked. melder_1 holds
    mutation_research.py for it and takes spellbook.py once S1 and S2 of
    EPIC-2026-10-18-spell_identity_is_the_code land, notching above them. Its probe on 0.2.8256 widens the
    defect: bind's collision guard misses a version alone in a minted index (M4b, M5b), and a transfer by
    that version's spell_id is refused (M7).
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-17_minted_index_missing_from_frame_registry_story.md:304-327
  - context_compass/artifacts/minted_index_registry_20261018/runs/probe_minted_index_fix_cases_0_2_8256_gil0.txt:1-31
  - src/melder/aether/aether.py:2550-2622
  IMPACT: S4 is the story in progress with melder_1; S7 follows it, S8 stays on hold (M1-33).
  NEXT: Keep this record current as melder_1 lands S4.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-19T00:49:20Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M1-42 consumed (melder_1, 2026-10-19T00:25:06Z): S4 (STORY-2026-10-17-minted_index_missing_from_frame_registry)
    landed at 0.2.8259 and is turned in - the index remove_from_spell_index mints is registered with the frame as
    bind registers its new index, the root's teardown unregisters it with the rest, and residency reads its
    version parked until a notch - with the system documents, the graph and the release note, rebuilt last with
    both checks OK; spellbook.py and spell.py are melder_0's again and mutation_research.py is released. The
    identity epic (EPIC-2026-10-18-spell_identity_is_the_code) is turned in with its S1 and S2 landed and S3-S5
    parked, so S1, S2 and S5 here, which waited for it (M1-32), wait for the owner's word.
  EVIDENCE:
  - context_compass/tickets/stories/completed/2026-10-17_minted_index_missing_from_frame_registry_story.md:3-9
  - context_compass/artifacts/minted_index_registry_20261018/runs/rebuild_asset_check_after_llm_0_2_8259.txt:1-3
  - context_compass/artifacts/minted_index_registry_20261018/runs/rebuild_llm_check_0_2_8259.txt:1-3
  IMPACT: S4, S6 and S9 are done and S10 withdrawn; S7 is next with melder_1, S8 stays on hold (M1-33), S3 waits for
    its open question, and S1, S2 and S5 for the owner.
  NEXT: Keep this record current as melder_1 lands S7.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-19T01:07:36Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M1-43 consumed (melder_1, 2026-10-19T00:51:08Z): on the owner's word melder_1 takes S7
    (STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned) next; its fix sits in the Book
    teardown (`Spellbook._cleanup_spells`, `_cleanup_components`), so it claims spellbook.py back, and
    spell.py if the patch needs `Spell.cleanup`, editing nothing before melder_0's answer and the owner's
    word on the exact edits. melder_0 holds no edit in either and has no src/ lane open (the identity epic
    is turned in), so both go to melder_1 for S7 (M0-208, the ACK); conduit.py,
    spellbook_validation_error.py and change_control_manager.py stay with melder_0 while S8 is on hold.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-17_book_teardown_leaves_parked_versions_uncleaned_story.md:3-12
  - context_compass/attention_board.md:149-149
  IMPACT: S7 is in progress with melder_1, which holds spellbook.py and spell.py for it; a melder_0 lane that
    needs either claims it back by mailbox first.
  NEXT: Keep this record current as melder_1 lands S7.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

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
- State: in_progress (melder_0), handoff. A1-A12 are done; ten stories filed - S9 done (0.2.8256, the
  refusal; M1-38) and S4 done (0.2.8259; M1-42); S8 blocked, on hold by the owner (M1-33); S7 in progress
  with melder_1 (M1-43); S3 waiting for its open question; S1, S2 and S5 waiting for the owner's word, the
  identity epic they waited for (EPIC-2026-10-18-spell_identity_is_the_code) being turned in with its S3-S5
  parked (M1-32); S6 done; S10 withdrawn:
  STORY-2026-10-17-staged_version_releases_active_signature (p1),
  STORY-2026-10-17-notch_moves_signature_by_incoming_key_only (p2; answered: the notch moves the claim; its
  leaked claim outlives the Book, A7),
  STORY-2026-10-17-parked_cleanup_leaves_borrower_copies (p2),
  STORY-2026-10-17-minted_index_missing_from_frame_registry (p2; done: landed at 0.2.8259 with
  residency's parked verdict, turned in 2026-10-19),
  STORY-2026-10-17-restore_drops_separated_parked_version (p2; answered: restore and graft rebuild it
  parked; a graft activates it today, A12),
  STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool (p2; done: part A landed at 0.2.8254,
  turned in 2026-10-18 with part B superseded by EPIC-2026-10-18-spell_identity_is_the_code),
  STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned (p3),
  STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers (p2; answered: refused with nothing moved),
  STORY-2026-10-17-direct_cleanup_of_active_member_orphans_parked_versions (p2; done: landed at 0.2.8256
  with the refusal, turned in 2026-10-18) and
  STORY-2026-10-17-minted_index_selects_its_parked_version (p3; withdrawn: not a defect, owner 2026-10-17).
  The owner's order is parallel (M1-30, M1-32): S9 landed and melder_1 handed spellbook.py, spell.py and
  spell_index.py back (M1-37, M1-38); spellbook.py and spell.py are with melder_1 again for S7 (M1-43,
  M0-208); conduit.py, spellbook_validation_error.py and change_control_manager.py are with melder_0 while
  S8 is on hold; each lane claims a file from the other by mailbox before editing it.
- Done since: the owner told of S1-S5, then S6-S8, then S9-S10 with their questions, the widenings and S8's
  bind precedent (chat); melder_1 told of the eight stories whose fixes sit in its files (M0-181, M0-182,
  M0-184, M0-185). The owner answered S2 and S5 (DECISION note of 2026-10-17T21:55:46Z); melder_1 told (M0-186).
  The owner answered S8 (DECISION note of 2026-10-17T22:12:58Z); melder_1 told (M0-187). The owner withdrew S10 as
  not a defect (DECISION note of 2026-10-17T23:25:30Z); melder_1 told (M0-188). The owner chose S6's direction
  (DECISION note of 2026-10-17T23:50:39Z): the managed settings leave the spell_id; melder_0 runs its fix lane.
  The owner confirmed S6's scope (DECISION note of 2026-10-18T00:42:22Z); melder_1's 0.2.8253 landed (M1-26).
  S6's part A landed at 0.2.8254 and was rebuilt last; its files are released to melder_1 (M0-192). S6 is
  turned in on the owner's identity direction (DECISION note of 2026-10-18T12:06:53Z); its open items moved to
  EPIC-2026-10-18-spell_identity_is_the_code; melder_1 handed every file back (M1-28) and is told (M0-193).
- Done since: M1-38 consumed - S9 landed at 0.2.8256 with the refusal (FACT note of 2026-10-18T17:23:22Z).
- Done since: M1-39 consumed - S4 has the owner's word on edits A-C and is in progress with
  melder_1 (FACT note of 2026-10-18T18:08:26Z).
- Done since: M1-42 consumed - S4 landed at 0.2.8259 and is turned in (FACT note of 2026-10-19T00:49:20Z).
- Done since: M1-43 consumed - S7 is in progress with melder_1, which holds spellbook.py and spell.py for
  it (M0-208; FACT note of 2026-10-19T01:07:36Z).
- Next: (1) melder_1 fixes S7 (S4 and S9 landed, M1-38, M1-42), and S8 when the owner lifts its hold (M1-32,
  M1-33); (2) S3 after the owner answers its open question; S1, S2 and S5 on the owner's word, the identity
  epic they waited for being turned in; (3) each fix with the patch gate, its notch and the rebuild; (4) a
  fourth tranche on the owner's word.

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
