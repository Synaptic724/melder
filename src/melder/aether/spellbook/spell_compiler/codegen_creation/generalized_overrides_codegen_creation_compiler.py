from collections import Counter
from types import SimpleNamespace
from typing import Any, Callable, Dict, Optional, Sequence, Tuple

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.blueprints.execution_plan import (
    ExecutionPlanTargetKind,
)
from melder.aether.spellbook.spell_compiler.codegen_creation.generalized_no_overrides_codegen_creation_compiler import (
    _get_existing_creation,
    _register_spell_instance_prebound,
)
from melder.aether.spellbook.spell_compiler.executor_code_cache import (
    get_or_compile_executor_code,
)
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError

_MISSING = object()
_EMPTY_OVERRIDE_VALUES: Dict[str, Any] = {}


def compile_phase13_overrides_executor(
        *,
        execution_plan: Optional[Any],
        override_targets_by_spell_id: Dict[str, Tuple[Any, ...]],
        any_overrides_present: bool,
        path_registry: Optional[Any],
        plan_rows: Optional[Sequence[Dict[str, Any]]] = None,
        root_spell_id: Optional[str] = None,
        spell_lookup: Optional[Dict[str, Any]] = None,
) -> Callable[..., Any]:
    """
    Compile a spell-scoped Phase 13 overrides executor specialization.

    Purpose:
        Build the runtime callable used for override-aware meld execution after
        Phase 11 planning, without relying on legacy engine execution paths.

    Contract:
        - Executes Phase 11 steps in plan order.
        - Reuses and registers instances using the same Existence contracts as
          the no-overrides path.
        - Raises when overrides target an already-existing non-`many` instance.
        - Supports root positional override payloads through the special
          ``"__args__"`` keyword in root-step call kwargs.

    Args:
        execution_plan:
            Phase 11 override-aware execution plan.
        override_targets_by_spell_id:
            Deterministic map of spell_id -> socket refs targeted by the current
            override shape.
        any_overrides_present:
            True when this specialization represents a call with overrides.
        path_registry:
            Path registry from the active root blueprint, used to pre-filter
            non-shared step socket targets at specialization compile time.
        plan_rows:
            Optional schema-only step rows exported from Phase11 IR.
        root_spell_id:
            Optional root spell id for schema-row driven compilation.
        spell_lookup:
            Optional spell-id lookup used when hydrating schema rows.

    Returns:
        Callable[..., Any]:
            Executor receiving creations inputs plus
            `(override_map, root_positional_override)`.

    Raises:
        ValueError:
            If required inputs are missing.
        RuntimeError:
            If the execution plan has no root instance key.
    """
    compiled_executor, _ = _compile_phase13_overrides_executor_core(
        source=None,
        code_object=None,
        execution_plan=execution_plan,
        override_targets_by_spell_id=override_targets_by_spell_id,
        any_overrides_present=any_overrides_present,
        path_registry=path_registry,
        plan_rows=plan_rows,
        root_spell_id=root_spell_id,
        spell_lookup=spell_lookup,
    )
    return compiled_executor


def compile_phase13_overrides_executor_from_source(
        *,
        source: str,
        execution_plan: Optional[Any],
        override_targets_by_spell_id: Dict[str, Tuple[Any, ...]],
        any_overrides_present: bool,
        path_registry: Optional[Any],
        plan_rows: Optional[Sequence[Dict[str, Any]]] = None,
        root_spell_id: Optional[str] = None,
        spell_lookup: Optional[Dict[str, Any]] = None,
) -> Callable[..., Any]:
    """
    Compile a specialization executor from previously emitted source.

    Contract:
        - Reuses the same schema/plan validation as fresh compilation.
        - Uses the supplied source verbatim for code object compilation.
    """
    compiled_executor, _ = _compile_phase13_overrides_executor_core(
        source=source,
        code_object=None,
        execution_plan=execution_plan,
        override_targets_by_spell_id=override_targets_by_spell_id,
        any_overrides_present=any_overrides_present,
        path_registry=path_registry,
        plan_rows=plan_rows,
        root_spell_id=root_spell_id,
        spell_lookup=spell_lookup,
    )
    return compiled_executor


def compile_phase13_overrides_executor_code_object(
        *,
        source: str,
) -> Any:
    """
    Compile emitted override specialization source into a reusable code object.

    Contract:
        - Source must be a non-empty string.
        - Returned code object is safe to execute against different namespaces.
        - Uses the same synthetic filename as direct override compilation.
        - Resolves the code object through the process-wide executor code
          cache, so identity-free override source compiled before (this
          conjure/meld, an earlier one, or another Spellbook) is reused.
    """
    if not isinstance(source, str) or not source:
        raise ValueError("source must be a non-empty string.")
    try:
        return get_or_compile_executor_code(
            source=source,
            source_name="<melder_phase13_overrides_executor>",
        )
    except Exception as exc:
        raise RuntimeError(
            "Phase 13 overrides executor code generation failed."
        ) from exc


def compile_phase13_overrides_executor_from_code_object(
        *,
        code_object: Any,
        execution_plan: Optional[Any],
        override_targets_by_spell_id: Dict[str, Tuple[Any, ...]],
        any_overrides_present: bool,
        path_registry: Optional[Any],
        plan_rows: Optional[Sequence[Dict[str, Any]]] = None,
        root_spell_id: Optional[str] = None,
        spell_lookup: Optional[Dict[str, Any]] = None,
) -> Callable[..., Any]:
    """
    Compile a specialization executor from a previously compiled code object.

    Contract:
        - Reuses schema/plan validation and namespace binding from core compile flow.
        - Executes `code_object` verbatim for specialization binding.
    """
    return _compile_phase13_overrides_executor_from_code_object_with_prefilter_cache(
        code_object=code_object,
        execution_plan=execution_plan,
        override_targets_by_spell_id=override_targets_by_spell_id,
        any_overrides_present=any_overrides_present,
        path_registry=path_registry,
        plan_rows=plan_rows,
        root_spell_id=root_spell_id,
        spell_lookup=spell_lookup,
    )


def _compile_phase13_overrides_executor_from_code_object_with_prefilter_cache(
        *,
        code_object: Any,
        execution_plan: Optional[Any],
        override_targets_by_spell_id: Dict[str, Tuple[Any, ...]],
        any_overrides_present: bool,
        path_registry: Optional[Any],
        plan_rows: Optional[Sequence[Dict[str, Any]]] = None,
        root_spell_id: Optional[str] = None,
        spell_lookup: Optional[Dict[str, Any]] = None,
        prefilter_step_targets_cache: Optional[Dict[Tuple[Any, ...], Tuple[Tuple[Any, ...], ...]]] = None,
        prefilter_cache_key: Optional[Tuple[Any, ...]] = None,
        prefilter_path_metadata_cache: Optional[Dict[Any, Tuple[Any, Any]]] = None,
) -> Callable[..., Any]:
    """
    Internal code-object compile path with optional prefilter cache injection.

    Contract:
        - Reuses schema/plan validation and namespace binding from core compile flow.
        - Executes `code_object` verbatim for specialization binding.
        - Optional prefilter caches allow step-target reuse across compiles.
    """
    if code_object is None:
        raise ValueError("code_object must not be None.")
    compiled_executor, _ = _compile_phase13_overrides_executor_core(
        source=None,
        code_object=code_object,
        execution_plan=execution_plan,
        override_targets_by_spell_id=override_targets_by_spell_id,
        any_overrides_present=any_overrides_present,
        path_registry=path_registry,
        plan_rows=plan_rows,
        root_spell_id=root_spell_id,
        spell_lookup=spell_lookup,
        prefilter_step_targets_cache=prefilter_step_targets_cache,
        prefilter_cache_key=prefilter_cache_key,
        prefilter_path_metadata_cache=prefilter_path_metadata_cache,
    )
    return compiled_executor


def emit_phase13_overrides_executor_source(
        *,
        step_count: int,
) -> str:
    """
    Emit generated Phase12 override specialization source for a step count.

    Contract:
        - Source is deterministic for the same `step_count`.
        - Raises when step_count is invalid.
    """
    return _build_phase13_overrides_executor_source(
        step_count=step_count,
    )


def emit_phase13_overrides_executor_shape_source(
        *,
        plan_rows: Sequence[Dict[str, Any]],
        root_spell_id: Optional[str],
        spell_lookup: Optional[Dict[str, Any]] = None,
        override_targeted_spell_ids: Optional[Tuple[str, ...]] = None,
        override_target_counts_by_spell_id: Optional[Tuple[Tuple[str, int], ...]] = None,
        override_target_counts_by_step: Optional[Tuple[int, ...]] = None,
        has_root_positional_override: bool = False,
) -> str:
    """
    Emit shape-specialized Phase12 override source from static plan rows.

    Purpose:
        Build generated source that specializes per-step target-kind and
        existence branch selection to reduce runtime branch depth in hot
        override lanes.

    Contract:
        - Source is deterministic for the same plan-row shape metadata.
        - Validates required row fields and existence enum names.
        - Preserves emitted executor contracts used by core override compilation.
    """
    step_source_metadata = _build_shape_source_step_metadata(
        plan_rows=plan_rows,
        root_spell_id=root_spell_id,
        spell_lookup=spell_lookup,
        override_targeted_spell_ids=override_targeted_spell_ids,
        override_target_counts_by_spell_id=override_target_counts_by_spell_id,
        override_target_counts_by_step=override_target_counts_by_step,
        has_root_positional_override=has_root_positional_override,
    )
    return _build_phase13_overrides_executor_shape_source(
        step_source_metadata=step_source_metadata,
    )


def build_phase13_override_step_target_counts_from_rows(
        *,
        plan_rows: Sequence[Dict[str, Any]],
        override_targets_by_spell_id: Dict[str, Tuple[Any, ...]],
        path_registry: Optional[Any],
        prefilter_step_targets_cache: Optional[Dict[Tuple[Any, ...], Tuple[Tuple[Any, ...], ...]]] = None,
        prefilter_cache_key: Optional[Tuple[Any, ...]] = None,
        prefilter_path_metadata_cache: Optional[Dict[Any, Tuple[Any, Any]]] = None,
) -> Tuple[int, ...]:
    """
    Build deterministic per-step override target counts from schema rows.

    Purpose:
        Expose compile-time step target counts so shape-source emission can
        specialize by exact per-step count (0/1/2/many) safely, including
        graphs where one spell_id appears in multiple plan steps.

    Contract:
        - Uses the same prefilter logic as override executor compile flow.
        - Requires only schema row fields used by step target filtering.
        - Returns one count per input row in row order.
    """
    if plan_rows is None:
        raise ValueError("plan_rows must not be None.")
    if override_targets_by_spell_id is None:
        raise ValueError("override_targets_by_spell_id must not be None.")

    step_stubs = []
    required_fields = (
        "spell_id",
        "shared_instance",
        "override_match_prefix",
        "override_match_prefix_len",
    )
    for row_index, row in enumerate(plan_rows):
        for field_name in required_fields:
            if field_name not in row:
                raise RuntimeError(
                    "Phase 13 overrides step schema is missing required field "
                    f"'{field_name}' at index {row_index}."
                )
        step_stubs.append(
            SimpleNamespace(
                spell=SimpleNamespace(
                    spell_index=SimpleNamespace(
                        current=row["spell_id"],
                    ),
                ),
                shared_instance=bool(row["shared_instance"]),
                override_match_prefix=row["override_match_prefix"],
                override_match_prefix_len=row["override_match_prefix_len"],
            )
        )

    step_targets = _build_step_override_targets(
        steps=tuple(step_stubs),
        override_targets_by_spell_id=override_targets_by_spell_id,
        path_registry=path_registry,
        prefilter_step_targets_cache=prefilter_step_targets_cache,
        prefilter_cache_key=prefilter_cache_key,
        prefilter_path_metadata_cache=prefilter_path_metadata_cache,
    )
    return tuple(
        len(step_target_matches)
        for step_target_matches in step_targets
    )


def _compile_phase13_overrides_executor_core(
        *,
        source: Optional[str],
        code_object: Optional[Any],
        execution_plan: Optional[Any],
        override_targets_by_spell_id: Dict[str, Tuple[Any, ...]],
        any_overrides_present: bool,
        path_registry: Optional[Any],
        plan_rows: Optional[Sequence[Dict[str, Any]]],
        root_spell_id: Optional[str],
        spell_lookup: Optional[Dict[str, Any]],
        prefilter_step_targets_cache: Optional[Dict[Tuple[Any, ...], Tuple[Tuple[Any, ...], ...]]] = None,
        prefilter_cache_key: Optional[Tuple[Any, ...]] = None,
        prefilter_path_metadata_cache: Optional[Dict[Any, Tuple[Any, Any]]] = None,
) -> Tuple[Callable[..., Any], Optional[str]]:
    """
    Shared compile flow for fresh and source-restored override executors.

    Contract:
        - Validates plan/schema inputs before compiling generated source.
        - Returns both the compiled callable and source used for compilation.
    """
    if execution_plan is None and not plan_rows:
        raise ValueError("execution_plan must not be None.")
    if override_targets_by_spell_id is None:
        raise ValueError("override_targets_by_spell_id must not be None.")

    if plan_rows:
        steps = _hydrate_steps_from_rows(
            plan_rows=plan_rows,
            spell_lookup=spell_lookup,
        )
        resolved_root_spell_id = root_spell_id
        if resolved_root_spell_id is None and execution_plan is not None:
            resolved_root_spell_id = execution_plan.root_spell_id
        root_instance_key = _resolve_root_instance_key(
            steps=steps,
            root_spell_id=resolved_root_spell_id,
        )
        if root_instance_key is None:
            raise RuntimeError("Phase 13 override executor requires a root instance key.")
        root_spell_id = resolved_root_spell_id
    else:
        resolved_execution_plan = execution_plan
        if resolved_execution_plan is None:
            raise ValueError(
                "execution_plan must not be None when plan_rows are absent."
            )
        root_instance_key = resolved_execution_plan.root_instance_key
        if root_instance_key is None:
            raise RuntimeError("Phase 13 override executor requires a root instance key.")
        steps = tuple(resolved_execution_plan.steps)
        root_spell_id = resolved_execution_plan.root_spell_id

    step_override_targets = _build_step_override_targets(
        steps=steps,
        override_targets_by_spell_id=override_targets_by_spell_id,
        path_registry=path_registry,
        prefilter_step_targets_cache=prefilter_step_targets_cache,
        prefilter_cache_key=prefilter_cache_key,
        prefilter_path_metadata_cache=prefilter_path_metadata_cache,
    )

    source_to_compile = source
    if source_to_compile is not None and (
            not isinstance(source_to_compile, str) or not source_to_compile
    ):
        raise ValueError("source must be a non-empty string.")
    if source_to_compile is None and code_object is None:
        source_to_compile = emit_phase13_overrides_executor_source(
            step_count=len(steps),
        )
    if code_object is None:
        if source_to_compile is None:
            raise RuntimeError(
                "Phase 13 override executor requires source text when no code object is supplied."
            )
        code_object = compile_phase13_overrides_executor_code_object(
            source=source_to_compile,
        )

    namespace = _build_phase13_overrides_executor_namespace(
        steps=steps,
        step_override_targets=step_override_targets,
        root_instance_key=root_instance_key,
        root_spell_id=root_spell_id,
        any_overrides_present=any_overrides_present,
    )
    local_namespace: Dict[str, Any] = {}
    try:
        exec(
            code_object,
            namespace,
            local_namespace,
        )
    except Exception as exc:
        raise RuntimeError(
            "Phase 13 overrides executor code generation failed."
        ) from exc

    compiled_executor = local_namespace.get("_phase13_executor")
    if callable(compiled_executor):
        return compiled_executor, source_to_compile
    raise RuntimeError(
        "Phase 13 overrides executor source did not define a callable _phase13_executor."
    )


def _build_phase13_overrides_executor_namespace(
        *,
        steps: Tuple[Any, ...],
        step_override_targets: Tuple[Tuple[Any, ...], ...],
        root_instance_key: Tuple[str, Optional[int]],
        root_spell_id: Optional[str],
        any_overrides_present: bool,
) -> Dict[str, Any]:
    """
    Build namespace values for generated override specialization source.

    Contract:
        - Captures immutable specialization constants as function defaults.
        - Exposes helper callables required by generated executor source.
        - Prebinds per-step registration flags to avoid hot-path attribute reads.
    """
    return {
        "MeldExecutionError": MeldExecutionError,
        "Sequence": Sequence,
        "Existence": Existence,
        "ExecutionPlanTargetKind": ExecutionPlanTargetKind,
        "_MISSING": _MISSING,
        "_construct_spell_instance_with_overrides": _construct_spell_instance_with_overrides,
        "_build_step_override_values": _build_step_override_values,
        "_build_kwargs_with_overrides": _build_kwargs_with_overrides,
        "_invoke_spell_with_kwargs": _invoke_spell_with_kwargs,
        "_EMPTY_OVERRIDE_VALUES": _EMPTY_OVERRIDE_VALUES,
        "_get_existing_creation": _get_existing_creation,
        "_register_spell_instance_prebound": _register_spell_instance_prebound,
        "_raise_override_on_existing_instance": _raise_override_on_existing_instance,
        "step_spells": tuple(
            plan_step.spell
            for plan_step in steps
        ),
        "step_spell_ids": tuple(
            plan_step.spell.spell_id
            for plan_step in steps
        ),
        "step_has_disposal_methods": tuple(
            plan_step.spell.has_disposal_methods
            for plan_step in steps
        ),
        "step_disposal_methods": tuple(
            plan_step.spell.disposal_method_names
            for plan_step in steps
        ),
        "step_existences": tuple(
            plan_step.existence
            for plan_step in steps
        ),
        "step_creations_target_kinds": tuple(
            plan_step.creations_target_kind
            for plan_step in steps
        ),
        "step_is_root": tuple(
            plan_step.spell.spell_index.current == root_spell_id
            for plan_step in steps
        ),
        "step_has_targeted_overrides": tuple(
            bool(override_targets)
            for override_targets in step_override_targets
        ),
        "step_override_target_counts": tuple(
            len(override_targets)
            for override_targets in step_override_targets
        ),
        "step_is_existing_unique_creation": tuple(
            (
                    plan_step.spell.existence is Existence.unique
                    and plan_step.spell.is_existing_creation
            )
            for plan_step in steps
        ),
        "step_is_callable_spell": tuple(
            (
                    plan_step.spell.is_class_spell
                    or plan_step.spell.is_method_spell
                    or plan_step.spell.is_lambda_spell
            )
            for plan_step in steps
        ),
        "step_instance_keys": tuple(
            plan_step.instance_key
            for plan_step in steps
        ),
        "step_use_spell_lock_hints": tuple(
            plan_step.use_spell_lock_hint
            for plan_step in steps
        ),
        "step_must_register_flags": tuple(
            plan_step.must_register
            for plan_step in steps
        ),
        "steps": steps,
        "step_override_targets": step_override_targets,
        "root_instance_key": root_instance_key,
        "root_spell_id": root_spell_id,
        "any_overrides_present": any_overrides_present,
    }


def _build_phase13_overrides_executor_source(
        *,
        step_count: int,
) -> str:
    """
    Build generated Python source for override specialization execution.

    Contract:
        - Emits one direct step-resolution block per Phase11 step.
        - Inlines override-aware existence/lock/reuse/register semantics.
        - Uses prebound defaults for specialization constants.
        - Preserves root-result verification semantics.
    """
    if step_count < 0:
        raise ValueError("step_count must not be negative.")

    lines = [
        "def _phase13_executor(",
        "        caller_creations,",
        "        override_map,",
        "        root_positional_override,",
        "        *,",
        "        owner_creations=None,",
        "        caller_creations_lock_held=False,",
        "        steps=steps,",
        "        step_spells=step_spells,",
        "        step_spell_ids=step_spell_ids,",
        "        step_has_disposal_methods=step_has_disposal_methods,",
        "        step_disposal_methods=step_disposal_methods,",
        "        step_override_targets=step_override_targets,",
        "        step_existences=step_existences,",
        "        step_creations_target_kinds=step_creations_target_kinds,",
        "        step_is_root=step_is_root,",
        "        step_has_targeted_overrides=step_has_targeted_overrides,",
        "        step_instance_keys=step_instance_keys,",
        "        step_use_spell_lock_hints=step_use_spell_lock_hints,",
        "        step_must_register_flags=step_must_register_flags,",
        "        root_instance_key=root_instance_key,",
        "        root_spell_id=root_spell_id,",
        "        any_overrides_present=any_overrides_present,",
        "        Existence=Existence,",
        "        ExecutionPlanTargetKind=ExecutionPlanTargetKind,",
        "        _construct_spell_instance_with_overrides=_construct_spell_instance_with_overrides,",
        "        _get_existing_creation=_get_existing_creation,",
        "        _register_spell_instance_prebound=_register_spell_instance_prebound,",
        "        _raise_override_on_existing_instance=_raise_override_on_existing_instance,",
        "        MeldExecutionError=MeldExecutionError,",
        "    ):",
        "    instance_results = {}",
    ]

    for index in range(step_count):
        _append_overrides_step_source(
            lines=lines,
            step_index=index,
        )

    lines.extend([
        "    if root_instance_key not in instance_results:",
        "        raise MeldExecutionError(",
        "            spell_id=root_instance_key[0],",
        "            spell_name=root_instance_key[0],",
        "            message=(",
        "                \"Phase 13 override executor did not produce the root \"",
        "                f\"instance '{root_instance_key[0]}'.\"",
        "            ),",
        "        )",
        "    return instance_results[root_instance_key]",
    ])
    return "\n".join(lines)


def _build_shape_source_step_metadata(
        *,
        plan_rows: Sequence[Dict[str, Any]],
        root_spell_id: Optional[str],
        spell_lookup: Optional[Dict[str, Any]],
        override_targeted_spell_ids: Optional[Tuple[str, ...]],
        override_target_counts_by_spell_id: Optional[Tuple[Tuple[str, int], ...]],
        override_target_counts_by_step: Optional[Tuple[int, ...]],
        has_root_positional_override: bool,
) -> Tuple[Tuple[Any, ...], ...]:
    """
    Build immutable per-step metadata used by shape-specialized source emission.

    Contract:
        - Validates required row fields needed by shape-specialized emission.
        - Resolves row existence names to Existence enum values.
        - Marks root-step membership using `root_spell_id`.
    """
    if plan_rows is None:
        raise ValueError("plan_rows must not be None.")
    targeted_spell_ids = set(override_targeted_spell_ids or ())
    target_counts_by_spell_id = dict(override_target_counts_by_spell_id or ())
    step_spell_ids = [
        row["spell_id"]
        for row in plan_rows
        if "spell_id" in row
    ]
    step_counts_by_spell_id = Counter(step_spell_ids)
    has_step_target_counts = (
            override_target_counts_by_step is not None
            and len(override_target_counts_by_step) == len(plan_rows)
    )
    step_metadata = []
    required_fields = (
        "spell_id",
        "existence",
        "creations_target_kind",
        "uses_positional_override",
        "dependency_resolution_order",
        "contract_positional_override",
        "has_contract_payload",
        "contract_payload_items",
        "use_spell_lock_hint",
        "must_register",
    )
    for row_index, row in enumerate(plan_rows):
        for field_name in required_fields:
            if field_name not in row:
                raise RuntimeError(
                    "Phase 13 overrides step schema is missing required field "
                    f"'{field_name}' at index {row_index}."
                )
        spell_id = row["spell_id"]
        existence_name = row["existence"]
        try:
            existence = Existence[existence_name]
        except KeyError as exc:
            raise RuntimeError(
                "Phase 13 overrides step schema contains unknown existence "
                f"'{existence_name}' at index {row_index}."
            ) from exc
        dependency_resolution_order = tuple(
            (
                param_name,
                tuple(dependency_keys),
            )
            for param_name, dependency_keys in row["dependency_resolution_order"]
        )
        has_contract_payload = bool(row["has_contract_payload"])
        contract_payload_items: Tuple[Tuple[str, Any], ...] = ()
        if has_contract_payload:
            contract_payload_items = tuple(
                (param_name, value)
                for param_name, value in row["contract_payload_items"]
            )
        if has_step_target_counts:
            step_target_counts = override_target_counts_by_step
            if step_target_counts is None:
                raise RuntimeError(
                    "Phase 13 overrides step schema requires step target counts."
                )
            static_override_target_count = int(
                step_target_counts[row_index]
            )
        else:
            static_override_target_count = (
                int(target_counts_by_spell_id.get(spell_id, 0))
                if step_counts_by_spell_id.get(spell_id, 0) == 1
                else -1
            )
        static_is_existing_unique_creation: Optional[bool] = None
        static_is_callable_spell: Optional[bool] = None
        static_has_disposal_methods: Optional[bool] = None
        if spell_lookup is not None:
            spell = spell_lookup.get(spell_id)
            if spell is not None:
                try:
                    spell_existence = spell.existence
                    spell_is_existing_creation = spell.is_existing_creation
                    spell_is_class_spell = spell.is_class_spell
                    spell_is_method_spell = spell.is_method_spell
                    spell_is_lambda_spell = spell.is_lambda_spell
                    spell_has_disposal_methods = spell.has_disposal_methods
                except AttributeError:
                    spell = None
                if spell is not None:
                    static_is_existing_unique_creation = (
                        spell_existence is Existence.unique
                        and bool(spell_is_existing_creation)
                    )
                    static_is_callable_spell = (
                        bool(spell_is_class_spell)
                        or bool(spell_is_method_spell)
                        or bool(spell_is_lambda_spell)
                    )
                    static_has_disposal_methods = bool(spell_has_disposal_methods)
        if static_is_existing_unique_creation is None and "is_existing_unique_creation" in row:
            static_is_existing_unique_creation = bool(
                row["is_existing_unique_creation"]
            )
        if static_is_callable_spell is None and "is_callable_spell" in row:
            static_is_callable_spell = bool(row["is_callable_spell"])
        if (
                static_has_disposal_methods is None
                and "has_disposal_methods" in row
        ):
            static_has_disposal_methods = bool(row["has_disposal_methods"])
        step_metadata.append(
            (
                spell_id,
                row["creations_target_kind"],
                existence,
                bool(row["use_spell_lock_hint"]),
                bool(row["must_register"]),
                spell_id == root_spell_id,
                spell_id in targeted_spell_ids,
                static_override_target_count,
                bool(row["uses_positional_override"]),
                spell_id == root_spell_id and has_root_positional_override,
                dependency_resolution_order,
                row["contract_positional_override"],
                has_contract_payload,
                contract_payload_items,
                static_is_existing_unique_creation,
                static_is_callable_spell,
                static_has_disposal_methods,
            )
        )
    return tuple(step_metadata)


def _build_phase13_overrides_executor_shape_source(
        *,
        step_source_metadata: Sequence[Tuple[Any, ...]],
) -> str:
    """
    Build generated override source specialized by static step metadata.

    Contract:
        - Emits one direct step-resolution block per metadata row.
        - Removes per-step runtime target-kind/existence branch selection.
        - Preserves root-result verification semantics.
    """
    if step_source_metadata is None:
        raise ValueError("step_source_metadata must not be None.")

    lines = [
        "def _phase13_executor(",
        "        caller_creations,",
        "        override_map,",
        "        root_positional_override,",
        "        *,",
        "        owner_creations=None,",
        "        caller_creations_lock_held=False,",
        "        steps=steps,",
        "        step_spells=step_spells,",
        "        step_spell_ids=step_spell_ids,",
        "        step_has_disposal_methods=step_has_disposal_methods,",
        "        step_disposal_methods=step_disposal_methods,",
        "        step_override_targets=step_override_targets,",
        "        step_has_targeted_overrides=step_has_targeted_overrides,",
        "        step_override_target_counts=step_override_target_counts,",
        "        step_is_existing_unique_creation=step_is_existing_unique_creation,",
        "        step_is_callable_spell=step_is_callable_spell,",
        "        step_instance_keys=step_instance_keys,",
        "        root_instance_key=root_instance_key,",
        "        root_spell_id=root_spell_id,",
        "        any_overrides_present=any_overrides_present,",
        "        _EMPTY_OVERRIDE_VALUES=_EMPTY_OVERRIDE_VALUES,",
        "        _MISSING=_MISSING,",
        "        _get_existing_creation=_get_existing_creation,",
        "        _register_spell_instance_prebound=_register_spell_instance_prebound,",
        "        _raise_override_on_existing_instance=_raise_override_on_existing_instance,",
        "        Sequence=Sequence,",
        "        MeldExecutionError=MeldExecutionError,",
        "    ):",
        "    instance_results = {}",
    ]
    if any(
            metadata[1] in (
                ExecutionPlanTargetKind.CALLER,
                ExecutionPlanTargetKind.SPELLSPACE,
            )
            for metadata in step_source_metadata
    ):
        lines.extend([
            "    if caller_creations is None:",
            "        raise RuntimeError(",
            "            \"Phase 13 CALLER/SPELLSPACE execution requires caller_creations.\"",
            "        )",
        ])

    for step_index, metadata in enumerate(step_source_metadata):
        (
            spell_id,
            creations_target_kind,
            existence,
            use_spell_lock_hint,
            must_register,
            is_root_step,
            has_static_targeted_overrides,
            static_override_target_count,
            use_positional_override,
            has_static_root_positional_override,
            dependency_resolution_order,
            contract_positional_override,
            has_contract_payload,
            contract_payload_items,
            static_is_existing_unique_creation,
            static_is_callable_spell,
            static_has_disposal_methods,
        ) = metadata
        _append_overrides_step_shape_source(
            lines=lines,
            step_index=step_index,
            spell_id=spell_id,
            creations_target_kind=creations_target_kind,
            existence=existence,
            use_spell_lock_hint=use_spell_lock_hint,
            must_register=must_register,
            is_root_step=is_root_step,
            has_static_targeted_overrides=has_static_targeted_overrides,
            static_override_target_count=static_override_target_count,
            use_positional_override=use_positional_override,
            has_static_root_positional_override=has_static_root_positional_override,
            dependency_resolution_order=dependency_resolution_order,
            contract_positional_override=contract_positional_override,
            has_contract_payload=has_contract_payload,
            contract_payload_items=contract_payload_items,
            static_is_existing_unique_creation=static_is_existing_unique_creation,
            static_is_callable_spell=static_is_callable_spell,
            static_has_disposal_methods=static_has_disposal_methods,
        )

    lines.extend([
        "    if root_instance_key not in instance_results:",
        "        raise MeldExecutionError(",
        "            spell_id=root_instance_key[0],",
        "            spell_name=root_instance_key[0],",
        "            message=(",
        "                \"Phase 13 override executor did not produce the root \"",
        "                f\"instance '{root_instance_key[0]}'.\"",
        "            ),",
        "        )",
        "    return instance_results[root_instance_key]",
    ])
    return "\n".join(lines)


def _append_overrides_construct_inline_source(
        *,
        lines: list[str],
        step_index: int,
        indent: str,
        static_override_target_count: int,
        positional_args_possible: bool,
        dependency_resolution_order: Tuple[Tuple[str, Tuple[Tuple[str, Optional[int]], ...]], ...],
        contract_positional_override: Optional[Sequence[Any]],
        has_contract_payload: bool,
        contract_payload_items: Tuple[Tuple[str, Any], ...],
        uses_positional_override: bool,
        static_is_existing_unique_creation: Optional[bool] = None,
        static_is_callable_spell: Optional[bool] = None,
) -> None:
    """
    Append generated source lines to construct one override-aware step instance.

    Contract:
        - Inlines override-value construction and kwargs materialization in the
          generated executor to avoid helper trampoline overhead.
        - Preserves existing helper semantics for single/two/many target
          override-map construction.
        - Preserves override precedence over dependency/contract payload values.
        - Emits static dependency and contract assembly blocks from Phase11 row
          metadata to avoid `_build_kwargs_with_overrides(...)` dispatch.
    """
    if static_override_target_count == 0:
        if positional_args_possible:
            lines.extend([
                f"{indent}if step_root_positional_override_{step_index} is None:",
                f"{indent}    override_values_{step_index} = _EMPTY_OVERRIDE_VALUES",
                f"{indent}else:",
                f"{indent}    override_values_{step_index} = {{",
                (
                    f"{indent}        \"__args__\": "
                    f"step_root_positional_override_{step_index},"
                ),
                f"{indent}    }}",
            ])
        else:
            lines.append(
                f"{indent}override_values_{step_index} = _EMPTY_OVERRIDE_VALUES"
            )
    elif static_override_target_count == 1:
        lines.extend([
            f"{indent}single_override_socket_{step_index} = override_targets_{step_index}[0]",
            (
                f"{indent}single_override_value_{step_index} = "
                f"override_map[single_override_socket_{step_index}]"
            ),
        ])
    elif static_override_target_count == 2:
        lines.extend([
            (
                f"{indent}first_override_socket_{step_index} = "
                f"override_targets_{step_index}[0]"
            ),
            (
                f"{indent}second_override_socket_{step_index} = "
                f"override_targets_{step_index}[1]"
            ),
            (
                f"{indent}first_override_value_{step_index} = "
                f"override_map[first_override_socket_{step_index}]"
            ),
            (
                f"{indent}second_override_value_{step_index} = "
                f"override_map[second_override_socket_{step_index}]"
            ),
        ])
    else:
        lines.extend([
            f"{indent}override_values_{step_index} = {{}}",
            (
                f"{indent}for override_socket_{step_index} in "
                f"override_targets_{step_index}:"
            ),
            (
                f"{indent}    override_values_{step_index}["
                f"override_socket_{step_index}.param_name] = "
                f"override_map[override_socket_{step_index}]"
            ),
        ])
        if positional_args_possible:
            lines.extend([
                f"{indent}if step_root_positional_override_{step_index} is not None:",
                (
                    f"{indent}    override_values_{step_index}[\"__args__\"] = "
                    f"step_root_positional_override_{step_index}"
                ),
            ])
    _append_overrides_kwargs_inline_source(
        lines=lines,
        step_index=step_index,
        indent=indent,
        static_override_target_count=static_override_target_count,
        positional_args_possible=positional_args_possible,
        dependency_resolution_order=dependency_resolution_order,
        contract_positional_override=contract_positional_override,
        has_contract_payload=has_contract_payload,
        contract_payload_items=contract_payload_items,
        uses_positional_override=uses_positional_override,
    )
    _append_overrides_invoke_source(
        lines=lines,
        step_index=step_index,
        indent=indent,
        positional_args_possible=positional_args_possible,
        static_is_existing_unique_creation=static_is_existing_unique_creation,
        static_is_callable_spell=static_is_callable_spell,
    )


def _append_overrides_kwargs_inline_source(
        *,
        lines: list[str],
        step_index: int,
        indent: str,
        static_override_target_count: int,
        positional_args_possible: bool,
        dependency_resolution_order: Tuple[Tuple[str, Tuple[Tuple[str, Optional[int]], ...]], ...],
        contract_positional_override: Optional[Sequence[Any]],
        has_contract_payload: bool,
        contract_payload_items: Tuple[Tuple[str, Any], ...],
        uses_positional_override: bool,
) -> None:
    """
    Append generated source lines for override-aware kwargs assembly.

    Contract:
        - Mirrors `_build_kwargs_with_overrides(...)` dependency/contract
          precedence semantics.
        - Emits static parameter/dependency lookups from shape metadata to
          remove runtime helper and per-step dependency-shape branching.
        - Preserves missing-dependency error translation contract.
    """
    if (
            not dependency_resolution_order
            and contract_positional_override is None
            and not has_contract_payload
    ):
        if static_override_target_count == 0:
            lines.append(f"{indent}kwargs_{step_index} = {{}}")
            if positional_args_possible:
                lines.extend([
                    f"{indent}if step_root_positional_override_{step_index} is not None:",
                    (
                        f"{indent}    kwargs_{step_index}[\"__args__\"] = "
                        f"step_root_positional_override_{step_index}"
                    ),
                ])
            return
        if static_override_target_count == 1:
            lines.extend([
                f"{indent}kwargs_{step_index} = {{",
                (
                    f"{indent}    single_override_socket_{step_index}.param_name: "
                    f"single_override_value_{step_index},"
                ),
                f"{indent}}}",
            ])
            if positional_args_possible:
                lines.extend([
                    f"{indent}if step_root_positional_override_{step_index} is not None:",
                    (
                        f"{indent}    kwargs_{step_index}[\"__args__\"] = "
                        f"step_root_positional_override_{step_index}"
                    ),
                ])
            return
        if static_override_target_count == 2:
            lines.extend([
                f"{indent}kwargs_{step_index} = {{",
                (
                    f"{indent}    first_override_socket_{step_index}.param_name: "
                    f"first_override_value_{step_index},"
                ),
                (
                    f"{indent}    second_override_socket_{step_index}.param_name: "
                    f"second_override_value_{step_index},"
                ),
                f"{indent}}}",
            ])
            if positional_args_possible:
                lines.extend([
                    f"{indent}if step_root_positional_override_{step_index} is not None:",
                    (
                        f"{indent}    kwargs_{step_index}[\"__args__\"] = "
                        f"step_root_positional_override_{step_index}"
                    ),
                ])
            return
        lines.append(
            f"{indent}kwargs_{step_index} = "
            f"override_values_{step_index} if override_values_{step_index} else {{}}"
        )
        return

    lines.append(f"{indent}kwargs_{step_index} = {{}}")

    def _append_missing_dependency_raise(
            *,
            dependency_name_literal: str,
            param_name_literal: str,
            inner_indent: str,
    ) -> None:
        """
        Append emitted source for a missing single dependency failure.

        Contract:
            - Emits the same MeldExecutionError shape used by the runtime
              kwargs builders.
            - Leaves the generated code positioned inside a surrounding
              `except KeyError as exc:` block.
        """
        lines.extend([
            f"{inner_indent}raise MeldExecutionError(",
            f"{inner_indent}    spell_id=spell_id_{step_index},",
            f"{inner_indent}    spell_name=spell_id_{step_index},",
            f"{inner_indent}    node_id=spell_id_{step_index},",
            f"{inner_indent}    param_name={param_name_literal},",
            (
                f"{inner_indent}    message=(\"Dependency \" + "
                f"{dependency_name_literal} + \" missing while building args for '\" + "
                f"spell_id_{step_index} + \"'.\"),"
            ),
            f"{inner_indent}) from exc",
        ])

    for param_index, dependency_entry in enumerate(dependency_resolution_order):
        param_name, dependency_keys = dependency_entry
        dependency_count = len(dependency_keys)
        if dependency_count == 0:
            continue
        param_name_literal = repr(param_name)
        if static_override_target_count == 1:
            lines.append(
                (
                    f"{indent}if single_override_socket_{step_index}.param_name != "
                    f"{param_name_literal}:"
                )
            )
            body_indent = f"{indent}    "
        elif static_override_target_count == 2:
            lines.extend([
                f"{indent}if (",
                (
                    f"{indent}    first_override_socket_{step_index}.param_name != "
                    f"{param_name_literal}"
                ),
                (
                    f"{indent}    and second_override_socket_{step_index}.param_name != "
                    f"{param_name_literal}"
                ),
                f"{indent}):",
            ])
            body_indent = f"{indent}    "
        else:
            lines.append(
                f"{indent}if {param_name_literal} not in override_values_{step_index}:"
            )
            body_indent = f"{indent}    "

        if dependency_count == 1:
            dependency_key = dependency_keys[0]
            dependency_key_literal = repr(dependency_key)
            dependency_name_literal = repr(dependency_key[0])
            lines.extend([
                f"{body_indent}try:",
                (
                    f"{body_indent}    kwargs_{step_index}[{param_name_literal}] = "
                    f"instance_results[{dependency_key_literal}]"
                ),
                f"{body_indent}except KeyError as exc:",
            ])
            _append_missing_dependency_raise(
                dependency_name_literal=dependency_name_literal,
                param_name_literal=param_name_literal,
                inner_indent=f"{body_indent}    ",
            )
            continue

        if dependency_count == 2:
            first_dependency_key = dependency_keys[0]
            second_dependency_key = dependency_keys[1]
            first_dependency_key_literal = repr(first_dependency_key)
            second_dependency_key_literal = repr(second_dependency_key)
            first_dependency_name_literal = repr(first_dependency_key[0])
            second_dependency_name_literal = repr(second_dependency_key[0])
            first_value_name = f"dep_value_{step_index}_{param_index}_0"
            second_value_name = f"dep_value_{step_index}_{param_index}_1"
            lines.extend([
                f"{body_indent}try:",
                (
                    f"{body_indent}    {first_value_name} = "
                    f"instance_results[{first_dependency_key_literal}]"
                ),
                f"{body_indent}except KeyError as exc:",
            ])
            _append_missing_dependency_raise(
                dependency_name_literal=first_dependency_name_literal,
                param_name_literal=param_name_literal,
                inner_indent=f"{body_indent}    ",
            )
            lines.extend([
                f"{body_indent}try:",
                (
                    f"{body_indent}    {second_value_name} = "
                    f"instance_results[{second_dependency_key_literal}]"
                ),
                f"{body_indent}except KeyError as exc:",
            ])
            _append_missing_dependency_raise(
                dependency_name_literal=second_dependency_name_literal,
                param_name_literal=param_name_literal,
                inner_indent=f"{body_indent}    ",
            )
            lines.extend([
                (
                    f"{body_indent}kwargs_{step_index}[{param_name_literal}] = "
                    f"[{first_value_name}, {second_value_name}]"
                ),
            ])
            continue

        values_name = f"dep_values_{step_index}_{param_index}"
        lines.append(f"{body_indent}{values_name} = []")
        for key_index, dependency_key in enumerate(dependency_keys):
            dependency_key_literal = repr(dependency_key)
            dependency_name_literal = repr(dependency_key[0])
            value_name = f"dep_value_{step_index}_{param_index}_{key_index}"
            lines.extend([
                f"{body_indent}try:",
                (
                    f"{body_indent}    {value_name} = "
                    f"instance_results[{dependency_key_literal}]"
                ),
                f"{body_indent}except KeyError as exc:",
            ])
            _append_missing_dependency_raise(
                dependency_name_literal=dependency_name_literal,
                param_name_literal=param_name_literal,
                inner_indent=f"{body_indent}    ",
            )
            lines.append(f"{body_indent}{values_name}.append({value_name})")
        lines.append(
            f"{body_indent}kwargs_{step_index}[{param_name_literal}] = {values_name}"
        )

    if contract_positional_override is not None:
        lines.append(
            f"{indent}kwargs_{step_index}[\"__args__\"] = {repr(contract_positional_override)}"
        )

    if has_contract_payload and contract_payload_items:
        for param_name, value in contract_payload_items:
            if param_name == "__args__" and uses_positional_override:
                continue
            param_name_literal = repr(param_name)
            if static_override_target_count == 1:
                lines.extend([
                    (
                        f"{indent}if single_override_socket_{step_index}.param_name != "
                        f"{param_name_literal}:"
                    ),
                    (
                        f"{indent}    kwargs_{step_index}[{param_name_literal}] = "
                        f"{repr(value)}"
                    ),
                ])
            elif static_override_target_count == 2:
                lines.extend([
                    f"{indent}if (",
                    (
                        f"{indent}    first_override_socket_{step_index}.param_name != "
                        f"{param_name_literal}"
                    ),
                    (
                        f"{indent}    and second_override_socket_{step_index}.param_name != "
                        f"{param_name_literal}"
                    ),
                    f"{indent}):",
                    (
                        f"{indent}    kwargs_{step_index}[{param_name_literal}] = "
                        f"{repr(value)}"
                    ),
                ])
            else:
                lines.extend([
                    (
                        f"{indent}if {param_name_literal} not in "
                        f"override_values_{step_index}:"
                    ),
                    (
                        f"{indent}    kwargs_{step_index}[{param_name_literal}] = "
                        f"{repr(value)}"
                    ),
                ])

    if static_override_target_count == 0:
        if positional_args_possible:
            lines.extend([
                f"{indent}if step_root_positional_override_{step_index} is not None:",
                (
                    f"{indent}    kwargs_{step_index}[\"__args__\"] = "
                    f"step_root_positional_override_{step_index}"
                ),
            ])
    elif static_override_target_count == 1:
        lines.append(
            (
                f"{indent}kwargs_{step_index}[single_override_socket_{step_index}.param_name] = "
                f"single_override_value_{step_index}"
            )
        )
        if positional_args_possible:
            lines.extend([
                f"{indent}if step_root_positional_override_{step_index} is not None:",
                (
                    f"{indent}    kwargs_{step_index}[\"__args__\"] = "
                    f"step_root_positional_override_{step_index}"
                ),
            ])
    elif static_override_target_count == 2:
        lines.extend([
            (
                f"{indent}kwargs_{step_index}[first_override_socket_{step_index}.param_name] = "
                f"first_override_value_{step_index}"
            ),
            (
                f"{indent}kwargs_{step_index}[second_override_socket_{step_index}.param_name] = "
                f"second_override_value_{step_index}"
            ),
        ])
        if positional_args_possible:
            lines.extend([
                f"{indent}if step_root_positional_override_{step_index} is not None:",
                (
                    f"{indent}    kwargs_{step_index}[\"__args__\"] = "
                    f"step_root_positional_override_{step_index}"
                ),
            ])
    else:
        lines.extend([
            f"{indent}if override_values_{step_index}:",
            f"{indent}    kwargs_{step_index}.update(override_values_{step_index})",
        ])


def _append_no_overrides_kwargs_inline_source(
        *,
        lines: list[str],
        step_index: int,
        indent: str,
        dependency_resolution_order: Tuple[Tuple[str, Tuple[Tuple[str, Optional[int]], ...]], ...],
        contract_positional_override: Optional[Sequence[Any]],
        has_contract_payload: bool,
        contract_payload_items: Tuple[Tuple[str, Any], ...],
        uses_positional_override: bool,
        emit_empty_kwargs: bool = True,
) -> None:
    """
    Append generated source lines for no-override kwargs assembly.

    Contract:
        - Mirrors `_build_kwargs_no_overrides(...)` dependency/contract behavior.
        - Avoids override-membership/update work in shape lanes where overrides
          are statically absent.
        - Preserves missing-dependency error translation contract.
    """
    if (
            not dependency_resolution_order
            and contract_positional_override is None
            and not has_contract_payload
    ):
        if emit_empty_kwargs:
            lines.append(f"{indent}kwargs_{step_index} = {{}}")
        return

    if (
            not dependency_resolution_order
            and contract_positional_override is None
            and has_contract_payload
    ):
        if not contract_payload_items:
            lines.append(f"{indent}kwargs_{step_index} = {{}}")
            return
        if not uses_positional_override:
            lines.append(
                f"{indent}kwargs_{step_index} = {dict(contract_payload_items)!r}"
            )
            return
        lines.append(f"{indent}kwargs_{step_index} = {{}}")
        for param_name, value in contract_payload_items:
            if param_name == "__args__":
                continue
            lines.append(
                f"{indent}kwargs_{step_index}[{param_name!r}] = {value!r}"
            )
        return

    lines.append(f"{indent}kwargs_{step_index} = {{}}")

    def _append_missing_dependency_raise(
            *,
            dependency_name_literal: str,
            param_name_literal: str,
            inner_indent: str,
    ) -> None:
        """
        Append emitted source for a missing dependency failure in the generic
        kwargs builder path.

        Contract:
            - Emits the same MeldExecutionError shape as the inline override
              constructor path.
            - Assumes the generated code is nested inside an `except` block.
        """
        lines.extend([
            f"{inner_indent}raise MeldExecutionError(",
            f"{inner_indent}    spell_id=spell_id_{step_index},",
            f"{inner_indent}    spell_name=spell_id_{step_index},",
            f"{inner_indent}    node_id=spell_id_{step_index},",
            f"{inner_indent}    param_name={param_name_literal},",
            (
                f"{inner_indent}    message=(\"Dependency \" + "
                f"{dependency_name_literal} + \" missing while building args for '\" + "
                f"spell_id_{step_index} + \"'.\"),"
            ),
            f"{inner_indent}) from exc",
        ])

    for param_index, dependency_entry in enumerate(dependency_resolution_order):
        param_name, dependency_keys = dependency_entry
        dependency_count = len(dependency_keys)
        if dependency_count == 0:
            continue
        param_name_literal = repr(param_name)

        if dependency_count == 1:
            dependency_key = dependency_keys[0]
            dependency_key_literal = repr(dependency_key)
            dependency_name_literal = repr(dependency_key[0])
            lines.extend([
                f"{indent}try:",
                (
                    f"{indent}    kwargs_{step_index}[{param_name_literal}] = "
                    f"instance_results[{dependency_key_literal}]"
                ),
                f"{indent}except KeyError as exc:",
            ])
            _append_missing_dependency_raise(
                dependency_name_literal=dependency_name_literal,
                param_name_literal=param_name_literal,
                inner_indent=f"{indent}    ",
            )
            continue

        if dependency_count == 2:
            first_dependency_key = dependency_keys[0]
            second_dependency_key = dependency_keys[1]
            first_dependency_key_literal = repr(first_dependency_key)
            second_dependency_key_literal = repr(second_dependency_key)
            first_dependency_name_literal = repr(first_dependency_key[0])
            second_dependency_name_literal = repr(second_dependency_key[0])
            first_value_name = f"dep_value_{step_index}_{param_index}_0"
            second_value_name = f"dep_value_{step_index}_{param_index}_1"
            lines.extend([
                f"{indent}try:",
                (
                    f"{indent}    {first_value_name} = "
                    f"instance_results[{first_dependency_key_literal}]"
                ),
                f"{indent}except KeyError as exc:",
            ])
            _append_missing_dependency_raise(
                dependency_name_literal=first_dependency_name_literal,
                param_name_literal=param_name_literal,
                inner_indent=f"{indent}    ",
            )
            lines.extend([
                f"{indent}try:",
                (
                    f"{indent}    {second_value_name} = "
                    f"instance_results[{second_dependency_key_literal}]"
                ),
                f"{indent}except KeyError as exc:",
            ])
            _append_missing_dependency_raise(
                dependency_name_literal=second_dependency_name_literal,
                param_name_literal=param_name_literal,
                inner_indent=f"{indent}    ",
            )
            lines.append(
                (
                    f"{indent}kwargs_{step_index}[{param_name_literal}] = "
                    f"[{first_value_name}, {second_value_name}]"
                )
            )
            continue

        values_name = f"dep_values_{step_index}_{param_index}"
        lines.append(f"{indent}{values_name} = []")
        for key_index, dependency_key in enumerate(dependency_keys):
            dependency_key_literal = repr(dependency_key)
            dependency_name_literal = repr(dependency_key[0])
            value_name = f"dep_value_{step_index}_{param_index}_{key_index}"
            lines.extend([
                f"{indent}try:",
                (
                    f"{indent}    {value_name} = "
                    f"instance_results[{dependency_key_literal}]"
                ),
                f"{indent}except KeyError as exc:",
            ])
            _append_missing_dependency_raise(
                dependency_name_literal=dependency_name_literal,
                param_name_literal=param_name_literal,
                inner_indent=f"{indent}    ",
            )
            lines.append(f"{indent}{values_name}.append({value_name})")
        lines.append(
            f"{indent}kwargs_{step_index}[{param_name_literal}] = {values_name}"
        )

    if contract_positional_override is not None:
        lines.append(
            f"{indent}kwargs_{step_index}[\"__args__\"] = {contract_positional_override!r}"
        )

    if has_contract_payload and contract_payload_items:
        for param_name, value in contract_payload_items:
            if param_name == "__args__" and uses_positional_override:
                continue
            lines.append(
                f"{indent}kwargs_{step_index}[{param_name!r}] = {value!r}"
            )


def _append_overrides_construct_no_overrides_source(
        *,
        lines: list[str],
        step_index: int,
        indent: str,
        positional_args_possible: bool,
        dependency_resolution_order: Tuple[Tuple[str, Tuple[Tuple[str, Optional[int]], ...]], ...],
        contract_positional_override: Optional[Sequence[Any]],
        has_contract_payload: bool,
        contract_payload_items: Tuple[Tuple[str, Any], ...],
        uses_positional_override: bool,
        static_is_existing_unique_creation: Optional[bool] = None,
        static_is_callable_spell: Optional[bool] = None,
) -> None:
    """
    Append generated source lines for no-override kwargs materialization.

    Contract:
        - Inlines `_build_kwargs_no_overrides(...)` semantics for shape lanes.
        - Preserves invoke semantics while inlining call dispatch.
    """
    kwargs_always_empty = (
        not positional_args_possible
        and not dependency_resolution_order
        and contract_positional_override is None
        and not has_contract_payload
    )
    _append_no_overrides_kwargs_inline_source(
        lines=lines,
        step_index=step_index,
        indent=indent,
        dependency_resolution_order=dependency_resolution_order,
        contract_positional_override=contract_positional_override,
        has_contract_payload=has_contract_payload,
        contract_payload_items=contract_payload_items,
        uses_positional_override=uses_positional_override,
        emit_empty_kwargs=not kwargs_always_empty,
    )
    _append_overrides_invoke_source(
        lines=lines,
        step_index=step_index,
        indent=indent,
        positional_args_possible=positional_args_possible,
        static_is_existing_unique_creation=static_is_existing_unique_creation,
        static_is_callable_spell=static_is_callable_spell,
        kwargs_always_empty=kwargs_always_empty,
    )


def _append_overrides_invoke_source(
        *,
        lines: list[str],
        step_index: int,
        indent: str,
        positional_args_possible: bool,
        static_is_existing_unique_creation: Optional[bool] = None,
        static_is_callable_spell: Optional[bool] = None,
        kwargs_always_empty: bool = False,
) -> None:
    """
    Append generated source for step-level invoke dispatch.

    Contract:
        - Preserves `_invoke_spell_with_kwargs(...)` behavior for existing
          creation, callable, and raw-value spell variants.
        - Supports `__args__` payload decoding only when the shape can carry
          positional overrides.
        - Keeps error translation in generated source for invalid args and
          invoke-time exceptions.
    """
    def _append_existing_creation_body(body_indent: str) -> None:
        """
        Append emitted source for the existing-creation fast path.

        Contract:
            - Reuses `user_created_object` directly.
            - Emits a RuntimeError when an existing-creation spell lacks the
              required prebound object.
        """
        lines.extend([
            f"{body_indent}instance_{step_index} = plan_step_{step_index}.spell.user_created_object",
            f"{body_indent}if instance_{step_index} is None:",
            f"{body_indent}    raise RuntimeError(",
            f"{body_indent}        \"[MELD] EXISTING_CREATION spell has no `user_created_object` \"",
            f"{body_indent}        \"(spell_id=\" + spell_id_{step_index} + \").\"",
            f"{body_indent}    )",
        ])

    def _append_callable_body(body_indent: str) -> None:
        """
        Append emitted source for callable-spell invocation.

        Contract:
            - Supports `__args__` positional override payloads only when the
              selected shape allows them.
            - Preserves MeldExecutionError wrapping for invalid `__args__`
              payloads and invoke-time exceptions.
        """
        if positional_args_possible:
            lines.extend([
                f"{body_indent}raw_args_{step_index} = kwargs_{step_index}.get(\"__args__\", _MISSING)",
                f"{body_indent}if raw_args_{step_index} is _MISSING:",
                f"{body_indent}    args_{step_index} = []",
                f"{body_indent}    call_kwargs_{step_index} = kwargs_{step_index}",
                f"{body_indent}elif isinstance(raw_args_{step_index}, tuple):",
                f"{body_indent}    args_{step_index} = raw_args_{step_index}",
                f"{body_indent}    if len(kwargs_{step_index}) == 1:",
                f"{body_indent}        call_kwargs_{step_index} = {{}}",
                f"{body_indent}    else:",
                f"{body_indent}        call_kwargs_{step_index} = dict(kwargs_{step_index})",
                f"{body_indent}        call_kwargs_{step_index}.pop(\"__args__\", None)",
                f"{body_indent}elif isinstance(raw_args_{step_index}, list):",
                f"{body_indent}    args_{step_index} = raw_args_{step_index}",
                f"{body_indent}    if len(kwargs_{step_index}) == 1:",
                f"{body_indent}        call_kwargs_{step_index} = {{}}",
                f"{body_indent}    else:",
                f"{body_indent}        call_kwargs_{step_index} = dict(kwargs_{step_index})",
                f"{body_indent}        call_kwargs_{step_index}.pop(\"__args__\", None)",
                f"{body_indent}else:",
                f"{body_indent}    raise MeldExecutionError(",
                f"{body_indent}        spell_id=plan_step_{step_index}.spell.spell_index.current,",
                f"{body_indent}        spell_name=plan_step_{step_index}.spell.spell_name,",
                f"{body_indent}        message=\"__args__ override must be a list or tuple.\",",
                f"{body_indent}    )",
                f"{body_indent}try:",
                (
                    f"{body_indent}    instance_{step_index} = "
                    f"plan_step_{step_index}.spell.spell(*args_{step_index}, **call_kwargs_{step_index})"
                ),
                f"{body_indent}except Exception as exc:",
                f"{body_indent}    raise MeldExecutionError(",
                f"{body_indent}        spell_id=plan_step_{step_index}.spell.spell_index.current,",
                f"{body_indent}        spell_name=plan_step_{step_index}.spell.spell_name,",
                (
                    f"{body_indent}        message=(\"Error invoking spell '\" + "
                    f"plan_step_{step_index}.spell.spell_name + \"'.\"),"
                ),
                f"{body_indent}        inner=exc,",
                f"{body_indent}    ) from exc",
            ])
            return
        if kwargs_always_empty:
            lines.extend([
                f"{body_indent}try:",
                (
                    f"{body_indent}    instance_{step_index} = "
                    f"plan_step_{step_index}.spell.spell()"
                ),
                f"{body_indent}except Exception as exc:",
                f"{body_indent}    raise MeldExecutionError(",
                f"{body_indent}        spell_id=plan_step_{step_index}.spell.spell_index.current,",
                f"{body_indent}        spell_name=plan_step_{step_index}.spell.spell_name,",
                (
                    f"{body_indent}        message=(\"Error invoking spell '\" + "
                    f"plan_step_{step_index}.spell.spell_name + \"'.\"),"
                ),
                f"{body_indent}        inner=exc,",
                f"{body_indent}    ) from exc",
            ])
            return
        lines.extend([
            f"{body_indent}try:",
            (
                f"{body_indent}    instance_{step_index} = "
                f"plan_step_{step_index}.spell.spell(**kwargs_{step_index})"
            ),
            f"{body_indent}except Exception as exc:",
            f"{body_indent}    raise MeldExecutionError(",
            f"{body_indent}        spell_id=plan_step_{step_index}.spell.spell_index.current,",
            f"{body_indent}        spell_name=plan_step_{step_index}.spell.spell_name,",
            (
                f"{body_indent}        message=(\"Error invoking spell '\" + "
                f"plan_step_{step_index}.spell.spell_name + \"'.\"),"
            ),
            f"{body_indent}        inner=exc,",
            f"{body_indent}    ) from exc",
        ])

    def _append_raw_value_body(body_indent: str) -> None:
        """
        Append emitted source for raw-value spell resolution.

        Contract:
            Raw-value spells bypass callable invocation and reuse the spell's
            stored object/value directly.
        """
        lines.append(
            f"{body_indent}instance_{step_index} = plan_step_{step_index}.spell.spell"
        )

    if static_is_existing_unique_creation is True:
        _append_existing_creation_body(indent)
        return

    has_existing_branch = static_is_existing_unique_creation is None
    if has_existing_branch:
        lines.append(f"{indent}if is_existing_unique_creation_{step_index}:")
        _append_existing_creation_body(f"{indent}    ")

    if static_is_callable_spell is True:
        if has_existing_branch:
            lines.append(f"{indent}elif is_callable_spell_{step_index}:")
            _append_callable_body(f"{indent}    ")
        else:
            _append_callable_body(indent)
        return

    if static_is_callable_spell is False:
        if has_existing_branch:
            lines.append(f"{indent}else:")
            _append_raw_value_body(f"{indent}    ")
        else:
            _append_raw_value_body(indent)
        return

    if has_existing_branch:
        lines.append(f"{indent}elif is_callable_spell_{step_index}:")
        _append_callable_body(f"{indent}    ")
        lines.append(f"{indent}else:")
        _append_raw_value_body(f"{indent}    ")
        return

    lines.append(f"{indent}if is_callable_spell_{step_index}:")
    _append_callable_body(f"{indent}    ")
    lines.append(f"{indent}else:")
    _append_raw_value_body(f"{indent}    ")


def _append_overrides_shape_owner_creations_source(
        *,
        lines: list[str],
        step_index: int,
) -> None:
    """
    Append emitted source lines for OWNER-target creations resolution.

    Contract:
        - Uses spell-owned creations when available.
        - Falls back to `owner_creations` when spell-owned creations are missing.
        - Raises when neither owner creations source is available.
    """
    lines.extend([
        f"    owner_creations_{step_index} = spell_{step_index}._owner_creations",
        f"    if owner_creations_{step_index} is not None:",
        f"        creations_{step_index} = owner_creations_{step_index}",
        "    elif owner_creations is None:",
        "        raise RuntimeError(",
        "            \"Phase 13 OWNER execution requires owner_creations.\"",
        "        )",
        "    else:",
        f"        creations_{step_index} = owner_creations",
    ])


def _append_overrides_step_shape_source(
        *,
        lines: list[str],
        step_index: int,
        spell_id: str,
        creations_target_kind: Any,
        existence: Existence,
        use_spell_lock_hint: bool,
        must_register: bool,
        is_root_step: bool,
        has_static_targeted_overrides: bool,
        static_override_target_count: int,
        use_positional_override: bool,
        has_static_root_positional_override: bool,
        dependency_resolution_order: Tuple[Tuple[str, Tuple[Tuple[str, Optional[int]], ...]], ...],
        contract_positional_override: Optional[Sequence[Any]],
        has_contract_payload: bool,
        contract_payload_items: Tuple[Tuple[str, Any], ...],
        static_is_existing_unique_creation: Optional[bool],
        static_is_callable_spell: Optional[bool],
        static_has_disposal_methods: Optional[bool],
) -> None:
    """
    Append one step block specialized by static target/existence metadata.

    Contract:
        - Preserves existing override-reuse and registration semantics.
        - Removes runtime target-kind and existence branch selection.
    """
    use_no_override_fast_path = (
        not has_static_targeted_overrides and not has_static_root_positional_override
    )
    positional_args_possible = (
        use_positional_override or has_static_root_positional_override
    )
    many_registration_static_enabled = (
        existence is Existence.many
        and must_register
        and static_has_disposal_methods is True
    )
    many_registration_runtime_enabled = (
        existence is Existence.many
        and must_register
        and static_has_disposal_methods is None
    )
    registration_metadata_required = (
        existence is not Existence.many
        or many_registration_static_enabled
        or many_registration_runtime_enabled
    )
    lines.extend([
        f"    plan_step_{step_index} = steps[{step_index}]",
        f"    spell_{step_index} = step_spells[{step_index}]",
    ])
    if registration_metadata_required:
        lines.append(
            f"    spell_id_{step_index} = step_spell_ids[{step_index}]"
        )
        if existence is not Existence.many or many_registration_runtime_enabled:
            lines.append(
                (
                    f"    has_disposal_methods_{step_index} = "
                    f"step_has_disposal_methods[{step_index}]"
                )
            )
        lines.append(
            (
                f"    disposal_methods_{step_index} = "
                f"step_disposal_methods[{step_index}]"
            )
        )
    if static_is_callable_spell is None:
        lines.extend([
            (
                f"    is_callable_spell_{step_index} = "
                f"step_is_callable_spell[{step_index}]"
            ),
        ])
    effective_is_existing_unique_creation_static = static_is_existing_unique_creation
    if existence is Existence.many:
        effective_is_existing_unique_creation_static = False
    else:
        lines.extend([
            (
                f"    has_targeted_overrides_{step_index} = "
                f"step_has_targeted_overrides[{step_index}]"
            ),
        ])
        if effective_is_existing_unique_creation_static is None:
            lines.extend([
                (
                    f"    is_existing_unique_creation_{step_index} = "
                    f"step_is_existing_unique_creation[{step_index}]"
                ),
            ])
    if not (existence is Existence.many and use_no_override_fast_path):
        lines.append(
            f"    override_targets_{step_index} = step_override_targets[{step_index}]"
        )
    if positional_args_possible:
        if is_root_step:
            lines.append(
                f"    step_root_positional_override_{step_index} = root_positional_override"
            )
        else:
            lines.append(
                f"    step_root_positional_override_{step_index} = None"
            )

    if creations_target_kind in (
            ExecutionPlanTargetKind.CALLER,
            ExecutionPlanTargetKind.SPELLSPACE,
    ):
        lines.append(f"    creations_{step_index} = caller_creations")
    elif creations_target_kind == ExecutionPlanTargetKind.OWNER:
        _append_overrides_shape_owner_creations_source(
            lines=lines,
            step_index=step_index,
        )
    else:
        lines.extend([
            "    raise RuntimeError(",
            (
                "        \"Unsupported creations target kind for spell "
                f"'{spell_id}'.\""
            ),
            "    )",
        ])

    if existence is Existence.many:
        if use_no_override_fast_path:
            _append_overrides_construct_no_overrides_source(
                lines=lines,
                step_index=step_index,
                indent="    ",
                positional_args_possible=positional_args_possible,
                dependency_resolution_order=dependency_resolution_order,
                contract_positional_override=contract_positional_override,
                has_contract_payload=has_contract_payload,
                contract_payload_items=contract_payload_items,
                uses_positional_override=use_positional_override,
                static_is_existing_unique_creation=effective_is_existing_unique_creation_static,
                static_is_callable_spell=static_is_callable_spell,
            )
        else:
            _append_overrides_construct_inline_source(
                lines=lines,
                step_index=step_index,
                indent="    ",
                static_override_target_count=static_override_target_count,
                positional_args_possible=positional_args_possible,
                dependency_resolution_order=dependency_resolution_order,
                contract_positional_override=contract_positional_override,
                has_contract_payload=has_contract_payload,
                contract_payload_items=contract_payload_items,
                uses_positional_override=use_positional_override,
                static_is_existing_unique_creation=effective_is_existing_unique_creation_static,
                static_is_callable_spell=static_is_callable_spell,
            )
        if many_registration_static_enabled:
            _append_overrides_many_register_inline_source(
                lines=lines,
                step_index=step_index,
                indent="    ",
                static_has_disposal_methods=True,
            )
        elif many_registration_runtime_enabled:
            _append_overrides_many_register_inline_source(
                lines=lines,
                step_index=step_index,
                indent="    ",
                static_has_disposal_methods=None,
            )
    elif existence in (
            Existence.unique_per_conduit,
            Existence.unique_per_spell_space,
    ):
        lines.extend([
            (
                f"    instance_{step_index} = _get_existing_creation("
                f"spell=spell_{step_index}, "
                f"creations=creations_{step_index}, "
                f"existence=plan_step_{step_index}.existence)"
            ),
            f"    if instance_{step_index} is not None:",
            (
                f"        _raise_override_on_existing_instance("
                f"spell=spell_{step_index}, "
                f"has_targeted_overrides=has_targeted_overrides_{step_index}, "
                f"any_overrides_present=any_overrides_present, "
                f"root_spell_id=root_spell_id)"
            ),
            "    else:",
            f"        with creations_{step_index}._lock:",
            (
                f"            instance_{step_index} = _get_existing_creation("
                f"spell=spell_{step_index}, "
                f"creations=creations_{step_index}, "
                f"existence=plan_step_{step_index}.existence)"
            ),
            f"            if instance_{step_index} is not None:",
            (
                f"                _raise_override_on_existing_instance("
                f"spell=spell_{step_index}, "
                f"has_targeted_overrides=has_targeted_overrides_{step_index}, "
                f"any_overrides_present=any_overrides_present, "
                f"root_spell_id=root_spell_id)"
            ),
            "            else:",
        ])
        if use_no_override_fast_path:
            _append_overrides_construct_no_overrides_source(
                lines=lines,
                step_index=step_index,
                indent="                ",
                positional_args_possible=positional_args_possible,
                dependency_resolution_order=dependency_resolution_order,
                contract_positional_override=contract_positional_override,
                has_contract_payload=has_contract_payload,
                contract_payload_items=contract_payload_items,
                uses_positional_override=use_positional_override,
                static_is_existing_unique_creation=effective_is_existing_unique_creation_static,
                static_is_callable_spell=static_is_callable_spell,
            )
        else:
            _append_overrides_construct_inline_source(
                lines=lines,
                step_index=step_index,
                indent="                ",
                static_override_target_count=static_override_target_count,
                positional_args_possible=positional_args_possible,
                dependency_resolution_order=dependency_resolution_order,
                contract_positional_override=contract_positional_override,
                has_contract_payload=has_contract_payload,
                contract_payload_items=contract_payload_items,
                uses_positional_override=use_positional_override,
                static_is_existing_unique_creation=effective_is_existing_unique_creation_static,
                static_is_callable_spell=static_is_callable_spell,
            )
        lines.extend([
            (
                f"                _register_spell_instance_prebound("
                f"spell_id=spell_id_{step_index}, "
                f"instance=instance_{step_index}, "
                f"creations=creations_{step_index}, "
                f"existence=plan_step_{step_index}.existence, "
                f"has_disposal_methods=has_disposal_methods_{step_index}, "
                f"disposal_methods=disposal_methods_{step_index})"
            ),
        ])
    elif use_spell_lock_hint:
        lines.extend([
            (
                f"    use_spell_lock_{step_index} = not ("
                f"caller_creations_lock_held and "
                f"creations_{step_index} is caller_creations)"
            ),
            f"    if use_spell_lock_{step_index}:",
            f"        with spell_{step_index}._lock:",
            f"            with creations_{step_index}._lock:",
            (
                f"                instance_{step_index} = _get_existing_creation("
                f"spell=spell_{step_index}, "
                f"creations=creations_{step_index}, "
                f"existence=plan_step_{step_index}.existence)"
            ),
            f"            if instance_{step_index} is not None:",
            (
                f"                _raise_override_on_existing_instance("
                f"spell=spell_{step_index}, "
                f"has_targeted_overrides=has_targeted_overrides_{step_index}, "
                f"any_overrides_present=any_overrides_present, "
                f"root_spell_id=root_spell_id)"
            ),
            "            else:",
        ])
        if use_no_override_fast_path:
            _append_overrides_construct_no_overrides_source(
                lines=lines,
                step_index=step_index,
                indent="                ",
                positional_args_possible=positional_args_possible,
                dependency_resolution_order=dependency_resolution_order,
                contract_positional_override=contract_positional_override,
                has_contract_payload=has_contract_payload,
                contract_payload_items=contract_payload_items,
                uses_positional_override=use_positional_override,
                static_is_existing_unique_creation=effective_is_existing_unique_creation_static,
                static_is_callable_spell=static_is_callable_spell,
            )
        else:
            _append_overrides_construct_inline_source(
                lines=lines,
                step_index=step_index,
                indent="                ",
                static_override_target_count=static_override_target_count,
                positional_args_possible=positional_args_possible,
                dependency_resolution_order=dependency_resolution_order,
                contract_positional_override=contract_positional_override,
                has_contract_payload=has_contract_payload,
                contract_payload_items=contract_payload_items,
                uses_positional_override=use_positional_override,
                static_is_existing_unique_creation=effective_is_existing_unique_creation_static,
                static_is_callable_spell=static_is_callable_spell,
            )
        lines.extend([
            f"                with creations_{step_index}._lock:",
            (
                f"                    _register_spell_instance_prebound("
                f"spell_id=spell_id_{step_index}, "
                f"instance=instance_{step_index}, "
                f"creations=creations_{step_index}, "
                f"existence=plan_step_{step_index}.existence, "
                f"has_disposal_methods=has_disposal_methods_{step_index}, "
                f"disposal_methods=disposal_methods_{step_index})"
            ),
            "    else:",
            f"        with creations_{step_index}._lock:",
            (
                f"            instance_{step_index} = _get_existing_creation("
                f"spell=spell_{step_index}, "
                f"creations=creations_{step_index}, "
                f"existence=plan_step_{step_index}.existence)"
            ),
            f"            if instance_{step_index} is not None:",
            (
                f"                _raise_override_on_existing_instance("
                f"spell=spell_{step_index}, "
                f"has_targeted_overrides=has_targeted_overrides_{step_index}, "
                f"any_overrides_present=any_overrides_present, "
                f"root_spell_id=root_spell_id)"
            ),
            "            else:",
        ])
        if use_no_override_fast_path:
            _append_overrides_construct_no_overrides_source(
                lines=lines,
                step_index=step_index,
                indent="                ",
                positional_args_possible=positional_args_possible,
                dependency_resolution_order=dependency_resolution_order,
                contract_positional_override=contract_positional_override,
                has_contract_payload=has_contract_payload,
                contract_payload_items=contract_payload_items,
                uses_positional_override=use_positional_override,
                static_is_existing_unique_creation=effective_is_existing_unique_creation_static,
                static_is_callable_spell=static_is_callable_spell,
            )
        else:
            _append_overrides_construct_inline_source(
                lines=lines,
                step_index=step_index,
                indent="                ",
                static_override_target_count=static_override_target_count,
                positional_args_possible=positional_args_possible,
                dependency_resolution_order=dependency_resolution_order,
                contract_positional_override=contract_positional_override,
                has_contract_payload=has_contract_payload,
                contract_payload_items=contract_payload_items,
                uses_positional_override=use_positional_override,
                static_is_existing_unique_creation=effective_is_existing_unique_creation_static,
                static_is_callable_spell=static_is_callable_spell,
            )
        lines.extend([
            (
                f"                _register_spell_instance_prebound("
                f"spell_id=spell_id_{step_index}, "
                f"instance=instance_{step_index}, "
                f"creations=creations_{step_index}, "
                f"existence=plan_step_{step_index}.existence, "
                f"has_disposal_methods=has_disposal_methods_{step_index}, "
                f"disposal_methods=disposal_methods_{step_index})"
            ),
        ])
    else:
        lines.extend([
            f"    with creations_{step_index}._lock:",
            (
                f"        instance_{step_index} = _get_existing_creation("
                f"spell=spell_{step_index}, "
                f"creations=creations_{step_index}, "
                f"existence=plan_step_{step_index}.existence)"
            ),
            f"        if instance_{step_index} is not None:",
            (
                f"            _raise_override_on_existing_instance("
                f"spell=spell_{step_index}, "
                f"has_targeted_overrides=has_targeted_overrides_{step_index}, "
                f"any_overrides_present=any_overrides_present, "
                f"root_spell_id=root_spell_id)"
            ),
            "        else:",
        ])
        if use_no_override_fast_path:
            _append_overrides_construct_no_overrides_source(
                lines=lines,
                step_index=step_index,
                indent="            ",
                positional_args_possible=positional_args_possible,
                dependency_resolution_order=dependency_resolution_order,
                contract_positional_override=contract_positional_override,
                has_contract_payload=has_contract_payload,
                contract_payload_items=contract_payload_items,
                uses_positional_override=use_positional_override,
                static_is_existing_unique_creation=effective_is_existing_unique_creation_static,
                static_is_callable_spell=static_is_callable_spell,
            )
        else:
            _append_overrides_construct_inline_source(
                lines=lines,
                step_index=step_index,
                indent="            ",
                static_override_target_count=static_override_target_count,
                positional_args_possible=positional_args_possible,
                dependency_resolution_order=dependency_resolution_order,
                contract_positional_override=contract_positional_override,
                has_contract_payload=has_contract_payload,
                contract_payload_items=contract_payload_items,
                uses_positional_override=use_positional_override,
                static_is_existing_unique_creation=effective_is_existing_unique_creation_static,
                static_is_callable_spell=static_is_callable_spell,
            )
        lines.extend([
            (
                f"            _register_spell_instance_prebound("
                f"spell_id=spell_id_{step_index}, "
                f"instance=instance_{step_index}, "
                f"creations=creations_{step_index}, "
                f"existence=plan_step_{step_index}.existence, "
                f"has_disposal_methods=has_disposal_methods_{step_index}, "
                f"disposal_methods=disposal_methods_{step_index})"
            ),
        ])

    lines.append(
        f"    instance_results[step_instance_keys[{step_index}]] = instance_{step_index}"
    )


def _append_overrides_many_register_inline_source(
        *,
        lines: list[str],
        step_index: int,
        indent: str,
        static_has_disposal_methods: Optional[bool],
) -> None:
    """
    Append direct Existence.many registration source for one emitted step.

    Contract:
        - Mirrors `_register_spell_instance_prebound(...)` Existence.many logic.
        - Registers only when disposal methods exist for the step spell.
        - Avoids the generic registration helper dispatch on this hot lane.
    """
    if static_has_disposal_methods is False:
        return
    if static_has_disposal_methods is True:
        lines.extend([
            f"{indent}with creations_{step_index}._lock:",
            f"{indent}    creations_{step_index}.add_many_creations(",
            f"{indent}        spell_id_{step_index},",
            f"{indent}        instance_{step_index},",
            f"{indent}        has_disposal_methods=True,",
            f"{indent}        disposal_methods=disposal_methods_{step_index},",
            f"{indent}    )",
        ])
        return

    lines.extend([
        f"{indent}if has_disposal_methods_{step_index}:",
        f"{indent}    with creations_{step_index}._lock:",
        f"{indent}        creations_{step_index}.add_many_creations(",
        f"{indent}            spell_id_{step_index},",
        f"{indent}            instance_{step_index},",
        (
            f"{indent}            has_disposal_methods="
            f"has_disposal_methods_{step_index},"
        ),
        f"{indent}            disposal_methods=disposal_methods_{step_index},",
        f"{indent}        )",
    ])


def _append_overrides_step_source(
        *,
        lines: list[str],
        step_index: int,
) -> None:
    """
    Append emitted source lines for one override-aware step execution block.

    Contract:
        - Emits deterministic variable names per step index.
        - Mirrors override-aware reuse, lock, and registration semantics.
    """
    lines.extend([
        f"    plan_step_{step_index} = steps[{step_index}]",
        f"    spell_{step_index} = step_spells[{step_index}]",
        f"    spell_id_{step_index} = step_spell_ids[{step_index}]",
        (
            f"    has_disposal_methods_{step_index} = "
            f"step_has_disposal_methods[{step_index}]"
        ),
        (
            f"    disposal_methods_{step_index} = "
            f"step_disposal_methods[{step_index}]"
        ),
        f"    existence_{step_index} = step_existences[{step_index}]",
        f"    target_kind_{step_index} = step_creations_target_kinds[{step_index}]",
        (
            f"    if target_kind_{step_index} in ("
            f"ExecutionPlanTargetKind.CALLER, ExecutionPlanTargetKind.SPELLSPACE):"
        ),
        "        if caller_creations is None:",
        "            raise RuntimeError(",
        "                \"Phase 13 CALLER/SPELLSPACE execution requires caller_creations.\"",
        "            )",
        f"        creations_{step_index} = caller_creations",
        f"    elif target_kind_{step_index} == ExecutionPlanTargetKind.OWNER:",
        f"        owner_creations_{step_index} = spell_{step_index}._owner_creations",
        f"        if owner_creations_{step_index} is not None:",
        f"            creations_{step_index} = owner_creations_{step_index}",
        "        elif owner_creations is None:",
        "            raise RuntimeError(",
        "                \"Phase 13 OWNER execution requires owner_creations.\"",
        "            )",
        "        else:",
        f"            creations_{step_index} = owner_creations",
        "    else:",
        (
            f"        raise RuntimeError("
            f"f\"Unsupported creations target kind '{{target_kind_{step_index}}}' "
            f"for spell '{{spell_{step_index}.spell_id}}'.\")"
        ),
        f"    override_targets_{step_index} = step_override_targets[{step_index}]",
        (
            f"    has_targeted_overrides_{step_index} = "
            f"step_has_targeted_overrides[{step_index}]"
        ),
        f"    is_root_step_{step_index} = step_is_root[{step_index}]",
        (
            f"    step_root_positional_override_{step_index} = "
            f"root_positional_override if is_root_step_{step_index} else None"
        ),
        f"    must_register_{step_index} = step_must_register_flags[{step_index}]",
        f"    if existence_{step_index} is Existence.many:",
        (
            f"        instance_{step_index} = _construct_spell_instance_with_overrides("
            f"plan_step=plan_step_{step_index}, "
            f"instance_results=instance_results, "
            f"override_targets=override_targets_{step_index}, "
            f"override_map=override_map, "
            f"root_positional_override=step_root_positional_override_{step_index})"
        ),
        f"        if must_register_{step_index}:",
        f"            with creations_{step_index}._lock:",
        (
            f"                _register_spell_instance_prebound("
            f"spell_id=spell_id_{step_index}, "
            f"instance=instance_{step_index}, "
            f"creations=creations_{step_index}, "
            f"existence=existence_{step_index}, "
            f"has_disposal_methods=has_disposal_methods_{step_index}, "
            f"disposal_methods=disposal_methods_{step_index})"
        ),
        (
            f"    elif existence_{step_index} in ("
            f"Existence.unique_per_conduit, Existence.unique_per_spell_space):"
        ),
        (
            f"        instance_{step_index} = _get_existing_creation("
            f"spell=spell_{step_index}, "
            f"creations=creations_{step_index}, "
            f"existence=existence_{step_index})"
        ),
        f"        if instance_{step_index} is not None:",
        (
            f"            _raise_override_on_existing_instance("
            f"spell=spell_{step_index}, "
            f"has_targeted_overrides=has_targeted_overrides_{step_index}, "
            f"any_overrides_present=any_overrides_present, "
            f"root_spell_id=root_spell_id)"
        ),
        "        else:",
        f"            with creations_{step_index}._lock:",
        (
            f"                instance_{step_index} = _get_existing_creation("
            f"spell=spell_{step_index}, "
            f"creations=creations_{step_index}, "
            f"existence=existence_{step_index})"
        ),
        f"                if instance_{step_index} is not None:",
        (
            f"                    _raise_override_on_existing_instance("
            f"spell=spell_{step_index}, "
            f"has_targeted_overrides=has_targeted_overrides_{step_index}, "
            f"any_overrides_present=any_overrides_present, "
            f"root_spell_id=root_spell_id)"
        ),
        "                else:",
        (
                    f"                    instance_{step_index} = _construct_spell_instance_with_overrides("
                    f"plan_step=plan_step_{step_index}, "
                    f"instance_results=instance_results, "
                    f"override_targets=override_targets_{step_index}, "
                    f"override_map=override_map, "
                    f"root_positional_override=step_root_positional_override_{step_index})"
        ),
        (
            f"                    _register_spell_instance_prebound("
            f"spell_id=spell_id_{step_index}, "
            f"instance=instance_{step_index}, "
            f"creations=creations_{step_index}, "
            f"existence=existence_{step_index}, "
            f"has_disposal_methods=has_disposal_methods_{step_index}, "
            f"disposal_methods=disposal_methods_{step_index})"
        ),
        "    else:",
        f"        use_spell_lock_{step_index} = step_use_spell_lock_hints[{step_index}]",
        "        if (",
        f"                use_spell_lock_{step_index}",
        "                and caller_creations_lock_held",
        f"                and creations_{step_index} is caller_creations",
        "        ):",
        f"            use_spell_lock_{step_index} = False",
        f"        if use_spell_lock_{step_index}:",
        f"            with spell_{step_index}._lock:",
        f"                with creations_{step_index}._lock:",
        (
            f"                    instance_{step_index} = _get_existing_creation("
            f"spell=spell_{step_index}, "
            f"creations=creations_{step_index}, "
            f"existence=existence_{step_index})"
        ),
        f"                if instance_{step_index} is not None:",
        (
            f"                    _raise_override_on_existing_instance("
            f"spell=spell_{step_index}, "
            f"has_targeted_overrides=has_targeted_overrides_{step_index}, "
            f"any_overrides_present=any_overrides_present, "
            f"root_spell_id=root_spell_id)"
        ),
        "                else:",
        (
                    f"                    instance_{step_index} = _construct_spell_instance_with_overrides("
                    f"plan_step=plan_step_{step_index}, "
                    f"instance_results=instance_results, "
                    f"override_targets=override_targets_{step_index}, "
                    f"override_map=override_map, "
                    f"root_positional_override=step_root_positional_override_{step_index})"
        ),
        f"                    with creations_{step_index}._lock:",
            (
                f"                        _register_spell_instance_prebound("
                f"spell_id=spell_id_{step_index}, "
                f"instance=instance_{step_index}, "
                f"creations=creations_{step_index}, "
                f"existence=existence_{step_index}, "
                f"has_disposal_methods=has_disposal_methods_{step_index}, "
                f"disposal_methods=disposal_methods_{step_index})"
            ),
        "        else:",
        f"            with creations_{step_index}._lock:",
        (
            f"                instance_{step_index} = _get_existing_creation("
            f"spell=spell_{step_index}, "
            f"creations=creations_{step_index}, "
            f"existence=existence_{step_index})"
        ),
        f"                if instance_{step_index} is not None:",
        (
            f"                    _raise_override_on_existing_instance("
            f"spell=spell_{step_index}, "
            f"has_targeted_overrides=has_targeted_overrides_{step_index}, "
            f"any_overrides_present=any_overrides_present, "
            f"root_spell_id=root_spell_id)"
        ),
        "                else:",
        (
                    f"                    instance_{step_index} = _construct_spell_instance_with_overrides("
                    f"plan_step=plan_step_{step_index}, "
                    f"instance_results=instance_results, "
                    f"override_targets=override_targets_{step_index}, "
                    f"override_map=override_map, "
                    f"root_positional_override=step_root_positional_override_{step_index})"
        ),
            (
                f"                    _register_spell_instance_prebound("
                f"spell_id=spell_id_{step_index}, "
                f"instance=instance_{step_index}, "
                f"creations=creations_{step_index}, "
                f"existence=existence_{step_index}, "
                f"has_disposal_methods=has_disposal_methods_{step_index}, "
                f"disposal_methods=disposal_methods_{step_index})"
            ),
        f"    instance_results[step_instance_keys[{step_index}]] = instance_{step_index}",
    ])


def _hydrate_steps_from_rows(
        *,
        plan_rows: Sequence[Dict[str, Any]],
        spell_lookup: Optional[Dict[str, Any]],
) -> Tuple[Any, ...]:
    """
    Hydrate override executor plan steps from schema-only Phase11 step rows.

    Contract:
        - Requires spell_lookup to resolve spell runtime objects.
        - Validates required row fields and existence enum names.
    """
    if spell_lookup is None:
        raise RuntimeError(
            "Phase 13 overrides schema rows require spell_lookup for step hydration."
        )

    steps = []
    for row_index, row in enumerate(plan_rows):
        required_fields = (
            "instance_key",
            "spell_id",
            "existence",
            "creations_target_kind",
            "shared_instance",
            "dependency_resolution_order",
            "override_match_prefix",
            "override_match_prefix_len",
            "uses_positional_override",
            "contract_positional_override",
            "has_contract_payload",
            "contract_payload_items",
            "use_spell_lock_hint",
            "must_register",
        )
        for field_name in required_fields:
            if field_name not in row:
                raise RuntimeError(
                    "Phase 13 overrides step schema is missing required field "
                    f"'{field_name}' at index {row_index}."
                )

        spell_id = row["spell_id"]
        spell = spell_lookup.get(spell_id)
        if spell is None:
            raise RuntimeError(
                f"Phase 13 overrides step schema references unknown spell_id '{spell_id}'."
            )

        existence_name = row["existence"]
        try:
            existence = Existence[existence_name]
        except KeyError as exc:
            raise RuntimeError(
                "Phase 13 overrides step schema contains unknown existence "
                f"'{existence_name}' at index {row_index}."
            ) from exc

        dependency_resolution_order = tuple(
            (
                param_name,
                tuple(dependency_keys),
            )
            for param_name, dependency_keys in row["dependency_resolution_order"]
        )
        has_contract_payload = bool(row["has_contract_payload"])
        contract_payload = None
        if has_contract_payload:
            contract_payload = {
                param_name: value
                for param_name, value in row["contract_payload_items"]
            }

        steps.append(
            SimpleNamespace(
                instance_key=tuple(row["instance_key"]),
                spell=spell,
                existence=existence,
                creations_target_kind=row["creations_target_kind"],
                shared_instance=row["shared_instance"],
                dependency_resolution_order=dependency_resolution_order,
                override_match_prefix=row["override_match_prefix"],
                override_match_prefix_len=row["override_match_prefix_len"],
                uses_positional_override=row["uses_positional_override"],
                contract_positional_override=row["contract_positional_override"],
                has_contract_payload=has_contract_payload,
                contract_payload=contract_payload,
                use_spell_lock_hint=row["use_spell_lock_hint"],
                must_register=row["must_register"],
            )
        )
    return tuple(steps)


def _resolve_root_instance_key(
        *,
        steps: Tuple[Any, ...],
        root_spell_id: Optional[str],
) -> Optional[Tuple[str, Optional[int]]]:
    """
    Resolve root instance key from hydrated schema steps.

    Contract:
        - Prefers canonical `(root_spell_id, None)` when present.
        - Falls back to first matching step instance key.
        - Returns None when no match exists.
    """
    if root_spell_id is None:
        return None
    for plan_step in steps:
        instance_key: Tuple[str, Optional[int]] = plan_step.instance_key
        if instance_key[0] == root_spell_id and instance_key[1] is None:
            return instance_key
    for plan_step in steps:
        fallback_instance_key: Tuple[str, Optional[int]] = plan_step.instance_key
        if fallback_instance_key[0] == root_spell_id:
            return fallback_instance_key
    return None


def _build_step_override_targets(
        *,
        steps: Tuple[Any, ...],
        override_targets_by_spell_id: Dict[str, Tuple[Any, ...]],
        path_registry: Optional[Any],
        prefilter_step_targets_cache: Optional[Dict[Tuple[Any, ...], Tuple[Tuple[Any, ...], ...]]] = None,
        prefilter_cache_key: Optional[Tuple[Any, ...]] = None,
        prefilter_path_metadata_cache: Optional[Dict[Any, Tuple[Any, Any]]] = None,
) -> Tuple[Tuple[Any, ...], ...]:
    """
    Build per-step override target tuples from spell-id grouped targets.

    Contract:
        - Preserves deterministic target order provided by the caller.
        - Returns empty tuples for steps with no targeted sockets.
        - Pre-filters non-shared step targets at compile time.
        - Supports external cache injection for step-target tuples and socket path
          metadata to reduce repeated prefilter work across compiles.
    """
    if (
            prefilter_step_targets_cache is not None
            and prefilter_cache_key is not None
    ):
        cached_step_targets = prefilter_step_targets_cache.get(prefilter_cache_key)
        if cached_step_targets is not None:
            return cached_step_targets

    path_metadata_cache = prefilter_path_metadata_cache
    if path_metadata_cache is None:
        path_metadata_cache = {}
    resolved_path_registry = path_registry

    def _resolve_socket_path_metadata(socket_ref: Any) -> Tuple[Any, Any]:
        """
        Resolve and memoize parent-path metadata for one socket reference.

        Contract:
            - Caches `(parent_id, depth)` by socket object identity.
            - Uses the supplied `path_registry` as the source of truth.
        """
        metadata = path_metadata_cache.get(socket_ref)
        if metadata is not None:
            return metadata
        if resolved_path_registry is None:
            raise RuntimeError(
                "path_registry must not be None when resolving override socket metadata."
            )
        metadata = (
            resolved_path_registry.parent_id(socket_ref.param_path_id),
            resolved_path_registry.depth(socket_ref.param_path_id),
        )
        path_metadata_cache[socket_ref] = metadata
        return metadata

    step_targets = []
    for plan_step in steps:
        spell_id = plan_step.spell.spell_index.current
        spell_targets = override_targets_by_spell_id.get(spell_id, ())
        if not spell_targets:
            step_targets.append(())
            continue

        if plan_step.shared_instance:
            step_targets.append(spell_targets)
            continue

        match_prefix = plan_step.override_match_prefix
        if match_prefix is None or path_registry is None:
            step_targets.append(())
            continue
        match_depth = plan_step.override_match_prefix_len + 1
        filtered_targets = []
        for socket_ref in spell_targets:
            parent_id, depth = _resolve_socket_path_metadata(socket_ref)
            if parent_id == match_prefix and depth == match_depth:
                filtered_targets.append(socket_ref)
        step_targets.append(tuple(filtered_targets))
    built_step_targets = tuple(step_targets)
    if (
            prefilter_step_targets_cache is not None
            and prefilter_cache_key is not None
    ):
        prefilter_step_targets_cache[prefilter_cache_key] = built_step_targets
    return built_step_targets

def _raise_override_on_existing_instance(
        *,
        spell: Any,
        has_targeted_overrides: bool,
        any_overrides_present: bool,
        root_spell_id: str,
) -> None:
    """
    Raise when overrides target an already-existing reusable instance.

    Contract:
        - Root-level override payloads block root-instance reuse.
        - Socket-targeted overrides block reuse for the targeted spell.
    """
    spell_id = spell.spell_index.current
    if spell_id == root_spell_id and any_overrides_present:
        raise MeldExecutionError(
            spell_id=spell_id,
            spell_name=spell.spell_name,
            node_id=spell_id,
            message=(
                "Overrides were supplied for a root spell that already exists. "
                "Shared instances cannot be overridden after creation."
            ),
        )
    if has_targeted_overrides:
        raise MeldExecutionError(
            spell_id=spell_id,
            spell_name=spell.spell_name,
            node_id=spell_id,
            message=(
                "Overrides were supplied for a spell instance that already exists. "
                "Shared instances cannot be overridden after creation."
            ),
        )


def _construct_spell_instance_with_overrides(
        *,
        plan_step: Any,
        instance_results: Dict[Tuple[str, Optional[int]], Any],
        override_targets: Tuple[Any, ...],
        override_map: Dict[Any, Any],
        root_positional_override: Optional[Sequence[Any]],
) -> Any:
    """
    Construct one step instance with override-aware kwargs materialization.

    Contract:
        - Dependency values are read from prior step results.
        - `override_targets` is already shape-filtered for this step.
        - Override values supersede dependency and contract payload values.
        - ``root_positional_override`` is applied as ``"__args__"`` for root steps.
        - Skips override-value helper dispatch when no step-target or root-arg
          overrides are present.
    """
    if not override_targets and root_positional_override is None:
        override_values = _EMPTY_OVERRIDE_VALUES
    else:
        override_values = _build_step_override_values(
            override_targets=override_targets,
            override_map=override_map,
            root_positional_override=root_positional_override,
        )
    kwargs = _build_kwargs_with_overrides(
        plan_step=plan_step,
        instance_results=instance_results,
        override_values=override_values,
    )
    return _invoke_spell_with_kwargs(
        spell=plan_step.spell,
        kwargs=kwargs,
    )


def _build_step_override_values(
        *,
        override_targets: Tuple[Any, ...],
        override_map: Dict[Any, Any],
        root_positional_override: Optional[Sequence[Any]],
) -> Dict[str, Any]:
    """
    Build per-step override payload values with an empty-target fast path.

    Contract:
        - Returns an empty mapping when no step targets and no positional payload.
        - Returns only ``"__args__"`` when root positional payload is supplied
          with no targeted socket overrides.
        - Uses direct single-target mapping when exactly one socket is targeted.
        - Uses direct two-target mapping when exactly two sockets are targeted.
        - Preserves targeted socket override resolution order.
    """
    if not override_targets:
        if root_positional_override is None:
            return {}
        return {
            "__args__": root_positional_override,
        }
    if len(override_targets) == 1:
        socket_ref = override_targets[0]
        if root_positional_override is None:
            return {
                socket_ref.param_name: override_map[socket_ref],
            }
        return {
            socket_ref.param_name: override_map[socket_ref],
            "__args__": root_positional_override,
        }
    if len(override_targets) == 2:
        first_socket_ref = override_targets[0]
        second_socket_ref = override_targets[1]
        override_values = {
            first_socket_ref.param_name: override_map[first_socket_ref],
        }
        override_values[second_socket_ref.param_name] = override_map[second_socket_ref]
        if root_positional_override is not None:
            override_values["__args__"] = root_positional_override
        return override_values

    override_values = _build_instance_override_map(
        override_targets=override_targets,
        override_map=override_map,
    )
    if root_positional_override is not None:
        override_values["__args__"] = root_positional_override
    return override_values


def _build_instance_override_map(
        *,
        override_targets: Tuple[Any, ...],
        override_map: Dict[Any, Any],
) -> Dict[str, Any]:
    """
    Resolve override values that apply to the current plan step instance.

    Contract:
        - Expects `override_targets` to be pre-filtered for the target step.
        - Materializes a parameter-value map in deterministic target order.
    """
    if not override_targets:
        return {}

    values: Dict[str, Any] = {}
    for socket_ref in override_targets:
        values[socket_ref.param_name] = override_map[socket_ref]
    return values


def _build_kwargs_with_overrides(
        *,
        plan_step: Any,
        instance_results: Dict[Tuple[str, Optional[int]], Any],
        override_values: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build call kwargs for one step using dependency, contract, and override values.

    Contract:
        - Override values take precedence over dependency and contract payloads.
        - Missing dependency instance keys raise MeldExecutionError.
    """
    dependency_resolution_order = plan_step.dependency_resolution_order
    contract_positional_override = plan_step.contract_positional_override
    if (
            not dependency_resolution_order
            and contract_positional_override is None
            and not plan_step.has_contract_payload
    ):
        return dict(override_values) if override_values else {}
    if (
            not dependency_resolution_order
            and contract_positional_override is None
            and plan_step.has_contract_payload
            and not override_values
    ):
        contract_payload = plan_step.contract_payload
        if not contract_payload:
            return {}
        if not plan_step.uses_positional_override:
            return dict(contract_payload)
        contract_kwargs: Dict[str, Any] = {}
        for param_name, value in contract_payload.items():
            if param_name == "__args__":
                continue
            contract_kwargs[param_name] = value
        return contract_kwargs

    spell = plan_step.spell
    spell_id = spell.spell_index.current
    kwargs: Dict[str, Any] = {}

    for param_name, dependency_keys in dependency_resolution_order:
        if param_name in override_values:
            continue
        dependency_count = len(dependency_keys)
        if dependency_count == 0:
            continue
        if dependency_count == 1:
            dependency_key = dependency_keys[0]
            try:
                kwargs[param_name] = instance_results[dependency_key]
            except KeyError as exc:
                raise MeldExecutionError(
                    spell_id=spell_id,
                    spell_name=spell_id,
                    node_id=spell_id,
                    param_name=param_name,
                    message=(
                        f"Dependency '{dependency_key[0]}' missing while "
                        f"building args for '{spell_id}'."
                    ),
                ) from exc
            continue
        if dependency_count == 2:
            first_dependency_key = dependency_keys[0]
            second_dependency_key = dependency_keys[1]
            try:
                first_value = instance_results[first_dependency_key]
            except KeyError as exc:
                raise MeldExecutionError(
                    spell_id=spell_id,
                    spell_name=spell_id,
                    node_id=spell_id,
                    param_name=param_name,
                    message=(
                        f"Dependency '{first_dependency_key[0]}' missing while "
                        f"building args for '{spell_id}'."
                    ),
                ) from exc
            try:
                second_value = instance_results[second_dependency_key]
            except KeyError as exc:
                raise MeldExecutionError(
                    spell_id=spell_id,
                    spell_name=spell_id,
                    node_id=spell_id,
                    param_name=param_name,
                    message=(
                        f"Dependency '{second_dependency_key[0]}' missing while "
                        f"building args for '{spell_id}'."
                    ),
                ) from exc
            kwargs[param_name] = [
                first_value,
                second_value,
            ]
            continue

        values = []
        for dependency_key in dependency_keys:
            try:
                values.append(instance_results[dependency_key])
            except KeyError as exc:
                raise MeldExecutionError(
                    spell_id=spell_id,
                    spell_name=spell_id,
                    node_id=spell_id,
                    param_name=param_name,
                    message=(
                        f"Dependency '{dependency_key[0]}' missing while "
                        f"building args for '{spell_id}'."
                    ),
                ) from exc
        if not values:
            continue
        if len(values) == 1:
            kwargs[param_name] = values[0]
        else:
            kwargs[param_name] = values

    if contract_positional_override is not None:
        kwargs["__args__"] = contract_positional_override

    if plan_step.has_contract_payload:
        contract_payload = plan_step.contract_payload
        if contract_payload:
            for param_name, value in contract_payload.items():
                if param_name == "__args__" and plan_step.uses_positional_override:
                    continue
                if param_name in override_values:
                    continue
                kwargs[param_name] = value

    if override_values:
        kwargs.update(override_values)
    return kwargs


def _invoke_spell_with_kwargs(
        *,
        spell: Any,
        kwargs: Dict[str, Any],
) -> Any:
    """
    Invoke one spell callable using override-aware kwargs payload.

    Contract:
        - Existing-creation singleton spells return user_created_object.
        - Non-callable spells return spell.spell directly.
        - ``"__args__"`` must be a list/tuple when supplied.
        - Avoids kwargs copy when positional override args are absent.
        - Preserves tuple positional payloads without rebuilding list objects.
    """
    if spell.existence is Existence.unique and spell.is_existing_creation:
        instance = spell.user_created_object
        if instance is None:
            raise RuntimeError(
                "[MELD] EXISTING_CREATION spell has no `user_created_object` "
                f"(spell_id={spell.spell_id})."
            )
        return instance

    if not (spell.is_class_spell or spell.is_method_spell or spell.is_lambda_spell):
        return spell.spell

    raw_args = kwargs.get("__args__", _MISSING)
    if raw_args is _MISSING:
        args: Sequence[Any] = []
        call_kwargs = kwargs
    elif isinstance(raw_args, tuple):
        args = raw_args
        if len(kwargs) == 1:
            call_kwargs = {}
        else:
            call_kwargs = dict(kwargs)
            call_kwargs.pop("__args__", None)
    elif isinstance(raw_args, list):
        args = raw_args
        if len(kwargs) == 1:
            call_kwargs = {}
        else:
            call_kwargs = dict(kwargs)
            call_kwargs.pop("__args__", None)
    else:
        raise MeldExecutionError(
            spell_id=spell.spell_index.current,
            spell_name=spell.spell_name,
            message="__args__ override must be a list or tuple.",
        )

    try:
        return spell.spell(*args, **call_kwargs)
    except Exception as exc:
        raise MeldExecutionError(
            spell_id=spell.spell_index.current,
            spell_name=spell.spell_name,
            message=f"Error invoking spell '{spell.spell_name}'.",
            inner=exc,
        ) from exc

