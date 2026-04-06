import threading
from typing import Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.acl.profiles.frame_acl_ruleset import FrameACLRuleSet
from melder.aether.nexus.acl.profiles.frame_acl_view_profile import FrameACLViewProfile
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class FrameACLCodegenProfile(Cleanable):
    """
    Purpose:
        Hold one reusable typed codegen-profile ruleset bundle.

    Contract:
        - Owns frame, conduit, spell, and capability rulesets.
        - Uses an instance lock because cleanup and ruleset ownership mutation
          are grouped state transitions in a nogil runtime.

    Lifecycle:
        Cleanup is idempotent and cascades into all owned rulesets.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_version",
        "_name",
        "_frame_ruleset",
        "_conduit_ruleset",
        "_spell_ruleset",
        "_capability_ruleset",
    ]

    def __init__(
            self,
            name: str,
            *,
            frame_ruleset: Optional[FrameACLRuleSet] = None,
            conduit_ruleset: Optional[FrameACLRuleSet] = None,
            spell_ruleset: Optional[FrameACLRuleSet] = None,
            capability_ruleset: Optional[FrameACLRuleSet] = None,
            version: str = "0.0.1",
    ) -> None:
        """
        Initialize one reusable codegen ACL profile.

        Args:
            name:
                Stable profile name.
            frame_ruleset:
                Optional frame-scoped ruleset override.
            conduit_ruleset:
                Optional conduit-scoped ruleset override.
            spell_ruleset:
                Optional spell-scoped ruleset override.
            capability_ruleset:
                Optional capability-scoped ruleset override.
            version:
                Profile version string.

        Returns:
            None.
        """
        super().__init__()
        if not name:
            raise ValueError("name cannot be empty.")
        if not version:
            raise ValueError("version cannot be empty.")
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._version: str = version
        self._name: str = name
        self._frame_ruleset = FrameACLViewProfile.coerce_ruleset(
            frame_ruleset,
            "{0}_frame".format(name),
        )
        self._conduit_ruleset = FrameACLViewProfile.coerce_ruleset(
            conduit_ruleset,
            "{0}_conduit".format(name),
        )
        self._spell_ruleset = FrameACLViewProfile.coerce_ruleset(
            spell_ruleset,
            "{0}_spell".format(name),
        )
        self._capability_ruleset = FrameACLViewProfile.coerce_ruleset(
            capability_ruleset,
            "{0}_capability".format(name),
        )

    def cleanup(self) -> None:
        """
        Idempotently clear the codegen profile and owned rulesets.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._frame_ruleset.cleanup()
            self._conduit_ruleset.cleanup()
            self._spell_ruleset.cleanup()
            self._capability_ruleset.cleanup()
            self._frame_ruleset = None
            self._conduit_ruleset = None
            self._spell_ruleset = None
            self._capability_ruleset = None
            self._version = None
            self._name = None
            self._id = None
        self._lock = None

    @classmethod
    def create_default(cls) -> "FrameACLCodegenProfile":
        """
        Create the default reusable codegen profile.

        Returns:
            FrameACLCodegenProfile: Default reusable codegen profile.
        """
        from melder.aether.nexus.acl.profiles.codegen.safe_profile import (
            create_safe_codegen_profile,
        )

        return create_safe_codegen_profile()

    @classmethod
    def create_safe(cls) -> "FrameACLCodegenProfile":
        """
        Create the reusable `safe` codegen profile.

        Returns:
            FrameACLCodegenProfile: Reusable `safe` codegen profile.
        """
        from melder.aether.nexus.acl.profiles.codegen.safe_profile import (
            create_safe_codegen_profile,
        )

        return create_safe_codegen_profile()

    @classmethod
    def create_hybrid(cls) -> "FrameACLCodegenProfile":
        """
        Create the reusable `hybrid` codegen profile.

        Returns:
            FrameACLCodegenProfile: Reusable `hybrid` codegen profile.
        """
        from melder.aether.nexus.acl.profiles.codegen.hybrid_profile import (
            create_hybrid_codegen_profile,
        )

        return create_hybrid_codegen_profile()

    @classmethod
    def create_permissive(cls) -> "FrameACLCodegenProfile":
        """
        Create the reusable `permissive` codegen profile.

        Returns:
            FrameACLCodegenProfile: Reusable `permissive` codegen profile.
        """
        from melder.aether.nexus.acl.profiles.codegen.permissive_profile import (
            create_permissive_codegen_profile,
        )

        return create_permissive_codegen_profile()

    @property
    def id(self) -> str:
        """Return the stable profile identifier."""
        self.check_cleaned()
        return self._id

    @property
    def version(self) -> str:
        """Return the reusable profile version string."""
        self.check_cleaned()
        return self._version

    @property
    def name(self) -> str:
        """Return the stable profile name."""
        self.check_cleaned()
        return self._name

    @property
    def frame_ruleset(self) -> FrameACLRuleSet:
        """Return the frame-scoped ruleset."""
        self.check_cleaned()
        return self._frame_ruleset

    @property
    def conduit_ruleset(self) -> FrameACLRuleSet:
        """Return the conduit-scoped ruleset."""
        self.check_cleaned()
        return self._conduit_ruleset

    @property
    def spell_ruleset(self) -> FrameACLRuleSet:
        """Return the spell-scoped ruleset."""
        self.check_cleaned()
        return self._spell_ruleset

    @property
    def capability_ruleset(self) -> FrameACLRuleSet:
        """Return the capability-scoped ruleset."""
        self.check_cleaned()
        return self._capability_ruleset
