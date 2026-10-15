# Task: Investigate a root torn down without leaving its cluster: it stays a member and the cluster cannot recover

## Metadata
- Task ID: TASK-2026-10-14-investigate_cluster_member_teardown_without_leave
- Story: none - D1 of EPIC-2026-10-14-slotted_lifetime_ownership_fixes (opened by
  TASK-2026-10-14-audit_slotted_lifetime_ownership, done)
- Status: review
- Owner: user
- Agent Name: melder_1
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-14T18:40:43Z
- Updated: 2026-10-15T00:07:24Z

## Objective
Melder never reconciles cluster membership with root teardown: `Conduit._cleanup_normal_conduit` cleans the
root's store and drops its facade but leaves no cluster, so the cluster keeps the dead root in `members`, and
as `master_conduit_id` when it led. Proven on 0.2.8235 by the audit probe: after a member is torn down,
`unelect_leader` raises AttributeError part-way (after unbinding whichever facades came first in set order),
`elect_leader` then refuses because a leader is still recorded, and a surviving member's cluster meld fails
or still resolves depending on the hash seed (c3); after the leader is torn down while elected, the cluster
keeps it as master and member and the leader's store has disposed the instance the members hold (c1).
`delete_cluster` pops the cluster before it unelects, so the same raise would leave it uncleaned. Find the
root cause and every verb that walks members, and lay out fix options for the owner's epic.

The owner's rule this is checked against: the cluster owns its membership and its instance; one member's end
must not wedge the cluster or dispose what the other members still hold.

## Ticket Contract
- ENTRY_GATE: the epic's board row routes it; the reproducer is rerun on the current tree; red tests fail before
  any src edit; the epic's patch docs are written, linked and mapped.
- EXECUTION_BOUNDARY: the code paths below, the fix, its tests and docstrings (owner directive 2026-10-14: fix it
  under EPIC-2026-10-14-slotted_lifetime_ownership_fixes); system docs, release note and notch with the epic.
- DEPENDENCIES: TASK-2026-10-14-audit_slotted_lifetime_ownership (the probe and its runs);
  EPIC-2026-10-14-many_child_follows_holder (0.2.8235).
- EXIT_GATE: root cause recorded; red tests red before and green after the fix, GIL off and on; the probe case
  clean; no warm meld path change; the owner accepts.
- FAILURE_ESCALATION: DECISION_REQUEST for every behaviour that is a design choice; BLOCKER if the reproducer no
  longer fails on the current tree (record it and stop).

## Scope Boundaries
- In scope: the defect named in the objective, its code paths and every caller that shares the cause.
- Out of scope: the fix itself; the other audit findings (their own tasks).

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: opened from the audit with a reproducer that fails on 0.2.8235, GIL off and on (owner directive,
  chat 2026-10-14: "make a task to investigate it and then we'll turn it into an epic").
- from_state: ready
- to_state: in_progress
- transition_reason: the epic's tranche reached D1 (D6 verdict recorded, 2026-10-14T19:03:12Z).
- from_state: in_progress
- to_state: review
- transition_reason: the fix landed with its red tests green GIL off and on; the lane's full tree is green GIL off and
  on at 0.2.8240 and the change is promoted into the system docs (epic Notes 2026-10-14T23:39:45Z and
  2026-10-15T00:00:12Z); the owner accepts.


## Steps / Checklist
- [x] Read root and frame teardown and every cluster verb that walks `members` (elect, unelect, join, leave,
      delete, share refresh); list each with what it does on a dead member.
- [x] Write red tests from the probe's c1 and c3 (member teardown then unelect, elect, delete and a member meld;
      leader teardown then a member meld and a new election).
- [x] Lay out fix options with their tradeoffs (leave-on-teardown, dissolve-on-leader-teardown, a walk that
      tolerates dead members, transactional membership) and record them for the owner.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Root cause with evidence, red tests, and fix options for the owner's epic.

## Files / Paths Impacted
- `src/melder/aether/conduit/conduit.py` (root teardown)
- `src/melder/aether/conduit/conduit_cluster.py`
- `src/melder/aether/aetheric_frame/conduit_cloud.py`
- `tests/` (red tests, when the investigation runs)

## Validation
- Reproducer run on 0.2.8235 (Python 3.14.7t, GIL off and on, identical): see Notes.
- Not run: anything else (the investigation has not started).
- Reproduce (from a tree root with src/ and tests/):
  `PYTHONPATH=src:. python context_compass/artifacts/slotted_lifetime_audit_20261014/probe_lifetime_owners.py c1 c3`

## Risks / Rollback Notes
- Investigation only; nothing to roll back.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without delegated acceptance or reserved-owner disposition and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Board sync completed for successor routing or closure anchor update.

## Open Questions
- Answered (owner, 2026-10-14: "a torn down root shouldn't live in a cluster"): a root's teardown
  leaves its cluster, and a leader's teardown leaves it inert and electable (0.2.8236).
- Answered by D2 (0.2.8237): the cluster's instances live in its team store and survive leader changes.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/slotted_lifetime_audit_20261014/ (the probe and its runs, shared with the audit task)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: decided when the owner's epic closes

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - UNKNOWN
- CONTEXT_TOPICS:
  - cluster membership after a member's or the leader's teardown
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): melder_1 (synaptic_python_developer); prose and evidence; the whole ticket; initial revision
  2026-10-14T18:40:43Z; the reproducer is the audit's probe. The rule and the directive are the owner's.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-14T18:40:43Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Opened from TASK-2026-10-14-audit_slotted_lifetime_ownership with a reproducer: probe case(s)
    c1 c3 fail the owner's rule on 0.2.8235 as described in the Objective, with identical output GIL off and
    on. The code paths below were read in full during the audit; the root-cause analysis, red tests and fix options
    are this task's work.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:967-1100
  - src/melder/aether/conduit/conduit_cluster.py:543-632
  - src/melder/aether/conduit/conduit_cluster.py:637-948
  - src/melder/aether/aetheric_frame/conduit_cloud.py:800-916
  - context_compass/artifacts/slotted_lifetime_audit_20261014/runs/probe_lifetime_owners_all_gil0.txt:2-10
  - context_compass/artifacts/slotted_lifetime_audit_20261014/runs/probe_lifetime_owners_all_gil0.txt:20-23
  - context_compass/artifacts/slotted_lifetime_audit_20261014/runs/probe_c3_hash_seeds.txt:1-31
  - context_compass/artifacts/slotted_lifetime_audit_20261014/probe_lifetime_owners.py:1-608
  IMPACT: The defect is real on today's tree; the owner can turn this task into an epic.
  NEXT: Rerun the reproducer on the current tree, then read the paths in Steps and record the root cause.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-14T18:55:12Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner turned the audit's tasks into one fix lane and put it first ("all these need to be fixed
    go ahead and target all these fixes since you have context first"); this task is now the epic's D1
    and covers the fix as well as the investigation (Ticket Contract updated).
  EVIDENCE: context_compass/tickets/epics/2026-10-14_slotted_lifetime_ownership_fixes_epic.md:147-159
  IMPACT: Investigation, red tests and the fix land here; docs, notes and the notch go with the epic's pass.
  NEXT: Wait for the epic's tranche order (D6 verdict, patch docs), then rerun the reproducer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-14T19:09:12Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Root cause (code re-read in full after compaction). `Conduit._cleanup_normal_conduit` never touches cluster
    membership: it cleans the root's own facade, ward, spaces and store (a leader's store holds the cluster instance),
    pops the root from the frame registry the cluster borrows, and cleans its DevOps identity, which drops only the
    DevOps conduit->cluster mirror. `ConduitCluster.members`, `master_conduit_id` and `shared_spells` keep the dead
    id. Every member walk then dereferences `_resolve_conduit_by_id(...)` without a None check
    (`bind_elected_leader`, `unbind_elected_leader`, `bind_member` on a dead leader), so unelect raises part-way,
    elect refuses or raises, a join into the cluster raises, and `delete_cluster` pops the cluster before its
    unelect raises, leaving it uncleaned. Facts the fix can use: frame teardown cleans every root before the cloud and
    DevOps (so a teardown-time leave can still run transactions); `CLUSTER_LEAVE` has no posture gate (only the
    cloud's direct API checks posture); the root ward's cleanup already severs every peer contract; and the DevOps
    registry holds an O(1) conduit->cluster index (`get_cluster_objects_for_conduit`), while
    `ConduitCloud.get_clusters_for_conduit` scans every cluster.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:967-1106
  - src/melder/aether/conduit/conduit_cluster.py:543-632
  - src/melder/aether/conduit/conduit_cluster.py:637-807
  - src/melder/aether/conduit/conduit_cluster.py:875-948
  - src/melder/aether/aetheric_frame/conduit_cloud.py:800-951
  - src/melder/aether/aetheric_frame/aetheric_frame.py:283-356
  - src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py:1171-1307
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:251-310
  IMPACT: The fix is a teardown-time leave found by key (no cluster scan), run at the start of root teardown while the
    root, its gate and its facade are still live; the cloud's join check can use the same O(1) index.
  NEXT: Probe a suspected pre-existing order bug: `remove_conduit_from_cluster` calls `remove_member` (which pops
    the leaver's `shared_spells`) before `handle_leave`, so the leaver's roots may never be unshared from peers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T19:10:02Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: A second, pre-existing leave defect in the same path is proven: `ConduitCloud.remove_conduit_from_cluster`
    calls `remove_member` (which pops the leaver's `shared_spells` entry) before `handle_leave`, whose first unshare
    loop reads that entry, so the leaver's shared roots stay contracted to every remaining member after an explicit
    leave. Probe (0.2.8235, GIL off and on, identical): after the leave the peer still holds the leaver's root (True);
    controls: a plain link contracts nothing (False), and `handle_leave` before `remove_member` unshares it (False).
    Folded into D1 because the teardown leave runs the same exit: one shared exit helper with the corrected order serves
    the cloud verb and root teardown.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/conduit_cloud.py:876-915
  - src/melder/aether/conduit/conduit_cluster.py:380-395
  - src/melder/aether/conduit/conduit_cluster.py:543-632
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/probes/probe_cluster_leave_order.py:1-115
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/probe_cluster_leave_order_gil0.txt:1-6
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/probe_cluster_leave_order_gil1.txt:1-6
  IMPACT: D1's fix covers explicit leave and teardown leave through one ordered exit; a red test pins the unshare.
  NEXT: Re-read the cluster-instance store routes (meld doors, site-plan cluster store read, purge authority) for D2.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T19:43:30Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Red tests written and run on 0.2.8235 (scratch tree, Python 3.14.7t, GIL off and on, identical): the new
    module test_conduit_integration_cluster_member_lifetime.py holds four D1 tests and all four fail for the defect,
    not the test - a torn-down member stays in `get_members()`; `delete_cluster` after a member teardown raises
    AttributeError "'NoneType' object has no attribute '_cluster_creations'" from `unbind_elected_leader`
    (conduit_cluster.py:726); a torn-down leader stays `master_conduit_id`; after `remove_conduit_from_cluster` the
    remaining member still holds the leaver's root through `get_spell_in_contracts`. The module's two controls (frame
    teardown disposes the cluster instance once; only the elected leader purges) pass.
  EVIDENCE:
  - tests/integration/melder/conduit/test_conduit_integration_cluster_member_lifetime.py:167-232
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/red_d1_d2_cluster_lifetime_0_2_8235_gil0.txt:1-54
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/red_d1_d2_cluster_lifetime_0_2_8235_gil1.txt:1-54
  IMPACT: The entry gate for D1's src edit is met (red tests, patch docs read in order after re-onboarding, mapping in
    the epic's 19:31:30Z PLAN note).
  NEXT: Land D1 per the cluster-exit patch: `_leave_cluster_for_teardown`, `release_member`/`drop_member`, the cloud's
    ordered leave and O(1) cluster lookup, the D6 docstring; notch 0.2.8236.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T19:57:49Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: D1 implemented per the cluster-exit patch and validated on the scratch tree (0.2.8235 + D1, Python 3.14.7t,
    GIL off): `Conduit._leave_cluster_for_teardown` runs first in `_cleanup_normal_conduit` (DevOps index read; live
    frame -> `ConduitCluster.release_member`, logged fallback or frame teardown -> `drop_member`);
    `release_member` = `handle_leave` then `remove_member`; `drop_member` = unbind all facades when it leads, then
    `remove_member` and its own facade; the cloud's leave calls `release_member`; `get_clusters_for_conduit` reads the
    registry index and names clusters through a new cloud-owned `_cluster_names_by_id` map (kept in create/delete/
    cleanup) instead of reading a cluster object, so a cluster cleaned concurrently is never touched; the D6 docstring
    paragraph is on `upgrade_to_normal`. Results: the four D1 red tests and a new teardown-fallback test pass, the four
    D2 tests still fail as expected, controls pass; unit_aether 4207 passed; comp_aether 1352 passed (1 xfailed);
    int_aether 785 passed (5 xfailed); int_conduit 283 passed plus the 4 D2 reds. Two cloud unit tests pinned the
    defect (the remove-then-leave order and the member-set scan) and were updated with the reason in their docstrings;
    new unit tests cover the ordered exit, the drop and the index lookup. The release example passes on D1 and fails on
    0.2.8235 (a torn-down leader stays recorded).
  EVIDENCE:
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/landing/apply_d1_0_2_8236.py:1-470
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/landing/tests_d1_0_2_8236.py:1-316
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/d1_scratch_gil0.txt:1-5
  IMPACT: D1 is ready to land as 0.2.8236 (src, tests, release note); D2 starts from this tree.
  NEXT: Land D1 into the working tree (apply scripts, notch 0.2.8236, release-note section), confirm the tree equals
    the scratch tree, run the D1 tests GIL on, then start D2.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-15T00:07:24Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Status to review. D1 (0.2.8236) holds at the end of the lane's pass: the audit probe's c1 and c3 show a
    torn-down member or leader no longer recorded in its cluster (unelect and elect work, the member's meld serves the
    same leaf), the full tree is green GIL off and on at 0.2.8240, and the system docs carry the cluster-exit
    invariant, its failure mode and the ConduitCluster and ConduitCloud rules.
  EVIDENCE:
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/probe_lifetime_owners_all_0_2_8240_gil0.txt:1-22
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/full_tree_0_2_8240_gil0.txt:1-28
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/full_tree_0_2_8240_gil1.txt:1-20
  - context_compass/system_docs/src_architecture.md:1000-1014
  - context_compass/system_docs/src_architecture.md:1785-1790
  - context_compass/system_docs/src_components.md:6191-6243
  - context_compass/system_docs/tests_components.md:1407-1415
  IMPACT: The task waits only for the owner's acceptance; closure goes with the epic.
  NEXT: The owner accepts or redirects; then close with the epic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
In review (2026-10-15). Landed as 0.2.8236: root teardown leaves its cluster first
(`Conduit._leave_cluster_for_teardown`: `ConduitCluster.release_member` while the frame lives, `drop_member` in
frame teardown or after a failed exit), the cloud's leave runs the ordered exit and unshares the leaver's roots,
and the cloud's cluster lookup reads the DevOps index and names clusters through `_cluster_names_by_id`. Red tests
green GIL off and on; the lane's full tree green at 0.2.8240 GIL off and on; promoted into src_architecture,
src_components and tests_components. Remaining: the owner's acceptance; commit and push are the owner's.

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
