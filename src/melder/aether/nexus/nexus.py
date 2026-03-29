import threading
from typing import Dict, Optional, Sequence, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.configuration.rift_configuration import RiftConfiguration
from melder.aether.nexus.configuration.nexus_configuration import (
    NexusConfiguration,
)
from melder.aether.nexus.configuration.nexus_frame_mode import (
    NexusFrameMode,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.interfaces.interfaces import (
    INexus,
    INexusConfiguration,
    IRift,
    IRiftConfiguration,
)


class Nexus(Cleanable, INexus):
    """
    Internal

    Public singleton root for Rift-domain state and lifecycle.

    Purpose:
        Provide one process-wide registry and policy/configuration root for
        live `Rift` objects while keeping `Aether` as hidden substrate rather
        than the public API root for Rift work.

    Contract:
        - Singleton.
        - Owns Nexus configuration, configured/enabled state, and live Rift
          registries.
        - Creates `Rift` objects from policy-approved config and frame-name
          assignments.
        - Does not target `Aether` operationally; it works only in terms of
          frame names and policy.

    Lifecycle:
        Created eagerly by `Aether` at package/runtime boot, but starts
        unconfigured and disabled until a user explicitly engages it.
    """

    __melder_internal__ = _mrg.sentinel
    _instance = None
    _singleton_lock = threading.RLock()
    _initialized = False
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_configuration",
        "_configured",
        "_enabled",
        "_rifts_by_id",
        "_rift_ids_by_name",
        "_target_frame_ref_counts",
        "_system_frame_ref_counts",
    ]

    def __new__(cls):
        """
        Ensure `Nexus` behaves as a singleton.

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
            configuration: Optional[INexusConfiguration] = None,
    ) -> None:
        """
        Internal

        Initialize the singleton Rift-domain root.

        Args:
            configuration:
                Optional preinstalled Nexus configuration. When omitted, Nexus
                starts unconfigured and disabled.

        Returns:
            None.
        """
        if not Nexus._initialized:
            super().__init__()
            self._id: str = IDBuilder.create_id()
            self._lock: threading.RLock = threading.RLock()
            self._configuration: Optional[INexusConfiguration] = configuration
            self._configured: bool = configuration is not None
            self._enabled: bool = False
            self._rifts_by_id: Dict[str, IRift] = {}
            self._rift_ids_by_name: Dict[str, str] = {}
            self._target_frame_ref_counts: Dict[str, int] = {}
            self._system_frame_ref_counts: Dict[str, int] = {}
            Nexus._initialized = True

    @classmethod
    def _reset_singleton_for_tests(cls) -> None:
        """
        Reset the Nexus singleton for test isolation.

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

    def cleanup(self) -> None:
        """
        Internal

        Idempotently cleanup Nexus-owned state and reset singleton status.

        Contract:
            - Cleans all registered Rifts.
            - Cleans any installed configuration.
            - Clears registries, ref counts, and configured/enabled flags.
            - Resets Nexus singleton state so tests can reinitialize cleanly.

        Returns:
            None.
        """
        if self._cleaned:
            return
        lock = self._lock
        with lock:
            if self._cleaned:
                return
            self._cleaned = True
            for rift in self._rifts_by_id.values():
                rift.cleanup()
            if self._configuration is not None:
                self._configuration.cleanup()

            self._configuration = None
            self._configured = None
            self._enabled = None
            self._rifts_by_id.clear()
            self._rift_ids_by_name.clear()
            self._target_frame_ref_counts.clear()
            self._system_frame_ref_counts.clear()
            self._rifts_by_id = None
            self._rift_ids_by_name = None
            self._target_frame_ref_counts = None
            self._system_frame_ref_counts = None
            self._id = None
        self._lock = None
        with Nexus._singleton_lock:
            Nexus._instance = None
            Nexus._initialized = False

    def create_system_configuration(self) -> INexusConfiguration:
        """
        Internal

        Create a fresh mutable Nexus configuration with default values.

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
        Internal

        Install configuration if needed and enable Nexus operations.

        Args:
            configuration:
                Optional replacement configuration.

        Returns:
            None.

        Raises:
            RuntimeError: If Nexus has no installed configuration.
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

    def disable(self) -> None:
        """
        Internal

        Disable Rift operations without discarding configuration or registry
        state.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._enabled = False

    def create_rift_configuration(self) -> IRiftConfiguration:
        """
        Internal

        Create a per-Rift configuration initialized from Nexus defaults.

        Returns:
            IRiftConfiguration: Mutable per-Rift configuration.

        Raises:
            RuntimeError: If Nexus is not configured.
        """
        self._require_configured()
        configuration = RiftConfiguration().with_defaults()
        configuration.with_target_frame_name(self._configuration.get_property("default_target_frame_name"))
        configuration.with_space_type(self._configuration.get_property("default_space_type"))
        configuration.with_auto_activate_on_program(self._configuration.get_property("default_auto_activate_on_program"))
        configuration.with_auto_create_space(self._configuration.get_property("default_auto_create_space"))
        configuration.with_validation_mode(self._configuration.get_property("default_validation_mode"))
        return configuration

    def create_rift(
            self,
            *,
            configuration: Optional[IRiftConfiguration] = None,
            rift_name: Optional[str] = None,
            rift_id: Optional[str] = None,
            local_conduit_id: Optional[str] = None,
            active_space_id: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
            creation_token: Optional[str] = None,
    ) -> IRift:
        """
        Internal

        Create and register one live Rift object.

        Args:
            configuration:
                Optional per-Rift configuration override.
            rift_name:
                Optional stable Rift name.
            rift_id:
                Optional explicit Rift id.
            local_conduit_id:
                Optional live local conduit id to seed on the Rift.
            active_space_id:
                Optional active room id to seed on the Rift.
            metadata:
                Optional Rift-level metadata.
            creation_token:
                Optional creation token when creation is token-gated.

        Returns:
            IRift: Newly created and registered live Rift.
        """
        self._require_rift_creation_allowed(creation_token)
        from melder.aether.nexus.rift.rift import Rift

        canonical_rift_id = rift_id or IDBuilder.create_id()
        bound_configuration = configuration or self.create_rift_configuration()
        if not bound_configuration.frozen:
            bound_configuration.finalize()

        self._validate_target_frame_configuration(bound_configuration)
        system_frame_name = self._determine_system_frame_name(canonical_rift_id)
        target_frame_name = bound_configuration.get_property("target_frame_name")

        with self._lock:
            rift = Rift(
                self,
                configuration=bound_configuration,
                system_frame_names=(system_frame_name,),
                default_system_frame_name=system_frame_name,
                target_frame_names=(target_frame_name,),
                default_target_frame_name=target_frame_name,
                rift_name=rift_name,
                rift_id=canonical_rift_id,
                local_conduit_id=local_conduit_id,
                active_space_id=active_space_id,
                metadata=metadata,
            )
            if bound_configuration.get_property("auto_activate_on_program"):
                rift.mark_active()
            self.add_rift(rift)
            return rift

    def add_rift(self, rift: IRift) -> None:
        """
        Internal

        Register one already-constructed Rift into Nexus.

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

            self._validate_target_frame_budget(rift.target_frame_names)
            self._validate_system_frame_budget(rift.system_frame_names)
            self._validate_active_rift_budget()

            self._rifts_by_id[rift.id] = rift
            if rift.rift_name:
                self._rift_ids_by_name[rift.rift_name] = rift.id
            for target_frame_name in rift.target_frame_names:
                self._increment_ref_count(self._target_frame_ref_counts, target_frame_name)
            for system_frame_name in rift.system_frame_names:
                self._increment_ref_count(self._system_frame_ref_counts, system_frame_name)
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

        Returns:
            bool: True when registered.
        """
        self._require_configured()
        return rift_id in self._rifts_by_id

    def remove_rift(self, rift_id: str) -> None:
        """
        Internal

        Remove one Rift from Nexus and update frame ref counts.

        Args:
            rift_id:
                Canonical Rift id.

        Returns:
            None.
        """
        self._require_enabled()
        with self._lock:
            try:
                rift = self._rifts_by_id.pop(rift_id)
            except KeyError as exc:
                raise ValueError("Rift with id '{0}' was not found.".format(rift_id)) from exc

            if rift.rift_name:
                self._rift_ids_by_name.pop(rift.rift_name, None)
            for target_frame_name in rift.target_frame_names:
                self._decrement_ref_count(self._target_frame_ref_counts, target_frame_name)
            for system_frame_name in rift.system_frame_names:
                self._decrement_ref_count(self._system_frame_ref_counts, system_frame_name)

    def list_rift_ids(self) -> list[str]:
        """
        Internal

        Return the currently registered Rift ids.

        Returns:
            list[str]: Snapshot of registered ids.
        """
        self._require_enabled()
        return list(self._rifts_by_id.keys())

    def _require_configured(self) -> None:
        """
        Internal

        Require that Nexus has an installed configuration.

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

        Returns:
            None.
        """
        self._require_enabled()
        if not self._configuration.get_property("allow_direct_rift_access"):
            raise ValueError("Direct Rift access is disabled.")
        if self._configuration.get_property("rift_access_token_required"):
            if access_token != self._configuration.get_property("rift_access_token_value"):
                raise ValueError("Valid Rift access token is required.")

    def _validate_target_frame_configuration(
            self,
            configuration: IRiftConfiguration,
    ) -> None:
        """
        Internal

        Validate one per-Rift target-frame configuration against Nexus policy.

        Args:
            configuration:
                Per-Rift configuration being applied.

        Returns:
            None.
        """
        requested_target_frame_name = configuration.get_property("target_frame_name")
        default_target_frame_name = self._configuration.get_property("default_target_frame_name")
        if not self._configuration.get_property("allow_target_frame_override"):
            if requested_target_frame_name != default_target_frame_name:
                raise ValueError("Target frame override is disabled.")
        self._validate_target_frame_names((requested_target_frame_name,))

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

    def _validate_system_frame_budget(self, system_frame_names: Sequence[str]) -> None:
        """
        Internal

        Validate internal system-frame budget before registration.

        Args:
            system_frame_names:
                Candidate system frame names on the Rift.

        Returns:
            None.
        """
        unique_new_system_frames = []
        for system_frame_name in system_frame_names:
            if system_frame_name not in self._system_frame_ref_counts and system_frame_name not in unique_new_system_frames:
                unique_new_system_frames.append(system_frame_name)
        if not unique_new_system_frames:
            return
        if len(self._system_frame_ref_counts) + len(unique_new_system_frames) > self._configuration.get_property(
                "max_system_frame_count"):
            raise ValueError("Nexus internal system-frame cap has been reached.")

    def _validate_active_rift_budget(self) -> None:
        """
        Internal

        Validate active-Rift budget before registration.

        Returns:
            None.
        """
        max_active_rift_count = self._configuration.get_property("max_active_rift_count")
        if max_active_rift_count == 0:
            return
        if len(self._rifts_by_id) >= max_active_rift_count:
            raise ValueError("Nexus active Rift cap has been reached.")

    def _determine_system_frame_name(self, rift_id: str) -> str:
        """
        Internal

        Determine the internal system frame name for one Rift from Nexus
        topology policy.

        Args:
            rift_id:
                Canonical Rift id used when the topology mode is
                `one_per_workspace`.

        Returns:
            str: Assigned system frame name.
        """
        system_frame_mode = self._configuration.get_property("system_frame_mode")
        default_system_frame_name = self._configuration.get_property("default_system_frame_name")
        if system_frame_mode == NexusFrameMode.one_per_workspace:
            return "{0}:{1}".format(default_system_frame_name, rift_id)
        return default_system_frame_name

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
