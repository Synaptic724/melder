import threading
from typing import List, Optional
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.nexus.acl.configurations.profiles.rules.frame_acl_rule import FrameACLRule
from melder.nexus.acl.configurations.profiles.rules.frame_acl_ruleset import FrameACLRuleSet
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.nexus.acl.configurations.profiles.rules.frame_acl_ruleset import FrameACLRuleSet


class FrameACLViewProfile(Cleanable):
    """

    Purpose:
        Hold one reusable typed view-profile ruleset bundle.

    Contract:
        - Owns frame, conduit, spell, and member rulesets.
        - Carries the required Nexus dataset contract for published records.
        - Carries the minimum spell payload detail floor required for richer
          spell/member rules.
        - Uses an instance lock because cleanup and ruleset ownership mutation
          are grouped state transitions in a nogil runtime.

    Lifecycle:
        Cleanup is idempotent and cascades into all owned rulesets.

    Threading:
        One instance lock guarding cleanup and ruleset-ownership transitions -
        grouped state under a nogil runtime.

    Registration:
        MELDER KERNEL - guarded. Built by the view profile builder from a
        registered strategy; never user-constructed.

    Subsystem Context:
        A REUSABLE view-family ruleset bundle, distinct from the applied
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
        This family governs what may be SEEN - specifically descriptor floors and payload visibility - and is consumed
        through `FrameViewer` and its helper surfaces. Its cleanup cascades into the owned rulesets
        because those ARE the profile's content; the composed
        `FrameACLProfile` behaves differently and deliberately does NOT clean
        the family profiles it merely references.
    """
    _ast_helper_access: str = "internal"
    __agent_purpose__: str = (
        "access: internal. FrameACLViewProfile runtime object. Melder kernel machinery: read it "
        "to understand the runtime, do not drive it directly."
    )

    __melder_internal__ = _mrg.sentinel
    _DEFAULT_SPELL_PAYLOAD_PROFILE_NAME = "general"
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_version",
        "_name",
        "_validation_strategy_name",
        "_required_nexus_label",
        "_required_nexus_version",
        "_minimum_spell_payload_type",
        "_minimum_spell_payload_version",
        "_frame_ruleset",
        "_conduit_ruleset",
        "_spell_ruleset",
        "_member_ruleset",
    ]

    def __init__(
            self,
            name: str,
            *,
            minimum_spell_payload_type: str,
            required_nexus_label: str = "default",
            required_nexus_version: str = "0.0.1",
            minimum_spell_payload_version: str = "0.0.1",
            frame_ruleset: Optional[FrameACLRuleSet] = None,
            conduit_ruleset: Optional[FrameACLRuleSet] = None,
            spell_ruleset: Optional[FrameACLRuleSet] = None,
            member_ruleset: Optional[FrameACLRuleSet] = None,
            validation_strategy_name: str = "generic",
            version: str = "0.0.1",
    ) -> None:
        """
        Initialize one reusable view ACL profile.

        Args:
            name:
                Stable profile name.
            required_nexus_label:
                Required Nexus dataset label for published records.
            required_nexus_version:
                Required Nexus dataset version for published records.
            minimum_spell_payload_type:
                Minimum spell payload detail type required by this profile.
            minimum_spell_payload_version:
                Minimum spell payload contract version required by this profile.
            frame_ruleset:
                Optional frame-scoped ruleset override.
            conduit_ruleset:
                Optional conduit-scoped ruleset override.
            spell_ruleset:
                Optional spell-scoped ruleset override.
            member_ruleset:
                Optional member-scoped ruleset override.
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
        if not required_nexus_label:
            raise ValueError("required_nexus_label cannot be empty.")
        if not required_nexus_version:
            raise ValueError("required_nexus_version cannot be empty.")
        if not minimum_spell_payload_type:
            raise ValueError(
                "minimum_spell_payload_type cannot be empty."
            )
        if not minimum_spell_payload_version:
            raise ValueError(
                "minimum_spell_payload_version cannot be empty."
            )
        if not validation_strategy_name:
            raise ValueError("validation_strategy_name cannot be empty.")
        if not version:
            raise ValueError("version cannot be empty.")
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._version: str = version
        self._name: str = name
        self._validation_strategy_name: str = validation_strategy_name
        self._required_nexus_label: str = required_nexus_label
        self._required_nexus_version: str = required_nexus_version
        self._minimum_spell_payload_type: str = minimum_spell_payload_type
        self._minimum_spell_payload_version: str = (
            minimum_spell_payload_version
        )
        self._frame_ruleset = self._coerce_ruleset(
            frame_ruleset,
            "{0}_frame".format(name),
        )
        self._conduit_ruleset = self._coerce_ruleset(
            conduit_ruleset,
            "{0}_conduit".format(name),
        )
        self._spell_ruleset = self._coerce_ruleset(
            spell_ruleset,
            "{0}_spell".format(name),
        )
        self._member_ruleset = self._coerce_ruleset(
            member_ruleset,
            "{0}_member".format(name),
        )

    def cleanup(self) -> None:
        """
        Idempotently clear the view profile and owned rulesets.

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
            self._member_ruleset.cleanup()

            del self._frame_ruleset
            del self._conduit_ruleset
            del self._spell_ruleset
            del self._member_ruleset
            del self._required_nexus_label
            del self._required_nexus_version
            del self._minimum_spell_payload_type
            del self._minimum_spell_payload_version
            del self._validation_strategy_name
            del self._version
            del self._name
            del self._id
        del self._lock

    @classmethod
    def create_default(cls) -> "FrameACLViewProfile":
        """
        Create the default reusable view profile.

        Contract:
            Delegates to the standard `safe` view profile factory.

        Returns:
            FrameACLViewProfile: Default reusable view profile.
        """
        from melder.nexus.acl.configurations.profiles.view.safe_profile import (
            SafeViewProfileStrategy,
        )

        return SafeViewProfileStrategy().build()

    @classmethod
    def create_safe(cls) -> "FrameACLViewProfile":
        """
        Create the reusable `safe` view profile.

        Contract:
            Returns the restrictive default view posture.

        Returns:
            FrameACLViewProfile: Reusable `safe` view profile.
        """
        from melder.nexus.acl.configurations.profiles.view.safe_profile import (
            SafeViewProfileStrategy,
        )

        return SafeViewProfileStrategy().build()

    @classmethod
    def create_hybrid(cls) -> "FrameACLViewProfile":
        """
        Create the reusable `hybrid` view profile.

        Contract:
            Returns the intermediate view posture between safe and permissive.

        Returns:
            FrameACLViewProfile: Reusable `hybrid` view profile.
        """
        from melder.nexus.acl.configurations.profiles.view.hybrid_profile import (
            HybridViewProfileStrategy,
        )

        return HybridViewProfileStrategy().build()

    @classmethod
    def create_permissive(cls) -> "FrameACLViewProfile":
        """
        Create the reusable `permissive` view profile.

        Contract:
            Returns the most open standard view posture.

        Returns:
            FrameACLViewProfile: Reusable `permissive` view profile.
        """
        from melder.nexus.acl.configurations.profiles.view.permissive_profile import (
            PermissiveViewProfileStrategy,
        )

        return PermissiveViewProfileStrategy().build()

    @classmethod
    def create_precision(cls) -> "FrameACLViewProfile":
        """
        Create the reusable `precision` view profile.

        Contract:
            Returns the standard precision-oriented view posture.

        Returns:
            FrameACLViewProfile: Reusable `precision` view profile.
        """
        from melder.nexus.acl.configurations.profiles.view.precision import (
            PrecisionViewProfileStrategy,
        )

        return PrecisionViewProfileStrategy().build()

    @property
    def id(self) -> str:
        """Return the stable identifier for this reusable view profile."""
        self.check_cleaned()
        return self._id

    @property
    def version(self) -> str:
        """Return the version string carried by this reusable view profile."""
        self.check_cleaned()
        return self._version

    @property
    def name(self) -> str:
        """Return the stable name of this reusable view profile."""
        self.check_cleaned()
        return self._name

    @property
    def validation_strategy_name(self) -> str:
        """Return the validator-owned strategy key for this profile."""
        self.check_cleaned()
        return self._validation_strategy_name

    @property
    def required_nexus_label(self) -> str:
        """Return the required Nexus dataset label for this profile."""
        self.check_cleaned()
        return self._required_nexus_label

    @property
    def required_nexus_version(self) -> str:
        """Return the required Nexus dataset version for this profile."""
        self.check_cleaned()
        return self._required_nexus_version

    @property
    def minimum_spell_payload_type(self) -> str:
        """Return the minimum spell payload detail type for this profile."""
        self.check_cleaned()
        return self._minimum_spell_payload_type

    @property
    def minimum_spell_payload_version(self) -> str:
        """Return the minimum spell payload version for this profile."""
        self.check_cleaned()
        return self._minimum_spell_payload_version

    @property
    def frame_ruleset(self) -> FrameACLRuleSet:
        """Return the owned frame-scoped ruleset for this view profile."""
        self.check_cleaned()
        return self._frame_ruleset

    @property
    def conduit_ruleset(self) -> FrameACLRuleSet:
        """Return the owned conduit-scoped ruleset for this view profile."""
        self.check_cleaned()
        return self._conduit_ruleset

    @property
    def spell_ruleset(self) -> FrameACLRuleSet:
        """Return the owned spell-scoped ruleset for this view profile."""
        self.check_cleaned()
        return self._spell_ruleset

    @property
    def member_ruleset(self) -> FrameACLRuleSet:
        """Return the owned member-scoped ruleset for this view profile."""
        self.check_cleaned()
        return self._member_ruleset

    @staticmethod
    def coerce_ruleset(
            ruleset: Optional[FrameACLRuleSet],
            default_name: str,
    ) -> FrameACLRuleSet:
        """Normalize one optional ruleset input into a usable ruleset object."""
        return FrameACLViewProfile._coerce_ruleset(ruleset, default_name)

    @staticmethod
    def build_rule(
            rule_name: str,
            operation: str,
            effect: str,
            conditions: Optional[dict] = None,
    ) -> FrameACLRule:
        """Build one typed ACL rule from the supplied rule components."""
        return FrameACLViewProfile._build_rule(
            rule_name,
            operation,
            effect,
            conditions,
        )

    @staticmethod
    def build_ruleset(
            name: str,
            rules: List[FrameACLRule],
    ) -> FrameACLRuleSet:
        """Build one typed ACL ruleset from a name and rule list."""
        return FrameACLViewProfile._build_ruleset(name, rules)

    @staticmethod
    def _coerce_ruleset(
            ruleset: Optional[FrameACLRuleSet],
            default_name: str,
    ) -> FrameACLRuleSet:
        """
        Normalize one optional ruleset into a concrete ruleset instance.

        Contract:
            Returns a new empty ruleset when `ruleset` is None and otherwise
            validates that the supplied object satisfies `FrameACLRuleSet`.
        """
        if ruleset is None:
            return FrameACLRuleSet(default_name)
        if not isinstance(ruleset, FrameACLRuleSet):
            raise TypeError("ruleset must be a FrameACLRuleSet instance.")
        return ruleset

    @staticmethod
    def _build_rule(
            rule_name: str,
            operation: str,
            effect: str,
            conditions: Optional[dict] = None,
    ) -> FrameACLRule:
        """
        Build one typed ACL rule from primitive rule components.
        """
        return FrameACLRule(
            rule_name=rule_name,
            operation=operation,
            effect=effect,
            conditions=conditions,
        )

    @staticmethod
    def _build_ruleset(
            name: str,
            rules: List[FrameACLRule],
    ) -> FrameACLRuleSet:
        """
        Build one typed ACL ruleset from a ruleset name and rule list.
        """
        return FrameACLRuleSet(name, rules=rules)
