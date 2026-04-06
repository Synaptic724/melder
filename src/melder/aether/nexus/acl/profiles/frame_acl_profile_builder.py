import threading
from typing import Dict, List, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.acl.profiles.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.aether.nexus.acl.profiles.frame_acl_profile import FrameACLProfile
from melder.aether.nexus.acl.profiles.frame_acl_ruleset import FrameACLRuleSet
from melder.aether.nexus.acl.profiles.frame_acl_view_profile import (
    FrameACLViewProfile,
)
from melder.aether.nexus.acl.profiles.codegen.hybrid_profile import (
    create_hybrid_codegen_profile,
)
from melder.aether.nexus.acl.profiles.codegen.permissive_profile import (
    create_permissive_codegen_profile,
)
from melder.aether.nexus.acl.profiles.codegen.safe_profile import (
    create_safe_codegen_profile,
)
from melder.aether.nexus.acl.profiles.view.hybrid_profile import (
    create_hybrid_view_profile,
)
from melder.aether.nexus.acl.profiles.view.permissive_profile import (
    create_permissive_view_profile,
)
from melder.aether.nexus.acl.profiles.view.safe_profile import (
    create_safe_view_profile,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class FrameACLProfileBuilder(Cleanable):
    """
    Purpose:
        Own the reusable ACL profile registries and compose `FrameACLProfile`
        objects from them.

    Contract:
        - Owns one view-profile registry and one codegen-profile registry.
        - Seeds the named profile ladder during construction.
        - Composed `FrameACLProfile` objects returned from `create_profile(...)`
          do not become builder-owned registry entries automatically.
        - Uses an instance lock because registry mutation and cleanup are
          grouped state transitions in a nogil runtime.

    Lifecycle:
        Cleanup is idempotent and cascades into all owned reusable profiles.
    """

    __melder_internal__ = _mrg.sentinel
    _DEFAULT_PROFILE_NAME = "safe"
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_version",
        "_view_profiles_by_name",
        "_codegen_profiles_by_name",
    ]

    def __init__(self) -> None:
        """
        Initialize one ACL profile builder/library.

        Returns:
            None.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._version: str = "0.0.1"
        self._view_profiles_by_name: Dict[str, FrameACLViewProfile] = {}
        self._codegen_profiles_by_name: Dict[str, FrameACLCodegenProfile] = {}
        self.register_view_profile(create_safe_view_profile())
        self.register_view_profile(create_hybrid_view_profile())
        self.register_view_profile(create_permissive_view_profile())
        self.register_codegen_profile(create_safe_codegen_profile())
        self.register_codegen_profile(create_hybrid_codegen_profile())
        self.register_codegen_profile(create_permissive_codegen_profile())

    def cleanup(self) -> None:
        """
        Idempotently clear the builder/library and owned reusable profiles.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            for view_profile in self._view_profiles_by_name.values():
                view_profile.cleanup()
            for codegen_profile in self._codegen_profiles_by_name.values():
                codegen_profile.cleanup()
            self._view_profiles_by_name.clear()
            self._codegen_profiles_by_name.clear()
            self._view_profiles_by_name = None
            self._codegen_profiles_by_name = None
            self._version = None
            self._id = None
        self._lock = None

    @property
    def id(self) -> str:
        """Return the stable builder identifier."""
        self.check_cleaned()
        return self._id

    @property
    def version(self) -> str:
        """Return the current builder version string."""
        self.check_cleaned()
        return self._version

    @property
    def view_profiles_by_name(self) -> Dict[str, FrameACLViewProfile]:
        """Return a detached snapshot of the view-profile registry."""
        self.check_cleaned()
        with self._lock:
            return dict(self._view_profiles_by_name)

    @property
    def codegen_profiles_by_name(self) -> Dict[str, FrameACLCodegenProfile]:
        """Return a detached snapshot of the codegen-profile registry."""
        self.check_cleaned()
        with self._lock:
            return dict(self._codegen_profiles_by_name)

    def register_view_profile(self, view_profile: FrameACLViewProfile) -> None:
        """
        Register or replace one reusable view profile.

        Args:
            view_profile:
                Reusable view profile to store by name.

        Returns:
            None.
        """
        self.check_cleaned()
        if not isinstance(view_profile, FrameACLViewProfile):
            raise TypeError("view_profile must be a FrameACLViewProfile.")
        with self._lock:
            existing = self._view_profiles_by_name.get(view_profile.name)
            if existing is not None and existing is not view_profile:
                existing.cleanup()
            self._view_profiles_by_name[view_profile.name] = view_profile

    def register_codegen_profile(
            self,
            codegen_profile: FrameACLCodegenProfile,
    ) -> None:
        """
        Register or replace one reusable codegen profile.

        Args:
            codegen_profile:
                Reusable codegen profile to store by name.

        Returns:
            None.
        """
        self.check_cleaned()
        if not isinstance(codegen_profile, FrameACLCodegenProfile):
            raise TypeError(
                "codegen_profile must be a FrameACLCodegenProfile."
            )
        with self._lock:
            existing = self._codegen_profiles_by_name.get(codegen_profile.name)
            if existing is not None and existing is not codegen_profile:
                existing.cleanup()
            self._codegen_profiles_by_name[codegen_profile.name] = codegen_profile

    def get_required_view_profile(
            self,
            profile_name: str,
    ) -> FrameACLViewProfile:
        """Return one reusable view profile or raise."""
        self.check_cleaned()
        with self._lock:
            try:
                return self._view_profiles_by_name[profile_name]
            except KeyError as exc:
                raise KeyError(profile_name) from exc

    def get_required_codegen_profile(
            self,
            profile_name: str,
    ) -> FrameACLCodegenProfile:
        """Return one reusable codegen profile or raise."""
        self.check_cleaned()
        with self._lock:
            try:
                return self._codegen_profiles_by_name[profile_name]
            except KeyError as exc:
                raise KeyError(profile_name) from exc

    def list_view_profile_names(self) -> List[str]:
        """Return the current reusable view-profile names."""
        self.check_cleaned()
        with self._lock:
            return list(self._view_profiles_by_name.keys())

    def list_codegen_profile_names(self) -> List[str]:
        """Return the current reusable codegen-profile names."""
        self.check_cleaned()
        with self._lock:
            return list(self._codegen_profiles_by_name.keys())

    def remove_view_profile(self, profile_name: str) -> bool:
        """
        Remove one reusable view profile unless it is the default profile.

        Returns:
            bool: True when the profile existed and was removed.
        """
        self.check_cleaned()
        if profile_name == self._DEFAULT_PROFILE_NAME:
            raise RuntimeError("Cannot remove the default view profile.")
        with self._lock:
            view_profile = self._view_profiles_by_name.pop(profile_name, None)
            if view_profile is None:
                return False
            view_profile.cleanup()
            return True

    def remove_codegen_profile(self, profile_name: str) -> bool:
        """
        Remove one reusable codegen profile unless it is the default profile.

        Returns:
            bool: True when the profile existed and was removed.
        """
        self.check_cleaned()
        if profile_name == self._DEFAULT_PROFILE_NAME:
            raise RuntimeError("Cannot remove the default codegen profile.")
        with self._lock:
            codegen_profile = self._codegen_profiles_by_name.pop(
                profile_name,
                None,
            )
            if codegen_profile is None:
                return False
            codegen_profile.cleanup()
            return True

    def create_profile(
            self,
            name: str,
            *,
            view_profile_name: str = _DEFAULT_PROFILE_NAME,
            codegen_profile_name: str = _DEFAULT_PROFILE_NAME,
            view_override_ruleset: Optional[FrameACLRuleSet] = None,
            codegen_override_ruleset: Optional[FrameACLRuleSet] = None,
    ) -> FrameACLProfile:
        """
        Compose one reusable view/codegen pair into a frame ACL profile.

        Args:
            name:
                Stable composed profile name.
            view_profile_name:
                Reusable view-profile name to resolve.
            codegen_profile_name:
                Reusable codegen-profile name to resolve.
            view_override_ruleset:
                Optional local view override ruleset.
            codegen_override_ruleset:
                Optional local codegen override ruleset.

        Returns:
            FrameACLProfile: Newly composed frame ACL profile.
        """
        self.check_cleaned()
        view_profile = self.get_required_view_profile(view_profile_name)
        codegen_profile = self.get_required_codegen_profile(codegen_profile_name)
        return FrameACLProfile(
            name,
            view_profile=view_profile,
            codegen_profile=codegen_profile,
            view_override_ruleset=view_override_ruleset,
            codegen_override_ruleset=codegen_override_ruleset,
        )
