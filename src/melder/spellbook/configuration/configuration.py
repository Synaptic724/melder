import threading
from typing import Any, Dict
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
            self._properties: ConcurrentDict = ConcurrentDict(self._load_default_dictionary())

            # Properties that must remain immutable after conjure (idempotent laws of the system).
            self._idempotent_keys = {"conduit_state", "debugging"}

            # Indicates whether the properties have been frozen (sealed after conjure).
            self._frozen = False

    def set_property(self, key: str, value: Any) -> None:
        """
        Define or overwrite a property.

        :param key: Property name (must be a string).
        :param value: Property value (must be a str, int, or bool).

        Behavior:
          - Idempotent properties cannot be modified after freeze.
          - Overwriting an existing property triggers a warning (but is allowed pre-freeze).

        Example:
            aether_properties.set_property('dynamic', False)
        """
        if not isinstance(key, str):
            raise TypeError("Key must be a string.")

        if not isinstance(value, (str, int, bool)):
            raise TypeError("Value must be of type str, int, or bool.")

        # Block mutation of critical system properties after freeze
        if self._frozen and key in self._idempotent_keys:
            raise RuntimeError(f"Cannot modify idempotent property '{key}' after system freeze.")

        if key in self._properties:
            print(f"Warning: Overwriting existing property '{key}'.")

        self._properties[key] = value

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
        Validate the properties to ensure they are set correctly.

        This method should be called before sealing the configuration.
        It checks for required properties and their types.

        Raises:
            ValueError if any required property is missing or has an invalid type.
        """
        # Implement validation logic as needed
        pass


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
        return self._properties.__iter__()


    def _load_default_dictionary(self) -> Dict[str, Any]:
        """
        Load the default dictionary of properties.
        :return:
        """
        # This method should be implemented to load default properties.
        # For now, it returns an empty dictionary.
        return { "conduit_state" : "automatic",
                 "debugging" : False }

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