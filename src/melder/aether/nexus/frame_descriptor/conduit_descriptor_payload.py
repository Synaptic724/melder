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
        - Cleanup is idempotent and clears all owned payload references.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "payload_version",
        "conduit_name",
        "conduit_state",
        "policy",
        "peer_conduit_ids",
    ]

    def __init__(
            self,
            *,
            conduit_name: Optional[str],
            conduit_state: ConduitState,
            policy: Optional[Policies],
            peer_conduit_ids: Tuple[str, ...],
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
            payload_version:
                Descriptor payload contract version.

        Returns:
            None.
        """
        super().__init__()
        if not payload_version:
            raise ValueError("payload_version cannot be empty.")
        self.payload_version: str = payload_version
        self.conduit_name = conduit_name
        self.conduit_state = conduit_state
        self.policy = policy
        self.peer_conduit_ids = tuple(peer_conduit_ids)

    def cleanup(self) -> None:
        """
        Idempotently clear the payload.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self.payload_version = None
        self.conduit_name = None
        self.conduit_state = None
        self.policy = None
        self.peer_conduit_ids = None
