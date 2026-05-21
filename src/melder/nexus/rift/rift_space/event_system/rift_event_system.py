import threading
from typing import Callable, Dict, Optional
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.nexus.rift.rift_space.event_system.rift_event import RiftEvent
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class RiftEventSystem(Cleanable):
    """
    Internal

    Room-local callback-driven event publisher owned by `RiftSpace`.

    Purpose:
        Centralize event callback registration, event creation, and synchronous
        event emission in one room-owned object instead of scattering that
        logic across `RiftSpace` and a separate configuration bag.

    Contract:
        - Owns the callback registry for one `RiftSpace`.
        - Owns the stable room identity required to build `RiftEvent` objects.
        - Emits events synchronously to the currently registered callbacks.
        - Cleanup is idempotent and clears all owned callbacks and identity
          references.

    Threading / Concurrency:
        Owns one instance `RLock` for grouped callback-registry mutation and
        event-system cleanup.

    Lifecycle:
        Owned by one `RiftSpace`. Cleanup happens as part of room teardown.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_rift_id",
        "_space_id",
        "_space_kind",
        "_callbacks_by_subscription_id",
    ]

    def __init__(
            self,
            *,
            rift_id: str,
            space_id: str,
            space_kind: str,
    ) -> None:
        """
        Initialize one room-local event system.

        Args:
            rift_id:
                Owning Rift id.
            space_id:
                Owning space id.
            space_kind:
                Owning space kind.

        Returns:
            None.

        Raises:
            ValueError: If one required identity field is empty.
        """
        super().__init__()
        if not rift_id:
            raise ValueError("rift_id cannot be empty.")
        if not space_id:
            raise ValueError("space_id cannot be empty.")
        if not space_kind:
            raise ValueError("space_kind cannot be empty.")
        self._lock: threading.RLock = threading.RLock()
        self._rift_id: str = rift_id
        self._space_id: str = space_id
        self._space_kind: str = space_kind
        self._callbacks_by_subscription_id: Dict[str, Callable[[RiftEvent], None]] = {}

    def cleanup(self) -> None:
        """
        Idempotently clear event-system state.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._callbacks_by_subscription_id.clear()

            del self._callbacks_by_subscription_id
            del self._space_kind
            del self._space_id
            del self._rift_id
        del self._lock

    @property
    def rift_id(self) -> str:
        """Return the owning Rift id."""
        self.check_cleaned()
        return self._rift_id

    @property
    def space_id(self) -> str:
        """Return the owning space id."""
        self.check_cleaned()
        return self._space_id

    @property
    def space_kind(self) -> str:
        """Return the owning space kind."""
        self.check_cleaned()
        return self._space_kind

    def register_event_callback(
            self,
            callback: Callable[[RiftEvent], None],
    ) -> str:
        """
        Register one event callback for this room.

        Args:
            callback:
                Callback invoked once per emitted event.

        Returns:
            str: Stable subscription id for later unregistration.

        Raises:
            TypeError: If `callback` is not callable.
        """
        self.check_cleaned()
        if not callable(callback):
            raise TypeError("callback must be callable.")
        with self._lock:
            subscription_id = IDBuilder.create_id()
            self._callbacks_by_subscription_id[subscription_id] = callback
            return subscription_id

    def unregister_event_callback(self, subscription_id: str) -> None:
        """
        Remove one event callback subscription by id.

        Args:
            subscription_id:
                Subscription id returned by `register_event_callback(...)`.

        Returns:
            None.

        Raises:
            ValueError: If `subscription_id` is empty.
        """
        self.check_cleaned()
        if not subscription_id:
            raise ValueError("subscription_id cannot be empty.")
        with self._lock:
            self._callbacks_by_subscription_id.pop(subscription_id, None)

    def create_event(
            self,
            event_type: str,
            *,
            payload: Optional[Dict[str, object]] = None,
            frame_name: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> RiftEvent:
        """
        Create one room-local runtime event without emitting it.

        Args:
            event_type:
                Stable event type name.
            payload:
                Optional payload mapping.
            frame_name:
                Optional related frame name.
            metadata:
                Optional metadata mapping.

        Returns:
            RiftEvent: New event object.

        Raises:
            ValueError: If `event_type` is empty.
        """
        self.check_cleaned()
        if not event_type:
            raise ValueError("event_type cannot be empty.")
        return RiftEvent(
            event_type=event_type,
            rift_id=self._rift_id,
            space_id=self._space_id,
            space_kind=self._space_kind,
            frame_name=frame_name,
            payload=payload,
            metadata=metadata,
        )

    def emit_event(self, event: RiftEvent) -> None:
        """
        Emit one runtime event to all registered callbacks.

        Args:
            event:
                Event object to emit.

        Returns:
            None.

        Raises:
            TypeError: If `event` does not satisfy `RiftEvent`.
        """
        self.check_cleaned()
        if not isinstance(event, RiftEvent):
            raise TypeError("event must satisfy RiftEvent.")
        with self._lock:
            callbacks = list(self._callbacks_by_subscription_id.values())
        for callback in callbacks:
            callback(event)

    def create_and_emit_event(
            self,
            event_type: str,
            *,
            payload: Optional[Dict[str, object]] = None,
            frame_name: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> RiftEvent:
        """
        Create one runtime event and emit it immediately.

        Args:
            event_type:
                Stable event type name.
            payload:
                Optional payload mapping.
            frame_name:
                Optional related frame name.
            metadata:
                Optional metadata mapping.

        Returns:
            RiftEvent: Emitted event object.
        """
        event = self.create_event(
            event_type,
            payload=payload,
            frame_name=frame_name,
            metadata=metadata,
        )
        self.emit_event(event)
        return event
