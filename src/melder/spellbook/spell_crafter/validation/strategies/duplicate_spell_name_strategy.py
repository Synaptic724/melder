from typing import Dict, List, Any
# Melder imports
from melder.spellbook.spell_crafter.validation.spell_validation_issue import SpellValidationIssue
from melder.spellbook.spell_crafter.validation.strategies.spell_validation_strategy import (
    SpellValidationStrategy,
)


class DuplicateSpellNameStrategy(SpellValidationStrategy):
    """
    Detect spells that share the same ``spell_name`` within the visible Spellbook
    (local + contracted).

    Now that `meld(...)` can resolve by ``spell_name`` / simple string, having
    multiple visible spells with the same name makes name-based resolution
    ambiguous and unsafe.

    This strategy treats such overlaps as **errors** and instructs the user to
    disambiguate via spellframe and/or binding_name.
    """

    __slots__ = SpellValidationStrategy.__slots__

    def __init__(self) -> None:
        super().__init__(
            name="duplicate_spell_name",
            description=(
                "Detects multiple visible spells that share the same spell_name, "
                "which would make name-based resolution via meld(spell_name=...) "
                "ambiguous."
            ),
        )

    def validate(self, context: "SpellValidationContext") -> None:
        self.check_cleaned()

        cancel_event = context.cancel_event
        if cancel_event is not None and cancel_event.is_set:
            cancel_event.throw_if_set()

        spell = context.spell
        scanner = context.scanner

        # If we don't have a spell or a scanner, we can't do any global checks.
        if spell is None or scanner is None:
            return

        spell_name = getattr(spell, "spell_name", None)
        if not spell_name:
            # Nothing to check if this spell has no name.
            return

        # Find all visible spells (local + contracted) that share this spell_name.
        matches = scanner.find_by_spell_name(
            spell_name=spell_name,
            include_contracted=True,
        )

        # If this spell is the only one with that name, we're fine.
        if not matches or len(matches) <= 1:
            return

        # Build a collision list for diagnostics.
        # Note: matches is Dict[ISpellIndex, ISpell]
        collisions: List[Dict[str, Any]] = []
        for index, other_spell in matches.items():
            try:
                spell_id = index.current
            except Exception:
                spell_id = None

            collisions.append(
                {
                    "spell_index_id": getattr(index, "id", None),
                    "spell_id": spell_id,
                    "spellframe": getattr(other_spell, "spellframe", None),
                    "binding_name": getattr(other_spell, "binding_name", None),
                }
            )

        context.issues.append(
            SpellValidationIssue(
                severity="error",
                code="DUPLICATE_SPELL_NAME",
                message=(
                    f"Multiple visible spells share the name {spell_name!r}. "
                    "Name-based resolution via meld(spell_name=...) would be "
                    "ambiguous. Disambiguate by using a spellframe (Protocol/"
                    "string frame key) and/or a binding_name so that each "
                    "resolution path is uniquely identifiable."
                ),
                details={
                    "spell_name": spell_name,
                    "collision_count": len(matches),
                    "collisions": collisions,
                },
            )
        )
