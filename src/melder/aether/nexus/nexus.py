import threading
from typing import Any, Dict, List, Optional, Sequence, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.aetheric_frame_configuration import AethericFrameConfiguration
from melder.aether.nexus.acl.frame_acl_compiler import FrameACLCompiler
from melder.aether.nexus.acl.frame_acl_compiled_access_surface import (
    CompiledFrameACLAccessSurface,
)
from melder.aether.nexus.acl.builder.frame_acl_builder import FrameACLBuilder
from melder.aether.nexus.acl.configurations.frame_acl_command_configuration import (
    FrameACLCommandConfiguration,
)
from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.acl.configurations.frame_acl_codegen_configuration import (
    FrameACLCodegenConfiguration,
)
from melder.aether.nexus.acl.configurations.frame_acl_view_configuration import (
    FrameACLViewConfiguration,
)
from melder.aether.nexus.acl.configurations.profiles.frame_acl_profile import FrameACLProfile
from melder.aether.nexus.frame_descriptor.frame_descriptor import FrameDescriptor
from melder.aether.nexus.frame_acl_manager import FrameACLManager
from melder.aether.nexus.frame_descriptor_manager import FrameDescriptorManager
from melder.aether.nexus.nexus_frame_record import NexusFrameRecord
from melder.aether.nexus.configuration.rift_configuration import RiftConfiguration
from melder.aether.nexus.configuration.nexus_configuration import (
    NexusConfiguration,
)
from melder.aether.nexus.configuration.nexus_frame_mode import (
    NexusFrameMode,
)
from melder.aether.nexus.configuration.rift_space_type import RiftSpaceType
from melder.aether.nexus.rift.frame_viewer.frame_viewer import FrameViewer
from melder.aether.nexus.rift.frame_viewer.profiles.frame_viewer_profile_builder import (
    FrameViewerProfileBuilder,
)
from melder.spellbook.configuration.system_state import SystemState
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.helpers.init_helpers import InitHelpers
from melder.utilities.interfaces.interfaces import (
    IAether,
    IAethericFrame,
    IConfiguration,
    INexus,
    INexusConfiguration,
    IRift,
    IRiftConfiguration,
    ISafeLogger,
)


class Nexus(Cleanable, INexus):
    """
    Purpose:
        Provide the public singleton root for Rift-domain registry,
        configuration, ACL-container access, and Nexus-managed frame policy.

    Contract:
        - `Nexus` is a process-wide singleton.
        - It owns Nexus configuration, configured/enabled state, live Rift
          registries, Rift profile templates, frame-descriptor management, and
          frame-local ACL manager access.
        - It holds the hidden `Aether` substrate reference required for
          Nexus-managed frame realization and disposal.
        - It creates `Rift` objects from policy-approved configuration and
          frame-name assignments.
        - It owns the lifecycle of Nexus-managed internal frames through
          `NexusFrameRecord` objects while leaving actual `AethericFrame`
          ownership to the hidden substrate.

    Lifecycle:
        Created eagerly by `Aether` at package/runtime boot, but starts
        unconfigured and disabled until a caller explicitly enables Rift-domain
        behavior.

    Threading:
        Uses one class-level singleton lock for instance creation and one
        instance `threading.RLock` for multi-step mutable state transitions.
    """

    __melder_internal__ = _mrg.sentinel
    _instance = None
    _singleton_lock = threading.RLock()
    _initialized = False
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_logger",
        "_aether",
        "_configuration",
        "_configured",
        "_enabled",
        "_rifts_by_id",
        "_rift_ids_by_name",
        "_next_default_rift_number",
        "_next_indexed_nexus_frame_number",
        "_rift_profiles_by_name",
        "_frame_acl_manager",
        "_frame_descriptor_manager",
        "_projected_frame_viewers_by_cache_key",
        "_target_frame_ref_counts",
    ]

    def __new__(cls, *args, **kwargs):
        """
        Ensure `Nexus` behaves as a singleton.

        Purpose:
            Return the one process-wide `Nexus` instance regardless of how many
            times the constructor is called.

        Threading:
            Uses the class-level singleton lock to serialize first-instance
            creation.

        Returns:
            Nexus: The one process-wide Nexus instance.
        """
        if cls._instance is None:
            with cls._singleton_lock:
                if cls._instance is None:
                    cls._instance = super(Nexus, cls).__new__(cls)
        return cls._instance

    def __init__(
            self,
            *,
            aether: Optional[IAether] = None,
            configuration: Optional[INexusConfiguration] = None,
            logger: Optional[Any] = None,
    ) -> None:
        """
        Initialize the singleton Rift-domain root.

        Purpose:
            Bind the singleton to the hidden substrate, create its owned
            registries/managers, and optionally install an initial
            configuration.

        Contract:
            - First construction requires a non-None `Aether` substrate.
            - Later constructor calls reuse the existing singleton and may only
              refresh the logger override.
            - Registry, manager, and counter state start empty on first
              initialization.
            - The singleton starts disabled even when configuration is supplied.

        Args:
            aether:
                Hidden owning `Aether` singleton used for Nexus-managed frame
                realization and disposal.
            configuration:
                Optional initial Nexus configuration. When omitted, Nexus starts
                unconfigured and disabled.
            logger:
                Optional logger instance or logger-like object used to override
                the default provider-backed logger.

        Returns:
            None.

        Raises:
            ValueError:
                If first-time initialization is attempted without an `Aether`
                substrate reference.
        """
        if Nexus._initialized:
            if logger is not None:
                self._logger.cleanup()
                self._logger = InitHelpers.resolve_safe_logger(logger)
            return

        if aether is None:
            with Nexus._singleton_lock:
                if Nexus._instance is self and not Nexus._initialized:
                    Nexus._instance = None
                    Nexus._initialized = False
            raise ValueError("Aether must be provided to initialize Nexus.")
        try:
            super().__init__()
            self._id: str = IDBuilder.create_id()
            self._lock: threading.RLock = threading.RLock()
            self._logger: ISafeLogger = InitHelpers.resolve_safe_logger(None)
            self._aether: IAether = aether
            self._configuration: Optional[INexusConfiguration] = configuration
            self._configured: bool = configuration is not None
            self._enabled: bool = False

            self._rifts_by_id: Dict[str, IRift] = {}
            self._rift_ids_by_name: Dict[str, str] = {}
            self._next_default_rift_number: int = 1
            self._next_indexed_nexus_frame_number: int = 1
            self._rift_profiles_by_name: Dict[str, IRiftConfiguration] = {}
            self._frame_acl_manager: Optional[FrameACLManager] = None
            self._frame_descriptor_manager: Optional[FrameDescriptorManager] = None
            self._frame_acl_manager = FrameACLManager(
                change_callback=self._on_frame_acl_changed,
            )
            self._projected_frame_viewers_by_cache_key: Dict[
                Tuple[Tuple[str, ...], Tuple[str, ...], str],
                FrameViewer,
            ] = {}
            self._target_frame_ref_counts: Dict[str, int] = {}

            self._frame_descriptor_manager = FrameDescriptorManager(aether)
            self._initialize_logging(logger)
            Nexus._initialized = True
        except Exception:
            with Nexus._singleton_lock:
                if Nexus._instance is self:
                    Nexus._instance = None
                Nexus._initialized = False
            raise

    def cleanup(self) -> None:
        """
        Idempotently cleanup Nexus-owned state and reset singleton status.

        Purpose:
            Tear down the Rift-domain root, its owned registries/managers, and
            the singleton bookkeeping used for later clean test reinitialization.

        Contract:
            - Safe to call more than once.
            - Cleans registered Rifts, profile templates, installed
              configuration, ACL manager, and descriptor manager before
              dropping references.
            - Resets class-level singleton state after instance teardown
              completes.

        Threading:
            Acquires the instance lock for mutable-state teardown, then the
            class-level singleton lock to reset singleton bookkeeping.

        Returns:
            None.
        """
        if self._cleaned:
            return
        lock = self._lock
        with lock:
            if self._cleaned:
                return
            self._logger.info("Cleaning Nexus singleton state.", "cleanup")
            self._cleaned = True
            for rift in self._rifts_by_id.values():
                rift.cleanup()
            if self._configuration is not None:
                self._configuration.cleanup()
            for profile in self._rift_profiles_by_name.values():
                profile.cleanup()
            if self._frame_acl_manager is not None:
                self._frame_acl_manager.cleanup()
            if self._frame_descriptor_manager is not None:
                self._frame_descriptor_manager.cleanup()
            for projected_frame_viewer in self._projected_frame_viewers_by_cache_key.values():
                projected_frame_viewer.cleanup()
            self._configuration = None
            self._configured = None
            self._enabled = None
            self._aether = None
            self._rifts_by_id.clear()
            self._rift_ids_by_name.clear()
            self._next_default_rift_number = None
            self._next_indexed_nexus_frame_number = None
            self._rift_profiles_by_name.clear()
            self._target_frame_ref_counts.clear()
            self._projected_frame_viewers_by_cache_key.clear()
            self._rifts_by_id = None
            self._rift_ids_by_name = None
            self._next_default_rift_number = None
            self._next_indexed_nexus_frame_number = None
            self._rift_profiles_by_name = None
            self._frame_acl_manager = None
            self._frame_descriptor_manager = None
            self._projected_frame_viewers_by_cache_key = None
            self._target_frame_ref_counts = None
            self._id = None
        if self._logger is not None:
            self._logger.cleanup()
            self._logger = None
        self._lock = None
        with Nexus._singleton_lock:
            Nexus._instance = None
            Nexus._initialized = False

    def _initialize_logging(self, logger: Optional[Any]) -> None:
        """
        Establish the Nexus logger through the hosted utility system.

        Purpose:
            Resolve the logger path used by Nexus lifecycle and registry
            operations.

        Priority:
            1) Explicit logger arg
            2) AetherUtilitySystem channel logger
            3) Silent no-op logger

        Args:
            logger:
                Optional explicit logger override.

        Returns:
            None.
        """
        try:
            if logger is not None:
                self._logger = InitHelpers.resolve_safe_logger(logger)
            else:
                self._logger = InitHelpers.resolve_channel_logger(
                    self,
                    groups=self._get_default_logger_groups(),
                    system_groups=self._get_default_logger_system_groups(),
                    props=self._get_default_logger_properties(),
                    channels="system",
                )
        except Exception as e:
            self._logger = InitHelpers.resolve_safe_logger(None)
            self._logger.error(
                f"Failed to initialize Nexus logger: {e}",
                "_initialize_logging",
                exc_info=True,
            )

    def _get_default_logger_groups(self) -> List[str]:
        """
        Build the default group metadata for the Nexus root logger.

        Purpose:
            Keep the default Nexus logger grouped as a lifecycle/registry root
            instead of leaving the grouping inline in `_initialize_logging()`.

        Contract:
            Returns only stable root-level grouping metadata for the Nexus
            object itself.

        Returns:
            List[str]: Default Nexus logger groups.
        """
        return ["nexus", "lifecycle", "registry"]

    def _get_default_logger_system_groups(self) -> List[str]:
        """
        Build the default system-group metadata for the Nexus root logger.

        Purpose:
            Declare the substrate and runtime domains the Nexus root
            participates in.

        Contract:
            Returns only stable system-level group metadata and does not encode
            mutable runtime flags such as enabled/disabled state.

        Returns:
            List[str]: Default Nexus logger system groups.
        """
        return ["nexus", "aether", "rift"]

    def _get_default_logger_properties(self) -> Dict[str, Any]:
        """
        Build the default property metadata for the Nexus root logger.

        Purpose:
            Attach stable provenance data to the default Nexus logger so Iris
            output can identify the root object consistently.

        Contract:
            - Includes only stable root-object metadata.
            - Avoids mutable runtime state that would drift after logger
              creation.

        Returns:
            Dict[str, Any]: Default Nexus logger property map.
        """
        return {
            "component": "nexus",
            "component_id": self._id,
            "singleton": True,
        }

    @classmethod
    def _reset_singleton_for_tests(cls) -> None:
        """
        Reset the Nexus singleton for test isolation.

        Purpose:
            Provide deterministic singleton teardown for test environments that
            need a clean `Nexus` bootstrap path.

        Contract:
            - Cleans the current singleton instance when one exists.
            - Resets class-level singleton bookkeeping even if cleanup raises
              during teardown.

        Returns:
            None.
        """
        with cls._singleton_lock:
            instance = cls._instance
            if instance is None:
                cls._initialized = False
                return
            try:
                instance.cleanup()
            finally:
                cls._instance = None
                cls._initialized = False

    @property
    def id(self) -> str:
        """
        Purpose:
            Return the stable Nexus identifier.

        Returns:
            str: Stable singleton id.
        """
        self.check_cleaned()
        return self._id

    @property
    def configuration(self) -> INexusConfiguration:
        """
        Purpose:
            Return the installed Nexus configuration.

        Contract:
            Returns the live installed configuration object, not a detached
            copy.

        Returns:
            INexusConfiguration: Installed process-wide config.

        Raises:
            RuntimeError: If Nexus has not been configured yet.
        """
        self._require_configured()
        return self._configuration

    @property
    def is_configured(self) -> bool:
        """
        Purpose:
            Return whether Nexus currently has an installed configuration.

        Returns:
            bool: True when configured.
        """
        self.check_cleaned()
        return self._configured

    @property
    def is_enabled(self) -> bool:
        """
        Purpose:
            Return whether Nexus is currently enabled for Rift operations.

        Returns:
            bool: True when enabled.
        """
        self.check_cleaned()
        return self._enabled

    def create_system_configuration(self) -> INexusConfiguration:
        """
        Create a fresh mutable Nexus configuration with default values.

        Purpose:
            Provide callers with a mutable process-level Nexus configuration
            seeded with repo defaults.

        Contract:
            - Returns a new `NexusConfiguration` instance on each call.
            - Applies the default property set before returning it.
            - Does not install the configuration onto Nexus automatically.

        Returns:
            INexusConfiguration: Fresh mutable Nexus config.
        """
        self.check_cleaned()
        return NexusConfiguration().with_defaults()

    def enable(
            self,
            configuration: Optional[INexusConfiguration] = None,
    ) -> None:
        """
        Install configuration if needed and enable Nexus operations.

        Purpose:
            Transition Nexus into its enabled state for Rift-domain operations.

        Contract:
            - Optionally replaces the installed configuration before enabling.
            - Finalizes the installed configuration before setting enabled.
            - Does not create a default configuration automatically when none
              is installed.

        Args:
            configuration:
                Optional replacement configuration.

        Returns:
            None.

        Raises:
            RuntimeError:
                If Nexus has no installed configuration.
        """
        self.check_cleaned()
        with self._lock:
            if configuration is not None:
                self._configuration = configuration
                self._configured = True
            self._require_configured()
            if not self._configuration.frozen:
                self._configuration.finalize()
            self._enabled = True
            self._logger.info("Nexus enabled.", "enable")

    def disable(self) -> None:
        """
        Disable Rift operations without discarding configuration or registry
        state.

        Purpose:
            Turn off Rift-domain operation entrypoints while preserving the
            installed configuration and current registries.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._enabled = False
            self._logger.info("Nexus disabled.", "disable")

    def create_rift_configuration(
            self,
            profile_name: Optional[str] = None,
    ) -> IRiftConfiguration:
        """
        Create a per-Rift configuration initialized from Nexus defaults.

        Purpose:
            Produce a mutable `RiftConfiguration` for a future Rift creation
            flow.

        Contract:
            - Requires Nexus to be configured.
            - When `profile_name` is supplied, clones the stored profile
              template instead of returning it directly.
            - When `profile_name` is omitted, seeds a fresh configuration from
              installed Nexus defaults.
            - Produces a bare Rift configuration: room identity/mode and
              validation posture only. It does not select a target frame.

        Args:
            profile_name:
                Optional registered profile name. When supplied, the returned
                configuration is cloned from the stored profile template.

        Returns:
            IRiftConfiguration: Mutable per-Rift configuration.

        Raises:
            RuntimeError:
                If Nexus is not configured.
            ValueError:
                If `profile_name` is unknown.
        """
        self._require_configured()
        if profile_name is not None:
            with self._lock:
                try:
                    template = self._rift_profiles_by_name[profile_name]
                except KeyError as exc:
                    raise ValueError("Rift profile '{0}' was not found.".format(profile_name)) from exc
            return self._clone_rift_configuration(template)

        configuration = RiftConfiguration().with_defaults()
        configuration.with_space_type(self._configuration.get_property("default_space_type"))
        configuration.with_auto_activate_on_program(self._configuration.get_property("default_auto_activate_on_program"))
        configuration.with_validation_mode(self._configuration.get_property("default_validation_mode"))
        return configuration

    def register_rift_profile(
            self,
            name: str,
            configuration: IRiftConfiguration,
    ) -> None:
        """
        Internal

        Register one named Rift configuration profile template on Nexus.

        Args:
            name:
                Stable profile name.
            configuration:
                Rift configuration to store as the profile template source.

        Contract:
            - Stores a frozen cloned template, not the original configuration
              object.
            - Replaces any existing template with the same name.

        Returns:
            None.

        Raises:
            ValueError: If `name` is empty.
        """
        self.check_cleaned()
        if not name:
            raise ValueError("Rift profile name cannot be empty.")
        template = self._clone_rift_configuration(configuration)
        template.finalize()
        with self._lock:
            existing_profile = self._rift_profiles_by_name.get(name)
            if existing_profile is not None:
                existing_profile.cleanup()
            self._rift_profiles_by_name[name] = template

    def create_rift(
            self,
            *,
            configuration: Optional[IRiftConfiguration] = None,
            rift_name: Optional[str] = None,
            rift_id: Optional[str] = None,
            space_id: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
            creation_token: Optional[str] = None,
            logger: Optional[Any] = None,
    ) -> IRift:
        """
        Internal

        Create and register one live Rift object.

        Contract:
            - Enforces the current Rift-creation gate before any object
              creation begins.
            - Finalizes the per-Rift configuration when needed and marks it
              consumed after successful registration.
            - Allocates default Rift and Nexus-frame names when callers do not
              supply them.
            - Creates the primary concrete space from the configured
              `space_type`.
            - Does not select or validate a target frame during bare Rift
              creation.
            - Registers the created Rift through `add_rift(...)` before
              returning it.

        Args:
            configuration:
                Optional per-Rift configuration override.
            rift_name:
                Optional stable Rift name.
            rift_id:
                Optional explicit Rift id.
            space_id:
                Optional explicit primary-space id to seed on the Rift.
            metadata:
                Optional Rift-level metadata.
            creation_token:
                Optional creation token when creation is token-gated.
            logger:
                Optional explicit logger override passed through to the created
                Rift.

        Returns:
            IRift: Newly created and registered live Rift.
        """
        self._require_rift_creation_allowed(creation_token)
        from melder.aether.nexus.rift.rift import Rift

        canonical_rift_id = rift_id or IDBuilder.create_id()
        bound_configuration = configuration or self.create_rift_configuration()
        if bound_configuration.consumed:
            raise ValueError("RiftConfiguration has already been consumed.")
        if not bound_configuration.frozen:
            bound_configuration.finalize()

        with self._lock:
            canonical_rift_name = rift_name or self._allocate_default_rift_name()
            rift = Rift(
                self,
                configuration=bound_configuration,
                rift_name=canonical_rift_name,
                rift_id=canonical_rift_id,
                space_id=space_id,
                metadata=metadata,
                logger=logger,
            )
            if bound_configuration.get_property("auto_activate_on_program"):
                rift.mark_active()
            self.add_rift(rift)
            bound_configuration.mark_consumed()
            self._logger.info(
                "Created Rift '{0}' (id={1}).".format(rift.rift_name, rift.id),
                "create_rift",
            )
            return rift

    def add_rift(self, rift: IRift) -> None:
        """
        Internal

        Register one already-constructed Rift into Nexus.

        Contract:
            - Rejects id/name collisions.
            - Validates target-frame, Nexus-frame, and active-Rift budgets
              before mutating registries.
            - Updates the id/name registries, target-frame ref counts, and
              Nexus-frame attachments as one Nexus-owned registration flow.

        Args:
            rift:
                Live Rift object.

        Returns:
            None.

        Raises:
            ValueError: If ids/names collide or frame budgets are exceeded.
        """
        self._require_enabled()
        with self._lock:
            if rift.id in self._rifts_by_id:
                raise ValueError("Rift with id '{0}' already exists.".format(rift.id))
            if rift.rift_name and rift.rift_name in self._rift_ids_by_name:
                raise ValueError("Rift name '{0}' already exists.".format(rift.rift_name))

            self._validate_target_frame_budget(rift.list_assigned_frame_names())
            self._validate_active_rift_budget()

            self._rifts_by_id[rift.id] = rift
            if rift.rift_name:
                self._rift_ids_by_name[rift.rift_name] = rift.id
            for target_frame_name in rift.list_assigned_frame_names():
                self._increment_ref_count(self._target_frame_ref_counts, target_frame_name)
            rift.mark_registered()

    def get_rift(
            self,
            rift_id: str,
            access_token: Optional[str] = None,
    ) -> IRift:
        """
        Internal

        Return a registered Rift by id.

        Args:
            rift_id:
                Canonical Rift id.
            access_token:
                Optional direct-access token.

        Contract:
            - Applies the current direct-Rift access gate before lookup.
            - Returns the live registered Rift object, not a detached copy.

        Returns:
            IRift: Registered Rift object.
        """
        self._require_rift_access_allowed(access_token)
        try:
            return self._rifts_by_id[rift_id]
        except KeyError as exc:
            raise ValueError("Rift with id '{0}' was not found.".format(rift_id)) from exc

    def get_rift_by_name(
            self,
            rift_name: str,
            access_token: Optional[str] = None,
    ) -> IRift:
        """
        Internal

        Resolve one registered Rift through the name -> id index.

        Args:
            rift_name:
                Stable Rift name.
            access_token:
                Optional direct-access token.

        Contract:
            - Applies the current direct-Rift access gate before lookup.
            - Resolves through the name-to-id index and then returns the same
              live object exposed by `get_rift(...)`.

        Returns:
            IRift: Registered Rift object.
        """
        self._require_rift_access_allowed(access_token)
        try:
            rift_id = self._rift_ids_by_name[rift_name]
        except KeyError as exc:
            raise ValueError("Rift with name '{0}' was not found.".format(rift_name)) from exc
        return self.get_rift(rift_id, access_token=access_token)

    def has_rift(self, rift_id: str) -> bool:
        """
        Internal

        Return whether a Rift id is currently registered.

        Args:
            rift_id:
                Canonical Rift id.

        Contract:
            Performs a registry existence check only; it does not apply the
            direct-access gate or materialize any Rift object.

        Returns:
            bool: True when registered.
        """
        self._require_configured()
        return rift_id in self._rifts_by_id

    def remove_rift(self, rift_id: str) -> None:
        """
        Internal

        Remove one Rift from Nexus and update frame lifecycle state.

        Contract:
            - Removes the Rift from Nexus registries under the Nexus lock.
            - Decrements target-frame ref counts and detaches the Rift from its
              Nexus-managed frames as part of registry teardown.
            - Disposes orphaned Nexus-managed frames only after the locked
              registry mutation phase completes.
            - Cleans the removed Rift before returning.

        Args:
            rift_id:
                Canonical Rift id.

        Returns:
            None.
        """
        self._require_enabled()
        frame_names_to_cleanup: List[str] = []
        rift_name: Optional[str] = None
        with self._lock:
            try:
                rift = self._rifts_by_id.pop(rift_id)
            except KeyError as exc:
                raise ValueError("Rift with id '{0}' was not found.".format(rift_id)) from exc

            rift_name = rift.rift_name
            if rift.rift_name:
                self._rift_ids_by_name.pop(rift.rift_name, None)
            for target_frame_name in rift.list_assigned_frame_names():
                self._decrement_ref_count(self._target_frame_ref_counts, target_frame_name)
            frame_names_to_cleanup.extend(self._detach_rift_from_nexus_frames(rift.id))

        for frame_name in frame_names_to_cleanup:
            self._dispose_nexus_frame(frame_name)
        rift.cleanup()
        self._logger.info(
            "Removed Rift '{0}' (id={1}).".format(rift_name, rift_id),
            "remove_rift",
        )

    def _refresh_frame_posture_cache(
            self,
            frame_name: str,
    ) -> Optional[AethericFrameConfiguration]:
        """
        Internal

        Refresh the cached frame posture for one frame from Aether.

        Args:
            frame_name:
                Target frame name.

        Returns:
            Optional[AethericFrameConfiguration]: Bound frame posture when
            available, otherwise None.
        """
        frame_posture = self._frame_descriptor_manager._refresh_frame_posture_cache(frame_name)
        if self._frame_descriptor_manager._has_frame_descriptor(frame_name):
            self._ensure_frame_acl_container(frame_name)
        return frame_posture

    def _get_publishable_frame_posture(
            self,
            frame_name: str,
    ) -> Optional[AethericFrameConfiguration]:
        """
        Internal

        Return the cached publishable frame posture when the frame may publish
        passive Nexus records.

        Args:
            frame_name:
                Target frame name.

        Returns:
            Optional[AethericFrameConfiguration]: Publishable frame posture or
            None when publication should short-circuit.
        """
        frame_posture = self._frame_descriptor_manager._get_publishable_frame_posture(frame_name)
        if self._frame_descriptor_manager._has_frame_descriptor(frame_name):
            self._ensure_frame_acl_container(frame_name)
        return frame_posture

    def _publish_frame_record(self, spellbook: Any) -> bool:
        """
        Internal

        Publish one canonical frame record for a Spellbook's frame.

        Args:
            spellbook:
                Spellbook whose frame posture should be published.

        Returns:
            bool: True when the record was published, False when publication
            short-circuited.
        """
        published = self._frame_descriptor_manager._publish_frame_record(spellbook)
        if self._frame_descriptor_manager._has_frame_descriptor(spellbook._aetheric_frame):
            self._ensure_frame_acl_container(spellbook._aetheric_frame)
            self._invalidate_projected_frame_viewers(spellbook._aetheric_frame)
        return published

    def _publish_conduit_record(self, conduit: Any) -> bool:
        """
        Internal

        Publish or update one canonical conduit record for a normal/root
        conduit.

        Args:
            conduit:
                Conduit instance to publish.

        Returns:
            bool: True when the record was published, False when publication
            short-circuited.
        """
        published = self._frame_descriptor_manager._publish_conduit_record(conduit)
        if self._frame_descriptor_manager._has_frame_descriptor(conduit._aetheric_frame):
            self._ensure_frame_acl_container(conduit._aetheric_frame)
            self._invalidate_projected_frame_viewers(conduit._aetheric_frame)
        return published

    def _remove_conduit_record(
            self,
            conduit_id: str,
            frame_name: str,
    ) -> bool:
        """
        Internal

        Remove one canonical conduit record when the frame remains publishable.

        Args:
            conduit_id:
                Conduit id to remove.
            frame_name:
                Owning frame name.

        Returns:
            bool: True when the remove path executed, False when publication
            short-circuited.
        """
        removed = self._frame_descriptor_manager._remove_conduit_record(
            conduit_id,
            frame_name,
        )
        if self._frame_descriptor_manager._has_frame_descriptor(frame_name):
            self._ensure_frame_acl_container(frame_name)
            self._invalidate_projected_frame_viewers(frame_name)
        return removed

    def _publish_spell_record(
            self,
            spellbook: Any,
            spell: Any,
            owner_conduit_id: Optional[str],
    ) -> bool:
        """
        Internal

        Publish or update one canonical spell record.

        Args:
            spellbook:
                Owning Spellbook.
            spell:
                Spell instance to publish.
            owner_conduit_id:
                Owning conduit id when known.

        Returns:
            bool: True when the record was published, False when publication
            short-circuited.
        """
        published = self._frame_descriptor_manager._publish_spell_record(
            spellbook,
            spell,
            owner_conduit_id,
        )
        if self._frame_descriptor_manager._has_frame_descriptor(spellbook._aetheric_frame):
            self._ensure_frame_acl_container(spellbook._aetheric_frame)
            self._invalidate_projected_frame_viewers(spellbook._aetheric_frame)
        return published

    def _remove_spell_record(
            self,
            origin_spellbook_id: str,
            spell_id: str,
            frame_name: str,
    ) -> bool:
        """
        Internal

        Remove one canonical spell record by its composite storage key.

        Args:
            origin_spellbook_id:
                Owning Spellbook id.
            spell_id:
                Current spell/version id.
            frame_name:
                Owning frame name.

        Returns:
            bool: True when the remove path executed, False when publication
            short-circuited.
        """
        removed = self._frame_descriptor_manager._remove_spell_record(
            origin_spellbook_id,
            spell_id,
            frame_name,
        )
        if self._frame_descriptor_manager._has_frame_descriptor(frame_name):
            self._ensure_frame_acl_container(frame_name)
            self._invalidate_projected_frame_viewers(frame_name)
        return removed

    def list_rift_ids(self) -> list[str]:
        """
        Return the currently registered Rift ids.

        Purpose:
            Expose the current live Rift registry contents at the id level.

        Contract:
            Requires Nexus to be enabled before callers may inspect the live
            Rift registry.

        Returns:
            list[str]: Snapshot of registered ids.
        """
        self._require_enabled()
        return list(self._rifts_by_id.keys())

    def get_frame_acl_version(self) -> str:
        """
        Return the current placeholder ACL manager version string.

        Contract:
            Returns the version reported by the live Nexus-owned
            `FrameACLManager`.

        Returns:
            str: Current ACL manager version.
        """
        self.check_cleaned()
        return self._frame_acl_manager.version

    def register_frame_acl_profile(
            self,
            frame_acl_profile: FrameACLProfile,
    ) -> None:
        """
        Register or replace one named ACL profile on the Nexus-owned manager.

        Args:
            frame_acl_profile:
                Profile object to store by its own name.

        Contract:
            Delegates registration to the Nexus-owned ACL manager and replaces
            any existing distinct profile with the same name.

        Returns:
            None.
        """
        self.check_cleaned()
        self._frame_acl_manager._register_frame_acl_profile(frame_acl_profile)

    def get_frame_acl_profile(self, profile_name: str) -> FrameACLProfile:
        """
        Return one registered ACL profile by name.

        Args:
            profile_name:
                Profile name to resolve.

        Contract:
            Resolves through the Nexus-owned ACL manager without synthesizing a
            missing profile.

        Returns:
            FrameACLProfile: Existing stored profile.

        Raises:
            KeyError: If the profile is not registered.
        """
        self.check_cleaned()
        return self._frame_acl_manager._get_required_frame_acl_profile(profile_name)

    def list_frame_acl_profile_names(self) -> List[str]:
        """
        Return the current ACL profile names in insertion order.

        Contract:
            Returns a snapshot list from the Nexus-owned ACL manager's composed
            profile registry.

        Returns:
            List[str]: Current profile names.
        """
        self.check_cleaned()
        return self._frame_acl_manager._list_frame_acl_profile_names()

    def remove_frame_acl_profile(self, profile_name: str) -> bool:
        """
        Remove and cleanup one registered ACL profile by name.

        Args:
            profile_name:
                Profile name to remove.

        Contract:
            Delegates removal to the Nexus-owned ACL manager and returns False
            when the profile name is not currently registered.

        Returns:
            bool: True when the profile existed and was removed.
        """
        self.check_cleaned()
        return self._frame_acl_manager._remove_frame_acl_profile(profile_name)

    def get_frame_acl_builder(self, frame_name: str) -> FrameACLBuilder:
        """
        Return the unique frame ACL builder object for one frame.

        Purpose:
            Provide the root-level entrypoint for frame-scoped ACL authoring.

        Contract:
            - Ensures the matching frame ACL container exists before builder
              lookup.
            - Returns the same builder object for repeated calls against the
              same frame.

        Args:
            frame_name:
                Stable frame name whose ACL builder should be returned.

        Returns:
            FrameACLBuilder:
                The one builder object owned by the frame's ACL container.
        """
        self.check_cleaned()
        self._ensure_frame_acl_container(frame_name)
        return self._frame_acl_manager._get_or_create_frame_acl_builder(frame_name)

    def get_current_frame_acl_configuration(
            self,
            frame_name: str,
            *,
            view_contract_name: str = "default",
            command_contract_name: str = "default",
            codegen_contract_name: str = "default",
    ) -> FrameACLConfiguration:
        """
        Return the current selected frame ACL configuration for one frame.

        Purpose:
            Expose the currently selected ACL configuration for a frame through
            the Nexus facade.

        Args:
            frame_name:
                Stable frame name whose current ACL configuration is requested.
            view_contract_name:
                Selected view ACL contract name.
            command_contract_name:
                Selected command ACL contract name.
            codegen_contract_name:
                Selected codegen ACL contract name.

        Returns:
            FrameACLConfiguration:
                The currently selected ACL configuration for the frame.
        """
        self.check_cleaned()
        self._ensure_frame_acl_container(frame_name)
        return self._frame_acl_manager._get_current_frame_acl_configuration(
            frame_name,
            view_contract_name=view_contract_name,
            command_contract_name=command_contract_name,
            codegen_contract_name=codegen_contract_name,
        )

    def get_current_view_frame_acl_configuration(
            self,
            frame_name: str,
            *,
            contract_name: str = "default",
    ) -> FrameACLViewConfiguration:
        """
        Return the current selected view ACL configuration for one frame/contract.

        Returns:
            FrameACLViewConfiguration: Current view configuration.
        """
        self.check_cleaned()
        self._ensure_frame_acl_container(frame_name)
        return self._frame_acl_manager._get_current_view_frame_acl_configuration(
            frame_name,
            contract_name=contract_name,
        )

    def get_current_command_frame_acl_configuration(
            self,
            frame_name: str,
            *,
            contract_name: str = "default",
    ) -> FrameACLCommandConfiguration:
        """
        Return the current selected command ACL configuration for one frame/contract.

        Returns:
            FrameACLCommandConfiguration: Current command configuration.
        """
        self.check_cleaned()
        self._ensure_frame_acl_container(frame_name)
        return self._frame_acl_manager._get_current_command_frame_acl_configuration(
            frame_name,
            contract_name=contract_name,
        )

    def get_current_codegen_frame_acl_configuration(
            self,
            frame_name: str,
            *,
            contract_name: str = "default",
    ) -> FrameACLCodegenConfiguration:
        """
        Return the current selected codegen ACL configuration for one frame/contract.

        Returns:
            FrameACLCodegenConfiguration: Current codegen configuration.
        """
        self.check_cleaned()
        self._ensure_frame_acl_container(frame_name)
        return self._frame_acl_manager._get_current_codegen_frame_acl_configuration(
            frame_name,
            contract_name=contract_name,
        )

    def get_named_frame_acl_configuration(
            self,
            frame_name: str,
            contract_name: str = "default",
    ) -> FrameACLConfiguration:
        """
        Return one named frame ACL configuration for a frame.

        Purpose:
            Expose the per-frame named ACL contract registry through the Nexus
            facade.

        Args:
            frame_name:
                Stable frame name whose named ACL contract is requested.
            contract_name:
                Frame-local contract name to resolve.

        Returns:
            FrameACLConfiguration:
                Named ACL configuration for the frame.
        """
        self.check_cleaned()
        self._ensure_frame_acl_container(frame_name)
        return self._frame_acl_manager._get_named_frame_acl_configuration(
            frame_name,
            contract_name=contract_name,
        )

    def list_named_frame_acl_configuration_names(
            self,
            frame_name: str,
    ) -> List[str]:
        """
        Return all named ACL contract names for a frame.

        Purpose:
            Expose the frame-local named ACL registry keys through the Nexus
            facade.

        Args:
            frame_name:
                Stable frame name whose contract names are requested.

        Returns:
            List[str]:
                Registered ACL contract names for the frame.
        """
        self.check_cleaned()
        self._ensure_frame_acl_container(frame_name)
        return self._frame_acl_manager._list_named_frame_acl_configuration_names(
            frame_name
        )

    def register_named_frame_acl_configuration(
            self,
            frame_name: str,
            configuration: FrameACLConfiguration,
            *,
            contract_name: str = "default",
    ) -> FrameACLConfiguration:
        """
        Register one named ACL configuration for a frame.

        Purpose:
            Add a new frame-local named ACL contract through the Nexus facade.

        Args:
            frame_name:
                Stable frame name that owns the contract registry.
            configuration:
                Locked ACL configuration node to register.
            contract_name:
                Frame-local contract name.

        Returns:
            FrameACLConfiguration:
                Registered named configuration node.
        """
        self.check_cleaned()
        self._ensure_frame_acl_container(frame_name)
        registered_configuration = self._frame_acl_manager._register_named_frame_acl_configuration(
            frame_name,
            configuration,
            contract_name=contract_name,
        )
        return registered_configuration

    def insert_head_frame_acl_configuration(
            self,
            frame_name: str,
            configuration: FrameACLConfiguration,
            *,
            select_as_current: bool = True,
    ) -> FrameACLConfiguration:
        """
        Install one same-name ACL bundle revision across the three families.

        Purpose:
            Install a locked ACL bundle into the same named view, command, and
            codegen chains through the Nexus facade.

        Args:
            frame_name:
                Stable frame name that owns the ACL registry.
            configuration:
                Locked configuration node to install.
            select_as_current:
                Ignored. Bundle-chain current/head separation no longer exists
                as a primary storage model.

        Returns:
            FrameACLConfiguration:
                Installed assembled configuration snapshot.

        Raises:
            TypeError, ValueError:
                Propagated when validation fails or family-chain install rejects
                the bundle.
        """
        self.check_cleaned()
        self._ensure_frame_acl_container(frame_name)
        inserted_configuration = self._frame_acl_manager._install_named_frame_acl_configuration(
            frame_name,
            configuration,
            contract_name="default",
        )
        return inserted_configuration

    def create_frame_viewer(
            self,
            frame_names: Sequence[str],
            *,
            contract_names_by_frame_name: Optional[Dict[str, str]] = None,
            view_profile_name: str = "general",
            viewer_profile_name: str = "general",
    ) -> FrameViewer:
        """
        Build one projected `FrameViewer` from one or more frame names.

        Purpose:
            Provide a thin Nexus facade that assembles projected frame views
            into one consumer-facing `FrameViewer`.

        Contract:
            - Every frame name is projected independently from descriptor truth
              plus compiled ACL output.
            - The returned viewer is detached and not cached by Nexus.

        Args:
            frame_names:
                Frame names to project into the viewer.
            contract_names_by_frame_name:
                Optional per-frame selected ACL contract names. Each frame may
                provide either one same-name string or a dict keyed by `view`,
                `command`, and `codegen`.
            view_profile_name:
                View profile name applied to each projected view.
            viewer_profile_name:
                Viewer profile name applied to the projected viewer.

        Returns:
            FrameViewer:
                Derived projected frame viewer.
        """
        self.check_cleaned()
        if isinstance(frame_names, str) or not isinstance(frame_names, Sequence):
            raise TypeError("frame_names must be a sequence.")
        for frame_name in frame_names:
            if not isinstance(frame_name, str) or not frame_name:
                raise ValueError("frame_names must contain non-empty strings.")
        normalized_contract_names_by_frame_name: Dict[str, Dict[str, str]] = {}
        for frame_name in frame_names:
            normalized_contract_names_by_frame_name[frame_name] = {
                "view": "default",
                "command": "default",
                "codegen": "default",
            }
        if contract_names_by_frame_name is not None:
            if not isinstance(contract_names_by_frame_name, dict):
                raise TypeError(
                    "contract_names_by_frame_name must be a dict when provided."
                )
            for frame_name, contract_name in contract_names_by_frame_name.items():
                if frame_name not in normalized_contract_names_by_frame_name:
                    raise ValueError(
                        "contract_names_by_frame_name contains unknown frame '{0}'.".format(
                            frame_name
                        )
                    )
                normalized_contract_names_by_frame_name[frame_name] = (
                    self._normalize_acl_selection_input(contract_name)
                )
        viewer_profile_builder = FrameViewerProfileBuilder()
        viewer_profile = viewer_profile_builder.get_required_profile(
            viewer_profile_name
        )
        active_profiles_by_name = {
            profile_name: viewer_profile_builder.get_required_profile(profile_name).clone()
            for profile_name in viewer_profile_builder.list_profile_names()
        }
        frame_descriptors_by_name: Dict[str, FrameDescriptor] = {}
        frame_acl_configurations_by_frame_name: Dict[str, FrameACLConfiguration] = {}
        compiled_access_surfaces_by_frame_name: Dict[
            str,
            CompiledFrameACLAccessSurface,
        ] = {}
        compiler = FrameACLCompiler(self._frame_acl_manager.frame_acl_profile_builder)
        try:
            for frame_name in frame_names:
                descriptor = self._get_required_frame_descriptor(frame_name)
                contract_selection = normalized_contract_names_by_frame_name[frame_name]
                configuration = self._frame_acl_manager._get_current_frame_acl_configuration(
                    frame_name,
                    view_contract_name=contract_selection["view"],
                    command_contract_name=contract_selection["command"],
                    codegen_contract_name=contract_selection["codegen"],
                )
                self._frame_acl_manager._validate_frame_acl_configuration_against_descriptor(
                    frame_name,
                    configuration,
                    descriptor,
                )
                compiled_access_surfaces_by_frame_name[frame_name] = (
                    compiler.compile_frame_access_surface(
                        descriptor,
                        configuration,
                    )
                )
                frame_descriptors_by_name[frame_name] = descriptor
                frame_acl_configurations_by_frame_name[frame_name] = configuration
            return FrameViewer(
                profile_builder=FrameViewerProfileBuilder(),
                active_profiles_by_name=active_profiles_by_name,
                frame_descriptors_by_name=frame_descriptors_by_name,
                frame_acl_configurations_by_frame_name=(
                    frame_acl_configurations_by_frame_name
                ),
                compiled_access_surfaces_by_frame_name=(
                    compiled_access_surfaces_by_frame_name
                ),
                default_profile_name=viewer_profile.name,
                selected_profile_names_by_frame_name={
                    frame_name: viewer_profile.name
                    for frame_name in frame_descriptors_by_name.keys()
                },
                metadata={
                    "frame_count": len(frame_descriptors_by_name),
                    "available_view_count": len(frame_descriptors_by_name),
                    "assigned_frame_names": tuple(frame_names),
                    "acl_selection_by_frame_name": {
                        frame_name: dict(contract_selection)
                        for frame_name, contract_selection in (
                            normalized_contract_names_by_frame_name.items()
                        )
                    },
                    "contract_names_by_frame_name": {
                        frame_name: dict(contract_selection)
                        for frame_name, contract_selection in (
                            normalized_contract_names_by_frame_name.items()
                        )
                    },
                    "view_profile_name": view_profile_name,
                    "viewer_profile_name": viewer_profile.name,
                    "viewer_profile_version": viewer_profile.version,
                    "default_grouping": viewer_profile.default_grouping,
                    "default_detail_level": viewer_profile.default_detail_level,
                    "enabled_helpers": viewer_profile.enabled_helpers,
                    "tool_names": viewer_profile.list_tool_names(),
                    "tool_handler_names_by_name": viewer_profile.tool_handler_names_by_name,
                },
            )
        finally:
            compiler.cleanup()
            viewer_profile_builder.cleanup()

    def create_frame_viewer_for_rift(
            self,
            rift_id: str,
            *,
            view_profile_name: str = "general",
            viewer_profile_name: str = "general",
    ) -> FrameViewer:
        """
        Build one projected `FrameViewer` from a Rift's assigned target frames.

        Contract:
            - Resolves the live Rift first and projects its currently assigned
              target frames through `create_frame_viewer(...)`.
            - Enriches the returned viewer metadata with Rift-specific
              identifiers and assigned-frame information.
            - Derives a default view frame only when the Rift currently has
              exactly one assigned target frame.

        Args:
            rift_id:
                Existing Rift id whose assigned target frames should populate
                the viewer.
            view_profile_name:
                View profile name applied to each projected frame view.
            viewer_profile_name:
                Viewer profile name applied to the hosted viewer.

        Returns:
            FrameViewer: Projected viewer populated from the Rift assignment
            chain.
        """
        self.check_cleaned()
        if not rift_id:
            raise ValueError("rift_id cannot be empty.")
        rift = self._get_required_rift(rift_id)
        assigned_frame_names = rift.list_assigned_frame_names()
        contract_names_by_frame_name = {
            frame_name: rift.get_selected_contract_names(frame_name)
            for frame_name in assigned_frame_names
        }
        frame_viewer = self.create_frame_viewer(
            assigned_frame_names,
            contract_names_by_frame_name=contract_names_by_frame_name,
            view_profile_name=view_profile_name,
            viewer_profile_name=viewer_profile_name,
        )
        current_metadata = frame_viewer.metadata
        current_metadata["rift_id"] = rift.id
        current_metadata["frame_link_contract_ids_by_frame_name"] = {
            frame_name: rift.get_frame_link_contract(frame_name).contract_id
            for frame_name in assigned_frame_names
        }
        current_metadata["assigned_frame_names"] = assigned_frame_names
        current_metadata["selected_contract_names_by_frame_name"] = (
            contract_names_by_frame_name
        )
        default_view_frame_name = None
        if len(assigned_frame_names) == 1:
            default_view_frame_name = assigned_frame_names[0]
        return FrameViewer(
            profile_builder=FrameViewerProfileBuilder(),
            active_profiles_by_name={
                profile_name: frame_viewer_profile.clone()
                for profile_name, frame_viewer_profile in (
                    frame_viewer.active_profiles_by_name.items()
                )
            },
            default_profile_name=frame_viewer.profile_name,
            frame_descriptors_by_name=frame_viewer.frame_descriptors_by_name,
            frame_acl_configurations_by_frame_name=(
                frame_viewer.frame_acl_configurations_by_frame_name
            ),
            compiled_access_surfaces_by_frame_name=(
                frame_viewer.compiled_access_surfaces_by_frame_name
            ),
            default_view_frame_name=default_view_frame_name,
            metadata=current_metadata,
        )

    def create_frame_viewer_for_rift_frame(
            self,
            rift_id: str,
            frame_name: str,
            *,
            viewer_profile_name: str = "general",
    ) -> FrameViewer:
        """
        Build one frame-specific viewer transaction for a Rift.

        Args:
            rift_id:
                Existing Rift id.
            frame_name:
                Target frame name already available to the Rift contract.
            viewer_profile_name:
                Viewer profile name selected for the target frame.

        Returns:
            FrameViewer: Frame-scoped viewer for the requested frame.
        """
        self.check_cleaned()
        if not rift_id:
            raise ValueError("rift_id cannot be empty.")
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        rift = self._get_required_rift(rift_id)
        frame_link_contract = rift.get_frame_link_contract(frame_name)
        frame_viewer = self.create_frame_viewer(
            [frame_name],
            contract_names_by_frame_name={
                frame_name: frame_link_contract.get_selected_contract_names()
            },
            viewer_profile_name=viewer_profile_name,
        )
        current_metadata = frame_viewer.metadata
        current_metadata["rift_id"] = rift.id
        current_metadata["frame_link_contract_id"] = frame_link_contract.contract_id
        current_metadata["assigned_frame_names"] = (frame_name,)
        current_metadata["selected_contract_names_by_frame_name"] = {
            frame_name: frame_link_contract.get_selected_contract_names()
        }
        return FrameViewer(
            profile_builder=FrameViewerProfileBuilder(),
            active_profiles_by_name={
                profile_key: frame_viewer_profile.clone()
                for profile_key, frame_viewer_profile in (
                    frame_viewer.active_profiles_by_name.items()
                )
            },
            default_profile_name=frame_viewer.profile_name,
            frame_descriptors_by_name=frame_viewer.frame_descriptors_by_name,
            frame_acl_configurations_by_frame_name=(
                frame_viewer.frame_acl_configurations_by_frame_name
            ),
            compiled_access_surfaces_by_frame_name=(
                frame_viewer.compiled_access_surfaces_by_frame_name
            ),
            selected_profile_names_by_frame_name={frame_name: viewer_profile_name},
            default_view_frame_name=frame_name,
            metadata=current_metadata,
        )

    def create_cached_frame_viewer(
            self,
            frame_names: Sequence[str],
            *,
            contract_names_by_frame_name: Optional[Dict[str, str]] = None,
            view_profile_name: str = "general",
            viewer_profile_name: str = "general",
    ) -> FrameViewer:
        """
        Build or reuse one cached projected `FrameViewer`.

        Purpose:
            Avoid rebuilding the same projected multi-frame viewer when the
            underlying frame-view cache inputs have not changed.

        Args:
            frame_names:
                Frame names to project into the viewer.
            contract_names_by_frame_name:
                Optional per-frame selected ACL contract names. Each frame may
                provide either one same-name string or a dict keyed by `view`,
                `command`, and `codegen`.
            view_profile_name:
                View profile name applied to each projected view.
            viewer_profile_name:
                Viewer profile name applied to the projected viewer.

        Returns:
            FrameViewer: Detached projected frame viewer.
        """
        self.check_cleaned()
        if isinstance(frame_names, str) or not isinstance(frame_names, Sequence):
            raise TypeError("frame_names must be a sequence.")
        normalized_frame_names: List[str] = []
        frame_configuration_ids: List[str] = []
        normalized_contract_names_by_frame_name: Dict[str, Dict[str, str]] = {}
        for frame_name in frame_names:
            if not isinstance(frame_name, str) or not frame_name:
                raise ValueError("frame_names must contain non-empty strings.")
            normalized_frame_names.append(frame_name)
            normalized_contract_names_by_frame_name[frame_name] = {
                "view": "default",
                "command": "default",
                "codegen": "default",
            }
        if contract_names_by_frame_name is not None:
            if not isinstance(contract_names_by_frame_name, dict):
                raise TypeError(
                    "contract_names_by_frame_name must be a dict when provided."
                )
            for frame_name, contract_name in contract_names_by_frame_name.items():
                if frame_name not in normalized_contract_names_by_frame_name:
                    raise ValueError(
                        "contract_names_by_frame_name contains unknown frame '{0}'.".format(
                            frame_name
                        )
                    )
                normalized_contract_names_by_frame_name[frame_name] = (
                    self._normalize_acl_selection_input(contract_name)
                )
        for frame_name in normalized_frame_names:
            contract_selection = normalized_contract_names_by_frame_name[frame_name]
            frame_configuration_ids.append(
                self._frame_acl_manager._get_current_frame_acl_configuration(
                    frame_name,
                    view_contract_name=contract_selection["view"],
                    command_contract_name=contract_selection["command"],
                    codegen_contract_name=contract_selection["codegen"],
                ).configuration_id
            )
        cache_key = self._make_projected_frame_viewer_cache_key(
            tuple(sorted(normalized_frame_names)),
            tuple(
                configuration_id
                for _, configuration_id in sorted(
                    zip(normalized_frame_names, frame_configuration_ids)
                )
            ),
            view_profile_name,
            viewer_profile_name,
        )
        with self._lock:
            cached_frame_viewer = self._projected_frame_viewers_by_cache_key.get(
                cache_key
            )
        if cached_frame_viewer is not None:
            return cached_frame_viewer.clone()
        projected_frame_viewer = self.create_frame_viewer(
            normalized_frame_names,
            contract_names_by_frame_name=normalized_contract_names_by_frame_name,
            view_profile_name=view_profile_name,
            viewer_profile_name=viewer_profile_name,
        )
        with self._lock:
            existing_frame_viewer = self._projected_frame_viewers_by_cache_key.get(
                cache_key
            )
            if existing_frame_viewer is not None:
                existing_frame_viewer.cleanup()
            self._projected_frame_viewers_by_cache_key[cache_key] = (
                projected_frame_viewer
            )
        return projected_frame_viewer.clone()

    def create_cached_frame_viewer_for_rift(
            self,
            rift_id: str,
            *,
            view_profile_name: str = "general",
            viewer_profile_name: str = "general",
    ) -> FrameViewer:
        """
        Build or reuse one cached projected viewer for a Rift's assigned
        target frames.

        Contract:
            - Resolves the live Rift first and projects its currently assigned
              target frames through `create_cached_frame_viewer(...)`.
            - Enriches the returned viewer metadata with Rift-specific
              identifiers and assigned-frame information.
            - Derives a default view frame only when the Rift currently has
              exactly one assigned target frame.

        Args:
            rift_id:
                Existing Rift id whose assigned target frames should populate
                the viewer.
            view_profile_name:
                View profile name applied to each projected frame view.
            viewer_profile_name:
                Viewer profile name applied to the hosted viewer.

        Returns:
            FrameViewer: Detached projected viewer for the Rift assignment
            chain.
        """
        self.check_cleaned()
        if not rift_id:
            raise ValueError("rift_id cannot be empty.")
        rift = self._get_required_rift(rift_id)
        assigned_frame_names = rift.list_assigned_frame_names()
        contract_names_by_frame_name = {
            frame_name: rift.get_selected_contract_names(frame_name)
            for frame_name in assigned_frame_names
        }
        frame_viewer = self.create_cached_frame_viewer(
            assigned_frame_names,
            contract_names_by_frame_name=contract_names_by_frame_name,
            view_profile_name=view_profile_name,
            viewer_profile_name=viewer_profile_name,
        )
        current_metadata = frame_viewer.metadata
        current_metadata["rift_id"] = rift.id
        current_metadata["frame_link_contract_ids_by_frame_name"] = {
            frame_name: rift.get_frame_link_contract(frame_name).contract_id
            for frame_name in assigned_frame_names
        }
        current_metadata["assigned_frame_names"] = assigned_frame_names
        current_metadata["selected_contract_names_by_frame_name"] = (
            contract_names_by_frame_name
        )
        default_view_frame_name = None
        if len(assigned_frame_names) == 1:
            default_view_frame_name = assigned_frame_names[0]
        return FrameViewer(
            profile_builder=FrameViewerProfileBuilder(),
            active_profiles_by_name={
                profile_name: frame_viewer_profile.clone()
                for profile_name, frame_viewer_profile in (
                    frame_viewer.active_profiles_by_name.items()
                )
            },
            default_profile_name=frame_viewer.profile_name,
            frame_descriptors_by_name=frame_viewer.frame_descriptors_by_name,
            frame_acl_configurations_by_frame_name=(
                frame_viewer.frame_acl_configurations_by_frame_name
            ),
            compiled_access_surfaces_by_frame_name=(
                frame_viewer.compiled_access_surfaces_by_frame_name
            ),
            default_view_frame_name=default_view_frame_name,
            metadata=current_metadata,
        )

    @staticmethod
    def _make_projected_frame_viewer_cache_key(
            frame_names: Tuple[str, ...],
            configuration_ids: Tuple[str, ...],
            view_profile_name: str,
            viewer_profile_name: str,
    ) -> Tuple[Tuple[str, ...], Tuple[str, ...], str]:
        """
        Build the stable cache key for one projected frame viewer.

        Args:
            frame_names:
                Sorted projected frame names.
            configuration_ids:
                Sorted current ACL configuration ids aligned to `frame_names`.
            view_profile_name:
                Applied view profile name.
            viewer_profile_name:
                Applied viewer profile name.

        Returns:
            Tuple[Tuple[str, ...], Tuple[str, ...], str]:
                Stable projected-viewer cache key.
        """
        return (
            tuple(
                "{0}:{1}".format(frame_name, view_profile_name)
                for frame_name in frame_names
            ),
            configuration_ids,
            "{0}:{1}".format(view_profile_name, viewer_profile_name),
        )

    @staticmethod
    def _normalize_acl_selection_input(
            contract_selection: object,
    ) -> Dict[str, str]:
        """
        Normalize one frame ACL selection payload into family-name form.

        Args:
            contract_selection:
                Either one same-name contract string or a dict keyed by
                `view`, `command`, and `codegen`.

        Returns:
            Dict[str, str]: Normalized selection map.
        """
        if isinstance(contract_selection, str):
            if not contract_selection:
                raise ValueError(
                    "contract_names_by_frame_name must contain non-empty strings."
                )
            return {
                "view": contract_selection,
                "command": contract_selection,
                "codegen": contract_selection,
            }
        if not isinstance(contract_selection, dict):
            raise ValueError(
                "contract_names_by_frame_name values must be strings or dicts."
            )
        normalized_selection = {
            "view": contract_selection.get("view", "default"),
            "command": contract_selection.get("command", "default"),
            "codegen": contract_selection.get("codegen", "default"),
        }
        for family_name, selected_contract_name in normalized_selection.items():
            if not isinstance(selected_contract_name, str) or not selected_contract_name:
                raise ValueError(
                    "contract selection field '{0}' must be a non-empty string.".format(
                        family_name
                    )
                )
        return normalized_selection

    def _invalidate_projected_frame_viewers(
            self,
            frame_name: Optional[str] = None,
    ) -> None:
        """
        Invalidate cached projected frame viewers.

        Args:
            frame_name:
                Optional single-frame scope. When omitted, every cached viewer
                is invalidated.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            cache_keys_to_remove: List[Tuple[Tuple[str, ...], Tuple[str, ...], str]] = []
            for cache_key in self._projected_frame_viewers_by_cache_key.keys():
                if (
                        frame_name is None
                        or any(
                            cached_frame_name.split(":", 1)[0] == frame_name
                            for cached_frame_name in cache_key[0]
                        )
                ):
                    cache_keys_to_remove.append(cache_key)
            for cache_key in cache_keys_to_remove:
                projected_frame_viewer = self._projected_frame_viewers_by_cache_key.pop(
                    cache_key,
                    None,
                )
                if projected_frame_viewer is not None:
                    projected_frame_viewer.cleanup()

    def _refresh_attached_rift_viewers_for_frame(self, frame_name: str) -> None:
        """
        Reattach live Rift-space viewers affected by one frame ACL change.

        Args:
            frame_name:
                Frame name whose selected ACL family revision changed.

        Returns:
            None.
        """
        self.check_cleaned()
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        with self._lock:
            rifts = list(self._rifts_by_id.values())
        for rift in rifts:
            if frame_name not in rift.list_assigned_frame_names():
                continue
            space = rift.space
            current_viewer = space.frame_viewer
            if current_viewer is None:
                continue
            current_profile_name = current_viewer.profile_name or "general"
            rift.attach_frame_viewer(
                cached=False,
                view_profile_name=current_profile_name,
                viewer_profile_name=current_profile_name,
            )

    def _on_frame_acl_changed(self, frame_name: str) -> None:
        """
        Handle one frame ACL registry change.

        Args:
            frame_name:
                Frame name whose ACL state changed.

        Returns:
            None.
        """
        self._invalidate_projected_frame_viewers(frame_name)
        self._refresh_attached_rift_viewers_for_frame(frame_name)

    def get_nexus_frame_for_rift(
            self,
            rift_id: str,
            frame_name: Optional[str] = None,
    ) -> IAethericFrame:
        """
        Internal

        Return a Nexus-managed frame reference for one Rift under the current
        topology rules.

        Args:
            rift_id:
                Requesting Rift id.
            frame_name:
                Optional explicit Nexus frame name. When omitted, `Nexus`
                derives the requested frame from the current topology mode.

        Returns:
            IAethericFrame: Resolved Nexus frame.

        Raises:
            ValueError: If the requesting Rift or requested frame is not
                available under the current mode rules.
        """
        self._require_enabled()
        with self._lock:
            rift = self._get_required_rift(rift_id)
            nexus_frame_mode = self._configuration.get_property("nexus_frame_mode")

            if nexus_frame_mode == NexusFrameMode.single:
                requested_frame_name = frame_name or self._configuration.get_property(
                    "default_nexus_frame_name"
                )
                if requested_frame_name != self._configuration.get_property("default_nexus_frame_name"):
                    raise ValueError("Shared Nexus mode only exposes the shared frame.")
                nexus_frame_record = self._get_required_nexus_frame_record(requested_frame_name)
                return nexus_frame_record.frame

            if nexus_frame_mode == NexusFrameMode.one_per_workspace:
                requested_frame_name = frame_name or self._determine_nexus_frame_name(rift.id)
                if requested_frame_name != self._determine_nexus_frame_name(rift.id):
                    raise ValueError("Rift can only access its own private Nexus frame.")
                nexus_frame_record = self._get_required_nexus_frame_record(requested_frame_name)
                if rift.id not in nexus_frame_record.attached_rift_ids:
                    raise ValueError("Rift is not attached to the requested private Nexus frame.")
                return nexus_frame_record.frame

            if frame_name is None:
                raise ValueError("Indexed Nexus mode requires an explicit frame_name for access.")
            requested_frame_name = frame_name
            nexus_frame_record = self._get_required_nexus_frame_record(requested_frame_name)
            if rift.id not in nexus_frame_record.attached_rift_ids:
                nexus_frame_record.attach_rift_id(rift.id)
            return nexus_frame_record.frame

    def create_nexus_frame_for_rift(
            self,
            rift_id: str,
            frame_name: Optional[str] = None,
            immutable: bool = False,
    ) -> IAethericFrame:
        """
        Internal

        Create or recover a Nexus-managed frame for one Rift under the current
        topology rules.

        Args:
            rift_id:
                Requesting Rift id.
            frame_name:
                Optional explicit Nexus frame name.
            immutable:
                True when the new frame should survive zero attachments until an
                explicit external cleanup path removes it.

        Returns:
            IAethericFrame: Created or recovered Nexus frame.

        Raises:
            ValueError: If creation is not valid under the current topology
                rules.
        """
        self._require_enabled()
        with self._lock:
            rift = self._get_required_rift(rift_id)
            nexus_frame_mode = self._configuration.get_property("nexus_frame_mode")

            if nexus_frame_mode == NexusFrameMode.single:
                shared_frame_name = self._configuration.get_property("default_nexus_frame_name")
                nexus_frame_record = self._get_or_create_nexus_frame_record(
                    shared_frame_name,
                    creator_rift_id=rift.id,
                    immutable=immutable,
                )
                if rift.id not in nexus_frame_record.attached_rift_ids:
                    nexus_frame_record.attach_rift_id(rift.id)
                frame = nexus_frame_record.frame
                self._logger.info(
                    "Resolved Nexus frame '{0}' for Rift id={1}.".format(frame.name, rift_id),
                    "create_nexus_frame_for_rift",
                )
                return frame

            if nexus_frame_mode == NexusFrameMode.one_per_workspace:
                if immutable:
                    raise ValueError("one_per_workspace frames cannot be immutable.")
                private_frame_name = frame_name or self._determine_nexus_frame_name(rift.id)
                if private_frame_name != self._determine_nexus_frame_name(rift.id):
                    raise ValueError("Rift can only create or recover its own private Nexus frame.")
                nexus_frame_record = self._get_or_create_nexus_frame_record(
                    private_frame_name,
                    creator_rift_id=rift.id,
                    immutable=False,
                )
                if rift.id not in nexus_frame_record.attached_rift_ids:
                    nexus_frame_record.attach_rift_id(rift.id)
                frame = nexus_frame_record.frame
                self._logger.info(
                    "Resolved Nexus frame '{0}' for Rift id={1}.".format(frame.name, rift_id),
                    "create_nexus_frame_for_rift",
                )
                return frame

            new_frame_name = frame_name or self._allocate_indexed_nexus_frame_name()
            if self._get_nexus_frame_record(new_frame_name) is not None:
                raise ValueError("Indexed Nexus frame '{0}' already exists.".format(new_frame_name))
            self._validate_nexus_frame_budget((new_frame_name,))
            nexus_frame_record = self._create_nexus_frame_record(
                new_frame_name,
                creator_rift_id=rift.id,
                immutable=immutable,
            )
            nexus_frame_record.attach_rift_id(rift.id)
            frame = nexus_frame_record.frame
            self._logger.info(
                "Resolved Nexus frame '{0}' for Rift id={1}.".format(frame.name, rift_id),
                "create_nexus_frame_for_rift",
            )
            return frame

    def list_accessible_nexus_frame_names(self, rift_id: str) -> Tuple[str, ...]:
        """
        Internal

        Return the Nexus frame names the requesting Rift may currently access.

        Args:
            rift_id:
                Requesting Rift id.

        Contract:
            - Requires Nexus to be enabled.
            - Applies the current Nexus-frame topology mode when determining
              visibility.
            - Returns a snapshot tuple of currently accessible frame names.

        Returns:
            Tuple[str, ...]: Accessible Nexus frame names.
        """
        self._require_enabled()
        with self._lock:
            rift = self._get_required_rift(rift_id)
            nexus_frame_mode = self._configuration.get_property("nexus_frame_mode")
            if nexus_frame_mode == NexusFrameMode.single:
                shared_frame_name = self._configuration.get_property("default_nexus_frame_name")
                if self._get_nexus_frame_record(shared_frame_name) is not None:
                    return (shared_frame_name,)
                return tuple()
            if nexus_frame_mode == NexusFrameMode.one_per_workspace:
                private_frame_name = self._determine_nexus_frame_name(rift.id)
                if self._get_nexus_frame_record(private_frame_name) is not None:
                    return (private_frame_name,)
                return tuple()
            return tuple(
                sorted(
                    frame_name
                    for frame_name in self._list_nexus_frame_names()
                    if rift.id in self._get_required_nexus_frame_record(frame_name).attached_rift_ids
                )
            )

    def check_for_aetheric_frame(self, frame_name: str) -> None:
        """
        Internal

        Drop Nexus frame-record state when `Aether` is about to dispose a
        frame directly.

        Args:
            frame_name:
                Frame name about to be removed from `Aether`.

        Contract:
            - Short-circuits when Nexus is cleaned, disabled, or missing the
              descriptor manager.
            - Detaches the Nexus-managed frame record and matching ACL
              container before notifying attached Rifts.
            - Logs and returns quietly when no Nexus-managed frame record is
              present.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned or not self._enabled or self._frame_descriptor_manager is None:
                return
            nexus_frame_record = self._frame_descriptor_manager._detach_nexus_frame_record(frame_name)
            acl_container_removed = self._frame_acl_manager._remove_frame_acl_container(
                frame_name
            )
            if nexus_frame_record is None:
                if acl_container_removed:
                    self._logger.info(
                        "Removed frame ACL container for '{0}' during Aether detach.".format(
                            frame_name
                        ),
                        "check_for_aetheric_frame",
                    )
                return

            attached_rift_ids = nexus_frame_record.attached_rift_ids
            for attached_rift_id in attached_rift_ids:
                attached_rift = self._rifts_by_id.get(attached_rift_id)
                if attached_rift is not None:
                    attached_rift.on_nexus_frame_disposed(frame_name)
            nexus_frame_record.cleanup()
            if acl_container_removed:
                self._logger.info(
                    "Removed frame ACL container for '{0}' during Aether detach.".format(
                        frame_name
                    ),
                    "check_for_aetheric_frame",
                )
        self._logger.info(
            "Dropped Nexus frame record for '{0}' during Aether detach.".format(frame_name),
            "check_for_aetheric_frame",
        )

    def _require_configured(self) -> None:
        """
        Internal

        Require that Nexus has an installed configuration.

        Contract:
            Raises before callers touch configuration-dependent Nexus behavior
            when no installed configuration is present.

        Returns:
            None.

        Raises:
            RuntimeError: If Nexus is not configured.
        """
        self.check_cleaned()
        if not self._configured or self._configuration is None:
            raise RuntimeError("Nexus is not configured.")

    def _require_enabled(self) -> None:
        """
        Internal

        Require that Nexus is enabled.

        Contract:
            Requires configuration first, then enforces the enabled-state gate
            for live Rift-domain operations.

        Returns:
            None.

        Raises:
            RuntimeError: If Nexus is disabled.
        """
        self._require_configured()
        if not self._enabled:
            raise RuntimeError("Nexus is disabled.")

    def _require_rift_creation_allowed(self, creation_token: Optional[str]) -> None:
        """
        Internal

        Enforce process-wide Rift creation policy.

        Args:
            creation_token:
                Optional caller-supplied creation token.

        Contract:
            - Requires Nexus to be enabled first.
            - Enforces both the global creation flag and the optional
              creation-token gate.

        Returns:
            None.
        """
        self._require_enabled()
        if not self._configuration.get_property("allow_rift_creation"):
            raise ValueError("Rift creation is disabled.")
        if self._configuration.get_property("creation_token_required"):
            if creation_token != self._configuration.get_property("creation_token_value"):
                raise ValueError("Valid creation token is required.")

    def _require_rift_access_allowed(self, access_token: Optional[str]) -> None:
        """
        Internal

        Enforce direct Rift retrieval policy.

        Args:
            access_token:
                Optional caller-supplied Rift access token.

        Contract:
            - Requires Nexus to be enabled first.
            - Enforces both the global direct-access flag and the optional
              access-token gate.

        Returns:
            None.
        """
        self._require_enabled()
        if not self._configuration.get_property("allow_direct_rift_access"):
            raise ValueError("Direct Rift access is disabled.")
        if self._configuration.get_property("rift_access_token_required"):
            if access_token != self._configuration.get_property("rift_access_token_value"):
                raise ValueError("Valid Rift access token is required.")

    def _validate_target_frame_runtime_requirements(
            self,
            target_frame_name: str,
            requested_space_type: RiftSpaceType,
    ) -> None:
        """
        Internal

        Validate that one target frame exposes the minimum Melder runtime
        posture required by the requested Rift room mode.

        Rules:
            - AR always requires `rift_enabled=True` on the target
              frame configuration.
            - Codegen Rift spaces additionally require
              `ai_native_enabled=True`.
            - Codegen Rift spaces additionally require
              `system_state == dynamic`.
            - If a frame declares `ai_native_enabled=True`, it must also be in
              dynamic system state.

        Args:
            target_frame_name:
                Melder frame the Rift will attach to.
            requested_space_type:
                Requested top-level Rift room mode.

        Returns:
            None.
        """
        target_frame_configuration = self._get_required_target_frame_runtime_configuration(
            target_frame_name
        )
        rift_enabled = target_frame_configuration.rift_enabled
        if not rift_enabled:
            raise ValueError(
                "AR requires rift_enabled on target frame '{0}'.".format(
                    target_frame_name
                )
            )

        ai_native_enabled = target_frame_configuration.ai_native_enabled
        target_system_state = target_frame_configuration.system_state

        if ai_native_enabled and target_system_state != SystemState.dynamic:
            raise ValueError(
                "Target frame '{0}' has ai_native_enabled but is not in dynamic system_state.".format(
                    target_frame_name
                )
            )

        if requested_space_type == RiftSpaceType.codegen:
            if not ai_native_enabled:
                raise ValueError(
                    "Codegen AR requires ai_native_enabled on target frame '{0}'.".format(
                        target_frame_name
                    )
                )
            if target_system_state != SystemState.dynamic:
                raise ValueError(
                    "Codegen AR requires target frame '{0}' to be in dynamic system_state.".format(
                        target_frame_name
                    )
                )

    def _get_required_target_frame_runtime_configuration(
            self,
            target_frame_name: str,
    ) -> Any:
        """
        Internal

        Return the AR-relevant runtime posture for one target frame.

        Purpose:
            Prefer the dedicated `AethericFrameConfiguration` when one has been
            bound during conjure, but tolerate older/manual paths by deriving
            the same narrow posture from the full bound Spellbook
            `Configuration` when needed.

        Args:
            target_frame_name:
                Target frame name being validated.

        Returns:
            Any: Runtime posture object exposing `system_state`,
            `ai_native_enabled`, and `rift_enabled`.

        Raises:
            ValueError: If the target frame does not exist or neither frame
                posture nor full configuration is available.
        """
        try:
            target_frame_configuration = self._aether._get_aetheric_frame_configuration(
                target_frame_name
            )
        except ValueError as exc:
            raise ValueError(
                "Target frame '{0}' does not exist.".format(target_frame_name)
            ) from exc

        if target_frame_configuration is not None:
            return target_frame_configuration

        legacy_configuration = self._get_required_target_frame_configuration(
            target_frame_name
        )
        return legacy_configuration.to_aetheric_frame_configuration(
            origin_spellbook_id=None,
        )

    def _get_required_target_frame_configuration(
            self,
            target_frame_name: str,
    ) -> IConfiguration:
        """
        Internal

        Return the bound Melder configuration for one target frame or raise.

        Args:
            target_frame_name:
                Target frame name being validated.

        Returns:
            IConfiguration: Bound Melder configuration.
        """
        try:
            target_frame_configuration = self._aether._get_configuration(
                target_frame_name
            )
        except ValueError as exc:
            raise ValueError(
                "Target frame '{0}' does not exist.".format(target_frame_name)
            ) from exc
        if target_frame_configuration is None:
            raise ValueError(
                "Target frame '{0}' must have a bound Configuration for AR use.".format(
                    target_frame_name
                )
            )
        return target_frame_configuration

    def _get_required_target_frame_boolean(
            self,
            target_frame_configuration: IConfiguration,
            target_frame_name: str,
            property_name: str,
    ) -> bool:
        """
        Internal

        Read one required boolean property from a target frame configuration.

        Args:
            target_frame_configuration:
                Bound Melder configuration for the target frame.
            target_frame_name:
                Target frame name being validated.
            property_name:
                Required boolean property name.

        Returns:
            bool: Property value.
        """
        try:
            value = target_frame_configuration.get_property(property_name)
        except KeyError as exc:
            raise ValueError(
                "Target frame '{0}' must define '{1}' for AR use.".format(
                    target_frame_name,
                    property_name,
                )
            ) from exc
        if not isinstance(value, bool):
            raise ValueError(
                "Target frame '{0}' has invalid '{1}' value '{2}'.".format(
                    target_frame_name,
                    property_name,
                    value,
                )
            )
        return value

    def _get_required_target_frame_system_state(
            self,
            target_frame_configuration: IConfiguration,
            target_frame_name: str,
    ) -> SystemState:
        """
        Internal

        Read the bound Melder system_state for one target frame.

        Args:
            target_frame_configuration:
                Bound Melder configuration for the target frame.
            target_frame_name:
                Target frame name being validated.

        Returns:
            SystemState: Bound target-frame system state.
        """
        try:
            system_state = target_frame_configuration.get_property("system_state")
        except KeyError as exc:
            raise ValueError(
                "Target frame '{0}' must define 'system_state' for AR use.".format(
                    target_frame_name
                )
            ) from exc
        if not isinstance(system_state, SystemState):
            raise ValueError(
                "Target frame '{0}' has invalid system_state '{1}'.".format(
                    target_frame_name,
                    system_state,
                )
            )
        return system_state

    def _validate_target_frame_names(self, target_frame_names: Sequence[str]) -> None:
        """
        Internal

        Validate target frame names against allow-list and deny-list policy.

        Args:
            target_frame_names:
                Candidate target frame names.

        Returns:
            None.
        """
        denied_target_frame_names = self._configuration.get_property("denied_target_frame_names")
        allowed_target_frame_names = self._configuration.get_property("allowed_target_frame_names")
        for target_frame_name in target_frame_names:
            if target_frame_name in denied_target_frame_names:
                raise ValueError("Target frame '{0}' is denied by Nexus policy.".format(target_frame_name))
            if allowed_target_frame_names and target_frame_name not in allowed_target_frame_names:
                raise ValueError("Target frame '{0}' is not allowed by Nexus policy.".format(target_frame_name))

    def _validate_target_frame_budget(self, target_frame_names: Sequence[str]) -> None:
        """
        Internal

        Validate target-frame budget before registration.

        Args:
            target_frame_names:
                Candidate target frame names on the Rift.

        Returns:
            None.
        """
        unique_new_target_frames = []
        for target_frame_name in target_frame_names:
            if target_frame_name not in self._target_frame_ref_counts and target_frame_name not in unique_new_target_frames:
                unique_new_target_frames.append(target_frame_name)
        if not unique_new_target_frames:
            return
        if not self._configuration.get_property("allow_multiple_target_frames"):
            if len(self._target_frame_ref_counts) + len(unique_new_target_frames) > 1:
                raise ValueError("Multiple target frames are disabled.")
        if len(self._target_frame_ref_counts) + len(unique_new_target_frames) > self._configuration.get_property(
                "max_target_frame_count"):
            raise ValueError("Nexus target-frame cap has been reached.")

    def _validate_nexus_frame_budget(self, nexus_frame_names: Sequence[str]) -> None:
        """
        Internal

        Validate internal Nexus-frame budget before registration.

        Args:
            nexus_frame_names:
                Candidate Nexus frame names on the Rift.

        Returns:
            None.
        """
        unique_new_nexus_frames = []
        for nexus_frame_name in nexus_frame_names:
            if self._get_nexus_frame_record(nexus_frame_name) is None and nexus_frame_name not in unique_new_nexus_frames:
                unique_new_nexus_frames.append(nexus_frame_name)
        if not unique_new_nexus_frames:
            return
        if self._count_nexus_frame_records() + len(unique_new_nexus_frames) > self._configuration.get_property(
                "max_nexus_frame_count"):
            raise ValueError("Nexus internal frame cap has been reached.")

    def _validate_active_rift_budget(self) -> None:
        """
        Internal

        Validate active-Rift budget before registration.

        Contract:
            - Treats `0` as "unlimited".
            - Raises before registration when the configured active-Rift cap
              would be exceeded.

        Returns:
            None.
        """
        max_active_rift_count = self._configuration.get_property("max_active_rift_count")
        if max_active_rift_count == 0:
            return
        if len(self._rifts_by_id) >= max_active_rift_count:
            raise ValueError("Nexus active Rift cap has been reached.")

    def _determine_nexus_frame_name(self, rift_id: str) -> str:
        """
        Internal

        Determine the internal Nexus frame name for one Rift from Nexus
        topology policy.

        Args:
            rift_id:
                Canonical Rift id used when the topology mode is
                `one_per_workspace`.

        Contract:
            - Returns the shared configured frame name in `single` mode.
            - Returns a per-Rift derived name in `one_per_workspace` mode.
            - Allocates the next indexed name in `indexed` mode.

        Returns:
            str: Assigned Nexus frame name.
        """
        nexus_frame_mode = self._configuration.get_property("nexus_frame_mode")
        default_nexus_frame_name = self._configuration.get_property("default_nexus_frame_name")
        if nexus_frame_mode == NexusFrameMode.one_per_workspace:
            return "{0}:{1}".format(default_nexus_frame_name, rift_id)
        if nexus_frame_mode == NexusFrameMode.indexed:
            return self._allocate_indexed_nexus_frame_name()
        return default_nexus_frame_name

    def _allocate_default_rift_name(self) -> str:
        """
        Internal

        Allocate the next deterministic default Rift name.

        Contract:
            - Probes forward from the current default-Rift counter.
            - Skips names already present in the Rift-name registry.
            - Advances the counter only after a free name is selected.

        Returns:
            str: Newly allocated default Rift name.

        Raises:
            RuntimeError: If no free deterministic default Rift name can be
                found within the bounded probe window.
        """
        start_number = self._next_default_rift_number
        max_attempts = len(self._rift_ids_by_name) + 1

        for attempt_offset in range(max_attempts):
            candidate_number = start_number + attempt_offset
            rift_name = "nexus_rift_{0}".format(candidate_number)
            if rift_name in self._rift_ids_by_name:
                continue
            self._next_default_rift_number = candidate_number + 1
            return rift_name

        raise RuntimeError(
            "Failed to allocate a deterministic default Rift name after "
            "{0} attempts starting at nexus_rift_{1}.".format(
                max_attempts,
                start_number,
            )
        )

    def _allocate_indexed_nexus_frame_name(self) -> str:
        """
        Internal

        Allocate the next deterministic indexed Nexus frame name.

        Contract:
            Derives the name from the configured default Nexus frame name and
            the current indexed-frame counter, then advances that counter.

        Returns:
            str: Newly allocated indexed Nexus frame name.
        """
        default_nexus_frame_name = self._configuration.get_property("default_nexus_frame_name")
        indexed_frame_name = "{0}:{1}".format(
            default_nexus_frame_name,
            self._next_indexed_nexus_frame_number,
        )
        self._next_indexed_nexus_frame_number = self._next_indexed_nexus_frame_number + 1
        return indexed_frame_name

    def _detach_rift_from_nexus_frames(self, rift_id: str) -> List[str]:
        """
        Internal

        Detach one Rift from its Nexus-frame records and determine which
        frames should be disposed.

        Args:
            rift:
                Rift being removed.

        Contract:
            - Removes the Rift from every currently assigned Nexus-frame
              record.
            - Returns only the frame names that should be disposed after
              detachment.

        Returns:
            List[str]: Frame names that should be disposed through `Aether`.
        """
        with self._lock:
            frame_names_to_cleanup = []
            nexus_frame_mode = self._configuration.get_property("nexus_frame_mode")
            if nexus_frame_mode == NexusFrameMode.single:
                candidate_frame_names = [
                    self._configuration.get_property("default_nexus_frame_name")
                ]
            elif nexus_frame_mode == NexusFrameMode.one_per_workspace:
                candidate_frame_names = [
                    self._determine_nexus_frame_name(rift_id)
                ]
            else:
                candidate_frame_names = self._list_nexus_frame_names()
            for nexus_frame_name in candidate_frame_names:
                nexus_frame_record = self._get_nexus_frame_record(nexus_frame_name)
                if nexus_frame_record is None:
                    continue
                if rift_id not in nexus_frame_record.attached_rift_ids:
                    continue
                nexus_frame_record.detach_rift_id(rift_id)
                if nexus_frame_record.has_attached_rifts():
                    continue
                if nexus_frame_record.immutable:
                    continue
                frame_names_to_cleanup.append(nexus_frame_name)
            return frame_names_to_cleanup

    def _dispose_nexus_frame(self, frame_name: str) -> None:
        """
        Internal

        Dispose one Nexus-managed frame through its record-owned frame object.

        Args:
            frame_name:
                Nexus frame name to dispose.

        Contract:
            Resolves the current Nexus-managed frame record first, then
            delegates disposal to the underlying frame object.

        Returns:
            None.
        """
        nexus_frame_record = self._get_nexus_frame_record(frame_name)
        if nexus_frame_record is None:
            return
        self._logger.info(
            "Disposing Nexus frame '{0}'.".format(frame_name),
            "_dispose_nexus_frame",
        )
        nexus_frame_record.frame.cleanup()

    def _get_required_frame_descriptor(
            self,
            frame_name: str,
    ) -> FrameDescriptor:
        """
        Internal

        Return one existing frame descriptor or raise.

        Args:
            frame_name:
                Frame name to resolve.

        Returns:
            FrameDescriptor: Existing descriptor.
        """
        return self._frame_descriptor_manager._get_required_frame_descriptor(frame_name)

    def _get_or_create_frame_descriptor(
            self,
            frame_name: str,
    ) -> FrameDescriptor:
        """
        Internal

        Return one existing frame descriptor or create it.

        Args:
            frame_name:
                Frame name to resolve.

        Returns:
            FrameDescriptor: Existing or newly created descriptor.
        """
        descriptor = self._frame_descriptor_manager._get_or_create_frame_descriptor(frame_name)
        self._ensure_frame_acl_container(frame_name)
        return descriptor

    def _get_nexus_frame_record(
            self,
            frame_name: str,
    ) -> Optional[NexusFrameRecord]:
        """
        Internal

        Return the descriptor-owned Nexus-managed frame record when present.

        Args:
            frame_name:
                Frame name to resolve.

        Returns:
            Optional[NexusFrameRecord]: Current Nexus-managed frame record.
        """
        return self._frame_descriptor_manager._get_nexus_frame_record(frame_name)

    def _list_nexus_frame_names(self) -> List[str]:
        """
        Internal

        Return the frame names that currently carry a Nexus-managed frame
        record.

        Returns:
            List[str]: Current Nexus-managed frame names.
        """
        return self._frame_descriptor_manager._list_nexus_frame_names()

    def _count_nexus_frame_records(self) -> int:
        """
        Internal

        Return the current number of Nexus-managed frame records.

        Returns:
            int: Number of descriptor-owned Nexus-managed frame records.
        """
        return self._frame_descriptor_manager._count_nexus_frame_records()

    def _get_required_rift(self, rift_id: str) -> IRift:
        """
        Internal

        Return one registered Rift or raise.

        Args:
            rift_id:
                Canonical Rift id.

        Contract:
            Resolves only existing live Rift registry entries and fails fast on
            absence.

        Returns:
            IRift: Registered Rift object.
        """
        try:
            return self._rifts_by_id[rift_id]
        except KeyError as exc:
            raise ValueError("Rift with id '{0}' was not found.".format(rift_id)) from exc

    def _get_required_nexus_frame_record(self, frame_name: str) -> NexusFrameRecord:
        """
        Internal

        Return one existing Nexus frame record or raise.

        Args:
            frame_name:
                Nexus frame name to resolve.

        Contract:
            Resolves only existing descriptor-owned Nexus frame records and
            fails fast when the frame has none.

        Returns:
            NexusFrameRecord: Existing frame record.
        """
        return self._frame_descriptor_manager._get_required_nexus_frame_record(frame_name)

    def _get_or_create_nexus_frame_record(
            self,
            frame_name: str,
            *,
            creator_rift_id: str,
            immutable: bool,
    ) -> NexusFrameRecord:
        """
        Internal

        Return one existing Nexus frame record or create it through Aether.

        Args:
            frame_name:
                Nexus frame name to resolve or create.
            creator_rift_id:
                Rift id that should be recorded as creator when creation is
                required.
            immutable:
                Immutable flag to apply on creation.

        Returns:
            NexusFrameRecord: Existing or newly created record.
        """
        nexus_frame_mode = self._configuration.get_property("nexus_frame_mode")
        nexus_frame_record = self._frame_descriptor_manager._get_or_create_nexus_frame_record(
            frame_name,
            creator_rift_id=creator_rift_id,
            immutable=immutable,
            nexus_frame_mode=nexus_frame_mode,
        )
        self._ensure_frame_acl_container(frame_name)
        return nexus_frame_record

    def _create_nexus_frame_record(
            self,
            frame_name: str,
            *,
            creator_rift_id: str,
            immutable: bool,
    ) -> NexusFrameRecord:
        """
        Internal

        Create one new Nexus frame record and realize its frame through Aether.

        Args:
            frame_name:
                Nexus frame name to create.
            creator_rift_id:
                Rift id recorded as creator/initial owner.
            immutable:
                Immutable flag for the new record.

        Returns:
            NexusFrameRecord: Newly created record.
        """
        nexus_frame_mode = self._configuration.get_property("nexus_frame_mode")
        nexus_frame_record = self._frame_descriptor_manager._create_nexus_frame_record(
            frame_name,
            creator_rift_id=creator_rift_id,
            immutable=immutable,
            nexus_frame_mode=nexus_frame_mode,
        )
        self._ensure_frame_acl_container(frame_name)
        return nexus_frame_record

    def _ensure_frame_acl_container(self, frame_name: str) -> None:
        """
        Internal

        Ensure the matching frame ACL container exists for a frame once the
        descriptor/runtime side has been resolved by the root.

        Args:
            frame_name:
                Frame name whose ACL container should exist.

        Contract:
            Delegates container creation/lookup to the Nexus-owned ACL manager
            and does not return the container to callers.

        Returns:
            None.
        """
        self._frame_acl_manager._ensure_frame_acl_container(frame_name)

    def _increment_ref_count(self, ref_counts: Dict[str, int], key: str) -> None:
        """
        Internal

        Increment one direct dict-backed reference count.

        Args:
            ref_counts:
                Mapping to mutate.
            key:
                Key to increment.

        Returns:
            None.
        """
        if key in ref_counts:
            ref_counts[key] = ref_counts[key] + 1
            return
        ref_counts[key] = 1

    def _decrement_ref_count(self, ref_counts: Dict[str, int], key: str) -> None:
        """
        Internal

        Decrement one direct dict-backed reference count and remove it at zero.

        Args:
            ref_counts:
                Mapping to mutate.
            key:
                Key to decrement.

        Returns:
            None.
        """
        if key not in ref_counts:
            return
        if ref_counts[key] <= 1:
            ref_counts.pop(key, None)
            return
        ref_counts[key] = ref_counts[key] - 1

    def _clone_rift_configuration(self, configuration: IRiftConfiguration) -> RiftConfiguration:
        """
        Internal

        Clone one Rift configuration into a fresh `RiftConfiguration` object.

        Args:
            configuration:
                Source configuration to clone.

        Returns:
            RiftConfiguration: Fresh cloned configuration.
        """
        cloned_configuration = RiftConfiguration()
        for key in configuration.available_properties.keys():
            if not configuration.has_property(key):
                continue
            value = configuration.get_property(key)
            cloned_configuration.set_property(key, value)
        return cloned_configuration
