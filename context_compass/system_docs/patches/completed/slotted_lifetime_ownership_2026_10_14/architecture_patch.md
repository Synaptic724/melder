# Architecture patch: slotted_lifetime_ownership_2026_10_14

## Metadata
- Patch ID: slotted_lifetime_ownership_2026_10_14
- Status: promoted at landing (2026-10-15) and archived; written before any src edit (2026-10-14); D3 rescoped by
  the owner (2026-10-14T22:14Z); contract invalidation left as it is by the owner (2026-10-14T23:00Z)
- Owner: user (rule and directives); melder_1 (synaptic_python_developer) (patch)
- Tickets: EPIC-2026-10-14-slotted_lifetime_ownership_fixes; tasks D1-D6 under it

## Objective
Fix the structure that recorded slotted instances under the wrong owner or left registry state stuck where an owner
ends or changes: a slotted instance and the `many` children built for it are recorded with the object its lifetime
names and move with it. Melder's infrastructure disposes what its own stores record when they end; it does not
police the application objects it hands out, which agents iterate on and clean up (owner ruling 2026-10-14,
promoted to src_architecture as "Runtime Model: Structure Is the Contract").
The lifetime audit (TASK-2026-10-14-audit_slotted_lifetime_ownership, 0.2.8235) proved five defect groups:
- D1 a root torn down without leaving its cluster stays a member (and leader); the cluster wedges. Found while
  re-reading: an explicit leave (`ConduitCloud.remove_conduit_from_cluster`) drops the leaver's share record before
  `handle_leave` reads it, so the leaver's roots stay contracted to every remaining member.
- D2 a `unique_per_conduit_cluster` instance lives in the elected leader conduit's own store, so a leader change
  strands it and a later election builds a second one.
- D3 a default transfer (`move_creations=False` until 0.2.8239) takes the source's instances out of its store and
  puts them nowhere, so a transferred `unique` is rebuilt as a second instance; owner ruling 2026-10-14: the public
  verb defaults to `move_creations=True` and its docstrings say what each value does. Contract invalidation lets a
  retired consumer go undisposed and leaves a lesser's consumer in place (b7, l1, l2): intended behaviour by the
  owner's ruling (2026-10-14), no change.
- D4 a holder moved by transfer leaves its `many` children in the source store, which disposes them later.
- D5 purging a holder leaves its `many` children registered and undisposed until the store ends.
- D6 was re-investigated: no defect (graduation's documented contract); one docstring paragraph.

## Non-goals
- managed_spell_quantity (its own epic); the cluster's documented share/membership transaction gap beyond the exit
  order; async; pool behaviour.
- References held by application code are never revoked (purge's existing rule).
- No public API shape change; the one public semantic change is the owner-ruled `move_creations` default (D3). No
  warm meld path change (`_site_plan_executor` bodies byte-identical); no persisted record or cache format change,
  no cache generation bump.
- Deleting a cluster that still has members keeps today's behaviour for shares (UNKNOWN whether intended; raised to
  the owner, not changed here).

## Changed components
| component | change | defect |
| --- | --- | --- |
| Conduit (root teardown) | leaves its cluster first: a transactional exit while the frame lives, an effect-only drop during frame teardown or after a failed exit | D1 |
| ConduitCluster | ordered exit (`release_member`: leave, then membership); effect-only `drop_member`; owns the team store | D1, D2 |
| ConduitCloud | explicit leave uses the ordered exit; `get_clusters_for_conduit` reads the DevOps index (O(1)); cleanup raises collected cluster disposal failures after finishing | D1, D2 |
| AethericFrame | logs the cloud's disposal failures during frame teardown and keeps going | D2 |
| ClusterCreations | fronts the cluster's team store; carries the elected leader's id | D2 |
| ConduitMeld | cluster purge authority read from the facade's leader id | D2 |
| Creations | holder disposal record with adopted children; `adopt_children`; extract/restore carry children; whole-store and purge disposal include them; `retire_singleton_creation` withdrawn (invalidation left as it is) | D4, D5 |
| SpellCompiler codegen (site-plan lowering) | a miss adopts its disposal-bearing children into the holder's record after publishing the holder | D4, D5 |
| Conduit / ConduitWard transfer verbs | `move_creations` defaults to True; the docstrings (the verbs, `TransferOfOwnership`, its move and teardown helpers) and the docs page state what each value does; no transfer logic changes | D3 |
| ConduitWard contract invalidation | no change by the owner's ruling (2026-10-14): a consumer a contract change retires is left to the agents (b7) and a lesser keeps its consumer (l1, l2) | D3 (no change) |
| Conduit.upgrade_to_normal (docstring) | retained objects may reference instances the old lineage disposes | D6 |

## Invariants
1. A root's teardown leaves no trace of it in any cluster: not in `members`, not as `master_conduit_id`, not in
   `shared_spells`, not in the DevOps membership index; the cluster stays electable and deletable.
2. An explicit leave and a teardown leave run one ordered exit: dissolve the team store when the leaver leads, then
   unshare in both directions while the leaver's share record is still present, then drop the membership.
3. A cluster's `unique_per_conduit_cluster` instances live in the cluster's own team store: election, unelection, a
   leader's leave and a leader's teardown never dispose them; the cluster's cleanup (deletion, frame teardown) does,
   once. A later election serves the same instances.
4. A slotted holder's disposal-bearing `many` children built in its first build are recorded in the holder's
   disposal record, keyed by the holder's spell id: whole-store disposal, purge, retirement, extraction and restore
   of the holder apply to them, holder first and then its children newest-first.
5. A transfer disposes nothing. By default (`move_creations=True`) the source's instances of every index member move
   to the target's store with the spell, so a transferred `unique` stays one object and a holder's adopted children
   move with it; `move_creations=False` is the caller's opt-out and keeps its behaviour (the active member's entries
   leave the source store and are neither moved nor disposed). Contract invalidation is unchanged by the owner's
   ruling: the objects it lets go of stay pending for agents to manage.
6. O(1) by key: every new lookup is a dict read keyed by an id (the DevOps conduit->cluster index, a holder's spell
   id, a child's spell id); the only list work is the identity scan from a just-appended child's bucket end, on the
   cold path. No meld path gains a lock, a scan or a line.
7. Locks: new state sits under existing leaf locks (the store lock, the cluster lock); adoption runs inside the
   holder's build lock with the store lock as its leaf; no new lock-order edge; user disposal methods run outside
   the store and build locks.
8. Disposal failures are never swallowed: purge and cluster deletion raise one ExceptionGroup after finishing; frame
   teardown (which must complete) logs them.

## Interface deltas
- Internal: `ConduitCluster.release_member(conduit)`, `drop_member(conduit)`; `ClusterCreations.bind(store,
  leader_conduit_id)` and `leader_conduit_id`; `Creations.adopt_children(...)`; `HolderDisposalEntry`;
  `Conduit._leave_cluster_for_teardown()`; the ward's `_transfer_spell_ownership` default `move_creations=True`.
- Public signature default (owner ruling 2026-10-14, Breaking): `Conduit.transfer_spell_ownership(...,
  move_creations=True)` (was False). No other public signature changes.
- Behaviour visible to users: a root's teardown leaves its cluster; an explicit leave unshares the leaver's roots;
  cluster instances survive leader changes and die with the cluster; `delete_cluster` may raise an ExceptionGroup of
  disposal failures after finishing; a transfer moves the source's instances with the spell unless the caller passes
  `move_creations=False`; purging or moving a holder disposes or moves its children; a `many` purge or
  live-creation probe of a child spell no longer counts children owned by a holder.
- Persisted: none (extract/restore rows are in-memory handoffs; plans are emitted at hydration).

## Migration order
Patch docs -> red tests per task (GIL off and on) -> D1 src (notch 0.2.8236, with the D6 docstring) -> D2 src
(0.2.8237) -> D4/D5 src (0.2.8238) -> D3 transfer default (0.2.8239) -> red tests green, existing tests updated
where they pin a corrected representation (reason recorded) -> audit probe clean -> full tree GIL off and on ->
emission diff and meld benchmarks -> system docs, indexes, graph -> release note -> patch archived -> assets and
llm_support last. The invalidation half of D3 was ruled out (no change, 2026-10-14); a docstring notch (0.2.8240)
documents the transfer handover: stewardship, not a working setup.

## Rollback
Each notch is one cohesive change: revert its files and tests. Nothing persisted depends on any of them.

## Coverage matrix
| invariant | evidence |
| --- | --- |
| 1, 2 | component: root teardown (member and leader) leaves the cluster; unelect, elect, join and delete work after it; explicit leave unshares (probe_cluster_leave_order) |
| 3 | component: leader leaves / is torn down, the next election serves the same instance; deletion disposes it once; purge authority |
| 4 | component: purge, transfer move and scope end with holder-owned children; unit: adoption, extract/restore rows, disposal order |
| 5 | integration: a default transfer keeps a transferred `unique` one object (holder and consumer share it) and moves a tracked `many` object; `move_creations=False` still builds anew on the target |
| 6, 7 | emission diff of warm bodies; unit: adoption under the build lock; benchmarks within noise |
| 8 | component: delete_cluster raises after finishing; frame teardown logs |
