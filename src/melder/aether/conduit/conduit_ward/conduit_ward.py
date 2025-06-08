from uuid import UUID
import threading
from typing import List, Optional
from melder.aether.aether import Aether
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.utilities.concurrent_dictionary import ConcurrentDict
from melder.utilities.concurrent_list import ConcurrentList
from melder.utilities.general_helpers import EnumHelpers
from melder.utilities.interfaces import IConduit, IConduitWard
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.contract.contract import Detail, Contract

# TODO: Ensure that links properly connect to the spell and its dependencies not just the spell itself.
# TODO: If a specific policy is set such as blacklist or whitelist, ensure that the spellbook the entire spellbook is managed properly.

##### IMPORTANT NOTE #####
# TODO: Remember that this entire system is revolved around dynamic spell management. If a core scope that everyone is borrowing from is disposed, how can we handle that situation?


#region ConduitWard
class ConduitWard(IConduitWard):
    """
    ConduitWard manages the dynamic linking, lineage, and permission policy
    for a single conduit within the Melder framework.

    Key Responsibilities:
    - Maintains contracts with other conduits (both outbound and inbound).
    - Handles lineage via parent and lesser conduit tracking.
    - Enforces conduit access policies (e.g., whitelist, block, dynamic).
    - Manages thread-safe operations using internal locking.

    Contract Directionality:
    - _initiated_contracts: Links this conduit has initiated to others.
    - _provider_contracts: Links where this conduit has been the provider target.
    """
    _aether = Aether()
    def __init__(self, conduit: IConduit, dynamic: bool, conduit_type: ConduitState, policy: Policies):
        super().__init__()
        self._lock: threading.RLock  = threading.RLock()

        ## Conduit Ward properties
        self._conduit: IConduit = conduit
        self._dynamic: bool = dynamic
        self._conduit_type: ConduitState = conduit_type
        self._id = conduit.__creation_context__._conduit_id

        self._policy_set: bool = False
        self._policy: Policies = self._set_initial_policy(policy)

        # Contracts between conduits
        self._initiated_index: ConcurrentDict[UUID, UUID] = ConcurrentDict()  # [Target ConduitID] -> [ContractID]
        self._received_index: ConcurrentDict[UUID, UUID] = ConcurrentDict()  # [Source ConduitID] -> [ContractID]

        self._contracts: ConcurrentDict[UUID, Contract] = ConcurrentDict() # [ContractID] -> Contract

        # Lineage Links
        self._parent_conduit: IConduit | None = None
        self._lesser_conduits: ConcurrentDict[UUID, IConduit] = ConcurrentDict() # [Lesser ConduitID] -> Lesser Conduit

#region Properties
#endregion Properties

#region Conduit Ward Configuration
    def _convert_to_normal_conduit(self) -> None:
        """
        Internal

        Converts this Conduit to a normal Conduit.
        This is meant for internal use please do not use this outside of the class.
        """
        if self._conduit_type != ConduitState.lesser:
            raise RuntimeError("Conduit is not a lesser conduit.")
        if self._sealed:
            raise RuntimeError("Cannot convert a sealed Conduit.")
        with self._lock:
            if not self._dynamic:
                raise RuntimeError("Dynamic environment is not enabled. Cannot upgrade to normal conduit.")
            if self._parent_conduit is not None and self._conduit_type == ConduitState.lesser and self._lesser_conduits is None:
                self._parent_conduit = None
                self._conduit_type = ConduitState.normal #policy stays as delegate until the user adds a spell then it goes to dynamic
                self._policy = Policies.dynamic #Sets default to dynamic policy
            else:
                raise RuntimeError("No parent conduit link found. Cannot convert to normal conduit. Unknown error")

    def _set_initial_policy(self, policy: Policies) -> Optional[Policies]:
        """
        Internal

        Sets the default policy for this Conduit.
        This is meant for internal use please do not use this outside of the class.
        """
        if self._sealed:
            raise RuntimeError("Cannot set policy on a sealed Conduit.")

        # Ensure only valid enum instances are passed
        if not policy is None:
            if not isinstance(policy, Policies):
                raise TypeError(f"permissions must be an instance of Permissions enum, got {type(policy).__name__}")
            self._policy_set = True
            return policy

        with self._lock:
            if self._conduit_type == ConduitState.lesser:
                return Policies.lesser_conduit
            else:
                raise RuntimeError("Policy already set. Cannot set policy again.")

    def _set_new_policy(self, policy: str | Policies) -> None:
        """
        Internal

        Sets a new policy for this Conduit.
        This is meant for internal use; do not call externally.

        This method is internal and assumes the conduit is operating in dynamic mode.
        Certain policies like `block_all` and `whitelist_all` require an empty spellbook.
        Policy `lesser_conduit` is restricted to conduits of type `lesser`.
        """
        if self._sealed:
            raise RuntimeError("Cannot set policy on a sealed Conduit.")
        if not self._dynamic:
            raise RuntimeError("Dynamic environment is not enabled. Cannot set policy.")
        if self._conduit_type == ConduitState.lesser:
            raise RuntimeError("Cannot set policy on a lesser Conduit. Convert to a normal Conduit first.")

        with self._lock:
            new_policy = EnumHelpers.convert_enum_and_check(policy, Policies)

            if new_policy == Policies.automatic:
                raise RuntimeError("Cannot set policy to 'automatic' in dynamic mode.")
            if new_policy == Policies.lesser_conduit and self._conduit_type != ConduitState.lesser:
                raise RuntimeError("Cannot set policy to 'lesser_conduit' on a non-lesser Conduit.")
            if (new_policy == Policies.block_all or new_policy == Policies.whitelist_all) and self._conduit._spellbook._find_spell_count() > 0:
                raise RuntimeError("Cannot set policy to 'block_all' or 'whitelist_all' when there are existing spells in the spellbook.")

            self._policy = new_policy

#endregion Conduit Ward Configuration
#region Link Management
    def _link(self, target_conduit: IConduit) -> bool:
        """
        Internal

        Attempts to link this Conduit to another Conduit.

        Linking is only allowed if the world is in dynamic mode.

        Args:
            target_conduit (Conduit): The target Conduit to link to.

        Returns:
            bool: True if linking succeeds (currently not implemented).
        """
        if self._sealed:
            raise RuntimeError("Cannot link to a sealed Conduit Ward.")
        with self._lock:
            if not self._dynamic:
                raise RuntimeError("Dynamic environment is not enabled. Cannot link conduits.")
            if target_conduit.__creation_context__._conduit_id == self._id:
                raise RuntimeError("Cannot link a conduit to itself.")
            # Check if the target conduit is already linked
            if target_conduit._conduit_state == ConduitState.lesser:
                raise RuntimeError("Cannot link to a lesser conduit. Use _link_lesser_conduit instead.")
            if target_conduit._conduit_state == ConduitState.normal:
                if self._find_contract(target_conduit):
                    return True
                else:
                    # If the target conduit is normal, we can link it
                    if self._create_new_contract(target_conduit):
                        return True
                    else:
                        raise RuntimeError("Failed to create a new contract with the target conduit.")
            return False

    def _create_new_contract(self, target_conduit: IConduit) -> bool:
        """
        Internal
        Creates a new contract with the specified target conduit.
        :param target_conduit:
        :return:
        """
        with self._lock:
            # Create new contract
            contract = Contract(self, target_conduit._conduit_ward)

            # Register the contract in both wards
            self._contracts[contract._id] = contract
            target_conduit._conduit_ward._contracts[contract._id] = contract

            # Update the initiated and received indices
            self._initiated_index[target_conduit.__creation_context__._conduit_id] = contract._id
            target_conduit._conduit_ward._received_index[self._id] = contract._id
            return True


    def _find_contract_id(self, target_conduit: IConduit) -> Optional[UUID]:
        """
        Internal

        Finds a contract ID with the specified target conduit.

        Args:
            target_conduit (IConduit): The target conduit to find the contract for.

        Returns:
            Optional[Contract]: The found contract or None if not found.
        """
        if self._sealed:
            raise RuntimeError("Cannot find contracts in a sealed Conduit Ward.")
        if not isinstance(target_conduit, IConduit):
            raise TypeError(f"Expected IConduit instance, got {type(target_conduit).__name__}")

        initiated_contract = self._initiated_index.get(target_conduit._conduit_ward._id, None)
        received_contract = self._received_index.get(target_conduit._conduit_ward._id, None)

        return initiated_contract if initiated_contract is not None else received_contract

    def _find_contract(self, target_conduit: IConduit) -> Optional[Contract]:
        """
        Internal

        Finds the contract object linked to the given target conduit.

        Returns:
            Optional[Contract]: The contract object if it exists.
        """
        if self._sealed:
            raise RuntimeError("Cannot find contracts in a sealed Conduit Ward.")
        if not isinstance(target_conduit, IConduit):
            raise TypeError(f"Expected IConduit instance, got {type(target_conduit).__name__}")

        peer_id = target_conduit._conduit_ward._id
        contract_id = self._initiated_index.get(peer_id) or self._received_index.get(peer_id)
        return self._contracts.get(contract_id)

    def _sever_link(self, target_conduit: IConduit):
        """
        Internal

        Sever the link between this Conduit and its target Conduit.

        This is meant for internal use please do not use this outside of the class.
        """
        if self._sealed:
            raise RuntimeError("Cannot sever a link in a sealed Conduit Ward.")
        with self._lock:
            raise NotImplementedError("Severing links is not implemented yet.")

    def _link_lesser_conduit(self, lesser_conduit: IConduit):
        """
        Internal

        Links a lesser conduit to this conduit in automatic mode.

        This sets up the tree relationship between the current conduit and the lesser one.
        It should only be called internally. When called, the lesser conduit is registered
        under this ward, and the parent conduit reference is assigned in the lesser.

        Args:
            lesser_conduit (Conduit): The lesser conduit to link.
        """
        if self._sealed:
            raise RuntimeError("Cannot link to a sealed Conduit Ward.")
        with self._lock:
            self._lesser_conduits[lesser_conduit.__creation_context__._conduit_id] = lesser_conduit
            lesser_conduit._parent_conduit = self._conduit

    def _get_lesser_conduit(self, conduit_id: UUID) -> Optional[IConduit]:
        """
        Recursively searches for a lesser conduit with the given ID.

        Args:
            conduit_id (UUID): The ID of the conduit to retrieve.

        Returns:
            Optional[IConduit]: The matched conduit if found, else None.
        """
        if self._sealed:
            raise RuntimeError("Cannot get lesser conduits from a sealed Conduit Ward.")

        # Search immediate children
        for conduit in self._lesser_conduits.values():
            if conduit.__creation_context__._conduit_id == conduit_id:
                return conduit

            # Recurse into the child's ward if it has one
            ward = getattr(conduit, "_conduit_ward", None)
            if ward:
                result = ward._get_lesser_conduit(conduit_id)
                if result is not None:
                    return result

        return None

    def _get_links(self):
        """
        Internal

        Returns a list of all links associated with this conduit. Excluding lesser conduits.
        :return:
        """
        raise NotImplementedError("get_links is not implemented yet.")

    def _get_linked_conduits(self) -> List[IConduit]:
        """
        Internal

        Returns a list of conduits linked to this conduit.
        :return: List of linked conduits.
        """
        if self._sealed:
            raise RuntimeError("Cannot get linked conduits from a sealed Conduit Ward.")
        with self._lock:
            raise NotImplementedError("get_links is not implemented yet.")

    def _get_initiated_conduit(self, conduit_id: UUID) -> Optional[IConduit]:
        """
        Internal

        Returns a specific conduit linked to this conduit by its ID.

        Args:
            conduit_id (UUID): The ID of the conduit to retrieve.

        Returns:
            Optional[IConduit]: The linked conduit if found, otherwise None.
        """
        if self._sealed:
            raise RuntimeError("Cannot get linked conduits from a sealed Conduit Ward.")
        with self._lock:
            raise NotImplementedError("get_linked_conduit is not implemented yet.")

    def _get_provider_conduit(self, conduit_id: UUID) -> Optional[IConduit]:
        """
        Internal

        Returns a specific conduit linked to this conduit by its ID.

        Args:
            conduit_id (UUID): The ID of the conduit to retrieve.

        Returns:
            Optional[IConduit]: The linked conduit if found, otherwise None.
        """
        if self._sealed:
            raise RuntimeError("Cannot get linked conduits from a sealed Conduit Ward.")
        with self._lock:
            raise NotImplementedError("get_linked_conduit is not implemented yet.")

    def seal_all_lesser_conduits(self) -> None:
        """
        Public

        Severs all lesser conduits linked to this conduit.

        This is typically used when upgrading a conduit to a normal state,
        as lesser conduits must be detached first.

        Note:
            You can also simply call `seal()` on the parent conduit, which will
            recursively seal all linked lesser conduits automatically.
        """
        if self._sealed:
            raise RuntimeError("Cannot sever links in a sealed Conduit Ward.")
        with self._lock:
            for conduit in self._lesser_conduits.values():
                conduit.seal()
            self._lesser_conduits.clear()

    def _sever_all_linked_conduits(self) -> None:
        """
        Private

        Severs all links to conduits linked to this conduit. Excludes lesser conduits.
        """
        if self._sealed:
            raise RuntimeError("Cannot sever links in a sealed Conduit Ward.")
        with self._lock:
            raise NotImplementedError("Severing all links is not implemented yet.")


#endregion Link Management
#region Cleanup
    def seal(self):
        """
        Seals the conduit ward, preventing any further modifications.
        """
        raise NotImplementedError("is not implemented yet.")
        if self._sealed:
            return
        with self._lock:
            self._clean_up_links()
            self._clean_up_lesser_conduits_links()
            self._conduit = None
            self._dynamic = None
            self.sever_link(self._parent_conduit_link)
            self._conduit_type = self._conduit_type.sealed
            self._policy = None
            self._sealed = True


    def _clean_up_lesser_conduits_links(self):
        """
        Cleans up all lesser conduits.
        :return:
        """
        raise NotImplementedError("is not implemented yet.")
        if self._lesser_conduits_links:
            for lesser_conduit in self._lesser_conduits_links:
                lesser_conduit.seal()
            self._lesser_conduits_links.dispose()

    def _clean_up_links(self):
        """
        Cleans up all links.
        :return:
        """
        raise NotImplementedError("is not implemented yet.")
        if self._conduit_links:
            for link in self._conduit_links:
                link.seal()
            self._conduit_links.dispose()
#endregion Cleanup
#endregion ConduitWard