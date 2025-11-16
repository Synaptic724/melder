import logging
from threading import RLock
from typing import Optional, Any
import ulid

from melder.spellbook.bind.spell_index import SpellIndex
# Melder Imports
from melder.utilities.data_structures.concurrent_dictionary import ConcurrentDict
from melder.utilities.data_structures.concurrent_list import ConcurrentList
from melder.utilities.data_structures.concurrent_set import ConcurrentSet
from melder.utilities.interfaces.interfaces import IConduit, IConduitCloud, IChannelLogger, IConfiguration
from melder.utilities.general_base.cleanable import Cleanable
from melder.aether.aetheric_frame import AethericFrame
from melder.utilities.helpers.init_helpers import InitHelpers

class Aether(Cleanable):
    """
    The global singleton that holds and manages all AethericFrames.

    Aether is the top-level "universe" of the melder system. It is
    responsible for creating and managing isolated frames, holding the
    "default" frame, and acting as the central point of access for
    all conduit-related systems.

    It provides internal-only methods (prefixed with '_') for other
    parts of the melder system to interact with the global state in a
    thread-safe manner.
    """
    _instance = None
    _lock = RLock()
    _initialized = False

    def __new__(cls):
        """Ensures that Aether is a singleton."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(Aether, cls).__new__(cls)
        return cls._instance

    def __init__(self, logger: Any | None = None):
        """Initializes the Aether singleton, creating the 'default' frame."""
        if not Aether._initialized:
            super().__init__()
            Aether._initialized = True

            self._id: str = str(ulid.ULID())
            # --- Safe logger facade (ChannelLogger or std logger) ---
            self._logger = InitHelpers.resolve_safe_logger(logger)
            self._logger.debug("Aether initialized", "__init__")

            # --- Frame setup ---
            self._aetheric_frames: ConcurrentDict[str, AethericFrame] = ConcurrentDict()
            self._aetheric_frames["default"] = AethericFrame("default")
            self._default_frame: AethericFrame = self._aetheric_frames["default"]

    def cleanup(self):
        """
        Cleans up the entire Aether, recursively cleaning all frames and conduits.

        Clears all registries and renders the Aether unusable.
        This operation is idempotent.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            try:
                self._cleaned = True
                self._logger.debug("Cleaning up Aether...", "cleanup")
                self.cleanup_aetheric_frames() # This will clean each individual frame
                self._default_frame = None
                self._aetheric_frames.cleanup() # This cleans the ConcurrentDictionary
                self._aetheric_frames = None
                self._logger.debug("Aether cleanup successful", "cleanup")
            except Exception as e:
                self._logger.error(f"Error cleaning up Aether: {e}", "cleanup", exc_info=True)
                raise

        if self._logger is not None:
            if hasattr(self._logger, 'cleanup'):
                self._logger.cleanup()
            self._logger = None

    def cleanup_aetheric_frames(self):
        """
        Signs all aetheric frames and their contents.
        """
        self._logger.debug("Cleaning all aetheric frames...", "cleanup_aetheric_frames")

        for frame_name, frame in self._aetheric_frames.items():
            try:
                self._logger.debug(f"Cleaning frame '{frame_name}'", "cleanup_aetheric_frames")
                frame.cleanup()
            except Exception as e:
                # Tolerant behavior: log and continue
                self._logger.error(f"Error cleaning frame '{frame_name}': {e}", "cleanup_aetheric_frames", exc_info=True)

    # region Configuration

    @property
    def logger(self) -> IChannelLogger | logging.Logger | None:
        """
        Gets the raw logger instance (IChannelLogger, Logger, or Handler)
        that is currently wrapped by the internal SafeLogger.

        Returns:
            The raw logger object, or None if no logger is set.
        """
        return self._logger._logger # Accesses the raw logger inside SafeLogger

    @logger.setter
    def logger(self, value: IChannelLogger | logging.Logger | None):
        """
        Sets or updates the logger for the Aether singleton.

        The provided logger (or Handler) will be wrapped by the
        internal SafeLogger for unified logging calls.

        Args:
            value: The IChannelLogger, Logger, Handler, or None to use.
        """
        self._logger = InitHelpers.resolve_safe_logger(value)


    def _bind_configuration(self, configuration, aetheric_frame_name: str = "default") -> None:
        """
        Binds a configuration object to a specific Aetheric Frame.

        Args:
            configuration: The configuration object to bind.
            aetheric_frame_name: The name of the frame.

        Raises:
            ValueError: If the specified frame does not exist.
        """
        self._logger.debug(f"Binding configuration to frame '{aetheric_frame_name}'", "_bind_configuration")

        with self._lock:
            if aetheric_frame_name != "default":
                try:
                    self._aetheric_frames[aetheric_frame_name]._configuration = configuration
                except KeyError:
                    self._logger.error(f"Aetheric frame '{aetheric_frame_name}' does not exist.", "_bind_configuration", exc_info=True)
                    raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
            else:
                self._default_frame._configuration = configuration

        self._logger.debug(f"Configuration bound to frame '{aetheric_frame_name}'", "_bind_configuration")

    def _get_configuration(self, aetheric_frame_name: str = "default") -> Optional[IConfiguration]:
        """
        Retrieves the configuration object from a specific Aetheric Frame.

        Args:
            aetheric_frame_name: The name of the frame.

        Returns:
            The configuration object, or None if not set.

        Raises:
            ValueError: If the specified frame does not exist.
        """
        if aetheric_frame_name != "default":
            try:
                cfg = self._aetheric_frames[aetheric_frame_name]._configuration
            except KeyError:
                self._logger.error(f"Aetheric frame '{aetheric_frame_name}' does not exist.", "_get_configuration", exc_info=True)
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            cfg = self._default_frame._configuration

        self._logger.debug(f"Retrieved configuration from frame '{aetheric_frame_name}'", "_get_configuration")
        return cfg

    # endregion Configuration
    # region Conduit Management

    def _register_conduit_cloud(self, conduit: IConduit, aetheric_frame_name: str = "default"):
        """
        Registers a conduit with the ConduitCloud of a specific frame.

        Args:
            conduit: The conduit to register.
            aetheric_frame_name: The name of the frame.

        Raises:
            ValueError: If the specified frame does not exist.
        """
        self._logger.debug(f"Registering conduit with cloud in frame '{aetheric_frame_name}'", "_register_conduit_cloud")

        if aetheric_frame_name != "default":
            try:
                conduit_cloud = self._aetheric_frames[aetheric_frame_name]._conduit_cloud
            except KeyError:
                self._logger.error(f"Aetheric frame '{aetheric_frame_name}' does not exist.", "_register_conduit_cloud", exc_info=True)
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            conduit_cloud = self._default_frame._conduit_cloud

        conduit_cloud._register_conduit(conduit)
        self._logger.debug(f"Conduit registered with cloud in frame '{aetheric_frame_name}'", "_register_conduit_cloud")

    def _get_conduit_cloud(self, aetheric_frame_name: str = "default") -> IConduitCloud:
        """
        Retrieves the ConduitCloud instance from a specific frame.

        Args:
            aetheric_frame_name: The name of the frame.

        Returns:
            ConduitCloud: The ConduitCloud for that frame.

        Raises:
            ValueError: If the specified frame does not exist.
        """
        if aetheric_frame_name != "default":
            try:
                cloud = self._aetheric_frames[aetheric_frame_name]._conduit_cloud
            except KeyError:
                self._logger.error(f"Aetheric frame '{aetheric_frame_name}' does not exist.", "_get_conduit_cloud", exc_info=True)
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            cloud = self._default_frame._conduit_cloud

        self._logger.debug(f"Retrieved conduit cloud for frame '{aetheric_frame_name}'", "_get_conduit_cloud")
        return cloud

    def _get_conduit_by_name(self, name: str, aetheric_frame_name: str = "default") -> IConduit:
        """
        Finds a root conduit within a frame by its name.

        Args:
            name (str): The name of the conduit.
            aetheric_frame_name (str): The name of the frame to search in.

        Returns:
            IConduit: The found conduit.

        Raises:
            ValueError: If the frame does not exist or the conduit is not found.
        """
        if aetheric_frame_name != "default":
            try:
                conduits = self._aetheric_frames[aetheric_frame_name]._conduits
            except KeyError:
                self._logger.error(f"Aetheric frame '{aetheric_frame_name}' does not exist.", "_get_conduit_by_name", exc_info=True)
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            conduits = self._default_frame._conduits

        for conduit in conduits.values():
            if conduit.name == name:
                self._logger.debug(f"Found conduit by name '{name}' in frame '{aetheric_frame_name}'", "_get_conduit_by_name")
                return conduit

        self._logger.error(f"Conduit with name {name} not found.", "_get_conduit_by_name", exc_info=True)
        raise ValueError(f"Conduit with name {name} not found.")

    def _get_conduit_by_id(self, signature: str, aetheric_frame_name: str = "default") -> IConduit:
        """
        Finds a root conduit within a frame by its id.

        Args:
            signature (str): The id of the conduit.
            aetheric_frame_name (str): The name of the frame to search in.

        Returns:
            IConduit: The found conduit.

        Raises:
            ValueError: If the frame does not exist or the conduit is not found.
        """
        if aetheric_frame_name != "default":
            try:
                conduits = self._aetheric_frames[aetheric_frame_name]._conduits
            except KeyError:
                self._logger.error(f"Aetheric frame '{aetheric_frame_name}' does not exist.", "_get_conduit_by_id", exc_info=True)
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            conduits = self._default_frame._conduits

        if signature in conduits:
            self._logger.debug(f"Found conduit by id '{signature}' in frame '{aetheric_frame_name}'", "_get_conduit_by_id")
            return conduits[signature]

        self._logger.error(f"Conduit with signature {signature} not found.", "_get_conduit_by_id", exc_info=True)
        raise ValueError(f"Conduit with signature {signature} not found.")

    def _add_conduit(self, conduit: IConduit, aetheric_frame_name: str = "default"):
        """
        Adds a new root conduit to a frame. (Internal use)

        Args:
            conduit (IConduit): The conduit to add.
            aetheric_frame_name (str): The name of the frame.

        Raises:
            ValueError: If the frame does not exist or the conduit ID already exists.
        """
        self._logger.debug(f"Adding conduit to frame '{aetheric_frame_name}'", "_add_conduit")

        if aetheric_frame_name != "default":
            try:
                conduits = self._aetheric_frames[aetheric_frame_name]._conduits
            except KeyError:
                self._logger.error(f"Aetheric frame '{aetheric_frame_name}' does not exist.", "_add_conduit", exc_info=True)
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            conduits = self._default_frame._conduits

        cid = conduit._id
        if cid in conduits:
            self._logger.error(f"Conduit with ID {cid} already exists.", "_add_conduit", exc_info=True)
            raise ValueError(f"Conduit with ID {cid} already exists.")

        conduits[cid] = conduit
        self._logger.debug(f"Conduit '{cid}' added to frame '{aetheric_frame_name}'", "_add_conduit")

    def _remove_conduit(self, conduit: IConduit, aetheric_frame_name: str = "default"):
        """
        Removes a root conduit from a frame. (Internal use)

        Args:
            conduit (IConduit): The conduit to remove.
            aetheric_frame_name (str): The name of the frame.

        Raises:
            ValueError: If the frame does not exist or the conduit is not found.
        """
        self._logger.debug(f"Removing conduit from frame '{aetheric_frame_name}'", "_remove_conduit")

        if aetheric_frame_name != "default":
            try:
                conduits = self._aetheric_frames[aetheric_frame_name]._conduits
            except KeyError:
                self._logger.error(f"Aetheric frame '{aetheric_frame_name}' does not exist.", "_remove_conduit", exc_info=True)
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            conduits = self._default_frame._conduits

        conduit_id = conduit._id
        removed = conduits.pop(conduit_id, None)
        if removed is None:
            self._logger.error(f"Conduit with ID {conduit_id} does not exist.", "_remove_conduit", exc_info=True)
            raise ValueError(f"Conduit with ID {conduit_id} does not exist.")

        self._logger.debug(f"Conduit '{conduit_id}' removed from frame '{aetheric_frame_name}'", "_remove_conduit")

    def _create_cluster(self, cluster_name: str, aetheric_frame_name: str = "default"):
        """
        Creates a new conduit cluster within a frame. (Internal use)

        Args:
            cluster_name (str): The name for the new cluster.
            aetheric_frame_name (str): The name of the frame.

        Raises:
            ValueError: If the frame does not exist or the cluster name is taken.
        """
        self._logger.debug(f"Creating cluster '{cluster_name}' in frame '{aetheric_frame_name}'", "_create_cluster")

        if aetheric_frame_name != "default":
            try:
                conduit_clusters = self._aetheric_frames[aetheric_frame_name]._conduit_clusters
            except KeyError:
                self._logger.error(f"Aetheric frame '{aetheric_frame_name}' does not exist.", "_create_cluster", exc_info=True)
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            conduit_clusters = self._default_frame._conduit_clusters

        if cluster_name in conduit_clusters:
            self._logger.error(f"Cluster with name {cluster_name} already exists.", "_create_cluster", exc_info=True)
            raise ValueError(f"Cluster with name {cluster_name} already exists.")

        conduit_clusters[cluster_name] = ConcurrentList()
        self._logger.debug(f"Cluster '{cluster_name}' created in frame '{aetheric_frame_name}'", "_create_cluster")

    def _add_conduit_to_cluster(self, conduit: IConduit, cluster_name: str, aetheric_frame_name: str = "default"):
        """
        Adds a conduit's id to a cluster. (Internal use)

        Args:
            conduit (IConduit): The conduit to add.
            cluster_name (str): The name of the cluster.
            aetheric_frame_name (str): The name of the frame.

        Raises:
            ValueError: If the frame or cluster does not exist.
        """
        self._logger.debug(f"Adding conduit to cluster '{cluster_name}' in frame '{aetheric_frame_name}'", "_add_conduit_to_cluster")

        if aetheric_frame_name != "default":
            try:
                conduit_clusters = self._aetheric_frames[aetheric_frame_name]._conduit_clusters
            except KeyError:
                self._logger.error(f"Aetheric frame '{aetheric_frame_name}' does not exist.", "_add_conduit_to_cluster", exc_info=True)
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            conduit_clusters = self._default_frame._conduit_clusters

        if cluster_name not in conduit_clusters:
            self._logger.error(f"Cluster with name {cluster_name} does not exist.", "_add_conduit_to_cluster", exc_info=True)
            raise ValueError(f"Cluster with name {cluster_name} does not exist.")

        conduit_id = conduit._id
        conduit_clusters[cluster_name].append(conduit_id)
        self._logger.debug(f"Conduit '{conduit_id}' added to cluster '{cluster_name}'", "_add_conduit_to_cluster")

    def _remove_conduit_from_cluster(self, conduit: IConduit, cluster_name: str, aetheric_frame_name: str = "default"):
        """
        Removes a conduit's id from a cluster. (Internal use)

        Args:
            conduit (IConduit): The conduit to remove.
            cluster_name (str): The name of the cluster.
            aetheric_frame_name (str): The name of the frame.

        Raises:
            ValueError: If the frame or cluster does not exist.
        """
        self._logger.debug(f"Removing conduit from cluster '{cluster_name}' in frame '{aetheric_frame_name}'", "_remove_conduit_from_cluster")

        if aetheric_frame_name != "default":
            try:
                conduit_clusters = self._aetheric_frames[aetheric_frame_name]._conduit_clusters
            except KeyError:
                self._logger.error(f"Aetheric frame '{aetheric_frame_name}' does not exist.", "_remove_conduit_from_cluster", exc_info=True)
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            conduit_clusters = self._default_frame._conduit_clusters

        if cluster_name not in conduit_clusters:
            self._logger.error(f"Cluster with name {cluster_name} does not exist.", "_remove_conduit_from_cluster", exc_info=True)
            raise ValueError(f"Cluster with name {cluster_name} does not exist.")

        conduit_id = conduit._id
        try:
            conduit_clusters[cluster_name].remove(conduit_id)
        except Exception as e:
            self._logger.error(f"Error removing conduit '{conduit_id}' from cluster '{cluster_name}': {e}", "_remove_conduit_from_cluster", exc_info=True)
            raise

        self._logger.debug(f"Conduit '{conduit_id}' removed from cluster '{cluster_name}'", "_remove_conduit_from_cluster")

    def _get_conduits_in_cluster(self, cluster_name: str, aetheric_frame_name: str = "default") -> ConcurrentList[str]:
        """
        Gets a list of all conduit ids in a specific cluster.

        Args:
            cluster_name (str): The name of the cluster.
            aetheric_frame_name (str): The name of the frame.

        Returns:
            ConcurrentList[str]: A list of conduit ids.

        Raises:
            ValueError: If the frame or cluster does not exist.
        """
        if aetheric_frame_name != "default":
            try:
                conduit_clusters = self._aetheric_frames[aetheric_frame_name]._conduit_clusters
            except KeyError:
                self._logger.error(f"Aetheric frame '{aetheric_frame_name}' does not exist.", "_get_conduits_in_cluster", exc_info=True)
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            conduit_clusters = self._default_frame._conduit_clusters

        if cluster_name not in conduit_clusters:
            self._logger.error(f"Cluster with name {cluster_name} does not exist.", "_get_conduits_in_cluster", exc_info=True)
            raise ValueError(f"Cluster with name {cluster_name} does not exist.")

        self._logger.debug(f"Retrieved conduits for cluster '{cluster_name}' in frame '{aetheric_frame_name}'", "_get_conduits_in_cluster")
        return conduit_clusters[cluster_name]

    def _get_conduit_by_spell_id(self, spell_id: str, aetheric_frame_name: str = "default") -> IConduit:
        """
        Finds the conduit that owns a specific spell ID within a frame.

        Args:
            spell_id (str): The spell ID (SHA256 hash) to search for.
            aetheric_frame_name (str): The name of the frame.

        Returns:
            IConduit: The conduit that owns the spell.

        Raises:
            ValueError: If the frame does not exist or the spell ID is not found.
        """
        # Select frame
        if aetheric_frame_name != "default":
            try:
                spell_registry = self._aetheric_frames[aetheric_frame_name]._spell_registry
            except KeyError:
                self._logger.error(
                    f"Aetheric frame '{aetheric_frame_name}' does not exist.",
                    "_get_conduit_by_spell_id",
                    exc_info=True
                )
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            spell_registry = self._default_frame._spell_registry

        # Search each SpellIndex for the SHA256 version
        for conduit_id, spell_set in spell_registry.items():
            for spell_index in spell_set:
                if spell_index.has_version(spell_id):
                    self._logger.debug(
                        f"Found conduit '{conduit_id}' owning version '{spell_id}' "
                        f"under SpellIndex '{spell_index.id}'",
                        "_get_conduit_by_spell_id"
                    )
                    return self._get_conduit_by_id(conduit_id, aetheric_frame_name)

        self._logger.error(
            f"Spell version {spell_id} not found in any conduit.",
            "_get_conduit_by_spell_id", exc_info=True
        )
        raise ValueError(f"Spell version {spell_id} not found in any conduit.")

    # endregion Conduit Management

    # region Spell Management

    def _check_for_spell(self, spell_id: str, aetheric_frame_name: str = "default") -> bool:
        """
        Checks if a SHA256 spell_id exists in ANY SpellIndex within a frame,
        using the frame's _version_registry cache.

        NOTE:
            Call `_refresh_version_registry(...)` after mutation/research
            changes so this remains accurate.

        Args:
            spell_id (str): The SHA256 spell ID to check.
            aetheric_frame_name (str): The name of the frame.

        Returns:
            bool: True if the spell ID exists in the frame, False otherwise.
        """
        # Pick frame
        if aetheric_frame_name != "default":
            try:
                frame = self._aetheric_frames[aetheric_frame_name]
            except KeyError:
                self._logger.error(
                    f"Aetheric frame '{aetheric_frame_name}' does not exist.",
                    "_check_for_spell",
                    exc_info=True
                )
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            frame = self._default_frame

        # Fast O(1-ish) lookup via cached version_registry
        found = frame.has_version(spell_id)

        self._logger.debug(
            f"Check for spell version '{spell_id}' in frame '{aetheric_frame_name}': {found}",
            "_check_for_spell"
        )
        return found


    def _add_spells_to_aether(self, conduit_id: str, spell_set: ConcurrentSet[SpellIndex],
                              aetheric_frame_name: str = "default") -> None:
        """
        Registers a set of SpellIndex objects for a conduit and refreshes version registry.

        Args:
            conduit_id (str): The id of the owning conduit.
            spell_set (ConcurrentSet[SpellIndex]): The set of SpellIndex objects to register.
            aetheric_frame_name (str): The name of the frame.
        """

        # Validate spell_set contents
        for item in spell_set:
            if not isinstance(item, SpellIndex):
                raise TypeError("spell_set must contain only SpellIndex instances")

        # Pick frame
        if aetheric_frame_name != "default":
            try:
                frame = self._aetheric_frames[aetheric_frame_name]
            except KeyError:
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            frame = self._default_frame

        spell_registry = frame._spell_registry

        # Prevent duplicate conduit registration
        if conduit_id in spell_registry:
            raise ValueError(f"Spell registry already contains Conduit ID {conduit_id}.")

        # Add spell set
        spell_registry[conduit_id] = spell_set

        # Critical: update SHA256 version registry
        frame.refresh_version_registry()


    def _register_single_spell_index(self, conduit_id: str, spell_index: SpellIndex,
                                     aetheric_frame_name: str = "default") -> None:
        """
        Registers a single SpellIndex under a conduit and refreshes version registry.

        Args:
            conduit_id (str): The id of the owning conduit.
            spell_index (SpellIndex): The SpellIndex to register.
            aetheric_frame_name (str): The name of the frame.

        Raises:
            ValueError: If the specified frame does not exist.
        """

        # Pick frame registry
        if aetheric_frame_name != "default":
            try:
                frame = self._aetheric_frames[aetheric_frame_name]
            except KeyError:
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            frame = self._default_frame

        spell_registry = frame._spell_registry

        # Ensure there is a spell set for this conduit
        if conduit_id not in spell_registry:
            spell_registry[conduit_id] = ConcurrentSet()

        # Add SpellIndex
        spell_registry[conduit_id].add(spell_index)

        # 🔥 Critical: keep version registry in sync
        frame.refresh_version_registry()

    def _remove_single_spell_index(self, conduit_id: str, spell_index: SpellIndex,
                                   aetheric_frame_name: str = "default"):
        """
        Removes a SpellIndex and refreshes version registry so SHA256 ancestry collapses correctly.

        Args:
            conduit_id (str): The id of the owning conduit.
            spell_index (SpellIndex): The SpellIndex to remove.
            aetheric_frame_name (str): The name of the frame.

        Raises:
            ValueError: If the specified frame does not exist.
        """

        # Pick frame
        if aetheric_frame_name != "default":
            try:
                frame = self._aetheric_frames[aetheric_frame_name]
            except KeyError:
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            frame = self._default_frame

        spell_registry = frame._spell_registry

        # Nothing to remove
        if conduit_id not in spell_registry:
            return

        # Remove SpellIndex safely
        try:
            spell_registry[conduit_id].remove(spell_index)
        except KeyError:
            pass

        # Critical: remove stale versions from registry
        frame.refresh_version_registry()


    def _refresh_version_registry(self, aetheric_frame_name: str = "default") -> None:
        """
        Rebuilds the version registry for the given frame from its SpellIndexes.

        Call this manually after research/mutation updates so that SHA256-based
        lookups stay accurate and O(1) over the cached sets.
        """
        if aetheric_frame_name != "default":
            try:
                frame = self._aetheric_frames[aetheric_frame_name]
            except KeyError:
                self._logger.error(
                    f"Aetheric frame '{aetheric_frame_name}' does not exist.",
                    "_refresh_version_registry",
                    exc_info=True
                )
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            frame = self._default_frame

        frame.refresh_version_registry()
        self._logger.debug(
            f"Refreshed version registry for frame '{aetheric_frame_name}'",
            "_refresh_version_registry"
        )

    def _get_all_spell_versions(self, aetheric_frame_name: str = "default") -> set[str]:
        """
        Returns a flat set of all SHA256 versions for a given frame,
        using the frame's _version_registry.

        Call `_refresh_version_registry` first if you need the latest state.
        """
        if aetheric_frame_name != "default":
            try:
                frame = self._aetheric_frames[aetheric_frame_name]
            except KeyError:
                self._logger.error(
                    f"Aetheric frame '{aetheric_frame_name}' does not exist.",
                    "_get_all_spell_versions",
                    exc_info=True
                )
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            frame = self._default_frame

        versions = frame.get_all_versions()
        self._logger.debug(
            f"Collected {len(versions)} spell versions from frame '{aetheric_frame_name}'",
            "_get_all_spell_versions"
        )
        return versions

    # endregion Spell Management