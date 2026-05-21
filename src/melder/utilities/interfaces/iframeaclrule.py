from typing import Any, Dict, Protocol, runtime_checkable
from melder.utilities.interfaces.icleanable import ICleanable

@runtime_checkable
class IFrameACLRule(ICleanable, Protocol):
    """
    ACL rule contract for reusable profile and applied configuration work.
    """

    @property
    def rule_name(self) -> str:
        """
        Return the stable rule name.

        Returns:
            str: Stable rule name.
        """
        ...

    @property
    def operation(self) -> str:
        """
        Return the rule operation.

        Returns:
            str: Rule operation.
        """
        ...

    @property
    def effect(self) -> str:
        """
        Return the rule effect.

        Returns:
            str: Rule effect.
        """
        ...

    @property
    def conditions(self) -> Dict[str, Any]:
        """
        Return a detached snapshot of rule conditions.

        Returns:
            Dict[str, Any]: Detached condition snapshot.
        """
        ...

    def to_json_dict(self) -> Dict[str, Any]:
        """
        Return the rule as a JSON-compatible dictionary.

        Returns:
            Dict[str, Any]: JSON-compatible rule dictionary.
        """
        ...
