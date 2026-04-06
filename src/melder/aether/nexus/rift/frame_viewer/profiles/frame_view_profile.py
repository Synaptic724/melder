from typing import Optional, Sequence, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class FrameViewProfile(Cleanable):
    """
    Purpose:
        Represent one reusable posture profile for projected `FrameView`
        objects.

    Contract:
        - Modifies view defaults only; does not redefine permissions.
        - Carries stable profile identity and version.
        - Stores preferred kind ordering and default detail posture.

    Lifecycle:
        Cleanup is idempotent and clears owned metadata only.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_profile_id",
        "_name",
        "_version",
        "_default_detail_level",
        "_preferred_kind_order",
    ]

    def __init__(
            self,
            name: str,
            *,
            version: str = "0.0.1",
            default_detail_level: str = "summary",
            preferred_kind_order: Optional[Sequence[str]] = None,
    ) -> None:
        """
        Initialize one frame-view profile.

        Args:
            name:
                Stable profile name.
            version:
                Profile version string.
            default_detail_level:
                Default detail posture for projected views.
            preferred_kind_order:
                Preferred ordering of visible kinds.

        Returns:
            None.
        """
        super().__init__()
        if not name:
            raise ValueError("name cannot be empty.")
        if not version:
            raise ValueError("version cannot be empty.")
        if not default_detail_level:
            raise ValueError("default_detail_level cannot be empty.")
        self._profile_id: str = IDBuilder.create_id()
        self._name: str = name
        self._version: str = version
        self._default_detail_level: str = default_detail_level
        self._preferred_kind_order: Tuple[str, ...] = tuple(
            preferred_kind_order or ("frame", "conduit", "spell")
        )

    @classmethod
    def create_general(cls) -> "FrameViewProfile":
        """
        Create the seeded `general` frame-view profile.

        Returns:
            FrameViewProfile: Seeded `general` frame-view profile.
        """
        return cls(
            "general",
            default_detail_level="summary",
            preferred_kind_order=("frame", "conduit", "spell"),
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
    def default_detail_level(self) -> str:
        self.check_cleaned()
        return self._default_detail_level

    @property
    def preferred_kind_order(self) -> Tuple[str, ...]:
        self.check_cleaned()
        return self._preferred_kind_order

    def cleanup(self) -> None:
        """
        Idempotently clear the frame-view profile.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._preferred_kind_order = None
        self._default_detail_level = None
        self._version = None
        self._name = None
        self._profile_id = None
