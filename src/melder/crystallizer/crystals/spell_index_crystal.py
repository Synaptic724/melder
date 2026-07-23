from typing import List, Optional

from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class SpellIndexCrystal(Cleanable):
    """
    Digital twin of one live SpellIndex: the record's membership map.

    Purpose:
        Custody crystals capture each spell's bind facts, but index GROUPING
        (which parked members ride which lineage, and which member is
        selected) is index-owned state. This twin records it so restore can
        regroup staged members onto the right lineage and transfer of
        ownership can re-anchor a moved index under its new spellbook.

    Guidance:
        Treat `index_id` as a record-local grouping key, not durable identity.
        Stable spell SHA members and the selected SHA are the meaningful
        cross-session coordinates. Whole-world restore creates fresh indexes;
        finer-grained movement should use `capture_index_graft()` and
        `graft_index()` because a twin alone does not carry each member's
        custody payload required for hydration.

    Contract:
        - Pure data from birth; replace-on-emit at every membership,
          selection, or ownership change (full snapshot per emission).
        - `index_id` is the live SpellIndex's ULID: RECORD-LOCAL ONLY
          (emitted, never rehydrated; restore mints fresh identities).
        - Member/selected ids are spell SHA256s: stable cross-session
          coordinates.

    Threading:
        Immutable after construction; safe to share across threads.

    Lifecycle / Cleanup:
        Owned by one `PersistenceProfile`. Cleanup releases copied membership
        data only and never mutates a live `SpellIndex` or its selection.

    Registration:
        MELDER KERNEL - guarded. Emitted by the crystallizer's builders from live
        runtime truth and owned by one `PersistenceProfile`; never
        user-constructed or bound.

    Subsystem Context:
        One member of the crystal-twin family. Where the custody crystals (spell
        crystals) capture each spell's bind facts, this twin captures the
        index-owned GROUPING state: which parked members ride which lineage and
        which member is selected. Restore reads it to regroup staged members onto
        the right lineage, and transfer-of-ownership uses it to re-anchor a moved
        index under its new spellbook. It rides under its owning
        `SpellbookCrystal`.

    System Context:
        One node of the V3 crystallizer's serialize-then-restore model, where
        splitting index GROUPING from spell CUSTODY is the design point: a spell's
        durable identity is its stable SHA256, but "which index it currently sits
        in and whether it is the selected member" is grouping state the index owns
        and can change (notch, add/remove). Recording that separately -
        record-local `index_id` for correlation, stable member/selected SHAs as
        the real coordinates - is what lets restore mint fresh indexes yet still
        rebuild the exact historical membership, while finer-grained movement goes
        through the graft path (a twin alone lacks each member's custody payload).
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Digital twin of one live SpellIndex: the record's membership map. "
        "Melder kernel machinery: read it to understand the runtime, do not drive it directly."
    )

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_index_id",
        "_spellbook_id",
        "_selected_spell_id",
        "_member_spell_ids",
    ]

    def __init__(
            self,
            index_id: str,
            spellbook_id: str,
            selected_spell_id: Optional[str],
            member_spell_ids: List[str],
    ) -> None:
        """
        Initialize one index twin from live index truth.

        Args:
            index_id:
                Live SpellIndex ULID (record-local foreign key).
            spellbook_id:
                Owning spellbook identity (the subtree-sweep edge).
            selected_spell_id:
                SHA of the active member, or None when headless.
            member_spell_ids:
                SHAs of every member (active + parked), detached copy.

        Returns:
            None.
        """
        super().__init__()
        self._index_id: str = index_id
        self._spellbook_id: str = spellbook_id
        self._selected_spell_id: Optional[str] = selected_spell_id
        self._member_spell_ids: List[str] = list(member_spell_ids)

    def cleanup(self) -> None:
        """
        Idempotently release the twin's held data.

        Contract:
            Terminal for this value carrier; deletes owner, selection, and
            member coordinates without removing any live spell.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._member_spell_ids.clear()
        del self._member_spell_ids
        del self._index_id
        del self._spellbook_id
        del self._selected_spell_id

    @property
    def index_id(self) -> str:
        """
        Return the live index's record-local ULID key.

        Contract:
            - RECORD-LOCAL grouping ULID (emitted, never rehydrated); the member
              and selected spell SHA256s are the stable coordinates.

        Returns:
            str: Index identity within this record.
        """
        self.check_cleaned()
        return self._index_id

    @property
    def spellbook_id(self) -> str:
        """
        Return the owning spellbook edge (the subtree-sweep match).

        Contract:
            - The owning-spellbook subtree-sweep edge; record-local, correlated
              through the spellbook twin on restore.

        Returns:
            str: Owner spellbook identity.
        """
        self.check_cleaned()
        return self._spellbook_id

    def describe(self) -> dict:
        """
        Return the detached plain-data snapshot of this index twin.

        Contract:
            - Detached plain-data snapshot carrying `twin_kind: "spell_index"`;
              a full membership + selection snapshot (replace-on-emit).

        Returns:
            dict: twin_kind, index identity, owner edge, selection, and a
            copied member list.
        """
        self.check_cleaned()
        return {
            "twin_kind": "spell_index",
            "index_id": self._index_id,
            "spellbook_id": self._spellbook_id,
            "selected_spell_id": self._selected_spell_id,
            "member_spell_ids": list(self._member_spell_ids),
        }
