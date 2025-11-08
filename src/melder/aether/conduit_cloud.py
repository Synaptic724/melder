from melder.utilities.data_structures.concurrent_dictionary import ConcurrentDict
from melder.utilities.interfaces.interfaces import IConduit
from melder.utilities.general_base.sealable import Sealable
from threading import Lock


class ConduitCloud(Sealable):
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
        _registry (ConcurrentDict): A map of `conduit_name` to `IConduit` instance.
    """
    def __init__(self, name: str):
        """
        Initializes the ConduitCloud.

        Args:
            name (str): The name of the AethericFrame this cloud serves.
        """
        super().__init__()
        self._lock = Lock()
        self._name = name
        self._registry = ConcurrentDict()


    def get_conduit(self, name: str) -> IConduit:
        """
        Retrieves a conduit by its registered name.

        Args:
            name (str): The unique name of the conduit.

        Returns:
            IConduit: The conduit instance.

        Raises:
            RuntimeError: If the ConduitCloud is sealed.
            ValueError: If a conduit with that name is not found.
        """
        if self._sealed:
            raise RuntimeError("ConduitCloud is sealed and cannot be used.")
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
        if conduit.name is None:
            raise ValueError("Conduit name cannot be None for cloud registration.")

        if conduit.name in self._registry:
            raise ValueError(f"Conduit with name {conduit.name} already exists in the cloud. Please rename conduit to something unique.")
        self._registry[conduit.name] = conduit

    def seal(self):
        """
        Seals the ConduitCloud, clearing its registry.

        This operation is idempotent.
        """
        with self._lock:
            if self._sealed:
                return
            self._registry.clear()
            self._sealed = True
