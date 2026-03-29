from typing import Dict, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.interfaces.interfaces import IRiftEventConfiguration, IRiftSpace
from melder.aether.nexus.rift_space.rift_event_configuration import RiftEventConfiguration


class RiftSpace(Cleanable, IRiftSpace):
    """
    Internal

    Base room/workspace class for `Rift`.

    Purpose:
        Provide the base room/workspace contract for `Rift`.

    Contract:
        - Owns stable room identity and room-local metadata.
        - Keeps a room name for paired lookup through the owning Rift.
        - Carries a room-kind marker (`base`, `static`, `dynamic`).
        - Carries a room-level event configuration seam for future action and
          memory enrichment.
        - Does not yet implement full action history, memory points,
          checkpoints, or disposition semantics.

    Lifecycle:
        Owned by a `Rift`. Cleanup clears room-local fields and cleans
        the attached `RiftEventConfiguration`.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_space_id",
        "_space_name",
        "_owner_rift_id",
        "_space_kind",
        "_metadata",
        "_event_configuration",
    ]

    def __init__(
            self,
            owner_rift_id: str,
            *,
            space_name: Optional[str] = None,
            space_kind: str = "base",
            metadata: Optional[Dict[str, object]] = None,
            event_configuration: Optional[IRiftEventConfiguration] = None,
            space_id: Optional[str] = None,
    ) -> None:
        """
        Internal

        Initialize the base room.

        Args:
            owner_rift_id:
                Canonical owning Rift id.
            space_name:
                Optional stable room name.
            space_kind:
                Room-kind discriminator.
            metadata:
                Extensible room-local metadata.
            event_configuration:
                Optional room-level event configuration.
            space_id:
                Optional explicit room id. When omitted a new id is created.

        Returns:
            None.

        Raises:
            ValueError: If `owner_rift_id` is empty.
        """
        super().__init__()
        if not owner_rift_id:
            raise ValueError("owner_rift_id cannot be empty.")

        self._space_id: str = space_id or IDBuilder.create_id()
        self._space_name: Optional[str] = space_name
        self._owner_rift_id: str = owner_rift_id
        self._space_kind: str = space_kind
        self._metadata: Dict[str, object] = dict(metadata) if metadata else {}
        self._event_configuration: IRiftEventConfiguration = (
            event_configuration if event_configuration is not None else RiftEventConfiguration()
        )

    def cleanup(self) -> None:
        """
        Internal

        Idempotently cleanup room-local state and the attached event
        configuration.

        Contract:
            - Cleans the owned event configuration before dropping references.
            - Clears room identity metadata and room-local metadata maps.
            - Leaves the room unusable after cleanup.

        Returns:
            None.
        """
        if self._cleaned:
            return

        self._cleaned = True
        self._event_configuration.cleanup()
        self._space_name = None
        self._owner_rift_id = None
        self._space_kind = None
        self._metadata.clear()
        self._metadata = None
        self._event_configuration = None
        self._space_id = None

    @property
    def space_id(self) -> str:
        """
        Purpose:
            Return the canonical room id.

        Returns:
            str: The room id.
        """
        self.check_cleaned()
        return self._space_id

    @property
    def space_name(self) -> Optional[str]:
        """
        Purpose:
            Return the optional stable room name.

        Returns:
            Optional[str]: Room name, if one exists.
        """
        self.check_cleaned()
        return self._space_name

    @property
    def owner_rift_id(self) -> str:
        """
        Purpose:
            Return the canonical owning Rift id.

        Returns:
            str: Owning Rift id.
        """
        self.check_cleaned()
        return self._owner_rift_id

    @property
    def space_kind(self) -> str:
        """
        Purpose:
            Return the room-kind discriminator.

        Returns:
            str: Room kind label.
        """
        self.check_cleaned()
        return self._space_kind

    @property
    def metadata(self) -> Dict[str, object]:
        """
        Purpose:
            Return the room-local metadata map.

        Returns:
            Dict[str, object]: Extensible room metadata.
        """
        self.check_cleaned()
        return self._metadata

    @property
    def event_configuration(self) -> IRiftEventConfiguration:
        """
        Purpose:
            Return the room-level event configuration.

        Contract:
            This is the room-local configuration seam for future action/memory
            enrichment, not a global ARS configuration object.

        Returns:
            IRiftEventConfiguration: The room event configuration object.
        """
        self.check_cleaned()
        return self._event_configuration
