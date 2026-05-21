from typing import Protocol, runtime_checkable
from melder.utilities.interfaces.iframeaclcodegenprofile import (
    IFrameACLCodegenProfile,
)

@runtime_checkable
class IFrameACLCodegenProfileStrategy(Protocol):
    """
    Reusable strategy contract for building one configured codegen ACL profile.

    Contract:
        - Exposes one stable strategy/profile name.
        - Returns a freshly configured `IFrameACLCodegenProfile` instance when
          asked to build.
        - Carries no shared mutable module-level state itself.
    """

    @property
    def name(self) -> str:
        """
        Return the stable codegen-profile strategy name.

        Returns:
            str: Canonical strategy/profile name.
        """
        ...

    def build(self) -> IFrameACLCodegenProfile:
        """
        Build and return one configured codegen ACL profile instance.

        Returns:
            IFrameACLCodegenProfile: Fresh configured profile instance.
        """
        ...

