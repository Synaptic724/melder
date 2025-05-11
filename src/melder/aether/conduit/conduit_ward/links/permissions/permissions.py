from enum import Enum, auto
from melder.utilities.concurrent_dictionary import ConcurrentDict

class Permission(Enum):
    READ = auto()
    WRITE = auto()

class Permissions:
    """
    Manages permissions for a Link.

    Permissions define what actions are allowed between linked Conduits.
    """

    def __init__(self):
        self._permissions = ConcurrentDict()

    def add(self, permission: str) -> None:
        """
        Add a permission.

        Args:
            permission (str): The permission to add.
        """
        self._permissions[permission] = True

    def remove(self, permission: str) -> None:
        """
        Remove a permission if it exists.

        Args:
            permission (str): The permission to remove.
        """
        if permission in self._permissions:
            del self._permissions[permission]

    def has(self, permission: str) -> bool:
        """
        Check if a permission exists.

        Args:
            permission (str): The permission to check.

        Returns:
            bool: True if permission exists, False otherwise.
        """
        return permission in self._permissions