from typing import Dict, List, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.rift.frame_link.frame_link import FrameLink
from melder.aether.nexus.rift.frame_viewer.profiles.general.view_frame import (
    GeneralViewFrame,
)
from melder.utilities.general_base.cleanable import Cleanable


class GeneralViewSpell(Cleanable):
    """
    Purpose:
        Hold spell-scoped viewer helper methods for the `general` profile.

    Contract:
        - Operates on one bound frame through the shared frame helper surface.
        - Returns ACL-filtered spell links and spell descriptions only.

    Lifecycle:
        Cleanup is idempotent and clears the helper reference.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_frame_view",
    ]

    def __init__(self, *, frame_view: Optional[GeneralViewFrame]) -> None:
        """
        Initialize one spell-scoped helper surface.

        Args:
            frame_view:
                Shared frame helper used to source ACL-filtered links.

        Returns:
            None.
        """
        super().__init__()
        self._frame_view: Optional[GeneralViewFrame] = frame_view

    def cleanup(self) -> None:
        """
        Idempotently clear the helper surface.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._frame_view = None

    def list_spells(self) -> List[FrameLink]:
        self.check_cleaned()
        return self._get_required_frame_view().list_targets(source_kind="spell")

    def describe_spells(self) -> List[Dict[str, object]]:
        self.check_cleaned()
        return self._get_required_frame_view().describe_targets(source_kind="spell")

    def get_required_spell(self, spell_source_id: str) -> FrameLink:
        self.check_cleaned()
        if not spell_source_id:
            raise ValueError("spell_source_id cannot be empty.")
        return self._get_required_frame_view().get_required_target_by_source(
            source_kind="spell",
            source_id=spell_source_id,
        )

    def _get_required_frame_view(self) -> GeneralViewFrame:
        if self._frame_view is None:
            raise ValueError("GeneralViewSpell is not bound to a frame view.")
        return self._frame_view
