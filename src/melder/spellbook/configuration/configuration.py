import threading
from typing import Any, Dict, List, Type
from melder.utilities.concurrent_dictionary import ConcurrentDict
from melder.utilities.interfaces import ISeal

class Configuration(ISeal):
    """
    Configuration governs the behavior of the system.

    It acts as the configuration core for:
      - How Conduits manage their services
      - How Scopes and dynamic behaviors function
      - System-wide flags such as debugging mode, dynamic expansion, and policies

    It is a singleton class, ensuring that only one instance exists throughout the system.
    Once Aether is conjured, critical properties become immutable to preserve system integrity.

    This object should only be configured once and then frozen to prevent any further changes.
    """
    _instance = None
    _lock = threading.RLock()
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(Configuration, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not Configuration._initialized:
            Configuration._initialized = True
            self.sealed = False
            # Private dictionary storing all properties.
            self._properties: ConcurrentDict = ConcurrentDict()
            self.available_properties: Dict[str, Type] = {
                "conduit_state": str,
                "debugging": bool,
                "disposal": bool,
                "disposal_method_names": list
            }

            # Properties that must remain immutable after conjure (idempotent laws of the system).
            self._idempotent_keys = {"conduit_state", "debugging", "disposal", "disposal_method_names"}

            # Indicates whether the properties have been frozen (sealed after conjure).
            self._frozen = False

    def set_property(self, key: str, value: Any) -> None:
        """
        Define or overwrite a property.

        - Idempotent properties (like 'conduit_state', 'debugging', etc.)
          can only be set once. Attempts to overwrite will raise an error,
          even before the configuration is frozen.

        - Non-idempotent properties can be freely modified before freeze.
        """
        if not isinstance(key, str):
            raise TypeError("Key must be a string.")

        # Enforce idempotency for critical system properties
        if key in self._idempotent_keys:
            if key in self._properties:
                raise RuntimeError(f"Cannot modify idempotent property '{key}' once set.")

        # Enforce freeze globally
        if self._frozen:
            raise RuntimeError("Cannot modify configuration after it is frozen.")

        self._properties[key] = value

    def clear_properties(self) -> None:
        """
        Clear all properties in the configuration.

        This method is useful for resetting the configuration to its initial state.
        """
        if self._frozen:
            raise RuntimeError("Cannot clear properties after configuration is frozen")
        elif self.sealed:
            raise RuntimeError("Cannot clear properties after configuration is sealed")
        self._properties.clear()


    def freeze(self) -> None:
        """
        Freeze the property system, sealing all idempotent properties.

        Once frozen:
          - Critical properties like 'dynamic' and 'debugging' can no longer be modified.
          - Non-idempotent properties can still be adjusted if needed (depending on design choice).

        This is called automatically during Aether conjure.
        """
        if not self.validate():
            raise ValueError("Configuration validation failed. Cannot freeze.")
        self._properties.freeze()
        with Configuration._lock:
            self.sealed = True
        self._frozen = True

    def validate(self) -> bool:
        """
        Validate that all required configuration properties exist and match expected types.

        Raises:
            ValueError: If any property is missing or has the wrong type.
        """
        for key, expected_type in self.available_properties.items():
            # Check presence
            if key not in self._properties:
                raise ValueError(f"Missing required configuration property: '{key}'.")

            # Check type
            value = self._properties[key]
            if not isinstance(value, expected_type):
                raise ValueError(
                    f"Invalid type for property '{key}': "
                    f"expected {expected_type.__name__}, got {type(value).__name__}."
                )

        return True

    def get_property(self, key: str) -> Any:
        """
        Retrieve the value of a property.

        :param key: The name of the property.
        :return: The stored value (str, int, or bool).

        Raises:
            KeyError if the property does not exist.

        Example:
            dynamic_mode = aether_properties.get_property('dynamic')
        """
        try:
            return self._properties[key]
        except KeyError:
            raise KeyError(f"Property '{key}' not found in Aether properties.")

    def has_property(self, key: str) -> bool:
        """
        Check if a property is defined.

        :param key: The property name to check.
        :return: True if the property exists, False otherwise.

        Example:
            if aether_properties.has_property('debugging'):
                # Safe to access 'debugging' property
        """
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
        self._properties.batch_update(lambda d: d.update({
            "conduit_state": "automatic",
            "debugging": False,
            "disposal": False,
            "disposal_method_names": []
        }))

    def seal(self) -> None:
        """
        Seal the properties, preventing any further modifications.

        This is called automatically during Aether conjure.
        """
        if self.sealed:
            return
        with Configuration._lock:
            self._properties.dispose()
            self.sealed = True
            self._frozen = True