#    Copyright [2025] [Mark Thomas Geleta]
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0

import threading
from logging import warning
from typing import Optional, Type, Any, Tuple
from uuid import UUID
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.spellbook.existence.existence import Existence
from melder.utilities.concurrent_set import ConcurrentSet
from melder.utilities.interfaces import IConduit, ISpellbook, IConduitCloud, ISpell
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.aether import Aether
from melder.aether.conduit.meld.debugging.debugging import ConduitCreationContext
from melder.spellbook.configuration.configuration import Configuration
from melder.aether.conduit.meld.meld import Meld
from melder.aether.conduit.conduit_ward.conduit_ward import ConduitWard
from threading import RLock
from melder.aether.conduit.creations.creations import Creations, LesserCreations

#region Conduit
class Conduit(IConduit):
    """
    A Conduit is a modular graph node that behaves like a scope and a factory.

    It can spawn lesser Conduits, link to other Conduits if dynamic mode is enabled,
    and manage the lifecycle of services registered inside itself.
    """

    _aether = Aether()

    def __init__(self, spellbook: ISpellbook, configuration: Configuration, conduit_state: ConduitState, aetheric_frame: str, policy: Policies, name: Optional[str] = None):
        """
        Public API

        Initializes a new Conduit.

        Args:
            spellbook (Spellbook): The Spellbook governing this Conduit.
            configuration (Configuration): The locked system configuration.
            conduit_state (str): The role of this Conduit ('normal' or 'lesser').
            name (str, optional): An optional name for easier identification.
        """
        super().__init__()
        # General Init
        self._lock: threading.RLock = RLock()
        self._name = name
        self.__debugger_mode__ = False
        self.__dynamic_environment__ = False
        self._creation_context = ConduitCreationContext()
        self._aetheric_frame = aetheric_frame

        # Special Configuration
        self._configuration = configuration
        self._conduit_state = conduit_state  # can be normal, lesser
        self._creations = self._creations_configuration(configuration)
        self._spellbook: ISpellbook = spellbook
        self._meld = Meld(self._creations, self._spellbook) # instance melder which is used by the conduit to create objects

        # Internal configuration
        self._apply_configuration_flags()
        self._conduit_ward = ConduitWard(self, self.__dynamic_environment__, self._conduit_state, policy) # The conduit ward is responsible for maintaining the links between conduits and their behaviours.

        if self._conduit_state == ConduitState.normal:
            self._add_conduit_to_aether()
            self._add_spells_to_aether()
            if self.__dynamic_environment__ and self._name is not None:
                Conduit._aether._register_conduit_cloud(self, self._aetheric_frame)
        elif self._conduit_state == ConduitState.lesser:
            if self._name is not None:
                warning("Lesser conduits cannot have a name. self._name is now set to None.")
            self._name = None

#region Utilities
    def __repr__(self):
        """
        Public API

        Returns a string representation of the Conduit instance.
        :return:
        """
        return (
            f"<Conduit name={self.name} "
            f"id={self._creation_context._conduit_id}>"
        )

#endregion Utilities

#region Properties
    @property
    def name(self) -> str:
        """
        Public API

        Returns the name of this Conduit. Name must be created during conduit creation.
        """
        return self._name if self._name else None


    @name.setter
    def name(self, name: str):
        """
        Public API

        Allows user to name conduit if available
        :return:
        """
        if self._name is not None:
            raise RuntimeError("Conduit name is set.")
        self._name = name

    @property
    def __creation_context__(self) -> ConduitCreationContext:
        """
        Public API

        This property exposes the internal creation metadata for this conduit,
        including unique ID, creation path, and lifecycle configuration context.

        Intended for:
        - Advanced diagnostics
        - Contract validation systems
        - Internal resolver systems
        """
        return self._creation_context
#endregion
#region Conduit Configuration
    def register_conduit_cloud(self, conduit: IConduit):
        """
        Public API

        Registers a conduit in the dynamic mode registry. You can use this method if you forgot to name your conduit in order
        to name it afterward and register it. You can only register it once.
        :param conduit:
        :return:
        """
        if self.__dynamic_environment__ == False:
            raise RuntimeError("Dynamic environment is not enabled. Cannot register in the conduit cloud.")
        if self._conduit_state == ConduitState.lesser:
            raise RuntimeError("Lesser conduits cannot register in the conduit cloud.")
        if self._name is None:
            raise RuntimeError("Conduit name is not set. Please set a name before registering in the conduit cloud.")
        if self.__dynamic_environment__:
            Conduit._aether._register_conduit_cloud(conduit, self._aetheric_frame)

    def _apply_configuration_flags(self):
        """
        Internal

        Sets the environment mode and debugging mode for this Conduit
        based on the configuration instance passed.
        """
        if self._configuration.get_property("system_state") == "automatic":
            self.__dynamic_environment__ = False
        elif self._configuration.get_property("system_state") == "dynamic":
            self.__dynamic_environment__ = True

        if self._configuration.get_property("debugging"):
            self.__debugger_mode__ = True

    def _add_conduit_to_aether(self) -> None:
        """
        Internal

        Adds the newly created Conduit into the shared Aether world.

        Args:
            conduit (Conduit): The Conduit instance to add.
        """
        if Conduit._aether is None:
            raise RuntimeError("Aether is not initialized.")
        Conduit._aether._add_conduit(self, self._aetheric_frame)


    def _creations_configuration(self, configuration: Configuration) -> Creations or LesserCreations:
        """
        Internal

        Returns the current creations configuration for this Conduit.
        """
        if self._conduit_state == ConduitState.lesser:
            return LesserCreations(configuration.get_property("disposal"), configuration.get_property("disposal_method_names"))
        elif self._conduit_state == ConduitState.normal:
            return Creations(configuration.get_property("disposal"), configuration.get_property("disposal_method_names"))
        else:
            raise RuntimeError("Conduit state is unknown")

#endregion Conduit Configuration
#region Conduit Management
    def upgrade_to_normal(self, name: Optional[str] = None) -> None:
        """
        Public API

        Upgrades this Conduit to a normal state. This allows the conduit to create its own links
        through the aether system. This will fork this conduit into a new tree and create new links with the parent.
        This conduit and its children go with it, only a normal scope can access the spellbook to bind new spells.

        This conduit will begin as a lesser_conduit policy conduit then change automatically after a single spell is registered and not just contracted.

        Please name the conduit if your intention is to add it to the Conduit Cloud.
        :return:
        """
        with self._lock:
            if not self.__dynamic_environment__:
                raise RuntimeError("Dynamic environment is not enabled. Cannot upgrade to normal conduit.")

            if self._conduit_state != ConduitState.lesser:
                raise RuntimeError("Only lesser conduits can be upgraded.")

            # Step 1: Change state
            self._conduit_state = ConduitState.normal
            self._name = name

            # Step 2: Transfer creation data
            creations_data = self._creations.transfer_data_and_clear()

            # Step 3: Create new Creations and inject data
            new_creations = Creations(
                disposal_enabled=self._configuration.get_property("disposal"),
                disposal_method_names=self._configuration.get_property("disposal_method_names")
            )
            new_creations._upgrade_from_lesser_conduit(**creations_data)

            # Step 4: Replace the old creations
            self._creations = new_creations

            # Step 5: Reconfigure the conduit ward
            self._conduit_ward._convert_to_normal_conduit()

            # Step 6: Reconfigure the spellbook
            self._spellbook.create_new_preset_spellbook()

            # Step 7: Register as a full Conduit in Aether
            Conduit._add_conduit_to_aether(self)
            if self.__dynamic_environment__ and self._name is not None:
                Conduit._aether._register_conduit_cloud(self, self._aetheric_frame)


    def set_new_policy(self, policy: str) -> None:
        """
        Public API

        Sets a new policy for this Conduit. This is only allowed in dynamic mode.
        :param policy: The new policy to set.
        :return:
        """
        if not self.__dynamic_environment__:
            raise RuntimeError("Dynamic environment is not enabled. Cannot set new policy.")
        with self._lock:
            self._conduit_ward._set_new_policy(policy)

    def create_lesser_conduit(self) -> IConduit:
        """
        Public API

        Creates a lesser Conduit (child node) attached to this Conduit.

        Args:
            spellbook (Spellbook): The Spellbook to govern the new Conduit.
            name (str, optional): Optional name for the new Conduit.

        Returns:
            Conduit: The newly created lesser Conduit.
        """
        if self._sealed:
            raise RuntimeError("Cannot create a lesser Conduit in a sealed Conduit.")

        with self._lock:
            new_conduit = Conduit(
                spellbook=self._spellbook,
                configuration=self._configuration,
                conduit_state=ConduitState.lesser,
                aetheric_frame=self._aetheric_frame,
                policy=Policies.lesser_conduit
            )

        self._conduit_ward._link_lesser_conduit(new_conduit)

        return new_conduit


#endregion Conduit Management
#region Spellbook Management API
    def _add_spells_to_aether(self) -> None:
        """
        Internal

        Adds the newly created Conduit into the shared Aether world.

        Args:
            conduit (Conduit): The Conduit instance to add.
        """
        if Conduit._aether is None:
            raise RuntimeError("Aether is not initialized.")

        spell_set= ConcurrentSet(self._spellbook._spells.keys())
        Conduit._aether._add_spells_to_aether(self.__creation_context__._conduit_id, spell_set, self._aetheric_frame)

    def get_conduit_by_spell_id(self, spell_id: str, aetheric_frame_name: str = "default") -> Optional[IConduit]:
        """
        Public API

        Retrieves the conduit that has registered a spell with the given spell_id.

        Args:
            spell_id (str): The unique identifier of the spell.
            aetheric_frame_name (str): The aetheric frame to check against. Defaults to "default".

        Returns:
            Optional[IConduit]: The conduit that registered the spell, or None if not found.
        """
        if self._sealed:
            raise RuntimeError("Cannot get conduits in a sealed Conduit.")
        with self._lock:
            return Conduit._aether._get_conduit_by_spell_id(spell_id, aetheric_frame_name)

    def check_spell_id(self, spell_id: str, aetheric_frame_name: str = "default") -> bool:
        """
        Public API

        Checks if a spell with the given spell_id exists in the spellbook.

        Args:
            spell_id (str): The unique identifier of the spell.
            aetheric_frame_name (str): The aetheric frame to check against. Defaults to "default".

        Returns:
            bool: True if the spell exists, False otherwise.
        """
        if self._sealed:
            raise RuntimeError("Cannot check spells in a sealed Conduit.")
        with self._lock:
            return Conduit._aether._check_for_spell(spell_id, aetheric_frame_name)

    def get_spell_by_id(self, spell_id: str, aetheric_frame_name: str = "default") -> Optional[Any]:
        """
        Public API

        Retrieves a spell by its unique identifier (spell_id) from the spellbook.

        Args:
            spell_id (str): The unique identifier of the spell.
            aetheric_frame_name (str): The aetheric frame to check against. Defaults to "default".

        Returns:
            Optional[Any]: The spell object if found, otherwise None.
        """
        if self._sealed:
            raise RuntimeError("Cannot get spells in a sealed Conduit.")
        with self._lock:
            conduit = self.get_conduit_by_spell_id(spell_id, aetheric_frame_name)
            return conduit._spellbook._find_spell(spell_id) if conduit else None

    def find_contracted_spell(self, spell_id: str) -> Optional[ISpell]:
        """
        Internal

        method to locate a spell by its spell_id.
        """
        return self._spellbook._find_contracted_spell(spell_id)

    def find_spell_id(self, spellframe: str, spell_name: str, binding_name: str) -> Optional[str]:
        """
        Public API

        Find a spell by its frame, name, and binding name.
        :param spellframe:
        :param spell_name:
        :param binding_name:
        :return: SHA256 of the spell
        """
        spell_id = self._spellbook.find_spell_id(spellframe, spell_name, binding_name)
        if not spell_id:
            raise ValueError(f"Spell '{spell_name}' not found in the spellbook.")
        return spell_id

    def find_spell_key(self, spellframe: str, spell_name: str, binding_name: str) -> Optional[tuple]:
        """
        Public API

        Find a spell by its frame, name, and binding name.
        :param spellframe:
        :param spell_name:
        :param binding_name:
        :return: spell's key
        """
        spell_key = self._spellbook.find_spell_key(spellframe, spell_name, binding_name)
        if not spell_key:
            raise ValueError(f"Spell '{spell_name}' not found in the spellbook.")
        return spell_key

    def inspect_spell(self, spell: Any, aetheric_frame= "default") -> Optional[str]:
        """
        Public API

        This method will inspect any object placed into it and check if it's
        a valid spell in the Aether Registry. Returns the SHA256 if found, else None
        :return:
        """
        with self._lock:
            return self._spellbook.inspect_spell(spell, aetheric_frame)

    def bind(self, *, spell, existence: str, permissions: str = "create", spellframe=None, name=None, **kwargs) -> str:
        """
        Bind a spell to the spellbook using the `Bind` system.

        This will:
        - Inspect and profile the spell.
        - Generate a fingerprint-based spell_id.
        - Register it in the global registry under the given permissions.
        - Optionally attach lifecycle hooks.

        ⚠️ Permissions govern how the spell may be accessed by other conduits
        under contract or delegation. They do **not** affect spell behavior
        within the owner conduit.

        ──────────────────────────────────────────────
        Permissions:
            - "read":
                Allows downstream conduits to use the spell but not modify or recreate it.

            - "create":
                Grants full access — including creation of new instances derived from the spell.

            - "block":
                Disallows all borrowing or usage from other conduits.
                Still usable within the owning conduit.

        Parameters:
            spell (object):
                The spell object to bind.

            existence (Existence):
                Declares the lifecycle type of the spell (e.g., SINGLETON, TRANSIENT).

            permissions (str):
                Access level exposed to downstream conduits.
                Must be one of: "read", "create", "block"
                Defaults to "create".

            spellframe (str, optional):
                Optional frame/grouping for organizational lookup.

            name (str, optional):
                Optional override for spell binding name.

            **kwargs:
                - pre_hooks: List[Callable] — Executed before casting.
                - activation_hooks: List[Callable] — Executed during casting.
                - post_hooks: List[Callable] — Executed after casting.

        Returns:
            str: The unique SHA256 spell ID.
        """
        if self._sealed:
            raise RuntimeError("Cannot bind spells in a sealed Conduit.")
        if not self._conduit_state == ConduitState.normal:
            raise RuntimeError("Only normal conduits can bind spells.")

        with self._lock:
            return self._spellbook.bind(spell=spell, existence=existence, spellframe=spellframe, name=name, permissions=permissions, **kwargs)

    def get_spell_permissions(self, spell_id: str) -> Optional[str]:
        """
        Public API

        Get the permissions for a spell by its spell_id.
        :param spell_id: SHA256 identifier of the spell.
        :return: The permissions associated with the spell, or None if not found.
        """
        spell = self._spellbook._find_spell(spell_id)
        if spell:
            return spell.permissions.name
        else:
            raise RuntimeError(f"Spell with ID {spell_id} not found in the spellbook.")

#endregion Spellbook Management API
#region fakemeld
    def meld(self, spell_name: str, spell_type: str, spellframe: Type = None):
        """
        Public API

        :param spell_name:
        :param spell_type:
        :param spellframe:
        :return:
        """
        raise NotImplementedError("Not ready yet, not even using real class")
        if spell_type == "class":
            class_spell = self._spellbook.get(spell_name)
            if not class_spell:
                raise ValueError(f"No class registered for spell '{spell_name}'")
            instance = class_spell()
            if spellframe and not isinstance(instance, spellframe):
                raise TypeError(
                    f"Spell '{spell_name}' does not comply with required SpellFrame '{spellframe.__name__}'")
            return instance

        elif spell_type == "method":
            method_spell = self._spellbook.get(spell_name)
            if not method_spell:
                raise ValueError(f"No method registered for spell '{spell_name}'")
            result = method_spell()
            if spellframe and not isinstance(result, spellframe):
                raise TypeError(
                    f"Spell '{spell_name}' does not comply with required SpellFrame '{spellframe.__name__}'")
            return result

        else:
            raise ValueError(f"Invalid spell type '{spell_type}'")
#endregion
#region Conduit Cloud
    def get_conduit_cloud(self) -> IConduitCloud:
        """
        Public API

        Returns the conduit cloud. The conduit cloud is a registry of all conduits it behaves
        like an abstractfactory object under the best circumstances. Users should separate their objects into
        different conduits and use the conduit cloud to access them. This is a global registry of all conduits.

        This object is designed to be used in dynamic mode only. It mitigates the service locator pattern.
        :return:
        """
        if self._conduit_state == ConduitState.lesser:
            raise RuntimeError("Lesser conduits cannot access the conduit cloud.")
        if self.__dynamic_environment__:
            raise RuntimeError("Dynamic environment is not enabled. Cannot access conduit cloud.")
        return Conduit._aether._get_conduit_cloud(self._aetheric_frame)

#endregion Conduit Cloud
#region Aether API
    def get_conduit_by_id(self, conduit_id: UUID, aetheric_frame:str = "default") -> Optional[IConduit]:
        """
        Public API

        Retrieves a conduit by its unique ID.

        Args:
            conduit_id (UUID): The unique identifier of the conduit.
            aetheric_frame (str): The aetheric frame to check against. Defaults to "default".

        Returns:
            Optional[IConduit]: The conduit instance if found, otherwise None.
        """
        if self._sealed:
            raise RuntimeError("Cannot get conduits in a sealed Conduit.")
        if not isinstance(aetheric_frame, str):
            raise TypeError(f"Expected aetheric_frame to be a string, got {type(aetheric_frame).__name__}")
        if aetheric_frame == "default":
            aetheric_frame = self._aetheric_frame

        with self._lock:
            return Conduit._aether._get_conduit_by_id(conduit_id, aetheric_frame)

    def get_conduit_by_name(self, name: str, aetheric_frame:str = "default") -> Optional[IConduit]:
        """
        Public API

        Retrieves a conduit by its name.

        Args:
            name (str): The name of the conduit.
            aetheric_frame (str): The aetheric frame to check against. Defaults to "default".

        Returns:
            Optional[IConduit]: The conduit instance if found, otherwise None.
        """
        if self._sealed:
            raise RuntimeError("Cannot get conduits in a sealed Conduit.")
        if not isinstance(aetheric_frame, str):
            raise TypeError(f"Expected aetheric_frame to be a string, got {type(aetheric_frame).__name__}")
        if aetheric_frame == "default":
            aetheric_frame = self._aetheric_frame
        with self._lock:
            return Conduit._aether._get_conduit_by_name(name, aetheric_frame)

#endregion Aether API
#region Conduit Ward API
    def link(self, target_conduit: IConduit) -> bool:
        """
        Public API

        Attempts to link this Conduit to another Conduit.

        Linking is only allowed if the world is in dynamic mode.

        Args:
            target_conduit (Conduit): The target Conduit to link to.

        Returns:
            bool: True if linking succeeds (currently not implemented).
        """
        if self._sealed:
            raise RuntimeError("Cannot link to a sealed Conduit.")
        if not self.__dynamic_environment__:
            raise RuntimeError("Dynamic environment is not enabled. Cannot manage link services.")
        if not isinstance(target_conduit, IConduit):
            raise TypeError(f"Expected IConduit instance, got {type(target_conduit).__name__}")
        if not target_conduit.__creation_context__._conduit_id:
            raise RuntimeError("Target conduit does not have a valid creation context.")
        with self._lock:
            return self._conduit_ward._link(target_conduit)

    def sever_link(self, target_conduit: IConduit) -> bool:
        """
        Public API

        Sever the link between this Conduit and its target Conduit. This will also validate if the link exists, if it can be severed, and
        it will remove the link and contracted spells from the Conduit.

        This is meant for internal use please do not use this outside of the class.
        """
        if self._sealed:
            raise RuntimeError("Cannot sever a link in a sealed Conduit.")
        if not self.__dynamic_environment__:
            raise RuntimeError("Dynamic environment is not enabled. Cannot manage link services.")
        with self._lock:
            return self._conduit_ward._sever_link(target_conduit)


    def get_links(self):
        """
        Public API

        Returns a list of all links associated with this conduit. Excluding lesser conduits.
        :return:
        """
        if self._sealed:
            raise RuntimeError("Cannot get links in a sealed Conduit.")
        if not self.__dynamic_environment__:
            raise RuntimeError("Dynamic environment is not enabled. Cannot manage link services.")
        with self._lock:
            return self._conduit_ward._get_links()

    def get_lesser_conduit(self, conduit_id: UUID) -> Optional[IConduit]:
        """
        Internal

        Returns a specific lesser conduit linked to this conduit by its ID.

        Args:
            conduit_id (UUID): The ID of the conduit to retrieve.

        Returns:
            Optional[IConduit]: The linked conduit if found, otherwise None.
        """
        if self._sealed:
            raise RuntimeError("Cannot get lesser conduits from a sealed Conduit.")
        with self._lock:
            return self._conduit_ward._get_lesser_conduit(conduit_id)


    def get_initiated_conduit(self, conduit_id: UUID) -> Optional[IConduit]:
        """
        Public API

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
        with self._lock:
            return self._conduit_ward._get_initiated_conduit(conduit_id)


    def get_provider_conduit(self, conduit_id: UUID) -> Optional[IConduit]:
        """
        Public API

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
        with self._lock:
            return self._conduit_ward._get_provider_conduit(conduit_id)


    def get_initiated_conduits(self) -> list[IConduit]:
        """
        Public API

        Returns a list of all conduits that this conduit has initiated contracts toward.

        This method retrieves all conduits that this conduit has linked to as the initiator.

        Returns:
            list[IConduit]: A list of conduits that this conduit has initiated contracts toward.
        """
        if self._sealed:
            raise RuntimeError("Cannot get linked conduits from a sealed Conduit Ward.")
        with self._lock:
            return self._conduit_ward._get_initiated_conduits()

    def get_provider_conduits(self) -> list[IConduit]:
        """
        Public API

        Returns a list of all conduits that have linked to this conduit as the provider.

        This method retrieves all conduits that have initiated contracts to this conduit.

        Returns:
            list[IConduit]: A list of conduits that have linked to this conduit as the provider.
        """
        if self._sealed:
            raise RuntimeError("Cannot get linked conduits from a sealed Conduit Ward.")
        with self._lock:
            return self._conduit_ward._get_provider_conduits()

    def seal_lesser_conduits(self):
        """
        Public API

        Seals all lesser conduits linked to this conduit.
        This is used to prevent further operations on lesser conduits.
        Generally used when upgrading a lesser conduit to a normal conduit.

        This method is called when you seal a conduit, or you can call it manually to seal all lesser conduits.
        """
        if self._sealed:
            raise RuntimeError("Cannot get linked conduits from a sealed Conduit.")
        self._conduit_ward.seal_all_lesser_conduits()

#endregion Conduit Ward API
#region Spell Contracting API
    def _qualify_contracts(self):
        """
        Internal

        This method is used to qualify the contracts for spellbinding.
        :return:
        """
        if self._sealed:
            raise RuntimeError("Cannot interact with spell contracts in a sealed Conduit.")
        if self._conduit_state != ConduitState.normal:
            raise RuntimeError("Only normal conduits can create spell contracts.")
        if not self.__dynamic_environment__:
            raise RuntimeError("Dynamic environment is not enabled. Cannot interact with spell contracts.")


    def add_spell_to_contract(self, *, spell: ISpell = None, spell_id: str = None, conduit: IConduit = None, conduit_id: UUID = None,
                               permissions: str = "create", aetheric_frame = "default") -> bool | None:
        """
        Public API

        Establishes a single spell contract between this conduit and another target conduit.

        This allows one conduit to borrow or grant a specific spell, identified either by object or ID,
        to/from a peer conduit. The contract defines the permissions under which the spell can be used.

        You may provide either a `spell` object or a `spell_id`. The target conduit may be specified directly
        or resolved via its ID and aetheric frame.

        :param spell: The spell object to contract (optional if spell_id is provided).
        :param spell_id: The unique ID of the spell to contract (optional if spell is provided).
        :param conduit: The target conduit to contract with.
        :param conduit_id: The UUID of the target conduit (used if `conduit` is not provided).
        :param permissions: The permission level granted for this spell (default is "create").
        :param aetheric_frame: Optional frame override used to locate the target conduit.
        :return: True if the contract was created, False otherwise.
        """
        self._qualify_contracts()
        return self._conduit_ward._add_spell_to_contract(spell=spell, spell_id=spell_id, conduit=conduit, conduit_id=conduit_id,
                                                          permissions=permissions, aetheric_frame=aetheric_frame)


    def add_spells_to_contract(self, spell_ids: list[str], conduit: IConduit = None, conduit_id: UUID = None,
                               permissions: str = "create", aetheric_frame = "default") -> dict:
        """
        Public API

        Establishes multiple spell contracts with another conduit in a single operation.

        Allows you to bulk-grant or bulk-borrow spells by specifying a list of spell IDs. Each spell
        will be contracted using the same permission level. Useful when synchronizing multiple
        behaviors between agents or systems.

        :param spell_ids: List of spell IDs to contract.
        :param conduit: The target conduit to contract with.
        :param conduit_id: The UUID of the target conduit (used if `conduit` is not provided).
        :param permissions: The permission level granted for all spells (default is "create").
        :param aetheric_frame: Optional frame override used to locate the target conduit.
        :return: Dictionary of spell_id -> success boolean for each attempted contract.
        """
        self._qualify_contracts()
        return self._conduit_ward._add_spells_to_contract(spell_ids=spell_ids,
                                                          conduit=conduit, conduit_id=conduit_id,
                                                          permissions=permissions, aetheric_frame=aetheric_frame)

    def remove_spell_from_contract(self, *, spell: ISpell = None, spell_id: str = None, conduit: IConduit = None,
                                    conduit_id: UUID = None, aetheric_frame = "default") -> bool | None:
        """
        Public API

        Removes a single spell contract between this conduit and another.

        Either the `spell` or `spell_id` can be provided to specify the contract to dissolve.
        Once removed, the spell is no longer accessible across the link.

        :param spell: The spell object to remove (optional if `spell_id` is provided).
        :param spell_id: The unique ID of the spell to remove.
        :param conduit: The target conduit involved in the contract.
        :param conduit_id: UUID of the target conduit (used if `conduit` not provided).
        :param aetheric_frame: Optional frame override to resolve the target conduit.
        :return: True if the spell was successfully removed from the contract, False otherwise.
        """
        self._qualify_contracts()
        return self._conduit_ward._remove_spell_from_contract(spell=spell, spell_id=spell_id, conduit=conduit,
                                                              conduit_id=conduit_id, aetheric_frame=aetheric_frame)

    def remove_spells_from_contract(self, *, spell_ids: list[str] = None, conduit: IConduit = None,
                                     conduit_id: UUID = None, aetheric_frame = "default") -> dict:
        """
        Public API

        Removes multiple spells from an existing contract with a target conduit.

        Useful for bulk cleanup or revocation when retiring behaviors or permissions.

        :param spell_ids: List of spell IDs to remove.
        :param conduit: Target conduit object.
        :param conduit_id: UUID of target conduit (used if `conduit` is not provided).
        :param aetheric_frame: Optional frame override.
        :return: Dictionary of spell_id -> success boolean for each removal attempt.
        """
        self._qualify_contracts()
        return self._conduit_ward._remove_spells_from_contract(spell_ids=spell_ids, conduit=conduit,
                                                                conduit_id=conduit_id, aetheric_frame=aetheric_frame)

    def _remove_all_spells_from_contract(self, *, conduit: IConduit = None, conduit_id: UUID = None, aetheric_frame = "default") -> bool | None:
        """
        Public API

        Dissolves all spell contracts between this conduit and the specified target.

        All borrowed and granted spells in the active contract will be severed, effectively
        resetting the relationship between the two conduits.

        :param conduit: Target conduit object.
        :param conduit_id: UUID of target conduit (used if `conduit` is not provided).
        :param aetheric_frame: Optional frame override.
        :return: True if all spells were successfully removed, False otherwise.
        """
        self._qualify_contracts()
        return self._conduit_ward._remove_all_spells_from_contract(conduit=conduit, conduit_id=conduit_id, aetheric_frame=aetheric_frame)

    def get_all_spells_in_contracts(self, validate: bool = True) -> Optional[dict[str, list[Tuple[str, 'ISpell']]]]:
        """
        Public API

        Retrieves all active spells that this conduit has access to through its contracts.

        Walks all current spell contracts and collects the spell IDs and objects that are currently
        borrowed from other conduits. Optionally validates contracts before collecting data.

        :param validate: If True, performs contract consistency validation before returning data.
        :return: Dictionary mapping peer conduit UUIDs to lists of (spell_id, ISpell) tuples,
                 or None if no contracts exist.
        """
        self._qualify_contracts()
        if not isinstance(validate, bool):
            raise TypeError(f"Expected validate to be a boolean, got {type(validate).__name__}")
        return self._conduit_ward._get_all_spells_in_contracts(validate=validate)

    def get_spell_in_contracts(self, spell_id: str) -> Optional[tuple[UUID, ISpell]]:
        """
        Public API

        Searches all known contracts to find the origin of a specific spell.

        Looks for a specific spell by ID and returns the UUID of the conduit it's contracted from
        along with the spell object, if found.

        :param spell_id: The unique ID of the spell.
        :return: Tuple of (conduit_id, spell) if found, otherwise None.
        """
        self._qualify_contracts()
        if not isinstance(spell_id, str):
            raise TypeError(f"Expected spell_id to be a string, got {type(spell_id).__name__}")
        return self._conduit_ward._get_spell_in_contracts(spell_id)

    def get_spells_in_contract_by_conduit(self, conduit_id: UUID) -> dict[str, list[tuple[str, ISpell]]] | None:
        """
        Public API

        Retrieves all spell contracts associated with a specific peer conduit, identified by UUID.

        Returns a detailed list of all spells that this conduit currently accesses or has granted
        through its relationship with the specified peer.

        :param conduit_id: UUID of the target conduit.
        :return: Dictionary of spell_id -> (spell_id, ISpell) tuples or None if not found.
        """
        self._qualify_contracts()
        if not isinstance(conduit_id, UUID):
            raise TypeError(f"Expected conduit_id to be a UUID, got {type(conduit_id).__name__}")
        return self._conduit_ward._get_spells_in_contract_by_conduit(conduit_id)

    def get_spells_in_contract_by_conduit_name(self, conduit_name: str) -> dict[str, list[tuple[str, ISpell]]] | None:
        """
        Public API

        Retrieves all spell contracts associated with a peer conduit identified by name.

        Same as `get_spells_in_contract_by_conduit`, but performs resolution using a
        human-readable name instead of UUID. Useful for logs, debugging, or UI.

        :param conduit_name: Name of the peer conduit.
        :return: Dictionary of spell_id -> (spell_id, ISpell) tuples or None if not found.
        """
        self._qualify_contracts()
        if not isinstance(conduit_name, str):
            raise TypeError(f"Expected conduit_name to be a string, got {type(conduit_name).__name__}")
        return self._conduit_ward._get_spells_in_contract_by_conduit_name(conduit_name)


    def get_contracted_conduits(self) -> list[Tuple[str, IConduit]] | None:
        """
        Public API

        Lists all conduits that have an active spell contract with this conduit.

        Each returned conduit represents a peer in the current dynamic spell network.
        This is useful for visualizing the relationship graph or performing audits.

        :return: List of (conduit_id, IConduit) tuples, or None if no contracts exist.
        """
        self._qualify_contracts()
        return self._conduit_ward._get_contracted_conduits()

    def _describe_contract(self, conduit_id: UUID) -> dict:
        """
        Public API

        Produces a detailed diagnostic summary of a contract established with a specific conduit.

        This method inspects the contract associated with the provided `conduit_id` and returns metadata
        including the peer conduit’s name, the number of active spells involved, and permission levels
        granted for each spell. It is primarily used for debugging, introspection, and UI inspection tools.

        Useful for tracing spell relationships, verifying proper link formation, or exposing data
        for system monitoring.

        :param conduit_id: UUID of the peer conduit whose contract you wish to examine.
        :return: Dictionary containing:
            - contract_id: UUID of the contract
            - peer_conduit_name: Human-readable name of the peer conduit
            - spell_count: Total number of spells in the contract
            - spells: List of dictionaries with:
                - spell_id: Unique spell identifier
                - permissions: Permission level granted to this spell
        """
        self._qualify_contracts()
        return self._conduit_ward._describe_contract(conduit_id)

    def validate_contracts_and_define(self) -> dict[UUID, bool]:
        """
        Public API

        Validates all known contracts attached to this conduit and confirms mutual agreement and consistency.

        This method performs a deep validation pass over each contract by ensuring:
            - Both sides list the same spells in the contract
            - Permission levels are symmetrical
            - All referenced spells are valid and exist in the correct peer spellbook

        Contracts that fail validation are marked as `False` in the returned dictionary.
        This is critical for maintaining integrity across a distributed or multi-agent conduit network.

        :return: Dictionary mapping contract UUIDs to validation results:
                 - True: Contract is valid and consistent
                 - False: Contract is malformed or inconsistent
        """
        self._qualify_contracts()
        return self._conduit_ward._validate_contracts_and_define()


    def validate_received_contracts(self) -> bool:
        """
        Public API

        Performs a high-level validation check across all contracts involving this conduit.

        Internally calls `_validate_contracts_and_define` and aggregates the results to determine
        whether every connected contract is structurally valid and symmetrical. This is typically used
        during diagnostics, debugging, or safety checks before major state changes (e.g., disposing,
        spell resolution, or spell reflection).

        :return: True if all active contracts pass validation, False otherwise.
        """
        self._qualify_contracts()
        return self._conduit_ward._validate_received_contracts()


#endregion Spell Contracting API
#region Cleanup and Disposal

    def seal(self):
        """
        Public API

        Seals this Conduit and all its lesser Conduits.

        Prevents further operation, releases internal references,
        and unregisters from the Aether.
        """
        raise NotImplementedError("Sealing is not implemented yet.")
        if self._sealed:
            return
        with self._lock:
            if self._sealed:
                return

            # Phase 1: Cleanup and disposal
            self._clean_up_lesser_conduits_links()
            self._clean_up_links()
            self._spellbook.seal()
            self._creations.seal()

            # Phase 2: De-reference internal structures
            self._spellbook = None
            self._creations = None
            self._creation_context = None

            # Phase 3: Deregister from the world
            if Conduit._aether and not Conduit._aether.sealed:
                Conduit._aether._remove_conduit(self, self._aetheric_frame)

            self._conduit_state = ConduitState.sealed
            self._sealed = True

#endregion Cleanup and Disposal
#endregion Conduit