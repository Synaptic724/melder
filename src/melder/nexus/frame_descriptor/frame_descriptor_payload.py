import threading
from typing import Tuple

from melder.aether.spellbook.configuration.system_state import SystemState
from melder.utilities.general_base.cleanable import Cleanable


class FrameDescriptorPayload(Cleanable):
    """
    Descriptor-safe published frame payload.

    Purpose:
        Store the descriptive frame-facing payload on `FrameRecord` without
        flattening posture and topology data back into the record surface.

    Contract:
        - `payload_version` preserves the descriptor payload contract version.
        - Payload fields are descriptor-safe and value-oriented.
        - Cleanup is idempotent and clears all owned payload references.

    Threading:
        Detached value payload; immutable in practice and safe to share.

    Registration:
        MELDER KERNEL - guarded. Attached to its record during passive
        publication; never user-constructed.

    Subsystem Context:
        The descriptive payload half of the frame record pair. The RECORD holds
        directly targetable identity; the PAYLOAD holds description.

    System Context:
        Keeping payload separate from record - rather than flattening it back
        onto the record surface - is what lets description evolve without
        destabilizing identity. `payload_version` makes that explicit: a
        consumer can reason about the payload contract it received rather than
        assuming the current shape.
        For frames the split also keeps posture and topology data off the record surface, so a consumer asking 'does this frame exist and may I attach' does not have to parse everything known about it.
        Payloads carry no live runtime object references, which is what makes a
        descriptor safe to publish, hold, and project. A payload holding live
        objects would extend their lifetime and let a viewer reach the runtime
        it is only meant to describe.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Descriptor-safe published frame payload. Melder kernel machinery: read
        it to understand the runtime, do not drive it directly.
    """

    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "payload_version",
        "system_state",
        "ai_native_enabled",
        "rift_enabled",
        "root_conduit_count",
        "root_conduit_ids",
        "named_root_conduits",
        "conduit_cloud_entry_count",
        "conduit_cloud_names",
        "cluster_count",
        "cluster_names",
    ]

    def __init__(
            self,
            *,
            system_state: SystemState,
            ai_native_enabled: bool,
            rift_enabled: bool,
            root_conduit_count: int,
            root_conduit_ids: Tuple[str, ...],
            named_root_conduits: Tuple[Tuple[str, str], ...],
            conduit_cloud_entry_count: int,
            conduit_cloud_names: Tuple[str, ...],
            cluster_count: int,
            cluster_names: Tuple[str, ...],
            payload_version: str = "0.0.1",
    ) -> None:
        """
        Initialize one descriptor-safe frame payload.

        Args:
            system_state:
                Current frame system state.
            ai_native_enabled:
                Whether AI-native posture is enabled for the frame.
            rift_enabled:
                Whether the frame is publishable to Nexus/Rift-facing layers.
            root_conduit_count:
                Count of root conduits registered in the frame.
            root_conduit_ids:
                Sorted tuple of root conduit ids.
            named_root_conduits:
                Sorted tuple of `(conduit_id, conduit_name)` entries.
            conduit_cloud_entry_count:
                Count of conduit-cloud entries.
            conduit_cloud_names:
                Sorted tuple of conduit-cloud names.
            cluster_count:
                Count of conduit clusters.
            cluster_names:
                Sorted tuple of cluster names.
            payload_version:
                Descriptor payload contract version.
        Contract:
            - Stores one descriptor-facing snapshot of frame posture for Nexus
              publication.
            - Normalizes iterable inputs into tuples so the payload remains
              value-oriented and stable after construction.
            - Preserves the payload contract version alongside the frame-facing
              posture fields.
        Raises:
            ValueError:
                If `payload_version` is empty.

        Returns:
            None.
        """
        super().__init__()
        if not payload_version:
            raise ValueError("payload_version cannot be empty.")
        self._lock: threading.RLock = threading.RLock()
        self.payload_version: str = payload_version
        self.system_state = system_state
        self.ai_native_enabled = ai_native_enabled
        self.rift_enabled = rift_enabled
        self.root_conduit_count = root_conduit_count
        self.root_conduit_ids = tuple(root_conduit_ids)
        self.named_root_conduits = tuple(named_root_conduits)
        self.conduit_cloud_entry_count = conduit_cloud_entry_count
        self.conduit_cloud_names = tuple(conduit_cloud_names)
        self.cluster_count = cluster_count
        self.cluster_names = tuple(cluster_names)

    def cleanup(self) -> None:
        """
        Idempotently clear the payload.

        Contract:
            - Safe to call more than once.
            - Clears all stored descriptor-facing posture fields.
            - Leaves future callers to fail through `check_cleaned()`.
            - Runs grouped teardown under the payload-owned instance lock.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            del self.payload_version
            del self.system_state
            del self.ai_native_enabled
            del self.rift_enabled
            del self.root_conduit_count
            del self.root_conduit_ids
            del self.named_root_conduits
            del self.conduit_cloud_entry_count
            del self.conduit_cloud_names
            del self.cluster_count
            del self.cluster_names
            del self._lock
