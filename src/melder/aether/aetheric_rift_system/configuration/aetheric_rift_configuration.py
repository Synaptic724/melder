import threading
from typing import Dict, Optional, Tuple, Type, Union

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.aetheric_rift_system.configuration.rift_space_type import RiftSpaceType
from melder.aether.aetheric_rift_system.configuration.rift_validation_mode import RiftValidationMode
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.general_helpers import EnumHelpers
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.interfaces.interfaces import IAethericRiftConfiguration, IRiftEventConfiguration


class AethericRiftConfiguration(Cleanable, IAethericRiftConfiguration):
    """
    Internal

    Per-Rift configuration object used by the AR system to build/program one
    canonical Rift state.

    Purpose:
        Capture configurable runtime behavior for one Rift without making the
        public Rift shell itself the configuration root.

    Contract:
        - Mutable until frozen.
        - Stores typed properties in one property bag.
        - Provides fluent `with_*` helpers mirroring the Spellbook
          configuration style.
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

        Initialize an empty per-Rift configuration.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._frozen: bool = False
        self._properties: Dict[str, object] = {}
        self.available_properties: Dict[str, Union[Type, Tuple[Type, ...]]] = {
            "target_frame_name": str,
            "space_type": RiftSpaceType,
            "space_name": (str, type(None)),
            "auto_activate_on_program": bool,
            "auto_create_space": bool,
            "validation_mode": RiftValidationMode,
            "event_configuration": (IRiftEventConfiguration, type(None)),
        }

    def cleanup(self) -> None:
        """
        Internal

        Idempotently cleanup the configuration and clear all state.
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
        self.check_cleaned()
        return self._frozen

    def set_property(self, key: str, value: object) -> None:
        self.check_cleaned()
        if self._frozen:
            raise RuntimeError("Cannot modify AethericRiftConfiguration after freeze().")
        if key not in self.available_properties:
            raise ValueError(f"Unknown AethericRiftConfiguration property: '{key}'.")

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
        self.check_cleaned()
        return self._properties[key]

    def has_property(self, key: str) -> bool:
        self.check_cleaned()
        return key in self._properties

    def load_default_dictionary(self) -> None:
        self.check_cleaned()
        defaults = {
            "target_frame_name": "default",
            "space_type": RiftSpaceType.static,
            "space_name": None,
            "auto_activate_on_program": True,
            "auto_create_space": False,
            "validation_mode": RiftValidationMode.strict,
            "event_configuration": None,
        }
        for key, value in defaults.items():
            self.set_property(key, value)

    def validate(self) -> bool:
        self.check_cleaned()
        for key in self.available_properties.keys():
            if key not in self._properties:
                raise ValueError(f"Missing required configuration property: '{key}'.")
        return True

    def freeze(self) -> None:
        self.check_cleaned()
        if self._frozen:
            return
        if not self.validate():
            raise ValueError("AethericRiftConfiguration validation failed.")
        self._frozen = True

    def finalize(self) -> "IAethericRiftConfiguration":
        self.freeze()
        return self

    def build(self) -> "IAethericRiftConfiguration":
        return self.finalize()

    def with_defaults(self) -> "IAethericRiftConfiguration":
        self.load_default_dictionary()
        return self

    def with_target_frame_name(self, frame_name: str) -> "IAethericRiftConfiguration":
        self.set_property("target_frame_name", frame_name)
        return self

    def with_space_type(
            self,
            space_type: Union[RiftSpaceType, str],
    ) -> "IAethericRiftConfiguration":
        self.set_property("space_type", space_type)
        return self

    def with_space_name(
            self,
            space_name: Optional[str],
    ) -> "IAethericRiftConfiguration":
        self.set_property("space_name", space_name)
        return self

    def with_auto_activate_on_program(
            self,
            enabled: bool = True,
    ) -> "IAethericRiftConfiguration":
        self.set_property("auto_activate_on_program", enabled)
        return self

    def with_auto_create_space(
            self,
            enabled: bool = True,
    ) -> "IAethericRiftConfiguration":
        self.set_property("auto_create_space", enabled)
        return self

    def with_validation_mode(
            self,
            mode: Union[RiftValidationMode, str],
    ) -> "IAethericRiftConfiguration":
        self.set_property("validation_mode", mode)
        return self

    def with_event_configuration(
            self,
            event_configuration: Optional[IRiftEventConfiguration],
    ) -> "IAethericRiftConfiguration":
        self.set_property("event_configuration", event_configuration)
        return self

    def _convert_enum_if_needed(self, key: str, value: object) -> object:
        if key == "space_type":
            return EnumHelpers.convert_enum_and_check(value, RiftSpaceType)
        if key == "validation_mode":
            return EnumHelpers.convert_enum_and_check(value, RiftValidationMode)
        return value
