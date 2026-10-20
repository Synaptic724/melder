# Task: Audit every slotted lifetime against the owner's ownership rule and open one investigation task per defect

## Metadata
- Task ID: TASK-2026-10-14-audit_slotted_lifetime_ownership
- Story: none - standalone; follows EPIC-2026-10-14-many_child_follows_holder (fix 0.2.8235 in review)
- Status: done
- Owner: user
- Agent Name: melder_1
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-14T18:14:30Z
- Updated: 2026-10-14T18:54:21Z

- Completed: 2026-10-14T18:54:21Z
- Summary: Audited every slotted lifetime against the owner's ownership rule on 0.2.8235 with two probes (GIL off
  and on): `many` children follow their holder on every route; six defect groups (D1-D6) proven and opened as
  tasks, now under EPIC-2026-10-14-slotted_lifetime_ownership_fixes. No src change; no notch.

## Objective
The owner asked whether `unique_per_conduit`, `unique_per_conduit_cluster` and `unique_per_conduit_lineage` are "set
up properly" after 0.2.8235 and directed: "create tickets for each bug you find please make a task to investigate it
and then we'll turn it into an epic each bug you find" (chat 2026-10-14). The rule being audited is the owner's: the
object a lifetime names owns the instance and everything built for it, which therefore lives exactly as long as that
object - the spell's owning root for `unique`, the conduit for `unique_per_conduit`, the spellspace for
`unique_per_spell_space`, the lineage root for lineage, the cluster for cluster. Deliver a verdict per lifetime with
probe evidence, and one investigation task per proven defect for the owner to turn into an epic.

## Ticket Contract
- ENTRY_GATE: board row `slotted_lifetime_audit` routes here; the owner's directive is recorded; each claim is
  backed by a probe run or a full read of the code it describes before it is written as FACT.
- EXECUTION_BOUNDARY: read-only on `src/` and `tests/`; probes and their outputs under
  `artifacts/slotted_lifetime_audit_20261014/`; new investigation tasks under `tickets/tasks/`; this ticket's Notes.
  No source or test edits.
- DEPENDENCIES: TASK-2026-10-14-fix_many_child_follows_holder (0.2.8235, in review) and its route probe;
  EPIC-2026-10-14-many_child_follows_holder open questions 1-2 (purge, transfer), which this audit may turn into
  defects with evidence.
- EXIT_GATE: every slotted lifetime has a verdict for each event below, backed by a probe or by code read in full;
  every proven defect has its own investigation task; the owner has the summary.
- FAILURE_ESCALATION: DECISION_REQUEST where a behaviour is a design choice rather than a defect (the owner rules);
  BLOCKER if a probe cannot be built without changing src.

## Scope Boundaries
- In scope: the five slotted lifetimes and their `many` children under the events that end or change an owner -
  the melding scope's end (lesser pool return, spellspace exit), the owner root's teardown, a cluster leader change,
  lineage changes (link, sever, lesser upgrade), ownership transfer and purge - in automatic and dynamic worlds;
  Phase 6 ordering where a dependency's owner can end before its holder's.
- Out of scope: fixes (each defect gets its own task, then the owner's epic); `managed_spell_quantity`; performance.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the owner directed the audit and the per-defect tasks in chat (2026-10-14).
- from_state: in_progress
- to_state: review
- transition_reason: every slotted lifetime has a verdict backed by a probe or a full read, and each of the six
  proven defect groups has its investigation task (2026-10-14T18:41:39Z); the epics are the owner's call.
- from_state: review
- to_state: done
- transition_reason: the owner acted on the summary and directed the fixes (chat 2026-10-14); the six tasks moved
  under EPIC-2026-10-14-slotted_lifetime_ownership_fixes.

## Steps / Checklist
- [x] Record the after-fix route probe (all twelve affected routes now dispose the child with the holder's owner).
- [x] Read how each lifetime's store is chosen and what ends it (site-plan routes, Creations, ConduitCluster,
      ConduitWard lineage, upgrade, TransferOfOwnership, purge); record each finding.
- [x] Probe each lifetime under each event in scope, GIL off and on; record each result.
- [x] For each proven defect, open an investigation task with the reproducer, the code path and the open questions.
- [x] Write the per-lifetime verdict table and report to the owner.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- The verdict per lifetime (Notes, 2026-10-14T18:41:39Z) with probe evidence; six investigation tasks, status ready:
  - tickets/tasks/2026-10-14_investigate_cluster_member_teardown_without_leave_task.md
  - tickets/tasks/2026-10-14_investigate_cluster_instance_not_rehomed_on_leader_change_task.md
  - tickets/tasks/2026-10-14_investigate_stored_instances_dropped_without_disposal_task.md
  - tickets/tasks/2026-10-14_investigate_transfer_leaves_holder_children_behind_task.md
  - tickets/tasks/2026-10-14_investigate_purge_leaves_holder_children_registered_task.md
  - tickets/tasks/2026-10-14_investigate_upgrade_retained_holders_keep_old_dependencies_task.md

## Files / Paths Impacted
- `context_compass/artifacts/slotted_lifetime_audit_20261014/` (probes, runs)
- `context_compass/tickets/tasks/` (one new investigation task per defect)

## Validation
- Run on the device VM (Python 3.14.7t, GIL off and on, identical output; live src copied to a scratch tree): the
  many-child route probe (17 lines) and the audit probe (11 cases), plus case c3 under six hash seeds.
- Not run: anything in the test suite (no src or test changed); the Windows tiers and hosted CI.

## Risks / Rollback Notes
- Read-only audit; nothing to roll back.

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

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/slotted_lifetime_audit_20261014/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: decided at closure; the per-defect tasks cite these probes

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - UNKNOWN
- CONTEXT_TOPICS:
  - which object owns each slotted lifetime's instance and its children, and what ends it
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): melder_1 (synaptic_python_developer); prose, design and evidence; the whole ticket; initial
  revision 2026-10-14T18:14:30Z; evidence in Notes. The rule and the directive are the owner's.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-14T18:14:30Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Opened from the owner's directive. Known: 0.2.8235 routes a slotted holder's `many` children to the store
    the holder is published to (`c{i}`), so the children of every lifetime now follow their holder's store. Not yet
    known, and the subject of this audit: whether each holder's store is itself the object the lifetime names, under
    every event that ends or changes that object - a cluster leader change, lineage changes, transfer, purge, an owner
    root's teardown while other roots still use the instance, and Phase 6 ordering where a dependency's owner can end
    first. Each candidate is UNKNOWN until a probe or a full code read settles it.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1319-1381
  - context_compass/tickets/epics/2026-10-14_many_child_follows_holder_epic.md:123-125
  IMPACT: Defines the audit's matrix; each proven defect becomes its own investigation task.
  NEXT: Record the after-fix route probe, then read the store selection and the ending events lifetime by lifetime.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-14T18:27:59Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The `many`-child half of the owner's question is settled on 0.2.8235, for every lifetime he named. The
    proof's route probe, rerun on the live src (copied to a scratch tree), GIL off and on with identical output:
    each of the twelve routes that disposed a holder's child when the melding scope ended on 0.2.8234 (`at_exit=1`) now
    keeps it alive and serves the same holder (`same=True at_exit=0`) until the holder's owner ends (`at_end=1`),
    building it once - `unique` through a lesser, a root spellspace and a lesser's spellspace, nested under a
    per-conduit consumer, by an override and with the specializer on; `unique_per_conduit` through a root and a
    lesser's spellspace; lineage through a lesser and a root spellspace; a borrowed `unique`; a cluster holder
    through a member. The five controls are unchanged (a per-conduit holder at a lesser and a spellspace holder are
    disposed when their own owner, that lesser or spellspace, ends: `at_exit=1` by design). Not probed by a dedicated
    route: lineage first melded in a lesser's spellspace, a cluster holder first melded in a spellspace (same `c{i}`
    path).
  EVIDENCE:
  - context_compass/artifacts/slotted_lifetime_audit_20261014/runs/probe_many_child_routes_after_fix_gil0.txt:1-18
  - context_compass/artifacts/slotted_lifetime_audit_20261014/runs/probe_many_child_routes_after_fix_gil1.txt:1-18
  - context_compass/artifacts/many_child_registration_20261014/runs/probe_many_child_routes.txt:1-39
  - context_compass/artifacts/many_child_registration_20261014/probe_many_child_routes.py:1-477
  IMPACT: The children follow their holder's store for unique_per_conduit, cluster and lineage; what remains open is
    whether each holder's store is itself the object its lifetime names under every event that ends or moves it.
  NEXT: Read how each lifetime's store is chosen and what ends it - the cluster store first (leader election and
    teardown), then lineage (link, sever, upgrade), transfer and purge.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T18:30:25Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: A `unique_per_conduit_cluster` instance is owned by the elected leader conduit, not by the cluster. The team
    store is the leader's own conduit store (`leader._creations`, the store that also holds the leader's per-conduit
    instances); each member root's `ClusterCreations` facade only references it and never cleans it. Three
    consequences, each to be probed: (1) a leader that leaves dissolves the cluster to inert with no re-home
    ("v1: owner-leave dissolves the cluster to inert -- no re-home"), so the cluster's instances and their children
    stay in the departed leader's store and a later leader builds new ones; (2) a root's teardown never leaves its
    cluster - `_cleanup_normal_conduit` cleans its own store and drops its facade but calls no `handle_leave`
    (the only callers are `ConduitCloud.remove_conduit_from_cluster` and the Rift `leave_cluster` command), so a
    leader torn down while elected disposes the instances and leaves every member facade bound to a cleaned store;
    (3) holders in other members (a per-conduit or lineage holder may depend on a cluster instance under Phase 6's
    ranks) keep the instance after the leader's store disposes it.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_cluster.py:26-171
  - src/melder/aether/conduit/conduit_cluster.py:543-632
  - src/melder/aether/conduit/conduit_cluster.py:637-808
  - src/melder/aether/conduit/creations/cluster_creations.py:9-264
  - src/melder/aether/conduit/conduit.py:967-1100
  - src/melder/aether/aetheric_frame/conduit_cloud.py:800-916
  IMPACT: The cluster lifetime does not meet the owner's rule (the cluster, not the leader, should own the instance);
    whether each consequence is a defect is settled by a probe, case by case.
  NEXT: Read the lineage store's repointing (link, sever, upgrade), transfer and purge, then write one audit probe
    with a case per candidate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T18:31:37Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Three more ending events, read in full; each is a candidate to probe. (1) Ownership transfer handles only
    the transferred spell's entries in the SOURCE conduit's own store (lineage is skipped). The default
    (`move_creations=False`) calls `_teardown_creations`, which only extracts the holder - `extract_spell_creations`
    runs no disposal - so a transferred holder's disposal methods never run; `_move_creations` carries the index
    members' entries to the target store but not the holder's `many` children (other spell ids), which stay in the
    source store and die with it while the moved holder lives on. Both helpers swallow every exception
    (`except Exception: continue` / `pass`). (2) Purge detaches and disposes only the purged spell id's entries; the
    holder's `many` children stay registered in the same store until it is cleaned, and every rebuild after a purge
    adds another set. (3) Lesser upgrade repoints the upgraded conduit's (and its spaces' and lessers') lineage and
    cluster stores to its own, while instances it melded before - lineage holders in the old root's store, `unique`
    holders in their owner's - stay where they were, held by the per-conduit holders the upgraded conduit keeps.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:361-505
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1506-1575
  - src/melder/aether/conduit/creations/creations.py:858-960
  - src/melder/aether/conduit/creations/creations.py:1075-1137
  - src/melder/aether/conduit/conduit.py:2351-2405
  - src/melder/aether/spellbook/spellbook.py:7180-7205
  IMPACT: Transfer, purge and upgrade can each leave an instance or a child with no owner that will dispose it, or
    dispose a dependency under a live holder; the probe decides which actually happens.
  NEXT: Write one audit probe with a case per candidate (cluster leader leave and teardown, a member holder over a
    cluster instance, transfer with and without move, purge cycles, upgrade, a borrower's holder over a lender's
    unique) and run it GIL off and on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T18:36:45Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The audit probe (8 cases, fresh world each, GIL off and on with identical output) proves five defects
    against the owner's rule. (1) Cluster, leader change (c2): with a leader that does not own the spell, the
    leader leaving and a member being elected yields a second cluster instance; the first stays in the departed
    leader's store, the member's per-conduit holder keeps it, and tearing the departed leader down disposes it while
    the member still serves that holder. Leader teardown while elected (c1): the root never leaves the cluster, which
    keeps the dead leader as master and member, and the instance is disposed. (2) Dropped without disposal (t3, b7,
    c1): the default ownership transfer removes a disposal-bearing `unique` holder from the source store and never
    disposes it (closes 0 through both teardowns; the target builds a new one), and a lender's (or cluster leader's)
    teardown makes `ConduitWard._invalidate_contract_consumers` drop the borrower's SpellContract consumer the same
    way (gone from the store, `closes` 0 after the borrower's own teardown) - both remove instances with
    `extract_spell_creations`, which runs no disposal. (3) Transfer with `move_creations=True` of a holder alone
    (t4b): the holder moves, its `many` child stays in the source store, and the source's teardown disposes it while
    the target serves the same holder (with `include_dependencies=True` the child moves too, t4). (4) Purge (p5):
    five purge-and-meld cycles dispose five holders and none of their children, which stay registered until the
    root's teardown (5 in the store). (5) Lesser upgrade (u6): the per-conduit holder the upgraded conduit retains
    keeps the old lineage's instance, which the old root's teardown disposes while the holder is still undisposed.
  EVIDENCE:
  - context_compass/artifacts/slotted_lifetime_audit_20261014/runs/probe_lifetime_owners_gil0.txt:1-64
  - context_compass/artifacts/slotted_lifetime_audit_20261014/runs/probe_lifetime_owners_gil1.txt:1-64
  - context_compass/artifacts/slotted_lifetime_audit_20261014/probe_lifetime_owners.py:1-475
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2682-2737
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1546-1575
  IMPACT: Five investigation tasks are owed (one per defect group). Still to probe: a member torn down without
    leaving (cluster walks over a dead member), lineage first melded in a lesser's spellspace and a cluster holder
    first melded in a member's spellspace (the two `many`-child routes without a dedicated probe).
  NEXT: Add those three cases to the probe and run it GIL off and on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T18:38:09Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Three more cases (the probe now has 11; full runs GIL off and on, identical). (c3) A non-leader member root
    torn down without leaving stays in `members`, and the cluster cannot recover: `unelect_leader` walks the member
    set, resolves the dead member to None and raises AttributeError ('NoneType' object has no attribute
    '_cluster_creations') part-way, after unbinding whichever facades came first in set order, with
    `master_conduit_id` still set - so `elect_leader` refuses ("a leader is already elected") and, depending on the
    hash seed, a surviving member's next cluster meld fails "no elected cluster leader" (2 of 6 seeds) or still
    resolves (4 of 6). `delete_cluster` pops the cluster and then unelects, so the same raise would leave the popped
    cluster uncleaned. (r8, r9) The two `many`-child routes without a dedicated probe are sound on 0.2.8235: a
    lineage holder first melded in a lesser's spellspace and a cluster holder first melded in a member's spellspace
    keep their child through the scope's end and the lesser's return or the member's teardown, the owner serves the
    same holder, and the child is disposed once, with the lineage root or the leader.
  EVIDENCE:
  - context_compass/artifacts/slotted_lifetime_audit_20261014/runs/probe_lifetime_owners_all_gil0.txt:20-23
  - context_compass/artifacts/slotted_lifetime_audit_20261014/runs/probe_lifetime_owners_all_gil0.txt:69-80
  - context_compass/artifacts/slotted_lifetime_audit_20261014/runs/probe_lifetime_owners_all_gil1.txt:1-80
  - context_compass/artifacts/slotted_lifetime_audit_20261014/runs/probe_c3_hash_seeds.txt:1-31
  - context_compass/artifacts/slotted_lifetime_audit_20261014/probe_lifetime_owners.py:1-608
  - src/melder/aether/conduit/conduit_cluster.py:694-727
  - src/melder/aether/aetheric_frame/conduit_cloud.py:800-827
  IMPACT: c3 joins the cluster defect group (membership is never reconciled with root teardown); the `many`-child
    question is closed for every lifetime and route.
  NEXT: Write the investigation tasks, one per defect group, then the verdict table and the owner's summary.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T18:41:39Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Verdict per lifetime on 0.2.8235 (every row from a probe case or a full code read above).
    `many` children: sound for every slotted lifetime and every probed route (12 routes, the 5 controls, r8, r9).
    `unique_per_spell_space`: sound - the space owns the holder and its children. `unique_per_conduit`: sound
    within a root; defective where its holder depends on an instance owned elsewhere - a cluster instance it keeps
    after a leader change (D2), a contracted instance whose lender's teardown drops the holder undisposed (D3), an
    old-lineage instance after an upgrade (D6) - and under purge (D5). `unique_per_conduit_lineage`: sound within a
    root (transfer leaves instances resolver-relative by design); defective after an upgrade (D6).
    `unique_per_conduit_cluster`: not set up per the owner's rule - the leader conduit, not the cluster, owns the
    instance (D2), and a root's teardown never leaves its cluster (D1). `unique`: transfer drops it undisposed by
    default (D3) or leaves its children behind with `move_creations` (D4); purge leaves children (D5). Opened, one
    investigation task per defect group, status ready, for the owner to turn into epics:
    D1 TASK-2026-10-14-investigate_cluster_member_teardown_without_leave (c1, c3);
    D2 TASK-2026-10-14-investigate_cluster_instance_not_rehomed_on_leader_change (c2);
    D3 TASK-2026-10-14-investigate_stored_instances_dropped_without_disposal (t3, b7, c1);
    D4 TASK-2026-10-14-investigate_transfer_leaves_holder_children_behind (t4, t4b);
    D5 TASK-2026-10-14-investigate_purge_leaves_holder_children_registered (p5);
    D6 TASK-2026-10-14-investigate_upgrade_retained_holders_keep_old_dependencies (u6).
  EVIDENCE:
  - context_compass/artifacts/slotted_lifetime_audit_20261014/runs/probe_lifetime_owners_all_gil0.txt:1-80
  - context_compass/artifacts/slotted_lifetime_audit_20261014/runs/probe_many_child_routes_after_fix_gil0.txt:1-18
  - context_compass/tickets/tasks/2026-10-14_investigate_cluster_member_teardown_without_leave_task.md:1-169
  - context_compass/tickets/tasks/2026-10-14_investigate_cluster_instance_not_rehomed_on_leader_change_task.md:1-165
  - context_compass/tickets/tasks/2026-10-14_investigate_stored_instances_dropped_without_disposal_task.md:1-167
  - context_compass/tickets/tasks/2026-10-14_investigate_transfer_leaves_holder_children_behind_task.md:1-158
  - context_compass/tickets/tasks/2026-10-14_investigate_purge_leaves_holder_children_registered_task.md:1-157
  - context_compass/tickets/tasks/2026-10-14_investigate_upgrade_retained_holders_keep_old_dependencies_task.md:1-159
  IMPACT: The owner's question is answered with evidence and every proven defect has its own task; D4 and D5 are the
    many-child epic's open questions 2 and 1, now with reproducers.
  NEXT: Owner reviews the verdict and turns the investigation tasks into epics (or redirects); then this task closes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T18:54:21Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Closed: the exit gate is met - every slotted lifetime has a verdict, every proven defect its task, and the
    owner acted on the summary ("yeah a torn down root shouldn't live in a cluster all these need to be fixed go ahead
    and target all these fixes ... investigate D6 again just make sure"). The six tasks continue under
    EPIC-2026-10-14-slotted_lifetime_ownership_fixes, which carries the owner's transfer guidance (a `many` spell's
    objects may stay behind; a unique kind's instance moves or is disposed with its children). The probe folder stays
    as reference evidence, re-associated with the epic.
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-14_slotted_lifetime_ownership_fixes_epic.md:1-60
  - context_compass/artifacts/slotted_lifetime_audit_20261014/runs/probe_lifetime_owners_all_gil0.txt:1-80
  IMPACT: The audit is done; the fix lane routes through the epic.
  NEXT: none (successor: EPIC-2026-10-14-slotted_lifetime_ownership_fixes).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
In review (2026-10-14). The owner asked whether `unique_per_conduit`, `unique_per_conduit_cluster` and
`unique_per_conduit_lineage` are set up properly. The `many`-child half is: on 0.2.8235 every lifetime's children follow
the holder's store on every probed route. Beyond children, the probe proved six defect groups, each now an
investigation task (status ready) for the owner to turn into an epic: D1 a root torn down without leaving its cluster
wedges it; D2 the cluster's instance belongs to the leader conduit, so a leader change leaves it behind; D3 transfer and
contract invalidation drop stored instances without disposal; D4 a transfer with move_creations leaves the holder's
children behind; D5 purge leaves the holder's children registered; D6 an upgraded lesser keeps holders whose
dependencies the old root disposes. Read-only audit: no src or test changed. Probes and runs:
`artifacts/slotted_lifetime_audit_20261014/`.

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
