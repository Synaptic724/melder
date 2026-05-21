import threading
from typing import Dict, List, Optional, Protocol, TypeVar
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.nexus.acl.configurations.profiles.codegen.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.nexus.acl.configurations.profiles.codegen.frame_acl_codegen_profile_builder import (
    FrameACLCodegenProfileBuilder,
)
from melder.nexus.acl.configurations.profiles.command.frame_acl_command_profile import (
    FrameACLCommandProfile,
)
from melder.nexus.acl.configurations.profiles.command.frame_acl_command_profile_builder import (
    FrameACLCommandProfileBuilder,
)
from melder.nexus.acl.configurations.profiles.frame_acl_profile import (
    FrameACLProfile,
)
from melder.nexus.acl.configurations.profiles.view.frame_acl_view_profile_builder import (
    FrameACLViewProfileBuilder,
)
from melder.nexus.acl.configurations.profiles.view.frame_acl_view_profile import (
    FrameACLViewProfile,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class _NamedCleanableProfile(Protocol):
    """Minimal profile surface needed by the generic registry helpers."""

    @property
    def name(self) -> str:
        """Return the stable registry name for this reusable profile."""
        ...

    def cleanup(self) -> None:
        """Release any resources owned by this reusable profile."""
        ...


_ProfileT = TypeVar("_ProfileT", bound=_NamedCleanableProfile)


class FrameACLProfileBuilder(Cleanable):
    """
    Registry and composition root for reusable frame ACL profiles.

    Purpose:
        Centralize the reusable view, command, and codegen profile catalogs for
        the Nexus ACL subsystem and compose those reusable family profiles into
        detached `FrameACLProfile` bundles on demand.

    Contract:
        - Owns the base profile registries for the view, command, and codegen
          ACL families.
        - Owns the precision-profile registries for those same families.
        - Seeds the standard safe/hybrid/permissive/precision reusable
          profiles during initialization through the family builders it owns.
        - Returns detached `FrameACLProfile` bundles from `create_profile(...)`
          without auto-registering those composed bundles back into the builder.
        - Cleans registered reusable profiles during builder teardown, but
          does not reach out into caller-owned composed bundles created earlier.
        - Uses an instance `RLock` because registry mutation, replacement, and
          cleanup are grouped state transitions in a nogil runtime.

    Threading:
        Registry reads and writes are serialized under the builder-owned lock.

    Lifecycle:
        After `cleanup()`, all registries and family builders are gone and the
        builder must be treated as unusable.
    """

    __melder_internal__ = _mrg.sentinel
    _DEFAULT_PROFILE_NAME = "safe"
    _DEFAULT_PRECISION_PROFILE_NAME = "precision"
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_version",
        "_view_profile_builder",
        "_command_profile_builder",
        "_codegen_profile_builder",
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

        Purpose:
            Construct the reusable ACL profile catalogs and seed them with the
            standard family presets used throughout the Nexus ACL runtime.

        Returns:
            None.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._version: str = "0.0.1"
        self._view_profile_builder: FrameACLViewProfileBuilder = (
            FrameACLViewProfileBuilder()
        )
        self._command_profile_builder: FrameACLCommandProfileBuilder = (
            FrameACLCommandProfileBuilder()
        )
        self._codegen_profile_builder: FrameACLCodegenProfileBuilder = (
            FrameACLCodegenProfileBuilder()
        )
        self._view_profiles_by_name: Dict[str, FrameACLViewProfile] = {}
        self._command_profiles_by_name: Dict[str, FrameACLCommandProfile] = {}
        self._codegen_profiles_by_name: Dict[str, FrameACLCodegenProfile] = {}
        self._view_precision_profiles_by_name: Dict[str, FrameACLViewProfile] = {}
        self._command_precision_profiles_by_name: Dict[str, FrameACLCommandProfile] = {}
        self._codegen_precision_profiles_by_name: Dict[str, FrameACLCodegenProfile] = {}
        self.register_view_profile(self._view_profile_builder.build_profile("safe"))
        self.register_view_profile(self._view_profile_builder.build_profile("hybrid"))
        self.register_view_profile(self._view_profile_builder.build_profile("permissive"))
        self.register_command_profile(self._command_profile_builder.build_profile("safe"))
        self.register_command_profile(self._command_profile_builder.build_profile("hybrid"))
        self.register_command_profile(self._command_profile_builder.build_profile("permissive"))
        self.register_codegen_profile(self._codegen_profile_builder.build_profile("safe"))
        self.register_codegen_profile(self._codegen_profile_builder.build_profile("hybrid"))
        self.register_codegen_profile(self._codegen_profile_builder.build_profile("permissive"))
        self.register_codegen_profile(self._codegen_profile_builder.build_profile("full_access"))
        self.register_view_precision_profile(
            self._view_profile_builder.build_profile("precision")
        )
        self.register_command_precision_profile(
            self._command_profile_builder.build_profile("precision")
        )
        self.register_codegen_precision_profile(
            self._codegen_profile_builder.build_profile("precision")
        )

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

            self._view_profile_builder.cleanup()
            self._command_profile_builder.cleanup()
            self._codegen_profile_builder.cleanup()

            del self._view_profiles_by_name
            del self._command_profiles_by_name
            del self._codegen_profiles_by_name
            del self._view_precision_profiles_by_name
            del self._command_precision_profiles_by_name
            del self._codegen_precision_profiles_by_name
            del self._view_profile_builder
            del self._command_profile_builder
            del self._codegen_profile_builder
            del self._version
            del self._id
        del self._lock

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
    def view_profile_builder(self) -> FrameACLViewProfileBuilder:
        """
        Return the family builder that owns view profile strategies.
        """
        self.check_cleaned()
        return self._view_profile_builder

    @property
    def command_profile_builder(self) -> FrameACLCommandProfileBuilder:
        """
        Return the family builder that owns command profile strategies.
        """
        self.check_cleaned()
        return self._command_profile_builder

    @property
    def codegen_profile_builder(self) -> FrameACLCodegenProfileBuilder:
        """
        Return the family builder that owns codegen profile strategies.
        """
        self.check_cleaned()
        return self._codegen_profile_builder

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
        """
        Register or replace one reusable view-family profile.

        Args:
            view_profile:
                Concrete view ACL profile to store by name.

        Returns:
            None.
        """
        if not isinstance(view_profile, FrameACLViewProfile):
            raise TypeError("view_profile must be a FrameACLViewProfile.")
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
        """
        Register or replace one reusable command-family profile.

        Args:
            command_profile:
                Concrete command ACL profile to store by name.

        Returns:
            None.
        """
        if not isinstance(command_profile, FrameACLCommandProfile):
            raise TypeError("command_profile must be a FrameACLCommandProfile.")
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
        """
        Register or replace one reusable codegen-family profile.

        Args:
            codegen_profile:
                Concrete codegen ACL profile to store by name.

        Returns:
            None.
        """
        if not isinstance(codegen_profile, FrameACLCodegenProfile):
            raise TypeError("codegen_profile must be a FrameACLCodegenProfile.")
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
        """
        Register or replace one reusable view precision profile.

        Args:
            precision_profile:
                Concrete view precision profile to store by name.

        Returns:
            None.
        """
        if not isinstance(precision_profile, FrameACLViewProfile):
            raise TypeError("precision_profile must be a FrameACLViewProfile.")
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
        """
        Register or replace one reusable command precision profile.

        Args:
            precision_profile:
                Concrete command precision profile to store by name.

        Returns:
            None.
        """
        if not isinstance(precision_profile, FrameACLCommandProfile):
            raise TypeError("precision_profile must be a FrameACLCommandProfile.")
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
        """
        Register or replace one reusable codegen precision profile.

        Args:
            precision_profile:
                Concrete codegen precision profile to store by name.

        Returns:
            None.
        """
        if not isinstance(precision_profile, FrameACLCodegenProfile):
            raise TypeError("precision_profile must be a FrameACLCodegenProfile.")
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
        """
        Return one registered reusable view profile by name.

        Args:
            profile_name:
                Name of the reusable view profile.

        Returns:
            FrameACLViewProfile: Registered view profile.
        """
        return self._get_required_profile(
            self._view_profiles_by_name,
            profile_name,
        )

    def get_required_command_profile(
            self,
            profile_name: str,
    ) -> FrameACLCommandProfile:
        """
        Return one registered reusable command profile by name.

        Args:
            profile_name:
                Name of the reusable command profile.

        Returns:
            FrameACLCommandProfile: Registered command profile.
        """
        return self._get_required_profile(
            self._command_profiles_by_name,
            profile_name,
        )

    def get_required_codegen_profile(
            self,
            profile_name: str,
    ) -> FrameACLCodegenProfile:
        """
        Return one registered reusable codegen profile by name.

        Args:
            profile_name:
                Name of the reusable codegen profile.

        Returns:
            FrameACLCodegenProfile: Registered codegen profile.
        """
        return self._get_required_profile(
            self._codegen_profiles_by_name,
            profile_name,
        )

    def get_required_view_precision_profile(
            self,
            profile_name: str,
    ) -> FrameACLViewProfile:
        """
        Return one registered reusable view precision profile by name.

        Args:
            profile_name:
                Name of the reusable view precision profile.

        Returns:
            FrameACLViewProfile: Registered view precision profile.
        """
        return self._get_required_profile(
            self._view_precision_profiles_by_name,
            profile_name,
        )

    def get_required_command_precision_profile(
            self,
            profile_name: str,
    ) -> FrameACLCommandProfile:
        """
        Return one registered reusable command precision profile by name.

        Args:
            profile_name:
                Name of the reusable command precision profile.

        Returns:
            FrameACLCommandProfile: Registered command precision profile.
        """
        return self._get_required_profile(
            self._command_precision_profiles_by_name,
            profile_name,
        )

    def get_required_codegen_precision_profile(
            self,
            profile_name: str,
    ) -> FrameACLCodegenProfile:
        """
        Return one registered reusable codegen precision profile by name.

        Args:
            profile_name:
                Name of the reusable codegen precision profile.

        Returns:
            FrameACLCodegenProfile: Registered codegen precision profile.
        """
        return self._get_required_profile(
            self._codegen_precision_profiles_by_name,
            profile_name,
        )

    def list_view_profile_names(self) -> List[str]:
        """Return registered reusable view-profile names in insertion order."""
        return self._list_profile_names(self._view_profiles_by_name)

    def list_command_profile_names(self) -> List[str]:
        """Return registered reusable command-profile names in insertion order."""
        return self._list_profile_names(self._command_profiles_by_name)

    def list_codegen_profile_names(self) -> List[str]:
        """Return registered reusable codegen-profile names in insertion order."""
        return self._list_profile_names(self._codegen_profiles_by_name)

    def list_view_precision_profile_names(self) -> List[str]:
        """Return registered reusable view precision-profile names in insertion order."""
        return self._list_profile_names(self._view_precision_profiles_by_name)

    def list_command_precision_profile_names(self) -> List[str]:
        """Return registered reusable command precision-profile names in insertion order."""
        return self._list_profile_names(
            self._command_precision_profiles_by_name
        )

    def list_codegen_precision_profile_names(self) -> List[str]:
        """Return registered reusable codegen precision-profile names in insertion order."""
        return self._list_profile_names(
            self._codegen_precision_profiles_by_name
        )

    def remove_view_profile(self, profile_name: str) -> bool:
        """Remove one non-default reusable view profile by name."""
        return self._remove_profile(
            self._view_profiles_by_name,
            profile_name,
            default_name=self._DEFAULT_PROFILE_NAME,
            label="view",
        )

    def remove_command_profile(self, profile_name: str) -> bool:
        """Remove one non-default reusable command profile by name."""
        return self._remove_profile(
            self._command_profiles_by_name,
            profile_name,
            default_name=self._DEFAULT_PROFILE_NAME,
            label="command",
        )

    def remove_codegen_profile(self, profile_name: str) -> bool:
        """Remove one non-default reusable codegen profile by name."""
        return self._remove_profile(
            self._codegen_profiles_by_name,
            profile_name,
            default_name=self._DEFAULT_PROFILE_NAME,
            label="codegen",
        )

    def remove_view_precision_profile(self, profile_name: str) -> bool:
        """Remove one non-default reusable view precision profile by name."""
        return self._remove_profile(
            self._view_precision_profiles_by_name,
            profile_name,
            default_name=self._DEFAULT_PRECISION_PROFILE_NAME,
            label="view precision",
        )

    def remove_command_precision_profile(self, profile_name: str) -> bool:
        """Remove one non-default reusable command precision profile by name."""
        return self._remove_profile(
            self._command_precision_profiles_by_name,
            profile_name,
            default_name=self._DEFAULT_PRECISION_PROFILE_NAME,
            label="command precision",
        )

    def remove_codegen_precision_profile(self, profile_name: str) -> bool:
        """Remove one non-default reusable codegen precision profile by name."""
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

        Args:
            name:
                Name for the composed frame ACL profile bundle.
            view_profile_name:
                Registered reusable view profile name to compose.
            command_profile_name:
                Registered reusable command profile name to compose.
            codegen_profile_name:
                Registered reusable codegen profile name to compose.
            view_override_ruleset:
                Optional detached view override ruleset for the composed bundle.
            command_override_ruleset:
                Optional detached command override ruleset for the composed bundle.
            codegen_override_ruleset:
                Optional detached codegen override ruleset for the composed bundle.

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
            registry: Dict[str, _ProfileT],
            profile: _ProfileT,
            expected_type: type[_ProfileT],
            label: str,
    ) -> None:
        """
        Register or replace one reusable family profile inside one registry.

        Args:
            registry:
                Concrete reusable profile registry keyed by profile name.
            profile:
                Concrete family profile instance to register.
            expected_type:
                Concrete profile type required for this registry.
            label:
                User-facing label for validation errors.

        Returns:
            None.
        """
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
            registry: Dict[str, _ProfileT],
            profile_name: str,
    ) -> _ProfileT:
        """Return one registered concrete family profile or raise KeyError."""
        self.check_cleaned()
        with self._lock:
            try:
                return registry[profile_name]
            except KeyError as exc:
                raise KeyError(profile_name) from exc

    def _list_profile_names(
            self,
            registry: Dict[str, _ProfileT],
    ) -> List[str]:
        """Return the registered names for one concrete family registry."""
        self.check_cleaned()
        with self._lock:
            return list(registry.keys())

    def _remove_profile(
            self,
            registry: Dict[str, _ProfileT],
            profile_name: str,
            *,
            default_name: str,
            label: str,
    ) -> bool:
        """
        Remove one concrete reusable family profile unless it is the default.

        Args:
            registry:
                Concrete reusable profile registry keyed by name.
            profile_name:
                Name of the profile to remove.
            default_name:
                Registry-specific default profile that may not be removed.
            label:
                User-facing family label for error messages.

        Returns:
            bool: True when a profile was removed, otherwise False.
        """
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
