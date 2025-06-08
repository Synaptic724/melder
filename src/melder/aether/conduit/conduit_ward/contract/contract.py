from typing import Optional
from uuid import UUID, uuid4
from threading import RLock
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.utilities.concurrent_dictionary import ConcurrentDict
from melder.utilities.interfaces import ISeal, IConduitWard


class _Detail(ISeal):
    """
    Represents a spell-level permission entry for a specific conduit
    within a contract. This defines what access the conduit has to a spell.

    Fields:
    - spell_id: The identifier of the spell this permission applies to.
    - permissions: Permissions enum (read, create, block).

    Once sealed, the Detail becomes immutable and clears internal state.
    """

    def __init__(self, spell_id: str, permissions: Permissions):
        super().__init__()
        self._lock = RLock()

        if not isinstance(permissions, Permissions):
            raise TypeError(
                f"permissions must be an instance of Permissions enum, got {type(permissions).__name__}"
            )

        with self._lock:
            self.spell_id = spell_id
            self.permissions = permissions

    def seal(self):
        """
        Internal

        Seal this detail, nullifying sensitive data and marking it immutable.
        """
        if self._sealed:
            return
        with self._lock:
            if self._sealed:
                return
            self._sealed = True
            self.spell_id = None
            self.permissions = None


class _Contract(ISeal):
    """
    A symmetric contract between two conduit wards.

    Each contract maintains permission details for both sides independently.
    There is no directional bias (no initiator or provider); both parties
    may define what spells they allow the other to use.

    Fields:
    - _ward_a / _ward_b: The two conduit ward participants in this contract.
    - _details_a / _details_b: Spell permission maps for each ward's view.
    - _id: Unique identifier for this contract instance.
    """

    def __init__(self, ward_a: IConduitWard, ward_b: IConduitWard):
        super().__init__()
        self._lock = RLock()
        self._id: UUID = uuid4()

        self._ward_a: IConduitWard = ward_a
        self._ward_b: IConduitWard = ward_b

        # Each side stores its own view of spell permissions.
        self._details_a: ConcurrentDict[str, _Detail] = ConcurrentDict() # Borrowed from conduit b
        self._details_b: ConcurrentDict[str, _Detail] = ConcurrentDict() # Borrowed from conduit a

    def _get_peer(self, ward: IConduitWard) -> IConduitWard:
        """
        Internal

        Return the opposite conduit in this contract.
        """
        if ward is self._ward_a:
            return self._ward_b
        if ward is self._ward_b:
            return self._ward_a
        raise ValueError("Ward is not a member of this contract.")

    def _get_opposite_conduit(self, contract: '_Contract', known_id: UUID) -> Optional['IConduit']:
        """
        Internal

        Helper to find the opposite conduit in a contract based on a known conduit ID.
        :param contract:
        :param known_id:
        :return:
        """
        if contract._ward_a._id == known_id:
            return contract._ward_b._conduit
        elif contract._ward_b._id == known_id:
            return contract._ward_a._conduit
        return None

    def _get_detail_map(self, ward: IConduitWard) -> ConcurrentDict[str, _Detail]:
        """
        Internal

        Helper to return the permission map associated with a given ward.
        """
        if ward is self._ward_a:
            return self._details_a
        if ward is self._ward_b:
            return self._details_b
        raise ValueError("Invalid ward for contract access.")

    def _add(self, ward: IConduitWard, contract_detail: _Detail) -> None:
        """
        Internal

        Add a spell-level permission detail to the contract on behalf of the given ward.
        """
        self._get_detail_map(ward)[contract_detail.spell_id] = contract_detail

    def _remove(self, ward: IConduitWard, spell_id: str) -> None:
        """
        Internal

        Remove a spell-level permission detail from the given ward's view.
        """
        detail_map = self._get_detail_map(ward)
        if spell_id in detail_map:
            del detail_map[spell_id]

    def _has(self, ward: IConduitWard, spell_id: str, permission: Permissions) -> bool:
        """
        Internal

        Check if the given ward has permission for the specified spell.
        """
        detail_map = self._get_detail_map(ward)
        if spell_id not in detail_map:
            return False
        return detail_map[spell_id].permissions == permission

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
            detail_map[spell_id] = _Detail(spell_id, permission)

    def seal(self):
        """
        Internal

        Seal the contract, clearing its wards and internal details.
        """
        if self._sealed:
            return
        with self._lock:
            if self._sealed:
                return
            self.clean_up()
            self._ward_a = None
            self._ward_b = None
            self._sealed = True

    def clean_up(self):
        """
        Internal

        Seal and clear all spell details from both sides.
        """
        for detail in self._details_a.values():
            detail.seal()
        self._details_a.clear()

        for detail in self._details_b.values():
            detail.seal()
        self._details_b.clear()
