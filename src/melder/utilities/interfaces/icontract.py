from typing import Dict, Optional, Protocol, runtime_checkable
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.iconduit import IConduit
from melder.utilities.interfaces.iconduitward import IConduitWard
from melder.utilities.interfaces.idetail import IDetail

@runtime_checkable
class IContract(ICleanable, Protocol):
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

    _id: str
    _ward_a: IConduitWard
    _ward_b: IConduitWard
    _details_a: 'Dict[str, IDetail]'
    _details_b: 'Dict[str, IDetail]'

    def _clean_up(self) -> None:
        """
        Internal

        Clean up and clear all spell details from both sides.
        """
        ...

    def _get_peer(self, ward: IConduitWard) -> IConduitWard:
        """
        Internal

        Return the opposite ward participant in this contract.
        """
        ...

    def _get_opposite_conduit(self, contract: 'IContract', known_id: str) -> Optional[IConduit]:
        """
        Internal

        Resolve the opposite conduit in a contract from one known conduit id.

        Returns:
            Optional[IConduit]: Opposite conduit when the known id participates
            in the contract; otherwise None.
        """
        ...

    def _get_detail_map(self, ward: IConduitWard) -> 'Dict[str, IDetail]':
        """
        Internal

        Return the permission-detail map associated with one ward.
        """
        ...

    def _add(self, ward: IConduitWard, contract_detail: IDetail) -> None:
        """
        Internal

        Add one spell-level permission detail to the contract for the given ward.
        """
        ...

    def _remove(self, ward: IConduitWard, spell_id: str) -> None:
        """
        Internal

        Remove one spell-level permission detail from the given ward's view.
        """
        ...

    def _clear_contract(self) -> None:
        """
        Internal

        Clear all spell details from both sides of the contract.
        This is typically called when cleaning the contract.
        """
        ...

    def _check_if_exists_and_permissions(self, ward: IConduitWard, spell_id: str, permission: 'Permissions') -> bool:
        """
        Internal

        Check whether the given ward currently grants the specified permission
        for one spell id.
        """
        ...

    def _check_if_exists(self, ward: IConduitWard, spell_id: str) -> bool:
        """
        Internal

        Check whether a spell exists in the given ward's permission map.
        """
        ...

    def _find_spell_in_ward(self, spell_id: str) -> IConduitWard | None:
        """
        Internal

        Find which ward currently carries the specified spell id, if any.
        """
        ...

    def _grant(self, ward: IConduitWard, spell_ids: list[str], permission: 'Permissions') -> None:
        """
        Internal

        Grant a list of spells with a single permission type for the specified ward.

        Args:
            ward (IConduitWard): The ward granting access.
            spell_ids (list[str]): List of spell IDs to grant.
            permission (Permissions): The permission level to assign.
        """
        ...
