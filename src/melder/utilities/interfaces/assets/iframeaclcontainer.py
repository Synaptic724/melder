import threading
from threading import RLock
from types import ModuleType
from typing import runtime_checkable, Type, Protocol, Optional, List, Union, Dict, Any, Iterable, Iterator, Callable, \
    Tuple, Mapping, Set, Sequence, Self

from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.dev_ops.spell_system_states.spell_state_change_reason import SpellStateChangeReason
from melder.spellbook.existence.existence import Existence
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


from melder.utilities.interfaces.assets.icleanable import ICleanable

@runtime_checkable
class IFrameACLContainer(ICleanable, Protocol):
    """
    Frame-local ACL container contract used by the builder boundary.
    """

    frame_name: str
    frame_acl_configuration: IFrameACLConfiguration
    frame_acl_builder: IFrameACLBuilder
    frame_acl_profile_builder: IFrameACLProfileBuilder
    named_configurations_by_name: Dict[str, IFrameACLConfiguration]
    frame_acl_set_compatibility_validator: IFrameACLSetCompatibilityValidator
    view_chain_names: List[str]
    command_chain_names: List[str]
    codegen_chain_names: List[str]

    def install_configuration(
            self,
            configuration: IFrameACLConfiguration,
            *,
            contract_name: str = "default",
    ) -> None:
        """
        Install one validated ACL configuration into the container.

        Returns:
            None.
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

    def list_named_configuration_names(self) -> List[str]:
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
