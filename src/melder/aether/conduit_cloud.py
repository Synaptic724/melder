import threading
from typing import Dict
import ulid
# Melder imports
from melder.utilities.interfaces.interfaces import IConduit
from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class ConduitCloud(Cleanable):
    """
    An abstract factory for named conduits, active only in "dynamic" mode.

    The ConduitCloud provides a central location to retrieve conduits by a
    human-readable name, rather than by contract or instance. This behaves
    like a service locator pattern, intended for top-level access in
    highly dynamic systems where contracts are not always feasible.

    This object is thread-safe.

    Attributes:
        _lock (Lock): A lock for registry modifications.
        _name (str): The name of the frame this cloud belongs to.
        _registry (Dict): A map of `conduit_name` to `IConduit` instance.
    """
    __melder_internal__ = _mrg.sentinel
    def __init__(self, name: str):
        """
        Initializes the ConduitCloud.

        Args:
            name (str): The name of the AethericFrame this cloud serves.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()
        self._name: str = name
        self._registry: Dict = {}
        self._id: str = str(ulid.ULID())

    def cleanup(self):
        """
        Cleans up the ConduitCloud, clearing its registry.

        This operation is idempotent.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._registry.clear()
            self._registry = None
            self._cleaned = True
        self._lock = None


    #region Context Manager
    def __enter__(self):
        """
        Enters the context manager for Aether.
        """
        self._lock.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exits the context manager for Aether.
        """
        self._lock.release()

    #endregion Context Manager


    def get_conduit(self, name: str) -> IConduit:
        """
        Retrieves a conduit by its registered name.

        Args:
            name (str): The unique name of the conduit.

        Returns:
            IConduit: The conduit instance.

        Raises:
            RuntimeError: If the ConduitCloud is cleaned.
            ValueError: If a conduit with that name is not found.
        """
        self.check_cleaned()
        if name in self._registry:
            return self._registry[name]
        raise ValueError(f"Conduit with name {name} not found.")

    def _register_conduit(self, conduit: IConduit):
        """
        Registers a named conduit into the cloud. (Internal use)

        Args:
            conduit (IConduit): The conduit instance to register.

        Raises:
            ValueError: If the conduit's name is None or already exists
                in the registry.
        """
        self.check_cleaned()
        if conduit.name is None:
            raise ValueError("Conduit name cannot be None for cloud registration.")

        if conduit.name in self._registry:
            raise ValueError(f"Conduit with name {conduit.name} already exists in the cloud. Please rename conduit to something unique.")
        self._registry[conduit.name] = conduit

    def _unregister_conduit(self, conduit: IConduit):
        """
        Removes a named conduit from the cloud. (Internal use)

        Args:
            conduit (IConduit): The conduit instance to unregister.

        Raises:
            ValueError: If the conduit has no name or is not registered.
        """
        self.check_cleaned()
        if conduit.name is None:
            raise ValueError("Conduit name cannot be None for cloud unregistration.")

        removed = self._registry.pop(conduit.name, None)
        if removed is None:
            raise ValueError(f"Conduit with name {conduit.name} is not registered in the cloud.")
