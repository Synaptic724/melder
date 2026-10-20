# Story: restore_drops_separated_parked_version - a restore rebuilds a parked version alone in its own index

## Metadata
- Story ID: STORY-2026-10-17-restore_drops_separated_parked_version
- Epic: EPIC-2026-10-17-correctness_defects
- Status: ready
- Owner: user
- Agent Name: unassigned
- Agent Role: UNKNOWN
- Priority: p2
- Created: 2026-10-17T20:36:54Z
- Updated: 2026-10-17T23:25:30Z

## User Narrative
As an agent who separated a version into its own index with `remove_from_spell_index` and checkpointed the world, I
want a restore of that checkpoint to rebuild the version, parked in an index of its own, so that the restored world
holds every version the recorded one held.

## Value / MRP Alignment
A restore rebuilds structure (owner ruling: structure is the contract; a restore rebuilds structure with fresh
identities). The record already captures the separated version and its index; the restore drops the version and
still calls itself complete, so the restored structure is wrong while the report reads as success.

## Ticket Contract
- ENTRY_GATE: the owner schedules the story and assigns an agent (the open question was answered on 2026-10-17); an
  active board row; component patches for the restore engine's staged lane and the graft runner's fresh-index lane.
- EXECUTION_BOUNDARY: `RestoreEngine` (the staged lane: `_bind_one_staged`, `_live_index_for`, or a step after
  them) - rebuild a recorded index whose members are all parked through public verbs, mapping its identity - and
  `GraftRunner`'s fresh-index lane, which parks such members instead of binding the recorded selection active (G2).
  Both lanes decide from each member's recorded custody: the selection of such an index names its parked member,
  and that stays (STORY-2026-10-17-minted_index_selects_its_parked_version, withdrawn). Regression tests; system
  docs with their indexes and the graph; the release note; one notch; the rebuild last.
- DEPENDENCIES: EPIC-2026-10-17-correctness_defects; the probe, its targets and runs (Artifact Links);
  STORY-2026-10-17-minted_index_missing_from_frame_registry (a rebuilt minted index must also be known to the frame);
  STORY-2026-10-17-staged_version_releases_active_signature (staging during a restore releases the sibling's claim).
- EXIT_GATE: the probe's R2 rebuilds French parked in its own index with no shortfall for it; R1 and R3 unchanged;
  regression tests pass with the GIL off and on; docs, notch and the rebuild with both checks OK.
- FAILURE_ESCALATION: CONFLICT if a public verb route needs a file another lane holds.

## Requirements (Functional)
- A restore of a record holding an index whose members are all parked rebuilds that index in the same Book, with
  every member parked and the recorded index identity mapped to the new one - through public verbs only (for example
  staging each member onto a live anchor of its Book, then separating it with `remove_from_spell_index`).
- The report counts the members as staged and files no `staged_member_anchor_index_not_rebuilt` shortfall for them.
- A graft of such an index's record (fresh-index mode) rebuilds its members parked in a fresh index of the host
  Book, never active, and its report counts them as parked.

## Requirements (Non-Functional)
- All-or-nothing stays: a failure while rebuilding such an index tears the restore down like any other stage.

## Scope Boundaries
- In scope: the restore and the graft of parked-only indexes.
- Out of scope: the claims and registry those verbs leave behind (the sibling stories); the record format.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: the defect is proven on 0.2.8251 by a probe through a real checkpoint, flush, boot and restore,
  GIL off and on (Notes); one open question for the owner.

## Dependencies / Related Work
- STORY-2026-10-17-minted_index_missing_from_frame_registry.
- STORY-2026-10-17-staged_version_releases_active_signature.

## Tasks (Implementation Checklist)
- [x] Task: the owner's answer on the open question (2026-10-17: restore what should be restored; DECISION note).
- [ ] Task: patch docs for the restore engine's staged lane; the owner's approval.
- [ ] Task: the fix with symptom-named regression tests, docs, notch and the rebuild last.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- Restoring R2's checkpoint gives a Book with English active and French parked, French in an index of its own whose
  recorded identity maps to it, and no shortfall naming French.
- Grafting the minted index's record (G2) gives the host French parked in an index of its own, none active.
- A world whose separated version was then notched active (R3) and a plain staged world (R1) restore as before.

## Validation / Test Plan
- Regression tests named for the symptom, e.g. `test_restore_rebuilds_a_parked_version_separated_into_its_own_index`;
  GIL off and on; the probe re-run.

## UX / API / Data Notes
- No public signature changes. Visible today: `load_checkpoint` returns status "complete" with the shortfall
  "staged_member_anchor_index_not_rebuilt: <index id>", and the version is gone from the rebuilt Book.

## Risks / Mitigations
- Rebuilding by staging then separating goes through `bind_inactive`, which releases a sibling's claim until
  STORY-2026-10-17-staged_version_releases_active_signature lands; land that one first or heal it in the test.
- The restore's selection stage (`_enforce_selections`) notches a rebuilt index whose live selection differs from
  the recorded one, and a parked-only index's recorded selection is its parked member: the rebuild must not reach
  that notch, or the member comes back active.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Is a parked-only index meant to survive a restore? The record captures it today; if it is not meant to, the
  record should stop capturing it and the report should say why - the owner's call.
  Answered (owner, 2026-10-17T21:55:46Z): "I think we restore what should be restored" - it is rebuilt
  parked, by a restore and by a graft (DECISION note).

## Decision Log
- 2026-10-17T20:36:54Z: filed under EPIC-2026-10-17-correctness_defects from sweep A5 (Notes).
- 2026-10-17T21:55:46Z: the owner answered the open question - restore what should be restored: a parked-only
  index is rebuilt parked by a restore and by a graft (DECISION note).
- 2026-10-17T23:25:30Z: STORY-2026-10-17-minted_index_selects_its_parked_version withdrawn (owner: not a defect); the
  selection stays, so both lanes read each member's recorded custody (FACT note).

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/correctness_defects_20261017/probes/probe_restore_staged_structure.py (cases R1-R3)
  - artifacts/correctness_defects_20261017/probes/restore_targets.py
  - artifacts/correctness_defects_20261017/runs/probe_restore_staged_structure_gil0.txt
  - artifacts/correctness_defects_20261017/runs/probe_restore_staged_structure_gil1.txt
  - artifacts/correctness_defects_20261017/probes/probe_graft_parked_members.py (case G2: the graft activates the separated version; FACT note)
  - artifacts/correctness_defects_20261017/runs/probe_graft_parked_members_gil0.txt
  - artifacts/correctness_defects_20261017/runs/probe_graft_parked_members_gil1.txt
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: the probe is re-run at the fix and kept as the defect's reproducer

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - restore of a parked version separated into its own index
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose and evidence (the probe); filed 2026-10-17T20:36:54Z.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-17T20:36:54Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The defect, read whole and proven on 0.2.8251. The restore replays a Book as: active binds, conjure, staged
    members onto live anchors (`_bind_one_staged`), selections. A staged member's anchor is found by
    `_live_index_for`, which translates a recorded index id only after one of its members was bound active; an
    index whose members are all parked - the index `remove_from_spell_index` mints - never gets one, so the member
    is skipped with the shortfall "staged_member_anchor_index_not_rebuilt: <index>" and the report still says
    "complete". The record does hold it: `_apply_remove_from_index` emits both index snapshots. Probe R2 (record,
    seal, flush, fresh boot, reload, restore): the recorded Book has English active and French parked in its own
    index; the rebuilt Book has English alone. Identical with the GIL off and on.
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1915-2003
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2201-2269
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2400-2441
  - src/melder/aether/spellbook/spellbook.py:4271-4356
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_restore_staged_structure.py:1-160
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_restore_staged_structure_gil0.txt:1-18
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_restore_staged_structure_gil1.txt:1-18
  IMPACT: A restored world silently holds fewer versions than the recorded one, under a "complete" report.
  NEXT: The owner's answer on the open question, then patch docs for the staged lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-17T21:47:06Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The graft side of this gap (sweep A12, probe G2). A graft of the index `remove_from_spell_index` minted does
    not drop French - it binds French ACTIVE in the host, because the minted index records French as its selection
    (STORY-2026-10-17-minted_index_selects_its_parked_version) and a fresh-index graft binds the selected member
    active and parks only the others. So neither restore nor graft rebuilds a parked-only index as parked today:
    restore drops it, graft activates it. Identical with the GIL off and on.
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader_system/graft_runner.py:230-330
  - src/melder/crystallizer/crystal_loader_system/graft_runner.py:375-489
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_graft_parked_members.py:1-152
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_graft_parked_members_gil0.txt:7-12
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_graft_parked_members_gil1.txt:7-12
  IMPACT: The open question covers both lanes: a fix for "survives a restore" should give the graft runner the same
    parked-only lane, and the selection fix decides what the graft's anchor rule meets.
  NEXT: The owner's answer on the open question.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-17T21:55:46Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The open question is answered (owner, chat 2026-10-17): "I'm not sure whats the most correct thing? I think
    we restore what should be restored", with melder_0's recommendation given in reply: a version separated into an
    index of its own is structure an agent made with a public verb (`remove_from_spell_index`) and the record already
    holds it, and a restore rebuilds structure (Runtime Model), so it should be restored: a restore rebuilds it parked
    in a fresh index of its Book, and a graft of that index rebuilds it parked, never active (G2 today activates it).
    The "stop recording it" branch is out. The graft runner joins the execution boundary.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:26-34
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2201-2269
  - src/melder/crystallizer/crystal_loader_system/graft_runner.py:230-330
  - src/melder/crystallizer/crystal_loader_system/graft_runner.py:375-489
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_graft_parked_members_gil0.txt:7-12
  IMPACT: The ENTRY_GATE's question is met; the fix covers both lanes and depends on S10 for the graft's anchor rule.
  NEXT: The owner's scheduling; then patch docs for the restore engine's staged lane and the graft runner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-17T23:25:30Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: STORY-2026-10-17-minted_index_selects_its_parked_version is withdrawn (owner, chat 2026-10-17: not a defect -
    moving a version is the agent's call and making it active takes a notch), so the selection of a parked-only index
    keeps naming its parked member. Both lanes of this story therefore decide from each member's recorded custody,
    which the graft record carries per member (`custody_state`), not from the recorded selection: today the graft's
    fresh-index lane binds the selected member active, and the restore's selection stage notches any rebuilt index
    whose live selection differs from the record, so a rebuilt parked-only index must not reach that notch.
  EVIDENCE:
  - src/melder/crystallizer/persistence/persistence_profile.py:900-969
  - src/melder/crystallizer/crystal_loader_system/graft_runner.py:230-330
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2271-2321
  IMPACT: This story enforces the owner's rule on the graft and restore side: a parked member comes back parked, and
    only a notch makes it active.
  NEXT: The owner's scheduling; the patch docs for both lanes key on the members' recorded custody.
  REREAD: REQUIRED
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
- Scope: a restore and a graft rebuild a parked version that sits alone in its own index, parked (Requirements).
  Defect proven on 0.2.8251 (Notes); probes, targets and runs in Artifact Links.
- State: ready, unassigned; filed by melder_0 under EPIC-2026-10-17-correctness_defects; the owner answered its
  question (restore and graft rebuild a parked-only index parked). The fix sits in restore_engine.py and
  graft_runner.py, which no other lane holds.
- Next: (1) the owner's scheduling; (2) patch docs; (3) the fix, its tests, docs, notch and the rebuild.

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
