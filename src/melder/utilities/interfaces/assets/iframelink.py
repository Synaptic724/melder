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
class IFrameLink(ICleanable, Protocol):
    """
    Interface for one view-safe frame target entry.
    """

    @property
    def link_id(self) -> str:
        """
        Return the canonical target-entry id.
        """
        ...

    @property
    def frame_name(self) -> str:
        """
        Return the owning frame name.
        """
        ...

    @property
    def source_kind(self) -> str:
        """
        Return the source kind label.
        """
        ...

    @property
    def source_id(self) -> str:
        """
        Return the stable source identifier.
        """
        ...

    @property
    def display_name(self) -> str:
        """
        Return the viewer-facing display name.
        """
        ...

    @property
    def metadata(self) -> Dict[str, object]:
        """
        Return detached metadata for the target entry.
        """
        ...

    def clone(self) -> "IFrameLink":
        """
        Return a detached copy of this target entry.
        """
        ...
