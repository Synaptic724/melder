import uuid
from melder.utilities.interfaces import Seal
from melder.utilities.concurrent_list import ConcurrentList
from melder.utilities.concurrent_dictionary import ConcurrentDict
from melder.spellbook.configuration.configuration import Configuration
import threading
from abc import ABC, abstractmethod

class ISpellbook(ABC, Seal):
    """
    Interface for Spellbook, which is a graph structure that behaves like a scope and a factory.
    """
    @abstractmethod
    def bind(self, spell):
        """
        Adds a new spell to the Spellbook.
        :param spell: The spell to add.
        """
        pass

    @abstractmethod
    def remove_bind(self, spell):
        """
        Removes a spell from the Spellbook.
        :param spell: The spell to remove.
        """
        pass

class Spellbook(ISpellbook):
    """
    The Spellbook stores all spells and sets the system configuration
    if it's the first Spellbook created.
    """
    _lock = threading.Lock()
    # Class variable shared across all Spellbooks
    _configuration_locked: bool = False
    _configuration = Configuration()

    @classmethod
    def is_configuration_locked(cls) -> bool:
        """
        Check if the global configuration has been locked.
        """
        return cls._configuration_locked

    @classmethod
    def lock_configuration(cls) -> None:
        """
        Lock the global configuration, preventing future modification.
        """
        if cls._configuration_locked:
            raise RuntimeError("Configuration is already locked.")
        # Lock the configuration

        with cls._lock:
            # Perform any necessary operations to lock the configuration
            cls._configuration_locked = True

    def __init__(self):
        # Normal instance variables here
        pass

