from typing import Dict, Optional, Protocol, Tuple, runtime_checkable
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.iriftconfiguration import IRiftConfiguration
from melder.utilities.interfaces.iriftgate import IRiftGate
from melder.utilities.interfaces.iriftspace import IRiftSpace

@runtime_checkable
class IRift(ICleanable, Protocol):
    """
    Interface for the public live Rift runtime object.
    """

    @property
    def id(self) -> str:
        """
        Return the stable identifier for this Rift instance.
        """
        ...

    @property
    def rift_name(self) -> Optional[str]:
        """
        Return the human-readable Rift name, if one has been assigned.
        """
        ...

    @property
    def configuration(self) -> IRiftConfiguration:
        """
        Return the configuration object that defines this Rift's runtime policy.
        """
        ...

    def list_assigned_frame_names(self) -> Tuple[str, ...]:
        """
        Return the frame names currently assigned to this Rift.
        """
        ...

    def get_frame_link_contract(self, frame_name: str) -> object:
        """
        Return the per-frame contract object for one engaged target frame.
        """
        ...

    def get_selected_contract_names(self, frame_name: str) -> Dict[str, str]:
        """
        Return the selected view/command/codegen contract names for one engaged
        target frame.
        """
        ...

    @property
    def space(self) -> IRiftSpace:
        """
        Return the one owned RiftSpace for this Rift.
        """
        ...

    @property
    def metadata(self) -> Dict[str, object]:
        """
        Return the metadata mapping associated with this Rift.
        """
        ...

    @property
    def is_registered(self) -> bool:
        """
        Return whether this Rift has been registered with Nexus.
        """
        ...

    @property
    def is_active(self) -> bool:
        """
        Return whether this Rift is currently marked active.
        """
        ...

    @property
    def rift_gate(self) -> IRiftGate:
        """
        Return the Rift-owned gate for this runtime instance.
        """
        ...

    def _get_required_codegen_projection(self, frame_name: str) -> "CodegenProjection":
        """
        Return the required codegen projection for one frame.
        """
        ...

    def mark_registered(self) -> None:
        """
        Mark this Rift as registered with its owning Nexus.

        Returns:
            None.
        """
        ...

    def mark_active(self) -> None:
        """
        Mark this Rift as active.

        Returns:
            None.
        """
        ...

    def mark_inactive(self) -> None:
        """
        Mark this Rift as inactive.

        Returns:
            None.
        """
        ...

    def create_frame_link(self, frame_name: str) -> None:
        """
        Validate and engage one target frame for this Rift.

        A successful frame-link operation updates the Rift-local frame contract
        and may refresh the attached viewer for the owned space.
        """
        ...

    def get_nexus_frame(self, frame_name: Optional[str] = None) -> "IConduit":
        """
        Return one rooted Nexus conduit accessible through this Rift.
        """
        ...

    def create_nexus_frame(
            self,
            frame_name: Optional[str] = None,
            root_conduit_name: str = "root",
            immutable: bool = False,
    ) -> "IConduit":
        """
        Create and return one rooted Nexus conduit through this Rift's Nexus access surface.
        """
        ...

    def list_accessible_nexus_frame_names(self) -> Tuple[str, ...]:
        """
        Return the Nexus frame names this Rift may currently access.
        """
        ...

    def list_accessible_non_nexus_frame_names(self) -> Tuple[str, ...]:
        """
        Return the published non-Nexus frame names this Rift may currently access.
        """
        ...

    def on_nexus_frame_disposed(self, frame_name: str) -> None:
        """
        Notify this Rift that one accessible Nexus frame has been disposed.

        Returns:
            None.
        """
        ...
