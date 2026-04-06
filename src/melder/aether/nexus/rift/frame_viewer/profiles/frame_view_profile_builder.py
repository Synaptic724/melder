import threading
from typing import Dict, List

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.rift.frame_viewer.profiles.frame_view_profile import (
    FrameViewProfile,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class FrameViewProfileBuilder(Cleanable):
    """
    Purpose:
        Own the reusable `FrameViewProfile` registry.

    Contract:
        - Seeds one `general` profile by default.
        - Returns profiles by name for Nexus projection use.

    Lifecycle:
        Cleanup is idempotent and cascades into owned profiles.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_builder_id",
        "_lock",
        "_profiles_by_name",
    ]

    def __init__(self) -> None:
        """
        Initialize the frame-view profile builder.

        Returns:
            None.
        """
        super().__init__()
        self._builder_id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._profiles_by_name: Dict[str, FrameViewProfile] = {}
        self.register_profile(FrameViewProfile.create_general())

    def register_profile(self, profile: FrameViewProfile) -> None:
        """
        Register or replace one frame-view profile.

        Args:
            profile:
                Profile to store by name.

        Returns:
            None.
        """
        self.check_cleaned()
        if not isinstance(profile, FrameViewProfile):
            raise TypeError("profile must be a FrameViewProfile.")
        with self._lock:
            existing = self._profiles_by_name.get(profile.name)
            if existing is not None and existing is not profile:
                existing.cleanup()
            self._profiles_by_name[profile.name] = profile

    def get_required_profile(self, profile_name: str) -> FrameViewProfile:
        """
        Return one registered frame-view profile or raise.

        Args:
            profile_name:
                Profile name to resolve.

        Returns:
            FrameViewProfile: Existing frame-view profile.
        """
        self.check_cleaned()
        with self._lock:
            try:
                return self._profiles_by_name[profile_name]
            except KeyError as exc:
                raise KeyError(profile_name) from exc

    def list_profile_names(self) -> List[str]:
        """
        Return current frame-view profile names.

        Returns:
            List[str]: Current profile names.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._profiles_by_name.keys())

    def cleanup(self) -> None:
        """
        Idempotently clear the builder and its profiles.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            for profile in self._profiles_by_name.values():
                profile.cleanup()
            self._profiles_by_name.clear()
            self._profiles_by_name = None
            self._builder_id = None
        self._lock = None
