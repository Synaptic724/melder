import threading
import uuid
from abc import ABC, abstractmethod
from melder.utilities.interfaces import ISeal
from melder.utilities.concurrent_list import ConcurrentList
from melder.utilities.concurrent_dictionary import ConcurrentDict

class LinkPermissions:
    """
    Class to manage permissions for linking.
    """
    def __init__(self):
        self.permissions = ConcurrentDict()

    def add_permission(self, permission):
        self.permissions[permission] = True

    def remove_permission(self, permission):
        if permission in self.permissions:
            del self.permissions[permission]

    def has_permission(self, permission) -> bool:
        return permission in self.permissions


class ILink(ABC, ISeal):
    """
    Interface for Link, which is a graph structure that behaves like a scope and a factory.
    """
    @abstractmethod
    def link(self):
        """
        Links the conduit to another conduit.
        :return:
        """
        pass

    @abstractmethod
    def seal(self):
        """
        Disposes of the current conduit and its lesser conduits
        """
        pass



class Link(ILink):
    """
    Link is a graph structure that also behaves like a scope and a factory.
    """
    def __init__(self):
        """
        Initializes the Link with a root node.
        """
        self.sealed = False

        self._link_creator = None
        self._link_target = None
        self._permissions = LinkPermissions()
        self._lock = threading.RLock()
        self._ID = uuid.uuid4()


    def link(self, target_link) -> bool:
        """
        Links the current link to another link while dynamic environment is enabled.
        :param target_link: The target link to link to.
        """
        if self.sealed:
            raise RuntimeError("Cannot link to a sealed link.")
        if not self._dynamic_environment:
            raise RuntimeError("Dynamic environment is not enabled. Cannot manually link services.")
        with self._lock:
            self._greater_link = target_link
            target_link._lesser_links.append(self)


    def seal(self):
        """
        Seals the current link and its lesser links.
        """
        if self.sealed:
            raise RuntimeError("Link is already sealed.")
        with self._lock:
            for link in self._lesser_links:
                link.seal()
            self.sealed = True