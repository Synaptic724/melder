from typing import List
# Melder imports
from melder.spellbook.spell_crafter.validation.spell_validation_issue import SpellValidationIssue
from melder.spellbook.spell_crafter.validation.strategies.spell_validation_strategy import SpellValidationStrategy


class SelfDependencyStrategy(SpellValidationStrategy):
    """
    Detect trivial self-dependencies (a spell depending on itself).

    This is always a configuration bug and is treated as an error.
    """

    __slots__ = SpellValidationStrategy.__slots__

    def __init__(self) -> None:
        super().__init__(
            name="self_dependency",
            description="Detects spells that directly depend on themselves.",
        )

    def validate(self, context: 'SpellValidationContext') -> None:
        self.check_cleaned()

        cancel_event = context.cancel_event
        if cancel_event is not None and cancel_event.is_set:
            cancel_event.throw_if_set()

        spell = context.spell
        deps: List[str] = getattr(spell, "dependencies", [])
        if not deps:
            return

        root_id = spell.spell_index.current
        if root_id in deps:
            context.issues.append(
                SpellValidationIssue(
                    severity="error",
                    code="SELF_DEPENDENCY",
                    message=(
                        f"Spell {spell.spell_name!r} declares a dependency on itself "
                        f"(spell_id={root_id}). This indicates a configuration bug."
                    ),
                    details={"spell_id": root_id},
                )
            )

