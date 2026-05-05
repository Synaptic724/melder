from typing import Protocol, runtime_checkable

@runtime_checkable
class IFrameACLViewProfileStrategy(Protocol):
    """
    Reusable strategy contract for building one configured view ACL profile.

    Contract:
        - Exposes one stable strategy/profile name.
        - Returns a freshly configured `IFrameACLViewProfile` instance when
          asked to build.
        - Carries no shared mutable module-level state itself.
    """

    @property
    def name(self) -> str:
        """
        Return the stable view-profile strategy name.

        Returns:
            str: Canonical strategy/profile name.
        """
        ...

    def build(self) -> "IFrameACLViewProfile":
        """
        Build and return one configured view ACL profile instance.

        Returns:
            IFrameACLViewProfile: Fresh configured profile instance.
        """
        ...
