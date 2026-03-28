import threading
from typing import Dict, Optional, Sequence, Tuple, Type, Union

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.aetheric_rift_system.configuration.aetheric_rift_system_frame_mode import (
    AethericRiftSystemFrameMode,
)
from melder.aether.aetheric_rift_system.configuration.rift_space_type import RiftSpaceType
from melder.aether.aetheric_rift_system.configuration.rift_validation_mode import RiftValidationMode
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.general_helpers import EnumHelpers
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.interfaces.interfaces import IAethericRiftSystemConfiguration


class AethericRiftSystemConfiguration(Cleanable, IAethericRiftSystemConfiguration):
    """
    Internal

    Process-wide configuration for the hosted `AethericRiftSystem`.

    Purpose:
        Hold central ARS governance and default-programming behavior without
        pushing per-Rift room/history semantics up into the process-wide layer.

    Contract:
        - Mutable until frozen.
        - Stores typed properties in one property bag.
        - Governs process-wide creation/access policy, system-frame topology,
          target-frame restrictions, and per-Rift defaults.
        - Once finalized, property mutation is disallowed.

    Lifecycle:
        Owned by `Aether` / `AethericRiftSystem` when a user explicitly engages
        ARS and installs a configuration. Cleanup clears all stored properties
        and freezes the object permanently.
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

        Initialize an empty AR system configuration.

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
            "allow_direct_state_access": bool,
            "state_access_token_required": bool,
            "state_access_token_value": (str, type(None)),
            "allow_external_rift_registration": bool,
            "allow_nested_rift_creation": bool,
            "max_active_rift_count": int,
            "system_frame_mode": AethericRiftSystemFrameMode,
            "default_system_frame_name": str,
            "auto_create_system_frames": bool,
            "max_system_frame_count": int,
            "default_target_frame_name": str,
            "allowed_target_frame_names": tuple,
            "denied_target_frame_names": tuple,
            "allow_target_frame_override": bool,
            "allow_multiple_target_frames": bool,
            "max_target_frame_count": int,
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
            raise RuntimeError("Cannot modify AethericRiftSystemConfiguration after freeze().")
        if key not in self.available_properties:
            raise ValueError("Unknown AethericRiftSystemConfiguration property: '{0}'.".format(key))

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

        Load the standard default property set for ARS master-user engagement.

        Contract:
            - Populates every required system-governance field.
            - Uses the easy-start defaults agreed for master-user ARS setup:
              `single` system-frame mode, `default` target frame, and no token
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
            "allow_direct_state_access": True,
            "state_access_token_required": False,
            "state_access_token_value": None,
            "allow_external_rift_registration": True,
            "allow_nested_rift_creation": False,
            "max_active_rift_count": 0,
            "system_frame_mode": AethericRiftSystemFrameMode.single,
            "default_system_frame_name": "aetheric_frame_system",
            "auto_create_system_frames": True,
            "max_system_frame_count": 1,
            "default_target_frame_name": "default",
            "allowed_target_frame_names": ("default",),
            "denied_target_frame_names": tuple(),
            "allow_target_frame_override": False,
            "allow_multiple_target_frames": False,
            "max_target_frame_count": 1,
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
              target-frame allow/deny coherence, and target-frame caps.

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
        system_frame_mode = self.get_property("system_frame_mode")
        default_system_frame_name = self.get_property("default_system_frame_name")
        default_target_frame_name = self.get_property("default_target_frame_name")
        allowed_target_frame_names = self.get_property("allowed_target_frame_names")
        denied_target_frame_names = self.get_property("denied_target_frame_names")
        max_system_frame_count = self.get_property("max_system_frame_count")
        allow_multiple_target_frames = self.get_property("allow_multiple_target_frames")
        max_target_frame_count = self.get_property("max_target_frame_count")

        if max_active_rift_count < 0:
            raise ValueError("max_active_rift_count must be >= 0.")
        if not default_system_frame_name:
            raise ValueError("default_system_frame_name cannot be empty.")
        if not default_target_frame_name:
            raise ValueError("default_target_frame_name cannot be empty.")
        if max_system_frame_count < 1:
            raise ValueError("max_system_frame_count must be >= 1.")
        if max_target_frame_count < 1:
            raise ValueError("max_target_frame_count must be >= 1.")
        if system_frame_mode == AethericRiftSystemFrameMode.single and max_system_frame_count != 1:
            raise ValueError("max_system_frame_count must be 1 when system_frame_mode is single.")
        if not allow_multiple_target_frames and max_target_frame_count != 1:
            raise ValueError("max_target_frame_count must be 1 when allow_multiple_target_frames is False.")
        if default_target_frame_name in denied_target_frame_names:
            raise ValueError("default_target_frame_name cannot also be denied.")
        if allowed_target_frame_names and default_target_frame_name not in allowed_target_frame_names:
            raise ValueError("default_target_frame_name must be present in allowed_target_frame_names.")
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
            raise ValueError("AethericRiftSystemConfiguration validation failed.")
        self._frozen = True

    def finalize(self) -> "IAethericRiftSystemConfiguration":
        """
        Fluent

        Validate and freeze the configuration, then return `self`.

        Returns:
            IAethericRiftSystemConfiguration: This configuration instance.
        """
        self.freeze()
        return self

    def build(self) -> "IAethericRiftSystemConfiguration":
        """
        Fluent alias for finalize().

        Returns:
            IAethericRiftSystemConfiguration: This configuration instance.
        """
        return self.finalize()

    def with_defaults(self) -> "IAethericRiftSystemConfiguration":
        """
        Fluent

        Load the standard AR system defaults and return `self`.

        Returns:
            IAethericRiftSystemConfiguration: This configuration instance.
        """
        self.load_default_dictionary()
        return self

    def with_rift_creation_enabled(
            self,
            enabled: bool = True,
    ) -> "IAethericRiftSystemConfiguration":
        """
        Fluent

        Set whether ARS may create or program new Rifts.

        Args:
            enabled:
                True to permit Rift creation/programming under the remaining
                policy gates.

        Returns:
            IAethericRiftSystemConfiguration: This configuration instance.
        """
        self.set_property("allow_rift_creation", enabled)
        return self

    def with_creation_token_required(
            self,
            enabled: bool = True,
    ) -> "IAethericRiftSystemConfiguration":
        """
        Fluent

        Set whether Rift creation/programming requires a creation token.

        Args:
            enabled:
                True to require `creation_token_value` during creation.

        Returns:
            IAethericRiftSystemConfiguration: This configuration instance.
        """
        self.set_property("creation_token_required", enabled)
        return self

    def with_creation_token(
            self,
            token_value: Optional[str],
    ) -> "IAethericRiftSystemConfiguration":
        """
        Fluent

        Set the process-wide creation token value for ARS.

        Args:
            token_value:
                Optional creation token string. `None` clears the token value.

        Returns:
            IAethericRiftSystemConfiguration: This configuration instance.
        """
        self.set_property("creation_token_value", token_value)
        return self

    def with_direct_rift_access(
            self,
            enabled: bool = True,
    ) -> "IAethericRiftSystemConfiguration":
        """
        Fluent

        Set whether callers may retrieve live Rift objects directly from ARS.

        Args:
            enabled:
                True to allow direct live-Rift access under the remaining
                policy gates.

        Returns:
            IAethericRiftSystemConfiguration: This configuration instance.
        """
        self.set_property("allow_direct_rift_access", enabled)
        return self

    def with_rift_access_token_required(
            self,
            enabled: bool = True,
    ) -> "IAethericRiftSystemConfiguration":
        """
        Fluent

        Set whether direct live-Rift access requires a token.

        Args:
            enabled:
                True to require `rift_access_token_value` for direct Rift
                retrieval.

        Returns:
            IAethericRiftSystemConfiguration: This configuration instance.
        """
        self.set_property("rift_access_token_required", enabled)
        return self

    def with_rift_access_token(
            self,
            token_value: Optional[str],
    ) -> "IAethericRiftSystemConfiguration":
        """
        Fluent

        Set the token value used for direct live-Rift access.

        Args:
            token_value:
                Optional Rift-access token string. `None` clears the token.

        Returns:
            IAethericRiftSystemConfiguration: This configuration instance.
        """
        self.set_property("rift_access_token_value", token_value)
        return self

    def with_direct_state_access(
            self,
            enabled: bool = True,
    ) -> "IAethericRiftSystemConfiguration":
        """
        Fluent

        Set whether callers may retrieve canonical Rift state directly from ARS.

        Args:
            enabled:
                True to allow direct state access under the remaining policy
                gates.

        Returns:
            IAethericRiftSystemConfiguration: This configuration instance.
        """
        self.set_property("allow_direct_state_access", enabled)
        return self

    def with_state_access_token_required(
            self,
            enabled: bool = True,
    ) -> "IAethericRiftSystemConfiguration":
        """
        Fluent

        Set whether direct canonical state access requires a token.

        Args:
            enabled:
                True to require `state_access_token_value` for direct state
                retrieval.

        Returns:
            IAethericRiftSystemConfiguration: This configuration instance.
        """
        self.set_property("state_access_token_required", enabled)
        return self

    def with_state_access_token(
            self,
            token_value: Optional[str],
    ) -> "IAethericRiftSystemConfiguration":
        """
        Fluent

        Set the token value used for direct canonical state access.

        Args:
            token_value:
                Optional state-access token string. `None` clears the token.

        Returns:
            IAethericRiftSystemConfiguration: This configuration instance.
        """
        self.set_property("state_access_token_value", token_value)
        return self

    def with_allow_external_rift_registration(
            self,
            enabled: bool = True,
    ) -> "IAethericRiftSystemConfiguration":
        """
        Fluent

        Set whether ARS may program externally created Rift shells.

        Args:
            enabled:
                True to permit external Rift registration/programming.

        Returns:
            IAethericRiftSystemConfiguration: This configuration instance.
        """
        self.set_property("allow_external_rift_registration", enabled)
        return self

    def with_allow_nested_rift_creation(
            self,
            enabled: bool = True,
    ) -> "IAethericRiftSystemConfiguration":
        """
        Fluent

        Set whether running Rifts may create nested Rifts.

        Args:
            enabled:
                True to permit nested Rift creation flows.

        Returns:
            IAethericRiftSystemConfiguration: This configuration instance.
        """
        self.set_property("allow_nested_rift_creation", enabled)
        return self

    def with_max_active_rift_count(
            self,
            count: int,
    ) -> "IAethericRiftSystemConfiguration":
        """
        Fluent

        Set the cap on concurrently registered active Rifts.

        Args:
            count:
                Maximum number of active Rifts. `0` means unlimited.

        Returns:
            IAethericRiftSystemConfiguration: This configuration instance.
        """
        self.set_property("max_active_rift_count", count)
        return self

    def with_system_frame_mode(
            self,
            mode: Union[AethericRiftSystemFrameMode, str],
    ) -> "IAethericRiftSystemConfiguration":
        """
        Fluent

        Set the internal ARS system-frame topology mode.

        Args:
            mode:
                Frame-topology mode enum or string.

        Returns:
            IAethericRiftSystemConfiguration: This configuration instance.
        """
        self.set_property("system_frame_mode", mode)
        return self

    def with_default_system_frame_name(
            self,
            frame_name: str,
    ) -> "IAethericRiftSystemConfiguration":
        """
        Fluent

        Set the default ARS-owned internal system frame name.

        Args:
            frame_name:
                System-frame name used in `single` mode and as the base name
                in other modes.

        Returns:
            IAethericRiftSystemConfiguration: This configuration instance.
        """
        self.set_property("default_system_frame_name", frame_name)
        return self

    def with_auto_create_system_frames(
            self,
            enabled: bool = True,
    ) -> "IAethericRiftSystemConfiguration":
        """
        Fluent

        Set whether `Aether` / ARS may auto-create internal system frames.

        Args:
            enabled:
                True to auto-create required system frames on engagement or
                state creation.

        Returns:
            IAethericRiftSystemConfiguration: This configuration instance.
        """
        self.set_property("auto_create_system_frames", enabled)
        return self

    def with_max_system_frame_count(
            self,
            count: int,
    ) -> "IAethericRiftSystemConfiguration":
        """
        Fluent

        Set the cap on ARS-owned internal system frames.

        Args:
            count:
                Maximum number of internal system frames ARS may own.

        Returns:
            IAethericRiftSystemConfiguration: This configuration instance.
        """
        self.set_property("max_system_frame_count", count)
        return self

    def with_default_target_frame_name(
            self,
            frame_name: str,
    ) -> "IAethericRiftSystemConfiguration":
        """
        Fluent

        Set the default external target frame for new Rifts.

        Args:
            frame_name:
                Default target `AethericFrame` name.

        Returns:
            IAethericRiftSystemConfiguration: This configuration instance.
        """
        self.set_property("default_target_frame_name", frame_name)
        return self

    def with_allowed_target_frame_names(
            self,
            frame_names: Sequence[str],
    ) -> "IAethericRiftSystemConfiguration":
        """
        Fluent

        Set the allow-list for targetable frames.

        Args:
            frame_names:
                Sequence of permitted target frame names.

        Returns:
            IAethericRiftSystemConfiguration: This configuration instance.
        """
        self.set_property("allowed_target_frame_names", frame_names)
        return self

    def with_denied_target_frame_names(
            self,
            frame_names: Sequence[str],
    ) -> "IAethericRiftSystemConfiguration":
        """
        Fluent

        Set the deny-list for targetable frames.

        Args:
            frame_names:
                Sequence of denied target frame names.

        Returns:
            IAethericRiftSystemConfiguration: This configuration instance.
        """
        self.set_property("denied_target_frame_names", frame_names)
        return self

    def with_target_frame_override(
            self,
            enabled: bool = True,
    ) -> "IAethericRiftSystemConfiguration":
        """
        Fluent

        Set whether callers may override the default target frame.

        Args:
            enabled:
                True to allow per-Rift target-frame override requests.

        Returns:
            IAethericRiftSystemConfiguration: This configuration instance.
        """
        self.set_property("allow_target_frame_override", enabled)
        return self

    def with_multiple_target_frames(
            self,
            enabled: bool = True,
    ) -> "IAethericRiftSystemConfiguration":
        """
        Fluent

        Set whether ARS may target multiple external frames across its Rifts.

        Args:
            enabled:
                True to permit more than one distinct target frame.

        Returns:
            IAethericRiftSystemConfiguration: This configuration instance.
        """
        self.set_property("allow_multiple_target_frames", enabled)
        return self

    def with_max_target_frame_count(
            self,
            count: int,
    ) -> "IAethericRiftSystemConfiguration":
        """
        Fluent

        Set the cap on distinct target frames ARS may use.

        Args:
            count:
                Maximum number of distinct target frames.

        Returns:
            IAethericRiftSystemConfiguration: This configuration instance.
        """
        self.set_property("max_target_frame_count", count)
        return self

    def with_default_space_type(
            self,
            space_type: Union[RiftSpaceType, str],
    ) -> "IAethericRiftSystemConfiguration":
        """
        Fluent

        Set the default room type for newly created Rifts.

        Args:
            space_type:
                Default room-kind enum or string.

        Returns:
            IAethericRiftSystemConfiguration: This configuration instance.
        """
        self.set_property("default_space_type", space_type)
        return self

    def with_default_auto_activate_on_program(
            self,
            enabled: bool = True,
    ) -> "IAethericRiftSystemConfiguration":
        """
        Fluent

        Set whether newly programmed Rifts activate automatically.

        Args:
            enabled:
                True to mark new Rifts active during programming.

        Returns:
            IAethericRiftSystemConfiguration: This configuration instance.
        """
        self.set_property("default_auto_activate_on_program", enabled)
        return self

    def with_default_auto_create_space(
            self,
            enabled: bool = True,
    ) -> "IAethericRiftSystemConfiguration":
        """
        Fluent

        Set whether newly programmed Rifts auto-create an initial room.

        Args:
            enabled:
                True to create the initial room automatically.

        Returns:
            IAethericRiftSystemConfiguration: This configuration instance.
        """
        self.set_property("default_auto_create_space", enabled)
        return self

    def with_default_validation_mode(
            self,
            mode: Union[RiftValidationMode, str],
    ) -> "IAethericRiftSystemConfiguration":
        """
        Fluent

        Set the default validation posture for newly created Rifts.

        Args:
            mode:
                Validation mode enum or string.

        Returns:
            IAethericRiftSystemConfiguration: This configuration instance.
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
        if key == "system_frame_mode":
            return EnumHelpers.convert_enum_and_check(value, AethericRiftSystemFrameMode)
        if key == "default_space_type":
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
