import threading
from typing import List, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.acl.profiles.frame_acl_rule import FrameACLRule
from melder.aether.nexus.acl.profiles.frame_acl_ruleset import FrameACLRuleSet
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class FrameACLViewProfile(Cleanable):
    """
    Purpose:
        Hold one reusable typed view-profile ruleset bundle.

    Contract:
        - Owns frame, conduit, spell, and member rulesets.
        - Carries the required frame and conduit payload contracts.
        - Carries the minimum spell payload floor required for richer member
          rules.
        - Uses an instance lock because cleanup and ruleset ownership mutation
          are grouped state transitions in a nogil runtime.

    Lifecycle:
        Cleanup is idempotent and cascades into all owned rulesets.
    """

    __melder_internal__ = _mrg.sentinel
    _DEFAULT_SPELL_PAYLOAD_PROFILE_NAME = "general"
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_version",
        "_name",
        "_required_frame_payload_profile_name",
        "_required_frame_payload_profile_version",
        "_required_conduit_payload_profile_name",
        "_required_conduit_payload_profile_version",
        "_minimum_spell_payload_profile_name",
        "_minimum_spell_payload_profile_version",
        "_frame_ruleset",
        "_conduit_ruleset",
        "_spell_ruleset",
        "_member_ruleset",
    ]

    def __init__(
            self,
            name: str,
            *,
            minimum_spell_payload_profile_name: str,
            required_frame_payload_profile_name: str = "frame",
            required_frame_payload_profile_version: str = "0.0.1",
            required_conduit_payload_profile_name: str = "conduit",
            required_conduit_payload_profile_version: str = "0.0.1",
            minimum_spell_payload_profile_version: str = "0.0.1",
            frame_ruleset: Optional[FrameACLRuleSet] = None,
            conduit_ruleset: Optional[FrameACLRuleSet] = None,
            spell_ruleset: Optional[FrameACLRuleSet] = None,
            member_ruleset: Optional[FrameACLRuleSet] = None,
            version: str = "0.0.1",
    ) -> None:
        """
        Initialize one reusable view ACL profile.

        Args:
            name:
                Stable profile name.
            required_frame_payload_profile_name:
                Required frame descriptor payload family name.
            required_frame_payload_profile_version:
                Required frame descriptor payload contract version.
            required_conduit_payload_profile_name:
                Required conduit descriptor payload family name.
            required_conduit_payload_profile_version:
                Required conduit descriptor payload contract version.
            minimum_spell_payload_profile_name:
                Minimum spell payload floor required by this profile.
            minimum_spell_payload_profile_version:
                Minimum spell payload contract version required by this profile.
            frame_ruleset:
                Optional frame-scoped ruleset override.
            conduit_ruleset:
                Optional conduit-scoped ruleset override.
            spell_ruleset:
                Optional spell-scoped ruleset override.
            member_ruleset:
                Optional member-scoped ruleset override.
            version:
                Profile version string.

        Returns:
            None.
        """
        super().__init__()
        if not name:
            raise ValueError("name cannot be empty.")
        if not required_frame_payload_profile_name:
            raise ValueError("required_frame_payload_profile_name cannot be empty.")
        if not required_frame_payload_profile_version:
            raise ValueError("required_frame_payload_profile_version cannot be empty.")
        if not required_conduit_payload_profile_name:
            raise ValueError("required_conduit_payload_profile_name cannot be empty.")
        if not required_conduit_payload_profile_version:
            raise ValueError("required_conduit_payload_profile_version cannot be empty.")
        if not minimum_spell_payload_profile_name:
            raise ValueError(
                "minimum_spell_payload_profile_name cannot be empty."
            )
        if not minimum_spell_payload_profile_version:
            raise ValueError(
                "minimum_spell_payload_profile_version cannot be empty."
            )
        if not version:
            raise ValueError("version cannot be empty.")
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._version: str = version
        self._name: str = name
        self._required_frame_payload_profile_name: str = (
            required_frame_payload_profile_name
        )
        self._required_frame_payload_profile_version: str = (
            required_frame_payload_profile_version
        )
        self._required_conduit_payload_profile_name: str = (
            required_conduit_payload_profile_name
        )
        self._required_conduit_payload_profile_version: str = (
            required_conduit_payload_profile_version
        )
        self._minimum_spell_payload_profile_name: str = (
            minimum_spell_payload_profile_name
        )
        self._minimum_spell_payload_profile_version: str = (
            minimum_spell_payload_profile_version
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
            self._frame_ruleset = None
            self._conduit_ruleset = None
            self._spell_ruleset = None
            self._member_ruleset = None
            self._required_frame_payload_profile_name = None
            self._required_frame_payload_profile_version = None
            self._required_conduit_payload_profile_name = None
            self._required_conduit_payload_profile_version = None
            self._minimum_spell_payload_profile_name = None
            self._minimum_spell_payload_profile_version = None
            self._version = None
            self._name = None
            self._id = None
        self._lock = None

    @classmethod
    def create_default(cls) -> "FrameACLViewProfile":
        """
        Create the default reusable view profile.

        Contract:
            Delegates to the standard `safe` view profile factory.

        Returns:
            FrameACLViewProfile: Default reusable view profile.
        """
        from melder.aether.nexus.acl.profiles.view.safe_profile import (
            create_safe_view_profile,
        )

        return create_safe_view_profile()

    @classmethod
    def create_safe(cls) -> "FrameACLViewProfile":
        """
        Create the reusable `safe` view profile.

        Contract:
            Returns the restrictive default view posture.

        Returns:
            FrameACLViewProfile: Reusable `safe` view profile.
        """
        from melder.aether.nexus.acl.profiles.view.safe_profile import (
            create_safe_view_profile,
        )

        return create_safe_view_profile()

    @classmethod
    def create_hybrid(cls) -> "FrameACLViewProfile":
        """
        Create the reusable `hybrid` view profile.

        Contract:
            Returns the intermediate view posture between safe and permissive.

        Returns:
            FrameACLViewProfile: Reusable `hybrid` view profile.
        """
        from melder.aether.nexus.acl.profiles.view.hybrid_profile import (
            create_hybrid_view_profile,
        )

        return create_hybrid_view_profile()

    @classmethod
    def create_permissive(cls) -> "FrameACLViewProfile":
        """
        Create the reusable `permissive` view profile.

        Contract:
            Returns the most open standard view posture.

        Returns:
            FrameACLViewProfile: Reusable `permissive` view profile.
        """
        from melder.aether.nexus.acl.profiles.view.permissive_profile import (
            create_permissive_view_profile,
        )

        return create_permissive_view_profile()

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
    def required_frame_payload_profile_name(self) -> str:
        """Return the required frame payload family name for this profile."""
        self.check_cleaned()
        return self._required_frame_payload_profile_name

    @property
    def required_frame_payload_profile_version(self) -> str:
        """Return the required frame payload contract version for this profile."""
        self.check_cleaned()
        return self._required_frame_payload_profile_version

    @property
    def required_conduit_payload_profile_name(self) -> str:
        """Return the required conduit payload family name for this profile."""
        self.check_cleaned()
        return self._required_conduit_payload_profile_name

    @property
    def required_conduit_payload_profile_version(self) -> str:
        """Return the required conduit payload contract version for this profile."""
        self.check_cleaned()
        return self._required_conduit_payload_profile_version

    @property
    def minimum_spell_payload_profile_name(self) -> str:
        """Return the minimum spell payload floor required by this view profile."""
        self.check_cleaned()
        return self._minimum_spell_payload_profile_name

    @property
    def minimum_spell_payload_profile_version(self) -> str:
        """Return the minimum spell payload contract version for this profile."""
        self.check_cleaned()
        return self._minimum_spell_payload_profile_version

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
            validates that the supplied object is already a `FrameACLRuleSet`.
        """
        if ruleset is None:
            return FrameACLRuleSet(default_name)
        if not isinstance(ruleset, FrameACLRuleSet):
            raise TypeError("ruleset must be a FrameACLRuleSet.")
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
