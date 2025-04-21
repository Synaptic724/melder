from typing import Optional
from melder.spellbook.spellbook import Spellbook
from melder.utilities.concurrent_list import ConcurrentList
from melder.utilities.interfaces import ISeal
from melder.aether.aether import Aether
from melder.aether.conduit.meld.debugging.debugging import ConduitCreationContext
from melder.spellbook.configuration.configuration import Configuration
import threading
from abc import ABC, abstractmethod



class IConduit(ABC, ISeal):
    """
    Interface for Conduit, which is a graph structure that behaves like a scope and a factory.
    """
    @abstractmethod
    def link(self):
        """
        Links the conduit to another conduit.
        :return:
        """
        pass

    @abstractmethod
    def meld(self):
        """
        Melding is the process of creating a new object.
        :return:
        """
        pass

    @abstractmethod
    def seal(self):
        """
        Disposes of the current conduit and its lesser conduits
        """
        pass

    @abstractmethod
    def create_lesser_conduit(self):
        """
        Creates a new lesser conduit.
        :return:
        """
        pass


class Conduit(IConduit):
    """
    Conduit is a graph structure that also behaviours like a scope and a factory.
    """
    _configuration = None
    _aether = Aether()

    _configuration_set = False
    _debugger_mode = False
    _dynamic_environment = False

    def __init__(self, spellbook: Spellbook, configuration: Configuration, name: Optional[str] = None):
        """
        Initializes the Conduit with a root node.
        """
        self.name = name
        self.sealed = False
        self._lock = threading.RLock()
        self.creation_context = ConduitCreationContext()
        self._spellbook = spellbook
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
        Sets the configuration for the conduit.
        """
        if Conduit._configuration_set:
            raise RuntimeError("Configuration is already set.")

        cls._set_environment()
        cls._set_debug_settings()
        cls._configuration_set = True

    @classmethod
    def _set_environment(cls):
        """
        Sets the environment for the conduit.
        :return:
        """
        if Conduit._configuration.get_property("conduit_state") == "automatic":
            Conduit._dynamic_environment = False
        elif Conduit._configuration.get_property("conduit_state") == "dynamic":
            Conduit._dynamic_environment = True

    @classmethod
    def _set_debug_settings(cls):
        """
        Sets the debugging settings for the conduit.
        :return:
        """
        if Conduit._configuration.get_property("debugging"):
            Conduit._debugger_mode = True
        else:
            Conduit._debugger_mode = False

    def _create_internal_configuration(self) -> None:
        """
        Creates the internal configuration for the conduit.
        """
        self._configure_conduit_links()

    def _configure_conduit_links(self) -> None:
        """
        Configures the conduit links based on the current configuration.
        """
        if Conduit._dynamic_environment:
            self._conduit_links = ConcurrentList()
        else:
            self._conduit_links = None

    @classmethod
    def _add_conduit_to_aether(cls, conduit) -> None:
        """
        Adds the conduit to the Aether.
        """
        if cls._aether is None:
            raise RuntimeError("Aether is not initialized.")
        cls._aether.add_conduit(conduit)

    def link(self, target_conduit) -> bool:
        """
        Links the current conduit to another conduit while dynamic environment is enabled.
        :param target_conduit: The target conduit to link to.
        """
        if self.sealed:
            raise RuntimeError("Cannot link to a sealed conduit.")
        if not Conduit._dynamic_environment:
            raise RuntimeError("Dynamic environment is not enabled. Cannot manually link services.")
        with self._lock:
            raise NotImplementedError("Linking conduits is not implemented yet.")

    def create_lesser_conduit(self, spellbook: Spellbook, name: Optional[str] = None) -> "Conduit":
        """
        Creates a new lesser conduit and adds it to the list of lesser conduits.
        """
        if self.sealed:
            raise RuntimeError("Cannot create a lesser conduit in a sealed conduit.")
        with self._lock:
            new_conduit = Conduit(
                spellbook=spellbook,
                configuration=self._configuration,
                name=name
            )
            self._lesser_conduits.append(new_conduit)
            return new_conduit


    def seal(self):
        """
        Disposes of the entire tree structure.
        """
        if self.sealed:
            return
        with self._lock:
            # Dispose of all children
            if self._lesser_conduits:
                for lesser_conduit in self._lesser_conduits:
                    lesser_conduit.seal()
                self._lesser_conduits.dispose()

            self._lesser_conduits = None
            self._conduit_links = None
            self._aether = None
            self.sealed = True

