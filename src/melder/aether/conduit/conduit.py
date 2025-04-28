from typing import Optional
from melder.utilities.concurrent_list import ConcurrentList
from melder.utilities.interfaces import IConduit, ISpellbook, IMeld
from melder.aether.aether import Aether
from melder.aether.conduit.meld.debugging.debugging import ConduitCreationContext
from melder.spellbook.configuration.configuration import Configuration
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
        self.name = name
        self.__debugger_mode__ = False
        self.__dynamic_environment__ = False
        self._creation_context = ConduitCreationContext()

        # Conduit Links
        self._conduit_links = None
        self._lesser_conduits_links = ConcurrentList()

        # Special Configuration
        self._configuration = configuration
        self._conduit_state = self._set_conduit_state(conduit_state)  # can be normal, lesser
        self._creations = self._creations_configuration(configuration)
        self._spellbook = spellbook

        # Internal configuration
        self._apply_configuration_flags()
        self._create_internal_configuration()

        if self._conduit_state == ConduitState.normal:
            Conduit._add_conduit_to_aether(self)

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

    def upgrade_to_normal(self):
        """
        Upgrades this Conduit to a normal state. This allows the conduit to create its own links
        through the aether system. This will fork this conduit into a new tree and create new links with the parent.
        This conduit and its children go with it, only a normal scope can access the spellbook to bind new spells.

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

    @classmethod
    def _add_conduit_to_aether(cls, conduit: IConduit) -> None:
        """
        Adds the newly created Conduit into the shared Aether world.

        Args:
            conduit (Conduit): The Conduit instance to add.
        """
        if cls._aether is None:
            raise RuntimeError("Aether is not initialized.")
        cls._aether._add_conduit(conduit)

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

    def create_lesser_conduit(self, spellbook: ISpellbook, name: Optional[str] = None) -> IConduit:
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
                spellbook=spellbook,
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
