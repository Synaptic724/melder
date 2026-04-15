import threading
from typing import Optional, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.utilities.general_base.cleanable import Cleanable


class ConduitDescriptorPayload(Cleanable):
    """
    Descriptor-safe published conduit payload.

    Purpose:
        Store the descriptive conduit-facing payload on `ConduitRecord`
        without flattening it back into the record surface.

    Contract:
        - `payload_version` preserves the descriptor payload contract version.
        - Payload fields are descriptor-safe and value-oriented.
        - Carries enough lineage metadata to distinguish root/normal conduits
          from lesser conduits without introducing a second record family.
        - Cleanup is idempotent and clears all owned payload references.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "payload_version",
        "conduit_name",
        "conduit_state",
        "policy",
        "peer_conduit_ids",
        "parent_conduit_id",
        "lineage_depth",
    ]

    def __init__(
            self,
            *,
            conduit_name: Optional[str],
            conduit_state: ConduitState,
            policy: Optional[Policies],
            peer_conduit_ids: Tuple[str, ...],
            parent_conduit_id: Optional[str] = None,
            lineage_depth: int = 0,
            payload_version: str = "0.0.1",
    ) -> None:
        """
        Initialize one descriptor-safe conduit payload.

        Args:
            conduit_name:
                Optional conduit display name.
            conduit_state:
                Current conduit runtime state.
            policy:
                Current conduit policy when available.
            peer_conduit_ids:
                Sorted tuple of directly linked peer conduit ids.
            parent_conduit_id:
                Parent conduit id for lesser conduits, or None for root/normal
                conduits without a published parent.
            lineage_depth:
                Zero-based lineage depth where root/normal conduits publish as
                `0` and lesser conduits publish relative depth beneath the root.
            payload_version:
                Descriptor payload contract version.
        Contract:
            - Stores one descriptor-facing snapshot of conduit posture for
              Nexus publication.
            - Normalizes peer conduit ids into a tuple so the payload remains
              value-oriented and stable after construction.
            - Preserves conduit state/policy as descriptor-facing values rather
              than flattening them into the record surface.
            - Preserves parent/depth lineage hints so consumers can navigate
              lesser topology without rebuilding lineage state from runtime
              objects.
        Raises:
            ValueError:
                If `payload_version` is empty or `lineage_depth` is negative.
        """
        super().__init__()
        if not payload_version:
            raise ValueError("payload_version cannot be empty.")
        if lineage_depth < 0:
            raise ValueError("lineage_depth cannot be negative.")
        self._lock: threading.RLock = threading.RLock()
        self.payload_version: str = payload_version
        self.conduit_name = conduit_name
        self.conduit_state = conduit_state
        self.policy = policy
        self.peer_conduit_ids = tuple(peer_conduit_ids)
        self.parent_conduit_id = parent_conduit_id
        self.lineage_depth = lineage_depth

    def cleanup(self) -> None:
        """
        Idempotently clear the payload.

        Contract:
            - Safe to call more than once.
            - Clears all stored descriptor-facing conduit posture fields.
            - Leaves future callers to fail through `check_cleaned()`.
            - Runs grouped teardown under the payload-owned instance lock.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self.payload_version = None
            self.conduit_name = None
            self.conduit_state = None
            self.policy = None
            self.peer_conduit_ids = None
            self.parent_conduit_id = None
            self.lineage_depth = None
            self._lock = None
