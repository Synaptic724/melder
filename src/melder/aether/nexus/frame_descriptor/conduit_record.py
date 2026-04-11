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
        - Carries one deterministic Nexus publication contract.
        - Mutable through explicit Nexus upsert/remove paths only.
        - Cleanup is idempotent and clears all owned references.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "nexus_label",
        "nexus_version",
        "conduit_id",
        "root_conduit_id",
        "frame_name",
        "origin_spellbook_id",
        "payload",
    ]

    def __init__(
            self,
            *,
            nexus_label: str = "default",
            nexus_version: str = "0.0.1",
            conduit_id: str,
            root_conduit_id: str,
            frame_name: str,
            origin_spellbook_id: Optional[str],
            payload: IConduitDescriptorPayload,
    ) -> None:
        """
        Initialize one canonical conduit record.

        Args:
            nexus_label:
                Published Nexus dataset label for this record.
            nexus_version:
                Published Nexus dataset version for this record.
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
        Contract:
            - Captures one snapshot of Nexus publication state for a single
              published conduit.
            - Stores the descriptor payload by ownership, so cleanup of the
              record also owns cleanup of the payload.
            - Preserves both the conduit id and its root lineage id so Nexus
              can reason about directly published conduits and their lineage
              roots separately.
        Raises:
            ValueError:
                If `nexus_label`, `nexus_version`, or `payload` is missing.
            TypeError:
                If `payload` does not satisfy `IConduitDescriptorPayload`.
        """
        super().__init__()
        if not nexus_label:
            raise ValueError("nexus_label cannot be empty.")
        if not nexus_version:
            raise ValueError("nexus_version cannot be empty.")
        if payload is None:
            raise ValueError("payload cannot be None.")
        if not isinstance(payload, IConduitDescriptorPayload):
            raise TypeError("payload must satisfy IConduitDescriptorPayload.")
        self._id: str = IDBuilder.create_id()
        self.nexus_label = nexus_label
        self.nexus_version = nexus_version
        self.conduit_id = conduit_id
        self.root_conduit_id = root_conduit_id
        self.frame_name = frame_name
        self.origin_spellbook_id = origin_spellbook_id
        self.payload = payload

    def cleanup(self) -> None:
        """
        Idempotently clear the record and its owned payload.

        Contract:
            - Safe to call more than once.
            - Clears every stored publication field.
            - Cleans the owned descriptor payload before dropping the payload
              reference.
            - Leaves future callers to fail through `check_cleaned()`.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self.nexus_label = None
        self.nexus_version = None
        self.conduit_id = None
        self.root_conduit_id = None
        self.frame_name = None
        self.origin_spellbook_id = None
        if self.payload is not None:
            self.payload.cleanup()
        self.payload = None
