from typing import Mapping, Optional, Protocol, Sequence, runtime_checkable
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.iframeaclcodegenprofile import IFrameACLCodegenProfile
from melder.utilities.interfaces.iframeaclcommandprofile import IFrameACLCommandProfile
from melder.utilities.interfaces.iframeaclprofile import IFrameACLProfile
from melder.utilities.interfaces.iframeaclruleset import IFrameACLRuleSet
from melder.utilities.interfaces.iframeaclviewprofile import IFrameACLViewProfile

@runtime_checkable
class IFrameACLProfileBuilder(ICleanable, Protocol):
    """
    Reusable ACL profile builder/library contract.
    """

    @property
    def version(self) -> str:
        """
        Return the current version string for this ACL profile builder/library.
        """
        ...

    @property
    def view_profiles_by_name(self) -> Mapping[str, IFrameACLViewProfile]:
        """
        Return a detached snapshot of the reusable view-profile registry.
        """
        ...

    @property
    def command_profiles_by_name(self) -> Mapping[str, IFrameACLCommandProfile]:
        """
        Return a detached snapshot of the reusable command-profile registry.
        """
        ...

    @property
    def codegen_profiles_by_name(self) -> Mapping[str, IFrameACLCodegenProfile]:
        """
        Return a detached snapshot of the reusable codegen-profile registry.
        """
        ...

    @property
    def view_precision_profiles_by_name(self) -> Mapping[str, IFrameACLViewProfile]:
        """
        Return a detached snapshot of the reusable view precision profiles.
        """
        ...

    @property
    def command_precision_profiles_by_name(self) -> Mapping[str, IFrameACLCommandProfile]:
        """
        Return a detached snapshot of the reusable command precision profiles.
        """
        ...

    @property
    def codegen_precision_profiles_by_name(self) -> Mapping[str, IFrameACLCodegenProfile]:
        """
        Return a detached snapshot of the reusable codegen precision profiles.
        """
        ...

    def register_view_profile(self, view_profile: IFrameACLViewProfile) -> None:
        """
        Register or replace one reusable view-side ACL profile.

        Returns:
            None.
        """
        ...

    def register_codegen_profile(
            self,
            codegen_profile: IFrameACLCodegenProfile,
    ) -> None:
        """
        Register or replace one reusable codegen-side ACL profile.

        Returns:
            None.
        """
        ...

    def register_command_profile(
            self,
            command_profile: IFrameACLCommandProfile,
    ) -> None:
        """
        Register or replace one reusable command-side ACL profile.

        Returns:
            None.
        """
        ...

    def register_view_precision_profile(
            self,
            precision_profile: IFrameACLViewProfile,
    ) -> None:
        """
        Register or replace one reusable view precision profile.

        Returns:
            None.
        """
        ...

    def register_command_precision_profile(
            self,
            precision_profile: IFrameACLCommandProfile,
    ) -> None:
        """
        Register or replace one reusable command precision profile.

        Returns:
            None.
        """
        ...

    def register_codegen_precision_profile(
            self,
            precision_profile: IFrameACLCodegenProfile,
    ) -> None:
        """
        Register or replace one reusable codegen precision profile.

        Returns:
            None.
        """
        ...

    def get_required_view_profile(
            self,
            profile_name: str,
    ) -> IFrameACLViewProfile:
        """
        Return one existing view-side profile or raise.

        Returns:
            IFrameACLViewProfile: Registered view profile.
        """
        ...

    def get_required_codegen_profile(
            self,
            profile_name: str,
    ) -> IFrameACLCodegenProfile:
        """
        Return one existing codegen-side profile or raise.

        Returns:
            IFrameACLCodegenProfile: Registered codegen profile.
        """
        ...

    def get_required_command_profile(
            self,
            profile_name: str,
    ) -> IFrameACLCommandProfile:
        """
        Return one existing command-side profile or raise.

        Returns:
            IFrameACLCommandProfile: Registered command profile.
        """
        ...

    def get_required_view_precision_profile(
            self,
            profile_name: str,
    ) -> IFrameACLViewProfile:
        """
        Return one existing view precision profile or raise.

        Returns:
            IFrameACLViewProfile: Registered view precision profile.
        """
        ...

    def get_required_command_precision_profile(
            self,
            profile_name: str,
    ) -> IFrameACLCommandProfile:
        """
        Return one existing command precision profile or raise.

        Returns:
            IFrameACLCommandProfile: Registered command precision profile.
        """
        ...

    def get_required_codegen_precision_profile(
            self,
            profile_name: str,
    ) -> IFrameACLCodegenProfile:
        """
        Return one existing codegen precision profile or raise.

        Returns:
            IFrameACLCodegenProfile: Registered codegen precision profile.
        """
        ...

    def list_view_profile_names(self) -> Sequence[str]:
        """
        Return the registered view-profile names.

        Returns:
            List[str]: Current view-profile names.
        """
        ...

    def list_codegen_profile_names(self) -> Sequence[str]:
        """
        Return the registered codegen-profile names.

        Returns:
            List[str]: Current codegen-profile names.
        """
        ...

    def list_command_profile_names(self) -> Sequence[str]:
        """
        Return the registered command-profile names.

        Returns:
            List[str]: Current command-profile names.
        """
        ...

    def list_view_precision_profile_names(self) -> Sequence[str]:
        """
        Return the registered view precision-profile names.

        Returns:
            List[str]: Current view precision-profile names.
        """
        ...

    def list_command_precision_profile_names(self) -> Sequence[str]:
        """
        Return the registered command precision-profile names.

        Returns:
            List[str]: Current command precision-profile names.
        """
        ...

    def list_codegen_precision_profile_names(self) -> Sequence[str]:
        """
        Return the registered codegen precision-profile names.

        Returns:
            List[str]: Current codegen precision-profile names.
        """
        ...

    def remove_view_profile(self, profile_name: str) -> bool:
        """
        Remove one view-side profile by name.

        Returns:
            bool: True when the profile existed and was removed.
        """
        ...

    def remove_codegen_profile(self, profile_name: str) -> bool:
        """
        Remove one codegen-side profile by name.

        Returns:
            bool: True when the profile existed and was removed.
        """
        ...

    def remove_command_profile(self, profile_name: str) -> bool:
        """
        Remove one command-side profile by name.

        Returns:
            bool: True when the profile existed and was removed.
        """
        ...

    def remove_view_precision_profile(self, profile_name: str) -> bool:
        """
        Remove one view precision profile by name.

        Returns:
            bool: True when the profile existed and was removed.
        """
        ...

    def remove_command_precision_profile(self, profile_name: str) -> bool:
        """
        Remove one command precision profile by name.

        Returns:
            bool: True when the profile existed and was removed.
        """
        ...

    def remove_codegen_precision_profile(self, profile_name: str) -> bool:
        """
        Remove one codegen precision profile by name.

        Returns:
            bool: True when the profile existed and was removed.
        """
        ...

    def create_profile(
            self,
            name: str,
            *,
            view_profile_name: str,
            command_profile_name: str,
            codegen_profile_name: str,
            view_override_ruleset: Optional[IFrameACLRuleSet] = None,
            command_override_ruleset: Optional[IFrameACLRuleSet] = None,
            codegen_override_ruleset: Optional[IFrameACLRuleSet] = None,
    ) -> IFrameACLProfile:
        """
        Compose one frame ACL profile from registered view/codegen profiles.

        Returns:
            IFrameACLProfile: Newly composed frame ACL profile.
        """
        ...

