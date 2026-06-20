import threading
from typing import TYPE_CHECKING, Dict, Set, Optional, List, ClassVar

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.creations.cluster_creations import ClusterCreations
from melder.aether.aetheric_frame.dev_ops.devops_identity import DevopsIdentity
from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
    DevopsInformationRegistry,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.aether.conduit.conduit_ward.contract.detail_reason import DetailReason
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeTransactionType,
)
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
if TYPE_CHECKING:
    from melder.aether.conduit.conduit import Conduit
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.bind.spell_index import SpellIndex

class ConduitCluster(Cleanable):
    """
    A membership group of conduits with TWO INDEPENDENT LAYERS:
    leaderless spell-sharing (the core, always on) and an OPTIONAL elected-leader
    team store (only ever needed for `unique_per_conduit_cluster` spells).

    Read this before reasoning about cluster behaviour. The two layers are easy
    to conflate, and most of the cluster works with NO leader at all.

    ==================================================================
    LAYER 1 - Spell sharing (the core; always on; needs NO leader)
    ==================================================================
    The cluster's primary job. Members automatically contract ("share") their
    shareable root `SpellIndex` lineages to one another, so every member can
    resolve every other member's shared roots. This layer is fully functional
    with no elected leader; a cluster can exist and share spells forever without
    one.

        - Membership is `members: Set[str]` (conduit ids).
        - `handle_join(conduit)`: add the conduit to `members`, refresh its
          shareable roots, then share its roots TO every existing peer and each
          peer's roots TO it (both directions).
        - `handle_leave(conduit)`: remove the conduit from `members`, tear down
          the shared roots in both directions, and drop its `shared_spells`
          entry.
        - Each individual share/unshare is its own per-pair `cluster_link`
          change-control transaction (opened via `peer.transaction(...)` inside
          `share_to_borrower` / `remove_shared_from_borrower`).
        - `shared_spells` maps owner conduit id -> the shareable root
          `SpellIndex`es that owner contributes.
        - `auto_link_dependencies`: when True each shared root drags its
          dependency closure into the contract; when False only the root shares.

    CURRENT GAP (intended work, not yet built): the membership mutation
    (`members.add` / `members.discard`) and the share fan-out are NOT wrapped as
    a single atomic transaction today - membership is a bare lock op and each
    share is a separate `cluster_link` transaction, so a concurrent join, leave,
    or ownership transfer can interleave mid-entry/exit. Transactionalizing the
    whole conduit entry/exit is planned.

    ==================================================================
    LAYER 2 - Elected-leader team store (OPTIONAL; only for
              `unique_per_conduit_cluster` spells)
    ==================================================================
    A separate overlay. A `unique_per_conduit_cluster` spell must resolve into
    ONE shared creation store across the whole cluster: the elected leader
    conduit's `Creations`.

        - The LIVE team-store facade is PER MEMBER ROOT CONDUIT. Each root
          conduit owns a `_cluster_creations: ClusterCreations`, and the conduits
          in its lineage share that one facade. The meld front door resolves a
          `unique_per_conduit_cluster` instance through
          `conduit._cluster_creations.resolved_store()`.
        - `elect_leader(leader_conduit_id)` (transactional): opens an
          `ELECT_CONDUIT_CLUSTER_LEADER` transaction, then `bind_elected_leader`
          walks `members` and binds every member root's facade to the elected
          leader's `_creations`, recording `master_conduit_id`. Election is
          inert -> active, so no lineage drain is required.
        - `unelect_leader()` (transactional): opens an
          `UNELECT_CONDUIT_CLUSTER_LEADER` transaction whose strategy drains
          every member root lineage to zero (so no meld is mid-create against the
          leader store), `unbind_elected_leader` unbinds every member facade and
          clears `master_conduit_id`, then the lineages reopen on every exit path
          (fail-closed).
        - `bind_elected_leader` REFUSES re-election: it raises if
          `master_conduit_id` is already set. Unelect back to inert before
          electing a different leader.
        - While inert (no leader), `_cluster_creations.resolved_store()`
          HARD-ERRORS, so a `unique_per_conduit_cluster` meld with no leader
          fails at the meld door instead of resolving into nothing.
        - Concurrency safety for bind/unbind comes from the elect/unelect
          transaction quiesce (the strategy seals the member conduits, and for
          unelect drains their lineages), NOT from a lock on the facade.

    GOTCHA: the cluster also owns a `self.cluster_creations: ClusterCreations`
    field, but it is CURRENTLY VESTIGIAL - it is constructed and cleaned up, yet
    never bound, unbound, or resolved. The operative team-store facades are the
    per-root-conduit `_cluster_creations` instances described above. Do not
    confuse the cluster-owned facade with the per-conduit ones.

    ==================================================================
    Invariants
    ==================================================================
        - `master_conduit_id` is the single source of truth for "is a leader
          elected": set by `bind_elected_leader`, cleared by
          `unbind_elected_leader`, `None` when inert.
        - One cluster per conduit (INTENDED): a conduit owns a single
          `_cluster_creations` facade, so it can only ever front ONE cluster's
          team store. Rejecting a join when the conduit is already clustered is
          planned; it is not enforced yet.

    Threading:
        One internal `_lock` (RLock) guards membership and shared-root state.
        Team-store bind/unbind safety comes from the elect/unelect transaction
        quiesce, not from this lock.

    Lifecycle:
        Becomes unusable after `cleanup()` completes; cleanup cleans the owned
        (currently vestigial) `cluster_creations` facade and drops references.

    Attributes:
        members:
            Set of conduit ids currently in the cluster.
        shared_spells:
            Mapping from owner conduit id to the shareable root `SpellIndex`
            values contributed by that owner.
        auto_link_dependencies:
            When True, a dependency closure is auto-contracted with each shared
            root. When False, only the root spell is linked.
        master_conduit_id:
            Elected leader conduit id, or None when no leader is elected (inert).
        cluster_creations:
            Cluster-owned team-store facade. Currently vestigial (see the GOTCHA
            above); the live facades are the per-root-conduit `_cluster_creations`.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_name",
        "_registry",
        "_aetheric_frame_name",
        "members",
        "shared_spells",
        "auto_link_dependencies",
        "_cleaned",
        "_id",
        "_devops_identity",
        "_devops_information_registry",
        "cluster_creations",
        "master_conduit_id",
    ]

    def __init__(
            self,
            name: str,
            registry: Dict[str, Conduit],
            aetheric_frame_name: str,
            devops_information_registry: DevopsInformationRegistry,
            auto_link_dependencies: bool = True,
    ):
        """
        Initialize a cluster container.

        Args:
            name: Cluster name.
            registry: Borrowed frame-local conduit registry keyed by conduit id.
            aetheric_frame_name: Owning frame name for contract operations.
            devops_information_registry:
                Frame-owned dev-ops registry used for cluster identity and
                membership tracking.
            auto_link_dependencies: If True, sharing pulls dependency closure.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()
        self._id: str = IDBuilder.create_id()
        self._name: str = name
        self._registry: Dict[str, Conduit] = registry
        self._aetheric_frame_name: str = aetheric_frame_name
        self._devops_information_registry: DevopsInformationRegistry = (
            devops_information_registry
        )
        self.members: Set[str] = set()
        self.shared_spells: Dict[str, Set[SpellIndex]] = {}
        self.auto_link_dependencies: bool = auto_link_dependencies
        self._devops_identity: DevopsIdentity = DevopsIdentity(
            owner_kind="conduit_cluster",
            owner_id=self._id,
            aetheric_frame_name=self._aetheric_frame_name,
            metadata={
                "cluster_name": self._name,
                "auto_link_dependencies": self.auto_link_dependencies,
            },
            available_transactions=(
                "cluster_link",
                "elect_conduit_cluster_leader",
                "unelect_conduit_cluster_leader",
            ),
        )
        self._devops_identity.attach_registry(
            self._devops_information_registry,
            object_ref=self,
        )
        # Cluster team-store facade. The cluster owns it; it fronts the elected
        # leader conduit's `Creations` and starts disabled (no leader). A
        # `unique_per_conduit_cluster` spell resolves its instance through this
        # facade. The leader bind/unbind happens through the elect/unelect
        # cluster-leader transactions (not here).
        self.cluster_creations: ClusterCreations = ClusterCreations()
        self.master_conduit_id: Optional[str] = None

    def cleanup(self) -> None:
        """
        Idempotently clear cluster membership state and release references.

        Contract:
            - Safe to call multiple times.
            - Clears member and shared-root registries before dropping owned
              references.
            - Leaves the instance permanently cleaned.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            member_ids = list(self.members)
            if self.members is not None:
                self.members.clear()
            if self.shared_spells is not None:
                for v in self.shared_spells.values():
                    try:
                        v.clear()
                    except Exception:
                        pass
                self.shared_spells.clear()
            for conduit_id in member_ids:
                self._devops_identity.unregister_cluster_member(conduit_id)
            self._devops_identity.cleanup()
            self.cluster_creations.cleanup()
            del self.cluster_creations
            del self.master_conduit_id
            del self.auto_link_dependencies
            del self._devops_information_registry
            del self._devops_identity
            del self._registry
            del self._aetheric_frame_name
            del self._name
        del self._lock

    @property
    def id(self) -> str:
        """
        Unique identifier for the cluster.
        """
        return self._id

    @property
    def name(self) -> str:
        """
        Name of the cluster.
        """
        return self._name

    def add_member(self, conduit_id: str) -> None:
        """
        Add a conduit id to the cluster membership.

        Args:
            conduit_id: Conduit identifier.
        """
        self.check_cleaned()
        with self._lock:
            self.members.add(conduit_id)
            self._devops_identity.register_cluster_member(conduit_id)

    def remove_member(self, conduit_id: str) -> None:
        """
        Remove a conduit id and its shared roots.

        Args:
            conduit_id: Conduit identifier.
        """
        self.check_cleaned()
        with self._lock:
            self.members.discard(conduit_id)
            self.shared_spells.pop(conduit_id, None)
            self._devops_identity.unregister_cluster_member(conduit_id)

    def add_shared_spell(self, owner_id: str, spell_index: SpellIndex) -> None:
        """
        Record a shareable root SpellIndex for an owner.

        Args:
            owner_id: Conduit id that owns the spell.
            spell_index: Root SpellIndex to share.
        """
        self.check_cleaned()
        with self._lock:
            bucket = self.shared_spells.setdefault(owner_id, set())
            bucket.add(spell_index)

    def remove_shared_spell(self, owner_id: str, spell_index: SpellIndex) -> None:
        """
        Remove a recorded shareable root for an owner.

        Args:
            owner_id: Conduit id that owns the spell.
            spell_index: Root SpellIndex to remove.
        """
        self.check_cleaned()
        with self._lock:
            bucket = self.shared_spells.get(owner_id)
            if bucket is None:
                return
            bucket.discard(spell_index)
            if not bucket:
                self.shared_spells.pop(owner_id, None)

    def get_shared_spells(self) -> Dict[str, Set[SpellIndex]]:
        """
        Snapshot of shared roots.

        Returns:
            Dict mapping owner_id -> set of SpellIndex.
        """
        self.check_cleaned()
        with self._lock:
            return {k: set(v) for k, v in self.shared_spells.items()}

    def get_members(self) -> Set[str]:
        """
        Snapshot of cluster members.

        Returns:
            Set of conduit ids.
        """
        self.check_cleaned()
        with self._lock:
            return set(self.members)

    @staticmethod
    def _assert_normal_conduit(conduit: Conduit) -> None:
        """
        Raise when a cluster operation targets a non-normal conduit.

        Contract:
            - Cluster membership and share flows operate only on normal/root conduits.
            - Lesser, pooled, or cleaned conduits are rejected before cluster state mutates.
        """
        if conduit._conduit_state is not ConduitState.normal:
            raise RuntimeError(
                "ConduitCluster operations require a normal conduit."
            )

    # ------------------------------------------------------------------
    # Share helpers (operate on live conduit objects)
    # ------------------------------------------------------------------
    def handle_join(self, conduit: Conduit) -> None:
        """
        Add a member and auto-share all roots between the new member and existing peers.

        Contract:
            - Adds the joining conduit id to cluster membership first.
            - Refreshes shareable roots for all current members, including the
              new member.
            - Shares roots in both directions between the joiner and each
              existing peer.

        Args:
            conduit: The conduit joining the cluster.

        Returns:
            None
        """
        self.check_cleaned()
        self._assert_normal_conduit(conduit)
        with self._lock:
            self.members.add(conduit._id)
            member_ids = set(self.members)

        # Refresh registry for all members (including new)
        for member_id in member_ids:
            member = self._resolve_conduit_by_id(member_id)
            if member is None:
                continue
            self.refresh_shareable_roots(member)

        # Share both directions between joiner and existing members
        for peer_id in member_ids:
            if peer_id == conduit._id:
                continue
            peer = self._resolve_conduit_by_id(peer_id)
            if peer is None:
                continue
            self.share_to_borrower(conduit, peer)
            self.share_to_borrower(peer, conduit)

    def handle_leave(self, conduit: Conduit) -> None:
        """
        Remove a member and tear down shared roots between it and remaining peers.

        Contract:
            - Removes the leaving conduit id from cluster membership first.
            - Removes roots owned by the leaver from all remaining peers.
            - Removes roots owned by remaining peers from the leaving conduit.
            - Drops the leaver's shared-root registry entry after teardown.

        Args:
            conduit: The conduit leaving the cluster.

        Returns:
            None
        """
        self.check_cleaned()
        self._assert_normal_conduit(conduit)
        with self._lock:
            self.members.discard(conduit._id)
            member_ids = set(self.members)
            leaver_id = conduit._id

        peers: List[Conduit] = []
        for conduit_id in member_ids:
            peer = self._resolve_conduit_by_id(conduit_id)
            if peer is not None:
                peers.append(peer)

        # Remove spells this conduit owned from peers
        for peer in peers:
            self.remove_shared_from_borrower(
                conduit,
                peer,
                self._aetheric_frame_name,
            )

        # Remove spells peers owned from this conduit
        for peer in peers:
            self.remove_shared_from_borrower(
                peer,
                conduit,
                self._aetheric_frame_name,
            )

        with self._lock:
            self.shared_spells.pop(leaver_id, None)

    # ------------------------------------------------------------------
    # Cluster leader election (bind / unbind the shared team store)
    # ------------------------------------------------------------------
    def bind_elected_leader(self, leader_conduit_id: str) -> None:
        """
        Bind the elected leader's creation store into every member root's facade.

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
            - Records the elected leader id in `master_conduit_id`.
            - Binds only: it does not begin, commit, or abort the election
              transaction. The caller runs it as the in-window effect.

        Args:
            leader_conduit_id (str):
                Conduit id of the elected leader. Must resolve to a live, normal
                cluster member root whose creation store becomes the shared store.

        Threading:
            Runs inside the election transaction's held window, after the member
            conduits are sealed, so membership is stable for the walk and no meld
            is mid-create against an inert facade (election is inert -> active).
            Members are live root conduits and the member set is a thread-safe
            collection, so the walk needs no snapshot and no extra lock.

        Returns:
            None.

        Raises:
            RuntimeError: If the cluster has been cleaned, or a leader is already
                elected (re-election without an intervening unelect).
        """
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

    def unbind_elected_leader(self) -> None:
        """
        Unbind the leader's creation store from every member root's facade.

        Purpose:
            Deactivate the cluster team store and return the cluster to inert, so a
            `unique_per_conduit_cluster` meld hard-errors again until a new leader
            is elected.

        Contract:
            - Walks the current member set and unbinds each member root's
              `_cluster_creations` facade, dropping its reference to the leader
              store. The leader conduit still owns and cleans that store; the
              facade only releases the reference, never cleans the store.
            - Idempotent per facade: unbinding an inert facade is a no-op.
            - Clears `master_conduit_id`.
            - Unbinds only: it does not begin, commit, or abort the unelection
              transaction. The caller runs it as the in-window effect.

        Threading:
            Runs inside the unelection transaction's held window, after every
            member root lineage has been drained to zero, so no meld is mid-create
            against the leader store when it is released. Members are live root
            conduits and the member set is a thread-safe collection, so the walk
            needs no snapshot and no extra lock.

        Returns:
            None.
        """
        self.check_cleaned()
        for member_id in self.members:
            member = self._resolve_conduit_by_id(member_id)
            member._cluster_creations.unbind()
        self.master_conduit_id = None

    def elect_leader(self, leader_conduit_id: str) -> None:
        """
        Elect a cluster leader inside an `ELECT_CONDUIT_CLUSTER_LEADER` transaction.

        Purpose:
            Wrap the leader bind in the change-control transaction that isolates
            it. The DevOps strategy owns the isolation (sealing the member
            conduits); this method owns the in-window effect (`bind_elected_leader`).

        Contract:
            - Opens the elect transaction through the frame mediator using the
              cluster's own dev-ops identity, supplying the member conduit ids as
              the seal footprint. The strategy claims those conduits EXCLUSIVE for
              the held window.
            - Runs `bind_elected_leader` as the in-window effect, then commits.
            - Election is an inert -> active transition, so no member lineage drain
              is required (the cluster door hard-errors while inert, so no meld is
              mid-create against the team store).
            - On any failure the transaction is ended with `success=False`
              (abort) and the original exception propagates; never swallowed.

        Args:
            leader_conduit_id (str):
                Conduit id of the elected leader. Must resolve to a live, normal
                cluster member root whose creation store becomes the shared store.

        Returns:
            None.

        Raises:
            RuntimeError: If the cluster has been cleaned, or the leader conduit
                cannot be resolved.
            Exception: Any error raised by `bind_elected_leader` is propagated
                after the transaction is aborted.

        Threading:
            The mediator seals the member conduits before the bind runs, so
            membership is stable and the effect executes under exclusive locks.
        """
        self.check_cleaned()
        leader = self._resolve_conduit_by_id(leader_conduit_id)
        if leader is None:
            raise RuntimeError(
                "Cannot elect a cluster leader: leader conduit could not be resolved."
            )
        mediator = leader._get_required_transaction_mediator()
        mediator.start_transaction(
            identity=self._devops_identity,
            transaction_type=ChangeTransactionType.ELECT_CONDUIT_CLUSTER_LEADER,
            metadata={
                "origin_surface": "conduit_cluster.elect_leader",
                "cluster_id": self._id,
                "member_conduit_ids": tuple(sorted(self.members)),
                "leader_conduit_id": leader_conduit_id,
            },
        )
        succeeded = False
        try:
            self.bind_elected_leader(leader_conduit_id)
            succeeded = True
        finally:
            mediator.end_transaction(
                expected_type=ChangeTransactionType.ELECT_CONDUIT_CLUSTER_LEADER,
                success=succeeded,
            )

    def unelect_leader(self) -> None:
        """
        Unelect the cluster leader inside an `UNELECT_CONDUIT_CLUSTER_LEADER`
        transaction.

        Purpose:
            Wrap the leader unbind in the change-control transaction that makes it
            safe. The DevOps strategy owns the isolation and the lineage freeze;
            this method owns the in-window effect (`unbind_elected_leader`).

        Contract:
            - Opens the unelect transaction through the frame mediator using the
              cluster's own dev-ops identity, supplying the member conduit ids as
              the seal footprint and the member root ids as the drain footprint.
            - The strategy claims the member conduits EXCLUSIVE and, in its
              `on_start`, drains every member root lineage to zero through the
              DevOps-owned `ConduitLineageGateOps`, so no meld is mid-create
              against the leader store. Its `on_end` reopens every member root
              lineage on every exit path (fail-closed).
            - Runs `unbind_elected_leader` as the in-window effect, then commits.
            - An empty cluster has no bound leader, so this is a no-op and opens no
              transaction (there is also no member through which to reach the
              mediator).
            - On any failure the transaction is ended with `success=False`
              (abort) and the original exception propagates; never swallowed.

        Returns:
            None.

        Raises:
            RuntimeError: If the cluster has been cleaned, or a member conduit
                cannot be resolved.
            Exception: Any error raised by the lineage drain or
                `unbind_elected_leader` is propagated after the transaction is
                aborted and the lineages are reopened.

        Threading:
            Every member root lineage is drained to zero before the in-window
            unbind, so no meld is mid-create against the leader store when its
            reference is released.
        """
        self.check_cleaned()
        member_ids = tuple(sorted(self.members))
        if not member_ids:
            self.unbind_elected_leader()
            return
        any_member = self._resolve_conduit_by_id(member_ids[0])
        if any_member is None:
            raise RuntimeError(
                "Cannot unelect a cluster leader: member conduit could not be resolved."
            )
        mediator = any_member._get_required_transaction_mediator()
        gate_ops = any_member._aetheric_frame.dev_ops_manager.conduit_lineage_gate_ops
        mediator.start_transaction(
            identity=self._devops_identity,
            transaction_type=ChangeTransactionType.UNELECT_CONDUIT_CLUSTER_LEADER,
            metadata={
                "origin_surface": "conduit_cluster.unelect_leader",
                "cluster_id": self._id,
                "member_conduit_ids": member_ids,
                "member_root_conduit_ids": member_ids,
                "conduit_lineage_gate_ops": gate_ops,
            },
        )
        succeeded = False
        try:
            self.unbind_elected_leader()
            succeeded = True
        finally:
            mediator.end_transaction(
                expected_type=ChangeTransactionType.UNELECT_CONDUIT_CLUSTER_LEADER,
                success=succeeded,
            )

    def refresh_shareable_roots(self, owner: Conduit) -> None:
        """
        Ensure shared_spells has all shareable SpellIndexes for the owner.

        Args:
            owner: Conduit whose shareable roots should be recorded.

        Returns:
            None
        """
        self.check_cleaned()
        self._assert_normal_conduit(owner)
        shareables = self._get_shareable_spells(owner)
        owner_id = owner._id
        for spell in shareables:
            self.add_shared_spell(owner_id, spell.spell_index)

    def refresh_member_shares(self, conduit: Conduit) -> None:
        """
        Refresh and (re)share this member's shareable roots with all peers in the cluster.

        Args:
            conduit: Member conduit whose roots should be refreshed.

        Returns:
            None
        """
        self.check_cleaned()
        self._assert_normal_conduit(conduit)
        with self._lock:
            member_ids = set(self.members)
        self.refresh_shareable_roots(conduit)
        for peer_id in member_ids:
            if peer_id == conduit._id:
                continue
            peer = self._resolve_conduit_by_id(peer_id)
            if peer is None:
                continue
            self.share_to_borrower(conduit, peer)
            self.share_to_borrower(peer, conduit)

    def add_and_share_spell(
            self,
            owner: Conduit,
            spell: Spell,
            link_dependencies: Optional[bool] = None,
    ) -> None:
        """
        Explicitly add a shared root and propagate it to current peers.

        Contract:
            - Records the root in `shared_spells` before propagation.
            - Uses cluster dependency policy unless an explicit override is
              supplied.
            - Attempts propagation peer by peer and skips peers that fail
              without aborting the whole share pass.

        Args:
            owner: Conduit that owns the spell.
            spell: Spell object to share.
            link_dependencies: Override auto_link_dependencies if provided.
        """
        self.check_cleaned()
        self._assert_normal_conduit(owner)
        owner_id = owner._id
        self.add_shared_spell(owner_id, spell.spell_index)
        # Decide dependency behaviour (explicit override beats cluster default)
        link_deps = self.auto_link_dependencies if link_dependencies is None else bool(link_dependencies)

        with self._lock:
            member_ids = set(self.members)
        for peer_id in member_ids:
            if peer_id == owner_id:
                continue
            peer = self._resolve_conduit_by_id(peer_id)
            if peer is None:
                continue
            if link_deps:
                cluster_root_id = self._cluster_root_id(owner_id, spell.spell_id)
                try:
                    with peer.transaction(
                        "cluster_link",
                        conduits=[peer, owner],
                    ):
                        peer.add_spell_to_contract(
                            spell=spell,
                            conduit=owner,
                            permissions=getattr(spell, "permissions", "create"),
                            aetheric_frame=self._aetheric_frame_name,
                            reason=DetailReason.root,
                            root_spell_id=cluster_root_id,
                            link_dependencies=True,
                        )
                except Exception:
                    continue

    def remove_and_strip_spell(self, owner: Conduit, spell: Spell) -> None:
        """
        Explicitly remove a shared root from the cluster and strip it from peers.

        Contract:
            - Removes the root from `shared_spells` before peer cleanup.
            - Attempts to remove cluster-root contracts from each peer.
            - Re-adds the plain root contract only when the cluster-root removal
              succeeded and the follow-up manual root re-add also succeeds.

        Args:
            owner: Conduit that owns the spell.
            spell: Spell object to remove.
        """
        self.check_cleaned()
        self._assert_normal_conduit(owner)
        owner_id = owner._id
        self.remove_shared_spell(owner_id, spell.spell_index)

        with self._lock:
            member_ids = set(self.members)
        for peer_id in member_ids:
            if peer_id == owner_id:
                continue
            peer = self._resolve_conduit_by_id(peer_id)
            if peer is None:
                continue
            try:
                cluster_root_id = self._cluster_root_id(owner_id, spell.spell_id)
                with peer.transaction(
                    "cluster_link",
                    conduits=[peer, owner],
                ):
                    peer.remove_root_from_contracts(
                        root_spell_id=cluster_root_id,
                        conduit=owner,
                        aetheric_frame=self._aetheric_frame_name,
                    )
            except Exception:
                continue
            else:
                try:
                    with peer.transaction(
                        "cluster_link",
                        conduits=[peer, owner],
                    ):
                        peer.add_spell_to_contract(
                            spell=spell,
                            conduit=owner,
                            permissions=getattr(spell, "permissions", "create"),
                            aetheric_frame=self._aetheric_frame_name,
                            reason=DetailReason.manual,
                            root_spell_id=spell.spell_id,
                            link_dependencies=False,
                        )
                except Exception:
                    continue

    def share_to_borrower(self, owner: Conduit, borrower: Conduit) -> None:
        """
        Contract all shared roots from one owner into one borrower.

        Contract:
            - Reads the owner's shared roots under the cluster lock.
            - Resolves each root back to a live spell object before contracting.
            - Uses the current dependency-sharing policy to decide whether
              dependency closure is included.

        Args:
            owner: Conduit that owns the roots.
            borrower: Conduit that should receive the contracts.

        Returns:
            None
        """
        self.check_cleaned()
        self._assert_normal_conduit(owner)
        self._assert_normal_conduit(borrower)
        owner_id = owner._id
        with self._lock:
            indices = set(self.shared_spells.get(owner_id, set()))
            link_deps = bool(self.auto_link_dependencies)
        for idx in indices:
            spell = self._resolve_spell_from_index(owner, idx)
            if spell is None:
                continue
            try:
                cluster_root_id = self._cluster_root_id(owner_id, spell.spell_id)
                with borrower.transaction(
                    "cluster_link",
                    conduits=[borrower, owner],
                ):
                    borrower.add_spell_to_contract(
                        spell=spell,
                        conduit=owner,
                        permissions=getattr(spell, "permissions", "create"),
                        aetheric_frame=self._aetheric_frame_name,
                        reason=DetailReason.root,
                        root_spell_id=cluster_root_id,
                        link_dependencies=link_deps,
                    )
            except Exception:
                continue

    def remove_shared_from_borrower(self, owner: Conduit, borrower: Conduit, aetheric_frame: str = "default") -> None:
        """
        Remove all shared roots from one owner on the borrower side.

        Contract:
            - Reads the owner's shared roots under the cluster lock.
            - Resolves each root back to a live spell object before removal.
            - Removes cluster-scoped root contracts only; unrelated manual
              contracts are left to other flows.

        Args:
            owner: Conduit that owns the roots.
            borrower: Conduit to remove the contracted roots from.
            aetheric_frame: Frame name for removal calls.

        Returns:
            None
        """
        self.check_cleaned()
        self._assert_normal_conduit(owner)
        self._assert_normal_conduit(borrower)
        owner_id = owner._id
        with self._lock:
            indices = set(self.shared_spells.get(owner_id, set()))
        for idx in indices:
            spell = self._resolve_spell_from_index(owner, idx)
            if spell is None:
                continue
            try:
                cluster_root_id = self._cluster_root_id(owner_id, spell.spell_id)
                with borrower.transaction(
                    "cluster_link",
                    conduits=[borrower, owner],
                ):
                    borrower.remove_root_from_contracts(
                        root_spell_id=cluster_root_id,
                        conduit=owner,
                        aetheric_frame=aetheric_frame,
                    )
            except Exception:
                continue

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _get_shareable_spells(self, conduit: Conduit) -> List[Spell]:
        """
        Return shareable spells from a conduit (existence == unique_per_conduit_cluster).

        Args:
            conduit: Conduit whose spellbook to inspect.

        Returns:
            list: Shareable spell objects.
        """
        self.check_cleaned()
        book = conduit._spellbook
        if book is None or book._spells is None:
            return []
        with book._lock:
            return [
                spell for spell in book._spells.values()
                if hasattr(spell, "existence") and spell.existence == Existence.unique_per_conduit_cluster
            ]

    def _resolve_spell_from_index(self, conduit: Conduit, spell_index: SpellIndex) -> Optional[Spell]:
        """
        Resolve a Spell object from a conduit given its SpellIndex.

        Args:
            conduit: Conduit that owns the SpellIndex.
            spell_index: SpellIndex to resolve.

        Returns:
            Optional[Spell]: The spell if found.
        """
        self.check_cleaned()
        book = conduit._spellbook
        if book is None or book._spells is None:
            return None
        with book._lock:
            return book._spells.get(spell_index)

    def _resolve_conduit_by_id(self, conduit_id: str) -> Optional[Conduit]:
        """
        Resolve one conduit directly from the borrowed frame-local registry.

        Args:
            conduit_id: Conduit identifier to resolve.

        Returns:
            Optional[Conduit]: Matching conduit when present, else None.
        """
        self.check_cleaned()
        return self._registry.get(conduit_id)

    # ------------------------------------------------------------------
    # Configuration / diagnostics
    # ------------------------------------------------------------------
    def set_auto_link_dependencies(self, enabled: bool) -> None:
        """
        Configure whether a dependency closure is auto-contracted when sharing roots.

        Args:
            enabled: True to include deps, False for roots only.
        """
        self.check_cleaned()
        with self._lock:
            self.auto_link_dependencies = bool(enabled)

    def _cluster_root_id(self, owner_id: str, spell_id: str) -> str:
        """
        Build a cluster-scoped root spell identifier for contract sources.

        This tag allows the cluster to remove only the contracts it created
        without disrupting pre-existing manual links that may share the same
        spell root.

        Args:
            owner_id: Conduit id that owns the shared spell.
            spell_id: Spell version id for the shared root.

        Returns:
            str: Deterministic cluster-scoped root identifier.
        """
        self.check_cleaned()
        return f"cluster:{self._name}:{owner_id}:{spell_id}"

    def describe(self) -> dict:
        """
        Return a diagnostic snapshot of the cluster.

        Returns:
            dict:
                Snapshot containing cluster name, dependency-link policy,
                member ids, and shared-root lineage ids grouped by owner.
        """
        self.check_cleaned()
        with self._lock:
            shared_summary = {
                owner: [idx.id for idx in indices]
                for owner, indices in self.shared_spells.items()
            }
            return {
                "name": self._name,
                "auto_link_dependencies": self.auto_link_dependencies,
                "members": list(self.members),
                "shared_spells": shared_summary,
            }

