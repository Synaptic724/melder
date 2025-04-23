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

    def __init__(self):
        # Normal instance variables here
        self._lock = threading.RLock()
        self._conjured = False
        self._configuration_locked: bool = False
        self._configuration = Configuration()

    def is_configuration_locked(self) -> bool:
        """
        Check if the configuration for this Spellbook has been locked.
        """
        return self._configuration_locked

    def lock_configuration(self) -> None:
        """
        Lock this Spellbook's configuration, preventing future modification.
        """
        if self._configuration_locked:
            raise RuntimeError("Configuration is already locked.")
        with self._lock:
            self._configuration_locked = True

    def configure_conduit_state(self, **kwargs) -> None:
        """
        Configure the conduit state.

        Only verifies allowed keys at this stage.
        Type and value validation happens during final validation.

        If any configuration errors occur, all attempted settings are cleared.
        """
        if self._configuration_locked:
            raise RuntimeError("Configuration is locked. Cannot modify conduit state.")

        try:
            for key, value in kwargs.items():
                if key not in self._configuration.available_properties:
                    raise KeyError(
                        f"Unknown configuration key '{key}'. "
                        f"Allowed keys are: {list(self._configuration.available_properties.keys())}"
                    )

                self._configuration.set_property(key, value)

            if not self._configuration.validate():
                raise ValueError("Invalid configuration. Please check your settings.")

            self._configuration.freeze()
            self._configuration_locked = True

        except (KeyError, ValueError) as e:
            self._configuration.clear_properties()
            raise e

        except Exception:
            raise

    def get_configuration(self) -> Configuration:
        """
        Get the current configuration of the Spellbook.
        :return: The current configuration.
        """
        return self._configuration

    def conjure(self, name: str = None) -> Conduit:
        """
        Conjure a new Conduit from this Spellbook.

        Automatic mode:
            - Only one conduit per Spellbook.
            - Configuration is frozen once.

        Dynamic mode:
            - Each Spellbook can conjure once.
            - Configuration is frozen the first time.
        """
        with self._lock:
            if self._conjured:
                raise RuntimeError(
                    "This Spellbook has already conjured a Conduit. "
                    "Only one is allowed per Spellbook."
                )

            if not self.is_configuration_locked():
                self._configuration.load_default_dictionary()
                self._configuration.freeze()
                self._configuration_locked = True

            self._conjured = True
            return Conduit(spellbook=self, name=name, conduit_state="normal", configuration=self._configuration)
