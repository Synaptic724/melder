import threading
from typing import Any, Dict, List, Type
from melder.utilities.data_structures.concurrent_dictionary import ConcurrentDict
from melder.utilities.general_base.sealable import Sealable
from melder.spellbook.configuration.system_state import SystemState

class Configuration(Sealable):
    """
    Configuration governs the behavior of the entire system.

    It acts as the configuration core for:
    * **Conduit Management:** How Conduits handle service lifecycles.
    * **Dynamic Behavior:** Flags controlling dynamic linking, expansion, and policies.
    * **System Flags:** Global settings like debugging mode and resource disposal.

    This object should only be configured once and then frozen to prevent any further changes,
    enforcing idempotent laws across the system. Thread-safe operations are ensured with RLock.
    """

    def __init__(self, aether_frame: str = "default"):
        """
        Initializes a new Configuration manager.

        Args:
            aether_frame (str): The name of the Aether frame this configuration is associated with (defaults to "default").
        """
        # Thread-safe lock for concurrent access
        super().__init__()
        self._lock = threading.RLock()
        self._aether_frame = aether_frame
        self._sealed = False
        self._frozen = False

        # Private dictionary storing all properties.
        self._properties: ConcurrentDict = ConcurrentDict()
        self.available_properties: Dict[str, Type] = {
            "system_state": SystemState,
            "debugging": bool,
            "disposal": bool,
            "disposal_method_names": list
        }

        # Properties that must remain immutable after conjure (idempotent laws of the system).
        self._idempotent_keys = {"system_state", "debugging", "disposal", "disposal_method_names"}

    def seal(self) -> None:
        """
        Seals the configuration, preventing any further modifications and cleaning up resources.

        This method sets both the `sealed` and `frozen` flags.

        Raises:
            RuntimeError: If the configuration is already sealed.
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
        Defines or overwrites a property in the configuration.

        - **Idempotent properties** (e.g., 'system_state') can only be set *once* before the configuration is sealed.
        - **Non-idempotent properties** can be freely modified before the configuration is frozen.

        Args:
            key (str): The name of the property to set.
            value (Any): The value for the property.

        Raises:
            RuntimeError: If the configuration is sealed or frozen.
            RuntimeError: If attempting to modify an idempotent property that is already set.
            TypeError: If `key` is not a string.
            ValueError: If an enum conversion fails.
        """
        self.check_sealed()
        if not isinstance(key, str):
            raise TypeError("Key must be a string.")
        with self._lock:
            if key in self._idempotent_keys and key in self._properties:
                raise RuntimeError(f"Cannot modify idempotent property '{key}' once set.")
            if self._frozen:
                raise RuntimeError("Cannot modify configuration after it is frozen.")
            if key == "system_state" and not isinstance(value, SystemState):
                raise ValueError("system_state must be a SystemState enum.")
            self._properties[key] = value

    def clear_properties(self) -> None:
        """
        Clears all properties in the configuration.

        This method is useful for resetting the configuration to its initial state before it is frozen.

        Raises:
            RuntimeError: If the configuration is sealed or frozen.
        """
        self.check_sealed()
        with self._lock:
            if self._frozen:
                raise RuntimeError("Cannot clear properties after configuration is frozen")
            self._properties.clear()

    def freeze(self) -> None:
        """
        Freezes the configuration property system.

        Once frozen, no properties, including non-idempotent ones, can be modified.
        Validation is performed automatically upon freezing.

        Raises:
            RuntimeError: If the configuration is sealed.
            ValueError: If configuration validation fails prior to freezing (e.g., missing required properties).
        """
        self.check_sealed()
        if not self.validate():
            # Note: validate() itself raises ValueError with a specific message.
            raise ValueError("Configuration validation failed. Cannot freeze.")
        self._properties.freeze()
        with self._lock:
            self._frozen = True

    def validate(self) -> bool:
        """
        Validates that all required configuration properties exist and match expected types.

        Performs both presence/type checks and enum-specific validation.

        Returns:
            bool: True if all validation checks pass.

        Raises:
            RuntimeError: If the configuration is sealed.
            ValueError: If any property is missing or has the wrong type/value.
        """
        self.check_sealed()
        for key, expected_type in self.available_properties.items():
            if key not in self._properties:
                raise ValueError(f"Missing required configuration property: '{key}'.")

            value = self._properties[key]
            # Handle tuple of expected types
            if not isinstance(expected_type, tuple):
                expected_type = (expected_type,)

            if not isinstance(value, expected_type):
                expected_names = [t.__name__ for t in expected_type]
                raise ValueError(
                    f"Invalid type for property '{key}': "
                    f"expected {', '.join(expected_names)}, got {type(value).__name__}."
                )

        # Additional validation for specific properties
        if self.validate_enums():
            return True
        else:
            # Should be caught by validate_enums internal ValueError, but included for safety.
            raise ValueError("Enum validation failed. Invalid enum values found in properties.")

    def validate_enums(self) -> bool:
        """
        Internal

        Validates that all properties intended to be Enums (like `SystemState`) are indeed set to a valid Enum instance.

        Returns:
            bool: True if all enum values are valid.

        Raises:
            RuntimeError: If the configuration is sealed.
            ValueError: If a known enum property is set to an invalid type.
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
        Internal

        Converts string inputs into the correct enum types for known keys.

        Args:
            key (str): The property key.
            value (Any): The value to check/convert.

        Returns:
            Any: The converted Enum value or the original value if no conversion is needed.

        Raises:
            ValueError: If the string value is not a valid enum member or if the input type is incorrect.
        """
        enum_map: Dict[str, Type] = {
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
        Retrieves the value of a configuration property.

        Args:
            key (str): The name of the property.

        Returns:
            Any: The stored value (str, int, bool, Enum, etc.).

        Raises:
            RuntimeError: If the configuration is sealed.
            KeyError: If the property does not exist in the configuration.
        """
        self.check_sealed()
        try:
            return self._properties[key]
        except KeyError:
            raise KeyError(f"Property '{key}' not found in Aether properties.")

    def has_property(self, key: str) -> bool:
        """
        Checks if a configuration property is defined.

        Args:
            key (str): The property name to check.

        Returns:
            bool: True if the property exists, False otherwise.

        Raises:
            RuntimeError: If the configuration is sealed.
        """
        self.check_sealed()
        return key in self._properties

    def __iter__(self):
        """
        Allows iteration over the configuration properties (keys).

        Returns:
            Iterator: Property names (keys) in the configuration.
        """
        return iter(self._properties)

    def load_default_dictionary(self) -> None:
        """
        Loads and applies a default set of properties atomically.

        This method sets sensible defaults for core properties like `system_state`, `debugging`, and `disposal`.

        Raises:
            RuntimeError: If the configuration is sealed.
        """
        self.check_sealed()
        self._properties.batch_update(lambda d: d.update({
            "system_state": SystemState.automatic,
            "debugging": False,
            "disposal": False,
            "disposal_method_names": [],
        }))