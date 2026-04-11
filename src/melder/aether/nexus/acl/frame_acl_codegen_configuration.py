import json
import threading
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
        Represent the applied codegen-side ACL configuration for one frame.

    Contract:
        - Carries the reusable codegen profile identity/version it was derived
          from.
        - Owns detached override rulesets for frame, conduit, spell, and
          capability concerns.
        - Remains serializable for persistence.
        - Uses a lock because cleanup and grouped override replacement mutate
          multiple owned fields together in a nogil runtime.

    Lifecycle:
        Cleanup is idempotent and cascades into all owned override rulesets
        before references are cleared.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
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
    ) -> None:
        """
        Initialize one applied codegen-side ACL configuration object.

        Args:
            profile_name:
                Reusable codegen profile name that seeded this config.
            profile_version:
                Reusable codegen profile version that seeded this config.
            frame_override_ruleset:
                Optional frame-level override ruleset.
            conduit_override_ruleset:
                Optional conduit-level override ruleset.
            spell_override_ruleset:
                Optional spell-level override ruleset.
            capability_override_ruleset:
                Optional capability-level override ruleset.
        Contract:
            - Captures one applied codegen ACL bundle derived from a reusable
              profile plus optional override rulesets.
            - Normalizes every override input into a detached `FrameACLRuleSet`
              owned by this configuration object.
            - Preserves the profile identity/version used by downstream codegen
              selection and serialization flows.

        Raises:
            ValueError:
                If required identity fields are empty.
            TypeError:
                If one override ruleset has the wrong type.
        """
        super().__init__()
        if not profile_name:
            raise ValueError("profile_name cannot be empty.")
        if not profile_version:
            raise ValueError("profile_version cannot be empty.")
        self._id: str = IDBuilder.create_id()
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

    def cleanup(self) -> None:
        """
        Idempotently clear the applied codegen configuration and overrides.

        Contract:
            - Safe to call more than once.
            - Cleans all owned override rulesets before dropping references.
            - Leaves future callers to fail through `check_cleaned()`.
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
            self._profile_version = None
            self._profile_name = None
            self._id = None
        self._lock = None

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
        """
        Build one applied codegen configuration from a reusable codegen profile.

        Contract:
            - Copies profile identity from the reusable profile.
            - Normalizes the supplied override rulesets into detached owned
              rulesets on the returned configuration object.

        Args:
            profile:
                Reusable source codegen profile.
            frame_override_ruleset:
                Optional frame-level override ruleset.
            conduit_override_ruleset:
                Optional conduit-level override ruleset.
            spell_override_ruleset:
                Optional spell-level override ruleset.
            capability_override_ruleset:
                Optional capability-level override ruleset.

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
        )

    @classmethod
    def from_json_dict(
            cls,
            payload: Dict[str, Any],
    ) -> "FrameACLCodegenConfiguration":
        """
        Build one applied codegen configuration from a JSON-compatible payload.

        Contract:
            - Reconstructs a complete typed configuration object from a
              JSON-compatible dictionary.
            - Fills missing override sections with empty named rulesets so the
              returned object is still a complete bundle.

        Args:
            payload:
                JSON-compatible codegen configuration payload.

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
        )

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
                "frame_override_ruleset": (
                    self._frame_override_ruleset.to_json_dict()
                ),
                "conduit_override_ruleset": (
                    self._conduit_override_ruleset.to_json_dict()
                ),
                "spell_override_ruleset": (
                    self._spell_override_ruleset.to_json_dict()
                ),
                "capability_override_ruleset": (
                    self._capability_override_ruleset.to_json_dict()
                ),
            }

    def to_json_string(self) -> str:
        """
        Return the applied codegen configuration as a normalized JSON string.

        Contract:
            Uses `sort_keys=True` so equivalent codegen configurations produce
            the same canonical JSON text.

        Returns:
            str: Normalized JSON payload string.
        """
        self.check_cleaned()
        return json.dumps(self.to_json_dict(), sort_keys=True)

    def clone(self) -> "FrameACLCodegenConfiguration":
        """
        Return a detached copy of the applied codegen configuration.

        Contract:
            Round-trips through the JSON form so the returned object does not
            share override-ruleset ownership with the source configuration.

        Returns:
            FrameACLCodegenConfiguration: Detached configuration copy.
        """
        self.check_cleaned()
        return FrameACLCodegenConfiguration.from_json_dict(self.to_json_dict())

    @staticmethod
    def _coerce_ruleset(
            ruleset: Optional[FrameACLRuleSet],
            default_name: str,
    ) -> FrameACLRuleSet:
        """
        Normalize one optional override ruleset input.

        Contract:
            - Returns a detached clone when a ruleset is supplied.
            - Creates a default empty ruleset when the input is None.

        Args:
            ruleset:
                Optional incoming override ruleset.
            default_name:
                Ruleset name used when a default ruleset must be created.

        Returns:
            FrameACLRuleSet: Detached existing ruleset clone or a newly created
            default ruleset.
        """
        if ruleset is None:
            return FrameACLRuleSet(default_name)
        if not isinstance(ruleset, FrameACLRuleSet):
            raise TypeError("ruleset must be a FrameACLRuleSet.")
        return ruleset.clone()
