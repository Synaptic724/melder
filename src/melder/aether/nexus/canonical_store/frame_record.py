from typing import Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.spellbook.configuration.system_state import SystemState
from melder.utilities.general_base.cleanable import Cleanable


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
        "frame_name",
        "frame_id",
        "origin_spellbook_id",
        "system_state",
        "ai_native_enabled",
        "rift_enabled",
    ]

    def __init__(
            self,
            *,
            frame_name: str,
            frame_id: str,
            origin_spellbook_id: Optional[str],
            system_state: SystemState,
            ai_native_enabled: bool,
            rift_enabled: bool,
    ) -> None:
        """
        Initialize one canonical frame record.

        Args:
            frame_name:
                Stable frame name.
            frame_id:
                Stable runtime frame id.
            origin_spellbook_id:
                Spellbook id that caused this record to be published.
            system_state:
                Current frame system state.
            ai_native_enabled:
                Whether AI-native posture is enabled for the frame.
            rift_enabled:
                Whether the frame is eligible for passive Nexus publication and
                later Rift-facing interaction.
        """
        super().__init__()
        self.frame_name = frame_name
        self.frame_id = frame_id
        self.origin_spellbook_id = origin_spellbook_id
        self.system_state = system_state
        self.ai_native_enabled = ai_native_enabled
        self.rift_enabled = rift_enabled

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
        self.origin_spellbook_id = None
        self.system_state = None
        self.ai_native_enabled = None
        self.rift_enabled = None
