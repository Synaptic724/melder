import threading
from typing import Optional, Set, Dict

import ulid
# Melder Imports
from melder.utilities.interfaces import IConduit, IAether, IAethericFrame
from melder.utilities.general_base.cleanable import Cleanable
from melder.aether.aetheric_frame_configuration import AethericFrameConfiguration
from melder.aether.conduit_cloud import ConduitCloud
from melder.spellbook.bind.spell_index import SpellIndex
from melder.aether.dev_ops.spell_system_states.spell_system_states import SpellSystemStates
from melder.aether.dev_ops.dev_ops_manager import DevOpsManager
from melder.aether.conduit.conduit_cluster import ConduitCluster
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class AethericFrame(Cleanable, IAethericFrame):
    """
    Manage one isolated runtime frame within `Aether`.

    `AethericFrame` is the per-frame ownership boundary beneath the global
    `Aether` singleton. It owns the frame-local conduit registry, spell/index
    registries, cluster state, frame-level posture/config references, and the
    DevOps and mutation services tied to that frame.

    Contract:
      - Owns root conduits and their spell registries.
      - Owns a stable root-conduit name index for per-frame lookup.
      - Owns the version registry for all `SpellIndex` lineages in this frame.
      - Owns `SpellSystemStates` and `DevOpsManager` for this frame.
      - Owns one narrow frame-level AR posture object distinct from the richer
        shared Spellbook configuration object.
      - Detaches itself from `Aether` only after frame-owned cleanup completes.

    Threading / Concurrency:
      - Uses one frame-local `RLock` to guard cleanup and frame-owned registry
        mutation.
      - Relies on child objects to guard their own internal state.
    """
    __melder_internal__ = _mrg.sentinel
    def __init__(self, aether: IAether, name: str) -> None:
        """
        Initialize a new AethericFrame.

        Args:
            aether:
                Owning `Aether` singleton responsible for registry attachment
                and detachment of this frame.
            name: Human-readable name for this frame. Used for identification
                  and logging; uniqueness is expected but not enforced here.
        """
        super().__init__()

        if aether is None:
            raise TypeError("aether cannot be None")
        if not isinstance(aether, IAether):
            raise TypeError("aether must satisfy IAether")
        if not name:
            raise ValueError("name cannot be empty")

        self._aether: IAether = aether
        self.name: str = name
        self._id: str = str(ulid.ULID())
        self._lock: threading.RLock = threading.RLock()

        # All root conduits created in this frame:
        #   conduit_id -> IConduit
        self._conduits: Dict[str, IConduit] = {}
        # Stable root-conduit name registry:
        #   conduit_name -> conduit_id
        self._conduit_ids_by_name: Dict[str, str] = {}

        # SpellIndex registry per conduit:
        #   conduit_id -> Set[SpellIndex]
        self._spell_registry: Dict[str, Set[SpellIndex]] = {}

        # SHA256 version registry per conduit:
        #   conduit_id -> Set[str]
        self._version_registry: Dict[str, Set[str]] = {}

        # Conduit clusters (grouping by logical name):
        #   cluster_name -> ConduitCluster
        self._conduit_clusters: Dict[str, ConduitCluster] = {}

        # Dynamic-mode "cloud" factory for named conduits.
        self._conduit_cloud: ConduitCloud = ConduitCloud(name)

        # Per-frame graph + dirtiness registry for all spell lineages.
        self._spell_system_states: SpellSystemStates = SpellSystemStates(self)

        # Per-frame DevOps hub: incidents + change-control over this frame.
        self._dev_ops_manager: DevOpsManager = DevOpsManager(self._spell_system_states)

        # Shared full Spellbook configuration for this frame (set elsewhere).
        self._configuration = None
        # Narrow frame-level AR posture derived from Spellbook configuration.
        self._frame_configuration: Optional[AethericFrameConfiguration] = None

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------
    def cleanup(self) -> None:
        """
        Clean up the frame and all of its owned runtime state.

        Contract:
        - Idempotent and lock-guarded.
        - Cleans frame-owned conduits, registries, mutation services, and
          DevOps services before dropping top-level references.
        - Detaches the cleaned frame from its owner `Aether` after teardown is
          complete.

        Returns:
            None.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._cleanup_data_structures()
            if self._frame_configuration is not None:
                self._frame_configuration.cleanup()
                self._frame_configuration = None
            self._configuration = None
            self._id = None
            self._aether._detach_cleaned_frame(self.name, self)
            self.name = None
            self._aether = None
        self._lock = None



    def _cleanup_data_structures(self) -> None:
        """
        Clean up all frame-owned registries and child services.

        Contract:
        - Cleans child conduits before clearing conduit registries.
        - Clears spell, version, and cluster registries owned by the frame.
        - Cleans conduit cloud, mutation research, spell-system-state, and
          DevOps services when present.

        Returns:
            None.
        """
        # Conduits
        if self._conduits is not None:
            for conduit in list(self._conduits.values()):
                try:
                    conduit.cleanup()
                except Exception:
                    # DevOps surfaces can record incidents if you want;
                    # frame cleanup never dies on conduit cleanup.
                    pass
            self._conduits.clear()
            self._conduits = None

        if self._conduit_ids_by_name is not None:
            self._conduit_ids_by_name.clear()
            self._conduit_ids_by_name = None

        # SpellIndex registry
        if self._spell_registry is not None:
            self._spell_registry.clear()
            self._spell_registry = None

        # Version registry
        if self._version_registry is not None:
            self._version_registry.clear()
            self._version_registry = None

        # Conduit clusters
        if self._conduit_clusters is not None:
            for cluster in list(self._conduit_clusters.values()):
                try:
                    cluster.cleanup()
                except Exception:
                    pass
            self._conduit_clusters.clear()
            self._conduit_clusters = None

        # Dynamic conduit cloud
        if self._conduit_cloud is not None:
            self._conduit_cloud.cleanup()
            self._conduit_cloud = None

        # Spell system states registry
        if self._spell_system_states is not None:
            self._spell_system_states.cleanup()
            self._spell_system_states = None

        # DevOps manager (incidents + change control)
        if self._dev_ops_manager is not None:
            self._dev_ops_manager.cleanup()
            self._dev_ops_manager = None

    # ------------------------------------------------------------------
    # Context Manager
    # ------------------------------------------------------------------
    def __enter__(self) -> "AethericFrame":
        """
        Enter the frame lock context and return `self`.

        Returns:
            AethericFrame:
                This frame instance while the frame-level lock is held.
        """
        self.check_cleaned()
        self._lock.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        Exit the frame lock context and release the frame-level lock.

        Returns:
            None.
        """
        # No check_cleaned() here to guarantee lock release on teardown paths.
        self._lock.release()

    # ------------------------------------------------------------------
    # DevOps / control-plane accessors
    # ------------------------------------------------------------------
    @property
    def spell_system_states(self) -> SpellSystemStates:
        """
        Per-frame SpellSystemStates registry.

        This is the "control tower" for:
          - lineage graph topology,
          - dirty vs transitively dirty flags,
          - basic impact analysis.

        MutationResearch and DevOpsManager both use this as the ground truth.
        """
        self.check_cleaned()
        return self._spell_system_states

    @property
    def dev_ops_manager(self) -> DevOpsManager:
        """
        Per-frame DevOps hub.

        Exposes:
          - incident_manager
          - change_control_manager
          - direct access back to SpellSystemStates

        This is the primary entrypoint for AI / tools that want to reason
        about health, incidents, and pending changes in this frame.
        """
        self.check_cleaned()
        return self._dev_ops_manager

    @property
    def frame_configuration(self) -> Optional[AethericFrameConfiguration]:
        """
        Return the narrow frame-level AR posture, if one has been bound.

        Returns:
            Optional[AethericFrameConfiguration]: Bound frame posture or None
            when no posture has been bound yet.
        """
        self.check_cleaned()
        return self._frame_configuration

    # ------------------------------------------------------------------
    # Version Registry Maintenance
    # ------------------------------------------------------------------
    def refresh_version_registry(self) -> None:
        """
        Rebuild the version registry from the current `SpellIndex` registry.

        Contract:
          - Recomputes the per-conduit cached version-id sets from scratch.
          - Intended after binding, mutation, or promotion changes that may
            alter the set of version ids advertised by one or more spell
            lineages.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            if self._spell_registry is None:
                return

            # Start fresh
            self._version_registry = {}

            for conduit_id, spell_set in self._spell_registry.items():
                version_set: Set[str] = set()

                for spell_index in spell_set:
                    # SpellIndex.get_all_versions() returns set[str]
                    versions = spell_index.get_all_versions()
                    for version_id in versions:
                        version_set.add(version_id)

                self._version_registry[conduit_id] = version_set

    def has_version(self, version_id: str) -> bool:
        """
        Check whether the given SHA256 `version_id` exists in this frame.

        Contract:
          - Uses the cached `_version_registry`.
          - Returns False for empty ids or when the cache is unavailable.

        Returns:
            bool:
                True when any conduit in this frame owns a `SpellIndex` whose
                version set contains `version_id`.
        """
        self.check_cleaned()
        if not version_id:
            return False

        with self._lock:
            if self._version_registry is None:
                return False

            for version_set in self._version_registry.values():
                if version_id in version_set:
                    return True
        return False

    def get_all_versions(self) -> set[str]:
        """
        Return a flat set of all cached SHA256 version ids in this frame.

        Contract:
          - Uses the cached `_version_registry`.
          - Returns an empty set when the cache is unavailable.

        Returns:
            set[str]:
                All cached version ids across every conduit in the frame.
        """
        self.check_cleaned()
        result: set[str] = set()
        with self._lock:
            if self._version_registry is None:
                return result

            for version_set in self._version_registry.values():
                for version_id in version_set:
                    result.add(version_id)
        return result

    def find_and_return_spell_index(self, version_id: str) -> SpellIndex | None:
        """
        Find and return the `SpellIndex` that contains the given version id.

        Contract:
          - Scans the frame-owned `_spell_registry`.
          - Returns `None` for empty ids or when no matching lineage is found.

        Args:
            version_id: SHA256 version id to search for.

        Returns:
            SpellIndex | None:
                The lineage that owns `version_id`, or `None` when no lineage
                in this frame advertises that version.
        """
        self.check_cleaned()
        if not version_id:
            return None

        with self._lock:
            if self._spell_registry is None:
                return None

            for spell_set in self._spell_registry.values():
                for spell_index in spell_set:
                    if version_id in spell_index.get_all_versions():
                        return spell_index
        return None
