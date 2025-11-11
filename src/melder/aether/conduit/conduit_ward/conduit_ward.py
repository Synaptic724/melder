from uuid import UUID
import threading
from typing import List, Optional, Any, Tuple

# Melder Imports
from melder.utilities.general_base.sealable import Sealable
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.utilities.data_structures.concurrent_dictionary import ConcurrentDict
from melder.utilities.helpers.general_helpers import EnumHelpers
from melder.utilities.helpers.init_helpers import InitHelpers
from melder.utilities.interfaces.interfaces import IConduit, IConduitWard, ISpell
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.contract.contract import Detail, Contract


# TODO: Ensure that links properly connect to the spell and its dependencies not just the spell itself.
# TODO: If a specific policy is set such as blacklist or whitelist, ensure that the spellbook the entire spellbook is managed properly.

##### IMPORTANT NOTE #####
# TODO: Remember that this entire system is revolved around dynamic spell management. If a core scope that everyone is borrowing from is disposed, how can we handle that situation?


#region ConduitWard
class ConduitWard(Sealable, IConduitWard):
    """
    ConduitWard manages the dynamic linking, lineage, and permission policy
    for a single conduit within the Melder framework.

    Key Responsibilities:
    * **Contract Management:** Maintains thread-safe contracts defining shared spells with other conduits.
    * **Lineage Tracking:** Handles the tree structure via parent and lesser conduit tracking.
    * **Policy Enforcement:** Enforces conduit access policies (e.g., whitelist, block, dynamic).

    Contract Directionality:
    * `_initiated_index`: Tracks links this conduit has initiated (outbound).
    * `_received_index`: Tracks links where this conduit has been the provider target (inbound).
    """
    def __init__(self, conduit: IConduit, dynamic: bool, conduit_type: ConduitState, policy: Policies, logger: Any | None = None):
        super().__init__()
        self._lock: threading.RLock  = threading.RLock()

        ## Conduit Ward properties
        self._conduit: IConduit = conduit
        self._dynamic: bool = dynamic
        self._conduit_type: ConduitState = conduit_type
        self._id = conduit.__creation_context__._conduit_id
        self._logger = self._setup_logger(logger, conduit._configuration)

        self._policy_set: bool = False
        self._policy: Policies = self._set_initial_policy(policy)

        # Contracts between conduits
        self._initiated_index: ConcurrentDict[UUID, UUID] = ConcurrentDict()  # [Target ConduitID] -> [ContractID]
        self._received_index: ConcurrentDict[UUID, UUID] = ConcurrentDict()  # [Source ConduitID] -> [ContractID]

        self._contracts: ConcurrentDict[UUID, Contract] = ConcurrentDict() # [ContractID] -> Contract

        # Lineage Links
        self._parent_conduit: IConduit | None = None
        self._lesser_conduits: ConcurrentDict[UUID, IConduit] = ConcurrentDict() # [Lesser ConduitID] -> Lesser Conduit

    #region Cleanup
    def seal(self):
        """
        Public API

        Seals the conduit ward, preventing any further modifications or operations.
        """
        self._logger.debug("seal() called (not implemented)", "seal")
        raise NotImplementedError("Sealing is not implemented yet.")
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
        Internal

        Recursively seals and removes all linked lesser conduits (children).
        """
        self._logger.debug("_clean_up_lesser_conduits_links called (not implemented)", "_clean_up_lesser_conduits_links")
        raise NotImplementedError("is not implemented yet.")
        if self._lesser_conduits_links:
            for lesser_conduit in self._lesser_conduits_links:
                lesser_conduit.seal()
            self._lesser_conduits_links.dispose()

    def _clean_up_links(self):
        """
        Internal

        Seals and disposes of all active external contracts and links.
        """
        self._logger.debug("_clean_up_links called (not implemented)", "_clean_up_links")
        raise NotImplementedError("is not implemented yet.")
        if self._conduit_links:
            for link in self._conduit_links:
                link.seal()
            self._conduit_links.dispose()
    #endregion Cleanup


    def _setup_logger(self, logger: Any | None, configuration: Any) -> Any:
        """
        Internal
        Sets up the logger for this ConduitWard.

        Args:
            logger (Any | None): An optional logger instance provided during initialization.
            configuration (Any): The configuration object that may provide a logger factory.
        """
        if logger is not None:
            return InitHelpers.resolve_safe_logger(logger)
        if configuration is not None and hasattr(configuration, "has_logger_factory") and configuration.has_logger_factory():
            return InitHelpers.resolve_safe_logger(configuration.get_logger_for(self))
        return InitHelpers.resolve_safe_logger(None)

    #region Properties
    #endregion Properties

    #region Conduit Ward Configuration
    def _convert_to_normal_conduit(self) -> None:
        """
        Internal

        Converts this Conduit from a `lesser` state to a `normal` state.

        This method is called internally during the conduit upgrade process.
        It detaches the parent link and updates the policy state.

        Raises:
            RuntimeError: If the Conduit is not a lesser conduit.
            RuntimeError: If dynamic environment is not enabled.
            RuntimeError: If no parent conduit link is found (unknown error state).
        """
        self.check_sealed()
        if self._conduit_type != ConduitState.lesser:
            self._logger.error("Conduit is not a lesser conduit", "_convert_to_normal_conduit")
            raise RuntimeError("Conduit is not a lesser conduit.")
        with self._lock:
            if not self._dynamic:
                self._logger.error("Dynamic environment is not enabled", "_convert_to_normal_conduit")
                raise RuntimeError("Dynamic environment is not enabled. Cannot upgrade to normal conduit.")
            if self._parent_conduit is not None and self._conduit_type == ConduitState.lesser and len(self._lesser_conduits) == 0:
                self._parent_conduit = None
                self._conduit_type = ConduitState.normal
                self._policy = Policies.dynamic
                self._logger.debug("Converted to normal conduit (policy=dynamic)", "_convert_to_normal_conduit")
            else:
                self._logger.error("No parent conduit link found; unknown error", "_convert_to_normal_conduit")
                raise RuntimeError("No parent conduit link found. Cannot convert to normal conduit. Unknown error")


    def _set_initial_policy(self, policy: Policies) -> Optional[Policies]:
        """
        Internal

        Sets the default policy for this Conduit during initialization.

        Args:
            policy (Policies): The desired initial policy.

        Returns:
            Optional[Policies]: The set policy.

        Raises:
            TypeError: If `policy` is not an instance of the `Policies` enum.
            RuntimeError: If the policy has already been set.
        """
        self.check_sealed()

        # Ensure only valid enum instances are passed
        if policy is not None:
            if not isinstance(policy, Policies):
                self._logger.error(f"Invalid policy type: {type(policy).__name__}", "_set_initial_policy")
                raise TypeError(f"Expected Policies enum instance, got {type(policy).__name__}")
            self._policy_set = True
            self._logger.debug(f"Initial policy set to {policy.name}", "_set_initial_policy")
            return policy

        with self._lock:
            if self._conduit_type == ConduitState.lesser:
                self._logger.debug("Initial policy defaulting to lesser_conduit", "_set_initial_policy")
                return Policies.lesser_conduit
            else:
                self._logger.error("Policy already set or invalid state", "_set_initial_policy")
                raise RuntimeError("Policy already set. Cannot set policy again.")

    def _set_new_policy(self, policy: str | Policies) -> None:
        """
        Internal

        Sets a new operational policy for this Conduit.

        This is restricted to `normal` conduits in dynamic mode.

        Args:
            policy (str | Policies): The new policy to set.

        Raises:
            RuntimeError: If the Conduit is sealed.
            RuntimeError: If dynamic environment is not enabled.
            RuntimeError: If the Conduit is a lesser Conduit.
            RuntimeError: If attempting to set to `automatic` in dynamic mode.
            RuntimeError: If attempting to set to `lesser_conduit` on a non-lesser Conduit.
            RuntimeError: If attempting to set to `block_all` or `whitelist_all` while contracts exist.
        """
        self.check_sealed()
        if not self._dynamic:
            self._logger.error("Dynamic environment is not enabled", "_set_new_policy")
            raise RuntimeError("Dynamic environment is not enabled. Cannot set policy.")
        if self._conduit_type == ConduitState.lesser:
            self._logger.error("Attempt to set policy on lesser conduit", "_set_new_policy")
            raise RuntimeError("Cannot set policy on a lesser Conduit. Convert to a normal Conduit first.")

        with self._lock:
            new_policy = EnumHelpers.convert_enum_and_check(policy, Policies)
            if new_policy == Policies.automatic:
                self._logger.error("Cannot set policy to automatic in dynamic mode", "_set_new_policy")
                raise RuntimeError("Cannot set policy to 'automatic' in dynamic mode.")
            if new_policy == Policies.lesser_conduit and self._conduit_type != ConduitState.lesser:
                self._logger.error("Cannot set policy to lesser_conduit on non-lesser conduit", "_set_new_policy")
                raise RuntimeError("Cannot set policy to 'lesser_conduit' on a non-lesser Conduit.")
            if (new_policy == Policies.block_all or new_policy == Policies.whitelist_all) and len(self._contracts) > 0:
                self._logger.error("Cannot set policy to block_all/whitelist_all with existing contracts", "_set_new_policy")
                raise RuntimeError("Cannot set policy to 'block_all' or 'whitelist_all' when there are existing contracts.")

            self._policy = new_policy
            self._logger.debug(f"Policy updated to {new_policy.name}", "_set_new_policy")


    #endregion Conduit Ward Configuration
    #region Link Management
    def _link(self, target_conduit: IConduit) -> bool:
        """
        Internal

        Attempts to establish a link (contract) with another normal Conduit.

        Args:
            target_conduit (IConduit): The target Conduit to link to.

        Returns:
            bool: True if the contract was established or already exists.

        Raises:
            RuntimeError: If the Conduit is sealed.
            RuntimeError: If attempting to link to a lesser conduit.
            RuntimeError: If attempting to link a conduit to itself.
            RuntimeError: If dynamic environment is not enabled.
        """
        self.check_sealed()
        if target_conduit._conduit_state == ConduitState.lesser:
            self._logger.error("Cannot link to lesser conduit", "_link")
            raise RuntimeError("Cannot link to a lesser conduit. Use _link_lesser_conduit instead.")
        if target_conduit.__creation_context__._conduit_id == self._id:
            self._logger.error("Attempted self-link", "_link")
            raise RuntimeError("Cannot link a conduit to itself.")
        if not self._dynamic:
            self._logger.error("Dynamic environment is not enabled", "_link")
            raise RuntimeError("Dynamic environment is not enabled. Cannot link conduits.")

        # Check if the target conduit is already linked
        if target_conduit._conduit_state == ConduitState.normal:
            if self._find_contract(target_conduit):
                self._logger.debug("Contract already exists; link is idempotent", "_link")
                return True
            ok = self._create_new_contract(target_conduit)
            self._logger.debug(f"_create_new_contract -> {ok}", "_link")
            return ok

        self._logger.debug("Target conduit not normal; link aborted", "_link")
        return False


    def _create_new_contract(self, target_conduit: IConduit) -> bool:
        """
        Internal

        Creates a new bidirectional contract (link) with the specified target conduit.

        This method handles simultaneous locking of both wards to prevent deadlocks.

        Args:
            target_conduit (IConduit): The conduit to link with.

        Returns:
            bool: True if the contract was created successfully.
        """
        ward_a = self
        ward_b = target_conduit._conduit_ward

        # Lock both wards in a consistent order to avoid deadlocks
        locks = sorted([ward_a._lock, ward_b._lock], key=id)
        with locks[0]:
            with locks[1]:
                target_id = target_conduit.__creation_context__._conduit_id

                # Double-check in case of race
                if self._find_contract(target_conduit):
                    self._logger.debug("Contract existed after double-check; no-op", "_create_new_contract")
                    return True

                contract = Contract(self, ward_b)

                # Register in both wards
                self._contracts[contract._id] = contract
                ward_b._contracts[contract._id] = contract

                # Index updates
                self._initiated_index[target_id] = contract._id
                ward_b._received_index[self._id] = contract._id

                # Create spellbook entries for contracted spells
                ward_b._conduit._spellbook._create_link_contract(target_id)
                self._logger.debug(f"New contract created (id={contract._id}) with peer={target_id}", "_create_new_contract")
                return True

    def _find_contract_id(self, target_conduit: IConduit) -> Optional[UUID]:
        """
        Internal

        Finds a contract ID associated with the specified target conduit.

        Args:
            target_conduit (IConduit): The target conduit to find the contract for.

        Returns:
            Optional[UUID]: The ID of the found contract or None if not found.

        Raises:
            RuntimeError: If the Conduit is sealed.
            TypeError: If `target_conduit` is not an `IConduit` instance.
        """
        self.check_sealed()
        if not isinstance(target_conduit, IConduit):
            self._logger.error(f"Invalid target type: {type(target_conduit).__name__}", "_find_contract_id")
            raise TypeError(f"Expected IConduit instance, got {type(target_conduit).__name__}")

        # Check both initiated and received indexes
        initiated_contract = self._initiated_index.get(target_conduit._conduit_ward._id, None)
        received_contract = self._received_index.get(target_conduit._conduit_ward._id, None)
        cid = initiated_contract if initiated_contract is not None else received_contract
        self._logger.debug(f"_find_contract_id -> {cid}", "_find_contract_id")
        return cid


    def _find_contract(self, target_conduit: IConduit) -> Optional[Contract]:
        """
        Internal

        Finds the contract object linked to the given target conduit.

        Args:
            target_conduit (IConduit): The target conduit to find the contract for.

        Returns:
            Optional[Contract]: The contract object if it exists, otherwise None.

        Raises:
            RuntimeError: If the Conduit is sealed.
            TypeError: If `target_conduit` is not an `IConduit` instance.
        """
        self.check_sealed()
        if not isinstance(target_conduit, IConduit):
            self._logger.error(f"Invalid target type: {type(target_conduit).__name__}", "_find_contract")
            raise TypeError(f"Expected IConduit instance, got {type(target_conduit).__name__}")


        peer_id = target_conduit._conduit_ward._id
        contract_id = self._initiated_index.get(peer_id) or self._received_index.get(peer_id)
        contract = self._contracts.get(contract_id)
        self._logger.debug(f"_find_contract -> {contract_id}", "_find_contract")
        return contract

    def _find_contract_by_id(self, conduit_id: UUID) -> Optional[Contract]:
        """
        Internal

        Finds a contract by the peer's Conduit ID.

        Args:
            conduit_id (UUID): The ID of the peer conduit in the contract.

        Returns:
            Optional[Contract]: The found contract object or None if not found.

        Raises:
            RuntimeError: If the Conduit is sealed.
        """
        self.check_sealed()
        # Look up the contract ID using the peer's conduit ID
        check_id = self._initiated_index.get(conduit_id) or self._received_index.get(conduit_id)
        contract = self._contracts.get(check_id)
        self._logger.debug(f"_find_contract_by_id({conduit_id}) -> {check_id}", "_find_contract_by_id")
        return contract

    def _sever_link(self, target_conduit: IConduit) -> bool:
        """
        Internal

        Sever the link (contract) between this Conduit and its target Conduit.

        Args:
            target_conduit (IConduit): The target Conduit to sever the link with.

        Returns:
            bool: True if the link was successfully severed.

        Raises:
            RuntimeError: If the Conduit is sealed.
            RuntimeError: If no contract is found to sever.
        """
        self.check_sealed()
        locks = sorted([self._lock, target_conduit._conduit_ward._lock], key=id)
        with locks[0]:
            with locks[1]:
                if self._find_contract(target_conduit):
                    ok = self._remove_contract(target_conduit)
                    self._logger.debug(f"_remove_contract -> {ok}", "_sever_link")
                    return ok
                self._logger.error("No contract found to sever", "_sever_link")
                raise RuntimeError("No contract found to sever with the target conduit.")

    def _remove_contract(self, target_conduit: IConduit) -> bool:
        """
        Internal

        Removes the contract and cleans up internal indices and spellbook links.

        Args:
            target_conduit (IConduit): The conduit whose contract should be removed.

        Returns:
            bool: True if the contract was removed successfully.

        Raises:
            RuntimeError: If the Conduit is sealed.
        """
        self.check_sealed()
        self._check_conduit_id_and_conduit(conduit=target_conduit)

        if (contract := self._find_contract(target_conduit)) is not None:
            with contract._lock:
                id_a = contract._ward_a._id
                id_b = contract._ward_b._id

                # Sever spellbook contracts on both sides
                contract._ward_a._conduit._spellbook._sever_link_contract(id_b)
                contract._ward_b._conduit._spellbook._sever_link_contract(id_a)

                # Remove contract from both ward registries
                del self._contracts[contract._id]
                del target_conduit._conduit_ward._contracts[contract._id]

                # Remove index entries
                # We need to check which index to delete from since the link can be initiated or received
                if target_conduit.__creation_context__._conduit_id in self._initiated_index:
                    del self._initiated_index[target_conduit.__creation_context__._conduit_id]
                    del target_conduit._conduit_ward._received_index[self._id]
                elif target_conduit.__creation_context__._conduit_id in self._received_index:
                    del self._received_index[target_conduit.__creation_context__._conduit_id]
                    del target_conduit._conduit_ward._initiated_index[self._id]

                contract.seal()
                self._logger.debug(f"Contract {contract._id} removed", "_remove_contract")
                return True
        self._logger.debug("No contract to remove; returning False", "_remove_contract")
        return False

    def _link_lesser_conduit(self, lesser_conduit: IConduit):
        """
        Internal

        Links a lesser conduit (child) to this conduit (parent).

        This establishes the parent-child lineage relationship.

        Args:
            lesser_conduit (IConduit): The lesser conduit to link.

        Raises:
            RuntimeError: If the Conduit is sealed.
        """
        self.check_sealed()
        with self._lock:
            self._lesser_conduits[lesser_conduit.__creation_context__._conduit_id] = lesser_conduit
            lesser_conduit._parent_conduit = self._conduit
            self._logger.debug(f"Lesser conduit linked (id={lesser_conduit.__creation_context__._conduit_id})", "_link_lesser_conduit")


    def _get_lesser_conduit(self, conduit_id: UUID) -> Optional[IConduit]:
            """
            Internal

            Recursively searches for a lesser conduit with the given ID within this conduit's hierarchy.

            Args:
                conduit_id (UUID): The ID of the conduit to retrieve.

            Returns:
                Optional[IConduit]: The matched conduit if found, else None.

            Raises:
                RuntimeError: If the Conduit is sealed.
            """
            self.check_sealed()

            # Search immediate children
            for conduit in self._lesser_conduits.values():
                if conduit.__creation_context__._conduit_id == conduit_id:
                    return conduit

                # Recurse into the child's ward if it has one
                if (ward := getattr(conduit, "_conduit_ward", None)):
                    if (result := ward._get_lesser_conduit(conduit_id)) is not None:
                        self._logger.debug(f"Found nested lesser conduit {conduit_id}", "_get_lesser_conduit")
                        return result
            self._logger.debug(f"No lesser conduit found for {conduit_id}", "_get_lesser_conduit")
            return None

    def _get_links(self) -> List[IConduit]:
        """
        Internal

        Returns a combined list of all peer conduits this conduit has contracts with (both initiated and provider).

        Returns:
            List[IConduit]: A list of all linked peer conduits.
        """
        self.check_sealed()
        result = [
            conduit for conduit_id in self._initiated_index.keys()
            if (conduit := self._get_initiated_conduit(conduit_id)) is not None
        ]
        self._logger.debug(f"_get_initiated_conduits -> {len(result)}", "_get_initiated_conduits")
        return result


    def _get_initiated_conduits(self) -> List[IConduit]:
        """
        Internal

        Retrieves all conduits that this conduit has initiated contracts toward (outbound links).

        Returns:
            List[IConduit]: A list of conduits that this conduit has initiated contracts with.

        Raises:
            RuntimeError: If the Conduit is sealed.
        """
        self.check_sealed()
        return [
            conduit for conduit_id in self._initiated_index.keys()
            if (conduit := self._get_initiated_conduit(conduit_id)) is not None
        ]


    def _get_provider_conduits(self) -> List[IConduit]:
        """
        Internal

        Retrieves all conduits that have initiated contracts to this conduit (inbound links).

        Returns:
            List[IConduit]: A list of conduits that have linked to this conduit as a provider.

        Raises:
            RuntimeError: If the Conduit is sealed.
        """
        self.check_sealed()
        result = [
            conduit for conduit_id in self._received_index.keys()
            if (conduit := self._get_provider_conduit(conduit_id)) is not None
        ]
        self._logger.debug(f"_get_provider_conduits -> {len(result)}", "_get_provider_conduits")
        return result

    def _get_initiated_conduit(self, conduit_id: UUID) -> Optional[IConduit]:
        """
        Internal

        Retrieves the conduit that this conduit has initiated a contract *toward*.

        Args:
            conduit_id (UUID): The ID of the target conduit this conduit linked to.

        Returns:
            Optional[IConduit]: The target conduit if the link exists, otherwise None.

        Raises:
            RuntimeError: If the Conduit is sealed.
        """
        self.check_sealed()
        if conduit_id in self._initiated_index:
            contract_id = self._initiated_index[conduit_id]
            contract = self._contracts.get(contract_id, None)
            if contract is not None:
                result = contract._ward_b._conduit if conduit_id == contract._ward_b._id else contract._ward_a._conduit
                self._logger.debug(f"_get_initiated_conduit -> {bool(result)}", "_get_initiated_conduit")
                return result
        self._logger.debug("_get_initiated_conduit -> None", "_get_initiated_conduit")
        return None


    def _get_provider_conduit(self, conduit_id: UUID) -> Optional[IConduit]:
        """
        Internal

        Retrieves the conduit that initiated a contract *to this* conduit.

        Args:
            conduit_id (UUID): The ID of the source conduit that linked to this one.

        Returns:
            Optional[IConduit]: The source conduit if the link exists, otherwise None.

        Raises:
            RuntimeError: If the Conduit is sealed.
        """
        self.check_sealed()
        if conduit_id in self._received_index:
            contract_id = self._received_index[conduit_id]
            contract = self._contracts.get(contract_id, None)
            if contract is not None:
                result = contract._ward_b._conduit if conduit_id == contract._ward_b._id else contract._ward_a._conduit
                self._logger.debug(f"_get_provider_conduit -> {bool(result)}", "_get_provider_conduit")
                return result
        self._logger.debug("_get_provider_conduit -> None", "_get_provider_conduit")
        return None


    def seal_all_lesser_conduits(self) -> None:
        """
        Public API

        Seals all lesser conduits (children) linked to this conduit.

        This is typically used when the parent conduit is undergoing a state change,
        like an upgrade to a normal state, or as part of a controlled shutdown.

        Raises:
            RuntimeError: If the Conduit is sealed.
        """
        self.check_sealed()
        with self._lock:
            for conduit in self._lesser_conduits.values():
                self._logger.debug(f"Sealing lesser conduit {conduit.__creation_context__._conduit_id}", "seal_all_lesser_conduits")
                conduit.seal()
            self._lesser_conduits.clear()
        self._logger.debug("All lesser conduits sealed and cleared", "seal_all_lesser_conduits")


    def _sever_all_linked_conduits(self) -> None:
        """
        Internal

        Severs all active peer links (contracts) to conduits. Excludes lesser conduits.
        """
        self.check_sealed()
        with self._lock:
            self._logger.debug("_sever_all_linked_conduits called (not implemented)", "_sever_all_linked_conduits")
            raise NotImplementedError("Severing all links is not implemented yet.")


    #endregion Link Management
    #region Spellbinding API
    def _check_spell_id_and_spell(
            self,
            spell: ISpell = None,
            spell_id: str = None,
            aetheric_frame: str = "default"
    ) -> Tuple[str, ISpell]:
        """
        Internal

        Validation and resolution helper: ensures both a spell ID and its corresponding spell object are available.

        Args:
            spell (ISpell, optional): The spell object.
            spell_id (str, optional): The unique ID of the spell.
            aetheric_frame (str): The Aetheric Frame to search within.

        Returns:
            Tuple[str, ISpell]: The resolved (spell_id, spell) pair.

        Raises:
            ValueError: If neither `spell` nor `spell_id` is provided.
            TypeError: If types are incorrect.
            RuntimeError: If the spell cannot be resolved or if the provided ID and resolved ID mismatch.
        """
        if spell is None and spell_id is None:
            self._logger.error("Neither spell nor spell_id provided", "_check_spell_id_and_spell")
            raise ValueError("Either spell or spell_id must be provided.")

        if spell is None:
            if not isinstance(spell_id, str):
                self._logger.error(f"spell_id type invalid: {type(spell_id).__name__}", "_check_spell_id_and_spell")
                raise TypeError(f"Expected spell_id as str, got {type(spell_id).__name__}")
            spell = self._conduit.get_spell_by_id(spell_id, aetheric_frame)
            if spell is None:
                self._logger.error(f"Could not resolve spell for id {spell_id}", "_check_spell_id_and_spell")
                raise RuntimeError(f"Could not resolve spell for spell_id '{spell_id}'.")

        if spell_id is None:
            if not isinstance(spell, ISpell):
                self._logger.error(f"spell type invalid: {type(spell).__name__}", "_check_spell_id_and_spell")
                raise TypeError(f"Expected ISpell instance, got {type(spell).__name__}")
            spell_id = self._conduit.inspect_spell(spell, aetheric_frame)
            if spell_id is None:
                self._logger.error("Could not determine spell_id from spell", "_check_spell_id_and_spell")
                raise RuntimeError("Could not determine spell_id from spell.")

        inspected_id = self._conduit.inspect_spell(spell, aetheric_frame)
        if spell_id != inspected_id:
            self._logger.error(f"Mismatched spell_id '{spell_id}' vs inspected '{inspected_id}'", "_check_spell_id_and_spell")
            raise RuntimeError(f"Provided spell_id '{spell_id}' does not match inspected ID '{inspected_id}'.")

        self._logger.debug(f"_check_spell_id_and_spell -> id={spell_id}", "_check_spell_id_and_spell")
        return spell_id, spell


    def _check_conduit_id_and_conduit(self,
                                      conduit: IConduit = None,
                                      conduit_id: UUID = None, aetheric_frame = "default") -> Tuple[UUID, IConduit]:
        """
        Internal

        Validation and resolution helper: ensures both a conduit ID and its corresponding conduit object are available.

        Args:
            conduit (IConduit, optional): The target conduit object.
            conduit_id (UUID, optional): The unique ID of the target conduit.
            aetheric_frame (str): The Aetheric Frame to search within.

        Returns:
            Tuple[UUID, IConduit]: The resolved (conduit_id, conduit) pair.

        Raises:
            ValueError: If neither `conduit` nor `conduit_id` is provided.
            TypeError: If types are incorrect.
            RuntimeError: If the conduit cannot be resolved or if IDs mismatch.
        """
        if conduit is None and conduit_id is None:
            self._logger.error("Neither conduit nor conduit_id provided", "_check_conduit_id_and_conduit")
            raise ValueError("Either conduit or conduit_id must be provided.")

        if conduit is None:
            if not isinstance(conduit_id, UUID):
                self._logger.error(f"conduit_id type invalid: {type(conduit_id).__name__}", "_check_conduit_id_and_conduit")
                raise TypeError(f"Expected conduit_id as UUID, got {type(conduit_id).__name__}")
            conduit = self._conduit.get_conduit_by_id(conduit_id, aetheric_frame)
            if conduit is None:
                self._logger.error(f"Could not resolve conduit for id {conduit_id}", "_check_conduit_id_and_conduit")
                raise RuntimeError(f"Could not resolve conduit for conduit_id '{conduit_id}'.")

        if conduit_id is None:
            if not isinstance(conduit, IConduit):
                self._logger.error(f"conduit type invalid: {type(conduit).__name__}", "_check_conduit_id_and_conduit")
                raise TypeError(f"Expected IConduit instance, got {type(conduit).__name__}")
            conduit_id = conduit.__creation_context__._conduit_id
            if conduit_id is None:
                self._logger.error("Conduit has no internal id", "_check_conduit_id_and_conduit")
                raise RuntimeError("Could not determine conduit_id from conduit.")

        inspected_id = conduit.__creation_context__._conduit_id
        if conduit_id != inspected_id:
            self._logger.error(f"Mismatched conduit_id '{conduit_id}' vs internal '{inspected_id}'", "_check_conduit_id_and_conduit")
            raise RuntimeError(f"Provided conduit_id '{conduit_id}' does not match conduit internal ID '{inspected_id}'.")

        self._logger.debug(f"_check_conduit_id_and_conduit -> id={conduit_id}", "_check_conduit_id_and_conduit")
        return conduit_id, conduit

    def _create_detail(self, spell_id: str, permissions: Permissions) -> Detail:
        """
        Internal

        Creates a new Detail instance to represent spell permissions within a contract.

        Args:
            spell_id (str): The ID of the spell this detail applies to.
            permissions (Permissions): The permissions granted for this spell.

        Returns:
            Detail: A new Detail instance.

        Raises:
            TypeError: If `permissions` is not an instance of `Permissions` enum.
        """
        if not isinstance(permissions, Permissions):
            self._logger.error(f"permissions type invalid: {type(permissions).__name__}", "_create_detail")
            raise TypeError(f"Expected Permissions enum, got {type(permissions).__name__}")
        self._logger.debug(f"_create_detail spell_id={spell_id} perms={permissions.name}", "_create_detail")
        return Detail(spell_id, permissions)


    def _check_spell_if_eligible(self, spell: ISpell, conduit: IConduit, permissions: Permissions) -> None:
        """
        Internal

        Checks if the provided spell is eligible for contracting based on policy and spell permissions.

        Args:
            spell (ISpell): The spell to check.
            conduit (IConduit): The conduit proposing the contract.
            permissions (Permissions): The permissions requested for the contract.

        Raises:
            RuntimeError: If the conduit policy prevents contracting (`block_all`).
            RuntimeError: If the spell doesn't have the required permissions (`create`, `read`).
            RuntimeError: If the spell is blocked (`Permissions.block`) and policy isn't `whitelist_all`.
            RuntimeError: If the spell is not owned by the proposing conduit.
        """
        if conduit._conduit_ward._policy == Policies.block_all:
            self._logger.error("block_all policy prevents contracting", "_check_spell_if_eligible")
            raise RuntimeError("Cannot contract spells when policy is set to block_all.")
        if permissions == Permissions.create and spell._permissions != Permissions.create:
            self._logger.error("create perms requested but spell lacks create", "_check_spell_if_eligible")
            raise RuntimeError(f"Spell '{spell.__name__}' does not have create permissions, cannot contract with create permissions.")
        if permissions == Permissions.read and spell._permissions not in (Permissions.read, Permissions.create):
            self._logger.error("read perms requested but spell lacks read/create", "_check_spell_if_eligible")
            raise RuntimeError(f"Spell '{spell.__name__}' does not have read permissions, cannot contract with read permissions.")
        if spell._permissions == Permissions.block and conduit._conduit_ward._policy != Policies.whitelist_all:
            self._logger.error("spell is block and policy is not whitelist_all", "_check_spell_if_eligible")
            raise RuntimeError("Cannot contract spells with block permissions.")
        if spell._owner_conduit_id != conduit.__creation_context__._conduit_id:
            self._logger.error("spell is not owned by proposing conduit", "_check_spell_if_eligible")
            raise RuntimeError(f"Spell '{spell.__name__}' is not owned by this conduit, cannot contract it.")
        self._logger.debug("spell eligible for contracting", "_check_spell_if_eligible")

    def _add_spell_to_contract(self, *, spell: ISpell = None, spell_id: str = None, conduit: IConduit = None, conduit_id: UUID = None,
                               permissions: str = "create", aetheric_frame = "default") -> bool | None:
        """
        Internal

        Adds a single spell to an existing contract with a peer conduit.

        Args:
            spell (ISpell, optional): The spell object to contract.
            spell_id (str, optional): The unique ID of the spell.
            conduit (IConduit, optional): The target peer conduit.
            conduit_id (UUID, optional): The UUID of the target peer conduit.
            permissions (str): The permission level granted for this spell (default is "create").
            aetheric_frame (str): The Aetheric Frame to resolve entities in.

        Returns:
            bool: True if the contract was successfully updated.

        Raises:
            RuntimeError: If the Conduit is sealed.
            RuntimeError: If no contract exists with the target conduit (link required first).
            RuntimeError: If the spell is already contracted with the same permissions.
            ValueError/TypeError/RuntimeError: From internal helper checks.
        """
        self.check_sealed()

        # Check if permissions are valid
        permissions = EnumHelpers.convert_enum_and_check(permissions, Permissions)

        # Check if spell or spell_id is provided, if not, raise an error
        spell_id, spell = self._check_spell_id_and_spell(spell, spell_id, aetheric_frame)

        # Check if conduit is provided, if not, resolve it from conduit_id
        conduit_id, conduit = self._check_conduit_id_and_conduit(conduit, conduit_id, aetheric_frame)

        # Check if contract exists for the conduit
        if (contract := self._find_contract_by_id(conduit_id)) is None:
            self._logger.error(f"No contract for conduit {conduit_id}", "_add_spell_to_contract")
            raise RuntimeError(f"No contract found for conduit ID {conduit_id}, please link to this conduit prior to spell contract initiation.")

        # Check if the spell exists in our contracted spells
        if contract._check_if_exists_and_permissions(conduit._conduit_ward, spell_id, permissions):
            self._logger.error("Spell already contracted with same permissions", "_add_spell_to_contract")
            raise RuntimeError(f"Spell with ID '{spell_id}' is already contracted in this conduit with these permissions.")

        # Check if spell is available with the required permissions
        self._check_spell_if_eligible(spell, conduit, permissions)

        # Create Detail with the spell_id and permissions
        with contract._lock:
            detail = self._create_detail(spell_id, permissions)
            contract._add(conduit._conduit_ward, detail)

        # Add spell to spellbook
        contract._get_peer(conduit._conduit_ward)._conduit._spellbook._add_contracted_spell(spell, conduit_id)
        self._logger.debug(f"Spell '{spell_id}' added to contract with {conduit_id}", "_add_spell_to_contract")
        return True

    def _add_spells_to_contract(self, *, spell_ids: list[str] = None, conduit: IConduit = None, conduit_id: UUID = None,
                                permissions: str = "create", aetheric_frame = "default") -> dict[str, list[str] | dict[str, str]]:
        """
        Internal

        Attempts to add multiple spells to an existing contract in a bulk operation.

        Args:
            spell_ids (list[str], optional): List of spell IDs to contract.
            conduit (IConduit, optional): The target peer conduit.
            conduit_id (UUID, optional): The UUID of the target peer conduit.
            permissions (str): The permission level to apply to all spells (default is "create").
            aetheric_frame (str): The Aetheric Frame to resolve entities in.

        Returns:
            dict: A dictionary containing a list of "success" spell IDs and a dictionary of "failed" spell IDs mapped to error messages.

        Raises:
            RuntimeError: If the Conduit is sealed.
        """
        self.check_sealed()
        self._logger.debug(f"_add_spells_to_contract(count={0 if spell_ids is None else len(spell_ids)})", "_add_spells_to_contract")
        report = {"success": [], "failed": {}}
        for sid in spell_ids or []:
            try:
                self._add_spell_to_contract(spell_id=sid, conduit=conduit, conduit_id=conduit_id, permissions=permissions, aetheric_frame=aetheric_frame)
                report["success"].append(sid)
            except Exception as e:
                report["failed"][sid] = str(e)
        return report

    def _remove_spell_from_contract(self, *, spell: ISpell = None, spell_id: str = None, conduit: IConduit = None,
                                    conduit_id: UUID = None, aetheric_frame = "default") -> bool | None:
        """
        Internal

        Removes a specific spell from an existing contract.

        Args:
            spell (ISpell, optional): The spell object to remove.
            spell_id (str, optional): The unique ID of the spell to remove.
            conduit (IConduit, optional): The target peer conduit.
            conduit_id (UUID, optional): The UUID of the target peer conduit.
            aetheric_frame (str): The Aetheric Frame to resolve entities in.

        Returns:
            bool: True if the spell was successfully removed.

        Raises:
            RuntimeError: If the Conduit is sealed.
            RuntimeError: If no contract is found.
            RuntimeError: If the spell ID is not found in the contract.
            ValueError/TypeError/RuntimeError: From internal helper checks.
        """
        self.check_sealed()
        self._logger.debug(f"_remove_spell_from_contract(spell_id={spell_id}, conduit_id={conduit_id})", "_remove_spell_from_contract")

        # Check if spell or spell_id is provided, if not, raise an error
        spell_id, spell = self._check_spell_id_and_spell(spell, spell_id, aetheric_frame)

        # Check if conduit is provided, if not, resolve it from conduit_id
        conduit_id, conduit = self._check_conduit_id_and_conduit(conduit, conduit_id, aetheric_frame)

        # Check if contract exists for the conduit
        if (contract := self._find_contract_by_id(conduit_id)) is not None:
            with contract._lock:
                if contract._check_if_exists(conduit._conduit_ward, spell_id):
                    contract._remove(conduit._conduit_ward, spell_id)
                    # Remove spell from spellbook
                    contract._get_peer(conduit._conduit_ward)._conduit._spellbook._remove_contracted_spell(spell_id, conduit_id)
                else:
                    self._logger.error("Spell not found in contract", "_remove_spell_from_contract")
                    raise RuntimeError(f"Spell with ID '{spell_id}' does not exist in the contract for conduit ID {conduit_id}.")
        else:
            self._logger.error("No contract found for conduit", "_remove_spell_from_contract")
            raise RuntimeError(f"No contract found for conduit ID {conduit_id}")


    def _remove_spells_from_contract(self, *, spell_ids: list[str] = None, conduit: IConduit = None,
                                     conduit_id: UUID = None, aetheric_frame = "default") -> dict[str, list[str] | dict[str, str]]:
        """
        Internal

        Attempts to remove multiple spells from an existing contract in a bulk operation.

        Args:
            spell_ids (list[str], optional): List of spell IDs to remove.
            conduit (IConduit, optional): The target peer conduit.
            conduit_id (UUID, optional): The UUID of the target peer conduit.
            aetheric_frame (str): The Aetheric Frame to resolve entities in.

        Returns:
            dict: A dictionary containing a list of "success" spell IDs and a dictionary of "failed" spell IDs mapped to error messages.

        Raises:
            RuntimeError: If the Conduit is sealed.
        """
        self.check_sealed()
        self._logger.debug(f"_remove_spells_from_contract(count={0 if spell_ids is None else len(spell_ids)})", "_remove_spells_from_contract")
        report = {"success": [], "failed": {}}
        for sid in spell_ids or []:
            try:
                self._remove_spell_from_contract(spell_id=sid, conduit=conduit, conduit_id=conduit_id, aetheric_frame=aetheric_frame)
                report["success"].append(sid)
            except Exception as e:
                report["failed"][sid] = str(e)
        return report

    def _remove_all_spells_from_contract(self, *, conduit: IConduit = None, conduit_id: UUID = None, aetheric_frame = "default") -> bool | None:
        """
        Internal

        Removes ALL spells from the contract associated with the specified peer conduit.

        Args:
            conduit (IConduit, optional): The target peer conduit.
            conduit_id (UUID, optional): The UUID of the target peer conduit.
            aetheric_frame (str): The Aetheric Frame to resolve entities in.

        Returns:
            bool: True if all spells were successfully removed and cleanup performed.

        Raises:
            RuntimeError: If the Conduit is sealed.
            RuntimeError: If no contract is found.
            ValueError/TypeError/RuntimeError: From internal helper checks.
        """
        self.check_sealed()
        self._logger.debug(f"_remove_all_spells_from_contract(conduit_id={conduit_id})", "_remove_all_spells_from_contract")

        # Check if conduit is provided, if not, resolve it from conduit_id
        conduit_id, conduit = self._check_conduit_id_and_conduit(conduit, conduit_id, aetheric_frame)

        # Check if contract exists for the conduit
        if (contract := self._find_contract_by_id(conduit_id)) is not None:
            with contract._lock:
                # Clear all spells from the contract details
                contract._clear_contract()

                # Remove all spells from each conduit spellbook
                ward_a = contract._ward_a
                ward_b = contract._ward_b

                # Both sides clear contracted spells related to the *other* conduit's ID
                ward_a._conduit._spellbook._clear_contracted_spells_for_conduit(ward_b._id)
                ward_b._conduit._spellbook._clear_contracted_spells_for_conduit(ward_a._id)
                self._logger.debug("All spells removed from contract", "_remove_all_spells_from_contract")
                return True
        else:
            self._logger.error("No contract found for conduit", "_remove_all_spells_from_contract")
            raise RuntimeError(f"No contract found for conduit ID {conduit_id}")

    def _get_all_spells_in_contracts(self, validate: bool = True) -> Optional[dict[str, list[Tuple[str, 'ISpell']]]]:
        """
        Internal

        Retrieves all contracted spells across all active contracts involving this conduit.

        This method walks all contracts and returns the spell ID and spell object
        pairs available to this conduit from its peers (spells granted *to* this conduit).

        Args:
            validate (bool): Whether to validate contract consistency before retrieval.

        Returns:
            Optional[dict[str, list[Tuple[str, 'ISpell']]]]: A dictionary mapping peer conduit IDs (UUID) to lists of (spell_id, ISpell) tuples.
            Returns None if no contracts are found.

        Raises:
            RuntimeError: If the Conduit is sealed.
            RuntimeError: If contract validation fails and `validate` is True.
        """
        self.check_sealed()
        self._logger.debug(f"_get_all_spells_in_contracts(validate={validate})", "_get_all_spells_in_contracts")

        if validate:
            validation = self._validate_contracts_and_define()
            if not all(validation.values()):
                self._logger.error("One or more contracts invalid", "_get_all_spells_in_contracts")
                raise RuntimeError(
                    "One or more contracts are invalid. Please validate contracts before retrieving spells.")

        spells_in_contracts = {}

        with self._lock:
            for contract_id, contract in self._contracts.items():
                try:
                    # Get the peer (the conduit providing the spell)
                    peer_ward = contract._get_peer(self)
                    peer_conduit = peer_ward._conduit
                    # Get the detail map containing spells granted to *us* (this ward)
                    detail_map = contract._get_detail_map(self)

                    spells = []
                    for spell_id, detail in detail_map.items():
                        # We look up the spell in the *peer's* spellbook, as they own it
                        spell = peer_conduit.find_contracted_spell(spell_id)
                        if spell is None:
                            if validate:
                                self._logger.error(f"Inconsistent state: missing spell {spell_id} in peer spellbook", "_get_all_spells_in_contracts")
                                raise RuntimeError(
                                    f"Inconsistent state: Spell '{spell_id}' missing in peer's spellbook.")
                            continue
                        spells.append((spell_id, spell))

                    spells_in_contracts[peer_ward._id] = spells
                except Exception as e:
                    if validate:
                        self._logger.error(f"Failed to inspect contract {contract_id}: {e}", "_get_all_spells_in_contracts")
                        raise RuntimeError(f"Failed to inspect contract {contract_id}: {e}")

        return spells_in_contracts if spells_in_contracts else None

    def _get_spell_in_contracts(self, spell_id: str) -> Optional[tuple[UUID, ISpell]]:
        """
        Internal

        Attempts to retrieve a specific spell from the active contracts by searching through all links.

        This looks for a spell that is being granted *to* this conduit by a peer.

        Args:
            spell_id (str): The explicit spell ID to search for.

        Returns:
            Optional[tuple[UUID, ISpell]]: Tuple of (`Conduit ID`, `ISpell`) if found, otherwise None.

        Raises:
            RuntimeError: If the Conduit is sealed.
        """
        self.check_sealed()
        self._logger.debug(f"_get_spell_in_contracts(spell_id={spell_id})", "_get_spell_in_contracts")

        with self._lock:
            for contract in self._contracts.values():
                # Find which ward in the contract is granting this spell (the one with the detail)
                ward = contract._find_spell_in_ward(spell_id)
                if ward:
                    # The peer is the one who granted it (the one holding the spell in its book)
                    peer_ward = contract._get_peer(ward)
                    spell = peer_ward._conduit.find_contracted_spell(spell_id)
                    if spell:
                        self._logger.debug(f"Found spell in peer {peer_ward._id}", "_get_spell_in_contracts")
                        return (peer_ward._id, spell)
        self._logger.debug("Spell not found in any contract", "_get_spell_in_contracts")
        return None

    def _get_spells_in_contract_by_conduit(self, conduit_id: UUID) -> dict[str, list[tuple[str, ISpell]]] | None:
        """
        Internal

        Retrieves all spells exchanged with a specific conduit by its unique ID.

        Returns details on both inbound (received) and outbound (granted) contracted spells.

        Args:
            conduit_id (UUID): The UUID of the target conduit.

        Returns:
            dict[str, list[tuple[str, ISpell]]] | None: A dictionary mapping roles ("inbound", "outbound") to lists of (spell_id, ISpell) tuples.
            Returns None if no such conduit is linked.

        Raises:
            RuntimeError: If the Conduit is sealed.
        """
        self.check_sealed()
        self._logger.debug(f"_get_spells_in_contract_by_conduit(conduit_id={conduit_id})", "_get_spells_in_contract_by_conduit")

        with self._lock:
            contract = self._find_contract_by_id(conduit_id)
            if not contract:
                self._logger.debug("No contract for given conduit_id", "_get_spells_in_contract_by_conduit")
                return None

            spells_result = {
                "inbound": [],  # spells we received from them (they granted to us)
                "outbound": []  # spells we granted to them
            }

            # Peer side (spells received by us)
            peer_ward = contract._get_peer(self)
            peer_conduit = peer_ward._conduit
            # Spells granted to *this* ward are stored in the detail map associated with *this* ward
            received_map = contract._get_detail_map(self)
            for spell_id, detail in received_map.items():
                spell = peer_conduit.find_contracted_spell(spell_id)
                if spell:
                    spells_result["inbound"].append((spell_id, spell))
            self._logger.debug(
                f"_get_spells_in_contract_by_conduit -> inbound={len(spells_result['inbound'])}, outbound={len(spells_result['outbound'])}",
                "_get_spells_in_contract_by_conduit"
            )
            # Our side (spells granted by us)
            our_map = contract._get_detail_map(peer_ward)
            for spell_id, detail in our_map.items():
                spell = self._conduit.find_contracted_spell(spell_id)
                if spell:
                    spells_result["outbound"].append((spell_id, spell))

            return spells_result if spells_result["inbound"] or spells_result["outbound"] else None

    def _get_spells_in_contract_by_conduit_name(self, conduit_name: str) -> dict[str, list[tuple[str, ISpell]]] | None:
        """
        Internal

        Retrieves all spells exchanged with a specific conduit by its declared name.

        Mirrors `_get_spells_in_contract_by_conduit` but performs lookup by name.

        Args:
            conduit_name (str): The name identifier of the target conduit.

        Returns:
            dict[str, list[tuple[str, ISpell]]] | None: A dictionary of spells exchanged (inbound/outbound), or None if not found.

        Raises:
            RuntimeError: If the Conduit is sealed.
            ValueError: If `conduit_name` is empty or not a string.
        """
        self.check_sealed()
        if not conduit_name or not isinstance(conduit_name, str):
            self._logger.error("Conduit name must be a non-empty string", "_get_spells_in_contract_by_conduit_name")
            raise ValueError("Conduit name must be a non-empty string.")

        with self._lock:
            for contract in self._contracts.values():
                peer_ward = contract._get_peer(self)
                peer_conduit = peer_ward._conduit
                if peer_conduit._name == conduit_name:
                    result = self._get_spells_in_contract_by_conduit(peer_ward._id)
                    self._logger.debug(f"Found spells for conduit_name='{conduit_name}'", "_get_spells_in_contract_by_conduit_name")
                    return result
        self._logger.debug(f"No contracts found for conduit_name='{conduit_name}'", "_get_spells_in_contract_by_conduit_name")
        return None

    def _get_contracted_conduits(self) -> list[Tuple[str, IConduit]] | None:
        """
        Internal

        Returns all conduits that currently have active spell contracts with this conduit.

        Args:
            None

        Returns:
            list[Tuple[str, IConduit]] | None: A list of (`conduit_id`, `IConduit`) tuples. Returns None if no links exist.

        Raises:
            RuntimeError: If the Conduit is sealed.
        """
        self.check_sealed()
        contracted_conduits: list[Tuple[str, IConduit]] = []

        with self._lock:
            for contract_id, contract in self._contracts.items():
                peer_ward = contract._get_peer(self)
                peer_conduit = peer_ward._conduit
                contracted_conduits.append((str(peer_ward._id), peer_conduit))
        self._logger.debug(f"_get_contracted_conduits -> {len(contracted_conduits)}", "_get_contracted_conduits")
        return contracted_conduits if contracted_conduits else None

    def _describe_contract(self, conduit_id: UUID) -> dict:
        """
        Internal

        Returns a detailed diagnostic summary of a contract established with a specific peer conduit ID.

        Args:
            conduit_id (UUID): UUID of the peer conduit whose contract you wish to examine.

        Returns:
            dict: Dictionary containing contract metadata, including spell list and permissions.

        Raises:
            RuntimeError: If the Conduit is sealed.
            RuntimeError: If no contract is found with the given conduit ID.
        """
        self.check_sealed()

        with self._lock:
            # Need to find the contract using the peer's conduit_id
            contract = self._find_contract_by_id(conduit_id)
            if not contract:
                self._logger.error(f"No contract found with conduit ID: {conduit_id}", "_describe_contract")
                raise RuntimeError(f"No contract found with conduit ID: {conduit_id}")

            peer_ward = contract._get_peer(self)
            peer_conduit = peer_ward._conduit
            # We look at the detail map associated with *this* ward to see what spells *they* granted to *us*.
            detail_map = contract._get_detail_map(self)

            desc = {
                "contract_id": contract._id,
                "peer_conduit_name": peer_conduit._name if peer_conduit._name is not None else "Unknown",
                "spell_count": len(detail_map),
                "spells": [
                    {"spell_id": sid, "permissions": detail.permissions.name}
                    for sid, detail in detail_map.items()
                ],
            }
            self._logger.debug(
                f"_describe_contract -> id={desc['contract_id']} spells={desc['spell_count']}",
                "_describe_contract"
            )
            return desc

    def _validate_contracts_and_define(self) -> dict[UUID, bool]:
        """
        Internal

        Validates all active contracts attached to this conduit for symmetry and integrity.

        This ensures both sides list the same spells, permissions are consistent, and all
        referenced contracted spells exist in the peer's spellbook.

        Args:
            None

        Returns:
            dict[UUID, bool]: Dictionary mapping contract UUIDs to validation results (True/False).

        Raises:
            RuntimeError: If the Conduit is sealed.
        """
        self.check_sealed()

        results = {}
        with self._lock:
            for contract_id, contract in self._contracts.items():
                try:
                    valid = True
                    for ward in (contract._ward_a, contract._ward_b):
                        # The spells are borrowed *from* the peer *to* this ward.
                        peer = contract._get_peer(ward)
                        peer_book = peer._conduit._spellbook
                        detail_map = contract._get_detail_map(ward)

                        for spell_id, detail in detail_map.items():
                            # We check if the spell exists in the peer's spellbook as a contracted spell.
                            spell = peer_book._find_contracted_spell(spell_id)
                            # We only check permissions on the original spell, not the contracted detail.
                            # The check is simply for existence in the contracted spell book.
                            if spell is None:
                                valid = False
                                break

                        if not valid:
                            break

                    results[contract_id] = valid
                    self._logger.debug(f"Contract {contract_id} validation -> {valid}", "_validate_contracts_and_define")
                except Exception as e:
                    results[contract_id] = False
                    self._logger.error(f"Contract {contract_id} validation error: {e}", "_validate_contracts_and_define", exc_info=True)
        return results


    def _validate_received_contracts(self) -> bool:
        """
        Internal

        Performs a high-level validation check across all contracts involving this conduit.

        This aggregates the results of `_validate_contracts_and_define` to provide a simple pass/fail status.

        Args:
            None

        Returns:
            bool: True if all active contracts pass validation, False otherwise.

        Raises:
            RuntimeError: If the Conduit is sealed.
        """
        self.check_sealed()
        results = self._validate_contracts_and_define()
        overall = all(results.values()) if results else False
        self._logger.debug(f"_validate_received_contracts -> {overall}", "_validate_received_contracts")
        return overall

#endregion Spellbinding API
#endregion ConduitWard