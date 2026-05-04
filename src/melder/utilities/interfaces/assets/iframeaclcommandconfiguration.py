from typing import runtime_checkable, Protocol, Optional, Dict, Any

from melder.utilities.interfaces.assets.icleanable import ICleanable


@runtime_checkable
class IFrameACLCommandConfiguration(ICleanable, Protocol):
    """
    Typed frame command ACL configuration contract.

    Contract:
        - Carries one command-policy profile identity/version pair.
        - Represents the command-side sibling inside a frame ACL bundle.
        - Is policy/configuration data only; it does not execute commands or
          validate descriptor truth by itself.
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

    def clone(self) -> "IFrameACLCommandConfiguration":
        """
        Return a detached configuration copy.

        Returns:
            IFrameACLCommandConfiguration: Detached configuration copy.
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
            profile: IFrameACLCommandProfile,
            *,
            precision_profile: Optional[IFrameACLCommandProfile] = None,
    ) -> None:
        """
        Replace the base and optional precision profiles on the mutable config.

        Returns:
            None.
        """
        ...
