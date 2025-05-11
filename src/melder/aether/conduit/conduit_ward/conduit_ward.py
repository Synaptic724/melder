import uuid
import threading
from enum import Enum
from typing import List
from melder.aether.aether import Aether
from melder.utilities.concurrent_dictionary import ConcurrentDict
from melder.utilities.concurrent_list import ConcurrentList
from melder.utilities.concurrent_set import ConcurrentSet
from melder.utilities.interfaces import IConduit, ISpellbook, IConduitWard, IPolicy

class Permission(Enum):
    READ = "read"
    WRITE = "write"
    BORROW = "borrow"
    CLONE = "clone"

class LinkContract:
    def __init__(self, object_id: uuid.UUID, permissions: List[Permission], propagate: bool = False):
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



class ConduitWard(IConduitWard):
    """
    Conduitward is a class that manages the links between conduits.
    """
    _aether = Aether()
    def __init__(self, conduit: IConduit, dynamic: bool, conduit_type: str):
        """
        Conduitward is a class that manages the links between conduits.
        :param conduit:
        """
        super().__init__()
        self._lock = threading.RLock()
        self._conduit = conduit
        self._dynamic = dynamic
        self._conduit_type = conduit_type
        self._policy = None

        ## Internal structures
        self._conduit_link = None
        self._lesser_conduits_links = ConcurrentList()
        self.active_links = ConcurrentList()
        self._create_internal_configuration()


#region Properties
    @property
    def policy(self) -> IPolicy:
        """
        Gets the policy for the conduit ward.
        :return:
        """
        return self._policy

    @policy.setter
    def policy(self, value: IPolicy):
        """
        Sets the policy for the conduit ward.
        :param policy:
        :return:
        """
        self._policy = value
#endregion

    def _create_internal_configuration(self) -> None:
        """
        Creates per-Conduit internal structures based on the current world configuration.
        """
        self._configure_conduit_links()

    def _configure_conduit_links(self) -> None:
        """
        Configures whether this Conduit maintains linkable connections.
        Only enabled in dynamic environments.
        """
        if self._dynamic:
            self._conduit_links = ConcurrentList()
        else:
            self._conduit_links = None

    def remove_link(self, other_conduit):
        pass

    def get_links(self):
        return self.active_links

    def add_link(self, other_conduit):
        pass

    def seal(self):
        """
        Seals the conduit ward, preventing any further modifications.
        """
        pass


    def _clean_up_lesser_conduits_links(self):
        """
        Cleans up all lesser conduits.
        :return:
        """
        if self._lesser_conduits_links:
            for lesser_conduit in self._lesser_conduits_links:
                lesser_conduit.seal()
            self._lesser_conduits_links.dispose()

    def _clean_up_links(self):
        """
        Cleans up all links.
        :return:
        """
        if self._conduit_links:
            for link in self._conduit_links:
                link.seal()
            self._conduit_links.dispose()
