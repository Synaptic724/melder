from typing import runtime_checkable, Protocol

from melder.utilities.interfaces.assets.icleanable import ICleanable


@runtime_checkable
class IFrameACLCommandProfile(ICleanable, Protocol):
    """
    Reusable command-side ACL profile contract.
    """

    name: str
    version: str
    validation_strategy_name: str
    frame_ruleset: IFrameACLRuleSet
    conduit_ruleset: IFrameACLRuleSet
    spell_ruleset: IFrameACLRuleSet
    member_ruleset: IFrameACLRuleSet
