from typing import TYPE_CHECKING, Optional

from melder.aether.spellbook.spell_compiler.blueprints.occurrence_plan import (
    OccurrencePlanBuilder,
)
from melder.aether.spellbook.spell_compiler.phases.compiler_phase_8 import (
    CompilerPhase8,
)
from melder.aether.spellbook.spell_compiler.spell_analyzer.spell_analyzer_strategy import (
    SpellAnalyzerStrategy,
)
from melder.aether.spellbook.spell_compiler.spell_analyzer.spell_occurrence_instance_analysis import (
    SpellOccurrenceInstanceAnalysis,
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


class SpellOccurrenceInstanceAnalyzerStrategy(SpellAnalyzerStrategy):
    """
    Build the occurrence-instance analysis artifact for one spell.

    Purpose:
        Derive instance-key layout, shared spell ids, canonical occurrences,
        and the root instance key from the occurrence graph and publish them as
        their own compiler-owned artifact.

    Contract:
        - Requires `_occurrence_graph_analysis` to exist already.
        - Reuses current Phase 8 instance/sharedness logic for parity.
        - Publishes `_occurrence_instance_analysis`.
        - Also publishes `_occurrence_analysis_shape_profile` because the
          current shape profile depends on graph, order, and instance data.
    """

    __slots__ = ()

    @property
    def strategy_id(self) -> str:
        """
        Return the stable identifier for this occurrence-instance strategy.
        """
        return "spell_occurrence_instance_analyzer"

    def analyze(
            self,
            spell: "Spell",
            artifact: "SpellCompilerArtifact",
    ) -> None:
        """
        Build and publish the occurrence-instance analysis artifact.
        """
        artifact.check_cleaned()
        if spell.is_existing_creation:
            return
        graph_analysis = artifact._occurrence_graph_analysis
        if graph_analysis is None:
            raise RuntimeError(
                "SpellOccurrenceInstanceAnalyzerStrategy requires occurrence graph analysis first."
            )

        spellbook: Optional["Spellbook"] = spell._spellbook
        if spellbook is None:
            raise RuntimeError(
                "SpellOccurrenceInstanceAnalyzerStrategy requires a live owning Spellbook."
            )
        root_blueprint: Optional["RootResolutionBlueprint"] = artifact._root_blueprint_phase5
        if root_blueprint is None:
            raise RuntimeError(
                "SpellOccurrenceInstanceAnalyzerStrategy requires Phase 5 root blueprint truth."
            )

        builder = OccurrencePlanBuilder(
            root_spell=spell,
            blueprint=root_blueprint,
            spell_lookup=spellbook._spell_id_pool,
            system_states=spell._spell_system_states,
        )
        (
            instance_keys_by_spell_id,
            canonical_occurrences_by_spell_id,
            root_instance_key,
            shared_spell_ids,
        ) = builder._build_instance_plan(
            occurrence_graph=graph_analysis.occurrence_graph,
            root_spell_id=graph_analysis.root_spell_id,
        )
        builder.cleanup()

        instance_analysis = SpellOccurrenceInstanceAnalysis(
            instance_keys_by_spell_id=instance_keys_by_spell_id,
            canonical_occurrences_by_spell_id=canonical_occurrences_by_spell_id,
            root_instance_key=root_instance_key,
            shared_spell_ids=shared_spell_ids,
        )
        previous_instance = artifact._occurrence_instance_analysis
        artifact._occurrence_instance_analysis = instance_analysis

        order_analysis = artifact._occurrence_order_analysis
        if order_analysis is not None:
            occurrence_plan_like = type(
                "_OccurrencePlanLike",
                (),
                {
                    "occurrence_graph": graph_analysis.occurrence_graph,
                    "execution_order": order_analysis.execution_order,
                    "instance_keys_by_spell_id": instance_analysis.instance_keys_by_spell_id,
                    "shared_spell_ids": instance_analysis.shared_spell_ids,
                    "path_registry": graph_analysis.path_registry,
                },
            )()
            artifact._occurrence_analysis_shape_profile = (
                CompilerPhase8._build_phase8_occurrence_shape_profile(
                    occurrence_plan_like,
                )
            )

        self._cleanup_previous(previous_instance, instance_analysis)

    @staticmethod
    def _cleanup_previous(
            previous: Optional[SpellOccurrenceInstanceAnalysis],
            current: SpellOccurrenceInstanceAnalysis,
    ) -> None:
        """
        Best-effort cleanup for one superseded occurrence-instance analysis artifact.
        """
        if previous is None or previous is current:
            return
        try:
            previous.cleanup()
        except Exception:
            pass
