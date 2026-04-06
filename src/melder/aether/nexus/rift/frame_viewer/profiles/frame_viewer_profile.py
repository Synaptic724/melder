from typing import Optional, Sequence, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class FrameViewerProfile(Cleanable):
    """
    Purpose:
        Represent one reusable posture profile for `FrameViewer`.

    Contract:
        - Modifies viewer defaults and enabled helper ids only.
        - Does not redefine permissions.
        - Carries stable profile identity and version.

    Lifecycle:
        Cleanup is idempotent and clears owned metadata only.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_profile_id",
        "_name",
        "_version",
        "_enabled_helpers",
        "_default_grouping",
        "_default_detail_level",
    ]

    def __init__(
            self,
            name: str,
            *,
            version: str = "0.0.1",
            enabled_helpers: Optional[Sequence[str]] = None,
            default_grouping: str = "frame",
            default_detail_level: str = "summary",
    ) -> None:
        """
        Initialize one frame-viewer profile.

        Args:
            name:
                Stable profile name.
            version:
                Profile version string.
            enabled_helpers:
                Enabled helper ids for this viewer posture.
            default_grouping:
                Default grouping mode.
            default_detail_level:
                Default detail posture.

        Returns:
            None.
        """
        super().__init__()
        if not name:
            raise ValueError("name cannot be empty.")
        if not version:
            raise ValueError("version cannot be empty.")
        if not default_grouping:
            raise ValueError("default_grouping cannot be empty.")
        if not default_detail_level:
            raise ValueError("default_detail_level cannot be empty.")
        self._profile_id: str = IDBuilder.create_id()
        self._name: str = name
        self._version: str = version
        self._enabled_helpers: Tuple[str, ...] = tuple(
            enabled_helpers or (
                "list_frame_names",
                "list_links",
                "list_links_by_kind",
                "list_links_grouped_by_frame",
                "list_links_grouped_by_kind",
                "list_display_names",
                "count_links",
                "describe_frame",
                "describe_frames",
                "get_required_link_by_source",
            )
        )
        self._default_grouping: str = default_grouping
        self._default_detail_level: str = default_detail_level

    @classmethod
    def create_general(cls) -> "FrameViewerProfile":
        """
        Create the seeded `general` frame-viewer profile.

        Returns:
            FrameViewerProfile: Seeded `general` frame-viewer profile.
        """
        return cls(
            "general",
            default_grouping="frame",
            default_detail_level="summary",
        )

    @property
    def name(self) -> str:
        self.check_cleaned()
        return self._name

    @property
    def version(self) -> str:
        self.check_cleaned()
        return self._version

    @property
    def enabled_helpers(self) -> Tuple[str, ...]:
        self.check_cleaned()
        return self._enabled_helpers

    @property
    def default_grouping(self) -> str:
        self.check_cleaned()
        return self._default_grouping

    @property
    def default_detail_level(self) -> str:
        self.check_cleaned()
        return self._default_detail_level

    def cleanup(self) -> None:
        """
        Idempotently clear the frame-viewer profile.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._enabled_helpers = None
        self._default_grouping = None
        self._default_detail_level = None
        self._version = None
        self._name = None
        self._profile_id = None
