from typing import Any, Dict, Optional, Protocol, runtime_checkable
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.iframeaclcodegenprofile import IFrameACLCodegenProfile
from melder.utilities.interfaces.iframeaclruleset import IFrameACLRuleSet

@runtime_checkable
class IFrameACLCodegenConfiguration(ICleanable, Protocol):
    """
    Typed frame codegen ACL configuration contract.

    Contract:
        - Carries one codegen-policy profile identity/version pair.
        - Owns detached frame, conduit, spell, and capability override rulesets.
        - Represents the codegen-side sibling inside a frame ACL bundle.
        - Is configuration data only; it does not validate or execute codegen
          work by itself.
    """

    @property
    def configuration_id(self) -> str:
        ...

    @property
    def source_configuration_id(self) -> Optional[str]:
        ...

    @property
    def previous_configuration_id(self) -> Optional[str]:
        ...

    @property
    def created_at(self) -> str:
        ...

    @property
    def reason(self) -> str:
        ...

    @property
    def locked(self) -> bool:
        ...

    @property
    def profile_name(self) -> str:
        ...

    @property
    def profile_version(self) -> str:
        ...

    @property
    def precision_profile_name(self) -> Optional[str]:
        ...

    @property
    def precision_profile_version(self) -> Optional[str]:
        ...

    @property
    def frame_override_ruleset(self) -> IFrameACLRuleSet:
        ...

    @property
    def conduit_override_ruleset(self) -> IFrameACLRuleSet:
        ...

    @property
    def spell_override_ruleset(self) -> IFrameACLRuleSet:
        ...

    @property
    def capability_override_ruleset(self) -> IFrameACLRuleSet:
        ...

    def to_json_dict(self) -> Dict[str, Any]:
        """
        Return the configuration as a JSON-compatible dictionary.

        Returns:
            Dict[str, Any]: JSON-compatible configuration payload.
        """
        ...

    def to_json_string(self) -> str:
        """
        Return the configuration as a normalized JSON string.

        Returns:
            str: Normalized JSON payload string.
        """
        ...

    def clone(self) -> "IFrameACLCodegenConfiguration":
        """
        Return a detached configuration copy.

        Returns:
            IFrameACLCodegenConfiguration: Detached configuration copy.
        """
        ...

    def finalize(self) -> None:
        """
        Lock the configuration against further mutation.

        Returns:
            None.
        """
        ...

    def set_profiles(
            self,
            profile: IFrameACLCodegenProfile,
            *,
            precision_profile: Optional[IFrameACLCodegenProfile] = None,
    ) -> None:
        """
        Replace the base and optional precision profiles on the mutable config.

        Returns:
            None.
        """
        ...
