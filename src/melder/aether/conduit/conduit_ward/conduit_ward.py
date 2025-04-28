import uuid
from abc import ABC
from melder.utilities.concurrent_dictionary import ConcurrentDict
from melder.utilities.concurrent_list import ConcurrentList
from melder.utilities.interfaces import ISeal, IConduit, ISpellbook
import threading


class ConduitWard(ISeal):
    def __init__(self, conduit: IConduit):
        """
        Conduitward is a class that manages the links between conduits.
        :param conduit:
        """
        super().__init__()
        self._lock = threading.RLock()
        self._conduit = conduit
        self.active_links = ConcurrentList()

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