from typing import Optional
from melder.spellbook.spellbook import Spellbook
from melder.utilities.concurrent_dictionary import ConcurrentDict
from melder.utilities.concurrent_list import ConcurrentList
from melder.utilities.interfaces import ISeal
from melder.aether.aether import Aether
from melder.aether.conduit.meld.debugging.debugging import ConduitCreationContext
from melder.spellbook.configuration.configuration import Configuration
from melder.aether.links.link import Link
import threading
from abc import ABC, abstractmethod
from melder.aether.conduit.creations.creations import Creations

class IConduit(ABC, ISeal):
    """
    Interface for a Conduit, which behaves as both a scope and a factory within the system.
    """

    @abstractmethod
    def link(self):
        """
        Links this Conduit to another Conduit.
        Only allowed if the world environment is dynamic.
        """
        pass

    @abstractmethod
    def meld(self):
        """
        Melding is the process of creating or materializing an object
        from the Conduit's registered spells.
        """
        pass

    @abstractmethod
    def seal(self):
        """
        Seals this Conduit and all its lesser Conduits.
        Prevents further linking, melding, or creation.
        """
        pass

    @abstractmethod
    def create_lesser_conduit(self):
        """
        Creates a new lesser Conduit (child scope) beneath this Conduit.
        """
        pass


class Conduit(IConduit):
    """
    A Conduit is a modular graph node that behaves like a scope and a factory.

    It can spawn lesser Conduits, link to other Conduits if dynamic mode is enabled,
    and manage the lifecycle of services registered inside itself.
    """

    _configuration = None
    _aether = Aether()

    _configuration_set = False
    _debugger_mode = False
    _dynamic_environment = False

    def __init__(self, spellbook: Spellbook, configuration: Configuration, name: Optional[str] = None):
        """
        Initializes a new Conduit.

        Args:
            spellbook (Spellbook): The Spellbook governing this Conduit.
            configuration (Configuration): The locked system configuration.
            name (str, optional): An optional name for easier identification.
        """
        self.name = name
        self.sealed = False
        self._lock = threading.RLock()
        self._creation_context = ConduitCreationContext()
        self._spellbook = spellbook
        self._creations = Creations(configuration.get_property("disposal"), configuration.get_property("disposal_method_names"))
        Conduit._configuration = configuration

        with self._lock:
            if not Conduit._configuration_set:
                Conduit._set_configuration()

        self._conduit_links = None
        self._lesser_conduits = None

        self._create_internal_configuration()
        Conduit._add_conduit_to_aether(self)

    @classmethod
    def _set_configuration(cls) -> None:
        """
        Locks the system configuration for all Conduits.
        Sets dynamic environment mode and debugging mode flags.
        This operation is idempotent and can only occur once.
        """
        if Conduit._configuration_set:
            raise RuntimeError("Configuration is already set.")

        cls._set_environment()
        cls._set_debug_settings()
        cls._configuration_set = True

    @classmethod
    def _set_environment(cls):
        """
        Sets the environment mode (dynamic or automatic) for all Conduits.
        Dynamic mode allows runtime linking; automatic prohibits it.
        """
        if Conduit._configuration.get_property("conduit_state") == "automatic":
            Conduit._dynamic_environment = False
        elif Conduit._configuration.get_property("conduit_state") == "dynamic":
            Conduit._dynamic_environment = True

    @classmethod
    def _set_debug_settings(cls):
        """
        Sets the debugging mode for Conduits based on system configuration.
        """
        if Conduit._configuration.get_property("debugging"):
            Conduit._debugger_mode = True
        else:
            Conduit._debugger_mode = False

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
        if Conduit._dynamic_environment:
            self._conduit_links = ConcurrentList()
        else:
            self._conduit_links = None

    @classmethod
    def _add_conduit_to_aether(cls, conduit) -> None:
        """
        Adds the newly created Conduit into the shared Aether world.

        Args:
            conduit (Conduit): The Conduit instance to add.
        """
        if cls._aether is None:
            raise RuntimeError("Aether is not initialized.")
        cls._aether.add_conduit(conduit)

    def link(self, target_conduit) -> bool:
        """
        Attempts to link this Conduit to another Conduit.

        Linking is only allowed if the world is in dynamic mode.

        Args:
            target_conduit (Conduit): The target Conduit to link to.

        Returns:
            bool: True if linking succeeds (currently not implemented).
        """
        if self.sealed:
            raise RuntimeError("Cannot link to a sealed Conduit.")
        if not Conduit._dynamic_environment:
            raise RuntimeError("Dynamic environment is not enabled. Cannot manually link services.")
        with self._lock:
            raise NotImplementedError("Linking conduits is not implemented yet.")

    def create_lesser_conduit(self, spellbook: Spellbook, name: Optional[str] = None) -> "Conduit":
        """
        Creates a lesser Conduit (child node) attached to this Conduit.

        Args:
            spellbook (Spellbook): The Spellbook to govern the new Conduit.
            name (str, optional): Optional name for the new Conduit.

        Returns:
            Conduit: The newly created lesser Conduit.
        """
        if self.sealed:
            raise RuntimeError("Cannot create a lesser Conduit in a sealed Conduit.")
        new_conduit = Conduit(
            spellbook=spellbook,
            configuration=self._configuration,
            name=name
        )
        self._lesser_conduits.append(new_conduit)
        return new_conduit

    def seal(self):
        """
        Seals this Conduit and all its lesser Conduits.

        Prevents further operation, releases internal references,
        and unregisters from the Aether.
        """
        if self.sealed:
            return
        with self._lock:
            self.clean_up_lesser_conduits()
            self.clean_up_links()
            self._spellbook.seal()
            self._creations.seal()
            self._conduit_links.dispose()

            # Null out everything
            self._spellbook = None
            self._creations = None
            self._conduit_links = None
            self._creation_context = None
            self._lesser_conduits = None
            self._conduit_links = None

            self.sealed = True

    def clean_up_lesser_conduits(self):
        """
        Cleans up all lesser conduits.
        :return:
        """
        if self._lesser_conduits:
            for lesser_conduit in self._lesser_conduits:
                lesser_conduit.seal()
            self._lesser_conduits.dispose()

    def clean_up_links(self):
        """
        Cleans up all links.
        :return:
        """
        if self._conduit_links:
            for link in self._conduit_links:
                link.seal()
            self._conduit_links.dispose()