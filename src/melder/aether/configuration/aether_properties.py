from typing import Any
from melder.utilities.concurrent_dictionary import ConcurrentDict
from melder.utilities.interfaces import Seal

class AetherProperties(Seal):
    """
    AetherProperties governs the behavior of the Aether system.

    It acts as the configuration core for:
      - How Aether executes
      - How Conduits manage their services
      - How Scopes and dynamic behaviors function
      - System-wide flags such as debugging mode, dynamic expansion, and policies

    Once Aether is conjured, critical properties become immutable to preserve system integrity.
    """

    def __init__(self):
        # Private dictionary storing all properties.
        self._properties: ConcurrentDict = ConcurrentDict()

        # Properties that must remain immutable after conjure (idempotent laws of the system).
        self._idempotent_keys = {"dynamic", "debugging"}

        # Indicates whether the properties have been frozen (sealed after conjure).
        self._frozen = False

        self._sealed = False

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
        self._properties.freeze()
        self._frozen = True

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

    def seal(self) -> None:
        """
        Seal the properties, preventing any further modifications.

        This is called automatically during Aether conjure.
        """
        if self._sealed:
            return
        self._properties.dispose()
        self._sealed = True
        self._frozen = True