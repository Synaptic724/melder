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
        spellbook = context.spellbook

        # If we don't have a spell or a spellbook, we can't do any global checks.
        if spell is None or spellbook is None:
            return

        spell_name = spell.spell_name
        if not spell_name:
            # Nothing to check if this spell has no name.
            return

        # Build a collision list for diagnostics.
        collisions: List[Dict[str, Any]] = []
        for spell_id, other_spell in spellbook._spell_id_pool.items():
            if other_spell.spell_name != spell_name:
                continue
            index = other_spell.spell_index
            collisions.append(
                {
                    "spell_index_id": index.id,
                    "spell_id": spell_id,
                    "spellframe": other_spell.spellframe,
                    "binding_name": other_spell.binding_name,
                }
            )

        # If this spell is the only one with that name, we're fine.
        if len(collisions) <= 1:
            return

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
                    "collision_count": len(collisions),
                    "collisions": collisions,
                },
            )
        )
