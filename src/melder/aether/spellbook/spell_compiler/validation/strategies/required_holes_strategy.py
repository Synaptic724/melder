from typing import TYPE_CHECKING



from melder.aether.spellbook.spell_compiler.validation.spell_validation_issue import SpellValidationIssue
from melder.aether.spellbook.spell_compiler.validation.strategies.spell_validation_strategy import SpellValidationStrategy
if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.validation.spell_validation_context import SpellValidationContext


class RequiredHolesStrategy(SpellValidationStrategy):
    """
    Surface any **required holes** discovered in Phase 1.

    Required holes are parameters that:

        * Are classified as PLAIN (no DI).
        * Have **no default value**.
        * Therefore must be satisfied by the caller (e.g. via spell overrides,
          manual composition, or root-level parameters in meld()).

    Contract:
    - Reports caller-required parameters that Melder DI will never satisfy.
    - Emits warnings rather than hard errors because the caller may still
      provide these values at invocation time.

    Registration:
        MELDER KERNEL. A built-in strategy; registered, never bound.

    Subsystem Context:
        A built-in of the `validation/strategies` family; it consumes the Phase-1
        `SpellRequirements.iter_required_holes()` view.

    System Context:
        Phase 4 (validation) of the conjure pipeline. It emits warnings only - they
        ride along without breaking the build.
    """

    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Phase-4 strategy: emits a REQUIRED_HOLE warning per PLAIN, "
        "default-less parameter - a hole Melder DI will never fill, so the caller must supply it "
        "via overrides or manual composition. Reporting only."
    )
    __slots__ = SpellValidationStrategy.__slots__

    def __init__(self) -> None:
        """
        Initialize the required-holes strategy.

        Contract:
            Seeds the stable strategy name/description published through the
            validation pipeline.
        """
        super().__init__(
            name="required_holes",
            description="Flags parameters that DI will never satisfy and that lack defaults.",
        )

    def validate(self, context: SpellValidationContext) -> None:
        """
        Emit warnings for required holes discovered in the requirements model.

        Contract:
        - Stops early if the validation context has been cancelled.
        - Emits one `REQUIRED_HOLE` warning per parameter that must be supplied
          by the caller.
        - Performs reporting only; it does not attempt to synthesize defaults
          or convert the hole into a DI target.
        """
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
