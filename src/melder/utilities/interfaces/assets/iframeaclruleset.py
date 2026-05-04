import threading
from threading import RLock
from types import ModuleType
from typing import runtime_checkable, Type, Protocol, Optional, List, Union, Dict, Any, Iterable, Iterator, Callable, \
    Tuple, Mapping, Set, Sequence, Self

from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.dev_ops.spell_system_states.spell_state_change_reason import SpellStateChangeReason
from melder.spellbook.existence.existence import Existence
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


from melder.utilities.interfaces.assets.icleanable import ICleanable

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
