import uuid
from melder.utilities.interfaces import ISeal
from melder.utilities.concurrent_list import ConcurrentList
from melder.utilities.concurrent_dictionary import ConcurrentDict
from melder.spellbook.configuration.configuration import Configuration
from melder.aether.conduit.conduit import Conduit
import threading
from abc import ABC, abstractmethod

class ISpellbook(ABC, ISeal):
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
    _lock = threading.RLock()
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

    @classmethod
    def configure_conduit_state(cls, **kwargs) -> None:
        """
        Configure the conduit state

        Available configuration keys:

        - conduit_state: The state to set for the conduit system (please read documentation, automatic set by default)
        - debugging: Enable or disable debugging mode (please read documentation, disabled by default)

        This method is idempotent meaning it will not allow you to run it more than once. It will also freeze the configuration.
        :param **kwargs: Configuration options.
        """
        if cls._configuration_locked:
            raise RuntimeError("Configuration is locked. Cannot modify conduit state.")

        for key, value in kwargs.items():
            if key in cls._configuration:
                print(f"Warning: Overwriting existing configuration '{key}'.")
            else:
                raise KeyError(f"Unknown configuration key '{key}'.")
            cls._configuration.set_property(key, value)

        if cls._configuration.validate():
            cls._configuration.freeze()
            cls._configuration_locked = True
        else:
            raise ValueError("Invalid configuration. Please check your settings.")

    @classmethod
    def get_configuration(cls) -> Configuration:
        """
        Get the current configuration of the Spellbook.
        :return: The current configuration.
        """
        return cls._configuration

    def conjure(self, name:str = None) -> Conduit:
        """
        Conjure a new Conduit from this Spellbook.

        Args:
            name (str, optional): The name to assign to the Conduit.

        Returns:
            Conduit: A new Conduit tied to this Spellbook and configured under current world settings.

        Raises:
            RuntimeError: If the Spellbook has already been conjured and configuration is locked.
        """
        if self.is_configuration_locked():
            raise RuntimeError("Spellbook is already conjured.")
        # Perform any necessary operations to conjure the Spellbook
        Spellbook._configuration_locked = True
        return Conduit(spellbook=self, name=name, configuration=Spellbook._configuration)


