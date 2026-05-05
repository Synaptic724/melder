from typing import Protocol, runtime_checkable
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.iframeaclcodegenprofile import IFrameACLCodegenProfile
from melder.utilities.interfaces.iframeaclcommandprofile import IFrameACLCommandProfile
from melder.utilities.interfaces.iframeaclruleset import IFrameACLRuleSet
from melder.utilities.interfaces.iframeaclviewprofile import IFrameACLViewProfile

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
