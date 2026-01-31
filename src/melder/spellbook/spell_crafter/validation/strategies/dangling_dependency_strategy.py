from typing import List

from melder.spellbook.spell_crafter.validation.spell_validation_issue import SpellValidationIssue
from melder.spellbook.spell_crafter.validation.strategies.spell_validation_strategy import SpellValidationStrategy


class DanglingDependenciesStrategy(SpellValidationStrategy):
    """
    Verify that all dependency spell_ids attached to a spell actually exist.

    This runs at the **Spellbook** level using the Spellbook's live
    spell_id_pool map and ensures that every id in ``spell.dependencies``
    resolves to a visible spell in the owning Spellbook.
    """

    __slots__ = SpellValidationStrategy.__slots__

    def __init__(self) -> None:
        super().__init__(
            name="dangling_dependencies",
            description="Checks that all dependency spell_ids resolve to spells.",
        )

    def validate(self, context: 'SpellValidationContext') -> None:
        self.check_cleaned()

        cancel_event = context.cancel_event
        if cancel_event is not None and cancel_event.is_set:
            cancel_event.throw_if_set()

        spell = context.spell
        deps: List[str] = spell.dependencies
        if not deps:
            return

        spellbook = context.spellbook
        if spellbook is None:
            # We can't validate existence without a Spellbook – warn and bail.
            context.issues.append(
                SpellValidationIssue(
                    severity="warning",
                    code="NO_SPELLBOOK_FOR_DEPENDENCY_CHECK",
                    message=(
                        f"Spell {spell.spell_name!r} has dependencies but no owning "
                        "Spellbook is attached; dependency existence cannot be verified."
                    ),
                    details={},
                )
            )
            return

        for dep_id in deps:
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()

            if dep_id not in spellbook._spell_id_pool:
                context.issues.append(
                    SpellValidationIssue(
                        severity="error",
                        code="DANGLING_DEPENDENCY",
                        message=(
                            f"Spell {spell.spell_name!r} depends on spell_id={dep_id!r}, "
                            "but no such spell is visible in the owning Spellbook."
                        ),
                        details={"missing_spell_id": dep_id},
                    )
                )
