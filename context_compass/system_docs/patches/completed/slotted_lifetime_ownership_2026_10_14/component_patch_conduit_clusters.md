# Component patch: Conduit clusters - exit, teardown and the team store (slotted_lifetime_ownership_2026_10_14)

Components: Conduit Runtime (root teardown), ConduitCluster, ClusterCreations, ConduitCloud, AethericFrame (cloud
teardown), Meld Resolution Runtime (cluster purge authority). Defects D1 and D2.

## Before / after
- Root teardown (`Conduit._cleanup_normal_conduit`): never touched cluster membership; the cluster kept the dead id in
  `members`, `master_conduit_id` and `shared_spells`, and every member walk then failed. After: its first step,
  `_leave_cluster_for_teardown`, finds the root's clusters through the DevOps conduit->cluster index (one dict read;
  membership is exclusive, so at most one) and, while the frame is live, runs the ordered exit
  `ConduitCluster.release_member` (transactional); during frame teardown (the frame is already marked cleaned, so no
  transaction can start) or when the transactional exit raised (logged), it runs `ConduitCluster.drop_member`, the
  same effects without transactions.
- Explicit leave (`ConduitCloud.remove_conduit_from_cluster`): called `remove_member` (which pops the leaver's share
  record) and then `handle_leave`, whose unshare reads that record, so the leaver's roots stayed contracted to every
  peer. After: `release_member` - `handle_leave` (unelect first when the leaver leads; CLUSTER_LEAVE: discard the
  member, unshare both directions, pop the share record, unbind its facade) and then `remove_member` (DevOps index and
  the cluster record).
- `ConduitCloud.get_clusters_for_conduit`: scanned every cluster's member set. After: reads the DevOps index
  (`get_clusters_for_conduit`, cluster ids) and names them through the cloud-owned `_cluster_names_by_id` map,
  so a cluster deleted concurrently is never touched (aligned at promotion: the patch first said the cloud read
  cluster objects from the registry) - O(1) under exclusive membership, same list-of-names contract. Join
  exclusivity and the transfer borrower walk inherit it.
- Team store: `bind_elected_leader`/`bind_member` bound each member facade to `leader._creations`, so the cluster
  instance lived and died with the leader conduit. After: the cluster owns one `Creations` team store (owner and scope
  id = the cluster id), built with the cluster; election binds every member facade to it and records the elected
  leader's id on the facade; unelection, a leader's leave and a leader's teardown only unbind; the cluster's cleanup
  disposes the store. A later election serves the same instances.
- `ClusterCreations`: fronted the leader conduit's store. After: fronts the cluster's team store and carries
  `leader_conduit_id` (None while inert); `bind(store, leader_conduit_id)`; `unbind()` clears both.
- Cluster purge authority (`ConduitMeld._get_purge_creations`): compared the caller with the store's
  `owner_conduit_id` (the leader conduit). After: compares with the facade's `leader_conduit_id`; same refusal text.
- `ConduitCluster.cleanup`: cleaned membership only. After: also cleans the team store outside the cluster lock and
  raises its disposal failures as one ExceptionGroup after finishing. `ConduitCloud.cleanup` collects those groups
  from every cluster and raises them after it finished; `AethericFrame._cleanup_data_structures` logs that group like
  a failing conduit and keeps going. `delete_cluster` (unelect, then cleanup) raises them to its caller.

## Interface deltas
- Internal: `ConduitCluster.release_member(conduit)`, `ConduitCluster.drop_member(conduit)`, the cluster's
  `_team_store` slot; the cloud's `_cluster_names_by_id` map; `ClusterCreations.bind(store, leader_conduit_id)`,
  `ClusterCreations.leader_conduit_id`;
  `Conduit._leave_cluster_for_teardown()`.
- Public signatures unchanged. `ConduitCloud.delete_cluster` documents the ExceptionGroup it may now raise after
  finishing; `remove_conduit_from_cluster` unshares the leaver's roots; `describe_live_creation_status` keeps the
  `cluster_leader` label for the team store.

## State / failure deltas
- A cluster never holds a torn-down root; a leader's teardown leaves the cluster inert with its instances intact.
- An empty cluster keeps its instances until it is deleted or its frame is torn down (they belong to the cluster).
- A failed transactional teardown exit is logged and replaced by the effect-only drop (the root is going away and
  cannot retry); the drop unbinds facades without draining member lineages, safe because the team store stays alive.
- Disposal failures of cluster instances surface: raised by `delete_cluster`, logged by frame teardown.

## Dependency / ordering
- The teardown exit runs first in root teardown, while the root is registered, its creation gate is live (the
  unelect drains member lineages through it) and its facade is not yet cleaned.
- Frame teardown cleans roots before the cloud and DevOps, so the effect-only drop finds every surviving member live.
- D2 lands after D1 (separate notch); D1 alone already stops the wedge, D2 stops the leader-change strand.

## Validation expectations
Red first (0.2.8235), then green GIL off and on: member teardown then unelect/elect/join/delete; leader teardown keeps
the instance and a re-election serves it; explicit leave unshares; a leader change keeps the instance; deletion
disposes it once and raises a failing disposal after finishing; purge authority follows the elected leader. Existing
tests that pin `resolved_store() is leader._creations` or a one-argument `bind(store)` are updated with this reason.
