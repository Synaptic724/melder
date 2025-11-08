from uuid import UUID
import threading
from typing import List, Optional, Any, Tuple
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.utilities.data_structures.concurrent_dictionary import ConcurrentDict
from melder.utilities.helpers.general_helpers import EnumHelpers
from melder.utilities.interfaces.interfaces import IConduit, IConduitWard, ISpell
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
            if (new_policy == Policies.block_all or new_policy == Policies.whitelist_all) and len(self._contracts) > 0:
                raise RuntimeError("Cannot set policy to 'block_all' or 'whitelist_all' when there are existing contracts.")

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
        if target_conduit._conduit_state == ConduitState.lesser:
            raise RuntimeError("Cannot link to a lesser conduit. Use _link_lesser_conduit instead.")
        if target_conduit.__creation_context__._conduit_id == self._id:
            raise RuntimeError("Cannot link a conduit to itself.")
        if not self._dynamic:
            raise RuntimeError("Dynamic environment is not enabled. Cannot link conduits.")

        # Check if the target conduit is already linked
        if target_conduit._conduit_state == ConduitState.normal:
            if self._find_contract(target_conduit):
                return True
            return self._create_new_contract(target_conduit)

        return False


    def _create_new_contract(self, target_conduit: IConduit) -> bool:
        """
        Internal

        Creates a new contract with the specified target conduit.

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
                    return True

                contract = Contract(self, ward_b)

                # Register in both wards
                self._contracts[contract._id] = contract
                ward_b._contracts[contract._id] = contract

                # Index updates
                self._initiated_index[target_id] = contract._id
                ward_b._received_index[self._id] = contract._id

                # Create spellbook entries
                ward_b._conduit._spellbook._create_link_contract(target_id)

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

    def _find_contract_by_id(self, conduit_id: UUID) -> Optional[Contract]:
        """
        Internal

        Finds a contract by its ID.

        Args:
            contract_id (UUID): The ID of the contract to find.

        Returns:
            Optional[Contract]: The found contract or None if not found.
        """
        if self._sealed:
            raise RuntimeError("Cannot find contracts in a sealed Conduit Ward.")
        check_id = self._initiated_index.get(conduit_id) or self._received_index.get(conduit_id)
        return self._contracts.get(check_id)

    def _sever_link(self, target_conduit: IConduit) -> bool:
        """
        Internal

        Sever the link between this Conduit and its target Conduit.
        """
        if self._sealed:
            raise RuntimeError("Cannot sever a link in a sealed Conduit Ward.")

        locks = sorted([self._lock, target_conduit._conduit_ward._lock], key=id)
        with locks[0]:
            with locks[1]:
                if self._find_contract(target_conduit):
                    return self._remove_contract(target_conduit)
                else:
                    raise RuntimeError("No contract found to sever with the target conduit.")

    def _remove_contract(self, target_conduit: IConduit) -> bool:
        """
        Internal

        Removes the contract with the specified target conduit.
        """
        if self._sealed:
            raise RuntimeError("Cannot remove contracts in a sealed Conduit Ward.")

        conduit_id, conduit = self._check_conduit_id_and_conduit(conduit=target_conduit)

        if (contract := self._find_contract(target_conduit)) is not None:
            with contract._lock:
                id_a = contract._ward_a._id
                id_b = contract._ward_b._id
                if id_a == conduit_id:
                    contract._ward_a._conduit._spellbook._sever_link_contract(id_a)
                    contract._ward_b._conduit._spellbook._sever_link_contract(id_b)
                else:
                    contract._ward_b._conduit._spellbook._sever_link_contract(id_b)
                    contract._ward_a._conduit._spellbook._sever_link_contract(id_a)

                del self._contracts[contract._id]
                del target_conduit._conduit_ward._contracts[contract._id]

                del self._initiated_index[target_conduit.__creation_context__._conduit_id]
                del target_conduit._conduit_ward._received_index[self._id]

                contract.seal()
                return True
        return False

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
            if (ward := getattr(conduit, "_conduit_ward", None)):
                if (result := ward._get_lesser_conduit(conduit_id)) is not None:
                    return result

        return None

    def _get_links(self) -> List[IConduit]:
        """
        Internal

        Returns a list of all links associated with this conduit. Excluding lesser conduits.
        :return: List[IConduit]
        """
        with self._lock:
            return self._get_initiated_conduits() + self._get_provider_conduits()


    def _get_initiated_conduits(self) -> List[IConduit]:
        """
        Internal

        Retrieves all conduits that this conduit has initiated contracts toward.

        Returns:
            List[IConduit]: A list of conduits that this conduit has initiated contracts with.
        """
        if self._sealed:
            raise RuntimeError("Cannot get linked conduits from a sealed Conduit Ward.")
        return [
            conduit for conduit_id in self._initiated_index.keys()
            if (conduit := self._get_initiated_conduit(conduit_id)) is not None
        ]


    def _get_provider_conduits(self) -> List[IConduit]:
        """
        Internal

        Retrieves all conduits that have initiated contracts to this conduit.

        Returns:
            List[IConduit]: A list of conduits that have linked to this conduit as a provider.
        """
        if self._sealed:
            raise RuntimeError("Cannot get linked conduits from a sealed Conduit Ward.")
        return [
            conduit for conduit_id in self._received_index.keys()
            if (conduit := self._get_provider_conduit(conduit_id)) is not None
        ]

    def _get_initiated_conduit(self, conduit_id: UUID) -> Optional[IConduit]:
        """
        Internal

        Retrieves the conduit that this conduit has initiated a contract *toward*.

        This method uses the `_initiated_index` to resolve an outbound connection,
        where this conduit was the initiator of the contract.

        Args:
            conduit_id (UUID): The ID of the target conduit this conduit linked to.

        Returns:
            Optional[IConduit]: The target conduit if the link exists, otherwise None.
        """
        if self._sealed:
            raise RuntimeError("Cannot get linked conduits from a sealed Conduit Ward.")
        if conduit_id in self._initiated_index:
            contract_id = self._initiated_index[conduit_id]
            if (contract := self._contracts.get(contract_id, None)) is not None:
                return contract._ward_b._conduit if conduit_id == contract._ward_b._id else contract._ward_a._conduit

    def _get_provider_conduit(self, conduit_id: UUID) -> Optional[IConduit]:
        """
        Internal

        Retrieves the conduit that initiated a contract *to this* conduit.

        This method uses the `_received_index` to resolve an inbound connection,
        where another conduit linked to this one as the contract provider.

        Args:
            conduit_id (UUID): The ID of the source conduit that linked to this one.

        Returns:
            Optional[IConduit]: The source conduit if the link exists, otherwise None.
        """
        if self._sealed:
            raise RuntimeError("Cannot get linked conduits from a sealed Conduit Ward.")
        if conduit_id in self._received_index:
            contract_id = self._received_index[conduit_id]
            if (contract := self._contracts.get(contract_id, None)) is not None:
                return contract._ward_b._conduit if conduit_id == contract._ward_b._id else contract._ward_a._conduit


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
#region Spellbinding API
    def _check_spell_id_and_spell(
            self,
            spell: ISpell = None,
            spell_id: str = None,
            aetheric_frame: str = "default"
    ) -> Tuple[str, ISpell]:
        """
        Internal

        Validation and resolution of spell_id and spell object.

        Requires either spell or spell_id. Resolves and validates the pair.
        Returns (spell_id, spell).
        """
        if spell is None and spell_id is None:
            raise ValueError("Either spell or spell_id must be provided.")

        # Resolve spell from spell_id
        if spell is None:
            if not isinstance(spell_id, str):
                raise TypeError(f"Expected spell_id as str, got {type(spell_id).__name__}")
            spell = self._conduit.get_spell_by_id(spell_id, aetheric_frame)
            if spell is None:
                raise RuntimeError(f"Could not resolve spell for spell_id '{spell_id}'.")

        # Resolve spell_id from spell
        if spell_id is None:
            if not isinstance(spell, ISpell):
                raise TypeError(f"Expected ISpell instance, got {type(spell).__name__}")
            spell_id = self._conduit.inspect_spell(spell, aetheric_frame)
            if spell_id is None:
                raise RuntimeError("Could not determine spell_id from spell.")

        # Final integrity check
        inspected_id = self._conduit.inspect_spell(spell, aetheric_frame)
        if spell_id != inspected_id:
            raise RuntimeError(f"Provided spell_id '{spell_id}' does not match inspected ID '{inspected_id}'.")

        return spell_id, spell


    def _check_conduit_id_and_conduit(self,
            conduit: IConduit = None,
            conduit_id: UUID = None, aetheric_frame = "default") -> Tuple[UUID, IConduit]:
        """
        Internal

        Validation and resolution of conduit_id and conduit object.

        Requires either conduit or conduit_id. Resolves and validates the pair.
        Returns (conduit_id, conduit).
        """
        if conduit is None and conduit_id is None:
            raise ValueError("Either conduit or conduit_id must be provided.")

        # Resolve conduit from conduit_id
        if conduit is None:
            if not isinstance(conduit_id, UUID):
                raise TypeError(f"Expected conduit_id as UUID, got {type(conduit_id).__name__}")
            conduit = self._conduit.get_conduit_by_id(conduit_id, aetheric_frame)
            if conduit is None:
                raise RuntimeError(f"Could not resolve conduit for conduit_id '{conduit_id}'.")

        # Resolve conduit_id from conduit
        if conduit_id is None:
            if not isinstance(conduit, IConduit):
                raise TypeError(f"Expected IConduit instance, got {type(conduit).__name__}")
            conduit_id = conduit.__creation_context__._conduit_id
            if conduit_id is None:
                raise RuntimeError("Could not determine conduit_id from conduit.")

        inspected_id = conduit.__creation_context__._conduit_id
        if conduit_id != inspected_id:
            raise RuntimeError(
                f"Provided conduit_id '{conduit_id}' does not match conduit internal ID '{inspected_id}'.")

        return conduit_id, conduit

    def _create_detail(self, spell_id: str, permissions: Permissions) -> Detail:
        """
        Internal

        Creates a new Detail instance for spell permissions.

        Args:
            spell_id (str): The ID of the spell this detail applies to.
            permissions (Permissions): The permissions granted for this spell.

        Returns:
            Detail: A new Detail instance with the specified spell_id and permissions.
        """
        if not isinstance(permissions, Permissions):
            raise TypeError(f"Expected Permissions enum, got {type(permissions).__name__}")
        return Detail(spell_id, permissions)


    def _check_spell_if_eligible(self, spell: ISpell, conduit: IConduit, permissions: Permissions) -> None:
        """
        Internal
        Checks if the provided spell is eligible for contracting based on the conduit policy.
        :param spell: The spell to check.
        :return: bool indicating if the spell is eligible.
        """
        if conduit._conduit_ward._policy == Policies.block_all:
            raise RuntimeError("Cannot contract spells when policy is set to block_all.")
        if permissions == Permissions.create and spell._permissions != Permissions.create:
            raise RuntimeError(f"Spell '{spell.__name__}' does not have create permissions, cannot contract with create permissions.")
        if permissions == Permissions.read and spell._permissions not in (Permissions.read, Permissions.create):
            raise RuntimeError(f"Spell '{spell.__name__}' does not have read permissions, cannot contract with read permissions.")
        if spell._permissions == Permissions.block and conduit._conduit_ward._policy != Policies.whitelist_all:
            raise RuntimeError("Cannot contract spells with block permissions.")
        if spell._owner_conduit_id != conduit.__creation_context__._conduit_id:
            raise RuntimeError(f"Spell '{spell.__name__}' is not owned by this conduit, cannot contract it.")

    def _add_spell_to_contract(self, *, spell: ISpell = None, spell_id: str = None, conduit: IConduit = None, conduit_id: UUID = None,
                               permissions: str = "create", aetheric_frame = "default") -> bool | None:
        """
        Internal

        Creates a new spell contract for this conduit. This is used to create a contract
        :return: bool
        """
        if self._sealed:
            raise RuntimeError("Cannot validate contracts in a sealed Conduit Ward.")

        # Check if permissions are valid
        permissions = EnumHelpers.convert_enum_and_check(permissions, Permissions)

        # Check if spell or spell_id is provided, if not, raise an error
        spell_id, spell = self._check_spell_id_and_spell(spell, spell_id, aetheric_frame)

        # Check if conduit is provided, if not, resolve it from conduit_id
        conduit_id, conduit = self._check_conduit_id_and_conduit(conduit, conduit_id, aetheric_frame)

        # Check if contract exists for the conduit if not raise an error. Link must exist prior to spell contract initiation.
        if (contract := self._find_contract_by_id(conduit_id)) is None:
            raise RuntimeError(f"No contract found for conduit ID {conduit_id}, please link to this conduit prior to spell contract initiation.")

        # Check if the spell exists in our contracted spells
        if contract._check_if_exists_and_permissions(conduit._conduit_ward, spell_id, permissions):
            raise RuntimeError(f"Spell with ID '{spell_id}' is already contracted in this conduit with these permissions.")

        # Check if spell is available with the required permissions
        self._check_spell_if_eligible(spell, conduit, permissions)

        # Create Detail with the spell_id and permissions
        with contract._lock:
            detail = self._create_detail(spell_id, permissions)
            contract._add(conduit._conduit_ward, detail)

        # Add spell to spellbook
        conduit._spellbook._add_contracted_spell(spell, conduit_id)

        return True

    def _add_spells_to_contract(self, *, spell_ids: list[str] = None, conduit: IConduit = None, conduit_id: UUID = None,
                               permissions: str = "create", aetheric_frame = "default") -> dict[str, list[str] | dict[str, str]]:
        """
        Internal

        Creates a new spell contracts for this conduit. This is used to create multiple contracts.
        :return: dict with success and failed spell IDs.
        """
        if self._sealed:
            raise RuntimeError("Cannot validate contracts in a sealed Conduit Ward.")

        report = {"success": [], "failed": {}}
        for spell_id in spell_ids:
            try:
                self._add_spell_to_contract(spell_id=spell_id, conduit=conduit, conduit_id=conduit_id,
                                            permissions=permissions, aetheric_frame=aetheric_frame)
                report["success"].append(spell_id)
            except Exception as e:
                report["failed"][spell_id] = str(e)
        return report

    def _remove_spell_from_contract(self, *, spell: ISpell = None, spell_id: str = None, conduit: IConduit = None,
                                    conduit_id: UUID = None, aetheric_frame = "default") -> bool | None:
        """
        Internal

        Removes a specific spell contract by its spell or spell_id.
        :param spell_id:
        :return: bool
        """
        if self._sealed:
            raise RuntimeError("Cannot validate contracts in a sealed Conduit Ward.")

        # Check if spell or spell_id is provided, if not, raise an error
        spell_id, spell = self._check_spell_id_and_spell(spell, spell_id, aetheric_frame)

        # Check if conduit is provided, if not, resolve it from conduit_id
        conduit_id, conduit = self._check_conduit_id_and_conduit(conduit, conduit_id, aetheric_frame)

        # Check if contract exists for the conduit if not raise an error. Link must exist prior to spell contract initiation.
        if (contract := self._find_contract_by_id(conduit_id)) is not None:
            with contract._lock:
                if contract._check_if_exists(conduit._conduit_ward, spell_id):
                    contract._remove(conduit._conduit_ward, spell_id)
                    # Remove spell from spellbook
                    conduit._spellbook._remove_contracted_spell(spell_id, conduit_id)
                else:
                    raise RuntimeError(f"Spell with ID '{spell_id}' does not exist in the contract for conduit ID {conduit_id}.")
        else:
            raise RuntimeError(f"No contract found for conduit ID {conduit_id}")


    def _remove_spells_from_contract(self, *, spell_ids: list[str] = None, conduit: IConduit = None,
                                     conduit_id: UUID = None, aetheric_frame = "default") -> dict[str, list[str] | dict[str, str]]:
        """
        Internal

        Removes some spells from the contract associated with this conduit.
        :return: bool
        """
        if self._sealed:
            raise RuntimeError("Cannot validate contracts in a sealed Conduit Ward.")

        report = {"success": [], "failed": {}}
        for spell_id in spell_ids:
            try:
                self._remove_spell_from_contract(spell_id=spell_id, conduit=conduit, conduit_id=conduit_id,
                                            aetheric_frame=aetheric_frame)
                report["success"].append(spell_id)
            except Exception as e:
                report["failed"][spell_id] = str(e)
        return report

    def _remove_all_spells_from_contract(self, *, conduit: IConduit = None, conduit_id: UUID = None, aetheric_frame = "default") -> bool | None:
        """
        Internal

        Removes all spell contracts associated with this conduit.
        :return: bool
        """
        if self._sealed:
            raise RuntimeError("Cannot validate contracts in a sealed Conduit Ward.")

        # Check if conduit is provided, if not, resolve it from conduit_id
        conduit_id, conduit = self._check_conduit_id_and_conduit(conduit, conduit_id, aetheric_frame)

        # Check if contract exists for the conduit if not raise an error. Link must exist prior to spell contract initiation.
        if (contract := self._find_contract_by_id(conduit_id)) is not None:
            with contract._lock:
                # Clear all spells from the contract
                contract._clear_contract()

                # Remove all spells from each conduit spellbook
                ward_a = contract._ward_a
                ward_b = contract._ward_b

                # Remove all spells from spellbook
                ward_a._conduit._spellbook._clear_contracted_spells_for_conduit(conduit_id)
                ward_b._conduit._spellbook._clear_contracted_spells_for_conduit(conduit_id)
        else:
            raise RuntimeError(f"No contract found for conduit ID {conduit_id}")

    def _get_all_spells_in_contracts(self, validate: bool = True) -> Optional[dict[str, list[Tuple[str, 'ISpell']]]]:
        """
        Internal

        Retrieves all contracted spells across all active contracts involving this conduit.

        This method walks all symmetric contracts and returns the spell ID and spell object
        pairs available to this conduit from its peers. Useful for full introspection
        into what powers have been granted from all linked conduits.

        :param validate: Whether to validate contract consistency before retrieval.
        :return: A dictionary mapping conduit IDs to lists of (spell_id, ISpell) tuples.
                 Returns None if no contracts are found.
        """
        if self._sealed:
            raise RuntimeError("Cannot validate contracts in a sealed Conduit Ward.")

        if validate:
            validation = self._validate_contracts_and_define()
            if not all(validation.values()):
                raise RuntimeError(
                    "One or more contracts are invalid. Please validate contracts before retrieving spells.")

        spells_in_contracts = {}

        with self._lock:
            for contract_id, contract in self._contracts.items():
                try:
                    peer_ward = contract._get_peer(self)
                    peer_conduit = peer_ward._conduit
                    detail_map = contract._get_detail_map(self)

                    spells = []
                    for spell_id, detail in detail_map.items():
                        spell = peer_conduit._spellbook._find_contracted_spell(spell_id)
                        if spell is None:
                            if validate:
                                raise RuntimeError(
                                    f"Inconsistent state: Spell '{spell_id}' missing in peer's spellbook.")
                            continue
                        spells.append((spell_id, spell))

                    spells_in_contracts[peer_ward._id] = spells
                except Exception as e:
                    if validate:
                        raise RuntimeError(f"Failed to inspect contract {contract_id}: {e}")

        return spells_in_contracts if spells_in_contracts else None

    def _get_spell_in_contracts(self, spell_id: str) -> Optional[tuple[UUID, ISpell]]:
        """
        Internal

        Attempts to retrieve a specific spell from the active contracts.

        This will search through all known contracts, across both sides, to find
        the spell either by direct object or by its ID.

        :param spell_id: The explicit spell ID to search for.
        :return: Conduit ID and ISpell tuple if found, otherwise None.
        """
        if self._sealed:
            raise RuntimeError("Cannot retrieve contracted conduits from a sealed Conduit Ward.")

        with self._lock:
            for contract in self._contracts.values():
                ward = contract._find_spell_in_ward(spell_id)
                if ward:
                    spell = ward._conduit.find_contracted_spell(spell_id)
                    if spell:
                        return (ward._id, spell)

        return None

    def _get_spells_in_contract_by_conduit(self, conduit_id: UUID) -> dict[str, list[tuple[str, ISpell]]] | None:
        """
        Internal

        Retrieves all spells exchanged with a specific conduit by its unique ID.

        This includes both spells this conduit has been granted from the peer, and
        spells this conduit has allowed the peer to use — depending on contract terms.

        :param conduit_id: The UUID of the target conduit.
        :return: A dictionary mapping roles ("inbound", "outbound") to lists of (spell_id, ISpell) tuples.
                 Returns None if no such conduit is linked.
        """
        if self._sealed:
            raise RuntimeError("Cannot retrieve contracted spells from a sealed Conduit Ward.")

        with self._lock:
            contract = self._find_contract_by_id(conduit_id)
            if not contract:
                return None

            spells_result = {
                "inbound": [],  # spells we received from them
                "outbound": []  # spells we granted to them
            }

            # Peer side
            peer_ward = contract._get_peer(self)
            peer_conduit = peer_ward._conduit
            peer_map = contract._get_detail_map(self)
            for spell_id, detail in peer_map.items():
                spell = peer_conduit._spellbook._find_contracted_spell(spell_id)
                if spell:
                    spells_result["inbound"].append((spell_id, spell))

            # Our side
            our_map = contract._get_detail_map(peer_ward)
            for spell_id, detail in our_map.items():
                spell = self._conduit._spellbook._find_contracted_spell(spell_id)
                if spell:
                    spells_result["outbound"].append((spell_id, spell))

            return spells_result if spells_result["inbound"] or spells_result["outbound"] else None

    def _get_spells_in_contract_by_conduit_name(self, conduit_name: str) -> dict[str, list[tuple[str, ISpell]]] | None:
        """
        Internal

        Retrieves all spells exchanged with a specific conduit by its declared name.

        Mirrors `_get_spells_in_contract_by_conduit` but uses a human-readable name
        instead of UUID. Useful for introspection and debugging.

        :param conduit_name: The name identifier of the target conduit.
        :return: A dictionary of spell IDs to (spell_id, ISpell) tuples, or None if not found.
        """
        if self._sealed:
            raise RuntimeError("Cannot retrieve contracted spells from a sealed Conduit Ward.")
        if not conduit_name or not isinstance(conduit_name, str):
            raise ValueError("Conduit name must be a non-empty string.")

        with self._lock:
            for contract in self._contracts.values():
                peer_ward = contract._get_peer(self)
                peer_conduit = peer_ward._conduit
                if getattr(peer_conduit, "_name", None) == conduit_name:
                    return self._get_spells_in_contract_by_conduit(peer_ward._id)

        return None

    def _get_contracted_conduits(self) -> list[Tuple[str, IConduit]] | None:
        """
        Internal

        Returns all conduits that currently have active spell contracts with this conduit.

        This includes all linked conduits regardless of whether they initiated the link,
        as contracts are symmetrical. Useful for auditing relationships and walking the
        dependency graph.

        :return: A list of (conduit_id, IConduit) tuples. Returns None if no links exist.
        """
        if self._sealed:
            raise RuntimeError("Cannot retrieve contracted conduits from a sealed Conduit Ward.")

        contracted_conduits = []
        with self._lock:
            for contract_id, contract in self._contracts.items():
                peer_ward = contract._get_peer(self)
                peer_conduit = peer_ward._conduit
                contracted_conduits.append((peer_ward._id, peer_conduit))

        return contracted_conduits if contracted_conduits else None

    def _describe_contract(self, conduit_id: UUID) -> dict:
        """
        Internal

        Returns a detailed description of the contract, including spell counts,
        permissions, and peer metadata.
        """
        if self._sealed:
            raise RuntimeError("Cannot describe contract from a sealed Conduit Ward.")

        with self._lock:
            contract = self._contracts.get(conduit_id)
            if not contract:
                raise RuntimeError(f"No contract found with conduit ID: {conduit_id}")

            peer_ward = contract._get_peer(self)
            peer_conduit = peer_ward._conduit
            detail_map = contract._get_detail_map(self)

            return {
                "contract_id": conduit_id,
                "peer_conduit_name": getattr(peer_conduit, "_name", "Unknown"),
                "spell_count": len(detail_map),
                "spells": [
                    {
                        "spell_id": spell_id,
                        "permissions": detail.permissions.name,
                    }
                    for spell_id, detail in detail_map.items()
                ]
            }

    def _validate_contracts_and_define(self) -> dict[UUID, bool]:
        """
        Internal

        Validates that each contract is symmetrical in terms of what was borrowed and ensures
        all referenced spells exist in the respective peer spellbooks.
        """
        if self._sealed:
            raise RuntimeError("Cannot validate contracts in a sealed Conduit Ward.")

        results = {}
        with self._lock:
            for contract_id, contract in self._contracts.items():
                try:
                    valid = True
                    for ward in (contract._ward_a, contract._ward_b):
                        peer = contract._get_peer(ward)
                        peer_book = peer._conduit._spellbook
                        detail_map = contract._get_detail_map(ward)

                        for spell_id, detail in detail_map.items():
                            spell = peer_book._find_contracted_spell_by_id(spell_id, ward._id)
                            if spell is None or spell.permissions != detail.permissions:
                                valid = False
                                break

                        if not valid:
                            break

                    results[contract_id] = valid

                except Exception:
                    results[contract_id] = False

        return results


    def _validate_received_contracts(self) -> bool:
        """
        Internal

        Validates all contracts associated with this conduit ward.

        This checks that each contract is symmetrical, spell maps are consistent,
        and that no dangling references exist.

        Returns:
            bool: True if all contracts are valid, False otherwise.
        """
        results = self._validate_contracts_and_define()
        return all(results.values()) if results else False

#endregion Spellbinding API
#region Cleanup
    def seal(self):
        """
        Seals the conduit ward, preventing any further modifications.
        """
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