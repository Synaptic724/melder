import threading
from logging import warning
from typing import Optional, Type, Any, Tuple
from uuid import UUID
import ulid
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.spellbook.configuration.system_state import SystemState
from melder.spellbook.existence.existence import Existence
from melder.utilities.data_structures.concurrent_set import ConcurrentSet
from melder.utilities.general_base.sealable import Sealable
from melder.utilities.interfaces.interfaces import IConduit, ISpellbook, IConduitCloud, ISpell, IConfiguration
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.aether import Aether
from melder.aether.conduit.meld.debugging.debugging import ConduitCreationContext
from melder.aether.conduit.meld.meld import Meld
from melder.aether.conduit.conduit_ward.conduit_ward import ConduitWard
from threading import RLock
from melder.aether.conduit.creations.creations import Creations
from melder.aether.conduit.creations.lesser_creations import LesserCreations


#region Conduit
class Conduit(Sealable, IConduit):
    """
    A Conduit is a modular graph node that behaves like a scope and a factory.

    It can spawn lesser Conduits, link to other Conduits if dynamic mode is enabled,
    and manage the lifecycle of services registered inside itself.
    """
    _aether = Aether()

    def __init__(self, spellbook: ISpellbook, configuration: IConfiguration, conduit_state: ConduitState,
                 aetheric_frame: str, policy: Policies, name: Optional[str] = None):
        """
        Public API

        Initializes a new Conduit.

        Args:
            spellbook (ISpellbook): The Spellbook governing this Conduit.
            configuration (IConfiguration): The locked system configuration.
            conduit_state (str): The role of this Conduit ('normal' or 'lesser').
            name (str, optional): An optional name for easier identification.
        """
        super().__init__()
        # General Init
        self._lock: threading.RLock = RLock()
        self._id: str = str(ulid.ULID())
        self._name: str = name
        self.__debugger_mode__: bool = False
        self.__dynamic_environment__: bool = False
        self._creation_context: ConduitCreationContext = ConduitCreationContext()
        self._aetheric_frame: str = aetheric_frame

        # Special Configuration
        if not isinstance(configuration, IConfiguration):
            raise TypeError(f"Expected IConfiguration instance, got {type(configuration).__name__}")

        self._configuration: IConfiguration = configuration
        self._conduit_state: ConduitState = conduit_state  # can be normal, lesser
        self._creations: Creations | LesserCreations = self._creations_configuration(configuration)
        self._spellbook: ISpellbook = spellbook
        self._meld: Meld = Meld(self._creations, self._spellbook) # instance melder which is used by the conduit to create objects

        # Internal configuration
        self._apply_configuration_flags()
        self._conduit_ward: ConduitWard = ConduitWard(self, self.__dynamic_environment__, self._conduit_state, policy) # The conduit ward is responsible for maintaining the links between conduits and their behaviours.

        if self._conduit_state == ConduitState.normal:
            self._add_conduit_to_aether()
            self._add_spells_to_aether()
            if self.__dynamic_environment__ and self._name is not None:
                Conduit._aether._register_conduit_cloud(self, self._aetheric_frame)
        elif self._conduit_state == ConduitState.lesser:
            if self._name is not None:
                warning("Lesser conduits cannot have a name. self._name is now set to None.")
            self._name = None

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
    def name(self) -> Optional[str]:
        """
        Public API

        Returns the name of this Conduit. Name must be created during conduit creation.
        """
        return self._name if self._name else None


    @name.setter
    def name(self, name: str) -> None:
        """
        Public API

        Allows user to name conduit if available

        Raises:
            RuntimeError: If the Conduit name is already set.
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

        Args:
            conduit (IConduit): The conduit instance to register.

        Raises:
            RuntimeError: If dynamic environment is not enabled.
            RuntimeError: If the conduit is a lesser conduit.
            RuntimeError: If the Conduit name is not set.
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
        if self._configuration.get_property("system_state") == SystemState.automatic:
            self.__dynamic_environment__ = False
        elif self._configuration.get_property("system_state") == SystemState.dynamic:
            self.__dynamic_environment__ = True

        if self._configuration.get_property("debugging"):
            self.__debugger_mode__ = True

    def _add_conduit_to_aether(self) -> None:
        """
        Internal

        Adds the newly created Conduit into the shared Aether world.

        Raises:
            RuntimeError: If Aether is not initialized.
        """
        if Conduit._aether is None:
            raise RuntimeError("Aether is not initialized.")
        Conduit._aether._add_conduit(self, self._aetheric_frame)


    def _creations_configuration(self, configuration: IConfiguration) -> Creations | LesserCreations:
        """
        Internal

        Returns the current creations configuration for this Conduit.

        Args:
            configuration (IConfiguration): The locked system configuration.

        Returns:
            Creations | LesserCreations: The appropriate creation manager based on conduit state.

        Raises:
            RuntimeError: If the Conduit state is unknown.
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

        Upgrades this Conduit from a lesser to a **normal** state.

        This process allows the conduit to create its own links through the Aether system.
        It effectively forks this conduit into a new tree, retaining its children and
        creation data, and establishes new links with the parent. Only a normal conduit
        can access the Spellbook to bind new spells.

        Please name the conduit if your intention is to add it to the Conduit Cloud.

        Args:
            name (str, optional): An optional name to assign to the upgraded conduit.

        Raises:
            RuntimeError: If the dynamic environment is not enabled.
            RuntimeError: If the current conduit state is not 'lesser'.
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

        Args:
            policy (str): The new policy to set, governing linking behavior.

        Raises:
            RuntimeError: If dynamic environment is not enabled.
        """
        if not self.__dynamic_environment__:
            raise RuntimeError("Dynamic environment is not enabled. Cannot set new policy.")
        with self._lock:
            self._conduit_ward._set_new_policy(policy)

    def create_lesser_conduit(self) -> IConduit:
        """
        Public API

        Creates a **lesser Conduit** (child node) attached to this Conduit.

        The lesser conduit inherits the parent's Spellbook and Configuration but is restricted
        in its ability to establish external links or register new spells.

        Returns:
            IConduit: The newly created lesser Conduit instance.

        Raises:
            RuntimeError: If the parent Conduit is sealed.
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

        Adds the newly created Conduit's initial spells into the shared Aether world's registry.

        Raises:
            RuntimeError: If Aether is not initialized.
        """
        if Conduit._aether is None:
            raise RuntimeError("Aether is not initialized.")

        spell_set= ConcurrentSet(self._spellbook._spells.keys())
        Conduit._aether._add_spells_to_aether(self.__creation_context__._conduit_id, spell_set, self._aetheric_frame)

    def get_conduit_by_spell_id(self, spell_id: str, aetheric_frame_name: str = "default") -> Optional[IConduit]:
        """
        Public API

        Retrieves the conduit that has registered a spell with the given spell_id.

        This method queries the Aether to find the original source conduit for a specific spell ID.

        Args:
            spell_id (str): The unique identifier of the spell.
            aetheric_frame_name (str): The aetheric frame to check against. Defaults to "default".

        Returns:
            Optional[IConduit]: The conduit that registered the spell, or None if not found.

        Raises:
            RuntimeError: If the Conduit is sealed.
        """
        if self._sealed:
            raise RuntimeError("Cannot get conduits in a sealed Conduit.")
        with self._lock:
            return Conduit._aether._get_conduit_by_spell_id(spell_id, aetheric_frame_name)

    def check_spell_id(self, spell_id: str, aetheric_frame_name: str = "default") -> bool:
        """
        Public API

        Checks if a spell with the given spell_id exists within the global Aether registry.

        Args:
            spell_id (str): The unique identifier of the spell to check.
            aetheric_frame_name (str): The Aetheric Frame to search within. Defaults to "default".

        Returns:
            bool: True if the Spell exists in the Aether, False otherwise.

        Raises:
            RuntimeError: If the Conduit is sealed.
        """
        if self._sealed:
            raise RuntimeError("Cannot check spells in a sealed Conduit.")
        with self._lock:
            return Conduit._aether._check_for_spell(spell_id, aetheric_frame_name)

    def get_spell_by_id(self, spell_id: str, aetheric_frame_name: str = "default") -> Optional[Any]:
        """
        Public API

        Retrieves a spell object by its unique identifier (spell_id) from the spellbook of its owner.

        The method first finds the owning conduit via Aether and then fetches the spell from that conduit's spellbook.

        Args:
            spell_id (str): The unique identifier of the spell.
            aetheric_frame_name (str): The aetheric frame to check against. Defaults to "default".

        Returns:
            Optional[Any]: The spell object if found, otherwise None.

        Raises:
            RuntimeError: If the Conduit is sealed.
        """
        if self._sealed:
            raise RuntimeError("Cannot get spells in a sealed Conduit.")
        with self._lock:
            conduit = self.get_conduit_by_spell_id(spell_id, aetheric_frame_name)
            return conduit._spellbook._find_spell(spell_id) if conduit else None

    def find_contracted_spell(self, spell_id: str) -> Optional[ISpell]:
        """
        Internal

        Method to locate a spell by its spell_id within this Conduit's **contracted** spells.

        Args:
            spell_id (str): The unique ID of the spell to find.

        Returns:
            Optional[ISpell]: The contracted spell instance, or None if not found.
        """
        return self._spellbook._find_contracted_spell(spell_id)

    def find_spell_id(self, spellframe: str, spell_name: str, binding_name: str) -> Optional[str]:
        """
        Public API

        Finds a spell's unique ID (SHA256) using its logical identifiers.

        Args:
            spellframe (str): The logical namespace or grouping label.
            spell_name (str): The name of the spell class or function.
            binding_name (str): The secondary key to distinguish the spell.

        Returns:
            Optional[str]: The unique SHA256 identifier of the spell.

        Raises:
            ValueError: If the spell is not found in the spellbook.
        """
        spell_id = self._spellbook.find_spell_id(spellframe, spell_name, binding_name)
        if not spell_id:
            raise ValueError(f"Spell '{spell_name}' not found in the spellbook.")
        return spell_id

    def find_spell_key(self, spellframe: str, spell_name: str, binding_name: str) -> Optional[tuple]:
        """
        Public API

        Finds a spell's primary lookup key using its logical identifiers.

        The key is typically a tuple used for internal retrieval within the spellbook.

        Args:
            spellframe (str): The logical namespace or grouping label.
            spell_name (str): The name of the spell class or function.
            binding_name (str): The secondary key to distinguish the spell.

        Returns:
            Optional[tuple]: The spell's key (frame, name, binding_name) tuple.

        Raises:
            ValueError: If the spell is not found in the spellbook.
        """
        spell_key = self._spellbook.find_spell_key(spellframe, spell_name, binding_name)
        if not spell_key:
            raise ValueError(f"Spell '{spell_name}' not found in the spellbook.")
        return spell_key

    def inspect_spell(self, spell: Any, aetheric_frame= "default") -> Optional[str]:
        """
        Public API

        Inspects any object to determine if it is a valid, registered spell in the Aether Registry.

        This method uses the Spellbook's internal reflection to identify the spell.

        Args:
            spell (Any): The class, function, or object instance to inspect.
            aetheric_frame (str): The Aetheric Frame to search within. Defaults to "default".

        Returns:
            Optional[str]: The SHA256 unique ID of the spell if found, otherwise None.
        """
        with self._lock:
            return self._spellbook.inspect_spell(spell, aetheric_frame)

    def bind(self, *, spell, existence: str, permissions: str = "create", spellframe=None, binding_name=None, **kwargs) -> str:
        """
        Binds a spell into the Spellbook for future instantiation and dependency injection.

        The `bind()` method registers a class, function, or object into Melder’s system,
        associating it with a lifecycle (`Existence`), a permission policy, and optional metadata.
        Once bound, the spell becomes available for resolution and casting within its conduit
        or across systems (depending on permissions).

        ──────────────────────────────────────────────
        🧠 Binding Overview:
            - Profiles the spell via reflection.
            - Computes a unique SHA256 `spell_id`.
            - Stores the spell into the internal spell registry.
            - Assigns its lookup key via `(spellframe, binding_name)`.
            - Applies lifecycle and permission policies.
            - Optionally attaches lifecycle hooks.

        ──────────────────────────────────────────────
        🛡️ Permissions (access control to other conduits):
            - `"read"`:
                Allows other conduits to *use* the spell but not create new instances.
                Useful for shared utilities or resources.

            - `"create"` (default):
                Allows other conduits to both use *and* create instances from this spell.

            - `"block"`:
                Completely blocks access to the spell from other conduits.
                Only the owning conduit can use or instantiate it.

        🔄 Existence (spell lifecycle):
            Determines how the spell instance is managed (singleton, transient, etc.).
            Use `Existence.unique`, `Existence.many`, etc., for fine-grained control.

        📦 Spellframe (optional):
            Logical namespace or grouping label.
            Often corresponds to a shared interface, protocol, or feature group.

        🔑 Binding Name (optional):
            Secondary key used to distinguish different versions or roles of the same type.
            Useful when multiple spells are bound under the same interface.

        ──────────────────────────────────────────────
        🪝 Lifecycle Hooks (optional `**kwargs`):

            - `pre_hooks`: List[Callable]
                Executed *before* the spell is constructed or cast.
                Can be used for validation, preparation, or logging.

            - `activation_hooks`: List[Callable]
                Executed *during* spell construction. Useful for modifying dependencies
                or adapting runtime context.

            - `post_hooks`: List[Callable]
                Executed *after* the spell has been cast. Often used for initialization,
                analytics, or final injection steps.

            ⚠️ All hooks must be callables.

        ──────────────────────────────────────────────
        Args:
            spell (Any): The class, function, or object to bind into the spellbook.
            existence (Existence): The lifecycle scope for this spell.
            permissions (str): Permission level exposed to other conduits ("read", "create", "block").
            spellframe (Optional[Any]): Logical interface or category for grouping.
            binding_name (Optional[str]): Name key to distinguish this spell among others in its frame.
            **kwargs:
                - pre_hooks (Optional[List[Callable]]): Hooks executed before casting.
                - activation_hooks (Optional[List[Callable]]): Hooks executed during casting/construction.
                - post_hooks (Optional[List[Callable]]): Hooks executed after casting/construction.

        Returns:
            str: The unique SHA256 `spell_id` associated with the bound spell.

        Raises:
            RuntimeError: If the Conduit is sealed.
            RuntimeError: If the Conduit is not a 'normal' conduit (only normal conduits can bind spells).
            RuntimeError: If the spell is already bound in the registry.
            TypeError: If invalid hook types are provided.
        """
        if self._sealed:
            raise RuntimeError("Cannot bind spells in a sealed Conduit.")
        if not self._conduit_state == ConduitState.normal:
            raise RuntimeError("Only normal conduits can bind spells.")

        with self._lock:
            return self._spellbook.bind(spell=spell, existence=existence, spellframe=spellframe, binding_name=binding_name, permissions=permissions, **kwargs)

    def get_spell_permissions(self, spell_id: str) -> Optional[str]:
        """
        Public API

        Get the permissions for a spell by its spell_id.

        This returns the access level ("read", "create", "block") defined when the spell was bound.

        Args:
            spell_id (str): SHA256 identifier of the spell.

        Returns:
            Optional[str]: The permissions associated with the spell's binding.

        Raises:
            RuntimeError: If the spell with the given ID is not found in the spellbook.
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

        Placeholder for the service resolution/dependency injection mechanism.

        Args:
            spell_name (str): The name of the spell to resolve.
            spell_type (str): The expected type ("class" or "method").
            spellframe (Type, optional): An optional interface or type to validate against.

        Raises:
            NotImplementedError: As this method is not yet fully implemented.
            ValueError: If no spell is registered for the given name/type.
            TypeError: If the resolved instance does not comply with the required SpellFrame.
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

        Returns the global Conduit Cloud, a registry of all normal conduits in the current Aetheric Frame.

        This object is designed to be used in dynamic mode only and serves as an Abstract Factory/Service Locator.

        Returns:
            IConduitCloud: The conduit cloud instance.

        Raises:
            RuntimeError: If the Conduit is a lesser conduit.
            RuntimeError: If dynamic environment is not enabled.
        """
        if self._conduit_state == ConduitState.lesser:
            raise RuntimeError("Lesser conduits cannot access the conduit cloud.")
        if not self.__dynamic_environment__:
            raise RuntimeError("Dynamic environment is not enabled. Cannot access conduit cloud.")
        return Conduit._aether._get_conduit_cloud(self._aetheric_frame)

    #endregion Conduit Cloud
    #region Aether API
    def get_conduit_by_id(self, conduit_id: UUID, aetheric_frame:str = "default") -> Optional[IConduit]:
        """
        Public API

        Retrieves a conduit by its unique ID from the Aether.

        Args:
            conduit_id (UUID): The unique identifier of the conduit.
            aetheric_frame (str): The aetheric frame to check against. Defaults to this conduit's frame.

        Returns:
            Optional[IConduit]: The conduit instance if found, otherwise None.

        Raises:
            RuntimeError: If the Conduit is sealed.
            TypeError: If the `aetheric_frame` is not a string.
        """
        self.check_sealed()

        if not isinstance(aetheric_frame, str):
            raise TypeError(f"Expected aetheric_frame to be a string, got {type(aetheric_frame).__name__}")
        if aetheric_frame == "default":
            aetheric_frame = self._aetheric_frame

        with self._lock:
            return Conduit._aether._get_conduit_by_id(conduit_id, aetheric_frame)

    def get_conduit_by_name(self, name: str, aetheric_frame:str = "default") -> Optional[IConduit]:
        """
        Public API

        Retrieves a conduit by its name from the Aether.

        Args:
            name (str): The name of the conduit.
            aetheric_frame (str): The aetheric frame to check against. Defaults to this conduit's frame.

        Returns:
            Optional[IConduit]: The conduit instance if found, otherwise None.

        Raises:
            RuntimeError: If the Conduit is sealed.
            TypeError: If the `aetheric_frame` is not a string.
        """
        self.check_sealed()
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

        Attempts to establish a link between this Conduit and a `target_conduit`.

        Linking is only allowed if the world is in dynamic mode. This process initiates a contract
        relationship between the two conduits based on the current policy.

        Args:
            target_conduit (IConduit): The target Conduit to link to.

        Returns:
            bool: True if the linking process succeeds.

        Raises:
            RuntimeError: If the Conduit is sealed.
            RuntimeError: If dynamic environment is not enabled.
            TypeError: If `target_conduit` is not an `IConduit` instance.
            RuntimeError: If the target conduit does not have a valid creation context.
        """
        self.check_sealed()
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

        Sever the link and the corresponding spell contracts between this Conduit and its target Conduit.

        This method validates the link's existence, ensures it can be severed according to policy,
        and removes the link and all contracted spells. This is intended for public use to dissolve a relationship.

        Args:
            target_conduit (IConduit): The target Conduit whose link to sever.

        Returns:
            bool: True if the link was successfully severed.

        Raises:
            RuntimeError: If the Conduit is sealed.
            RuntimeError: If dynamic environment is not enabled.
        """
        self.check_sealed()
        if not self.__dynamic_environment__:
            raise RuntimeError("Dynamic environment is not enabled. Cannot manage link services.")
        with self._lock:
            return self._conduit_ward._sever_link(target_conduit)


    def get_links(self):
        """
        Public API

        Returns a list of all active peer links associated with this conduit.

        This list excludes links to lesser (child) conduits.

        Returns:
            list: A list of the linked conduit instances.

        Raises:
            RuntimeError: If the Conduit is sealed.
            RuntimeError: If dynamic environment is not enabled.
        """
        self.check_sealed()
        if not self.__dynamic_environment__:
            raise RuntimeError("Dynamic environment is not enabled. Cannot manage link services.")
        with self._lock:
            return self._conduit_ward._get_links()

    def get_lesser_conduit(self, conduit_id: UUID) -> Optional[IConduit]:
        """
        Internal

        Returns a specific lesser conduit (child) linked to this conduit by its ID.

        Args:
            conduit_id (UUID): The ID of the lesser conduit to retrieve.

        Returns:
            Optional[IConduit]: The linked lesser conduit if found, otherwise None.

        Raises:
            RuntimeError: If the Conduit is sealed.
        """
        self.check_sealed()
        with self._lock:
            return self._conduit_ward._get_lesser_conduit(conduit_id)


    def get_initiated_conduit(self, conduit_id: UUID) -> Optional[IConduit]:
        """
        Public API

        Retrieves the conduit that this conduit has initiated a contract *toward*.

        This method uses the internal index to resolve an outbound connection,
        where this conduit was the **initiator** of the contract.

        Args:
            conduit_id (UUID): The ID of the target conduit this conduit linked to.

        Returns:
            Optional[IConduit]: The target conduit if the link exists, otherwise None.

        Raises:
            RuntimeError: If the Conduit is sealed.
        """
        self.check_sealed()
        with self._lock:
            return self._conduit_ward._get_initiated_conduit(conduit_id)


    def get_provider_conduit(self, conduit_id: UUID) -> Optional[IConduit]:
        """
        Public API

        Retrieves the conduit that initiated a contract *to this* conduit.

        This method uses the internal index to resolve an inbound connection,
        where another conduit linked to this one as the **provider**.

        Args:
            conduit_id (UUID): The ID of the source conduit that linked to this one.

        Returns:
            Optional[IConduit]: The source conduit if the link exists, otherwise None.

        Raises:
            RuntimeError: If the Conduit is sealed.
        """
        self.check_sealed()
        with self._lock:
            return self._conduit_ward._get_provider_conduit(conduit_id)


    def get_initiated_conduits(self) -> list[IConduit]:
        """
        Public API

        Returns a list of all conduits that this conduit has initiated contracts toward (outbound links).

        This is useful for understanding the dependencies and relationships initiated by this conduit.

        Returns:
            list[IConduit]: A list of conduits this conduit linked to.

        Raises:
            RuntimeError: If the Conduit is sealed.
        """
        self.check_sealed()
        with self._lock:
            return self._conduit_ward._get_initiated_conduits()

    def get_provider_conduits(self) -> list[IConduit]:
        """
        Public API

        Returns a list of all conduits that have initiated contracts to this conduit (inbound links).

        These are the conduits that depend on this one for contracted spells.

        Returns:
            list[IConduit]: A list of conduits that have linked to this conduit as the provider.

        Raises:
            RuntimeError: If the Conduit is sealed.
        """
        self.check_sealed()
        with self._lock:
            return self._conduit_ward._get_provider_conduits()

    def seal_lesser_conduits(self):
        """
        Public API

        Seals all lesser conduits (children) linked to this conduit.

        This prevents further operations on lesser conduits and is typically used when the parent
        is sealing or undergoing a major state change (e.g., upgrade).

        Raises:
            RuntimeError: If the Conduit is sealed.
        """
        self.check_sealed()
        self._conduit_ward.seal_all_lesser_conduits()

    #endregion Conduit Ward API
    #region Spell Contracting API
    def _qualify_contracts(self):
        """
        Internal

        Performs checks to ensure the conduit is in a state capable of managing spell contracts.

        Raises:
            RuntimeError: If the Conduit is sealed.
            RuntimeError: If the Conduit is not a 'normal' conduit.
            RuntimeError: If dynamic environment is not enabled.
        """
        self.check_sealed()
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

        You must provide either a `spell` object or a `spell_id`. The target conduit must be specified
        either directly or resolved via its ID and aetheric frame.

        Args:
            spell (ISpell, optional): The spell object to contract.
            spell_id (str, optional): The unique ID of the spell to contract.
            conduit (IConduit, optional): The target conduit to contract with.
            conduit_id (UUID, optional): The UUID of the target conduit (used if `conduit` is not provided).
            permissions (str): The permission level granted for this spell (default is "create").
            aetheric_frame (str): Optional frame override used to locate the target conduit.

        Returns:
            bool | None: True if the contract was created, False otherwise. None if an internal error occurs.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (sealed, not normal, not dynamic).
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
        will be contracted using the same permission level.

        Args:
            spell_ids (list[str]): List of spell IDs to contract.
            conduit (IConduit, optional): The target conduit to contract with.
            conduit_id (UUID, optional): The UUID of the target conduit (used if `conduit` is not provided).
            permissions (str): The permission level granted for all spells (default is "create").
            aetheric_frame (str): Optional frame override used to locate the target conduit.

        Returns:
            dict: Dictionary of `spell_id` -> success boolean for each attempted contract.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (sealed, not normal, not dynamic).
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

        Args:
            spell (ISpell, optional): The spell object to remove.
            spell_id (str, optional): The unique ID of the spell to remove.
            conduit (IConduit, optional): The target conduit involved in the contract.
            conduit_id (UUID, optional): UUID of the target conduit (used if `conduit` not provided).
            aetheric_frame (str): Optional frame override to resolve the target conduit.

        Returns:
            bool | None: True if the spell was successfully removed from the contract, False otherwise. None if an internal error occurs.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (sealed, not normal, not dynamic).
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

        Args:
            spell_ids (list[str], optional): List of spell IDs to remove.
            conduit (IConduit, optional): Target conduit object.
            conduit_id (UUID, optional): UUID of target conduit (used if `conduit` is not provided).
            aetheric_frame (str): Optional frame override.

        Returns:
            dict: Dictionary of `spell_id` -> success boolean for each removal attempt.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (sealed, not normal, not dynamic).
        """
        self._qualify_contracts()
        return self._conduit_ward._remove_spells_from_contract(spell_ids=spell_ids, conduit=conduit,
                                                               conduit_id=conduit_id, aetheric_frame=aetheric_frame)

    def _remove_all_spells_from_contract(self, *, conduit: IConduit = None, conduit_id: UUID = None, aetheric_frame = "default") -> bool | None:
        """
        Public API

        Dissolves **all** spell contracts between this conduit and the specified target.

        All borrowed and granted spells in the active contract will be severed, effectively
        resetting the spell relationship between the two conduits.

        Args:
            conduit (IConduit, optional): Target conduit object.
            conduit_id (UUID, optional): UUID of target conduit (used if `conduit` is not provided).
            aetheric_frame (str): Optional frame override.

        Returns:
            bool | None: True if all spells were successfully removed, False otherwise. None if an internal error occurs.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (sealed, not normal, not dynamic).
        """
        self._qualify_contracts()
        return self._conduit_ward._remove_all_spells_from_contract(conduit=conduit, conduit_id=conduit_id, aetheric_frame=aetheric_frame)

    def get_all_spells_in_contracts(self, validate: bool = True) -> Optional[dict[str, list[Tuple[str, 'ISpell']]]]:
        """
        Public API

        Retrieves all active spells that this conduit has access to through its contracts (i.e., borrowed spells).

        Walks all current spell contracts and collects the spell IDs and objects that are currently
        borrowed from other conduits. Optionally validates contracts before collecting data.

        Args:
            validate (bool): If True, performs contract consistency validation before returning data.

        Returns:
            Optional[dict[str, list[Tuple[str, 'ISpell']]]]: Dictionary mapping peer conduit UUIDs to lists of (spell_id, ISpell) tuples,
            or None if no contracts exist.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (sealed, not normal, not dynamic).
            TypeError: If `validate` is not a boolean.
        """
        self._qualify_contracts()
        if not isinstance(validate, bool):
            raise TypeError(f"Expected validate to be a boolean, got {type(validate).__name__}")
        return self._conduit_ward._get_all_spells_in_contracts(validate=validate)

    def get_spell_in_contracts(self, spell_id: str) -> Optional[tuple[UUID, ISpell]]:
        """
        Public API

        Searches all known contracts to find the origin of a specific contracted spell.

        Looks for a specific spell by ID and returns the UUID of the conduit it's contracted from
        along with the spell object, if found.

        Args:
            spell_id (str): The unique ID of the spell.

        Returns:
            Optional[tuple[UUID, ISpell]]: Tuple of (`conduit_id`, `spell`) if found, otherwise None.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (sealed, not normal, not dynamic).
            TypeError: If `spell_id` is not a string.
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

        Args:
            conduit_id (UUID): UUID of the target peer conduit.

        Returns:
            dict[str, list[tuple[str, ISpell]]] | None: Dictionary of `spell_id` -> (`spell_id`, `ISpell`) tuples or None if not found.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (sealed, not normal, not dynamic).
            TypeError: If `conduit_id` is not a UUID.
        """
        self._qualify_contracts()
        if not isinstance(conduit_id, UUID):
            raise TypeError(f"Expected conduit_id to be a UUID, got {type(conduit_id).__name__}")
        return self._conduit_ward._get_spells_in_contract_by_conduit(conduit_id)

    def get_spells_in_contract_by_conduit_name(self, conduit_name: str) -> dict[str, list[tuple[str, ISpell]]] | None:
        """
        Public API

        Retrieves all spell contracts associated with a peer conduit identified by name.

        Performs resolution using a human-readable name instead of UUID.

        Args:
            conduit_name (str): Name of the peer conduit.

        Returns:
            dict[str, list[tuple[str, ISpell]]] | None: Dictionary of `spell_id` -> (`spell_id`, `ISpell`) tuples or None if not found.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (sealed, not normal, not dynamic).
            TypeError: If `conduit_name` is not a string.
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

        Returns:
            list[Tuple[str, IConduit]] | None: List of (`conduit_id`, `IConduit`) tuples, or None if no contracts exist.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (sealed, not normal, not dynamic).
        """
        self._qualify_contracts()
        return self._conduit_ward._get_contracted_conduits()

    def _describe_contract(self, conduit_id: UUID) -> dict:
        """
        Public API

        Produces a detailed diagnostic summary of a contract established with a specific conduit.

        This method inspects the contract associated with the provided `conduit_id` and returns metadata
        including the peer conduit’s name, the number of active spells involved, and permission levels.
        Primarily used for debugging, introspection, and UI inspection tools.

        Args:
            conduit_id (UUID): UUID of the peer conduit whose contract you wish to examine.

        Returns:
            dict: Dictionary containing contract metadata, including a list of spells and their permissions.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (sealed, not normal, not dynamic).
        """
        self._qualify_contracts()
        return self._conduit_ward._describe_contract(conduit_id)

    def validate_contracts_and_define(self) -> dict[UUID, bool]:
        """
        Public API

        Validates all known contracts attached to this conduit and confirms mutual agreement and consistency.

        This performs a deep validation pass, ensuring both sides list the same spells, permissions are symmetrical,
        and all referenced spells are valid.

        Returns:
            dict[UUID, bool]: Dictionary mapping contract UUIDs to validation results:
                 - True: Contract is valid and consistent
                 - False: Contract is malformed or inconsistent

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (sealed, not normal, not dynamic).
        """
        self._qualify_contracts()
        return self._conduit_ward._validate_contracts_and_define()


    def validate_received_contracts(self) -> bool:
        """
        Public API

        Performs a high-level validation check across all contracts involving this conduit.

        Aggregates the results of `_validate_contracts_and_define` to determine whether every connected
        contract is structurally valid and symmetrical.

        Returns:
            bool: True if all active contracts pass validation, False otherwise.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (sealed, not normal, not dynamic).
        """
        self._qualify_contracts()
        return self._conduit_ward._validate_received_contracts()


#endregion Spell Contracting API
#endregion Conduit