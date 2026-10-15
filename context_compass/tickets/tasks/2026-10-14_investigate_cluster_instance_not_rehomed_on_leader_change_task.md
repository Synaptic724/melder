# Task: Investigate a cluster instance owned by the elected leader conduit and left behind by a leader change

## Metadata
- Task ID: TASK-2026-10-14-investigate_cluster_instance_not_rehomed_on_leader_change
- Story: none - D2 of EPIC-2026-10-14-slotted_lifetime_ownership_fixes (opened by
  TASK-2026-10-14-audit_slotted_lifetime_ownership, done)
- Status: review
- Owner: user
- Agent Name: melder_1
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-14T18:40:43Z
- Updated: 2026-10-15T00:07:24Z

## Objective
A `unique_per_conduit_cluster` instance lives in the elected leader's own conduit store, which the members'
facades only reference; v1 dissolves the cluster when the leader leaves, with no re-home ("owner-leave
dissolves the cluster to inert -- no re-home"). Proven on 0.2.8235 (c2): with a leader that does not own the
spell, the leader leaving and a member being elected builds a second instance; the first stays in the departed
leader's store, a member's per-conduit holder keeps it, and the departed leader's teardown disposes it while
the member still serves that holder. Under the owner's rule the cluster, not its current leader, owns the
instance. Find where the instance should live and what a leader change must do to it and to the holders built
over it, and lay out options for the owner's epic.

The owner's rule this is checked against: the object a lifetime names owns the instance - for
`unique_per_conduit_cluster`, the cluster.

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
- transition_reason: the epic's tranche reached D2 with D1 (cluster code re-read, 2026-10-14).
- from_state: in_progress
- to_state: review
- transition_reason: the fix landed with its red tests green GIL off and on; the lane's full tree is green GIL off and
  on at 0.2.8240 and the change is promoted into the system docs (epic Notes 2026-10-14T23:39:45Z and
  2026-10-15T00:00:12Z); the owner accepts.


## Steps / Checklist
- [x] Read the store selection for cluster sites, `ClusterCreations`, elect/unelect/leave and the holders'
      invalidation paths; record what a leader change does to the instance and to holders over it.
- [x] Write red tests from the probe's c2 (leader leaves, a member is elected, the departed leader is torn down).
- [x] Lay out options (a cluster-owned store; re-homing the instance at election; disposing it and invalidating
      its holders at a leader change) with their lock and transaction costs, for the owner.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Root cause with evidence, red tests, and fix options for the owner's epic.

## Files / Paths Impacted
- `src/melder/aether/conduit/creations/cluster_creations.py`
- `src/melder/aether/conduit/conduit_cluster.py`
- `src/melder/aether/conduit/meld/conduit_meld.py` (cluster store selection)
- `tests/` (red tests, when the investigation runs)

## Validation
- Reproducer run on 0.2.8235 (Python 3.14.7t, GIL off and on, identical): see Notes.
- Not run: anything else (the investigation has not started).
- Reproduce (from a tree root with src/ and tests/):
  `PYTHONPATH=src:. python context_compass/artifacts/slotted_lifetime_audit_20261014/probe_lifetime_owners.py c2`

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
- Answered by the owner's directive to fix all of the audit's findings (2026-10-14) and landed as
  0.2.8237: the instance survives a leader change in a store the cluster owns and is disposed by the
  cluster's cleanup.
- Yes: `resolved_store()` still raises while no leader is elected, and the elected leader's id is the
  purge authority.

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
  - which object owns a unique_per_conduit_cluster instance across leader changes
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
    c2 fail the owner's rule on 0.2.8235 as described in the Objective, with identical output GIL off and
    on. The code paths below were read in full during the audit; the root-cause analysis, red tests and fix options
    are this task's work.
  EVIDENCE:
  - src/melder/aether/conduit/creations/cluster_creations.py:9-264
  - src/melder/aether/conduit/conduit_cluster.py:26-171
  - src/melder/aether/conduit/conduit_cluster.py:543-632
  - src/melder/aether/conduit/conduit_cluster.py:637-727
  - context_compass/artifacts/slotted_lifetime_audit_20261014/runs/probe_lifetime_owners_all_gil0.txt:11-19
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
    go ahead and target all these fixes since you have context first"); this task is now the epic's D2
    and covers the fix as well as the investigation (Ticket Contract updated).
  EVIDENCE: context_compass/tickets/epics/2026-10-14_slotted_lifetime_ownership_fixes_epic.md:147-159
  IMPACT: Investigation, red tests and the fix land here; docs, notes and the notch go with the epic's pass.
  NEXT: Wait for the epic's tranche order (D6 verdict, patch docs), then rerun the reproducer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-14T19:14:12Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Root cause (code re-read in full after compaction): `bind_elected_leader` and `bind_member` bind every
    member root's `ClusterCreations` facade to `leader._creations`, the leader conduit's own store, so the
    cluster instance's lifetime is the leader conduit's: a leader change leaves it in the departed leader's store
    (disposed at that conduit's teardown) and the next election builds a second one. Every emitted route reads the
    store through `meld._cluster_creations.resolved_store()` per call (door compiler, site-plan lowering, generalized
    and solo compilers), and the doors' probes and `meld_existing_spell` do the same, so a cluster-owned team store
    changes no generated code. The only reader of the store's owner id is purge authority
    (`ConduitMeld._get_purge_creations` compares `creations.owner_conduit_id` with the caller), so a cluster store
    needs the elected leader's id from the facade instead. Tests that pin the old representation
    (`resolved_store() is leader._creations`, one-argument `facade.bind(store)`) must change with the fix.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_cluster.py:637-767
  - src/melder/aether/conduit/creations/cluster_creations.py:1-264
  - src/melder/aether/conduit/meld/conduit_meld.py:209-262
  - src/melder/aether/conduit/meld/conduit_meld.py:820-872
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1520-1520
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:665-665
  - tests/component/melder/aether/conduit/test_conduit_component_cluster.py:811-812
  - tests/unit/melder/aether/conduit/test_conduit_cluster.py:1183-1280
  IMPACT: Fix shape: the cluster owns one `Creations` team store (scope id = cluster id); election binds facades to
    it and records the leader on the facade (purge authority); unelect, a leader's leave or teardown only unbind; the
    cluster's cleanup (deletion, frame teardown) disposes it. Warm meld paths unchanged.
  NEXT: Re-read transfer (execute, move/teardown of creations), contract invalidation and the many-child emission for
    D3-D5.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T19:22:48Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Fix shape chosen (epic F2; the alternatives were weighed against the owner's rule): the cluster owns one
    `Creations` team store (owner and scope id = the cluster id), built with the cluster. `bind_elected_leader` and
    `bind_member` bind each member facade to that store and record the elected leader's id on the facade;
    unelect, a leader's leave and a leader's teardown only unbind, so the instance and the holders over it survive a
    leader change and a later election serves the same instance; the cluster's cleanup (delete_cluster after its
    unelect, or the cloud at frame teardown) disposes the store and raises its disposal failures after finishing (the
    frame logs them, as it does for conduits). Purge authority stays "the elected cluster leader", read from the facade
    instead of the store's owner id; the error text is unchanged. Rejected: re-homing the instance into the next
    leader's store (nowhere to park it while the cluster is inert, so a leader teardown still disposes it under live
    holders) and disposing it at every leader change (disposes a dependency under live holders). The
    `describe_live_creation_status` label `cluster_leader` is kept (public diagnostics value).
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-14_slotted_lifetime_ownership_fixes_epic.md:82-95
  - src/melder/aether/conduit/meld/conduit_meld.py:1040-1078
  IMPACT: Changes ConduitCluster, ClusterCreations, ConduitMeld._get_purge_creations and ConduitCloud cleanup; no
    emitted code changes; tests pinning `resolved_store() is leader._creations` are updated with this reason.
  NEXT: Record D3-D5's shared mechanism after re-reading the transfer, invalidation and emission paths.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T19:43:30Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Red tests written and run on 0.2.8235 (scratch tree, Python 3.14.7t, GIL off and on, identical): four D2 tests
    in test_conduit_integration_cluster_member_lifetime.py fail for the defect - after the leader leaves and a member is
    elected, the member's meld builds a second instance; the leader's teardown runs the instance's `close` while a
    member's holder still holds it (closes 1); `delete_cluster` disposes nothing (closes 0); a failing `close` raises
    nothing from `delete_cluster`. The two controls pass: frame teardown disposes the instance exactly once, and only
    the elected leader may purge it (a member gets the "elected cluster leader" RuntimeError).
  EVIDENCE:
  - tests/integration/melder/conduit/test_conduit_integration_cluster_member_lifetime.py:235-329
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/red_d1_d2_cluster_lifetime_0_2_8235_gil0.txt:1-54
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/red_d1_d2_cluster_lifetime_0_2_8235_gil1.txt:1-54
  IMPACT: D2's entry gate is met; the controls pin what the team store must keep (frame teardown disposes once, purge
    authority follows the elected leader).
  NEXT: Land D1 first (0.2.8236), then the team store (0.2.8237) per the clusters patch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T20:11:27Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: D2 implemented per the clusters patch (team-store section) and validated on the scratch tree (D1 + D2,
    Python 3.14.7t, GIL off): `ConduitCluster` builds `_team_store = Creations(owner_conduit_id=cluster id, id=cluster
    id)`; `bind_elected_leader`/`bind_member` bind facades to it with the leader id (unresolvable leader -> RuntimeError);
    `ClusterCreations.bind(store, leader_conduit_id)` plus a `leader_conduit_id` property, cleared by `unbind`;
    `ConduitMeld._get_purge_creations` reads cluster purge authority from the facade (same refusal text, return type
    `Creations`); cluster cleanup disposes the store outside its lock and raises "Conduit cluster cleaned with disposal
    failures." last; the cloud raises its clusters' groups after finishing and the frame logs them; stale "leader's
    store" docstrings/comments in the meld doors, spellspace, Creations and the door compiler now say "team store"
    (emitted code unchanged: the door keeps its `leader_creations` local). Results: all ten lifetime tests pass;
    unit_aether 4214, comp_aether 1352 (1 xfailed), int_aether 785 (5 xfailed), int_conduit 288, comp_cryst 110,
    int_cryst 273 (3 xfailed). Eleven unit/component tests and three integration tests pinned the leader-conduit store
    (`resolved_store() is leader._creations`, one-argument `bind(store)`, the many-child cluster test disposing at the
    leader's teardown); each was updated with the reason in its docstring. The release example passes on D2 and fails
    on 0.2.8235 at the second-instance line.
  EVIDENCE:
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/landing/apply_d2_0_2_8237.py:1-914
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/landing/cluster_creations_new.py:1-301
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/landing/tests_d2_0_2_8237.py:1-596
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/d2_scratch_gil0.txt:1-8
  IMPACT: D2 lands as 0.2.8237 with a release-note section, the clusters guide and the example-25 wording; the
    0.2.8235 many-child note now names the cluster, not its leader, as the holder's keeper.
  NEXT: Land D2 in the working tree (apply, tests, notch script), confirm it equals the scratch tree, run GIL on, then
    read the creations, codegen and holder-children patch docs for D4/D5.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-15T00:07:24Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Status to review. D2 (0.2.8237) holds at the end of the lane's pass: the audit probe's c2 shows a re-election
    serving the original instance (no second one) and the departed leader's teardown no longer disposing it; r9 shows
    a cluster holder's child kept in the cluster's store; the full tree is green GIL off and on at 0.2.8240; the
    system docs carry the team-store invariant, the failure mode, the ConduitCluster rules and the Meld store
    selection.
  EVIDENCE:
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/probe_lifetime_owners_all_0_2_8240_gil0.txt:10-18
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/probe_lifetime_owners_all_0_2_8240_gil0.txt:74-79
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/full_tree_0_2_8240_gil0.txt:1-28
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/full_tree_0_2_8240_gil1.txt:1-20
  - context_compass/system_docs/src_architecture.md:987-999
  - context_compass/system_docs/src_architecture.md:1779-1784
  - context_compass/system_docs/src_components.md:6191-6220
  IMPACT: The task waits only for the owner's acceptance; closure goes with the epic.
  NEXT: The owner accepts or redirects; then close with the epic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
In review (2026-10-15). Landed as 0.2.8237: the cluster owns a `Creations` team store; election binds every member
facade to it with the leader's id (the purge authority), and a root joining while a leader is elected is bound
too; unelection, a leader's leave or teardown keep it; the cluster's cleanup disposes it once (`delete_cluster`
raises failures after deleting, frame teardown logs them). Red tests green GIL off and on; the lane's full tree
green at 0.2.8240; promoted into the system docs. Remaining: the owner's acceptance; commit and push are the
owner's.

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
