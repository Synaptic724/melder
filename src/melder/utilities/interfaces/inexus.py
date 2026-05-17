from typing import Any, Dict, List, Optional, Protocol, Tuple, runtime_checkable
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.iconduit import IConduit
from melder.utilities.interfaces.iframeaclconfiguration import IFrameACLConfiguration
from melder.utilities.interfaces.inexusconfiguration import INexusConfiguration
from melder.utilities.interfaces.irift import IRift
from melder.utilities.interfaces.iriftconfiguration import IRiftConfiguration
from melder.utilities.interfaces.iriftgate import IRiftGate
from melder.utilities.interfaces.iriftgatecontroller import IRiftGateController

@runtime_checkable
class INexus(ICleanable, Protocol):
    """
    Interface for the Nexus singleton root.
    """

    @property
    def id(self) -> str:
        """
        Return the stable identifier for this Nexus instance.
        """
        ...

    @property
    def configuration(self) -> INexusConfiguration:
        """
        Return the active Nexus configuration object.
        """
        ...

    @property
    def is_configured(self) -> bool:
        """
        Return whether Nexus has been configured with a finalized configuration.
        """
        ...

    @property
    def is_enabled(self) -> bool:
        """
        Return whether Nexus is currently enabled for Rift management operations.
        """
        ...

    @property
    def rift_gate_controller(self) -> IRiftGateController:
        """
        Return the Nexus-owned Rift gate controller.
        """
        ...

    def create_system_configuration(self) -> INexusConfiguration:
        """
        Create and return a new mutable Nexus configuration object.
        """
        ...

    def enable(
            self,
            configuration: Optional[INexusConfiguration] = None,
    ) -> None:
        """
        Enable Nexus, optionally binding a configuration as part of the enable flow.

        Returns:
            None.
        """
        ...

    def disable(self) -> None:
        """
        Disable Nexus and stop further Rift operations until re-enabled.

        Returns:
            None.
        """
        ...

    def create_rift_configuration(
            self,
            profile_name: Optional[str] = None,
    ) -> IRiftConfiguration:
        """
        Create and return a new Rift configuration, optionally seeded from a named profile.
        """
        ...

    def register_rift_profile(
            self,
            name: str,
            configuration: IRiftConfiguration,
    ) -> None:
        """
        Register one reusable Rift configuration profile under a stable name.

        Returns:
            None.
        """
        ...

    def create_rift(
            self,
            *,
            configuration: Optional[IRiftConfiguration] = None,
            rift_name: Optional[str] = None,
            rift_id: Optional[str] = None,
            space_id: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
            creation_token: Optional[str] = None,
            logger: Optional[Any] = None,
    ) -> IRift:
        """
        Create, configure, and return one Rift through the Nexus root.
        """
        ...

    def add_rift(self, rift: IRift) -> None:
        """
        Register one already-created Rift instance with the Nexus.

        Returns:
            None.
        """
        ...

    def get_rift(
            self,
            rift_id: str,
            access_token: Optional[str] = None,
    ) -> IRift:
        """
        Return one registered Rift by id, applying access checks as needed.
        """
        ...

    def get_rift_by_name(
            self,
            rift_name: str,
            access_token: Optional[str] = None,
    ) -> IRift:
        """
        Return one registered Rift by its human-readable name.
        """
        ...

    def has_rift(self, rift_id: str) -> bool:
        """
        Return whether a Rift with the given id is currently registered.
        """
        ...

    def remove_rift(self, rift_id: str) -> None:
        """
        Remove one Rift registration by id.

        Returns:
            None.
        """
        ...

    def list_rift_ids(self) -> List[str]:
        """
        Return the currently registered Rift identifiers.
        """
        ...

    def get_rift_gate(self, rift_id: str) -> Optional[IRiftGate]:
        """
        Return the registered Rift gate for one Rift id, if present.
        """
        ...

    def enable_rift_gate(self, rift_id: str) -> None:
        """
        Open one Rift gate by Rift id.
        """
        ...

    def disable_rift_gate(self, rift_id: str) -> None:
        """
        Close one Rift gate by Rift id.
        """
        ...

    def close_and_wait_rift(
            self,
            rift_id: str,
            timeout: float = 30.0,
            interval: float = 0.1,
    ) -> None:
        """
        Terminally close and drain one Rift gate.
        """
        ...

    def count_active_rift_threads(self, rift_id: str) -> int:
        """
        Return active ticket count for one Rift gate.
        """
        ...

    def count_active_rift_threads_total(self) -> int:
        """
        Return active ticket count summed across all Rift gates.
        """
        ...

    def enable_all_rift_gates(self) -> None:
        """
        Open every registered Rift gate.
        """
        ...

    def disable_all_rift_gates(self) -> None:
        """
        Close every registered Rift gate.
        """
        ...

    def set_rift_gate_entry_mode(self, rift_id: str, entry_mode: str) -> None:
        """
        Set the admission mode for one registered Rift gate.
        """
        ...

    def set_all_rift_gate_entry_mode(self, entry_mode: str) -> None:
        """
        Set the admission mode for every registered Rift gate.
        """
        ...

    def get_nexus_frame_for_rift(
            self,
            rift_id: str,
            frame_name: Optional[str] = None,
    ) -> IConduit:
        """
        Return one existing accessible rooted Nexus conduit for the specified Rift.
        """
        ...

    def create_nexus_frame_for_rift(
            self,
            rift_id: str,
            frame_name: Optional[str] = None,
            root_conduit_name: str = "root",
            immutable: bool = False,
    ) -> IConduit:
        """
        Create and return one rooted Nexus conduit scoped for the specified Rift.
        """
        ...

    def authorize_frame_link_for_rift(self, rift_id: str, frame_name: str) -> bool:
        """
        Authorize one Rift frame-link request against Nexus-managed frame policy.
        """
        ...

    def list_accessible_nexus_frame_names(self, rift_id: str) -> Tuple[str, ...]:
        """
        Return the Nexus frame names currently accessible to the specified Rift.
        """
        ...

    def get_named_frame_acl_configuration(
            self,
            frame_name: str,
            contract_name: str = "default",
    ) -> IFrameACLConfiguration:
        """
        Return one named frame ACL configuration for a frame.
        """
        ...

    def list_named_frame_acl_configuration_names(
            self,
            frame_name: str,
    ) -> List[str]:
        """
        Return all named ACL contract names for a frame.
        """
        ...

    def register_named_frame_acl_configuration(
            self,
            frame_name: str,
            configuration: IFrameACLConfiguration,
            *,
            contract_name: str = "default",
    ) -> IFrameACLConfiguration:
        """
        Register one named ACL configuration for a frame.
        """
        ...

    def insert_head_frame_acl_configuration(
            self,
            frame_name: str,
            configuration: IFrameACLConfiguration,
            *,
            select_as_current: bool = True,
    ) -> IFrameACLConfiguration:
        """
        Install one replacement revision into the selected same-name ACL contract.
        """
        ...

    def get_current_view_frame_acl_configuration(
            self,
            frame_name: str,
            *,
            contract_name: str = "default",
    ) -> object:
        """
        Return the current selected view ACL configuration for one frame/contract.
        """
        ...

    def get_current_command_frame_acl_configuration(
            self,
            frame_name: str,
            *,
            contract_name: str = "default",
    ) -> object:
        """
        Return the current selected command ACL configuration for one frame/contract.
        """
        ...

    def get_current_codegen_frame_acl_configuration(
            self,
            frame_name: str,
            *,
            contract_name: str = "default",
    ) -> object:
        """
        Return the current selected codegen ACL configuration for one frame/contract.
        """
        ...

    def get_current_frame_acl_configuration(
            self,
            frame_name: str,
            *,
            view_contract_name: str = "default",
            command_contract_name: str = "default",
            codegen_contract_name: str = "default",
    ) -> IFrameACLConfiguration:
        """
        Return one assembled ACL snapshot for the selected family contracts.
        """
        ...

    def get_current_view_frame_acl_configuration(
            self,
            frame_name: str,
            *,
            contract_name: str = "default",
    ) -> object:
        """
        Return the current selected view ACL configuration for one frame/contract.
        """
        ...

    def get_current_command_frame_acl_configuration(
            self,
            frame_name: str,
            *,
            contract_name: str = "default",
    ) -> object:
        """
        Return the current selected command ACL configuration for one frame/contract.
        """
        ...

    def get_current_codegen_frame_acl_configuration(
            self,
            frame_name: str,
            *,
            contract_name: str = "default",
    ) -> object:
        """
        Return the current selected codegen ACL configuration for one frame/contract.
        """
        ...

    def check_for_aetheric_frame(self, frame_name: str) -> None:
        """
        Validate that one named Aetheric frame exists and is accessible.

        Returns:
            None.
        """
        ...
