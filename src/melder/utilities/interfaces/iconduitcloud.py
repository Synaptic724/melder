from typing import runtime_checkable, Optional, Protocol, Tuple
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.iconduit import IConduit

@runtime_checkable
class IConduitCloud(ICleanable, Protocol):
    """
    Interface for a frame-local conduit and cluster service facade.

    The ConduitCloud provides a central location to retrieve root conduits
    within one frame, manage explicit dynamic cloud registration, and orchestrate
    frame-local conduit-cluster behavior.
    """
    _id: str

    @property
    def frame_name(self) -> str:
        """
        Return the owning frame name served by this cloud.
        """
        ...

    def get_conduit(self, name: str) -> IConduit:
        """
        Retrieve a root conduit by its registered name in this frame.

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
        Retrieve a root conduit by its registered name in this frame.
        """
        ...

    def get_conduit_by_id(self, conduit_id: str) -> IConduit:
        """
        Retrieve a root conduit by its registered identifier in this frame.
        """
        ...

    def list_conduit_ids(self) -> Tuple[str, ...]:
        """
        Return the registered root-conduit identifiers in this frame.
        """
        ...

    def list_conduit_names(self) -> Tuple[str, ...]:
        """
        Return the registered root-conduit names in this frame.
        """
        ...

    def list_cloud_names(self) -> Tuple[str, ...]:
        """
        Return the explicit dynamic cloud-entry names in this frame.
        """
        ...

    def count_conduits(self) -> int:
        """
        Return the number of registered root conduits in this frame.
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

    def _register_conduit(self, conduit: IConduit) -> None:
        """
        Registers a named conduit into the cloud. (Internal use)

        Args:
            conduit (IConduit): The conduit instance to register.

        Raises:
            ValueError: If the conduit's name is None or already exists
                in the registry.
        """
        ...

    def _unregister_conduit(self, conduit: IConduit) -> None:
        """
        Remove one named conduit from the cloud. (Internal use)

        Args:
            conduit (IConduit): The conduit instance to unregister.

        Raises:
            ValueError: If the conduit name is missing or not registered.
        """
        ...

    def _add_root_conduit(self, conduit: IConduit) -> None:
        """
        Register one root conduit into the borrowed frame-owned root stores.
        """
        ...

    def _remove_root_conduit(self, conduit: IConduit) -> None:
        """
        Remove one root conduit from the borrowed frame-owned root stores.
        """
        ...

    def create_cluster(self, cluster_name: str) -> None:
        """
        Create one frame-local conduit cluster.
        """
        ...

    def delete_cluster(self, cluster_name: str) -> None:
        """
        Delete one frame-local conduit cluster.
        """
        ...

    def add_conduit_to_cluster(self, conduit: IConduit, cluster_name: str) -> None:
        """
        Add one conduit to one frame-local cluster.
        """
        ...

    def remove_conduit_from_cluster(
            self,
            conduit: IConduit,
            cluster_name: str,
    ) -> None:
        """
        Remove one conduit from one frame-local cluster.
        """
        ...

    def get_clusters_for_conduit(self, conduit_id: str) -> list[str]:
        """
        Return the cluster names that contain one conduit id.
        """
        ...

    def refresh_cluster_shares_for_conduit(self, conduit: IConduit) -> None:
        """
        Refresh cluster sharing for one conduit across all of its clusters.
        """
        ...

    def list_cluster_names(self) -> Tuple[str, ...]:
        """
        Return the current frame-local cluster names.
        """
        ...
