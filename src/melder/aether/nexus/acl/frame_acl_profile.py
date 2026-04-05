import json
import threading
from typing import Any, Dict, List, Optional, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class ViewACLDetails(Cleanable):
    """
    Purpose:
        Hold the placeholder serialized view-ACL details for one ACL profile
        strategy entry.

    Contract:
        - Owns one normalized JSON payload string.
        - Exposes parsed and serialized views of that payload.
        - Can be reused by `FrameACLProfile` strategies without introducing
          live ACL-application logic yet.

    Threading:
        Uses one instance `threading.RLock` to serialize payload mutation and
        cleanup.

    Lifecycle:
        Cleanup is idempotent and clears id, lock, and payload references.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_normalized_json_payload_string",
    ]

    def __init__(
            self,
            json_payload_string: str = "{}",
    ) -> None:
        """
        Initialize one view ACL details object.

        Purpose:
            Create the placeholder holder for serialized view-ACL profile
            details.

        Contract:
            - Payload is normalized into sorted-key JSON on construction.
            - Empty/default construction produces the normalized empty-object
              payload.

        Args:
            json_payload_string:
                JSON payload string to normalize and store.

        Returns:
            None.

        Raises:
            TypeError:
                If `json_payload_string` is not a string.
            ValueError:
                If the payload is not valid JSON.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._normalized_json_payload_string: str = self._normalize_json_payload(
            json_payload_string
        )

    def cleanup(self) -> None:
        """
        Idempotently clear the details object.

        Purpose:
            Tear down the placeholder details holder and release its payload.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._normalized_json_payload_string = None
            self._id = None
        self._lock = None

    @property
    def id(self) -> str:
        """
        Return the stable details-object identifier.

        Returns:
            str: Stable details-object id.
        """
        self.check_cleaned()
        return self._id

    @property
    def normalized_json_payload_string(self) -> str:
        """
        Return the canonical normalized JSON payload string.

        Returns:
            str: Normalized JSON payload string.
        """
        self.check_cleaned()
        with self._lock:
            return self._normalized_json_payload_string

    def set_json_payload_string(
            self,
            json_payload_string: str,
    ) -> None:
        """
        Replace the serialized view-ACL payload.

        Args:
            json_payload_string:
                JSON payload string to normalize and store.

        Returns:
            None.

        Raises:
            TypeError:
                If `json_payload_string` is not a string.
            ValueError:
                If the payload is not valid JSON.
        """
        self.check_cleaned()
        normalized_json_payload_string = self._normalize_json_payload(
            json_payload_string
        )
        with self._lock:
            self._normalized_json_payload_string = normalized_json_payload_string

    def to_json_dict(self) -> Dict[str, Any]:
        """
        Return the stored payload as a detached JSON-compatible dictionary.

        Returns:
            Dict[str, Any]: Parsed payload dictionary.
        """
        self.check_cleaned()
        return json.loads(self.normalized_json_payload_string)

    def to_json_string(self) -> str:
        """
        Return the canonical normalized payload string.

        Returns:
            str: Normalized payload string.
        """
        self.check_cleaned()
        return self.normalized_json_payload_string

    @staticmethod
    def _normalize_json_payload(json_payload_string: str) -> str:
        """
        Normalize one JSON payload into stable sorted-key string form.

        Args:
            json_payload_string:
                JSON payload string to normalize.

        Returns:
            str: Canonical normalized JSON string.

        Raises:
            TypeError:
                If `json_payload_string` is not a string.
            ValueError:
                If the payload is not valid JSON.
        """
        if not isinstance(json_payload_string, str):
            raise TypeError("json_payload_string must be a string.")
        try:
            parsed_payload = json.loads(json_payload_string)
        except json.JSONDecodeError as exc:
            raise ValueError("json_payload_string must be valid JSON.") from exc
        return json.dumps(parsed_payload, sort_keys=True)


class CodegenACLDetails(Cleanable):
    """
    Purpose:
        Hold the placeholder serialized codegen-ACL details for one ACL profile
        strategy entry.

    Contract:
        - Owns one normalized JSON payload string.
        - Exposes parsed and serialized views of that payload.
        - Can be reused by `FrameACLProfile` strategies without introducing
          live ACL-application logic yet.

    Threading:
        Uses one instance `threading.RLock` to serialize payload mutation and
        cleanup.

    Lifecycle:
        Cleanup is idempotent and clears id, lock, and payload references.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_normalized_json_payload_string",
    ]

    def __init__(
            self,
            json_payload_string: str = "{}",
    ) -> None:
        """
        Initialize one codegen ACL details object.

        Purpose:
            Create the placeholder holder for serialized codegen-ACL profile
            details.

        Contract:
            - Payload is normalized into sorted-key JSON on construction.
            - Empty/default construction produces the normalized empty-object
              payload.

        Args:
            json_payload_string:
                JSON payload string to normalize and store.

        Returns:
            None.

        Raises:
            TypeError:
                If `json_payload_string` is not a string.
            ValueError:
                If the payload is not valid JSON.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._normalized_json_payload_string: str = self._normalize_json_payload(
            json_payload_string
        )

    def cleanup(self) -> None:
        """
        Idempotently clear the details object.

        Purpose:
            Tear down the placeholder details holder and release its payload.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._normalized_json_payload_string = None
            self._id = None
        self._lock = None

    @property
    def id(self) -> str:
        """
        Return the stable details-object identifier.

        Returns:
            str: Stable details-object id.
        """
        self.check_cleaned()
        return self._id

    @property
    def normalized_json_payload_string(self) -> str:
        """
        Return the canonical normalized JSON payload string.

        Returns:
            str: Normalized JSON payload string.
        """
        self.check_cleaned()
        with self._lock:
            return self._normalized_json_payload_string

    def set_json_payload_string(
            self,
            json_payload_string: str,
    ) -> None:
        """
        Replace the serialized codegen-ACL payload.

        Args:
            json_payload_string:
                JSON payload string to normalize and store.

        Returns:
            None.

        Raises:
            TypeError:
                If `json_payload_string` is not a string.
            ValueError:
                If the payload is not valid JSON.
        """
        self.check_cleaned()
        normalized_json_payload_string = self._normalize_json_payload(
            json_payload_string
        )
        with self._lock:
            self._normalized_json_payload_string = normalized_json_payload_string

    def to_json_dict(self) -> Dict[str, Any]:
        """
        Return the stored payload as a detached JSON-compatible dictionary.

        Returns:
            Dict[str, Any]: Parsed payload dictionary.
        """
        self.check_cleaned()
        return json.loads(self.normalized_json_payload_string)

    def to_json_string(self) -> str:
        """
        Return the canonical normalized payload string.

        Returns:
            str: Normalized payload string.
        """
        self.check_cleaned()
        return self.normalized_json_payload_string

    @staticmethod
    def _normalize_json_payload(json_payload_string: str) -> str:
        """
        Normalize one JSON payload into stable sorted-key string form.

        Args:
            json_payload_string:
                JSON payload string to normalize.

        Returns:
            str: Canonical normalized JSON string.

        Raises:
            TypeError:
                If `json_payload_string` is not a string.
            ValueError:
                If the payload is not valid JSON.
        """
        if not isinstance(json_payload_string, str):
            raise TypeError("json_payload_string must be a string.")
        try:
            parsed_payload = json.loads(json_payload_string)
        except json.JSONDecodeError as exc:
            raise ValueError("json_payload_string must be valid JSON.") from exc
        return json.dumps(parsed_payload, sort_keys=True)


class FrameACLRule(Cleanable):
    """
    Purpose:
        Represent one typed ACL rule used by reusable view/codegen profiles.

    Contract:
        - Rule identity is stable for the lifetime of the object.
        - `rule_name`, `operation`, and `effect` are required and non-empty.
        - `effect` must be `allow` or `deny`.
        - `conditions` is stored as a detached mapping.

    Lifecycle:
        Cleanup is idempotent and clears all owned rule metadata.
    """

    __melder_internal__ = _mrg.sentinel
    _ALLOW_EFFECT = "allow"
    _DENY_EFFECT = "deny"
    _VALID_EFFECTS = (_ALLOW_EFFECT, _DENY_EFFECT)
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_rule_name",
        "_operation",
        "_effect",
        "_conditions",
    ]

    def __init__(
            self,
            *,
            rule_name: str,
            operation: str,
            effect: str,
            conditions: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize one typed ACL rule.

        Args:
            rule_name:
                Stable rule name within an owning ruleset.
            operation:
                Rule operation name.
            effect:
                Rule effect. Must be `allow` or `deny`.
            conditions:
                Optional detached condition payload carried by the rule.

        Returns:
            None.
        """
        super().__init__()
        if not rule_name:
            raise ValueError("rule_name cannot be empty.")
        if not operation:
            raise ValueError("operation cannot be empty.")
        if effect not in self._VALID_EFFECTS:
            raise ValueError(
                "effect must be one of: {0}.".format(
                    ", ".join(self._VALID_EFFECTS),
                )
            )
        if conditions is not None and not isinstance(conditions, dict):
            raise TypeError("conditions must be a dict when provided.")
        self._id: str = IDBuilder.create_id()
        self._rule_name: str = rule_name
        self._operation: str = operation
        self._effect: str = effect
        self._conditions: Dict[str, Any] = (
            dict(conditions) if conditions is not None else {}
        )

    def cleanup(self) -> None:
        """
        Idempotently clear the rule.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        if self._conditions is not None:
            self._conditions.clear()
        self._rule_name = None
        self._operation = None
        self._effect = None
        self._conditions = None
        self._id = None

    @property
    def id(self) -> str:
        """
        Return the stable rule identifier.

        Returns:
            str: Stable rule id.
        """
        self.check_cleaned()
        return self._id

    @property
    def rule_name(self) -> str:
        """
        Return the stable rule name.

        Returns:
            str: Stable rule name.
        """
        self.check_cleaned()
        return self._rule_name

    @property
    def operation(self) -> str:
        """
        Return the rule operation.

        Returns:
            str: Rule operation.
        """
        self.check_cleaned()
        return self._operation

    @property
    def effect(self) -> str:
        """
        Return the rule effect.

        Returns:
            str: Rule effect.
        """
        self.check_cleaned()
        return self._effect

    @property
    def conditions(self) -> Dict[str, Any]:
        """
        Return a detached snapshot of rule conditions.

        Returns:
            Dict[str, Any]: Detached condition snapshot.
        """
        self.check_cleaned()
        return dict(self._conditions)


class FrameACLRuleSet(Cleanable):
    """
    Purpose:
        Hold one named collection of typed ACL rules.

    Contract:
        - Rules are stored by `rule_name`.
        - Re-registering a name replaces and cleans the older rule.
        - Returned registry snapshots are detached from future mutation.

    Threading:
        Uses one instance `threading.RLock` to serialize rule-map mutation and
        cleanup.

    Lifecycle:
        Cleanup is idempotent and cascades into all owned rules.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_name",
        "_rules_by_name",
    ]

    def __init__(
            self,
            name: str,
            rules: Optional[List[FrameACLRule]] = None,
    ) -> None:
        """
        Initialize one named ACL ruleset.

        Args:
            name:
                Stable ruleset name.
            rules:
                Optional initial rules to own.

        Returns:
            None.
        """
        super().__init__()
        if not name:
            raise ValueError("name cannot be empty.")
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._name: str = name
        self._rules_by_name: Dict[str, FrameACLRule] = {}
        if rules is not None:
            for rule in rules:
                self.register_rule(rule)

    def cleanup(self) -> None:
        """
        Idempotently clear the ruleset and owned rules.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            for rule in self._rules_by_name.values():
                rule.cleanup()
            self._rules_by_name.clear()
            self._rules_by_name = None
            self._name = None
            self._id = None
        self._lock = None

    @property
    def name(self) -> str:
        """
        Return the stable ruleset name.

        Returns:
            str: Stable ruleset name.
        """
        self.check_cleaned()
        return self._name

    @property
    def rules_by_name(self) -> Dict[str, FrameACLRule]:
        """
        Return a detached snapshot of the rule registry.

        Returns:
            Dict[str, FrameACLRule]: Detached rule-registry snapshot.
        """
        self.check_cleaned()
        with self._lock:
            return dict(self._rules_by_name)

    def list_rule_names(self) -> List[str]:
        """
        Return current rule names in insertion order.

        Returns:
            List[str]: Current rule names.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._rules_by_name.keys())

    def get_required_rule(self, rule_name: str) -> FrameACLRule:
        """
        Return one existing rule or raise.

        Args:
            rule_name:
                Rule name to resolve.

        Returns:
            FrameACLRule: Existing rule.
        """
        self.check_cleaned()
        with self._lock:
            try:
                return self._rules_by_name[rule_name]
            except KeyError as exc:
                raise KeyError(rule_name) from exc

    def register_rule(self, rule: FrameACLRule) -> None:
        """
        Register or replace one rule in the ruleset.

        Args:
            rule:
                Rule object to store by its own name.

        Returns:
            None.
        """
        self.check_cleaned()
        if not isinstance(rule, FrameACLRule):
            raise TypeError("rule must be a FrameACLRule.")
        with self._lock:
            existing = self._rules_by_name.get(rule.rule_name)
            if existing is not None and existing is not rule:
                existing.cleanup()
            self._rules_by_name[rule.rule_name] = rule

    def remove_rule(self, rule_name: str) -> bool:
        """
        Remove one rule from the ruleset.

        Args:
            rule_name:
                Rule name to remove.

        Returns:
            bool: True when the rule existed and was removed.
        """
        self.check_cleaned()
        with self._lock:
            rule = self._rules_by_name.pop(rule_name, None)
            if rule is None:
                return False
            rule.cleanup()
            return True


class FrameACLViewProfile(Cleanable):
    """
    Purpose:
        Hold one reusable typed view-profile ruleset bundle.

    Contract:
        - Owns frame, conduit, spell, and member rulesets.
        - Carries the minimum spell payload floor required for richer member
          rules.
        - Cleanup is idempotent and cascades into all owned rulesets.
    """

    __melder_internal__ = _mrg.sentinel
    _SAFE_PROFILE_NAME = "safe"
    _HYBRID_PROFILE_NAME = "hybrid"
    _PERMISSIVE_PROFILE_NAME = "permissive"
    _DEFAULT_PROFILE_NAME = _SAFE_PROFILE_NAME
    _DEFAULT_SPELL_PAYLOAD_PROFILE_NAME = "detailed"
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_version",
        "_name",
        "_minimum_spell_payload_profile_name",
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
            frame_ruleset: Optional[FrameACLRuleSet] = None,
            conduit_ruleset: Optional[FrameACLRuleSet] = None,
            spell_ruleset: Optional[FrameACLRuleSet] = None,
            member_ruleset: Optional[FrameACLRuleSet] = None,
    ) -> None:
        super().__init__()
        if not name:
            raise ValueError("name cannot be empty.")
        if not minimum_spell_payload_profile_name:
            raise ValueError(
                "minimum_spell_payload_profile_name cannot be empty."
            )
        self._id: str = IDBuilder.create_id()
        self._version: str = "0.0.1"
        self._name: str = name
        self._minimum_spell_payload_profile_name = (
            minimum_spell_payload_profile_name
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

    @classmethod
    def create_default(cls) -> "FrameACLViewProfile":
        return cls.create_safe()

    @classmethod
    def create_safe(cls) -> "FrameACLViewProfile":
        """
        Create the restrictive reusable view profile.

        Returns:
            FrameACLViewProfile: Safe reusable view profile.
        """
        return cls(
            cls._SAFE_PROFILE_NAME,
            minimum_spell_payload_profile_name=(
                cls._DEFAULT_SPELL_PAYLOAD_PROFILE_NAME
            ),
            frame_ruleset=cls._build_ruleset(
                "{0}_frame".format(cls._SAFE_PROFILE_NAME),
                [
                    cls._build_rule("frame_visible", "visible", "allow"),
                    cls._build_rule("frame_show_payload", "show_payload", "allow"),
                ],
            ),
            conduit_ruleset=cls._build_ruleset(
                "{0}_conduit".format(cls._SAFE_PROFILE_NAME),
                [
                    cls._build_rule("conduit_visible", "visible", "allow"),
                    cls._build_rule("conduit_show_payload", "show_payload", "allow"),
                    cls._build_rule("conduit_hide_policy", "show_policy", "deny"),
                    cls._build_rule("conduit_hide_peer_links", "show_peer_links", "deny"),
                ],
            ),
            spell_ruleset=cls._build_ruleset(
                "{0}_spell".format(cls._SAFE_PROFILE_NAME),
                [
                    cls._build_rule("spell_visible", "visible", "allow"),
                    cls._build_rule(
                        "spell_show_binding_payload",
                        "show_binding_payload",
                        "allow",
                    ),
                    cls._build_rule(
                        "spell_show_resolution_payload",
                        "show_resolution_payload",
                        "allow",
                    ),
                    cls._build_rule("spell_show_metadata", "show_metadata", "allow"),
                    cls._build_rule(
                        "spell_hide_class_profile",
                        "show_class_profile",
                        "deny",
                    ),
                    cls._build_rule(
                        "spell_hide_callable_profile",
                        "show_callable_profile",
                        "deny",
                    ),
                    cls._build_rule(
                        "spell_hide_instance_members",
                        "show_instance_members",
                        "deny",
                    ),
                    cls._build_rule(
                        "spell_hide_dynamic_access",
                        "show_dynamic_access",
                        "deny",
                    ),
                ],
            ),
            member_ruleset=cls._build_ruleset(
                "{0}_member".format(cls._SAFE_PROFILE_NAME),
                [
                    cls._build_rule(
                        "member_hide_dunder_pattern",
                        "show_member",
                        "deny",
                        {"pattern": "__*"},
                    ),
                    cls._build_rule(
                        "member_hide___dict__",
                        "show_member",
                        "deny",
                        {"member_name": "__dict__"},
                    ),
                    cls._build_rule(
                        "member_hide___class__",
                        "show_member",
                        "deny",
                        {"member_name": "__class__"},
                    ),
                    cls._build_rule(
                        "member_hide___mro__",
                        "show_member",
                        "deny",
                        {"member_name": "__mro__"},
                    ),
                    cls._build_rule(
                        "member_hide___bases__",
                        "show_member",
                        "deny",
                        {"member_name": "__bases__"},
                    ),
                    cls._build_rule(
                        "member_hide___subclasses__",
                        "show_member",
                        "deny",
                        {"member_name": "__subclasses__"},
                    ),
                    cls._build_rule(
                        "member_hide___globals__",
                        "show_member",
                        "deny",
                        {"member_name": "__globals__"},
                    ),
                    cls._build_rule(
                        "member_hide___closure__",
                        "show_member",
                        "deny",
                        {"member_name": "__closure__"},
                    ),
                    cls._build_rule(
                        "member_hide___code__",
                        "show_member",
                        "deny",
                        {"member_name": "__code__"},
                    ),
                    cls._build_rule(
                        "member_hide___getattribute__",
                        "show_member",
                        "deny",
                        {"member_name": "__getattribute__"},
                    ),
                    cls._build_rule(
                        "member_hide___setattr__",
                        "show_member",
                        "deny",
                        {"member_name": "__setattr__"},
                    ),
                    cls._build_rule(
                        "member_hide___delattr__",
                        "show_member",
                        "deny",
                        {"member_name": "__delattr__"},
                    ),
                    cls._build_rule(
                        "member_hide___reduce__",
                        "show_member",
                        "deny",
                        {"member_name": "__reduce__"},
                    ),
                    cls._build_rule(
                        "member_hide___reduce_ex__",
                        "show_member",
                        "deny",
                        {"member_name": "__reduce_ex__"},
                    ),
                ],
            ),
        )

    @classmethod
    def create_hybrid(cls) -> "FrameACLViewProfile":
        """
        Create the middle-tier reusable view profile.

        Returns:
            FrameACLViewProfile: Hybrid reusable view profile.
        """
        return cls(
            cls._HYBRID_PROFILE_NAME,
            minimum_spell_payload_profile_name=(
                cls._DEFAULT_SPELL_PAYLOAD_PROFILE_NAME
            ),
            frame_ruleset=cls._build_ruleset(
                "{0}_frame".format(cls._HYBRID_PROFILE_NAME),
                [
                    cls._build_rule("frame_visible", "visible", "allow"),
                    cls._build_rule("frame_show_payload", "show_payload", "allow"),
                ],
            ),
            conduit_ruleset=cls._build_ruleset(
                "{0}_conduit".format(cls._HYBRID_PROFILE_NAME),
                [
                    cls._build_rule("conduit_visible", "visible", "allow"),
                    cls._build_rule("conduit_show_payload", "show_payload", "allow"),
                    cls._build_rule("conduit_show_policy", "show_policy", "allow"),
                    cls._build_rule("conduit_show_peer_links", "show_peer_links", "allow"),
                ],
            ),
            spell_ruleset=cls._build_ruleset(
                "{0}_spell".format(cls._HYBRID_PROFILE_NAME),
                [
                    cls._build_rule("spell_visible", "visible", "allow"),
                    cls._build_rule(
                        "spell_show_binding_payload",
                        "show_binding_payload",
                        "allow",
                    ),
                    cls._build_rule(
                        "spell_show_resolution_payload",
                        "show_resolution_payload",
                        "allow",
                    ),
                    cls._build_rule("spell_show_metadata", "show_metadata", "allow"),
                    cls._build_rule(
                        "spell_show_class_profile",
                        "show_class_profile",
                        "allow",
                    ),
                    cls._build_rule(
                        "spell_show_callable_profile",
                        "show_callable_profile",
                        "allow",
                    ),
                    cls._build_rule(
                        "spell_hide_instance_members",
                        "show_instance_members",
                        "deny",
                    ),
                    cls._build_rule(
                        "spell_hide_dynamic_access",
                        "show_dynamic_access",
                        "deny",
                    ),
                ],
            ),
            member_ruleset=cls._build_ruleset(
                "{0}_member".format(cls._HYBRID_PROFILE_NAME),
                [
                    cls._build_rule(
                        "member_hide_dunder_pattern",
                        "show_member",
                        "deny",
                        {"pattern": "__*"},
                    ),
                    cls._build_rule(
                        "member_hide___dict__",
                        "show_member",
                        "deny",
                        {"member_name": "__dict__"},
                    ),
                    cls._build_rule(
                        "member_hide___class__",
                        "show_member",
                        "deny",
                        {"member_name": "__class__"},
                    ),
                ],
            ),
        )

    @classmethod
    def create_permissive(cls) -> "FrameACLViewProfile":
        """
        Create the widest reusable view profile currently supported.

        Returns:
            FrameACLViewProfile: Permissive reusable view profile.
        """
        return cls(
            cls._PERMISSIVE_PROFILE_NAME,
            minimum_spell_payload_profile_name=(
                cls._DEFAULT_SPELL_PAYLOAD_PROFILE_NAME
            ),
            frame_ruleset=cls._build_ruleset(
                "{0}_frame".format(cls._PERMISSIVE_PROFILE_NAME),
                [
                    cls._build_rule("frame_visible", "visible", "allow"),
                    cls._build_rule("frame_show_payload", "show_payload", "allow"),
                ],
            ),
            conduit_ruleset=cls._build_ruleset(
                "{0}_conduit".format(cls._PERMISSIVE_PROFILE_NAME),
                [
                    cls._build_rule("conduit_visible", "visible", "allow"),
                    cls._build_rule("conduit_show_payload", "show_payload", "allow"),
                    cls._build_rule("conduit_show_policy", "show_policy", "allow"),
                    cls._build_rule("conduit_show_peer_links", "show_peer_links", "allow"),
                ],
            ),
            spell_ruleset=cls._build_ruleset(
                "{0}_spell".format(cls._PERMISSIVE_PROFILE_NAME),
                [
                    cls._build_rule("spell_visible", "visible", "allow"),
                    cls._build_rule(
                        "spell_show_binding_payload",
                        "show_binding_payload",
                        "allow",
                    ),
                    cls._build_rule(
                        "spell_show_resolution_payload",
                        "show_resolution_payload",
                        "allow",
                    ),
                    cls._build_rule("spell_show_metadata", "show_metadata", "allow"),
                    cls._build_rule(
                        "spell_show_class_profile",
                        "show_class_profile",
                        "allow",
                    ),
                    cls._build_rule(
                        "spell_show_callable_profile",
                        "show_callable_profile",
                        "allow",
                    ),
                    cls._build_rule(
                        "spell_show_instance_members",
                        "show_instance_members",
                        "allow",
                    ),
                    cls._build_rule(
                        "spell_show_dynamic_access",
                        "show_dynamic_access",
                        "allow",
                    ),
                ],
            ),
            member_ruleset=cls._build_ruleset(
                "{0}_member".format(cls._PERMISSIVE_PROFILE_NAME),
                [
                    cls._build_rule(
                        "member_hide_dunder_pattern",
                        "show_member",
                        "deny",
                        {"pattern": "__*"},
                    ),
                    cls._build_rule(
                        "member_hide___dict__",
                        "show_member",
                        "deny",
                        {"member_name": "__dict__"},
                    ),
                ],
            ),
        )

    def cleanup(self) -> None:
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
        self._version = None
        self._minimum_spell_payload_profile_name = None
        self._name = None
        self._id = None

    @property
    def version(self) -> str:
        """
        Return the reusable profile version string.

        Returns:
            str: Profile version string.
        """
        self.check_cleaned()
        return self._version

    @property
    def name(self) -> str:
        self.check_cleaned()
        return self._name

    @property
    def minimum_spell_payload_profile_name(self) -> str:
        self.check_cleaned()
        return self._minimum_spell_payload_profile_name

    @property
    def frame_ruleset(self) -> FrameACLRuleSet:
        self.check_cleaned()
        return self._frame_ruleset

    @property
    def conduit_ruleset(self) -> FrameACLRuleSet:
        self.check_cleaned()
        return self._conduit_ruleset

    @property
    def spell_ruleset(self) -> FrameACLRuleSet:
        self.check_cleaned()
        return self._spell_ruleset

    @property
    def member_ruleset(self) -> FrameACLRuleSet:
        self.check_cleaned()
        return self._member_ruleset

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

    @staticmethod
    def _build_rule(
            rule_name: str,
            operation: str,
            effect: str,
            conditions: Optional[Dict[str, Any]] = None,
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


class FrameACLCodegenProfile(Cleanable):
    """
    Purpose:
        Hold one reusable typed codegen-profile ruleset bundle.

    Contract:
        - Owns frame, conduit, spell, and capability rulesets.
        - Cleanup is idempotent and cascades into all owned rulesets.
    """

    __melder_internal__ = _mrg.sentinel
    _SAFE_PROFILE_NAME = "safe"
    _HYBRID_PROFILE_NAME = "hybrid"
    _PERMISSIVE_PROFILE_NAME = "permissive"
    _DEFAULT_PROFILE_NAME = _SAFE_PROFILE_NAME
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_version",
        "_name",
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
    ) -> None:
        super().__init__()
        if not name:
            raise ValueError("name cannot be empty.")
        self._id: str = IDBuilder.create_id()
        self._version: str = "0.0.1"
        self._name: str = name
        self._frame_ruleset = FrameACLViewProfile._coerce_ruleset(
            frame_ruleset,
            "{0}_frame".format(name),
        )
        self._conduit_ruleset = FrameACLViewProfile._coerce_ruleset(
            conduit_ruleset,
            "{0}_conduit".format(name),
        )
        self._spell_ruleset = FrameACLViewProfile._coerce_ruleset(
            spell_ruleset,
            "{0}_spell".format(name),
        )
        self._capability_ruleset = FrameACLViewProfile._coerce_ruleset(
            capability_ruleset,
            "{0}_capability".format(name),
        )

    @classmethod
    def create_default(cls) -> "FrameACLCodegenProfile":
        return cls.create_safe()

    @classmethod
    def create_safe(cls) -> "FrameACLCodegenProfile":
        """
        Create the restrictive reusable codegen profile.

        Returns:
            FrameACLCodegenProfile: Safe reusable codegen profile.
        """
        return cls(
            cls._SAFE_PROFILE_NAME,
            frame_ruleset=FrameACLViewProfile._build_ruleset(
                "{0}_frame".format(cls._SAFE_PROFILE_NAME),
                [
                    FrameACLViewProfile._build_rule("frame_query", "query", "allow"),
                ],
            ),
            conduit_ruleset=FrameACLViewProfile._build_ruleset(
                "{0}_conduit".format(cls._SAFE_PROFILE_NAME),
                [
                    FrameACLViewProfile._build_rule("conduit_query", "query", "allow"),
                    FrameACLViewProfile._build_rule("conduit_link", "link", "deny"),
                    FrameACLViewProfile._build_rule("conduit_unlink", "unlink", "deny"),
                    FrameACLViewProfile._build_rule(
                        "conduit_create_lesser",
                        "create_lesser_conduit",
                        "deny",
                    ),
                    FrameACLViewProfile._build_rule(
                        "conduit_transfer_ownership",
                        "transfer_ownership",
                        "deny",
                    ),
                ],
            ),
            spell_ruleset=FrameACLViewProfile._build_ruleset(
                "{0}_spell".format(cls._SAFE_PROFILE_NAME),
                [
                    FrameACLViewProfile._build_rule(
                        "spell_resolve_existing",
                        "resolve_existing",
                        "allow",
                    ),
                    FrameACLViewProfile._build_rule(
                        "spell_bind_existing",
                        "bind_existing",
                        "allow",
                    ),
                    FrameACLViewProfile._build_rule(
                        "spell_local_create",
                        "local_create",
                        "deny",
                    ),
                    FrameACLViewProfile._build_rule(
                        "spell_invoke_method",
                        "invoke_method",
                        "deny",
                    ),
                    FrameACLViewProfile._build_rule(
                        "spell_read_attribute",
                        "read_attribute",
                        "deny",
                    ),
                    FrameACLViewProfile._build_rule(
                        "spell_write_attribute",
                        "write_attribute",
                        "deny",
                    ),
                ],
            ),
            capability_ruleset=FrameACLViewProfile._build_ruleset(
                "{0}_capability".format(cls._SAFE_PROFILE_NAME),
                [
                    FrameACLViewProfile._build_rule(
                        "capability_dynamic_access",
                        "dynamic_access",
                        "deny",
                    ),
                    FrameACLViewProfile._build_rule(
                        "capability_mutation",
                        "mutation",
                        "deny",
                    ),
                    FrameACLViewProfile._build_rule(
                        "capability_contract_override",
                        "contract_override",
                        "deny",
                    ),
                    FrameACLViewProfile._build_rule(
                        "capability_unsafe_reflection",
                        "unsafe_reflection",
                        "deny",
                    ),
                    FrameACLViewProfile._build_rule(
                        "capability_dunder_access",
                        "dunder_access",
                        "deny",
                    ),
                ],
            ),
        )

    @classmethod
    def create_hybrid(cls) -> "FrameACLCodegenProfile":
        """
        Create the middle-tier reusable codegen profile.

        Returns:
            FrameACLCodegenProfile: Hybrid reusable codegen profile.
        """
        return cls(
            cls._HYBRID_PROFILE_NAME,
            frame_ruleset=FrameACLViewProfile._build_ruleset(
                "{0}_frame".format(cls._HYBRID_PROFILE_NAME),
                [
                    FrameACLViewProfile._build_rule("frame_query", "query", "allow"),
                ],
            ),
            conduit_ruleset=FrameACLViewProfile._build_ruleset(
                "{0}_conduit".format(cls._HYBRID_PROFILE_NAME),
                [
                    FrameACLViewProfile._build_rule("conduit_query", "query", "allow"),
                    FrameACLViewProfile._build_rule("conduit_link", "link", "allow"),
                    FrameACLViewProfile._build_rule("conduit_unlink", "unlink", "allow"),
                    FrameACLViewProfile._build_rule(
                        "conduit_create_lesser",
                        "create_lesser_conduit",
                        "deny",
                    ),
                    FrameACLViewProfile._build_rule(
                        "conduit_transfer_ownership",
                        "transfer_ownership",
                        "deny",
                    ),
                ],
            ),
            spell_ruleset=FrameACLViewProfile._build_ruleset(
                "{0}_spell".format(cls._HYBRID_PROFILE_NAME),
                [
                    FrameACLViewProfile._build_rule(
                        "spell_resolve_existing",
                        "resolve_existing",
                        "allow",
                    ),
                    FrameACLViewProfile._build_rule(
                        "spell_bind_existing",
                        "bind_existing",
                        "allow",
                    ),
                    FrameACLViewProfile._build_rule(
                        "spell_invoke_method",
                        "invoke_method",
                        "allow",
                    ),
                    FrameACLViewProfile._build_rule(
                        "spell_read_attribute",
                        "read_attribute",
                        "allow",
                    ),
                    FrameACLViewProfile._build_rule(
                        "spell_local_create",
                        "local_create",
                        "deny",
                    ),
                    FrameACLViewProfile._build_rule(
                        "spell_write_attribute",
                        "write_attribute",
                        "deny",
                    ),
                ],
            ),
            capability_ruleset=FrameACLViewProfile._build_ruleset(
                "{0}_capability".format(cls._HYBRID_PROFILE_NAME),
                [
                    FrameACLViewProfile._build_rule(
                        "capability_dynamic_access",
                        "dynamic_access",
                        "deny",
                    ),
                    FrameACLViewProfile._build_rule(
                        "capability_mutation",
                        "mutation",
                        "deny",
                    ),
                    FrameACLViewProfile._build_rule(
                        "capability_contract_override",
                        "contract_override",
                        "deny",
                    ),
                    FrameACLViewProfile._build_rule(
                        "capability_unsafe_reflection",
                        "unsafe_reflection",
                        "deny",
                    ),
                    FrameACLViewProfile._build_rule(
                        "capability_dunder_access",
                        "dunder_access",
                        "deny",
                    ),
                ],
            ),
        )

    @classmethod
    def create_permissive(cls) -> "FrameACLCodegenProfile":
        """
        Create the widest reusable codegen profile currently supported.

        Returns:
            FrameACLCodegenProfile: Permissive reusable codegen profile.
        """
        return cls(
            cls._PERMISSIVE_PROFILE_NAME,
            frame_ruleset=FrameACLViewProfile._build_ruleset(
                "{0}_frame".format(cls._PERMISSIVE_PROFILE_NAME),
                [
                    FrameACLViewProfile._build_rule("frame_query", "query", "allow"),
                ],
            ),
            conduit_ruleset=FrameACLViewProfile._build_ruleset(
                "{0}_conduit".format(cls._PERMISSIVE_PROFILE_NAME),
                [
                    FrameACLViewProfile._build_rule("conduit_query", "query", "allow"),
                    FrameACLViewProfile._build_rule("conduit_link", "link", "allow"),
                    FrameACLViewProfile._build_rule("conduit_unlink", "unlink", "allow"),
                    FrameACLViewProfile._build_rule(
                        "conduit_create_lesser",
                        "create_lesser_conduit",
                        "allow",
                    ),
                    FrameACLViewProfile._build_rule(
                        "conduit_transfer_ownership",
                        "transfer_ownership",
                        "allow",
                    ),
                ],
            ),
            spell_ruleset=FrameACLViewProfile._build_ruleset(
                "{0}_spell".format(cls._PERMISSIVE_PROFILE_NAME),
                [
                    FrameACLViewProfile._build_rule(
                        "spell_resolve_existing",
                        "resolve_existing",
                        "allow",
                    ),
                    FrameACLViewProfile._build_rule(
                        "spell_bind_existing",
                        "bind_existing",
                        "allow",
                    ),
                    FrameACLViewProfile._build_rule(
                        "spell_local_create",
                        "local_create",
                        "allow",
                    ),
                    FrameACLViewProfile._build_rule(
                        "spell_invoke_method",
                        "invoke_method",
                        "allow",
                    ),
                    FrameACLViewProfile._build_rule(
                        "spell_read_attribute",
                        "read_attribute",
                        "allow",
                    ),
                    FrameACLViewProfile._build_rule(
                        "spell_write_attribute",
                        "write_attribute",
                        "allow",
                    ),
                ],
            ),
            capability_ruleset=FrameACLViewProfile._build_ruleset(
                "{0}_capability".format(cls._PERMISSIVE_PROFILE_NAME),
                [
                    FrameACLViewProfile._build_rule(
                        "capability_dynamic_access",
                        "dynamic_access",
                        "allow",
                    ),
                    FrameACLViewProfile._build_rule(
                        "capability_contract_override",
                        "contract_override",
                        "allow",
                    ),
                    FrameACLViewProfile._build_rule(
                        "capability_mutation",
                        "mutation",
                        "deny",
                    ),
                    FrameACLViewProfile._build_rule(
                        "capability_unsafe_reflection",
                        "unsafe_reflection",
                        "deny",
                    ),
                    FrameACLViewProfile._build_rule(
                        "capability_dunder_access",
                        "dunder_access",
                        "deny",
                    ),
                ],
            ),
        )

    def cleanup(self) -> None:
        if self._cleaned:
            return
        self._cleaned = True
        self._frame_ruleset.cleanup()
        self._conduit_ruleset.cleanup()
        self._spell_ruleset.cleanup()
        self._capability_ruleset.cleanup()
        self._version = None
        self._frame_ruleset = None
        self._conduit_ruleset = None
        self._spell_ruleset = None
        self._capability_ruleset = None
        self._name = None
        self._id = None

    @property
    def name(self) -> str:
        self.check_cleaned()
        return self._name

    @property
    def version(self) -> str:
        """
        Return the reusable profile version string.

        Returns:
            str: Profile version string.
        """
        self.check_cleaned()
        return self._version

    @property
    def frame_ruleset(self) -> FrameACLRuleSet:
        self.check_cleaned()
        return self._frame_ruleset

    @property
    def conduit_ruleset(self) -> FrameACLRuleSet:
        self.check_cleaned()
        return self._conduit_ruleset

    @property
    def spell_ruleset(self) -> FrameACLRuleSet:
        self.check_cleaned()
        return self._spell_ruleset

    @property
    def capability_ruleset(self) -> FrameACLRuleSet:
        self.check_cleaned()
        return self._capability_ruleset


class FrameACLProfile(Cleanable):
    """
    Purpose:
        Represent one composed ACL profile that pairs a reusable view profile
        with a reusable codegen profile plus local override rulesets.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_version",
        "_name",
        "_view_profile",
        "_codegen_profile",
        "_view_override_ruleset",
        "_codegen_override_ruleset",
    ]

    def __init__(
            self,
            name: str,
            *,
            view_profile: FrameACLViewProfile,
            codegen_profile: FrameACLCodegenProfile,
            view_override_ruleset: Optional[FrameACLRuleSet] = None,
            codegen_override_ruleset: Optional[FrameACLRuleSet] = None,
    ) -> None:
        super().__init__()
        if not name:
            raise ValueError("name cannot be empty.")
        if not isinstance(view_profile, FrameACLViewProfile):
            raise TypeError("view_profile must be a FrameACLViewProfile.")
        if not isinstance(codegen_profile, FrameACLCodegenProfile):
            raise TypeError("codegen_profile must be a FrameACLCodegenProfile.")
        self._id: str = IDBuilder.create_id()
        self._version: str = "0.0.1"
        self._name: str = name
        self._view_profile = view_profile
        self._codegen_profile = codegen_profile
        self._view_override_ruleset = FrameACLViewProfile._coerce_ruleset(
            view_override_ruleset,
            "{0}_view_override".format(name),
        )
        self._codegen_override_ruleset = FrameACLViewProfile._coerce_ruleset(
            codegen_override_ruleset,
            "{0}_codegen_override".format(name),
        )

    def cleanup(self) -> None:
        if self._cleaned:
            return
        self._cleaned = True
        self._view_override_ruleset.cleanup()
        self._codegen_override_ruleset.cleanup()
        self._view_override_ruleset = None
        self._codegen_override_ruleset = None
        self._view_profile = None
        self._codegen_profile = None
        self._version = None
        self._name = None
        self._id = None

    @property
    def name(self) -> str:
        self.check_cleaned()
        return self._name

    @property
    def version(self) -> str:
        """
        Return the composed profile version string.

        Returns:
            str: Profile version string.
        """
        self.check_cleaned()
        return self._version

    @property
    def view_profile(self) -> FrameACLViewProfile:
        self.check_cleaned()
        return self._view_profile

    @property
    def codegen_profile(self) -> FrameACLCodegenProfile:
        self.check_cleaned()
        return self._codegen_profile

    @property
    def view_override_ruleset(self) -> FrameACLRuleSet:
        self.check_cleaned()
        return self._view_override_ruleset

    @property
    def codegen_override_ruleset(self) -> FrameACLRuleSet:
        self.check_cleaned()
        return self._codegen_override_ruleset


class FrameACLProfileBuilder(Cleanable):
    """
    Purpose:
        Own the reusable ACL profile registries and compose `FrameACLProfile`
        objects from them.
    """

    __melder_internal__ = _mrg.sentinel
    _DEFAULT_PROFILE_NAME = "safe"
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_version",
        "_view_profiles_by_name",
        "_codegen_profiles_by_name",
    ]

    def __init__(self) -> None:
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._version: str = "0.0.1"
        self._view_profiles_by_name: Dict[str, FrameACLViewProfile] = {}
        self._codegen_profiles_by_name: Dict[str, FrameACLCodegenProfile] = {}
        self.register_view_profile(FrameACLViewProfile.create_safe())
        self.register_view_profile(FrameACLViewProfile.create_hybrid())
        self.register_view_profile(FrameACLViewProfile.create_permissive())
        self.register_codegen_profile(FrameACLCodegenProfile.create_safe())
        self.register_codegen_profile(FrameACLCodegenProfile.create_hybrid())
        self.register_codegen_profile(FrameACLCodegenProfile.create_permissive())

    def cleanup(self) -> None:
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            for view_profile in self._view_profiles_by_name.values():
                view_profile.cleanup()
            for codegen_profile in self._codegen_profiles_by_name.values():
                codegen_profile.cleanup()
            self._view_profiles_by_name.clear()
            self._codegen_profiles_by_name.clear()
            self._view_profiles_by_name = None
            self._codegen_profiles_by_name = None
            self._version = None
            self._id = None
        self._lock = None

    @property
    def version(self) -> str:
        self.check_cleaned()
        return self._version

    @property
    def view_profiles_by_name(self) -> Dict[str, FrameACLViewProfile]:
        self.check_cleaned()
        with self._lock:
            return dict(self._view_profiles_by_name)

    @property
    def codegen_profiles_by_name(self) -> Dict[str, FrameACLCodegenProfile]:
        self.check_cleaned()
        with self._lock:
            return dict(self._codegen_profiles_by_name)

    def register_view_profile(self, view_profile: FrameACLViewProfile) -> None:
        self.check_cleaned()
        if not isinstance(view_profile, FrameACLViewProfile):
            raise TypeError("view_profile must be a FrameACLViewProfile.")
        with self._lock:
            existing = self._view_profiles_by_name.get(view_profile.name)
            if existing is not None and existing is not view_profile:
                existing.cleanup()
            self._view_profiles_by_name[view_profile.name] = view_profile

    def register_codegen_profile(
            self,
            codegen_profile: FrameACLCodegenProfile,
    ) -> None:
        self.check_cleaned()
        if not isinstance(codegen_profile, FrameACLCodegenProfile):
            raise TypeError(
                "codegen_profile must be a FrameACLCodegenProfile."
            )
        with self._lock:
            existing = self._codegen_profiles_by_name.get(codegen_profile.name)
            if existing is not None and existing is not codegen_profile:
                existing.cleanup()
            self._codegen_profiles_by_name[codegen_profile.name] = codegen_profile

    def get_required_view_profile(
            self,
            profile_name: str,
    ) -> FrameACLViewProfile:
        self.check_cleaned()
        with self._lock:
            try:
                return self._view_profiles_by_name[profile_name]
            except KeyError as exc:
                raise KeyError(profile_name) from exc

    def get_required_codegen_profile(
            self,
            profile_name: str,
    ) -> FrameACLCodegenProfile:
        self.check_cleaned()
        with self._lock:
            try:
                return self._codegen_profiles_by_name[profile_name]
            except KeyError as exc:
                raise KeyError(profile_name) from exc

    def list_view_profile_names(self) -> List[str]:
        self.check_cleaned()
        with self._lock:
            return list(self._view_profiles_by_name.keys())

    def list_codegen_profile_names(self) -> List[str]:
        self.check_cleaned()
        with self._lock:
            return list(self._codegen_profiles_by_name.keys())

    def remove_view_profile(self, profile_name: str) -> bool:
        self.check_cleaned()
        if profile_name == self._DEFAULT_PROFILE_NAME:
            raise RuntimeError("Cannot remove the default view profile.")
        with self._lock:
            view_profile = self._view_profiles_by_name.pop(profile_name, None)
            if view_profile is None:
                return False
            view_profile.cleanup()
            return True

    def remove_codegen_profile(self, profile_name: str) -> bool:
        self.check_cleaned()
        if profile_name == self._DEFAULT_PROFILE_NAME:
            raise RuntimeError("Cannot remove the default codegen profile.")
        with self._lock:
            codegen_profile = self._codegen_profiles_by_name.pop(
                profile_name,
                None,
            )
            if codegen_profile is None:
                return False
            codegen_profile.cleanup()
            return True

    def create_profile(
            self,
            name: str,
            *,
            view_profile_name: str = _DEFAULT_PROFILE_NAME,
            codegen_profile_name: str = _DEFAULT_PROFILE_NAME,
            view_override_ruleset: Optional[FrameACLRuleSet] = None,
            codegen_override_ruleset: Optional[FrameACLRuleSet] = None,
    ) -> FrameACLProfile:
        self.check_cleaned()
        view_profile = self.get_required_view_profile(view_profile_name)
        codegen_profile = self.get_required_codegen_profile(codegen_profile_name)
        return FrameACLProfile(
            name,
            view_profile=view_profile,
            codegen_profile=codegen_profile,
            view_override_ruleset=view_override_ruleset,
            codegen_override_ruleset=codegen_override_ruleset,
        )
