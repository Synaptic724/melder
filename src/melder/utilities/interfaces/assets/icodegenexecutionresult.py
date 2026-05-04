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
class ICodegenExecutionResult(ICleanable, Protocol):
    """
    Interface for the executor-owned codegen result type.
    """

    @property
    def accepted(self) -> bool:
        """
        Return the execution acceptance state.
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
        Return the optional execution reason.
        """
        ...

    @property
    def validation_issues(self) -> Tuple[str, ...]:
        """
        Return the propagated validation issues.
        """
        ...

    @property
    def runtime_error(self) -> Optional[str]:
        """
        Return the optional runtime error summary.
        """
        ...

    @property
    def result(self) -> Optional[object]:
        """
        Return the optional final execution result.
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
        Return the public execution payload.
        """
        ...
