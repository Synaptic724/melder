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
        Configure the conduit state.

        Only verifies allowed keys at this stage.
        Type and value validation happens during final validation.

        If any configuration errors occur, all attempted settings are cleared.
        """
        if cls._configuration_locked:
            raise RuntimeError("Configuration is locked. Cannot modify conduit state.")

        try:
            for key, value in kwargs.items():
                if key not in cls._configuration.available_properties:
                    raise KeyError(
                        f"Unknown configuration key '{key}'. "
                        f"Allowed keys are: {list(cls._configuration.available_properties.keys())}"
                    )

                cls._configuration.set_property(key, value)

            if not cls._configuration.validate():
                raise ValueError("Invalid configuration. Please check your settings.")

            cls._configuration.freeze()
            cls._configuration_locked = True

        except (KeyError, ValueError) as e:
            cls._configuration.clear_properties()
            raise e

        except Exception:
            raise

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
        else:
            Spellbook._configuration.load_default_dictionary()
            Spellbook._configuration.freeze()
            Spellbook._configuration_locked = True

        # Perform any necessary operations to conjure the Spellbook
        return Conduit(spellbook=self, name=name, configuration=Spellbook._configuration)


