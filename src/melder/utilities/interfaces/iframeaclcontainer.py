from typing import TYPE_CHECKING, Mapping, Protocol, Sequence, runtime_checkable
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.iframeaclbuilder import IFrameACLBuilder
from melder.utilities.interfaces.iframeaclcodegenconfiguration import IFrameACLCodegenConfiguration
from melder.utilities.interfaces.iframeaclcommandconfiguration import IFrameACLCommandConfiguration
from melder.utilities.interfaces.iframeaclconfiguration import IFrameACLConfiguration
from melder.utilities.interfaces.iframeaclprofilebuilder import IFrameACLProfileBuilder
from melder.utilities.interfaces.iframeaclviewconfiguration import IFrameACLViewConfiguration

if TYPE_CHECKING:
    from melder.nexus.acl.validator.compatibility.frame_acl_set_compatibility_validator import (
        FrameACLSetCompatibilityValidator,
    )

if TYPE_CHECKING:
    from melder.nexus.acl.validator.compatibility.frame_acl_set_compatibility_validator import (
        FrameACLSetCompatibilityValidator,
    )

@runtime_checkable
class IFrameACLContainer(ICleanable, Protocol):
    """
    Frame-local ACL container contract used by the builder boundary.
    """

    @property
    def frame_name(self) -> str:
        """
        Return the owning frame name.
        """
        ...

    @property
    def frame_acl_configuration(self) -> IFrameACLConfiguration:
        """
        Return the assembled default ACL configuration snapshot.
        """
        ...

    @property
    def frame_acl_builder(self) -> IFrameACLBuilder:
        """
        Return the unique builder object for this frame container.
        """
        ...

    @property
    def frame_acl_profile_builder(self) -> IFrameACLProfileBuilder:
        """
        Return the shared ACL profile builder/library for this frame container.
        """
        ...

    @property
    def named_configurations_by_name(self) -> Mapping[str, IFrameACLConfiguration]:
        """
        Return assembled same-name ACL snapshots keyed by contract name.
        """
        ...

    @property
    def frame_acl_set_compatibility_validator(
            self,
    ) -> "FrameACLSetCompatibilityValidator":
        """
        Return the frame-scoped ACL set compatibility validator.
        """
        ...

    @property
    def view_chain_names(self) -> Sequence[str]:
        """
        Return named view-chain registry keys.
        """
        ...

    @property
    def command_chain_names(self) -> Sequence[str]:
        """
        Return named command-chain registry keys.
        """
        ...

    @property
    def codegen_chain_names(self) -> Sequence[str]:
        """
        Return named codegen-chain registry keys.
        """
        ...

    def install_configuration(
            self,
            configuration: IFrameACLConfiguration,
            *,
            contract_name: str = "default",
    ) -> IFrameACLConfiguration:
        """
        Install one validated ACL configuration into the container.

        Returns:
            IFrameACLConfiguration: Newly assembled current ACL snapshot.
        """
        ...

    def get_named_configuration(
            self,
            contract_name: str = "default",
    ) -> IFrameACLConfiguration:
        """
        Return one named ACL configuration for this frame.
        """
        ...

    def list_named_configuration_names(self) -> Sequence[str]:
        """
        Return all registered ACL contract names for this frame.
        """
        ...

    def register_named_configuration(
            self,
            configuration: IFrameACLConfiguration,
            *,
            contract_name: str = "default",
    ) -> IFrameACLConfiguration:
        """
        Register one additional named ACL configuration for this frame.
        """
        ...

    def get_current_view_configuration(
            self,
            contract_name: str = "default",
    ) -> IFrameACLViewConfiguration:
        """
        Return the current selected view configuration for one contract.
        """
        ...

    def get_current_command_configuration(
            self,
            contract_name: str = "default",
    ) -> IFrameACLCommandConfiguration:
        """
        Return the current selected command configuration for one contract.
        """
        ...

    def get_current_codegen_configuration(
            self,
            contract_name: str = "default",
    ) -> IFrameACLCodegenConfiguration:
        """
        Return the current selected codegen configuration for one contract.
        """
        ...

    def create_new_from_view_configuration(
            self,
            configuration_id: str,
            *,
            contract_name: str = "default",
            reason: str,
    ) -> IFrameACLViewConfiguration:
        """
        Create a new view draft copied from one existing view revision.
        """
        ...

    def create_new_from_command_configuration(
            self,
            configuration_id: str,
            *,
            contract_name: str = "default",
            reason: str,
    ) -> IFrameACLCommandConfiguration:
        """
        Create a new command draft copied from one existing command revision.
        """
        ...

    def create_new_from_codegen_configuration(
            self,
            configuration_id: str,
            *,
            contract_name: str = "default",
            reason: str,
    ) -> IFrameACLCodegenConfiguration:
        """
        Create a new codegen draft copied from one existing codegen revision.
        """
        ...

    def insert_head_view_configuration(
            self,
            configuration: IFrameACLViewConfiguration,
            *,
            contract_name: str = "default",
            select_as_current: bool,
    ) -> IFrameACLViewConfiguration:
        """
        Insert one view configuration revision at the head of a named chain.
        """
        ...

    def insert_head_command_configuration(
            self,
            configuration: IFrameACLCommandConfiguration,
            *,
            contract_name: str = "default",
            select_as_current: bool,
    ) -> IFrameACLCommandConfiguration:
        """
        Insert one command configuration revision at the head of a named chain.
        """
        ...

    def insert_head_codegen_configuration(
            self,
            configuration: IFrameACLCodegenConfiguration,
            *,
            contract_name: str = "default",
            select_as_current: bool,
    ) -> IFrameACLCodegenConfiguration:
        """
        Insert one codegen configuration revision at the head of a named chain.
        """
        ...

    def build_selected_configuration(
            self,
            *,
            view_contract_name: str = "default",
            command_contract_name: str = "default",
            codegen_contract_name: str = "default",
            reason: str = "assembled_selection",
    ) -> IFrameACLConfiguration:
        """
        Assemble one full ACL snapshot from selected family chains.
        """
        ...

    def select_current_view_configuration(
            self,
            configuration_id: str,
            *,
            contract_name: str = "default",
    ) -> IFrameACLViewConfiguration:
        """
        Select one existing view configuration revision as current.
        """
        ...

    def select_current_command_configuration(
            self,
            configuration_id: str,
            *,
            contract_name: str = "default",
    ) -> IFrameACLCommandConfiguration:
        """
        Select one existing command configuration revision as current.
        """
        ...

    def select_current_codegen_configuration(
            self,
            configuration_id: str,
            *,
            contract_name: str = "default",
    ) -> IFrameACLCodegenConfiguration:
        """
        Select one existing codegen configuration revision as current.
        """
        ...

    def rollback_view_configuration(
            self,
            configuration_id: str,
            *,
            contract_name: str = "default",
    ) -> IFrameACLViewConfiguration:
        """
        Roll current view selection back to one historical revision.
        """
        ...

    def rollback_command_configuration(
            self,
            configuration_id: str,
            *,
            contract_name: str = "default",
    ) -> IFrameACLCommandConfiguration:
        """
        Roll current command selection back to one historical revision.
        """
        ...

    def rollback_codegen_configuration(
            self,
            configuration_id: str,
            *,
            contract_name: str = "default",
    ) -> IFrameACLCodegenConfiguration:
        """
        Roll current codegen selection back to one historical revision.
        """
        ...



