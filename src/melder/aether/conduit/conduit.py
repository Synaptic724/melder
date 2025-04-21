from typing import Optional
from melder.utilities.interfaces import Seal
from melder.aether.aether import Aether
from melder.aether.conduit.meld.debugging.debugging import ConduitCreationContext
import threading
from abc import ABC, abstractmethod



class IConduit(ABC, Seal):
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
    def __init__(self, name: Optional[str] = None):
        """
        Initializes the Conduit with a root node.
        """
        self.name = name
        self.sealed = False
        self._lock = threading.RLock()
        self.CreationContext = ConduitCreationContext()

        self._conduit_links = None
        self._lesser_conduits = None

        self._spellbook = None
        self._aether = Aether()
        self._dynamic_environment = self._aether.dynamic_environment


    def link(self, target_conduit) -> bool:
        """
        Links the current conduit to another conduit while dynamic environment is enabled.
        :param target_conduit: The target conduit to link to.
        """
        if self.sealed:
            raise RuntimeError("Cannot link to a sealed conduit.")
        if not self._dynamic_environment:
            raise RuntimeError("Dynamic environment is not enabled. Cannot manually link services.")
        with self._lock:
            raise NotImplementedError("Linking conduits is not implemented yet.")

    def create_lesser_conduit(self, name: Optional[str] = None) -> "Conduit":
        """
        Creates a new lesser conduit and adds it to the list of lesser conduits.
        """
        if self.sealed:
            raise RuntimeError("Cannot create a lesser conduit in a sealed conduit.")
        with self._lock:
            new_conduit = Conduit(name=name)
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
            for lesser_conduit in self._lesser_conduits:
                lesser_conduit.seal()
            # Dispose of the current node
            self._lesser_conduits.dispose()

            self._lesser_conduits = None
            self._conduit_links = None
            self._aether = None
            self.sealed = True

