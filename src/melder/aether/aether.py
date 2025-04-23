import uuid
from melder.utilities.concurrent_dictionary import ConcurrentDict
from melder.utilities.interfaces import ISeal, IConduit
import threading

class Aether(ISeal):
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
            self._conduits = ConcurrentDict()

    def get_conduit(self, name: str) -> IConduit:
        """
        Returns a conduit by its name.
        """
        for conduit in self._conduits.values():
            if conduit.name == name:
                return conduit
        raise ValueError(f"Conduit with name {name} not found.")

    def get_conduit_by_signature(self, signature: uuid.uuid4) -> IConduit:
        """
        Returns a conduit by its signature.
        """
        for conduit in self._conduits.values():
            if conduit.signature == signature:
                return conduit
        raise ValueError(f"Conduit with signature {signature} not found.")

    def _add_conduit(self, conduit: IConduit):
        """
        Adds a new conduit to the Aether. This is primarily used by conduits internally. Not meant for external use.
        """
        self._conduits[conduit.__creation_context__._conduit_id] = conduit

    def _remove_conduit(self, conduit: IConduit):
        """
        Removes a conduit from the Aether. Not meant for external use.
        """
        self._conduits.pop(conduit.__creation_context__._conduit_id)

    def _link_conduit_by_signature(self, req_conduit, conduit_signature: uuid.uuid4):
        """
        Returns a conduit in order to link them. Not meant for external use.
        """
        raise NotImplementedError()
        for conduit in self._conduits.values():
            if conduit.signature == conduit_signature:
                req_conduit.link(conduit)
                return
        raise ValueError(f"Conduit signature: {conduit_signature}, not found.")

    def _link_conduit_by_name(self, req_conduit: IConduit, conduit_name: str):
        """
        Returns a conduit in order to link them. Not meant for external use.
        """
        raise NotImplementedError("Not implemented.")
        for conduit in self._conduits.values():
            if conduit.name == conduit_name:
                req_conduit.link(conduit)
                return
        raise ValueError(f"Conduit name: {conduit_name}, not found.")

    def seal(self):
        """
        Dispose of the Aether and all its conduits.
        """
        if self.sealed:
            return
        for conduit in self._conduits.values():
            conduit.seal()
        self._conduits.clear()
        self.sealed = True