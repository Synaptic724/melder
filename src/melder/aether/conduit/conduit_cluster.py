import threading
from typing import Dict, Set
from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.existence.existence import Existence
from melder.utilities.general_base.cleanable import Cleanable
from melder.aether.conduit.conduit_ward.contract.detail_reason import DetailReason
from melder.aether.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeTransactionType,
)
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class ConduitCluster(Cleanable):
    """
    Cluster-local registry for membership and spell sharing semantics.

    Responsibilities:
        - Track membership (conduit ids) for the cluster.
        - Track which root SpellIndex lineages each owner contributes to the cluster.
        - Orchestrate automatic contracting of shared roots (and optionally their
          dependencies) between owners and borrowers on join/leave events.

    Attributes:
        members: Set of conduit_ids currently in the cluster.
        shared_spells: Dict mapping owner_conduit_id -> set[SpellIndex] roots to auto-share.
        auto_link_dependencies: When True, dependency closure is auto-contracted along
            with each root; when False, only roots are linked (advanced/debug use).
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = (
        "_lock",
        "_name",
        "members",
        "shared_spells",
        "auto_link_dependencies",
        "_cleaned",
    )

    def __init__(self, name: str, auto_link_dependencies: bool = True):
        """
        Initialize a cluster container.

        Args:
            name: Cluster name.
            auto_link_dependencies: If True, sharing pulls dependency closure.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()
        self._name: str = name
        self.members: Set[str] = set()
        self.shared_spells: Dict[str, Set[SpellIndex]] = {}
        self.auto_link_dependencies: bool = auto_link_dependencies

    def cleanup(self):
        """
        Idempotently clear registry state and release references.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            if self.members is not None:
                self.members.clear()
            if self.shared_spells is not None:
                for v in self.shared_spells.values():
                    try:
                        v.clear()
                    except Exception:
                        pass
                self.shared_spells.clear()
            self.auto_link_dependencies = None
            self._name = None
            self._cleaned = True
        self._lock = None

    def add_member(self, conduit_id: str) -> None:
        """
        Add a conduit id to the cluster membership.

        Args:
            conduit_id: Conduit identifier.
        """
        with self._lock:
            self.members.add(conduit_id)

    def remove_member(self, conduit_id: str) -> None:
        """
        Remove a conduit id and its shared roots.

        Args:
            conduit_id: Conduit identifier.
        """
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
        with self._lock:
            return {k: set(v) for k, v in self.shared_spells.items()}

    def get_members(self) -> Set[str]:
        """
        Snapshot of cluster members.

        Returns:
            Set of conduit ids.
        """
        with self._lock:
            return set(self.members)

    # ------------------------------------------------------------------
    # Share helpers (operate on live conduit objects)
    # ------------------------------------------------------------------
    def handle_join(self, conduit, frame, aetheric_frame_name: str = "default") -> None:
        """
        Add a member and auto-share all roots between the new member and existing peers.

        Args:
            conduit: The conduit joining the cluster.
            frame: The owning AethericFrame (provides conduit lookup).
            aetheric_frame_name: Frame name for compatibility with Aether hooks.

        Returns:
            None
        """
        with self._lock:
            self.members.add(conduit._id)
            member_ids = set(self.members)

        # Refresh registry for all members (including new)
        for member_id in member_ids:
            member = frame._conduits.get(member_id)
            if member is None:
                continue
            self.refresh_shareable_roots(member)

        # Share both directions between joiner and existing members
        for peer_id in member_ids:
            if peer_id == conduit._id:
                continue
            peer = frame._conduits.get(peer_id)
            if peer is None:
                continue
            self.share_to_borrower(conduit, peer)
            self.share_to_borrower(peer, conduit)

    def handle_leave(self, conduit, frame, aetheric_frame_name: str = "default") -> None:
        """
        Remove a member and tear down shared roots between it and remaining peers.

        Args:
            conduit: The conduit leaving the cluster.
            frame: The owning AethericFrame (provides conduit lookup).
            aetheric_frame_name: Frame name (for teardown calls).

        Returns:
            None
        """
        with self._lock:
            self.members.discard(conduit._id)
            member_ids = set(self.members)
            leaver_id = conduit._id

        peers = [frame._conduits.get(cid) for cid in member_ids if frame._conduits.get(cid) is not None]

        # Remove spells this conduit owned from peers
        for peer in peers:
            self.remove_shared_from_borrower(conduit, peer, aetheric_frame_name)

        # Remove spells peers owned from this conduit
        for peer in peers:
            self.remove_shared_from_borrower(peer, conduit, aetheric_frame_name)

        with self._lock:
            self.shared_spells.pop(leaver_id, None)

    def refresh_shareable_roots(self, owner) -> None:
        """
        Ensure shared_spells has all shareable SpellIndexes for the owner.

        Args:
            owner: Conduit whose shareable roots should be recorded.

        Returns:
            None
        """
        shareables = self._get_shareable_spells(owner)
        owner_id = owner._id
        for spell in shareables:
            self.add_shared_spell(owner_id, spell.spell_index)

    def refresh_member_shares(self, conduit, frame, aetheric_frame_name: str = "default") -> None:
        """
        Refresh and (re)share this member's shareable roots with all peers in the cluster.

        Args:
            conduit: Member conduit whose roots should be refreshed.
            frame: Owning AethericFrame for conduit lookup.
            aetheric_frame_name: Frame name for compatibility with Aether hooks.

        Returns:
            None
        """
        with self._lock:
            member_ids = set(self.members)
        self.refresh_shareable_roots(conduit)
        for peer_id in member_ids:
            if peer_id == conduit._id:
                continue
            peer = frame._conduits.get(peer_id)
            if peer is None:
                continue
            self.share_to_borrower(conduit, peer)
            self.share_to_borrower(peer, conduit)

    def add_and_share_spell(self, owner, borrower_frame, spell, aetheric_frame_name: str = "default",
                            link_dependencies: bool | None = None) -> None:
        """
        Explicitly add a spell to the shared set and propagate it to peers.

        Args:
            owner: Conduit that owns the spell.
            borrower_frame: AethericFrame for conduit lookup.
            spell: Spell object to share.
            aetheric_frame_name: Frame name for removal calls.
            link_dependencies: Override auto_link_dependencies if provided.
        """
        owner_id = owner._id
        self.add_shared_spell(owner_id, spell.spell_index)
        # Decide dependency behavior (explicit override beats cluster default)
        link_deps = self.auto_link_dependencies if link_dependencies is None else bool(link_dependencies)

        with self._lock:
            member_ids = set(self.members)
        for peer_id in member_ids:
            if peer_id == owner_id:
                continue
            peer = borrower_frame._conduits.get(peer_id)
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
                            aetheric_frame=aetheric_frame_name,
                            reason=DetailReason.root,
                            root_spell_id=cluster_root_id,
                            link_dependencies=True,
                        )
                except Exception:
                    continue

    def remove_and_strip_spell(self, owner, borrower_frame, spell, aetheric_frame_name: str = "default") -> None:
        """
        Explicitly remove a shared spell from the cluster and strip it from peers.

        Args:
            owner: Conduit that owns the spell.
            borrower_frame: AethericFrame for conduit lookup.
            spell: Spell object to remove.
            aetheric_frame_name: Frame name for removal calls.
        """
        owner_id = owner._id
        self.remove_shared_spell(owner_id, spell.spell_index)

        with self._lock:
            member_ids = set(self.members)
        for peer_id in member_ids:
            if peer_id == owner_id:
                continue
            peer = borrower_frame._conduits.get(peer_id)
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
                        aetheric_frame=aetheric_frame_name,
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
                            aetheric_frame=aetheric_frame_name,
                            reason=DetailReason.manual,
                            root_spell_id=spell.spell_id,
                            link_dependencies=False,
                        )
                except Exception:
                    continue

    def share_to_borrower(self, owner, borrower) -> None:
        """
        Contract all shared roots from owner into borrower (with deps if enabled).

        Args:
            owner: Conduit that owns the roots.
            borrower: Conduit that should receive the contracts.

        Returns:
            None
        """
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
                        aetheric_frame=getattr(owner, "_aetheric_frame", "default"),
                        reason=DetailReason.root,
                        root_spell_id=cluster_root_id,
                        link_dependencies=link_deps,
                    )
            except Exception:
                continue

    def remove_shared_from_borrower(self, owner, borrower, aetheric_frame: str = "default") -> None:
        """
        Remove all shared roots from owner on the borrower side.

        Args:
            owner: Conduit that owns the roots.
            borrower: Conduit to remove the contracted roots from.
            aetheric_frame: Frame name for removal calls.

        Returns:
            None
        """
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
    def _get_shareable_spells(self, conduit):
        """
        Return shareable spells from a conduit (existence == unique_per_conduit_cluster).

        Args:
            conduit: Conduit whose spellbook to inspect.

        Returns:
            list: Shareable spell objects.
        """
        book = conduit._spellbook
        if book is None or book._spells is None:
            return []
        with book._lock:
            return [
                spell for spell in book._spells.values()
                if hasattr(spell, "existence") and spell.existence == Existence.unique_per_conduit_cluster
            ]

    def _resolve_spell_from_index(self, conduit, spell_index: SpellIndex):
        """
        Resolve a Spell object from a conduit given its SpellIndex.

        Args:
            conduit: Conduit that owns the SpellIndex.
            spell_index: SpellIndex to resolve.

        Returns:
            Spell | None: The spell if found.
        """
        book = conduit._spellbook
        if book is None or book._spells is None:
            return None
        with book._lock:
            return book._spells.get(spell_index)

    # ------------------------------------------------------------------
    # Configuration / diagnostics
    # ------------------------------------------------------------------
    def set_auto_link_dependencies(self, enabled: bool) -> None:
        """
        Configure whether dependency closure is auto-contracted when sharing roots.

        Args:
            enabled: True to include deps, False for roots only.
        """
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
        return f"cluster:{self._name}:{owner_id}:{spell_id}"

    def describe(self) -> dict:
        """
        Return a diagnostic snapshot of the cluster.

        Returns:
            dict: containing name, auto_link_dependencies, members, shared roots summary.
        """
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
