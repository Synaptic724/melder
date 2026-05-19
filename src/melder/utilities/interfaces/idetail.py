from typing import Set, Protocol, runtime_checkable
from melder.aether.conduit.conduit_ward.contract.contract_types.contract_types import ContractTypes
from melder.aether.conduit.conduit_ward.contract.detail_reason import DetailReason
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.ispellindex import ISpellIndex

@runtime_checkable
class IDetail(ICleanable, Protocol):
    """
    One lineage-aware spell detail stored inside a contract.
    """
    _id: str
    spell_index: ISpellIndex
    spell_id: str
    permissions: Permissions
    contract_type: ContractTypes
    reason: DetailReason
    sources: Set[str]

    def has_version(self, version_id: str) -> bool:
        """
        Return whether the lineage contains the provided version id.
        """
        ...

    def add_source(self, root_spell_id: str) -> None:
        """
        Record one root-lineage source for this detail.
        """
        ...

    def remove_source(self, root_spell_id: str) -> bool:
        """
        Remove one root-lineage source and report whether the detail should be
        deleted afterward.
        """
        ...
