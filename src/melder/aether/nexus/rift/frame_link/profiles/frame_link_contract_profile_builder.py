import threading
from typing import Dict, List

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.rift.frame_link.profiles.frame_link_contract_profile import (
    FrameLinkContractProfile,
)
from melder.aether.nexus.rift.frame_link.profiles.hybrid_profile import (
    create_hybrid_frame_link_contract_profile,
)
from melder.aether.nexus.rift.frame_link.profiles.permissive_profile import (
    create_permissive_frame_link_contract_profile,
)
from melder.aether.nexus.rift.frame_link.profiles.safe_profile import (
    create_safe_frame_link_contract_profile,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class FrameLinkContractProfileBuilder(Cleanable):
    """
    Purpose:
        Own the reusable downstream frame-link contract profile registry.

    Contract:
        - Seeds the named downstream profile ladder:
          - `safe`
          - `hybrid`
          - `permissive`
        - Uses an instance lock because registry mutation and cleanup are
          grouped state transitions in a nogil runtime.

    Lifecycle:
        Cleanup is idempotent and cascades into all owned profiles.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_version",
        "_profiles_by_name",
    ]

    def __init__(self) -> None:
        """
        Initialize one downstream contract profile builder.

        Returns:
            None.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._version: str = "0.0.1"
        self._profiles_by_name: Dict[str, FrameLinkContractProfile] = {}
        self.register_profile(create_safe_frame_link_contract_profile())
        self.register_profile(create_hybrid_frame_link_contract_profile())
        self.register_profile(create_permissive_frame_link_contract_profile())

    def cleanup(self) -> None:
        """
        Idempotently clear the profile builder and owned profiles.

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
            self._version = None
            self._id = None
        self._lock = None

    @property
    def version(self) -> str:
        """Return the builder version string."""
        self.check_cleaned()
        return self._version

    def register_profile(self, profile: FrameLinkContractProfile) -> None:
        """
        Register or replace one downstream contract profile.

        Args:
            profile:
                Downstream contract profile to store by name.

        Returns:
            None.
        """
        self.check_cleaned()
        if not isinstance(profile, FrameLinkContractProfile):
            raise TypeError("profile must be a FrameLinkContractProfile.")
        with self._lock:
            existing = self._profiles_by_name.get(profile.name)
            if existing is not None and existing is not profile:
                existing.cleanup()
            self._profiles_by_name[profile.name] = profile

    def get_required_profile(self, profile_name: str) -> FrameLinkContractProfile:
        """
        Return one existing downstream contract profile or raise.

        Args:
            profile_name:
                Profile name to resolve.

        Returns:
            FrameLinkContractProfile: Existing downstream contract profile.
        """
        self.check_cleaned()
        with self._lock:
            try:
                return self._profiles_by_name[profile_name]
            except KeyError as exc:
                raise KeyError(profile_name) from exc

    def list_profile_names(self) -> List[str]:
        """
        Return the current downstream contract profile names.

        Returns:
            List[str]: Current profile names.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._profiles_by_name.keys())

