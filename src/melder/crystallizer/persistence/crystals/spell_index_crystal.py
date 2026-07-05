from typing import List, Optional

from melder.utilities.general_base.cleanable import Cleanable


class SpellIndexCrystal(Cleanable):
    """
    Digital twin of one live SpellIndex: the record's membership map.

    Purpose:
        Custody crystals capture each spell's bind facts, but index GROUPING
        (which parked members ride which lineage, and which member is
        selected) is index-owned state. This twin records it so restore can
        regroup staged members onto the right lineage and transfer of
        ownership can re-anchor a moved index under its new spellbook.

    Contract:
        - Pure data from birth; replace-on-emit at every membership,
          selection, or ownership change (full snapshot per emission).
        - `index_id` is the live SpellIndex's ULID: RECORD-LOCAL ONLY
          (emitted, never rehydrated; restore mints fresh identities).
        - Member/selected ids are spell SHA256s: stable cross-session
          coordinates.

    Threading:
        Immutable after construction; safe to share across threads.
    """

    __melder_internal__ = True
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

        Returns:
            str: Index identity within this record.
        """
        self.check_cleaned()
        return self._index_id

    @property
    def spellbook_id(self) -> str:
        """
        Return the owning spellbook edge (the subtree-sweep match).

        Returns:
            str: Owner spellbook identity.
        """
        self.check_cleaned()
        return self._spellbook_id

    def describe(self) -> dict:
        """
        Return the detached plain-data snapshot of this index twin.

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
