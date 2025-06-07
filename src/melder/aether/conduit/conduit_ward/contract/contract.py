from uuid import UUID, uuid4
from melder.aether.conduit.conduit_ward.contract.contract_types.contract_types import ContractTypes
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.utilities.concurrent_dictionary import ConcurrentDict
from melder.utilities.interfaces import ISeal, IConduitWard
from threading import RLock

class Detail(ISeal):
    """
    Represents a spell-level permission entry within a Contract.

    Each Detail object binds a specific spell ID to a set of permissions
    and tracks which provider conduit issued the permission.

    Fields:
    - spell_id: Unique identifier for the spell
    - permissions: Enum defining granted permissions (e.g., READ, WRITE)
    - _provider_id: UUID of the conduit providing the spell

    Once sealed, the Detail becomes immutable and clears sensitive fields.
    """

    def __init__(self, spell_id: str, permissions: Permissions):
        super().__init__()
        self._lock = RLock()
        self.spell_id = spell_id

        # Enforce type safety for permissions enum
        if permissions is not None:
            if not isinstance(permissions, Permissions):
                raise TypeError(
                    f"permissions must be an instance of Permissions enum, got {type(permissions).__name__}"
                )

        self.permissions = permissions

    def seal(self):
        """
        Seal the Detail entry, making it immutable and nullifying sensitive fields.
        """
        if self._sealed:
            return
        with self._lock:
            if self._sealed:
                return
            self._sealed = True
            self.spell_id = None
            self.permissions = None

class Contract(ISeal):
    """
    Standard contract for normal conduit links.

    This contract allows fine-grained permission control per spell.
    It tracks both ends of the conduit relationship (initiator and provider)
    and holds a mapping from spell_id to permission details.

    Fields:
    - _initiator_id / _initiator_ward: UUID and ward initiating the contract
    - _provider_id / _provider_ward: UUID and ward providing the spells
    - _contract_details: Maps spell_id → Detail (permissions, etc.)
    """

    def __init__(self, initiator_id: UUID, initiator_ward: IConduitWard, provider_id: UUID, provider_ward: IConduitWard):
        super().__init__()
        self._lock = RLock()
        self._initiator_id: UUID = initiator_id
        self._initiator_ward: IConduitWard = initiator_ward
        self._provider_id: UUID = provider_id
        self._provider_ward: IConduitWard = provider_ward

        # Spell-level permission map
        self._contract_details: ConcurrentDict[str, Detail] = ConcurrentDict()

    @staticmethod
    def type() -> ContractTypes:
        """
        Returns the contract type: normal conduit.
        """
        return ContractTypes.normal_conduit

    def add(self, contract_detail: Detail) -> None:
        """
        Add a spell-level permission entry to the contract.
        """
        self._contract_details[contract_detail.spell_id] = contract_detail

    def remove(self, contract_detail: Detail) -> None:
        """
        Remove a spell-level permission entry from the contract.
        """
        if contract_detail.spell_id in self._contract_details:
            del self._contract_details[contract_detail.spell_id]

    def has(self, spell_id: str, permission: Permissions) -> bool:
        """
        Check if a spell has the required permission.

        Args:
            spell_id (str): The identifier for the spell
            permission (Permissions): The permission to check for

        Returns:
            bool: True if permission exists, False otherwise
        """
        if spell_id not in self._contract_details:
            return False
        return self._contract_details[spell_id].permissions == permission

    def seal(self):
        """
        Seal the contract and its associated details.
        Clears all internal state to ensure immutability and cleanup.
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
        Seal and remove all spell-level details in the contract.
        """
        for detail in self._contract_details.values():
            detail.seal()
        self._contract_details.clear()