import threading
from typing import TYPE_CHECKING, Dict, Set, Optional, List, ClassVar
from mypy_extensions import mypyc_attr
from melder.aether.spellbook.existence.existence import Existence
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
@mypyc_attr(native_class=True)
class ConduitCluster(Cleanable):
    """
    Cluster-local registry for conduit membership and shared-root policy.

    Contract:
        - Tracks cluster membership by conduit id.
        - Tracks which root `SpellIndex` lineages each owner contributes to the
          cluster for automatic sharing.
        - Orchestrates automatic contracting and removal of shared roots between
          owners and borrowers during join, leave, and refresh flows.
        - Uses one internal lock to protect membership and shared-root state.
        - Becomes unusable after `cleanup()` completes.

    Attributes:
        members:
            Set of conduit ids currently in the cluster.
        shared_spells:
            Mapping from owner conduit id to the shareable root `SpellIndex`
            values contributed by that owner.
        auto_link_dependencies:
            When True, a dependency closure is auto-contracted with each shared
            root. When False, only the root spell is linked.
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
    ]

    def __init__(
            self,
            name: str,
            registry: Dict[str, Conduit],
            aetheric_frame_name: str,
            auto_link_dependencies: bool = True,
    ):
        """
        Initialize a cluster container.

        Args:
            name: Cluster name.
            registry: Borrowed frame-local conduit registry keyed by conduit id.
            aetheric_frame_name: Owning frame name for contract operations.
            auto_link_dependencies: If True, sharing pulls dependency closure.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()
        self._id: str = IDBuilder.create_id()
        self._name: str = name
        self._registry: Dict[str, Conduit] = registry
        self._aetheric_frame_name: str = aetheric_frame_name
        self.members: Set[str] = set()
        self.shared_spells: Dict[str, Set[SpellIndex]] = {}
        self.auto_link_dependencies: bool = auto_link_dependencies

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
            if self.members is not None:
                self.members.clear()
            if self.shared_spells is not None:
                for v in self.shared_spells.values():
                    try:
                        v.clear()
                    except Exception:
                        pass
                self.shared_spells.clear()
            del self.auto_link_dependencies
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

    def refresh_shareable_roots(self, owner: Conduit) -> None:
        """
        Ensure shared_spells has all shareable SpellIndexes for the owner.

        Args:
            owner: Conduit whose shareable roots should be recorded.

        Returns:
            None
        """
        self.check_cleaned()
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
                        ChangeTransactionType.LINK,
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
                    ChangeTransactionType.LINK,
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
                        ChangeTransactionType.LINK,
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
                    ChangeTransactionType.LINK,
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
                    ChangeTransactionType.LINK,
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

