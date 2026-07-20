import threading
import time
from typing import TYPE_CHECKING, Any, ClassVar, Dict, List, Mapping, Optional, Sequence, Tuple, Union
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

if TYPE_CHECKING:
    from melder.aether.aether import Aether
    from melder.crystallizer.crystallizer import Crystallizer
    from melder.aether.aetheric_frame.aetheric_frame_configuration import (
        AethericFrameConfiguration,
    )
    from melder.aether.conduit.conduit import Conduit
    from melder.aether.spellbook.configuration.spellbook_configuration import (
        SpellbookConfiguration,
    )
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spellbook import Spellbook
    from melder.nexus.frame_descriptor.frame_descriptor import FrameDescriptor
    from melder.nexus.rift.rift import Rift
    from melder.nexus.acl.builder.frame_acl_builder import FrameACLBuilder
    from melder.nexus.acl.configurations.frame_acl_command_configuration import (
        FrameACLCommandConfiguration,
    )
    from melder.nexus.acl.configurations.frame_acl_codegen_configuration import (
        FrameACLCodegenConfiguration,
    )
    from melder.nexus.acl.configurations.frame_acl_view_configuration import (
        FrameACLViewConfiguration,
    )
    from melder.nexus.acl.configurations.profiles.frame_acl_profile import (
        FrameACLProfile,
    )

from melder.crystallizer.crystals.recorded_unit_state import RecordedUnitState
from melder.nexus.acl.frame_acl_compiler import FrameACLCompiler
from melder.nexus.acl.frame_acl_compiled_access_surface import (
    CompiledFrameACLAccessSurface,
)
from melder.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.nexus.frame_acl_manager import FrameACLManager
from melder.nexus.frame_descriptor_manager import FrameDescriptorManager
from melder.nexus.nexus_frame_manager import NexusFrameManager
from melder.nexus.configuration.rift_configuration import RiftConfiguration
from melder.nexus.configuration.nexus_configuration import (
    NexusConfiguration,
)
from melder.nexus.configuration.rift_space_type import RiftSpaceType
from melder.nexus.configuration.rift_validation_mode import RiftValidationMode
from melder.nexus.rift.projection.codegen_projection import CodegenProjection
from melder.nexus.rift.projection.command_projection import CommandProjection
from melder.nexus.rift.projection.frame_projection_set import FrameProjectionSet
from melder.nexus.rift.projection.view_projection import ViewProjection
from melder.nexus.rift.rift_gate_controller.rift_gate_controller import (
    RiftGateController,
)
from melder.nexus.rift.rift_gate.rift_gate import RiftGate
from melder.aether.spellbook.configuration.system_state import SystemState
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.helpers.init_helpers import InitHelpers

class Nexus(Cleanable):
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
        - It exposes `NexusFrameManager` as the sole Nexus-managed frame
          authoring and topology facade while leaving actual
          `AethericFrame` ownership to the hidden substrate.

    Lifecycle:
        Created eagerly by `Aether` at package/runtime boot, but starts
        unconfigured and disabled until a caller explicitly enables Rift-domain
        behavior.

    Threading:
        Uses one class-level singleton lock for instance creation and one
        instance `threading.RLock` for multi-step mutable state transitions.

    Threading:
        Registry mutation and ACL-change fan-out are serialized internally. The
        refresh barrier is config-backed through `NexusConfiguration`
        (`projection_refresh_gate_enabled` plus timeout and poll interval).

    Registration:
        MELDER KERNEL - guarded. Process-wide singleton created eagerly by
        `Aether` at boot; users engage it, they never construct it.

    Subsystem Context:
        The PUBLIC AR root - and the one to hold onto: `Nexus` is public,
        `Aether` is hidden substrate. It owns process-wide policy, the Rift
        registry, `FrameDescriptorManager`, `NexusFrameManager`,
        `FrameACLManager`, and `RiftGateController`.

    System Context:
        Nexus exists so the AR surface can be public WITHOUT exposing the
        substrate. It holds a hidden `Aether` reference for Nexus-managed frame
        realization and disposal, but `Aether` never appears in its public
        contract - which is what lets frame ownership stay with the substrate
        while authoring and topology policy live up here.
        It starts UNCONFIGURED AND DISABLED even though it is constructed
        eagerly at boot. That two-step engagement means merely importing melder
        never opens an AR surface; a user must configure and enable before any
        Rift can be created, so the AR layer is opt-in rather than ambient.
        Its most load-bearing runtime behaviour is the ACL fan-out: on a chain
        bump it computes the UNION of impacted Rifts by testing each Rift's
        assigned frame-contract set, then refreshes each impacted Rift once for
        its changed-frame SUBSET rather than wholesale. Single-frame callbacks
        delegate into that same batch primitive, so there is exactly one refresh
        path rather than two that could diverge.
    """
    __ast_helper_access__: str = "public"
    __agent_purpose__: str = (
        "access: public. The PUBLIC AR root over the hidden Aether substrate. Starts unconfigured and "
        "disabled - call configure(...) then enable() before "
        "create_rift_configuration()/create_rift(...). Owns frame descriptors, ACL, and managed-frame "
        "authoring."
    )

    __melder_internal__ = _mrg.sentinel
    _instance: ClassVar[Optional["Nexus"]] = None
    _lock: ClassVar[threading.RLock] = threading.RLock()
    _initialized: ClassVar[bool] = False
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_logger",
        "_aether",
        "_configuration",
        "_configured",
        "_enabled",
        "_rifts_by_id",
        "_rift_ids_by_name",
        "_next_default_rift_number",
        "_rift_profiles_by_name",
        "_rift_gate_controller",
        "_frame_acl_manager",
        "_frame_descriptor_manager",
        "_frame_manager",
        "_target_frame_ref_counts",
        "_crystallizer",
    ]

    def __new__(cls, *args: object, **kwargs: object) -> "Nexus":
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
        instance = cls._instance
        if instance is None:
            with cls._lock:
                instance = cls._instance
                if instance is None:
                    instance = super(Nexus, cls).__new__(cls)
                    cls._instance = instance
        assert instance is not None
        return instance

    def __init__(
            self,
            *,
            aether: Optional[Aether] = None,
            configuration: Optional[NexusConfiguration] = None,
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
            - Initialization is once-only: the `_initialized` check and the
              whole manager-graph construction run under the class-level
              `_lock`, so exactly one thread builds the singleton state and
              every concurrent first caller blocks until that build completes
              (BUG-003 regression contract, 2026-07-17 audit).
            - Registry, manager, and counter state start empty on first
              initialization.
            - The singleton starts disabled even when configuration is supplied.
            - On construction failure (including a missing `Aether` on first
              init), singleton bookkeeping (`_instance`, `_initialized`) is
              reset under the held lock so a later `Nexus(...)` can construct
              cleanly.

        Threading:
            - The post-boot fast path reads `_initialized` without the lock,
              so the logger-only refresh stays lock-free; the pre-boot path
              re-checks it under `Nexus._lock` before constructing
              (double-checked initialization).
            - `Aether.__init__` constructs `Nexus(aether=self)` while holding
              `Aether._lock`, so lock nesting is one-way
              `Aether._lock` -> `Nexus._lock`; nothing constructed in this
              body re-enters `Aether()` or `Nexus()`.

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
                self._initialize_logging(logger)
            return
        with Nexus._lock:
            if Nexus._initialized:
                # A concurrent first caller finished construction while this
                # thread waited on the lock: honor the logger-refresh contract
                # and return the fully built singleton.
                if logger is not None:
                    self._initialize_logging(logger)
                return
            if aether is None:
                # Already under Nexus._lock: reset bookkeeping so a later
                # properly-formed first construction can proceed.
                if Nexus._instance is self:
                    Nexus._instance = None
                Nexus._initialized = False
                raise ValueError("Nexus must be initialized with an Aether instance.")
            try:
                super().__init__()
                self._id: str = IDBuilder.create_id()
                self._logger = InitHelpers.resolve_safe_logger(None)
                self._aether: Aether = aether
                self._crystallizer: Crystallizer = aether._crystallizer
                self._configuration: Optional[NexusConfiguration] = configuration
                self._configured: bool = configuration is not None
                self._enabled: bool = False

                self._rifts_by_id: Dict[str, Rift] = {}
                self._rift_ids_by_name: Dict[str, str] = {}
                self._next_default_rift_number: int = 1
                self._rift_profiles_by_name: Dict[str, RiftConfiguration] = {}
                self._rift_gate_controller: RiftGateController = RiftGateController()
                self._frame_acl_manager: FrameACLManager = FrameACLManager(
                    change_callback=self._on_frame_acl_changed,
                )
                self._target_frame_ref_counts: Dict[str, int] = {}

                self._frame_descriptor_manager: FrameDescriptorManager = FrameDescriptorManager(aether)
                self._frame_manager: NexusFrameManager = NexusFrameManager(
                    nexus=self,
                )
                self._initialize_logging(logger)
                # BUG-003 (2026-07-17 audit): the once-only latch flips while
                # the class lock is still held so the unlocked fast path above
                # can only observe a fully constructed singleton.
                Nexus._initialized = True
            except Exception:
                # Already under Nexus._lock: reset bookkeeping so a later
                # Nexus(...) call can construct a fresh singleton cleanly.
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
        with self._lock:
            if self._cleaned:
                return
            self._logger.info("Cleaning Nexus singleton state.", "cleanup")
            self._cleaned = True
            # Record the teardown when the record outlives Nexus. In the
            # Aether full-teardown lane the crystallizer is already cleaned
            # (frames -> crystallizer -> MR -> Nexus), so this skips there.
            if not self._crystallizer.cleaned and self._crystallizer.activated:
                self._crystallizer.emit_nexus_state(RecordedUnitState.cleaned)
            for rift in self._rifts_by_id.values():
                rift.cleanup()
            if self._configuration is not None:
                self._configuration.cleanup()
            for profile in self._rift_profiles_by_name.values():
                profile.cleanup()
            if self._rift_gate_controller is not None:
                self._rift_gate_controller.cleanup()
            if self._frame_acl_manager is not None:
                self._frame_acl_manager.cleanup()
            if self._frame_descriptor_manager is not None:
                self._frame_descriptor_manager.cleanup()
            if self._frame_manager is not None:
                self._frame_manager.cleanup()
            self._rifts_by_id.clear()
            self._rift_ids_by_name.clear()
            self._rift_profiles_by_name.clear()
            self._target_frame_ref_counts.clear()
            if self._logger is not None:
                self._logger.cleanup()

            del self._logger
            del self._configuration
            del self._configured
            del self._enabled
            del self._aether
            del self._next_default_rift_number
            del self._rifts_by_id
            del self._rift_ids_by_name
            del self._rift_profiles_by_name
            del self._rift_gate_controller
            del self._frame_acl_manager
            del self._frame_descriptor_manager
            del self._frame_manager
            del self._crystallizer
            del self._target_frame_ref_counts
            del self._id

        with Nexus._lock:
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

        Contract:
            - Same-sink refresh REUSES the existing wrapper (BUG-279,
              2026-07-17 audit): refreshing with the raw sink the current
              wrapper already owns is a no-op, so the sink retained by the
              live wrapper is never torn down by its own refresh.
            - The displaced wrapper is retired only when the underlying raw
              sinks differ; alias detection is at sink identity, not wrapper
              identity, because every refresh builds a distinct wrapper.

        Args:
            logger:
                Optional explicit logger override.

        Returns:
            None.
        """
        # Both call paths (__init__ first boot and re-init logger refresh)
        # assign self._logger before this method runs, so direct access is the
        # truthful owned-field contract here.
        previous_logger = self._logger
        try:
            if logger is not None:
                if previous_logger._logger is logger:
                    # BUG-279 (2026-07-17 audit): same-sink refresh - the
                    # current wrapper already owns this exact raw sink.
                    # Building a replacement and cleaning the "displaced"
                    # wrapper would terminally clean the sink the new wrapper
                    # still references, so reuse the existing wrapper as-is.
                    return
                next_logger = InitHelpers.resolve_safe_logger(logger)
            else:
                next_logger = InitHelpers.resolve_channel_logger(
                    self,
                    groups=self._get_default_logger_groups(),
                    system_groups=self._get_default_logger_system_groups(),
                    props=self._get_default_logger_properties(),
                    channels="system",
                )
            if (
                previous_logger is not next_logger
                and previous_logger._logger is not next_logger._logger
            ):
                try:
                    # Best-effort teardown of the displaced logger; a logger
                    # swap must never fail because old-handle cleanup raised.
                    # Skipped when both wrappers share one raw sink (BUG-279).
                    previous_logger.cleanup()
                except Exception:
                    pass
            self._logger = next_logger
        except Exception as e:
            fallback_logger = InitHelpers.resolve_safe_logger(None)
            if previous_logger is not fallback_logger:
                try:
                    # Best-effort teardown of the displaced logger; the silent
                    # fallback path must always complete.
                    previous_logger.cleanup()
                except Exception:
                    pass
            self._logger = fallback_logger
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
        with cls._lock:
            instance = cls._instance
            if instance is None:
                cls._initialized = False
                return
            try:
                try:
                    instance.cleanup()
                except AttributeError:
                    # First-time initialization can fail before the Cleanable
                    # base state and other owned fields are fully attached.
                    # Test-only singleton reset must still clear class-level
                    # bookkeeping in that partial-init case.
                    pass
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
    def frame_manager(self) -> NexusFrameManager:
        """
        Return the Nexus frame authoring facade.

        Returns:
            NexusFrameManager: Manager for authored Nexus-managed frames.
        """
        self.check_cleaned()
        return self._frame_manager

    @property
    def configuration(self) -> NexusConfiguration:
        """
        Purpose:
            Return the installed Nexus configuration.

        Contract:
            Returns the live installed configuration object, not a detached
            copy.

        Returns:
            NexusConfiguration: Installed process-wide config.

        Raises:
            RuntimeError: If Nexus has not been configured yet.
        """
        self._require_configured()
        configuration = self._configuration
        if configuration is None:
            raise RuntimeError("Nexus is not configured.")
        return configuration

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

    @property
    def rift_gate_controller(self) -> RiftGateController:
        """
        Return the Nexus-owned Rift gate controller.

        Returns:
            RiftGateController: Controller for registered Rift gates.
        """
        self.check_cleaned()
        return self._rift_gate_controller

    def create_system_configuration(self) -> NexusConfiguration:
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
            NexusConfiguration: Fresh mutable Nexus config.
        """
        self.check_cleaned()
        return NexusConfiguration().with_defaults()

    def enable(
            self,
            configuration: Optional[NexusConfiguration] = None,
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
            configured = self.configuration
            if not configured.frozen:
                configured.finalize()
            else:
                # Pre-frozen configuration (the RELOAD lane seals without
                # emission because enable had not happened yet): enable is
                # the activation moment, so the twin emission fires here -
                # same fix class as the spellbook conjure re-freeze.
                configured.emit_configured_twin_when_recording()
            self._enabled = True
            self._logger.info("Nexus enabled.", "enable")
            # Record the lifecycle flip: the twin (emitted at configuration
            # freeze) is retained; the state switch carries enable truth.
            if self._crystallizer.activated:
                self._crystallizer.emit_nexus_state(RecordedUnitState.enabled)

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
            # Disable keeps the installed configuration, so the twin stays;
            # the record flips the state switch instead of evicting.
            if self._crystallizer.activated:
                self._crystallizer.emit_nexus_state(RecordedUnitState.disabled)

    def create_rift_configuration(
            self,
            profile_name: Optional[str] = None,
    ) -> RiftConfiguration:
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
            RiftConfiguration: Mutable per-Rift configuration.

        Raises:
            RuntimeError:
                If Nexus is not configured.
            ValueError:
                If `profile_name` is unknown.
        """
        configured = self.configuration
        if profile_name is not None:
            with self._lock:
                try:
                    template = self._rift_profiles_by_name[profile_name]
                except KeyError as exc:
                    raise ValueError("Rift profile '{0}' was not found.".format(profile_name)) from exc
            return self._clone_rift_configuration(template)

        configuration = RiftConfiguration().with_defaults()
        default_space_type = configured.get_property("default_space_type")
        if not isinstance(default_space_type, RiftSpaceType):
            raise TypeError("default_space_type must remain a RiftSpaceType.")
        default_auto_activate_on_program = configured.get_property(
            "default_auto_activate_on_program"
        )
        if not isinstance(default_auto_activate_on_program, bool):
            raise TypeError(
                "default_auto_activate_on_program must remain a bool."
            )
        default_validation_mode = configured.get_property(
            "default_validation_mode"
        )
        if not isinstance(default_validation_mode, RiftValidationMode):
            raise TypeError(
                "default_validation_mode must remain a RiftValidationMode."
            )
        configuration.with_space_type(default_space_type)
        configuration.with_auto_activate_on_program(
            default_auto_activate_on_program
        )
        configuration.with_validation_mode(default_validation_mode)
        return configuration

    def register_rift_profile(
            self,
            name: str,
            configuration: RiftConfiguration,
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
            configuration: Optional[RiftConfiguration] = None,
            rift_name: Optional[str] = None,
            rift_id: Optional[str] = None,
            space_id: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
            creation_token: Optional[str] = None,
            logger: Optional[Any] = None,
    ) -> Rift:
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
            Rift: Newly created and registered live Rift.
        """
        self._require_rift_creation_allowed(creation_token)
        from melder.nexus.rift.rift import Rift

        canonical_rift_id = rift_id or IDBuilder.create_id()
        bound_configuration = configuration or self.create_rift_configuration()
        if bound_configuration.consumed:
            raise ValueError("RiftConfiguration has already been consumed.")
        if not bound_configuration.frozen:
            bound_configuration.finalize()

        with self._lock:
            canonical_rift_name = rift_name or self._allocate_default_rift_name()
            rift_gate = self._rift_gate_controller.create_rift_gate(canonical_rift_id)
            rift = None
            try:
                rift = Rift(
                    self,
                    configuration=bound_configuration,
                    rift_gate=rift_gate,
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
            except Exception:
                self._rift_gate_controller.unregister_rift_gate(canonical_rift_id)
                if rift is not None:
                    rift.cleanup()
                else:
                    rift_gate.cleanup()
                raise

    def add_rift(self, rift: Rift) -> None:
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
            existing_gate = self._rift_gate_controller.get_rift_gate(rift.id)
            if existing_gate is None:
                self._rift_gate_controller.register_rift_gate(
                    rift.id,
                    rift.rift_gate,
                )
            elif existing_gate is not rift.rift_gate:
                raise ValueError(
                    "Rift gate for id '{0}' does not match the registered gate.".format(
                        rift.id
                    )
                )

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
    ) -> Rift:
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
            Rift: Registered Rift object.
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
    ) -> Rift:
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
            Rift: Registered Rift object.
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
            self._rift_gate_controller.unregister_rift_gate(rift.id)
            for target_frame_name in rift.list_assigned_frame_names():
                self._decrement_ref_count(self._target_frame_ref_counts, target_frame_name)
            frame_names_to_cleanup.extend(
                self._frame_manager.get_frame_names_to_cleanup_for_removed_rift(
                    rift.id
                )
            )

        for frame_name in frame_names_to_cleanup:
            self._frame_manager.remove(frame_name)
        rift.cleanup()
        self._logger.info(
            "Removed Rift '{0}' (id={1}).".format(rift_name, rift_id),
            "remove_rift",
        )

    def _publish_frame_record(self, spellbook: Spellbook) -> bool:
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
        if self._frame_descriptor_manager._has_frame_descriptor(spellbook._aetheric_frame_name):
            self._ensure_frame_acl_container(spellbook._aetheric_frame_name)
        return published

    def _publish_conduit_record(self, conduit: Conduit) -> bool:
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
        if self._frame_descriptor_manager._has_frame_descriptor(conduit._aetheric_frame_name):
            self._ensure_frame_acl_container(conduit._aetheric_frame_name)
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
        return removed

    def _publish_spell_record(
            self,
            spellbook: Spellbook,
            spell: Spell,
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
        if self._frame_descriptor_manager._has_frame_descriptor(spellbook._aetheric_frame_name):
            self._ensure_frame_acl_container(spellbook._aetheric_frame_name)
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

    def get_rift_gate(self, rift_id: str) -> Optional[RiftGate]:
        """
        Return the registered Rift gate for one Rift id, if present.

        Args:
            rift_id:
                Canonical Rift id.

        Returns:
            Optional[RiftGate]: Registered Rift gate when present.
        """
        self.check_cleaned()
        return self._rift_gate_controller.get_rift_gate(rift_id)

    def enable_rift_gate(self, rift_id: str) -> None:
        """
        Open one Rift gate by Rift id.

        Args:
            rift_id:
                Canonical Rift id.

        Returns:
            None.
        """
        self.check_cleaned()
        gate = self._rift_gate_controller.get_rift_gate(rift_id)
        if gate is None:
            return
        gate.open()

    def disable_rift_gate(self, rift_id: str) -> None:
        """
        Close one Rift gate by Rift id.

        Args:
            rift_id:
                Canonical Rift id.

        Returns:
            None.
        """
        self.check_cleaned()
        gate = self._rift_gate_controller.get_rift_gate(rift_id)
        if gate is None:
            return
        gate.close()

    def close_and_wait_rift(
            self,
            rift_id: str,
            timeout: float = 30.0,
            interval: float = 0.1,
    ) -> None:
        """
        Terminally close and drain one Rift gate.

        Args:
            rift_id:
                Canonical Rift id.
            timeout:
                Maximum seconds to wait for ticket drain.
            interval:
                Poll interval in seconds while draining.

        Returns:
            None.
        """
        self.check_cleaned()
        self._rift_gate_controller.close_and_wait_until_rift_free(
            rift_id,
            timeout=timeout,
            interval=interval,
        )

    def count_active_rift_threads(self, rift_id: str) -> int:
        """
        Return active ticket count for one Rift gate.

        Args:
            rift_id:
                Canonical Rift id.

        Returns:
            int: Active ticket count.
        """
        self.check_cleaned()
        return self._rift_gate_controller.count_active_threads_for_rift(rift_id)

    def count_active_rift_threads_total(self) -> int:
        """
        Return active ticket count summed across all Rift gates.

        Returns:
            int: Total active ticket count.
        """
        self.check_cleaned()
        return self._rift_gate_controller.count_active_threads_total()

    def enable_all_rift_gates(self) -> None:
        """
        Open every registered Rift gate.

        Returns:
            None.
        """
        self.check_cleaned()
        self._rift_gate_controller.enable_all_rift_gates()

    def disable_all_rift_gates(self) -> None:
        """
        Close every registered Rift gate.

        Returns:
            None.
        """
        self.check_cleaned()
        self._rift_gate_controller.disable_all_rift_gates()

    def set_rift_gate_entry_mode(self, rift_id: str, entry_mode: str) -> None:
        """
        Set the admission mode for one registered Rift gate.

        Args:
            rift_id:
                Canonical Rift id.
            entry_mode:
                Admission mode to apply.

        Returns:
            None.
        """
        self.check_cleaned()
        self._rift_gate_controller.set_rift_gate_entry_mode(rift_id, entry_mode)

    def set_all_rift_gate_entry_mode(self, entry_mode: str) -> None:
        """
        Set the admission mode for every registered Rift gate.

        Args:
            entry_mode:
                Admission mode to apply.

        Returns:
            None.
        """
        self.check_cleaned()
        self._rift_gate_controller.set_all_rift_gate_entry_mode(entry_mode)

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

        Args:
            frame_name:
                Frame whose currently selected VIEW ACL revision should be read.
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

        Args:
            frame_name:
                Frame whose currently selected COMMAND ACL revision should be read.
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

        Args:
            frame_name:
                Frame whose currently selected CODEGEN ACL revision should be read.
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
        if not isinstance(configuration, FrameACLConfiguration):
            raise TypeError(
                "configuration must be a FrameACLConfiguration instance."
            )
        self._ensure_frame_acl_container(frame_name)
        registered_configuration = self._frame_acl_manager._register_named_frame_acl_configuration(
            frame_name,
            configuration,
            contract_name=contract_name,
        )
        return registered_configuration

    @staticmethod
    def _clone_frame_acl_configuration(
            configuration: FrameACLConfiguration,
            *,
            reason: str,
    ) -> FrameACLConfiguration:
        """
        Return a detached ACL configuration clone for projection-owned state.

        Args:
            configuration:
                Source ACL configuration.
            reason:
                Clone reason recorded on the detached bundle.

        Returns:
            FrameACLConfiguration: Detached ACL configuration clone.
        """
        return FrameACLConfiguration.create_from_selected_configurations(
            frame_name=configuration.frame_name,
            view_configuration=configuration.view_configuration,
            command_configuration=configuration.command_configuration,
            codegen_configuration=configuration.codegen_configuration,
            reason=reason,
            locked=True,
            configuration_id=configuration.configuration_id,
        )

    @staticmethod
    def _clone_compiled_access_surface(
            compiled_access_surface: CompiledFrameACLAccessSurface,
    ) -> CompiledFrameACLAccessSurface:
        """
        Return a detached compiled ACL surface clone for projection-owned state.

        Args:
            compiled_access_surface:
                Source compiled ACL access surface.

        Returns:
            CompiledFrameACLAccessSurface: Detached compiled ACL surface clone.
        """
        return CompiledFrameACLAccessSurface(
            frame_name=compiled_access_surface.frame_name,
            configuration_id=compiled_access_surface.configuration_id,
            view_profile_name=compiled_access_surface.view_profile_name,
            view_profile_version=compiled_access_surface.view_profile_version,
            codegen_profile_name=compiled_access_surface.codegen_profile_name,
            codegen_profile_version=compiled_access_surface.codegen_profile_version,
            codegen_imports_enabled=compiled_access_surface.codegen_imports_enabled,
            allowed_import_module_roots=(
                compiled_access_surface.allowed_import_module_roots
            ),
            denied_import_module_roots=(
                compiled_access_surface.denied_import_module_roots
            ),
            denied_builtin_names=compiled_access_surface.denied_builtin_names,
            codegen_unsafe_reflection_allowed=(
                compiled_access_surface.codegen_unsafe_reflection_allowed
            ),
            codegen_dunder_access_allowed=(
                compiled_access_surface.codegen_dunder_access_allowed
            ),
            codegen_recursive_codegen_allowed=(
                compiled_access_surface.codegen_recursive_codegen_allowed
            ),
            command_frame_enabled=compiled_access_surface.command_frame_enabled,
            allowed_kinds=compiled_access_surface.allowed_kinds,
            allowed_commands=compiled_access_surface.allowed_commands,
            frame_payload_fields=compiled_access_surface.frame_payload_fields,
            visible_conduit_ids=compiled_access_surface.visible_conduit_ids,
            visible_spell_keys=compiled_access_surface.visible_spell_keys,
            visible_spell_index_ids=compiled_access_surface.visible_spell_index_ids,
            enabled_conduit_ids=compiled_access_surface.enabled_conduit_ids,
            enabled_spell_index_ids=compiled_access_surface.enabled_spell_index_ids,
            conduit_payload_sections_by_id=(
                compiled_access_surface.conduit_payload_sections_by_id
            ),
            spell_payload_sections_by_key=(
                compiled_access_surface.spell_payload_sections_by_key
            ),
            metadata=compiled_access_surface.metadata,
        )

    def _create_frame_projection_set(
            self,
            *,
            frame_name: str,
            contract_selection: Dict[str, str],
    ) -> FrameProjectionSet:
        """
        Build one detached projection set for a targeted frame.

        Args:
            frame_name:
                Target frame name.
            contract_selection:
                Selected contract names for `view`, `command`, and `codegen`.

        Returns:
            FrameProjectionSet: Fresh projection set for the frame.
        """
        descriptor = self._get_required_frame_descriptor(frame_name)
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
        compiler = FrameACLCompiler(self._frame_acl_manager.frame_acl_profile_builder)
        compiled_access_surface: Optional[CompiledFrameACLAccessSurface] = None
        try:
            compiled_access_surface = compiler.compile_frame_access_surface(
                descriptor,
                configuration,
            )
            view_projection = ViewProjection(
                frame_name=frame_name,
                frame_descriptor=descriptor,
                frame_acl_configuration=self._clone_frame_acl_configuration(
                    configuration,
                    reason="view_projection_clone",
                ),
                compiled_access_surface=self._clone_compiled_access_surface(
                    compiled_access_surface
                ),
                metadata={"surface": "view"},
            )
            command_projection = CommandProjection(
                frame_name=frame_name,
                frame_descriptor=descriptor,
                frame_acl_configuration=self._clone_frame_acl_configuration(
                    configuration,
                    reason="command_projection_clone",
                ),
                compiled_access_surface=self._clone_compiled_access_surface(
                    compiled_access_surface
                ),
                metadata={"surface": "command"},
            )
            codegen_projection = CodegenProjection(
                frame_name=frame_name,
                frame_descriptor=descriptor,
                frame_acl_configuration=self._clone_frame_acl_configuration(
                    configuration,
                    reason="codegen_projection_clone",
                ),
                compiled_access_surface=self._clone_compiled_access_surface(
                    compiled_access_surface
                ),
                metadata={"surface": "codegen"},
            )
        finally:
            compiler.cleanup()
            if compiled_access_surface is not None:
                compiled_access_surface.cleanup()
            configuration.cleanup()
        return FrameProjectionSet(
            frame_name=frame_name,
            view_projection=view_projection,
            command_projection=command_projection,
            codegen_projection=codegen_projection,
            metadata={
                "selected_contract_names": dict(contract_selection),
            },
        )

    def create_frame_projection_sets(
            self,
            frame_names: Sequence[str],
            *,
            contract_names_by_frame_name: Optional[
                Mapping[str, Union[str, Mapping[str, str]]]
            ] = None,
    ) -> Dict[str, FrameProjectionSet]:
        """
        Build projection sets for the requested frame names.

        Args:
            frame_names:
                Frame names to project.
            contract_names_by_frame_name:
                Optional per-frame selected ACL contract names.

        Returns:
            Dict[str, IFrameProjectionSet]: Fresh projection sets keyed by frame name.
        """
        self.check_cleaned()
        if isinstance(frame_names, str) or not isinstance(frame_names, Sequence):
            raise TypeError("frame_names must be a sequence.")
        normalized_frame_names: List[str] = []
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
        return {
            frame_name: self._create_frame_projection_set(
                frame_name=frame_name,
                contract_selection=normalized_contract_names_by_frame_name[frame_name],
            )
            for frame_name in normalized_frame_names
        }

    def insert_head_frame_acl_configuration(
            self,
            frame_name: str,
            configuration: FrameACLConfiguration,
            *,
            select_as_current: bool = True,
    ) -> FrameACLConfiguration:
        """
        Install one replacement revision into the selected same-name ACL contract.

        Purpose:
            Expose the public Nexus seam for replacing the current selected
            same-name ACL bundle revision under an existing named contract.

        Contract:
            - Installs the supplied locked ACL bundle into the selected named
              contract set for the frame.
            - Preserves the current same-name contract model by advancing the
              selected bundle revision instead of creating a new contract name.
            - `select_as_current` is retained for compatibility with existing
              callers, but current/head separation is already implicit in the
              install path and does not require separate branch logic here.

        Args:
            frame_name:
                Stable frame name that owns the ACL registry.
            configuration:
                Locked ACL configuration node to install.
            select_as_current:
                Compatibility-only flag preserved for existing callers.

        Returns:
            FrameACLConfiguration:
                Installed assembled configuration snapshot.
        """
        self.check_cleaned()
        if not isinstance(configuration, FrameACLConfiguration):
            raise TypeError(
                "configuration must be a FrameACLConfiguration instance."
            )
        self._ensure_frame_acl_container(frame_name)
        return self._frame_acl_manager._install_named_frame_acl_configuration(
            frame_name,
            configuration,
            contract_name="default",
        )

    def create_frame_projection_sets_for_rift(
            self,
            rift_id: str,
            *,
            frame_names: Optional[Sequence[str]] = None,
    ) -> Dict[str, FrameProjectionSet]:
        """
        Build projection sets from one Rift's current frame contracts.

        Args:
            rift_id:
                Existing Rift id whose frame contracts should be projected.
            frame_names:
                Optional explicit multi-frame scope for one or more engaged
                frames.

        Returns:
            Dict[str, IFrameProjectionSet]: Projection sets keyed by frame name.
        """
        self.check_cleaned()
        if not rift_id:
            raise ValueError("rift_id cannot be empty.")
        rift = self._get_required_rift(rift_id)
        assigned_frame_names = rift.list_assigned_frame_names()
        selected_frame_names = assigned_frame_names
        if frame_names is not None:
            selected_frame_names = self._normalize_requested_frame_name_batch(
                frame_names,
                argument_name="frame_names",
            )
            for frame_name in selected_frame_names:
                if frame_name not in assigned_frame_names:
                    raise ValueError(
                        "Frame '{0}' is not assigned to Rift '{1}'.".format(
                            frame_name,
                            rift_id,
                        )
                    )
        contract_names_by_frame_name = {
            selected_frame_name: rift.get_selected_contract_names(selected_frame_name)
            for selected_frame_name in selected_frame_names
        }
        return self.create_frame_projection_sets(
            selected_frame_names,
            contract_names_by_frame_name=contract_names_by_frame_name,
        )

    @staticmethod
    def _normalize_requested_frame_name_batch(
            frame_names: Sequence[str],
            *,
            argument_name: str = "frame_names",
    ) -> Tuple[str, ...]:
        """
        Normalize one explicit frame-name batch while preserving caller order.

        Args:
            frame_names:
                Sequence of requested frame names.
            argument_name:
                Argument label used for error messages.

        Returns:
            Tuple[str, ...]: Deduplicated frame names in first-seen order.

        Raises:
            ValueError:
                If the payload is empty, is a bare string, or contains an empty
                frame name.
        """
        if isinstance(frame_names, str):
            raise ValueError(
                "{0} must be a sequence of frame names, not one string.".format(
                    argument_name
                )
            )
        normalized_frame_names: List[str] = []
        seen_frame_names = set()
        for frame_name in frame_names:
            if not isinstance(frame_name, str) or not frame_name:
                raise ValueError(
                    "{0} must contain non-empty frame names.".format(argument_name)
                )
            if frame_name in seen_frame_names:
                continue
            seen_frame_names.add(frame_name)
            normalized_frame_names.append(frame_name)
        if len(normalized_frame_names) == 0:
            raise ValueError("{0} cannot be empty.".format(argument_name))
        return tuple(normalized_frame_names)

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

    def _wait_until_rift_gate_is_idle(
            self,
            rift_id: str,
            *,
            timeout: float = 30.0,
            interval: float = 0.1,
    ) -> None:
        """
        Wait for one Rift gate to drain active tickets without terminal closure.

        Args:
            rift_id:
                Existing Rift id.
            timeout:
                Maximum seconds to wait for ticket drain.
            interval:
                Poll interval in seconds while draining.

        Returns:
            None.
        """
        self.check_cleaned()
        gate = self.get_rift_gate(rift_id)
        if gate is None:
            return
        deadline = time.monotonic() + timeout
        while gate.has_active_tickets():
            if time.monotonic() >= deadline:
                raise RuntimeError(
                    "Timeout waiting for Rift gate '{0}' to drain.".format(rift_id)
                )
            time.sleep(interval)

    def _refresh_rift_projection_sets_for_frames(
            self,
            frame_names: Sequence[str],
    ) -> None:
        """
        Synchronously refresh projection sets for all impacted Rifts in one batch.

        Args:
            frame_names:
                Changed frame names whose projections should refresh.

        Returns:
            None.
        """
        self.check_cleaned()
        if not self._configured or self._configuration is None or not self._enabled:
            return
        normalized_frame_names = self._normalize_requested_frame_name_batch(
            frame_names,
            argument_name="frame_names",
        )
        with self._lock:
            rifts = list(self._rifts_by_id.values())
            projection_refresh_gate_enabled = self._configuration.get_property(
                "projection_refresh_gate_enabled"
            )
            timeout = self._configuration.get_property(
                "projection_refresh_gate_timeout_seconds"
            )
            interval = self._configuration.get_property(
                "projection_refresh_gate_poll_interval_seconds"
            )
        if not isinstance(projection_refresh_gate_enabled, bool):
            raise TypeError(
                "projection_refresh_gate_enabled must remain a bool."
            )
        if not isinstance(timeout, (int, float)):
            raise TypeError(
                "projection_refresh_gate_timeout_seconds must remain numeric."
            )
        if not isinstance(interval, (int, float)):
            raise TypeError(
                "projection_refresh_gate_poll_interval_seconds must remain numeric."
            )
        impacted_rifts = []
        frame_names_by_rift_id: Dict[str, Tuple[str, ...]] = {}
        for rift in rifts:
            assigned_frame_names = rift.list_assigned_frame_names()
            impacted_frame_names = tuple(
                frame_name
                for frame_name in normalized_frame_names
                if frame_name in assigned_frame_names
            )
            if len(impacted_frame_names) == 0:
                continue
            impacted_rifts.append(rift)
            frame_names_by_rift_id[rift.id] = impacted_frame_names
        if not projection_refresh_gate_enabled:
            for rift in impacted_rifts:
                rift.refresh_runtime_projections(
                    frame_names=frame_names_by_rift_id[rift.id]
                )
            return
        disabled_rift_ids: List[str] = []
        try:
            for rift in impacted_rifts:
                self.disable_rift_gate(rift.id)
                disabled_rift_ids.append(rift.id)
            for rift in impacted_rifts:
                self._wait_until_rift_gate_is_idle(
                    rift.id,
                    timeout=timeout,
                    interval=interval,
                )
            for rift in impacted_rifts:
                rift.refresh_runtime_projections(
                    frame_names=frame_names_by_rift_id[rift.id]
                )
        finally:
            for rift_id in disabled_rift_ids:
                try:
                    # Best-effort gate reopen: every gate disabled above must
                    # get its reopen attempt even when refresh failed or an
                    # earlier reopen raised.
                    self.enable_rift_gate(rift_id)
                except Exception:
                    pass

    def _on_frame_acl_changed(self, frame_name: str) -> None:
        """
        Handle one frame ACL registry change.

        Args:
            frame_name:
                Frame name whose ACL state changed.

        Returns:
            None.
        """
        self._refresh_rift_projection_sets_for_frames((frame_name,))

    def get_nexus_frame_for_rift(
            self,
            rift_id: str,
            frame_name: Optional[str] = None,
    ) -> Conduit:
        """
        Internal

        Return a rooted Nexus-managed conduit for one Rift under the current
        topology rules.

        Args:
            rift_id:
                Requesting Rift id.
            frame_name:
                Optional explicit Nexus frame name. When omitted, `Nexus`
                derives the requested frame from the current topology mode.

        Returns:
            Conduit: Root conduit for the resolved Nexus-managed frame.

        Raises:
            ValueError: If the requesting Rift or requested frame is not
                available under the current mode rules.
        """
        frame = self._frame_manager.get_frame_for_rift(
            rift_id,
            frame_name=frame_name,
        )
        return self._frame_manager._get_required_root_conduit_for_frame(frame.name)

    def create_nexus_frame_for_rift(
            self,
            rift_id: str,
            frame_name: Optional[str] = None,
            root_conduit_name: str = "root",
            immutable: bool = False,
    ) -> Conduit:
        """
        Internal

        Create one rooted Nexus-managed conduit for one Rift under the current
        topology rules.

        Args:
            rift_id:
                Requesting Rift id.
            frame_name:
                Optional explicit Nexus frame name.
            root_conduit_name:
                Root conduit name to use for newly created frames.
            immutable:
                True when the new frame should survive zero attachments until an
                explicit external cleanup path removes it.

        Returns:
            Conduit: Root conduit for the newly created frame.

        Raises:
            ValueError: If creation is not valid under the current topology
                rules or the target frame already exists.
        """
        root_conduit = self._frame_manager.create_frame_for_rift(
            rift_id,
            frame_name=frame_name,
            root_conduit_name=root_conduit_name,
            immutable=immutable,
        )
        self._logger.info(
            "Resolved Nexus rooted conduit '{0}' for Rift id={1}.".format(
                root_conduit.id,
                rift_id,
            ),
            "create_nexus_frame_for_rift",
        )
        return root_conduit

    def authorize_frame_link_for_rift(self, rift_id: str, frame_name: str) -> bool:
        """
        Internal

        Authorize one Rift frame-link request against Nexus-managed frame policy.

        Purpose:
            Keep Nexus as the owner of Nexus-managed frame topology rules when a
            live `Rift` tries to attach to a frame by name through its
            frame-link API.

        Args:
            rift_id:
                Requesting Rift id.
            frame_name:
                Target frame name being attached through the Rift frame-link
                path.

        Contract:
            - Returns `False` when the target frame is not Nexus-managed.
            - Returns `True` when the frame is Nexus-managed and accessible to
              the requesting Rift.
            - Raises `ValueError` when the frame is Nexus-managed but not
              accessible under the current topology mode.

        Returns:
            bool: True when the target frame is Nexus-managed and authorized.
        """
        return self._frame_manager.authorize_frame_link_for_rift(
            rift_id,
            frame_name,
        )

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
        return self._frame_manager.list_accessible_frame_names_for_rift(rift_id)

    def list_accessible_non_nexus_frame_names(self, rift_id: str) -> Tuple[str, ...]:
        """
        Internal

        Return the published non-Nexus frame names the requesting Rift may
        currently target.

        Args:
            rift_id:
                Requesting Rift id.

        Contract:
            - Requires Nexus to be enabled.
            - Starts from published descriptor truth only.
            - Excludes every manager-owned Nexus frame name.
            - Applies generic target-frame name policy and the requesting
              Rift's current room runtime requirements before returning names.

        Returns:
            Tuple[str, ...]: Accessible published non-Nexus frame names.
        """
        self.check_cleaned()
        self._require_enabled()
        rift = self._get_required_rift(rift_id)
        requested_space_type = rift.configuration.get_property("space_type")
        if not isinstance(requested_space_type, RiftSpaceType):
            raise TypeError("space_type must remain a RiftSpaceType.")
        nexus_managed_frame_names = set(self._frame_manager.list_frame_names())
        accessible_non_nexus_frame_names: List[str] = []
        for frame_name in self._frame_descriptor_manager.list_published_frame_names():
            if frame_name in nexus_managed_frame_names:
                continue
            try:
                self._validate_target_frame_names((frame_name,))
                self._validate_target_frame_runtime_requirements(
                    frame_name,
                    requested_space_type,
                )
            except ValueError:
                continue
            accessible_non_nexus_frame_names.append(frame_name)
        return tuple(accessible_non_nexus_frame_names)

    def check_for_aetheric_frame(self, frame_name: str) -> None:
        """
        Internal

        Drop Nexus-managed frame state when `Aether` is about to dispose a
        frame directly.

        Args:
            frame_name:
                Frame name about to be removed from `Aether`.

        Contract:
            - Short-circuits when Nexus is cleaned or missing the descriptor
              manager.
            - Drops manager-owned authored state when the frame is a
              Nexus-managed frame.
            - Falls back to descriptor/ACL cleanup for non-managed frames that
              still have passive Nexus-side state.
            - Logs and returns quietly when no managed or descriptor-owned
              state is present.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned or self._frame_descriptor_manager is None:
                return
            handled = self._frame_manager.handle_aether_frame_disposal(frame_name)
            if not handled:
                if self._frame_descriptor_manager._has_frame_descriptor(frame_name):
                    descriptor = self._frame_descriptor_manager._get_required_frame_descriptor(
                        frame_name
                    )
                    descriptor.clear_runtime_publication_state()
                acl_container_removed = self._frame_acl_manager._remove_frame_acl_container(
                    frame_name
                )
                if not acl_container_removed:
                    return
        self._logger.info(
            "Dropped Nexus managed frame '{0}' during Aether detach.".format(
                frame_name
            ),
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
        configuration = self.configuration
        if not configuration.get_property("allow_rift_creation"):
            raise ValueError("Rift creation is disabled.")
        if configuration.get_property("creation_token_required"):
            if creation_token != configuration.get_property("creation_token_value"):
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
        configuration = self.configuration
        if not configuration.get_property("allow_direct_rift_access"):
            raise ValueError("Direct Rift access is disabled.")
        if configuration.get_property("rift_access_token_required"):
            if access_token != configuration.get_property("rift_access_token_value"):
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
    ) -> AethericFrameConfiguration:
        """
        Internal

        Return the AR-relevant runtime posture for one target frame.

        Purpose:
            Resolve the dedicated `AethericFrameConfiguration` bound during
            conjure for the target frame; AR use requires that bound posture
            and there is no fallback derivation path.

        Args:
            target_frame_name:
                Target frame name being validated.

        Returns:
            AethericFrameConfiguration: Bound runtime posture exposing
            `system_state`, `ai_native_enabled`, and `rift_enabled`.

        Raises:
            ValueError: If the target frame does not exist or has no bound
                `AethericFrameConfiguration`.
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

        raise ValueError(
            "Target frame '{0}' must have a bound AethericFrameConfiguration for AR use.".format(
                target_frame_name
            )
        )

    def _get_required_target_frame_configuration(
            self,
            target_frame_name: str,
    ) -> SpellbookConfiguration:
        """
        Internal

        Return the bound Melder configuration for one target frame or raise.

        Args:
            target_frame_name:
                Target frame name being validated.

        Returns:
            SpellbookConfiguration: Bound Melder configuration.
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
        configuration = self.configuration
        denied_target_frame_names = configuration.get_property("denied_target_frame_names")
        allowed_target_frame_names = configuration.get_property("allowed_target_frame_names")
        if not isinstance(denied_target_frame_names, tuple) or not all(
                isinstance(frame_name, str)
                for frame_name in denied_target_frame_names
        ):
            raise TypeError(
                "denied_target_frame_names must remain a tuple[str, ...]."
            )
        if not isinstance(allowed_target_frame_names, tuple) or not all(
                isinstance(frame_name, str)
                for frame_name in allowed_target_frame_names
        ):
            raise TypeError(
                "allowed_target_frame_names must remain a tuple[str, ...]."
            )
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
        configuration = self.configuration
        allow_multiple_target_frames = configuration.get_property(
            "allow_multiple_target_frames"
        )
        if not isinstance(allow_multiple_target_frames, bool):
            raise TypeError(
                "allow_multiple_target_frames must remain a bool."
            )
        if not allow_multiple_target_frames:
            if len(self._target_frame_ref_counts) + len(unique_new_target_frames) > 1:
                raise ValueError("Multiple target frames are disabled.")
        max_target_frame_count = configuration.get_property(
            "max_target_frame_count"
        )
        if not isinstance(max_target_frame_count, int):
            raise TypeError("max_target_frame_count must remain an int.")
        if len(self._target_frame_ref_counts) + len(unique_new_target_frames) > max_target_frame_count:
            raise ValueError("Nexus target-frame cap has been reached.")

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
        configuration = self.configuration
        max_active_rift_count = configuration.get_property("max_active_rift_count")
        if not isinstance(max_active_rift_count, int):
            raise TypeError("max_active_rift_count must remain an int.")
        if max_active_rift_count == 0:
            return
        if len(self._rifts_by_id) >= max_active_rift_count:
            raise ValueError("Nexus active Rift cap has been reached.")

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

    def _get_required_rift(self, rift_id: str) -> Rift:
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
            Rift: Registered Rift object.
        """
        try:
            return self._rifts_by_id[rift_id]
        except KeyError as exc:
            raise ValueError("Rift with id '{0}' was not found.".format(rift_id)) from exc

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

    def _validate_frame_acl_configuration_against_descriptor(
            self,
            frame_name: str,
            configuration: FrameACLConfiguration,
            descriptor: FrameDescriptor,
    ) -> bool:
        """
        Internal

        Validate one frame ACL configuration against the supplied descriptor.

        Returns:
            bool: True when validation succeeds.
        """
        return self._frame_acl_manager._validate_frame_acl_configuration_against_descriptor(
            frame_name,
            configuration,
            descriptor,
        )

    def _increment_target_frame_ref_count(self, target_frame_name: str) -> None:
        """
        Internal

        Increment the internal target-frame ref count for the supplied frame.

        Returns:
            None.
        """
        self._increment_ref_count(self._target_frame_ref_counts, target_frame_name)

    def _reserve_target_frame(self, target_frame_name: str) -> None:
        """
        Internal

        Atomically reserve one target-frame slot: validate the target-frame
        budget and increment its ref count as one critical section.

        Contract:
            - Acquires the Nexus ``ClassVar`` ``_lock`` so the budget check and
              the ref-count increment cannot interleave. Two Rifts attaching
              distinct target frames therefore cannot both observe the same
              empty budget and both commit past ``max_target_frame_count`` under
              the free-threaded runtime (BUG-055).
            - Acquires only the Nexus lock; the caller must not hold a Rift lock
              across this call, so no cross-object lock ordering is introduced.
            - Re-entrant-safe because ``_lock`` is an ``RLock``.

        Args:
            target_frame_name:
                Target frame name being newly attached.

        Returns:
            None.

        Raises:
            ValueError:
                If the configured target-frame budget would be exceeded.
        """
        with self._lock:
            self._validate_target_frame_budget((target_frame_name,))
            self._increment_target_frame_ref_count(target_frame_name)

    def _remove_frame_acl_container(self, frame_name: str) -> bool:
        """
        Internal

        Remove the matching frame ACL container for a frame, if present.

        Args:
            frame_name:
                Frame name whose ACL container should be removed.

        Returns:
            bool: True when a container was removed.
        """
        return self._frame_acl_manager._remove_frame_acl_container(frame_name)

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

    def _clone_rift_configuration(self, configuration: RiftConfiguration) -> RiftConfiguration:
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




