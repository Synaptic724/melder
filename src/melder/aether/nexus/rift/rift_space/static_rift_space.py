from typing import Dict, Optional

from melder.aether.nexus.rift.rift_space.rift_space import RiftSpace
from melder.utilities.interfaces.interfaces import IStaticRiftSpace, IRiftEventConfiguration


class StaticRiftSpace(RiftSpace, IStaticRiftSpace):
    """
    Internal

    Purpose:
        Represent the lower-risk concrete room type.

    Contract:
        - Inherits all base room behavior.
        - Fixes `space_kind` to `static`.
        - Represents the lower-risk room surface where declared targets and a
          more stable local structure are the primary operational model.
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

        Initialize a static room.

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
            fixing the room kind to `static`.
        """
        super().__init__(
            owner_rift_id,
            space_name=space_name,
            space_kind="static",
            metadata=metadata,
            event_configuration=event_configuration,
            space_id=space_id,
        )
