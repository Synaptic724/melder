from typing import Protocol, runtime_checkable
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.iframeaclruleset import IFrameACLRuleSet

@runtime_checkable
class IFrameACLCodegenProfile(ICleanable, Protocol):
    """
    Reusable codegen-side ACL profile contract.
    """

    @property
    def name(self) -> str:
        """
        Return the stable profile name.

        Returns:
            str: Stable profile name.
        """
        ...

    @property
    def version(self) -> str:
        """
        Return the profile version string.

        Returns:
            str: Profile version string.
        """
        ...

    @property
    def validation_strategy_name(self) -> str:
        """
        Return the validator-owned strategy key for this profile.

        Returns:
            str: Validator-owned strategy key.
        """
        ...

    @property
    def frame_ruleset(self) -> IFrameACLRuleSet:
        """
        Return the owned frame ruleset.

        Returns:
            IFrameACLRuleSet: Owned frame ruleset.
        """
        ...

    @property
    def conduit_ruleset(self) -> IFrameACLRuleSet:
        """
        Return the owned conduit ruleset.

        Returns:
            IFrameACLRuleSet: Owned conduit ruleset.
        """
        ...

    @property
    def spell_ruleset(self) -> IFrameACLRuleSet:
        """
        Return the owned spell ruleset.

        Returns:
            IFrameACLRuleSet: Owned spell ruleset.
        """
        ...

    @property
    def capability_ruleset(self) -> IFrameACLRuleSet:
        """
        Return the owned capability ruleset.

        Returns:
            IFrameACLRuleSet: Owned capability ruleset.
        """
        ...
