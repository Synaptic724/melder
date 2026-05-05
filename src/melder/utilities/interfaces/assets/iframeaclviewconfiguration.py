from typing import Any, Dict, Optional, Protocol, runtime_checkable
from melder.utilities.interfaces.assets.icleanable import ICleanable
from melder.utilities.interfaces.assets.iframeaclruleset import IFrameACLRuleSet
from melder.utilities.interfaces.assets.iframeaclviewprofile import IFrameACLViewProfile

@runtime_checkable
class IFrameACLViewConfiguration(ICleanable, Protocol):
    """
    Typed frame view ACL configuration contract.

    Contract:
        - Carries one view-policy profile identity/version pair plus the
          descriptor floor fields derived from the selected profile.
        - Owns detached frame, conduit, spell, and member override rulesets.
        - Represents the view-side sibling inside a frame ACL bundle.
        - Is configuration data only; it does not publish view surfaces by
          itself.
    """

    configuration_id: str
    source_configuration_id: Optional[str]
    previous_configuration_id: Optional[str]
    created_at: str
    reason: str
    locked: bool
    profile_name: str
    profile_version: str
    precision_profile_name: Optional[str]
    precision_profile_version: Optional[str]
    required_nexus_label: str
    required_nexus_version: str
    minimum_spell_payload_type: str
    minimum_spell_payload_version: str
    frame_override_ruleset: IFrameACLRuleSet
    conduit_override_ruleset: IFrameACLRuleSet
    spell_override_ruleset: IFrameACLRuleSet
    member_override_ruleset: IFrameACLRuleSet

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

    def clone(self) -> "IFrameACLViewConfiguration":
        """
        Return a detached configuration copy.

        Returns:
            IFrameACLViewConfiguration: Detached configuration copy.
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
            profile: IFrameACLViewProfile,
            *,
            precision_profile: Optional[IFrameACLViewProfile] = None,
    ) -> None:
        """
        Replace the base and optional precision profiles on the mutable config.

        Returns:
            None.
        """
        ...
