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
class ICodegenNamespace(ICleanable, Protocol):
    """
    Interface for one live codegen namespace.
    """

    @property
    def configuration(self) -> ICodegenNamespaceConfiguration:
        """
        Return the configuration that produced this namespace.
        """
        ...

    @property
    def globals_dict(self) -> Dict[str, object]:
        """
        Return the live globals dictionary.
        """
        ...

    @property
    def locals_dict(self) -> Dict[str, object]:
        """
        Return the live locals dictionary.
        """
        ...

    @property
    def metadata(self) -> Dict[str, object]:
        """
        Return detached metadata for this namespace.
        """
        ...

    def get_result(self) -> Optional[object]:
        """
        Return the optional `result` value from this namespace.
        """
        ...
