import threading
from typing import Dict, List, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.acl.configurations.profiles.codegen.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.aether.nexus.acl.configurations.profiles.codegen.hybrid_profile import (
    create_hybrid_codegen_profile,
)
from melder.aether.nexus.acl.configurations.profiles.codegen.permissive_profile import (
    create_permissive_codegen_profile,
)
from melder.aether.nexus.acl.configurations.profiles.codegen.full_access_profile import (
    create_full_access_codegen_profile,
)
from melder.aether.nexus.acl.configurations.profiles.codegen.precision import (
    create_precision_codegen_profile,
)
from melder.aether.nexus.acl.configurations.profiles.codegen.safe_profile import (
    create_safe_codegen_profile,
)
from melder.aether.nexus.acl.configurations.profiles.command.frame_acl_command_profile import (
    FrameACLCommandProfile,
)
from melder.aether.nexus.acl.configurations.profiles.command.hybrid_profile import (
    create_hybrid_command_profile,
)
from melder.aether.nexus.acl.configurations.profiles.command.permissive_profile import (
    create_permissive_command_profile,
)
from melder.aether.nexus.acl.configurations.profiles.command.precision import (
    create_precision_command_profile,
)
from melder.aether.nexus.acl.configurations.profiles.command.safe_profile import (
    create_safe_command_profile,
)
from melder.aether.nexus.acl.configurations.profiles.frame_acl_profile import (
    FrameACLProfile,
)
from melder.aether.nexus.acl.configurations.profiles.rules.frame_acl_ruleset import (
    FrameACLRuleSet,
)
from melder.aether.nexus.acl.configurations.profiles.view.frame_acl_view_profile import (
    FrameACLViewProfile,
)
from melder.aether.nexus.acl.configurations.profiles.view.hybrid_profile import (
    create_hybrid_view_profile,
)
from melder.aether.nexus.acl.configurations.profiles.view.permissive_profile import (
    create_permissive_view_profile,
)
from melder.aether.nexus.acl.configurations.profiles.view.precision import (
    create_precision_view_profile,
)
from melder.aether.nexus.acl.configurations.profiles.view.safe_profile import (
    create_safe_view_profile,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class FrameACLProfileBuilder(Cleanable):
    """
    Purpose:
        Own the reusable ACL profile registries and compose family bundles from
        them.

    Contract:
        - Owns base profile registries for view, command, and codegen.
        - Owns precision profile registries for view, command, and codegen.
        - Composed `FrameACLProfile` objects returned from `create_profile(...)`
          do not become builder-owned registry entries automatically.
        - Uses an instance lock because registry mutation and cleanup are
          grouped state transitions in a nogil runtime.
    """

    __melder_internal__ = _mrg.sentinel
    _DEFAULT_PROFILE_NAME = "safe"
    _DEFAULT_PRECISION_PROFILE_NAME = "precision"
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_version",
        "_view_profiles_by_name",
        "_command_profiles_by_name",
        "_codegen_profiles_by_name",
        "_view_precision_profiles_by_name",
        "_command_precision_profiles_by_name",
        "_codegen_precision_profiles_by_name",
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
        self._command_profiles_by_name: Dict[str, FrameACLCommandProfile] = {}
        self._codegen_profiles_by_name: Dict[str, FrameACLCodegenProfile] = {}
        self._view_precision_profiles_by_name: Dict[str, FrameACLViewProfile] = {}
        self._command_precision_profiles_by_name: Dict[str, FrameACLCommandProfile] = {}
        self._codegen_precision_profiles_by_name: Dict[str, FrameACLCodegenProfile] = {}
        self.register_view_profile(create_safe_view_profile())
        self.register_view_profile(create_hybrid_view_profile())
        self.register_view_profile(create_permissive_view_profile())
        self.register_command_profile(create_safe_command_profile())
        self.register_command_profile(create_hybrid_command_profile())
        self.register_command_profile(create_permissive_command_profile())
        self.register_codegen_profile(create_safe_codegen_profile())
        self.register_codegen_profile(create_hybrid_codegen_profile())
        self.register_codegen_profile(create_permissive_codegen_profile())
        self.register_codegen_profile(create_full_access_codegen_profile())
        self.register_view_precision_profile(create_precision_view_profile())
        self.register_command_precision_profile(create_precision_command_profile())
        self.register_codegen_precision_profile(create_precision_codegen_profile())

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
            for registry in (
                    self._view_profiles_by_name,
                    self._command_profiles_by_name,
                    self._codegen_profiles_by_name,
                    self._view_precision_profiles_by_name,
                    self._command_precision_profiles_by_name,
                    self._codegen_precision_profiles_by_name,
            ):
                for profile in registry.values():
                    profile.cleanup()
                registry.clear()
            self._view_profiles_by_name = None
            self._command_profiles_by_name = None
            self._codegen_profiles_by_name = None
            self._view_precision_profiles_by_name = None
            self._command_precision_profiles_by_name = None
            self._codegen_precision_profiles_by_name = None
            self._version = None
            self._id = None

    @property
    def id(self) -> str:
        """Return the stable identifier for this ACL profile builder/library."""
        self.check_cleaned()
        return self._id

    @property
    def version(self) -> str:
        """Return the current version string for this ACL profile builder/library."""
        self.check_cleaned()
        return self._version

    @property
    def view_profiles_by_name(self) -> Dict[str, FrameACLViewProfile]:
        """Return a detached snapshot of the reusable view-profile registry."""
        self.check_cleaned()
        with self._lock:
            return dict(self._view_profiles_by_name)

    @property
    def command_profiles_by_name(self) -> Dict[str, FrameACLCommandProfile]:
        """Return a detached snapshot of the reusable command-profile registry."""
        self.check_cleaned()
        with self._lock:
            return dict(self._command_profiles_by_name)

    @property
    def codegen_profiles_by_name(self) -> Dict[str, FrameACLCodegenProfile]:
        """Return a detached snapshot of the reusable codegen-profile registry."""
        self.check_cleaned()
        with self._lock:
            return dict(self._codegen_profiles_by_name)

    @property
    def view_precision_profiles_by_name(self) -> Dict[str, FrameACLViewProfile]:
        """Return a detached snapshot of the reusable view precision profiles."""
        self.check_cleaned()
        with self._lock:
            return dict(self._view_precision_profiles_by_name)

    @property
    def command_precision_profiles_by_name(self) -> Dict[str, FrameACLCommandProfile]:
        """Return a detached snapshot of the reusable command precision profiles."""
        self.check_cleaned()
        with self._lock:
            return dict(self._command_precision_profiles_by_name)

    @property
    def codegen_precision_profiles_by_name(self) -> Dict[str, FrameACLCodegenProfile]:
        """Return a detached snapshot of the reusable codegen precision profiles."""
        self.check_cleaned()
        with self._lock:
            return dict(self._codegen_precision_profiles_by_name)

    def register_view_profile(self, view_profile: FrameACLViewProfile) -> None:
        self._register_profile(
            self._view_profiles_by_name,
            view_profile,
            FrameACLViewProfile,
            "view_profile",
        )

    def register_command_profile(
            self,
            command_profile: FrameACLCommandProfile,
    ) -> None:
        self._register_profile(
            self._command_profiles_by_name,
            command_profile,
            FrameACLCommandProfile,
            "command_profile",
        )

    def register_codegen_profile(
            self,
            codegen_profile: FrameACLCodegenProfile,
    ) -> None:
        self._register_profile(
            self._codegen_profiles_by_name,
            codegen_profile,
            FrameACLCodegenProfile,
            "codegen_profile",
        )

    def register_view_precision_profile(
            self,
            precision_profile: FrameACLViewProfile,
    ) -> None:
        self._register_profile(
            self._view_precision_profiles_by_name,
            precision_profile,
            FrameACLViewProfile,
            "precision_profile",
        )

    def register_command_precision_profile(
            self,
            precision_profile: FrameACLCommandProfile,
    ) -> None:
        self._register_profile(
            self._command_precision_profiles_by_name,
            precision_profile,
            FrameACLCommandProfile,
            "precision_profile",
        )

    def register_codegen_precision_profile(
            self,
            precision_profile: FrameACLCodegenProfile,
    ) -> None:
        self._register_profile(
            self._codegen_precision_profiles_by_name,
            precision_profile,
            FrameACLCodegenProfile,
            "precision_profile",
        )

    def get_required_view_profile(
            self,
            profile_name: str,
    ) -> FrameACLViewProfile:
        return self._get_required_profile(
            self._view_profiles_by_name,
            profile_name,
        )

    def get_required_command_profile(
            self,
            profile_name: str,
    ) -> FrameACLCommandProfile:
        return self._get_required_profile(
            self._command_profiles_by_name,
            profile_name,
        )

    def get_required_codegen_profile(
            self,
            profile_name: str,
    ) -> FrameACLCodegenProfile:
        return self._get_required_profile(
            self._codegen_profiles_by_name,
            profile_name,
        )

    def get_required_view_precision_profile(
            self,
            profile_name: str,
    ) -> FrameACLViewProfile:
        return self._get_required_profile(
            self._view_precision_profiles_by_name,
            profile_name,
        )

    def get_required_command_precision_profile(
            self,
            profile_name: str,
    ) -> FrameACLCommandProfile:
        return self._get_required_profile(
            self._command_precision_profiles_by_name,
            profile_name,
        )

    def get_required_codegen_precision_profile(
            self,
            profile_name: str,
    ) -> FrameACLCodegenProfile:
        return self._get_required_profile(
            self._codegen_precision_profiles_by_name,
            profile_name,
        )

    def list_view_profile_names(self) -> List[str]:
        return self._list_profile_names(self._view_profiles_by_name)

    def list_command_profile_names(self) -> List[str]:
        return self._list_profile_names(self._command_profiles_by_name)

    def list_codegen_profile_names(self) -> List[str]:
        return self._list_profile_names(self._codegen_profiles_by_name)

    def list_view_precision_profile_names(self) -> List[str]:
        return self._list_profile_names(self._view_precision_profiles_by_name)

    def list_command_precision_profile_names(self) -> List[str]:
        return self._list_profile_names(
            self._command_precision_profiles_by_name
        )

    def list_codegen_precision_profile_names(self) -> List[str]:
        return self._list_profile_names(
            self._codegen_precision_profiles_by_name
        )

    def remove_view_profile(self, profile_name: str) -> bool:
        return self._remove_profile(
            self._view_profiles_by_name,
            profile_name,
            default_name=self._DEFAULT_PROFILE_NAME,
            label="view",
        )

    def remove_command_profile(self, profile_name: str) -> bool:
        return self._remove_profile(
            self._command_profiles_by_name,
            profile_name,
            default_name=self._DEFAULT_PROFILE_NAME,
            label="command",
        )

    def remove_codegen_profile(self, profile_name: str) -> bool:
        return self._remove_profile(
            self._codegen_profiles_by_name,
            profile_name,
            default_name=self._DEFAULT_PROFILE_NAME,
            label="codegen",
        )

    def remove_view_precision_profile(self, profile_name: str) -> bool:
        return self._remove_profile(
            self._view_precision_profiles_by_name,
            profile_name,
            default_name=self._DEFAULT_PRECISION_PROFILE_NAME,
            label="view precision",
        )

    def remove_command_precision_profile(self, profile_name: str) -> bool:
        return self._remove_profile(
            self._command_precision_profiles_by_name,
            profile_name,
            default_name=self._DEFAULT_PRECISION_PROFILE_NAME,
            label="command precision",
        )

    def remove_codegen_precision_profile(self, profile_name: str) -> bool:
        return self._remove_profile(
            self._codegen_precision_profiles_by_name,
            profile_name,
            default_name=self._DEFAULT_PRECISION_PROFILE_NAME,
            label="codegen precision",
        )

    def create_profile(
            self,
            name: str,
            *,
            view_profile_name: str = _DEFAULT_PROFILE_NAME,
            command_profile_name: str = _DEFAULT_PROFILE_NAME,
            codegen_profile_name: str = _DEFAULT_PROFILE_NAME,
            view_override_ruleset: Optional[FrameACLRuleSet] = None,
            command_override_ruleset: Optional[FrameACLRuleSet] = None,
            codegen_override_ruleset: Optional[FrameACLRuleSet] = None,
    ) -> FrameACLProfile:
        """
        Compose one reusable view/command/codegen trio into a frame ACL profile.

        Returns:
            FrameACLProfile: Newly composed frame ACL profile.
        """
        self.check_cleaned()
        view_profile = self.get_required_view_profile(view_profile_name)
        command_profile = self.get_required_command_profile(command_profile_name)
        codegen_profile = self.get_required_codegen_profile(codegen_profile_name)
        return FrameACLProfile(
            name,
            view_profile=view_profile,
            command_profile=command_profile,
            codegen_profile=codegen_profile,
            view_override_ruleset=view_override_ruleset,
            command_override_ruleset=command_override_ruleset,
            codegen_override_ruleset=codegen_override_ruleset,
        )

    def _register_profile(
            self,
            registry: Dict[str, object],
            profile: object,
            expected_type: type,
            label: str,
    ) -> None:
        self.check_cleaned()
        if not isinstance(profile, expected_type):
            raise TypeError("{0} must be a {1}.".format(label, expected_type.__name__))
        with self._lock:
            existing = registry.get(profile.name)
            if existing is not None and existing is not profile:
                existing.cleanup()
            registry[profile.name] = profile

    def _get_required_profile(
            self,
            registry: Dict[str, object],
            profile_name: str,
    ) -> object:
        self.check_cleaned()
        with self._lock:
            try:
                return registry[profile_name]
            except KeyError as exc:
                raise KeyError(profile_name) from exc

    def _list_profile_names(
            self,
            registry: Dict[str, object],
    ) -> List[str]:
        self.check_cleaned()
        with self._lock:
            return list(registry.keys())

    def _remove_profile(
            self,
            registry: Dict[str, object],
            profile_name: str,
            *,
            default_name: str,
            label: str,
    ) -> bool:
        self.check_cleaned()
        if profile_name == default_name:
            raise RuntimeError(
                "Cannot remove the default {0} profile.".format(label)
            )
        with self._lock:
            profile = registry.pop(profile_name, None)
            if profile is None:
                return False
            profile.cleanup()
            return True
