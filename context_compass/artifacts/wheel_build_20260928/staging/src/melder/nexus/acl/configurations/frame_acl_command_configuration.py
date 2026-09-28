import json
import threading
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from melder.nexus.acl.configurations.profiles.command.frame_acl_command_profile import (
    FrameACLCommandProfile,
)
from melder.nexus.acl.configurations.profiles.rules.frame_acl_ruleset import FrameACLRuleSet
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.nexus.acl.configurations.profiles.command.frame_acl_command_profile import FrameACLCommandProfile
from melder.nexus.acl.configurations.profiles.rules.frame_acl_ruleset import FrameACLRuleSet


class FrameACLCommandConfiguration(Cleanable):
    """

    Purpose:
        Represent one applied command-side ACL configuration revision.

    Contract:
        - Carries stable command-profile identity/version plus detached frame,
          conduit, spell, and member override rulesets.
        - Carries revision metadata so container-owned chains can version these
          objects directly.
        - Remains serializable for persistence and detached cloning.
        - Uses an instance lock because cleanup and grouped metadata/ruleset
          mutation touch multiple owned fields in a nogil runtime.

    Threading:
        One instance lock. The docstring's justification is exact and worth
        keeping: cleanup and grouped metadata/ruleset mutation touch several
        owned fields together, and under free-threaded 3.14t there is no GIL
        making that grouping incidentally atomic.

    Lifecycle / Cleanup:
        One applied revision inside a container-owned command chain. Cleanup is
        idempotent and releases the detached rulesets it owns.

    Registration:
        MELDER KERNEL - guarded. Produced by the ACL authoring path
        (`FrameACLBuilder` -> `FrameACLContainer`); never user-constructed.

    Subsystem Context:
        The applied-revision object of the command family - one of three
        independent chains a `FrameACLContainer` owns (view, command, codegen).
        It governs what may be DONE, and its answers are consumed through `CommandSystem` and its three room postures.

    System Context:
        Carrying revision metadata ON the configuration is what lets a
        container version these objects DIRECTLY rather than wrapping them in a
        separate history record. A chain is therefore a list of self-describing
        revisions, which is why a chain bump can fan a projection refresh out
        through `Nexus` carrying enough identity for each Rift to know what
        changed.
        Rulesets are DETACHED rather than shared with the profile they came
        from: a revision must remain a stable historical answer, so later edits
        to a reusable profile cannot retroactively rewrite what a committed
        revision granted. Staying serializable is the same property viewed from
        persistence - a revision has to survive round-tripping to be auditable.
        This family governs member read/invoke/write posture; the other two chains answer their own
        questions independently, which is what makes least privilege
        expressible per frame.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. FrameACLCommandConfiguration runtime object. Melder kernel machinery:
        read it to understand the runtime, do not drive it directly.
    """

    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_source_configuration_id",
        "_previous_configuration_id",
        "_created_at",
        "_reason",
        "_locked",
        "_lock",
        "_profile_name",
        "_profile_version",
        "_precision_profile_name",
        "_precision_profile_version",
        "_frame_override_ruleset",
        "_conduit_override_ruleset",
        "_spell_override_ruleset",
        "_member_override_ruleset",
    ]

    def __init__(
            self,
            *,
            profile_name: str,
            profile_version: str,
            precision_profile_name: Optional[str] = None,
            precision_profile_version: Optional[str] = None,
            frame_override_ruleset: Optional[FrameACLRuleSet] = None,
            conduit_override_ruleset: Optional[FrameACLRuleSet] = None,
            spell_override_ruleset: Optional[FrameACLRuleSet] = None,
            member_override_ruleset: Optional[FrameACLRuleSet] = None,
            source_configuration_id: Optional[str] = None,
            previous_configuration_id: Optional[str] = None,
            reason: str = "direct",
            locked: bool = True,
    ) -> None:
        """
        Initialize one applied command-side ACL configuration revision.

        Args:
            profile_name:
                Stable command-profile name.
            profile_version:
                Stable command-profile version.
            precision_profile_name:
                Optional reusable precision profile name.
            precision_profile_version:
                Optional reusable precision profile version.
            frame_override_ruleset:
                Optional frame-level command ruleset override.
            conduit_override_ruleset:
                Optional conduit-level command ruleset override.
            spell_override_ruleset:
                Optional spell-level command ruleset override.
            member_override_ruleset:
                Optional member-level command ruleset override.
            source_configuration_id:
                Source configuration id when copied from another revision.
            previous_configuration_id:
                Previous chain node id when already known.
            reason:
                Human-readable creation reason.
            locked:
                True when this revision starts finalized for chain ownership.

        Returns:
            None.
        """
        super().__init__()
        if not profile_name:
            raise ValueError("profile_name cannot be empty.")
        if not profile_version:
            raise ValueError("profile_version cannot be empty.")
        if (
                (precision_profile_name is None) !=
                (precision_profile_version is None)
        ):
            raise ValueError(
                "precision_profile_name and precision_profile_version must both be set or both be None."
            )
        if not isinstance(reason, str) or not reason:
            raise ValueError("reason cannot be empty.")

        self._id: str = IDBuilder.create_id()
        self._source_configuration_id: Optional[str] = source_configuration_id
        self._previous_configuration_id: Optional[str] = previous_configuration_id
        self._created_at: str = datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        self._reason: str = reason
        self._locked: bool = locked
        self._lock: threading.RLock = threading.RLock()
        self._profile_name: str = profile_name
        self._profile_version: str = profile_version
        self._precision_profile_name: Optional[str] = precision_profile_name
        self._precision_profile_version: Optional[str] = precision_profile_version
        self._frame_override_ruleset = self._coerce_ruleset(
            frame_override_ruleset,
            "{0}_frame_override".format(profile_name),
        )
        self._conduit_override_ruleset = self._coerce_ruleset(
            conduit_override_ruleset,
            "{0}_conduit_override".format(profile_name),
        )
        self._spell_override_ruleset = self._coerce_ruleset(
            spell_override_ruleset,
            "{0}_spell_override".format(profile_name),
        )
        self._member_override_ruleset = self._coerce_ruleset(
            member_override_ruleset,
            "{0}_member_override".format(profile_name),
        )

    @classmethod
    def create_default(
            cls,
            *,
            source_configuration_id: Optional[str] = None,
            previous_configuration_id: Optional[str] = None,
            reason: str = "default",
            locked: bool = True,
    ) -> "FrameACLCommandConfiguration":
        """
        Create the default command configuration revision.

        Args:
            source_configuration_id: Optional id of the source configuration.
            previous_configuration_id: Optional id of the prior revision.
            reason: Audit reason recorded on the configuration.
            locked: When True (default), the result is locked/immutable.

        Returns:
            FrameACLCommandConfiguration: Default command configuration.
        """
        return cls.from_profile(
            FrameACLCommandProfile.create_default(),
            source_configuration_id=source_configuration_id,
            previous_configuration_id=previous_configuration_id,
            reason=reason,
            locked=locked,
        )

    @classmethod
    def from_profile(
            cls,
            profile: FrameACLCommandProfile,
            *,
            precision_profile: Optional[FrameACLCommandProfile] = None,
            frame_override_ruleset: Optional[FrameACLRuleSet] = None,
            conduit_override_ruleset: Optional[FrameACLRuleSet] = None,
            spell_override_ruleset: Optional[FrameACLRuleSet] = None,
            member_override_ruleset: Optional[FrameACLRuleSet] = None,
            source_configuration_id: Optional[str] = None,
            previous_configuration_id: Optional[str] = None,
            reason: str = "from_profile",
            locked: bool = True,
    ) -> "FrameACLCommandConfiguration":
        """
        Build one applied command configuration from reusable profile assets.

        Args:
            profile: Source command profile to apply.
            precision_profile: Optional precision profile overlay.
            frame_override_ruleset: Optional frame-scope override rules.
            conduit_override_ruleset: Optional conduit-scope override rules.
            spell_override_ruleset: Optional spell-scope override rules.
            member_override_ruleset: Optional member-scope override rules.
            source_configuration_id: Optional id of the source configuration.
            previous_configuration_id: Optional id of the prior revision.
            reason: Audit reason recorded on the configuration.
            locked: When True (default), the result is locked/immutable.

        Returns:
            FrameACLCommandConfiguration: Applied command configuration.

        Raises:
            TypeError: If `profile` or `precision_profile` is the wrong type.
        """
        if not isinstance(profile, FrameACLCommandProfile):
            raise TypeError("profile must be a FrameACLCommandProfile instance.")
        if (
                precision_profile is not None
                and not isinstance(precision_profile, FrameACLCommandProfile)
        ):
            raise TypeError("precision_profile must be a FrameACLCommandProfile instance.")
        return cls(
            profile_name=profile.name,
            profile_version=profile.version,
            precision_profile_name=(
                precision_profile.name if precision_profile is not None else None
            ),
            precision_profile_version=(
                precision_profile.version if precision_profile is not None else None
            ),
            frame_override_ruleset=frame_override_ruleset,
            conduit_override_ruleset=conduit_override_ruleset,
            spell_override_ruleset=spell_override_ruleset,
            member_override_ruleset=member_override_ruleset,
            source_configuration_id=source_configuration_id,
            previous_configuration_id=previous_configuration_id,
            reason=reason,
            locked=locked,
        )

    @classmethod
    def from_json_dict(
            cls,
            payload: Dict[str, Any],
            *,
            source_configuration_id: Optional[str] = None,
            previous_configuration_id: Optional[str] = None,
            reason: str = "from_json",
            locked: bool = True,
    ) -> "FrameACLCommandConfiguration":
        """
        Build one applied command configuration from a JSON-compatible payload.

        Args:
            payload: JSON-compatible dict describing the configuration.
            source_configuration_id: Optional id of the source configuration.
            previous_configuration_id: Optional id of the prior revision.
            reason: Audit reason recorded on the configuration.
            locked: When True (default), the result is locked/immutable.

        Returns:
            FrameACLCommandConfiguration: Reconstructed command configuration.

        Raises:
            TypeError: If `payload` is not a dict.
        """
        if not isinstance(payload, dict):
            raise TypeError("payload must be a dict.")
        return cls(
            profile_name=payload.get("profile_name", "safe"),
            profile_version=payload.get("profile_version", "0.0.1"),
            precision_profile_name=payload.get("precision_profile_name"),
            precision_profile_version=payload.get("precision_profile_version"),
            frame_override_ruleset=FrameACLRuleSet.from_json_dict(
                payload.get(
                    "frame_override_ruleset",
                    {"name": "frame_override", "rules": []},
                )
            ),
            conduit_override_ruleset=FrameACLRuleSet.from_json_dict(
                payload.get(
                    "conduit_override_ruleset",
                    {"name": "conduit_override", "rules": []},
                )
            ),
            spell_override_ruleset=FrameACLRuleSet.from_json_dict(
                payload.get(
                    "spell_override_ruleset",
                    {"name": "spell_override", "rules": []},
                )
            ),
            member_override_ruleset=FrameACLRuleSet.from_json_dict(
                payload.get(
                    "member_override_ruleset",
                    {"name": "member_override", "rules": []},
                )
            ),
            source_configuration_id=source_configuration_id,
            previous_configuration_id=previous_configuration_id,
            reason=reason,
            locked=locked,
        )

    @classmethod
    def create_new_from_configuration(
            cls,
            source_configuration: "FrameACLCommandConfiguration",
            *,
            reason: str,
    ) -> "FrameACLCommandConfiguration":
        """
        Create one new unlocked configuration copied from an existing config.

        Args:
            source_configuration: Existing configuration to copy from.
            reason: Audit reason recorded on the new draft.

        Returns:
            FrameACLCommandConfiguration: New unlocked detached configuration copy.

        Raises:
            TypeError: If `source_configuration` is the wrong type.
        """
        if not isinstance(source_configuration, FrameACLCommandConfiguration):
            raise TypeError(
                "source_configuration must be a FrameACLCommandConfiguration."
            )
        return cls.from_json_dict(
            source_configuration.to_json_dict(),
            source_configuration_id=source_configuration.configuration_id,
            previous_configuration_id=None,
            reason=reason,
            locked=False,
        )

    def cleanup(self) -> None:
        """
        Idempotently clear the applied command configuration and overrides.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._frame_override_ruleset.cleanup()
            self._conduit_override_ruleset.cleanup()
            self._spell_override_ruleset.cleanup()
            self._member_override_ruleset.cleanup()

            del self._frame_override_ruleset
            del self._conduit_override_ruleset
            del self._spell_override_ruleset
            del self._member_override_ruleset
            del self._source_configuration_id
            del self._previous_configuration_id
            del self._created_at
            del self._reason
            del self._locked
            del self._precision_profile_name
            del self._precision_profile_version
            del self._profile_version
            del self._profile_name
            del self._id
        del self._lock

    @property
    def configuration_id(self) -> str:
        """
        Return the stable configuration-node id.

        Returns:
            str: Unique configuration id.
        """
        self.check_cleaned()
        with self._lock:
            return self._id

    @property
    def source_configuration_id(self) -> Optional[str]:
        """
        Return the source configuration id when this node was copied.

        Returns:
            Optional[str]: Source configuration id.
        """
        self.check_cleaned()
        with self._lock:
            return self._source_configuration_id

    @property
    def previous_configuration_id(self) -> Optional[str]:
        """
        Return the previous chain node id when known.

        Returns:
            Optional[str]: Previous configuration id.
        """
        self.check_cleaned()
        with self._lock:
            return self._previous_configuration_id

    @property
    def created_at(self) -> str:
        """
        Return the UTC creation timestamp string.

        Returns:
            str: ISO-8601 UTC creation timestamp.
        """
        self.check_cleaned()
        with self._lock:
            return self._created_at

    @property
    def reason(self) -> str:
        """
        Return the recorded creation reason.

        Returns:
            str: Human-readable creation reason.
        """
        self.check_cleaned()
        with self._lock:
            return self._reason

    @property
    def locked(self) -> bool:
        """
        Return whether this configuration node is finalized.

        Returns:
            bool: True when the node is locked for chain ownership.
        """
        self.check_cleaned()
        with self._lock:
            return self._locked

    @property
    def profile_name(self) -> str:
        """
        Return the command profile name that seeded this configuration.

        Returns:
            str: Command profile name.
        """
        self.check_cleaned()
        with self._lock:
            return self._profile_name

    @property
    def profile_version(self) -> str:
        """
        Return the command profile version that seeded this configuration.

        Returns:
            str: Command profile version.
        """
        self.check_cleaned()
        with self._lock:
            return self._profile_version

    @property
    def precision_profile_name(self) -> Optional[str]:
        """
        Return the optional reusable precision profile name.

        Returns:
            Optional[str]: Precision profile name when one is selected.
        """
        self.check_cleaned()
        with self._lock:
            return self._precision_profile_name

    @property
    def precision_profile_version(self) -> Optional[str]:
        """
        Return the optional reusable precision profile version.

        Returns:
            Optional[str]: Precision profile version when one is selected.
        """
        self.check_cleaned()
        with self._lock:
            return self._precision_profile_version

    @property
    def frame_override_ruleset(self) -> FrameACLRuleSet:
        """
        Return the frame-level command override ruleset.

        Returns:
            FrameACLRuleSet: Frame-level command override ruleset.
        """
        self.check_cleaned()
        with self._lock:
            return self._frame_override_ruleset

    @property
    def conduit_override_ruleset(self) -> FrameACLRuleSet:
        """
        Return the conduit-level command override ruleset.

        Returns:
            FrameACLRuleSet: Conduit-level command override ruleset.
        """
        self.check_cleaned()
        with self._lock:
            return self._conduit_override_ruleset

    @property
    def spell_override_ruleset(self) -> FrameACLRuleSet:
        """
        Return the spell-level command override ruleset.

        Returns:
            FrameACLRuleSet: Spell-level command override ruleset.
        """
        self.check_cleaned()
        with self._lock:
            return self._spell_override_ruleset

    @property
    def member_override_ruleset(self) -> FrameACLRuleSet:
        """
        Return the member-level command override ruleset.

        Returns:
            FrameACLRuleSet: Member-level command override ruleset.
        """
        self.check_cleaned()
        with self._lock:
            return self._member_override_ruleset

    def to_json_dict(self) -> Dict[str, Any]:
        """
        Return the applied command configuration as a JSON-compatible dict.

        Returns:
            Dict[str, Any]: JSON-compatible command configuration payload.
        """
        self.check_cleaned()
        with self._lock:
            return {
                "profile_name": self._profile_name,
                "profile_version": self._profile_version,
                "precision_profile_name": self._precision_profile_name,
                "precision_profile_version": self._precision_profile_version,
                "frame_override_ruleset": self._frame_override_ruleset.to_json_dict(),
                "conduit_override_ruleset": (
                    self._conduit_override_ruleset.to_json_dict()
                ),
                "spell_override_ruleset": self._spell_override_ruleset.to_json_dict(),
                "member_override_ruleset": self._member_override_ruleset.to_json_dict(),
            }

    def to_json_string(self) -> str:
        """
        Return the applied command configuration as a normalized JSON string.

        Returns:
            str: Normalized JSON payload string.
        """
        self.check_cleaned()
        return json.dumps(self.to_json_dict(), sort_keys=True)

    def clone(self) -> "FrameACLCommandConfiguration":
        """
        Return a detached copy of the applied command configuration.

        Returns:
            FrameACLCommandConfiguration: Detached configuration copy.
        """
        self.check_cleaned()
        return FrameACLCommandConfiguration.from_json_dict(
            self.to_json_dict(),
            source_configuration_id=self._source_configuration_id,
            previous_configuration_id=self._previous_configuration_id,
            reason=self._reason,
            locked=self._locked,
        )

    def set_previous_configuration_id(
            self,
            previous_configuration_id: Optional[str],
    ) -> None:
        """
        Update the previous-node pointer while the config is mutable.

        Args:
            previous_configuration_id:
                Previous configuration id or None.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            if self._locked:
                raise RuntimeError(
                    "Cannot change previous_configuration_id on a locked configuration."
                )
            self._previous_configuration_id = previous_configuration_id

    def finalize(self) -> None:
        """
        Lock this configuration node against further chain metadata mutation.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._locked = True

    def set_profiles(
            self,
            profile: FrameACLCommandProfile,
            *,
            precision_profile: Optional[FrameACLCommandProfile] = None,
    ) -> None:
        """
        Replace the base and precision profile identity while the config is mutable.

        Args:
            profile:
                Replacement base command profile.
            precision_profile:
                Optional replacement precision command profile.

        Returns:
            None.
        """
        self.check_cleaned()
        if not isinstance(profile, FrameACLCommandProfile):
            raise TypeError("profile must be a FrameACLCommandProfile instance.")
        if (
                precision_profile is not None
                and not isinstance(precision_profile, FrameACLCommandProfile)
        ):
            raise TypeError(
                "precision_profile must be a FrameACLCommandProfile instance.."
            )
        with self._lock:
            if self._locked:
                raise RuntimeError(
                    "Cannot change profiles on a locked configuration."
                )
            self._profile_name = profile.name
            self._profile_version = profile.version
            self._precision_profile_name = (
                precision_profile.name if precision_profile is not None else None
            )
            self._precision_profile_version = (
                precision_profile.version if precision_profile is not None else None
            )

    @staticmethod
    def _coerce_ruleset(
            ruleset: Optional[FrameACLRuleSet],
            default_name: str,
    ) -> FrameACLRuleSet:
        """
        Normalize one optional override ruleset input.

        Returns:
            FrameACLRuleSet: Detached existing ruleset clone or a new default.
        """
        if ruleset is None:
            return FrameACLRuleSet(default_name)
        if not isinstance(ruleset, FrameACLRuleSet):
            raise TypeError("ruleset must be a FrameACLRuleSet instance.")
        return ruleset.clone()
