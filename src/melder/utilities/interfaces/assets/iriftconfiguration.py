import threading
from threading import RLock
from types import ModuleType
from typing import runtime_checkable, Type, Protocol, Optional, List, Union, Dict, Any, Iterable, Iterator, Callable, \
    Tuple, Mapping, Set, Sequence, Self

from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.dev_ops.spell_system_states.spell_state_change_reason import SpellStateChangeReason
from melder.spellbook.existence.existence import Existence
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


from melder.utilities.interfaces.assets.icleanable import ICleanable

@runtime_checkable
class IRiftConfiguration(ICleanable, Protocol):
    """
    Interface for per-Rift programming/build configuration.
    """

    available_properties: Dict[str, object]

    @property
    def frozen(self) -> bool:
        """
        Return whether this Rift configuration has been frozen against further mutation.
        """
        ...

    @property
    def consumed(self) -> bool:
        """
        Return whether this configuration has already been consumed by a Rift creation flow.
        """
        ...

    def set_property(self, key: str, value: object) -> None:
        """
        Set one Rift configuration property by key.

        Returns:
            None.
        """
        ...

    def get_property(self, key: str) -> object:
        """
        Return one Rift configuration property value by key.
        """
        ...

    def has_property(self, key: str) -> bool:
        """
        Return whether one Rift configuration property exists.
        """
        ...

    def load_default_dictionary(self) -> None:
        """
        Load the default Rift configuration dictionary into this instance.

        Returns:
            None.
        """
        ...

    def validate(self) -> bool:
        """
        Validate the current Rift configuration payload.
        """
        ...

    def freeze(self) -> None:
        """
        Freeze the current Rift configuration so later mutation is disallowed.

        Returns:
            None.
        """
        ...

    def finalize(self) -> "IRiftConfiguration":
        """
        Finalize this configuration and return the resulting configuration object.
        """
        ...

    def build(self) -> "IRiftConfiguration":
        """
        Build and return the finalized Rift configuration object.
        """
        ...

    def with_defaults(self) -> "IRiftConfiguration":
        """
        Apply the default Rift configuration values and return this configuration.
        """
        ...

    def with_space_type(self, space_type: object) -> "IRiftConfiguration":
        """
        Set the top-level RiftSpace type for this Rift configuration.
        """
        ...

    def with_space_name(self, space_name: Optional[str]) -> "IRiftConfiguration":
        """
        Set the primary space name for this Rift configuration.
        """
        ...

    def with_auto_activate_on_program(self, enabled: bool = True) -> "IRiftConfiguration":
        """
        Set whether the Rift should be marked active during programming.
        """
        ...

    def with_validation_mode(self, mode: object) -> "IRiftConfiguration":
        """
        Set the validation posture for this Rift configuration.
        """
        ...

    def mark_consumed(self) -> None:
        """
        Mark this configuration as consumed so it is not reused for another Rift build.

        Returns:
            None.
        """
        ...
