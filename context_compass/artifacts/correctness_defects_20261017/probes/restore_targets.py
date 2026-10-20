"""Importable spell targets for probe_restore_staged_structure.py (hydration re-imports them by module and qualname)."""
from typing import Protocol


class Greeter(Protocol):
    """The contract every greeter version implements."""

    def greet(self) -> str: ...


class English:
    """Version 1, bound active."""

    def greet(self) -> str:
        """Return the English greeting."""
        return "hello"


class French:
    """Version 2, staged parked."""

    def greet(self) -> str:
        """Return the French greeting."""
        return "bonjour"
