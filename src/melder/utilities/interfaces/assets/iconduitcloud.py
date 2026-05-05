from typing import runtime_checkable, Optional, Protocol, Tuple
from melder.utilities.interfaces.assets.icleanable import ICleanable
from melder.utilities.interfaces.assets.iconduit import IConduit

class IConduitCloud(ICleanable, Protocol):
    """
    An Interface for an abstract factory for named conduits.

    The ConduitCloud provides a central location to retrieve conduits by a
    human-readable name, intended for top-level access in
    highly dynamic systems.
    """
    _id: str

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
        ...

    def get_conduit_by_name(self, name: str) -> IConduit:
        """
        Retrieve a conduit by its registered name.
        """
        ...

    def get_conduit_by_id(self, conduit_id: str) -> IConduit:
        """
        Retrieve a conduit by its registered identifier.
        """
        ...

    def list_conduit_ids(self) -> Tuple[str, ...]:
        """
        Return the registered conduit identifiers in this cloud.
        """
        ...

    def list_conduit_names(self) -> Tuple[str, ...]:
        """
        Return the registered conduit names in this cloud.
        """
        ...

    def count_conduits(self) -> int:
        """
        Return the number of registered conduits in this cloud.
        """
        ...

    def has_conduit_id(self, conduit_id: str) -> bool:
        """
        Return whether the given conduit id is present in this cloud.
        """
        ...

    def has_conduit_name(self, name: str) -> bool:
        """
        Return whether the given conduit name is present in this cloud.
        """
        ...

    def find_conduit_id_by_name(self, name: str) -> Optional[str]:
        """
        Return the conduit id registered for one name, if present.
        """
        ...

    def _register_conduit(self, conduit: IConduit):
        """
        Registers a named conduit into the cloud. (Internal use)

        Args:
            conduit (IConduit): The conduit instance to register.

        Raises:
            ValueError: If the conduit's name is None or already exists
                in the registry.
        """
        ...
