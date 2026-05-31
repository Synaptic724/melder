from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple

from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_injection_analysis import (
    SpellInjectionAnalysis,
    SpellInjectionInstanceSpec,
    SpellInjectionParamSource,
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


class SpellInjectionProcessorStrategy(SpellArtifactProcessorStrategy):
    """
    Fit the injection section of `SpellCodegenModel`.

    Purpose:
        Consume the already-fitted occurrence sections and produce per-instance
        injection wiring plus the summary facts that later planner work will use.
    """

    __slots__ = ()

    @property
    def strategy_id(self) -> str:
        """
        Return the stable processor strategy id.
        """
        return "spell_injection_processor"

    def process(
            self,
            spell: Spell,
            artifact: "SpellCompilerArtifact",
            model: "SpellCodegenModel",
    ) -> None:
        """
        Fit the injection model section.

        Contract:
            - Requires `graph_shape`, `instance_shape`, and `contract_shape`.
            - Writes only `model.injection_shape` plus compatible top-level
              summary selectors owned by this strategy.
            - Does not read or build old `InjectionPlan` objects.
        """
        _ = spell
        _ = artifact
        graph_shape = model.graph_shape
        if graph_shape is None:
            raise RuntimeError(
                "SpellInjectionProcessorStrategy requires graph_shape first."
            )
        instance_shape = model.instance_shape
        if instance_shape is None:
            raise RuntimeError(
                "SpellInjectionProcessorStrategy requires instance_shape first."
            )
        contract_shape = model.contract_shape
        if contract_shape is None:
            raise RuntimeError(
                "SpellInjectionProcessorStrategy requires contract_shape first."
            )

        injection_shape = SpellInjectionAnalysis(
            root_spell_id=graph_shape.root_spell_id,
            root_instance_key=instance_shape.root_instance_key,
            instance_specs_by_instance_key=self._build_instance_specs(
                occurrence_graph=graph_shape.occurrence_graph,
                instance_shape=instance_shape,
                contract_shape=contract_shape,
            ),
        )
        previous_injection_shape = model.injection_shape
        model.injection_shape = injection_shape
        model.root_dependency_count = injection_shape.root_dependency_count
        model.root_positional_override_relevant = (
            injection_shape.root_uses_positional_override
        )
        model.dependency_arity_histogram = (
            injection_shape.dependency_arity_histogram
        )
        self._cleanup_previous(previous_injection_shape, injection_shape)

    @staticmethod
    def _cleanup_previous(
            previous: Optional[SpellInjectionAnalysis],
            current: SpellInjectionAnalysis,
    ) -> None:
        """
        Best-effort cleanup for one superseded injection section.
        """
        if previous is None or previous is current:
            return
        try:
            previous.cleanup()
        except Exception:
            pass

    def _build_instance_specs(
            self,
            *,
            occurrence_graph: Dict[OccurrenceKey, Dict[str, list[OccurrenceKey]]],
            instance_shape,
            contract_shape,
    ) -> Dict[InstanceKey, SpellInjectionInstanceSpec]:
        """
        Build per-instance injection specs from fitted occurrence sections.

        Contract:
            - Shared spell ids resolve through canonical occurrences.
            - Non-shared spell ids resolve through path-bearing instance keys.
            - Contract payloads attach only to the matching provider
              occurrence.
        """
        instance_specs_by_instance_key: Dict[InstanceKey, SpellInjectionInstanceSpec] = {}

        for spell_id, instance_keys in instance_shape.instance_keys_by_spell_id.items():
            shared_spell = spell_id in instance_shape.shared_spell_ids
            canonical_occurrence = None
            if shared_spell:
                canonical_occurrence = (
                    instance_shape.canonical_occurrences_by_spell_id.get(spell_id)
                )
                if canonical_occurrence is None:
                    raise RuntimeError(
                        "Shared spell is missing a canonical occurrence."
                    )

            for instance_key in instance_keys:
                if shared_spell:
                    occurrence = canonical_occurrence
                else:
                    occurrence_path = instance_key[1]
                    if occurrence_path is None:
                        raise RuntimeError(
                            "Non-shared instance key is missing its occurrence path."
                        )
                    occurrence = (spell_id, occurrence_path)

                if occurrence is None:
                    raise RuntimeError(
                        "Injection occurrence resolution failed."
                    )

                dependencies = occurrence_graph[occurrence]
                contract_payload = contract_shape.contract_overrides_by_occurrence.get(
                    occurrence
                )
                normalized_contract_payload = self._clone_contract_payload(
                    contract_payload
                )
                param_sources: Dict[str, SpellInjectionParamSource] = {}
                allow_list_aggregation = False
                uses_positional_override = False

                for param_name, dependency_occurrences in dependencies.items():
                    dependency_keys = []
                    for dependency_occurrence in dependency_occurrences:
                        dependency_spell_id, dependency_path = dependency_occurrence
                        if dependency_spell_id in instance_shape.shared_spell_ids:
                            dependency_keys.append((dependency_spell_id, None))
                        else:
                            dependency_keys.append((dependency_spell_id, dependency_path))
                    if len(dependency_keys) > 1:
                        allow_list_aggregation = True
                    param_sources[param_name] = SpellInjectionParamSource(
                        kind="dependency",
                        dependency_keys=tuple(dependency_keys),
                        override_key=param_name,
                    )

                if normalized_contract_payload is not None:
                    if "__args__" in normalized_contract_payload:
                        uses_positional_override = True
                    for param_name in normalized_contract_payload.keys():
                        if param_name == "__args__":
                            continue
                        existing_param_source = param_sources.get(param_name)
                        if existing_param_source is None:
                            param_sources[param_name] = SpellInjectionParamSource(
                                kind="contract",
                                dependency_keys=(),
                                override_key=param_name,
                                contract_key=param_name,
                            )
                        else:
                            param_sources[param_name] = SpellInjectionParamSource(
                                kind=existing_param_source.kind,
                                dependency_keys=existing_param_source.dependency_keys,
                                override_key=existing_param_source.override_key or param_name,
                                contract_key=param_name,
                            )

                instance_specs_by_instance_key[instance_key] = SpellInjectionInstanceSpec(
                    param_sources=param_sources,
                    allow_list_aggregation=allow_list_aggregation,
                    uses_positional_override=uses_positional_override,
                    contract_payload=normalized_contract_payload,
                )

        return instance_specs_by_instance_key

    @staticmethod
    def _clone_contract_payload(
            payload: Optional[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """
        Clone contract payloads for injection-section ownership.
        """
        if payload is None:
            return None
        cloned_payload = dict(payload)
        if "__args__" in cloned_payload and isinstance(cloned_payload["__args__"], list):
            cloned_payload["__args__"] = tuple(cloned_payload["__args__"])
        return cloned_payload
