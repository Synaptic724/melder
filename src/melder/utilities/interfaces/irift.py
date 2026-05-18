from typing import Dict, Optional, Protocol, Tuple, runtime_checkable
from melder.aether.nexus.rift.projection.codegen_projection import CodegenProjection
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.iconduit import IConduit
from melder.utilities.interfaces.iframelinkcontract import IFrameLinkContract
from melder.utilities.interfaces.iriftconfiguration import IRiftConfiguration
from melder.utilities.interfaces.iriftgate import IRiftGate
from melder.utilities.interfaces.iriftspace import IRiftSpace

@runtime_checkable
class IRift(ICleanable, Protocol):
    """
    Interface for the public live Rift runtime object.

    Purpose:
        Define the stable live-session contract exposed by the Nexus/Rift AR
        layer without binding callers to the concrete `Rift` implementation.

    Contract:
        - Represents one registered or registerable live Rift session.
        - Owns exactly one primary `IRiftSpace`.
        - Tracks frame-link contract state for engaged target frames.
        - Exposes Nexus-managed frame access and frame-link lifecycle methods.
        - Exposes only runtime-facing accessors and commands; it does not own
          global Nexus configuration or frame-descriptor publication.
    """

    @property
    def id(self) -> str:
        """
        Return the stable identifier for this Rift instance.

        Contract:
            - Stable for the lifetime of the Rift.
            - Used by Nexus registry, room-memory metadata, and frame-link
              ownership surfaces.
        """
        ...

    @property
    def rift_name(self) -> Optional[str]:
        """
        Return the human-readable Rift name, if one has been assigned.

        Contract:
            - May be `None` when the Rift was created without a stable name.
            - When present, the value is metadata only and does not replace the
              canonical `id`.
        """
        ...

    @property
    def configuration(self) -> IRiftConfiguration:
        """
        Return the configuration object that defines this Rift's runtime policy.

        Contract:
            - Returns the finalized per-Rift configuration snapshot owned by
              this session.
            - The returned configuration defines room posture and validation
              behavior for this Rift.
        """
        ...

    def list_assigned_frame_names(self) -> Tuple[str, ...]:
        """
        Return the frame names currently assigned to this Rift.

        Contract:
            - Returns only currently engaged frame names.
            - Order is stable for the current runtime snapshot.
        """
        ...

    def get_frame_link_contract(self, frame_name: str) -> IFrameLinkContract:
        """
        Return the per-frame contract object for one engaged target frame.

        Args:
            frame_name:
                Engaged target frame name.

        Returns:
            IFrameLinkContract: Rift-local contract object for the selected
            frame.

        Raises:
            ValueError:
                If the frame name is empty or not currently engaged on this
                Rift.
        """
        ...

    def get_selected_contract_names(self, frame_name: str) -> Dict[str, str]:
        """
        Return the selected view/command/codegen contract names for one engaged
        target frame.

        Args:
            frame_name:
                Engaged target frame name.

        Returns:
            Dict[str, str]: Detached mapping containing the selected
            `view`, `command`, and `codegen` contract names for the frame.
        """
        ...

    @property
    def space(self) -> IRiftSpace:
        """
        Return the one owned RiftSpace for this Rift.

        Contract:
            - Returns the live owned primary room.
            - The room is cleaned with the Rift and is not a detached copy.
        """
        ...

    @property
    def metadata(self) -> Dict[str, object]:
        """
        Return the metadata mapping associated with this Rift.

        Contract:
            - Returns Rift-owned metadata for this live session.
            - Callers must treat the returned mapping as descriptive runtime
              state rather than a mutation API.
        """
        ...

    @property
    def is_registered(self) -> bool:
        """
        Return whether this Rift has been registered with Nexus.

        Contract:
            - True means the Rift is present in the live Nexus registry.
            - False means the Rift exists locally but is not yet or no longer
              registered.
        """
        ...

    @property
    def is_active(self) -> bool:
        """
        Return whether this Rift is currently marked active.

        Contract:
            - Active state is session/runtime metadata.
            - It does not by itself imply any specific frame assignment count.
        """
        ...

    @property
    def rift_gate(self) -> IRiftGate:
        """
        Return the Rift-owned gate for this runtime instance.

        Contract:
            - Returns the live gate coordinating Rift admission/drain behavior.
            - The gate is owned by the Rift and cleaned with it.
        """
        ...

    def _get_required_codegen_projection(self, frame_name: str) -> CodegenProjection:
        """
        Return the required codegen projection for one frame.

        Args:
            frame_name:
                Target frame name.

        Returns:
            CodegenProjection: Installed codegen projection for the frame.

        Raises:
            ValueError:
                If the frame has no installed codegen projection in this Rift.
        """
        ...

    def refresh_runtime_projections(
            self,
            frame_names: Optional[Tuple[str, ...]] = None,
    ) -> None:
        """
        Refresh the Rift-owned projection registry for the supplied frames or
        for all currently assigned frames when omitted.
        """
        ...

    def mark_registered(self) -> None:
        """
        Mark this Rift as registered with its owning Nexus.

        Contract:
            - Updates only the Rift-local registration flag.
            - Does not create or destroy the Nexus registry entry by itself.

        Returns:
            None.
        """
        ...

    def mark_active(self) -> None:
        """
        Mark this Rift as active.

        Contract:
            - Updates only the Rift-local active flag.
            - Does not by itself attach frames or mutate room state.

        Returns:
            None.
        """
        ...

    def mark_inactive(self) -> None:
        """
        Mark this Rift as inactive.

        Contract:
            - Updates only the Rift-local active flag.
            - Does not remove engaged frames or clean the owned room.

        Returns:
            None.
        """
        ...

    def create_frame_link(self, frame_name: str) -> None:
        """
        Validate and engage one target frame for this Rift.

        Contract:
            - Validates the target frame through the owning Nexus policy and
              runtime-posture gates.
            - Creates or reuses a Rift-local frame-link contract for the
              selected frame.
            - May refresh the attached room/viewer state after engagement.

        Args:
            frame_name:
                Target frame name to engage.

        Returns:
            None.
        """
        ...

    def get_nexus_frame(self, frame_name: Optional[str] = None) -> IConduit:
        """
        Return one rooted Nexus conduit accessible through this Rift.

        Args:
            frame_name:
                Optional target frame name. When omitted, the implementation may
                apply the Rift's current default-frame rules.

        Returns:
            IConduit: Rooted conduit for the resolved Nexus-managed frame.
        """
        ...

    def create_nexus_frame(
            self,
            frame_name: Optional[str] = None,
            root_conduit_name: str = "root",
            immutable: bool = False,
    ) -> IConduit:
        """
        Create and return one rooted Nexus conduit through this Rift's Nexus
        access surface.

        Args:
            frame_name:
                Optional target Nexus-managed frame name.
            root_conduit_name:
                Root conduit name to use when creating the frame.
            immutable:
                Optional caller posture flag forwarded into the creation path.

        Returns:
            IConduit: Rooted conduit for the newly created Nexus-managed frame.
        """
        ...

    def list_accessible_nexus_frame_names(self) -> Tuple[str, ...]:
        """
        Return the Nexus frame names this Rift may currently access.

        Returns:
            Tuple[str, ...]: Accessible Nexus-managed frame names.
        """
        ...

    def list_accessible_non_nexus_frame_names(self) -> Tuple[str, ...]:
        """
        Return the published non-Nexus frame names this Rift may currently
        access.

        Returns:
            Tuple[str, ...]: Accessible published non-Nexus frame names.
        """
        ...

    def on_nexus_frame_disposed(self, frame_name: str) -> None:
        """
        Notify this Rift that one accessible Nexus frame has been disposed.

        Args:
            frame_name:
                Disposed Nexus-managed frame name.

        Contract:
            - Allows the Rift to react to downstream frame disposal.
            - Does not require the Rift to own the frame lifecycle itself.

        Returns:
            None.
        """
        ...
