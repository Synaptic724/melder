# Story: minted_index_selects_its_parked_version - an index never names a parked version as its active one

- Completed: 2026-10-17T23:25:30Z
- Summary: withdrawn on the owner's ruling (chat 2026-10-17), not a defect: moving a version with
  `remove_from_spell_index` is the agent's call and making it active takes a notch, so the split-off index naming
  its parked member stays as it is. No fix, no notch; nothing edited. The graft side (a graft activating that
  member without a notch) stays in STORY-2026-10-17-restore_drops_separated_parked_version.

## Metadata
- Story ID: STORY-2026-10-17-minted_index_selects_its_parked_version
- Epic: EPIC-2026-10-17-correctness_defects
- Status: done
- Owner: user
- Agent Name: unassigned
- Agent Role: UNKNOWN
- Priority: p3
- Created: 2026-10-17T21:47:06Z
- Updated: 2026-10-17T23:25:30Z

## User Narrative
As an agent who separates a parked version into its own index and later records or grafts that index, I want the
index to say that its version is parked, so that the record and a graft bring the version back parked, as it was,
instead of active.

## Value / MRP Alignment
Which version of a lineage is active is structure (owner ruling: a notch only moves which version is active). The
index `remove_from_spell_index` mints names its parked member as its selection, so the index and the Book disagree;
the Crystallizer record keeps the index's answer and a graft acts on it, turning a parked version into an active one.

## Ticket Contract
- ENTRY_GATE: the owner's answer to the open question below (S5's was answered on 2026-10-17: a parked-only index is
  rebuilt parked); the owner schedules the story and assigns an agent; melder_1 has released spellbook.py; an active
  board row; patch docs for the seam (and for SpellIndex when the answer is (a)).
- EXECUTION_BOUNDARY: `Spellbook._apply_remove_from_index` and, per the answer, `SpellIndex` (an index whose
  members are all parked selects nothing) with the readers of `selected_spell_id` that assume an active version -
  or those readers alone (the record's index crystal, the graft runner, `_is_selected_unless_cleaned`); regression
  tests; the system documents (the SpellIndex Mutation Surface, a failure mode) with their indexes and the graph;
  the release note; one notch; the rebuild last.
- DEPENDENCIES: EPIC-2026-10-17-correctness_defects; the probe and its runs (Artifact Links);
  STORY-2026-10-17-minted_index_missing_from_frame_registry (the same seam: one patch can carry both);
  STORY-2026-10-17-restore_drops_separated_parked_version (the restore and graft lanes for a parked-only index).
- EXIT_GATE: probe G2 brings French back parked (S5's answer, with S5's graft lane), and the live minted index no
  longer names French as selected (or no reader treats that as active, per the answer); G1, G3 and G4 unchanged;
  regression tests pass with the GIL off and on; docs, notch and the rebuild with both checks OK.
- FAILURE_ESCALATION: DECISION_REQUEST for the open question; CONFLICT while spellbook.py is held, or if the S4 fix
  lands first with another shape for the minted index.

## Requirements (Functional)
- No index names a parked version as the version it selects: after `remove_from_spell_index`, the minted index's
  selection does not make its parked member read as active to any reader (the record, a graft,
  `_is_selected_unless_cleaned`, which is documented to answer False for a parked member).
- A notch inside the minted index still makes its member active, and from then on the index selects it.
- A graft of the minted index's record never binds the parked member active.

## Requirements (Non-Functional)
- `selected_spell_id` is the compiler's hottest fingerprint read; answer (a) must keep that read lock-free and cheap,
  and the patch must enumerate its readers before changing what it may return.

## Scope Boundaries
- In scope: the selection of the index `remove_from_spell_index` mints, and what readers make of it.
- Out of scope: the frame registration of that index (S4); rebuilding it parked through restore or graft (S5); the
  throwaway index Bind mints inside `bind_inactive`, which never outlives the call.

## State Transition Event
- from_state: ready
- to_state: done
- transition_reason: withdrawn on the owner's ruling (chat 2026-10-17): not a defect - moving a version is the
  agent's call and making it active takes a notch (DECISION note). Filed draft -> ready at 2026-10-17T21:47:06Z.

## Dependencies / Related Work
- STORY-2026-10-17-minted_index_missing_from_frame_registry (same seam).
- STORY-2026-10-17-restore_drops_separated_parked_version (restore drops the version; graft activates it).

## Tasks (Implementation Checklist)
- [x] Task: the owner's answer on the open question (2026-10-17: not a defect; withdrawn, DECISION note).
- [ ] Task: patch docs for the seam; the owner's approval (not needed: withdrawn).
- [ ] Task: the fix with symptom-named regression tests, docs, notch and the rebuild last (not needed: withdrawn).
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- After `remove_from_spell_index(spell_id=French)`: the minted index does not report French as active - to the
  record, to `_is_selected_unless_cleaned(French)` (False) and to a graft.
- Grafting that index's record into a host gives French parked there (S5's lane), never active.
- After a notch to French inside the minted index, the index selects French as today.

## Validation / Test Plan
- Regression tests named for the symptom, e.g. `test_a_minted_index_does_not_select_its_parked_version` and
  `test_graft_of_a_parked_only_index_does_not_activate_its_version`; GIL off and on; the probe re-run. Not run: no
  fix exists yet.

## UX / API / Data Notes
- Visible today: `minted_index.selected_spell_id` returns the parked version's spell_id, the captured graft record's
  `index_payload["selected_spell_id"]` names it while its member's `custody_state` is "inactive", and
  `graft_index` reports `members_bound: 1, members_parked: 0` with the version active in the host.

## Risks / Mitigations
- Answer (a) changes what `selected_spell_id` may return; every reader must be checked, the compiler's included.
  Answer (b) keeps the field and moves the truth to the readers, which can drift again.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Should the index `remove_from_spell_index` mints (a) select nothing until a notch makes its member active
  (recommended: the index then says what is true, and the notch already handles an index with no active version),
  or (b) keep naming its member while the record, the graft and the release resolver check the Book's active map
  instead of trusting the selection?
  Answered (owner, 2026-10-17T23:25:30Z): neither - not a defect: "if you go into a [...] spell index and you move
  the version [...] then its not my [...] problem you gotta use notch" (DECISION note).

## Decision Log
- 2026-10-17T21:47:06Z: filed under EPIC-2026-10-17-correctness_defects from sweep A12 (Notes).
- 2026-10-17T21:55:46Z: S5's question answered by the owner (rebuild parked); G2's criterion narrowed (FACT note).
- 2026-10-17T23:25:30Z: the owner ruled it not a defect - moving a version is the agent's call, activation takes a
  notch; withdrawn (DECISION note).

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/correctness_defects_20261017/probes/probe_graft_parked_members.py (case G2, with G1 and G3 as controls)
  - artifacts/correctness_defects_20261017/runs/probe_graft_parked_members_gil0.txt
  - artifacts/correctness_defects_20261017/runs/probe_graft_parked_members_gil1.txt
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: withdrawn with no fix; the probe and its runs stay rowed under
  STORY-2026-10-17-restore_drops_separated_parked_version (G2) and
  STORY-2026-10-17-staged_version_releases_active_signature (G4)

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - the selection of the index remove_from_spell_index mints
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose and evidence (the probe); filed 2026-10-17T21:47:06Z.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-17T21:47:06Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The defect, read whole and proven on 0.2.8252. `_apply_remove_from_index` mints `SpellIndex(initial_id=
    spell_id)`, whose constructor makes its one member the selection, and leaves it so while the member stays parked
    in the Book. `selected_spell_id` is documented as "the active spell's id" and `_is_selected_unless_cleaned` as
    answering False for a parked member; for the minted index both name the parked version. The record's index
    crystal captures that selection, and `GraftRunner.run` (fresh-index mode) binds the selected member active and
    parks only the others. Probe G2: French separated into the minted index (parked in the Book); the live index
    selects French; the record says selected French with French's custody "inactive"; the graft reports one bound,
    none parked, and the host holds French active. G1 and G3 graft members of a registered index right. Identical
    with the GIL off and on.
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
  IMPACT: A parked version comes back active from a graft; the index and the Book disagree on what is active.
  NEXT: The owner's answer on the open question (and S5's), then patch docs for the seam.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-17T21:55:46Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: S5's open question is answered (owner, chat 2026-10-17: "we restore what should be restored"): a parked-only
    index is rebuilt parked by a restore and by a graft. So G2's exit criterion is "French comes back parked", not a
    refusal; the graft's lane for it is S5's, and this story keeps the selection the record and the graft read.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-17_restore_drops_separated_parked_version_story.md:94-98
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_graft_parked_members_gil0.txt:7-12
  IMPACT: One answer left for this story (its own open question).
  NEXT: The owner's answer on this story's open question.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-17T23:25:30Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner ruled on this story (chat 2026-10-17): "if you go into a [...] spell index and you move the version
    [...] then its not my [...] problem you gotta use notch". Not a defect: moving a version with
    `remove_from_spell_index` is the agent's call and making it active takes a notch, so the split-off index naming
    its parked member as its selection stays as it is; the story is withdrawn with no fix and no notch. What his
    rule does cover - a graft activating that parked member without a notch (G2) - is already the graft lane of
    STORY-2026-10-17-restore_drops_separated_parked_version, which now decides from each member's recorded custody
    instead of the selection. melder_0 tells the owner so in this turn's reply; his word can override.
  EVIDENCE:
  - context_compass/tickets/stories/completed/2026-10-17_minted_index_selects_its_parked_version_story.md:107-112
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_graft_parked_members_gil0.txt:7-12
  IMPACT: The story closes as withdrawn; S5 carries the graft side; melder_1's files lose one story.
  NEXT: None for this story.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Closure Confirmation
- [x] Work walkthrough shared with user
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
- Scope: the index `remove_from_spell_index` mints names its parked member as its selection (Notes, probe G2).
- State: done - withdrawn on the owner's ruling (2026-10-17): not a defect; moving a version is the agent's call and
  making it active takes a notch. No fix, no notch; nothing edited.
- Next: none here. The graft side (a graft activating the parked member without a notch) stays in
  STORY-2026-10-17-restore_drops_separated_parked_version, whose lanes read each member's recorded custody.

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
