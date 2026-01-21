from enum import Enum, auto
from typing import Optional
from melder.utilities.helpers.general_helpers import EnumHelpers
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class ConduitState(Enum):
    """
    Enum representing the state of a Conduit.
    """
    __melder_internal__ = _mrg.sentinel
    normal = auto()
    lesser = auto()
    cleaned = auto()

    def __str__(self):
        """
        String representation of the ConduitState.
        """
        return self.name.lower()

    @staticmethod
    def resolve(value: str | Enum | None) -> Optional['ConduitState']:
        """
        Resolve a string or ConduitState value into a valid ConduitState enum.

        Args:
            value: Either a lowercase string ("normal", "lesser", etc.), a ConduitState, or None.

        Returns:
            ConduitState enum.

        Raises:
            ValueError: If the string does not match any ConduitState member.
        """
        EnumHelpers.convert_enum_and_check(value=value, enum=ConduitState)