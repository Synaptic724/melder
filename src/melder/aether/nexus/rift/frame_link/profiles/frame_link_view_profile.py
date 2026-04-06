from typing import Optional, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class FrameLinkViewProfile(Cleanable):
    """
    Purpose:
        Represent one reusable downstream view projection profile for frame-link
        contract shaping.

    Contract:
        - Carries the reusable profile identity and version.
        - Provides optional narrowing for visible kinds and payload sections.
        - Remains downstream and must not redefine ACL truth; it only shapes the
          projection of compiled access output.

    Lifecycle:
        Cleanup is idempotent and clears owned projection metadata.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_name",
        "_version",
        "_allowed_kinds",
        "_frame_payload_fields",
        "_conduit_payload_sections",
        "_spell_payload_sections",
    ]

    def __init__(
            self,
            name: str,
            *,
            version: str = "0.0.1",
            allowed_kinds: Optional[Tuple[str, ...]] = None,
            frame_payload_fields: Optional[Tuple[str, ...]] = None,
            conduit_payload_sections: Optional[Tuple[str, ...]] = None,
            spell_payload_sections: Optional[Tuple[str, ...]] = None,
    ) -> None:
        """
        Initialize one frame-link view profile.

        Args:
            name:
                Stable profile name.
            version:
                Profile version string.
            allowed_kinds:
                Optional visible kind filter.
            frame_payload_fields:
                Optional visible frame payload fields.
            conduit_payload_sections:
                Optional visible conduit payload sections.
            spell_payload_sections:
                Optional visible spell payload sections.

        Returns:
            None.
        """
        super().__init__()
        if not name:
            raise ValueError("name cannot be empty.")
        if not version:
            raise ValueError("version cannot be empty.")
        self._id: str = IDBuilder.create_id()
        self._name: str = name
        self._version: str = version
        self._allowed_kinds: Tuple[str, ...] = tuple(allowed_kinds or tuple())
        self._frame_payload_fields: Tuple[str, ...] = tuple(
            frame_payload_fields or tuple()
        )
        self._conduit_payload_sections: Tuple[str, ...] = tuple(
            conduit_payload_sections or tuple()
        )
        self._spell_payload_sections: Tuple[str, ...] = tuple(
            spell_payload_sections or tuple()
        )

    def cleanup(self) -> None:
        """
        Idempotently clear the view profile.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._allowed_kinds = None
        self._frame_payload_fields = None
        self._conduit_payload_sections = None
        self._spell_payload_sections = None
        self._version = None
        self._name = None
        self._id = None

    @property
    def name(self) -> str:
        """Return the stable profile name."""
        self.check_cleaned()
        return self._name

    @property
    def version(self) -> str:
        """Return the reusable profile version string."""
        self.check_cleaned()
        return self._version

    @property
    def allowed_kinds(self) -> Tuple[str, ...]:
        """Return the allowed kind filter."""
        self.check_cleaned()
        return self._allowed_kinds

    @property
    def frame_payload_fields(self) -> Tuple[str, ...]:
        """Return the visible frame payload fields."""
        self.check_cleaned()
        return self._frame_payload_fields

    @property
    def conduit_payload_sections(self) -> Tuple[str, ...]:
        """Return the visible conduit payload sections."""
        self.check_cleaned()
        return self._conduit_payload_sections

    @property
    def spell_payload_sections(self) -> Tuple[str, ...]:
        """Return the visible spell payload sections."""
        self.check_cleaned()
        return self._spell_payload_sections
