# Epic: slotted_lifetime_ownership_fixes - every slotted instance lives and dies with the object its lifetime names

## Metadata
- Epic ID: EPIC-2026-10-14-slotted_lifetime_ownership_fixes
- Status: in_progress
- Owner: user
- Agent Name: melder_1
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-14T18:52:55Z
- Updated: 2026-10-14T23:39:45Z
- Target Window: 2026-Q4
- Related Program/Initiative: EPIC-2026-10-14-many_child_follows_holder (0.2.8235, in review);
  TASK-2026-10-14-audit_slotted_lifetime_ownership (the audit that proved D1-D6); EPIC-2026-10-14-managed_spell_quantity
  (waits behind this epic)

## Problem / Opportunity
The lifetime audit (TASK-2026-10-14-audit_slotted_lifetime_ownership, probe `probe_lifetime_owners.py`, GIL off and
on, 0.2.8235) proved six defect groups where Melder's structure recorded a slotted instance, or the `many` children
built for it, under the wrong owner, or kept registry state an agent cannot get past (aligned 2026-10-15 to the
owner's ruling: correctness lives in the structure, not in the objects Melder hands out; the earlier framing here
was my own paraphrase):
- D1 a root torn down without leaving its cluster stays a member (and master); the cluster cannot unelect, elect or
  be deleted cleanly afterwards.
- D2 a `unique_per_conduit_cluster` instance lives in the elected leader conduit's own store, so a leader change leaves
  it behind and a later election builds a second one.
- D3 the default ownership transfer took the source's instances out of its store and put them nowhere, so a
  transferred `unique` was rebuilt as a second instance; contract invalidation lets retired consumers go undisposed
  (intended behaviour by the owner's ruling).
- D4 a transferred holder moved with `move_creations` leaves its `many` children in the source store, which disposes
  them under the moved holder.
- D5 purging a holder leaves its `many` children registered (and undisposed) until the store ends.
- D6 a lesser upgraded to a root keeps holders whose dependencies the old root disposes (re-investigated: no
  defect; a docstring paragraph).

## MRP Alignment (Most Reasonable Product)
Fix the structure, not the objects: where an owner ends or changes, a slotted instance and the `many` children built
for it are recorded with the object its lifetime names and move with it, and no registry keeps a torn-down root.
Melder's infrastructure disposes what its own stores record when they end; it does not police the objects it hands
out - agents iterate on them, leave them pending and clean them up (owner ruling 2026-10-14, promoted to
src_architecture as "Runtime Model: Structure Is the Contract"). The meld paths keep their O(1) shape.

## Ticket Contract
- ENTRY_GATE: the owner's directive (Decision Log 2026-10-14); each task's defect re-proven by a red test before its
  src edit; patch docs written and linked before any `src/` edit.
- EXECUTION_BOUNDARY: root and frame teardown (cluster leave), `ConduitCluster`/`ConduitCloud`/`ClusterCreations`
  (the team store), `Creations` (holder-owned children, retirement with disposal), the site-plan miss emission,
  `TransferOfOwnership` (move and teardown), `ConduitWard` contract invalidation, the purge doors, `upgrade_to_normal`
  if D6 holds; their tests, system docs, graph, release note, notches and the rebuild.
- DEPENDENCIES: EPIC-2026-10-14-many_child_follows_holder (0.2.8235); the audit probe and its runs.
- EXIT_GATE: every task's red tests green, the audit probe shows no defect, the full tree green GIL off and on, warm
  meld paths unchanged (emission diff, benchmarks within noise), docs, graph, release note, notches and assets
  current; the owner accepts.
- FAILURE_ESCALATION: DECISION_REQUEST where a fix would change public API, a persisted record format or a warm meld
  path; CONFLICT when an existing test pins a defect as a contract; BLOCKER on unexplained failures.

## Goals (Outcomes)
- D1: a root's teardown leaves its cluster (dissolving it first when it leads), so no torn-down root stays a member.
- D2: the cluster owns its team store; `unique_per_conduit_cluster` instances survive leader changes and die with the
  cluster.
- D3 (rescoped by the owner, Decision Log "transfer default"): a transfer disposes nothing and moves the source's
  objects by default (`move_creations=True`), so a `unique` stays one object; contract invalidation stays as it is
  (owner ruling, Decision Log "contract invalidation and the runtime model").
- D4/D5: a slotted holder's `many` children belong to it: purging, moving or disposing the holder does the same to
  its children.
- D6: re-investigated; fixed if confirmed.

## Non-Goals (Explicit Exclusions)
- managed_spell_quantity (its own epic, after this one).
- Changing which objects callers may keep: references held by application code are never revoked.
- New public API beyond what a fix needs; warm meld path changes.

## Scope Boundaries
- In scope: the six defect groups, their tests, docs, graph, release note, notches and rebuild.
- Out of scope: the cluster's documented share/membership transaction gap beyond what D1 needs; async; pools.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the owner turned the audit's tasks into this epic and directed the fixes first (chat
  2026-10-14, Decision Log).

## Success Metrics
- The audit probe's eleven cases report no defect (D6 per its re-investigation; b7 accepted as intended by the
  owner's ruling), GIL off and on.
- Each task's red tests green; the full tree green GIL off and on.
- Warm `_site_plan_executor` bodies byte-identical; meld micro-benchmarks within noise.

## Requirements (Functional + Non-Functional)
- F1 (D1) Root teardown leaves its cluster through the leave path (unelect first when it leads), bypassing only the
  posture gate; frame teardown keeps working.
- F2 (D2) The team store belongs to the cluster; election binds members' facades to it; leader leave or teardown
  never disposes cluster instances; cluster deletion or cleanup does.
- F3 (D3, rescoped 2026-10-14) The public transfer verbs default to `move_creations=True` and their docstrings say
  what each value does; a transfer disposes nothing. Contract invalidation is unchanged (owner ruling).
- F4 (D4/D5) Children built in a holder's first build are recorded with that holder; purge, move and disposal of the
  holder apply to them.
- N1 O(1): no scan of a store, a member set or a registry is added to a meld path; teardown, transfer, purge and
  invalidation find what they retire by key.
- N2 Locks: new state is guarded by existing leaf locks; no new lock-order edge; disposal runs outside locks.
- N3 The synaptic_python_developer code rules; rich docstrings on every touched method.

## Constraints / Assumptions
- Site plans are emitted at hydration from manifest rows, so emission changes need no persisted-format change (as in
  0.2.8235); any Creations format change must keep extract/restore and crystallizer rows coherent.

## Dependencies / External References
- context_compass/tickets/tasks/completed/2026-10-14_audit_slotted_lifetime_ownership_task.md
- context_compass/artifacts/slotted_lifetime_audit_20261014/probe_lifetime_owners.py

## Milestones (Track Progress)
- [x] Milestone 1: D6 re-investigated; patch docs written and linked.
- [x] Milestone 2: D1 and D2 landed (cluster): 0.2.8236 and 0.2.8237.
- [x] Milestone 3: D3, D4 and D5 landed. D4/D5 landed as 0.2.8238 and the D3 transfer default as 0.2.8239, its
      handover docstring as 0.2.8240; the D3 invalidation half was ruled out by the owner (no change).
- [ ] Milestone 4: D6 per its verdict; full tree, docs, graph, release note, notches, rebuild; owner acceptance.

## Stories (Required to Complete)
- [ ] None - six tasks directly under the epic.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] D1 TASK-2026-10-14-investigate_cluster_member_teardown_without_leave
- [ ] D2 TASK-2026-10-14-investigate_cluster_instance_not_rehomed_on_leader_change
- [ ] D3 TASK-2026-10-14-investigate_stored_instances_dropped_without_disposal
- [ ] D4 TASK-2026-10-14-investigate_transfer_leaves_holder_children_behind
- [ ] D5 TASK-2026-10-14-investigate_purge_leaves_holder_children_registered
- [ ] D6 TASK-2026-10-14-investigate_upgrade_retained_holders_keep_old_dependencies

## Acceptance Criteria (Epic Done)
- Every task done with recorded evidence; the owner accepts.

## Risks / Mitigations
- A change to how `Creations` records children ripples into extract/restore, purge, cleanup and probes -> one
  mechanism, covered by the existing Creations suites plus new tests; the many-child tests updated where they pin the
  representation, with the reason recorded.
- Root teardown now runs leave transactions -> ordering checked against frame teardown; failures logged as teardown
  errors are today.
- Cluster store ownership moves -> facades, purge authority and probes reviewed together.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Red tests from the probe cases first, then the fixes; the audit probe rerun; the full tree GIL off and on; an
  emission diff for warm paths; meld micro-benchmarks before and after.

## Rollout / Adoption Plan
- Behaviour fixes in the next release; release note entries per notch.

## Open Questions
- D5 as landed (0.2.8238): purging a holder disposes the `many` children recorded with it. Offered to the owner
  (2026-10-14) to revert purge to leaving them registered; kept as landed unless he says otherwise.

## Decision Log
- 2026-10-14: fix all of them, first. The owner: "yeah a torn down root shouldn't live in a cluster all these need to
  be fixed go ahead and target all these fixes since you have context first ... investigate D6 again just make sure,
  continue".
- 2026-10-14: transfer semantics. The owner: "transfer of ownership and leaving behind its children are normal usually
  remember melder is a runtime ecosystem not a static library ... its built for agents ... and transfer of ownership
  with many can leave its objects behind optionally unless its a unique kind of some sort". Read as: a transferred
  `many` spell's objects may stay with the source (the `move_creations` option); a unique kind's instance is never left
  behind - it moves, or it is disposed - and the `many` children built for it
  (EPIC-2026-10-14-many_child_follows_holder) go with it.
- 2026-10-14: efficiency. The owner: "remember to use my O(1) systems here because there is significant work in making
  thing efficient in this library so go double check and fix all those tickets please".
- 2026-10-14: transfer default (supersedes my reading of the transfer ruling above as "a unique kind is moved or
  disposed"). After reading the transfer tests and docs together, the owner: "I think we set the
  move_creation=True by default isn't that the best play?", then "no we leave it alone and simply leave it default
  true, its up to the user to break their own shit". Read as: `transfer_spell_ownership` defaults to
  `move_creations=True`, so a transferred `unique` stays one object; `move_creations=False` and a move into a slot
  the target already fills keep today's behaviour and are documented; a transfer disposes nothing.
- 2026-10-14: contract invalidation and the runtime model. The owner: "no we leave it alone and simply leave it
  default true, its up to the user to break their own shit", then "objects are left as they are the agents can clean
  them up later ... this is an agentic ecosystem its not a fucken normal program", "correctness is in the structure
  and infrastructure not objects that are generated from melder ... even crystallizer just restores infrastructure
  and structure and not the baseline objects" and "the melder infrastructure enforces that but not userland shit".
  Read as: contract invalidation stays as it is (b7, l1, l2 are intended); a defect is wrong or stuck structure;
  objects Melder lets go of stay pending for agents; my earlier paraphrase of a disposal rule is erased.
- 2026-10-14: D4 and the transfer handover. The owner: "moving the many is fine", then "people will need to
  understand that transfer of ownership will likely end in a broken state ... they just need to register to all the
  dependencies so they can make their own version while you throw out the trash" and "update the documents too
  properly so you fully understand next time". Read as: D4 stays as landed (0.2.8238); the transfer docstring, the
  docs page and the release note say a transfer hands over stewardship, not a working setup (0.2.8240); the system
  docs record the runtime model.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/slotted_lifetime_audit_20261014/ (the probe and its runs)
  - artifacts/slotted_lifetime_fixes_20261014/ (probes, red/green runs, landing scripts)
  - system_docs/patches/completed/slotted_lifetime_ownership_2026_10_14/ (nine patch docs, promoted and archived
    2026-10-15)
- DISPOSITION: retain_as_reference (artifacts); promote_to_documentation (patch docs, done)
- CLEANUP_TRIGGER: patch docs archived to patches/completed at landing (done); artifacts decided at closure

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - UNKNOWN
- CONTEXT_TOPICS:
  - who owns, moves and disposes each slotted instance and its children
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_1 (synaptic_python_developer); prose and design; the whole ticket; initial revision
  2026-10-14T18:52:55Z; the rule and the directives are the owner's, quoted in the Decision Log.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-14T18:52:55Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Opened from the owner's directive to fix the audit's findings first. Tranche order: re-investigate D6;
    read the code each fix touches and write the patch docs; D1 (teardown leaves the cluster) and D2 (cluster-owned
    team store); the holder-owned children mechanism that D3, D4 and D5 share; D3's retirements with disposal and the
    transfer rules; D6 per its verdict; red tests before each src edit; full tree GIL off and on; docs, graph, release
    note, one notch per landed fix, rebuild last.
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-10-14_audit_slotted_lifetime_ownership_task.md:306-340
  - context_compass/artifacts/slotted_lifetime_audit_20261014/runs/probe_lifetime_owners_all_gil0.txt:1-80
  IMPACT: The six tasks become this epic's tasks; managed_spell_quantity waits behind it.
  NEXT: Re-investigate D6 (upgrade semantics, retained creations, disposal order) and record the verdict.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

- DATETIME: 2026-10-14T19:03:12Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: ALIGNMENT_CHECK
  CLAIM: D6 re-investigated as the owner asked: no defect. Graduation keeps retained objects only for eventual
    disposal, old spell ids no longer resolve (so no meld serves a retained holder again), and each object is
    disposed by the owner its lifetime names; existing tests pin both halves. The remaining gap is one docstring
    paragraph on `upgrade_to_normal` (retained objects may reference instances the old lineage disposes), folded
    into the epic's conduit.py change. The epic's behaviour fixes are therefore D1-D5; D6 waits for the owner's
    confirmation in review and does not block the tranche.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-14_investigate_upgrade_retained_holders_keep_old_dependencies_task.md:165-194
  - src/melder/aether/conduit/conduit.py:2406-2547
  IMPACT: Milestone 1 narrows to the patch docs; the patch scope is D1-D5 plus the D6 docstring.
  NEXT: Re-read the cluster code (ConduitCluster, ClusterCreations, ConduitCloud, root teardown) for D1/D2.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-14T19:31:30Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Patch docs written and linked (patch id slotted_lifetime_ownership_2026_10_14; read order architecture ->
    component -> code description, consumed before any src edit). Patch -> implementation -> validation mapping:
    (1) clusters patch + cluster-exit description -> 0.2.8236: `Conduit._leave_cluster_for_teardown` first in root
    teardown, `ConduitCluster.release_member`/`drop_member`, cloud leave uses the ordered exit, cloud cluster lookup
    from the DevOps index, plus the D6 `upgrade_to_normal` docstring -> red tests c1/c3 member and leader teardown,
    explicit-leave unshare, then green; (2) clusters patch team-store section -> 0.2.8237: the cluster's `Creations`
    team store, facade leader id, purge authority, cluster/cloud cleanup raising and frame logging -> red tests c2
    (leader change keeps the instance), deletion disposes once, purge authority; (3) creations + codegen patches +
    holder-children description -> 0.2.8238: `HolderDisposalEntry`, `adopt_children`, record-aware disposal,
    extract/restore rows, the miss adoption line -> red tests p5 and t4b, unit adoption/order tests, emission diff;
    (4) transfer + ward patches + transfer-disposal description -> 0.2.8239: per-existence teardown with deferred
    disposal outside the window, invalidation retiring slotted consumers -> red tests t3, b7, many left behind. Then
    the audit probe, the full tree GIL off and on, benchmarks, docs, graph, release note, archive, rebuild.
  EVIDENCE:
  - context_compass/system_docs/patches/active/slotted_lifetime_ownership_2026_10_14/architecture_patch.md:1-101
  - context_compass/system_docs/patches/active/slotted_lifetime_ownership_2026_10_14/component_patch_conduit_clusters.md:1-61
  - context_compass/system_docs/patches/active/slotted_lifetime_ownership_2026_10_14/component_patch_creations.md:1-51
  - context_compass/system_docs/patches/active/slotted_lifetime_ownership_2026_10_14/component_patch_spellcompiler_codegen.md:1-29
  - context_compass/system_docs/patches/active/slotted_lifetime_ownership_2026_10_14/component_patch_ownership_transfer.md:1-37
  - context_compass/system_docs/patches/active/slotted_lifetime_ownership_2026_10_14/component_patch_conduit_ward_contracts.md:1-28
  - context_compass/system_docs/patches/active/slotted_lifetime_ownership_2026_10_14/code_description_patch_cluster_exit.md:1-35
  - context_compass/system_docs/patches/active/slotted_lifetime_ownership_2026_10_14/code_description_patch_holder_children.md:1-32
  - context_compass/system_docs/patches/active/slotted_lifetime_ownership_2026_10_14/code_description_patch_transfer_disposal.md:1-26
  IMPACT: Milestone 1 is met; the entry gate for src edits is the red tests of each tranche.
  NEXT: Write the red tests for D1 and D2 (component module for cluster exit and team store) and run them on 0.2.8235.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T20:11:51Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Milestone 2 met in the working tree: D1 landed as 0.2.8236 (root teardown leaves its cluster through the
    ordered exit, explicit leave unshares, O(1) cluster lookup) and D2 as 0.2.8237 (the cluster owns its team store).
    The ten lifetime tests are red on 0.2.8235 (8, the two controls green) and green on 0.2.8237, GIL off and on;
    aether, conduit and crystallizer chunks are green on the scratch tree. One design detail differs from the patch
    doc: the cloud names clusters through a cloud-owned id->name map instead of reading a cluster object from the
    registry, so a cluster deleted concurrently is never touched (patch doc to be aligned at promotion). Fourteen tests
    that pinned the defects' representations were updated with recorded reasons.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-14_investigate_cluster_member_teardown_without_leave_task.md:225-272
  - context_compass/tickets/tasks/2026-10-14_investigate_cluster_instance_not_rehomed_on_leader_change_task.md:221-269
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/red_d1_d2_cluster_lifetime_0_2_8235_gil0.txt:1-54
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/d2_scratch_gil0.txt:1-8
  IMPACT: The cluster tranche is done; the holder-children tranche (D4/D5, then D3) starts from 0.2.8237.
  NEXT: Read the creations, codegen and holder-children patch docs and the Creations/site-plan code in full, write the
    D4/D5 red tests (purge and transfer move with holder-owned children), run them on 0.2.8237.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T20:22:50Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Correction of a factual error found at re-onboarding: four timestamps written before the compaction were
    ahead of the clock (estimated, not read): the D1 note and Updated (20:05:00Z), the D2 note and Updated
    (20:40:00Z), the epic's 0.2.8237 MEASURE note and Updated (20:47:00Z) and the board row (20:48:00Z), while
    `date -u` read 20:21:11Z after the compaction. Each was rewritten to its file's last-write time from `stat`
    (19:57:49Z, 20:11:27Z, 20:11:51Z, 20:11:58Z), which bounds when the entry was written; nothing else in those
    entries changed. Timestamps are read from `date -u` at write time from here on.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-14_investigate_cluster_member_teardown_without_leave_task.md:247-247
  - context_compass/tickets/tasks/2026-10-14_investigate_cluster_instance_not_rehomed_on_leader_change_task.md:241-241
  - context_compass/tickets/epics/2026-10-14_slotted_lifetime_ownership_fixes_epic.md:270-270
  - context_compass/attention_board.md:199-199
  IMPACT: The lane's record orders correctly again; other agents reading the board see no future-dated row.
  NEXT: Re-read the creations, codegen and holder-children patch docs, then write the D4/D5 red tests.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-14T20:53:54Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: D4/D5 landed as 0.2.8238 in the working tree: one representation (a holder's adopted children in its
    `HolderDisposalEntry`, written by the miss right after publication) fixes purge (D5) and the transfer move (D4)
    with no transfer change; every retirement keyed by the holder reaches its children with one dict read, and warm
    plan bodies are byte-identical (emission diff, eight shapes). Red module 8 red on 0.2.8237 and 10/10 green on
    0.2.8238, GIL off and on; aether, conduit, spellbook and crystallizer chunks green. Deliberate behaviour change,
    in the release note: a `many` purge or live probe of a child spell counts only children no holder owns.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-14_investigate_purge_leaves_holder_children_registered_task.md:194-216
  - context_compass/tickets/tasks/2026-10-14_investigate_transfer_leaves_holder_children_behind_task.md:236-258
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/emission_diff_d45_0_2_8238.txt:1-9
  IMPACT: Milestone 3 needs only D3; until 0.2.8239 the extract-and-drop retirements also drop adopted children
    (RISK on D3), so 0.2.8239 lands in this pass before any hand-off.
  NEXT: D3: red tests (default transfer disposes a unique holder and its children once, many left in the source,
    contract invalidation disposes the borrower's consumer), run on 0.2.8238, then implement 0.2.8239.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T22:14:49Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner narrowed D3's transfer half (Decision Log, 2026-10-14 "transfer default"): the public transfer
    defaults to `move_creations=True` and the docstrings and docs say what each value does; nothing is disposed by a
    transfer, `False` and a move into a filled slot stay as they are. My dispose-on-transfer plan was my own reading
    and is withdrawn (it would have closed objects the transfer is meant to carry). The invalidation half (b7: a
    consumer retired by a contract change is dropped undisposed; l2: a lesser serves a consumer whose dependency was
    disposed) waits for the owner's ruling, and the 0.2.8238 interim RISK on D3 (adopted children leave with an
    invalidated holder) stays open with it.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-14_investigate_stored_instances_dropped_without_disposal_task.md:216-376
  - context_compass/tickets/epics/2026-10-14_slotted_lifetime_ownership_fixes_epic.md:147-164
  IMPACT: 0.2.8239 is the default flip; the end-of-pass work (probe, full tree, docs, graph, rebuild) follows it, and
    the invalidation fix becomes its own notch only if the owner wants it.
  NEXT: Rewrite the transfer patch docs, write the regression tests, land 0.2.8239; ask the owner about invalidation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T22:41:43Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: D3's transfer half landed as 0.2.8239, per the owner's ruling: the public transfer verbs default to
    `move_creations=True` (a `unique` stays one object, the source's objects follow the spell, nothing is disposed),
    with docstrings, the docs page, three regression tests (red on 0.2.8238, green after, GIL off and on), the release
    note's Breaking section and the notch. No transfer step, lock or meld path changed. The epic now waits on one
    owner decision - what contract invalidation does with the consumers it retires (b7 drops one undisposed; l1/l2 a
    lesser keeps serving its consumer, in l2 with a disposed dependency) - which decides whether a 0.2.8240 notch joins
    this pass before the end-of-pass work (audit probe, full tree, benchmarks, docs, graph, archive, rebuild).
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-14_investigate_stored_instances_dropped_without_disposal_task.md:369-498
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/probe_d3_move_and_lesser_0_2_8238_gil0.txt:1-26
  IMPACT: Milestone 3 is met except the invalidation half; the rebuild stays last, after the owner's ruling.
  NEXT: Ask the owner the invalidation question with the three cases and the options.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T23:39:45Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: End-of-pass validation of the lane at 0.2.8240 (D1-D5, the transfer default and the handover docs), GIL off
    and on: every code chunk of the test tree passed on a scratch tree synced from the repository (unit_mr 277,
    unit_aether 4228, unit_sb 2355, unit_util 821, unit_cryst 599, comp_aether 1352, comp_sb 819, comp_mr 40,
    comp_cryst 110, int_aether 785, int_conduit 301, int_sb 613, int_mr 67, int_cryst 273, int_mt 54, int_live 1,
    exper 250; xfail, skip and xpass counts as at 0.2.8235), and unit_arch 18 and unit_gh 491 on the repository;
    unit_llm, unit_build, unit_top and comp_util wait for the docs and the rebuild. The audit probe's eleven cases
    show D1, D2, D4 and D5 fixed, t3 moved by default, D6 unchanged and b7 as the owner ruled it (identical GIL off
    and on except one random contract id). Emission 0.2.8235 -> 0.2.8240 over the probe shapes: all 12 warm
    executors byte-identical, the only change the cold-path `adopt_children` line in 14 misses. Warm melds by id
    (unique, per-conduit, cluster) sit inside the VM's run-to-run band of about 8% in both directions over two
    interleaved rounds; the cluster door's `resolved_store` body is unchanged.
  EVIDENCE:
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/full_tree_0_2_8240_gil0.txt:1-28
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/full_tree_0_2_8240_gil1.txt:1-20
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/probe_lifetime_owners_all_0_2_8240_gil0.txt:1-79
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/emission_diff_lane_0_2_8235_to_0_2_8240.txt:1-16
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/bench_warm_meld_lane_gil0.txt:1-13
  - src/melder/aether/conduit/creations/cluster_creations.py:193-227
  IMPACT: The code side of the exit gate is met; what remains is documentation (system docs, graph, patch archive,
    packaging lines) and the rebuild, then the asset-dependent chunks.
  NEXT: Promote the lane and the owner's runtime model into src_architecture, src_components and tests_components.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-15T00:00:12Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The lane and the owner's runtime model are promoted into the system docs (land_docs_0_2_8240.py). The first
    run stopped on an ASCII assertion before writing anything: src_architecture already carries box-drawing
    characters and src_components an en dash, so the script now checks that the landing adds none and computes all
    three documents before writing any. src_architecture gains "Runtime Model: Structure Is the Contract"
    (correctness lives in the structure; generated objects are working material agents iterate on, leave pending
    and clean up; the infrastructure cleans its own state, not userland objects; a defect is wrong or stuck
    structure), the transfer sequence's move step and handover, four invariants (transfer default, holder records,
    cluster team store, cluster exit), five failure modes, the remeasured code map with a cluster_creations.py
    entry, two sources and the handoff. src_components gains the per-component rules (transfer contract, flow and
    diagram; cluster exit and team store; cloud lookups; holder records; the adoption line; store selection; probe
    counts; root teardown) and its code map; tests_components the two new integration modules, the transfer
    module's extent and the handoff. All three indexes regenerated, --check OK (59, 149 and 66 sections).
  EVIDENCE:
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/landing/land_docs_0_2_8240.py:1-550
  - context_compass/system_docs/src_architecture.md:522-548
  - context_compass/system_docs/src_architecture.md:826-842
  - context_compass/system_docs/src_architecture.md:959-1014
  - context_compass/system_docs/src_architecture.md:1764-1790
  - context_compass/system_docs/src_components.md:6163-6243
  - context_compass/system_docs/src_components.md:6634-6657
  - context_compass/system_docs/tests_components.md:1407-1415
  IMPACT: The next agent reading src_architecture meets the owner's model before any lifetime question, so a
    dispose-everything reading is not re-imposed; the packaged hardcopy documents pick it up at the rebuild.
  NEXT: Align the patch docs and this epic's framing to the ruling, then archive the patch folder.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Opened 2026-10-14 when the owner turned the lifetime audit's six tasks into one fix lane and put it first. D6 was
re-investigated (no defect; docstring landed with D1). Patch docs are written and linked. In the working tree, red
tests green GIL off and on: D1 0.2.8236 (teardown leaves the cluster), D2 0.2.8237 (the cluster's team store), D4/D5
0.2.8238 (holder-owned `many` children) and the D3 transfer default 0.2.8239 (`move_creations=True`; a transfer
disposes nothing, by the owner's ruling). Open: the D3 invalidation half (b7, l1, l2) and its interim RISK, waiting
for the owner. Then: the audit probe, full tree GIL off and on, benchmarks, system docs and graph, patch archive,
release-note packaging lines and the rebuild; owner acceptance, commit and push are the owner's.

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
