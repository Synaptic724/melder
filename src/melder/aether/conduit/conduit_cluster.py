import threading
from contextlib import nullcontext
from typing import TYPE_CHECKING, Dict, Set, Optional, List, ClassVar

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.aetheric_frame.dev_ops.devops_identity import DevopsIdentity
from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
    DevopsInformationRegistry,
)
from melder.crystallizer.crystallizer import Crystallizer
from melder.crystallizer.crystals.cluster_crystal import (
    ClusterCrystal,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.aether.conduit.creations.creations import Creations
from melder.aether.conduit.conduit_ward.contract.detail_reason import DetailReason
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeTransactionType,
)
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
    shareable root spell indexes to one another, so every member can
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
        - `release_member(conduit)`: the ordered exit every leave takes -
          `handle_leave` first (it unelects first when the leaver leads), then
          `remove_member` (the DevOps membership edge and the record). The
          cloud's explicit leave and a root's teardown both run it (0.2.8236).
        - `drop_member(conduit)`: the same exit without transactions, for a
          root torn down while its frame is torn down (no transaction can
          start then) or whose transactional exit failed in its teardown.
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

        - The LIVE team-store facade is PER MEMBER ROOT CONDUIT. Each root
          conduit owns a `_cluster_creations: ClusterCreations`, and the conduits
          in its lineage share that one facade. The meld front door resolves a
          `unique_per_conduit_cluster` instance through
          `conduit._cluster_creations.resolved_store()`.
        - `elect_leader(leader_conduit_id)` (transactional): opens an
          `ELECT_CONDUIT_CLUSTER_LEADER` transaction, then `bind_elected_leader`
          walks `members` and binds every member root's facade to the team
          store with the elected leader's id (the facade's purge authority),
          recording `master_conduit_id`. Election is inert -> active, so no
          lineage drain is required.
        - `unelect_leader()` (transactional): opens an
          `UNELECT_CONDUIT_CLUSTER_LEADER` transaction whose strategy drains
          every member root lineage to zero (so no meld is mid-create against the
          team store), `unbind_elected_leader` unbinds every member facade and
          clears `master_conduit_id`, then the lineages reopen on every exit path
          (fail-closed). The team store and its instances stay with the cluster.
        - `bind_elected_leader` REFUSES re-election: it raises if
          `master_conduit_id` is already set. Unelect back to inert before
          electing a different leader.
        - While inert (no leader), `_cluster_creations.resolved_store()`
          HARD-ERRORS, so a `unique_per_conduit_cluster` meld with no leader
          fails at the meld door instead of resolving into nothing.
        - Concurrency safety for bind/unbind comes from the elect/unelect
          transaction quiesce (the strategy seals the member conduits, and for
          unelect drains their lineages), NOT from a lock on the facade.

    ==================================================================
    Invariants
    ==================================================================
        - `master_conduit_id` is the single source of truth for "is a leader
          elected": set by `bind_elected_leader`, cleared by
          `unbind_elected_leader`, `None` when inert.
        - One cluster per conduit: a conduit owns a single
          `_cluster_creations` facade, so it can only ever front ONE cluster's
          team store; `ConduitCloud.add_conduit_to_cluster` refuses a join when
          the conduit is already clustered.
        - A torn-down root is never a member: a normal root's teardown leaves
          its cluster first (`Conduit._leave_cluster_for_teardown`), so
          `members` and `master_conduit_id` only ever hold live roots and every
          member walk (elect, unelect, join, delete) finds each member
          (0.2.8236; before, the dead id stayed and those walks failed on it).
        - The team store lives exactly as long as the cluster: built with it,
          never disposed by an election, an unelection or a member's exit, and
          disposed by `cleanup()` (0.2.8237).

    Threading:
        One internal `_lock` (RLock) guards membership and shared-root state.
        Team-store bind/unbind safety comes from the elect/unelect transaction
        quiesce, not from this lock.

    Lifecycle:
        Becomes unusable after `cleanup()` completes; cleanup clears membership
        and shared-root state, disposes the team store's instances (raising their
        disposal failures after it finished) and drops references.

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

    Registration:
        MELDER KERNEL - guarded. Clusters are created and joined through
        conduit/frame verbs, not constructed by users.

    Subsystem Context:
        The third inter-conduit relationship, alongside links and contracts.
        `ConduitWard` handles pairwise relationships; a cluster is the N-way
        one, and it is built ON TOP of ward contracting rather than beside it -
        each share is an ordinary `cluster_link` transaction producing ordinary
        contracts. Its storage sibling `ClusterCreations` extends `Cleanable`
        directly rather than `Creations`, because cluster scope is not a
        conduit scope.

    System Context:
        The two-layer split documented above is the thing to internalize,
        because conflating the layers produces wrong conclusions about
        clusters. Layer 1 - spell sharing - is the actual purpose and needs NO
        leader; a cluster can share roots forever with `master_conduit_id` as
        None. Layer 2 exists ONLY to give `unique_per_conduit_cluster` spells a
        single owning store, which is a question that simply does not arise
        unless such a spell exists.
        Sharing uses a cluster-scoped `root_spell_id` of the form
        `cluster:{name}:{owner_id}:{spell_id}` precisely so cluster teardown
        removes only cluster-created contracts and cannot disturb links a
        member formed independently. Permissions default to the spell's own
        `permissions` with a `create` fallback, because a cluster whose members
        could only READ each other's roots would be inert.
        The CURRENT GAP above is a real, documented limitation, not an
        oversight: membership mutation and the share fan-out are not yet one
        atomic transaction, so a concurrent join, leave, or ownership transfer
        can interleave mid-entry. Leadership is likewise a runtime election and
        is never replayed from a record - the crystallizer's
        `cluster_membership` preflight row reports a recorded leader as INFO
        rather than restoring it, for exactly this reason.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. A membership group of conduits with TWO INDEPENDENT LAYERS: leaderless
        spell-sharing (the core, always on) and an OPTIONAL elected-leader team store (only ever
        needed for `unique_per_conduit_cluster` spells). Melder kernel machinery: read it to
        understand the runtime, do not drive it directly.
    """
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
        "master_conduit_id",
        "_team_store",
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

        Contract:
            - Builds the cluster's team store (owner and scope id = the cluster
              id), which holds the cluster's `unique_per_conduit_cluster`
              instances until `cleanup()`.

        Returns:
            None.
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
                "cluster_join",
                "cluster_leave",
                "elect_conduit_cluster_leader",
                "unelect_conduit_cluster_leader",
            ),
        )
        self._devops_identity.attach_registry(
            self._devops_information_registry,
            object_ref=self,
        )
        self.master_conduit_id: Optional[str] = None
        # The cluster's team store (0.2.8237): `unique_per_conduit_cluster`
        # instances live here for the cluster's whole life; an election only
        # binds the member facades to it.
        self._team_store: Creations = Creations(
            owner_conduit_id=self._id,
            id=self._id,
        )
        # Record: an empty created cluster IS configured state (its name
        # exists in the frame cloud); emit the birth snapshot so restore
        # rebuilds empty clusters too (config-less-unit-at-init precedent).
        with self._lock:
            self._emit_cluster_record()

    def cleanup(self) -> None:
        """
        Idempotently clear cluster membership state, dispose the team store and release references.

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
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            # Record eviction: a live cluster deletion takes its twin with
            # it (in Aether full teardown the crystallizer is already
            # cleaned - frames die first - so this skips there).
            if Crystallizer._initialized:
                record_crystallizer = Crystallizer()
                if (
                        not record_crystallizer.cleaned
                        and record_crystallizer.activated
                ):
                    record_crystallizer.emit_cluster_removed(self._id)
                del record_crystallizer
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
            del self.master_conduit_id
            del self.auto_link_dependencies
            del self._devops_information_registry
            del self._devops_identity
            del self._registry
            del self._aetheric_frame_name
            del self._name
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

    def _emit_cluster_record(self) -> None:
        """
        Internal

        Emit this cluster's membership/leadership snapshot into the record.

        Purpose:
            Clusters have no crystallizer-bearing parent object, so this
            follows the configuration precedent: pull the singleton
            (guarded for the pre-boot case), emit when recording, drop the
            handle. Replace-on-emit keeps exactly one snapshot per cluster.

        Contract:
            - NO-OP before the Aether boots or while the crystallizer is
              not activated.
            - Callers hold `self._lock` (the snapshot reads members/shares/
              leader consistently).

        Returns:
            None.
        """
        if not Crystallizer._initialized:
            return
        crystallizer = Crystallizer()
        if crystallizer.activated:
            crystallizer.emit(
                ClusterCrystal(
                    cluster_id=self._id,
                    cluster_name=self._name,
                    frame_name=self._aetheric_frame_name,
                    member_conduit_ids=sorted(self.members),
                    leader_conduit_id=self.master_conduit_id,
                    shared_spells=[
                        {
                            "owner_conduit_id": owner_id,
                            "index_id": shared_index.id,
                        }
                        for owner_id, shared_indexes in (
                            self.shared_spells.items()
                        )
                        for shared_index in shared_indexes
                    ],
                )
            )
        del crystallizer

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

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self.members.add(conduit_id)
            self._devops_identity.register_cluster_member(conduit_id)
            self._emit_cluster_record()

    def remove_member(self, conduit_id: str) -> None:
        """
        Remove a conduit id and its shared roots.

        Args:
            conduit_id: Conduit identifier.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self.members.discard(conduit_id)
            self.shared_spells.pop(conduit_id, None)
            self._devops_identity.unregister_cluster_member(conduit_id)
            self._emit_cluster_record()

    def add_shared_spell(self, owner_id: str, spell_index: SpellIndex) -> None:
        """
        Record a shareable root SpellIndex for an owner.

        Args:
            owner_id: Conduit id that owns the spell.
            spell_index: Root SpellIndex to share.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            bucket = self.shared_spells.setdefault(owner_id, set())
            bucket.add(spell_index)
            self._emit_cluster_record()

    def remove_shared_spell(self, owner_id: str, spell_index: SpellIndex) -> None:
        """
        Remove a recorded shareable root for an owner.

        Args:
            owner_id: Conduit id that owns the spell.
            spell_index: Root SpellIndex to remove.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            bucket = self.shared_spells.get(owner_id)
            if bucket is None:
                return
            bucket.discard(spell_index)
            if not bucket:
                self.shared_spells.pop(owner_id, None)
            self._emit_cluster_record()

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
            involved_conduit_ids = set(self.members)
        involved_conduit_ids.add(conduit._id)

        mediator = conduit._get_required_transaction_mediator()
        mediator.start_transaction(
            identity=self._devops_identity,
            transaction_type=ChangeTransactionType.CLUSTER_JOIN,
            metadata={
                "origin_surface": "conduit_cluster.handle_join",
                "cluster_id": self._id,
                "conduit_ids": tuple(sorted(involved_conduit_ids)),
            },
        )
        succeeded = False
        try:
            with self._lock:
                self.members.add(conduit._id)
                member_ids = set(self.members)

            # Refresh registry for all members (including the new one).
            for member_id in member_ids:
                member = self._resolve_conduit_by_id(member_id)
                if member is None:
                    continue
                self.refresh_shareable_roots(member)

            # Share both directions between the joiner and existing members. The
            # shares run WITHOUT their own cluster_link transactions: the
            # CLUSTER_JOIN seal already holds every involved conduit, so a nested
            # cluster_link (a different owner) would self-conflict and time out.
            for peer_id in member_ids:
                if peer_id == conduit._id:
                    continue
                peer = self._resolve_conduit_by_id(peer_id)
                if peer is None:
                    continue
                self.share_to_borrower(conduit, peer, open_transaction=False)
                self.share_to_borrower(peer, conduit, open_transaction=False)

            # Activate the joiner's team-store facade if the cluster already has
            # an elected leader (join INTO a live cluster). No-op while inert.
            self.bind_member(conduit)
            succeeded = True
        finally:
            mediator.end_transaction(
                expected_type=ChangeTransactionType.CLUSTER_JOIN,
                success=succeeded,
            )

    def handle_leave(self, conduit: Conduit) -> None:
        """
        Remove a member and tear down shared roots between it and remaining peers.

        Contract:
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

        Args:
            conduit: The conduit leaving the cluster.

        Returns:
            None
        """
        self.check_cleaned()
        self._assert_normal_conduit(conduit)

        # If the conduit leaving IS the elected leader, unelect first through the
        # drained UNELECT transaction: the cluster becomes inert until the next
        # election, and its instances stay in the team store, which the cluster
        # owns (0.2.8237), so the next leader serves them. This runs BEFORE the
        # membership transaction so the leader is still a member for the unbind
        # walk and every member lineage is drained before the facades are unbound.
        if (
            self.master_conduit_id is not None
            and conduit._id == self.master_conduit_id
        ):
            self.unelect_leader()

        with self._lock:
            involved_conduit_ids = set(self.members)
        involved_conduit_ids.add(conduit._id)

        mediator = conduit._get_required_transaction_mediator()
        mediator.start_transaction(
            identity=self._devops_identity,
            transaction_type=ChangeTransactionType.CLUSTER_LEAVE,
            metadata={
                "origin_surface": "conduit_cluster.handle_leave",
                "cluster_id": self._id,
                "conduit_ids": tuple(sorted(involved_conduit_ids)),
            },
        )
        succeeded = False
        try:
            with self._lock:
                self.members.discard(conduit._id)
                member_ids = set(self.members)
                leaver_id = conduit._id

            peers: List[Conduit] = []
            for conduit_id in member_ids:
                peer = self._resolve_conduit_by_id(conduit_id)
                if peer is not None:
                    peers.append(peer)

            # Tear down shared roots in both directions. The unshares run WITHOUT
            # their own cluster_link transactions: the CLUSTER_LEAVE seal already
            # holds every involved conduit, so a nested cluster_link (a different
            # owner) would self-conflict and time out.
            for peer in peers:
                self.remove_shared_from_borrower(
                    conduit,
                    peer,
                    self._aetheric_frame_name,
                    open_transaction=False,
                )
            for peer in peers:
                self.remove_shared_from_borrower(
                    peer,
                    conduit,
                    self._aetheric_frame_name,
                    open_transaction=False,
                )

            with self._lock:
                self.shared_spells.pop(leaver_id, None)

            # Drop the leaver's own team-store facade (idempotent). For a
            # non-leader leave this releases its handle to the team store; for a
            # leader-leave the cluster was already unelected above and its walk
            # unbound this facade too. No-op while inert.
            self.unbind_member(conduit)
            succeeded = True
        finally:
            mediator.end_transaction(
                expected_type=ChangeTransactionType.CLUSTER_LEAVE,
                success=succeeded,
            )

    def release_member(self, conduit: Conduit) -> None:
        """
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
        """
        self.handle_leave(conduit)
        self.remove_member(conduit._id)

    def drop_member(self, conduit: Conduit) -> None:
        """
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
        """
        self.check_cleaned()
        if (
            self.master_conduit_id is not None
            and conduit._id == self.master_conduit_id
        ):
            self.unbind_elected_leader()
        self.remove_member(conduit._id)
        conduit._cluster_creations.unbind()

    # ------------------------------------------------------------------
    # Cluster leader election (bind / unbind the shared team store)
    # ------------------------------------------------------------------
    def bind_elected_leader(self, leader_conduit_id: str) -> None:
        """
        Bind the cluster's team store into every member root's facade under the elected leader.

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
            - Records the elected leader id in `master_conduit_id`.
            - Binds only: it does not begin, commit, or abort the election
              transaction. The caller runs it as the in-window effect.

        Args:
            leader_conduit_id (str):
                Conduit id of the elected leader. Must resolve to a live, normal
                cluster member root; it holds purge authority over the team
                store while elected.

        Threading:
            Runs inside the election transaction's held window, after the member
            conduits are sealed, so membership is stable for the walk and no meld
            is mid-create against an inert facade (election is inert -> active).
            Members are live root conduits and the member set is a thread-safe
            collection, so the walk needs no snapshot and no extra lock.

        Returns:
            None.

        Raises:
            RuntimeError: If the cluster has been cleaned, a leader is already
                elected (re-election without an intervening unelect), or the
                leader conduit cannot be resolved.
        """
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
        with self._lock:
            self._emit_cluster_record()

    def unbind_elected_leader(self) -> None:
        """
        Unbind the team store from every member root's facade (the cluster turns inert).

        Purpose:
            Deactivate the cluster team store and return the cluster to inert, so a
            `unique_per_conduit_cluster` meld hard-errors again until a new leader
            is elected.

        Contract:
            - Walks the current member set and unbinds each member root's
              `_cluster_creations` facade, dropping its reference to the team
              store and the leader's id. The cluster still owns the store and its
              instances (0.2.8237): nothing is disposed here, and the next
              election serves them again.
            - Idempotent per facade: unbinding an inert facade is a no-op.
            - Clears `master_conduit_id`.
            - Unbinds only: it does not begin, commit, or abort the unelection
              transaction. The caller runs it as the in-window effect.

        Threading:
            Runs inside the unelection transaction's held window, after every
            member root lineage has been drained to zero, so no meld is mid-create
            against the team store when the facades release it. Members are live root
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
        with self._lock:
            self._emit_cluster_record()

    def bind_member(self, conduit: "Conduit") -> None:
        """
        Bind one joining member's facade to the team store under the current leader.

        Purpose:
            Activate the team store for a single conduit that joins a cluster
            which ALREADY has an elected leader. `bind_elected_leader` covers the
            members present at election; this covers a join INTO a live cluster
            without re-walking the membership or re-electing.

        Contract:
            - No-op when the cluster is inert (`master_conduit_id is None`): the
              joiner's facade stays disabled until a leader is elected, which
              picks it up via `bind_elected_leader`.
            - When a leader is elected, binds the joining conduit's
              `_cluster_creations` to the team store with the current leader's
              id. Does NOT change `master_conduit_id` (the leader is unchanged).

        Args:
            conduit:
                The joining member root conduit whose facade is activated.

        Threading:
            Runs inside the `CLUSTER_JOIN` transaction's held window, whose seal
            holds the joiner and the leader, so the bind never races a meld.

        Returns:
            None.

        Raises:
            RuntimeError: If the cluster has been cleaned.
        """
        self.check_cleaned()
        if self.master_conduit_id is None:
            return
        conduit._cluster_creations.bind(self._team_store, self.master_conduit_id)

    def unbind_member(self, conduit: "Conduit") -> None:
        """
        Unbind one leaving member's facade from the team store.

        Purpose:
            Deactivate the team store for one conduit leaving the cluster, by
            dropping its own facade pointer, without disturbing the leader or the
            other members.

        Contract:
            - Always drops the leaving conduit's `_cluster_creations` reference
              (idempotent: a no-op when its facade is already inert). Never cleans
              the team store. Does NOT change `master_conduit_id`.
            - Drops the leaver's OWN facade only. When the leaving conduit is the
              elected leader, `handle_leave` first dissolves the cluster through
              `unelect_leader` (drained: clears `master_conduit_id` and unbinds
              every member, the leader included, which is still a member then);
              this call is unconditional so a non-leader's facade is dropped too
              and a repeated exit stays a no-op.

        Args:
            conduit:
                The leaving member root conduit whose facade is disabled.

        Threading:
            Runs inside the `CLUSTER_LEAVE` transaction's held window, whose seal
            holds the leaver. No lineage drain is required: `unbind` only drops
            the facade pointer, the team store stays alive (owned by the
            cluster), and any in-flight meld holds its own store reference.

        Returns:
            None.

        Raises:
            RuntimeError: If the cluster has been cleaned.
        """
        self.check_cleaned()
        conduit._cluster_creations.unbind()

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
                cluster member root; it holds purge authority over the team
                store while elected.

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
              against the team store. Its `on_end` reopens every member root
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
            unbind, so no meld is mid-create against the team store when the
            facades release it.
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

        Returns:
            None.
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
                        ChangeTransactionType.CLUSTER_LINK,
                        conduits=[peer, owner],
                    ):
                        peer.add_spell_to_contract(
                            spell=spell,
                            conduit=owner,
                            permissions=spell.permissions,
                            aetheric_frame=self._aetheric_frame_name,
                            reason=DetailReason.root,
                            root_spell_id=cluster_root_id,
                            link_dependencies=True,
                        )
                except Exception:
                    continue

    def remove_and_strip_spell(self, owner: "Conduit", spell: "Spell") -> None:
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

        Returns:
            None.
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
                    ChangeTransactionType.CLUSTER_LINK,
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
                        ChangeTransactionType.CLUSTER_LINK,
                        conduits=[peer, owner],
                    ):
                        peer.add_spell_to_contract(
                            spell=spell,
                            conduit=owner,
                            permissions=spell.permissions,
                            aetheric_frame=self._aetheric_frame_name,
                            reason=DetailReason.manual,
                            root_spell_id=spell.spell_id,
                            link_dependencies=False,
                        )
                except Exception:
                    continue

    def share_to_borrower(
            self,
            owner: Conduit,
            borrower: Conduit,
            *,
            open_transaction: bool = True,
    ) -> None:
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
            open_transaction:
                When True (default) each per-pair share runs inside its own
                `cluster_link` change-control transaction. When False the caller
                already holds the change-control window -- a `CLUSTER_JOIN`
                transaction sealing every involved conduit -- so each share runs
                directly under the held locks instead of opening a nested
                transaction that would self-conflict on those scopes.

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
                share_window = (
                    borrower.transaction(
                        ChangeTransactionType.CLUSTER_LINK,
                        conduits=[borrower, owner],
                    )
                    if open_transaction
                    else nullcontext()
                )
                with share_window:
                    borrower.add_spell_to_contract(
                        spell=spell,
                        conduit=owner,
                        permissions=spell.permissions,
                        aetheric_frame=self._aetheric_frame_name,
                        reason=DetailReason.root,
                        root_spell_id=cluster_root_id,
                        link_dependencies=link_deps,
                    )
            except Exception:
                continue

    def remove_shared_from_borrower(
            self,
            owner: Conduit,
            borrower: Conduit,
            aetheric_frame: str = "default",
            *,
            open_transaction: bool = True,
    ) -> None:
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
            open_transaction:
                When True (default) each per-pair unshare runs inside its own
                `cluster_link` change-control transaction. When False the caller
                already holds the change-control window -- a `CLUSTER_LEAVE`
                transaction sealing every involved conduit -- so each unshare runs
                directly under the held locks instead of opening a nested
                transaction that would self-conflict on those scopes.

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
                unshare_window = (
                    borrower.transaction(
                        ChangeTransactionType.CLUSTER_LINK,
                        conduits=[borrower, owner],
                    )
                    if open_transaction
                    else nullcontext()
                )
                with unshare_window:
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
                if spell.existence == Existence.unique_per_conduit_cluster
            ]

    def _resolve_spell_from_index(self, conduit: "Conduit", spell_index: "SpellIndex") -> Optional[Spell]:
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

        Returns:
            None.
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
            spell_id: The shared root's spell_id.

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
                member ids, and shared root SpellIndex ids grouped by owner.
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

