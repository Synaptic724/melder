import ulid
from melder.utilities.data_structures.concurrent_dictionary import ConcurrentDict
from melder.utilities.data_structures.concurrent_list import ConcurrentList
from melder.utilities.data_structures.concurrent_set import ConcurrentSet
from melder.utilities.interfaces.interfaces import IConduit
from melder.utilities.general_base.cleanable import Cleanable
from melder.aether.conduit_cloud import ConduitCloud
from melder.spellbook.bind.spell_index import SpellIndex
from threading import RLock

class AethericFrame(Cleanable):
    """
    Manages an isolated "universe" or "frame" within the Aether.

    An AethericFrame holds all top-level conduits, spell registries, and
    configurations for a specific, isolated domain. This allows multiple
    systems (e.g., different plugins or applications) to use the same
    Aether without interfering with each other's service registrations.

    This object is thread-safe.

    Attributes:
        name (str): The unique name of this frame.
        _lock (RLock): A reentrant lock ensuring thread-safe operations.
        _conduits (ConcurrentDict): Stores all root conduits created within this frame.
        _spell_registry (ConcurrentDict): Maps conduit ids to the set of
            spell IDs they own.
        _conduit_clusters (ConcurrentDict): Organizes conduits into named groups.
        _conduit_cloud (ConduitCloud): The abstract factory for named conduits
            in dynamic mode.
        _configuration (Configuration): The frozen configuration for this frame.
    """
    def __init__(self, name: str):
        """
        Initializes a new AethericFrame.

        Args:
            name (str): The unique, human-readable name for this frame.
        """
        super().__init__()
        self.name = name
        self._id: str = str(ulid.ULID())
        self._lock = RLock()
        # This retains all normal conduits i.e roots created by a spellbook
        # _conduits maps conduit IDs to IConduit instances
        self._conduits: ConcurrentDict[str, IConduit] = ConcurrentDict()
        # Holds conduit ids and their spell indices
        self._spell_registry: ConcurrentDict[str, ConcurrentSet[SpellIndex]] = ConcurrentDict()
        # Holds conduit ids and their spell IDs (SHA256 hashes)
        self._version_registry: ConcurrentDict[str, ConcurrentSet[str]] = ConcurrentDict()
        # Clusters only hold conduit IDs for grouping
        self._conduit_clusters: ConcurrentDict[str, ConcurrentList[str]] = ConcurrentDict()
        # This is the dynamic mode registry
        self._conduit_cloud = ConduitCloud(name)
        # This is the configuration for the Aetheric Frame
        self._configuration = None

    def cleanup(self):
        """
        Cleans up the Aetheric Frame, recursively cleaning all its conduits
        and clearing all internal registries.

        Once cleaned, the frame cannot be used. This operation is idempotent.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            # Cleanup all conduits and clear the registry
            for conduit in self._conduits.values():
                try:
                    conduit.cleanup()
                except Exception:
                    pass

            self._conduits.cleanup()
            self._spell_registry.cleanup()
            self._conduit_clusters.cleanup()
            self._conduit_cloud.cleanup()
            self._version_registry.cleanup()
            self._conduits = None
            self._spell_registry = None
            self._conduit_clusters = None
            self._conduit_cloud = None


    # -----------------------------
    # Version Registry Maintenance
    # -----------------------------

    def refresh_version_registry(self) -> None:
        """
        Rebuilds the version registry from the current SpellIndex registry.

        After this runs:
          - _version_registry[conduit_id] will contain all SHA256 versions
            for every SpellIndex owned by that conduit.
        """
        with self._lock:
            # Start fresh
            self._version_registry = ConcurrentDict()

            for conduit_id, spell_set in self._spell_registry.items():
                version_set = ConcurrentSet()

                for spell_index in spell_set:
                    # SpellIndex.get_all_versions() returns set[str]
                    versions = spell_index.get_all_versions()
                    for version_id in versions:
                        version_set.add(version_id)

                self._version_registry[conduit_id] = version_set

    def has_version(self, version_id: str) -> bool:
        """
        Checks if the given SHA256 version_id exists in this frame,
        using the prebuilt _version_registry.

        Args:
            version_id (str): The SHA256 version ID to check.

        Returns:
            bool: True if the version ID exists in this frame, False otherwise.
        """
        with self._lock:
            for version_set in self._version_registry.values():
                if version_id in version_set:
                    return True
        return False

    def get_all_versions(self) -> set[str]:
        """
        Returns a flat set of ALL SHA256 version IDs in this frame,
        using the prebuilt _version_registry.

        Returns:
            set[str]: A set of all version IDs in this frame.
        """
        result: set[str] = set()
        with self._lock:
            for version_set in self._version_registry.values():
                for version_id in version_set:
                    result.add(version_id)
        return result