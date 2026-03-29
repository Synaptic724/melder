from typing import Callable, Iterable, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import IRiftAction, IRiftEventConfiguration, IRiftMemory


class RiftEventConfiguration(Cleanable, IRiftEventConfiguration):
    """
    Internal

    Minimal configuration seam for room-level action and memory event handling.

    Purpose:
        Provide one room-local configuration object that defines how
        `RiftAction` and `RiftMemory` events are enriched and observed without
        introducing a separate hook/plugin object hierarchy.

    Contract:
        - Stores ordered callables for action and memory enrichment/observation.
        - Does not execute those callables by itself; execution belongs to the
          room/activity layer.
        - Cleanup is idempotent and clears all configured callables.

    Lifecycle:
        Owned by `RiftSpace`. When the room is cleaned, this configuration is
        cleaned with it.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_action_enrichers",
        "_memory_enrichers",
        "_action_observers",
        "_memory_observers",
    ]

    def __init__(
            self,
            *,
            action_enrichers: Optional[Iterable[Callable[[IRiftAction], None]]] = None,
            memory_enrichers: Optional[Iterable[Callable[[IRiftMemory], None]]] = None,
            action_observers: Optional[Iterable[Callable[[IRiftAction], None]]] = None,
            memory_observers: Optional[Iterable[Callable[[IRiftMemory], None]]] = None,
    ) -> None:
        """
        Internal

        Initialize room-level event configuration.

        Args:
            action_enrichers:
                Optional ordered callables that enrich `RiftAction` events.
            memory_enrichers:
                Optional ordered callables that enrich `RiftMemory` events.
            action_observers:
                Optional ordered callables that observe `RiftAction` events.
            memory_observers:
                Optional ordered callables that observe `RiftMemory` events.

        Returns:
            None.

        Raises:
            No custom validation errors are raised in this scaffold. Iterable
            inputs are normalized to ordered lists owned by this configuration.
        """
        super().__init__()
        self._action_enrichers = list(action_enrichers) if action_enrichers else []
        self._memory_enrichers = list(memory_enrichers) if memory_enrichers else []
        self._action_observers = list(action_observers) if action_observers else []
        self._memory_observers = list(memory_observers) if memory_observers else []

    def cleanup(self) -> None:
        """
        Internal

        Idempotently clear all configured event callables.

        Contract:
            - Drops all ordered callback lists.
            - Leaves the configuration unusable after cleanup.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._action_enrichers = None
        self._memory_enrichers = None
        self._action_observers = None
        self._memory_observers = None
