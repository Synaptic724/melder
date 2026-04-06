import json
import threading
from typing import Any, Dict, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.acl.profiles.frame_acl_ruleset import FrameACLRuleSet
from melder.aether.nexus.acl.profiles.frame_acl_view_profile import (
    FrameACLViewProfile,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class FrameACLViewConfiguration(Cleanable):
    """
    Purpose:
        Represent the applied view-side ACL configuration for one frame.

    Contract:
        - Carries the reusable view profile identity/version it was derived
          from.
        - Carries the required frame and conduit payload contracts.
        - Owns detached override rulesets for frame, conduit, spell, and
          member concerns.
        - Remains serializable for persistence through `to_json_dict()` and
          `to_json_string()`.
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
        "_required_frame_payload_profile_name",
        "_required_frame_payload_profile_version",
        "_required_conduit_payload_profile_name",
        "_required_conduit_payload_profile_version",
        "_minimum_spell_payload_profile_name",
        "_minimum_spell_payload_profile_version",
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
            minimum_spell_payload_profile_name: str,
            required_frame_payload_profile_name: str = "frame",
            required_frame_payload_profile_version: str = "0.0.1",
            required_conduit_payload_profile_name: str = "conduit",
            required_conduit_payload_profile_version: str = "0.0.1",
            minimum_spell_payload_profile_version: str = "0.0.1",
            frame_override_ruleset: Optional[FrameACLRuleSet] = None,
            conduit_override_ruleset: Optional[FrameACLRuleSet] = None,
            spell_override_ruleset: Optional[FrameACLRuleSet] = None,
            member_override_ruleset: Optional[FrameACLRuleSet] = None,
    ) -> None:
        """
        Initialize one applied view-side ACL configuration object.

        Args:
            profile_name:
                Reusable view profile name that seeded this config.
            profile_version:
                Reusable view profile version that seeded this config.
            required_frame_payload_profile_name:
                Required frame descriptor payload family name.
            required_frame_payload_profile_version:
                Required frame descriptor payload contract version.
            required_conduit_payload_profile_name:
                Required conduit descriptor payload family name.
            required_conduit_payload_profile_version:
                Required conduit descriptor payload contract version.
            minimum_spell_payload_profile_name:
                Minimum spell payload floor required for richer member rules.
            minimum_spell_payload_profile_version:
                Minimum spell payload contract version required for richer
                spell/member view rules.
            frame_override_ruleset:
                Optional frame-level override ruleset.
            conduit_override_ruleset:
                Optional conduit-level override ruleset.
            spell_override_ruleset:
                Optional spell-level override ruleset.
            member_override_ruleset:
                Optional member-level override ruleset.

        Returns:
            None.

        Raises:
            ValueError:
                If required identity/floor fields are empty.
            TypeError:
                If one override ruleset has the wrong type.
        """
        super().__init__()
        if not profile_name:
            raise ValueError("profile_name cannot be empty.")
        if not profile_version:
            raise ValueError("profile_version cannot be empty.")
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
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._profile_name: str = profile_name
        self._profile_version: str = profile_version
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

    def cleanup(self) -> None:
        """
        Idempotently clear the applied view configuration and its overrides.

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
            self._frame_override_ruleset = None
            self._conduit_override_ruleset = None
            self._spell_override_ruleset = None
            self._member_override_ruleset = None
            self._required_frame_payload_profile_name = None
            self._required_frame_payload_profile_version = None
            self._required_conduit_payload_profile_name = None
            self._required_conduit_payload_profile_version = None
            self._minimum_spell_payload_profile_name = None
            self._minimum_spell_payload_profile_version = None
            self._profile_version = None
            self._profile_name = None
            self._id = None
        self._lock = None

    @classmethod
    def from_profile(
            cls,
            profile: FrameACLViewProfile,
            *,
            frame_override_ruleset: Optional[FrameACLRuleSet] = None,
            conduit_override_ruleset: Optional[FrameACLRuleSet] = None,
            spell_override_ruleset: Optional[FrameACLRuleSet] = None,
            member_override_ruleset: Optional[FrameACLRuleSet] = None,
    ) -> "FrameACLViewConfiguration":
        """
        Build one applied view configuration from a reusable view profile.

        Args:
            profile:
                Reusable source view profile.
            frame_override_ruleset:
                Optional frame-level override ruleset.
            conduit_override_ruleset:
                Optional conduit-level override ruleset.
            spell_override_ruleset:
                Optional spell-level override ruleset.
            member_override_ruleset:
                Optional member-level override ruleset.

        Returns:
            FrameACLViewConfiguration: Applied view configuration.
        """
        if not isinstance(profile, FrameACLViewProfile):
            raise TypeError("profile must be a FrameACLViewProfile.")
        return cls(
            profile_name=profile.name,
            profile_version=profile.version,
            required_frame_payload_profile_name=(
                profile.required_frame_payload_profile_name
            ),
            required_frame_payload_profile_version=(
                profile.required_frame_payload_profile_version
            ),
            required_conduit_payload_profile_name=(
                profile.required_conduit_payload_profile_name
            ),
            required_conduit_payload_profile_version=(
                profile.required_conduit_payload_profile_version
            ),
            minimum_spell_payload_profile_name=(
                profile.minimum_spell_payload_profile_name
            ),
            minimum_spell_payload_profile_version=(
                profile.minimum_spell_payload_profile_version
            ),
            frame_override_ruleset=frame_override_ruleset,
            conduit_override_ruleset=conduit_override_ruleset,
            spell_override_ruleset=spell_override_ruleset,
            member_override_ruleset=member_override_ruleset,
        )

    @classmethod
    def from_json_dict(
            cls,
            payload: Dict[str, Any],
    ) -> "FrameACLViewConfiguration":
        """
        Build one applied view configuration from a JSON-compatible payload.

        Args:
            payload:
                JSON-compatible view configuration payload.

        Returns:
            FrameACLViewConfiguration: Reconstructed applied view configuration.
        """
        if not isinstance(payload, dict):
            raise TypeError("payload must be a dict.")
        return cls(
            profile_name=payload.get("profile_name"),
            profile_version=payload.get("profile_version"),
            required_frame_payload_profile_name=payload.get(
                "required_frame_payload_profile_name",
                "frame",
            ),
            required_frame_payload_profile_version=payload.get(
                "required_frame_payload_profile_version",
                "0.0.1",
            ),
            required_conduit_payload_profile_name=payload.get(
                "required_conduit_payload_profile_name",
                "conduit",
            ),
            required_conduit_payload_profile_version=payload.get(
                "required_conduit_payload_profile_version",
                "0.0.1",
            ),
            minimum_spell_payload_profile_name=(
                payload.get("minimum_spell_payload_profile_name")
            ),
            minimum_spell_payload_profile_version=payload.get(
                "minimum_spell_payload_profile_version",
                "0.0.1",
            ),
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
        )

    @property
    def profile_name(self) -> str:
        """
        Return the reusable view profile name that seeded this config.

        Returns:
            str: Reusable view profile name.
        """
        self.check_cleaned()
        with self._lock:
            return self._profile_name

    @property
    def profile_version(self) -> str:
        """
        Return the reusable view profile version that seeded this config.

        Returns:
            str: Reusable view profile version.
        """
        self.check_cleaned()
        with self._lock:
            return self._profile_version

    @property
    def required_frame_payload_profile_name(self) -> str:
        """
        Return the required frame descriptor payload family name.

        Returns:
            str: Required frame descriptor payload family name.
        """
        self.check_cleaned()
        with self._lock:
            return self._required_frame_payload_profile_name

    @property
    def required_frame_payload_profile_version(self) -> str:
        """
        Return the required frame descriptor payload contract version.

        Returns:
            str: Required frame descriptor payload contract version.
        """
        self.check_cleaned()
        with self._lock:
            return self._required_frame_payload_profile_version

    @property
    def required_conduit_payload_profile_name(self) -> str:
        """
        Return the required conduit descriptor payload family name.

        Returns:
            str: Required conduit descriptor payload family name.
        """
        self.check_cleaned()
        with self._lock:
            return self._required_conduit_payload_profile_name

    @property
    def required_conduit_payload_profile_version(self) -> str:
        """
        Return the required conduit descriptor payload contract version.

        Returns:
            str: Required conduit descriptor payload contract version.
        """
        self.check_cleaned()
        with self._lock:
            return self._required_conduit_payload_profile_version

    @property
    def minimum_spell_payload_profile_name(self) -> str:
        """
        Return the minimum spell payload floor for this config.

        Returns:
            str: Minimum spell payload floor name.
        """
        self.check_cleaned()
        with self._lock:
            return self._minimum_spell_payload_profile_name

    @property
    def minimum_spell_payload_profile_version(self) -> str:
        """
        Return the minimum spell payload contract version for this config.

        Returns:
            str: Minimum spell payload contract version.
        """
        self.check_cleaned()
        with self._lock:
            return self._minimum_spell_payload_profile_version

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
    def member_override_ruleset(self) -> FrameACLRuleSet:
        """
        Return the member-level override ruleset.

        Returns:
            FrameACLRuleSet: Member-level override ruleset.
        """
        self.check_cleaned()
        with self._lock:
            return self._member_override_ruleset

    def to_json_dict(self) -> Dict[str, Any]:
        """
        Return the applied view configuration as a JSON-compatible dictionary.

        Returns:
            Dict[str, Any]: JSON-compatible view configuration payload.
        """
        self.check_cleaned()
        with self._lock:
            return {
                "profile_name": self._profile_name,
                "profile_version": self._profile_version,
                "required_frame_payload_profile_name": (
                    self._required_frame_payload_profile_name
                ),
                "required_frame_payload_profile_version": (
                    self._required_frame_payload_profile_version
                ),
                "required_conduit_payload_profile_name": (
                    self._required_conduit_payload_profile_name
                ),
                "required_conduit_payload_profile_version": (
                    self._required_conduit_payload_profile_version
                ),
                "minimum_spell_payload_profile_name": (
                    self._minimum_spell_payload_profile_name
                ),
                "minimum_spell_payload_profile_version": (
                    self._minimum_spell_payload_profile_version
                ),
                "frame_override_ruleset": (
                    self._frame_override_ruleset.to_json_dict()
                ),
                "conduit_override_ruleset": (
                    self._conduit_override_ruleset.to_json_dict()
                ),
                "spell_override_ruleset": (
                    self._spell_override_ruleset.to_json_dict()
                ),
                "member_override_ruleset": (
                    self._member_override_ruleset.to_json_dict()
                ),
            }

    def to_json_string(self) -> str:
        """
        Return the applied view configuration as a normalized JSON string.

        Returns:
            str: Normalized JSON payload string.
        """
        self.check_cleaned()
        return json.dumps(self.to_json_dict(), sort_keys=True)

    def clone(self) -> "FrameACLViewConfiguration":
        """
        Return a detached copy of the applied view configuration.

        Returns:
            FrameACLViewConfiguration: Detached configuration copy.
        """
        self.check_cleaned()
        return FrameACLViewConfiguration.from_json_dict(self.to_json_dict())

    @staticmethod
    def _coerce_ruleset(
            ruleset: Optional[FrameACLRuleSet],
            default_name: str,
    ) -> FrameACLRuleSet:
        """
        Normalize one optional override ruleset input.

        Args:
            ruleset:
                Optional incoming override ruleset.
            default_name:
                Ruleset name used when a default ruleset must be created.

        Returns:
            FrameACLRuleSet: Existing or newly created ruleset.
        """
        if ruleset is None:
            return FrameACLRuleSet(default_name)
        if not isinstance(ruleset, FrameACLRuleSet):
            raise TypeError("ruleset must be a FrameACLRuleSet.")
        return ruleset
