from typing import Any, Dict, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


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

        Contract:
            - Clears the owned detached condition map.
            - Drops the rule's identity and payload references.

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

    def to_json_dict(self) -> Dict[str, Any]:
        """
        Return the rule as a detached JSON-compatible dictionary.

        Contract:
            Returns a detached JSON-ready payload built from the rule's
            current state.

        Returns:
            Dict[str, Any]: JSON-compatible rule dictionary.
        """
        self.check_cleaned()
        return {
            "rule_name": self._rule_name,
            "operation": self._operation,
            "effect": self._effect,
            "conditions": dict(self._conditions),
        }

    @classmethod
    def from_json_dict(
            cls,
            payload: Dict[str, Any],
    ) -> "FrameACLRule":
        """
        Build one rule from a JSON-compatible dictionary.

        Args:
            payload:
                JSON-compatible rule dictionary.

        Contract:
            Validates only the outer payload type here and delegates the field-
            level invariants to the normal constructor.

        Returns:
            FrameACLRule: Reconstructed rule object.
        """
        if not isinstance(payload, dict):
            raise TypeError("payload must be a dict.")
        return cls(
            rule_name=payload.get("rule_name"),
            operation=payload.get("operation"),
            effect=payload.get("effect"),
            conditions=payload.get("conditions"),
        )

    def clone(self) -> "FrameACLRule":
        """
        Return a detached copy of the rule.

        Contract:
            Clones through the JSON-compatible round-trip path so the returned
            rule has detached condition state.

        Returns:
            FrameACLRule: Detached rule copy.
        """
        self.check_cleaned()
        return FrameACLRule.from_json_dict(self.to_json_dict())
