import threading
from typing import Optional
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.nexus.acl.configurations.profiles.view.frame_acl_view_profile import FrameACLViewProfile
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.nexus.acl.configurations.profiles.rules.frame_acl_ruleset import FrameACLRuleSet


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

    Threading:
        One instance lock guarding cleanup and ruleset-ownership transitions -
        grouped state under a nogil runtime.

    Registration:
        MELDER KERNEL - guarded. Built by the codegen profile builder from a
        registered strategy; never user-constructed.

    Subsystem Context:
        A REUSABLE codegen-family ruleset bundle, distinct from the applied
        revision that references it. Profiles are library objects shared across
        frames; configurations are per-frame applied state.

    System Context:
        The reusable-versus-applied split is the core of the ACL model. A
        profile is a named posture (`safe`, `hybrid`, `permissive`,
        `precision`, `full_access` where the family offers it) authored once and
        referenced by many frames, while local override rulesets on the applied
        configuration express per-frame deviation. Without that split every
        frame would restate an entire policy, and a fleet-wide posture change
        would mean editing every frame.
        This family governs what may be GENERATED AND RUN - specifically import allowlists, builtin/meta posture, recursive codegen - and is consumed
        through `CodegenSystem` beneath `CodegenCommandSystem`. Its cleanup cascades into the owned rulesets
        because those ARE the profile's content; the composed
        `FrameACLProfile` behaves differently and deliberately does NOT clean
        the family profiles it merely references.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_version",
        "_name",
        "_validation_strategy_name",
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
            validation_strategy_name: str = "generic",
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
            validation_strategy_name:
                Validator-owned strategy key used for profile-specific checks.
            version:
                Profile version string.

        Returns:
            None.
        """
        super().__init__()
        if not name:
            raise ValueError("name cannot be empty.")
        if not validation_strategy_name:
            raise ValueError("validation_strategy_name cannot be empty.")
        if not version:
            raise ValueError("version cannot be empty.")
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._version: str = version
        self._name: str = name
        self._validation_strategy_name: str = validation_strategy_name
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

        Contract:
            - Cleans all owned rulesets before dropping references.
            - Leaves the profile unusable after cleanup.

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

            del self._frame_ruleset
            del self._conduit_ruleset
            del self._spell_ruleset
            del self._capability_ruleset
            del self._validation_strategy_name
            del self._version
            del self._name
            del self._id
        del self._lock

    @classmethod
    def create_default(cls) -> "FrameACLCodegenProfile":
        """
        Create the default reusable codegen profile.

        Contract:
            Delegates to the standard `safe` codegen profile factory.

        Returns:
            FrameACLCodegenProfile: Default reusable codegen profile.
        """
        from melder.nexus.acl.configurations.profiles.codegen.safe_profile import (
            SafeCodegenProfileStrategy,
        )

        return SafeCodegenProfileStrategy().build()

    @classmethod
    def create_safe(cls) -> "FrameACLCodegenProfile":
        """
        Create the reusable `safe` codegen profile.

        Contract:
            Returns the restrictive default codegen posture.

        Returns:
            FrameACLCodegenProfile: Reusable `safe` codegen profile.
        """
        from melder.nexus.acl.configurations.profiles.codegen.safe_profile import (
            SafeCodegenProfileStrategy,
        )

        return SafeCodegenProfileStrategy().build()

    @classmethod
    def create_hybrid(cls) -> "FrameACLCodegenProfile":
        """
        Create the reusable `hybrid` codegen profile.

        Contract:
            Returns the intermediate codegen posture between safe and
            permissive.

        Returns:
            FrameACLCodegenProfile: Reusable `hybrid` codegen profile.
        """
        from melder.nexus.acl.configurations.profiles.codegen.hybrid_profile import (
            HybridCodegenProfileStrategy,
        )

        return HybridCodegenProfileStrategy().build()

    @classmethod
    def create_permissive(cls) -> "FrameACLCodegenProfile":
        """
        Create the reusable `permissive` codegen profile.

        Contract:
            Returns the most open standard codegen posture.

        Returns:
            FrameACLCodegenProfile: Reusable `permissive` codegen profile.
        """
        from melder.nexus.acl.configurations.profiles.codegen.permissive_profile import (
            PermissiveCodegenProfileStrategy,
        )

        return PermissiveCodegenProfileStrategy().build()

    @classmethod
    def create_full_access(cls) -> "FrameACLCodegenProfile":
        """
        Create the reusable `full_access` codegen profile.

        Contract:
            Returns the least restrictive standard codegen posture in the
            current ACL model.

        Returns:
            FrameACLCodegenProfile: Reusable `full_access` codegen profile.
        """
        from melder.nexus.acl.configurations.profiles.codegen.full_access_profile import (
            FullAccessCodegenProfileStrategy,
        )

        return FullAccessCodegenProfileStrategy().build()

    @classmethod
    def create_precision(cls) -> "FrameACLCodegenProfile":
        """
        Create the reusable `precision` codegen profile.

        Contract:
            Returns the standard precision-oriented codegen posture.

        Returns:
            FrameACLCodegenProfile: Reusable `precision` codegen profile.
        """
        from melder.nexus.acl.configurations.profiles.codegen.precision import (
            PrecisionCodegenProfileStrategy,
        )

        return PrecisionCodegenProfileStrategy().build()

    @property
    def id(self) -> str:
        """Return the stable identifier for this reusable codegen profile."""
        self.check_cleaned()
        return self._id

    @property
    def version(self) -> str:
        """Return the version string carried by this reusable codegen profile."""
        self.check_cleaned()
        return self._version

    @property
    def name(self) -> str:
        """Return the stable name of this reusable codegen profile."""
        self.check_cleaned()
        return self._name

    @property
    def validation_strategy_name(self) -> str:
        """Return the validator-owned strategy key for this profile."""
        self.check_cleaned()
        return self._validation_strategy_name

    @property
    def frame_ruleset(self) -> FrameACLRuleSet:
        """Return the owned frame-scoped ruleset for this codegen profile."""
        self.check_cleaned()
        return self._frame_ruleset

    @property
    def conduit_ruleset(self) -> FrameACLRuleSet:
        """Return the owned conduit-scoped ruleset for this codegen profile."""
        self.check_cleaned()
        return self._conduit_ruleset

    @property
    def spell_ruleset(self) -> FrameACLRuleSet:
        """Return the owned spell-scoped ruleset for this codegen profile."""
        self.check_cleaned()
        return self._spell_ruleset

    @property
    def capability_ruleset(self) -> FrameACLRuleSet:
        """Return the owned capability-scoped ruleset for this codegen profile."""
        self.check_cleaned()
        return self._capability_ruleset
