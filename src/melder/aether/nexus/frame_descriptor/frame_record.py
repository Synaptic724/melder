from typing import Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.interfaces.interfaces import IFrameDescriptorPayload


class FrameRecord(Cleanable):
    """
    Internal

    Canonical Nexus record for one AR-publishable frame.

    Purpose:
        Hold the frame-level posture Nexus needs to reason about one frame as a
        publishable AR/Rift source without depending on the richer shared
        Spellbook configuration object.

    Contract:
        - One record per frame name.
        - Carries only the current frame-level posture needed for the first
          passive-ingest slice.
        - Mutable through explicit Nexus upsert paths only.
        - Cleanup is idempotent and clears all owned references.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "frame_name",
        "frame_id",
        "config_origin_spellbook_id",
        "payload",
    ]

    def __init__(
            self,
            *,
            frame_name: str,
            frame_id: str,
            config_origin_spellbook_id: Optional[str],
            payload: IFrameDescriptorPayload,
    ) -> None:
        """
        Initialize one canonical frame record.

        Args:
            frame_name:
                Stable frame name.
            frame_id:
                Stable runtime frame id.
            config_origin_spellbook_id:
                Spellbook id that originally established the bound frame
                posture/config path when known.
            payload:
                Descriptor-safe frame payload for this record.
        """
        super().__init__()
        if payload is None:
            raise ValueError("payload cannot be None.")
        if not isinstance(payload, IFrameDescriptorPayload):
            raise TypeError("payload must satisfy IFrameDescriptorPayload.")
        self._id: str = IDBuilder.create_id()
        self.frame_name = frame_name
        self.frame_id = frame_id
        self.config_origin_spellbook_id = config_origin_spellbook_id
        self.payload = payload

    def cleanup(self) -> None:
        """
        Idempotently clear the record.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self.frame_name = None
        self.frame_id = None
        self.config_origin_spellbook_id = None
        if self.payload is not None:
            self.payload.cleanup()
        self.payload = None
