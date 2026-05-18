from typing import Any, Dict, Iterable, List, Optional, Protocol, Tuple, runtime_checkable
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.contract.contract_types.contract_types import (
    ContractTypes,
)
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeTransactionType,
)
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.iconduit import IConduit
from melder.utilities.interfaces.idetail import IDetail
from melder.utilities.interfaces.isafelogger import ISafeLogger
from melder.utilities.interfaces.ispell import ISpell

@runtime_checkable
class IConduitWard(ICleanable, Protocol):
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

    # Core fields (structural)
    _conduit: 'IConduit'
    _logger: 'ISafeLogger'
    _dynamic: bool
    _conduit_type: 'ConduitState'
    _id: str
    _display_name: str
    _log_groups: List[str]
    _log_sysgroups: List[str]
    _policy_set: bool
    _policy: Optional['Policies']
    _initiated_index: Dict[str, str]
    _received_index: Dict[str, str]
    _contracts: 'Dict[str, Any]'
    _parent_conduit: Optional['IConduit']
    _root_conduit: Optional['IConduit']
    _lesser_conduits: 'Dict[str, IConduit]'
    _lock: Any

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------
    def cleanup(self) -> None:
        """
        Public API

        Clean up the conduit ward and invalidate it for further use.
        """
        ...

    def _clean_up_lesser_conduits_links(self) -> None:
        """
        Internal

        Recursively clean and detach all linked lesser conduits (children).
        """
        ...

    def _clean_up_links(self) -> None:
        """
        Internal

        Clean and dispose all active external contracts and links.
        """
        ...

    def cleanup_all_lesser_conduits(self) -> None:
        """
        Public API

        Clean up all lesser conduits (children) linked to this conduit.

        This is typically used when the parent conduit is undergoing a state change,
        like an upgrade to a normal state, or as part of a controlled shutdown.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    # ------------------------------------------------------------------
    # Context Manager
    # ------------------------------------------------------------------
    def __enter__(self) -> 'IConduitWard':
        """
        Enter the conduit-ward coordination context.

        Returns:
            IConduitWard: This ward instance while its internal coordination
            state is held for the caller.
        """
        ...

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        Exit the conduit-ward coordination context.

        The concrete implementation is expected to release any ward-scoped lock
        acquired in :meth:`__enter__` and not suppress exceptions from the
        with-body.
        """
        ...

    # ------------------------------------------------------------------
    # Change Control
    # ------------------------------------------------------------------
    def begin_transaction(
            self,
            transaction_type: "ChangeTransactionType | str",
            *,
            conduit_ids: Optional[Iterable[str]] = None,
            conduits: Optional[Iterable["IConduit"]] = None,
            scope_keys: Optional[Iterable[str]] = None,
            scope_hashes: Optional[Iterable[str]] = None,
            binding_keys: Optional[Iterable[Tuple[str, str]]] = None,
            contract_keys: Optional[Iterable[Tuple[str, str, str]]] = None,
            metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Public API

        Begin a change-control transaction through the owning Conduit.

        Args:
            transaction_type:
                Transaction type enum or string value (e.g. "link", "bind").
            conduit_ids:
                Optional list of conduits participating in non-link requests.
            conduits:
                Optional list of conduit objects participating in the request.
            scope_keys:
                Optional normalized scope keys for conflict checks.
            scope_hashes:
                Optional normalized scope hashes for conflict checks.
            binding_keys:
                Optional binding keys affected by the request.
            contract_keys:
                Optional contract keys affected by the request.
            metadata:
                Optional structured metadata for diagnostics.
        Returns:
            None.
        Raises:
            RuntimeError: If the ConduitWard is cleaned.
            RuntimeError: If the owning Conduit is not normal.
            RuntimeError: If change-control admission is denied.
            ValueError: If transaction_type is invalid.
            TypeError: If transaction_type has an invalid type.
        """
        ...

    def end_transaction(
            self,
            transaction_type: "ChangeTransactionType | str | None" = None,
    ) -> None:
        """
        Public API

        End the active change-control transaction through the owning Conduit.

        Args:
            transaction_type:
                Optional transaction type assertion for safety checks.
        Returns:
            None.
        Raises:
            RuntimeError: If the ConduitWard is cleaned.
            RuntimeError: If the owning Conduit is not normal.
            RuntimeError: If no change transaction is active.
            RuntimeError: If transaction_type does not match the active request.
            ValueError: If transaction_type is invalid.
            TypeError: If transaction_type has an invalid type.
        """
        ...

    # ------------------------------------------------------------------
    # Conduit Ward Configuration
    # ------------------------------------------------------------------
    @property
    def root_conduit(self) -> Optional['IConduit']:
        """
        Return the root (normal) conduit for this lineage.

        Raises:
            RuntimeError: If the root conduit is missing or not normal.
        """
        ...

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
        ...

    def _set_initial_policy(self, policy: 'Policies') -> Optional['Policies']:
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
        ...

    def _set_new_policy(self, policy: 'str | Policies') -> None:
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
        ...

    # ------------------------------------------------------------------
    # Link Management
    # ------------------------------------------------------------------
    def _link(self, target_conduit: 'IConduit') -> bool:
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
        ...

    def _create_new_contract(self, target_conduit: 'IConduit') -> bool:
        """
        Internal

        Creates a new bidirectional contract (link) with the specified target conduit.

        This method handles simultaneous locking of both wards to prevent deadlocks.

        Args:
            target_conduit (IConduit): The conduit to link with.

        Returns:
            bool: True if the contract was created successfully.
        """
        ...

    def _find_contract_id(self, target_conduit: 'IConduit') -> Optional[str]:
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
        ...

    def _find_contract(self, target_conduit: 'IConduit') -> Optional[Any]:
        """
        Internal

        Finds the contract object linked to the given target conduit.

        Args:
            target_conduit (IConduit): The target conduit to find the contract for.

        Returns:
            Optional[Any]: The contract object if it exists, otherwise None.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            TypeError: If `target_conduit` is not an `IConduit` instance.
        """
        ...

    def _find_contract_by_id(self, conduit_id: str) -> Optional[Any]:
        """
        Internal

        Finds a contract by the peer's Conduit ID.

        Args:
            conduit_id (str): The ID of the peer conduit in the contract.

        Returns:
            Optional[Any]: The found contract object or None if not found.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    def _sever_link(self, target_conduit: 'IConduit') -> bool:
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
        ...

    def _remove_contract(self, target_conduit: 'IConduit') -> bool:
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
        ...

    def _link_lesser_conduit(self, lesser_conduit: 'IConduit') -> None:
        """
        Internal

        Links a lesser conduit (child) to this conduit (parent).

        This establishes the parent-child lineage relationship.

        Args:
            lesser_conduit (IConduit): The lesser conduit to link.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    def _get_lesser_conduit(self, conduit_id: str) -> Optional['IConduit']:
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
        ...

    def _get_links(self) -> List['IConduit']:
        """
        Internal

        Returns a combined list of all peer conduits this conduit has contracts with (both initiated and provider).

        Returns:
            List[IConduit]: A list of all linked peer conduits.
        """
        ...

    def _get_initiated_conduits(self) -> List['IConduit']:
        """
        Internal

        Retrieves all conduits that this conduit has initiated contracts toward (outbound links).

        Returns:
            List[IConduit]: A list of conduits that this conduit has initiated contracts with.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    def _get_provider_conduits(self) -> List['IConduit']:
        """
        Internal

        Retrieves all conduits that have initiated contracts to this conduit (inbound links).

        Returns:
            List[IConduit]: A list of conduits that have linked to this conduit as a provider.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    def _get_initiated_conduit(self, conduit_id: str) -> Optional['IConduit']:
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
        ...

    def _get_provider_conduit(self, conduit_id: str) -> Optional['IConduit']:
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
        ...

    def _sever_all_linked_conduits(self) -> None:
        """
        Internal

        Severs all active peer links (contracts) to conduits. Excludes lesser conduits.
        """
        ...

    # ------------------------------------------------------------------
    # Spellbinding API
    # ------------------------------------------------------------------
    def _check_spell_id_and_spell(
            self,
            spell: Optional['ISpell'] = None,
            spell_id: Optional[str] = None,
            aetheric_frame: str = "default",
    ) -> Tuple[str, 'ISpell']:
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
        ...

    def _check_conduit_id_and_conduit(
            self,
            conduit: Optional['IConduit'] = None,
            conduit_id: Optional[str] = None,
            aetheric_frame: str = "default",
    ) -> Tuple[str, 'IConduit']:
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
        ...

    def _create_detail(
            self,
            spell: 'ISpell',
            permissions: 'Permissions',
            contract_type: 'ContractTypes',
    ) -> 'IDetail':
        """
        Internal

        Factory for a lineage-aware Detail entry.

        Args:
            spell (ISpell): The spell being granted/received.
            permissions (Permissions): The permissions applied to this lineage.
            contract_type (ContractTypes): Role of this Detail from the
                perspective of the ward that will own it.

        Returns:
            IDetail: A new detail instance.
        """
        ...

    def _check_spell_if_eligible(
            self,
            spell: 'ISpell',
            conduit: 'IConduit',
            permissions: 'Permissions',
    ) -> None:
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
        ...

    def _add_spell_to_contract(
            self,
            *,
            spell: Optional['ISpell'] = None,
            spell_id: Optional[str] = None,
            conduit: Optional['IConduit'] = None,
            conduit_id: Optional[str] = None,
            permissions: str = "create",
            aetheric_frame: str = "default",
            reason: Any = None,
            root_spell_id: str | None = None,
            link_dependencies: bool = False,
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
        ...

    def _add_spells_to_contract(
            self,
            *,
            spell_ids: Optional[list[str]] = None,
            conduit: Optional['IConduit'] = None,
            conduit_id: Optional[str] = None,
            permissions: str = "create",
            aetheric_frame: str = "default",
            reason: Any = None,
            link_dependencies: bool = False,
    ) -> dict[str, list[str] | dict[str, str]]:
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
        ...

    def _remove_spell_from_contract(
            self,
            *,
            spell: Optional['ISpell'] = None,
            spell_id: Optional[str] = None,
            conduit: Optional['IConduit'] = None,
            conduit_id: Optional[str] = None,
            aetheric_frame: str = "default",
    ) -> bool | None:
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
        ...

    def _remove_spells_from_contract(
            self,
            *,
            spell_ids: Optional[list[str]] = None,
            conduit: Optional['IConduit'] = None,
            conduit_id: Optional[str] = None,
            aetheric_frame: str = "default",
    ) -> dict[str, list[str] | dict[str, str]]:
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
        ...

    def _remove_all_spells_from_contract(
            self,
            *,
            conduit: Optional['IConduit'] = None,
            conduit_id: Optional[str] = None,
            aetheric_frame: str = "default",
    ) -> bool | None:
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
        ...

    def _get_all_spells_in_contracts(
            self,
            validate: bool = True,
    ) -> Optional[dict[str, list[Tuple[str, 'ISpell']]]]:
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
        ...

    def _get_spell_in_contracts(self, spell_id: str) -> Optional[tuple[str, 'ISpell']]:
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
        ...

    def _get_spells_in_contract_by_conduit(
            self,
            conduit_id: str,
    ) -> dict[str, list[tuple[str, 'ISpell']]] | None:
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
            if no such conduit is linked. When a contract exists but contains no
            spells, the inbound/outbound lists are empty.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    def _get_spells_in_contract_by_conduit_name(
            self,
            conduit_name: str,
    ) -> dict[str, list[tuple[str, 'ISpell']]] | None:
        """
        Internal

        Retrieves all spells exchanged with a specific conduit by its declared name.

        Mirrors `_get_spells_in_contract_by_conduit` but performs lookup by name.

        Args:
            conduit_name (str): The name identifier of the target conduit.

        Returns:
            dict[str, list[tuple[str, ISpell]]] | None: A dictionary of spells exchanged (inbound/outbound), or None if not found.
            When a contract exists but contains no spells, inbound/outbound lists are empty.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            ValueError: If `conduit_name` is empty or not a string.
        """
        ...

    def _get_contracted_conduits(self) -> list[Tuple[str, 'IConduit']] | None:
        """
        Internal

        Return all conduits that currently have active spell contracts with this conduit.

        Returns:
            list[tuple[str, IConduit]] | None:
                List of ``(conduit_id, conduit)`` tuples for current contract
                peers, or ``None`` when no links exist.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    def _describe_contract(self, conduit_id: str) -> dict:
        """
        Internal

        Return a detailed diagnostic summary of one contract by peer conduit id.

        Args:
            conduit_id (str): id of the peer conduit whose contract you wish to examine.

        Returns:
            dict: Contract metadata payload, including spell list and
            permissions.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If no contract is found with the given conduit ID.
        """
        ...

    def _validate_contracts_and_define(self) -> dict[str, bool]:
        """
        Internal

        Validates all active contracts attached to this conduit for symmetry and integrity.

        This ensures both sides list the same spells, permissions are consistent, and all
        referenced contracted spells exist in the peer's spellbook.

        Returns:
            dict[str, bool]:
                Mapping of contract id to validation result.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    def _validate_received_contracts(self) -> bool:
        """
        Internal

        Performs a high-level validation check across all contracts involving this conduit.

        This aggregates the results of `_validate_contracts_and_define` to provide a simple pass/fail status.

        Returns:
            bool: True if all active contracts pass validation, False otherwise.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...
