from typing import runtime_checkable, Protocol, Dict, Any

from melder.utilities.interfaces.assets.icleanable import ICleanable


@runtime_checkable
class IFrameACLRule(ICleanable, Protocol):
    """
    ACL rule contract for reusable profile and applied configuration work.
    """

    rule_name: str
    operation: str
    effect: str
    conditions: Dict[str, Any]

    def to_json_dict(self) -> Dict[str, Any]:
        """
        Return the rule as a JSON-compatible dictionary.

        Returns:
            Dict[str, Any]: JSON-compatible rule dictionary.
        """
        ...
