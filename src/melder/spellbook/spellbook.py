import uuid
from melder.utilities.interfaces import ISpellbook
from melder.utilities.concurrent_list import ConcurrentList
from melder.utilities.concurrent_dictionary import ConcurrentDict
from melder.spellbook.configuration.configuration import Configuration
from melder.aether.conduit.conduit import Conduit
import threading


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
        self._lock = threading.RLock()
        self._conjured = False

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

    def conjure(self, name: str = None) -> None:
        """
        Conjure a new Conduit from this Spellbook.

        Automatic mode:
            - Only one spellbook can conjure.
            - Configuration is frozen once.

        Dynamic mode:
            - Each spellbook can conjure once.
            - Configuration is frozen the first time.
        """
        mode = Spellbook._configuration.get_property("conduit_state")

        if mode == "automatic":
            self._conjure_automatic(name)
        elif mode == "dynamic":
            self._conjure_dynamic(name)
        else:
            raise RuntimeError(f"Unknown conduit_state: {mode}")

    def _conjure_automatic(self, name: str = None) -> Conduit:
        """
        Conjure a new Conduit from this Spellbook in automatic mode.
        """
        with Spellbook._lock:
            # Dynamically create the __global_conjured__ attribute if it doesn't exist
            if getattr(Spellbook, "__global_conjured__", False):
                raise RuntimeError("Automatic mode allows only one Spellbook to conjure once.")

            if not Spellbook.is_configuration_locked():
                Spellbook._configuration.load_default_dictionary()
                Spellbook._configuration.freeze()
                Spellbook._configuration_locked = True

            # Only now — patch the global conjure flag
            setattr(Spellbook, "__global_conjured__", True)

            return Conduit(spellbook=self, name=name, configuration=Spellbook._configuration)

    def _conjure_dynamic(self, name: str = None) -> Conduit:
        """
        Conjure a new Conduit from this Spellbook in dynamic mode.
        """
        with self._lock:
            if self._conjured:
                raise RuntimeError("This Spellbook already conjured a Conduit.")

            if not Spellbook.is_configuration_locked():
                Spellbook._configuration.load_default_dictionary()
                Spellbook._configuration.freeze()
                Spellbook._configuration_locked = True

            self._conjured = True
            return Conduit(spellbook=self, name=name, configuration=Spellbook._configuration)
