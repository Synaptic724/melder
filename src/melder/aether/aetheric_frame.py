from __future__ import annotations
import threading
import ulid
# Melder Imports
from melder.utilities.data_structures.concurrent_dict import ConcurrentDict
from melder.utilities.data_structures.concurrent_list import ConcurrentList
from melder.utilities.data_structures.concurrent_set import ConcurrentSet
from melder.utilities.interfaces.interfaces import IConduit
from melder.utilities.general_base.cleanable import Cleanable
from melder.aether.conduit_cloud import ConduitCloud
from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.mutations.mutation_research import MutationResearch
from melder.aether.dev_ops.spell_system_states.spell_system_states import SpellSystemStates
from melder.aether.dev_ops.dev_ops_manager import DevOpsManager


class AethericFrame(Cleanable):
    """
    Manages an isolated "universe" or "frame" within the Aether.

    An AethericFrame holds all top-level conduits, spell registries, dev-ops
    control-plane state, and configuration for a specific, isolated domain.

    High-level responsibilities:
      - Owns root conduits and their spell registries.
      - Owns the version registry for all SpellIndex lineages in this frame.
      - Owns the MutationResearch hub for this frame.
      - Owns SpellSystemStates (graph / dirtiness brain).
      - Owns DevOpsManager (incidents + change-control over this frame).

    This object is thread-safe.
    """

    def __init__(self, name: str) -> None:
        """
        Initialize a new AethericFrame.

        Args:
            name: Human-readable name for this frame. Used for identification
                  and logging; uniqueness is expected but not enforced here.
        """
        super().__init__()

        if not name:
            raise ValueError("name cannot be empty")

        self.name: str = name
        self._id: str = str(ulid.ULID())
        self._lock: threading.RLock = threading.RLock()

        # All root conduits created in this frame:
        #   conduit_id -> IConduit
        self._conduits: ConcurrentDict[str, IConduit] = ConcurrentDict()

        # SpellIndex registry per conduit:
        #   conduit_id -> ConcurrentSet[SpellIndex]
        self._spell_registry: ConcurrentDict[str, ConcurrentSet[SpellIndex]] = ConcurrentDict()

        # SHA256 version registry per conduit:
        #   conduit_id -> ConcurrentSet[str]
        self._version_registry: ConcurrentDict[str, ConcurrentSet[str]] = ConcurrentDict()

        # Conduit clusters (grouping by logical name):
        #   cluster_name -> ConcurrentList[conduit_id]
        self._conduit_clusters: ConcurrentDict[str, ConcurrentList[str]] = ConcurrentDict()

        # Dynamic-mode "cloud" factory for named conduits.
        self._conduit_cloud: ConduitCloud = ConduitCloud(name)

        # Per-frame mutation research hub (local lab entrypoint).
        self._mutation_research: MutationResearch = MutationResearch(self)

        # Per-frame graph + dirtiness registry for all spell lineages.
        self._spell_system_states: SpellSystemStates = SpellSystemStates(self)

        # Per-frame DevOps hub: incidents + change-control over this frame.
        self._dev_ops_manager: DevOpsManager = DevOpsManager(self._spell_system_states)

        # Frozen configuration for this frame (set elsewhere).
        self._configuration = None

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------
    def cleanup(self) -> None:
        """
        Clean up the AethericFrame and all of its owned resources.

        Idempotent and lock-guarded:

        - Calls cleanup() on all root conduits.
        - Cleans and nulls all concurrent registries.
        - Cleans and nulls:
            * MutationResearch
            * SpellSystemStates
            * DevOpsManager
        - Drops configuration and identifiers.

        After cleanup():
        - All public methods should raise via check_cleaned().
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return

            self._cleaned = True
            self._cleanup_data_structures()

            # Configuration + identifiers
            self._configuration = None
            self.name = None
            self._id = None

        # Drop lock last.
        self._lock = None


    def _cleanup_data_structures(self) -> None:
        """
        Clean up all owned data structures.
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
            self._conduits.cleanup()
            self._conduits = None

        # SpellIndex registry
        if self._spell_registry is not None:
            self._spell_registry.cleanup()
            self._spell_registry = None

        # Version registry
        if self._version_registry is not None:
            self._version_registry.cleanup()
            self._version_registry = None

        # Conduit clusters
        if self._conduit_clusters is not None:
            self._conduit_clusters.cleanup()
            self._conduit_clusters = None

        # Dynamic conduit cloud
        if self._conduit_cloud is not None:
            self._conduit_cloud.cleanup()
            self._conduit_cloud = None

        # Mutation research hub
        if self._mutation_research is not None:
            self._mutation_research.cleanup()
            self._mutation_research = None

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
        Enter the AethericFrame context.

        This simply acquires the frame-level lock. It does not change
        ownership semantics; it's a convenience for short critical sections.
        """
        self.check_cleaned()
        self._lock.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        Exit the AethericFrame context and release the frame-level lock.
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
    def mutation_research(self) -> MutationResearch:
        """
        Per-frame mutation research hub.

        This is the "lab" entrypoint that can:
          - create research conduits & spellbooks,
          - stage mutation workspaces,
          - coordinate with DevOpsManager / SpellSystemStates.

        Exact API lives in MutationResearch.
        """
        self.check_cleaned()
        return self._mutation_research

    # ------------------------------------------------------------------
    # Version Registry Maintenance
    # ------------------------------------------------------------------
    def refresh_version_registry(self) -> None:
        """
        Rebuild the version registry from the current SpellIndex registry.

        After this runs:
          - _version_registry[conduit_id] will contain all SHA256 versions
            for every SpellIndex owned by that conduit.

        This is meant to be called after significant changes to bindings,
        e.g. bulk rebinding or promotion waves.
        """
        self.check_cleaned()
        with self._lock:
            if self._spell_registry is None:
                return

            # Start fresh
            self._version_registry = ConcurrentDict()

            for conduit_id, spell_set in self._spell_registry.items():
                version_set: ConcurrentSet[str] = ConcurrentSet()

                for spell_index in spell_set:
                    # SpellIndex.get_all_versions() returns set[str]
                    versions = spell_index.get_all_versions()
                    for version_id in versions:
                        version_set.add(version_id)

                self._version_registry[conduit_id] = version_set

    def has_version(self, version_id: str) -> bool:
        """
        Check if the given SHA256 version_id exists in this frame.

        Uses the prebuilt _version_registry.

        Returns:
            True if any conduit in this frame owns a SpellIndex whose
            versions set contains `version_id`, otherwise False.
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
        Return a flat set of all SHA256 version ids in this frame.

        Uses the prebuilt _version_registry and merges all per-conduit
        version sets into a single set.
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
        Find and return the SpellIndex that contains the given SHA256 version id.

        This scans the SpellIndex registry (_spell_registry) and checks
        SpellIndex.get_all_versions() for membership.

        Args:
            version_id: SHA256 version id to search for.

        Returns:
            The SpellIndex instance that owns `version_id`, or None if no
            SpellIndex within this frame advertises that version.
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
