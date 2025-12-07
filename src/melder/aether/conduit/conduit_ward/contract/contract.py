from typing import Optional, Any, Dict
from threading import RLock
# Melder imports
from melder.aether.conduit.conduit_ward.contract.details import Detail
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.interfaces.interfaces import IConduitWard, IConduit, IContract
from melder.utilities.general_base.cleanable import Cleanable

class Contract(Cleanable):
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
        if contract._ward_a._id == known_id:
            return contract._ward_b._conduit
        elif contract._ward_b._id == known_id:
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

    def _add(self, ward: IConduitWard, contract_detail: Detail) -> None:
        """
        Internal

        Add a spell-level permission detail to the contract on behalf of the given ward.

        Args:
            ward: Ward that owns the detail map being updated.
            contract_detail: Detail entry to insert.
        """
        self._get_detail_map(ward)[contract_detail.spell_id] = contract_detail

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

        Args:
            ward (IConduitWard): The ward granting access.
            spell_ids (list[str]): List of spell IDs to grant.
            permission (Permissions): The permission level to assign.
        """
        detail_map = self._get_detail_map(ward)
        for spell_id in spell_ids:
            detail_map[spell_id] = Detail(spell_id, permission)
