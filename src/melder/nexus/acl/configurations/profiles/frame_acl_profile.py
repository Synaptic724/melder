import threading
from typing import Optional
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.nexus.acl.configurations.profiles.codegen.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.nexus.acl.configurations.profiles.command.frame_acl_command_profile import (
    FrameACLCommandProfile,
)
from melder.nexus.acl.configurations.profiles.rules.frame_acl_ruleset import (
    FrameACLRuleSet,
)
from melder.nexus.acl.configurations.profiles.view.frame_acl_view_profile import (
    FrameACLViewProfile,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class FrameACLProfile(Cleanable):
    """

    Purpose:
        Represent one composed ACL profile that pairs reusable view, command,
        and codegen base profiles with local override rulesets.

    Contract:
        - Family profile references are shared library objects and are not
          cleaned by this composed profile.
        - Local override rulesets are owned by this composed profile.
        - Uses an instance lock because cleanup and override ownership mutation
          are grouped state transitions in a nogil runtime.

    Lifecycle:
        Cleanup is idempotent and clears owned override rulesets plus shared
        profile references.

    Registration:
        MELDER KERNEL - guarded. Composed from library profiles plus local
        overrides.

    Subsystem Context:
        The COMPOSED profile, pairing reusable view, command, and codegen base
        profiles with local override rulesets. It sits above the three
        single-family profiles.

    System Context:
        Its ownership split is the detail to get right, and the docstring states
        it precisely: family profile references are SHARED LIBRARY OBJECTS and
        are NOT cleaned by this composed profile, while the local override
        rulesets ARE owned and cleaned. Cleaning a shared library profile from
        here would tear it out from under every other frame referencing it.
        That asymmetry is the reusable-versus-applied model made concrete -
        shared postures are borrowed, per-frame deviation is owned - and it is
        why the single-family profiles cascade cleanup into their rulesets while
        this one deliberately does not cascade into its family references.
    """
    _ast_helper_access: str = "internal"
    __agent_purpose__: str = (
        "access: internal. FrameACLProfile runtime object. Melder kernel machinery: read it to "
        "understand the runtime, do not drive it directly."
    )

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_version",
        "_name",
        "_view_profile",
        "_command_profile",
        "_codegen_profile",
        "_view_override_ruleset",
        "_command_override_ruleset",
        "_codegen_override_ruleset",
    ]

    def __init__(
            self,
            name: str,
            *,
            view_profile: FrameACLViewProfile,
            command_profile: Optional[FrameACLCommandProfile] = None,
            codegen_profile: FrameACLCodegenProfile,
            view_override_ruleset: Optional[FrameACLRuleSet] = None,
            command_override_ruleset: Optional[FrameACLRuleSet] = None,
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
            command_profile:
                Shared reusable command profile.
            codegen_profile:
                Shared reusable codegen profile.
            view_override_ruleset:
                Optional local view override ruleset.
            command_override_ruleset:
                Optional local command override ruleset.
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
        if command_profile is None:
            command_profile = FrameACLCommandProfile.create_default()
        if not isinstance(command_profile, FrameACLCommandProfile):
            raise TypeError("command_profile must be a FrameACLCommandProfile.")
        if not isinstance(codegen_profile, FrameACLCodegenProfile):
            raise TypeError("codegen_profile must be a FrameACLCodegenProfile.")
        if not version:
            raise ValueError("version cannot be empty.")
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._version: str = version
        self._name: str = name
        self._view_profile = view_profile
        self._command_profile = command_profile
        self._codegen_profile = codegen_profile
        self._view_override_ruleset = FrameACLViewProfile.coerce_ruleset(
            view_override_ruleset,
            "{0}_view_override".format(name),
        )
        self._command_override_ruleset = FrameACLCommandProfile.coerce_ruleset(
            command_override_ruleset,
            "{0}_command_override".format(name),
        )
        self._codegen_override_ruleset = FrameACLViewProfile.coerce_ruleset(
            codegen_override_ruleset,
            "{0}_codegen_override".format(name),
        )

    def cleanup(self) -> None:
        """
        Idempotently clear the composed profile.

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
            self._command_override_ruleset.cleanup()
            self._codegen_override_ruleset.cleanup()

            del self._view_override_ruleset
            del self._command_override_ruleset
            del self._codegen_override_ruleset
            del self._view_profile
            del self._command_profile
            del self._codegen_profile
            del self._version
            del self._name
            del self._id
        del self._lock

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
    def command_profile(self) -> FrameACLCommandProfile:
        """Return the shared reusable command profile referenced by this composition."""
        self.check_cleaned()
        return self._command_profile

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
    def command_override_ruleset(self) -> FrameACLRuleSet:
        """Return the owned command override ruleset for this composed profile."""
        self.check_cleaned()
        return self._command_override_ruleset

    @property
    def codegen_override_ruleset(self) -> FrameACLRuleSet:
        """Return the owned codegen override ruleset for this composed profile."""
        self.check_cleaned()
        return self._codegen_override_ruleset
