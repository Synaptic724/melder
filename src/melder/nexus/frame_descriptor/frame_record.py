import threading
from typing import Optional
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.nexus.frame_descriptor.frame_descriptor_payload import FrameDescriptorPayload


class FrameRecord(Cleanable):
    """
    Internal

    Canonical Nexus record for one AR-publishable frame.

    Purpose:
        Hold the frame-level posture Nexus needs to reason about one frame as a
        publishable AR/Rift source without depending on the richer shared
        Spellbook configuration object.

    Contract:
        - One record per frame name.
        - Carries one deterministic Nexus publication contract.
        - Carries only the current frame-level posture needed for the first
          passive-ingest slice.
        - Mutable through explicit Nexus upsert paths only.
        - Cleanup is idempotent and clears all owned references.

    Registration:
        MELDER KERNEL - guarded. Published passively by frames; never
        user-constructed.

    Subsystem Context:
        The canonical Nexus record for one AR-publishable frame, owned by
        `FrameDescriptorManager` and paired with `FrameDescriptorPayload`.

    System Context:
        Holding frame posture WITHOUT depending on the richer shared
        `SpellbookConfiguration` is the important independence. The AR layer
        needs to reason about a frame as a publishable source; coupling that to
        the full book configuration would drag Spellbook concerns into Nexus and
        make AR visibility depend on binding-time state it has no business
        reading.
        Records are the precondition for attachment: `Rift.create_frame_link`
        REQUIRES descriptor truth to already exist, so a frame that has not
        published cannot be linked. That ordering is what prevents a Rift from
        attaching to something the AR layer cannot describe.
    """
    _ast_helper_access: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Canonical Nexus record for one AR-publishable frame. Melder kernel "
        "machinery: read it to understand the runtime, do not drive it directly."
    )

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "nexus_label",
        "nexus_version",
        "frame_name",
        "frame_id",
        "config_origin_spellbook_id",
        "payload",
    ]

    def __init__(
            self,
            *,
            nexus_label: str = "default",
            nexus_version: str = "0.0.1",
            frame_name: str,
            frame_id: str,
            config_origin_spellbook_id: Optional[str],
            payload: FrameDescriptorPayload,
    ) -> None:
        """
        Initialize one canonical frame record.

        Args:
            nexus_label:
                Published Nexus dataset label for this record.
            nexus_version:
                Published Nexus dataset version for this record.
            frame_name:
                Stable frame name.
            frame_id:
                Stable runtime frame id.
            config_origin_spellbook_id:
                Spellbook id that originally established the bound frame
                posture/config path when known.
            payload:
                Descriptor-safe frame payload for this record.
        Contract:
            - Captures one snapshot of Nexus publication state for a single
              published frame.
            - Stores the descriptor payload by ownership, so cleanup of the
              record also owns cleanup of the payload.
            - Preserves the published Nexus label/version alongside the frame
              identity fields used by downstream viewers.
        Raises:
            ValueError:
                If `nexus_label`, `nexus_version`, or `payload` is missing.
            TypeError:
                If `payload` does not satisfy `FrameDescriptorPayload`.

        Returns:
            None.
        """
        super().__init__()
        if not nexus_label:
            raise ValueError("nexus_label cannot be empty.")
        if not nexus_version:
            raise ValueError("nexus_version cannot be empty.")
        if payload is None:
            raise ValueError("payload cannot be None.")
        if not isinstance(payload, FrameDescriptorPayload):
            raise TypeError("payload must satisfy FrameDescriptorPayload.")
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self.nexus_label = nexus_label
        self.nexus_version = nexus_version
        self.frame_name = frame_name
        self.frame_id = frame_id
        self.config_origin_spellbook_id = config_origin_spellbook_id
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
            - Runs grouped teardown under the record-owned instance lock.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            if self.payload is not None:
                self.payload.cleanup()

            del self.nexus_label
            del self.nexus_version
            del self.frame_name
            del self.frame_id
            del self.config_origin_spellbook_id
            del self.payload
            del self._id
            del self._lock
