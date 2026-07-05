from typing import Dict, List

from melder.utilities.general_base.cleanable import Cleanable


class ContractCrystal(Cleanable):
    """
    Digital twin of one ward Contract: the record's relationship map.

    Purpose:
        Links and contracts are the world's inter-conduit relationships -
        which conduits are linked, which spells/lineages are shared into
        which peer, with what permissions and direction. This twin records
        the WHOLE contract (both sides' detail views) so restore can
        re-establish relationships after owner worlds rebuild (link edges
        replay LAST per the restore ordering canon).

    Contract:
        - Pure data from birth; replace-on-emit at every contract mutation
          (full snapshot per emission; the crystallizer builder projects
          live Detail/IndexDetail objects into plain dicts).
        - `contract_id` and `index_id` values are RECORD-LOCAL ULIDs
          (emitted, never rehydrated); conduit ids are record-local too -
          restore correlates them through the conduit twins' translation
          map. Spell ids are SHA coordinates (stable cross-session).

    Threading:
        Immutable after construction; safe to share across threads.
    """

    __melder_internal__ = True
    __slots__ = Cleanable.__slots__ + [
        "_contract_id",
        "_conduit_a_id",
        "_conduit_b_id",
        "_details_a",
        "_details_b",
        "_index_details_a",
        "_index_details_b",
    ]

    def __init__(
            self,
            contract_id: str,
            conduit_a_id: str,
            conduit_b_id: str,
            details_a: List[Dict[str, object]],
            details_b: List[Dict[str, object]],
            index_details_a: List[Dict[str, object]],
            index_details_b: List[Dict[str, object]],
    ) -> None:
        """
        Initialize one contract twin from projected live truth.

        Args:
            contract_id:
                Live Contract ULID (record-local key).
            conduit_a_id:
                Ward A's conduit identity (initiator side of the link).
            conduit_b_id:
                Ward B's conduit identity (receiver side of the link).
            details_a:
                Plain-dict projections of ward A's spell Details
                (what A borrows from B).
            details_b:
                Plain-dict projections of ward B's spell Details
                (what B borrows from A).
            index_details_a:
                Plain-dict projections of ward A's lineage subscriptions.
            index_details_b:
                Plain-dict projections of ward B's lineage subscriptions.

        Returns:
            None.
        """
        super().__init__()
        self._contract_id: str = contract_id
        self._conduit_a_id: str = conduit_a_id
        self._conduit_b_id: str = conduit_b_id
        self._details_a: List[Dict[str, object]] = list(details_a)
        self._details_b: List[Dict[str, object]] = list(details_b)
        self._index_details_a: List[Dict[str, object]] = list(index_details_a)
        self._index_details_b: List[Dict[str, object]] = list(index_details_b)

    def cleanup(self) -> None:
        """
        Idempotently release the twin's held data.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._details_a.clear()
        self._details_b.clear()
        self._index_details_a.clear()
        self._index_details_b.clear()
        del self._contract_id
        del self._conduit_a_id
        del self._conduit_b_id
        del self._details_a
        del self._details_b
        del self._index_details_a
        del self._index_details_b

    @property
    def contract_id(self) -> str:
        """
        Return the live contract's record-local ULID key.

        Returns:
            str: Contract identity within this record.
        """
        self.check_cleaned()
        return self._contract_id

    @property
    def conduit_a_id(self) -> str:
        """
        Return ward A's conduit identity (a sweep edge).

        Returns:
            str: Conduit id of the link's initiator side.
        """
        self.check_cleaned()
        return self._conduit_a_id

    @property
    def conduit_b_id(self) -> str:
        """
        Return ward B's conduit identity (a sweep edge).

        Returns:
            str: Conduit id of the link's receiver side.
        """
        self.check_cleaned()
        return self._conduit_b_id

    def describe(self) -> dict:
        """
        Return the detached plain-data snapshot of this contract twin.

        Returns:
            dict: twin_kind, contract identity, both conduit edges, and
            copied per-side detail/subscription lists.
        """
        self.check_cleaned()
        return {
            "twin_kind": "contract",
            "contract_id": self._contract_id,
            "conduit_a_id": self._conduit_a_id,
            "conduit_b_id": self._conduit_b_id,
            "details_a": [dict(entry) for entry in self._details_a],
            "details_b": [dict(entry) for entry in self._details_b],
            "index_details_a": [
                dict(entry) for entry in self._index_details_a
            ],
            "index_details_b": [
                dict(entry) for entry in self._index_details_b
            ],
        }
