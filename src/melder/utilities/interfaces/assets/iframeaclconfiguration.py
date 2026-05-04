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
class IFrameACLConfiguration(ICleanable, Protocol):
    """
    Typed frame ACL root configuration contract.

    Contract:
        - Represents one selected frame-local ACL bundle.
        - Owns the typed child configurations that describe view, command, and
          codegen policy for that bundle.
        - Is the unit selected by named frame ACL contract binding.
    """

    frame_name: str
    configuration_id: str
    locked: bool
    view_configuration: IFrameACLViewConfiguration
    command_configuration: IFrameACLCommandConfiguration
    codegen_configuration: IFrameACLCodegenConfiguration
