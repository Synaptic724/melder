from typing import Optional, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class FrameLinkCodegenProfile(Cleanable):
    """
    Purpose:
        Represent one reusable downstream codegen projection profile for
        frame-link contract shaping.

    Contract:
        - Carries the reusable profile identity and version.
        - Provides optional narrowing for allowed command names.
        - Remains downstream and must not redefine ACL truth.

    Lifecycle:
        Cleanup is idempotent and clears owned projection metadata.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_name",
        "_version",
        "_allowed_commands",
    ]

    def __init__(
            self,
            name: str,
            *,
            version: str = "0.0.1",
            allowed_commands: Optional[Tuple[str, ...]] = None,
    ) -> None:
        """
        Initialize one frame-link codegen profile.

        Args:
            name:
                Stable profile name.
            version:
                Profile version string.
            allowed_commands:
                Optional allowed command filter.

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
        self._allowed_commands: Tuple[str, ...] = tuple(
            allowed_commands or tuple()
        )

    def cleanup(self) -> None:
        """
        Idempotently clear the codegen profile.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._allowed_commands = None
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
    def allowed_commands(self) -> Tuple[str, ...]:
        """Return the allowed command filter."""
        self.check_cleaned()
        return self._allowed_commands
