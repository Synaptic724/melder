from threading import RLock
from typing import Any, Dict, Iterator, Optional, Tuple
# Melder imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import ISpellbook, ISpellIndex, ISpell
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

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
    __melder_internal__ = _mrg.sentinel
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

    def iter_contracted_spells(self) -> Iterator[Tuple[ISpellIndex, ISpell]]:
        """
        Iterate over **contracted** spells only.

        This walks all contracted spell maps exposed by the Spellbook and yields
        their contents as a flat stream.

        Yields:
            Tuples of ``(spell_index, spell)`` for each contracted spell.
        """
        self.check_cleaned()

        # contracted_spells is a mapping: conduit_id -> Mapping[ISpellIndex, ISpell]
        for _conduit_id, contracted in self._spellbook.contracted_spells.items():
            for index, spell in contracted.items():
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
        for _conduit_id, contracted in self._spellbook.contracted_spells.items():
            for index, spell in contracted.items():
                yield index, spell

    def iter_spells(
            self,
            *,
            include_contracted: bool = True,
    ) -> Iterator[Tuple[ISpellIndex, ISpell]]:
        """
        Convenience iterator that selects between local-only and all-visible spells.

        Args:
            include_contracted:
                If True, yields both local and contracted spells (equivalent to
                :meth:`iter_all_spells`). If False, yields only local spells
                (equivalent to :meth:`iter_local_spells`).

        Yields:
            Tuples of ``(spell_index, spell)``.
        """
        self.check_cleaned()
        if include_contracted:
            yield from self.iter_all_spells()
        else:
            yield from self.iter_local_spells()

    # ------------------------------------------------------------------
    # Simple query helpers (Phase 2/3 building blocks)
    # ------------------------------------------------------------------

    def find_by_frame_and_binding(
            self,
            spellframe: Any,
            binding_name: Optional[str] = None,
            *,
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
        iterator = self.iter_spells(include_contracted=include_contracted)

        for index, spell in iterator:
            if spell.spellframe is spellframe or spell.spellframe == spellframe:
                if spell.binding_name == binding_name:
                    result[index] = spell

        return result

    def find_single_by_frame_and_binding(
            self,
            spellframe: Any,
            binding_name: Optional[str] = None,
            *,
            include_contracted: bool = True,
            raise_on_ambiguity: bool = True,
    ) -> Optional[ISpell]:
        """
        Resolve a **single** spell for a (frame, binding) pair.

        This is a thin helper over :meth:`find_by_frame_and_binding` that is
        useful in DI contexts where you *expect* a unique match for a given
        (frame, binding) and want that expectation expressed explicitly.

        Behavior:
            - If no spells match, returns None.
            - If exactly one spell matches, returns that spell.
            - If more than one matches:
                * If ``raise_on_ambiguity`` is True, raises a RuntimeError.
                * Otherwise, returns None (caller can handle ambiguity).

        Args:
            spellframe:
                Frame object to match (Protocol, class, or string frame key).
            binding_name:
                Optional binding name to match.
            include_contracted:
                Whether to include contracted spells.
            raise_on_ambiguity:
                Control behavior when multiple matches are found.

        Returns:
            Optional[ISpell]: The resolved spell or None.
        """
        matches = self.find_by_frame_and_binding(
            spellframe=spellframe,
            binding_name=binding_name,
            include_contracted=include_contracted,
        )

        if not matches:
            return None

        if len(matches) == 1:
            # Return the single Spell instance.
            return next(iter(matches.values()))

        if raise_on_ambiguity:
            raise RuntimeError(
                f"Ambiguous spell resolution for frame={spellframe!r}, "
                f"binding_name={binding_name!r}: found {len(matches)} matches."
            )

        return None

    def find_by_frame(
            self,
            spellframe: Any,
            *,
            include_contracted: bool = True,
    ) -> Dict[ISpellIndex, ISpell]:
        """
        Find all spells that share the given spellframe, ignoring binding name.

        This is useful for:
          - Discovering all implementations of a Protocol frame.
          - Building menus / registries for a particular frame.

        Args:
            spellframe:
                Frame object to match.
            include_contracted:
                Whether to include contracted spells.

        Returns:
            Dict[ISpellIndex, ISpell]: mapping of matching spells.
        """
        self.check_cleaned()

        result: Dict[ISpellIndex, ISpell] = {}
        iterator = self.iter_spells(include_contracted=include_contracted)

        for index, spell in iterator:
            if spell.spellframe is spellframe or spell.spellframe == spellframe:
                result[index] = spell

        return result

    def find_by_binding_name(
            self,
            binding_name: Optional[str],
            *,
            include_contracted: bool = True,
    ) -> Dict[ISpellIndex, ISpell]:
        """
        Find all spells that share a given binding name, regardless of frame.

        This is especially handy for:
          - Locating all "named" bindings (e.g., "primary", "secondary").
          - Debugging ambiguous-name situations across frames.

        Args:
            binding_name:
                Logical binding name to match. If None, matches only spells with
                a None binding name.
            include_contracted:
                Whether to include contracted spells.

        Returns:
            Dict[ISpellIndex, ISpell]: mapping of matching spells.
        """
        self.check_cleaned()

        result: Dict[ISpellIndex, ISpell] = {}
        iterator = self.iter_spells(include_contracted=include_contracted)

        for index, spell in iterator:
            if spell.binding_name == binding_name:
                result[index] = spell

        return result

    def find_by_spell_name(
            self,
            spell_name: str,
            *,
            include_contracted: bool = True,
    ) -> Dict[ISpellIndex, ISpell]:
        """
        Find spells by their **internal spell_name** (usually the function/class __name__).

        This is primarily diagnostic / tooling sugar and should not be used as
        the primary DI key, but it is extremely useful when you're investigating
        a particular class/function and want to see all of its bindings.

        Args:
            spell_name:
                The `spell.spell_name` value to match.
            include_contracted:
                Whether to include contracted spells.

        Returns:
            Dict[ISpellIndex, ISpell]: mapping of matching spells.
        """
        self.check_cleaned()
        if not spell_name:
            raise ValueError("spell_name cannot be empty.")

        result: Dict[ISpellIndex, ISpell] = {}
        iterator = self.iter_spells(include_contracted=include_contracted)

        for index, spell in iterator:
            if spell.spell_name == spell_name:
                result[index] = spell

        return result

    def find_by_index(
            self,
            spell_index: ISpellIndex,
            *,
            include_contracted: bool = True,
    ) -> Optional[ISpell]:
        """
        Resolve a spell by its `SpellIndex` (lineage identity).

        This helper centralizes the “local vs contracted” lookup story for
        cases where higher layers already have an `ISpellIndex` and just need
        the corresponding `ISpell`.

        Semantics:
            - First tries the local `Spellbook.spells` map.
            - If not found and `include_contracted` is True, walks contracted
              spell maps and returns the first match.
            - If still not found, returns None.

        Args:
            spell_index:
                The SpellIndex to look up.
            include_contracted:
                Whether to consider contracted spells.

        Returns:
            Optional[ISpell]: The resolved spell, or None if not found.
        """
        self.check_cleaned()
        if spell_index is None:
            raise ValueError("spell_index cannot be None.")

        # Fast local lookup first.
        local = self._spellbook.spells.get(spell_index)
        if local is not None:
            return local

        if not include_contracted:
            return None

        # Linear scan across contracted maps.
        for _conduit_id, contracted in self._spellbook.contracted_spells.items():
            spell = contracted.get(spell_index)
            if spell is not None:
                return spell

        return None

    def find_by_target(
            self,
            target: Any,
            *,
            include_contracted: bool = True,
    ) -> Dict[ISpellIndex, ISpell]:
        """
        Find all spells whose underlying blueprint/creation matches a given object.

        This is a **structural / identity** helper intended for introspection and
        resolution-graph tooling. It looks at:

          - `spell.spell` (the bound object: class/function/lambda/instance).
          - `spell.user_created_object` (for EXISTING_CREATION* spells).

        Identity semantics:
          - Primary check is `is` identity (same object).
          - For `spell.spell`, we also fall back to `==` equality as a last resort
            to accommodate some value-type style registrations, but identity is
            the main path.

        Args:
            target:
                The object to match against spell blueprints / existing objects.
            include_contracted:
                Whether to include contracted spells.

        Returns:
            Dict[ISpellIndex, ISpell]: mapping of all spells that match.
        """
        self.check_cleaned()
        if target is None:
            raise ValueError("target cannot be None.")

        result: Dict[ISpellIndex, ISpell] = {}
        iterator = self.iter_spells(include_contracted=include_contracted)

        for index, spell in iterator:
            # Match against the primary blueprint (class/function/instance).
            if spell.spell is target or spell.spell == target:
                result[index] = spell
                continue

            # For EXISTING_CREATION* spells, match against the attached instance.
            if spell.has_existing_object and spell.user_created_object is target:
                result[index] = spell

        return result
