import threading
from typing import Dict, Optional, Sequence, Tuple, Type, Union
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.aether.nexus.configuration.nexus_frame_mode import (
    NexusFrameMode,
)
from melder.aether.nexus.configuration.rift_space_type import RiftSpaceType
from melder.aether.nexus.configuration.rift_validation_mode import RiftValidationMode
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.general_helpers import EnumHelpers
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.interfaces import INexusConfiguration


class NexusConfiguration(Cleanable, INexusConfiguration):
    """
    Internal

    Process-wide configuration for `Nexus`.

    Purpose:
        Hold central Nexus governance and default-programming behavior without
        pushing per-Rift room/history semantics up into the process-wide layer.

    Contract:
        - Mutable until frozen.
        - Stores typed properties in one property bag.
        - Governs process-wide creation/access policy, Nexus-frame topology,
          target-frame restrictions, and per-Rift defaults.
        - Once finalized, property mutation is disallowed.

    Lifecycle:
        Owned by `Nexus` once a user explicitly engages it and installs a
        configuration. Cleanup clears all stored properties and freezes the
        object permanently.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_frozen",
        "_properties",
        "available_properties",
    ]

    def __init__(self) -> None:
        """
        Internal

        Initialize an empty Nexus configuration.

        Returns:
            None.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._frozen: bool = False
        self._properties: Dict[str, object] = {}
        self.available_properties: Dict[str, Union[Type, Tuple[Type, ...]]] = {
            "allow_rift_creation": bool,
            "creation_token_required": bool,
            "creation_token_value": (str, type(None)),
            "allow_direct_rift_access": bool,
            "rift_access_token_required": bool,
            "rift_access_token_value": (str, type(None)),
            "allow_external_rift_registration": bool,
            "allow_nested_rift_creation": bool,
            "max_active_rift_count": int,
            "nexus_frame_mode": NexusFrameMode,
            "default_nexus_frame_name": str,
            "auto_create_nexus_frames": bool,
            "max_nexus_frame_count": int,
            "allowed_target_frame_names": tuple,
            "denied_target_frame_names": tuple,
            "allow_target_frame_override": bool,
            "allow_multiple_target_frames": bool,
            "max_target_frame_count": int,
            "projection_refresh_gate_enabled": bool,
            "projection_refresh_gate_timeout_seconds": (int, float),
            "projection_refresh_gate_poll_interval_seconds": (int, float),
            "default_space_type": RiftSpaceType,
            "default_auto_activate_on_program": bool,
            "default_auto_create_space": bool,
            "default_validation_mode": RiftValidationMode,
        }

    @property
    def id(self) -> str:
        """
        Purpose:
            Return the stable identity for this configuration object.

        Returns:
            str: Stable configuration identifier.
        """
        self.check_cleaned()
        return self._id

    @property
    def frozen(self) -> bool:
        """
        Purpose:
            Return whether further mutation is forbidden.

        Returns:
            bool: True when the configuration is finalized.
        """
        self.check_cleaned()
        return self._frozen

    def cleanup(self) -> None:
        """
        Internal

        Idempotently cleanup the configuration and clear all state.

        Contract:
            - Marks the object cleaned and frozen.
            - Clears the property bag and available-property registry.
            - Leaves the object permanently unusable after cleanup.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._frozen = True
            self._properties.clear()
            self._properties = None
            self.available_properties.clear()
            self.available_properties = None
        self._lock = None
        self._id = None

    def set_property(self, key: str, value: object) -> None:
        """
        Internal

        Set one configuration property before finalize().

        Args:
            key:
                Property name.
            value:
                Property value.

        Contract:
            - Rejects mutation after freeze().
            - Normalizes enum-backed and frame-list-backed values before storage.
            - Enforces the declared type contract for every property.

        Returns:
            None.

        Raises:
            RuntimeError: If the configuration is already frozen.
            ValueError: If the property name is unknown.
            TypeError: If the supplied value does not satisfy the declared type.
        """
        self.check_cleaned()
        if self._frozen:
            raise RuntimeError("Cannot modify NexusConfiguration after freeze().")
        if key not in self.available_properties:
            raise ValueError("Unknown NexusConfiguration property: '{0}'.".format(key))

        expected_type = self.available_properties[key]
        converted_value = self._convert_property_value_if_needed(key, value)
        if not isinstance(expected_type, tuple):
            expected_type = (expected_type,)
        if not isinstance(converted_value, expected_type):
            expected_names = ", ".join(t.__name__ for t in expected_type)
            raise TypeError(
                "Invalid type for property '{0}': expected {1}, got {2}.".format(
                    key,
                    expected_names,
                    type(converted_value).__name__,
                )
            )
        self._properties[key] = converted_value

    def get_property(self, key: str) -> object:
        """
        Internal

        Return one configuration property value.

        Args:
            key:
                Property name.

        Contract:
            - Returns the currently stored property value exactly as normalized
              during `set_property(...)`.

        Returns:
            object: Stored property value.

        Raises:
            KeyError: If the property has not been set.
        """
        self.check_cleaned()
        return self._properties[key]

    def has_property(self, key: str) -> bool:
        """
        Internal

        Return whether a property has been set.

        Args:
            key:
                Property name.

        Contract:
            - Returns presence only; does not validate semantic completeness.

        Returns:
            bool: True when present.
        """
        self.check_cleaned()
        return key in self._properties

    def load_default_dictionary(self) -> None:
        """
        Internal

        Load the standard default property set for Nexus master-user engagement.

        Contract:
            - Populates every required Nexus-governance field.
            - Uses the easy-start defaults agreed for master-user Nexus setup:
              `single` Nexus-frame mode, `default` target frame, and no token
              requirements.

        Returns:
            None.
        """
        self.check_cleaned()
        defaults = {
            "allow_rift_creation": True,
            "creation_token_required": False,
            "creation_token_value": None,
            "allow_direct_rift_access": True,
            "rift_access_token_required": False,
            "rift_access_token_value": None,
            "allow_external_rift_registration": True,
            "allow_nested_rift_creation": False,
            "max_active_rift_count": 0,
            "nexus_frame_mode": NexusFrameMode.single,
            "default_nexus_frame_name": "aetheric_frame_system",
            "auto_create_nexus_frames": True,
            "max_nexus_frame_count": 1,
            "allowed_target_frame_names": ("default",),
            "denied_target_frame_names": tuple(),
            "allow_target_frame_override": False,
            "allow_multiple_target_frames": False,
            "max_target_frame_count": 1,
            "projection_refresh_gate_enabled": True,
            "projection_refresh_gate_timeout_seconds": 30.0,
            "projection_refresh_gate_poll_interval_seconds": 0.1,
            "default_space_type": RiftSpaceType.static,
            "default_auto_activate_on_program": True,
            "default_auto_create_space": False,
            "default_validation_mode": RiftValidationMode.strict,
        }
        for key, value in defaults.items():
            self.set_property(key, value)

    def validate(self) -> bool:
        """
        Internal

        Validate that all required properties exist and the governance schema is
        self-consistent.

        Contract:
            - Ensures every declared property has a value.
            - Enforces cross-field invariants such as single-frame mode budget,
              Nexus-frame mode budget, target-frame allow/deny coherence, and
              target-frame caps.

        Returns:
            bool: True when the configuration is valid.

        Raises:
            ValueError: If a required property is missing or a cross-field
                invariant is violated.
        """
        self.check_cleaned()
        for key in self.available_properties.keys():
            if key not in self._properties:
                raise ValueError("Missing required configuration property: '{0}'.".format(key))

        max_active_rift_count = self.get_property("max_active_rift_count")
        nexus_frame_mode = self.get_property("nexus_frame_mode")
        default_nexus_frame_name = self.get_property("default_nexus_frame_name")
        allowed_target_frame_names = self.get_property("allowed_target_frame_names")
        denied_target_frame_names = self.get_property("denied_target_frame_names")
        max_nexus_frame_count = self.get_property("max_nexus_frame_count")
        allow_multiple_target_frames = self.get_property("allow_multiple_target_frames")
        max_target_frame_count = self.get_property("max_target_frame_count")
        projection_refresh_gate_timeout_seconds = self.get_property(
            "projection_refresh_gate_timeout_seconds"
        )
        projection_refresh_gate_poll_interval_seconds = self.get_property(
            "projection_refresh_gate_poll_interval_seconds"
        )

        if max_active_rift_count < 0:
            raise ValueError("max_active_rift_count must be >= 0.")
        if not default_nexus_frame_name:
            raise ValueError("default_nexus_frame_name cannot be empty.")
        if max_nexus_frame_count < 1:
            raise ValueError("max_nexus_frame_count must be >= 1.")
        if max_target_frame_count < 1:
            raise ValueError("max_target_frame_count must be >= 1.")
        if nexus_frame_mode == NexusFrameMode.single and max_nexus_frame_count != 1:
            raise ValueError("max_nexus_frame_count must be 1 when nexus_frame_mode is single.")
        if not allow_multiple_target_frames and max_target_frame_count != 1:
            raise ValueError("max_target_frame_count must be 1 when allow_multiple_target_frames is False.")
        if projection_refresh_gate_timeout_seconds <= 0:
            raise ValueError("projection_refresh_gate_timeout_seconds must be > 0.")
        if projection_refresh_gate_poll_interval_seconds <= 0:
            raise ValueError(
                "projection_refresh_gate_poll_interval_seconds must be > 0."
            )
        return True

    def freeze(self) -> None:
        """
        Internal

        Validate and freeze the configuration.

        Contract:
            - Calls `validate()` first.
            - Idempotent when already frozen.

        Returns:
            None.

        Raises:
            ValueError: If validation fails.
        """
        self.check_cleaned()
        if self._frozen:
            return
        if not self.validate():
            raise ValueError("NexusConfiguration validation failed.")
        self._frozen = True

    def finalize(self) -> "INexusConfiguration":
        """
        Fluent

        Validate and freeze the configuration, then return `self`.

        Contract:
            - Returns this same configuration instance after freezing it.
            - Does not allocate or clone a detached configuration object.

        Returns:
            INexusConfiguration: This configuration instance.
        """
        self.freeze()
        return self

    def build(self) -> "INexusConfiguration":
        """
        Fluent alias for `finalize()`.

        Contract:
            - Preserves the builder-style API used elsewhere in the runtime.
            - Returns this same configuration instance after finalize/freeze.

        Returns:
            INexusConfiguration: This configuration instance.
        """
        return self.finalize()

    def with_defaults(self) -> "INexusConfiguration":
        """
        Fluent

        Load the standard Nexus defaults and return `self`.

        Contract:
            - Delegates to `load_default_dictionary()`.
            - Applies the default process-wide governance/property set in-place.
            - Leaves the configuration mutable until `freeze()` or `finalize()`.

        Returns:
            INexusConfiguration: This configuration instance.
        """
        self.load_default_dictionary()
        return self

    def with_rift_creation_enabled(
            self,
            enabled: bool = True,
    ) -> "INexusConfiguration":
        """
        Fluent

        Set whether Nexus may create new Rifts.

        Args:
            enabled:
                True to permit Rift creation/programming under the remaining
                policy gates.

        Returns:
            INexusConfiguration: This configuration instance.
        """
        self.set_property("allow_rift_creation", enabled)
        return self

    def with_creation_token_required(
            self,
            enabled: bool = True,
    ) -> "INexusConfiguration":
        """
        Fluent

        Set whether Rift creation/programming requires a creation token.

        Args:
            enabled:
                True to require `creation_token_value` during creation.

        Returns:
            INexusConfiguration: This configuration instance.
        """
        self.set_property("creation_token_required", enabled)
        return self

    def with_creation_token(
            self,
            token_value: Optional[str],
    ) -> "INexusConfiguration":
        """
        Fluent

        Set the process-wide creation token value for Nexus.

        Args:
            token_value:
                Optional creation token string. `None` clears the token value.

        Returns:
            INexusConfiguration: This configuration instance.
        """
        self.set_property("creation_token_value", token_value)
        return self

    def with_direct_rift_access(
            self,
            enabled: bool = True,
    ) -> "INexusConfiguration":
        """
        Fluent

        Set whether callers may retrieve live Rift objects directly from Nexus.

        Args:
            enabled:
                True to allow direct live-Rift access under the remaining
                policy gates.

        Returns:
            INexusConfiguration: This configuration instance.
        """
        self.set_property("allow_direct_rift_access", enabled)
        return self

    def with_rift_access_token_required(
            self,
            enabled: bool = True,
    ) -> "INexusConfiguration":
        """
        Fluent

        Set whether direct live-Rift access requires a token.

        Args:
            enabled:
                True to require `rift_access_token_value` for direct Rift
                retrieval.

        Returns:
            INexusConfiguration: This configuration instance.
        """
        self.set_property("rift_access_token_required", enabled)
        return self

    def with_rift_access_token(
            self,
            token_value: Optional[str],
    ) -> "INexusConfiguration":
        """
        Fluent

        Set the token value used for direct live-Rift access.

        Args:
            token_value:
                Optional Rift-access token string. `None` clears the token.

        Returns:
            INexusConfiguration: This configuration instance.
        """
        self.set_property("rift_access_token_value", token_value)
        return self

    def with_allow_external_rift_registration(
            self,
            enabled: bool = True,
    ) -> "INexusConfiguration":
        """
        Fluent

        Set whether Nexus may program externally created Rift shells.

        Args:
            enabled:
                True to permit external Rift registration/programming.

        Returns:
            INexusConfiguration: This configuration instance.
        """
        self.set_property("allow_external_rift_registration", enabled)
        return self

    def with_allow_nested_rift_creation(
            self,
            enabled: bool = True,
    ) -> "INexusConfiguration":
        """
        Fluent

        Set whether running Rifts may create nested Rifts.

        Args:
            enabled:
                True to permit nested Rift creation flows.

        Returns:
            INexusConfiguration: This configuration instance.
        """
        self.set_property("allow_nested_rift_creation", enabled)
        return self

    def with_max_active_rift_count(
            self,
            count: int,
    ) -> "INexusConfiguration":
        """
        Fluent

        Set the cap on concurrently registered active Rifts.

        Args:
            count:
                Maximum number of active Rifts. `0` means unlimited.

        Returns:
            INexusConfiguration: This configuration instance.
        """
        self.set_property("max_active_rift_count", count)
        return self

    def with_nexus_frame_mode(
            self,
            mode: Union[NexusFrameMode, str],
    ) -> "INexusConfiguration":
        """
        Fluent

        Set the internal Nexus frame topology mode.

        Args:
            mode:
                Frame-topology mode enum or string.

        Returns:
            INexusConfiguration: This configuration instance.
        """
        self.set_property("nexus_frame_mode", mode)
        return self

    def with_default_nexus_frame_name(
            self,
            frame_name: str,
    ) -> "INexusConfiguration":
        """
        Fluent

        Set the default Nexus-owned internal frame name.

        Args:
            frame_name:
                Frame name used in `single` mode and as the base name
                in other modes.

        Returns:
            INexusConfiguration: This configuration instance.
        """
        self.set_property("default_nexus_frame_name", frame_name)
        return self

    def with_auto_create_nexus_frames(
            self,
            enabled: bool = True,
    ) -> "INexusConfiguration":
        """
        Fluent

        Set whether the runtime may auto-create internal Nexus frames when Rift
        activation later resolves them through `Aether`.

        Args:
            enabled:
                True to auto-create required Nexus frames on engagement or
                state creation.

        Returns:
            INexusConfiguration: This configuration instance.
        """
        self.set_property("auto_create_nexus_frames", enabled)
        return self

    def with_max_nexus_frame_count(
            self,
            count: int,
    ) -> "INexusConfiguration":
        """
        Fluent

        Set the cap on Nexus-assigned internal frames.

        Args:
            count:
                Maximum number of internal Nexus frames allowed.

        Returns:
            INexusConfiguration: This configuration instance.
        """
        self.set_property("max_nexus_frame_count", count)
        return self

    def with_allowed_target_frame_names(
            self,
            frame_names: Sequence[str],
    ) -> "INexusConfiguration":
        """
        Fluent

        Set the allow-list for targetable frames.

        Args:
            frame_names:
                Sequence of permitted target frame names.

        Returns:
            INexusConfiguration: This configuration instance.
        """
        self.set_property("allowed_target_frame_names", frame_names)
        return self

    def with_denied_target_frame_names(
            self,
            frame_names: Sequence[str],
    ) -> "INexusConfiguration":
        """
        Fluent

        Set the deny-list for targetable frames.

        Args:
            frame_names:
                Sequence of denied target frame names.

        Returns:
            INexusConfiguration: This configuration instance.
        """
        self.set_property("denied_target_frame_names", frame_names)
        return self

    def with_target_frame_override(
            self,
            enabled: bool = True,
    ) -> "INexusConfiguration":
        """
        Fluent

        Set whether callers may override the allowed target-frame selection.

        Args:
            enabled:
                True to allow per-Rift target-frame override requests.

        Returns:
            INexusConfiguration: This configuration instance.
        """
        self.set_property("allow_target_frame_override", enabled)
        return self

    def with_multiple_target_frames(
            self,
            enabled: bool = True,
    ) -> "INexusConfiguration":
        """
        Fluent

        Set whether Nexus may target multiple external frames across its Rifts.

        Args:
            enabled:
                True to permit more than one distinct target frame.

        Returns:
            INexusConfiguration: This configuration instance.
        """
        self.set_property("allow_multiple_target_frames", enabled)
        return self

    def with_max_target_frame_count(
            self,
            count: int,
    ) -> "INexusConfiguration":
        """
        Fluent

        Set the cap on distinct target frames Nexus may use.

        Args:
            count:
                Maximum number of distinct target frames.

        Returns:
            INexusConfiguration: This configuration instance.
        """
        self.set_property("max_target_frame_count", count)
        return self

    def with_projection_refresh_gate(
            self,
            enabled: bool = True,
    ) -> "INexusConfiguration":
        """
        Fluent

        Set whether ACL-driven projection refresh uses the RiftGate drain
        barrier.

        Args:
            enabled:
                True to block new entrants, wait for in-flight work to drain,
                refresh projections/viewers, then reopen gates.

        Returns:
            INexusConfiguration: This configuration instance.
        """
        self.set_property("projection_refresh_gate_enabled", enabled)
        return self

    def with_projection_refresh_gate_timeout_seconds(
            self,
            timeout_seconds: Union[int, float],
    ) -> "INexusConfiguration":
        """
        Fluent

        Set the timeout used while waiting for impacted Rift gates to drain.

        Args:
            timeout_seconds:
                Positive timeout in seconds.

        Returns:
            INexusConfiguration: This configuration instance.
        """
        self.set_property(
            "projection_refresh_gate_timeout_seconds",
            timeout_seconds,
        )
        return self

    def with_projection_refresh_gate_poll_interval_seconds(
            self,
            interval_seconds: Union[int, float],
    ) -> "INexusConfiguration":
        """
        Fluent

        Set the poll interval used while waiting for impacted Rift gates to
        drain.

        Args:
            interval_seconds:
                Positive poll interval in seconds.

        Returns:
            INexusConfiguration: This configuration instance.
        """
        self.set_property(
            "projection_refresh_gate_poll_interval_seconds",
            interval_seconds,
        )
        return self

    def with_default_space_type(
            self,
            space_type: Union[RiftSpaceType, str],
    ) -> "INexusConfiguration":
        """
        Fluent

        Set the default room type for newly created Rifts.

        Args:
            space_type:
                Default room-kind enum or string.

        Returns:
            INexusConfiguration: This configuration instance.
        """
        self.set_property("default_space_type", space_type)
        return self

    def with_default_auto_activate_on_program(
            self,
            enabled: bool = True,
    ) -> "INexusConfiguration":
        """
        Fluent

        Set whether newly programmed Rifts activate automatically.

        Args:
            enabled:
                True to mark new Rifts active during programming.

        Returns:
            INexusConfiguration: This configuration instance.
        """
        self.set_property("default_auto_activate_on_program", enabled)
        return self

    def with_default_auto_create_space(
            self,
            enabled: bool = True,
    ) -> "INexusConfiguration":
        """
        Fluent

        Set whether newly programmed Rifts auto-create an initial room.

        Args:
            enabled:
                True to create the initial room automatically.

        Returns:
            INexusConfiguration: This configuration instance.
        """
        self.set_property("default_auto_create_space", enabled)
        return self

    def with_default_validation_mode(
            self,
            mode: Union[RiftValidationMode, str],
    ) -> "INexusConfiguration":
        """
        Fluent

        Set the default validation posture for newly created Rifts.

        Args:
            mode:
                Validation mode enum or string.

        Returns:
            INexusConfiguration: This configuration instance.
        """
        self.set_property("default_validation_mode", mode)
        return self

    def _convert_property_value_if_needed(self, key: str, value: object) -> object:
        """
        Internal

        Normalize enum-backed and sequence-backed properties before storage.

        Args:
            key:
                Property name being assigned.
            value:
                Candidate property value.

        Returns:
            object: The normalized property value.

        Raises:
            TypeError: If a frame-name collection is invalid.
            ValueError: If an enum conversion or frame-name normalization fails.
        """
        if key == "nexus_frame_mode":
            return EnumHelpers.convert_enum_and_check(value, NexusFrameMode)
        if key == "default_space_type":
            if value == "dynamic":
                value = RiftSpaceType.codegen
            return EnumHelpers.convert_enum_and_check(value, RiftSpaceType)
        if key == "default_validation_mode":
            return EnumHelpers.convert_enum_and_check(value, RiftValidationMode)
        if key in {"allowed_target_frame_names", "denied_target_frame_names"}:
            return self._normalize_frame_names(value)
        return value

    def _normalize_frame_names(self, value: object) -> Tuple[str, ...]:
        """
        Internal

        Normalize a target-frame allow-list or deny-list into an immutable tuple.

        Args:
            value:
                Candidate frame-name collection.

        Contract:
            - Rejects single strings to avoid accidental character splitting.
            - Deduplicates frame names while preserving order.
            - Rejects empty frame names.

        Returns:
            Tuple[str, ...]: Normalized immutable frame-name sequence.

        Raises:
            TypeError: If the input is not a sequence of strings.
            ValueError: If any frame name is empty.
        """
        if isinstance(value, str):
            raise TypeError("Frame-name collections must be sequences of strings, not a single string.")
        if not isinstance(value, Sequence):
            raise TypeError("Frame-name collections must be sequences of strings.")

        normalized_frame_names = []
        for frame_name in value:
            if not isinstance(frame_name, str):
                raise TypeError("Frame-name collections must contain only strings.")
            if not frame_name:
                raise ValueError("Frame names cannot be empty.")
            if frame_name not in normalized_frame_names:
                normalized_frame_names.append(frame_name)
        return tuple(normalized_frame_names)
