from melder.spellbook.spell_crafter.validation.spell_validation_issue import SpellValidationIssue
from melder.spellbook.spell_crafter.validation.strategies.spell_validation_strategy import SpellValidationStrategy


class RequiredHolesStrategy(SpellValidationStrategy):
    """
    Surface any **required holes** discovered in Phase 1.

    Required holes are parameters that:

        * Are classified as PLAIN (no DI).
        * Have **no default value**.
        * Therefore must be satisfied by the caller (e.g. via spell overrides,
          manual composition, or root-level parameters in meld()).
    """

    __slots__ = SpellValidationStrategy.__slots__

    def __init__(self) -> None:
        super().__init__(
            name="required_holes",
            description="Flags parameters that DI will never satisfy and that lack defaults.",
        )

    def validate(self, context: 'SpellValidationContext') -> None:
        self.check_cleaned()

        cancel_event = context.cancel_event
        if cancel_event is not None and cancel_event.is_set:
            cancel_event.throw_if_set()

        requirements = context.requirements
        if requirements is None:
            return

        if not requirements.has_required_holes():
            return

        spell = context.spell

        for param in requirements.iter_required_holes():
            context.issues.append(
                SpellValidationIssue(
                    severity="warning",
                    code="REQUIRED_HOLE",
                    message=(
                        f"Parameter {param.name!r} on spell {spell.spell_name!r} "
                        "cannot be satisfied by Melder DI and has no default. "
                        "The caller must supply a value (e.g. via spell overrides "
                        "or manual composition)."
                    ),
                    details={
                        "parameter_name": param.name,
                        "position": param.position,
                        "annotation": param.annotation,
                    },
                )
            )