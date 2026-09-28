from typing import TYPE_CHECKING



from melder.aether.spellbook.spell_compiler.validation.spell_validation_issue import SpellValidationIssue
from melder.aether.spellbook.spell_compiler.validation.strategies.spell_validation_strategy import SpellValidationStrategy
if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.validation.spell_validation_context import SpellValidationContext


class ResolutionFramePresenceStrategy(SpellValidationStrategy):
    """
    Ensure Phase 3 has actually produced a resolution frame.

    This is the most basic structural check: if you somehow skip Phase 3, the
    spell is not resolvable. The former second check - a warning when the frame
    existed but `Spell.dependency_graph` was None - was retired on 2026-09-26
    together with the per-spell dependency graph object; the ordered frame on
    the compiler artifact is the only Phase-3 artifact this strategy inspects.

    Contract:
    - Verifies that Phase 3 produced the minimum runtime artifacts needed for
      downstream resolution.
    - Emits validation issues into the supplied context; it does not attempt to
      rebuild missing graph artifacts.

    Registration:
        MELDER KERNEL. A built-in strategy; registered, never bound.

    Subsystem Context:
        A built-in of the `validation/strategies` family - the most basic structural
        check, run first in the default registration order.

    System Context:
        Phase 4 (validation) of the conjure pipeline, verifying Phase-3 artifacts
        exist before the deeper strategies run.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Phase-4 structural gate: emits MISSING_RESOLUTION_FRAME (error) when
        Phase 3 produced no resolution frame. (MISSING_DEPENDENCY_GRAPH retired 2026-09-26.)
    """

    __slots__ = SpellValidationStrategy.__slots__

    def __init__(self) -> None:
        """
        Initialize the resolution-frame-presence strategy.

        Contract:
            Seeds the stable strategy name/description published through the
            validation pipeline.
        """
        super().__init__(
            name="resolution_frame_presence",
            description="Verifies that Phase 3 produced a resolution frame.",
        )

    def validate(self, context: SpellValidationContext) -> None:
        """
        Validate that Phase 3 artifacts exist for the current spell.

        Contract:
        - Stops early if the validation context has been cancelled.
        - Emits `MISSING_RESOLUTION_FRAME` when no resolution frame exists.
        - Emits nothing when the frame exists.
        """
        self.check_cleaned()

        cancel_event = context.cancel_event
        if cancel_event is not None and cancel_event.is_set:
            cancel_event.throw_if_set()

        spell = context.spell

        if context.resolution_frame is None:
            context.issues.append(
                SpellValidationIssue(
                    severity="error",
                    code="MISSING_RESOLUTION_FRAME",
                    message=(
                        f"Phase 3 (local resolution frame) has not been "
                        f"run for spell {spell.spell_name!r}."
                    ),
                    details={},
                )
            )
            return
