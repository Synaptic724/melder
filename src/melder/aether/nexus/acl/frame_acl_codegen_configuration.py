import json
from typing import Any, Dict, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.acl.profiles.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.aether.nexus.acl.profiles.frame_acl_ruleset import (
    FrameACLRuleSet,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class FrameACLCodegenConfiguration(Cleanable):
    """
    Purpose:
        Represent the applied codegen-side ACL configuration for one frame.

    Contract:
        - Carries the reusable codegen profile identity/version it was derived from.
        - Owns detached override rulesets for frame, conduit, spell, and
          capability concerns.
        - Remains serializable for persistence.

    Lifecycle:
        Cleanup is idempotent and cascades into all owned override rulesets.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
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
    ) -> None:
        super().__init__()
        if not profile_name:
            raise ValueError("profile_name cannot be empty.")
        if not profile_version:
            raise ValueError("profile_version cannot be empty.")
        self._id: str = IDBuilder.create_id()
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
    ) -> "FrameACLCodegenConfiguration":
        if not isinstance(profile, FrameACLCodegenProfile):
            raise TypeError("profile must be a FrameACLCodegenProfile.")
        return cls(
            profile_name=profile.name,
            profile_version=profile.version,
            frame_override_ruleset=frame_override_ruleset,
            conduit_override_ruleset=conduit_override_ruleset,
            spell_override_ruleset=spell_override_ruleset,
            capability_override_ruleset=capability_override_ruleset,
        )

    @classmethod
    def from_json_dict(
            cls,
            payload: Dict[str, Any],
    ) -> "FrameACLCodegenConfiguration":
        if not isinstance(payload, dict):
            raise TypeError("payload must be a dict.")
        return cls(
            profile_name=payload.get("profile_name"),
            profile_version=payload.get("profile_version"),
            frame_override_ruleset=FrameACLRuleSet.from_json_dict(
                payload.get("frame_override_ruleset", {"name": "frame_override", "rules": []})
            ),
            conduit_override_ruleset=FrameACLRuleSet.from_json_dict(
                payload.get("conduit_override_ruleset", {"name": "conduit_override", "rules": []})
            ),
            spell_override_ruleset=FrameACLRuleSet.from_json_dict(
                payload.get("spell_override_ruleset", {"name": "spell_override", "rules": []})
            ),
            capability_override_ruleset=FrameACLRuleSet.from_json_dict(
                payload.get("capability_override_ruleset", {"name": "capability_override", "rules": []})
            ),
        )

    def cleanup(self) -> None:
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
        self._profile_version = None
        self._profile_name = None
        self._id = None

    @property
    def profile_name(self) -> str:
        self.check_cleaned()
        return self._profile_name

    @property
    def profile_version(self) -> str:
        self.check_cleaned()
        return self._profile_version

    @property
    def frame_override_ruleset(self) -> FrameACLRuleSet:
        self.check_cleaned()
        return self._frame_override_ruleset

    @property
    def conduit_override_ruleset(self) -> FrameACLRuleSet:
        self.check_cleaned()
        return self._conduit_override_ruleset

    @property
    def spell_override_ruleset(self) -> FrameACLRuleSet:
        self.check_cleaned()
        return self._spell_override_ruleset

    @property
    def capability_override_ruleset(self) -> FrameACLRuleSet:
        self.check_cleaned()
        return self._capability_override_ruleset

    def to_json_dict(self) -> Dict[str, Any]:
        self.check_cleaned()
        return {
            "profile_name": self._profile_name,
            "profile_version": self._profile_version,
            "frame_override_ruleset": self._frame_override_ruleset.to_json_dict(),
            "conduit_override_ruleset": self._conduit_override_ruleset.to_json_dict(),
            "spell_override_ruleset": self._spell_override_ruleset.to_json_dict(),
            "capability_override_ruleset": self._capability_override_ruleset.to_json_dict(),
        }

    def to_json_string(self) -> str:
        self.check_cleaned()
        return json.dumps(self.to_json_dict(), sort_keys=True)

    def clone(self) -> "FrameACLCodegenConfiguration":
        self.check_cleaned()
        return FrameACLCodegenConfiguration.from_json_dict(self.to_json_dict())

    @staticmethod
    def _coerce_ruleset(
            ruleset: Optional[FrameACLRuleSet],
            default_name: str,
    ) -> FrameACLRuleSet:
        if ruleset is None:
            return FrameACLRuleSet(default_name)
        if not isinstance(ruleset, FrameACLRuleSet):
            raise TypeError("ruleset must be a FrameACLRuleSet.")
        return ruleset
