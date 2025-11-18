from threading import RLock

# Melder imports
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.conduit_ward.contract.contract_types.contract_types import ContractTypes
from melder.spellbook.bind.spell_index import SpellIndex
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class Detail(Cleanable):
    """
    Spell-level permission entry inside a Contract.

    This is now **lineage-aware** and direction-aware.

    Fields:
        spell_index (SpellIndex):
            The lineage identity for the contracted spell. This does not
            change when the spell is mutated.

        spell_id (str):
            The SHA256 version ID **at the time this detail was created**.
            This is stable and is used as the key inside the Contract's
            internal maps for compatibility with existing code.

        permissions (Permissions):
            The granted permission for this spell lineage (read/create/block).

        contract_type (ContractTypes):
            Whether this entry represents an initiated or received grant
            from the point of view of the ward that owns the Detail map.
    """

    __slots__ = (
        "_lock",
        "_id",
        "spell_index",
        "spell_id",
        "permissions",
        "contract_type",
    )

    def __init__(
            self,
            spell_index: SpellIndex,
            spell_id: str,
            permissions: Permissions,
            contract_type: ContractTypes,
    ) -> None:
        super().__init__()
        self._lock = RLock()
        self._id: str = IDBuilder.create_id()

        if not isinstance(spell_index, SpellIndex):
            raise TypeError(
                f"spell_index must be SpellIndex, got {type(spell_index).__name__}"
            )
        if not isinstance(permissions, Permissions):
            raise TypeError(
                f"permissions must be Permissions, got {type(permissions).__name__}"
            )
        if not isinstance(contract_type, ContractTypes):
            raise TypeError(
                f"contract_type must be ContractTypes, got {type(contract_type).__name__}"
            )

        # Note: spell_id is the version at contract creation time.
        with self._lock:
            self.spell_index: SpellIndex = spell_index
            self.spell_id: str = spell_id
            self.permissions: Permissions = permissions
            self.contract_type: ContractTypes = contract_type

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------

    def has_version(self, version_id: str) -> bool:
        """
        Returns True if this Detail's SpellIndex lineage contains the given
        version SHA in its history.
        """
        versions = self.spell_index._versions
        if not versions:
            return False
        return version_id in versions

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def cleanup(self) -> None:
        """
        Internal

        Cleanup this Detail, nullifying sensitive data and marking it
        as cleaned.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return

            self._cleaned = True

            self.spell_index = None
            self.spell_id = None
            self.permissions = None
            self.contract_type = None

            self._id = None
            self._lock = None
