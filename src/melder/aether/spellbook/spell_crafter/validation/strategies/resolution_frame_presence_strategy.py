from mypy_extensions import mypyc_attr

from melder.aether.spellbook.spell_crafter.validation.spell_validation_context import SpellValidationContext
from melder.aether.spellbook.spell_crafter.validation.spell_validation_issue import SpellValidationIssue
from melder.aether.spellbook.spell_crafter.validation.strategies.spell_validation_strategy import SpellValidationStrategy

@mypyc_attr(native_class=True)
class ResolutionFramePresenceStrategy(SpellValidationStrategy):
    """
    Ensure Phase 3 has actually produced a resolution frame and DAG.

    This is the most basic structural check: if you somehow skip Phase 3 or
    fail to attach a dependency graph, the spell is not resolvable.

    Contract:
    - Verifies that Phase 3 produced the minimum runtime artifacts needed for
      downstream resolution.
    - Emits validation issues into the supplied context; it does not attempt to
      rebuild missing graph artifacts.
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
            description="Verifies that Phase 3 produced a resolution frame and DAG.",
        )

    def validate(self, context: 'SpellValidationContext') -> None:
        """
        Validate that Phase 3 artifacts exist for the current spell.

        Contract:
        - Stops early if the validation context has been cancelled.
        - Emits `MISSING_RESOLUTION_FRAME` when no resolution frame exists.
        - Emits `MISSING_DEPENDENCY_GRAPH` when the frame exists but the spell
          still has no attached dependency graph.
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
