from typing import Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.interfaces.interfaces import IConduitDescriptorPayload


class ConduitRecord(Cleanable):
    """
    Internal

    Canonical Nexus record for one published conduit.

    Purpose:
        Hold only the directly targetable conduit information worth surfacing
        into Nexus in the first passive-ingest slice.

    Contract:
        - Root conduits publish by default.
        - Lesser conduits remain derived through lineage walking unless later
          promoted to normal.
        - Mutable through explicit Nexus upsert/remove paths only.
        - Cleanup is idempotent and clears all owned references.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "conduit_id",
        "root_conduit_id",
        "frame_name",
        "origin_spellbook_id",
        "payload",
    ]

    def __init__(
            self,
            *,
            conduit_id: str,
            root_conduit_id: str,
            frame_name: str,
            origin_spellbook_id: Optional[str],
            payload: IConduitDescriptorPayload,
    ) -> None:
        """
        Initialize one canonical conduit record.

        Args:
            conduit_id:
                Stable conduit id.
            root_conduit_id:
                Root lineage id for the conduit.
            frame_name:
                Owning frame name.
            origin_spellbook_id:
                Owning Spellbook id when known.
            payload:
                Descriptor-safe conduit payload for this record.
        """
        super().__init__()
        if payload is None:
            raise ValueError("payload cannot be None.")
        if not isinstance(payload, IConduitDescriptorPayload):
            raise TypeError("payload must satisfy IConduitDescriptorPayload.")
        self._id: str = IDBuilder.create_id()
        self.conduit_id = conduit_id
        self.root_conduit_id = root_conduit_id
        self.frame_name = frame_name
        self.origin_spellbook_id = origin_spellbook_id
        self.payload = payload

    def cleanup(self) -> None:
        """
        Idempotently clear the record.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self.conduit_id = None
        self.root_conduit_id = None
        self.frame_name = None
        self.origin_spellbook_id = None
        if self.payload is not None:
            self.payload.cleanup()
        self.payload = None
