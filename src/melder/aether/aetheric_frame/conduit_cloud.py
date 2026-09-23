import threading
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, ClassVar

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.aetheric_frame import AethericFrame
    from melder.aether.conduit.conduit import Conduit

from types import TracebackType

from melder.utilities.helpers.ulid_factory import new_ulid

# Melder imports
from melder.aether.conduit.conduit_cluster import ConduitCluster
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.aetheric_frame.dev_ops.devops_identity import DevopsIdentity
from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
    DevopsInformationRegistry,
)
from melder.aether.spellbook.configuration.system_state import SystemState
from melder.utilities.general_base.cleanable import Cleanable


class ConduitCloud(Cleanable):
    """
    Frame-scoped conduit and cluster service facade.

    `ConduitCloud` is the current-frame service surface used for:
    - direct named-conduit lookup inside one frame,
    - discovery of named normal roots and active lesser scopes,
    - cluster creation / membership / share refresh, and
    - frame-local conduit discovery that does not belong on `Conduit`.

    Contract:
    - One cloud belongs to one frame name.
    - Borrows the frame-owned root-conduit store for cluster operations.
    - Owns a separate named directory; discovery never grants root ownership.
    - Owns the frame-local cluster registry and cluster lifecycle.
    - Does not own conduit lifecycle; `AethericFrame` remains the owner of the
      borrowed conduit stores.
    - Thread-safe access is serialized with the instance `RLock`.

    Owned State:
        The cluster registry, named directory and temporary promotion-name claims.
        Directory values are borrowed live conduits, not owned lifecycle objects.

    Threading:
        One instance `RLock` serializes directory and claim mutation. Directory
        helpers never acquire frame/ward locks or invoke callbacks. Frame root
        registration enters in frame -> cloud order. Lookups confer no lease.

    Lifecycle / Cleanup:
        Owned by one `AethericFrame` and cleaned with it. Cleaning the cloud
        destroys clusters (which it owns) but never conduits (which it does
        not).

    Registration:
        MELDER KERNEL - guarded. Reached through
        `Conduit.get_conduit_cloud()` or `AethericFrame.conduit_cloud`; users
        do not construct one, and since 2026-08-04 the class is not exported
        from the package root either. The initializer needs an `AethericFrame`
        and a `DevopsInformationRegistry`, neither of which is public, so
        `md.ConduitCloud(...)` was a name that could never be called - the
        export advertised a door that was painted on. The REACH is unchanged.

    Subsystem Context:
        The discovery and cluster facade for one frame. It exists
        so that lookup-by-name and cluster mechanics do not have to live on
        `Conduit` itself - a conduit knows its own lineage and peers, but "which
        conduits exist in this frame" is a frame-scoped question.

    System Context:
        The borrow-versus-own split is the load-bearing distinction and it
        decides teardown correctness. Clusters are OWNED, so cloud cleanup
        destroys them; conduits are BORROWED, so cloud cleanup must leave them
        completely alone - their root or parent tears them down. The name directory
        does not insert lesser scopes into the frame's root-ownership registry.
        Getting this backwards would either strand cluster state or destroy
        live conduits out from under their owner.
        `has_conduit_name` and `has_cluster_name` are the sanctioned public
        probes. That matters beyond convenience: cross-package cloud access is
        public-verb-only by law, and the crystallizer's load-admission host
        preflight uses exactly these two to detect name collisions before a
        formation is composed into a live world. A probe must also never BIRTH
        what it checks for, which is why admission reads the frame registry
        directly rather than going through `_ensure_frame`.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Frame-scoped conduit and cluster discovery facade, reached through
        `Conduit.get_conduit_cloud()` or `AethericFrame.conduit_cloud` and never constructed -
        its initializer needs an AethericFrame and a DevopsInformationRegistry, neither of which
        is public. Use has_conduit_name(...)/has_cluster_name(...) to probe without creating, and
        the cluster verbs to form member groups. Melder kernel machinery: read it to understand
        the runtime, do not drive it directly.
    """
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_name",
        "_aetheric_frame",
        "_conduits",
        "_named_conduits",
        "_conduit_names_by_id",
        "_reserved_conduit_names",
        "_conduit_clusters",
        "_id",
        "_devops_identity",
        "_devops_information_registry",
    ]


    def __init__(
            self,
            name: str,
            aetheric_frame: "AethericFrame",
            conduits: Dict[str, "Conduit"],
            devops_information_registry: DevopsInformationRegistry,
    ) -> None:
        """
        Initialize the frame-scoped conduit and cluster service facade.

        Purpose:
            Create the frame-local service surface owned by one
            `AethericFrame` over its borrowed conduit stores.

        Args:
            name (str): The name of the AethericFrame this cloud serves.
            aetheric_frame (AethericFrame):
                Owning frame used to inspect current posture when dynamic-only
                cluster features are requested.
            conduits (Dict[str, Conduit]):
                Borrowed root-conduit registry owned by the frame.
            devops_information_registry:
                Frame-owned dev-ops registry used for cloud identity and
                cluster-relation tracking.
        Contract:
            - Starts with empty cluster, named-discovery and promotion-claim registries.
            - Stores the owning frame name for later diagnostics/identity.
            - Retains the frame-owned root store for clusters. Root and lesser
              lifecycle code explicitly publishes names into the owned directory.

        Returns:
            None.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()
        self._name: str = name
        self._aetheric_frame: AethericFrame = aetheric_frame
        self._conduits: Dict[str, "Conduit"] = conduits
        self._named_conduits: Dict[str, Conduit] = {}
        self._conduit_names_by_id: Dict[str, str] = {}
        self._reserved_conduit_names: Dict[str, str] = {}
        self._conduit_clusters: Dict[str, ConduitCluster] = {}
        self._id: str = new_ulid()
        self._devops_information_registry: DevopsInformationRegistry = (
            devops_information_registry
        )
        self._devops_identity: DevopsIdentity = DevopsIdentity(
            owner_kind="conduit_cloud",
            owner_id=self._id,
            aetheric_frame_name=self._name,
            metadata={
                "cloud_name": self._name,
            },
            available_transactions=tuple(),
        )
        self._devops_identity.attach_registry(
            self._devops_information_registry,
            object_ref=self,
        )

    def cleanup(self) -> None:
        """
        Release named discovery, promotion claims and owned clusters.

        Purpose:
            Drop directory references without disposing borrowed conduits or
            mutating the frame-owned root store.

        Contract:
            - Idempotent and lock-guarded.
            - Cleans cloud-owned cluster state before dropping owned refs.
            - Does not clean the conduit objects or clear the borrowed
              frame-owned root-conduit stores.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            for cluster in list(self._conduit_clusters.values()):
                # Best-effort: the clusters are cloud-owned and are dropped right
                # after this loop, so one cluster's cleanup failure must not abort
                # cleanup of the remaining clusters or the cloud teardown below.
                try:
                    cluster.cleanup()
                except Exception:
                    continue
            self._conduit_clusters.clear()
            self._named_conduits.clear()
            self._conduit_names_by_id.clear()
            self._reserved_conduit_names.clear()
            self._cleaned = True

            self._devops_identity.cleanup()

            del self._conduits
            del self._named_conduits
            del self._conduit_names_by_id
            del self._reserved_conduit_names
            del self._conduit_clusters
            del self._devops_information_registry
            del self._devops_identity
            del self._aetheric_frame
            del self._name
            del self._id
        del self._lock

    @staticmethod
    def _validate_conduit_name(name: Optional[str]) -> str:
        """Validate an exact application name before any lifecycle side effects.

        Contract:
            Names are nonempty strings. No trimming or case normalization occurs.
        Args:
            name: Requested root or lesser name.
        Raises:
            TypeError: The supplied name is not a string.
            ValueError: The supplied name is empty.
        Returns:
            str: The unchanged, validated name.
        """
        if not isinstance(name, str):
            raise TypeError("Conduit name must be a string.")
        if not name:
            raise ValueError("Conduit name must be a nonempty string.")
        return name

    def _assert_name_available(self, name: str, conduit_id: Optional[str] = None) -> None:
        """Refuse another scope's live name or pending promotion claim.

        Contract:
            A scope may retain its own name. This probe reserves nothing; final
            publication rechecks under the same reentrant directory lock.
            Internal callers operate within the owning frame's live lifecycle.
        Args:
            name: Exact, nonempty requested name.
            conduit_id: Existing identity allowed to retain its own name/claim.
        Raises:
            TypeError: Name is not a string.
            ValueError: Name is empty or belongs to another identity.
        Returns:
            None.
        """
        self._validate_conduit_name(name)
        with self._lock:
            registered = self._named_conduits.get(name)
            reserved_id = self._reserved_conduit_names.get(name)
            if (
                    (registered is not None and registered._id != conduit_id)
                    or (reserved_id is not None and reserved_id != conduit_id)
            ):
                raise ValueError(f"Conduit with name {name} already exists.")

    def _register_named_conduit(self, conduit: Conduit) -> None:
        """Publish a named scope, replacing its former alias on normal promotion.

        Contract:
            The caller owns the scope's lifecycle lock/attachment window. Both
            maps change in one directory critical section. Only this identity's
            old alias is retired; no root ownership or callback is invoked here.
            The frame-owned Cloud remains live for this internal operation.
        Args:
            conduit: Live named root or attached lesser being published.
        Raises:
            TypeError: The scope has no string name.
            ValueError: Its name is empty or occupied by another scope/claim.
        Returns:
            None.
        """
        with self._lock:
            name = self._validate_conduit_name(conduit._name)
            self._assert_name_available(name, conduit._id)
            previous_name = self._conduit_names_by_id.get(conduit._id)
            if previous_name is not None and previous_name != name:
                del self._named_conduits[previous_name]
            self._named_conduits[name] = conduit
            self._conduit_names_by_id[conduit._id] = name

    def _unregister_named_conduit(self, conduit: Conduit) -> None:
        """Retire this exact scope's directory entry without touching its lifecycle.

        Contract:
            Idempotent for an unpublished or already retired scope. Resolves the
            stored name by id, so failed promotion cleanup can retire an old alias
            even after the Conduit's requested name changed. Runs no callbacks.
            Frame teardown calls this before cleaning its owned Cloud.
        Args:
            conduit: Scope being returned, destroyed or removed as a root.
        Returns:
            None. The caller clears a reusable lesser's name before pooling.
        """
        with self._lock:
            name = self._conduit_names_by_id.get(conduit._id)
            if name is not None and self._named_conduits[name] is conduit:
                del self._named_conduits[name]
                del self._conduit_names_by_id[conduit._id]

    def _reserve_conduit_name(self, conduit: Conduit, name: str) -> None:
        """Reserve a promotion destination while retaining the lesser's live entry.

        Contract:
            Claims are private admission state, absent from discovery. The upgrade
            caller releases its claim in finally. No lock remains held during setup.
            Public promotion has already admitted the live scope/frame lifecycle.
        Args:
            conduit: Existing identity requesting promotion.
            name: Requested normal-root name.
        Raises:
            ValueError: Another identity owns or claims the name.
            TypeError: Name is not a string.
        Returns:
            None.
        """
        with self._lock:
            self._assert_name_available(name, conduit._id)
            self._reserved_conduit_names[name] = conduit._id

    def _release_conduit_name(self, conduit: Conduit, name: str) -> None:
        """Release only this identity's temporary promotion claim.

        Contract:
            Safe after a failed promotion or frame teardown: a cleaned Cloud has
            already cleared every claim. Does not remove a published directory entry.
        Args:
            conduit: Identity that reserved the name.
            name: Reserved destination name.
        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._reserved_conduit_names.get(name) == conduit._id:
                del self._reserved_conduit_names[name]

    def _assert_cluster_operations_allowed(self) -> None:
        """
        Raise when conduit-cluster operations are disabled for the current frame.

        Contract:
            - Rejects cluster work when the frame posture is not dynamic.
            - Rejects cluster work when cluster features are explicitly
              disabled.
            - Rejects cluster work when all post-conjure transactions are
              disabled at the frame level.
        """
        frame_configuration = self._aetheric_frame.frame_configuration
        if frame_configuration is None:
            raise RuntimeError("Frame configuration is unavailable.")
        if frame_configuration.disable_conduit_cluster:
            raise RuntimeError(
                "Conduit-cluster operations are disabled for this frame."
            )
        if frame_configuration.disable_all_transactions_after_conjure:
            raise RuntimeError(
                "Conduit-cluster operations are disabled after conjure for this frame."
            )
        if frame_configuration.system_state is not SystemState.dynamic:
            raise RuntimeError(
                "Conduit-cluster operations require dynamic mode."
            )

    @staticmethod
    def _assert_normal_conduit(conduit: Conduit) -> None:
        """
        Raise when a cluster operation targets a non-normal conduit.

        Contract:
            - Cluster membership is limited to normal/root conduits.
            - Lesser, pooled, or cleaned conduits are rejected at the cloud boundary.
        """
        if conduit._conduit_state is not ConduitState.normal:
            raise RuntimeError(
                "Conduit-cluster operations require a normal conduit."
            )


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
        Contract:
            - Releases unconditionally, including when the block raised. Exception
              arguments are accepted and IGNORED, so no exception is suppressed.
            - Exactly one release per `__enter__`; the lock is reentrant.

        Threading:
            Releases the cloud lock acquired by `__enter__`.

        Lifecycle / Cleanup:
            Performs no cleaned-state check - it is purely the unlock half.

        Raises:
            RuntimeError: If called without a matching `__enter__` on this thread.

        """
        self._lock.release()

    #endregion Context Manager

    @property
    def frame_name(self) -> str:
        """
        Return the owning frame name served by this cloud.

        Contract:
            - The frame this cloud belongs to, fixed at construction and never
              reassigned.
            - Read WITHOUT the lock, unlike the collection accessors, because the
              value is immutable.

        Threading:
            Unsynchronized read of an immutable slot; safe from any thread.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the cloud has been cleaned.

        Returns:
            str: The current frame name.
        """
        self.check_cleaned()
        return self._name


    def get_conduit(self, name: str) -> Conduit:
        """
        Return a named normal or lesser conduit from this frame.

        Purpose:
            Provide direct named-scope lookup without changing scope ownership.

        Args:
            name (str): The unique name of the conduit.

        Contract:
            - Returns the borrowed live conduit registered under this exact name.
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
        Return a named normal or lesser conduit from this frame.

        Args:
            name:
                Exact live scope name to resolve.

        Returns:
            Conduit: Matching conduit instance.

        Raises:
            RuntimeError: If the ConduitCloud is cleaned.
            ValueError: If the conduit name is not registered.
        """
        self.check_cleaned()
        with self._lock:
            conduit = self._named_conduits.get(name)
            if conduit is None:
                raise ValueError("Conduit with name {0} not found.".format(name))
            return conduit

    def get_conduit_by_id(self, conduit_id: str) -> Conduit:
        """
        Return a named normal or lesser conduit by id from this frame.

        Args:
            conduit_id:
                Named scope's live conduit id to resolve.

        Returns:
            Conduit: Matching conduit instance.

        Raises:
            RuntimeError: If the ConduitCloud is cleaned.
            ValueError: If the conduit id is not registered.
        """
        self.check_cleaned()
        with self._lock:
            name = self._conduit_names_by_id.get(conduit_id)
            if name is not None:
                return self._named_conduits[name]
        raise ValueError("Conduit with id {0} not found.".format(conduit_id))

    def list_conduit_ids(self) -> Tuple[str, ...]:
        """
        Return the registered named-scope ids in this frame.

        Contract:
            - Returns a TUPLE SNAPSHOT taken under the lock, so it cannot mutate
              underneath the caller - but it goes stale the moment a conduit is
              registered or removed.
            - Covers REGISTERED conduits only; one still being constructed is absent.

        Threading:
            Reads and writes under `self._lock`, so the result is a coherent
            snapshot rather than a torn read.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the cloud has been cleaned.

        Returns:
            Tuple[str, ...]: Snapshot of conduit ids.
        """
        self.check_cleaned()
        with self._lock:
            return tuple(self._conduit_names_by_id.keys())

    def list_conduit_names(self) -> Tuple[str, ...]:
        """
        Return the registered normal-root and lesser-scope names in this frame.

        Contract:
            - Returns only live named scopes; unnamed and idle shells are absent.
              It has the same membership count as list_conduit_ids(), but callers
              must resolve by key rather than relying on positional alignment.

        Threading:
            Reads and writes under `self._lock`, so the result is a coherent
            snapshot rather than a torn read.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the cloud has been cleaned.

        Returns:
            Tuple[str, ...]: Snapshot of conduit names.
        """
        self.check_cleaned()
        with self._lock:
            return tuple(self._named_conduits.keys())

    def list_cloud_names(self) -> Tuple[str, ...]:
        """
        Return named normal and lesser scopes in either runtime mode.

        Contract:
            - CURRENTLY IDENTICAL to `list_conduit_names()` - both return the keys of
              the same name map, so they are interchangeable today. Prefer
              `list_conduit_names()`, which describes what is actually returned.

        Threading:
            Reads and writes under `self._lock`, so the result is a coherent
            snapshot rather than a torn read.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the cloud has been cleaned.

        Returns:
            Tuple[str, ...]: Snapshot of named cloud entries.
        """
        self.check_cleaned()
        with self._lock:
            return tuple(self._named_conduits.keys())

    def count_conduits(self) -> int:
        """
        Return the number of named scopes registered in this frame.

        Contract:
            - Matches both list_conduit_ids() and list_conduit_names(). Only named
              scopes are counted; this is not the frame's normal-root count.

        Threading:
            Reads and writes under `self._lock`, so the result is a coherent
            snapshot rather than a torn read.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the cloud has been cleaned.

        Returns:
            int: Number of registered conduits.
        """
        self.check_cleaned()
        with self._lock:
            return len(self._named_conduits)

    def has_conduit_id(self, conduit_id: str) -> bool:
        """
        Return whether one named-scope id is registered in this frame.

        Args:
            conduit_id:
                Conduit id to check.

        Contract:
            - Membership test against registered ids. False means "not registered",
              which includes a conduit that was cleaned and removed.

        Threading:
            Reads and writes under `self._lock`, so the result is a coherent
            snapshot rather than a torn read.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the cloud has been cleaned.

        Returns:
            bool: True when the conduit id is registered.
        """
        self.check_cleaned()
        with self._lock:
            return conduit_id in self._conduit_names_by_id

    def has_conduit_name(self, name: str) -> bool:
        """
        Return whether one live scope name is registered in this frame.

        Args:
            name:
                Conduit name to check.

        Contract:
            - Tests live discovery only. Unnamed scopes and temporary promotion
              claims are absent; a False result does not reserve the name.

        Threading:
            Reads and writes under `self._lock`, so the result is a coherent
            snapshot rather than a torn read.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the cloud has been cleaned.

        Returns:
            bool: True when the conduit name is registered.
        """
        self.check_cleaned()
        with self._lock:
            return name in self._named_conduits

    def has_cluster_name(self, cluster_name: str) -> bool:
        """
        Return whether one cluster name exists in this frame's cloud.

        Purpose:
            The public cluster-existence probe (public_cloud_seams
            2026-07-12): the crystallizer's admission preflight and the
            restore engine's cluster reuse lane previously read the
            private registry directly as a documented seam - this verb
            retires that debt (mirrors has_conduit_name).

        Args:
            cluster_name:
                Cluster name to check.

        Returns:
            bool: True when the cluster name is registered.
        """
        self.check_cleaned()
        with self._lock:
            return cluster_name in self._conduit_clusters

    def find_conduit_id_by_name(self, name: str) -> Optional[str]:
        """
        Return the live normal or lesser id registered under one name, if present.

        Args:
            name:
                Conduit name to resolve.

        Contract:
            - Returns None on a miss rather than raising, so None means "no conduit
              registered under that name" - it is not an error channel.
            - Names are unique in the map, so this resolves to at most one id.

        Threading:
            Reads and writes under `self._lock`, so the result is a coherent
            snapshot rather than a torn read.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the cloud has been cleaned.

        Returns:
            Optional[str]: Matching conduit id, or None when missing.
        """
        self.check_cleaned()
        with self._lock:
            conduit = self._named_conduits.get(name)
            return None if conduit is None else conduit._id

    def create_cluster(self, cluster_name: str) -> None:
        """
        Create one frame-local conduit cluster.

        Args:
            cluster_name (str): New cluster name.

        Raises:
            ValueError: If the cluster already exists.

        Returns:
            None.
        """
        self.check_cleaned()
        self._assert_cluster_operations_allowed()
        with self._lock:
            if cluster_name in self._conduit_clusters:
                raise ValueError(
                    "Cluster with name {0} already exists.".format(cluster_name)
                )
            self._conduit_clusters[cluster_name] = ConduitCluster(
                cluster_name,
                self._conduits,
                self._name,
                self._devops_information_registry,
            )

    def delete_cluster(self, cluster_name: str) -> None:
        """
        Delete one frame-local conduit cluster.

        Args:
            cluster_name (str): Cluster name to remove.

        Raises:
            ValueError: If the cluster does not exist.

        Returns:
            None.
        """
        self.check_cleaned()
        self._assert_cluster_operations_allowed()
        with self._lock:
            cluster = self._conduit_clusters.pop(cluster_name, None)
        if cluster is None:
            raise ValueError(
                "Cluster with name {0} does not exist.".format(cluster_name)
            )
        # Dissolve the team store first if a leader is still elected: deleting an
        # active cluster must not leave member facades bound to a leader store the
        # cluster no longer coordinates. Members are still live here (delete is not
        # frame teardown), so the drained unelect is safe.
        if cluster.master_conduit_id is not None:
            cluster.unelect_leader()
        cluster.cleanup()

    def add_conduit_to_cluster(self, conduit: Conduit, cluster_name: str) -> None:
        """
        Add one conduit to one frame-local cluster.

        Args:
            conduit (Conduit): Conduit to add.
            cluster_name (str): Target cluster.

        Contract:
            - MEMBERSHIP IS EXCLUSIVE: a conduit may belong to AT MOST ONE cluster, and
              joining a second raises `ValueError`. That exclusivity is load bearing -
              it keeps `unique_per_conduit_cluster` resolution unambiguous, because
              one conduit maps to exactly one team store.
            - To move a conduit between clusters you must REMOVE IT FIRST; there is
              no reassignment path.
            - Refused by frame posture when cluster operations are disabled, and
              refused for any conduit that is not NORMAL - lesser and pooled conduits
              cannot join.

        Threading:
            Reads and writes under `self._lock`, so the result is a coherent
            snapshot rather than a torn read.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the cloud has been cleaned.

        Returns:
            None.
        """
        self.check_cleaned()
        self._assert_cluster_operations_allowed()
        cluster = self._get_cluster(cluster_name)
        self._assert_normal_conduit(conduit)
        # Exclusive membership: a conduit may belong to at most one cluster. This
        # keeps `unique_per_conduit_cluster` resolution unambiguous -- one cluster
        # per conduit is the single-store property the team-store design relies on.
        if self.get_clusters_for_conduit(conduit.id):
            raise ValueError(
                f"Conduit {conduit.id} is already in a cluster; cluster "
                f"membership is exclusive (one per conduit)."
            )
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

        Contract:
            - Removes membership and then runs the cluster's leave handling, so shares
              held for the member are released as part of this call rather than
              lazily.
            - Refused by frame posture when cluster operations are disabled, and
              refused for non-NORMAL conduits. Note this is the DIRECT-API path: the
              transaction layer does not posture-gate cluster LEAVE, so the two
              routes differ.

        Threading:
            Reads and writes under `self._lock`, so the result is a coherent
            snapshot rather than a torn read.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the cloud has been cleaned.

        Returns:
            None.
        """
        self.check_cleaned()
        self._assert_cluster_operations_allowed()
        cluster = self._get_cluster(cluster_name)
        self._assert_normal_conduit(conduit)
        cluster.remove_member(conduit.id)
        cluster.handle_leave(conduit)

    def get_clusters_for_conduit(self, conduit_id: str) -> List[str]:
        """
        Return the cluster names that contain one conduit id.

        Args:
            conduit_id (str): Conduit identifier to query.

        Contract:
            - Returns a LIST, but because membership is EXCLUSIVE it holds AT MOST ONE
              name. A length above one means a corrupted invariant, not a supported
              case.
            - An empty list means the conduit is in no cluster - not an error.
            - Snapshots the cluster map under the lock and then inspects members
              OUTSIDE it, so a concurrent join or leave can be missed.

        Threading:
            Reads and writes under `self._lock`, so the result is a coherent
            snapshot rather than a torn read.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the cloud has been cleaned.

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

        Contract:
            - Re-synchronizes the conduit's shares in whatever cluster it belongs to.
              Because membership is exclusive this touches at most one cluster, and
              it is a NO-OP for a conduit in none.
            - Refused by frame posture when cluster operations are disabled, and
              refused for non-NORMAL conduits.
            - Resolves membership and then refreshes WITHOUT holding the cloud lock
              across the whole sequence, so a concurrent leave can race it.

        Threading:
            Reads and writes under `self._lock`, so the result is a coherent
            snapshot rather than a torn read.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the cloud has been cleaned.

        Returns:
            None.
        """
        self.check_cleaned()
        self._assert_cluster_operations_allowed()
        self._assert_normal_conduit(conduit)
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

        Contract:
            - Tuple snapshot of registered cluster names, taken under the lock.
            - Lists clusters that EXIST, including any with no current members.

        Threading:
            Reads and writes under `self._lock`, so the result is a coherent
            snapshot rather than a torn read.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the cloud has been cleaned.

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

