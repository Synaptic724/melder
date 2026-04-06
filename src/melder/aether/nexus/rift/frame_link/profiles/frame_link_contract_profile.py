from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.rift.frame_link.profiles.frame_link_view_profile import (
    FrameLinkViewProfile,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class FrameLinkContractProfile(Cleanable):
    """
    Purpose:
        Represent one composed downstream frame-link exposure profile.

    Contract:
        - Wraps one reusable view projection profile with stable identity.
        - Remains downstream and must not redefine ACL truth.

    Lifecycle:
        Cleanup is idempotent and clears the profile reference.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_name",
        "_version",
        "_view_profile",
    ]

    def __init__(
            self,
            name: str,
            *,
            view_profile: FrameLinkViewProfile,
            version: str = "0.0.1",
    ) -> None:
        """
        Initialize one composed downstream frame-link exposure profile.

        Args:
            name:
                Stable composed profile name.
            view_profile:
                Reusable downstream view projection profile.
            version:
                Profile version string.

        Returns:
            None.
        """
        super().__init__()
        if not name:
            raise ValueError("name cannot be empty.")
        if not isinstance(view_profile, FrameLinkViewProfile):
            raise TypeError("view_profile must be a FrameLinkViewProfile.")
        if not version:
            raise ValueError("version cannot be empty.")
        self._id: str = IDBuilder.create_id()
        self._name: str = name
        self._version: str = version
        self._view_profile = view_profile

    def cleanup(self) -> None:
        """
        Idempotently clear the contract profile.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._view_profile = None
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
        """Return the profile version string."""
        self.check_cleaned()
        return self._version

    @property
    def view_profile(self) -> FrameLinkViewProfile:
        """Return the reusable downstream view projection profile."""
        self.check_cleaned()
        return self._view_profile
