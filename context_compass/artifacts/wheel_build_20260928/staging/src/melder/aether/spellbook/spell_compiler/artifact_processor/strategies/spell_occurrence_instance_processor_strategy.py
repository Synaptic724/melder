from collections import defaultdict
from typing import TYPE_CHECKING, Dict, List, Optional, Sequence, Set, Tuple

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_occurrence_instance_analysis import (
    SpellOccurrenceInstanceAnalysis,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.spell_artifact_processor_strategy import (
    SpellArtifactProcessorStrategy,
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
    Fit the occurrence instance/sharedness section of `SpellCodegenModel`.

    Purpose:
        Consume analyzer-owned graph truth and produce the instance-key and
        sharedness facts that describe what runtime objects will actually exist
        when the graph is executed.
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
            spell: Spell,
            artifact: SpellCompilerArtifact,
            model: SpellCodegenModel,
    ) -> None:
        """
        Fit the instance/sharedness model section.

        Contract:
            - Reads analyzer-owned `graph_shape` from the model shell.
            - Writes only `model.instance_shape` plus compatible top-level
              scalar facts owned by this strategy.
            - Does not synthesize a fake occurrence-plan adapter.
        """
        _ = artifact
        graph_shape = model.graph_shape
        if graph_shape is None:
            raise RuntimeError(
                "SpellOccurrenceInstanceProcessorStrategy requires graph_shape first."
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
            occurrence_graph=graph_shape.occurrence_graph,
            root_spell_id=graph_shape.root_spell_id,
            spell_lookup=spellbook._spell_id_pool,
            root_path_id=graph_shape.path_registry.root_path_id,
        )

        instance_shape = SpellOccurrenceInstanceAnalysis(
            instance_keys_by_spell_id=instance_keys_by_spell_id,
            canonical_occurrences_by_spell_id=canonical_occurrences_by_spell_id,
            root_instance_key=root_instance_key,
            shared_spell_ids=shared_spell_ids,
        )
        previous_instance_shape = model.instance_shape
        model.instance_shape = instance_shape
        model.node_count = instance_shape.unique_spell_count
        model.shared_node_count = instance_shape.shared_spell_count
        self._cleanup_previous(previous_instance_shape, instance_shape)

    @staticmethod
    def _cleanup_previous(
            previous: Optional[SpellOccurrenceInstanceAnalysis],
            current: SpellOccurrenceInstanceAnalysis,
    ) -> None:
        """
        Best-effort cleanup for one superseded instance/sharedness section.
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
            spell_lookup: Dict[str, Spell],
            root_path_id: int,
    ) -> Tuple[
        Dict[str, List[InstanceKey]],
        Dict[str, OccurrenceKey],
        InstanceKey,
        Set[str],
    ]:
        """
        Build per-spell instance keys and canonical occurrences.

        Contract:
            - `Existence.many` yields one instance per occurrence path.
            - Shared existences yield one canonical `(spell_id, None)` instance
              key plus a canonical occurrence for dependency routing.
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
                canonical_occurrences_by_spell_id[spell_id] = (
                    self._select_canonical_occurrence(occurrences)
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
            spell_lookup: Dict[str, Spell],
    ) -> InstanceKey:
        """
        Map one occurrence to its instance key based on existence policy.
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
