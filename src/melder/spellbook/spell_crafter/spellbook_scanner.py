from __future__ import annotations

from threading import RLock
from typing import Any, Dict, Iterable, Iterator, Optional, Tuple

from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import ISpellbook, ISpellIndex, ISpell


class SpellbookScanner(Cleanable):
    """
    Internal

    Lightweight helper for **walking and querying** a Spellbook.

    Goals
    -----
    - Centralize Spellbook traversal semantics (local vs contracted spells).
    - Provide simple, composable iterators that later phases (SpellCrafter,
      Resolution, Meld) can reuse.
    - Stay dumb: no DAGs, no resolution, no policies – just "find me spells".

    This is intentionally not exposed to users – it is an internal utility for
    the resolution / meld pipeline.
    """

    __slots__ = Cleanable.__slots__ + [
        "_spellbook",
        "_lock",
    ]

    def __init__(self, spellbook: ISpellbook) -> None:
        """
        Create a new scanner bound to a specific Spellbook.

        Args:
            spellbook:
                The Spellbook instance to walk. Must not be None.
        """
        super().__init__()

        if spellbook is None:
            raise ValueError("spellbook must not be None.")

        self._spellbook: ISpellbook = spellbook
        self._lock: RLock = RLock()

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def cleanup(self) -> None:
        """
        Deterministically tear down this scanner.

        This:
        - Drops the Spellbook reference.
        - Marks the scanner as cleaned.

        It does **not** mutate the Spellbook itself.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return

            self._spellbook = None
            self._cleaned = True

    # ------------------------------------------------------------------
    # Core accessors
    # ------------------------------------------------------------------

    @property
    def spellbook(self) -> ISpellbook:
        """
        Underlying Spellbook.

        Returned as-is; callers must treat it as read-only.
        """
        self.check_cleaned()
        return self._spellbook

    # ------------------------------------------------------------------
    # Iteration helpers
    # ------------------------------------------------------------------

    def iter_local_spells(self) -> Iterator[Tuple[ISpellIndex, ISpell]]:
        """
        Iterate over **local** spells registered directly in this Spellbook.

        Yields:
            Tuples of ``(spell_index, spell)`` for each locally registered spell.
        """
        self.check_cleaned()

        # `spells` is exposed as a MappingProxyType on Spellbook.
        for index, spell in self._spellbook.spells.items():
            yield index, spell

    def iter_all_spells(self) -> Iterator[Tuple[ISpellIndex, ISpell]]:
        """
        Iterate over **all** spells visible to this Spellbook.

        This includes:
            - Local spells.
            - Spells contracted from other Spellbooks / Conduits.

        Yields:
            Tuples of ``(spell_index, spell)``.
        """
        self.check_cleaned()

        # Local first.
        for index, spell in self._spellbook.spells.items():
            yield index, spell

        # Then contracted spells, if any.
        # contracted_spells is a mapping: conduit_id -> Mapping[ISpellIndex, ISpell]
        for _conduit_id, contracted in self._spellbook.contracted_spells.items():
            for index, spell in contracted.items():
                yield index, spell

    # ------------------------------------------------------------------
    # Simple query helpers (can be extended for Phase 2+)
    # ------------------------------------------------------------------

    def find_by_frame_and_binding(
            self,
            spellframe: Any,
            binding_name: Optional[str] = None,
            include_contracted: bool = True,
    ) -> Dict[ISpellIndex, ISpell]:
        """
        Find spells that match a given (frame, binding) pair.

        This is a **simple linear scan** over either local or all spells.
        It does not apply any permission / conduit policy – higher layers
        (Conduit, Ward, Contracts) remain responsible for that.

        Args:
            spellframe:
                Frame object to match (Protocol, class, or string frame key).
            binding_name:
                Optional binding name to match. If None, matches spells with
                a None binding name.
            include_contracted:
                If True, search both local and contracted spells. If False,
                search only local spells.

        Returns:
            Dict[ISpellIndex, ISpell]: mapping of matching spell indices to spells.
        """
        self.check_cleaned()

        result: Dict[ISpellIndex, ISpell] = {}
        iterator = self.iter_all_spells() if include_contracted else self.iter_local_spells()

        for index, spell in iterator:
            if spell.spellframe is spellframe or spell.spellframe == spellframe:
                if spell.binding_name == binding_name:
                    result[index] = spell

        return result
