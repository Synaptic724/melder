from typing import Dict, List, Optional

from melder.utilities.general_base.cleanable import Cleanable


class ClusterCrystal(Cleanable):
    """
    Digital twin of one frame-local ConduitCluster.

    Purpose:
        Clusters are the third inter-conduit relationship (after links and
        contracts): named member groups with shared lineage roots and an
        optional elected leader. This twin records membership, shares, and
        leadership so restore can regroup a frame's cluster topology.

    Contract:
        - Pure data from birth; replace-on-emit at every membership, share,
          or leadership change (full snapshot per emission).
        - `cluster_id` and shared `index_id` values are RECORD-LOCAL ULIDs
          (emitted, never rehydrated); `cluster_name` and `frame_name` are
          the stable cross-session coordinates; member/leader conduit ids
          correlate through the conduit twins' translation map at restore.

    Threading:
        Immutable after construction; safe to share across threads.
    """

    __melder_internal__ = True
    __slots__ = Cleanable.__slots__ + [
        "_cluster_id",
        "_cluster_name",
        "_frame_name",
        "_member_conduit_ids",
        "_leader_conduit_id",
        "_shared_spells",
    ]

    def __init__(
            self,
            cluster_id: str,
            cluster_name: str,
            frame_name: str,
            member_conduit_ids: List[str],
            leader_conduit_id: Optional[str],
            shared_spells: List[Dict[str, str]],
    ) -> None:
        """
        Initialize one cluster twin from live cluster truth.

        Args:
            cluster_id:
                Live ConduitCluster ULID (record-local key).
            cluster_name:
                Stable frame-local cluster name.
            frame_name:
                Owning frame name (the frame-sweep edge).
            member_conduit_ids:
                Member conduit ids, detached copy.
            leader_conduit_id:
                Elected leader's conduit id, or None when inert.
            shared_spells:
                Plain-dict share entries ({owner_conduit_id, index_id}).

        Returns:
            None.
        """
        super().__init__()
        self._cluster_id: str = cluster_id
        self._cluster_name: str = cluster_name
        self._frame_name: str = frame_name
        self._member_conduit_ids: List[str] = list(member_conduit_ids)
        self._leader_conduit_id: Optional[str] = leader_conduit_id
        self._shared_spells: List[Dict[str, str]] = list(shared_spells)

    def cleanup(self) -> None:
        """
        Idempotently release the twin's held data.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._member_conduit_ids.clear()
        self._shared_spells.clear()
        del self._cluster_id
        del self._cluster_name
        del self._frame_name
        del self._member_conduit_ids
        del self._leader_conduit_id
        del self._shared_spells

    @property
    def cluster_id(self) -> str:
        """
        Return the live cluster's record-local ULID key.

        Returns:
            str: Cluster identity within this record.
        """
        self.check_cleaned()
        return self._cluster_id

    @property
    def frame_name(self) -> str:
        """
        Return the owning frame edge (the frame-sweep match).

        Returns:
            str: Owning frame name.
        """
        self.check_cleaned()
        return self._frame_name

    def describe(self) -> dict:
        """
        Return the detached plain-data snapshot of this cluster twin.

        Returns:
            dict: twin_kind, identities, membership, leadership, and copied
            share entries.
        """
        self.check_cleaned()
        return {
            "twin_kind": "cluster",
            "cluster_id": self._cluster_id,
            "cluster_name": self._cluster_name,
            "frame_name": self._frame_name,
            "member_conduit_ids": list(self._member_conduit_ids),
            "leader_conduit_id": self._leader_conduit_id,
            "shared_spells": [dict(entry) for entry in self._shared_spells],
        }
