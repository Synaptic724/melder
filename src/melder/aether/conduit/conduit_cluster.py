import threading
from typing import Dict, Set
from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.existence.existence import Existence
from melder.utilities.general_base.cleanable import Cleanable
from melder.aether.conduit.conduit_ward.contract.detail_reason import DetailReason


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
            aetheric_frame_name: Frame name (for teardown calls).

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
            self.shared_spells.pop(conduit._id, None)

        peers = [frame._conduits.get(cid) for cid in member_ids if frame._conduits.get(cid) is not None]

        # Remove spells this conduit owned from peers
        for peer in peers:
            self.remove_shared_from_borrower(conduit, peer, aetheric_frame_name)

        # Remove spells peers owned from this conduit
        for peer in peers:
            self.remove_shared_from_borrower(peer, conduit, aetheric_frame_name)

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
                if link_deps:
                    borrower.add_spell_to_contract_with_dependencies(
                        spell=spell,
                        conduit=owner,
                        permissions=getattr(spell, "permissions", "create"),
                        aetheric_frame=getattr(owner, "_aetheric_frame", "default"),
                    )
                else:
                    borrower.add_spell_to_contract(
                        spell=spell,
                        conduit=owner,
                        permissions=getattr(spell, "permissions", "create"),
                        aetheric_frame=getattr(owner, "_aetheric_frame", "default"),
                        reason=DetailReason.root,
                        root_spell_id=spell.spell_id,
                        link_dependencies=False,
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
                borrower.remove_root_from_contracts(
                    root_spell_id=spell.spell_id,
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
        Return shareable spells from a conduit (existence == unique_per_conduit_cluster or unique).

        Args:
            conduit: Conduit whose spellbook to inspect.

        Returns:
            list: Shareable spell objects.
        """
        book = conduit._spellbook if hasattr(conduit, "_spellbook") else None
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
        book = conduit._spellbook if hasattr(conduit, "_spellbook") else None
        if book is None or book._spells is None:
            return None
        with book._lock:
            return book._spells.get(spell_index)
