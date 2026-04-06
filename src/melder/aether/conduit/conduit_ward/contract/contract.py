from typing import Optional, Any, Dict
from threading import RLock
# Melder imports
from melder.aether.conduit.conduit_ward.contract.details import Detail
from melder.aether.conduit.conduit_ward.contract.detail_reason import DetailReason
from melder.aether.conduit.conduit_ward.contract.contract_types.contract_types import ContractTypes
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.interfaces.interfaces import IConduitWard, IConduit, IContract
from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class Contract(Cleanable, IContract):
    """
    Bidirectional contract between two conduit wards.

    A Contract is symmetric: both wards keep their own Detail maps describing
    which lineages are shared and with what permissions. Each side can grant
    or revoke independently; the contract object simply tracks both views.

    Attributes:
        _ward_a / _ward_b: The two participating wards.
        _details_a / _details_b: Per-ward maps of spell_id -> Detail.
        _id: Unique identifier for this contract instance.
    """
    __melder_internal__ = _mrg.sentinel

    def __init__(self, ward_a: IConduitWard, ward_b: IConduitWard):
        """
        Create a new symmetric contract between two wards.

        Args:
            ward_a: First participating ward.
            ward_b: Second participating ward.
        """
        super().__init__()
        self._lock = RLock()
        self._id: str = IDBuilder.create_id()

        self._ward_a: IConduitWard = ward_a
        self._ward_b: IConduitWard = ward_b

        # Each side stores its own view of spell permissions.
        self._details_a: Dict[str, Detail] = {} # Borrowed from conduit b
        self._details_b: Dict[str, Detail] = {} # Borrowed from conduit a

    #region Cleanup
    def cleanup(self):
        """
        Idempotently tear down this contract and all contained Details.

        Clears both wards’ detail maps, nulls ward references, and marks the
        contract cleaned so it can no longer be used.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._clean_up()
            self._ward_a = None
            self._ward_b = None
            self._details_a = None
            self._details_b = None
            self._cleaned = True

    def _clean_up(self):
        """
        Internal helper to cleanup all Detail entries for both wards.
        """
        for detail in self._details_a.values():
            detail.cleanup()
        self._details_a.clear()

        for detail in self._details_b.values():
            detail.cleanup()
        self._details_b.clear()
    #endregion Cleanup


    #region Context Manager
    def __enter__(self):
        """
        Enters the context manager for Aether.
        """
        self._lock.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exits the context manager for Aether.
        """
        self._lock.release()

    #endregion Context Manager

    def _get_peer(self, ward: IConduitWard) -> IConduitWard:
        """
        Internal

        Return the opposite ward participant in this contract.

        Args:
            ward: The ward requesting its peer.

        Returns:
            IConduitWard: The other ward in the contract.

        Raises:
            ValueError: If the ward is not part of this contract.
        """
        if ward is self._ward_a:
            return self._ward_b
        if ward is self._ward_b:
            return self._ward_a
        raise ValueError("Ward is not a member of this contract.")

    def _get_opposite_conduit(self, contract: IContract, known_id: str) -> Optional[IConduit]:
        """
        Internal

        Helper to find the opposite conduit in a contract based on a known conduit ID.

        Args:
            contract: The contract to search within.
            known_id: Conduit ID you already know.
        Returns:
            Optional[IConduit]: The peer conduit if found, else None.
        """
        if contract._ward_a._conduit._id == known_id:
            return contract._ward_b._conduit
        elif contract._ward_b._conduit._id == known_id:
            return contract._ward_a._conduit
        return None

    def _get_detail_map(self, ward: IConduitWard) -> Dict[str, Detail]:
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

    def _add(self, ward: IConduitWard, contract_detail: Detail) -> bool:
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

    def _remove(self, ward: IConduitWard, spell_id: str) -> None:
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

    def _remove_source(self, ward: IConduitWard, spell_id: str, root_spell_id: str | None) -> bool:
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

    def _clear_contract(self):
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


    def _check_if_exists_and_permissions(self, ward: IConduitWard, spell_id: str, permission: Permissions) -> bool:
        """
        Internal

        Check if the given ward has permission for the specified spell.
        """
        detail_map = self._get_detail_map(ward)
        if spell_id not in detail_map:
            return False
        return detail_map[spell_id].permissions == permission

    def _check_if_exists(self, ward: IConduitWard, spell_id: str) -> bool:
        """
        Internal

        Check if a spell exists in the given ward's permission map.
        """
        detail_map = self._get_detail_map(ward)
        return spell_id in detail_map


    def _find_spell_in_ward(self, spell_id: str) -> IConduitWard | None:
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


    def _grant(self, ward: IConduitWard, spell_ids: list[str], permission: Permissions):
        """
        Internal

        Grant a list of spells with a single permission type for the specified ward.
        Each spell_id is resolved to a local SpellIndex owned by the ward's spellbook,
        and the Detail is recorded as an initiated grant.

        Args:
            ward (IConduitWard): The ward granting access.
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
                if candidate_index.has_version(spell_id):
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
