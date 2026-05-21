from typing import Dict, Optional, Protocol, Tuple, runtime_checkable
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.iaethericframe import IAethericFrame
from melder.utilities.interfaces.iconduit import IConduit
from melder.utilities.interfaces.inexusframeconfiguration import INexusFrameConfiguration

@runtime_checkable
class INexusFrameManager(ICleanable, Protocol):
    """
    Interface for the Nexus-managed frame authoring facade.

    Purpose:
        Expose the authored-frame creation contract used by collaborators that
        should depend on the frame-manager capability surface without importing
        the concrete runtime implementation directly.

    Contract:
        - Realizes only Nexus-managed frames that satisfy the fixed
          dynamic/AI-native/Rift-enabled posture contract.
        - Consumes authored `INexusFrameConfiguration` objects as immutable
          inputs to frame realization.
        - Returns rooted `IConduit` objects for the realized Nexus-managed
          workspace.
        - Exposes authoritative manager-owned frame existence and listing
          surfaces.
        - Exposes Rift-scoped frame access, creation, and cleanup-routing
          surfaces used by the public Nexus facade.
    """

    @property
    def id(self) -> str:
        """
        Return the stable manager identifier.
        """
        ...

    def exists(self, frame_name: str) -> bool:
        """
        Return whether the manager currently tracks the named frame.
        """
        ...

    def list_frame_names(self) -> Tuple[str, ...]:
        """
        Return the currently managed frame names in sorted order.
        """
        ...

    def create_dynamic_frame(
            self,
            frame_name: str,
            *,
            immutable: bool = False,
            metadata: Optional[Dict[str, object]] = None,
            root_conduit_name: str = "root",
    ) -> IConduit:
        """
        Create one rooted dynamic Nexus-managed conduit directly.
        """
        ...

    def create(
            self,
            configuration: INexusFrameConfiguration,
    ) -> IConduit:
        """
        Realize one rooted Nexus-managed conduit from authored configuration.

        Returns:
            IConduit: Root conduit for the realized Nexus-managed workspace.
        """
        ...

    def remove(self, frame_name: str) -> None:
        """
        Remove one managed frame when policy and live-use checks allow it.
        """
        ...

    def get_frame_for_rift(
            self,
            rift_id: str,
            frame_name: Optional[str] = None,
    ) -> IAethericFrame:
        """
        Return the managed frame currently accessible to the specified Rift.
        """
        ...

    def create_frame_for_rift(
            self,
            rift_id: str,
            frame_name: Optional[str] = None,
            *,
            root_conduit_name: str = "root",
            immutable: bool = False,
    ) -> IConduit:
        """
        Create and return one rooted managed frame for the specified Rift.
        """
        ...

    def authorize_frame_link_for_rift(self, rift_id: str, frame_name: str) -> bool:
        """
        Return whether the specified Rift may link to the named managed frame.
        """
        ...

    def list_accessible_frame_names_for_rift(self, rift_id: str) -> Tuple[str, ...]:
        """
        Return the managed frame names currently accessible to the specified Rift.
        """
        ...

    def get_frame_names_to_cleanup_for_removed_rift(
            self,
            rift_id: str,
    ) -> Tuple[str, ...]:
        """
        Return managed frame names that should be cleaned after the Rift is removed.
        """
        ...

    def handle_aether_frame_disposal(self, frame_name: str) -> bool:
        """
        Remove manager-owned bookkeeping for one externally disposed Aether frame.
        """
        ...

