from typing import Optional, Any, Dict, ClassVar
from threading import RLock
from types import TracebackType



# Melder imports
from melder.aether.conduit.conduit_ward.contract.details import Detail, IndexDetail
from melder.aether.conduit.conduit_ward.contract.detail_reason import DetailReason
from melder.aether.conduit.conduit_ward.contract.contract_types.contract_types import ContractTypes
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.utilities.helpers.id_builder import IDBuilder
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from melder.aether.conduit.conduit import Conduit
    from melder.aether.conduit.conduit_ward.conduit_ward import ConduitWard
from melder.utilities.general_base.cleanable import Cleanable

class Contract(Cleanable):
    """
    Bidirectional contract between two conduit wards.

    A Contract is symmetric: both wards keep their own Detail maps describing
    which lineages are shared and with what permissions. Each side can grant
    or revoke independently; the contract object simply tracks both views.

    In practice this object is the shared storage for:
        - per-ward spell/detail maps
        - the relationship between the two participating wards
        - lineage-aware source tagging used by dependency-linked rollback

    Attributes:
        _ward_a / _ward_b: The two participating wards.
        _details_a / _details_b: Per-ward maps of spell_id -> Detail.
        _id: Unique identifier for this contract instance.

    Owned State:
        One `RLock`, a stable `IDBuilder` id, the two ward references, and FOUR
        maps - not two. Each side owns both a `Detail` map keyed by spell_id
        and an `IndexDetail` map keyed by index_id.

    Contract:
        - Symmetric at the pair level, but never a shared table: each ward's
          view is stored separately and either side may grant or revoke
          independently.
        - The `_details_a` / `_details_b` naming is BORROW-DIRECTIONAL and
          reads backwards at first glance: `_details_a` holds what ward A
          borrowed FROM ward B.
        - Cleanup is idempotent; it clears both detail maps, nulls the ward
          references, and marks the contract unusable.

    Threading:
        One instance `RLock` guards mutation of the four maps. Lock order runs
        ward -> contract; a contract never reaches back up to lock a ward.

    Registration:
        MELDER KERNEL - guarded. Contracts are created by `ConduitWard` during
        `Conduit.link(...)`; a user never constructs one directly.

    Subsystem Context:
        The storage object beneath the four ward vocabularies: `Policies`
        decides whether a contract may form, `Permissions` bounds what each
        entry grants, and `ContractTypes` / `DetailReason` annotate each stored
        `Detail`. This class holds those entries; `ConduitWard` owns the verbs
        that write them.

    System Context:
        The two detail families exist because a contract must survive VERSION
        MOVEMENT. A `Detail` captures the spell_id visible at contract time,
        which is a point-in-time answer; an `IndexDetail` instead subscribes to
        a `SpellIndex`, so the borrower follows the lineage HEAD rather than a
        frozen version. That is what lets a notch repoint the active member of
        an index without silently stranding every peer that borrowed it.
        Keeping both is deliberate: the captured id preserves what was actually
        agreed, while the subscription tracks what is currently live.
        This split is durable, not just runtime - `ContractCrystal` records both
        endpoints with per-side `Detail` / `IndexDetail` projections, which is
        why a formation captured around only one conduit raises the
        crystallizer's `contract_peer` warning rather than restoring a
        half-contract silently.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Bidirectional contract between two conduit wards. Melder kernel
        machinery: read it to understand the runtime, do not drive it directly.
    """
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_id",
        "_ward_a",
        "_ward_b",
        "_details_a",
        "_details_b",
        "_index_details_a",
        "_index_details_b",
    ]

    def __init__(self, ward_a: ConduitWard, ward_b: ConduitWard):
        """
        Create a new symmetric contract between two wards.

        Args:
            ward_a: First participating ward.
            ward_b: Second participating ward.

        Returns:
            None.
        """
        super().__init__()
        self._lock = RLock()
        self._id: str = IDBuilder.create_id()

        self._ward_a: ConduitWard = ward_a
        self._ward_b: ConduitWard = ward_b

        # Each side stores its own view of spell permissions.
        self._details_a: Dict[str, Detail] = {} # Borrowed from conduit b
        self._details_b: Dict[str, Detail] = {} # Borrowed from conduit a

        # Index-link details: per-ward maps of index_id -> IndexDetail (lineage
        # subscriptions; the borrower follows the index, not a captured version).
        self._index_details_a: Dict[str, IndexDetail] = {} # Borrowed from conduit b
        self._index_details_b: Dict[str, IndexDetail] = {} # Borrowed from conduit a

    #region Cleanup
    def cleanup(self) -> None:
        """
        Idempotently tear down this contract and all contained Details.

        Clears both wards’ detail maps, nulls ward references, and marks the
        contract cleaned so it can no longer be used.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._clean_up()
            self._cleaned = True
            del self._ward_a
            del self._ward_b
            del self._details_a
            del self._details_b
            del self._index_details_a
            del self._index_details_b

    def _clean_up(self) -> None:
        """
        Internal helper to cleanup all Detail entries for both wards.
        """
        for detail in self._details_a.values():
            detail.cleanup()
        self._details_a.clear()

        for detail in self._details_b.values():
            detail.cleanup()
        self._details_b.clear()

        for index_detail in self._index_details_a.values():
            index_detail.cleanup()
        self._index_details_a.clear()

        for index_detail in self._index_details_b.values():
            index_detail.cleanup()
        self._index_details_b.clear()
    #endregion Cleanup


    #region Context Manager
    def __enter__(self) -> "Contract":
        """
        Acquire the contract lock and return this contract.

        Contract:
            This is a simple lock guard only; it does not open any higher-level
            transaction scope.
        """
        self._lock.acquire()
        return self

    def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc_value: BaseException | None,
            traceback: TracebackType | None,
    ) -> None:
        """
        Release the contract lock acquired by `__enter__`.
        """
        self._lock.release()

    #endregion Context Manager

    def _get_peer(self, ward: ConduitWard) -> ConduitWard:
        """
        Internal

        Return the opposite ward participant in this contract.

        Args:
            ward: The ward requesting its peer.

        Returns:
            ConduitWard: The other ward in the contract.

        Raises:
            ValueError: If the ward is not part of this contract.
        """
        if ward is self._ward_a:
            return self._ward_b
        if ward is self._ward_b:
            return self._ward_a
        raise ValueError("Ward is not a member of this contract.")

    def _get_opposite_conduit(self, contract: Contract, known_id: str) -> Optional[Conduit]:
        """
        Internal

        Helper to find the opposite conduit in a contract based on a known conduit ID.

        Args:
            contract: The contract to search within.
            known_id: Conduit ID you already know.
        Returns:
            Optional[Conduit]: The peer conduit if found, else None.
        """
        if contract._ward_a._conduit._id == known_id:
            return contract._ward_b._conduit
        elif contract._ward_b._conduit._id == known_id:
            return contract._ward_a._conduit
        return None

    def _get_detail_map(self, ward: ConduitWard) -> Dict[str, Detail]:
        """
        Internal

        Helper to return the permission map associated with a given ward.

        Args:
            ward: Ward whose detail map should be returned.

        Returns:
            Dict[str, Detail]: Map of spell_id -> Detail for the ward.

        Raises:
            ValueError: If the ward is not part of this contract.
        """
        if ward is self._ward_a:
            return self._details_a
        if ward is self._ward_b:
            return self._details_b
        raise ValueError("Invalid ward for contract access.")

    def _add(self, ward: ConduitWard, contract_detail: Detail) -> bool:
        """
        Internal

        Add a spell-level permission detail to the contract on behalf of the given ward.

        Args:
            ward: Ward that owns the detail map being updated.
            contract_detail: Detail entry to insert.

        Returns:
            bool: True if a new Detail was inserted, False if merged into an existing one.
        """
        detail_map = self._get_detail_map(ward)
        existing = detail_map.get(contract_detail.spell_id)
        if existing is not None:
            # Merge sources if this lineage already exists with the same permissions.
            if existing.permissions != contract_detail.permissions:
                raise RuntimeError(
                    f"Detail already exists for spell_id {contract_detail.spell_id} with different permissions "
                    f"({existing.permissions.name} != {contract_detail.permissions.name})."
                )
            if contract_detail.sources:
                for root_id in contract_detail.sources:
                    existing.add_source(root_id)
            return False
        detail_map[contract_detail.spell_id] = contract_detail
        return True

    def _remove(self, ward: ConduitWard, spell_id: str) -> None:
        """
        Internal

        Remove a spell-level permission detail from the given ward's view.

        Args:
            ward: Ward whose map should be updated.
            spell_id: Version ID key to remove.
        """
        detail_map = self._get_detail_map(ward)
        if spell_id in detail_map:
            del detail_map[spell_id]

    def _get_index_detail_map(self, ward: ConduitWard) -> Dict[str, IndexDetail]:
        """
        Internal

        Return the index-link detail map (index_id -> IndexDetail) for a ward.

        Args:
            ward: Ward whose index-detail map should be returned.

        Returns:
            Dict[str, IndexDetail]: Map of index_id -> IndexDetail for the ward.

        Raises:
            ValueError: If the ward is not part of this contract.
        """
        if ward is self._ward_a:
            return self._index_details_a
        if ward is self._ward_b:
            return self._index_details_b
        raise ValueError("Invalid ward for contract access.")

    def _add_index(self, ward: ConduitWard, index_detail: IndexDetail) -> bool:
        """
        Internal

        Add an index-link detail to the contract on behalf of the given ward,
        keyed by the index id. Merges sources when the same index is already
        linked with the same permissions.

        Args:
            ward: Ward that owns the index-detail map being updated.
            index_detail: IndexDetail entry to insert.

        Returns:
            bool: True if a new IndexDetail was inserted, False if merged.

        Raises:
            RuntimeError: If the index is already linked with different permissions.
        """
        detail_map = self._get_index_detail_map(ward)
        existing = detail_map.get(index_detail.index_id)
        if existing is not None:
            if existing.permissions != index_detail.permissions:
                raise RuntimeError(
                    f"IndexDetail already exists for index_id {index_detail.index_id} with "
                    f"different permissions ({existing.permissions.name} != "
                    f"{index_detail.permissions.name})."
                )
            if index_detail.sources:
                for root_id in index_detail.sources:
                    existing.add_source(root_id)
            return False
        detail_map[index_detail.index_id] = index_detail
        return True

    def _remove_index(self, ward: ConduitWard, index_id: str) -> None:
        """
        Internal

        Remove an index-link detail from the given ward's view.

        Args:
            ward: Ward whose index-detail map should be updated.
            index_id: Stable index id key to remove.
        """
        detail_map = self._get_index_detail_map(ward)
        if index_id in detail_map:
            del detail_map[index_id]

    def _check_index_exists(self, ward: ConduitWard, index_id: str) -> bool:
        """
        Internal

        Return whether the given ward has an index-link detail for `index_id`.

        Args:
            ward: Ward whose index-detail map should be checked.
            index_id: Stable index id to look for.

        Returns:
            bool: True if the index is linked in the ward's map.
        """
        return index_id in self._get_index_detail_map(ward)

    def _remove_source(self, ward: ConduitWard, spell_id: str, root_spell_id: str | None) -> bool:
        """
        Internal

        Remove a specific root spell_id source from a detail. If no sources remain,
        the detail is removed. Returns True if the detail was deleted.
        """
        detail_map = self._get_detail_map(ward)
        detail = detail_map.get(spell_id)
        if detail is None:
            return False
        # If no root is provided, drop the entire detail.
        if root_spell_id is None:
            detail_map.pop(spell_id, None)
            detail.cleanup()
            return True
        # Remove only the source; delete detail if sources empty afterward.
        should_delete = detail.remove_source(root_spell_id)
        if should_delete:
            detail_map.pop(spell_id, None)
            detail.cleanup()
            return True
        return False

    def _clear_contract(self) -> None:
        """
        Internal

        Clear all spell details from both sides of the contract.
        This is typically called when cleaning the contract.
        """
        with self._lock:
            for detail in self._details_a.values():
                detail.cleanup()
            for detail in self._details_b.values():
                detail.cleanup()
            self._details_a.clear()
            self._details_b.clear()


    def _check_if_exists_and_permissions(self, ward: ConduitWard, spell_id: str, permission: Permissions) -> bool:
        """
        Internal

        Check if the given ward has permission for the specified spell.
        """
        detail_map = self._get_detail_map(ward)
        if spell_id not in detail_map:
            return False
        return detail_map[spell_id].permissions == permission

    def _check_if_exists(self, ward: ConduitWard, spell_id: str) -> bool:
        """
        Internal

        Check if a spell exists in the given ward's permission map.
        """
        detail_map = self._get_detail_map(ward)
        return spell_id in detail_map


    def _find_spell_in_ward(self, spell_id: str) -> ConduitWard | None:
        """
        Internal

        Check if a spell exists in the given ward's permission map.
        """
        detail_map_a = self._get_detail_map(self._ward_a)
        detail_map_b = self._get_detail_map(self._ward_b)
        if spell_id in detail_map_a:
            return self._ward_a
        elif spell_id in detail_map_b:
            return self._ward_b
        else:
            return None


    def _grant(self, ward: ConduitWard, spell_ids: list[str], permission: Permissions) -> None:
        """
        Internal

        Grant a list of spells with a single permission type for the specified ward.
        Each spell_id is resolved to a local SpellIndex owned by the ward's spellbook,
        and the Detail is recorded as an initiated grant.

        Args:
            ward (ConduitWard): The ward granting access.
            spell_ids (list[str]): List of spell IDs to grant.
            permission (Permissions): The permission level to assign.

        Raises:
            ValueError: If a spell_id cannot be resolved to a local SpellIndex.
        """
        detail_map = self._get_detail_map(ward)
        spellbook = ward._conduit._spellbook
        local_spells = spellbook.spells
        for spell_id in spell_ids:
            spell_index = None
            for candidate_index in local_spells.keys():
                if candidate_index.has_spell(spell_id):
                    spell_index = candidate_index
                    break
            if spell_index is None:
                raise ValueError(
                    f"Spell id '{spell_id}' not found in spellbook."
                )
            detail_map[spell_id] = Detail(
                spell_index=spell_index,
                spell_id=spell_id,
                permissions=permission,
                contract_type=ContractTypes.initiated,
                reason=DetailReason.other,
            )

