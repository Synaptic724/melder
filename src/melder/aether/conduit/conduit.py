import time
import uuid
import datetime
from typing import Optional, List
from melder.utilities.interfaces import Seal
from melder.utilities.concurrent_list import ConcurrentList
from melder.utilities.concurrent_dictionary import ConcurrentDict
import threading
from abc import ABC, abstractmethod



class IConduit(ABC):
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
    def seal(self):
        """
        Disposes of the current conduit and its lesser conduits
        """
        pass



class Conduit(Seal):
    """
    Conduit is a graph structure that also behaviours like a scope and a factory.
    """
    def __init__(self, name: Optional[str] = None):
        """
        Initializes the Conduit with a root node.
        """
        self.name = name
        self.sealed = False

        self._greater_conduit_link = None
        self._lock = threading.RLock()
        self._lesser_conduits = ConcurrentList()
        self._ID = uuid.uuid4()
        self._creation_time = datetime.datetime.now()
        self._creation_time_ns = time.time_ns()
        self._dynamic_environment = False

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
            self.sealed = True

