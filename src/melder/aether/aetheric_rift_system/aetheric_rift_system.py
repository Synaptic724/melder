from typing import Dict, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.aetheric_rift_system.configuration.aetheric_rift_configuration import AethericRiftConfiguration
from melder.aether.aetheric_rift_system.configuration.aetheric_rift_system_configuration import (
    AethericRiftSystemConfiguration,
)
from melder.aether.aetheric_rift_system.configuration.aetheric_rift_system_frame_mode import (
    AethericRiftSystemFrameMode,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.interfaces.interfaces import (
    IAethericRift,
    IAethericRiftConfiguration,
    IAethericRiftState,
    IAethericRiftSystem,
    IAethericRiftSystemConfiguration,
)


class AethericRiftSystem(Cleanable, IAethericRiftSystem):
    """
    Internal

    Canonical ownership root for AethericRift runtime objects.

    Purpose:
        Provide one subsystem-owned registry for Rift instances and their
        canonical `AethericRiftState` objects while keeping `Aether` as a host
        and facade instead of the direct owner of those dictionaries.

    Contract:
        - Owns the authoritative Rift and RiftState dictionaries.
        - Distinguishes configuration lifecycle from runtime enablement.
        - May exist in an unconfigured state until a user explicitly engages
          ARS and installs a system configuration.
        - Enforces creation/access policy, target-frame governance, and
          internal system-frame topology only after configuration is installed.

    Lifecycle:
        Hosted by `Aether`. Cleanup clears any installed configuration, owned
        registries, and all live Rift/state references.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_configuration",
        "_configured",
        "_enabled",
        "_rifts_by_id",
        "_rift_states_by_id",
        "_rift_ids_by_name",
        "_target_frame_ref_counts",
        "_system_frame_ref_counts",
    ]

    def __init__(
            self,
            *,
            configuration: Optional[IAethericRiftSystemConfiguration] = None,
    ) -> None:
        """
        Internal

        Initialize the hosted AR system.

        Args:
            configuration:
                Optional preinstalled system configuration. When omitted, the
                AR system starts unconfigured and disabled until a user engages
                it explicitly.

        Returns:
            None.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._configuration: Optional[IAethericRiftSystemConfiguration] = configuration
        self._configured: bool = configuration is not None
        self._enabled: bool = False
        self._rifts_by_id: Dict[str, IAethericRift] = {}
        self._rift_states_by_id: Dict[str, IAethericRiftState] = {}
        self._rift_ids_by_name: Dict[str, str] = {}
        self._target_frame_ref_counts: Dict[str, int] = {}
        self._system_frame_ref_counts: Dict[str, int] = {}

    @property
    def id(self) -> str:
        """
        Purpose:
            Return the stable identifier for this AR system instance.

        Returns:
            str: The AR system id.
        """
        self.check_cleaned()
        return self._id

    @property
    def configuration(self) -> IAethericRiftSystemConfiguration:
        """
        Purpose:
            Return the installed AR system configuration.

        Returns:
            IAethericRiftSystemConfiguration: Installed system configuration.

        Raises:
            RuntimeError: If ARS has not been configured yet.
        """
        self._require_configured()
        return self._configuration

    @property
    def is_configured(self) -> bool:
        """
        Purpose:
            Return whether ARS currently has an installed configuration.

        Returns:
            bool: True when a configuration has been installed.
        """
        self.check_cleaned()
        return self._configured

    @property
    def is_enabled(self) -> bool:
        """
        Purpose:
            Return whether the hosted AR system is currently enabled.

        Returns:
            bool: True when AR runtime operations are enabled.
        """
        self.check_cleaned()
        return self._enabled

    def cleanup(self) -> None:
        """
        Internal

        Idempotently cleanup the AR system registry and owned references.

        Contract:
            - Cleans all registered Rift shells and canonical state objects.
            - Cleans any installed system configuration.
            - Clears configuration/runtime flags and all registry maps.

        Returns:
            None.
        """
        if self._cleaned:
            return

        self._cleaned = True
        for rift in self._rifts_by_id.values():
            rift.cleanup()
        for state in self._rift_states_by_id.values():
            state.cleanup()
        if self._configuration is not None:
            self._configuration.cleanup()
        self._configuration = None
        self._configured = None
        self._enabled = None
        self._rifts_by_id.clear()
        self._rift_states_by_id.clear()
        self._rift_ids_by_name.clear()
        self._target_frame_ref_counts.clear()
        self._system_frame_ref_counts.clear()
        self._rifts_by_id = None
        self._rift_states_by_id = None
        self._rift_ids_by_name = None
        self._target_frame_ref_counts = None
        self._system_frame_ref_counts = None
        self._id = None

    def create_system_configuration(self) -> IAethericRiftSystemConfiguration:
        """
        Internal

        Create a fresh mutable AR system configuration initialized with the
        standard master-user defaults.

        Contract:
            - Returns a new standalone configuration object.
            - Does not install the configuration into ARS.
            - Does not configure or enable the system by itself.

        Returns:
            IAethericRiftSystemConfiguration: Fresh mutable system config.
        """
        self.check_cleaned()
        return AethericRiftSystemConfiguration().with_defaults()

    def enable(
            self,
            configuration: Optional[IAethericRiftSystemConfiguration] = None,
    ) -> None:
        """
        Internal

        Install a configuration if needed and enable AR runtime operations.

        Args:
            configuration:
                Optional configuration to install during enablement.

        Contract:
            - Installs the provided configuration when one is supplied.
            - Requires ARS to be configured after the optional installation
              step.
            - Finalizes the installed configuration before enabling runtime
              operations.

        Returns:
            None.

        Raises:
            RuntimeError: If ARS has no installed configuration and none is
                provided.
        """
        self.check_cleaned()
        if configuration is not None:
            self._configuration = configuration
            self._configured = True
        self._require_configured()
        if not self._configuration.frozen:
            self._configuration.finalize()
        self._enabled = True

    def disable(self) -> None:
        """
        Internal

        Disable AR runtime operations while leaving installed configuration and
        registries intact.

        Contract:
            - Leaves `_configured` unchanged.
            - Does not clear installed configuration or registered objects.

        Returns:
            None.
        """
        self.check_cleaned()
        self._enabled = False

    def create_rift_configuration(self) -> IAethericRiftConfiguration:
        """
        Internal

        Create a per-Rift configuration initialized from the installed system
        defaults.

        Contract:
            - Requires ARS to be configured.
            - Copies the installed system defaults into a fresh per-Rift config.
            - Does not register or enable any Rift by itself.

        Returns:
            IAethericRiftConfiguration: Mutable per-Rift configuration.
        """
        self._require_configured()
        config = AethericRiftConfiguration().with_defaults()
        config.with_target_frame_name(self._configuration.get_property("default_target_frame_name"))
        config.with_space_type(self._configuration.get_property("default_space_type"))
        config.with_auto_activate_on_program(self._configuration.get_property("default_auto_activate_on_program"))
        config.with_auto_create_space(self._configuration.get_property("default_auto_create_space"))
        config.with_validation_mode(self._configuration.get_property("default_validation_mode"))
        return config

    def create_rift_state(
            self,
            *,
            configuration: Optional[IAethericRiftConfiguration] = None,
            rift_id: Optional[str] = None,
            rift_name: Optional[str] = None,
            local_conduit_id: Optional[str] = None,
            active_space_id: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> IAethericRiftState:
        """
        Internal

        Create canonical state for one Rift.

        Args:
            configuration:
                Optional per-Rift configuration override. When omitted, a fresh
                per-Rift configuration is derived from the installed system
                defaults.
            rift_id:
                Optional explicit Rift id.
            rift_name:
                Optional stable Rift name.
            local_conduit_id:
                Optional local conduit id for the canonical state.
            active_space_id:
                Optional active room id for the canonical state.
            metadata:
                Optional Rift-level metadata map.

        Contract:
            - Requires ARS to be configured and enabled.
            - Finalizes the per-Rift configuration before building state.
            - Validates target-frame policy against the installed ARS config.
            - Derives the internal system frame anchor from the current
              system-frame topology mode.

        Returns:
            IAethericRiftState: Newly created canonical state.
        """
        self._require_enabled()
        from melder.aether.aetheric_rift_system.aetheric_rift_state.aetheric_rift_state import AethericRiftState

        canonical_rift_id = rift_id or IDBuilder.create_id()
        bound_configuration = configuration or self.create_rift_configuration()
        if not bound_configuration.frozen:
            bound_configuration.finalize()

        self._validate_target_frame_configuration(bound_configuration)

        return AethericRiftState(
            configuration=bound_configuration,
            system_frame_name=self._determine_system_frame_name(canonical_rift_id),
            rift_id=canonical_rift_id,
            rift_name=rift_name,
            local_conduit_id=local_conduit_id,
            active_space_id=active_space_id,
            metadata=metadata,
        )

    def create_rift(
            self,
            *,
            configuration: Optional[IAethericRiftConfiguration] = None,
            rift_name: Optional[str] = None,
            rift_id: Optional[str] = None,
            local_conduit_id: Optional[str] = None,
            active_space_id: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
            creation_token: Optional[str] = None,
    ) -> IAethericRift:
        """
        Internal

        Create, program, and register a new Rift.

        Args:
            configuration:
                Optional per-Rift configuration override.
            rift_name:
                Optional stable Rift name.
            rift_id:
                Optional explicit Rift id.
            local_conduit_id:
                Optional local conduit id to store on the canonical state.
            active_space_id:
                Optional active room id to store on the canonical state.
            metadata:
                Optional Rift-level metadata.
            creation_token:
                Optional caller-supplied creation token used when creation is
                token-gated.

        Contract:
            - Requires ARS to be configured and enabled.
            - Enforces the process-wide creation policy before state/shell
              creation.
            - Creates canonical state first, then the public shell, then
              programs the shell against that state.

        Returns:
            IAethericRift: Live/programmed Rift shell.
        """
        self._require_rift_creation_allowed(creation_token)
        from melder.aether.aetheric_rift_system.aetheric_rift.aetheric_rift import AethericRift

        state = self.create_rift_state(
            configuration=configuration,
            rift_id=rift_id,
            rift_name=rift_name,
            local_conduit_id=local_conduit_id,
            active_space_id=active_space_id,
            metadata=metadata,
        )
        rift = AethericRift(
            self,
            rift_name=rift_name,
            rift_id=state.rift_id,
        )
        return self.program_rift(rift, state, creation_token=creation_token)

    def program_rift(
            self,
            rift: IAethericRift,
            state: IAethericRiftState,
            *,
            creation_token: Optional[str] = None,
    ) -> IAethericRift:
        """
        Internal

        Program a Rift shell by binding canonical state and registering it.

        Args:
            rift:
                Public Rift shell to bind and register.
            state:
                Canonical Rift state to bind into the shell.
            creation_token:
                Optional caller-supplied creation token used when creation is
                token-gated.

        Contract:
            - Requires ARS to be configured and enabled.
            - Enforces the same creation policy used by direct Rift creation.
            - Binds state into the shell, updates lifecycle flags, and
              registers the resulting live Rift.

        Returns:
            IAethericRift: Live/programmed Rift shell.
        """
        self._require_rift_creation_allowed(creation_token)
        rift.bind_state(state)
        state.mark_registered()
        if state.configuration.get_property("auto_activate_on_program"):
            state.mark_active()
        self.add_rift(rift, state)
        return rift

    def register_external_rift(
            self,
            rift: IAethericRift,
            state: Optional[IAethericRiftState] = None,
            *,
            configuration: Optional[IAethericRiftConfiguration] = None,
            local_conduit_id: Optional[str] = None,
            active_space_id: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
            creation_token: Optional[str] = None,
    ) -> IAethericRift:
        """
        Internal

        Program and register a Rift shell that was created externally.

        Args:
            rift:
                Externally created public Rift shell.
            state:
                Optional canonical state to bind. When omitted, ARS creates one.
            configuration:
                Optional per-Rift configuration override used only when state is
                not supplied.
            local_conduit_id:
                Optional local conduit id stored on created state.
            active_space_id:
                Optional active room id stored on created state.
            metadata:
                Optional Rift-level metadata used when state is created.
            creation_token:
                Optional caller-supplied creation token used when creation is
                token-gated.

        Contract:
            - Requires ARS to be configured and enabled.
            - Requires external registration to be allowed by policy.
            - Creates state when needed, then programs the shell through the
              normal registration path.

        Returns:
            IAethericRift: Live/programmed Rift shell.
        """
        self._require_rift_creation_allowed(creation_token)
        if not self._configuration.get_property("allow_external_rift_registration"):
            raise ValueError("External Rift registration is disabled.")
        bound_state = state or self.create_rift_state(
            configuration=configuration,
            rift_id=rift.id,
            rift_name=rift.rift_name,
            local_conduit_id=local_conduit_id,
            active_space_id=active_space_id,
            metadata=metadata,
        )
        return self.program_rift(rift, bound_state, creation_token=creation_token)

    def add_rift(self, rift: IAethericRift, state: IAethericRiftState) -> None:
        """
        Internal

        Register one Rift and its canonical state.

        Args:
            rift:
                Public Rift shell to register.
            state:
                Canonical Rift state bound to that shell.

        Contract:
            - Requires ARS to be configured and enabled.
            - Verifies id consistency and live-state binding before
              registration.
            - Enforces target-frame, system-frame, and active-Rift budget
              constraints before mutating the registries.

        Returns:
            None.

        Raises:
            ValueError: If ids conflict, the Rift is inert, or any registry or
                budget invariant is violated.
        """
        self._require_enabled()
        if rift.id != state.rift_id:
            raise ValueError("rift.id and state.rift_id must match.")
        if not rift.has_state:
            raise ValueError("Rift must have canonical state bound before registration.")
        if rift.id in self._rifts_by_id:
            raise ValueError("Rift with id '{0}' already exists.".format(rift.id))
        if state.rift_id in self._rift_states_by_id:
            raise ValueError("RiftState with id '{0}' already exists.".format(state.rift_id))
        if rift.rift_name and rift.rift_name in self._rift_ids_by_name:
            raise ValueError("Rift name '{0}' already exists.".format(rift.rift_name))
        self._validate_target_frame_budget(state.target_frame_name)
        self._validate_system_frame_budget(state.system_frame_name)
        self._validate_active_rift_budget()

        self._rifts_by_id[rift.id] = rift
        self._rift_states_by_id[state.rift_id] = state
        if rift.rift_name:
            self._rift_ids_by_name[rift.rift_name] = rift.id
        self._increment_ref_count(self._target_frame_ref_counts, state.target_frame_name)
        self._increment_ref_count(self._system_frame_ref_counts, state.system_frame_name)

    def get_rift(
            self,
            rift_id: str,
            access_token: Optional[str] = None,
    ) -> IAethericRift:
        """
        Internal

        Return a registered Rift by canonical id.

        Args:
            rift_id:
                Canonical Rift id.
            access_token:
                Optional direct-access token.

        Contract:
            - Requires ARS to be configured and enabled.
            - Enforces direct Rift access policy before lookup.

        Returns:
            IAethericRift: Registered Rift shell.
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
    ) -> IAethericRift:
        """
        Internal

        Resolve a Rift by name through the paired name -> id index.

        Args:
            rift_name:
                Stable Rift name.
            access_token:
                Optional direct-access token.

        Contract:
            - Requires ARS to be configured and enabled.
            - Enforces direct Rift access policy before lookup.

        Returns:
            IAethericRift: Registered Rift shell.
        """
        self._require_rift_access_allowed(access_token)
        try:
            rift_id = self._rift_ids_by_name[rift_name]
        except KeyError as exc:
            raise ValueError("Rift with name '{0}' was not found.".format(rift_name)) from exc
        return self.get_rift(rift_id, access_token=access_token)

    def get_rift_state(
            self,
            rift_id: str,
            access_token: Optional[str] = None,
    ) -> IAethericRiftState:
        """
        Internal

        Return canonical Rift state by Rift id.

        Args:
            rift_id:
                Canonical Rift id.
            access_token:
                Optional state-access token.

        Contract:
            - Requires ARS to be configured and enabled.
            - Enforces direct state access policy before lookup.

        Returns:
            IAethericRiftState: Registered canonical Rift state.
        """
        self._require_state_access_allowed(access_token)
        try:
            return self._rift_states_by_id[rift_id]
        except KeyError as exc:
            raise ValueError("RiftState with id '{0}' was not found.".format(rift_id)) from exc

    def has_rift(self, rift_id: str) -> bool:
        """
        Internal

        Return whether the Rift id is registered.

        Args:
            rift_id:
                Canonical Rift id.

        Contract:
            Requires ARS to be configured, but not enabled.

        Returns:
            bool: True when the Rift is currently registered.
        """
        self._require_configured()
        return rift_id in self._rifts_by_id

    def remove_rift(self, rift_id: str) -> None:
        """
        Internal

        Remove one Rift and its canonical state from the registry.

        Args:
            rift_id:
                Canonical Rift id.

        Contract:
            - Requires ARS to be configured and enabled.
            - Updates target/system-frame reference counts when canonical state
              is removed.

        Returns:
            None.
        """
        self._require_enabled()
        try:
            rift = self._rifts_by_id.pop(rift_id)
        except KeyError as exc:
            raise ValueError("Rift with id '{0}' was not found.".format(rift_id)) from exc

        state = self._rift_states_by_id.pop(rift_id, None)
        if rift.rift_name:
            self._rift_ids_by_name.pop(rift.rift_name, None)
        if state is not None:
            self._decrement_ref_count(self._target_frame_ref_counts, state.target_frame_name)
            self._decrement_ref_count(self._system_frame_ref_counts, state.system_frame_name)

    def list_rift_ids(self) -> list[str]:
        """
        Internal

        Return the currently registered Rift ids.

        Contract:
            Requires ARS to be configured and enabled.

        Returns:
            list[str]: Snapshot of registered Rift ids.
        """
        self._require_enabled()
        return list(self._rifts_by_id.keys())

    def _require_configured(self) -> None:
        """
        Internal

        Require that ARS currently has an installed configuration.

        Returns:
            None.

        Raises:
            RuntimeError: If ARS has not been configured yet.
        """
        self.check_cleaned()
        if not self._configured or self._configuration is None:
            raise RuntimeError("AethericRiftSystem is not configured.")

    def _require_enabled(self) -> None:
        """
        Internal

        Require that AR runtime operations are enabled.

        Returns:
            None.

        Raises:
            RuntimeError: If the AR system is currently disabled.
        """
        self._require_configured()
        if not self._enabled:
            raise RuntimeError("AethericRiftSystem is disabled.")

    def _require_rift_creation_allowed(self, creation_token: Optional[str]) -> None:
        """
        Internal

        Enforce process-wide Rift creation/programming policy.

        Args:
            creation_token:
                Optional caller-supplied creation token.

        Returns:
            None.

        Raises:
            RuntimeError: If ARS is not configured or enabled.
            ValueError: If creation is disabled or token validation fails.
        """
        self._require_enabled()
        if not self._configuration.get_property("allow_rift_creation"):
            raise ValueError("AethericRift creation is disabled.")
        if self._configuration.get_property("creation_token_required"):
            if creation_token != self._configuration.get_property("creation_token_value"):
                raise ValueError("Valid creation token is required.")

    def _require_rift_access_allowed(self, access_token: Optional[str]) -> None:
        """
        Internal

        Enforce direct live-Rift retrieval policy.

        Args:
            access_token:
                Optional caller-supplied Rift access token.

        Returns:
            None.

        Raises:
            RuntimeError: If ARS is not configured or enabled.
            ValueError: If direct Rift access is disabled or token validation
                fails.
        """
        self._require_enabled()
        if not self._configuration.get_property("allow_direct_rift_access"):
            raise ValueError("Direct Rift access is disabled.")
        if self._configuration.get_property("rift_access_token_required"):
            if access_token != self._configuration.get_property("rift_access_token_value"):
                raise ValueError("Valid Rift access token is required.")

    def _require_state_access_allowed(self, access_token: Optional[str]) -> None:
        """
        Internal

        Enforce direct canonical Rift-state retrieval policy.

        Args:
            access_token:
                Optional caller-supplied state access token.

        Returns:
            None.

        Raises:
            RuntimeError: If ARS is not configured or enabled.
            ValueError: If direct state access is disabled or token validation
                fails.
        """
        self._require_enabled()
        if not self._configuration.get_property("allow_direct_state_access"):
            raise ValueError("Direct Rift state access is disabled.")
        if self._configuration.get_property("state_access_token_required"):
            if access_token != self._configuration.get_property("state_access_token_value"):
                raise ValueError("Valid state access token is required.")

    def _validate_target_frame_configuration(
            self,
            configuration: IAethericRiftConfiguration,
    ) -> None:
        """
        Internal

        Validate one per-Rift target-frame configuration against the installed
        system policy.

        Args:
            configuration:
                Per-Rift configuration being programmed.

        Returns:
            None.

        Raises:
            ValueError: If target-frame override is disabled or the requested
                frame is not permitted.
        """
        requested_target_frame_name = configuration.get_property("target_frame_name")
        default_target_frame_name = self._configuration.get_property("default_target_frame_name")
        if not self._configuration.get_property("allow_target_frame_override"):
            if requested_target_frame_name != default_target_frame_name:
                raise ValueError("Target frame override is disabled.")
        self._validate_target_frame_name(requested_target_frame_name)

    def _validate_target_frame_name(self, target_frame_name: str) -> None:
        """
        Internal

        Validate one target frame name against allow-list and deny-list policy.

        Args:
            target_frame_name:
                Candidate target frame name.

        Returns:
            None.

        Raises:
            ValueError: If the frame is denied or not in the allow-list.
        """
        denied_target_frame_names = self._configuration.get_property("denied_target_frame_names")
        allowed_target_frame_names = self._configuration.get_property("allowed_target_frame_names")
        if target_frame_name in denied_target_frame_names:
            raise ValueError("Target frame '{0}' is denied by AR system policy.".format(target_frame_name))
        if allowed_target_frame_names and target_frame_name not in allowed_target_frame_names:
            raise ValueError("Target frame '{0}' is not allowed by AR system policy.".format(target_frame_name))

    def _validate_target_frame_budget(self, target_frame_name: str) -> None:
        """
        Internal

        Validate distinct target-frame budget before registration.

        Args:
            target_frame_name:
                Candidate target frame name.

        Returns:
            None.

        Raises:
            ValueError: If multiple target frames are disabled or the cap is
                exceeded.
        """
        if target_frame_name in self._target_frame_ref_counts:
            return
        if not self._configuration.get_property("allow_multiple_target_frames"):
            if len(self._target_frame_ref_counts) >= 1:
                raise ValueError("Multiple target frames are disabled.")
        if len(self._target_frame_ref_counts) >= self._configuration.get_property("max_target_frame_count"):
            raise ValueError("AethericRiftSystem target-frame cap has been reached.")

    def _validate_system_frame_budget(self, system_frame_name: str) -> None:
        """
        Internal

        Validate internal AR system-frame budget before registration.

        Args:
            system_frame_name:
                Candidate internal system frame name.

        Returns:
            None.

        Raises:
            ValueError: If the system-frame cap is exceeded.
        """
        if system_frame_name in self._system_frame_ref_counts:
            return
        if len(self._system_frame_ref_counts) >= self._configuration.get_property("max_system_frame_count"):
            raise ValueError("AethericRiftSystem internal system-frame cap has been reached.")

    def _validate_active_rift_budget(self) -> None:
        """
        Internal

        Validate active Rift budget before registration.

        Returns:
            None.

        Raises:
            ValueError: If the active-Rift cap is exceeded.
        """
        max_active_rift_count = self._configuration.get_property("max_active_rift_count")
        if max_active_rift_count == 0:
            return
        if len(self._rifts_by_id) >= max_active_rift_count:
            raise ValueError("AethericRiftSystem active Rift cap has been reached.")

    def _determine_system_frame_name(self, rift_id: str) -> str:
        """
        Internal

        Determine the internal AR system frame name for one Rift.

        Args:
            rift_id:
                Canonical Rift id used when the topology mode is
                `one_per_workspace`.

        Returns:
            str: Internal system frame name selected from the current topology
            mode.
        """
        system_frame_mode = self._configuration.get_property("system_frame_mode")
        default_system_frame_name = self._configuration.get_property("default_system_frame_name")
        if system_frame_mode == AethericRiftSystemFrameMode.one_per_workspace:
            return "{0}:{1}".format(default_system_frame_name, rift_id)
        return default_system_frame_name

    def _increment_ref_count(self, ref_counts: Dict[str, int], key: str) -> None:
        """
        Internal

        Increment one direct dict-backed reference count.

        Args:
            ref_counts:
                Reference-count mapping to mutate.
            key:
                Key whose count should be incremented.

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

        Decrement one direct dict-backed reference count and remove the key when
        it reaches zero.

        Args:
            ref_counts:
                Reference-count mapping to mutate.
            key:
                Key whose count should be decremented.

        Returns:
            None.
        """
        if key not in ref_counts:
            return
        if ref_counts[key] <= 1:
            ref_counts.pop(key, None)
            return
        ref_counts[key] = ref_counts[key] - 1
