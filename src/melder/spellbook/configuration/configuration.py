import threading
from enum import Enum
from typing import Any, Dict, List, Type, Callable
from melder.utilities.data_structures.concurrent_dictionary import ConcurrentDict
from melder.utilities.general_base.sealable import Sealable
from melder.spellbook.configuration.system_state import SystemState
from melder.utilities.helpers.general_helpers import EnumHelpers
from melder.utilities.interfaces.interfaces import IConfiguration, IAethericFrame
from melder.utilities.helpers.package import Pack

class Configuration(Sealable, IConfiguration):
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
        self._aether_frame: str = aether_frame
        self._sealed = False
        self._frozen = False

        self._logger_factory: Pack[[object], Any] | None = None # Pack is used for management of callables

        # Private dictionary storing all properties.
        self._properties: ConcurrentDict = ConcurrentDict()
        self.available_properties: ConcurrentDict[str, Type] = ConcurrentDict({
            "system_state": SystemState,
            "debugging": bool,
            "disposal": bool,
            "disposal_method_names": list,
            "propagate_factory_logger": bool,
        })

        # Properties that must remain immutable after conjure (idempotent laws of the system).
        self._idempotent_keys = {"system_state", "debugging", "disposal", "disposal_method_names", "propagate_factory_logger"}

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

            if self._logger_factory is not None:
                if hasattr(self._logger_factory, "cleanup"):
                    self._logger_factory.cleanup()
                self._logger_factory = None

            self._properties.cleanup()
            self._properties = None
            self.available_properties.cleanup()
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
        if self._frozen:
            raise RuntimeError("Cannot modify configuration after it is frozen.")

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

    def should_propagate(self) -> bool:
        """
        Internal

        Return True if a logger factory is present AND propagation is enabled.
        """
        self.check_sealed()
        with self._lock:
            factory_present = self._logger_factory is not None
            enabled = bool(self._properties.get("propagate_factory_logger", False))
        return factory_present and enabled


    def is_logger_propagation_enabled(self) -> bool:
        """
        Public API

        Return the raw propagation flag (does not check for a factory).
        """
        self.check_sealed()
        with self._lock:
            return bool(self._properties.get("propagate_factory_logger", False))

    def set_logger_factory(self, factory: Callable[[object], Any]) -> None:
        """
        Set the logger factory used by this configuration to produce per-object loggers.

        Contract:
            factory(obj: object) -> Any
            (e.g., Iris ChannelLogger, SafeLogger, stdlib logger, or None)

        Rules:
            - Must be set BEFORE freeze().
            - Not part of the idempotent properties.
            - Thread-safe replacement.

        Raises:
            RuntimeError: If the configuration is sealed or frozen.
            TypeError: If 'factory' is not callable.
        """
        self.check_sealed()
        if factory is None:
            raise TypeError("logger_factory cannot be None; must be callable(obj) -> Any")
        if self._frozen:
            raise RuntimeError("Cannot modify logger factory after configuration is frozen.")
        if not callable(factory):
            raise TypeError("logger_factory must be callable(obj) -> Any")

        packed_callable = Pack.bundle(factory)
        if packed_callable.is_async:
            raise TypeError("logger_factory must be a synchronous callable.")

        with self._lock:
            self._logger_factory = packed_callable
            self._logger_factory_set = True


    def get_logger_for(self, obj: object) -> Any | None:
        """
        Resolve a logger-like for 'obj' using the current logger factory.

        Returns:
            Any: Whatever the factory returns (Iris logger, SafeLogger, stdlib logger, or None).
        """
        self.check_sealed()
        with self._lock:
            factory = self._logger_factory
        if factory is None:
            return None
        return factory(obj)

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
        if self._frozen:
            return
        if not self.validate():
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
        enum_map: Dict[str, Type[Enum]] = {
            "system_state": SystemState,
        }

        enum_type = enum_map.get(key)
        if enum_type is None:
            # No conversion rule for this key; keep the original value (per docstring).
            return value

        # Normalize via shared helper: accepts str|Enum, raises on None/invalid.
        return EnumHelpers.convert_enum_and_check(value, enum_type)

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
            "system_state": self._convert_enum_if_needed("system_state", "automatic"),
            "debugging": False,
            "disposal": False,
            "disposal_method_names": [],
            "propagate_factory_logger": True,
        }))

    def has_logger_factory(self) -> bool:
        """Return True if a logger factory has been set."""
        self.check_sealed()
        with self._lock:
            return self._logger_factory is not None

    # ---------------------------
    # Fluent / Builder-style API
    # ---------------------------

    def clear_logger_factory(self) -> IConfiguration:
        """
        Clear the logger factory (pre-freeze only) and return `self`.
        """
        self.check_sealed()
        if self._frozen:
            raise RuntimeError("Cannot modify logger factory after configuration is frozen.")
        with self._lock:
            self._logger_factory = None
            self._logger_factory_set = False
        return self

    def with_logger_factory(self, factory: Callable[[object], Any]) -> IConfiguration:
        """
        Fluent

        Set the logger factory (factory(obj) -> Any) and return `self`.
        Must be called before freeze().
        """
        self.set_logger_factory(factory)
        return self


    def with_defaults(self) -> IConfiguration:
        """
        Fluent

        Load Melder’s standard defaults into this configuration and return `self`
        so you can keep chaining.

        Behavior:
        - Sets: system_state="automatic", debugging=False, disposal=False,
          disposal_method_names=[].
        - Respects idempotency and immutability rules (raises if frozen or sealed).

        Returns:
            IConfiguration: This same configuration instance (for chaining).
        """
        self.load_default_dictionary()
        return self

    def with_system_state(self, state: SystemState | str) -> IConfiguration:
        """
        Fluent

        Set the system state ("automatic" or "dynamic") and return `self`.

        Notes:
        - Accepts either SystemState or a case-insensitive string.
        - Idempotent: can be set only once before freeze; attempting to overwrite raises.

        Args:
            state: Desired system state (SystemState or "automatic"|"dynamic").

        Returns:
            IConfiguration: This same configuration instance (for chaining).
        """
        self.set_property("system_state", state)
        return self

    def with_debugging(self, enabled: bool = True) -> IConfiguration:
        """
        Fluent

        Enable or disable debugging and return `self`.

        Args:
            enabled: True to enable debugging; False to disable.

        Returns:
            IConfiguration: This same configuration instance (for chaining).
        """
        self.set_property("debugging", enabled)
        return self

    def with_disposal(self, enabled: bool = True) -> IConfiguration:
        """
        Fluent

        Enable or disable disposal features and return `self`.

        Args:
            enabled: True to enable disposal semantics; False to disable.

        Returns:
            IConfiguration: This same configuration instance (for chaining).
        """
        self.set_property("disposal", enabled)
        return self

    def with_disposal_method_names(self, names: list[str]) -> IConfiguration:
        """
        Fluent

        Replace the entire list of disposal method names and return `self`.

        Example:
            cfg.with_disposal_method_names(["close", "cleanup"])

        Args:
            names: Full replacement list of method names (strings).

        Returns:
            IConfiguration: This same configuration instance (for chaining).
        """
        if not isinstance(names, list):
            raise TypeError("disposal_method_names must be a list[str].")
        self.set_property("disposal_method_names", names)
        return self

    def add_disposal_methods(self, *names: str) -> IConfiguration:
        """
        Fluent

        Append one or more disposal method names (deduplicated, order-preserving)
        and return `self`.

        Behavior:
        - Initializes the list to [] if unset.
        - Preserves existing order; adds new names at the end if not already present.

        Args:
            *names: One or more method names to add.

        Returns:
            IConfiguration: This same configuration instance (for chaining).
        """
        current = self._properties.get("disposal_method_names", [])
        if not isinstance(current, list):
            raise ValueError("Internal error: 'disposal_method_names' is not a list.")
        seen = set(current)
        extended: list[str] = list(current)
        for nm in names:
            if not isinstance(nm, str):
                raise TypeError("All disposal method names must be strings.")
            if nm not in seen:
                extended.append(nm)
                seen.add(nm)
        self.set_property("disposal_method_names", extended)
        return self

    def with_logger_propagation(self, enabled: bool = True) -> 'IConfiguration':
        """
        Fluent

        Enable/disable propagation of the logger factory to Aether/Spellbook/Conduits
        and return self.

        Args:
            enabled: True to enable propagation, False to disable.

        Returns:
            IConfiguration: this instance.
        """
        self.set_property("propagate_factory_logger", bool(enabled))
        return self

    def finalize(self) -> IConfiguration:
        """
        Fluent

        Validate and freeze, returning `self`.

        Returns:
            IConfiguration: This same configuration instance (for chaining).
        """
        self.freeze()
        return self

    def build(self) -> IConfiguration:
        """
        Fluent alias for finalize().
        """
        return self.finalize()

    def dynamic_defaults(self) -> IConfiguration:
        """
        Fluent

        Load defaults and set dynamic state, returning `self`.
        """
        return self.with_defaults().with_system_state("dynamic")

    def automatic_defaults(self) -> IConfiguration:
        """
        Fluent

        Load defaults and set automatic state, returning `self`.
        """
        return self.with_defaults().with_system_state("automatic")
