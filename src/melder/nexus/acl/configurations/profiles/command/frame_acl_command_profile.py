import threading
from typing import List, Optional

from melder.nexus.acl.configurations.profiles.rules.frame_acl_rule import (
    FrameACLRule,
)
from melder.nexus.acl.configurations.profiles.rules.frame_acl_ruleset import (
    FrameACLRuleSet,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.nexus.acl.configurations.profiles.rules.frame_acl_ruleset import FrameACLRuleSet


class FrameACLCommandProfile(Cleanable):
    """

    Purpose:
        Hold one reusable typed command-profile ruleset bundle.

    Contract:
        - Owns frame, conduit, spell, and member rulesets.
        - Carries one validator-owned strategy key used for profile-specific
          validation behavior.
        - Uses an instance lock because cleanup and ruleset ownership mutation
          are grouped state transitions in a nogil runtime.

    Lifecycle:
        Cleanup is idempotent and cascades into all owned rulesets.

    Threading:
        One instance lock guarding cleanup and ruleset-ownership transitions -
        grouped state under a nogil runtime.

    Registration:
        MELDER KERNEL - guarded. Built by the command profile builder from a
        registered strategy; never user-constructed.

    Subsystem Context:
        A REUSABLE command-family ruleset bundle, distinct from the applied
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
        This family governs what may be DONE - specifically member read/invoke/write posture - and is consumed
        through `CommandSystem` and its three room postures. Its cleanup cascades into the owned rulesets
        because those ARE the profile's content; the composed
        `FrameACLProfile` behaves differently and deliberately does NOT clean
        the family profiles it merely references.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. FrameACLCommandProfile runtime object. Melder kernel machinery: read "
        "it to understand the runtime, do not drive it directly."
    )

    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_version",
        "_name",
        "_validation_strategy_name",
        "_frame_ruleset",
        "_conduit_ruleset",
        "_spell_ruleset",
        "_member_ruleset",
    ]

    def __init__(
            self,
            name: str,
            *,
            frame_ruleset: Optional[FrameACLRuleSet] = None,
            conduit_ruleset: Optional[FrameACLRuleSet] = None,
            spell_ruleset: Optional[FrameACLRuleSet] = None,
            member_ruleset: Optional[FrameACLRuleSet] = None,
            validation_strategy_name: str = "generic",
            version: str = "0.0.1",
    ) -> None:
        """
        Initialize one reusable command ACL profile.

        Args:
            name:
                Stable profile name.
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
        if not validation_strategy_name:
            raise ValueError("validation_strategy_name cannot be empty.")
        if not version:
            raise ValueError("version cannot be empty.")
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._version: str = version
        self._name: str = name
        self._validation_strategy_name: str = validation_strategy_name
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
        Idempotently clear the command profile and owned rulesets.

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
            del self._validation_strategy_name
            del self._version
            del self._name
            del self._id
        del self._lock

    @classmethod
    def create_default(cls) -> "FrameACLCommandProfile":
        """Create the default reusable command profile."""
        from melder.nexus.acl.configurations.profiles.command.safe_profile import (
            SafeCommandProfileStrategy,
        )

        return SafeCommandProfileStrategy().build()

    @classmethod
    def create_safe(cls) -> "FrameACLCommandProfile":
        """Create the reusable `safe` command profile."""
        from melder.nexus.acl.configurations.profiles.command.safe_profile import (
            SafeCommandProfileStrategy,
        )

        return SafeCommandProfileStrategy().build()

    @classmethod
    def create_hybrid(cls) -> "FrameACLCommandProfile":
        """Create the reusable `hybrid` command profile."""
        from melder.nexus.acl.configurations.profiles.command.hybrid_profile import (
            HybridCommandProfileStrategy,
        )

        return HybridCommandProfileStrategy().build()

    @classmethod
    def create_permissive(cls) -> "FrameACLCommandProfile":
        """Create the reusable `permissive` command profile."""
        from melder.nexus.acl.configurations.profiles.command.permissive_profile import (
            PermissiveCommandProfileStrategy,
        )

        return PermissiveCommandProfileStrategy().build()

    @classmethod
    def create_precision(cls) -> "FrameACLCommandProfile":
        """Create the reusable `precision` command profile."""
        from melder.nexus.acl.configurations.profiles.command.precision import (
            PrecisionCommandProfileStrategy,
        )

        return PrecisionCommandProfileStrategy().build()

    @property
    def id(self) -> str:
        """Return the stable identifier for this reusable command profile."""
        self.check_cleaned()
        return self._id

    @property
    def version(self) -> str:
        """Return the version string carried by this reusable command profile."""
        self.check_cleaned()
        return self._version

    @property
    def name(self) -> str:
        """Return the stable name of this reusable command profile."""
        self.check_cleaned()
        return self._name

    @property
    def validation_strategy_name(self) -> str:
        """Return the validator-owned strategy key for this profile."""
        self.check_cleaned()
        return self._validation_strategy_name

    @property
    def frame_ruleset(self) -> FrameACLRuleSet:
        """Return the owned frame-scoped ruleset for this command profile."""
        self.check_cleaned()
        return self._frame_ruleset

    @property
    def conduit_ruleset(self) -> FrameACLRuleSet:
        """Return the owned conduit-scoped ruleset for this command profile."""
        self.check_cleaned()
        return self._conduit_ruleset

    @property
    def spell_ruleset(self) -> FrameACLRuleSet:
        """Return the owned spell-scoped ruleset for this command profile."""
        self.check_cleaned()
        return self._spell_ruleset

    @property
    def member_ruleset(self) -> FrameACLRuleSet:
        """Return the owned member-scoped ruleset for this command profile."""
        self.check_cleaned()
        return self._member_ruleset

    @staticmethod
    def coerce_ruleset(
            ruleset: Optional[FrameACLRuleSet],
            default_name: str,
    ) -> FrameACLRuleSet:
        """Normalize one optional ruleset input into a usable ruleset object.

        Args:
            ruleset: Optional ruleset to normalize; None yields an empty
                default-named ruleset.
            default_name: Name used when synthesizing a default ruleset.

        Returns:
            FrameACLRuleSet: A concrete usable ruleset.
        """
        return FrameACLCommandProfile._coerce_ruleset(ruleset, default_name)

    @staticmethod
    def build_rule(
            rule_name: str,
            operation: str,
            effect: str,
            conditions: Optional[dict] = None,
    ) -> FrameACLRule:
        """Build one typed ACL rule from the supplied rule components.

        Args:
            rule_name: Stable rule name.
            operation: Operation the rule governs.
            effect: Rule effect (e.g. "allow"/"deny").
            conditions: Optional condition dict.

        Returns:
            FrameACLRule: The constructed rule.
        """
        return FrameACLCommandProfile._build_rule(
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
        """Build one typed ACL ruleset from a name and rule list.

        Args:
            name: Ruleset name.
            rules: Rules to include.

        Returns:
            FrameACLRuleSet: The constructed ruleset.
        """
        return FrameACLCommandProfile._build_ruleset(name, rules)

    @staticmethod
    def _coerce_ruleset(
            ruleset: Optional[FrameACLRuleSet],
            default_name: str,
    ) -> FrameACLRuleSet:
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
        return FrameACLRuleSet(name, rules=rules)
