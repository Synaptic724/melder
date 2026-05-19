import threading
from typing import Dict, List, Optional, Sequence
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.nexus.acl.configurations.profiles.rules.frame_acl_rule import FrameACLRule
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.interfaces.iframeaclrule import IFrameACLRule
from melder.utilities.interfaces.iframeaclruleset import IFrameACLRuleSet


class FrameACLRuleSet(Cleanable, IFrameACLRuleSet):
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
            rules: Optional[Sequence[IFrameACLRule]] = None,
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
        self._rules_by_name: Dict[str, IFrameACLRule] = {}
        if rules is not None:
            for rule in rules:
                self.register_rule(rule)

    def cleanup(self) -> None:
        """
        Idempotently clear the ruleset and owned rules.

        Contract:
            - Cleans all owned rules before dropping references.
            - Leaves the ruleset unusable after cleanup.

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

            del self._rules_by_name
            del self._name
            del self._id
        del self._lock

    @property
    def id(self) -> str:
        """
        Return the stable ruleset identifier.

        Returns:
            str: Stable ruleset id.
        """
        self.check_cleaned()
        return self._id

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
    def rules_by_name(self) -> Dict[str, IFrameACLRule]:
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

        Contract:
            Returns a snapshot list of the current rule-name keys.

        Returns:
            List[str]: Current rule names.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._rules_by_name.keys())

    def get_required_rule(self, rule_name: str) -> IFrameACLRule:
        """
        Return one existing rule or raise.

        Args:
            rule_name:
                Rule name to resolve.

        Contract:
            Resolves only existing rules and fails fast on absence.

        Returns:
            FrameACLRule: Existing rule.
        """
        self.check_cleaned()
        with self._lock:
            try:
                return self._rules_by_name[rule_name]
            except KeyError as exc:
                raise KeyError(rule_name) from exc

    def register_rule(self, rule: IFrameACLRule) -> None:
        """
        Register or replace one rule in the ruleset.

        Args:
            rule:
                Rule object to store by its own name.

        Contract:
            - Replaces any existing distinct rule with the same `rule_name`.
            - Cleans the displaced rule before storing the new one.

        Returns:
            None.
        """
        self.check_cleaned()
        if not isinstance(rule, IFrameACLRule):
            raise TypeError("rule must satisfy IFrameACLRule.")
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

        Contract:
            - Cleans the removed rule before returning.
            - Returns False when the rule name is not registered.

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

    def to_json_dict(self) -> Dict[str, object]:
        """
        Return the ruleset as a detached JSON-compatible dictionary.

        Contract:
            Returns a detached JSON-ready payload built from the current rule
            snapshot.

        Returns:
            Dict[str, object]: JSON-compatible ruleset dictionary.
        """
        self.check_cleaned()
        return {
            "name": self._name,
            "rules": [rule.to_json_dict() for rule in self._rules_by_name.values()],
        }

    @classmethod
    def from_json_dict(
            cls,
            payload: Dict[str, object],
    ) -> "FrameACLRuleSet":
        """
        Build one ruleset from a JSON-compatible dictionary.

        Args:
            payload:
                JSON-compatible ruleset dictionary.

        Contract:
            Validates only the outer payload shape here and delegates rule-level
            invariants to `FrameACLRule.from_json_dict(...)`.

        Returns:
            FrameACLRuleSet: Reconstructed ruleset object.
        """
        if not isinstance(payload, dict):
            raise TypeError("payload must be a dict.")
        name = payload.get("name")
        rules_payload = payload.get("rules")
        if not isinstance(name, str):
            raise TypeError("payload['name'] must be a string.")
        if rules_payload is None:
            rules_payload = []
        if not isinstance(rules_payload, list):
            raise TypeError("rules must be a list.")
        return cls(
            name,
            rules=[
                FrameACLRule.from_json_dict(rule_payload)
                for rule_payload in rules_payload
            ],
        )

    def clone(self) -> "FrameACLRuleSet":
        """
        Return a detached copy of the ruleset.

        Contract:
            Clones through the JSON-compatible round-trip path so the returned
            ruleset has detached rule state.

        Returns:
            FrameACLRuleSet: Detached ruleset copy.
        """
        self.check_cleaned()
        return FrameACLRuleSet.from_json_dict(self.to_json_dict())
