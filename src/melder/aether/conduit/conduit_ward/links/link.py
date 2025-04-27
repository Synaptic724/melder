import threading
from enum import Enum
from typing import List
from uuid import UUID
from melder.utilities.interfaces import ISeal, IConduit
from melder.utilities.concurrent_dictionary import ConcurrentDict


class Permission(Enum):
    READ = "read"
    WRITE = "write"
    BORROW = "borrow"
    CLONE = "clone"

class LinkContract:
    def __init__(self, object_id: UUID, permissions: List[Permission], propagate: bool = False):
        self.object_id = object_id
        self.permissions = permissions
        self.propagate = propagate

class LinkPermissions:
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


class Link(ISeal):
    """
    Represents a connection between two Conduits.

    A Link defines the relationship, permissions, and lifecycle between
    the creator and target Conduits.
    """

    def __init__(self, creator: IConduit, target: IConduit):
        """
        Initialize a new Link between two Conduits.

        Args:
            creator (Conduit): The Conduit creating the link.
            target (Conduit): The Conduit being linked to.
        """
        self._creator = creator
        self._target = target

        self._incoming_permissions = LinkPermissions()  # Permissions the target has over the creator
        self._outgoing_permissions = LinkPermissions()  # Permissions the creator has over the target

        self._lock = threading.RLock()
        self.sealed = False

    def add_outgoing_permission(self, permission: str) -> None:
        """
        Add a permission allowing the creator to act on the target.

        Args:
            permission (str): The permission to add.
        """
        if self.sealed:
            raise RuntimeError("Cannot modify a sealed Link.")
        with self._lock:
            self._outgoing_permissions.add(permission)

    def add_incoming_permission(self, permission: str) -> None:
        """
        Add a permission allowing the target to act on the creator.

        Args:
            permission (str): The permission to add.
        """
        if self.sealed:
            raise RuntimeError("Cannot modify a sealed Link.")
        with self._lock:
            self._incoming_permissions.add(permission)

    def seal(self) -> None:
        """
        Seal this Link, preventing any further modifications.
        """
        if self.sealed:
            return
        with self._lock:
            self._creator = None
            self._target = None
            self._incoming_permissions = None
            self._outgoing_permissions = None
            self.sealed = True

