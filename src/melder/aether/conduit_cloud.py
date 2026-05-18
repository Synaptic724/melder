import threading
from typing import Dict, Optional, Tuple
import ulid
# Melder imports
from melder.utilities.interfaces.iconduit import IConduit
from melder.utilities.interfaces.iconduitcloud import IConduitCloud
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
            self._cleaned = True

            del self._registry
        del self._lock


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
        return self.get_conduit_by_name(name)

    def get_conduit_by_name(self, name: str) -> IConduit:
        """
        Return a registered conduit by name.

        Args:
            name:
                Registered conduit name to resolve.

        Returns:
            IConduit: Matching conduit instance.

        Raises:
            RuntimeError: If the ConduitCloud is cleaned.
            ValueError: If the conduit name is not registered.
        """
        self.check_cleaned()
        with self._lock:
            conduit = self._registry.get(name)
            if conduit is not None:
                return conduit
        raise ValueError("Conduit with name {0} not found.".format(name))

    def get_conduit_by_id(self, conduit_id: str) -> IConduit:
        """
        Return a registered conduit by id.

        Args:
            conduit_id:
                Conduit id to resolve.

        Returns:
            IConduit: Matching conduit instance.

        Raises:
            RuntimeError: If the ConduitCloud is cleaned.
            ValueError: If the conduit id is not registered.
        """
        self.check_cleaned()
        with self._lock:
            for conduit in self._registry.values():
                if conduit.id == conduit_id:
                    return conduit
        raise ValueError("Conduit with id {0} not found.".format(conduit_id))

    def list_conduit_ids(self) -> Tuple[str, ...]:
        """
        Return the registered conduit ids in this cloud.

        Returns:
            Tuple[str, ...]: Snapshot of conduit ids.
        """
        self.check_cleaned()
        with self._lock:
            return tuple(conduit.id for conduit in self._registry.values())

    def list_conduit_names(self) -> Tuple[str, ...]:
        """
        Return the registered conduit names in this cloud.

        Returns:
            Tuple[str, ...]: Snapshot of conduit names.
        """
        self.check_cleaned()
        with self._lock:
            return tuple(self._registry.keys())

    def count_conduits(self) -> int:
        """
        Return the number of registered conduits in this cloud.

        Returns:
            int: Number of registered conduits.
        """
        self.check_cleaned()
        with self._lock:
            return len(self._registry)

    def has_conduit_id(self, conduit_id: str) -> bool:
        """
        Return whether one conduit id is registered in this cloud.

        Args:
            conduit_id:
                Conduit id to check.

        Returns:
            bool: True when the conduit id is registered.
        """
        self.check_cleaned()
        with self._lock:
            return any(conduit.id == conduit_id for conduit in self._registry.values())

    def has_conduit_name(self, name: str) -> bool:
        """
        Return whether one conduit name is registered in this cloud.

        Args:
            name:
                Conduit name to check.

        Returns:
            bool: True when the conduit name is registered.
        """
        self.check_cleaned()
        with self._lock:
            return name in self._registry

    def find_conduit_id_by_name(self, name: str) -> Optional[str]:
        """
        Return the conduit id registered under one conduit name, if present.

        Args:
            name:
                Conduit name to resolve.

        Returns:
            Optional[str]: Matching conduit id, or None when missing.
        """
        self.check_cleaned()
        with self._lock:
            conduit = self._registry.get(name)
            if conduit is None:
                return None
            return conduit.id

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
        with self._lock:
            if conduit.name is None:
                raise ValueError("Conduit name cannot be None for cloud registration.")

            if conduit.name in self._registry:
                raise ValueError(
                    "Conduit with name {0} already exists in the cloud. Please rename conduit to something unique.".format(
                        conduit.name
                    )
                )
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
        with self._lock:
            conduit_name = conduit._name
            if conduit_name is None:
                raise ValueError("Conduit name cannot be None for cloud unregistration.")

            removed = self._registry.pop(conduit_name, None)
            if removed is None:
                raise ValueError(
                    "Conduit with name {0} is not registered in the cloud.".format(
                        conduit_name
                    )
                )
