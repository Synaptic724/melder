from typing import Dict, List

from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


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

    Guidance:
        Use this twin after endpoint conduits and their link relationship are
        understood. `details_a`/`details_b` describe what each ward borrows from
        its peer; index-detail rows describe lineage subscriptions. The two
        projections are intentionally retained together so inspection does not
        mistake one side's view for the complete contract. Runtime endpoint and
        index ids must be translated during restore; spell SHA coordinates do
        not translate.

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

    Lifecycle / Cleanup:
        Owned by one `PersistenceProfile`. Cleanup deletes copied relationship
        rows only and never severs a live contract.

    Registration:
        MELDER KERNEL - guarded. Emitted by the crystallizer's builders from live
        runtime truth and owned by one `PersistenceProfile`; never
        user-constructed or bound.

    Subsystem Context:
        One member of the crystal-twin family, capturing an inter-conduit
        RELATIONSHIP: which conduits are linked and which spells/lineages are
        shared into which peer, with what permissions and direction. Unlike the
        per-object twins, it records the WHOLE contract (both sides' details plus
        index-detail subscriptions) so restore can re-establish the relationship
        AFTER both endpoint worlds rebuild - link/contract edges replay LAST per
        the restore ordering canon.

    System Context:
        One node of the V3 crystallizer's serialize-then-restore model, and a
        case where the twin deliberately holds BOTH projections together. A
        contract is a two-sided fact; retaining only one ward's view would let
        inspection mistake a borrower's slice for the complete relationship, so
        the twin keeps both. Restore ordering follows from the same reasoning:
        a relationship references two conduits, so it can only be replayed once
        both exist - hence edges last. Endpoint and index ids are record-local
        (translated on restore); spell SHAs are the stable coordinates that
        survive a boot unchanged.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Digital twin of one ward Contract: the record's relationship map. "
        "Melder kernel machinery: read it to understand the runtime, do not drive it directly."
    )

    __melder_internal__ = _mrg.sentinel
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

        Contract:
            Terminal for this value carrier; no live ward, contract, detail, or
            subscription object is retained or mutated.

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

        Contract:
            - RECORD-LOCAL ULID (emitted, never rehydrated); the spell SHA
              coordinates inside the detail rows are the stable ones.

        Returns:
            str: Contract identity within this record.
        """
        self.check_cleaned()
        return self._contract_id

    @property
    def conduit_a_id(self) -> str:
        """
        Return ward A's conduit identity (a sweep edge).

        Contract:
            - The INITIATOR-side conduit edge, record-local; restore correlates
              it through the conduit twins' translation map.

        Returns:
            str: Conduit id of the link's initiator side.
        """
        self.check_cleaned()
        return self._conduit_a_id

    @property
    def conduit_b_id(self) -> str:
        """
        Return ward B's conduit identity (a sweep edge).

        Contract:
            - The RECEIVER-side conduit edge, record-local; translated on
              restore like `conduit_a_id`.

        Returns:
            str: Conduit id of the link's receiver side.
        """
        self.check_cleaned()
        return self._conduit_b_id

    def describe(self) -> dict:
        """
        Return the detached plain-data snapshot of this contract twin.

        Contract:
            - Detached plain-data snapshot carrying `twin_kind: "contract"`;
              retains BOTH sides' detail/subscription projections so no
              inspection mistakes one side for the whole contract.

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
