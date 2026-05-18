from typing import Protocol, runtime_checkable
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.iframeaclruleset import IFrameACLRuleSet

@runtime_checkable
class IFrameACLViewProfile(ICleanable, Protocol):
    """
    Reusable view-side ACL profile contract.
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
    def required_nexus_label(self) -> str:
        """
        Return the required Nexus dataset label.

        Returns:
            str: Required Nexus dataset label.
        """
        ...

    @property
    def required_nexus_version(self) -> str:
        """
        Return the required Nexus dataset version.

        Returns:
            str: Required Nexus dataset version.
        """
        ...

    @property
    def minimum_spell_payload_type(self) -> str:
        """
        Return the minimum spell payload detail type.

        Returns:
            str: Minimum spell payload detail type.
        """
        ...

    @property
    def minimum_spell_payload_version(self) -> str:
        """
        Return the minimum spell payload contract version.

        Returns:
            str: Minimum spell payload contract version.
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
    def member_ruleset(self) -> IFrameACLRuleSet:
        """
        Return the owned member ruleset.

        Returns:
            IFrameACLRuleSet: Owned member ruleset.
        """
        ...
