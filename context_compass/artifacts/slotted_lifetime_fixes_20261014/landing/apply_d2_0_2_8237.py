"""D2 (EPIC-2026-10-14-slotted_lifetime_ownership_fixes), notch 0.2.8237: the cluster owns its team store.

Patch: slotted_lifetime_ownership_2026_10_14 (component_patch_conduit_clusters.md, team-store section).
Run from a tree root: python <this file> [<tree root>]. Needs cluster_creations_new.py beside it (the full new
ClusterCreations module, LF; written with the file's CRLF endings).
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import edit_tool

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
CLUSTER = str(ROOT / "src/melder/aether/conduit/conduit_cluster.py")
FACADE = ROOT / "src/melder/aether/conduit/creations/cluster_creations.py"
CLOUD = str(ROOT / "src/melder/aether/aetheric_frame/conduit_cloud.py")
FRAME = str(ROOT / "src/melder/aether/aetheric_frame/aetheric_frame.py")
CONDUIT_MELD = str(ROOT / "src/melder/aether/conduit/meld/conduit_meld.py")
SPACE_MELD = str(ROOT / "src/melder/aether/conduit/meld/spellspace_meld.py")
SPACE = str(ROOT / "src/melder/aether/conduit/spell_space/spell_space.py")
CREATIONS = str(ROOT / "src/melder/aether/conduit/creations/creations.py")
DOOR = str(ROOT / "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py")

cluster_edits = [
    (
        """from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
""",
        """from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.aether.conduit.creations.creations import Creations
""",
    ),
    (
        """    ==================================================================
    LAYER 2 - Elected-leader team store (OPTIONAL; only for
              `unique_per_conduit_cluster` spells)
    ==================================================================
    A separate overlay. A `unique_per_conduit_cluster` spell must resolve into
    ONE shared creation store across the whole cluster: the elected leader
    conduit's `Creations`.
""",
        """    ==================================================================
    LAYER 2 - The cluster's team store, served through an elected leader
              (OPTIONAL; only for `unique_per_conduit_cluster` spells)
    ==================================================================
    A separate overlay. A `unique_per_conduit_cluster` spell must resolve into
    ONE shared creation store across the whole cluster: the cluster's own team
    store (`_team_store`, a `Creations` the cluster owns; owner and scope id =
    the cluster id). Since 0.2.8237 the store belongs to the cluster, not to the
    elected leader conduit: a leader change, a leader's leave and a leader's
    teardown keep its instances, the next election serves the same instances,
    and the cluster's cleanup (deletion, frame teardown) disposes them, once.
    Until 0.2.8236 the store was the elected leader conduit's own `Creations`,
    so a leader change stranded the instance (disposed later with that conduit,
    under the holders still using it) and the next election built a second one.
""",
    ),
    (
        """          walks `members` and binds every member root's facade to the elected
          leader's `_creations`, recording `master_conduit_id`. Election is
          inert -> active, so no lineage drain is required.
""",
        """          walks `members` and binds every member root's facade to the team
          store with the elected leader's id (the facade's purge authority),
          recording `master_conduit_id`. Election is inert -> active, so no
          lineage drain is required.
""",
    ),
    (
        """          every member root lineage to zero (so no meld is mid-create against the
          leader store), `unbind_elected_leader` unbinds every member facade and
          clears `master_conduit_id`, then the lineages reopen on every exit path
          (fail-closed).
""",
        """          every member root lineage to zero (so no meld is mid-create against the
          team store), `unbind_elected_leader` unbinds every member facade and
          clears `master_conduit_id`, then the lineages reopen on every exit path
          (fail-closed). The team store and its instances stay with the cluster.
""",
    ),
    (
        """          member walk (elect, unelect, join, delete) finds each member
          (0.2.8236; before, the dead id stayed and those walks failed on it).
""",
        """          member walk (elect, unelect, join, delete) finds each member
          (0.2.8236; before, the dead id stayed and those walks failed on it).
        - The team store lives exactly as long as the cluster: built with it,
          never disposed by an election, an unelection or a member's exit, and
          disposed by `cleanup()` (0.2.8237).
""",
    ),
    (
        """    Lifecycle:
        Becomes unusable after `cleanup()` completes; cleanup clears membership
        and shared-root state and drops references.
""",
        """    Lifecycle:
        Becomes unusable after `cleanup()` completes; cleanup clears membership
        and shared-root state, disposes the team store's instances (raising their
        disposal failures after it finished) and drops references.
""",
    ),
    (
        """        "_devops_information_registry",
        "master_conduit_id",
    ]
""",
        """        "_devops_information_registry",
        "master_conduit_id",
        "_team_store",
    ]
""",
    ),
    (
        """            auto_link_dependencies: If True, sharing pulls dependency closure.

        Returns:
            None.
        \"\"\"
""",
        """            auto_link_dependencies: If True, sharing pulls dependency closure.

        Contract:
            - Builds the cluster's team store (owner and scope id = the cluster
              id), which holds the cluster's `unique_per_conduit_cluster`
              instances until `cleanup()`.

        Returns:
            None.
        \"\"\"
""",
    ),
    (
        """        self.master_conduit_id: Optional[str] = None
""",
        """        self.master_conduit_id: Optional[str] = None
        # The cluster's team store (0.2.8237): `unique_per_conduit_cluster`
        # instances live here for the cluster's whole life; an election only
        # binds the member facades to it.
        self._team_store: Creations = Creations(
            owner_conduit_id=self._id,
            id=self._id,
        )
""",
    ),
    (
        """        Idempotently clear cluster membership state and release references.

        Contract:
            - Safe to call multiple times.
            - Clears member and shared-root registries before dropping owned
              references.
            - Leaves the instance permanently cleaned.

        Returns:
            None.
        \"\"\"
""",
        """        Idempotently clear cluster membership state, dispose the team store and release references.

        Contract:
            - Safe to call multiple times.
            - Clears member and shared-root registries before dropping owned
              references.
            - Disposes the team store - the cluster's `unique_per_conduit_cluster`
              instances - once, outside the cluster lock, after everything else
              is released (0.2.8237; until then the instances belonged to the
              elected leader conduit and deleting the cluster disposed nothing).
            - Every step runs when a disposal method fails; the failures are
              raised last, as one ExceptionGroup.
            - Leaves the instance permanently cleaned.

        Raises:
            ExceptionGroup: One or more team-store instances failed a disposal
                method ("Conduit cluster cleaned with disposal failures.").

        Threading:
            Membership state is cleared under the cluster lock; user disposal
            methods run after the lock is released. Callers quiesce cluster melds
            first: `delete_cluster` unelects (which drains every member lineage)
            and frame teardown has torn every member down.

        Returns:
            None.
        \"\"\"
""",
    ),
    (
        """            del self._name
        del self._lock
""",
        """            del self._name
            team_store = self._team_store
            del self._team_store
        del self._lock
        failures: List[Exception] = []
        try:
            team_store.cleanup()
        except ExceptionGroup as disposal_failures:
            failures.append(disposal_failures)
        if failures:
            raise ExceptionGroup(
                "Conduit cluster cleaned with disposal failures.", failures
            )
""",
    ),
    (
        """        # If the conduit leaving IS the elected leader, dissolve the team store
        # first through the drained UNELECT transaction (v1: owner-leave dissolves
        # the cluster to inert -- no re-home). This runs BEFORE the membership
        # transaction so the leader is still a member for the unbind walk and
        # every member lineage is drained before the leader store is released.
""",
        """        # If the conduit leaving IS the elected leader, unelect first through the
        # drained UNELECT transaction: the cluster becomes inert until the next
        # election, and its instances stay in the team store, which the cluster
        # owns (0.2.8237), so the next leader serves them. This runs BEFORE the
        # membership transaction so the leader is still a member for the unbind
        # walk and every member lineage is drained before the facades are unbound.
""",
    ),
    (
        """            # Drop the leaver's own team-store facade (idempotent). For a
            # non-leader leave this releases its handle to the leader store; for a
            # leader-leave the cluster was already dissolved above and this drops
            # the departed leader's own facade. No-op while inert.
""",
        """            # Drop the leaver's own team-store facade (idempotent). For a
            # non-leader leave this releases its handle to the team store; for a
            # leader-leave the cluster was already unelected above and its walk
            # unbound this facade too. No-op while inert.
""",
    ),
    (
        """        Bind the elected leader's creation store into every member root's facade.

        Purpose:
            Activate the cluster team store: make the elected leader conduit's
            creation store the single store every member resolves
            `unique_per_conduit_cluster` instances into.

        Contract:
            - Resolves the elected leader, then walks the current member set and
              binds the leader conduit's creation store into each member root's
              `_cluster_creations` facade. The leader is itself a member, so its
              own facade binds to its own store.
            - After this runs, a `unique_per_conduit_cluster` meld on any member
              lineage resolves into the leader store instead of hard-erroring.
            - Refuses re-election: raises if a leader is already elected
              (`master_conduit_id` is set), so an active cluster's leader store
              is never silently overwritten. The cluster must be unelected back
              to inert before a different leader can be elected.
""",
        """        Bind the cluster's team store into every member root's facade under the elected leader.

        Purpose:
            Activate the cluster team store: every member resolves
            `unique_per_conduit_cluster` instances into the store the cluster
            owns, and the facade records the elected leader as the conduit with
            purge authority over it.

        Contract:
            - Resolves the elected leader, then walks the current member set and
              binds the team store, with the leader's id, into each member root's
              `_cluster_creations` facade. The leader is itself a member, so its
              own facade is bound too.
            - The store is the cluster's (0.2.8237): a later election after an
              unelection binds the same store, so the instances built under an
              earlier leader are served again, never built twice. Until 0.2.8236
              each election bound the elected leader conduit's own store.
            - After this runs, a `unique_per_conduit_cluster` meld on any member
              lineage resolves into the team store instead of hard-erroring.
            - Refuses re-election: raises if a leader is already elected
              (`master_conduit_id` is set), so an active cluster's leader is
              never silently replaced. The cluster must be unelected back to
              inert before a different leader can be elected.
""",
    ),
    (
        """        Args:
            leader_conduit_id (str):
                Conduit id of the elected leader. Must resolve to a live, normal
                cluster member root whose creation store becomes the shared store.

        Threading:
""",
        """        Args:
            leader_conduit_id (str):
                Conduit id of the elected leader. Must resolve to a live, normal
                cluster member root; it holds purge authority over the team
                store while elected.

        Threading:
""",
    ),
    (
        """        Raises:
            RuntimeError: If the cluster has been cleaned, or a leader is already
                elected (re-election without an intervening unelect).
        \"\"\"
        self.check_cleaned()
        if self.master_conduit_id is not None:
            raise RuntimeError(
                "Cannot elect a cluster leader: a leader is already elected "
                f"('{self.master_conduit_id}'). Unelect the current leader first."
            )
        leader = self._resolve_conduit_by_id(leader_conduit_id)
        for member_id in self.members:
            member = self._resolve_conduit_by_id(member_id)
            member._cluster_creations.bind(leader._creations)
        self.master_conduit_id = leader_conduit_id
""",
        """        Raises:
            RuntimeError: If the cluster has been cleaned, a leader is already
                elected (re-election without an intervening unelect), or the
                leader conduit cannot be resolved.
        \"\"\"
        self.check_cleaned()
        if self.master_conduit_id is not None:
            raise RuntimeError(
                "Cannot elect a cluster leader: a leader is already elected "
                f"('{self.master_conduit_id}'). Unelect the current leader first."
            )
        if self._resolve_conduit_by_id(leader_conduit_id) is None:
            raise RuntimeError(
                "Cannot elect a cluster leader: leader conduit could not be resolved."
            )
        for member_id in self.members:
            member = self._resolve_conduit_by_id(member_id)
            member._cluster_creations.bind(self._team_store, leader_conduit_id)
        self.master_conduit_id = leader_conduit_id
""",
    ),
    (
        """        Unbind the leader's creation store from every member root's facade.
""",
        """        Unbind the team store from every member root's facade (the cluster turns inert).
""",
    ),
    (
        """            - Walks the current member set and unbinds each member root's
              `_cluster_creations` facade, dropping its reference to the leader
              store. The leader conduit still owns and cleans that store; the
              facade only releases the reference, never cleans the store.
""",
        """            - Walks the current member set and unbinds each member root's
              `_cluster_creations` facade, dropping its reference to the team
              store and the leader's id. The cluster still owns the store and its
              instances (0.2.8237): nothing is disposed here, and the next
              election serves them again.
""",
    ),
    (
        """            member root lineage has been drained to zero, so no meld is mid-create
            against the leader store when it is released. Members are live root
""",
        """            member root lineage has been drained to zero, so no meld is mid-create
            against the team store when the facades release it. Members are live root
""",
    ),
    (
        """        Bind one joining member's facade to the elected leader's store.
""",
        """        Bind one joining member's facade to the team store under the current leader.
""",
    ),
    (
        """            - When a leader is elected, binds the joining conduit's
              `_cluster_creations` to the elected leader's `_creations`. Does NOT
              change `master_conduit_id` (the leader is unchanged).
""",
        """            - When a leader is elected, binds the joining conduit's
              `_cluster_creations` to the team store with the current leader's
              id. Does NOT change `master_conduit_id` (the leader is unchanged).
""",
    ),
    (
        """        leader = self._resolve_conduit_by_id(self.master_conduit_id)
        conduit._cluster_creations.bind(leader._creations)
""",
        """        conduit._cluster_creations.bind(self._team_store, self.master_conduit_id)
""",
    ),
    (
        """        Unbind one leaving member's facade from the elected leader's store.
""",
        """        Unbind one leaving member's facade from the team store.
""",
    ),
    (
        """              (idempotent: a no-op when its facade is already inert). Never cleans
              the leader's store. Does NOT change `master_conduit_id`.
""",
        """              (idempotent: a no-op when its facade is already inert). Never cleans
              the team store. Does NOT change `master_conduit_id`.
""",
    ),
    (
        """            holds the leaver. No lineage drain is required: `unbind` only drops
            the facade pointer, the leader's store stays alive (owned by the
            leader conduit), and any in-flight meld holds its own store reference.
""",
        """            holds the leaver. No lineage drain is required: `unbind` only drops
            the facade pointer, the team store stays alive (owned by the
            cluster), and any in-flight meld holds its own store reference.
""",
    ),
    (
        """        Args:
            leader_conduit_id (str):
                Conduit id of the elected leader. Must resolve to a live, normal
                cluster member root whose creation store becomes the shared store.

        Returns:
""",
        """        Args:
            leader_conduit_id (str):
                Conduit id of the elected leader. Must resolve to a live, normal
                cluster member root; it holds purge authority over the team
                store while elected.

        Returns:
""",
    ),
    (
        """              DevOps-owned `ConduitLineageGateOps`, so no meld is mid-create
              against the leader store. Its `on_end` reopens every member root
""",
        """              DevOps-owned `ConduitLineageGateOps`, so no meld is mid-create
              against the team store. Its `on_end` reopens every member root
""",
    ),
    (
        """            unbind, so no meld is mid-create against the leader store when its
            reference is released.
""",
        """            unbind, so no meld is mid-create against the team store when the
            facades release it.
""",
    ),
]

cloud_edits = [
    (
        """        Contract:
            - Idempotent and lock-guarded.
            - Cleans cloud-owned cluster state before dropping owned refs.
            - Does not clean the conduit objects or clear the borrowed
              frame-owned root-conduit stores.

        Returns:
            None.
        \"\"\"
""",
        """        Contract:
            - Idempotent and lock-guarded.
            - Cleans cloud-owned cluster state before dropping owned refs. Each
              cluster disposes its team store as it is cleaned (0.2.8237); a
              cluster's disposal failures are collected and raised as one
              ExceptionGroup after the whole cloud is cleaned. Any other cluster
              cleanup error stays best-effort, as before.
            - Does not clean the conduit objects or clear the borrowed
              frame-owned root-conduit stores.

        Raises:
            ExceptionGroup: One or more clusters' team-store instances failed a
                disposal method ("Conduit clusters cleaned with disposal
                failures."), raised after the cloud finished its cleanup.

        Returns:
            None.
        \"\"\"
""",
    ),
    (
        """        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            for cluster in list(self._conduit_clusters.values()):
                # Best-effort: the clusters are cloud-owned and are dropped right
                # after this loop, so one cluster's cleanup failure must not abort
                # cleanup of the remaining clusters or the cloud teardown below.
                try:
                    cluster.cleanup()
                except Exception:
                    continue
""",
        """        if self._cleaned:
            return
        disposal_failures: List[Exception] = []
        with self._lock:
            if self._cleaned:
                return
            for cluster in list(self._conduit_clusters.values()):
                # Best-effort: the clusters are cloud-owned and are dropped right
                # after this loop, so one cluster's cleanup failure must not abort
                # cleanup of the remaining clusters or the cloud teardown below.
                # Its team-store disposal failures are raised once the cloud is
                # cleaned (0.2.8237).
                try:
                    cluster.cleanup()
                except ExceptionGroup as cluster_failures:
                    disposal_failures.append(cluster_failures)
                except Exception:
                    continue
""",
    ),
    (
        """            del self._name
            del self._id
        del self._lock

    @staticmethod
    def _validate_conduit_name(name: Optional[str]) -> str:
""",
        """            del self._name
            del self._id
        del self._lock
        if disposal_failures:
            raise ExceptionGroup(
                "Conduit clusters cleaned with disposal failures.", disposal_failures
            )

    @staticmethod
    def _validate_conduit_name(name: Optional[str]) -> str:
""",
    ),
    (
        """        Delete one frame-local conduit cluster.

        Args:
            cluster_name (str): Cluster name to remove.

        Raises:
            ValueError: If the cluster does not exist.

        Returns:
            None.
        \"\"\"
""",
        """        Delete one frame-local conduit cluster.

        Contract:
            - Removes the cluster from this cloud, unelects it when a leader is
              elected (draining every member lineage), then cleans it: the
              cluster's `unique_per_conduit_cluster` instances are disposed with
              it (0.2.8237; before, deleting a cluster disposed nothing and the
              instances died later with the leader conduit).
            - The deletion finishes before any disposal failure is raised.

        Args:
            cluster_name (str): Cluster name to remove.

        Raises:
            ValueError: If the cluster does not exist.
            ExceptionGroup: One or more of the cluster's instances failed a
                disposal method ("Conduit cluster cleaned with disposal
                failures."); the cluster is already deleted.

        Returns:
            None.
        \"\"\"
""",
    ),
    (
        """        # Dissolve the team store first if a leader is still elected: deleting an
        # active cluster must not leave member facades bound to a leader store the
        # cluster no longer coordinates. Members are still live here (delete is not
        # frame teardown), so the drained unelect is safe.
""",
        """        # Unelect first if a leader is still elected: deleting an active cluster
        # must not leave member facades bound to a team store the cleanup below
        # disposes. Members are still live here (delete is not frame teardown), so
        # the drained unelect is safe, and it quiesces cluster melds before the
        # cleanup disposes the cluster's instances.
""",
    ),
]

frame_edits = [
    (
        """        - Cleans conduit cloud, spell-system-state, and DevOps services when
          present.
""",
        """        - Cleans conduit cloud, spell-system-state, and DevOps services when
          present. The cloud raises its clusters' team-store disposal failures
          after it finished (0.2.8237); frame teardown logs them through the
          Aether logger, as it does a failing conduit, and keeps going.
""",
    ),
    (
        """        # Dynamic conduit cloud
        if self._conduit_cloud is not None:
            self._conduit_cloud.cleanup()
""",
        """        # Dynamic conduit cloud (cleaned after every root, so each root has left
        # its cluster and only the clusters' team stores remain to dispose).
        if self._conduit_cloud is not None:
            try:
                self._conduit_cloud.cleanup()
            except Exception:
                if self._aether._logger is not None:
                    self._aether._logger.error(
                        "Error cleaning the conduit cloud during frame teardown",
                        "_cleanup_data_structures",
                        exc_info=True,
                    )
""",
    ),
]

conduit_meld_edits = [
    (
        """    from melder.aether.conduit.creations.conduit_creations import ConduitCreations
""",
        """    from melder.aether.conduit.creations.conduit_creations import ConduitCreations
    from melder.aether.conduit.creations.creations import Creations
""",
    ),
    (
        """          (`_root_creations`) for `unique_per_conduit_lineage`, and the elected
          leader's store (`_cluster_creations.resolved_store()`) for
          `unique_per_conduit_cluster`.
""",
        """          (`_root_creations`) for `unique_per_conduit_lineage`, and the
          cluster's team store (`_cluster_creations.resolved_store()`, served
          while the cluster has an elected leader) for
          `unique_per_conduit_cluster`.
""",
    ),
    (
        """        owner's store for `unique`, the lineage root's for
        `unique_per_conduit_lineage`, the elected leader's for
        `unique_per_conduit_cluster` - so peers in a cluster or lineage
""",
        """        owner's store for `unique`, the lineage root's for
        `unique_per_conduit_lineage`, the cluster's team store for
        `unique_per_conduit_cluster` - so peers in a cluster or lineage
""",
    ),
    (
        """            - Unique uses the Spell owner, lineage uses this lineage's root,
              and cluster uses the currently elected leader's concrete store.
            - Shared-store purge requires the actual `_conduit_id` to own that
              store. A lesser's `_resolution_conduit_id` grants no authority.
""",
        """            - Unique uses the Spell owner, lineage uses this lineage's root,
              and cluster uses the cluster's team store.
            - Shared-store purge requires the actual `_conduit_id` to hold the
              authority: to own the store for unique and lineage, and to be the
              elected leader recorded on the cluster facade for cluster (the
              team store belongs to the cluster, so its owner id is the
              cluster's, 0.2.8237). A lesser's `_resolution_conduit_id` grants no
              authority.
""",
    ),
    (
        """        Returns:
            ConduitCreations: Existing store that this conduit may purge.
""",
        """        Returns:
            Creations: Existing store that this conduit may purge (a
                `ConduitCreations` except for the cluster's team store).
""",
    ),
    (
        """    def _get_purge_creations(self, spell: Spell) -> ConduitCreations:
""",
        """    def _get_purge_creations(self, spell: Spell) -> Creations:
""",
    ),
    (
        """        if existence is Existence.unique:
            creations = spell._owner_creations
            authority = "spell-owning conduit"
        elif existence is Existence.unique_per_conduit_lineage:
            creations = self._root_creations
            authority = "lineage root conduit"
        elif existence is Existence.unique_per_conduit_cluster:
            creations = self._cluster_creations.resolved_store()
            authority = "elected cluster leader"
        else:
            raise RuntimeError(f"Unsupported purge existence: {existence!r}.")
        if self._conduit_id != creations.owner_conduit_id:
            raise RuntimeError(
                f"Cannot purge spell '{spell.spell_name}' ({spell.spell_id}) "
                f"from conduit '{self._conduit_id}'; the {authority} "
                f"'{creations.owner_conduit_id}' must call purge."
            )
        return creations
""",
        """        creations: Creations
        if existence is Existence.unique:
            creations = spell._owner_creations
            authority = "spell-owning conduit"
            authority_conduit_id = creations.owner_conduit_id
        elif existence is Existence.unique_per_conduit_lineage:
            creations = self._root_creations
            authority = "lineage root conduit"
            authority_conduit_id = creations.owner_conduit_id
        elif existence is Existence.unique_per_conduit_cluster:
            # The team store belongs to the cluster (0.2.8237), so its owner id is
            # the cluster's; the elected leader recorded on the facade holds the
            # purge authority.
            creations = self._cluster_creations.resolved_store()
            authority = "elected cluster leader"
            authority_conduit_id = self._cluster_creations.leader_conduit_id
        else:
            raise RuntimeError(f"Unsupported purge existence: {existence!r}.")
        if self._conduit_id != authority_conduit_id:
            raise RuntimeError(
                f"Cannot purge spell '{spell.spell_name}' ({spell.spell_id}) "
                f"from conduit '{self._conduit_id}'; the {authority} "
                f"'{authority_conduit_id}' must call purge."
            )
        return creations
""",
    ),
    (
        """              root for `unique_per_conduit_lineage`, the elected leader for
              `unique_per_conduit_cluster`.
""",
        """              root for `unique_per_conduit_lineage`, the cluster's team store
              for `unique_per_conduit_cluster`.
""",
    ),
    (
        """              `unique_per_conduit_lineage` and the elected leader for
              `unique_per_conduit_cluster` (not live while none is elected).
""",
        """              `unique_per_conduit_lineage` and the cluster's team store for
              `unique_per_conduit_cluster` (not live while no leader is elected).
""",
    ),
    (
        """            # cluster/lineage live in the meld-supplied store (elected leader /
            # lineage-root), mirroring the front-door store selection above.
""",
        """            # cluster/lineage live in the meld-supplied store (cluster team store
            # / lineage root), mirroring the front-door store selection above.
""",
    ),
    (
        """              `unique_per_conduit_cluster` the elected leader's store, and is
              not live while no leader is elected.
""",
        """              `unique_per_conduit_cluster` the cluster's team store, and is
              not live while no leader is elected.
""",
    ),
    (
        """            # cluster/lineage live in the meld-supplied store (elected leader /
            # lineage-root); a cluster with no elected leader is simply not live.
""",
        """            # cluster/lineage live in the meld-supplied store (cluster team store
            # / lineage root); a cluster with no elected leader is simply not live.
""",
    ),
    (
        """                storage_scope_kind = "cluster_leader"
                storage_owner_conduit_id = None
            creation = (
                store.get_creation(spell_id) if store is not None else None
            )
            return {
                "is_live": creation is not None,
                "spell_id": spell_id,
                "spell_name": spell.spell_name,
                "existence": existence.name,
                "query_conduit_id": query_conduit_id,
                "storage_scope_kind": storage_scope_kind,
                "storage_owner_conduit_id": storage_owner_conduit_id,
                "active_spellspace_id": None,
""",
        """                # The label predates the team store (0.2.8237: the store is the
                # cluster's, served while a leader is elected); it is kept because
                # it is a published diagnostics value.
                storage_scope_kind = "cluster_leader"
                storage_owner_conduit_id = None
            creation = (
                store.get_creation(spell_id) if store is not None else None
            )
            return {
                "is_live": creation is not None,
                "spell_id": spell_id,
                "spell_name": spell.spell_name,
                "existence": existence.name,
                "query_conduit_id": query_conduit_id,
                "storage_scope_kind": storage_scope_kind,
                "storage_owner_conduit_id": storage_owner_conduit_id,
                "active_spellspace_id": None,
""",
    ),
]

space_meld_edits = [
    (
        """              `unique_per_conduit_cluster` melds resolved from inside the
              spellspace resolve into the same elected-leader store the owner
              conduit's cluster elected; a spellspace created after election
              still sees the filled facade through this shared reference.
""",
        """              `unique_per_conduit_cluster` melds resolved from inside the
              spellspace resolve into the same team store the owner conduit's
              cluster serves; a spellspace created after election still sees
              the filled facade through this shared reference.
""",
    ),
    (
        """              conduit, Spell owner, lineage root, or cluster leader store.
""",
        """              conduit, Spell owner, lineage root, or cluster team store.
""",
    ),
    (
        """            # cluster/lineage live in the meld-supplied store (elected leader /
            # lineage-root), mirroring the front-door store selection.
""",
        """            # cluster/lineage live in the meld-supplied store (cluster team store
            # / lineage root), mirroring the front-door store selection.
""",
    ),
    (
        """              store; `unique_per_conduit_cluster` the elected leader's store,
              and is not live while no leader is elected.
""",
        """              store; `unique_per_conduit_cluster` the cluster's team store,
              and is not live while no leader is elected.
""",
    ),
    (
        """            # cluster/lineage live in the meld-supplied store (elected leader /
            # lineage-root); a cluster with no elected leader is simply not live.
""",
        """            # cluster/lineage live in the meld-supplied store (cluster team store
            # / lineage root); a cluster with no elected leader is simply not live.
""",
    ),
]

space_edits = [
    (
        """        # `unique_per_conduit_cluster` spell resolved from within it stores in
        # the owner conduit's elected-leader store, so the spellspace meld
        # references the owner conduit's cluster facade
        # (`conduit_meld._cluster_creations`) rather than owning its own. The
        # facade is filled on election by ConduitCluster, so a spellspace built
        # after election still resolves into the same leader store.
""",
        """        # `unique_per_conduit_cluster` spell resolved from within it stores in
        # the owner conduit's cluster team store, so the spellspace meld
        # references the owner conduit's cluster facade
        # (`conduit_meld._cluster_creations`) rather than owning its own. The
        # facade is filled on election by ConduitCluster, so a spellspace built
        # after election still resolves into the same team store.
""",
    ),
    (
        """              Spell owner, lineage-root or cluster-leader store can be selected.
""",
        """              Spell owner, lineage-root or cluster team store can be selected.
""",
    ),
]

creations_edits = [
    (
        """        # (`unique_per_conduit_lineage` lineage root, `unique_per_conduit_cluster`
        # elected-leader store) lives on the meld front doors
""",
        """        # (`unique_per_conduit_lineage` lineage root, `unique_per_conduit_cluster`
        # cluster team store) lives on the meld front doors
""",
    ),
    (
        """        `ClusterCreations` does NOT extend this class - it extends `Cleanable`
        directly.
""",
        """        `ClusterCreations` does NOT extend this class - it extends `Cleanable`
        directly. A cluster's team store is a plain `Creations` that its
        `ConduitCluster` builds and owns (0.2.8237).
""",
    ),
]

door_edits = [
    (
        """        # unique_per_conduit_cluster: one instance per cluster, stored in the
        # elected leader's creations, resolved off the meld's cluster facade.
""",
        """        # unique_per_conduit_cluster: one instance per cluster, stored in the
        # cluster's team store (served while a leader is elected), resolved off
        # the meld's cluster facade. The emitted local keeps its historical name
        # `leader_creations`, so emitted door bodies are unchanged (0.2.8237).
""",
    ),
]

new_facade = (HERE / "cluster_creations_new.py").read_text(encoding="utf-8")
assert "\r" not in new_facade
FACADE.write_bytes(new_facade.replace("\n", "\r\n").encode("utf-8"))
print("facade rewritten")
print("cluster", edit_tool.apply(CLUSTER, cluster_edits))
print("cloud", edit_tool.apply(CLOUD, cloud_edits))
print("frame", edit_tool.apply(FRAME, frame_edits))
print("conduit_meld", edit_tool.apply(CONDUIT_MELD, conduit_meld_edits))
print("spellspace_meld", edit_tool.apply(SPACE_MELD, space_meld_edits))
print("spell_space", edit_tool.apply(SPACE, space_edits))
print("creations", edit_tool.apply(CREATIONS, creations_edits))
print("door", edit_tool.apply(DOOR, door_edits))
