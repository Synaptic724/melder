from typing import TYPE_CHECKING, Optional

from melder.aether.spellbook.spell_compiler.blueprints.occurrence_plan import (
    OccurrencePlanBuilder,
)
from melder.aether.spellbook.spell_compiler.spell_analyzer.spell_analyzer_strategy import (
    SpellAnalyzerStrategy,
)
from melder.aether.spellbook.spell_compiler.spell_analyzer.spell_occurrence_order_analysis import (
    SpellOccurrenceOrderAnalysis,
)

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.blueprints.root_resolution_blueprint import (
        RootResolutionBlueprint,
    )
    from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
        SpellCompilerArtifact,
    )


class SpellOccurrenceOrderAnalyzerStrategy(SpellAnalyzerStrategy):
    """
    Build the occurrence-order analysis artifact for one spell.

    Purpose:
        Derive the dependency-safe execution order from the occurrence graph
        produced earlier in the occurrence-analysis chain and publish it as its
        own compiler-owned artifact.

    Contract:
        - Requires `_occurrence_graph_analysis` to exist already.
        - Uses the current Phase 8 execution-order helper for parity.
        - Publishes only `_occurrence_order_analysis`.
        - Does not own instance/sharedness or contract payload routing.
    """

    __slots__ = ()

    @property
    def strategy_id(self) -> str:
        """
        Return the stable identifier for this occurrence-order strategy.
        """
        return "spell_occurrence_order_analyzer"

    def analyze(
            self,
            spell: "Spell",
            artifact: "SpellCompilerArtifact",
    ) -> None:
        """
        Build and publish the occurrence-order analysis artifact.
        """
        artifact.check_cleaned()
        if spell.is_existing_creation:
            return
        graph_analysis = artifact._occurrence_graph_analysis
        if graph_analysis is None:
            raise RuntimeError(
                "SpellOccurrenceOrderAnalyzerStrategy requires occurrence graph analysis first."
            )
        root_blueprint: Optional["RootResolutionBlueprint"] = artifact._root_blueprint_phase5
        if root_blueprint is None:
            raise RuntimeError(
                "SpellOccurrenceOrderAnalyzerStrategy requires Phase 5 root blueprint truth."
            )

        execution_order = OccurrencePlanBuilder._build_execution_order(
            occurrence_graph=graph_analysis.occurrence_graph,
            fallback_order=root_blueprint.ordered_node_ids,
        )
        order_analysis = SpellOccurrenceOrderAnalysis(
            execution_order=execution_order,
        )
        previous_order = artifact._occurrence_order_analysis
        artifact._occurrence_order_analysis = order_analysis
        self._cleanup_previous(previous_order, order_analysis)

    @staticmethod
    def _cleanup_previous(
            previous: Optional[SpellOccurrenceOrderAnalysis],
            current: SpellOccurrenceOrderAnalysis,
    ) -> None:
        """
        Best-effort cleanup for one superseded occurrence-order analysis artifact.
        """
        if previous is None or previous is current:
            return
        try:
            previous.cleanup()
        except Exception:
            pass
