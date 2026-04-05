from typing import Optional, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


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
        "conduit_name",
        "frame_name",
        "origin_spellbook_id",
        "conduit_state",
        "policy",
        "peer_conduit_ids",
    ]

    def __init__(
            self,
            *,
            conduit_id: str,
            root_conduit_id: str,
            conduit_name: Optional[str],
            frame_name: str,
            origin_spellbook_id: Optional[str],
            conduit_state: ConduitState,
            policy: Optional[Policies],
            peer_conduit_ids: Tuple[str, ...],
    ) -> None:
        """
        Initialize one canonical conduit record.

        Args:
            conduit_id:
                Stable conduit id.
            root_conduit_id:
                Root lineage id for the conduit.
            conduit_name:
                Optional conduit display name.
            frame_name:
                Owning frame name.
            origin_spellbook_id:
                Owning Spellbook id when known.
            conduit_state:
                Conduit runtime state.
            policy:
                Current conduit policy when available.
            peer_conduit_ids:
                Sorted tuple of directly linked peer conduit ids.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self.conduit_id = conduit_id
        self.root_conduit_id = root_conduit_id
        self.conduit_name = conduit_name
        self.frame_name = frame_name
        self.origin_spellbook_id = origin_spellbook_id
        self.conduit_state = conduit_state
        self.policy = policy
        self.peer_conduit_ids = peer_conduit_ids

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
        self.conduit_name = None
        self.frame_name = None
        self.origin_spellbook_id = None
        self.conduit_state = None
        self.policy = None
        self.peer_conduit_ids = None
