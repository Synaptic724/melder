from typing import Any, Callable, Dict, Optional, Sequence, Tuple

from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_no_overrides_codegen_creation_compiler import (
    compile_no_overrides_codegen_creation_executor_from_plan,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_overrides_codegen_creation_compiler import (
    _compile_overrides_codegen_creation_executor_from_code_object_with_prefilter_cache,
    build_overrides_codegen_creation_step_target_counts_from_rows,
    compile_overrides_codegen_creation_executor,
    compile_overrides_codegen_creation_executor_code_object,
    emit_overrides_codegen_creation_executor_shape_source,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.phase11_codegen_creation_shared import (
    Phase11CodegenCreationShared as SharedCompilerExecutions,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.generalized_codegen_creation_state import (
    GeneralizedCodegenCreationState,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.shared_strategy_assets.codegen_creation_family_step import (
    CodegenCreationFamilyStep,
)
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError


class GeneralizedFinalizeCreationContextStep(CodegenCreationFamilyStep):
    """
    Generalized family final output step.

    Purpose:
        Build the final override runtime callable and finish the narrow
        `SpellCodegenCreation` output from family-local scratch state.
    """

    __slots__ = ()

    @property
    def step_id(self) -> str:
        """
        Return the stable finalization step id.
        """
        return "generalized_finalize_creation_context"

    def apply(
            self,
            state: GeneralizedCodegenCreationState,
    ) -> None:
        """
        Build the final runtime doors from generalized family scratch state.
        """
        spell_codegen_model = state.spell_codegen_model
        spell_codegen_plan = state.spell_codegen_plan
        spell_codegen_creation = state.spell_codegen_creation

        no_overrides_plan = spell_codegen_plan.no_overrides_plan
        overrides_plan = spell_codegen_plan.overrides_plan
        if no_overrides_plan is None:
            raise RuntimeError(
                "Generalized finalize creation-context step requires a no_overrides_plan."
            )
        if overrides_plan is None:
            raise RuntimeError(
                "Generalized finalize creation-context step requires an overrides_plan."
            )

        route_key = state.resolve_route_key
        if route_key is None:
            route_key = self._resolve_route_key(spell_codegen_model)
        base_no_overrides_executor = state.base_no_overrides_executor
        if base_no_overrides_executor is None:
            base_no_overrides_executor = (
                self._build_base_no_overrides_executor(no_overrides_plan)
            )
            state.base_no_overrides_executor = base_no_overrides_executor
            spell_codegen_creation.no_overrides_executor = (
                base_no_overrides_executor
            )

        root_spell = state.root_spell
        if root_spell is None:
            root_spell = self._resolve_root_spell(
                spell_codegen_model=spell_codegen_model,
                spell_codegen_plan=spell_codegen_plan,
            )
            state.root_spell = root_spell

        overrides_runtime = self._build_overrides_runtime(
            spell_codegen_model=spell_codegen_model,
            overrides_plan=overrides_plan,
            root_spell=root_spell,
            base_no_overrides_executor=base_no_overrides_executor,
            override_targeting=state.override_targeting,
            plan_signature=state.override_plan_signature,
            path_registry=state.override_path_registry,
            plan_rows=state.override_plan_rows,
            override_root_spell_id=state.override_root_spell_id,
            spell_lookup=state.override_spell_lookup,
            empty_shape_key=state.override_empty_shape_key,
            baseline_executor=state.override_baseline_executor,
        )

        state.overrides_executor = overrides_runtime
        spell_codegen_creation.no_overrides_executor = base_no_overrides_executor
        spell_codegen_creation.overrides_executor = overrides_runtime
        spell_codegen_creation.metadata["resolve_route_key"] = route_key
        spell_codegen_creation.metadata["fast_transient_no_overrides_enabled"] = (
            state.fast_transient_no_overrides_enabled
        )
        spell_codegen_creation.metadata["no_overrides_lane_id"] = (
            no_overrides_plan.lane_id
        )
        spell_codegen_creation.metadata["override_lane_id"] = overrides_plan.lane_id
        spell_codegen_creation.metadata["no_overrides_fast_transient_available"] = (
            no_overrides_plan.fast_transient_plan is not None
        )
        spell_codegen_creation.metadata["override_step_count"] = (
            len(overrides_plan.steps)
        )

    @staticmethod
    def _resolve_route_key(
            spell_codegen_model: object,
    ) -> str:
        """
        Resolve the current runtime route key from processor-owned truth.
        """
        if spell_codegen_model.build_kind == "existing_creation":
            return "existing_creation"

        route_family = spell_codegen_model.route_family
        if route_family in (
                "spellspace",
                "unique_per_conduit",
                "many",
                "shared",
        ):
            return route_family
        raise RuntimeError(
            "SpellCodegenModel route_family is not ready for generalized creation-context "
            f"build: {route_family!r}."
        )

    @staticmethod
    def _resolve_root_spell(
            *,
            spell_codegen_model: object,
            spell_codegen_plan: object,
    ) -> Any:
        """
        Resolve the root runtime spell object for phase-11 executor construction.
        """
        no_overrides_plan = spell_codegen_plan.no_overrides_plan
        if no_overrides_plan is not None:
            root_spell_id = no_overrides_plan.root_spell_id
            runtime_shape = spell_codegen_model.spell_runtime_shape
            if runtime_shape is not None:
                record = runtime_shape.records_by_spell_id.get(root_spell_id)
                if record is not None:
                    return record.spell
            for step in no_overrides_plan.steps:
                if step.spell.spell_index.current == root_spell_id:
                    return step.spell
        raise RuntimeError(
            "generalized creation-context finalize step could not resolve the root spell object."
        )

    @staticmethod
    def _build_base_no_overrides_executor(
            no_overrides_plan: Any,
    ) -> Callable[..., Any]:
        """
        Build the underlying no-overrides route executor from the lane plan.
        """
        transient_schema = SharedCompilerExecutions.build_fast_transient_schema(
            no_overrides_plan.fast_transient_plan,
        )
        executor = compile_no_overrides_codegen_creation_executor_from_plan(
            plan=no_overrides_plan,
            transient_schema=transient_schema,
        )
        if executor is None:
            raise RuntimeError(
                "generalized creation-context finalize step could not build a no-overrides executor."
            )
        return executor

    def _build_overrides_runtime(
            self,
            *,
            spell_codegen_model: object,
            overrides_plan: Any,
            root_spell: Any,
            base_no_overrides_executor: Callable[..., Any],
            override_targeting: Optional[Any],
            plan_signature: Optional[Tuple[Any, ...]],
            path_registry: Optional[Any],
            plan_rows: Optional[Sequence[Dict[str, Any]]],
            override_root_spell_id: Optional[str],
            spell_lookup: Optional[Dict[str, Any]],
            empty_shape_key: Optional[Tuple[Any, ...]],
            baseline_executor: Optional[Callable[..., Any]],
    ) -> Callable[..., Any]:
        """
        Build the heavy override runtime callable closed over generalized state.
        """
        if override_targeting is None:
            raise RuntimeError(
                "generalized creation-context finalize step requires override_targeting."
            )
        if path_registry is None:
            graph_shape = spell_codegen_model.graph_shape
            path_registry = None if graph_shape is None else graph_shape.path_registry
        if plan_rows is None:
            plan_rows = self._build_override_plan_rows(overrides_plan.steps)
        if spell_lookup is None:
            spell_lookup = self._build_spell_lookup(overrides_plan.steps)
        if plan_signature is None:
            plan_signature = self._build_override_plan_signature(
                overrides_plan=overrides_plan,
                plan_rows=plan_rows,
            )
        if override_root_spell_id is None:
            override_root_spell_id = overrides_plan.root_spell_id
        if empty_shape_key is None:
            empty_shape_key = (
                plan_signature,
                (),
                -1,
            )
        if baseline_executor is None:
            baseline_executor = compile_overrides_codegen_creation_executor(
                execution_plan=None,
                override_targets_by_spell_id={},
                any_overrides_present=False,
                path_registry=path_registry,
                plan_rows=plan_rows,
                root_spell_id=override_root_spell_id,
                spell_lookup=spell_lookup,
            )

        override_specialization_cache: Dict[Tuple[Any, ...], Callable[..., Any]] = {}
        override_executor_source_cache_by_plan_signature: Dict[
            Tuple[Any, ...],
            str,
        ] = {}
        override_executor_code_object_cache_by_plan_signature: Dict[
            Tuple[Any, ...],
            Any,
        ] = {}
        override_prefilter_step_targets_cache: Dict[
            Tuple[Any, ...],
            Tuple[Tuple[Any, ...], ...],
        ] = {}
        override_prefilter_path_metadata_cache: Dict[Any, Tuple[Any, Any]] = {}
        override_last_state: Dict[str, Any] = {
            "socket_shape": None,
            "root_positional_arity": -2,
            "executor": None,
        }
        if baseline_executor is not None:
            override_specialization_cache[empty_shape_key] = baseline_executor

        root_spell_id = root_spell.spell_index.current or root_spell.spell_id

        def execute_with_overrides(
                caller_creations: Any,
                overrides: Optional[dict[str, Any]],
                caller_creations_lock_held: bool,
        ) -> Any:
            owner_creations = root_spell._owner_creations
            override_payload = overrides
            root_positional_override: Optional[Sequence[Any]] = None
            override_map: Dict[Any, Any] = {}
            socket_shape: Tuple[Tuple[Any, ...], ...] = ()

            if override_payload is None:
                if baseline_executor is not None:
                    return baseline_executor(
                        caller_creations,
                        override_map,
                        root_positional_override,
                        owner_creations=owner_creations,
                        caller_creations_lock_held=caller_creations_lock_held,
                    )
                executor = self._get_or_compile_override_executor(
                    shape_key=empty_shape_key,
                    override_targets_by_spell_id={},
                    any_overrides_present=False,
                    path_registry=path_registry,
                    plan_rows=plan_rows,
                    root_spell_id=override_root_spell_id,
                    spell_lookup=spell_lookup,
                    override_specialization_cache=override_specialization_cache,
                    override_executor_source_cache_by_plan_signature=(
                        override_executor_source_cache_by_plan_signature
                    ),
                    override_executor_code_object_cache_by_plan_signature=(
                        override_executor_code_object_cache_by_plan_signature
                    ),
                    override_prefilter_step_targets_cache=(
                        override_prefilter_step_targets_cache
                    ),
                    override_prefilter_path_metadata_cache=(
                        override_prefilter_path_metadata_cache
                    ),
                )
                return executor(
                    caller_creations,
                    override_map,
                    root_positional_override,
                    owner_creations=owner_creations,
                    caller_creations_lock_held=caller_creations_lock_held,
                )

            if override_payload:
                target_payload, root_positional_override = self._split_override_payload(
                    spell=root_spell,
                    override_payload=override_payload,
                )
                if target_payload:
                    try:
                        override_map, socket_shape = (
                            override_targeting._apply_with_socket_shape_prechecked(
                                spell_override=target_payload,
                            )
                        )
                    except MeldExecutionError:
                        raise
                    except Exception as exc:
                        raise MeldExecutionError(
                            spell_id=root_spell_id,
                            spell_name=root_spell.spell_name,
                            message="Failed to apply overrides.",
                            inner=exc,
                        ) from exc

            if root_positional_override is None:
                root_positional_arity = -1
            else:
                root_positional_arity = len(root_positional_override)
            if (
                    socket_shape is override_last_state["socket_shape"]
                    and root_positional_arity
                    == override_last_state["root_positional_arity"]
            ):
                executor = override_last_state["executor"]
            else:
                executor = None

            if executor is None:
                shape_key = (
                    plan_signature,
                    socket_shape,
                    root_positional_arity,
                )
                executor = override_specialization_cache.get(shape_key)
                if executor is None:
                    if override_map:
                        override_targets_by_spell_id = (
                            self._collect_override_targets_from_socket_shape(
                                override_map=override_map,
                                socket_shape=socket_shape,
                            )
                        )
                    else:
                        override_targets_by_spell_id = {}
                    executor = self._get_or_compile_override_executor(
                        shape_key=shape_key,
                        override_targets_by_spell_id=override_targets_by_spell_id,
                        any_overrides_present=overrides is not None,
                        path_registry=path_registry,
                        plan_rows=plan_rows,
                        root_spell_id=override_root_spell_id,
                        spell_lookup=spell_lookup,
                        override_specialization_cache=(
                            override_specialization_cache
                        ),
                        override_executor_source_cache_by_plan_signature=(
                            override_executor_source_cache_by_plan_signature
                        ),
                        override_executor_code_object_cache_by_plan_signature=(
                            override_executor_code_object_cache_by_plan_signature
                        ),
                        override_prefilter_step_targets_cache=(
                            override_prefilter_step_targets_cache
                        ),
                        override_prefilter_path_metadata_cache=(
                            override_prefilter_path_metadata_cache
                        ),
                        prefilter_cache_key=(
                            plan_signature,
                            socket_shape,
                        ),
                    )
                override_last_state["socket_shape"] = socket_shape
                override_last_state["root_positional_arity"] = (
                    root_positional_arity
                )
                override_last_state["executor"] = executor

            if executor is None:
                raise RuntimeError("Override executor resolution failed.")

            return executor(
                caller_creations,
                override_map,
                root_positional_override,
                owner_creations=owner_creations,
                caller_creations_lock_held=caller_creations_lock_held,
            )

        return execute_with_overrides

    @staticmethod
    def _build_override_plan_rows(
            steps: Sequence[Any],
    ) -> Tuple[Dict[str, Any], ...]:
        """
        Build deterministic schema rows from generalized override lane steps.
        """
        return tuple(
            SharedCompilerExecutions.build_phase11_step_ir_row(
                step,
                include_override_metadata=True,
            )
            for step in steps
        )

    @staticmethod
    def _build_override_plan_signature(
            *,
            overrides_plan: Any,
            plan_rows: Sequence[Dict[str, Any]],
    ) -> Tuple[Any, ...]:
        """
        Build the stable override plan signature used by specialization caching.
        """
        steps_rows_signature = SharedCompilerExecutions.hash_codegen_signature(
            tuple(plan_rows)
        )
        step_spell_ids = tuple(
            step.spell.spell_index.current
            for step in overrides_plan.steps
        )
        return (
            "generalized_overrides_lane_plan",
            SharedCompilerExecutions.hash_codegen_signature(
                overrides_plan.lane_id,
                overrides_plan.root_spell_id,
                step_spell_ids,
                steps_rows_signature,
            ),
            steps_rows_signature,
        )

    @staticmethod
    def _build_spell_lookup(
            steps: Sequence[Any],
    ) -> Dict[str, Any]:
        """
        Build a stable spell lookup keyed by spell_id from lane-plan steps.
        """
        spell_lookup: Dict[str, Any] = {}
        for step in steps:
            spell_id = step.spell.spell_index.current
            if spell_id in spell_lookup:
                continue
            spell_lookup[spell_id] = step.spell
        return spell_lookup

    @staticmethod
    def _split_override_payload(
            *,
            spell: Any,
            override_payload: Dict[str, Any],
    ) -> Tuple[Dict[str, Any], Optional[Sequence[Any]]]:
        """
        Split root positional overrides from targeted socket overrides.
        """
        raw_args = override_payload.get("__args__")
        if raw_args is None:
            return override_payload, None
        if isinstance(raw_args, tuple):
            normalized_root_args = raw_args
        elif isinstance(raw_args, list):
            normalized_root_args = tuple(raw_args)
        else:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current or spell.spell_id,
                spell_name=spell.spell_name,
                message="__args__ override must be a list or tuple.",
            )
        override_payload_size = len(override_payload)
        if override_payload_size == 1:
            return {}, normalized_root_args
        if override_payload_size == 2:
            for param_name, value in override_payload.items():
                if param_name != "__args__":
                    return {param_name: value}, normalized_root_args
        normalized_payload: Dict[str, Any] = {}
        for param_name, value in override_payload.items():
            if param_name == "__args__":
                continue
            normalized_payload[param_name] = value
        return normalized_payload, normalized_root_args

    @staticmethod
    def _collect_override_targets_from_socket_shape(
            *,
            override_map: Dict[Any, Any],
            socket_shape: Tuple[Tuple[Any, ...], ...],
    ) -> Dict[str, Tuple[Any, ...]]:
        """
        Group override targets by spell id from precomputed socket-shape rows.
        """
        if not socket_shape:
            return {}

        shape_row_to_socket_ref: Dict[Tuple[Any, ...], Any] = {}
        for socket_ref in override_map:
            shape_row_to_socket_ref[
                (
                    socket_ref.node_id,
                    socket_ref.param_path_id,
                    socket_ref.param_name,
                    GeneralizedFinalizeCreationContextStep._socket_kind_value(
                        socket_ref
                    ),
                )
            ] = socket_ref

        by_spell_id: Dict[str, list[Any]] = {}
        current_spell_id: Optional[str] = None
        current_bucket: Optional[list[Any]] = None
        for shape_row in socket_shape:
            node_id, _, _, _ = shape_row
            socket_ref = shape_row_to_socket_ref[shape_row]
            if node_id != current_spell_id:
                current_spell_id = node_id
                current_bucket = [socket_ref]
                by_spell_id[node_id] = current_bucket
            else:
                if current_bucket is None:
                    raise RuntimeError(
                        "Override target bucket was not initialized."
                    )
                current_bucket.append(socket_ref)

        return {
            spell_id: tuple(refs)
            for spell_id, refs in by_spell_id.items()
        }

    @staticmethod
    def _socket_kind_value(socket_ref: Any) -> int:
        """
        Return the stable socket-kind integer for one override target row.
        """
        try:
            return socket_ref.socket_kind_value
        except AttributeError:
            return socket_ref.socket_kind.value

    def _get_or_compile_override_executor(
            self,
            *,
            shape_key: Tuple[Any, ...],
            override_targets_by_spell_id: Dict[str, Tuple[Any, ...]],
            any_overrides_present: bool,
            path_registry: Optional[Any],
            plan_rows: Sequence[Dict[str, Any]],
            root_spell_id: Optional[str],
            spell_lookup: Dict[str, Any],
            override_specialization_cache: Dict[
                Tuple[Any, ...],
                Callable[..., Any],
            ],
            override_executor_source_cache_by_plan_signature: Dict[
                Tuple[Any, ...],
                str,
            ],
            override_executor_code_object_cache_by_plan_signature: Dict[
                Tuple[Any, ...],
                Any,
            ],
            override_prefilter_step_targets_cache: Dict[
                Tuple[Any, ...],
                Tuple[Tuple[Any, ...], ...],
            ],
            override_prefilter_path_metadata_cache: Dict[Any, Tuple[Any, Any]],
            prefilter_cache_key: Optional[Tuple[Any, ...]] = None,
    ) -> Callable[..., Any]:
        """
        Return a cached override executor, compiling it on structural miss.
        """
        executor = override_specialization_cache.get(shape_key)
        if executor is not None:
            return executor
        executor = self._compile_override_executor_from_plan_rows(
            shape_key=shape_key,
            override_targets_by_spell_id=override_targets_by_spell_id,
            any_overrides_present=any_overrides_present,
            path_registry=path_registry,
            plan_rows=plan_rows,
            root_spell_id=root_spell_id,
            spell_lookup=spell_lookup,
            override_executor_source_cache_by_plan_signature=(
                override_executor_source_cache_by_plan_signature
            ),
            override_executor_code_object_cache_by_plan_signature=(
                override_executor_code_object_cache_by_plan_signature
            ),
            override_prefilter_step_targets_cache=(
                override_prefilter_step_targets_cache
            ),
            override_prefilter_path_metadata_cache=(
                override_prefilter_path_metadata_cache
            ),
            prefilter_cache_key=prefilter_cache_key,
        )
        override_specialization_cache[shape_key] = executor
        return executor

    def _compile_override_executor_from_plan_rows(
            self,
            *,
            shape_key: Tuple[Any, ...],
            override_targets_by_spell_id: Dict[str, Tuple[Any, ...]],
            any_overrides_present: bool,
            path_registry: Optional[Any],
            plan_rows: Sequence[Dict[str, Any]],
            root_spell_id: Optional[str],
            spell_lookup: Dict[str, Any],
            override_executor_source_cache_by_plan_signature: Dict[
                Tuple[Any, ...],
                str,
            ],
            override_executor_code_object_cache_by_plan_signature: Dict[
                Tuple[Any, ...],
                Any,
            ],
            override_prefilter_step_targets_cache: Dict[
                Tuple[Any, ...],
                Tuple[Tuple[Any, ...], ...],
            ],
            override_prefilter_path_metadata_cache: Dict[Any, Tuple[Any, Any]],
            prefilter_cache_key: Optional[Tuple[Any, ...]],
    ) -> Callable[..., Any]:
        """
        Compile one override specialization from static plan rows.
        """
        targeted_spell_ids = tuple(sorted(override_targets_by_spell_id.keys()))
        override_target_counts_by_spell_id = tuple(
            sorted(
                (
                    spell_id,
                    len(targets),
                )
                for spell_id, targets in override_targets_by_spell_id.items()
                if targets
            )
        )
        override_target_counts_by_step = (
            build_overrides_codegen_creation_step_target_counts_from_rows(
                plan_rows=plan_rows,
                override_targets_by_spell_id=override_targets_by_spell_id,
                path_registry=path_registry,
                prefilter_step_targets_cache=(
                    override_prefilter_step_targets_cache
                ),
                prefilter_cache_key=prefilter_cache_key,
                prefilter_path_metadata_cache=(
                    override_prefilter_path_metadata_cache
                ),
            )
        )
        has_root_positional_override = shape_key[2] >= 0
        source = self._get_or_build_override_executor_source(
            source_cache_key=shape_key,
            plan_rows=plan_rows,
            root_spell_id=root_spell_id,
            spell_lookup=spell_lookup,
            override_targeted_spell_ids=targeted_spell_ids,
            override_target_counts_by_spell_id=override_target_counts_by_spell_id,
            override_target_counts_by_step=override_target_counts_by_step,
            has_root_positional_override=has_root_positional_override,
            override_executor_source_cache_by_plan_signature=(
                override_executor_source_cache_by_plan_signature
            ),
        )
        code_object = self._get_or_build_override_executor_code_object(
            source_cache_key=shape_key,
            source=source,
            override_executor_code_object_cache_by_plan_signature=(
                override_executor_code_object_cache_by_plan_signature
            ),
        )
        return _compile_overrides_codegen_creation_executor_from_code_object_with_prefilter_cache(
            code_object=code_object,
            execution_plan=None,
            override_targets_by_spell_id=override_targets_by_spell_id,
            any_overrides_present=any_overrides_present,
            path_registry=path_registry,
            plan_rows=plan_rows,
            root_spell_id=root_spell_id,
            spell_lookup=spell_lookup,
            prefilter_step_targets_cache=override_prefilter_step_targets_cache,
            prefilter_cache_key=prefilter_cache_key,
            prefilter_path_metadata_cache=override_prefilter_path_metadata_cache,
        )

    @staticmethod
    def _get_or_build_override_executor_code_object(
            *,
            source_cache_key: Tuple[Any, ...],
            source: str,
            override_executor_code_object_cache_by_plan_signature: Dict[
                Tuple[Any, ...],
                Any,
            ],
    ) -> Any:
        """
        Return the compiled override code object for one specialization shape.
        """
        code_object = override_executor_code_object_cache_by_plan_signature.get(
            source_cache_key
        )
        if code_object is not None:
            return code_object
        code_object = compile_overrides_codegen_creation_executor_code_object(
            source=source,
        )
        override_executor_code_object_cache_by_plan_signature[
            source_cache_key
        ] = code_object
        return code_object

    @staticmethod
    def _get_or_build_override_executor_source(
            *,
            source_cache_key: Tuple[Any, ...],
            plan_rows: Sequence[Dict[str, Any]],
            root_spell_id: Optional[str],
            spell_lookup: Dict[str, Any],
            override_targeted_spell_ids: Tuple[str, ...],
            override_target_counts_by_spell_id: Tuple[Tuple[str, int], ...],
            override_target_counts_by_step: Tuple[int, ...],
            has_root_positional_override: bool,
            override_executor_source_cache_by_plan_signature: Dict[
                Tuple[Any, ...],
                str,
            ],
    ) -> str:
        """
        Return emitted override source for one specialization shape.
        """
        source = override_executor_source_cache_by_plan_signature.get(
            source_cache_key
        )
        if source is not None:
            return source
        source = emit_overrides_codegen_creation_executor_shape_source(
            plan_rows=plan_rows,
            root_spell_id=root_spell_id,
            spell_lookup=spell_lookup,
            override_targeted_spell_ids=override_targeted_spell_ids,
            override_target_counts_by_spell_id=override_target_counts_by_spell_id,
            override_target_counts_by_step=override_target_counts_by_step,
            has_root_positional_override=has_root_positional_override,
        )
        override_executor_source_cache_by_plan_signature[
            source_cache_key
        ] = source
        return source
