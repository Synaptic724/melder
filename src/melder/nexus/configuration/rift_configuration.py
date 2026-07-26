import threading
from typing import Dict, Optional, Tuple, Type, Union

from melder.nexus.configuration.rift_space_type import RiftSpaceType
from melder.nexus.configuration.rift_validation_mode import RiftValidationMode
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.general_helpers import EnumHelpers
from melder.utilities.helpers.id_builder import IDBuilder


class RiftConfiguration(Cleanable):
    """
    Internal

    Per-Rift configuration object used by `Nexus` to build one live Rift.

    Purpose:
        Capture configurable runtime behavior for one Rift without making the
        live public `Rift` object itself the configuration root.

    Contract:
        - Mutable until frozen.
        - Stores typed properties in one property bag.
        - Provides fluent `with_*` helpers mirroring the Spellbook
          configuration style.
        - Captures per-Rift runtime defaults only; process-wide governance lives
          in `NexusConfiguration`.

    Registration:
        MELDER KERNEL - guarded. Built through `Nexus.create_rift_configuration`
        and consumed at Rift creation.

    Subsystem Context:
        The per-Rift configuration object, sitting below process-wide
        `NexusConfiguration`. Its `space_type` is what programs the Rift's one
        primary room.

    System Context:
        The opening line states the design rule plainly: the live public `Rift`
        is NOT the configuration root. Keeping configuration in a separate
        mutable-then-frozen object means a Rift's runtime surface stays about
        live behaviour, and configuration cannot be mutated through the object
        callers hold.
        This is also where the process-wide/per-Rift boundary lands. Creation
        and access gates, frame topology, and budgets are governance and belong
        to `NexusConfiguration`; room posture and per-Rift defaults legitimately
        differ between Rifts and belong here.

    AGENT_ACCESS: public

    AGENT_PURPOSE:
        access: public. Per-Rift settings, chiefly space_type which fixes the room posture for
        the Rift's life. Mutable until frozen. Build via Nexus.create_rift_configuration().
    """

    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_frozen",
        "_consumed",
        "_properties",
        "available_properties",
    ]

    def __init__(self) -> None:
        """
        Internal

        Initialize an empty per-Rift configuration.

        Contract:
            - STARTS EMPTY: the property bag holds nothing until seeded, so a bare
              configuration is not yet usable.
            - The schema is four keys - `space_type` (RiftSpaceType), `space_name`
              (str or None), `auto_activate_on_program` (bool) and
              `validation_mode` (RiftValidationMode). `space_name` is the only one
              that legally accepts None.
            - Lifecycle is MUTABLE -> FROZEN -> CONSUMED. Note the third stage is
              CONSUMED, not "activated": a rift configuration is spent by the rift
              that takes it rather than marked live in place.

        Owned State:
            Owns its lock, id, the property bag and the declared type table.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            None.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._frozen: bool = False
        self._consumed: bool = False
        self._properties: Dict[str, object] = {}
        self.available_properties: Dict[str, Union[Type, Tuple[Type, ...]]] = {
            "space_type": RiftSpaceType,
            "space_name": (str, type(None)),
            "auto_activate_on_program": bool,
            "validation_mode": RiftValidationMode,
        }

    def cleanup(self) -> None:
        """
        Internal

        Idempotently cleanup the configuration and clear all state.

        Contract:
            - Marks the object cleaned and frozen.
            - Clears the property bag and property registry.

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
            self._consumed = True
            self._properties.clear()
            self.available_properties.clear()

            del self._properties
            del self.available_properties
            del self._id
        del self._lock

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

    @property
    def consumed(self) -> bool:
        """
        Purpose:
            Return whether this configuration has already been consumed by Rift
            creation.

        Returns:
            bool: True when consumed.
        """
        self.check_cleaned()
        return self._consumed

    def set_property(self, key: str, value: object) -> None:
        """
        Internal

        Set one per-Rift configuration property before freeze().

        Args:
            key:
                Property name.
            value:
                Property value.

        Contract:
            - Rejects mutation after freeze().
            - Normalizes enum-backed values before storage.
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
            raise RuntimeError("Cannot modify RiftConfiguration after freeze().")
        if self._consumed:
            raise RuntimeError("Cannot modify RiftConfiguration after it has been consumed.")
        if key not in self.available_properties:
            raise ValueError(f"Unknown RiftConfiguration property: '{key}'.")

        expected_type = self.available_properties[key]
        converted_value = self._convert_enum_if_needed(key, value)
        if not isinstance(expected_type, tuple):
            expected_type = (expected_type,)
        if not isinstance(converted_value, expected_type):
            expected_names = ", ".join(t.__name__ for t in expected_type)
            raise TypeError(
                f"Invalid type for property '{key}': expected {expected_names}, got {type(converted_value).__name__}."
            )
        self._properties[key] = converted_value

    def get_property(self, key: str) -> object:
        """
        Internal

        Return one per-Rift configuration property value.

        Args:
            key:
                Property name.

        Returns:
            object: Stored property value.

        Raises:
            KeyError: If the property has not been set.
        """
        self.check_cleaned()
        return self._properties[key]

    @property
    def space_type(self) -> RiftSpaceType:
        """
        Return the typed top-level room kind for this configuration.

        Returns:
            RiftSpaceType: Stored room kind used when programming the primary
            Rift space.

        Raises:
            TypeError:
                If the stored `space_type` payload is not a `RiftSpaceType`.
        """
        value = self.get_property("space_type")
        if not isinstance(value, RiftSpaceType):
            raise TypeError("space_type must be a RiftSpaceType.")
        return value

    def has_property(self, key: str) -> bool:
        """
        Internal

        Return whether a property has been set.

        Args:
            key:
                Property name.

        Contract:
            - Tests whether the key has been SET, not whether it is a legal key. An
              unknown key returns False rather than raising.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            bool: True when present.
        """
        self.check_cleaned()
        return key in self._properties

    def load_default_dictionary(self) -> None:
        """
        Internal

        Load the standard default property set for one Rift.

        Contract:
            - Sets default room type, room naming posture, activation posture,
              validation mode, and room-event configuration defaults used when
              Nexus builds a Rift without overrides.
            - Does not select or bind any target frames.

        Returns:
            None.
        """
        self.check_cleaned()
        defaults = {
            "space_type": RiftSpaceType.static,
            "space_name": None,
            "auto_activate_on_program": True,
            "validation_mode": RiftValidationMode.strict,
        }
        for key, value in defaults.items():
            self.set_property(key, value)

    def validate(self) -> bool:
        """
        Internal

        Validate that every required per-Rift property is present.

        Contract:
            - Ensures every declared per-Rift property has a value before
              programming/build.
            - Performs presence checks only; enum normalization already happens
              during `set_property(...)`.

        Returns:
            bool: True when the configuration is valid.

        Raises:
            ValueError: If a required property is missing.
        """
        self.check_cleaned()
        for key in self.available_properties.keys():
            if key not in self._properties:
                raise ValueError(f"Missing required configuration property: '{key}'.")
        return True

    def freeze(self) -> None:
        """
        Internal

        Validate and freeze the configuration.

        Contract:
            - Calls `validate()` before setting the frozen state.
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
            raise ValueError("RiftConfiguration validation failed.")
        self._frozen = True

    def finalize(self) -> RiftConfiguration:
        """
        Fluent

        Validate and freeze the configuration, then return `self`.

        Contract:
            - Returns this same configuration instance after freezing it.
            - Does not allocate or clone a detached configuration object.

        Returns:
            RiftConfiguration: This configuration instance.
        """
        self.freeze()
        return self

    def mark_consumed(self) -> None:
        """
        Internal

        Mark this configuration as consumed by successful Rift creation.

        Contract:
            - Consumed configurations are not reusable for another Rift.
            - Does not imply cleanup.

        Returns:
            None.
        """
        self.check_cleaned()
        self._consumed = True

    def build(self) -> RiftConfiguration:
        """
        Fluent alias for `finalize()`.

        Contract:
            - Preserves the builder-style API used by Rift creation flows.
            - Returns this same configuration instance after finalize/freeze.

        Returns:
            RiftConfiguration: This configuration instance.
        """
        return self.finalize()

    def with_defaults(self) -> RiftConfiguration:
        """
        Fluent

        Load the standard per-Rift defaults and return `self`.

        Contract:
            - Delegates to `load_default_dictionary()`.
            - Applies the default per-Rift property set in-place.
            - Leaves the configuration mutable until `freeze()` or `finalize()`.

        Returns:
            RiftConfiguration: This configuration instance.
        """
        self.load_default_dictionary()
        return self

    def with_space_type(
            self,
            space_type: Union[RiftSpaceType, str],
    ) -> RiftConfiguration:
        """
        Fluent

        Set the top-level room type for this Rift.

        Args:
            space_type:
                Room-kind enum or string (`static`, `capability`, or
                `codegen`) used to
                instantiate the primary space during Rift creation.

        Contract:
            - Selects the PRIMARY space instantiated during rift creation. Accepts the
              enum or its string name (`static`, `capability`, `codegen`);
              conversion is checked, so an unrecognized name raises.
            - MUTATES THIS OBJECT and returns `self`; not a copying builder.
            - Refused once frozen.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            RiftConfiguration: This configuration instance.
        """
        self.set_property("space_type", space_type)
        return self

    def with_space_name(
            self,
            space_name: Optional[str],
    ) -> RiftConfiguration:
        """
        Fluent

        Set the initial room name for this Rift, if any.

        Args:
            space_name:
                Optional stable room name.

        Contract:
            - The one property whose declared type admits None, so passing None is a
              legal "unnamed space" rather than an error.
            - MUTATES THIS OBJECT and returns `self`.
            - Refused once frozen.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            RiftConfiguration: This configuration instance.
        """
        self.set_property("space_name", space_name)
        return self

    def with_auto_activate_on_program(
            self,
            enabled: bool = True,
    ) -> RiftConfiguration:
        """
        Fluent

        Set whether the Rift activates immediately when programmed.

        Args:
            enabled:
                True to mark the Rift active during programming.

        Contract:
            - Decides whether programming a rift also activates it, rather than
              leaving activation as a separate explicit step.
            - MUTATES THIS OBJECT and returns `self`.
            - Refused once frozen.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            RiftConfiguration: This configuration instance.
        """
        self.set_property("auto_activate_on_program", enabled)
        return self

    def with_validation_mode(
            self,
            mode: Union[RiftValidationMode, str],
    ) -> RiftConfiguration:
        """
        Fluent

        Set the validation posture for this Rift.

        Args:
            mode:
                Validation mode enum or string.

        Contract:
            - Sets the strictness applied to rift contents. Accepts the enum or its
              string name; conversion is checked.
            - MUTATES THIS OBJECT and returns `self`.
            - Refused once frozen.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            RiftConfiguration: This configuration instance.
        """
        self.set_property("validation_mode", mode)
        return self

    def _convert_enum_if_needed(self, key: str, value: object) -> object:
        """
        Internal

        Normalize enum-backed properties before storage.

        Args:
            key:
                Property name being assigned.
            value:
                Candidate property value.

        Returns:
            object: Normalized property value.
        """
        if key == "space_type":
            if value == "dynamic":
                value = RiftSpaceType.codegen
            return EnumHelpers.convert_enum_and_check(value, RiftSpaceType)
        if key == "validation_mode":
            return EnumHelpers.convert_enum_and_check(value, RiftValidationMode)
        return value
