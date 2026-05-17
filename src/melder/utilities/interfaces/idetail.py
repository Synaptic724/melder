from typing import runtime_checkable, Protocol
from melder.aether.conduit.conduit_ward.contract.contract_types.contract_types import ContractTypes
from melder.utilities.interfaces.icleanable import ICleanable

class IDetail(ICleanable, Protocol):
    """
    An Interface for a 'Detail', a single permission or rule within a Contract.
    """
    _id: str
    @property
    def type(self) -> 'ContractTypes':
        """
        The type of contract detail (e.g., 'grant', 'borrow').
        """
        ...

    def affects_permissions(self) -> bool:
        """
        Checks if this detail modifies spell permissions.

        Returns:
            bool: True if this detail grants or revokes spell access.
        """
        ...
