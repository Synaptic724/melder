from datetime import datetime, timezone
from typing import Dict, Optional

from melder.utilities.helpers.id_builder import IDBuilder


class RiftEvent:
    """
    Internal

    Immutable emitted event object for `RiftSpace`.

    Purpose:
        Carry one structured runtime event from `RiftSpace` to subscribed
        external callbacks without requiring a local queue or event thread.

    Contract:
        - Event identity and timestamp are fixed at creation time.
        - Payload and metadata are copied on construction.
        - The event object does not own cleanup or runtime orchestration.

    Args:
        event_type:
            Stable event type name.
        rift_id:
            Owning Rift id.
        space_id:
            Emitting space id.
        space_kind:
            Emitting space kind.
        frame_name:
            Optional related frame name.
        payload:
            Optional event payload mapping.
        metadata:
            Optional event metadata mapping.
        event_id:
            Optional explicit event id.
        emitted_at:
            Optional explicit emitted timestamp.

    Registration:
        MELDER KERNEL - guarded. Built by `RiftEventSystem` from room identity.

    Subsystem Context:
        The immutable event object of the room-local event system, paired with
        `RiftMemory` (the history record).

    System Context:
        Fixing identity and timestamp AT CREATION is what makes an event a
        factual account rather than a mutable notice. Subscribers may hold
        events indefinitely, and one that could change afterwards would let the
        record of what happened drift from what happened.
        Requiring no local queue or event thread follows from synchronous
        emission: the event is delivered before the emitting operation
        continues, so there is nothing to buffer. That keeps ordering trivially
        correct at the cost of letting a slow callback extend the operation -
        the honest trade for a room-local surface whose callbacks are registered
        by the room's own owner.
    """

    __ast_helper_access__: str = "public"
    __agent_purpose__: str = (
        "access: public. One immutable room event - type, ids, payload, and timestamp "
        "fixed at creation - delivered to the RiftSpace callbacks you register; you receive "
        "and read it, you do not construct it."
    )
    __slots__ = [
        "_id",
        "_event_type",
        "_emitted_at",
        "_rift_id",
        "_space_id",
        "_space_kind",
        "_frame_name",
        "_payload",
        "_metadata",
    ]

    def __init__(
            self,
            *,
            event_type: str,
            rift_id: str,
            space_id: str,
            space_kind: str,
            frame_name: Optional[str] = None,
            payload: Optional[Dict[str, object]] = None,
            metadata: Optional[Dict[str, object]] = None,
            event_id: Optional[str] = None,
            emitted_at: Optional[str] = None,
    ) -> None:
        """
        Initialize one immutable Rift-space event object.

        Returns:
            None.

        Raises:
            ValueError: If a required top-level field is empty.
        """
        if not event_type:
            raise ValueError("event_type cannot be empty.")
        if not rift_id:
            raise ValueError("rift_id cannot be empty.")
        if not space_id:
            raise ValueError("space_id cannot be empty.")
        if not space_kind:
            raise ValueError("space_kind cannot be empty.")
        self._id: str = event_id or IDBuilder.create_id()
        self._event_type: str = event_type
        self._emitted_at: str = emitted_at or datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        self._rift_id: str = rift_id
        self._space_id: str = space_id
        self._space_kind: str = space_kind
        self._frame_name: Optional[str] = frame_name
        self._payload: Dict[str, object] = dict(payload) if payload else {}
        self._metadata: Dict[str, object] = dict(metadata) if metadata else {}

    @property
    def event_id(self) -> str:
        """Return the stable event id."""
        return self._id

    @property
    def event_type(self) -> str:
        """Return the stable event type."""
        return self._event_type

    @property
    def emitted_at(self) -> str:
        """Return the UTC emitted timestamp."""
        return self._emitted_at

    @property
    def rift_id(self) -> str:
        """Return the owning Rift id."""
        return self._rift_id

    @property
    def space_id(self) -> str:
        """Return the emitting space id."""
        return self._space_id

    @property
    def space_kind(self) -> str:
        """Return the emitting space kind."""
        return self._space_kind

    @property
    def frame_name(self) -> Optional[str]:
        """Return the optional related frame name."""
        return self._frame_name

    @property
    def payload(self) -> Dict[str, object]:
        """Return a detached copy of the event payload."""
        return dict(self._payload)

    @property
    def metadata(self) -> Dict[str, object]:
        """Return a detached copy of the event metadata."""
        return dict(self._metadata)
