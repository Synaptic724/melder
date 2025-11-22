import threading
from typing import List, Optional, Any, Tuple

# Melder Imports
from melder.aether.conduit.conduit_ward.contract.contract_types.contract_types import ContractTypes
from melder.utilities.general_base.cleanable import Cleanable
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.utilities.data_structures.concurrent_dict import ConcurrentDict
from melder.utilities.helpers.general_helpers import EnumHelpers
from melder.utilities.interfaces.interfaces import IConduit, IConduitWard, ISpell, ISafeLogger, IConfiguration
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.contract.contract import Detail, Contract


# TODO: Ensure that links properly connect to the spell and its dependencies not just the spell itself.
# TODO: If a specific policy is set such as blacklist or whitelist, ensure that the spellbook the entire spellbook is managed properly.

##### IMPORTANT NOTE #####
# TODO: Remember that this entire system is revolved around dynamic spell management. If a core scope that everyone is borrowing from is disposed, how can we handle that situation?


#region ConduitWard
class ConduitWard(Cleanable, IConduitWard):
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
    def __init__(self, conduit: IConduit, dynamic: bool, conduit_type: ConduitState, policy: Policies, configuration: IConfiguration):
        super().__init__()
        self._lock: threading.RLock  = threading.RLock()

        ## Conduit Ward properties
        self._conduit: IConduit = conduit
        self._logger: ISafeLogger = conduit._logger
        self._dynamic: bool = dynamic
        self._conduit_type: ConduitState = conduit_type
        self._configuration: IConfiguration = configuration
        self._id = conduit._id
        self._display_name: str = self.__class__.__name__
        self._log_groups = ["spell_management", "spells"]
        self._log_sysgroups = ["conduit"]

        self._policy_set: bool = False
        # Contracts between conduits
        self._initiated_index: ConcurrentDict[str, str] = ConcurrentDict()  # [Target ConduitID] -> [ContractID]
        self._received_index: ConcurrentDict[str, str] = ConcurrentDict()  # [Source ConduitID] -> [ContractID]

        self._contracts: ConcurrentDict[str, Contract] = ConcurrentDict() # [ContractID] -> Contract

        # Lineage Links
        self._parent_conduit: IConduit | None = None
        self._lesser_conduits: ConcurrentDict[str, IConduit] = ConcurrentDict() # [Lesser ConduitID] -> Lesser Conduit

        try:
            self._policy = self._set_initial_policy(policy)
            self._logger.debug(
                f"ConduitWard init id={self._id} type={self._conduit_type.name} dynamic={self._dynamic}",
                method_name="__init__",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
        except Exception as e:
            self._logger.error(
                f"ConduitWard init failed: {e}",
                method_name="__init__", exc_info=True,
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise

    #region Cleanup
    def cleanup(self):
        """
        Public API

        Cleanups the conduit ward, preventing any further modifications or operations.
        """
        raise NotImplementedError("Cleaning is not implemented yet.")
        if self._cleaned:
            return
        with self._lock:
            self._logger.debug(
                "cleanup start",
                method_name="cleanup",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            self._clean_up_links()
            self._clean_up_lesser_conduits_links()
            self._conduit = None
            self._dynamic = None
            self.sever_link(self._parent_conduit_link)
            self._conduit_type = self._conduit_type.cleaned
            self._policy = None
            self._cleaned = True
            self._logger.info(
                "cleanup complete",
                method_name="cleanup",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )

            if self._logger is not None:
                self._display_name: str = ""
                self._log_groups.clear()
                self._log_groups = None
                self._log_sysgroups.clear()
                self._log_sysgroups = None
                self._logger = None


    def _clean_up_lesser_conduits_links(self):
        """
        Internal

        Recursively cleans up and removes all linked lesser conduits (children).
        """
        raise NotImplementedError("is not implemented yet.")
        if self._lesser_conduits_links:
            for lesser_conduit in self._lesser_conduits_links:
                try:
                    lesser_conduit.cleanup()
                except Exception as e:
                    self._logger.error(
                        f"cleanup lesser link failed: {e}",
                        method_name="_clean_up_lesser_conduits_links", exc_info=True,
                        owner_id=self._id, owner_display=self._display_name,
                        mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                    )
            self._lesser_conduits_links.dispose()
        self._logger.debug(
            "_clean_up_lesser_conduits_links done",
            method_name="_clean_up_lesser_conduits_links",
            owner_id=self._id, owner_display=self._display_name,
            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
        )

    def _clean_up_links(self):
        """
        Internal

        cleans and disposes of all active external contracts and links.
        """
        raise NotImplementedError("is not implemented yet.")
        if self._conduit_links:
            for link in self._conduit_links:
                try:
                    link.cleanup()
                except Exception as e:
                    self._logger.error(
                        f"cleanup link failed: {e}",
                        method_name="_clean_up_links", exc_info=True,
                        owner_id=self._id, owner_display=self._display_name,
                        mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                    )
            self._conduit_links.dispose()
        self._logger.debug(
            "_clean_up_links done",
            method_name="_clean_up_links",
            owner_id=self._id, owner_display=self._display_name,
            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
        )


    def cleanup_all_lesser_conduits(self) -> None:
        """
        Public API

        Cleans up all lesser conduits (children) linked to this conduit.

        This is typically used when the parent conduit is undergoing a state change,
        like an upgrade to a normal state, or as part of a controlled shutdown.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        raise NotImplementedError("is not implemented yet.")
        self._logger.debug(
            "cleanup_all_lesser_conduits",
            method_name="cleanup_all_lesser_conduits",
            owner_id=self._id, owner_display=self._display_name,
            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
        )
        with self._lock:
            for conduit in self._lesser_conduits.values():
                try:
                    conduit.cleanup()
                except Exception as e:
                    self._logger.error(
                        f"lesser cleanup failed: {e}",
                        method_name="cleanup_all_lesser_conduits", exc_info=True,
                        owner_id=self._id, owner_display=self._display_name,
                        mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                    )
            self._lesser_conduits.clear()
        self._logger.info(
            "cleanup_all_lesser_conduits complete",
            method_name="cleanup_all_lesser_conduits",
            owner_id=self._id, owner_display=self._display_name,
            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
        )
    #endregion Cleanup

    #region Context Manager
    def __enter__(self):
        """
        Enters the context manager for Aether.
        """
        self._lock.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exits the context manager for Aether.
        """
        self._lock.release()

    #endregion Context Manager
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
        self.check_cleaned()
        if self._conduit_type != ConduitState.lesser:
            self._logger.error(
                "convert_to_normal: not a lesser conduit",
                method_name="_convert_to_normal_conduit",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise RuntimeError("Conduit is not a lesser conduit.")
        with self._lock:
            if not self._dynamic:
                self._logger.error(
                    "convert_to_normal: non-dynamic env",
                    method_name="_convert_to_normal_conduit",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                raise RuntimeError("Dynamic environment is not enabled. Cannot upgrade to normal conduit.")
            if self._parent_conduit is not None and self._conduit_type == ConduitState.lesser and len(self._lesser_conduits) == 0:
                self._parent_conduit = None
                self._conduit_type = ConduitState.normal
                self._policy = Policies.dynamic
                self._logger.info(
                    "convert_to_normal: success",
                    method_name="_convert_to_normal_conduit",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
            else:
                self._logger.error(
                    "convert_to_normal: missing parent link or children present",
                    method_name="_convert_to_normal_conduit",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
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
        self.check_cleaned()

        if policy is not None:
            if not isinstance(policy, Policies):
                self._logger.error(
                    f"set_initial_policy: wrong type {type(policy).__name__}",
                    owner_id=self._id, owner_display=self._display_name,
                    method_name="_set_initial_policy",
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                raise TypeError(f"Expected Policies enum instance, got {type(policy).__name__}")
            self._policy_set = True
            self._logger.debug(
                f"set_initial_policy -> {policy.name}",
                method_name="_set_initial_policy",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            return policy

        with self._lock:
            if self._conduit_type == ConduitState.lesser:
                self._logger.debug(
                    "set_initial_policy -> lesser_conduit",
                    method_name="_set_initial_policy",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                return Policies.lesser_conduit
            else:
                self._logger.error(
                    "set_initial_policy called after policy already set or invalid state",
                    method_name="_set_initial_policy",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                raise RuntimeError("Policy already set. Cannot set policy again.")

    def _set_new_policy(self, policy: str | Policies) -> None:
        """
        Internal

        Sets a new operational policy for this Conduit.

        This is restricted to `normal` conduits in dynamic mode.

        Args:
            policy (str | Policies): The new policy to set.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If dynamic environment is not enabled.
            RuntimeError: If the Conduit is a lesser Conduit.
            RuntimeError: If attempting to set to `automatic` in dynamic mode.
            RuntimeError: If attempting to set to `lesser_conduit` on a non-lesser Conduit.
            RuntimeError: If attempting to set to `block_all` or `whitelist_all` while contracts exist.
        """
        self.check_cleaned()
        if not self._dynamic:
            self._logger.error(
                "set_new_policy: non-dynamic env",
                method_name="_set_new_policy",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise RuntimeError("Dynamic environment is not enabled. Cannot set policy.")
        if self._conduit_type == ConduitState.lesser:
            self._logger.error(
                "set_new_policy: on lesser conduit",
                method_name="_set_new_policy",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise RuntimeError("Cannot set policy on a lesser Conduit. Convert to a normal Conduit first.")

        with self._lock:
            new_policy = EnumHelpers.convert_enum_and_check(policy, Policies)
            if new_policy == Policies.automatic:
                self._logger.error(
                    "set_new_policy: automatic in dynamic env is invalid",
                    method_name="_set_new_policy",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                raise RuntimeError("Cannot set policy to 'automatic' in dynamic mode.")
            if new_policy == Policies.lesser_conduit and self._conduit_type != ConduitState.lesser:
                self._logger.error(
                    "set_new_policy: lesser_conduit on non-lesser",
                    method_name="_set_new_policy",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                raise RuntimeError("Cannot set policy to 'lesser_conduit' on a non-lesser Conduit.")
            if (new_policy == Policies.block_all or new_policy == Policies.whitelist_all) and len(self._contracts) > 0:
                self._logger.error(
                    "set_new_policy: block/whitelist with existing contracts",
                    method_name="_set_new_policy",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                raise RuntimeError("Cannot set policy to 'block_all' or 'whitelist_all' when there are existing contracts.")
            self._policy = new_policy
            self._logger.info(
                f"set_new_policy -> {self._policy.name}",
                method_name="_set_new_policy",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )

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
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If attempting to link to a lesser conduit.
            RuntimeError: If attempting to link a conduit to itself.
            RuntimeError: If dynamic environment is not enabled.
        """
        self.check_cleaned()
        if target_conduit._conduit_state == ConduitState.lesser:
            self._logger.error(
                "link: target is lesser conduit",
                method_name="_link",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise RuntimeError("Cannot link to a lesser conduit. Use _link_lesser_conduit instead.")
        if target_conduit._id == self._id:
            self._logger.error(
                "link: self-link attempt",
                method_name="_link",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise RuntimeError("Cannot link a conduit to itself.")
        if not self._dynamic:
            self._logger.error(
                "link: non-dynamic env",
                method_name="_link",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise RuntimeError("Dynamic environment is not enabled. Cannot link conduits.")

        if target_conduit._conduit_state == ConduitState.normal:
            if self._find_contract(target_conduit):
                self._logger.debug(
                    f"link: already linked -> {target_conduit._id}",
                    method_name="_link",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                return True
            self._logger.debug(
                f"link: creating contract -> {target_conduit._id}",
                method_name="_link",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            return self._create_new_contract(target_conduit)

        self._logger.error(
            "link: target not normal",
            method_name="_link",
            owner_id=self._id, owner_display=self._display_name,
            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
        )
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
        locks = sorted([ward_a._lock, ward_b._lock], key=id)
        with locks[0]:
            with locks[1]:
                target_id = target_conduit._id
                if self._find_contract(target_conduit):
                    self._logger.debug(
                        f"create_contract: already exists -> {target_id}",
                        method_name="_create_new_contract",
                        owner_id=self._id, owner_display=self._display_name,
                        mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                    )
                    return True

                contract = Contract(self, ward_b)
                self._contracts[contract._id] = contract
                ward_b._contracts[contract._id] = contract
                self._initiated_index[target_id] = contract._id
                ward_b._received_index[self._id] = contract._id

                try:
                    # Each side needs a contracted-spell bucket keyed by its peer's conduit id.
                    self._conduit._spellbook._create_link_contract(target_id)
                    ward_b._conduit._spellbook._create_link_contract(self._id)
                except Exception as e:
                    self._logger.error(
                        f"spellbook link create failed: {e}",
                        method_name="_create_new_contract", exc_info=True,
                        owner_id=self._id, owner_display=self._display_name,
                        mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                    )
                    raise

                self._logger.info(
                    f"create_contract: success id={contract._id} target={target_id}",
                    method_name="_create_new_contract",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                return True


    def _find_contract_id(self, target_conduit: IConduit) -> Optional[str]:
        """
        Internal

        Finds a contract ID associated with the specified target conduit.

        Args:
            target_conduit (IConduit): The target conduit to find the contract for.

        Returns:
            Optional[str]: The ID of the found contract or None if not found.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            TypeError: If `target_conduit` is not an `IConduit` instance.
        """
        self.check_cleaned()
        if not isinstance(target_conduit, IConduit):
            self._logger.error(
                f"find_contract_id: target not IConduit ({type(target_conduit).__name__})",
                method_name="_find_contract_id",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise TypeError(f"Expected IConduit instance, got {type(target_conduit).__name__}")
        initiated_contract = self._initiated_index.get(target_conduit._conduit_ward._id, None)
        received_contract = self._received_index.get(target_conduit._conduit_ward._id, None)
        cid = initiated_contract if initiated_contract is not None else received_contract
        self._logger.debug(
            f"find_contract_id -> {cid}",
            method_name="_find_contract_id",
            owner_id=self._id, owner_display=self._display_name,
            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
        )
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
            RuntimeError: If the Conduit is cleaned.
            TypeError: If `target_conduit` is not an `IConduit` instance.
        """
        self.check_cleaned()
        if not isinstance(target_conduit, IConduit):
            self._logger.error(
                f"find_contract: target not IConduit ({type(target_conduit).__name__})",
                method_name="_find_contract",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise TypeError(f"Expected IConduit instance, got {type(target_conduit).__name__}")
        peer_id = target_conduit._conduit_ward._id
        contract_id = self._initiated_index.get(peer_id) or self._received_index.get(peer_id)
        contract = self._contracts.get(contract_id)
        self._logger.debug(
            f"find_contract peer={peer_id} -> {'hit' if contract else 'miss'}",
            method_name="_find_contract",
            owner_id=self._id, owner_display=self._display_name,
            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
        )
        return contract

    def _find_contract_by_id(self, conduit_id: str) -> Optional[Contract]:
        """
        Internal

        Finds a contract by the peer's Conduit ID.

        Args:
            conduit_id (str): The ID of the peer conduit in the contract.

        Returns:
            Optional[Contract]: The found contract object or None if not found.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        check_id = self._initiated_index.get(conduit_id) or self._received_index.get(conduit_id)
        contract = self._contracts.get(check_id)
        self._logger.debug(
            f"find_contract_by_id {conduit_id} -> {'hit' if contract else 'miss'}",
            method_name="_find_contract_by_id",
            owner_id=self._id, owner_display=self._display_name,
            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
        )
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
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If no contract is found to sever.
        """
        self.check_cleaned()
        locks = sorted([self._lock, target_conduit._conduit_ward._lock], key=id)
        with locks[0]:
            with locks[1]:
                if self._find_contract(target_conduit):
                    self._logger.debug(
                        f"sever_link -> {target_conduit._id}",
                        method_name="_sever_link",
                        owner_id=self._id, owner_display=self._display_name,
                        mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                    )
                    return self._remove_contract(target_conduit)
                self._logger.error(
                    "sever_link: no contract found",
                    method_name="_sever_link",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
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
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        self._check_conduit_id_and_conduit(conduit=target_conduit)

        if (contract := self._find_contract(target_conduit)) is not None:
            with contract._lock:
                id_a = contract._ward_a._id
                id_b = contract._ward_b._id
                try:
                    contract._ward_a._conduit._spellbook._sever_link_contract(id_b)
                    contract._ward_b._conduit._spellbook._sever_link_contract(id_a)
                except Exception as e:
                    self._logger.error(
                        f"remove_contract spellbook sever failed: {e}",
                        method_name="_remove_contract", exc_info=True,
                        owner_id=self._id, owner_display=self._display_name,
                        mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                    )
                    raise

                try:
                    del self._contracts[contract._id]
                    del target_conduit._conduit_ward._contracts[contract._id]
                except Exception as e:
                    self._logger.error(
                        f"remove_contract registry delete failed: {e}",
                        method_name="_remove_contract", exc_info=True,
                        owner_id=self._id, owner_display=self._display_name,
                        mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                    )
                    raise

                if target_conduit._id in self._initiated_index:
                    del self._initiated_index[target_conduit._id]
                    del target_conduit._conduit_ward._received_index[self._id]
                elif target_conduit._id in self._received_index:
                    del self._received_index[target_conduit._id]
                    del target_conduit._conduit_ward._initiated_index[self._id]

                try:
                    contract.cleanup()
                except Exception as e:
                    self._logger.error(
                        f"contract cleanup failed: {e}",
                        method_name="_remove_contract", exc_info=True,
                        owner_id=self._id, owner_display=self._display_name,
                        mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                    )
                self._logger.info(
                    f"remove_contract: success target={target_conduit._id}",
                    method_name="_remove_contract",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                return True
        self._logger.debug(
            "remove_contract: no-op (no contract)",
            method_name="_remove_contract",
            owner_id=self._id, owner_display=self._display_name,
            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
        )
        return False

    def _link_lesser_conduit(self, lesser_conduit: IConduit):
        """
        Internal

        Links a lesser conduit (child) to this conduit (parent).

        This establishes the parent-child lineage relationship.

        Args:
            lesser_conduit (IConduit): The lesser conduit to link.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        with self._lock:
            self._lesser_conduits[lesser_conduit._id] = lesser_conduit
            lesser_conduit._parent_conduit = self._conduit
        self._logger.info(
            f"link_lesser: {lesser_conduit._id}",
            method_name="_link_lesser_conduit",
            owner_id=self._id, owner_display=self._display_name,
            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
        )

    def _get_lesser_conduit(self, conduit_id: str) -> Optional[IConduit]:
        """
        Internal

        Recursively searches for a lesser conduit with the given ID within this conduit's hierarchy.

        Args:
            conduit_id (str): The ID of the conduit to retrieve.

        Returns:
            Optional[IConduit]: The matched conduit if found, else None.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        for conduit in self._lesser_conduits.values():
            if conduit._id == conduit_id:
                self._logger.debug(
                    f"get_lesser_conduit {conduit_id} -> hit",
                    method_name="_get_lesser_conduit",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                return conduit
            ward = getattr(conduit, "_conduit_ward", None)
            if ward:
                result = ward._get_lesser_conduit(conduit_id)
                if result is not None:
                    self._logger.debug(
                        f"get_lesser_conduit {conduit_id} -> hit (nested)",
                        method_name="_get_lesser_conduit",
                        owner_id=self._id, owner_display=self._display_name,
                        mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                    )
                    return result
        self._logger.debug(
            f"get_lesser_conduit {conduit_id} -> miss",
            method_name="_get_lesser_conduit",
            owner_id=self._id, owner_display=self._display_name,
            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
        )
        return None

    def _get_links(self) -> List[IConduit]:
        """
        Internal

        Returns a combined list of all peer conduits this conduit has contracts with (both initiated and provider).

        Returns:
            List[IConduit]: A list of all linked peer conduits.
        """
        with self._lock:
            initiated = [self._get_initiated_conduit(cid) for cid in self._initiated_index.keys()]
            received = [self._get_provider_conduit(cid) for cid in self._received_index.keys()]
            result = [c for c in initiated + received if c is not None]
        self._logger.debug(
            f"get_links -> {len(result)}",
            method_name="_get_links",
            owner_id=self._id, owner_display=self._display_name,
            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
        )
        return result


    def _get_initiated_conduits(self) -> List[IConduit]:
        """
        Internal

        Retrieves all conduits that this conduit has initiated contracts toward (outbound links).

        Returns:
            List[IConduit]: A list of conduits that this conduit has initiated contracts with.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        result = [
            conduit for conduit_id in self._initiated_index.keys()
            if (conduit := self._get_initiated_conduit(conduit_id)) is not None
        ]
        self._logger.debug(
            f"get_initiated_conduits -> {len(result)}",
            method_name="_get_initiated_conduits",
            owner_id=self._id, owner_display=self._display_name,
            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
        )
        return result


    def _get_provider_conduits(self) -> List[IConduit]:
        """
        Internal

        Retrieves all conduits that have initiated contracts to this conduit (inbound links).

        Returns:
            List[IConduit]: A list of conduits that have linked to this conduit as a provider.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        result = [
            conduit for conduit_id in self._received_index.keys()
            if (conduit := self._get_provider_conduit(conduit_id)) is not None
        ]
        self._logger.debug(
            f"get_provider_conduits -> {len(result)}",
            method_name="_get_provider_conduits",
            owner_id=self._id, owner_display=self._display_name,
            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
        )
        return result

    def _get_initiated_conduit(self, conduit_id: str) -> Optional[IConduit]:
        """
        Internal

        Retrieves the conduit that this conduit has initiated a contract *toward*.

        Args:
            conduit_id (str): The ID of the target conduit this conduit linked to.

        Returns:
            Optional[IConduit]: The target conduit if the link exists, otherwise None.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        if conduit_id in self._initiated_index:
            contract_id = self._initiated_index[conduit_id]
            contract = self._contracts.get(contract_id, None)
            if contract is not None:
                res = contract._ward_b._conduit if conduit_id == contract._ward_b._id else contract._ward_a._conduit
                self._logger.debug(
                    f"get_initiated_conduit {conduit_id} -> {'hit' if res else 'miss'}",
                    method_name="_get_initiated_conduit",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                return res
        self._logger.debug(
            f"get_initiated_conduit {conduit_id} -> miss",
            method_name="_get_initiated_conduit",
            owner_id=self._id, owner_display=self._display_name,
            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
        )
        return None

    def _get_provider_conduit(self, conduit_id: str) -> Optional[IConduit]:
        """
        Internal

        Retrieves the conduit that initiated a contract *to this* conduit.

        Args:
            conduit_id (str): The ID of the source conduit that linked to this one.

        Returns:
            Optional[IConduit]: The source conduit if the link exists, otherwise None.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        if conduit_id in self._received_index:
            contract_id = self._received_index[conduit_id]
            contract = self._contracts.get(contract_id, None)
            if contract is not None:
                res = contract._ward_b._conduit if conduit_id == contract._ward_b._id else contract._ward_a._conduit
                self._logger.debug(
                    f"get_provider_conduit {conduit_id} -> {'hit' if res else 'miss'}",
                    method_name="_get_provider_conduit",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                return res
        self._logger.debug(
            f"get_provider_conduit {conduit_id} -> miss",
            method_name="_get_provider_conduit",
            owner_id=self._id, owner_display=self._display_name,
            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
        )
        return None

    def _sever_all_linked_conduits(self) -> None:
        """
        Internal

        Severs all active peer links (contracts) to conduits. Excludes lesser conduits.
        """
        self.check_cleaned()
        with self._lock:
            self._logger.debug(
                "sever_all_links: not implemented",
                method_name="_sever_all_linked_conduits",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
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
            self._logger.error(
                "check_spell_id_and_spell: neither spell nor spell_id provided",
                method_name="_check_spell_id_and_spell",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise ValueError("Either spell or spell_id must be provided.")

        if spell is None:
            if not isinstance(spell_id, str):
                self._logger.error(
                    f"check_spell_id_and_spell: spell_id wrong type {type(spell_id).__name__}",
                    method_name="_check_spell_id_and_spell",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                raise TypeError(f"Expected spell_id as str, got {type(spell_id).__name__}")
            spell = self._conduit.get_spell_by_id(spell_id, aetheric_frame)
            if spell is None:
                self._logger.error(
                    f"check_spell_id_and_spell: resolve by id failed ({spell_id})",
                    method_name="_check_spell_id_and_spell",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                raise RuntimeError(f"Could not resolve spell for spell_id '{spell_id}'.")

        if spell_id is None:
            if not isinstance(spell, ISpell):
                self._logger.error(
                    f"check_spell_id_and_spell: spell wrong type {type(spell).__name__}",
                    method_name="_check_spell_id_and_spell",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                raise TypeError(f"Expected ISpell instance, got {type(spell).__name__}")
            spell_id = self._conduit.inspect_spell(spell, aetheric_frame)
            if spell_id is None:
                self._logger.error(
                    "check_spell_id_and_spell: inspect spell id failed",
                    method_name="_check_spell_id_and_spell",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                raise RuntimeError("Could not determine spell_id from spell.")

        inspected_id = self._conduit.inspect_spell(spell, aetheric_frame)
        if spell_id != inspected_id:
            self._logger.error(
                f"check_spell_id_and_spell: mismatch provided={spell_id} inspected={inspected_id}",
                method_name="_check_spell_id_and_spell",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise RuntimeError(f"Provided spell_id '{spell_id}' does not match inspected ID '{inspected_id}'.")
        self._logger.debug(
            f"check_spell_id_and_spell -> {spell_id}",
            method_name="_check_spell_id_and_spell",
            owner_id=self._id, owner_display=self._display_name,
            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
        )
        return spell_id, spell


    def _check_conduit_id_and_conduit(self,
                                      conduit: IConduit = None,
                                      conduit_id: str = None, aetheric_frame = "default") -> Tuple[str, IConduit]:
        """
        Internal

        Validation and resolution helper: ensures both a conduit ID and its corresponding conduit object are available.

        Args:
            conduit (IConduit, optional): The target conduit object.
            conduit_id (str, optional): The unique ID of the target conduit.
            aetheric_frame (str): The Aetheric Frame to search within.

        Returns:
            Tuple[str, IConduit]: The resolved (conduit_id, conduit) pair.

        Raises:
            ValueError: If neither `conduit` nor `conduit_id` is provided.
            TypeError: If types are incorrect.
            RuntimeError: If the conduit cannot be resolved or if IDs mismatch.
        """
        if conduit is None and conduit_id is None:
            self._logger.error(
                "check_conduit_id_and_conduit: neither provided",
                method_name="_check_conduit_id_and_conduit",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise ValueError("Either conduit or conduit_id must be provided.")

        if conduit is None:
            if not isinstance(conduit_id, str):
                self._logger.error(
                    f"check_conduit_id_and_conduit: conduit_id wrong type {type(conduit_id).__name__}",
                    method_name="_check_conduit_id_and_conduit",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                raise TypeError(f"Expected conduit_id as str, got {type(conduit_id).__name__}")
            conduit = self._conduit.get_conduit_by_id(conduit_id, aetheric_frame)
            if conduit is None:
                self._logger.error(
                    f"check_conduit_id_and_conduit: resolve by id failed ({conduit_id})",
                    method_name="_check_conduit_id_and_conduit",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                raise RuntimeError(f"Could not resolve conduit for conduit_id '{conduit_id}'.")

        if conduit_id is None:
            if not isinstance(conduit, IConduit):
                self._logger.error(
                    f"check_conduit_id_and_conduit: conduit wrong type {type(conduit).__name__}",
                    method_name="_check_conduit_id_and_conduit",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                raise TypeError(f"Expected IConduit instance, got {type(conduit).__name__}")
            conduit_id = conduit._id
            if conduit_id is None:
                self._logger.error(
                    "check_conduit_id_and_conduit: conduit has no id",
                    method_name="_check_conduit_id_and_conduit",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                raise RuntimeError("Could not determine conduit_id from conduit.")

        inspected_id = conduit._id
        if conduit_id != inspected_id:
            self._logger.error(
                f"check_conduit_id_and_conduit: mismatch provided={conduit_id} inspected={inspected_id}",
                method_name="_check_conduit_id_and_conduit",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise RuntimeError(
                f"Provided conduit_id '{conduit_id}' does not match conduit internal ID '{inspected_id}'.")
        self._logger.debug(
            f"check_conduit_id_and_conduit -> {conduit_id}",
            method_name="_check_conduit_id_and_conduit",
            owner_id=self._id, owner_display=self._display_name,
            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
        )
        return conduit_id, conduit

    def _create_detail(
            self,
            spell: ISpell,
            permissions: Permissions,
            contract_type: ContractTypes,
    ) -> Detail:
        """
        Internal

        Factory for a lineage-aware Detail entry.

        Args:
            spell (ISpell): The spell being granted/received.
            permissions (Permissions): The permissions applied to this lineage.
            contract_type (ContractTypes): Role of this Detail from the
                perspective of the ward that will own it.

        Returns:
            Detail: A new Detail instance.
        """
        if not isinstance(permissions, Permissions):
            self._logger.error(
                f"_create_detail: permissions wrong type {type(permissions).__name__}",
                method_name="_create_detail",
                owner_id=self._id,
                owner_display=self._display_name,
                mask=True,
                groups=self._log_groups,
                system_groups=self._log_sysgroups,
            )
            raise TypeError(f"Expected Permissions enum, got {type(permissions).__name__}")

        if not isinstance(contract_type, ContractTypes):
            self._logger.error(
                f"_create_detail: contract_type wrong type {type(contract_type).__name__}",
                method_name="_create_detail",
                owner_id=self._id,
                owner_display=self._display_name,
                mask=True,
                groups=self._log_groups,
                system_groups=self._log_sysgroups,
            )
            raise TypeError(
                f"Expected ContractTypes enum, got {type(contract_type).__name__}"
            )

        spell_index = spell.spell_index
        spell_id = spell.spell_id  # SHA at the moment of contract creation

        self._logger.debug(
            f"_create_detail -> index={spell_index}, spell_id={spell_id}, perms={permissions.name}, type={contract_type.name}",
            method_name="_create_detail",
            owner_id=self._id,
            owner_display=self._display_name,
            mask=True,
            groups=self._log_groups,
            system_groups=self._log_sysgroups,
        )
        return Detail(
            spell_index=spell_index,
            spell_id=spell_id,
            permissions=permissions,
            contract_type=contract_type,
        )



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
            self._logger.error(
                "check_spell_if_eligible: policy block_all",
                method_name="_check_spell_if_eligible",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise RuntimeError("Cannot contract spells when policy is set to block_all.")
        if permissions == Permissions.create and spell._permissions != Permissions.create:
            self._logger.error(
                "check_spell_if_eligible: create requested but spell not create",
                method_name="_check_spell_if_eligible",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise RuntimeError(f"Spell '{spell.__name__}' does not have create permissions, cannot contract with create permissions.")
        if permissions == Permissions.read and spell._permissions not in (Permissions.read, Permissions.create):
            self._logger.error(
                "check_spell_if_eligible: read requested but spell not read/create",
                method_name="_check_spell_if_eligible",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise RuntimeError(f"Spell '{spell.__name__}' does not have read permissions, cannot contract with read permissions.")
        if spell._permissions == Permissions.block and conduit._conduit_ward._policy != Policies.whitelist_all:
            self._logger.error(
                "check_spell_if_eligible: spell blocked and not whitelist_all",
                method_name="_check_spell_if_eligible",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise RuntimeError("Cannot contract spells with block permissions.")
        if spell._owner_conduit_id != conduit._id:
            self._logger.error(
                "check_spell_if_eligible: not owner",
                method_name="_check_spell_if_eligible",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise RuntimeError(f"Spell '{spell.__name__}' is not owned by this conduit, cannot contract it.")
        self._logger.debug(
            f"check_spell_if_eligible ok: {getattr(spell,'__name__',type(spell).__name__)}",
            method_name="_check_spell_if_eligible",
            owner_id=self._id, owner_display=self._display_name,
            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
        )

    def _add_spell_to_contract(
            self,
            *,
            spell: ISpell = None,
            spell_id: str = None,
            conduit: IConduit = None,
            conduit_id: str = None,
            permissions: str = "create",
            aetheric_frame: str = "default",
    ) -> bool | None:
        """
        Internal

        Adds a single spell to an existing contract with a peer conduit.

        This now contracts the **SpellIndex lineage** and uses the spell's
        current version ID only as the initial reference. On mutation, the
        lineage will advance, and lookups will resolve to the new version.

        Args:
            spell (ISpell, optional): The spell object to contract.
            spell_id (str, optional): The unique version ID of the spell.
            conduit (IConduit, optional): The target peer conduit.
            conduit_id (str, optional): The id of the target peer conduit.
            permissions (str): The permission level granted for this spell.
            aetheric_frame (str): The Aetheric Frame to resolve entities in.

        Returns:
            bool | None: True if the contract was updated, None on internal error.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If no contract exists with the target conduit (link required first).
            RuntimeError: If the spell is already contracted with the same permissions.
            ValueError/TypeError/RuntimeError: From internal helper checks.
        """
        self.check_cleaned()

        # Normalize permissions into the enum
        permissions_enum = EnumHelpers.convert_enum_and_check(permissions, Permissions)

        # Resolve spell + spell_id and conduit + conduit_id via your existing helpers
        spell_id, spell = self._check_spell_id_and_spell(spell, spell_id, aetheric_frame)
        conduit_id, conduit = self._check_conduit_id_and_conduit(conduit, conduit_id, aetheric_frame)

        contract = self._find_contract_by_id(conduit_id)
        if contract is None:
            self._logger.error(
                f"add_spell_to_contract: no contract for {conduit_id}",
                method_name="_add_spell_to_contract",
                owner_id=self._id,
                owner_display=self._display_name,
                mask=True,
                groups=self._log_groups,
                system_groups=self._log_sysgroups,
            )
            raise RuntimeError(
                f"No contract found for conduit ID '{conduit_id}'. "
                f"Please link to this conduit prior to spell contract initiation."
            )

        # We still use the original spell_id for duplicate detection
        if contract._check_if_exists_and_permissions(conduit._conduit_ward, spell_id, permissions_enum):
            self._logger.error(
                f"add_spell_to_contract: already exists {spell_id} with same permissions",
                method_name="_add_spell_to_contract",
                owner_id=self._id,
                owner_display=self._display_name,
                mask=True,
                groups=self._log_groups,
                system_groups=self._log_sysgroups,
            )
            raise RuntimeError(
                f"Spell with ID '{spell_id}' is already contracted in this conduit with these permissions."
            )

        # Policy + ownership checks remain unchanged
        self._check_spell_if_eligible(spell, conduit, permissions_enum)

        # From this ConduitWard's perspective, the peer's Detail represents
        # a spell that the peer has **received** from us.
        contract_type = ContractTypes.received

        with contract._lock:
            detail = self._create_detail(spell, permissions_enum, contract_type)
            contract._add(conduit._conduit_ward, detail)

        # Inform the peer spellbook about the contracted spell (SpellIndex-based)
        try:
            peer_conduit = contract._get_peer(conduit._conduit_ward)._conduit
            peer_conduit._spellbook._add_contracted_spell(spell, conduit_id)
        except Exception as e:
            self._logger.error(
                f"add_spell_to_contract: spellbook add failed: {e}",
                method_name="_add_spell_to_contract",
                exc_info=True,
                owner_id=self._id,
                owner_display=self._display_name,
                mask=True,
                groups=self._log_groups,
                system_groups=self._log_sysgroups,
            )
            raise

        self._logger.info(
            f"add_spell_to_contract: success spell_id={spell_id} conduit_id={conduit_id} perms={permissions_enum.name}",
            method_name="_add_spell_to_contract",
            owner_id=self._id,
            owner_display=self._display_name,
            mask=True,
            groups=self._log_groups,
            system_groups=self._log_sysgroups,
        )
        return True


    def _add_spells_to_contract(self, *, spell_ids: list[str] = None, conduit: IConduit = None, conduit_id: str = None,
                                permissions: str = "create", aetheric_frame = "default") -> dict[str, list[str] | dict[str, str]]:
        """
        Internal

        Attempts to add multiple spells to an existing contract in a bulk operation.

        Args:
            spell_ids (list[str], optional): List of spell IDs to contract.
            conduit (IConduit, optional): The target peer conduit.
            conduit_id (str, optional): The id of the target peer conduit.
            permissions (str): The permission level to apply to all spells (default is "create").
            aetheric_frame (str): The Aetheric Frame to resolve entities in.

        Returns:
            dict: A dictionary containing a list of "success" spell IDs and a dictionary of "failed" spell IDs mapped to error messages.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        report = {"success": [], "failed": {}}
        self._logger.debug(
            f"add_spells_to_contract start count={0 if spell_ids is None else len(spell_ids)}",
            method_name="_add_spells_to_contract",
            owner_id=self._id, owner_display=self._display_name,
            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
        )
        for sid in (spell_ids or []):
            try:
                self._add_spell_to_contract(spell_id=sid, conduit=conduit, conduit_id=conduit_id,
                                            permissions=permissions, aetheric_frame=aetheric_frame)
                report["success"].append(sid)
            except Exception as e:
                report["failed"][sid] = str(e)
                self._logger.error(
                    f"add_spells_to_contract: {sid} failed: {e}",
                    method_name="_add_spells_to_contract", exc_info=True,
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
        self._logger.info(
            f"add_spells_to_contract done success={len(report['success'])} failed={len(report['failed'])}",
            method_name="_add_spells_to_contract",
            owner_id=self._id, owner_display=self._display_name,
            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
        )
        return report

    def _remove_spell_from_contract(self, *, spell: ISpell = None, spell_id: str = None, conduit: IConduit = None,
                                    conduit_id: str = None, aetheric_frame = "default") -> bool | None:
        """
        Internal

        Removes a specific spell from an existing contract.

        Args:
            spell (ISpell, optional): The spell object to remove.
            spell_id (str, optional): The unique ID of the spell to remove.
            conduit (IConduit, optional): The target peer conduit.
            conduit_id (str, optional): The id of the target peer conduit.
            aetheric_frame (str): The Aetheric Frame to resolve entities in.

        Returns:
            bool: True if the spell was successfully removed.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If no contract is found.
            RuntimeError: If the spell ID is not found in the contract.
            ValueError/TypeError/RuntimeError: From internal helper checks.
        """
        self.check_cleaned()
        spell_id, spell = self._check_spell_id_and_spell(spell, spell_id, aetheric_frame)
        conduit_id, conduit = self._check_conduit_id_and_conduit(conduit, conduit_id, aetheric_frame)
        contract = self._find_contract_by_id(conduit_id)
        if contract is not None:
            with contract._lock:
                if contract._check_if_exists(conduit._conduit_ward, spell_id):
                    contract._remove(conduit._conduit_ward, spell_id)
                    try:
                        contract._get_peer(conduit._conduit_ward)._conduit._spellbook._remove_contracted_spell(spell_id, conduit_id)
                    except Exception as e:
                        self._logger.error(
                            f"remove_spell_from_contract: spellbook remove failed: {e}",
                            method_name="_remove_spell_from_contract", exc_info=True,
                            owner_id=self._id, owner_display=self._display_name,
                            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                        )
                        raise
                else:
                    self._logger.error(
                        f"remove_spell_from_contract: spell not in contract ({spell_id})",
                        method_name="_remove_spell_from_contract",
                        owner_id=self._id, owner_display=self._display_name,
                        mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                    )
                    raise RuntimeError(f"Spell with ID '{spell_id}' does not exist in the contract for conduit ID {conduit_id}.")
            self._logger.info(
                f"remove_spell_from_contract: success {spell_id}",
                method_name="_remove_spell_from_contract",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            return True
        self._logger.error(
            f"remove_spell_from_contract: no contract for conduit {conduit_id}",
            method_name="_remove_spell_from_contract",
            owner_id=self._id, owner_display=self._display_name,
            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
        )
        raise RuntimeError(f"No contract found for conduit ID {conduit_id}")


    def _remove_spells_from_contract(self, *, spell_ids: list[str] = None, conduit: IConduit = None,
                                     conduit_id: str = None, aetheric_frame = "default") -> dict[str, list[str] | dict[str, str]]:
        """
        Internal

        Attempts to remove multiple spells from an existing contract in a bulk operation.

        Args:
            spell_ids (list[str], optional): List of spell IDs to remove.
            conduit (IConduit, optional): The target peer conduit.
            conduit_id (str, optional): The id of the target peer conduit.
            aetheric_frame (str): The Aetheric Frame to resolve entities in.

        Returns:
            dict: A dictionary containing a list of "success" spell IDs and a dictionary of "failed" spell IDs mapped to error messages.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        report = {"success": [], "failed": {}}
        self._logger.debug(
            f"remove_spells_from_contract start count={0 if spell_ids is None else len(spell_ids)}",
            method_name="_remove_spells_from_contract",
            owner_id=self._id, owner_display=self._display_name,
            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
        )
        for sid in (spell_ids or []):
            try:
                self._remove_spell_from_contract(spell_id=sid, conduit=conduit, conduit_id=conduit_id,
                                                 aetheric_frame=aetheric_frame)
                report["success"].append(sid)
            except Exception as e:
                report["failed"][sid] = str(e)
                self._logger.error(
                    f"remove_spells_from_contract: {sid} failed: {e}",
                    method_name="_remove_spells_from_contract", exc_info=True,
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
        self._logger.info(
            f"remove_spells_from_contract done success={len(report['success'])} failed={len(report['failed'])}",
            method_name="_remove_spells_from_contract",
            owner_id=self._id, owner_display=self._display_name,
            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
        )
        return report

    def _remove_all_spells_from_contract(self, *, conduit: IConduit = None, conduit_id: str = None, aetheric_frame = "default") -> bool | None:
        """
        Internal

        Removes ALL spells from the contract associated with the specified peer conduit.

        Args:
            conduit (IConduit, optional): The target peer conduit.
            conduit_id (str, optional): The id of the target peer conduit.
            aetheric_frame (str): The Aetheric Frame to resolve entities in.

        Returns:
            bool: True if all spells were successfully removed and cleanup performed.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If no contract is found.
            ValueError/TypeError/RuntimeError: From internal helper checks.
        """
        self.check_cleaned()
        conduit_id, conduit = self._check_conduit_id_and_conduit(conduit, conduit_id, aetheric_frame)
        contract = self._find_contract_by_id(conduit_id)
        if contract is not None:
            with contract._lock:
                contract._clear_contract()
                ward_a = contract._ward_a
                ward_b = contract._ward_b
                try:
                    ward_a._conduit._spellbook._clear_contracted_spells_for_conduit(ward_b._id)
                    ward_b._conduit._spellbook._clear_contracted_spells_for_conduit(ward_a._id)
                except Exception as e:
                    self._logger.error(
                        f"remove_all_spells_from_contract: spellbook clear failed: {e}",
                        method_name="_remove_all_spells_from_contract", exc_info=True,
                        owner_id=self._id, owner_display=self._display_name,
                        mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                    )
                    raise
            self._logger.info(
                f"remove_all_spells_from_contract: success conduit_id={conduit_id}",
                method_name="_remove_all_spells_from_contract",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            return True
        self._logger.error(
            f"remove_all_spells_from_contract: no contract for {conduit_id}",
            method_name="_remove_all_spells_from_contract",
            owner_id=self._id, owner_display=self._display_name,
            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
        )
        raise RuntimeError(f"No contract found for conduit ID {conduit_id}")

    def _get_all_spells_in_contracts(
            self,
            validate: bool = True,
    ) -> Optional[dict[str, list[Tuple[str, ISpell]]]]:
        """
        Internal

        Retrieves all spells that **this conduit can use** via active contracts.

        For each peer conduit, this returns a list of:
            (current_spell_version_id, ISpell)

        Semantics:
            * Contracts are anchored on SpellIndex (via Detail.spell_index).
            * Resolution uses Spellbook._find_contracted_spell(spell_index),
              so if the lineage has mutated, we get the **current** spell object.
            * The version ID returned in the tuple is spell.spell_id (head).
        """
        self.check_cleaned()

        if validate:
            validation = self._validate_contracts_and_define()
            if not all(validation.values()):
                self._logger.error(
                    "get_all_spells_in_contracts: validation failed",
                    method_name="_get_all_spells_in_contracts",
                    owner_id=self._id,
                    owner_display=self._display_name,
                    mask=True,
                    groups=self._log_groups,
                    system_groups=self._log_sysgroups,
                )
                raise RuntimeError(
                    "One or more contracts are invalid. Please validate contracts before retrieving spells."
                )

        spells_in_contracts: dict[str, list[Tuple[str, ISpell]]] = {}

        with self._lock:
            for contract_id, contract in self._contracts.items():
                try:
                    peer_ward = contract._get_peer(self)

                    # We want spells the peer has GRANTED to this conduit,
                    # which live in the peer's detail map.
                    detail_map = contract._get_detail_map(peer_ward)
                    if not detail_map:
                        continue

                    spells: list[Tuple[str, ISpell]] = []

                    for detail in detail_map.values():
                        # lineage-based resolution
                        spell_index = detail.spell_index
                        try:
                            spell = self._conduit._spellbook._find_contracted_spell(spell_index)
                        except Exception as e:
                            if validate:
                                self._logger.error(
                                    f"_get_all_spells_in_contracts: contracted spell lookup failed "
                                    f"for peer={peer_ward._id}, index={spell_index}: {e}",
                                    method_name="_get_all_spells_in_contracts",
                                    exc_info=True,
                                    owner_id=self._id,
                                    owner_display=self._display_name,
                                    mask=True,
                                    groups=self._log_groups,
                                    system_groups=self._log_sysgroups,
                                )
                                raise
                            continue

                        # Expose the CURRENT version id, not the historical one.
                        current_id = spell.spell_id
                        spells.append((current_id, spell))

                    if spells:
                        spells_in_contracts[peer_ward._id] = spells

                except Exception as e:
                    if validate:
                        self._logger.error(
                            f"inspect contract {contract_id} failed: {e}",
                            method_name="_get_all_spells_in_contracts",
                            exc_info=True,
                            owner_id=self._id,
                            owner_display=self._display_name,
                            mask=True,
                            groups=self._log_groups,
                            system_groups=self._log_sysgroups,
                        )
                        raise RuntimeError(f"Failed to inspect contract {contract_id}: {e}")

        self._logger.debug(
            f"get_all_spells_in_contracts -> {len(spells_in_contracts)} peers",
            method_name="_get_all_spells_in_contracts",
            owner_id=self._id,
            owner_display=self._display_name,
            mask=True,
            groups=self._log_groups,
            system_groups=self._log_sysgroups,
        )
        return spells_in_contracts if spells_in_contracts else None



    def _get_spell_in_contracts(self, spell_id: str) -> Optional[tuple[str, ISpell]]:
        """
        Internal

        Attempts to retrieve a specific spell that is being granted *to* this
        conduit by any peer via active contracts.

        This now behaves in a lineage-aware way:

            * spell_id may be ANY version SHA belonging to the lineage.
            * We search each Detail's SpellIndex using Detail.has_version(spell_id).
            * If matched, we resolve via Spellbook._find_contracted_spell(spell_index)
              and return the **current** spell object (not the historical version).

        Args:
            spell_id (str): The version ID (SHA) to search for.

        Returns:
            Optional[tuple[str, ISpell]]: (peer_conduit_id, ISpell) if found, else None.
        """
        self.check_cleaned()

        with self._lock:
            for contract in self._contracts.values():
                peer_ward = contract._get_peer(self)
                detail_map = contract._get_detail_map(peer_ward)

                if not detail_map:
                    continue

                for detail in detail_map.values():
                    if not detail.has_version(spell_id):
                        continue

                    spell_index = detail.spell_index
                    try:
                        spell = self._conduit._spellbook._find_contracted_spell(spell_index)
                    except Exception as e:
                        self._logger.error(
                            f"_get_spell_in_contracts: contracted spell lookup failed "
                            f"for version={spell_id}, index={spell_index}: {e}",
                            method_name="_get_spell_in_contracts",
                            exc_info=True,
                            owner_id=self._id,
                            owner_display=self._display_name,
                            mask=True,
                            groups=self._log_groups,
                            system_groups=self._log_sysgroups,
                        )
                        return None

                    self._logger.debug(
                        f"get_spell_in_contracts {spell_id} -> hit {peer_ward._id}",
                        method_name="_get_spell_in_contracts",
                        owner_id=self._id,
                        owner_display=self._display_name,
                        mask=True,
                        groups=self._log_groups,
                        system_groups=self._log_sysgroups,
                    )
                    return peer_ward._id, spell

        self._logger.debug(
            f"get_spell_in_contracts {spell_id} -> miss",
            method_name="_get_spell_in_contracts",
            owner_id=self._id,
            owner_display=self._display_name,
            mask=True,
            groups=self._log_groups,
            system_groups=self._log_sysgroups,
        )
        return None



    def _get_spells_in_contract_by_conduit(self, conduit_id: str) -> dict[str, list[tuple[str, ISpell]]] | None:
        """
        Internal

        Retrieves all spells exchanged with a specific conduit by its unique ID.

        - "inbound": spells the peer has granted to this conduit.
        - "outbound": spells this conduit has granted to the peer.

        Args:
            conduit_id (str): The id of the target conduit.

        Returns:
            dict[str, list[tuple[str, ISpell]]] | None: A dictionary mapping roles
            ("inbound", "outbound") to lists of (spell_id, ISpell) tuples, or None
            if no such conduit is linked.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        with self._lock:
            contract = self._find_contract_by_id(conduit_id)
            if not contract:
                self._logger.debug(
                    f"get_spells_in_contract_by_conduit {conduit_id} -> no contract",
                    method_name="_get_spells_in_contract_by_conduit",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                return None

            spells_result: dict[str, list[tuple[str, ISpell]]] = {"inbound": [], "outbound": []}

            peer_ward = contract._get_peer(self)

            # Inbound: spells the peer has granted to us (live in peer's detail map).
            received_map = contract._get_detail_map(peer_ward)
            for sid, detail in received_map.items():
                spell = self._conduit.find_contracted_spell(sid)
                if spell:
                    spells_result["inbound"].append((sid, spell))

            # Outbound: spells we have granted to the peer (live in our detail map).
            our_map = contract._get_detail_map(self)
            for sid, detail in our_map.items():
                spell: Optional[ISpell] = None
                try:
                    # This is a local spell we own; resolve via SpellIndex-aware get_spell_by_id.
                    spell = self._conduit.get_spell_by_id(sid)
                except Exception:
                    spell = None

                if spell is not None:
                    spells_result["outbound"].append((sid, spell))

        self._logger.debug(
            f"get_spells_in_contract_by_conduit {conduit_id} -> inbound={len(spells_result['inbound'])} outbound={len(spells_result['outbound'])}",
            method_name="_get_spells_in_contract_by_conduit",
            owner_id=self._id, owner_display=self._display_name,
            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
        )
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
            RuntimeError: If the Conduit is cleaned.
            ValueError: If `conduit_name` is empty or not a string.
        """
        self.check_cleaned()
        if not conduit_name or not isinstance(conduit_name, str):
            self._logger.error(
                "get_spells_in_contract_by_conduit_name: invalid name",
                method_name="_get_spells_in_contract_by_conduit_name",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise ValueError("Conduit name must be a non-empty string.")

        with self._lock:
            for contract in self._contracts.values():
                peer_ward = contract._get_peer(self)
                peer_conduit = peer_ward._conduit
                if getattr(peer_conduit, "_name", None) == conduit_name:
                    res = self._get_spells_in_contract_by_conduit(peer_ward._id)
                    self._logger.debug(
                        f"get_spells_in_contract_by_conduit_name {conduit_name} -> {'hit' if res else 'miss'}",
                        method_name="_get_spells_in_contract_by_conduit_name",
                        owner_id=self._id, owner_display=self._display_name,
                        mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                    )
                    return res

        self._logger.debug(
            f"get_spells_in_contract_by_conduit_name {conduit_name} -> miss",
            method_name="_get_spells_in_contract_by_conduit_name",
            owner_id=self._id, owner_display=self._display_name,
            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
        )
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
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        contracted_conduits = []
        with self._lock:
            for contract_id, contract in self._contracts.items():
                peer_ward = contract._get_peer(self)
                peer_conduit = peer_ward._conduit
                contracted_conduits.append((peer_ward._id, peer_conduit))
        self._logger.debug(
            f"get_contracted_conduits -> {len(contracted_conduits)}",
            method_name="_get_contracted_conduits",
            owner_id=self._id, owner_display=self._display_name,
            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
        )
        return contracted_conduits if contracted_conduits else None

    def _describe_contract(self, conduit_id: str) -> dict:
        """
        Internal

        Returns a detailed diagnostic summary of a contract established with a specific peer conduit ID.

        Args:
            conduit_id (str): id of the peer conduit whose contract you wish to examine.

        Returns:
            dict: Dictionary containing contract metadata, including spell list and permissions.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If no contract is found with the given conduit ID.
        """
        self.check_cleaned()
        with self._lock:
            contract = self._find_contract_by_id(conduit_id)
            if not contract:
                self._logger.error(
                    f"_describe_contract: no contract {conduit_id}",
                    method_name="_describe_contract",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                raise RuntimeError(f"No contract found with conduit ID: {conduit_id}")

            peer_ward = contract._get_peer(self)
            peer_conduit = peer_ward._conduit
            detail_map = contract._get_detail_map(self)

            result = {
                "contract_id": contract._id,
                "peer_conduit_name": getattr(peer_conduit, "_name", "Unknown"),
                "spell_count": len(detail_map),
                "spells": [
                    {
                        "spell_id": sid,
                        "permissions": detail.permissions.name,
                    }
                    for sid, detail in detail_map.items()
                ]
            }
        self._logger.debug(
            f"_describe_contract {conduit_id} -> count={result['spell_count']}",
            method_name="_describe_contract",
            owner_id=self._id, owner_display=self._display_name,
            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
        )
        return result

    def _validate_contracts_and_define(self) -> dict[str, bool]:
        """
        Internal

        Validates all active contracts attached to this conduit for symmetry and integrity.

        This ensures both sides list the same spells, permissions are consistent, and all
        referenced contracted spells exist in the peer's spellbook.

        Args:
            None

        Returns:
            dict[str, bool]: Dictionary mapping contract id to validation results (True/False).

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        results = {}
        with self._lock:
            for contract_id, contract in self._contracts.items():
                try:
                    valid = True
                    for ward in (contract._ward_a, contract._ward_b):
                        peer = contract._get_peer(ward)
                        peer_book = peer._conduit._spellbook
                        detail_map = contract._get_detail_map(ward)
                        for sid, detail in detail_map.items():
                            spell = peer_book._find_contracted_spell(sid)
                            if spell is None:
                                valid = False
                                break
                        if not valid:
                            break
                    results[contract_id] = valid
                except Exception:
                    results[contract_id] = False
        self._logger.debug(
            f"_validate_contracts_and_define -> ok={sum(1 for v in results.values() if v)} / total={len(results)}",
            method_name="_validate_contracts_and_define",
            owner_id=self._id, owner_display=self._display_name,
            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
        )
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
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        results = self._validate_contracts_and_define()
        ok = all(results.values()) if results else False
        self._logger.debug(
            f"_validate_received_contracts -> {ok}",
            method_name="_validate_received_contracts",
            owner_id=self._id, owner_display=self._display_name,
            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
        )
        return ok

#endregion Spellbinding API
#endregion ConduitWard