from typing import Dict, Optional, Protocol, Sequence, Tuple, runtime_checkable

from melder.aether.nexus.configuration.rift_space_type import RiftSpaceType
from melder.utilities.interfaces.iframeaclconfiguration import IFrameACLConfiguration
from melder.utilities.interfaces.iframeprojectionset import IFrameProjectionSet
from melder.utilities.interfaces.inexus import INexus


@runtime_checkable
class IFrameACLManagerRiftSurface(Protocol):
    """
    Frame ACL manager surface consumed by `Rift`.
    """

    def _get_current_frame_acl_configuration(
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

    def _validate_frame_acl_configuration_against_descriptor(
            self,
            frame_name: str,
            configuration: IFrameACLConfiguration,
            descriptor: object,
    ) -> None:
        """
        Validate one frame ACL configuration against published descriptor truth.
        """
        ...


@runtime_checkable
class INexusRiftRuntimeSurface(INexus, Protocol):
    """
    Shared Nexus runtime surface consumed by `Rift`.
    """

    def _validate_target_frame_names(
            self,
            target_frame_names: Sequence[str],
    ) -> None:
        """
        Validate target frame names against Nexus allow/deny policy.
        """
        ...

    def _validate_target_frame_runtime_requirements(
            self,
            target_frame_name: str,
            requested_space_type: RiftSpaceType,
    ) -> None:
        """
        Validate one target frame against the requested Rift room posture.
        """
        ...

    def _get_required_frame_descriptor(self, frame_name: str) -> object:
        """
        Return the required published descriptor for one target frame.
        """
        ...

    def _validate_target_frame_budget(
            self,
            target_frame_names: Sequence[str],
    ) -> None:
        """
        Validate whether the supplied target frame names fit the active Nexus budget.
        """
        ...

    _frame_acl_manager: IFrameACLManagerRiftSurface

    def _increment_ref_count(
            self,
            ref_counts: Dict[str, int],
            target_frame_name: str,
    ) -> None:
        """
        Increment one dict-backed reference-count map.
        """
        ...

    _target_frame_ref_counts: Dict[str, int]

    def create_frame_projection_sets_for_rift(
            self,
            rift_id: str,
            *,
            frame_names: Optional[Sequence[str]] = None,
    ) -> Dict[str, IFrameProjectionSet]:
        """
        Build projection sets for the selected frames currently assigned to one Rift.
        """
        ...

    def list_accessible_non_nexus_frame_names(self, rift_id: str) -> Tuple[str, ...]:
        """
        Return the published non-Nexus frame names currently accessible to one Rift.
        """
        ...
