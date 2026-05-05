from typing import Protocol, runtime_checkable
from melder.utilities.interfaces.assets.icleanable import ICleanable
from melder.utilities.interfaces.assets.iframeaclcodegenprofile import IFrameACLCodegenProfile
from melder.utilities.interfaces.assets.iframeaclcommandprofile import IFrameACLCommandProfile
from melder.utilities.interfaces.assets.iframeaclruleset import IFrameACLRuleSet
from melder.utilities.interfaces.assets.iframeaclviewprofile import IFrameACLViewProfile

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
