from enum import Enum, auto
from typing import Optional


class ConduitState(Enum):
    """
    Enum representing the state of a Conduit.
    """
    normal = auto()
    lesser = auto()
    sealed = auto()

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
        if isinstance(value, ConduitState):
            return value
        elif isinstance(value, str):
            try:
                return ConduitState[value.lower()]
            except KeyError:
                valid = [s.name.lower() for s in ConduitState]
                raise ValueError(f"Invalid ConduitState '{value}'. Expected one of: {valid}")
        elif value is None:
            return None
        else:
            raise TypeError(f"Expected str, ConduitState, or None — got {type(value).__name__}.")