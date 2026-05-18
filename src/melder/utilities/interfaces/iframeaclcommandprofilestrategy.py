from typing import Protocol, runtime_checkable
from melder.aether.nexus.acl.configurations.profiles.command.frame_acl_command_profile import (
    FrameACLCommandProfile,
)
@runtime_checkable
class IFrameACLCommandProfileStrategy(Protocol):
    """
    Reusable strategy contract for building one configured command ACL profile.

    Contract:
        - Exposes one stable strategy/profile name.
        - Returns a freshly configured `FrameACLCommandProfile` instance when
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

    def build(self) -> FrameACLCommandProfile:
        """
        Build and return one configured command ACL profile instance.

        Returns:
            FrameACLCommandProfile: Fresh configured profile instance.
        """
        ...
