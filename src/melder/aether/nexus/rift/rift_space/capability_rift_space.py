from typing import Dict, Optional

from melder.aether.nexus.rift.rift_space.rift_space import RiftSpace
from melder.utilities.interfaces.interfaces import (
    ICapabilityRiftSpace,
    IRiftEventConfiguration,
)


class CapabilityRiftSpace(RiftSpace, ICapabilityRiftSpace):
    """
    Internal

    Purpose:
        Represent the middle-ground concrete room type for restrictive
        pre-published execution workflows.

    Contract:
        - Inherits all base room behavior.
        - Fixes `space_kind` to `capability`.
        - Exists as a placeholder room type only in this cut; actual capability
          execution semantics are intentionally not implemented here.
    """

    def __init__(
            self,
            owner_rift_id: str,
            *,
            space_name: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
            event_configuration: Optional[IRiftEventConfiguration] = None,
            space_id: Optional[str] = None,
    ) -> None:
        """
        Internal

        Initialize a capability room.

        Args:
            owner_rift_id:
                Canonical owning Rift id.
            space_name:
                Optional stable room name.
            metadata:
                Extensible room metadata.
            event_configuration:
                Optional room-level event configuration.
            space_id:
                Optional explicit room id.

        Returns:
            None.

        Contract:
            Delegates all storage and lifecycle behavior to `RiftSpace` while
            fixing the room kind to `capability`.
        """
        super().__init__(
            owner_rift_id,
            space_name=space_name,
            space_kind="capability",
            metadata=metadata,
            event_configuration=event_configuration,
            space_id=space_id,
        )
