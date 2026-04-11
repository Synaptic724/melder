import json
import threading
from typing import Any, Dict, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.acl.profiles.frame_acl_ruleset import FrameACLRuleSet
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class FrameACLCommandConfiguration(Cleanable):
    """
    Purpose:
        Represent the applied command-side ACL configuration for one frame.

    Contract:
        - Carries stable profile identity/version for the command layer.
        - Owns detached override rulesets for frame, conduit, spell, and
          member command policy.
        - Remains serializable for persistence and cloning.
        - Uses an instance lock because cleanup and grouped replacement mutate
          multiple owned fields together in a nogil runtime.
        - Is policy data only. It does not resolve targets, execute commands,
          or validate descriptor/runtime truth by itself.

    Lifecycle:
        Cleanup is idempotent and cascades into all owned rulesets before
        dropping references.

    Threading / Concurrency:
        - Uses an instance `RLock` to serialize grouped cleanup and future
          grouped mutation safely in a nogil runtime.

    Notes:
        - This object is the command-policy sibling to
          `FrameACLViewConfiguration` and `FrameACLCodegenConfiguration`.
        - The bundle selection seam still lives one level up in
          `FrameACLConfiguration`.
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
        "_member_override_ruleset",
    ]

    def __init__(
            self,
            *,
            profile_name: str,
            profile_version: str,
            frame_override_ruleset: Optional[FrameACLRuleSet] = None,
            conduit_override_ruleset: Optional[FrameACLRuleSet] = None,
            spell_override_ruleset: Optional[FrameACLRuleSet] = None,
            member_override_ruleset: Optional[FrameACLRuleSet] = None,
    ) -> None:
        """
        Initialize one applied command-side ACL configuration object.

        Args:
            profile_name:
                Stable command-profile name carried by this configuration.
            profile_version:
                Stable command-profile version carried by this configuration.
            frame_override_ruleset:
                Optional frame-level command ruleset override.
            conduit_override_ruleset:
                Optional conduit-level command ruleset override.
            spell_override_ruleset:
                Optional spell-level command ruleset override.
            member_override_ruleset:
                Optional member-level command ruleset override.

        Returns:
            None.

        Raises:
            ValueError:
                If one required profile identity field is empty.
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
        self._member_override_ruleset = self._coerce_ruleset(
            member_override_ruleset,
            "{0}_member_override".format(profile_name),
        )

    @classmethod
    def create_default(cls) -> "FrameACLCommandConfiguration":
        """
        Create the default command configuration.

        Contract:
            - Produces a stable baseline command configuration with the
              reserved default profile identity.
            - Seeds empty detached rulesets for all command-policy families.
            - Returns a new configuration object on every call.

        Returns:
            FrameACLCommandConfiguration: Default command configuration.
        """
        return cls(
            profile_name="default",
            profile_version="0.0.1",
        )

    @classmethod
    def from_json_dict(
            cls,
            payload: Dict[str, Any],
    ) -> "FrameACLCommandConfiguration":
        """
        Build one applied command configuration from a JSON-compatible payload.

        Contract:
            - Reconstructs one detached command configuration from a
              JSON-compatible dictionary.
            - Missing profile identity fields fall back to the default command
              profile in this first implementation cut.
            - Missing ruleset payloads normalize to empty detached rulesets for
              the corresponding family.

        Args:
            payload:
                JSON-compatible command configuration payload.

        Returns:
            FrameACLCommandConfiguration: Reconstructed command configuration.

        Raises:
            TypeError:
                If `payload` is not a dictionary.
        """
        if not isinstance(payload, dict):
            raise TypeError("payload must be a dict.")
        return cls(
            profile_name=payload.get("profile_name", "default"),
            profile_version=payload.get("profile_version", "0.0.1"),
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

    def cleanup(self) -> None:
        """
        Idempotently clear the applied command configuration and overrides.

        Contract:
            - Safe to call more than once.
            - Cleans all owned rulesets before dropping references.
            - Leaves the object unusable after cleanup completes.

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
            self._profile_version = None
            self._profile_name = None
            self._id = None
        self._lock = None

    @property
    def profile_name(self) -> str:
        """
        Return the command profile name that seeded this configuration.

        Contract:
            Read-only identity accessor. The returned value is stable for the
            lifetime of a live configuration object.

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

        Contract:
            Read-only identity accessor. The returned value is stable for the
            lifetime of a live configuration object.

        Returns:
            str: Command profile version.
        """
        self.check_cleaned()
        with self._lock:
            return self._profile_version

    @property
    def frame_override_ruleset(self) -> FrameACLRuleSet:
        """
        Return the frame-level command override ruleset.

        Contract:
            Returns the owned ruleset object, not a clone. Callers must treat it
            as container-owned policy state.

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

        Contract:
            Returns the owned ruleset object, not a clone. Callers must treat it
            as container-owned policy state.

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

        Contract:
            Returns the owned ruleset object, not a clone. Callers must treat it
            as container-owned policy state.

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

        Contract:
            Returns the owned ruleset object, not a clone. Callers must treat it
            as container-owned policy state.

        Returns:
            FrameACLRuleSet: Member-level command override ruleset.
        """
        self.check_cleaned()
        with self._lock:
            return self._member_override_ruleset

    def to_json_dict(self) -> Dict[str, Any]:
        """
        Return the applied command configuration as a JSON-compatible dict.

        Contract:
            - Returns a detached JSON-ready payload.
            - Does not expose live internal dictionaries directly.

        Returns:
            Dict[str, Any]: JSON-compatible command configuration payload.
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
                "member_override_ruleset": (
                    self._member_override_ruleset.to_json_dict()
                ),
            }

    def to_json_string(self) -> str:
        """
        Return the applied command configuration as a normalized JSON string.

        Contract:
            - Serializes through `to_json_dict()`.
            - Produces a stable key-sorted representation suitable for
              persistence, comparison, or cloning workflows.

        Returns:
            str: Normalized JSON payload string.
        """
        self.check_cleaned()
        return json.dumps(self.to_json_dict(), sort_keys=True)

    def clone(self) -> "FrameACLCommandConfiguration":
        """
        Return a detached copy of the applied command configuration.

        Contract:
            - Returns a deep detached copy through the JSON round-trip path.
            - The clone owns its own ruleset objects and can be mutated or
              cleaned independently of the source object.

        Returns:
            FrameACLCommandConfiguration: Detached configuration copy.
        """
        self.check_cleaned()
        return FrameACLCommandConfiguration.from_json_dict(self.to_json_dict())

    @staticmethod
    def _coerce_ruleset(
            ruleset: Optional[FrameACLRuleSet],
            default_name: str,
    ) -> FrameACLRuleSet:
        """
        Normalize one optional override ruleset input.

        Contract:
            - Missing rulesets normalize to a new empty ruleset with the
              provided default name.
            - Existing rulesets are cloned so the configuration owns detached
              policy state.

        Args:
            ruleset:
                Optional incoming override ruleset.
            default_name:
                Ruleset name used when a default ruleset must be created.

        Returns:
            FrameACLRuleSet: Detached existing ruleset clone or a new default.

        Raises:
            TypeError:
                If `ruleset` is provided but is not a `FrameACLRuleSet`.
        """
        if ruleset is None:
            return FrameACLRuleSet(default_name)
        if not isinstance(ruleset, FrameACLRuleSet):
            raise TypeError("ruleset must be a FrameACLRuleSet.")
        return ruleset.clone()
