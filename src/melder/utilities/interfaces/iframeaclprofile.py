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

    @property
    def name(self) -> str:
        ...

    @property
    def version(self) -> str:
        ...

    @property
    def view_profile(self) -> IFrameACLViewProfile:
        ...

    @property
    def command_profile(self) -> IFrameACLCommandProfile:
        ...

    @property
    def codegen_profile(self) -> IFrameACLCodegenProfile:
        ...

    @property
    def view_override_ruleset(self) -> IFrameACLRuleSet:
        ...

    @property
    def command_override_ruleset(self) -> IFrameACLRuleSet:
        ...

    @property
    def codegen_override_ruleset(self) -> IFrameACLRuleSet:
        ...
