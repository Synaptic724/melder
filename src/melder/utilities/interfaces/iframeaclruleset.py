from typing import Any, Dict, List, Protocol, runtime_checkable
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.iframeaclrule import IFrameACLRule

@runtime_checkable
class IFrameACLRuleSet(ICleanable, Protocol):
    """
    ACL ruleset contract for reusable profile and applied configuration work.
    """

    name: str
    rules_by_name: Dict[str, IFrameACLRule]

    def list_rule_names(self) -> List[str]:
        """
        Return the current rule names in insertion order.

        Returns:
            List[str]: Current rule names.
        """
        ...

    def get_required_rule(self, rule_name: str) -> IFrameACLRule:
        """
        Return one existing rule or raise.

        Returns:
            IFrameACLRule: Existing rule.
        """
        ...

    def register_rule(self, rule: IFrameACLRule) -> None:
        """
        Register or replace one rule.

        Returns:
            None.
        """
        ...

    def remove_rule(self, rule_name: str) -> bool:
        """
        Remove one rule.

        Returns:
            bool: True when the rule existed and was removed.
        """
        ...

    def to_json_dict(self) -> Dict[str, Any]:
        """
        Return the ruleset as a JSON-compatible dictionary.

        Returns:
            Dict[str, Any]: JSON-compatible ruleset dictionary.
        """
        ...

    def clone(self) -> "IFrameACLRuleSet":
        """
        Return a detached ruleset copy.

        Returns:
            IFrameACLRuleSet: Detached ruleset copy.
        """
        ...
