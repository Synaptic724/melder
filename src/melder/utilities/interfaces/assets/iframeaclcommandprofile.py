from typing import Protocol, runtime_checkable
from melder.utilities.interfaces.assets.icleanable import ICleanable
from melder.utilities.interfaces.assets.iframeaclruleset import IFrameACLRuleSet

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
