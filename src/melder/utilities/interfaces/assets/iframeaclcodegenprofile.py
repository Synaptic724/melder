from typing import runtime_checkable, Protocol

from melder.utilities.interfaces.assets.icleanable import ICleanable


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
