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
class IFrameACLRule(ICleanable, Protocol):
    """
    ACL rule contract for reusable profile and applied configuration work.
    """

    rule_name: str
    operation: str
    effect: str
    conditions: Dict[str, Any]

    def to_json_dict(self) -> Dict[str, Any]:
        """
        Return the rule as a JSON-compatible dictionary.

        Returns:
            Dict[str, Any]: JSON-compatible rule dictionary.
        """
        ...
