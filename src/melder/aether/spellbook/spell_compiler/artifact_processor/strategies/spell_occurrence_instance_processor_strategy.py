from collections import defaultdict
from typing import TYPE_CHECKING, Dict, List, Optional, Sequence, Set, Tuple

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.phases.compiler_phase_8 import (
    CompilerPhase8,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.spell_artifact_processor_strategy import (
    SpellArtifactProcessorStrategy,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_occurrence_instance_analysis import (
    SpellOccurrenceInstanceAnalysis,
)

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
        SpellCodegenModel,
    )
    from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
        SpellCompilerArtifact,
    )


OccurrenceKey = Tuple[str, int]
InstanceKey = Tuple[str, Optional[int]]


class SpellOccurrenceInstanceProcessorStrategy(SpellArtifactProcessorStrategy):
    """
    Build processor-owned occurrence instance/sharedness output from graph truth.

    Purpose:
        Consume the analyzer-owned occurrence graph and produce the
        instance/sharedness artifact plus the combined occurrence shape profile
        used by later model assembly.
    """

    __slots__ = ()

    @property
    def strategy_id(self) -> str:
        """
        Return the stable processor strategy id.
        """
        return "spell_occurrence_instance_processor"

    def process(
            self,
            spell: "Spell",
            artifact: "SpellCompilerArtifact",
            model: "SpellCodegenModel",
    ) -> None:
        """
        Build and publish the occurrence instance/sharedness artifact on the
        compiler artifact.
        """
        graph_analysis = artifact._occurrence_graph_analysis
        if graph_analysis is None:
            raise RuntimeError(
                "SpellOccurrenceInstanceProcessorStrategy requires occurrence graph analysis first."
            )
        order_analysis = model.occurrence_order_analysis
        if order_analysis is None:
            raise RuntimeError(
                "SpellOccurrenceInstanceProcessorStrategy requires occurrence order analysis first."
            )
        spellbook = spell._spellbook
        if spellbook is None:
            raise RuntimeError(
                "SpellOccurrenceInstanceProcessorStrategy requires a live owning Spellbook."
            )

        (
            instance_keys_by_spell_id,
            canonical_occurrences_by_spell_id,
            root_instance_key,
            shared_spell_ids,
        ) = self._build_instance_plan(
            occurrence_graph=graph_analysis.occurrence_graph,
            root_spell_id=graph_analysis.root_spell_id,
            spell_lookup=spellbook._spell_id_pool,
            root_path_id=graph_analysis.path_registry.root_path_id,
        )

        instance_analysis = SpellOccurrenceInstanceAnalysis(
            instance_keys_by_spell_id=instance_keys_by_spell_id,
            canonical_occurrences_by_spell_id=canonical_occurrences_by_spell_id,
            root_instance_key=root_instance_key,
            shared_spell_ids=shared_spell_ids,
        )
        previous_instance = model.occurrence_instance_analysis
        model.occurrence_instance_analysis = instance_analysis

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
        model.occurrence_shape_profile = (
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
        Best-effort cleanup for one superseded occurrence-instance artifact.
        """
        if previous is None or previous is current:
            return
        try:
            previous.cleanup()
        except Exception:
            pass

    @staticmethod
    def _is_shared_existence(
            existence: Existence,
    ) -> bool:
        """
        Determine whether an existence policy yields a shared instance.
        """
        return existence is not Existence.many

    @staticmethod
    def _occurrence_sort_key(
            occurrence: OccurrenceKey,
    ) -> Tuple[str, int]:
        """
        Build a deterministic ordering key for occurrence tuples.
        """
        if occurrence[1] is None:
            return occurrence[0], -1
        return occurrence[0], occurrence[1]

    def _build_instance_plan(
            self,
            *,
            occurrence_graph: Dict[OccurrenceKey, Dict[str, List[OccurrenceKey]]],
            root_spell_id: str,
            spell_lookup: Dict[str, "Spell"],
            root_path_id: int,
    ) -> Tuple[
        Dict[str, List[InstanceKey]],
        Dict[str, OccurrenceKey],
        InstanceKey,
        Set[str],
    ]:
        """
        Build per-spell instance keys and canonical occurrences.
        """
        occurrences_by_spell_id: Dict[str, List[OccurrenceKey]] = defaultdict(list)
        for occurrence in sorted(
                occurrence_graph.keys(),
                key=self._occurrence_sort_key,
        ):
            occurrences_by_spell_id[occurrence[0]].append(occurrence)

        instance_keys_by_spell_id: Dict[str, List[InstanceKey]] = {}
        canonical_occurrences_by_spell_id: Dict[str, OccurrenceKey] = {}
        shared_spell_ids: Set[str] = set()

        for spell_id in sorted(occurrences_by_spell_id.keys()):
            occurrences = sorted(
                occurrences_by_spell_id[spell_id],
                key=self._occurrence_sort_key,
            )
            if self._is_shared_existence(spell_lookup[spell_id].existence):
                shared_spell_ids.add(spell_id)
                canonical_occurrences_by_spell_id[spell_id] = self._select_canonical_occurrence(
                    occurrences
                )
                instance_keys_by_spell_id[spell_id] = [(spell_id, None)]
                continue
            instance_keys_by_spell_id[spell_id] = [
                (spell_id, path_id)
                for _, path_id in occurrences
            ]

        root_instance_key = self._instance_key_for_occurrence(
            occurrence=(root_spell_id, root_path_id),
            spell_lookup=spell_lookup,
        )
        return (
            instance_keys_by_spell_id,
            canonical_occurrences_by_spell_id,
            root_instance_key,
            shared_spell_ids,
        )

    def _instance_key_for_occurrence(
            self,
            *,
            occurrence: OccurrenceKey,
            spell_lookup: Dict[str, "Spell"],
    ) -> InstanceKey:
        """
        Map an occurrence to its instance key based on existence policy.
        """
        if self._is_shared_existence(spell_lookup[occurrence[0]].existence):
            return occurrence[0], None
        return occurrence[0], occurrence[1]

    def _select_canonical_occurrence(
            self,
            occurrences: Sequence[OccurrenceKey],
    ) -> OccurrenceKey:
        """
        Pick a stable occurrence for shared instance dependency paths.
        """
        return min(
            occurrences,
            key=self._occurrence_sort_key,
        )
