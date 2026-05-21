import threading
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple
if TYPE_CHECKING:
    from melder.aether.conduit.conduit import Conduit
import ulid
from mypy_extensions import mypyc_attr
from types import TracebackType

# Melder imports
from melder.aether.conduit.conduit_cluster import ConduitCluster
from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

@mypyc_attr(native_class=True)
class ConduitCloud(Cleanable):
    """
    Frame-scoped conduit and cluster service facade.

    `ConduitCloud` is the current-frame service surface used for:
    - direct root-conduit lookup inside one frame,
    - derived named-cloud visibility over frame-owned conduits,
    - cluster creation / membership / share refresh, and
    - frame-local conduit discovery that does not belong on `Conduit`.

    Contract:
    - One cloud belongs to one frame name.
    - Borrows frame-owned root-conduit stores by reference.
    - Owns the frame-local cluster registry and cluster lifecycle.
    - Does not own conduit lifecycle; `AethericFrame` remains the owner of the
      borrowed conduit stores.
    - Thread-safe access is serialized with the instance `RLock`.
    """
    __melder_internal__ = _mrg.sentinel

    def __init__(
            self,
            name: str,
            conduits: Dict[str, "Conduit"],
            conduit_ids_by_name: Dict[str, str],
    ) -> None:
        """
        Initialize the frame-scoped conduit and cluster service facade.

        Purpose:
            Create the frame-local service surface owned by one
            `AethericFrame` over its borrowed conduit stores.

        Args:
            name (str): The name of the AethericFrame this cloud serves.
            conduits (Dict[str, Conduit]):
                Borrowed root-conduit registry owned by the frame.
            conduit_ids_by_name (Dict[str, str]):
                Borrowed root-conduit name registry owned by the frame.
        Contract:
            - Starts with an empty owned cluster registry.
            - Stores the owning frame name for later diagnostics/identity.
            - Retains borrowed references to the frame-owned root-conduit
              stores instead of copying them.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()
        self._name: str = name
        self._conduits: Dict[str, "Conduit"] = conduits
        self._conduit_ids_by_name: Dict[str, str] = conduit_ids_by_name
        self._conduit_clusters: Dict[str, ConduitCluster] = {}
        self._id: str = str(ulid.ULID())

    def cleanup(self) -> None:
        """
        Clear the owned dynamic cloud registry and finalize the cloud.

        Purpose:
            Drop the cloud-owned dynamic registry without mutating the
            frame-owned conduit stores.

        Contract:
            - Idempotent and lock-guarded.
            - Cleans cloud-owned cluster state before dropping owned refs.
            - Does not clean the conduit objects or clear the borrowed
              frame-owned root-conduit stores.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            for cluster in list(self._conduit_clusters.values()):
                try:
                    cluster.cleanup()
                except Exception:
                    pass
            self._conduit_clusters.clear()
            self._cleaned = True

            del self._conduits
            del self._conduit_ids_by_name
            del self._conduit_clusters
            del self._name
            del self._id
        del self._lock


    #region Context Manager
    def __enter__(self) -> "ConduitCloud":
        """
        Acquire the registry lock and return this cloud.

        Contract:
            - Holds the cloud lock until `__exit__` runs.
        """
        self._lock.acquire()
        return self

    def __exit__(
            self,
            exc_type: Optional[type[BaseException]],
            exc_value: Optional[BaseException],
            traceback: Optional[TracebackType],
    ) -> None:
        """
        Release the registry lock acquired by `__enter__`.
        """
        self._lock.release()

    #endregion Context Manager

    @property
    def frame_name(self) -> str:
        """
        Return the owning frame name served by this cloud.

        Returns:
            str: The current frame name.
        """
        self.check_cleaned()
        return self._name


    def get_conduit(self, name: str) -> Conduit:
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
            Conduit: The conduit instance.

        Raises:
            RuntimeError: If the ConduitCloud is cleaned.
            ValueError: If a conduit with that name is not found.
        """
        return self.get_conduit_by_name(name)

    def get_conduit_by_name(self, name: str) -> Conduit:
        """
        Return a root conduit by name from this frame.

        Args:
            name:
                Root conduit name to resolve.

        Returns:
            Conduit: Matching conduit instance.

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

    def get_conduit_by_id(self, conduit_id: str) -> Conduit:
        """
        Return a root conduit by id from this frame.

        Args:
            conduit_id:
                Root conduit id to resolve.

        Returns:
            Conduit: Matching conduit instance.

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

    def list_cloud_names(self) -> Tuple[str, ...]:
        """
        Return the derived named dynamic root-conduit view for this frame.

        Returns:
            Tuple[str, ...]: Snapshot of dynamic cloud-entry names.
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
            self._conduit_clusters[cluster_name] = ConduitCluster(
                cluster_name,
                self._conduits,
                self._name,
            )

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

    def add_conduit_to_cluster(self, conduit: Conduit, cluster_name: str) -> None:
        """
        Add one conduit to one frame-local cluster.

        Args:
            conduit (Conduit): Conduit to add.
            cluster_name (str): Target cluster.
        """
        self.check_cleaned()
        cluster = self._get_cluster(cluster_name)
        cluster.add_member(conduit.id)
        cluster.handle_join(conduit)

    def remove_conduit_from_cluster(
            self,
            conduit: Conduit,
            cluster_name: str,
    ) -> None:
        """
        Remove one conduit from one frame-local cluster.

        Args:
            conduit (Conduit): Conduit to remove.
            cluster_name (str): Target cluster.
        """
        self.check_cleaned()
        cluster = self._get_cluster(cluster_name)
        cluster.remove_member(conduit.id)
        cluster.handle_leave(conduit)

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

    def refresh_cluster_shares_for_conduit(self, conduit: Conduit) -> None:
        """
        Refresh cluster sharing for one conduit across all of its clusters.

        Args:
            conduit (Conduit): Target conduit.
        """
        self.check_cleaned()
        cluster_names = self.get_clusters_for_conduit(conduit.id)
        for cluster_name in cluster_names:
            cluster = self._get_cluster(cluster_name)
            cluster.refresh_member_shares(conduit)

    def get_cluster(self, cluster_name: str) -> ConduitCluster:
        """
        Return one frame-local cluster by name.

        Args:
            cluster_name (str): Target cluster name.

        Returns:
            ConduitCluster: Matching cluster.

        Raises:
            ValueError: If the cluster does not exist.
        """
        return self._get_cluster(cluster_name)

    def list_cluster_names(self) -> Tuple[str, ...]:
        """
        Return the current frame-local cluster names.

        Returns:
            Tuple[str, ...]: Snapshot of cluster names.
        """
        self.check_cleaned()
        with self._lock:
            return tuple(self._conduit_clusters.keys())

    def _get_cluster(self, cluster_name: str) -> ConduitCluster:
        """
        Resolve one frame-local cluster by name.

        Args:
            cluster_name (str): Target cluster name.

        Returns:
            ConduitCluster: Matching cluster.

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

