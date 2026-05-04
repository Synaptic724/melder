from typing import runtime_checkable, Protocol

from melder.utilities.interfaces.assets.icleanable import ICleanable


@runtime_checkable
class IFrameACLProfile(ICleanable, Protocol):
    """
    Composed frame ACL profile contract.
    """

    name: str
    version: str
    view_profile: IFrameACLViewProfile
    command_profile: IFrameACLCommandProfile
    codegen_profile: IFrameACLCodegenProfile
    view_override_ruleset: IFrameACLRuleSet
    command_override_ruleset: IFrameACLRuleSet
    codegen_override_ruleset: IFrameACLRuleSet
