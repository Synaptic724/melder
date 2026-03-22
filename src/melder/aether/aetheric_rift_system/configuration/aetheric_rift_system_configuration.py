import threading
from typing import Dict, Optional, Sequence, Tuple, Type, Union

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
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
        - Governs process-wide creation/access policy, frame topology, target
          frame restrictions, and per-Rift defaults.
        - Once finalized, property mutation is disallowed.

    Lifecycle:
        Owned by `Aether` / `AethericRiftSystem` as the installed central
        governance object. Cleanup clears all stored properties and freezes the
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
            "shared_system_frame_enabled": bool,
            "default_system_frame_name": str,
            "isolated_system_frame_name_prefix": str,
            "auto_create_system_frame": bool,
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

    def cleanup(self) -> None:
        """
        Internal

        Idempotently cleanup the configuration and clear all state.

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

    @property
    def frozen(self) -> bool:
        """
        Returns:
            bool: True when the configuration is finalized.
        """
        self.check_cleaned()
        return self._frozen

    def set_property(self, key: str, value: object) -> None:
        """
        Internal

        Set one configuration property before finalize().

        Args:
            key:
                Property name.
            value:
                Property value.

        Returns:
            None.

        Raises:
            RuntimeError: If the configuration is cleaned or frozen.
            TypeError: If the property type is invalid.
            ValueError: If the property name is unknown.
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

        Returns:
            object: Stored property value.
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

        Returns:
            bool: True when present.
        """
        self.check_cleaned()
        return key in self._properties

    def load_default_dictionary(self) -> None:
        """
        Internal

        Load the standard default property set for the AR system.

        Returns:
            None.
        """
        self.check_cleaned()
        defaults = {
            "allow_rift_creation": False,
            "creation_token_required": False,
            "creation_token_value": None,
            "allow_direct_rift_access": False,
            "rift_access_token_required": False,
            "rift_access_token_value": None,
            "allow_direct_state_access": False,
            "state_access_token_required": False,
            "state_access_token_value": None,
            "allow_external_rift_registration": False,
            "allow_nested_rift_creation": False,
            "shared_system_frame_enabled": True,
            "default_system_frame_name": "aetheric_rift_system",
            "isolated_system_frame_name_prefix": "aetheric_rift",
            "auto_create_system_frame": True,
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

        Returns:
            bool: True when the configuration is valid.

        Raises:
            ValueError: If a required property is missing or the property set is
                internally inconsistent.
        """
        self.check_cleaned()
        for key in self.available_properties.keys():
            if key not in self._properties:
                raise ValueError("Missing required configuration property: '{0}'.".format(key))

        default_system_frame_name = self.get_property("default_system_frame_name")
        isolated_system_frame_name_prefix = self.get_property("isolated_system_frame_name_prefix")
        default_target_frame_name = self.get_property("default_target_frame_name")
        allowed_target_frame_names = self.get_property("allowed_target_frame_names")
        denied_target_frame_names = self.get_property("denied_target_frame_names")
        shared_system_frame_enabled = self.get_property("shared_system_frame_enabled")
        max_system_frame_count = self.get_property("max_system_frame_count")
        allow_multiple_target_frames = self.get_property("allow_multiple_target_frames")
        max_target_frame_count = self.get_property("max_target_frame_count")

        if not default_system_frame_name:
            raise ValueError("default_system_frame_name cannot be empty.")
        if not isolated_system_frame_name_prefix:
            raise ValueError("isolated_system_frame_name_prefix cannot be empty.")
        if not default_target_frame_name:
            raise ValueError("default_target_frame_name cannot be empty.")
        if max_system_frame_count < 1:
            raise ValueError("max_system_frame_count must be >= 1.")
        if max_target_frame_count < 1:
            raise ValueError("max_target_frame_count must be >= 1.")
        if shared_system_frame_enabled and max_system_frame_count != 1:
            raise ValueError("max_system_frame_count must be 1 when shared_system_frame_enabled is True.")
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

        Returns:
            None.
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
        """
        self.freeze()
        return self

    def build(self) -> "IAethericRiftSystemConfiguration":
        """
        Fluent alias for finalize().
        """
        return self.finalize()

    def with_defaults(self) -> "IAethericRiftSystemConfiguration":
        """
        Fluent

        Load the standard AR system defaults and return `self`.
        """
        self.load_default_dictionary()
        return self

    def with_rift_creation_enabled(
            self,
            enabled: bool = True,
    ) -> "IAethericRiftSystemConfiguration":
        self.set_property("allow_rift_creation", enabled)
        return self

    def with_creation_token_required(
            self,
            enabled: bool = True,
    ) -> "IAethericRiftSystemConfiguration":
        self.set_property("creation_token_required", enabled)
        return self

    def with_creation_token(
            self,
            token_value: Optional[str],
    ) -> "IAethericRiftSystemConfiguration":
        self.set_property("creation_token_value", token_value)
        return self

    def with_direct_rift_access(
            self,
            enabled: bool = True,
    ) -> "IAethericRiftSystemConfiguration":
        self.set_property("allow_direct_rift_access", enabled)
        return self

    def with_rift_access_token_required(
            self,
            enabled: bool = True,
    ) -> "IAethericRiftSystemConfiguration":
        self.set_property("rift_access_token_required", enabled)
        return self

    def with_rift_access_token(
            self,
            token_value: Optional[str],
    ) -> "IAethericRiftSystemConfiguration":
        self.set_property("rift_access_token_value", token_value)
        return self

    def with_direct_state_access(
            self,
            enabled: bool = True,
    ) -> "IAethericRiftSystemConfiguration":
        self.set_property("allow_direct_state_access", enabled)
        return self

    def with_state_access_token_required(
            self,
            enabled: bool = True,
    ) -> "IAethericRiftSystemConfiguration":
        self.set_property("state_access_token_required", enabled)
        return self

    def with_state_access_token(
            self,
            token_value: Optional[str],
    ) -> "IAethericRiftSystemConfiguration":
        self.set_property("state_access_token_value", token_value)
        return self

    def with_allow_external_rift_registration(
            self,
            enabled: bool = True,
    ) -> "IAethericRiftSystemConfiguration":
        self.set_property("allow_external_rift_registration", enabled)
        return self

    def with_allow_nested_rift_creation(
            self,
            enabled: bool = True,
    ) -> "IAethericRiftSystemConfiguration":
        self.set_property("allow_nested_rift_creation", enabled)
        return self

    def with_shared_system_frame_enabled(
            self,
            enabled: bool = True,
    ) -> "IAethericRiftSystemConfiguration":
        self.set_property("shared_system_frame_enabled", enabled)
        return self

    def with_default_system_frame_name(
            self,
            frame_name: str,
    ) -> "IAethericRiftSystemConfiguration":
        self.set_property("default_system_frame_name", frame_name)
        return self

    def with_isolated_system_frame_name_prefix(
            self,
            prefix: str,
    ) -> "IAethericRiftSystemConfiguration":
        self.set_property("isolated_system_frame_name_prefix", prefix)
        return self

    def with_auto_create_system_frame(
            self,
            enabled: bool = True,
    ) -> "IAethericRiftSystemConfiguration":
        self.set_property("auto_create_system_frame", enabled)
        return self

    def with_max_system_frame_count(
            self,
            count: int,
    ) -> "IAethericRiftSystemConfiguration":
        self.set_property("max_system_frame_count", count)
        return self

    def with_default_target_frame_name(
            self,
            frame_name: str,
    ) -> "IAethericRiftSystemConfiguration":
        self.set_property("default_target_frame_name", frame_name)
        return self

    def with_allowed_target_frame_names(
            self,
            frame_names: Sequence[str],
    ) -> "IAethericRiftSystemConfiguration":
        self.set_property("allowed_target_frame_names", frame_names)
        return self

    def with_denied_target_frame_names(
            self,
            frame_names: Sequence[str],
    ) -> "IAethericRiftSystemConfiguration":
        self.set_property("denied_target_frame_names", frame_names)
        return self

    def with_target_frame_override(
            self,
            enabled: bool = True,
    ) -> "IAethericRiftSystemConfiguration":
        self.set_property("allow_target_frame_override", enabled)
        return self

    def with_multiple_target_frames(
            self,
            enabled: bool = True,
    ) -> "IAethericRiftSystemConfiguration":
        self.set_property("allow_multiple_target_frames", enabled)
        return self

    def with_max_target_frame_count(
            self,
            count: int,
    ) -> "IAethericRiftSystemConfiguration":
        self.set_property("max_target_frame_count", count)
        return self

    def with_default_space_type(
            self,
            space_type: Union[RiftSpaceType, str],
    ) -> "IAethericRiftSystemConfiguration":
        self.set_property("default_space_type", space_type)
        return self

    def with_default_auto_activate_on_program(
            self,
            enabled: bool = True,
    ) -> "IAethericRiftSystemConfiguration":
        self.set_property("default_auto_activate_on_program", enabled)
        return self

    def with_default_auto_create_space(
            self,
            enabled: bool = True,
    ) -> "IAethericRiftSystemConfiguration":
        self.set_property("default_auto_create_space", enabled)
        return self

    def with_default_validation_mode(
            self,
            mode: Union[RiftValidationMode, str],
    ) -> "IAethericRiftSystemConfiguration":
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
        """
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

        Returns:
            Tuple[str, ...]: Normalized immutable frame-name sequence.

        Raises:
            TypeError: If the input is not a valid string sequence.
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
