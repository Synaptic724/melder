import logging
from threading import RLock
from typing import Optional, Any, Dict, List, Set
import ulid
# Melder Imports
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.nexus.nexus import Nexus
from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.existence.existence import Existence
from melder.aether.conduit.conduit_cluster import ConduitCluster
from melder.utilities.interfaces.interfaces import IConduit, IConduitCloud, IChannelLogger, IConfiguration, \
    IDevOpsManager, ISpellSystemStates, IIncidentManager, IChangeControlManager, IAether, INexus
from melder.utilities.general_base.cleanable import Cleanable
from melder.aether.aetheric_frame import AethericFrame
from melder.aether.aetheric_frame_configuration import AethericFrameConfiguration
from melder.utilities.helpers.init_helpers import InitHelpers
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class Aether(Cleanable, IAether):
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
    __melder_internal__ = _mrg.sentinel
    _instance = None
    _lock = RLock()
    _initialized = False

    def __new__(cls, *args, **kwargs):
        """Ensures that Aether is a singleton."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(Aether, cls).__new__(cls)
        return cls._instance

    def __init__(self, logger: Optional[Any] = None):
        """
        Initialize the Aether singleton and its always-on frame substrate.

        Purpose:
            Create the root `Aether` host, bootstrap the default
            `AethericFrame`, and prepare optional hosted subsystems such as the
            private `Nexus` singleton.

        Contract:
            - Initializes the default frame eagerly.
            - Initializes the hosted Nexus singleton eagerly as an object, but
              leaves it unconfigured and disabled until a user explicitly
              engages it.
            - Does not preinstall a Nexus configuration during normal boot.

        Args:
            logger:
                Optional logger instance or logger-like object used to seed the
                SafeLogger facade.

        Returns:
            None.
        """
        if not Aether._initialized:
            super().__init__()
            # Initialize potentially nullable fields early for safe cleanup
            self._aetheric_frames = None
            self._default_frame = None
            self._nexus = None
            self._aether_utility_system = None
            self._logger = InitHelpers.resolve_safe_logger(None)

            Aether._initialized = True

            self._id: str = str(ulid.ULID())
            self._aether_utility_system: AetherUtilitySystem = AetherUtilitySystem()
            try:
                if logger is None:
                    self._logger = InitHelpers.resolve_channel_logger(
                        self,
                        groups=["aether", "lifecycle"],
                        system_groups=["aether"],
                        props={"component": "aether"},
                        channels="system",
                    )
                else:
                    self._logger = InitHelpers.resolve_safe_logger(logger)
            except Exception as e:
                self._logger = InitHelpers.resolve_safe_logger(None)
                self._logger.error(
                    f"Failed to initialize Aether logger: {e}",
                    "__init__",
                    exc_info=True,
                )
            # --- Frame setup ---
            self._aetheric_frames: Dict[str, AethericFrame] = {"default": AethericFrame(self, "default")}
            self._default_frame: AethericFrame = self._aetheric_frames["default"]
            self._nexus: INexus = Nexus(aether=self)

    def cleanup(self):
        """
        Cleanup the entire Aether, recursively cleaning all frames and hosted
        subsystems.

        Purpose:
            Tear down the global runtime root and all owned frame or subsystem
            state so the singleton can be safely reinitialized.

        Contract:
            - Idempotent.
            - Cleans frames before resetting singleton state.
            - Cleans the hosted Nexus singleton if it exists.
            - Drops any pending or installed Nexus configuration reference.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            try:
                self._cleaned = True
                if self._aetheric_frames is not None:
                    self.cleanup_aetheric_frames() # This will clean each individual frame
                    self._aetheric_frames.clear() # This cleans the ConcurrentDictionary
                    self._aetheric_frames = None

                if self._nexus is not None:
                    self._nexus.cleanup()
                    self._nexus = None
                if self._aether_utility_system is not None:
                    self._aether_utility_system.cleanup()
                    self._aether_utility_system = None
                self._default_frame = None
                
                # Reset Singleton state to allow re-initialization (e.g. in tests)
                Aether._instance = None
                Aether._initialized = False
            except Exception as e:
                self._logger.error(f"Error cleaning up Aether: {e}", "cleanup", exc_info=True)
                raise

        if self._logger is not None:
            if hasattr(self._logger, 'cleanup'):
                self._logger.cleanup()
            self._logger = None

    @classmethod
    def _reset_singleton_for_tests(cls) -> None:
        """
        Reset the Aether singleton for test isolation.

        Purpose:
            Provide a deterministic way for tests to discard any existing
            singleton instance and force re-initialization on next use.

        Contract:
            - If an instance exists, cleanup() is invoked to release resources.
            - _instance and _initialized are cleared so Aether() creates a fresh instance.
            - This method does not create a new instance.

        Returns:
            None.

        Raises:
            Exception: Propagates any exception raised by cleanup().

        Threading:
            Acquires the class-level lock to serialize singleton resets.

        Lifecycle:
            Triggers normal cleanup semantics on the current instance, including
            frame cleanup and logger teardown.
        """
        with cls._lock:
            instance = cls._instance
            if instance is None:
                cls._initialized = False
                return
            try:
                instance.cleanup()
            finally:
                cls._instance = None
                cls._initialized = False

    def _ensure_default_frame(self) -> None:
        """
        Raise a clear error if the default frame is unavailable.
        """
        if self._default_frame is None:
            raise RuntimeError("Default AethericFrame has been cleaned or is unavailable.")

    def _detach_cleaned_frame(
            self,
            frame_name: str,
            frame: AethericFrame,
    ) -> None:
        """
        Internal

        Remove one already-cleaned frame from the Aether registry.

        Contract:
            - Used by `AethericFrame.cleanup()` after frame-owned teardown has
              already completed.
            - Removes the frame from the Aether registry only when the
              registered object matches the cleaned frame instance.
            - Clears the default-frame pointer when the removed frame was the
              default.
            - Drops any matching Nexus frame record before the registry entry is
              removed.

        Args:
            frame_name:
                Name of the cleaned frame.
            frame:
                Cleaned frame instance requesting detachment.

        Returns:
            None.
        """
        if not frame_name:
            return

        with self._lock:
            if self._aetheric_frames is None:
                return

            registered_frame = self._aetheric_frames.get(frame_name)
            if registered_frame is None or registered_frame is not frame:
                return

            if self._nexus is not None:
                try:
                    self._nexus.check_for_aetheric_frame(frame_name)
                except Exception as e:
                    self._logger.error(
                        f"Error detaching Nexus frame record for '{frame_name}': {e}",
                        "_detach_cleaned_frame",
                        exc_info=True,
                    )

            self._aetheric_frames.pop(frame_name, None)
            if self._default_frame is frame:
                self._default_frame = None

            self._logger.info(
                f"Frame '{frame_name}' removed from Aether "
                f"(default_cleared={self._default_frame is None})",
                "_detach_cleaned_frame",
            )

    def cleanup_aetheric_frames(self):
        """
        Signs all aetheric frames and their contents.
        """
        if self._aetheric_frames is None:
            return
        for frame_name, frame in list(self._aetheric_frames.items()):
            try:
                frame.cleanup()
            except Exception as e:
                self._logger.error(
                    f"Error cleaning frame '{frame_name}': {e}",
                    "cleanup_aetheric_frames",
                    exc_info=True,
                )

    # region Configuration

    #region Context Manager
    def __enter__(self):
        """Enters the context manager for Aether."""
        self._lock.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exits the context manager for Aether."""
        self._lock.release()

    #endregion Context Manager

    #region Rift Hosting

    #endregion Rift Hosting


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

    def _ensure_frame(self, aetheric_frame_name: str = "default") -> AethericFrame:
        """
        Internal

        Ensure an AethericFrame exists for the given name, creating it if missing.

        Purpose:
            Provide a single, thread-safe creation path for named frames so
            Spellbooks can initialize against a new frame without raising.

        Contract:
            - Returns the existing frame when it already exists.
            - Creates and registers a new frame when absent.
            - Does not mutate the default frame pointer unless the name is "default".

        Args:
            aetheric_frame_name: The frame name to ensure exists.

        Returns:
            AethericFrame: The existing or newly created frame.

        Raises:
            RuntimeError: If the Aether is cleaned or its frame registry is unavailable.
            ValueError: If the frame name is invalid for frame construction.

        Threading:
            Acquires the Aether lock to serialize frame creation.

        Lifecycle:
            The created frame is owned by Aether and will be cleaned by Aether.cleanup().
        """
        self.check_cleaned()
        if not isinstance(aetheric_frame_name, str):
            raise TypeError("aetheric_frame_name must be a string.")

        if self._aetheric_frames is None:
            raise RuntimeError("Aether frame registry is unavailable.")

        with self._lock:
            if self._aetheric_frames is None:
                raise RuntimeError("Aether frame registry is unavailable.")

            frame = self._aetheric_frames.get(aetheric_frame_name)
            if frame is not None:
                return frame

            frame = AethericFrame(self, aetheric_frame_name)
            self._aetheric_frames[aetheric_frame_name] = frame
            if aetheric_frame_name == "default":
                self._default_frame = frame

            return frame


    def _bind_configuration(self, configuration, aetheric_frame_name: str = "default") -> None:
        """
        Binds a configuration object to a specific Aetheric Frame.

        Args:
            configuration: The configuration object to bind.
            aetheric_frame_name: The name of the frame.

        Raises:
            ValueError: If the specified frame does not exist.
        """
        self.check_cleaned()

        with self._lock:
            if aetheric_frame_name != "default":
                try:
                    self._aetheric_frames[aetheric_frame_name]._configuration = configuration
                except KeyError:
                    self._logger.error(f"Aetheric frame '{aetheric_frame_name}' does not exist.", "_bind_configuration", exc_info=True)
                    raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
            else:
                self._ensure_default_frame()
                self._default_frame._configuration = configuration


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
        self.check_cleaned()
        if aetheric_frame_name != "default":
            try:
                cfg = self._aetheric_frames[aetheric_frame_name]._configuration
            except KeyError:
                self._logger.error(f"Aetheric frame '{aetheric_frame_name}' does not exist.", "_get_configuration", exc_info=True)
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            self._ensure_default_frame()
            cfg = self._default_frame._configuration

        return cfg

    def _bind_aetheric_frame_configuration(
            self,
            frame_configuration: AethericFrameConfiguration,
            aetheric_frame_name: str = "default",
    ) -> None:
        """
        Bind one narrow frame-level AR posture object to a specific frame.

        Purpose:
            Preserve one canonical AR posture for a frame without replacing the
            richer shared Spellbook configuration object.

        Contract:
            - First writer wins for a given frame.
            - Later identical posture attempts are treated as idempotent.
            - Later conflicting posture attempts are ignored and logged.

        Args:
            frame_configuration:
                Narrow frame-level posture object to bind.
            aetheric_frame_name:
                Target frame name.

        Returns:
            None.

        Raises:
            TypeError: If `frame_configuration` is not an
                `AethericFrameConfiguration`.
            ValueError: If the specified frame does not exist.
        """
        self.check_cleaned()
        if not isinstance(frame_configuration, AethericFrameConfiguration):
            raise TypeError(
                "frame_configuration must be an AethericFrameConfiguration."
            )

        with self._lock:
            if aetheric_frame_name != "default":
                try:
                    frame = self._aetheric_frames[aetheric_frame_name]
                except KeyError:
                    self._logger.error(
                        f"Aetheric frame '{aetheric_frame_name}' does not exist.",
                        "_bind_aetheric_frame_configuration",
                        exc_info=True,
                    )
                    raise ValueError(
                        f"Aetheric frame '{aetheric_frame_name}' does not exist."
                    )
            else:
                self._ensure_default_frame()
                frame = self._default_frame

            existing_frame_configuration = frame.frame_configuration
            if existing_frame_configuration is None:
                frame._frame_configuration = frame_configuration
                return

            if existing_frame_configuration.matches_posture(frame_configuration):
                if existing_frame_configuration is not frame_configuration:
                    frame_configuration.cleanup()
                return

            self._logger.warning(
                "Ignored conflicting AethericFrameConfiguration for frame "
                "'{0}'. Existing={1}, attempted={2}.".format(
                    aetheric_frame_name,
                    existing_frame_configuration.describe_posture(),
                    frame_configuration.describe_posture(),
                ),
                "_bind_aetheric_frame_configuration",
            )
            frame_configuration.cleanup()

    def _get_aetheric_frame_configuration(
            self,
            aetheric_frame_name: str = "default",
    ) -> Optional[AethericFrameConfiguration]:
        """
        Return the narrow frame-level AR posture object for one frame.

        Args:
            aetheric_frame_name:
                Target frame name.

        Returns:
            Optional[AethericFrameConfiguration]: Bound frame posture or None.

        Raises:
            ValueError: If the specified frame does not exist.
        """
        self.check_cleaned()
        if aetheric_frame_name != "default":
            try:
                frame = self._aetheric_frames[aetheric_frame_name]
            except KeyError:
                self._logger.error(
                    f"Aetheric frame '{aetheric_frame_name}' does not exist.",
                    "_get_aetheric_frame_configuration",
                    exc_info=True,
                )
                raise ValueError(
                    f"Aetheric frame '{aetheric_frame_name}' does not exist."
                )
        else:
            self._ensure_default_frame()
            frame = self._default_frame

        return frame.frame_configuration

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
        self.check_cleaned()

        if aetheric_frame_name != "default":
            try:
                conduit_cloud = self._aetheric_frames[aetheric_frame_name]._conduit_cloud
            except KeyError:
                self._logger.error(f"Aetheric frame '{aetheric_frame_name}' does not exist.", "_register_conduit_cloud", exc_info=True)
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            self._ensure_default_frame()
            conduit_cloud = self._default_frame._conduit_cloud

        conduit_cloud._register_conduit(conduit)

    def _unregister_conduit_cloud(self, conduit: IConduit, aetheric_frame_name: str = "default"):
        """
        Unregisters a conduit from the ConduitCloud of a specific frame.

        Args:
            conduit: The conduit to unregister.
            aetheric_frame_name: The name of the frame.

        Raises:
            ValueError: If the specified frame does not exist.
        """
        self.check_cleaned()

        if aetheric_frame_name != "default":
            try:
                conduit_cloud = self._aetheric_frames[aetheric_frame_name]._conduit_cloud
            except KeyError:
                self._logger.error(f"Aetheric frame '{aetheric_frame_name}' does not exist.", "_unregister_conduit_cloud", exc_info=True)
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            self._ensure_default_frame()
            conduit_cloud = self._default_frame._conduit_cloud

        conduit_cloud._unregister_conduit(conduit)
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
        self.check_cleaned()
        if aetheric_frame_name != "default":
            try:
                cloud = self._aetheric_frames[aetheric_frame_name]._conduit_cloud
            except KeyError:
                self._logger.error(f"Aetheric frame '{aetheric_frame_name}' does not exist.", "_get_conduit_cloud", exc_info=True)
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            self._ensure_default_frame()
            cloud = self._default_frame._conduit_cloud

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
        self.check_cleaned()
        if aetheric_frame_name != "default":
            try:
                frame = self._aetheric_frames[aetheric_frame_name]
            except KeyError:
                self._logger.error(f"Aetheric frame '{aetheric_frame_name}' does not exist.", "_get_conduit_by_name", exc_info=True)
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            self._ensure_default_frame()
            frame = self._default_frame

        conduit_id = frame._conduit_ids_by_name.get(name)
        if conduit_id is not None:
            conduit = frame._conduits.get(conduit_id)
            if conduit is not None:
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
        self.check_cleaned()
        if aetheric_frame_name != "default":
            try:
                conduits = self._aetheric_frames[aetheric_frame_name]._conduits
            except KeyError:
                self._logger.error(f"Aetheric frame '{aetheric_frame_name}' does not exist.", "_get_conduit_by_id", exc_info=True)
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            self._ensure_default_frame()
            conduits = self._default_frame._conduits

        if signature in conduits:
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
            ValueError: If the frame does not exist, the conduit id already
                exists, the root conduit name is missing, or the root conduit
                name already exists in the frame.
        """
        self.check_cleaned()

        if aetheric_frame_name != "default":
            try:
                frame = self._aetheric_frames[aetheric_frame_name]
            except KeyError:
                self._logger.error(f"Aetheric frame '{aetheric_frame_name}' does not exist.", "_add_conduit", exc_info=True)
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            self._ensure_default_frame()
            frame = self._default_frame

        conduits = frame._conduits
        cid = conduit._id
        conduit_name = conduit.name
        if not conduit_name:
            self._logger.error("Root conduit name is required.", "_add_conduit", exc_info=True)
            raise ValueError("Root conduit name is required.")
        if cid in conduits:
            self._logger.error(f"Conduit with ID {cid} already exists.", "_add_conduit", exc_info=True)
            raise ValueError(f"Conduit with ID {cid} already exists.")
        existing_name_id = frame._conduit_ids_by_name.get(conduit_name)
        if existing_name_id is not None and existing_name_id != cid:
            self._logger.error(
                f"Conduit with name {conduit_name} already exists.",
                "_add_conduit",
                exc_info=True,
            )
            raise ValueError(f"Conduit with name {conduit_name} already exists.")

        conduits[cid] = conduit
        frame._conduit_ids_by_name[conduit_name] = cid

    def _remove_conduit(self, conduit: IConduit, aetheric_frame_name: str = "default"):
        """
        Removes a root conduit from a frame. (Internal use)

        Args:
            conduit (IConduit): The conduit to remove.
            aetheric_frame_name (str): The name of the frame.

        Raises:
            ValueError: If the frame does not exist or the conduit is not found.
        """
        self.check_cleaned()

        if aetheric_frame_name != "default":
            try:
                frame = self._aetheric_frames[aetheric_frame_name]
            except KeyError:
                self._logger.error(f"Aetheric frame '{aetheric_frame_name}' does not exist.", "_remove_conduit", exc_info=True)
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            self._ensure_default_frame()
            frame = self._default_frame

        conduits = frame._conduits
        conduit_id = conduit._id
        removed = conduits.pop(conduit_id, None)
        if removed is None:
            self._logger.error(f"Conduit with ID {conduit_id} does not exist.", "_remove_conduit", exc_info=True)
            raise ValueError(f"Conduit with ID {conduit_id} does not exist.")
        conduit_name = removed.name
        if conduit_name:
            mapped_id = frame._conduit_ids_by_name.get(conduit_name)
            if mapped_id == conduit_id:
                frame._conduit_ids_by_name.pop(conduit_name, None)


    def _create_cluster(self, cluster_name: str, aetheric_frame_name: str = "default"):
        """
        Creates a new conduit cluster within a frame. (Internal use)

        Args:
            cluster_name (str): The name for the new cluster.
            aetheric_frame_name (str): The name of the frame.

        Raises:
            ValueError: If the frame does not exist or the cluster name is taken.
        """
        self.check_cleaned()

        if aetheric_frame_name != "default":
            try:
                conduit_clusters = self._aetheric_frames[aetheric_frame_name]._conduit_clusters
            except KeyError:
                self._logger.error(f"Aetheric frame '{aetheric_frame_name}' does not exist.", "_create_cluster", exc_info=True)
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            self._ensure_default_frame()
            conduit_clusters = self._default_frame._conduit_clusters

        if cluster_name in conduit_clusters:
            self._logger.error(f"Cluster with name {cluster_name} already exists.", "_create_cluster", exc_info=True)
            raise ValueError(f"Cluster with name {cluster_name} already exists.")

        conduit_clusters[cluster_name] = ConduitCluster(cluster_name)

    def _remove_cluster(self, cluster_name: str, aetheric_frame_name: str = "default") -> None:
        """
        Removes an existing conduit cluster within a frame. (Internal use)

        Args:
            cluster_name (str): The name of the cluster to remove.
            aetheric_frame_name (str): The name of the frame.

        Raises:
            ValueError: If the frame does not exist or the cluster is missing.
        """
        self.check_cleaned()

        if aetheric_frame_name != "default":
            try:
                conduit_clusters = self._aetheric_frames[aetheric_frame_name]._conduit_clusters
            except KeyError:
                self._logger.error(f"Aetheric frame '{aetheric_frame_name}' does not exist.", "_remove_cluster", exc_info=True)
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            self._ensure_default_frame()
            conduit_clusters = self._default_frame._conduit_clusters

        cluster = conduit_clusters.pop(cluster_name, None)
        if cluster is None:
            self._logger.error(f"Cluster with name {cluster_name} does not exist.", "_remove_cluster", exc_info=True)
            raise ValueError(f"Cluster with name {cluster_name} does not exist.")

        try:
            cluster.cleanup()
        except Exception:
            self._logger.error(f"Cluster cleanup failed for '{cluster_name}'", "_remove_cluster", exc_info=True)


    def _get_cluster(self, cluster_name: str, aetheric_frame_name: str = "default") -> ConduitCluster:
        """
        Internal helper to fetch a ConduitCluster by name and frame.
        """
        if aetheric_frame_name != "default":
            try:
                clusters = self._aetheric_frames[aetheric_frame_name]._conduit_clusters
            except KeyError:
                self._logger.error(f"Aetheric frame '{aetheric_frame_name}' does not exist.", "_get_cluster", exc_info=True)
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            self._ensure_default_frame()
            clusters = self._default_frame._conduit_clusters

        if cluster_name not in clusters:
            self._logger.error(f"Cluster with name {cluster_name} does not exist.", "_get_cluster", exc_info=True)
            raise ValueError(f"Cluster with name {cluster_name} does not exist.")
        return clusters[cluster_name]

    # ------------------------------------------------------------------
    # Cluster sharing hooks and helpers
    # ------------------------------------------------------------------
    def _on_conduit_joined_cluster(self, conduit: IConduit, cluster_name: str, aetheric_frame_name: str = "default"):
        """
        Internal hook: auto-share eligible spells when a conduit joins a cluster.

        Args:
            conduit: The conduit being added to the cluster.
            cluster_name: Name of the cluster.
            aetheric_frame_name: Frame name for lookup.

        Returns:
            None
        """
        cluster = self._get_cluster(cluster_name, aetheric_frame_name)
        frame = self._aetheric_frames[aetheric_frame_name] if aetheric_frame_name != "default" else self._default_frame
        cluster.handle_join(conduit, frame, aetheric_frame_name)

    def _on_conduit_left_cluster(self, conduit: IConduit, cluster_name: str, aetheric_frame_name: str = "default"):
        """
        Internal hook: teardown auto-shared spells when a conduit leaves a cluster.

        Args:
            conduit: The conduit being removed from the cluster.
            cluster_name: Name of the cluster.
            aetheric_frame_name: Frame name for lookup.

        Returns:
            None
        """
        cluster = self._get_cluster(cluster_name, aetheric_frame_name)
        frame = self._aetheric_frames[aetheric_frame_name] if aetheric_frame_name != "default" else self._default_frame
        cluster.handle_leave(conduit, frame, aetheric_frame_name)

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
        self.check_cleaned()

        cluster = self._get_cluster(cluster_name, aetheric_frame_name)
        conduit_id = conduit._id
        cluster.add_member(conduit_id)
        try:
            self._on_conduit_joined_cluster(conduit, cluster_name, aetheric_frame_name)
        except Exception as e:
            self._logger.error(f"_add_conduit_to_cluster: cluster join hook failed: {e}", "_add_conduit_to_cluster", exc_info=True)

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
        self.check_cleaned()

        cluster = self._get_cluster(cluster_name, aetheric_frame_name)
        conduit_id = conduit._id
        try:
            cluster.remove_member(conduit_id)
        except Exception as e:
            self._logger.error(f"Error removing conduit '{conduit_id}' from cluster '{cluster_name}': {e}", "_remove_conduit_from_cluster", exc_info=True)
            raise

        try:
            self._on_conduit_left_cluster(conduit, cluster_name, aetheric_frame_name)
        except Exception as e:
            self._logger.error(f"_remove_conduit_from_cluster: cluster leave hook failed: {e}", "_remove_conduit_from_cluster", exc_info=True)

    def _get_conduits_in_cluster(self, cluster_name: str, aetheric_frame_name: str = "default") -> List[str]:
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
        self.check_cleaned()
        cluster = self._get_cluster(cluster_name, aetheric_frame_name)
        return list(cluster.get_members())

    def _get_clusters_for_conduit(self, conduit_id: str, aetheric_frame_name: str = "default") -> List[str]:
        """
        Return cluster names that contain the given conduit_id.

        Args:
            conduit_id: Target conduit identifier.
            aetheric_frame_name: Frame name.

        Returns:
            List[str]: Cluster names containing the conduit.
        """
        if aetheric_frame_name != "default":
            clusters = self._aetheric_frames[aetheric_frame_name]._conduit_clusters
        else:
            self._ensure_default_frame()
            clusters = self._default_frame._conduit_clusters
        return [name for name, cluster in clusters.items() if conduit_id in cluster.get_members()]

    def _share_new_spell_to_clusters(self, conduit: IConduit, spell: Any, aetheric_frame_name: str = "default") -> None:
        """
        Share a newly bound shareable spell from a conduit to its clusters.

        Args:
            conduit: Owner conduit.
            spell: Newly bound spell.
            aetheric_frame_name: Frame name for lookup.
        """
        if spell.existence != Existence.unique_per_conduit_cluster:
            return
        conduit_id = conduit._id
        cluster_names = self._get_clusters_for_conduit(conduit_id, aetheric_frame_name)
        if not cluster_names:
            return
        # For each cluster, add to registry and push to peers
        frame = self._aetheric_frames[aetheric_frame_name] if aetheric_frame_name != "default" else self._default_frame
        for cname in cluster_names:
            cluster = self._get_cluster(cname, aetheric_frame_name)
            cluster.add_shared_spell(conduit_id, spell.spell_index)
            for peer_id in cluster.get_members():
                if peer_id == conduit_id:
                    continue
                peer = frame._conduits.get(peer_id)
                if peer is None:
                    continue
                cluster.share_to_borrower(conduit, peer)

    def _refresh_cluster_shares_for_conduit(self, conduit: IConduit, aetheric_frame_name: str = "default") -> None:
        """
        Refresh sharing for an existing conduit across all clusters it belongs to.

        Args:
            conduit: Target conduit.
            aetheric_frame_name: Frame name.

        Returns:
            None
        """
        conduit_id = conduit._id
        cluster_names = self._get_clusters_for_conduit(conduit_id, aetheric_frame_name)
        if not cluster_names:
            return
        frame = self._aetheric_frames[aetheric_frame_name] if aetheric_frame_name != "default" else self._default_frame
        for cname in cluster_names:
            cluster = self._get_cluster(cname, aetheric_frame_name)
            cluster.refresh_member_shares(conduit, frame, aetheric_frame_name)

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
        self.check_cleaned()
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
            self._ensure_default_frame()
            spell_registry = self._default_frame._spell_registry

        # Search each SpellIndex for the SHA256 version
        for conduit_id, spell_set in spell_registry.items():
            for spell_index in spell_set:
                if spell_index.has_version(spell_id):
                    return self._get_conduit_by_id(conduit_id, aetheric_frame_name)

        self._logger.error(
            f"Spell version {spell_id} not found in any conduit.",
            "_get_conduit_by_spell_id", exc_info=True
        )
        raise ValueError(f"Spell version {spell_id} not found in any conduit.")

    # endregion Conduit Management

    # region Spell Management

    def _check_for_spell(self, spell_id: str, aetheric_frame_name: str = "default") -> SpellIndex | None:
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
            SpellIndex | None: The SpellIndex containing the spell ID, or None if not found.
        """
        self.check_cleaned()
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
            self._ensure_default_frame()
            frame = self._default_frame

        # Fast O(1-ish) lookup via cached version_registry
        found = frame.has_version(spell_id)
        if found is True:
            return frame.find_and_return_spell_index(spell_id)
        else:
            return None

    def _add_spells_to_aether(self, conduit_id: str, spell_set: Set[SpellIndex],
                              aetheric_frame_name: str = "default") -> None:
        """
        Registers a set of SpellIndex objects for a conduit and refreshes version registry.

        Args:
            conduit_id (str): The id of the owning conduit.
            spell_set (ConcurrentSet[SpellIndex]): The set of SpellIndex objects to register.
            aetheric_frame_name (str): The name of the frame.
        """
        self.check_cleaned()

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
            self._ensure_default_frame()
            frame = self._default_frame

        spell_registry = frame._spell_registry

        # Prevent duplicate conduit registration
        if conduit_id in spell_registry:
            raise ValueError(f"Spell registry already contains Conduit ID {conduit_id}.")

        # Add spell set
        spell_registry[conduit_id] = spell_set

        # Critical: update SHA256 version registry
        frame.refresh_version_registry()

    def _remove_spells_from_aether(self, conduit_id: str, spell_set: Set[SpellIndex],
                                   aetheric_frame_name: str = "default") -> None:
        """
        Unregisters a set of SpellIndex objects for a conduit and refreshes version registry.

        Args:
            conduit_id (str): The id of the owning conduit.
            spell_set (Set[SpellIndex]): The set of SpellIndex objects to unregister.
            aetheric_frame_name (str): The name of the frame.
        """
        self.check_cleaned()

        if aetheric_frame_name != "default":
            try:
                frame = self._aetheric_frames[aetheric_frame_name]
            except KeyError:
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            self._ensure_default_frame()
            frame = self._default_frame

        spell_registry = frame._spell_registry

        if conduit_id not in spell_registry:
            return

        for spell_index in list(spell_set):
            try:
                spell_registry[conduit_id].remove(spell_index)
            except Exception:
                pass

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
        self.check_cleaned()

        # Pick frame registry
        if aetheric_frame_name != "default":
            try:
                frame = self._aetheric_frames[aetheric_frame_name]
            except KeyError:
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            self._ensure_default_frame()
            frame = self._default_frame

        spell_registry = frame._spell_registry

        # Ensure there is a spell set for this conduit
        if conduit_id not in spell_registry:
            spell_registry[conduit_id] = set()

        # Add SpellIndex
        spell_registry[conduit_id].add(spell_index)

        # Critical: keep version registry in sync
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
        self.check_cleaned()

        # Pick frame
        if aetheric_frame_name != "default":
            try:
                frame = self._aetheric_frames[aetheric_frame_name]
            except KeyError:
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            self._ensure_default_frame()
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
        self.check_cleaned()
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
            self._ensure_default_frame()
            frame = self._default_frame

        frame.refresh_version_registry()

    def _get_all_spell_versions(self, aetheric_frame_name: str = "default") -> set[str]:
        """
        Returns a flat set of all SHA256 versions for a given frame,
        using the frame's _version_registry.

        Call `_refresh_version_registry` first if you need the latest state.
        """
        self.check_cleaned()
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
            self._ensure_default_frame()
            frame = self._default_frame

        versions = frame.get_all_versions()
        return versions

    # endregion Spell Management

    #region Mutation Research

    def _get_mutation_research(self, aetheric_frame_name: str = "default") -> "MutationResearch":
        """
        Retrieves the MutationResearch manager associated with a specific Aetheric Frame.

        Internal use only.

        Args:
            aetheric_frame_name (str): The name of the frame whose MutationResearch
                object should be retrieved. Defaults to "default".

        Returns:
            MutationResearch: The MutationResearch instance for the target frame.

        Raises:
            ValueError: If the specified frame does not exist.
            RuntimeError: If the Aether or target frame has been cleaned.
        """
        self.check_cleaned()
        # Select frame
        if aetheric_frame_name != "default":
            try:
                frame = self._aetheric_frames[aetheric_frame_name]
            except KeyError:
                self._logger.error(
                    f"Aetheric frame '{aetheric_frame_name}' does not exist.",
                    "_get_mutation_research",
                    exc_info=True
                )
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            self._ensure_default_frame()
            frame = self._default_frame

        # Validate frame
        if frame is None or frame._cleaned:
            raise RuntimeError(
                f"The AethericFrame '{aetheric_frame_name}' has been cleaned or is unavailable."
            )

        return frame._mutation_research

    #endregion Mutation Research
    #region DevOps Management
    def _get_devops_manager(self, aetheric_frame_name: str = "default") -> IDevOpsManager:
        """
        Retrieves the DevOpsManager associated with a specific Aetheric Frame.

        Internal use only.

        Args:
            aetheric_frame_name (str): The name of the frame whose DevOpsManager
                object should be retrieved. Defaults to "default".

        Returns:
            DevOpsManager: The DevOpsManager instance for the target frame.

        Raises:
            ValueError: If the specified frame does not exist.
            RuntimeError: If the Aether or target frame has been cleaned.
        """
        self.check_cleaned()
        # Select frame
        if aetheric_frame_name != "default":
            try:
                frame = self._aetheric_frames[aetheric_frame_name]
            except KeyError:
                self._logger.error(
                    f"Aetheric frame '{aetheric_frame_name}' does not exist.",
                    "_get_devops_manager",
                    exc_info=True
                )
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            self._ensure_default_frame()
            frame = self._default_frame

        # Validate frame
        if frame is None or frame._cleaned:
            raise RuntimeError(
                f"The AethericFrame '{aetheric_frame_name}' has been cleaned or is unavailable."
            )

        return frame._dev_ops_manager


    def _get_spell_system_states(self, aetheric_frame_name: str = "default") -> ISpellSystemStates:
        """
        Retrieves the global SpellSystemStates manager.

        Returns:
            ISpellSystemStates: The SpellSystemStates instance.
        """
        self.check_cleaned()
        return self._get_devops_manager(aetheric_frame_name).spell_system_states

    def _get_incident_manager(self, aetheric_frame_name: str = "default") -> IIncidentManager:
        """
        Retrieves the IncidentManager from the DevOpsManager of a specific frame.

        Returns:
            IncidentManager: The IncidentManager instance.
        """
        self.check_cleaned()
        return self._get_devops_manager(aetheric_frame_name).incident_manager

    def _get_change_control_manager(self, aetheric_frame_name: str = "default") -> IChangeControlManager:
        """
        Retrieves the ChangeControlManager from the DevOpsManager of a specific frame.

        Returns:
            ChangeControlManager: The ChangeControlManager instance.
        """
        self.check_cleaned()
        return self._get_devops_manager(aetheric_frame_name).change_control_manager

    def _revalidate_dirty_roots(
            self,
            conduit_id: str,
            aetheric_frame_name: str = "default",
            cancel_event: Any = None,
    ) -> None:
        """
        Trigger revalidation of dirty roots for a conduit via ChangeControlManager.
        """
        self.check_cleaned()
        if not conduit_id:
            raise ValueError("conduit_id cannot be empty.")
        devops = self._get_devops_manager(aetheric_frame_name)
        devops.revalidate_dirty_roots(conduit_id, cancel_event=cancel_event)

    #endregion DevOps Management
