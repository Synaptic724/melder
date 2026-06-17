import inspect
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional, Tuple

from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.spellbook.configuration.system_state import SystemState
from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_occurrence_contract_analysis import (
    SpellOccurrenceContractAnalysis,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.spell_artifact_processor_strategy import (
    SpellArtifactProcessorStrategy,
)
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.utilities.helpers.general_helpers import EnumHelpers

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
        SpellCodegenModel,
    )
    from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
        SpellCompilerArtifact,
    )
    from melder.aether.spellbook.spellbook import Spellbook


OccurrenceKey = Tuple[str, int]


class SpellOccurrenceContractProcessorStrategy(SpellArtifactProcessorStrategy):
    """
    Fit the occurrence contract-routing section of `SpellCodegenModel`.

    Purpose:
        Consume analyzer-owned graph truth and produce the SpellContract
        provider-routing and payload facts that later planner work will need
        without leaving contract payload logic stranded in the analyzer lane.
    """

    __slots__ = ()

    @property
    def strategy_id(self) -> str:
        """
        Return the stable processor strategy id.
        """
        return "spell_occurrence_contract_processor"

    def process(
            self,
            spell: Spell,
            artifact: SpellCompilerArtifact,
            model: SpellCodegenModel,
    ) -> None:
        """
        Fit the contract-routing model section.

        Contract:
            - Reads analyzer-owned `graph_shape` from the model shell.
            - Writes only `model.contract_shape` plus compatible top-level
              `contract_payload_count`.
            - Does not write back onto `SpellCompilerArtifact`.
        """
        _ = artifact
        graph_shape = model.graph_shape
        if graph_shape is None:
            raise RuntimeError(
                "SpellOccurrenceContractProcessorStrategy requires graph_shape first."
            )
        spellbook = spell._spellbook
        if spellbook is None:
            raise RuntimeError(
                "SpellOccurrenceContractProcessorStrategy requires a live owning Spellbook."
            )

        (
            contract_overrides_by_occurrence,
            contract_overrides_by_spell_id,
            contract_dependencies_complete,
        ) = self._compile_contract_overrides(
            occurrence_graph=graph_shape.occurrence_graph,
            spell_lookup=spellbook._spell_id_pool,
            spellbook=spellbook,
            path_registry=graph_shape.path_registry,
        )

        contract_shape = SpellOccurrenceContractAnalysis(
            contract_overrides_by_occurrence=contract_overrides_by_occurrence,
            contract_overrides_by_spell_id=contract_overrides_by_spell_id,
            contract_dependencies_complete=contract_dependencies_complete,
        )
        previous_contract_shape = model.contract_shape
        model.contract_shape = contract_shape
        model.contract_payload_count = contract_shape.contract_payload_count
        self._cleanup_previous(previous_contract_shape, contract_shape)

    @staticmethod
    def _cleanup_previous(
            previous: Optional[SpellOccurrenceContractAnalysis],
            current: SpellOccurrenceContractAnalysis,
    ) -> None:
        """
        Best-effort cleanup for one superseded contract-routing section.
        """
        if previous is None or previous is current:
            return
        try:
            previous.cleanup()
        except Exception:
            pass

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

    def _compile_contract_overrides(
            self,
            *,
            occurrence_graph: Dict[OccurrenceKey, Dict[str, List[OccurrenceKey]]],
            spell_lookup: Dict[str, Spell],
            spellbook: Spellbook,
            path_registry: Any,
    ) -> Tuple[
        Dict[OccurrenceKey, Dict[str, Any]],
        Dict[str, List[Tuple[OccurrenceKey, Dict[str, Any]]]],
        bool,
    ]:
        """
        Compile SpellContract override payload maps for the model section.
        """
        overrides_by_occurrence: Dict[OccurrenceKey, Dict[str, Any]] = {}
        overrides_by_spell_id: Dict[str, List[Tuple[OccurrenceKey, Dict[str, Any]]]] = {}
        complete = True

        for occurrence in sorted(
                occurrence_graph.keys(),
                key=self._occurrence_sort_key,
        ):
            if not self._compile_contract_overrides_for_occurrence(
                    occurrence=occurrence,
                    overrides_by_occurrence=overrides_by_occurrence,
                    overrides_by_spell_id=overrides_by_spell_id,
                    spell_lookup=spell_lookup,
                    spellbook=spellbook,
                    path_registry=path_registry,
            ):
                complete = False

        return overrides_by_occurrence, overrides_by_spell_id, complete

    def _compile_contract_overrides_for_occurrence(
            self,
            *,
            occurrence: OccurrenceKey,
            overrides_by_occurrence: Dict[OccurrenceKey, Dict[str, Any]],
            overrides_by_spell_id: Dict[str, List[Tuple[OccurrenceKey, Dict[str, Any]]]],
            spell_lookup: Dict[str, Spell],
            spellbook: Spellbook,
            path_registry: Any,
    ) -> bool:
        """
        Compile SpellContract override payloads for a single occurrence.
        """
        spell = spell_lookup.get(occurrence[0])
        if spell is None:
            raise RuntimeError(
                "Occurrence spell could not be resolved from the spell lookup."
            )

        complete = True
        allow_missing = self._allow_missing_contract_providers(spellbook)

        for param_name, contract in self._iter_spell_contract_defaults(spell):
            target_spell_id = self._resolve_spell_contract_spell_id(
                contract=contract,
                consumer_spell=spell,
                param_name=param_name,
                spellbook=spellbook,
                allow_missing=allow_missing,
            )
            if target_spell_id is None:
                complete = False
                continue

            child_occurrence = (
                target_spell_id,
                path_registry.extend_path(occurrence[1], param_name),
            )
            normalized_payload = self._normalize_contract_override_payload(
                payload=contract.spell_override,
                consumer_spell_id=spell.spell_index.selected_spell_id or spell.spell_id,
                consumer_spell_name=spell.spell_name,
                param_name=param_name,
            )
            if not normalized_payload:
                continue

            self._record_contract_override(
                occurrence=child_occurrence,
                spell_id=target_spell_id,
                overrides_by_occurrence=overrides_by_occurrence,
                overrides_by_spell_id=overrides_by_spell_id,
                normalized_payload=normalized_payload,
            )

        return complete

    @staticmethod
    def _iter_spell_contract_defaults(
            spell: Spell,
    ) -> Iterable[Tuple[str, SpellContract]]:
        """
        Yield SpellContract defaults discovered in the spell's callable surface.
        """
        contracts: List[Tuple[str, SpellContract]] = []
        if spell.is_existing_creation:
            signature = inspect.signature(spell.spell)
            for param_name, parameter in signature.parameters.items():
                if param_name in ("self", "cls"):
                    continue
                if parameter.kind in (
                        inspect.Parameter.VAR_POSITIONAL,
                        inspect.Parameter.VAR_KEYWORD,
                ):
                    continue
                if parameter.default is inspect.Parameter.empty:
                    continue
                if isinstance(parameter.default, SpellContract):
                    contracts.append((param_name, parameter.default))
            return contracts

        if spell._compiler_artifact._requirements is not None:
            for parameter in spell._compiler_artifact._requirements.parameters:
                if parameter.di_shape is ParameterDIShape.SPELL_CONTRACT:
                    if isinstance(parameter.default_value, SpellContract):
                        contracts.append((parameter.name, parameter.default_value))
            return contracts

        signature = inspect.signature(spell.spell)
        for param_name, parameter in signature.parameters.items():
            if param_name in ("self", "cls"):
                continue
            if parameter.kind in (
                    inspect.Parameter.VAR_POSITIONAL,
                    inspect.Parameter.VAR_KEYWORD,
            ):
                continue
            if parameter.default is inspect.Parameter.empty:
                continue
            if isinstance(parameter.default, SpellContract):
                contracts.append((param_name, parameter.default))

        return contracts

    def _resolve_spell_contract_spell_id(
            self,
            *,
            contract: SpellContract,
            consumer_spell: Spell,
            param_name: str,
            spellbook: Spellbook,
            allow_missing: bool = False,
    ) -> Optional[str]:
        """
        Resolve a SpellContract to a concrete provider spell id.
        """
        consumer_spell_id = consumer_spell.spell_index.selected_spell_id
        if consumer_spell_id is None:
            consumer_spell_id = consumer_spell.spell_id

        contracted_candidates = self._collect_contracted_contract_candidates(
            contract_key=contract.canonical_key,
            spellbook=spellbook,
        )
        if len(contracted_candidates) > 1:
            raise MeldExecutionError(
                spell_id=consumer_spell_id,
                spell_name=consumer_spell.spell_name,
                node_id=consumer_spell_id,
                param_name=param_name,
                message=(
                    "SpellContract resolved to multiple contracted spells. "
                    "Use distinct bindings or remove the ambiguous contracts."
                ),
            )
        if len(contracted_candidates) == 1:
            return contracted_candidates[0].spell_index.selected_spell_id

        if allow_missing:
            return None
        raise MeldExecutionError(
            spell_id=consumer_spell_id,
            spell_name=consumer_spell.spell_name,
            node_id=consumer_spell_id,
            param_name=param_name,
            message=(
                "SpellContract could not be resolved. "
                "No contracted spell matched the contract."
            ),
        )

    @staticmethod
    def _collect_contracted_contract_candidates(
            *,
            contract_key: Tuple[str, str],
            spellbook: Spellbook,
    ) -> List[Spell]:
        """
        Collect contracted spell candidates that satisfy the contract key.
        """
        contracted_candidates: List["Spell"] = []
        for conduit_id in sorted(spellbook._lookup_contracted_spells.keys()):
            spell_index = spellbook._lookup_contracted_spells[conduit_id].get(contract_key)
            if spell_index is None:
                continue
            contracted_map = spellbook._contracted_spells.get(conduit_id)
            if contracted_map is None:
                continue
            spell_obj = contracted_map.get(spell_index)
            if spell_obj is None:
                continue
            contracted_candidates.append(spell_obj)

        contracted_candidates.sort(
            key=lambda spell: spell.spell_index.selected_spell_id or spell.spell_id
        )
        return contracted_candidates

    @staticmethod
    def _normalize_contract_override_payload(
            *,
            payload: Any,
            consumer_spell_id: str,
            consumer_spell_name: str,
            param_name: str,
    ) -> Dict[str, Any]:
        """
        Normalize a SpellContract override payload for model storage.
        """
        if payload is None:
            return {}
        if isinstance(payload, dict):
            normalized_payload: Dict[str, Any] = {}
            for key, value in payload.items():
                if key == "__args__":
                    if not isinstance(value, (list, tuple)):
                        raise MeldExecutionError(
                            spell_id=consumer_spell_id,
                            spell_name=consumer_spell_name,
                            node_id=consumer_spell_id,
                            param_name=param_name,
                            message="SpellContract __args__ override must be a list or tuple.",
                        )
                    normalized_payload[key] = tuple(value)
                    continue
                normalized_payload[key] = value
            return normalized_payload
        if isinstance(payload, (list, tuple)):
            return {"__args__": tuple(payload)}
        raise MeldExecutionError(
            spell_id=consumer_spell_id,
            spell_name=consumer_spell_name,
            node_id=consumer_spell_id,
            param_name=param_name,
            message="SpellContract spell_override must be a dict, list, or tuple.",
        )

    @staticmethod
    def _record_contract_override(
            *,
            occurrence: OccurrenceKey,
            spell_id: str,
            overrides_by_occurrence: Dict[OccurrenceKey, Dict[str, Any]],
            overrides_by_spell_id: Dict[str, List[Tuple[OccurrenceKey, Dict[str, Any]]]],
            normalized_payload: Dict[str, Any],
    ) -> None:
        """
        Record a normalized SpellContract override payload.
        """
        stored_payload = dict(normalized_payload)
        if "__args__" in stored_payload and isinstance(stored_payload["__args__"], list):
            stored_payload["__args__"] = tuple(stored_payload["__args__"])
        overrides_by_occurrence[occurrence] = stored_payload
        overrides_by_spell_id.setdefault(spell_id, []).append(
            (occurrence, stored_payload)
        )

    @staticmethod
    def _allow_missing_contract_providers(
            spellbook: Spellbook,
    ) -> bool:
        """
        Determine whether processor analysis may tolerate missing providers.
        """
        if spellbook._aetheric_frame_configuration is None:
            raise RuntimeError("Root spellbook has no frame configuration.")
        return EnumHelpers.convert_enum_and_check(
            spellbook._aetheric_frame_configuration.system_state,
            SystemState,
        ) is SystemState.dynamic
