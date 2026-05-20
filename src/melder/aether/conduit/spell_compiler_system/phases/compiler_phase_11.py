from typing import Any, Dict, List, Optional, Tuple

from mypy_extensions import mypyc_attr

from melder.aether.conduit.spell_compiler_system.spell_compiler_artifact import (
    SpellCompilerArtifact,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_crafter.blueprints.execution_plan import (
    ExecutionPlan,
    ExecutionPlanBuilder,
    ExecutionPlanCallMode,
    ExecutionPlanVariant,
)
from melder.aether.spellbook.spell_types.spell_types import SpellType
from melder.utilities.interfaces.iinjectionplan import IInjectionPlan
from melder.utilities.interfaces.ioccurrenceplan import IOccurrencePlan
from melder.utilities.interfaces.ispell import ISpell
from melder.utilities.interfaces.ispellbook import ISpellbook
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent
from melder.aether.conduit.spell_compiler_system.phases.shared_compiler_executions import (
    SharedCompilerExecutions,
)


@mypyc_attr(native_class=True)
class CompilerPhase11:
    """
    Compiler phase 11 surface.

    Purpose:
        Expose the current execution-plan build behavior through a compiler-
        owned phase class.

    Contract:
        - Slot-only phase surface with no explicit `__init__`.
        - Directly ports the canonical `SpellCrafter` phase-11 behavior, except
          that it stops at the approved `11 -> 12` artifact handoff instead of
          immediately compiling phase 12 itself.
        - Does not own spell, artifact, or runtime collaborator lifecycle.
    """

    __slots__ = ()

    def _get_required_occurrence_plan_phase8(
            self,
            artifact: SpellCompilerArtifact,
    ) -> IOccurrencePlan:
        """
        Return the Phase 8 occurrence plan or raise.

        Returns:
            IOccurrencePlan: Attached Phase 8 occurrence plan.
        """
        occurrence_plan = artifact._occurrence_plan_phase8
        if occurrence_plan is None:
            raise RuntimeError("SpellCrafter Phase 8 occurrence plan is required.")
        return occurrence_plan

    def _freeze_phase11_schema_value(self, value: Any) -> Any:
        if value is None or isinstance(value, (bool, int, float, str)):
            return value
        if isinstance(value, dict):
            return tuple(
                sorted(
                    (
                        key,
                        self._freeze_phase11_schema_value(item),
                    )
                    for key, item in value.items()
                )
            )
        if isinstance(value, (list, tuple)):
            return tuple(
                self._freeze_phase11_schema_value(item)
                for item in value
            )
        if isinstance(value, set):
            return tuple(
                sorted(
                    (
                        self._freeze_phase11_schema_value(item)
                        for item in value
                    ),
                    key=repr,
                )
            )
        return repr(value)

    @staticmethod
    def _normalize_instance_key(
            instance_key: Tuple[str, Optional[int]],
    ) -> Tuple[str, Optional[int]]:
        return instance_key[0], instance_key[1]

    @staticmethod
    def _normalize_occurrence_key(
            occurrence_key: Tuple[str, Optional[int]],
    ) -> Tuple[str, Optional[int]]:
        return occurrence_key[0], occurrence_key[1]

    @staticmethod
    def _instance_key_sort_key(
            instance_key: Tuple[str, Optional[int]],
    ) -> Tuple[str, int]:
        path_id = instance_key[1]
        return (
            instance_key[0],
            -1 if path_id is None else path_id,
        )

    @staticmethod
    def _occurrence_key_sort_key(
            occurrence_key: Tuple[str, Optional[int]],
    ) -> Tuple[str, int]:
        path_id = occurrence_key[1]
        return (
            occurrence_key[0],
            -1 if path_id is None else path_id,
        )

    def _build_fast_transient_schema(
            self,
            transient_plan: Optional[Tuple[Any, ...]],
    ) -> Optional[Dict[str, Any]]:
        """
        Convert the Phase11 transient tuple into a schema-only IR payload.

        Purpose:
            Remove callable/object references from transient payload export while
            preserving all indices needed for no-overrides transient codegen.
        Contract:
            - Returns None when no transient plan exists.
            - Returned payload contains only ints and tuples of ints.
        Args:
            transient_plan:
                Phase 11 transient tuple payload.
        Returns:
            Optional[Dict[str, Any]]:
                Schema-only transient payload, or None.
        """
        if transient_plan is None:
            return None
        return {
            "step_count": transient_plan[0],
            "root_step_index": transient_plan[1],
            "call_modes": tuple(transient_plan[3]),
            "dep1": tuple(transient_plan[4]),
            "dep2a": tuple(transient_plan[5]),
            "dep2b": tuple(transient_plan[6]),
            "dep3a": tuple(transient_plan[7]),
            "dep3b": tuple(transient_plan[8]),
            "dep3c": tuple(transient_plan[9]),
            "dep4a": tuple(transient_plan[10]),
            "dep4b": tuple(transient_plan[11]),
            "dep4c": tuple(transient_plan[12]),
            "dep4d": tuple(transient_plan[13]),
            "dep5a": tuple(transient_plan[14]),
            "dep5b": tuple(transient_plan[15]),
            "dep5c": tuple(transient_plan[16]),
            "dep5d": tuple(transient_plan[17]),
            "dep5e": tuple(transient_plan[18]),
            "dep6a": tuple(transient_plan[19]),
            "dep6b": tuple(transient_plan[20]),
            "dep6c": tuple(transient_plan[21]),
            "dep6d": tuple(transient_plan[22]),
            "dep6e": tuple(transient_plan[23]),
            "dep6f": tuple(transient_plan[24]),
            "dep7a": tuple(transient_plan[25]),
            "dep7b": tuple(transient_plan[26]),
            "dep7c": tuple(transient_plan[27]),
            "dep7d": tuple(transient_plan[28]),
            "dep7e": tuple(transient_plan[29]),
            "dep7f": tuple(transient_plan[30]),
            "dep7g": tuple(transient_plan[31]),
            "dep8a": tuple(transient_plan[32]),
            "dep8b": tuple(transient_plan[33]),
            "dep8c": tuple(transient_plan[34]),
            "dep8d": tuple(transient_plan[35]),
            "dep8e": tuple(transient_plan[36]),
            "dep8f": tuple(transient_plan[37]),
            "dep8g": tuple(transient_plan[38]),
            "dep8h": tuple(transient_plan[39]),
        }

    def _build_fast_transient_signature(
            self,
            transient_schema: Optional[Dict[str, Any]],
    ) -> Optional[str]:
        """
        Build a deterministic signature for a Phase 11 fast transient plan.

        Purpose:
            Fingerprint transient plan structure without including call-target
            object identities, which are process-local and nondeterministic.
        Contract:
            - Returns None when no transient plan exists.
            - Signature includes step counts, call modes, and dependency index
              arrays used by no-overrides execution.
        Args:
            transient_schema:
                Schema-only transient payload exported by
                `_build_fast_transient_schema`.
        Returns:
            Optional[str]:
                Deterministic transient signature, or None.
        """
        if transient_schema is None:
            return None
        return SharedCompilerExecutions.hash_codegen_signature(
            transient_schema["step_count"],
            transient_schema["root_step_index"],
            transient_schema["call_modes"],
            transient_schema["dep1"],
            transient_schema["dep2a"],
            transient_schema["dep2b"],
            transient_schema["dep3a"],
            transient_schema["dep3b"],
            transient_schema["dep3c"],
            transient_schema["dep4a"],
            transient_schema["dep4b"],
            transient_schema["dep4c"],
            transient_schema["dep4d"],
            transient_schema["dep5a"],
            transient_schema["dep5b"],
            transient_schema["dep5c"],
            transient_schema["dep5d"],
            transient_schema["dep5e"],
            transient_schema["dep6a"],
            transient_schema["dep6b"],
            transient_schema["dep6c"],
            transient_schema["dep6d"],
            transient_schema["dep6e"],
            transient_schema["dep6f"],
            transient_schema["dep7a"],
            transient_schema["dep7b"],
            transient_schema["dep7c"],
            transient_schema["dep7d"],
            transient_schema["dep7e"],
            transient_schema["dep7f"],
            transient_schema["dep7g"],
            transient_schema["dep8a"],
            transient_schema["dep8b"],
            transient_schema["dep8c"],
            transient_schema["dep8d"],
            transient_schema["dep8e"],
            transient_schema["dep8f"],
            transient_schema["dep8g"],
            transient_schema["dep8h"],
        )

    def _build_phase12_no_overrides_step_signature_row(
            self,
            step: Any,
    ) -> Tuple[Any, ...]:
        """
        Build one deterministic signature row for no-overrides compile caching.

        Purpose:
            Capture only the step fields that influence phase12 no-overrides
            compiled source/namespace behaviour without constructing full IR
            payload dict rows.
        Contract:
            - Returns a tuple-only row with deterministic ordering.
            - Includes dependency, contract, lock, and registration semantics.
        Args:
            step:
                ExecutionPlanStep-like object.
        Returns:
            Tuple[Any, ...]:
                Deterministic row used by no-overrides plan signature hashing.
        """
        dependency_resolution_order = tuple(
            (
                param_name,
                tuple(dependency_keys),
            )
            for param_name, dependency_keys in step.dependency_resolution_order
        )
        contract_payload_items: Tuple[Any, ...] = ()
        if step.contract_payload:
            contract_payload_items = tuple(
                sorted(
                    (
                        param_name,
                        self._freeze_phase11_schema_value(value),
                    )
                    for param_name, value in step.contract_payload.items()
                )
            )
        return (
            tuple(step.instance_key),
            step.spell.spell_index.current,
            step.existence.name,
            step.creations_target_kind,
            dependency_resolution_order,
            bool(step.uses_positional_override),
            self._freeze_phase11_schema_value(step.contract_positional_override),
            bool(step.has_contract_payload),
            contract_payload_items,
            bool(step.use_spell_lock_hint),
            bool(step.must_register),
        )

    def _build_phase11_spell_signature_row(
            self,
            spell: ISpell,
    ) -> Tuple[Any, ...]:
        """
        Build a deterministic spell metadata row for Phase 11 no-overrides inputs.

        Purpose:
            Capture spell fields consumed by `ExecutionPlanBuilder.build` so
            phase11 can detect when a no-overrides rebuild is required.
        Contract:
            - Includes existence/register/disposal and optimistic-object identity.
            - Uses primitive/tuple values only for deterministic hashing.
        Args:
            spell:
                Spell referenced by occurrence execution order.
        Returns:
            Tuple[Any, ...]:
                Deterministic spell metadata row.
        """
        optimistic_object_identity = None
        if spell.user_created_object is not None:
            optimistic_object_identity = id(spell.user_created_object)
        is_callable_spell = spell.spell_type in (
            SpellType.SPELL,
            SpellType.SPELL_WITH_SPELLFRAME,
            SpellType.SPELL_WITH_BINDING_NAME,
            SpellType.SPELL_WITH_BINDING_NAME_WITH_SPELLFRAME,
            SpellType.METHOD,
            SpellType.METHOD_WITH_BINDING_NAME,
            SpellType.METHOD_WITH_SPELLFRAME,
            SpellType.METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME,
            SpellType.LAMBDA_METHOD_WITH_BINDING_NAME,
            SpellType.LAMBDA_METHOD_WITH_SPELLFRAME,
            SpellType.LAMBDA_METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME,
        )
        must_register = True
        if spell.existence is Existence.many and not spell.has_disposal_methods:
            must_register = False
        return (
            spell.spell_index.current,
            spell.existence.name,
            bool(spell.is_existing_creation),
            bool(is_callable_spell),
            bool(must_register),
            bool(spell.has_disposal_methods),
            tuple(spell.disposal_method_names),
            optimistic_object_identity,
        )

    @staticmethod
    def _build_phase11_injection_spec_signature_row(
            injection_spec: Any,
            *,
            include_override_metadata: bool = True,
    ) -> Tuple[Any, ...]:
        """
        Build deterministic InjectionSpec row for Phase 11 input signatures.

        Purpose:
            Normalize injection metadata used by `ExecutionPlanBuilder.build`
            without allocating Phase 11 steps.
        Contract:
            - Includes param source wiring, aggregation flags, and contract payload.
            - Returns tuple-only deterministic structure.
        Args:
            injection_spec:
                Phase 9 InjectionSpec-like object.
            include_override_metadata:
                Whether override metadata should be included in each param row.
        Returns:
            Tuple[Any, ...]:
                Deterministic signature row.
        """
        param_rows: List[Tuple[Any, ...]] = []
        param_sources = injection_spec.param_sources
        for param_name in sorted(param_sources.keys()):
            param_source = param_sources[param_name]
            dependency_keys = None
            if param_source.dependency_keys is not None:
                dependency_keys = tuple(
                    tuple(dependency_key)
                    for dependency_key in param_source.dependency_keys
                )
            override_key = None
            if include_override_metadata:
                override_key = param_source.override_key
            param_rows.append(
                (
                    param_name,
                    param_source.kind,
                    dependency_keys,
                    override_key,
                    param_source.contract_key,
                )
            )

        contract_payload = injection_spec.contract_payload
        normalized_contract_payload = None
        if contract_payload is not None:
            normalized_contract_payload = dict(contract_payload)
            if (
                    "__args__" in normalized_contract_payload
                    and isinstance(normalized_contract_payload["__args__"], list)
            ):
                normalized_contract_payload["__args__"] = tuple(
                    normalized_contract_payload["__args__"]
                )

        return (
            tuple(param_rows),
            bool(injection_spec.allow_list_aggregation),
            bool(injection_spec.uses_positional_override),
            normalized_contract_payload,
        )

    def _build_phase11_no_overrides_input_signature(
            self,
            *,
            occurrence_plan: IOccurrencePlan,
            injection_plan: Optional[IInjectionPlan],
            spell_lookup: Dict[str, ISpell],
    ) -> Optional[str]:
        """
        Build a deterministic no-overrides input signature for Phase 11 reuse.

        Purpose:
            Detect semantic drift in plan-builder inputs so repeated warm runs
            can safely skip redundant no-overrides full builds.
        Contract:
            - Returns `None` when required spell/injection inputs are missing,
              forcing the legacy rebuild path.
            - Includes occurrence graph rows, injection wiring rows, and spell
              metadata consumed by `ExecutionPlanBuilder.build`.
        Args:
            occurrence_plan:
                Phase 8 occurrence plan for this spell.
            injection_plan:
                Optional Phase 9 injection plan.
            spell_lookup:
                Spell lookup map keyed by spell id.
        Returns:
            Optional[str]:
                Deterministic input signature, or `None` when rebuild must not be
                elided due to missing inputs.
        """
        try:
            execution_order = tuple(occurrence_plan.execution_order)
            shared_spell_ids = occurrence_plan.shared_spell_ids
            shared_spell_ids_row = tuple(sorted(shared_spell_ids))
            root_instance_key = tuple(occurrence_plan.root_instance_key)
            root_spell_id = occurrence_plan.root_spell_id
            contract_dependencies_complete = bool(
                occurrence_plan.contract_dependencies_complete,
            )
            occurrence_graph = occurrence_plan.occurrence_graph
            instance_keys_by_spell_id = occurrence_plan.instance_keys_by_spell_id
            canonical_occurrences_by_spell_id = occurrence_plan.canonical_occurrences_by_spell_id
            contract_overrides_by_occurrence = (
                occurrence_plan.contract_overrides_by_occurrence
            )
        except AttributeError:
            return None

        spell_rows: List[Tuple[Any, ...]] = []
        occurrence_rows: List[Tuple[Any, ...]] = []

        for spell_id in execution_order:
            candidate_spell = spell_lookup.get(spell_id)
            if candidate_spell is None:
                return None
            spell_rows.append(self._build_phase11_spell_signature_row(candidate_spell))

            canonical_occurrence = canonical_occurrences_by_spell_id.get(spell_id)
            instance_keys = instance_keys_by_spell_id.get(spell_id, ())
            for instance_key in instance_keys:
                occurrence = self._normalize_occurrence_key(
                    (spell_id, instance_key[1])
                )
                graph_occurrence: Optional[Tuple[str, int]] = None
                if spell_id in shared_spell_ids and canonical_occurrence is not None:
                    occurrence = self._normalize_occurrence_key(
                        canonical_occurrence
                    )
                    graph_occurrence = canonical_occurrence
                elif instance_key[1] is not None:
                    graph_occurrence = (spell_id, instance_key[1])
                dependencies = (
                    occurrence_graph.get(graph_occurrence, {})
                    if graph_occurrence is not None
                    else {}
                )
                dependency_rows: List[Tuple[Any, ...]] = []
                for param_name in sorted(dependencies.keys()):
                    dependency_rows.append(
                        (
                            param_name,
                            tuple(
                                self._normalize_occurrence_key(
                                    dependency_occurrence
                                )
                                for dependency_occurrence in dependencies[param_name]
                            ),
                        )
                    )
                contract_payload = (
                    contract_overrides_by_occurrence.get(graph_occurrence)
                    if graph_occurrence is not None
                    else None
                )
                if contract_payload is not None and "__args__" in contract_payload:
                    args_payload = contract_payload["__args__"]
                    if isinstance(args_payload, list):
                        contract_payload = dict(contract_payload)
                        contract_payload["__args__"] = tuple(args_payload)
                occurrence_rows.append(
                    (
                        self._normalize_instance_key(instance_key),
                        self._normalize_occurrence_key(occurrence),
                        tuple(dependency_rows),
                        contract_payload,
                    )
                )

        injection_rows: Tuple[Any, ...] = ()
        if injection_plan is not None:
            try:
                injection_lookup = injection_plan.select_for_runtime(
                    root_spell_id=root_spell_id,
                )
            except AttributeError:
                return None
            if injection_lookup is None:
                return None
            injection_rows_list: List[Tuple[Any, ...]] = []
            for instance_key in sorted(injection_lookup.keys()):
                try:
                    injection_spec_row = self._build_phase11_injection_spec_signature_row(
                        injection_lookup[instance_key],
                        include_override_metadata=False,
                    )
                except AttributeError:
                    return None
                injection_rows_list.append(
                    (
                        self._normalize_instance_key(instance_key),
                        injection_spec_row,
                    )
                )
            injection_rows = tuple(injection_rows_list)

        return SharedCompilerExecutions.hash_codegen_signature(
            root_spell_id,
            root_instance_key,
            contract_dependencies_complete,
            execution_order,
            shared_spell_ids_row,
            tuple(spell_rows),
            tuple(occurrence_rows),
            injection_rows,
        )

    def _build_phase12_no_overrides_plan_signature(
            self,
            plan: ExecutionPlan,
            transient_schema: Optional[Dict[str, Any]],
    ) -> str:
        """
        Build deterministic no-overrides compile signature from a Phase11 plan.

        Purpose:
            Fingerprint compile-affecting plan semantics in phase11 hot path
            without building full no-overrides IR payload rows.
        Contract:
            - Includes root instance key, step semantic rows, and transient
              schema signature.
            - Returned signature changes when no-overrides compiler inputs drift.
        Args:
            plan:
                No-overrides execution plan.
            transient_schema:
                Schema-only transient payload for this plan.
        Returns:
            str:
                Deterministic compile cache signature.
        """
        step_signature_rows = tuple(
            self._build_phase12_no_overrides_step_signature_row(step)
            for step in plan.steps
        )
        transient_signature = self._build_fast_transient_signature(transient_schema)
        root_instance_key = None
        if plan.root_instance_key is not None:
            root_instance_key = self._normalize_instance_key(
                plan.root_instance_key
            )
        return SharedCompilerExecutions.hash_codegen_signature(
            plan.root_spell_id,
            root_instance_key,
            step_signature_rows,
            transient_signature,
        )

    def _cache_execution_plan_metrics(
            self,
            spell: ISpell,
            *,
            occurrence_plan: IOccurrencePlan,
            plan: ExecutionPlan,
    ) -> None:
        """
        Cache Phase 11 execution-plan metrics on the owning spell.

        Contract:
            - Requires valid Phase 8 occurrence plan and Phase 11 plan inputs.
            - Stores derived metrics on the spell for fast runtime inspection.
            - Intended for small/shallow graph path selection heuristics.
        Args:
            spell:
                Spell owning runtime metrics.
            occurrence_plan:
                Phase 8 occurrence plan.
            plan:
                Execution plan whose shape controls computed metrics.
        """
        if occurrence_plan is None or plan is None:
            return

        steps = plan.steps
        step_count = len(steps)
        unique_spell_count = len(plan.spell_id_step_index)

        max_dependency_count = 0
        has_contract_payloads = False
        has_existing_creations = False

        for step in steps:
            dependency_count = len(step.dependency_keys)
            if dependency_count > max_dependency_count:
                max_dependency_count = dependency_count
            if step.has_contract_payload:
                has_contract_payloads = True
            if step.spell.is_existing_creation:
                has_existing_creations = True

        max_occurrence_depth = 0
        occurrence_graph = occurrence_plan.occurrence_graph
        if occurrence_graph:
            path_registry = occurrence_plan.path_registry
            for _, path_id in occurrence_graph.keys():
                depth = path_registry.depth(path_id)
                if depth > max_occurrence_depth:
                    max_occurrence_depth = depth

        has_calln: Optional[bool] = None
        fast_plan = plan.fast_plan
        if fast_plan is not None:
            fast_call_modes = fast_plan[20]
            has_calln = ExecutionPlanCallMode.CALLN in fast_call_modes

        dispatch_route = "ENGINE"
        if plan.fast_transient_plan is not None and not has_existing_creations:
            if max_occurrence_depth <= 3 and step_count <= 8:
                dispatch_route = "FAST_TRANSIENT_TIER_0"
            elif max_occurrence_depth <= 6 and step_count <= 16 and max_dependency_count <= 8:
                dispatch_route = "FAST_TRANSIENT_TIER_1"
            elif max_occurrence_depth <= 8 and step_count <= 24 and max_dependency_count <= 8:
                dispatch_route = "FAST_TRANSIENT_TIER_2"
            elif max_occurrence_depth <= 9 and step_count <= 32 and max_dependency_count <= 10:
                dispatch_route = "FAST_TRANSIENT_TIER_3"
            else:
                dispatch_route = "ENGINE"

        spell.execution_plan_step_count = step_count
        spell.execution_plan_unique_spell_count = unique_spell_count
        spell.execution_plan_max_occurrence_depth = max_occurrence_depth
        spell.execution_plan_max_dependency_count = max_dependency_count
        spell.execution_plan_has_calln = has_calln
        spell.execution_plan_has_contract_payloads = has_contract_payloads
        spell.execution_plan_has_existing_creations = has_existing_creations
        spell.execution_plan_dispatch_route = dispatch_route

    def _build_execution_plan_variant(
            self,
            *,
            occurrence_plan: IOccurrencePlan,
            injection_plan: Optional[IInjectionPlan],
            spell_lookup: Dict[str, ISpell],
            plan_variant: str,
    ) -> ExecutionPlan:
        """
        Build one Phase 11 execution-plan variant from phase8/phase9 artifacts.

        Purpose:
            Provide the canonical builder path used when variant reuse is not
            possible or when a full rebuild is explicitly required.
        Contract:
            - Returns a fresh `ExecutionPlan` object for the requested variant.
            - Does not mutate source occurrence/injection artifacts.
        Args:
            occurrence_plan:
                Phase8 occurrence plan.
            injection_plan:
                Optional phase9 injection plan.
            spell_lookup:
                Spell lookup map keyed by spell id.
            plan_variant:
                Target `ExecutionPlanVariant` label.
        Returns:
            ExecutionPlan:
                Fresh execution plan for the requested variant.
        """
        builder = ExecutionPlanBuilder(
            occurrence_plan=occurrence_plan,
            injection_plan=injection_plan,
            spell_lookup=spell_lookup,
            plan_variant=plan_variant,
        )
        return builder.build()

    def _store_phase11_to_phase12_handoff(
            self,
            spell: ISpell,
            artifact: SpellCompilerArtifact,
            plan: Optional[ExecutionPlan],
    ) -> None:
        """
        Persist phase-11 handoff payloads/signatures required by phase-12.

        Purpose:
            Store no-overrides execution-plan schema and signatures directly on
            the owning artifact, and gate `resolution_complete` when the cached
            executor is still valid.
        Contract:
            - Clears phase-12 executor cache when a plan signature drifts.
            - Preserves `spell.resolution_complete = True` only when signature
              and executor cache line up.
            - Sets `resolution_complete = False` on missing or non-empty-plan
              signature changes.
        Args:
            spell:
                Spell that should receive resolution_complete state updates.
            artifact:
                Target artifact that stores phase11/phase12 handoff values.
            plan:
                No-overrides execution plan.
        Returns:
            None.
        """
        if plan is None or not plan.steps:
            artifact._phase11_no_overrides_transient_schema = None
            artifact._phase11_no_overrides_plan_signature = None
            artifact._phase12_no_overrides_executor = None
            artifact._phase12_no_overrides_executor_signature = None
            spell.resolution_complete = False
            return

        transient_schema = self._build_fast_transient_schema(plan.fast_transient_plan)
        plan_signature = self._build_phase12_no_overrides_plan_signature(
            plan=plan,
            transient_schema=transient_schema,
        )
        artifact._phase11_no_overrides_transient_schema = transient_schema
        artifact._phase11_no_overrides_plan_signature = plan_signature
        if artifact._phase12_no_overrides_executor_signature != plan_signature:
            artifact._phase12_no_overrides_executor = None
            artifact._phase12_no_overrides_executor_signature = None
            spell.resolution_complete = False
        elif artifact._phase12_no_overrides_executor is not None:
            spell.resolution_complete = True
        else:
            spell.resolution_complete = False

    def _mark_phase8_11_codegen_ir_dirty(
            self,
            artifact: SpellCompilerArtifact,
    ) -> None:
        """
        Mark phase8_11 codegen export as stale.

        Purpose:
            Record that one or more Phase8-11 artifacts are changed and a new IR
            export is required before consumers read phase8_11 payloads.
        Contract:
            - Idempotent; repeated calls keep the dirty state true.
            - Does not mutate codegen payloads directly.
        Returns:
            None.
        """
        artifact._phase8_11_codegen_ir_dirty = True

    def run(
            self,
            spell: ISpell,
            artifact: SpellCompilerArtifact,
            spellbook: ISpellbook,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        # ------------------------------------------------------------------
        # Phase 11 - Execution Assembly Plan
        # ------------------------------------------------------------------
        """
        Phase 11 - Execution plan compilation.

        Compiles a Phase 11 ExecutionPlan for spells using Phase 8-9
        artifacts. Existing-creation spells are treated as a no-op.
        Emits plan variants for override-free, override-aware, and
        override+mutation-aware execution plan.

        Contract:
            - Requires Phase 8 artifacts to be available.
            - Uses Phase 9 injection plan when available.
            - Replaces existing ExecutionPlan references for this spell.
            - Uses the Spellbook-managed spell_id_pool (spell_id -> ISpell) as the
              spell lookup map without rebuilding it per phase.
            - Reuses cached no-overrides plan when the deterministic Phase11
              no-overrides input signature is unchanged.
            - Reuses the full cached phase11 variant set when the signature is
              unchanged and cached sibling variants are available.
            - Falls back to the legacy no-overrides rebuild path when signature
              inputs are missing.
            - Stops at the approved phase-11/12 boundary by storing handoff
              state on the artifact instead of compiling phase 12 immediately.
        Args:
            spell:
                Spell being compiled.
            artifact:
                Spell compiler artifact containing phase-11 cached artifacts.
            spellbook:
                Spellbook used to resolve live spell lookup map.
            cancel_event:
                Optional cancellation signal shared across the scheduler.
        Raises:
            RuntimeError:
                If phase-8 or required phase-9 artifacts are missing.
        """
        artifact.check_cleaned()
        if spell.is_existing_creation:
            return

        occurrence_plan = self._get_required_occurrence_plan_phase8(artifact)
        injection_plan = artifact._injection_plan_phase9
        spell_lookup = spellbook._spell_id_pool

        # Fast key avoids rebuilding the deep phase11 no-overrides signature
        # when phase8/phase9 inputs and plan references are unchanged.
        phase11_no_overrides_fast_key = (
            artifact._phase8_occurrence_plan_input_signature,
            artifact._phase9_injection_plan_input_signature,
            id(occurrence_plan),
            id(injection_plan),
            id(spell_lookup),
        )
        can_reuse_no_overrides_fast_key = (
                artifact._phase8_occurrence_plan_input_signature is not None
                and (
                        injection_plan is None
                        or artifact._phase9_injection_plan_input_signature is not None
                )
        )
        no_overrides_input_signature: Optional[str]
        if (
                can_reuse_no_overrides_fast_key
                and artifact._phase11_no_overrides_fast_key == phase11_no_overrides_fast_key
                and artifact._phase11_no_overrides_input_signature is not None
        ):
            no_overrides_input_signature = artifact._phase11_no_overrides_input_signature
        else:
            no_overrides_input_signature = self._build_phase11_no_overrides_input_signature(
                occurrence_plan=occurrence_plan,
                injection_plan=injection_plan,
                spell_lookup=spell_lookup,
            )
            if can_reuse_no_overrides_fast_key:
                artifact._phase11_no_overrides_fast_key = phase11_no_overrides_fast_key
            else:
                artifact._phase11_no_overrides_fast_key = None
        previous_no_overrides_signature = artifact._phase11_no_overrides_input_signature
        no_overrides_signature_unchanged = (
                no_overrides_input_signature is not None
                and previous_no_overrides_signature == no_overrides_input_signature
        )
        if (
                no_overrides_signature_unchanged
                and artifact._execution_plan_phase11_no_overrides is not None
                and artifact._execution_plan_phase11_overrides is not None
                and artifact._execution_plan_phase11 is not None
        ):
            cached_plan_no_overrides = artifact._execution_plan_phase11_no_overrides
            artifact._phase11_no_overrides_input_signature = no_overrides_input_signature
            self._cache_execution_plan_metrics(
                spell,
                occurrence_plan=occurrence_plan,
                plan=cached_plan_no_overrides,
            )
            self._store_phase11_to_phase12_handoff(
                spell,
                artifact,
                cached_plan_no_overrides,
            )
            return

        if (
                no_overrides_signature_unchanged
                and artifact._execution_plan_phase11_no_overrides is not None
        ):
            plan_no_overrides = artifact._execution_plan_phase11_no_overrides
        else:
            plan_no_overrides = self._build_execution_plan_variant(
                occurrence_plan=occurrence_plan,
                injection_plan=injection_plan,
                spell_lookup=spell_lookup,
                plan_variant=ExecutionPlanVariant.NO_OVERRIDES_FAST,
            )
        artifact._phase11_no_overrides_input_signature = no_overrides_input_signature

        plan_overrides = self._build_execution_plan_variant(
            occurrence_plan=occurrence_plan,
            injection_plan=injection_plan,
            spell_lookup=spell_lookup,
            plan_variant=ExecutionPlanVariant.OVERRIDES,
        )

        plan_overrides_with_mutations = self._build_execution_plan_variant(
            occurrence_plan=occurrence_plan,
            injection_plan=injection_plan,
            spell_lookup=spell_lookup,
            plan_variant=ExecutionPlanVariant.OVERRIDES_WITH_MUTATIONS,
        )

        self._cache_execution_plan_metrics(
            spell,
            occurrence_plan=occurrence_plan,
            plan=plan_no_overrides,
        )

        # Hot-swap execution plans without cleaning previous plan objects
        # in-place; concurrent meld calls may still be executing old plans.
        artifact._execution_plan_phase11_no_overrides = plan_no_overrides
        artifact._execution_plan_phase11_overrides = plan_overrides
        artifact._execution_plan_phase11 = plan_overrides_with_mutations
        self._mark_phase8_11_codegen_ir_dirty(artifact)
        self._store_phase11_to_phase12_handoff(
            spell,
            artifact,
            plan_no_overrides,
        )
