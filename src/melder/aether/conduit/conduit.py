from typing import Optional
from melder.utilities.concurrent_dictionary import ConcurrentDict
from melder.utilities.concurrent_list import ConcurrentList
from melder.utilities.interfaces import IConduit, ISpellbook
from melder.aether.aether import Aether
from melder.aether.conduit.meld.debugging.debugging import ConduitCreationContext
from melder.spellbook.configuration.configuration import Configuration
from melder.aether.links.link import Link
import threading
from melder.aether.conduit.creations.creations import Creations


class Conduit(IConduit):
    """
    A Conduit is a modular graph node that behaves like a scope and a factory.

    It can spawn lesser Conduits, link to other Conduits if dynamic mode is enabled,
    and manage the lifecycle of services registered inside itself.
    """

    _configuration = None
    _aether = Aether()

    _configuration_set = False
    __debugger_mode__ = False
    __dynamic_environment__ = False

    def __init__(self, spellbook: ISpellbook, configuration: Configuration, name: Optional[str] = None):
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
        self.__creation_context__ = ConduitCreationContext()
        self._spellbook = spellbook
        self._creations = Creations(configuration.get_property("disposal"), configuration.get_property("disposal_method_names"))
        Conduit._configuration = configuration

        with self._lock:
            if not Conduit._configuration_set:
                Conduit._set_configuration()

        self._conduit_links = None
        self._lesser_conduits_links = ConcurrentList()

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
            Conduit.__dynamic_environment__ = False
        elif Conduit._configuration.get_property("conduit_state") == "dynamic":
            Conduit.__dynamic_environment__ = True

    @classmethod
    def _set_debug_settings(cls):
        """
        Sets the debugging mode for Conduits based on system configuration.
        """
        if Conduit._configuration.get_property("debugging"):
            Conduit.__debugger_mode__ = True
        else:
            Conduit.__debugger_mode__ = False

    @classmethod
    def _add_conduit_to_aether(cls, conduit: IConduit) -> None:
        """
        Adds the newly created Conduit into the shared Aether world.

        Args:
            conduit (Conduit): The Conduit instance to add.
        """
        if cls._aether is None:
            raise RuntimeError("Aether is not initialized.")
        cls._aether.add_conduit(conduit)

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
        if Conduit.__dynamic_environment__:
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
        if self.sealed:
            raise RuntimeError("Cannot link to a sealed Conduit.")
        if not Conduit.__dynamic_environment__:
            raise RuntimeError("Dynamic environment is not enabled. Cannot manually link services.")
        with self._lock:
            raise NotImplementedError("Linking conduits is not implemented yet.")

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
        if self.sealed:
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
        if self.sealed:
            raise RuntimeError("Cannot create a lesser Conduit in a sealed Conduit.")
        new_conduit = Conduit(
            spellbook=spellbook,
            configuration=self._configuration,
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
        if self.sealed:
            return
        with self._lock:
            self.clean_up_lesser_conduits_links()
            self.clean_up_links()
            self._spellbook.seal()
            self._creations.seal()
            self._conduit_links.dispose()

            # Null out everything
            self._spellbook = None
            self._creations = None
            self._conduit_links = None
            self.__creation_context__ = None
            self._lesser_conduits_links = None

            if self._aether and not self._aether.sealed:
                self._aether.remove_conduit(self)

            self.sealed = True

    def clean_up_lesser_conduits_links(self):
        """
        Cleans up all lesser conduits.
        :return:
        """
        if self._lesser_conduits_links:
            for lesser_conduit in self._lesser_conduits_links:
                lesser_conduit.seal()
            self._lesser_conduits_links.dispose()

    def clean_up_links(self):
        """
        Cleans up all links.
        :return:
        """
        if self._conduit_links:
            for link in self._conduit_links:
                link.seal()
            self._conduit_links.dispose()