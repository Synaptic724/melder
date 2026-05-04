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
class IFrameACLCodegenProfileStrategy(Protocol):
    """
    Reusable strategy contract for building one configured codegen ACL profile.

    Contract:
        - Exposes one stable strategy/profile name.
        - Returns a freshly configured `IFrameACLCodegenProfile` instance when
          asked to build.
        - Carries no shared mutable module-level state itself.
    """

    @property
    def name(self) -> str:
        """
        Return the stable codegen-profile strategy name.

        Returns:
            str: Canonical strategy/profile name.
        """
        ...

    def build(self) -> "IFrameACLCodegenProfile":
        """
        Build and return one configured codegen ACL profile instance.

        Returns:
            IFrameACLCodegenProfile: Fresh configured profile instance.
        """
        ...
