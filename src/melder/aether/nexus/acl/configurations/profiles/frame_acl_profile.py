import threading
from typing import Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.acl.configurations.profiles.codegen.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.aether.nexus.acl.configurations.profiles.rules.frame_acl_ruleset import FrameACLRuleSet
from melder.aether.nexus.acl.configurations.profiles.view.frame_acl_view_profile import (
    FrameACLViewProfile,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class FrameACLProfile(Cleanable):
    """
    Purpose:
        Represent one composed ACL profile that pairs a reusable view profile
        with a reusable codegen profile plus local override rulesets.

    Contract:
        - View/codegen profile references are shared library objects and are
          not cleaned by this composed profile.
        - Local override rulesets are owned by this composed profile.
        - Uses an instance lock because cleanup and override ownership mutation
          are grouped state transitions in a nogil runtime.

    Lifecycle:
        Cleanup is idempotent and clears owned override rulesets plus shared
        profile references.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_version",
        "_name",
        "_view_profile",
        "_codegen_profile",
        "_view_override_ruleset",
        "_codegen_override_ruleset",
    ]

    def __init__(
            self,
            name: str,
            *,
            view_profile: FrameACLViewProfile,
            codegen_profile: FrameACLCodegenProfile,
            view_override_ruleset: Optional[FrameACLRuleSet] = None,
            codegen_override_ruleset: Optional[FrameACLRuleSet] = None,
            version: str = "0.0.1",
    ) -> None:
        """
        Initialize one composed ACL profile.

        Args:
            name:
                Stable composed profile name.
            view_profile:
                Shared reusable view profile.
            codegen_profile:
                Shared reusable codegen profile.
            view_override_ruleset:
                Optional local view override ruleset.
            codegen_override_ruleset:
                Optional local codegen override ruleset.
            version:
                Profile version string.

        Returns:
            None.
        """
        super().__init__()
        if not name:
            raise ValueError("name cannot be empty.")
        if not isinstance(view_profile, FrameACLViewProfile):
            raise TypeError("view_profile must be a FrameACLViewProfile.")
        if not isinstance(codegen_profile, FrameACLCodegenProfile):
            raise TypeError("codegen_profile must be a FrameACLCodegenProfile.")
        if not version:
            raise ValueError("version cannot be empty.")
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._version: str = version
        self._name: str = name
        self._view_profile = view_profile
        self._codegen_profile = codegen_profile
        self._view_override_ruleset = FrameACLViewProfile.coerce_ruleset(
            view_override_ruleset,
            "{0}_view_override".format(name),
        )
        self._codegen_override_ruleset = FrameACLViewProfile.coerce_ruleset(
            codegen_override_ruleset,
            "{0}_codegen_override".format(name),
        )

    def cleanup(self) -> None:
        """
        Idempotently clear the composed profile.

        Contract:
            - Cleans the owned override rulesets only.
            - Drops references to the shared reusable profiles without
              cleaning those shared library objects.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._view_override_ruleset.cleanup()
            self._codegen_override_ruleset.cleanup()
            self._view_override_ruleset = None
            self._codegen_override_ruleset = None
            self._view_profile = None
            self._codegen_profile = None
            self._version = None
            self._name = None
            self._id = None
        self._lock = None

    @property
    def id(self) -> str:
        """Return the stable identifier for this composed ACL profile."""
        self.check_cleaned()
        return self._id

    @property
    def version(self) -> str:
        """Return the version string carried by this composed ACL profile."""
        self.check_cleaned()
        return self._version

    @property
    def name(self) -> str:
        """Return the stable name of this composed ACL profile."""
        self.check_cleaned()
        return self._name

    @property
    def view_profile(self) -> FrameACLViewProfile:
        """Return the shared reusable view profile referenced by this composition."""
        self.check_cleaned()
        return self._view_profile

    @property
    def codegen_profile(self) -> FrameACLCodegenProfile:
        """Return the shared reusable codegen profile referenced by this composition."""
        self.check_cleaned()
        return self._codegen_profile

    @property
    def view_override_ruleset(self) -> FrameACLRuleSet:
        """Return the owned view override ruleset for this composed profile."""
        self.check_cleaned()
        return self._view_override_ruleset

    @property
    def codegen_override_ruleset(self) -> FrameACLRuleSet:
        """Return the owned codegen override ruleset for this composed profile."""
        self.check_cleaned()
        return self._codegen_override_ruleset
