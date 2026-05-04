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
class ICodegenValidationResult(ICleanable, Protocol):
    """
    Interface for the validator-owned codegen result type.
    """

    @property
    def accepted(self) -> bool:
        """
        Return the validation acceptance state.
        """
        ...

    @property
    def frame_name(self) -> str:
        """
        Return the target frame name.
        """
        ...

    @property
    def reason(self) -> Optional[str]:
        """
        Return the optional validation reason.
        """
        ...

    @property
    def validation_issues(self) -> Tuple[str, ...]:
        """
        Return the validation issues tuple.
        """
        ...

    @property
    def transaction_id(self) -> Optional[str]:
        """
        Return the optional transaction id.
        """
        ...

    def to_payload(self) -> Dict[str, object]:
        """
        Return the public validation payload.
        """
        ...
