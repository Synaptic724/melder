from typing import Any, Dict, Optional, Protocol, runtime_checkable
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.iframeaclruleset import IFrameACLRuleSet
from melder.utilities.interfaces.iframeaclviewprofile import IFrameACLViewProfile

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
    def required_nexus_label(self) -> str:
        ...

    @property
    def required_nexus_version(self) -> str:
        ...

    @property
    def minimum_spell_payload_type(self) -> str:
        ...

    @property
    def minimum_spell_payload_version(self) -> str:
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
    def member_override_ruleset(self) -> IFrameACLRuleSet:
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
