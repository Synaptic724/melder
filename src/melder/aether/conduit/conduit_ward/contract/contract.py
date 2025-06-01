from uuid import UUID, uuid4
from melder.aether.conduit.conduit_ward.contract.contract_types.contract_types import ContractTypes
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.utilities.concurrent_dictionary import ConcurrentDict
from melder.utilities.concurrent_list import ConcurrentList
from melder.utilities.interfaces import ISeal, IConduitWard
from threading import RLock

class ContractHolder(ISeal):
    """
    Base class for all contract holders.
    Provides a common interface for sealing and managing contracts.
    """

    def __init__(self):
        super().__init__()
        self._lock = RLock()
        self._contracts: ConcurrentDict[UUID, Contract] = ConcurrentDict()
        self._delegate_contract: ConcurrentDict[UUID, DelegateContract] = ConcurrentDict()

    def seal(self):
        """
        Seal the contract holder to prevent further modifications.
        """
        if self._sealed:
            return
        with self._lock:
            if self._sealed:
                return
            self._sealed = True

class Detail(ISeal):
    """
    Represents a spell-level permission entry within a Contract.
    Each instance binds a specific spell to a set of permissions.
    """

    def __init__(self, provider_id: UUID, spell_id: str, permissions: Permissions):
        super().__init__()
        self._lock = RLock()
        self.spell_id = spell_id

        # Ensure only valid enum instances are passed
        if not permissions is None:
            if not isinstance(permissions, Permissions):
                raise TypeError(f"permissions must be an instance of Permissions enum, got {type(permissions).__name__}")

        self.permissions = permissions
        self._provider_id: UUID = provider_id

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
            self._provider_id = None

class Contract(ISeal):
    """
    Standard contract for normal conduit links.
    Maintains fine-grained control over individual spell permissions.
    """

    def __init__(self, initiator_id: UUID, initiator_ward: IConduitWard, provider_id: UUID, provider_ward: IConduitWard):
        super().__init__()
        self._lock = RLock()
        self._initiator_id: UUID = initiator_id
        self._initiator_ward: IConduitWard = initiator_ward
        self._provider_id: UUID = provider_id
        self._provider_ward: IConduitWard = provider_ward

        # Concurrent dictionary mapping spell_id → Detail
        self._contract_details: ConcurrentDict[str, Detail] = ConcurrentDict()

    @staticmethod
    def type() -> ContractTypes:
        """
        Identifies this detail as belonging to a normal conduit contract.
        """
        return ContractTypes.normal_conduit


    def add(self, contract_detail: Detail) -> None:
        """
        Add a new permission entry to the contract.
        """
        self._contract_details[contract_detail.spell_id] = contract_detail

    def remove(self, contract_detail: Detail) -> None:
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
            self._initiator_id = None
            self._initiator_ward = None
            self._provider_id = None
            self._provider_ward = None
            self._sealed = True

    def clean_up(self):
        """
        Clean up and seal all contract details before clearing them.
        """
        for detail in self._contract_details.values():
            detail.seal()
        self._contract_details.clear()

class DelegateContract(ISeal):
    """
    Lightweight contract for lesser conduits.
    Does not track per-spell permissions — assumes global WRITE-level permission.
    """
    def __init__(self, source_id: UUID, source_ward: IConduitWard, delegate_id: UUID, delegate_ward: IConduitWard):
        super().__init__()
        self._lock = RLock()
        self._source_id: UUID = source_id
        self._source_ward: IConduitWard = source_ward
        self._delegate_id: UUID = delegate_id
        self._delegate_ward: IConduitWard = delegate_ward

        # All lesser conduits default to WRITE permission
        self.permissions = Permissions.write

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
            self._source_id = None
            self._source_ward = None
            self._delegate_id = None
            self._delegate_ward = None
            self.permissions = None
