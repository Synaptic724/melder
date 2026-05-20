from typing import Any, Optional

from mypy_extensions import mypyc_attr

from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.ispell import ISpell
from melder.utilities.interfaces.ispellbook import ISpellbook
from melder.aether.spellbook.spell_crafter.spell_crafter import SpellCrafter


@mypyc_attr(native_class=True)
class SpellCompilerSystem(Cleanable):
    """
    Foundation surface for spell runtime compilation ownership.

    Purpose:
        Give the runtime an explicit object that can later own spell compiler
        logic without requiring `Spell` to lazily own `SpellCrafter` forever.

    Contract:
        - Owns one borrowed `Spellbook` reference for now.
        - Does not own per-spell compiler artifact state.
        - Current behavior is intentionally minimal and additive.
    """

    __slots__ = Cleanable.__slots__ + [
        "_spellbook",
        "_spellcrafter",
    ]

    def __init__(self, spellbook: ISpellbook) -> None:
        """
        Initialize one compiler-system foundation object.

        Args:
            spellbook: Spellbook whose spell/compiler context this system serves.

        Raises:
            ValueError: If spellbook is None.
        """
        super().__init__()
        if spellbook is None:
            raise ValueError("spellbook cannot be None.")
        self._spellbook: ISpellbook = spellbook
        self._spellcrafter: SpellCrafter = None

    def cleanup(self) -> None:
        """
        Release the borrowed spellbook reference.

        Contract:
            - Idempotent cleanup.
            - Does not clean the spellbook itself.
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._spellbook
        del self._spellcrafter

    def create_spell_crafter_for_spell(
            self,
            spell: ISpell,
            *,
            resolution_profile: Optional[Any] = None,
    ) -> Any:
        """
        Create one `SpellCrafter` for a target spell.

        Purpose:
            Provide the first explicit compiler-system seam while leaving the
            existing `SpellCrafter` implementation intact.

        Args:
            spell: Spell to compile.
            resolution_profile: Optional prebuilt resolution profile.

        Returns:
            Any: Newly created concrete `SpellCrafter`.
        """
        return SpellCrafter(
            spell,
            resolution_profile=resolution_profile,
        )
