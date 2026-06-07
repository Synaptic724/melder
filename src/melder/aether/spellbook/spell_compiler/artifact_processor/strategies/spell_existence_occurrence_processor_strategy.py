from typing import TYPE_CHECKING, Optional

from melder.aether.spellbook.spell_compiler.artifact_processor.spell_artifact_processor_strategy import (
    SpellArtifactProcessorStrategy,
)
from melder.aether.spellbook.spell_compiler.spell_analyzer.data.spell_existence_occurrence_analysis import (
    SpellExistenceOccurrenceAnalysis,
)

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
        SpellCodegenModel,
    )
    from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
        SpellCompilerArtifact,
    )


class SpellExistenceOccurrenceProcessorStrategy(SpellArtifactProcessorStrategy):
    """
    Publish phase-8 existence-occurrence truth onto the processor model.

    Purpose:
        Expose the raw+aggregate existence distribution captured in phase 8 as
        one planner-facing model section.
    """

    __slots__ = ()

    @property
    def strategy_id(self) -> str:
        """
        Return the stable processor strategy id.
        """
        return "spell_existence_occurrence_processor"

    def process(
            self,
            spell: "Spell",
            artifact: "SpellCompilerArtifact",
            model: "SpellCodegenModel",
    ) -> None:
        """
        Publish analyzer-owned existence-occurrence truth onto the model.
        """
        _ = spell
        graph_shape = artifact._occurrence_graph_analysis
        if graph_shape is None:
            raise RuntimeError(
                "SpellExistenceOccurrenceProcessorStrategy requires graph_shape first."
            )

        existence_occurrence_shape = graph_shape.existence_occurrence_analysis
        previous_existence_occurrence_shape = model.existence_occurrence_shape
        model.existence_occurrence_shape = existence_occurrence_shape
        self._cleanup_previous(
            previous_existence_occurrence_shape,
            existence_occurrence_shape,
        )

    @staticmethod
    def _cleanup_previous(
            previous: Optional[SpellExistenceOccurrenceAnalysis],
            current: Optional[SpellExistenceOccurrenceAnalysis],
    ) -> None:
        """
        The current payload is an immutable dataclass, so there is nothing to clean.
        """
        _ = previous
        _ = current
