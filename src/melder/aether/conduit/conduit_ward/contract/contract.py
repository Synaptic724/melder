from uuid import UUID, uuid4
from melder.aether.conduit.conduit_ward.contract.contract_types.contract_types import ContractTypes
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.utilities.concurrent_dictionary import ConcurrentDict
from melder.utilities.interfaces import ISeal
from threading import RLock


class NormalConduitDetail(ISeal):
    """
    Represents a spell-level permission entry within a NormalConduitContract.
    Each instance binds a specific spell to a set of permissions.
    """

    def __init__(self, link_id: UUID, spell_id: str, permissions: Permissions):
        super().__init__()
        self._lock = RLock()
        self.spell_id = spell_id

        # Ensure only valid enum instances are passed
        if not permissions is None:
            if not isinstance(permissions, Permissions):
                raise TypeError(f"permissions must be an instance of Permissions enum, got {type(permissions).__name__}")

        self.permissions = permissions
        self._link_id: UUID = link_id

    def seal(self):
        """
        Seal the detail to make it immutable and clean up any sensitive data.
        """
        if self._sealed:
            return
        with self._lock:
            if self._sealed:
                return

            self._sealed = True
            self.spell_id = None
            self.permissions = None
            self._link_id = None


class NormalConduitContract(ISeal):
    """
    Standard contract for normal conduit links.
    Maintains fine-grained control over individual spell permissions.
    """

    def __init__(self, link_id: UUID):
        super().__init__()
        self._lock = RLock()
        self.link_id = link_id

        # Concurrent dictionary mapping spell_id → NormalConduitDetail
        self._contract_details: ConcurrentDict[str, NormalConduitDetail] = ConcurrentDict()

    @staticmethod
    def type() -> ContractTypes:
        """
        Identifies this detail as belonging to a normal conduit contract.
        """
        return ContractTypes.normal_conduit


    def add(self, contract_detail: NormalConduitDetail) -> None:
        """
        Add a new permission entry to the contract.
        """
        self._contract_details[contract_detail.spell_id] = contract_detail

    def remove(self, contract_detail: NormalConduitDetail) -> None:
        """
        Remove a permission entry from the contract.
        """
        if contract_detail.spell_id in self._contract_details:
            del self._contract_details[contract_detail.spell_id]

    def has(self, spell_id: str, permission: Permissions) -> bool:
        """
        Check if a spell has the specified permission.
        """
        if spell_id not in self._contract_details:
            return False
        return self._contract_details[spell_id].permissions == permission

    def seal(self):
        """
        Seal the entire contract and its details, clearing internal state.
        """
        if self._sealed:
            return
        with self._lock:
            if self._sealed:
                return
            self.clean_up()
            self._sealed = True
            self.link_id = None

    def clean_up(self):
        """
        Clean up and seal all contract details before clearing them.
        """
        for detail in self._contract_details.values():
            detail.seal()
        self._contract_details.clear()


class LesserConduitContract(ISeal):
    """
    Lightweight contract for lesser conduits.
    Does not track per-spell permissions — assumes global WRITE-level permission.
    """

    def __init__(self, link_id: UUID):
        super().__init__()
        self._lock = RLock()
        self.link_id = link_id

        # All lesser conduits default to WRITE permission
        self.permissions = Permissions.WRITE

    @staticmethod
    def type() -> ContractTypes:
        """
        Identifies this detail as belonging to a normal conduit contract.
        """
        return ContractTypes.lesser_conduit

    def has(self, permission: Permissions) -> bool:
        """
        Check if the requested permission is allowed.
        For lesser conduits, only WRITE is allowed.
        """
        return permission == self.permissions

    def seal(self):
        """
        Seal the lesser contract, nullifying sensitive fields.
        """
        if self._sealed:
            return
        with self._lock:
            if self._sealed:
                return

            self._sealed = True
            self.link_id = None
            self.permissions = None
