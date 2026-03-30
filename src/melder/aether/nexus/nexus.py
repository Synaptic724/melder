import threading
from typing import Dict, List, Optional, Sequence, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.nexus_frame_record import NexusFrameRecord
from melder.aether.nexus.configuration.rift_configuration import RiftConfiguration
from melder.aether.nexus.configuration.nexus_configuration import (
    NexusConfiguration,
)
from melder.aether.nexus.configuration.nexus_frame_mode import (
    NexusFrameMode,
)
from melder.aether.nexus.rift_space.rift_event_configuration import RiftEventConfiguration
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.interfaces.interfaces import (
    IAether,
    IAethericFrame,
    INexus,
    INexusConfiguration,
    IRiftEventConfiguration,
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
        - Holds the hidden `Aether` substrate reference needed for Nexus-owned
          frame realization and disposal.
        - Owns Nexus configuration, configured/enabled state, and live Rift
          registries.
        - Creates `Rift` objects from policy-approved config and frame-name
          assignments.
        - Owns the lifecycle of Nexus-managed internal frames through
          `NexusFrameRecord` objects.

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
        "_aether",
        "_configuration",
        "_configured",
        "_enabled",
        "_rifts_by_id",
        "_rift_ids_by_name",
        "_next_default_rift_number",
        "_next_indexed_nexus_frame_number",
        "_rift_profiles_by_name",
        "_target_frame_ref_counts",
        "_nexus_frames_by_name",
    ]

    def __new__(cls, *args, **kwargs):
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
            aether: Optional[IAether] = None,
            configuration: Optional[INexusConfiguration] = None,
    ) -> None:
        """
        Internal

        Initialize the singleton Rift-domain root.

        Args:
            aether:
                Hidden owning `Aether` singleton used for Nexus-managed frame
                realization and disposal.
            configuration:
                Optional preinstalled Nexus configuration. When omitted, Nexus
                starts unconfigured and disabled.

        Returns:
            None.
        """
        if not Nexus._initialized:
            if aether is None:
                from melder.aether.aether import Aether
                aether = Aether()
            super().__init__()
            self._id: str = IDBuilder.create_id()
            self._lock: threading.RLock = threading.RLock()
            self._aether: IAether = aether
            self._configuration: Optional[INexusConfiguration] = configuration
            self._configured: bool = configuration is not None
            self._enabled: bool = False
            self._rifts_by_id: Dict[str, IRift] = {}
            self._rift_ids_by_name: Dict[str, str] = {}
            self._next_default_rift_number: int = 1
            self._next_indexed_nexus_frame_number: int = 1
            self._rift_profiles_by_name: Dict[str, IRiftConfiguration] = {}
            self._target_frame_ref_counts: Dict[str, int] = {}
            self._nexus_frames_by_name: Dict[str, NexusFrameRecord] = {}
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
            for profile in self._rift_profiles_by_name.values():
                profile.cleanup()
            for nexus_frame_record in self._nexus_frames_by_name.values():
                nexus_frame_record.cleanup()

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
            self._nexus_frames_by_name.clear()
            self._rifts_by_id = None
            self._rift_ids_by_name = None
            self._next_default_rift_number = None
            self._next_indexed_nexus_frame_number = None
            self._rift_profiles_by_name = None
            self._target_frame_ref_counts = None
            self._nexus_frames_by_name = None
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

    def create_rift_configuration(
            self,
            profile_name: Optional[str] = None,
    ) -> IRiftConfiguration:
        """
        Internal

        Create a per-Rift configuration initialized from Nexus defaults.

        Args:
            profile_name:
                Optional registered profile name. When supplied, the returned
                configuration is cloned from the stored profile template.

        Returns:
            IRiftConfiguration: Mutable per-Rift configuration.

        Raises:
            RuntimeError: If Nexus is not configured.
            ValueError: If `profile_name` is unknown.
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
        configuration.with_target_frame_name(self._configuration.get_property("default_target_frame_name"))
        configuration.with_space_type(self._configuration.get_property("default_space_type"))
        configuration.with_auto_activate_on_program(self._configuration.get_property("default_auto_activate_on_program"))
        configuration.with_auto_create_space(self._configuration.get_property("default_auto_create_space"))
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
        if bound_configuration.consumed:
            raise ValueError("RiftConfiguration has already been consumed.")
        if not bound_configuration.frozen:
            bound_configuration.finalize()

        self._validate_target_frame_configuration(bound_configuration)
        target_frame_name = bound_configuration.get_property("target_frame_name")

        with self._lock:
            canonical_rift_name = rift_name or self._allocate_default_rift_name()
            nexus_frame_name = self._determine_nexus_frame_name(canonical_rift_id)
            rift = Rift(
                self,
                configuration=bound_configuration,
                nexus_frame_names=(nexus_frame_name,),
                default_nexus_frame_name=nexus_frame_name,
                target_frame_names=(target_frame_name,),
                default_target_frame_name=target_frame_name,
                rift_name=canonical_rift_name,
                rift_id=canonical_rift_id,
                local_conduit_id=local_conduit_id,
                active_space_id=active_space_id,
                metadata=metadata,
            )
            if bound_configuration.get_property("auto_activate_on_program"):
                rift.mark_active()
            self.add_rift(rift)
            bound_configuration.mark_consumed()
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
            self._validate_nexus_frame_budget(rift.nexus_frame_names)
            self._validate_active_rift_budget()

            self._rifts_by_id[rift.id] = rift
            if rift.rift_name:
                self._rift_ids_by_name[rift.rift_name] = rift.id
            for target_frame_name in rift.target_frame_names:
                self._increment_ref_count(self._target_frame_ref_counts, target_frame_name)
            self._attach_rift_to_nexus_frames(rift)
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

        Remove one Rift from Nexus and update frame lifecycle state.

        Args:
            rift_id:
                Canonical Rift id.

        Returns:
            None.
        """
        self._require_enabled()
        frame_names_to_cleanup: List[str] = []
        with self._lock:
            try:
                rift = self._rifts_by_id.pop(rift_id)
            except KeyError as exc:
                raise ValueError("Rift with id '{0}' was not found.".format(rift_id)) from exc

            if rift.rift_name:
                self._rift_ids_by_name.pop(rift.rift_name, None)
            for target_frame_name in rift.target_frame_names:
                self._decrement_ref_count(self._target_frame_ref_counts, target_frame_name)
            frame_names_to_cleanup.extend(self._detach_rift_from_nexus_frames(rift))

        for frame_name in frame_names_to_cleanup:
            self._dispose_nexus_frame(frame_name)
        rift.cleanup()

    def list_rift_ids(self) -> list[str]:
        """
        Internal

        Return the currently registered Rift ids.

        Returns:
            list[str]: Snapshot of registered ids.
        """
        self._require_enabled()
        return list(self._rifts_by_id.keys())

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
                Optional explicit Nexus frame name. When omitted, the Rift's
                current default Nexus frame name is used.

        Returns:
            IAethericFrame: Resolved Nexus frame.

        Raises:
            ValueError: If the requesting Rift or requested frame is not
                available under the current mode rules.
        """
        self._require_enabled()
        with self._lock:
            rift = self._get_required_rift(rift_id)
            requested_frame_name = frame_name or rift.default_nexus_frame_name
            nexus_frame_mode = self._configuration.get_property("nexus_frame_mode")

            if nexus_frame_mode == NexusFrameMode.single:
                if requested_frame_name != self._configuration.get_property("default_nexus_frame_name"):
                    raise ValueError("Shared Nexus mode only exposes the shared frame.")
                nexus_frame_record = self._get_required_nexus_frame_record(requested_frame_name)
                return nexus_frame_record.frame

            if nexus_frame_mode == NexusFrameMode.one_per_workspace:
                if requested_frame_name not in rift.nexus_frame_names:
                    raise ValueError("Rift can only access its own private Nexus frame.")
                nexus_frame_record = self._get_required_nexus_frame_record(requested_frame_name)
                return nexus_frame_record.frame

            nexus_frame_record = self._get_required_nexus_frame_record(requested_frame_name)
            if rift.id not in nexus_frame_record.attached_rift_ids:
                nexus_frame_record.attach_rift_id(rift.id)
                rift._attach_nexus_frame_name(requested_frame_name)
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
                    rift._attach_nexus_frame_name(shared_frame_name)
                return nexus_frame_record.frame

            if nexus_frame_mode == NexusFrameMode.one_per_workspace:
                if immutable:
                    raise ValueError("one_per_workspace frames cannot be immutable.")
                private_frame_name = frame_name or rift.default_nexus_frame_name
                if private_frame_name != rift.default_nexus_frame_name:
                    raise ValueError("Rift can only create or recover its own private Nexus frame.")
                nexus_frame_record = self._get_or_create_nexus_frame_record(
                    private_frame_name,
                    creator_rift_id=rift.id,
                    immutable=False,
                )
                if rift.id not in nexus_frame_record.attached_rift_ids:
                    nexus_frame_record.attach_rift_id(rift.id)
                return nexus_frame_record.frame

            new_frame_name = frame_name or self._allocate_indexed_nexus_frame_name()
            if new_frame_name in self._nexus_frames_by_name:
                raise ValueError("Indexed Nexus frame '{0}' already exists.".format(new_frame_name))
            self._validate_nexus_frame_budget((new_frame_name,))
            nexus_frame_record = self._create_nexus_frame_record(
                new_frame_name,
                creator_rift_id=rift.id,
                immutable=immutable,
            )
            nexus_frame_record.attach_rift_id(rift.id)
            rift._attach_nexus_frame_name(new_frame_name)
            return nexus_frame_record.frame

    def list_accessible_nexus_frame_names(self, rift_id: str) -> Tuple[str, ...]:
        """
        Internal

        Return the Nexus frame names the requesting Rift may currently access.

        Args:
            rift_id:
                Requesting Rift id.

        Returns:
            Tuple[str, ...]: Accessible Nexus frame names.
        """
        self._require_enabled()
        with self._lock:
            rift = self._get_required_rift(rift_id)
            nexus_frame_mode = self._configuration.get_property("nexus_frame_mode")
            if nexus_frame_mode == NexusFrameMode.single:
                shared_frame_name = self._configuration.get_property("default_nexus_frame_name")
                if shared_frame_name in self._nexus_frames_by_name:
                    return (shared_frame_name,)
                return tuple()
            if nexus_frame_mode == NexusFrameMode.one_per_workspace:
                return rift.nexus_frame_names
            return tuple(sorted(self._nexus_frames_by_name.keys()))

    def check_for_aetheric_frame(self, frame_name: str) -> None:
        """
        Internal

        Drop Nexus frame-record state when `Aether` is about to dispose a
        frame directly.

        Args:
            frame_name:
                Frame name about to be removed from `Aether`.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned or not self._enabled or self._nexus_frames_by_name is None:
                return
            nexus_frame_record = self._nexus_frames_by_name.pop(frame_name, None)
            if nexus_frame_record is None:
                return

            attached_rift_ids = nexus_frame_record.attached_rift_ids
            for attached_rift_id in attached_rift_ids:
                attached_rift = self._rifts_by_id.get(attached_rift_id)
                if attached_rift is not None:
                    attached_rift.on_nexus_frame_disposed(frame_name)
            nexus_frame_record.cleanup()

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
            if nexus_frame_name not in self._nexus_frames_by_name and nexus_frame_name not in unique_new_nexus_frames:
                unique_new_nexus_frames.append(nexus_frame_name)
        if not unique_new_nexus_frames:
            return
        if len(self._nexus_frames_by_name) + len(unique_new_nexus_frames) > self._configuration.get_property(
                "max_nexus_frame_count"):
            raise ValueError("Nexus internal frame cap has been reached.")

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

    def _determine_nexus_frame_name(self, rift_id: str) -> str:
        """
        Internal

        Determine the internal Nexus frame name for one Rift from Nexus
        topology policy.

        Args:
            rift_id:
                Canonical Rift id used when the topology mode is
                `one_per_workspace`.

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

        Returns:
            str: Newly allocated default Rift name.
        """
        while True:
            rift_name = "nexus_rift_{0}".format(self._next_default_rift_number)
            self._next_default_rift_number = self._next_default_rift_number + 1
            if rift_name not in self._rift_ids_by_name:
                return rift_name

    def _allocate_indexed_nexus_frame_name(self) -> str:
        """
        Internal

        Allocate the next deterministic indexed Nexus frame name.

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

    def _attach_rift_to_nexus_frames(self, rift: IRift) -> None:
        """
        Internal

        Attach one Rift to its realized Nexus-frame records.

        Args:
            rift:
                Rift being registered.

        Returns:
            None.
        """
        nexus_frame_mode = self._configuration.get_property("nexus_frame_mode")
        for nexus_frame_name in rift.nexus_frame_names:
            nexus_frame_record = self._get_or_create_nexus_frame_record(
                nexus_frame_name,
                creator_rift_id=rift.id,
                immutable=False,
            )
            nexus_frame_record.attach_rift_id(rift.id)

    def _detach_rift_from_nexus_frames(self, rift: IRift) -> List[str]:
        """
        Internal

        Detach one Rift from its Nexus-frame records and determine which
        frames should be disposed.

        Args:
            rift:
                Rift being removed.

        Returns:
            List[str]: Frame names that should be disposed through `Aether`.
        """
        frame_names_to_cleanup = []
        for nexus_frame_name in rift.nexus_frame_names:
            nexus_frame_record = self._nexus_frames_by_name.get(nexus_frame_name)
            if nexus_frame_record is None:
                continue
            nexus_frame_record.detach_rift_id(rift.id)
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

        Returns:
            None.
        """
        nexus_frame_record = self._nexus_frames_by_name.get(frame_name)
        if nexus_frame_record is None:
            return
        nexus_frame_record.frame.cleanup()

    def _get_required_rift(self, rift_id: str) -> IRift:
        """
        Internal

        Return one registered Rift or raise.

        Args:
            rift_id:
                Canonical Rift id.

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

        Returns:
            NexusFrameRecord: Existing frame record.
        """
        try:
            return self._nexus_frames_by_name[frame_name]
        except KeyError as exc:
            raise ValueError("Nexus frame '{0}' was not found.".format(frame_name)) from exc

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
        nexus_frame_record = self._nexus_frames_by_name.get(frame_name)
        if nexus_frame_record is not None:
            return nexus_frame_record
        return self._create_nexus_frame_record(
            frame_name,
            creator_rift_id=creator_rift_id,
            immutable=immutable,
        )

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
        realized_frame = self._aether._ensure_frame(frame_name)
        nexus_frame_mode = self._configuration.get_property("nexus_frame_mode")
        nexus_frame_record = NexusFrameRecord(
            frame_name=frame_name,
            frame=realized_frame,
            nexus_frame_mode=nexus_frame_mode,
            creator_rift_id=creator_rift_id,
            owner_rift_id=creator_rift_id,
            immutable=immutable,
        )
        self._nexus_frames_by_name[frame_name] = nexus_frame_record
        return nexus_frame_record

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
            if key == "event_configuration" and value is not None:
                value = self._clone_rift_event_configuration(value)
            cloned_configuration.set_property(key, value)
        return cloned_configuration

    def _clone_rift_event_configuration(
            self,
            event_configuration: IRiftEventConfiguration,
    ) -> RiftEventConfiguration:
        """
        Internal

        Clone one `RiftEventConfiguration` into a fresh room-event config.

        Args:
            event_configuration:
                Source event configuration.

        Returns:
            RiftEventConfiguration: Fresh cloned event configuration.
        """
        return RiftEventConfiguration(
            action_enrichers=list(event_configuration._action_enrichers),
            memory_enrichers=list(event_configuration._memory_enrichers),
            action_observers=list(event_configuration._action_observers),
            memory_observers=list(event_configuration._memory_observers),
        )
