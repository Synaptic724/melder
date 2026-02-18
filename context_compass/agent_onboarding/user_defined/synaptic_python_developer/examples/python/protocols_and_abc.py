"""
Purpose:
- Show when to use Protocol versus ABC.

Notes:
- Protocols model structural contracts across multiple implementations.
- ABCs enforce shared behavior and explicit inheritance.
"""

from abc import ABC, abstractmethod
from typing import Protocol


class SupportsClose(Protocol):
    """
    Structural protocol for closeable resources.
    """

    def close(self) -> None:
        """
        Close the resource.
        """


class BaseStore(ABC):
    """
    Abstract base class for key/value stores.
    """

    @abstractmethod
    def get(self, key: str) -> str:
        """
        Retrieve a value by key.

        Args:
            key (str): Lookup key.

        Returns:
            str: Stored value.
        """


class InMemoryStore(BaseStore):
    """
    Simple in-memory store implementation.
    """

    def __init__(self) -> None:
        """
        Initialize the store.
        """
        self._data: dict[str, str] = {}

    def get(self, key: str) -> str:
        """
        Retrieve a value by key.

        Args:
            key (str): Lookup key.

        Returns:
            str: Stored value.

        Raises:
            KeyError: If the key is not present.
        """
        if key not in self._data:
            raise KeyError(key)
        return self._data[key]

    def set(self, key: str, value: str) -> None:
        """
        Set a value by key.

        Args:
            key (str): Lookup key.
            value (str): Value to store.
        """
        self._data[key] = value
