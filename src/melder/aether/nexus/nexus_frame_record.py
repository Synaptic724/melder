import threading
from typing import Optional, Set

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.configuration.nexus_frame_mode import NexusFrameMode
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.interfaces.interfaces import IAethericFrame


class NexusFrameRecord(Cleanable):
    """
    Internal

    Track one Nexus-managed internal frame and its attachment lifecycle.

    Purpose:
        Replace the older integer ref-count model with an explicit metadata
        object that records who created a Nexus-owned frame, who currently owns
        it, whether it is immutable, and which live Rifts are attached to it.

    Contract:
        - Holds a strong reference to the realized `AethericFrame`.
        - Tracks attached Rift ids as the source of truth for live usage.
        - Supports ownership transfer when the current owner detaches but other
          Rifts remain attached.
        - Does not cleanup the underlying frame object itself; `Aether` remains
          the real frame owner and disposal executor.

    Lifecycle:
        Owned by `Nexus`. Cleanup clears only record metadata and attachment
        state. The underlying frame is disposed separately through `Aether`.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_frame_name",
        "_frame",
        "_nexus_frame_mode",
        "_creator_rift_id",
        "_owner_rift_id",
        "_immutable",
        "_attached_rift_ids",
    ]

    def __init__(
            self,
            *,
            frame_name: str,
            frame: IAethericFrame,
            nexus_frame_mode: NexusFrameMode,
            creator_rift_id: str,
            owner_rift_id: Optional[str],
            immutable: bool = False,
    ) -> None:
        """
        Internal

        Initialize one Nexus-frame record.

        Args:
            frame_name:
                Stable Aether frame name tracked by this record.
            frame:
                Realized `AethericFrame` object held strongly while the record
                is live.
            nexus_frame_mode:
                Nexus topology mode that produced this frame assignment.
            creator_rift_id:
                Canonical Rift id that first realized the frame.
            owner_rift_id:
                Current owning Rift id. This may later transfer when the
                current owner detaches but other attachments remain.
            immutable:
                True when the frame should survive attachment count dropping to
                zero and instead only be removed by explicit external or Nexus
                cleanup.

        Returns:
            None.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._frame_name: str = frame_name
        self._frame: IAethericFrame = frame
        self._nexus_frame_mode: NexusFrameMode = nexus_frame_mode
        self._creator_rift_id: str = creator_rift_id
        self._owner_rift_id: Optional[str] = owner_rift_id
        self._immutable: bool = immutable
        self._attached_rift_ids: Set[str] = set()

    @property
    def id(self) -> str:
        """
        Purpose:
            Return the stable record id.

        Returns:
            str: Stable record identifier.
        """
        self.check_cleaned()
        return self._id

    @property
    def frame_name(self) -> str:
        """
        Purpose:
            Return the tracked Aether frame name.

        Returns:
            str: Tracked frame name.
        """
        self.check_cleaned()
        return self._frame_name

    @property
    def frame(self) -> IAethericFrame:
        """
        Purpose:
            Return the realized frame object attached to this record.

        Returns:
            IAethericFrame: Strongly held frame object.
        """
        self.check_cleaned()
        return self._frame

    @property
    def nexus_frame_mode(self) -> NexusFrameMode:
        """
        Purpose:
            Return the topology mode that produced this record.

        Returns:
            NexusFrameMode: Owning topology mode.
        """
        self.check_cleaned()
        return self._nexus_frame_mode

    @property
    def creator_rift_id(self) -> str:
        """
        Purpose:
            Return the Rift id that first realized this frame.

        Returns:
            str: Creator Rift id.
        """
        self.check_cleaned()
        return self._creator_rift_id

    @property
    def owner_rift_id(self) -> Optional[str]:
        """
        Purpose:
            Return the current owning Rift id.

        Returns:
            Optional[str]: Current owner, if one exists.
        """
        self.check_cleaned()
        return self._owner_rift_id

    @property
    def immutable(self) -> bool:
        """
        Purpose:
            Return whether the frame survives attachment count dropping to zero.

        Returns:
            bool: True when the frame is immutable.
        """
        self.check_cleaned()
        return self._immutable

    @property
    def attached_rift_ids(self) -> Set[str]:
        """
        Purpose:
            Return a snapshot of attached Rift ids.

        Returns:
            Set[str]: Snapshot of current attachments.
        """
        self.check_cleaned()
        return set(self._attached_rift_ids)

    @property
    def attached_rift_count(self) -> int:
        """
        Purpose:
            Return the current attachment count.

        Returns:
            int: Number of attached Rifts.
        """
        self.check_cleaned()
        return len(self._attached_rift_ids)

    def attach_rift_id(self, rift_id: str) -> None:
        """
        Internal

        Attach one Rift id to this frame record.

        Args:
            rift_id:
                Canonical Rift id to attach.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._attached_rift_ids.add(rift_id)
            if self._owner_rift_id is None:
                self._owner_rift_id = rift_id

    def detach_rift_id(self, rift_id: str) -> None:
        """
        Internal

        Detach one Rift id from this frame record.

        Args:
            rift_id:
                Canonical Rift id to detach.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._attached_rift_ids.discard(rift_id)
            if self._owner_rift_id == rift_id:
                self._transfer_ownership_to_any_attached_rift()

    def has_attached_rifts(self) -> bool:
        """
        Purpose:
            Return whether any Rifts remain attached.

        Returns:
            bool: True when at least one attachment remains.
        """
        self.check_cleaned()
        return len(self._attached_rift_ids) > 0

    def cleanup(self) -> None:
        """
        Internal

        Idempotently cleanup the frame record metadata.

        Contract:
            - Clears attachment state and strong metadata references.
            - Does not cleanup the underlying `AethericFrame`.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._attached_rift_ids.clear()
            self._attached_rift_ids = None
            self._frame = None
            self._frame_name = None
            self._nexus_frame_mode = None
            self._creator_rift_id = None
            self._owner_rift_id = None
            self._immutable = None
            self._id = None
        self._lock = None

    def _transfer_ownership_to_any_attached_rift(self) -> None:
        """
        Internal

        Transfer ownership to one remaining attached Rift when possible.

        Returns:
            None.
        """
        if not self._attached_rift_ids:
            self._owner_rift_id = None
            return
        self._owner_rift_id = sorted(self._attached_rift_ids)[0]
