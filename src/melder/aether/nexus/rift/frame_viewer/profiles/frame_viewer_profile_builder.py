import threading
from typing import Dict, List

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.rift.frame_viewer.profiles.frame_viewer_profile import (
    FrameViewerProfile,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class FrameViewerProfileBuilder(Cleanable):
    """
    Purpose:
        Own the reusable `FrameViewerProfile` registry.

    Contract:
        - Seeds one `general` profile by default.
        - Returns profiles by name for Nexus/viewer use.

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
        Initialize the frame-viewer profile builder.

        Returns:
            None.
        """
        super().__init__()
        self._builder_id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._profiles_by_name: Dict[str, FrameViewerProfile] = {}
        self.register_profile(FrameViewerProfile.create_general())
        self.register_profile(FrameViewerProfile.create_navigation())
        self.register_profile(FrameViewerProfile.create_inspection())

    def register_profile(self, profile: FrameViewerProfile) -> None:
        """
        Register or replace one frame-viewer profile.

        Args:
            profile:
                Profile to store by name.

        Returns:
            None.
        """
        self.check_cleaned()
        if not isinstance(profile, FrameViewerProfile):
            raise TypeError("profile must be a FrameViewerProfile.")
        with self._lock:
            existing = self._profiles_by_name.get(profile.name)
            if existing is not None and existing is not profile:
                existing.cleanup()
            self._profiles_by_name[profile.name] = profile

    def get_required_profile(self, profile_name: str) -> FrameViewerProfile:
        """
        Return one registered frame-viewer profile or raise.

        Args:
            profile_name:
                Profile name to resolve.

        Returns:
            FrameViewerProfile: Existing frame-viewer profile.
        """
        self.check_cleaned()
        with self._lock:
            try:
                return self._profiles_by_name[profile_name]
            except KeyError as exc:
                raise KeyError(profile_name) from exc

    def list_profile_names(self) -> List[str]:
        """
        Return current frame-viewer profile names.

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
