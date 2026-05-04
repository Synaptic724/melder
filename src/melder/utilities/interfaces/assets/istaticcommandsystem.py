import threading
from threading import RLock
from types import ModuleType
from typing import runtime_checkable, Type, Protocol, Optional, List, Union, Dict, Any, Iterable, Iterator, Callable, \
    Tuple, Mapping, Set, Sequence, Self

from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.dev_ops.spell_system_states.spell_state_change_reason import SpellStateChangeReason
from melder.spellbook.existence.existence import Existence
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


from melder.utilities.interfaces.assets.icommandsystem import ICommandSystem

@runtime_checkable
class IStaticCommandSystem(ICommandSystem, Protocol):
    """
    Interface for the static-room command system.
    """

    def meld_existing_spell(
            self,
            conduit_id: str,
            spell_name: Optional[str] = None,
            *,
            spell: Optional[object] = None,
            spellframe: Optional[object] = None,
            binding_name: Optional[str] = None,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one already-live spell runtime object through a selected conduit.
        """
        ...

    def describe_spell_status_by_source_id(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> dict:
        """
        Return static availability status for one published spell source id.
        """
        ...

    def describe_spell_status_by_id(
            self,
            spell_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> dict:
        """
        Return static availability status for one current spell id.
        """
        ...

    def describe_spell_status_by_index_id(
            self,
            spell_index_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> dict:
        """
        Return static availability status for one stable spell lineage id.
        """
        ...
