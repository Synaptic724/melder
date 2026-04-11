import json
import threading
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.acl.profiles.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.aether.nexus.acl.profiles.frame_acl_ruleset import FrameACLRuleSet
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class FrameACLCodegenConfiguration(Cleanable):
    """
    Purpose:
        Represent one applied codegen-side ACL configuration revision.

    Contract:
        - Carries reusable codegen-profile identity/version plus detached frame,
          conduit, spell, and capability override rulesets.
        - Carries revision metadata so container-owned chains can version these
          objects directly.
        - Remains serializable for persistence and detached cloning.
        - Uses an instance lock because cleanup and grouped metadata/ruleset
          mutation touch multiple owned fields in a nogil runtime.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_configuration_id",
        "_source_configuration_id",
        "_previous_configuration_id",
        "_created_at",
        "_reason",
        "_locked",
        "_lock",
        "_profile_name",
        "_profile_version",
        "_frame_override_ruleset",
        "_conduit_override_ruleset",
        "_spell_override_ruleset",
        "_capability_override_ruleset",
    ]

    def __init__(
            self,
            *,
            profile_name: str,
            profile_version: str,
            frame_override_ruleset: Optional[FrameACLRuleSet] = None,
            conduit_override_ruleset: Optional[FrameACLRuleSet] = None,
            spell_override_ruleset: Optional[FrameACLRuleSet] = None,
            capability_override_ruleset: Optional[FrameACLRuleSet] = None,
            source_configuration_id: Optional[str] = None,
            previous_configuration_id: Optional[str] = None,
            reason: str = "direct",
            locked: bool = True,
    ) -> None:
        """
        Initialize one applied codegen-side ACL configuration revision.

        Args:
            profile_name:
                Stable codegen-profile name.
            profile_version:
                Stable codegen-profile version.
            frame_override_ruleset:
                Optional frame-level override ruleset.
            conduit_override_ruleset:
                Optional conduit-level override ruleset.
            spell_override_ruleset:
                Optional spell-level override ruleset.
            capability_override_ruleset:
                Optional capability-level override ruleset.
            source_configuration_id:
                Source configuration id when copied from another revision.
            previous_configuration_id:
                Previous chain node id when already known.
            reason:
                Human-readable creation reason.
            locked:
                True when this revision starts finalized for chain ownership.
        """
        super().__init__()
        if not profile_name:
            raise ValueError("profile_name cannot be empty.")
        if not profile_version:
            raise ValueError("profile_version cannot be empty.")
        if not isinstance(reason, str) or not reason:
            raise ValueError("reason cannot be empty.")

        self._id: str = IDBuilder.create_id()
        self._configuration_id: str = IDBuilder.create_id()
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
        self._capability_override_ruleset = self._coerce_ruleset(
            capability_override_ruleset,
            "{0}_capability_override".format(profile_name),
        )

    @classmethod
    def from_profile(
            cls,
            profile: FrameACLCodegenProfile,
            *,
            frame_override_ruleset: Optional[FrameACLRuleSet] = None,
            conduit_override_ruleset: Optional[FrameACLRuleSet] = None,
            spell_override_ruleset: Optional[FrameACLRuleSet] = None,
            capability_override_ruleset: Optional[FrameACLRuleSet] = None,
            source_configuration_id: Optional[str] = None,
            previous_configuration_id: Optional[str] = None,
            reason: str = "from_profile",
            locked: bool = True,
    ) -> "FrameACLCodegenConfiguration":
        """
        Build one applied codegen configuration from a reusable profile.

        Returns:
            FrameACLCodegenConfiguration: Applied codegen configuration.
        """
        if not isinstance(profile, FrameACLCodegenProfile):
            raise TypeError("profile must be a FrameACLCodegenProfile.")
        return cls(
            profile_name=profile.name,
            profile_version=profile.version,
            frame_override_ruleset=frame_override_ruleset,
            conduit_override_ruleset=conduit_override_ruleset,
            spell_override_ruleset=spell_override_ruleset,
            capability_override_ruleset=capability_override_ruleset,
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
    ) -> "FrameACLCodegenConfiguration":
        """
        Build one applied codegen configuration from a JSON-compatible payload.

        Returns:
            FrameACLCodegenConfiguration: Reconstructed applied codegen config.
        """
        if not isinstance(payload, dict):
            raise TypeError("payload must be a dict.")
        return cls(
            profile_name=payload.get("profile_name"),
            profile_version=payload.get("profile_version"),
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
            capability_override_ruleset=FrameACLRuleSet.from_json_dict(
                payload.get(
                    "capability_override_ruleset",
                    {"name": "capability_override", "rules": []},
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
            source_configuration: "FrameACLCodegenConfiguration",
            *,
            reason: str,
    ) -> "FrameACLCodegenConfiguration":
        """
        Create one new unlocked configuration copied from an existing config.

        Returns:
            FrameACLCodegenConfiguration: New unlocked detached configuration copy.
        """
        if not isinstance(source_configuration, FrameACLCodegenConfiguration):
            raise TypeError(
                "source_configuration must be a FrameACLCodegenConfiguration."
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
        Idempotently clear the applied codegen configuration and overrides.

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
            self._capability_override_ruleset.cleanup()
            self._frame_override_ruleset = None
            self._conduit_override_ruleset = None
            self._spell_override_ruleset = None
            self._capability_override_ruleset = None
            self._configuration_id = None
            self._source_configuration_id = None
            self._previous_configuration_id = None
            self._created_at = None
            self._reason = None
            self._locked = None
            self._profile_version = None
            self._profile_name = None
            self._id = None
        self._lock = None

    @property
    def configuration_id(self) -> str:
        """
        Return the stable configuration-node id.

        Returns:
            str: Unique configuration id.
        """
        self.check_cleaned()
        with self._lock:
            return self._configuration_id

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
        Return the reusable codegen profile name that seeded this config.

        Returns:
            str: Reusable codegen profile name.
        """
        self.check_cleaned()
        with self._lock:
            return self._profile_name

    @property
    def profile_version(self) -> str:
        """
        Return the reusable codegen profile version that seeded this config.

        Returns:
            str: Reusable codegen profile version.
        """
        self.check_cleaned()
        with self._lock:
            return self._profile_version

    @property
    def frame_override_ruleset(self) -> FrameACLRuleSet:
        """
        Return the frame-level override ruleset.

        Returns:
            FrameACLRuleSet: Frame-level override ruleset.
        """
        self.check_cleaned()
        with self._lock:
            return self._frame_override_ruleset

    @property
    def conduit_override_ruleset(self) -> FrameACLRuleSet:
        """
        Return the conduit-level override ruleset.

        Returns:
            FrameACLRuleSet: Conduit-level override ruleset.
        """
        self.check_cleaned()
        with self._lock:
            return self._conduit_override_ruleset

    @property
    def spell_override_ruleset(self) -> FrameACLRuleSet:
        """
        Return the spell-level override ruleset.

        Returns:
            FrameACLRuleSet: Spell-level override ruleset.
        """
        self.check_cleaned()
        with self._lock:
            return self._spell_override_ruleset

    @property
    def capability_override_ruleset(self) -> FrameACLRuleSet:
        """
        Return the capability-level override ruleset.

        Returns:
            FrameACLRuleSet: Capability-level override ruleset.
        """
        self.check_cleaned()
        with self._lock:
            return self._capability_override_ruleset

    def to_json_dict(self) -> Dict[str, Any]:
        """
        Return the applied codegen configuration as a JSON-compatible dict.

        Returns:
            Dict[str, Any]: JSON-compatible codegen configuration payload.
        """
        self.check_cleaned()
        with self._lock:
            return {
                "profile_name": self._profile_name,
                "profile_version": self._profile_version,
                "frame_override_ruleset": self._frame_override_ruleset.to_json_dict(),
                "conduit_override_ruleset": (
                    self._conduit_override_ruleset.to_json_dict()
                ),
                "spell_override_ruleset": self._spell_override_ruleset.to_json_dict(),
                "capability_override_ruleset": (
                    self._capability_override_ruleset.to_json_dict()
                ),
            }

    def to_json_string(self) -> str:
        """
        Return the applied codegen configuration as a normalized JSON string.

        Returns:
            str: Normalized JSON payload string.
        """
        self.check_cleaned()
        return json.dumps(self.to_json_dict(), sort_keys=True)

    def clone(self) -> "FrameACLCodegenConfiguration":
        """
        Return a detached copy of the applied codegen configuration.

        Returns:
            FrameACLCodegenConfiguration: Detached configuration copy.
        """
        self.check_cleaned()
        return FrameACLCodegenConfiguration.from_json_dict(
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

    @staticmethod
    def _coerce_ruleset(
            ruleset: Optional[FrameACLRuleSet],
            default_name: str,
    ) -> FrameACLRuleSet:
        """
        Normalize one optional override ruleset input.

        Returns:
            FrameACLRuleSet: Detached existing ruleset clone or a newly created
            default ruleset.
        """
        if ruleset is None:
            return FrameACLRuleSet(default_name)
        if not isinstance(ruleset, FrameACLRuleSet):
            raise TypeError("ruleset must be a FrameACLRuleSet.")
        return ruleset.clone()
