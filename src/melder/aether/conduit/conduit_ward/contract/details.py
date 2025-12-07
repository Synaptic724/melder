from threading import RLock

# Melder imports
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.conduit_ward.contract.contract_types.contract_types import ContractTypes
from typing import Set
from melder.aether.conduit.conduit_ward.contract.detail_reason import DetailReason
from melder.spellbook.bind.spell_index import SpellIndex
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class Detail(Cleanable):
    """
    Spell-level permission entry stored inside a Contract.

    A `Detail` records which lineage is being shared, which version was
    present when the contract was created, and what permission applies.
    It is lineage-aware (uses `SpellIndex`) and direction-aware (via
    `contract_type`).

    Attributes:
        spell_index (SpellIndex): Lineage identity for the contracted spell.
        spell_id (str): Version ID captured at contract creation time.
        permissions (Permissions): Granted permission (read/create/block).
        contract_type (ContractTypes): Whether this entry was initiated
            or received from the owning ward’s perspective.
    """

    __slots__ = (
        "_lock",
        "_id",
        "spell_index",
        "spell_id",
        "permissions",
        "contract_type",
        "reason",
        "sources",
    )

    def __init__(
            self,
            spell_index: SpellIndex,
            spell_id: str,
            permissions: Permissions,
            contract_type: ContractTypes,
            reason: DetailReason = DetailReason.other,
            sources: Set[str] | None = None,
    ) -> None:
        """
        Initialize a contract detail.

        Args:
            spell_index: Lineage identifier for the contracted spell.
            spell_id: Version ID (SHA) captured at contract creation time.
            permissions: Permission granted to this lineage.
            contract_type: Direction of the grant from the owning ward’s view.

        Raises:
            TypeError: If any argument is not the expected type.
        """
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
        if not isinstance(reason, DetailReason):
            raise TypeError(
                f"reason must be DetailReason, got {type(reason).__name__}"
            )
        if sources is not None and not isinstance(sources, set):
            raise TypeError(
                f"sources must be a set of spell_ids when provided, got {type(sources).__name__}"
            )

        # Note: spell_id is the version at contract creation time.
        with self._lock:
            self.spell_index: SpellIndex = spell_index
            self.spell_id: str = spell_id
            self.permissions: Permissions = permissions
            self.contract_type: ContractTypes = contract_type
            self.reason: DetailReason = reason
            self.sources: Set[str] = sources if sources is not None else set()


    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def cleanup(self) -> None:
        """
        Idempotently clear contract metadata and mark this detail cleaned.

        Drops references to the lineage, version, permissions, and contract
        direction so the object cannot be reused after cleanup.
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
            self.reason = None
            if self.sources is not None:
                self.sources.clear()
            self.sources = None

            self._id = None
        self._lock = None


    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------

    def has_version(self, version_id: str) -> bool:
        """
        Check whether this lineage contains a specific version SHA.

        Args:
            version_id: SHA fingerprint to check within the lineage history.

        Returns:
            bool: True if the lineage advertises the version, else False.
        """
        self.check_cleaned()
        versions = self.spell_index._versions
        if not versions:
            return False
        return version_id in versions

    def add_source(self, root_spell_id: str) -> None:
        """Track that a root spell_id requested this Detail."""
        self.check_cleaned()
        if root_spell_id is None:
            return
        with self._lock:
            if self.sources is None:
                self.sources = set()
            self.sources.add(root_spell_id)

    def remove_source(self, root_spell_id: str) -> bool:
        """
        Remove a root spell_id source. Returns True if sources is now empty.
        """
        self.check_cleaned()
        if root_spell_id is None or self.sources is None:
            return False
        with self._lock:
            self.sources.discard(root_spell_id)
            return len(self.sources) == 0
