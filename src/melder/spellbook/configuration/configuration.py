import threading
from typing import Any, Dict, List, Type
from melder.utilities.data_structures.concurrent_dictionary import ConcurrentDict
from melder.utilities.general_base.sealable import Sealable
from melder.spellbook.configuration.system_state import SystemState

class Configuration(Sealable):
    """
    Configuration governs the behavior of the system.

    It acts as the configuration core for:
      - How Conduits manage their services
      - How Scopes and dynamic behaviors function
      - System-wide flags such as debugging mode, dynamic expansion, and policies

    This object should only be configured once and then frozen to prevent any further changes.
    Thread-safe operations are ensured with RLock.
    """

    def __init__(self, aether_frame: str = "default"):
        # Thread-safe lock for concurrent access
        super().__init__()
        self._lock = threading.RLock()
        self._aether_frame = aether_frame
        self._sealed = False
        self._frozen = False

        # Private dictionary storing all properties.
        self._properties: ConcurrentDict = ConcurrentDict()
        self.available_properties: Dict[str, Type] = {
            "system_state": (str, SystemState),
            "debugging": bool,
            "disposal": bool,
            "disposal_method_names": list
        }

        # Properties that must remain immutable after conjure (idempotent laws of the system).
        self._idempotent_keys = {"system_state", "debugging", "disposal", "disposal_method_names"}

    def seal(self) -> None:
        """
        Seal the properties, preventing any further modifications.

        This is called automatically during Aether conjure.
        """
        if self._sealed:
            return
        with self._lock:
            if self._sealed:
                return
            self._sealed = True
            self._frozen = True
            self._properties.cleanup()
            self._properties = None
            self.available_properties.clear()
            self.available_properties = None

    def set_property(self, key: str, value: Any) -> None:
        """
        Define or overwrite a property.

        - Idempotent properties (like 'conduit_state', 'debugging', etc.)
          can only be set once. Attempts to overwrite will raise an error,
          even before the configuration is frozen.

        - Non-idempotent properties can be freely modified before freeze.
        """
        self.check_sealed()
        if not isinstance(key, str):
            raise TypeError("Key must be a string.")

        with self._lock:
            if key in self._idempotent_keys and key in self._properties:
                raise RuntimeError(f"Cannot modify idempotent property '{key}' once set.")

            if self._frozen:
                raise RuntimeError("Cannot modify configuration after it is frozen.")

            value = self._convert_enum_if_needed(key, value)
            self._properties[key] = value

    def clear_properties(self) -> None:
        """
        Clear all properties in the configuration.

        This method is useful for resetting the configuration to its initial state.
        """
        self.check_sealed()
        with self._lock:
            if self._frozen:
                raise RuntimeError("Cannot clear properties after configuration is frozen")
            self._properties.clear()

    def freeze(self) -> None:
        """
        Freeze the property system.

        Once frozen:
          - Critical properties like 'dynamic' and 'debugging' can no longer be modified.
          - Non-idempotent properties can still be adjusted if needed (depending on design choice).

        This is called automatically during Aether conjure.
        """
        self.check_sealed()
        if not self.validate():
            raise ValueError("Configuration validation failed. Cannot freeze.")
        self._properties.freeze()
        with self._lock:
            self._frozen = True

    def validate(self) -> bool:
        """
        Validate that all required configuration properties exist and match expected types.

        Raises:
            ValueError: If any property is missing or has the wrong type.
        """
        self.check_sealed()
        for key, expected_type in self.available_properties.items():
            if key not in self._properties:
                raise ValueError(f"Missing required configuration property: '{key}'.")

            value = self._properties[key]
            if not isinstance(value, expected_type if isinstance(expected_type, tuple) else (expected_type,)):
                raise ValueError(
                    f"Invalid type for property '{key}': "
                    f"expected {expected_type.__name__}, got {type(value).__name__}."
                )

        # Additional validation for specific properties
        if self.validate_enums():
            return True
        else:
            raise ValueError("Enum validation failed. Invalid enum values found in properties.")

    def validate_enums(self) -> bool:
        """
        Validate that all enum properties are set to valid values.
        :return:
        """
        self.check_sealed()
        # Additional validation for specific properties
        if "system_state" in self._properties:
            system_state = self._properties["system_state"]
            if not isinstance(system_state, SystemState):
                raise ValueError(
                    f"Invalid type for 'system_state': expected SystemState, got {type(system_state).__name__}."
                )
        return True


    def _convert_enum_if_needed(self, key: str, value: Any) -> Any:
        """
        Converts string inputs into the correct enum types for known keys.
        Raises ValueError if the conversion fails.
        """
        enum_map = {
            "system_state": SystemState,
        }

        if key in enum_map:
            enum_type = enum_map[key]
            if isinstance(value, str):
                try:
                    return enum_type[value.lower()]  # Requires enum keys to be lowercase
                except KeyError:
                    valid_options = [e.name for e in enum_type]
                    raise ValueError(
                        f"Invalid value '{value}' for '{key}'. "
                        f"Expected one of: {valid_options}."
                    )
            elif not isinstance(value, enum_type):
                raise ValueError(
                    f"Invalid type for '{key}': expected {enum_type.__name__}, got {type(value).__name__}."
                )
        return value

    def get_property(self, key: str) -> Any:
        """
        Retrieve the value of a property.

        :param key: The name of the property.
        :return: The stored value (str, int, or bool).

        Raises:
            KeyError if the property does not exist.
        """
        self.check_sealed()
        try:
            return self._properties[key]
        except KeyError:
            raise KeyError(f"Property '{key}' not found in Aether properties.")

    def has_property(self, key: str) -> bool:
        """
        Check if a property is defined.

        :param key: The property name to check.
        :return: True if the property exists, False otherwise.
        """
        self.check_sealed()
        return key in self._properties

    def __iter__(self):
        """
        Allow iteration over the properties.
        :return: Property names (keys) in the configuration.
        """
        return iter(self._properties)

    def load_default_dictionary(self) -> None:
        """
        Load and apply the default dictionary of properties atomically.
        """
        self.check_sealed()
        self._properties.batch_update(lambda d: d.update({
            "system_state": self._convert_enum_if_needed("system_state", "automatic"),
            "debugging": False,
            "disposal": False,
            "disposal_method_names": [],
        }))