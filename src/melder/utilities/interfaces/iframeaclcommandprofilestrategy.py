from typing import Protocol, runtime_checkable
from melder.utilities.interfaces.iframeaclcommandprofile import IFrameACLCommandProfile
@runtime_checkable
class IFrameACLCommandProfileStrategy(Protocol):
    """
    Reusable strategy contract for building one configured command ACL profile.

    Contract:
        - Exposes one stable strategy/profile name.
        - Returns a freshly configured `IFrameACLCommandProfile` instance when
          asked to build.
        - Carries no shared mutable module-level state itself.
    """

    @property
    def name(self) -> str:
        """
        Return the stable command-profile strategy name.

        Returns:
            str: Canonical strategy/profile name.
        """
        ...

    def build(self) -> IFrameACLCommandProfile:
        """
        Build and return one configured command ACL profile instance.

        Returns:
            IFrameACLCommandProfile: Fresh configured profile instance.
        """
        ...
