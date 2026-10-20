"""D1 (EPIC-2026-10-14-slotted_lifetime_ownership_fixes), notch 0.2.8236: a root's teardown leaves its cluster.

Patch: slotted_lifetime_ownership_2026_10_14 (component_patch_conduit_clusters.md, code_description_patch_cluster_exit.md).
Run from the repository root (or a scratch tree root): python <this file> [<tree root>]
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import edit_tool

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
CLUSTER = str(ROOT / "src/melder/aether/conduit/conduit_cluster.py")
CLOUD = str(ROOT / "src/melder/aether/aetheric_frame/conduit_cloud.py")
CONDUIT = str(ROOT / "src/melder/aether/conduit/conduit.py")

cluster_edits = [
    (
        """        - `handle_leave(conduit)`: remove the conduit from `members`, tear down
          the shared roots in both directions, and drop its `shared_spells`
          entry.
""",
        """        - `handle_leave(conduit)`: remove the conduit from `members`, tear down
          the shared roots in both directions, and drop its `shared_spells`
          entry.
        - `release_member(conduit)`: the ordered exit every leave takes -
          `handle_leave` first (it unelects first when the leaver leads), then
          `remove_member` (the DevOps membership edge and the record). The
          cloud's explicit leave and a root's teardown both run it (0.2.8236).
        - `drop_member(conduit)`: the same exit without transactions, for a
          root torn down while its frame is torn down (no transaction can
          start then) or whose transactional exit failed in its teardown.
""",
    ),
    (
        """        - One cluster per conduit (INTENDED): a conduit owns a single
          `_cluster_creations` facade, so it can only ever front ONE cluster's
          team store. Rejecting a join when the conduit is already clustered is
          planned; it is not enforced yet.
""",
        """        - One cluster per conduit: a conduit owns a single
          `_cluster_creations` facade, so it can only ever front ONE cluster's
          team store; `ConduitCloud.add_conduit_to_cluster` refuses a join when
          the conduit is already clustered.
        - A torn-down root is never a member: a normal root's teardown leaves
          its cluster first (`Conduit._leave_cluster_for_teardown`), so
          `members` and `master_conduit_id` only ever hold live roots and every
          member walk (elect, unelect, join, delete) finds each member
          (0.2.8236; before, the dead id stayed and those walks failed on it).
""",
    ),
    (
        """        Contract:
            - Removes the leaving conduit id from cluster membership first.
            - Removes roots owned by the leaver from all remaining peers.
            - Removes roots owned by remaining peers from the leaving conduit.
            - Drops the leaver's shared-root registry entry after teardown.
""",
        """        Contract:
            - Removes the leaving conduit id from cluster membership first.
            - Removes roots owned by the leaver from all remaining peers.
            - Removes roots owned by remaining peers from the leaving conduit.
            - Drops the leaver's shared-root registry entry after teardown.
            - Reads the leaver's share record, so it must run while that record
              is present: callers take the ordered exit `release_member`, which
              calls this first and `remove_member` (which pops the record)
              after. Until 0.2.8236 the cloud's leave called `remove_member`
              first, and the leaver's roots stayed contracted to every remaining
              member.
            - Leaves the DevOps membership edge to `remove_member`.
""",
    ),
    (
        """            self.unbind_member(conduit)
            succeeded = True
        finally:
            mediator.end_transaction(
                expected_type=ChangeTransactionType.CLUSTER_LEAVE,
                success=succeeded,
            )

""",
        """            self.unbind_member(conduit)
            succeeded = True
        finally:
            mediator.end_transaction(
                expected_type=ChangeTransactionType.CLUSTER_LEAVE,
                success=succeeded,
            )

    def release_member(self, conduit: Conduit) -> None:
        \"\"\"
        Run one member's ordered exit: leave first, then drop the membership record.

        Purpose:
            The single exit every leave takes - the cloud's explicit leave
            (`ConduitCloud.remove_conduit_from_cluster`) and a root's teardown
            (`Conduit._leave_cluster_for_teardown`). Until 0.2.8236 the cloud
            removed the membership first (`remove_member` pops the leaver's share
            record) and `handle_leave` then found no record to unshare, so the
            leaver's shared roots stayed contracted to every remaining member.

        Contract:
            - `handle_leave(conduit)` first: when the conduit leads, the cluster
              is unelected (the drained UNELECT transaction); then, inside one
              CLUSTER_LEAVE transaction, the conduit leaves `members`, its shared
              roots are unshared from every peer and every peer's roots from it
              while its share record is still present, the record is popped and
              its facade is unbound.
            - `remove_member(conduit._id)` second: the DevOps membership edge goes
              and the record is emitted (its discard and pop are no-ops by then).
            - Safe for a conduit that is no longer a member: every effect is a
              discard, a pop or an idempotent unbind.

        Args:
            conduit: The normal root conduit leaving the cluster.

        Raises:
            RuntimeError: If the cluster has been cleaned, the conduit is not
                normal, or the frame refuses the transaction (a frame being torn
                down does; root teardown then uses `drop_member`).
            Exception: An error of the unelect or leave transaction propagates
                after that transaction is aborted.

        Threading:
            The membership change runs inside the transactions' held windows, as
            `handle_leave` documents; `remove_member` takes the cluster lock.

        Returns:
            None.
        \"\"\"
        self.handle_leave(conduit)
        self.remove_member(conduit._id)

    def drop_member(self, conduit: Conduit) -> None:
        \"\"\"
        Remove one member without transactions, for a root that is being torn down.

        Purpose:
            The exit's effects when no transaction can run: a root torn down while
            its frame is torn down (the frame is marked cleaned first, so the
            mediator refuses), or a root whose transactional exit
            (`release_member`) failed during its teardown.

        Contract:
            - When the conduit leads, `unbind_elected_leader()` unbinds every
              member's facade and clears `master_conduit_id`, so the cluster is
              inert. The walk meets only live members: every member torn down
              earlier left the cluster in its own teardown.
            - `remove_member(conduit._id)` drops the membership, the share record
              and the DevOps edge and emits the record; then the conduit's own
              facade is unbound.
            - Shares are not unshared here: the root's ward cleanup, later in the
              same teardown, severs every contract the root takes part in.
            - Idempotent for a conduit that is no longer a member.

        Args:
            conduit: The departing normal root conduit.

        Raises:
            RuntimeError: If the cluster has been cleaned.

        Threading:
            Opens no transaction and drains no lineage. It is for teardown, when
            no meld runs against the departing root; a live leave takes
            `release_member`.

        Returns:
            None.
        \"\"\"
        self.check_cleaned()
        if (
            self.master_conduit_id is not None
            and conduit._id == self.master_conduit_id
        ):
            self.unbind_elected_leader()
        self.remove_member(conduit._id)
        conduit._cluster_creations.unbind()

""",
    ),
    (
        """            - Drops the leaver's OWN facade only. When the leaving conduit is the
              elected leader, `handle_leave` first dissolves the cluster through
              `unelect_leader` (drained: clears `master_conduit_id` and unbinds
              the remaining members); this call then drops the departed leader's
              own facade. The cloud removes the leaver from `members` before
              `handle_leave`, so that drained walk cannot reach the leaver's
              facade -- which is why this unbind is unconditional.
""",
        """            - Drops the leaver's OWN facade only. When the leaving conduit is the
              elected leader, `handle_leave` first dissolves the cluster through
              `unelect_leader` (drained: clears `master_conduit_id` and unbinds
              every member, the leader included, which is still a member then);
              this call is unconditional so a non-leader's facade is dropped too
              and a repeated exit stays a no-op.
""",
    ),
]

cloud_edits = [
    (
        """        "_conduit_clusters",
        "_id",
        "_devops_identity",
        "_devops_information_registry",
    ]
""",
        """        "_conduit_clusters",
        "_cluster_names_by_id",
        "_id",
        "_devops_identity",
        "_devops_information_registry",
    ]
""",
    ),
    (
        """    Owned State:
        The cluster registry, named directory and temporary promotion-name claims.
""",
        """    Owned State:
        The cluster registry (by name, plus each cluster's name by its id for the
        O(1) membership lookup), named directory and temporary promotion-name
        claims.
""",
    ),
    (
        """        self._conduit_clusters: Dict[str, ConduitCluster] = {}
""",
        """        self._conduit_clusters: Dict[str, ConduitCluster] = {}
        self._cluster_names_by_id: Dict[str, str] = {}
""",
    ),
    (
        """            self._conduit_clusters.clear()
            self._named_conduits.clear()
""",
        """            self._conduit_clusters.clear()
            self._cluster_names_by_id.clear()
            self._named_conduits.clear()
""",
    ),
    (
        """            del self._conduit_clusters
            del self._devops_information_registry
""",
        """            del self._conduit_clusters
            del self._cluster_names_by_id
            del self._devops_information_registry
""",
    ),
    (
        """            self._conduit_clusters[cluster_name] = ConduitCluster(
                cluster_name,
                self._conduits,
                self._name,
                self._devops_information_registry,
            )
""",
        """            cluster = ConduitCluster(
                cluster_name,
                self._conduits,
                self._name,
                self._devops_information_registry,
            )
            self._conduit_clusters[cluster_name] = cluster
            self._cluster_names_by_id[cluster.id] = cluster_name
""",
    ),
    (
        """        with self._lock:
            cluster = self._conduit_clusters.pop(cluster_name, None)
        if cluster is None:
""",
        """        with self._lock:
            cluster = self._conduit_clusters.pop(cluster_name, None)
            if cluster is not None:
                del self._cluster_names_by_id[cluster.id]
        if cluster is None:
""",
    ),
    (
        """        Contract:
            - Removes membership and then runs the cluster's leave handling, so shares
              held for the member are released as part of this call rather than
              lazily.
""",
        """        Contract:
            - Runs the cluster's ordered exit (`ConduitCluster.release_member`): the
              leave first - unelecting first when the conduit leads, then unsharing
              the leaver's roots from every peer and every peer's roots from the
              leaver while the leaver's share record is still present - and the
              membership record after. Shares held for the member are released as
              part of this call rather than lazily. Until 0.2.8236 the membership
              went first, which popped the share record the unshare reads, so the
              leaver's roots stayed contracted to every remaining member.
""",
    ),
    (
        """        cluster.remove_member(conduit.id)
        cluster.handle_leave(conduit)
""",
        """        cluster.release_member(conduit)
""",
    ),
    (
        """            - Snapshots the cluster map under the lock and then inspects members
              OUTSIDE it, so a concurrent join or leave can be missed.
""",
        """            - O(1) by key (0.2.8236): reads the frame's DevOps conduit->cluster
              index, which every join and leave maintains, and names the clusters
              this cloud still maps by id; it never walks clusters or member sets
              (until 0.2.8236 it scanned every cluster's member set). A join or
              leave racing the call may or may not be seen.
""",
    ),
    (
        """        self.check_cleaned()
        with self._lock:
            clusters = list(self._conduit_clusters.items())
        return [
            name for name, cluster in clusters
            if conduit_id in cluster.get_members()
        ]
""",
        """        self.check_cleaned()
        cluster_ids = self._devops_information_registry.get_clusters_for_conduit(
            conduit_id
        )
        if not cluster_ids:
            return []
        with self._lock:
            return [
                self._cluster_names_by_id[cluster_id]
                for cluster_id in cluster_ids
                if cluster_id in self._cluster_names_by_id
            ]
""",
    ),
]

conduit_edits = [
    (
        """        Cleans up a normal Conduit.

        Contract:
            The cluster facade, the ward (lesser lineage), the SpellSpaces and the
            own store raise their disposal failures only after finishing; those
            groups are collected and returned, other step errors stay logged, and
            every later step still runs.

        Returns:
            List[Exception]: Collected disposal failure groups; empty when none failed.
        \"\"\"
        failures: List[Exception] = []
        self._remove_conduit_record_from_nexus()
""",
        """        Cleans up a normal Conduit.

        Contract:
            - First leaves its cluster (`_leave_cluster_for_teardown`), while this
              root is registered, its creation gate is live and its cluster facade
              is not cleaned, so no cluster keeps a torn-down root (0.2.8236).
            - The cluster facade, the ward (lesser lineage), the SpellSpaces and the
              own store raise their disposal failures only after finishing; those
              groups are collected and returned, other step errors stay logged, and
              every later step still runs.

        Returns:
            List[Exception]: Collected disposal failure groups; empty when none failed.
        \"\"\"
        failures: List[Exception] = []
        # 0) Leave the cluster first; failures are logged and teardown keeps going.
        self._leave_cluster_for_teardown()
        self._remove_conduit_record_from_nexus()
""",
    ),
    (
        """    def _cleanup_normal_conduit(self) -> List[Exception]:
""",
        """    def _leave_cluster_for_teardown(self) -> None:
        \"\"\"
        Internal

        Take this root out of its cluster as the first step of its teardown.

        Purpose:
            A torn-down root must leave no trace in a cluster: not in `members`,
            not as `master_conduit_id`, not in the share records, not in the
            DevOps membership index. Until 0.2.8236 root teardown never touched
            cluster membership, so the cluster kept the dead id and every later
            member walk (unelect, elect, join, delete) failed on it.

        Contract:
            - Finds the root's clusters through the frame's DevOps conduit->cluster
              index: one keyed read, and membership is exclusive, so at most one
              cluster. A root in no cluster pays only that read.
            - While the frame is live, runs the cluster's ordered exit
              (`ConduitCluster.release_member`: unelect first when this root leads,
              unshare both directions, then drop the membership) inside its
              transactions. It runs before any other teardown step, while this
              root is registered, its creation gate is live (the unelect drains
              member lineages through it) and its cluster facade is not cleaned.
            - During frame teardown the frame is marked cleaned before its roots
              are torn down, so no transaction can start; the root then runs
              `ConduitCluster.drop_member`, the same effects without transactions.
              That is the designed path, not a failure, and logs nothing.
            - A transactional exit that raises is logged and replaced by
              `drop_member`: the root is going away and cannot retry. A failing
              drop is logged too. Nothing is re-raised, so the teardown keeps
              going, as its other steps do.

        Threading:
            Reads the frame's registry slot directly, because the frame's public
            accessor refuses once the frame is marked cleaned. Takes no lock of
            its own: the cluster's transactions and its leaf lock serialize the
            exit.

        Returns:
            None.
        \"\"\"
        frame = self._aetheric_frame
        clusters = frame._devops_information_registry.get_cluster_objects_for_conduit(
            self._id
        )
        for cluster in clusters:
            if not frame._cleaned:
                try:
                    cluster.release_member(self)
                    continue
                except Exception:
                    self._logger.error(
                        "Error leaving the cluster during root teardown; dropping the membership",
                        "_leave_cluster_for_teardown",
                        exc_info=True,
                    )
            try:
                cluster.drop_member(self)
            except Exception:
                self._logger.error(
                    "Error dropping the cluster membership during root teardown",
                    "_leave_cluster_for_teardown",
                    exc_info=True,
                )

    def _cleanup_normal_conduit(self) -> List[Exception]:
""",
    ),
    (
        """            - The new root has no parent or inherited definitions/contracts.
              Old spell IDs are no longer resolvable; retained objects remain
              in their existing stores for eventual disposal.
""",
        """            - The new root has no parent or inherited definitions/contracts.
              Old spell IDs are no longer resolvable; retained objects remain
              in their existing stores for eventual disposal.
            - A retained object may hold references to instances the former
              lineage owns (a `unique` instance of a former root's spell, a
              lineage instance): those are disposed by their own owner, on that
              owner's schedule, not with this conduit, so a retained holder can
              outlive what it references. Melder does not serve a retained
              holder again (its spell ID no longer resolves) and never revokes
              references application code keeps.
""",
    ),
]

print("cluster", edit_tool.apply(CLUSTER, cluster_edits))
print("cloud", edit_tool.apply(CLOUD, cloud_edits))
print("conduit", edit_tool.apply(CONDUIT, conduit_edits))
