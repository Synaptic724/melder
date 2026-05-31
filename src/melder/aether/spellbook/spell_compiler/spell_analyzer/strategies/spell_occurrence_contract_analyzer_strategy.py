from typing import TYPE_CHECKING, Optional

from melder.aether.spellbook.spell_compiler.blueprints.occurrence_plan import (
    OccurrencePlanBuilder,
)
from melder.aether.spellbook.spell_compiler.spell_analyzer.spell_analyzer_strategy import (
    SpellAnalyzerStrategy,
)
from melder.aether.spellbook.spell_compiler.spell_analyzer.spell_occurrence_contract_analysis import (
    SpellOccurrenceContractAnalysis,
)

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.blueprints.root_resolution_blueprint import (
        RootResolutionBlueprint,
    )
    from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
        SpellCompilerArtifact,
    )
    from melder.aether.spellbook.spellbook import Spellbook


class SpellOccurrenceContractAnalyzerStrategy(SpellAnalyzerStrategy):
    """
    Build the occurrence-contract analysis artifact for one spell.

    Purpose:
        Derive SpellContract payload routing and contract-completeness truth
        from the occurrence graph and publish it as its own compiler-owned
        artifact.

    Contract:
        - Requires `_occurrence_graph_analysis` to exist already.
        - Reuses current Phase 8 contract-routing logic for parity.
        - Publishes only `_occurrence_contract_analysis`.
        - Does not own graph expansion, execution ordering, or instance/sharedness.
    """

    __slots__ = ()

    @property
    def strategy_id(self) -> str:
        """
        Return the stable identifier for this occurrence-contract strategy.
        """
        return "spell_occurrence_contract_analyzer"

    def analyze(
            self,
            spell: "Spell",
            artifact: "SpellCompilerArtifact",
    ) -> None:
        """
        Build and publish the occurrence-contract analysis artifact.
        """
        artifact.check_cleaned()
        if spell.is_existing_creation:
            return
        graph_analysis = artifact._occurrence_graph_analysis
        if graph_analysis is None:
            raise RuntimeError(
                "SpellOccurrenceContractAnalyzerStrategy requires occurrence graph analysis first."
            )

        spellbook: Optional["Spellbook"] = spell._spellbook
        if spellbook is None:
            raise RuntimeError(
                "SpellOccurrenceContractAnalyzerStrategy requires a live owning Spellbook."
            )
        root_blueprint: Optional["RootResolutionBlueprint"] = artifact._root_blueprint_phase5
        if root_blueprint is None:
            raise RuntimeError(
                "SpellOccurrenceContractAnalyzerStrategy requires Phase 5 root blueprint truth."
            )

        builder = OccurrencePlanBuilder(
            root_spell=spell,
            blueprint=root_blueprint,
            spell_lookup=spellbook._spell_id_pool,
            system_states=spell._spell_system_states,
        )
        (
            contract_overrides_by_occurrence,
            contract_overrides_by_spell_id,
            contract_dependencies_complete,
        ) = builder._compile_contract_overrides(
            occurrence_graph=graph_analysis.occurrence_graph,
        )
        builder.cleanup()

        contract_analysis = SpellOccurrenceContractAnalysis(
            contract_overrides_by_occurrence=contract_overrides_by_occurrence,
            contract_overrides_by_spell_id=contract_overrides_by_spell_id,
            contract_dependencies_complete=contract_dependencies_complete,
        )
        previous_contract = artifact._occurrence_contract_analysis
        artifact._occurrence_contract_analysis = contract_analysis
        self._cleanup_previous(previous_contract, contract_analysis)

    @staticmethod
    def _cleanup_previous(
            previous: Optional[SpellOccurrenceContractAnalysis],
            current: SpellOccurrenceContractAnalysis,
    ) -> None:
        """
        Best-effort cleanup for one superseded occurrence-contract analysis artifact.
        """
        if previous is None or previous is current:
            return
        try:
            previous.cleanup()
        except Exception:
            pass
