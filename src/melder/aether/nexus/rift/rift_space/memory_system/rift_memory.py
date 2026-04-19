from datetime import datetime, timezone
from typing import Dict

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.helpers.id_builder import IDBuilder


class RiftMemory:
    """
    Internal

    Immutable executed-step record emitted from `RiftSpace`.

    Purpose:
        Capture one immutable memory record for a completed Rift-level action
        using the sequencing and shared metadata provided by `RiftMemorySystem`.

    Contract:
        - `frame_name` and `action_name` are required.
        - `step_counter` and `epoch_counter` are captured at creation time and
          never mutated afterward.
        - Metadata is copied on construction so later context updates do not
          retroactively change previously emitted memories.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = [
        "_id",
        "_created_at",
        "_frame_name",
        "_action_name",
        "_step_counter",
        "_epoch_counter",
        "_metadata",
    ]

    def __init__(
            self,
            *,
            frame_name: str,
            action_name: str,
            step_counter: int,
            epoch_counter: int,
            metadata: Dict[str, object],
    ) -> None:
        """
        Initialize one immutable Rift memory record.

        Args:
            frame_name:
                Required frame name for the executed action.
            action_name:
                Required action name for the executed action.
            step_counter:
                Step counter snapshot from the owning memory system.
            epoch_counter:
                Epoch counter snapshot from the owning memory system.
            metadata:
                Final metadata snapshot for this memory.

        Returns:
            None.
        """
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        if not action_name:
            raise ValueError("action_name cannot be empty.")
        self._id: str = IDBuilder.create_id()
        self._created_at: str = datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        self._frame_name: str = frame_name
        self._action_name: str = action_name
        self._step_counter: int = step_counter
        self._epoch_counter: int = epoch_counter
        self._metadata: Dict[str, object] = dict(metadata)

    @property
    def memory_id(self) -> str:
        """Return the stable memory id."""
        return self._id

    @property
    def created_at(self) -> str:
        """Return the UTC creation timestamp."""
        return self._created_at

    @property
    def frame_name(self) -> str:
        """Return the required frame name for this memory."""
        return self._frame_name

    @property
    def action_name(self) -> str:
        """Return the action name captured by this memory."""
        return self._action_name

    @property
    def step_counter(self) -> int:
        """Return the step counter snapshot for this memory."""
        return self._step_counter

    @property
    def epoch_counter(self) -> int:
        """Return the epoch counter snapshot for this memory."""
        return self._epoch_counter

    @property
    def metadata(self) -> Dict[str, object]:
        """Return a detached copy of the memory metadata."""
        return dict(self._metadata)
