from typing import Protocol, runtime_checkable
from melder.aether.nexus.acl.configurations.profiles.codegen.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)

@runtime_checkable
class IFrameACLCodegenProfileStrategy(Protocol):
    """
    Reusable strategy contract for building one configured codegen ACL profile.

    Contract:
        - Exposes one stable strategy/profile name.
        - Returns a freshly configured `FrameACLCodegenProfile` instance when
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

    def build(self) -> FrameACLCodegenProfile:
        """
        Build and return one configured codegen ACL profile instance.

        Returns:
            FrameACLCodegenProfile: Fresh configured profile instance.
        """
        ...
