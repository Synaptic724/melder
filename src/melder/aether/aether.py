import uuid
from melder.utilities.interfaces import Seal
from melder.utilities.concurrent_list import ConcurrentList
import threading

class Aether(Seal):
    """
    Aether is a class that holds a reference to all conduit systems.
    Aether is also responsible for disposing of all conduits if required.

    It's a tool that will be used by conduits to link them together and
    allow them to communicate and extend their own behaviours.
    """
    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(Aether, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not Aether._initialized:
            Aether._initialized = True
            self.sealed = False
            self.conduits = ConcurrentList()


    def add_conduit(self, conduit):
        """
        Adds a new conduit to the Aether.
        """
        self.conduits.append(conduit)

    def remove_conduit(self, conduit):
        """
        Removes a conduit from the Aether.
        """
        self.conduits.remove(conduit)

    def link_conduit_by_signature(self, req_conduit, conduit_signature: uuid.uuid4):
        """
        Returns a conduit in order to link them.
        """
        raise NotImplementedError("Not implemented.")
        for conduit in self.conduits:
            if conduit.name == conduit_signature:
                req_conduit.link(conduit)
        raise ValueError(f"Conduit signature: {conduit_signature}, not found.")

    def link_conduit_by_name(self, req_conduit, conduit_name: str):
        """
        Returns a conduit in order to link them.
        """
        raise NotImplementedError("Not implemented.")
        for conduit in self.conduits:
            if conduit.name == conduit_name:
                req_conduit.link(conduit)
        raise ValueError(f"Conduit name: {conduit_name}, not found.")

    def seal(self):
        """
        Dispose of the Aether and all its conduits.
        """
        if self.sealed:
            return
        for conduit in self.conduits:
            conduit.dispose()
        self.conduits.clear()
        self.sealed = True

