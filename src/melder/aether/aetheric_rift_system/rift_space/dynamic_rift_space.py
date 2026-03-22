from typing import Dict, Optional

from melder.aether.aetheric_rift_system.rift_space.rift_event_configuration import RiftEventConfiguration
from melder.aether.aetheric_rift_system.rift_space.rift_space import RiftSpace
from melder.utilities.interfaces.interfaces import IDynamicRiftSpace, IRiftEventConfiguration


class DynamicRiftSpace(RiftSpace, IDynamicRiftSpace):
    """
    Internal

    Purpose:
        Represent the richer concrete room type for dynamic/local-construction
        workflows.

    Contract:
        Inherits all base room behavior and fixes `space_kind` to `dynamic`.
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

        Initialize a dynamic room.

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
        """
        super().__init__(
            owner_rift_id,
            space_name=space_name,
            space_kind="dynamic",
            metadata=metadata,
            event_configuration=event_configuration,
            space_id=space_id,
        )
