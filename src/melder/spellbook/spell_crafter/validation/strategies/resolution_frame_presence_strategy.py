from melder.spellbook.spell_crafter.validation.spell_validation_issue import SpellValidationIssue
from melder.spellbook.spell_crafter.validation.strategies.spell_validation_strategy import SpellValidationStrategy


class ResolutionFramePresenceStrategy(SpellValidationStrategy):
    """
    Ensure Phase 3 has actually produced a resolution frame and DAG.

    This is the most basic structural check: if you somehow skip Phase 3 or
    fail to attach a dependency graph, the spell is not resolvable.
    """

    __slots__ = SpellValidationStrategy.__slots__

    def __init__(self) -> None:
        super().__init__(
            name="resolution_frame_presence",
            description="Verifies that Phase 3 produced a resolution frame and DAG.",
        )

    def validate(self, context: 'SpellValidationContext') -> None:
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
                        f"Phase 3 (local resolution frame / DAG) has not been "
                        f"run for spell {spell.spell_name!r}."
                    ),
                    details={},
                )
            )
            return

        # Frame exists but dependency graph is missing – suspicious but not fatal.
        if spell.dependency_graph is None:
            context.issues.append(
                SpellValidationIssue(
                    severity="warning",
                    code="MISSING_DEPENDENCY_GRAPH",
                    message=(
                        "Spell has a resolution frame but no attached dependency "
                        "graph (Spell.dependency_graph is None). This is unusual "
                        "for normal meld pipelines."
                    ),
                    details={},
                )
            )
