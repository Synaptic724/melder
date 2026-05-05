from typing import Protocol, runtime_checkable
from melder.utilities.interfaces.assets.icleanable import ICleanable
from melder.utilities.interfaces.assets.iframeaclruleset import IFrameACLRuleSet

@runtime_checkable
class IFrameACLCodegenProfile(ICleanable, Protocol):
    """
    Reusable codegen-side ACL profile contract.
    """

    name: str
    version: str
    validation_strategy_name: str
    frame_ruleset: IFrameACLRuleSet
    conduit_ruleset: IFrameACLRuleSet
    spell_ruleset: IFrameACLRuleSet
    capability_ruleset: IFrameACLRuleSet
