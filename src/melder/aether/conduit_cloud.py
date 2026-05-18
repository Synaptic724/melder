import threading
from typing import Callable, Dict, List, Optional, Tuple
import ulid
# Melder imports
from melder.aether.conduit.conduit_cluster import ConduitCluster
from melder.utilities.interfaces.iconduit import IConduit
from melder.utilities.interfaces.iconduitcluster import IConduitCluster
from melder.utilities.interfaces.iconduitcloud import IConduitCloud
from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class ConduitCloud(Cleanable, IConduitCloud):
    """
    Frame-scoped conduit and cluster service facade.

    `ConduitCloud` is the current-frame service surface used for:
    - direct root-conduit lookup inside one frame,
    - explicit dynamic cloud registration,
    - cluster creation / membership / share refresh, and
    - root-conduit registry operations that do not belong on `Conduit`.

    Contract:
    - One cloud belongs to one frame name.
    - Borrows frame-owned root-conduit and cluster stores by reference.
    - Owns a separate dynamic cloud registry for explicit named-cloud exposure.
    - Does not own conduit lifecycle; `AethericFrame` remains the owner of the
      borrowed stores.
    - Thread-safe access is serialized with the instance `RLock`.
    """
    __melder_internal__ = _mrg.sentinel

    def __init__(
            self,
            name: str,
            conduits: Dict[str, IConduit],
            conduit_ids_by_name: Dict[str, str],
            conduit_clusters: Dict[str, IConduitCluster],
            owner_cleanup: Callable[[], None],
    ):
        """
        Initialize the frame-scoped conduit and cluster service facade.

        Purpose:
            Create the frame-local service surface owned by one
            `AethericFrame` over its borrowed conduit and cluster stores.

        Args:
            name (str): The name of the AethericFrame this cloud serves.
            conduits (Dict[str, IConduit]):
                Borrowed root-conduit registry owned by the frame.
            conduit_ids_by_name (Dict[str, str]):
                Borrowed root-conduit name registry owned by the frame.
            conduit_clusters (Dict[str, IConduitCluster]):
                Borrowed cluster registry owned by the frame.
            owner_cleanup (Callable[[], None]):
                Callback used to clean the owning frame when the root-conduit
                registry becomes empty.
        Contract:
            - Starts with an empty dynamic cloud registry.
            - Stores the owning frame name for later diagnostics/identity.
            - Retains borrowed references to the frame-owned root-conduit and
              cluster stores instead of copying them.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()
        self._name: str = name
        self._conduits: Dict[str, IConduit] = conduits
        self._conduit_ids_by_name: Dict[str, str] = conduit_ids_by_name
        self._conduit_clusters: Dict[str, IConduitCluster] = conduit_clusters
        self._owner_cleanup: Callable[[], None] = owner_cleanup
        self._registry: Dict[str, IConduit] = {}
        self._id: str = str(ulid.ULID())

    def cleanup(self):
        """
        Clear the owned dynamic cloud registry and finalize the cloud.

        Purpose:
            Drop the cloud-owned dynamic registry without mutating the
            frame-owned conduit and cluster stores.

        Contract:
            - Idempotent and lock-guarded.
            - Clears only cloud-owned registry state.
            - Does not clean the conduit objects or clear the borrowed frame
              stores.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._registry.clear()
            self._cleaned = True

            del self._registry
            del self._conduits
            del self._conduit_ids_by_name
            del self._conduit_clusters
            del self._owner_cleanup
            del self._name
            del self._id
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
        Return a root conduit by name from this frame.

        Purpose:
            Provide the direct human-readable root-conduit lookup path for one frame.

        Args:
            name (str): The unique name of the conduit.

        Contract:
            - Returns the live root conduit object registered in this frame.
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
        Return a root conduit by name from this frame.

        Args:
            name:
                Root conduit name to resolve.

        Returns:
            IConduit: Matching conduit instance.

        Raises:
            RuntimeError: If the ConduitCloud is cleaned.
            ValueError: If the conduit name is not registered.
        """
        self.check_cleaned()
        with self._lock:
            conduit_id = self._conduit_ids_by_name.get(name)
            if conduit_id is None:
                raise ValueError("Conduit with name {0} not found.".format(name))
            conduit = self._conduits.get(conduit_id)
            if conduit is None:
                raise ValueError("Conduit with name {0} not found.".format(name))
            return conduit

    def get_conduit_by_id(self, conduit_id: str) -> IConduit:
        """
        Return a root conduit by id from this frame.

        Args:
            conduit_id:
                Root conduit id to resolve.

        Returns:
            IConduit: Matching conduit instance.

        Raises:
            RuntimeError: If the ConduitCloud is cleaned.
            ValueError: If the conduit id is not registered.
        """
        self.check_cleaned()
        with self._lock:
            conduit = self._conduits.get(conduit_id)
            if conduit is not None:
                return conduit
        raise ValueError("Conduit with id {0} not found.".format(conduit_id))

    def list_conduit_ids(self) -> Tuple[str, ...]:
        """
        Return the registered root-conduit ids in this frame.

        Returns:
            Tuple[str, ...]: Snapshot of conduit ids.
        """
        self.check_cleaned()
        with self._lock:
            return tuple(self._conduits.keys())

    def list_conduit_names(self) -> Tuple[str, ...]:
        """
        Return the registered root-conduit names in this frame.

        Returns:
            Tuple[str, ...]: Snapshot of conduit names.
        """
        self.check_cleaned()
        with self._lock:
            return tuple(self._conduit_ids_by_name.keys())

    def count_conduits(self) -> int:
        """
        Return the number of registered root conduits in this frame.

        Returns:
            int: Number of registered conduits.
        """
        self.check_cleaned()
        with self._lock:
            return len(self._conduits)

    def has_conduit_id(self, conduit_id: str) -> bool:
        """
        Return whether one root conduit id is registered in this frame.

        Args:
            conduit_id:
                Conduit id to check.

        Returns:
            bool: True when the conduit id is registered.
        """
        self.check_cleaned()
        with self._lock:
            return conduit_id in self._conduits

    def has_conduit_name(self, name: str) -> bool:
        """
        Return whether one root conduit name is registered in this frame.

        Args:
            name:
                Conduit name to check.

        Returns:
            bool: True when the conduit name is registered.
        """
        self.check_cleaned()
        with self._lock:
            return name in self._conduit_ids_by_name

    def find_conduit_id_by_name(self, name: str) -> Optional[str]:
        """
        Return the root conduit id registered under one conduit name, if present.

        Args:
            name:
                Conduit name to resolve.

        Returns:
            Optional[str]: Matching conduit id, or None when missing.
        """
        self.check_cleaned()
        with self._lock:
            return self._conduit_ids_by_name.get(name)

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

    def _add_root_conduit(self, conduit: IConduit) -> None:
        """
        Register one root conduit into the borrowed frame-owned root stores.

        Args:
            conduit (IConduit): Root conduit to register.

        Raises:
            ValueError: If the conduit id or name is missing or already present.
        """
        self.check_cleaned()
        with self._lock:
            conduit_id = conduit.id
            conduit_name = conduit.name
            if not conduit_name:
                raise ValueError("Root conduit name is required.")
            if conduit_id in self._conduits:
                raise ValueError(
                    "Conduit with ID {0} already exists.".format(conduit_id)
                )
            existing_name_id = self._conduit_ids_by_name.get(conduit_name)
            if existing_name_id is not None and existing_name_id != conduit_id:
                raise ValueError(
                    "Conduit with name {0} already exists.".format(conduit_name)
                )
            self._conduits[conduit_id] = conduit
            self._conduit_ids_by_name[conduit_name] = conduit_id

    def _remove_root_conduit(self, conduit: IConduit) -> None:
        """
        Remove one root conduit from the borrowed frame-owned root stores.

        Args:
            conduit (IConduit): Root conduit to remove.

        Raises:
            ValueError: If the conduit is not present.
        """
        self.check_cleaned()
        with self._lock:
            conduit_id = conduit.id
            removed = self._conduits.pop(conduit_id, None)
            if removed is None:
                raise ValueError(
                    "Conduit with ID {0} does not exist.".format(conduit_id)
                )
            conduit_name = removed.name
            if conduit_name:
                mapped_id = self._conduit_ids_by_name.get(conduit_name)
                if mapped_id == conduit_id:
                    self._conduit_ids_by_name.pop(conduit_name, None)
                cloud_entry = self._registry.get(conduit_name)
                if cloud_entry is removed:
                    self._registry.pop(conduit_name, None)

    def cleanup_owner_frame_if_empty(self) -> bool:
        """
        Cleanup the owning frame when no root conduits remain.

        Returns:
            bool: True when owner cleanup was triggered, else False.
        """
        self.check_cleaned()
        with self._lock:
            should_cleanup = len(self._conduits) == 0
        if should_cleanup:
            self._owner_cleanup()
            return True
        return False

    def create_cluster(self, cluster_name: str) -> None:
        """
        Create one frame-local conduit cluster.

        Args:
            cluster_name (str): New cluster name.

        Raises:
            ValueError: If the cluster already exists.
        """
        self.check_cleaned()
        with self._lock:
            if cluster_name in self._conduit_clusters:
                raise ValueError(
                    "Cluster with name {0} already exists.".format(cluster_name)
                )
            self._conduit_clusters[cluster_name] = ConduitCluster(cluster_name)

    def delete_cluster(self, cluster_name: str) -> None:
        """
        Delete one frame-local conduit cluster.

        Args:
            cluster_name (str): Cluster name to remove.

        Raises:
            ValueError: If the cluster does not exist.
        """
        self.check_cleaned()
        with self._lock:
            cluster = self._conduit_clusters.pop(cluster_name, None)
        if cluster is None:
            raise ValueError(
                "Cluster with name {0} does not exist.".format(cluster_name)
            )
        cluster.cleanup()

    def add_conduit_to_cluster(self, conduit: IConduit, cluster_name: str) -> None:
        """
        Add one conduit to one frame-local cluster.

        Args:
            conduit (IConduit): Conduit to add.
            cluster_name (str): Target cluster.
        """
        self.check_cleaned()
        cluster = self._get_cluster(cluster_name)
        cluster.add_member(conduit.id)
        cluster.handle_join(conduit, self, self._name)

    def remove_conduit_from_cluster(
            self,
            conduit: IConduit,
            cluster_name: str,
    ) -> None:
        """
        Remove one conduit from one frame-local cluster.

        Args:
            conduit (IConduit): Conduit to remove.
            cluster_name (str): Target cluster.
        """
        self.check_cleaned()
        cluster = self._get_cluster(cluster_name)
        cluster.remove_member(conduit.id)
        cluster.handle_leave(conduit, self, self._name)

    def get_clusters_for_conduit(self, conduit_id: str) -> List[str]:
        """
        Return the cluster names that contain one conduit id.

        Args:
            conduit_id (str): Conduit identifier to query.

        Returns:
            List[str]: Cluster names containing the conduit.
        """
        self.check_cleaned()
        with self._lock:
            clusters = list(self._conduit_clusters.items())
        return [
            name for name, cluster in clusters
            if conduit_id in cluster.get_members()
        ]

    def refresh_cluster_shares_for_conduit(self, conduit: IConduit) -> None:
        """
        Refresh cluster sharing for one conduit across all of its clusters.

        Args:
            conduit (IConduit): Target conduit.
        """
        self.check_cleaned()
        cluster_names = self.get_clusters_for_conduit(conduit.id)
        for cluster_name in cluster_names:
            cluster = self._get_cluster(cluster_name)
            cluster.refresh_member_shares(conduit, self, self._name)

    def _get_cluster(self, cluster_name: str) -> IConduitCluster:
        """
        Resolve one frame-local cluster by name.

        Args:
            cluster_name (str): Target cluster name.

        Returns:
            IConduitCluster: Matching cluster.

        Raises:
            ValueError: If the cluster does not exist.
        """
        self.check_cleaned()
        with self._lock:
            cluster = self._conduit_clusters.get(cluster_name)
        if cluster is None:
            raise ValueError(
                "Cluster with name {0} does not exist.".format(cluster_name)
            )
        return cluster
