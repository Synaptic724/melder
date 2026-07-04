import logging
from threading import RLock
from types import TracebackType
from typing import TYPE_CHECKING, Optional, Any, Dict, Set, Tuple, ClassVar

from melder.utilities.helpers.ulid_factory import new_ulid


# Melder Imports
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.aether_configuration import AetherConfiguration
from melder.aether.aether_configuration_builder import AetherConfigurationBuilder
from melder.nexus.nexus import Nexus
from melder.crystallizer.crystallizer import Crystallizer
from melder.utilities.interfaces.ichannellogger import IChannelLogger
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.utilities.general_base.cleanable import Cleanable
from melder.aether.aetheric_frame.aetheric_frame import AethericFrame
from melder.aether.aetheric_frame.aetheric_frame_configuration import AethericFrameConfiguration
from melder.utilities.helpers.init_helpers import InitHelpers
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
if TYPE_CHECKING:
    from melder.mutation_research.mutation_research import MutationResearch
    from melder.aether.conduit.conduit import Conduit
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.change_control_manager import ChangeControlManager
    from melder.aether.aetheric_frame.conduit_cloud import ConduitCloud
    from melder.aether.aetheric_frame.dev_ops.dev_ops_manager import DevOpsManager
    from melder.aether.aetheric_frame.dev_ops.incident_manager.incident_manager import IncidentManager
    from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states import SpellSystemStates
    from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration


class Aether(Cleanable):
    """
    The global singleton root that owns all `AethericFrame` instances.

    `Aether` is the top-level runtime host for Melder. It owns the named frame
    registry, the always-present default frame, and the frame-level services
    that other runtime objects resolve through when they need configuration,
    conduit, cluster, spell, or DevOps state.

    Contract:
        - Enforces singleton construction through `__new__`.
        - Owns the lifecycle of registered `AethericFrame` instances.
        - Owns the default frame and ensures it exists while the singleton is live.
        - Hosts singleton-level subsystems such as Nexus, Crystallizer, and the
          utility system.
        - Hosts the singleton MutationResearch root above frame-local runtime
          state.
        - Owns one optional Aether root configuration that applies policy into
          the hosted utility system.
        - Becomes reinitializable only after `cleanup()` fully resets singleton state.

    Threading / Concurrency:
    - Uses the class-level `_lock` to serialize singleton construction and reset.
    - Uses the instance `_lock` to guard cleanup and frame-registry mutation.

    Lifecycle / Cleanup:
    - Cleans registered frames before dropping singleton-level references.
    - Resets `_instance` and `_initialized` so tests or later runtime flows can
      create a fresh singleton after teardown.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    _instance: ClassVar[Optional["Aether"]] = None
    _lock: ClassVar[RLock] = RLock()
    _initialized: ClassVar[bool] = False

    def __new__(cls, *args: object, **kwargs: object) -> "Aether":
        """
        Return the one process-wide `Aether` singleton instance.

        Contract:
            - Uses the class-level lock to serialize singleton construction.
            - Creates the singleton lazily on first access.
            - Returns the existing live instance on later calls until cleanup
              resets singleton state.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(Aether, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
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
            - Starts with a null SafeLogger wrapper and no attached raw logger.
            - Does not try to attach a real logger during boot.
            - Does not preinstall a Nexus configuration during normal boot.

        Returns:
            None.
        """
        if not Aether._initialized:
            try:
                super().__init__()
                self._id: str = new_ulid()
                self._crystallizer: Crystallizer = Crystallizer(aether=self)
                self._configuration: Optional[AetherConfiguration] = None
                self._configured: bool = False
                self._activated: bool = False
                self._logger = InitHelpers.resolve_safe_logger(None)
                self._aetheric_frames: Dict[str, AethericFrame] = {}
                self._default_frame: Optional[AethericFrame] = None
                self._aether_utility_system: AetherUtilitySystem = AetherUtilitySystem()
                # Crystallizer is constructed FIRST so it can be unfolded into
                # every frame/spellbook/conduit and into MutationResearch as the
                # passive emission sink (they hold a non-owning reference; Aether
                # owns and cleans it).
                default_frame = AethericFrame(self, "default")
                self._aetheric_frames["default"] = default_frame
                self._default_frame = default_frame
                # MutationResearch is constructed lazily on first access
                # (`_get_mutation_research`): its import chain and root build
                # cost several milliseconds on the cold import path (Aether()
                # runs at package import) while serving zero boot traffic.
                self._mutation_research: Optional["MutationResearch"] = None
                self._nexus: Nexus = Nexus(aether=self)
                Aether._initialized = True
            except Exception:
                with Aether._lock:
                    if Aether._instance is self:
                        Aether._instance = None
                    Aether._initialized = False
                raise

    def cleanup(self) -> None:
        """
        Cleanup the entire Aether singleton and all owned frame/subsystem state.

        Purpose:
            Tear down the global runtime host, including every owned frame and
            singleton-level subsystem, so a later clean bootstrap starts from a
            truly empty root.

        Contract:
            - Idempotent.
            - Cleans owned frames before dropping singleton-level references.
            - Cleans the hosted Nexus singleton and utility system when they exist.
            - Resets singleton bootstrap state so `Aether()` can be safely
              reinitialized later.
            - Logger cleanup is performed after frame and subsystem teardown.

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
                if self._crystallizer is not None:
                    self._crystallizer.cleanup()
                if self._mutation_research is not None:
                    self._mutation_research.cleanup()
                if self._configuration is not None:
                    self._configuration.cleanup()
                self._configured = False
                self._activated = False
                if self._nexus is not None:
                    self._nexus.cleanup()
                if self._aether_utility_system is not None:
                    self._aether_utility_system.cleanup()

                del self._aether_utility_system
                del self._aetheric_frames
                del self._crystallizer
                del self._mutation_research
                del self._configuration
                del self._nexus
                del self._default_frame


                # Reset Singleton state to allow re-initialization (e.g. in tests)
                Aether._instance = None
                Aether._initialized = False
            except Exception as e:
                self._logger.error(f"Error cleaning up Aether: {e}", "cleanup", exc_info=True)
                raise

        if self._logger is not None:
            if hasattr(self._logger, 'cleanup'):
                self._logger.cleanup()
        del self._logger

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

    def _ensure_default_frame(self) -> AethericFrame:
        """
        Ensure the singleton still has a live default frame.

        Contract:
            - Raises instead of silently recreating the default frame on a
              cleaned or partially torn-down singleton.
        """
        frame = self._default_frame
        if frame is None:
            raise RuntimeError("Default AethericFrame has been cleaned or is unavailable.")
        return frame

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
            - Notifies `Nexus` before the registry entry is removed so any
              manager-owned frame state, descriptor cache state, and ACL state
              can be detached consistently.

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
                        f"Error detaching Nexus frame state for '{frame_name}': {e}",
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

    def cleanup_aetheric_frames(self) -> None:
        """
        Cleanup every frame currently owned by the singleton.

        Contract:
            - Iterates over a snapshot of the frame registry.
            - Attempts every frame cleanup even if one frame raises.
            - Logs cleanup failures instead of stopping the full singleton
              teardown on the first frame error.
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
    def __enter__(self) -> "Aether":
        """
        Enter the Aether lock context and return `self`.

        Contract:
            - Acquires the singleton instance lock.
            - Returns the live singleton while the lock is held.

        Returns:
            Aether:
                This singleton instance while the lock is held.
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
        Exit the Aether lock context.

        Contract:
            - Releases the singleton instance lock acquired by `__enter__`.

        Returns:
            None.
        """
        self._lock.release()

    #endregion Context Manager

    #region Rift Hosting

    #endregion Rift Hosting


    @property
    def logger(self) -> IChannelLogger | logging.Logger | None:
        """
        Return the raw logger currently wrapped by the internal `SafeLogger`.

        Contract:
            - Exposes the underlying logger object for diagnostics or
              replacement.
            - Returns `None` when the wrapper currently holds the null logger.

        Returns:
            The raw logger object, or None if no logger is set.
        """
        return self._logger._logger # Accesses the raw logger inside SafeLogger

    @logger.setter
    def logger(self, value: IChannelLogger | logging.Logger | None) -> None:
        """
        Replace the attached logger through the explicit attach path.

        Contract:
            - Delegates to `attach_logger(...)`.

        Args:
            value: The IChannelLogger, Logger, Handler, or None to use.
        """
        self.attach_logger(value)

    def attach_logger(
            self,
            logger: IChannelLogger | logging.Logger | None,
    ) -> None:
        """
        Attach one real logger after Aether boot.

        Purpose:
            Aether is created too early in runtime boot for a real logger to be
            attached reliably in `__init__`. This method is the explicit
            post-boot logger-attachment seam.

        Contract:
            - Aether starts with a null `SafeLogger` wrapper and no attached
              raw logger.
            - Passing a real logger attaches it through the `SafeLogger`
              facade.
            - Passing None resets Aether back to the null logger wrapper.

        Args:
            logger:
                Real logger object to attach, or None to detach back to the
                null logger wrapper.

        Returns:
            None.
        """
        self.check_cleaned()
        self._logger = InitHelpers.resolve_safe_logger(logger)

    def enable_logging(
            self,
            logger: IChannelLogger | logging.Logger | None = None,
    ) -> None:
        """
        Enable Aether's own logger after boot.

        Purpose:
            Attach one explicit logger when provided, otherwise try the current
            automatic channel logger path through `AetherUtilitySystem`.

        Contract:
            - Passing an explicit logger always uses the direct safe-logger
              attachment path and does not require Aether root configuration.
            - Calling this method without an explicit logger requires:
              - an installed and activated `AetherConfiguration`
              - automatic channel logger activation enabled in that config
              - at least one automatic provider path registered on the hosted
                utility system (channel resolver or default logger)
            - The automatic path fails fast when that setup is incomplete
              instead of silently leaving Aether on the null logger path.

        Args:
            logger:
                Optional explicit logger override.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the automatic logger path is requested before Aether root
                configuration has been activated, if automatic channel logger
                activation is disabled, or if no automatic logger provider has
                been registered into the utility system.
        """
        self.check_cleaned()
        if logger is not None:
            self.attach_logger(logger)
            return
        if not self._activated or self._configuration is None:
            raise RuntimeError(
                "AetherConfiguration must be activated before automatic "
                "Aether logging can be enabled."
            )
        if not self._configuration.channel_logger_activation_enabled:
            raise RuntimeError(
                "Automatic channel logger activation is disabled in "
                "AetherConfiguration."
            )
        if not self._aether_utility_system.is_channel_logger_activation_enabled():
            raise RuntimeError(
                "AetherUtilitySystem automatic channel logger activation is "
                "disabled."
            )
        if (
                not self._aether_utility_system.has_channel_logger_resolver()
                and not self._aether_utility_system.has_default_logger()
        ):
            raise RuntimeError(
                "AetherUtilitySystem has no automatic logger provider "
                "configured."
            )
        self._logger = InitHelpers.resolve_channel_logger(
            self,
            groups=["aether", "lifecycle"],
            system_groups=["aether"],
            props={"component": "aether"},
            channels="system",
        )
        if self._logger._logger is None:
            raise RuntimeError(
                "Automatic Aether logger resolution returned no logger."
            )

    @property
    def configuration(self) -> Optional[AetherConfiguration]:
        """
        Return the installed Aether root configuration, if any.

        Returns:
            Optional[AetherConfiguration]: Installed root config.
        """
        self.check_cleaned()
        return self._configuration

    @property
    def configured(self) -> bool:
        """
        Return whether an Aether root configuration is installed.

        Returns:
            bool: True when a config is installed.
        """
        self.check_cleaned()
        return self._configured

    @property
    def mutation_research(self) -> MutationResearch:
        """
        Return the Aether-owned MutationResearch root.

        Returns:
            MutationResearch: Hosted mutation-research singleton.
        """
        self.check_cleaned()
        return self._get_mutation_research()

    @property
    def activated(self) -> bool:
        """
        Return whether the Aether root configuration has been applied.

        Returns:
            bool: True when root config has been activated.
        """
        self.check_cleaned()
        return self._activated

    def create_configuration(self) -> AetherConfiguration:
        """
        Create a fresh Aether root configuration object.

        Returns:
            AetherConfiguration: New mutable config object.
        """
        self.check_cleaned()
        return AetherConfiguration()

    def create_configuration_builder(self) -> AetherConfigurationBuilder:
        """
        Create a fresh fluent builder for Aether root configuration assembly.

        Purpose:
            Mirror the repo's configuration-builder workflow at the Aether root
            so callers do not need to import the builder directly just to
            assemble the first logger-policy slice.

        Returns:
            AetherConfigurationBuilder:
                New one-shot builder instance.
        """
        self.check_cleaned()
        return AetherConfigurationBuilder()

    def configure(self, configuration: AetherConfiguration) -> None:
        """
        Install one root configuration on Aether.

        Args:
            configuration:
                Root configuration object to install.

        Returns:
            None.
        """
        self.check_cleaned()
        if not isinstance(configuration, AetherConfiguration):
            raise TypeError("configuration must be an AetherConfiguration instance.")
        self._configuration = configuration
        self._configured = True

    def activate(
            self,
            configuration: Optional[AetherConfiguration] = None,
    ) -> None:
        """
        Activate the installed Aether root configuration.

        Args:
            configuration:
                Optional configuration to install before activation.

        Returns:
            None.
        """
        self.check_cleaned()
        if configuration is not None:
            self.configure(configuration)
        if not self._configured or self._configuration is None:
            raise RuntimeError("Aether is not configured.")
        if not self._configuration.activated:
            raise RuntimeError(
                "AetherConfiguration must be activated before activating Aether."
            )
        self._configuration.validate()
        self._apply_configuration_to_utility_system()
        self._activated = True

    def _apply_configuration_to_utility_system(self) -> None:
        """
        Apply the installed root configuration into the hosted utility system.

        Returns:
            None.
        """
        utility_system = self._aether_utility_system
        configuration = self._configuration
        if configuration is None:
            raise RuntimeError("Aether is not configured.")
        utility_system.set_channel_logger_activation_enabled(
            configuration.channel_logger_activation_enabled
        )
        utility_system.clear_channel_logger_resolver()
        utility_system.clear_default_logger()
        if configuration.channel_logger_resolver is not None:
            utility_system.register_channel_logger_resolver(
                configuration.channel_logger_resolver
            )
        if configuration.default_logger is not None:
            utility_system.register_default_logger(configuration.default_logger)

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

    def _create_frame(self, aetheric_frame_name: str = "default") -> AethericFrame:
        """
        Internal

        Create a new AethericFrame for the given name and fail if it already
        exists.

        Purpose:
            Provide a strict frame-creation path for callers that are
            authoring a brand-new frame and must not silently recover an
            existing frame shell.

        Contract:
            - Raises when the requested frame already exists.
            - Creates and registers a new frame when absent.
            - Does not mutate the default frame pointer unless the name is
              `"default"`.

        Args:
            aetheric_frame_name:
                The frame name to create.

        Returns:
            AethericFrame: Newly created frame.

        Raises:
            TypeError: If the frame name is not a string.
            RuntimeError: If the Aether is cleaned or the frame registry is
                unavailable.
            ValueError: If the frame already exists.

        Threading:
            Acquires the Aether lock to serialize frame creation.

        Lifecycle:
            The created frame is owned by Aether and will be cleaned by
            `Aether.cleanup()`.
        """
        self.check_cleaned()
        if not isinstance(aetheric_frame_name, str):
            raise TypeError("aetheric_frame_name must be a string.")

        if self._aetheric_frames is None:
            raise RuntimeError("Aether frame registry is unavailable.")

        with self._lock:
            if self._aetheric_frames is None:
                raise RuntimeError("Aether frame registry is unavailable.")
            if aetheric_frame_name in self._aetheric_frames:
                raise ValueError(
                    "AethericFrame '{0}' already exists.".format(
                        aetheric_frame_name
                    )
                )
            frame = AethericFrame(self, aetheric_frame_name)
            self._aetheric_frames[aetheric_frame_name] = frame
            if aetheric_frame_name == "default":
                self._default_frame = frame
            return frame


    def _bind_configuration(
            self,
            configuration: SpellbookConfiguration,
            aetheric_frame_name: str = "default",
    ) -> None:
        """
        Bind the shared Spellbook configuration object to one frame.

        Purpose:
            Preserve the richer configuration object alongside the narrower
            frame-level AR posture object.

        Contract:
            - Binds the first shared rich configuration published for the
              frame.
            - Leaves an existing shared rich configuration in place instead of
              overwriting it during later concurrent binds.
            - Does not validate or merge posture fields here; frame posture is
              owned separately by `AethericFrame`.

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
                    frame = self._aetheric_frames[aetheric_frame_name]
                except KeyError:
                    self._logger.error(f"Aetheric frame '{aetheric_frame_name}' does not exist.", "_bind_configuration", exc_info=True)
                    raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
                if frame._configuration is None:
                    frame._configuration = configuration
            else:
                frame = self._ensure_default_frame()
                if frame._configuration is None:
                    frame._configuration = configuration


    def _get_configuration(self, aetheric_frame_name: str = "default") -> Optional[SpellbookConfiguration]:
        """
        Return the shared Spellbook configuration object bound to one frame.

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
            frame = self._ensure_default_frame()
            cfg = frame._configuration

        return cfg

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
            frame = self._ensure_default_frame()

        return frame.frame_configuration

    # endregion Configuration
    # region Conduit Management

    def _get_existing_frame(
            self,
            aetheric_frame_name: str = "default",
    ) -> AethericFrame:
        """
        Return one existing frame without creating new custom frames.

        Args:
            aetheric_frame_name:
                Name of the target frame.

        Returns:
            AethericFrame: Existing frame handle.

        Raises:
            ValueError: If the specified custom frame does not exist.
        """
        self.check_cleaned()
        if aetheric_frame_name != "default":
            try:
                return self._aetheric_frames[aetheric_frame_name]
            except KeyError:
                self._logger.error(
                    f"Aetheric frame '{aetheric_frame_name}' does not exist.",
                    "_get_existing_frame",
                    exc_info=True,
                )
                raise ValueError(
                    f"Aetheric frame '{aetheric_frame_name}' does not exist."
                )
        return self._ensure_default_frame()

    def list_conduit_ids(
            self,
            aetheric_frame_name: str = "default",
    ) -> Tuple[str, ...]:
        """
        Return the registered root conduit identifiers for one frame.

        Args:
            aetheric_frame_name:
                Name of the target frame.

        Returns:
            Tuple[str, ...]: Snapshot of root conduit ids.

        Raises:
            ValueError: If the specified frame does not exist.
        """
        self.check_cleaned()
        if aetheric_frame_name != "default":
            try:
                frame = self._aetheric_frames[aetheric_frame_name]
            except KeyError:
                self._logger.error(
                    "Aetheric frame '{0}' does not exist.".format(
                        aetheric_frame_name
                    ),
                    "list_conduit_ids",
                    exc_info=True,
                )
                raise ValueError(
                    "Aetheric frame '{0}' does not exist.".format(
                        aetheric_frame_name
                    )
                )
        else:
            frame = self._ensure_default_frame()
        return tuple(frame._conduits.keys())

    def list_conduit_names(
            self,
            aetheric_frame_name: str = "default",
    ) -> Tuple[str, ...]:
        """
        Return the registered root conduit names for one frame.

        Args:
            aetheric_frame_name:
                Name of the target frame.

        Returns:
            Tuple[str, ...]: Snapshot of root conduit names.

        Raises:
            ValueError: If the specified frame does not exist.
        """
        self.check_cleaned()
        if aetheric_frame_name != "default":
            try:
                frame = self._aetheric_frames[aetheric_frame_name]
            except KeyError:
                self._logger.error(
                    "Aetheric frame '{0}' does not exist.".format(
                        aetheric_frame_name
                    ),
                    "list_conduit_names",
                    exc_info=True,
                )
                raise ValueError(
                    "Aetheric frame '{0}' does not exist.".format(
                        aetheric_frame_name
                    )
                )
        else:
            frame = self._ensure_default_frame()
        return tuple(frame._conduit_ids_by_name.keys())

    def count_conduits(self, aetheric_frame_name: str = "default") -> int:
        """
        Return the number of registered root conduits for one frame.

        Args:
            aetheric_frame_name:
                Name of the target frame.

        Returns:
            int: Number of registered root conduits.
        """
        return len(self.list_conduit_ids(aetheric_frame_name))

    def has_conduit_id(
            self,
            conduit_id: str,
            aetheric_frame_name: str = "default",
    ) -> bool:
        """
        Return whether one root conduit id exists in one frame.

        Args:
            conduit_id:
                Root conduit id to check.
            aetheric_frame_name:
                Name of the target frame.

        Returns:
            bool: True when the conduit id exists in the target frame.
        """
        return conduit_id in self.list_conduit_ids(aetheric_frame_name)

    def has_conduit_name(
            self,
            name: str,
            aetheric_frame_name: str = "default",
    ) -> bool:
        """
        Return whether one root conduit name exists in one frame.

        Args:
            name:
                Root conduit name to check.
            aetheric_frame_name:
                Name of the target frame.

        Returns:
            bool: True when the conduit name exists in the target frame.
        """
        return name in self.list_conduit_names(aetheric_frame_name)

    def find_conduit_id_by_name(
            self,
            name: str,
            aetheric_frame_name: str = "default",
    ) -> Optional[str]:
        """
        Return the registered root conduit id for one name, if present.

        Args:
            name:
                Root conduit name to resolve.
            aetheric_frame_name:
                Name of the target frame.

        Returns:
            Optional[str]: Matching conduit id, or None when missing.

        Raises:
            ValueError: If the specified frame does not exist.
        """
        self.check_cleaned()
        if aetheric_frame_name != "default":
            try:
                frame = self._aetheric_frames[aetheric_frame_name]
            except KeyError:
                self._logger.error(
                    "Aetheric frame '{0}' does not exist.".format(
                        aetheric_frame_name
                    ),
                    "find_conduit_id_by_name",
                    exc_info=True,
                )
                raise ValueError(
                    "Aetheric frame '{0}' does not exist.".format(
                        aetheric_frame_name
                    )
                )
        else:
            frame = self._ensure_default_frame()
        return frame._conduit_ids_by_name.get(name)

    def get_conduit_by_name(
            self,
            name: str,
            aetheric_frame_name: str = "default",
    ) -> Conduit:
        """
        Return one registered root conduit by name.

        Args:
            name:
                Root conduit name to resolve.
            aetheric_frame_name:
                Name of the target frame.

        Returns:
            Conduit: Matching root conduit.

        Raises:
            ValueError: If the frame does not exist or the conduit is missing.
        """
        self.check_cleaned()
        return self._get_conduit_by_name(name, aetheric_frame_name)

    def get_conduit_by_id(
            self,
            conduit_id: str,
            aetheric_frame_name: str = "default",
    ) -> Conduit:
        """
        Return one registered root conduit by id.

        Args:
            conduit_id:
                Root conduit id to resolve.
            aetheric_frame_name:
                Name of the target frame.

        Returns:
            Conduit: Matching root conduit.

        Raises:
            ValueError: If the frame does not exist or the conduit is missing.
        """
        self.check_cleaned()
        return self._get_conduit_by_id(conduit_id, aetheric_frame_name)

    def get_conduit_cloud(
            self,
            aetheric_frame_name: str = "default",
    ) -> ConduitCloud:
        """
        Return the frame-local conduit and cluster service for one frame.

        Purpose:
            Expose the frame-owned `ConduitCloud` through Aether so callers can
            start from the top-level runtime host and move into the frame-local
            conduit and cluster service surface explicitly.

        Args:
            aetheric_frame_name:
                Name of the target frame.

        Returns:
            ConduitCloud: The frame-local conduit cloud for the requested frame.

        Raises:
            ValueError: If the requested frame does not exist.
        """
        self.check_cleaned()
        frame = self._get_existing_frame(aetheric_frame_name)
        return frame._conduit_cloud

    def _get_conduit_by_name(self, name: str, aetheric_frame_name: str = "default") -> Conduit:
        """
        Find a root conduit within one frame by its registered name.

        Args:
            name (str):
                Name of the conduit.
            aetheric_frame_name (str):
                Name of the frame to search.

        Returns:
            Conduit:
                The matching conduit.

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
            frame = self._ensure_default_frame()

        conduit_id = frame._conduit_ids_by_name.get(name)
        if conduit_id is not None:
            conduit = frame._conduits.get(conduit_id)
            if conduit is not None:
                return conduit

        self._logger.error(f"Conduit with name {name} not found.", "_get_conduit_by_name", exc_info=True)
        raise ValueError(f"Conduit with name {name} not found.")

    def _get_conduit_by_id(self, signature: str, aetheric_frame_name: str = "default") -> Conduit:
        """
        Find a root conduit within one frame by its id.

        Args:
            signature (str):
                Id of the conduit.
            aetheric_frame_name (str):
                Name of the frame to search.

        Returns:
            Conduit:
                The matching conduit.

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
            frame = self._ensure_default_frame()
            conduits = frame._conduits

        if signature in conduits:
            return conduits[signature]

        self._logger.error(f"Conduit with signature {signature} not found.", "_get_conduit_by_id", exc_info=True)
        raise ValueError(f"Conduit with signature {signature} not found.")

    def _get_conduit_by_spell_id(self, spell_id: str, aetheric_frame_name: str = "default") -> Conduit:
        """
        Finds the conduit that owns a specific spell ID within a frame.

        Args:
            spell_id (str): The spell ID (SHA256 hash) to search for.
            aetheric_frame_name (str): The name of the frame.

        Returns:
            Conduit: The conduit that owns the spell.

        Raises:
            ValueError: If the frame does not exist or the spell ID is not found.
        """
        self.check_cleaned()
        # Select frame
        if aetheric_frame_name != "default":
            try:
                frame = self._aetheric_frames[aetheric_frame_name]
            except KeyError:
                self._logger.error(
                    f"Aetheric frame '{aetheric_frame_name}' does not exist.",
                    "_get_conduit_by_spell_id",
                    exc_info=True
                )
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            frame = self._ensure_default_frame()

        # Locked lookup so a concurrent conjure cannot mutate the registry mid-scan.
        conduit_id = frame.find_conduit_id_for_spell(spell_id)
        if conduit_id is not None:
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
        using the frame's _selected_spell_registry cache (maintained per-conduit as
        conduits register and unregister their lineages).

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
            frame = self._ensure_default_frame()

        # Fast O(1-ish) lookup via cached selected_spell_registry
        found = frame.has_spell(spell_id)
        if found is True:
            return frame.find_index_for_spell(spell_id)
        else:
            return None

    def _add_spells_to_aether(self, conduit_id: str, spell_set: Set[SpellIndex],
                              aetheric_frame_name: str = "default", spell_ids: Set[str] | None = None) -> None:
        """
        Registers a set of SpellIndex objects for a conduit and refreshes version registry.

        Args:
            conduit_id (str): The id of the owning conduit.
            spell_set (Set[SpellIndex]): The set of SpellIndex objects to register.
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
            frame = self._ensure_default_frame()

        # Frame-owned + lock-serialized: duplicate check, write, and version
        # refresh happen atomically under frame._lock (no direct dict poking).
        frame.register_conduit_spells(conduit_id, spell_set, spell_ids)

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
            frame = self._ensure_default_frame()

        # Frame-owned + lock-serialized: removal + version refresh atomically.
        frame.unregister_conduit_spells(conduit_id, spell_set)


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
            frame = self._ensure_default_frame()

        # Frame-owned + lock-serialized: ensure-set, add, version refresh atomically.
        frame.register_spell_index(conduit_id, spell_index)

    def _remove_single_spell_index(
            self,
            conduit_id: str,
            spell_index: SpellIndex,
            aetheric_frame_name: str = "default",
    ) -> None:
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
            frame = self._ensure_default_frame()

        # Frame-owned + lock-serialized: removal + version refresh atomically.
        frame.unregister_spell_index(conduit_id, spell_index)

    def _get_all_spell_ids(self, aetheric_frame_name: str = "default") -> set[str]:
        """
        Return a flat set of all spell version ids known for one frame.

        Contract:
            - Reads from the frame-owned cached version registry, maintained
              per-conduit on registration.

        Args:
            aetheric_frame_name (str):
                Name of the target frame.

        Returns:
            set[str]:
                All cached spell version ids for the frame.
        """
        self.check_cleaned()
        if aetheric_frame_name != "default":
            try:
                frame = self._aetheric_frames[aetheric_frame_name]
            except KeyError:
                self._logger.error(
                    f"Aetheric frame '{aetheric_frame_name}' does not exist.",
                    "_get_all_spell_ids",
                    exc_info=True
                )
                raise ValueError(f"Aetheric frame '{aetheric_frame_name}' does not exist.")
        else:
            frame = self._ensure_default_frame()

        spell_ids = frame.spells_in_index()
        return spell_ids

    # endregion Spell Management

    #region Mutation Research

    def _get_mutation_research(self) -> "MutationResearch":
        """
        Return the Aether-owned MutationResearch root, building it on first use.

        Internal use only.

        Contract:
            - Lazily constructs the MutationResearch root on first access
              (deferred out of `__init__` to keep the import-time `Aether()`
              bootstrap off the mutation_research import chain).
            - Double-checked under the singleton lock; exactly one instance
              is ever built per Aether lifetime.
            - A cleaned (but not yet del'd) root still raises, preserving the
              pre-lazy contract: cleanup never silently re-creates the root.

        Returns:
            MutationResearch: The hosted mutation-research singleton.

        Raises:
            RuntimeError: If the Aether or the root has been cleaned.
        """
        self.check_cleaned()
        research = self._mutation_research
        if research is None:
            with self._lock:
                self.check_cleaned()
                research = self._mutation_research
                if research is None:
                    from melder.mutation_research.mutation_research import (
                        MutationResearch,
                    )

                    research = MutationResearch(aether=self)
                    self._mutation_research = research
        if research.cleaned:
            raise RuntimeError("MutationResearch has been cleaned or is unavailable.")
        return research

    #endregion Mutation Research
    #region DevOps Management
    def _get_devops_manager(self, aetheric_frame_name: str = "default") -> DevOpsManager:
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
            frame = self._ensure_default_frame()

        # Validate frame
        if frame is None or frame._cleaned:
            raise RuntimeError(
                f"The AethericFrame '{aetheric_frame_name}' has been cleaned or is unavailable."
            )

        return frame._dev_ops_manager


    def _get_spell_system_states(self, aetheric_frame_name: str = "default") -> SpellSystemStates:
        """
        Retrieves the global SpellSystemStates manager.

        Returns:
            SpellSystemStates: The SpellSystemStates instance.
        """
        self.check_cleaned()
        return self._get_devops_manager(aetheric_frame_name).spell_system_states

    def _get_incident_manager(self, aetheric_frame_name: str = "default") -> IncidentManager:
        """
        Retrieves the IncidentManager from the DevOpsManager of a specific frame.

        Returns:
            IncidentManager: The IncidentManager instance.
        """
        self.check_cleaned()
        return self._get_devops_manager(aetheric_frame_name).incident_manager

    def _get_change_control_manager(self, aetheric_frame_name: str = "default") -> ChangeControlManager:
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
        Trigger revalidation of dirty roots for one conduit through DevOps.

        Contract:
            - Requires a non-empty conduit id.
            - Resolves the frame-specific DevOps manager first.
            - Delegates the actual revalidation to that manager.

        Args:
            conduit_id (str):
                Target conduit id.
            aetheric_frame_name (str):
                Name of the target frame.
            cancel_event:
                Optional cancellation signal passed through to DevOps.

        Returns:
            None.
        """
        self.check_cleaned()
        if not conduit_id:
            raise ValueError("conduit_id cannot be empty.")
        devops = self._get_devops_manager(aetheric_frame_name)
        devops.revalidate_dirty_roots(conduit_id, cancel_event=cancel_event)

    #endregion DevOps Management
