import threading
from threading import RLock
from types import ModuleType
from typing import runtime_checkable, Type, Protocol, Optional, List, Union, Dict, Any, Iterable, Iterator, Callable, \
    Tuple, Mapping, Set, Sequence, Self

from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.dev_ops.spell_system_states.spell_state_change_reason import SpellStateChangeReason
from melder.spellbook.existence.existence import Existence
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


@runtime_checkable
class IFrameACLViewProfileStrategy(Protocol):
    """
    Reusable strategy contract for building one configured view ACL profile.

    Contract:
        - Exposes one stable strategy/profile name.
        - Returns a freshly configured `IFrameACLViewProfile` instance when
          asked to build.
        - Carries no shared mutable module-level state itself.
    """

    @property
    def name(self) -> str:
        """
        Return the stable view-profile strategy name.

        Returns:
            str: Canonical strategy/profile name.
        """
        ...

    def build(self) -> "IFrameACLViewProfile":
        """
        Build and return one configured view ACL profile instance.

        Returns:
            IFrameACLViewProfile: Fresh configured profile instance.
        """
        ...
