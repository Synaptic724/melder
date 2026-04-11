import threading
from typing import Dict
import ulid
# Melder imports
from melder.utilities.interfaces.interfaces import IConduit, IConduitCloud
from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class ConduitCloud(Cleanable, IConduitCloud):
    """
    Frame-scoped registry of named conduits.

    `ConduitCloud` is the direct-name lookup surface used in dynamic runtime
    posture when callers need to resolve a conduit by a human-readable name
    instead of by contract or direct object reference.

    Contract:
    - One cloud belongs to one frame name.
    - Conduit names must be unique within the cloud.
    - The cloud does not own conduit lifecycle; it only owns the registry
      mapping.
    - Thread-safe access is serialized with the instance `RLock`.
    """
    __melder_internal__ = _mrg.sentinel
    def __init__(self, name: str):
        """
        Initialize the frame-scoped conduit-name registry.

        Purpose:
            Create the name-based conduit lookup surface owned by one
            `AethericFrame`.

        Args:
            name (str): The name of the AethericFrame this cloud serves.
        Contract:
            - Starts with an empty conduit registry.
            - Stores the owning frame name for later diagnostics/identity.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()
        self._name: str = name
        self._registry: Dict = {}
        self._id: str = str(ulid.ULID())

    def cleanup(self):
        """
        Clear the conduit registry and finalize the cloud.

        Purpose:
            Drop the frame-local name registry without touching the underlying
            conduit objects.

        Contract:
            - Idempotent and lock-guarded.
            - Clears only the registry; it does not clean the conduit objects
              themselves.
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
        Acquire the registry lock and return this cloud.

        Contract:
            - Holds the cloud lock until `__exit__` runs.
        """
        self._lock.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Release the registry lock acquired by `__enter__`.
        """
        self._lock.release()

    #endregion Context Manager


    def get_conduit(self, name: str) -> IConduit:
        """
        Return a registered conduit by name.

        Purpose:
            Provide the direct human-readable conduit lookup path for one frame.

        Args:
            name (str): The unique name of the conduit.

        Contract:
            - Returns the live registered conduit object.
            - Raises instead of silently returning None when the name is
              missing.

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
        Register one named conduit in the cloud.

        Purpose:
            Insert a live conduit into the frame-local name registry after the
            owning frame has already accepted the conduit.

        Args:
            conduit (IConduit): The conduit instance to register.

        Contract:
            - Conduit names must be present and unique.
            - The cloud stores the live conduit object without taking ownership
              of its lifecycle.

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
        Remove one named conduit from the cloud.

        Purpose:
            Keep the frame-local name registry in sync when a conduit leaves the
            owning frame.

        Args:
            conduit (IConduit): The conduit instance to unregister.

        Contract:
            - Requires the conduit name to be present.
            - Raises when the named conduit is not currently registered.

        Raises:
            ValueError: If the conduit has no name or is not registered.
        """
        self.check_cleaned()
        if conduit.name is None:
            raise ValueError("Conduit name cannot be None for cloud unregistration.")

        removed = self._registry.pop(conduit.name, None)
        if removed is None:
            raise ValueError(f"Conduit with name {conduit.name} is not registered in the cloud.")
