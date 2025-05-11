from typing import Optional, Type
from melder.utilities.concurrent_list import ConcurrentList
from melder.utilities.concurrent_set import ConcurrentSet
from melder.utilities.overload_dispatcher import OverloadDispatcher
from melder.utilities.interfaces import IConduit, ISpellbook, IConduitCloud
from melder.aether.aether import Aether
from melder.aether.conduit.meld.debugging.debugging import ConduitCreationContext
from melder.spellbook.configuration.configuration import Configuration
from melder.aether.conduit.meld.meld import Meld
from melder.aether.conduit.conduit_ward.conduit_ward import ConduitWard
import threading
from melder.aether.conduit.creations.creations import Creations, LesserCreations
from enum import Enum, auto

class ConduitState(Enum):
    """
    Enum representing the state of a Conduit.
    """
    normal = auto()
    lesser = auto()

class Conduit(IConduit):
    """
    A Conduit is a modular graph node that behaves like a scope and a factory.

    It can spawn lesser Conduits, link to other Conduits if dynamic mode is enabled,
    and manage the lifecycle of services registered inside itself.
    """

    _aether = Aether()

    def __init__(self, spellbook: ISpellbook, configuration: Configuration, conduit_state: str, name: Optional[str] = None):
        """
        Initializes a new Conduit.

        Args:
            spellbook (Spellbook): The Spellbook governing this Conduit.
            configuration (Configuration): The locked system configuration.
            conduit_state (str): The role of this Conduit ('normal' or 'lesser').
            name (str, optional): An optional name for easier identification.
        """
        super().__init__()
        # General Init
        self._lock = threading.RLock()
        self._name = name
        self._dispatchers = {}
        self.__debugger_mode__ = False
        self.__dynamic_environment__ = False
        self._creation_context = ConduitCreationContext()

        # Special Configuration
        self._configuration = configuration
        self._conduit_state = self._set_conduit_state(conduit_state)  # can be normal, lesser
        self._creations = self._creations_configuration(configuration)
        self._spellbook = spellbook
        self._meld = Meld(self._creations, self._spellbook) # instance melder which is used by the conduit to create objects

        # Internal configuration
        self._apply_configuration_flags()
        self._create_internal_configuration()

        if self._conduit_state == ConduitState.normal:
            self._add_conduit_to_aether()
            self._add_spells_to_aether()
            if self.__dynamic_environment__ and self._name is not None:
                Conduit._aether._register_conduit_cloud()
        elif self._conduit_state == ConduitState.lesser:
            self.lesser_conduit_contract_link() # TODO: some kind of operation should happen here

    @property
    def name(self) -> str:
        """
        Returns the name of this Conduit. Name must be created during conduit creation.
        """
        return self._name if self._name else None


    @name.setter
    def name(self, name: str):
        """
        Allows user to name conduit if available
        :return:
        """
        if self._name is not None:
            raise RuntimeError("Conduit name is set.")
        self._name = name


    def register_conduit_cloud(self, conduit: IConduit):
        """
        Registers a conduit in the dynamic mode registry. You can use this method if you forgot to name your conduit in order
        to name it afterward and register it. You can only register it once.
        :param conduit:
        :return:
        """
        if self._conduit_state == ConduitState.lesser:
            raise RuntimeError("Lesser conduits cannot register in the conduit cloud.")
        if self.__dynamic_environment__ and self._name is not None:
            Conduit._aether._register_conduit_cloud(conduit)


    def get_conduit_cloud(self) -> IConduitCloud:
        """
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
        return Conduit._aether._get_conduit_cloud()

#region fakemeld
    def meld(self, spell_name: str, spell_type: str, spellframe: Type = None):
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

    def _define(self, method_name):
        # Create the dispatcher if not yet defined
        if method_name not in self._dispatchers:
            self._dispatchers[method_name] = OverloadDispatcher()

            # Install a dynamic method onto this Conduit instance
            def dynamic_method(*args, **kwargs):
                return self._dispatchers[method_name](*args, **kwargs)
            setattr(self, method_name, dynamic_method)

        def decorator(func):
            self._dispatchers[method_name].register(func)
            return func

        return decorator

    @staticmethod
    def _set_conduit_state(state: str) -> ConduitState:
        """
        Sets the conduit state to normal or lesser.
        """
        if state == "lesser":
            return ConduitState.lesser
        elif state == "normal":
            return ConduitState.normal
        else:
            raise ValueError("Conduit state is unknown")

    def _creations_configuration(self, configuration: Configuration) -> Creations or LesserCreations:
        """
        Returns the current creations configuration for this Conduit.
        """
        if self._conduit_state == ConduitState.lesser:
            return LesserCreations(configuration.get_property("disposal"), configuration.get_property("disposal_method_names"))
        elif self._conduit_state == ConduitState.normal:
            return Creations(configuration.get_property("disposal"), configuration.get_property("disposal_method_names"))
        else:
            raise RuntimeError("Conduit state is unknown")

    def upgrade_to_normal(self, name: Optional[str] = None) -> None:
        """
        Upgrades this Conduit to a normal state. This allows the conduit to create its own links
        through the aether system. This will fork this conduit into a new tree and create new links with the parent.
        This conduit and its children go with it, only a normal scope can access the spellbook to bind new spells.

        Please name the conduit if your intention is to add it to the Conduit Cloud.
        :return:
        """
        with self._lock:
            if self._conduit_state != ConduitState.lesser:
                raise RuntimeError("Only lesser conduits can be upgraded.")

            # Step 1: Change state
            self._conduit_state = ConduitState.normal

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

            self._name = name
            # Step 5: Register as a full Conduit in Aether
            Conduit._add_conduit_to_aether(self)

    def _apply_configuration_flags(self):
        """
        Sets the environment mode and debugging mode for this Conduit
        based on the configuration instance passed.
        """
        if self._configuration.get_property("conduit_state") == "automatic":
            self.__dynamic_environment__ = False
        elif self._configuration.get_property("conduit_state") == "dynamic":
            self.__dynamic_environment__ = True

        if self._configuration.get_property("debugging"):
            self.__debugger_mode__ = True

    @property
    def __creation_context__(self) -> ConduitCreationContext:
        """
        🔮 Public (Advanced) API — use with care.

        This property exposes the internal creation metadata for this conduit,
        including unique ID, creation path, and lifecycle configuration context.

        Intended for:
        - Advanced diagnostics
        - Contract validation systems
        - Internal resolver systems

        Not recommended for casual use.
        """
        return self._creation_context

    def _add_conduit_to_aether(self) -> None:
        """
        Adds the newly created Conduit into the shared Aether world.

        Args:
            conduit (Conduit): The Conduit instance to add.
        """
        if Conduit._aether is None:
            raise RuntimeError("Aether is not initialized.")
        Conduit._aether._add_conduit(self)


    def _add_spells_to_aether(self) -> None:
        """
        Adds the newly created Conduit into the shared Aether world.

        Args:
            conduit (Conduit): The Conduit instance to add.
        """
        if Conduit._aether is None:
            raise RuntimeError("Aether is not initialized.")

        spell_set= ConcurrentSet(self._spellbook._spells.keys())
        Conduit._aether._add_spells_to_aether(self.__creation_context__._conduit_id, spell_set)

    def _create_internal_configuration(self) -> None:
        """
        Creates per-Conduit internal structures based on the current world configuration.
        """
        self._configure_conduit_links()

    def _configure_conduit_links(self) -> None:
        """
        Configures whether this Conduit maintains linkable connections.
        Only enabled in dynamic environments.
        """
        if self.__dynamic_environment__:
            self._conduit_links = ConcurrentList()
        else:
            self._conduit_links = None

    def link(self, target_conduit) -> bool:
        """
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
        with self._lock:
            raise NotImplementedError("Linking conduits is not implemented yet.")

    def sever_link(self):
        """
        Sever the link between this Conduit and its target Conduit.

        This is meant for internal use please do not use this outside of the class.
        """
        if self._sealed:
            raise RuntimeError("Cannot sever a link in a sealed Conduit.")
        if not self.__dynamic_environment__:
            raise RuntimeError("Dynamic environment is not enabled. Cannot manage link services.")
        with self._lock:
            raise NotImplementedError("Severing links is not implemented yet.")

    def _link_lesser_conduit(self, target_conduit) -> bool:
        """
        Attempts to link this Conduit to a lesser Conduit.
        This is meant for internal use please do not use this outside of the class.

        Linking for Automatic mode will transfer the spellbook of the existing conduit into the
        lesser conduit and setup permissions between objects using link.

        Args:
            target_conduit (Conduit): The target Conduit to link to.

        Returns:
            bool: True if linking succeeds (currently not implemented).
        """
        if self._sealed:
            raise RuntimeError("Cannot link to a sealed Conduit.")
        with self._lock:
            raise NotImplementedError("Linking conduits is not implemented yet.")

    def create_lesser_conduit(self, name: Optional[str] = None) -> IConduit:
        """
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
                spellbook=self._spellbook._lesser_conduit_spellbook_copy(),
                configuration=self._configuration,
                conduit_state="lesser",
                name=name
            )
        self._lesser_conduits_links.append(new_conduit)
        return new_conduit

    def seal(self):
        """
        Seals this Conduit and all its lesser Conduits.

        Prevents further operation, releases internal references,
        and unregisters from the Aether.
        """
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
            self._conduit_links = None
            self._creation_context = None
            self._lesser_conduits_links = None

            # Phase 3: Deregister from the world
            if self._aether and not self._aether.sealed:
                self._aether._remove_conduit(self)

            self._sealed = True

    def __repr__(self):
        return (
            f"<Conduit name={self.name} "
            f"id={self._creation_context._conduit_id}>"
        )

    def _clean_up_lesser_conduits_links(self):
        """
        Cleans up all lesser conduits.
        :return:
        """
        if self._lesser_conduits_links:
            for lesser_conduit in self._lesser_conduits_links:
                lesser_conduit.seal()
            self._lesser_conduits_links.dispose()

    def _clean_up_links(self):
        """
        Cleans up all links.
        :return:
        """
        if self._conduit_links:
            for link in self._conduit_links:
                link.seal()
            self._conduit_links.dispose()
