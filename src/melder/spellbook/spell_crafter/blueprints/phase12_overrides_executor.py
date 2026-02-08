from types import SimpleNamespace
from typing import Any, Callable, Dict, Optional, Sequence, Tuple

from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.blueprints.phase12_no_overrides_executor import (
    _get_existing_creation,
    _register_spell_instance,
    _select_creations_for_target_kind,
)
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError


def compile_phase12_overrides_executor(
        *,
        execution_plan: Optional[Any],
        override_targets_by_spell_id: Dict[str, Tuple[Any, ...]],
        any_overrides_present: bool,
        path_registry: Optional[Any],
        plan_rows: Optional[Sequence[Dict[str, Any]]] = None,
        root_spell_id: Optional[str] = None,
        spell_lookup: Optional[Dict[str, Any]] = None,
) -> Callable[[Any, Dict[Any, Any], Optional[Sequence[Any]]], Any]:
    """
    Compile a spell-scoped Phase 12 overrides executor specialization.

    Purpose:
        Build the runtime callable used for override-aware meld execution after
        Phase 11 planning, without relying on MeldEngine.

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
            Path registry from the active root blueprint, used for per-path
            socket filtering in non-shared instances.
        plan_rows:
            Optional schema-only step rows exported from Phase11 IR.
        root_spell_id:
            Optional root spell id for schema-row driven compilation.
        spell_lookup:
            Optional spell-id lookup used when hydrating schema rows.

    Returns:
        Callable[[Any, Dict[Any, Any], Optional[Sequence[Any]]], Any]:
            Executor receiving `(context, override_map, root_positional_override)`.

    Raises:
        ValueError:
            If required inputs are missing.
        RuntimeError:
            If the execution plan has no root instance key.
    """
    compiled_executor, _ = _compile_phase12_overrides_executor_core(
        source=None,
        execution_plan=execution_plan,
        override_targets_by_spell_id=override_targets_by_spell_id,
        any_overrides_present=any_overrides_present,
        path_registry=path_registry,
        plan_rows=plan_rows,
        root_spell_id=root_spell_id,
        spell_lookup=spell_lookup,
    )
    return compiled_executor


def compile_phase12_overrides_executor_from_source(
        *,
        source: str,
        execution_plan: Optional[Any],
        override_targets_by_spell_id: Dict[str, Tuple[Any, ...]],
        any_overrides_present: bool,
        path_registry: Optional[Any],
        plan_rows: Optional[Sequence[Dict[str, Any]]] = None,
        root_spell_id: Optional[str] = None,
        spell_lookup: Optional[Dict[str, Any]] = None,
) -> Callable[[Any, Dict[Any, Any], Optional[Sequence[Any]]], Any]:
    """
    Compile a specialization executor from previously emitted source.

    Contract:
        - Reuses the same schema/plan validation as fresh compilation.
        - Uses the supplied source verbatim for code object compilation.
    """
    compiled_executor, _ = _compile_phase12_overrides_executor_core(
        source=source,
        execution_plan=execution_plan,
        override_targets_by_spell_id=override_targets_by_spell_id,
        any_overrides_present=any_overrides_present,
        path_registry=path_registry,
        plan_rows=plan_rows,
        root_spell_id=root_spell_id,
        spell_lookup=spell_lookup,
    )
    return compiled_executor


def emit_phase12_overrides_executor_source(
        *,
        step_count: int,
) -> str:
    """
    Emit generated Phase12 override specialization source for a step count.

    Contract:
        - Source is deterministic for the same `step_count`.
        - Raises when step_count is invalid.
    """
    return _build_phase12_overrides_executor_source(
        step_count=step_count,
    )


def _compile_phase12_overrides_executor_core(
        *,
        source: Optional[str],
        execution_plan: Optional[Any],
        override_targets_by_spell_id: Dict[str, Tuple[Any, ...]],
        any_overrides_present: bool,
        path_registry: Optional[Any],
        plan_rows: Optional[Sequence[Dict[str, Any]]],
        root_spell_id: Optional[str],
        spell_lookup: Optional[Dict[str, Any]],
) -> Tuple[Callable[[Any, Dict[Any, Any], Optional[Sequence[Any]]], Any], str]:
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
            raise RuntimeError("Phase 12 override executor requires a root instance key.")
        root_spell_id = resolved_root_spell_id
    else:
        root_instance_key = execution_plan.root_instance_key
        if root_instance_key is None:
            raise RuntimeError("Phase 12 override executor requires a root instance key.")
        steps = tuple(execution_plan.steps)
        root_spell_id = execution_plan.root_spell_id

    step_override_targets = _build_step_override_targets(
        steps=steps,
        override_targets_by_spell_id=override_targets_by_spell_id,
    )

    source_to_compile = source
    if source_to_compile is None:
        source_to_compile = emit_phase12_overrides_executor_source(
            step_count=len(steps),
        )
    elif not isinstance(source_to_compile, str) or not source_to_compile:
        raise ValueError("source must be a non-empty string.")

    namespace = _build_phase12_overrides_executor_namespace(
        steps=steps,
        step_override_targets=step_override_targets,
        root_instance_key=root_instance_key,
        root_spell_id=root_spell_id,
        path_registry=path_registry,
        any_overrides_present=any_overrides_present,
    )
    local_namespace: Dict[str, Any] = {}
    try:
        exec(
            compile(source_to_compile, "<melder_phase12_overrides_executor>", "exec"),
            namespace,
            local_namespace,
        )
    except Exception as exc:
        raise RuntimeError(
            "Phase 12 overrides executor code generation failed."
        ) from exc

    compiled_executor = local_namespace.get("_phase12_executor")
    if callable(compiled_executor):
        return compiled_executor, source_to_compile
    raise RuntimeError(
        "Phase 12 overrides executor source did not define a callable _phase12_executor."
    )


def _build_phase12_overrides_executor_namespace(
        *,
        steps: Tuple[Any, ...],
        step_override_targets: Tuple[Tuple[Any, ...], ...],
        root_instance_key: Tuple[str, Optional[int]],
        root_spell_id: Optional[str],
        path_registry: Optional[Any],
        any_overrides_present: bool,
) -> Dict[str, Any]:
    """
    Build namespace values for generated override specialization source.

    Contract:
        - Captures immutable specialization constants as function defaults.
        - Exposes helper callables required by generated executor source.
    """
    return {
        "MeldExecutionError": MeldExecutionError,
        "_resolve_step_instance_with_overrides": _resolve_step_instance_with_overrides,
        "steps": steps,
        "step_override_targets": step_override_targets,
        "root_instance_key": root_instance_key,
        "root_spell_id": root_spell_id,
        "path_registry": path_registry,
        "any_overrides_present": any_overrides_present,
    }


def _build_phase12_overrides_executor_source(
        *,
        step_count: int,
) -> str:
    """
    Build generated Python source for override specialization execution.

    Contract:
        - Emits one direct step-resolution statement per Phase11 step.
        - Uses prebound defaults for specialization constants.
        - Preserves root-result verification semantics.
    """
    if step_count < 0:
        raise ValueError("step_count must not be negative.")

    lines = [
        "def _phase12_executor(",
        "        context,",
        "        override_map,",
        "        root_positional_override,",
        "        *,",
        "        steps=steps,",
        "        step_override_targets=step_override_targets,",
        "        root_instance_key=root_instance_key,",
        "        root_spell_id=root_spell_id,",
        "        path_registry=path_registry,",
        "        any_overrides_present=any_overrides_present,",
        "        _resolve_step_instance_with_overrides=_resolve_step_instance_with_overrides,",
        "        MeldExecutionError=MeldExecutionError,",
        "    ):",
        "    instance_results = {}",
    ]

    for index in range(step_count):
        lines.append(f"    plan_step_{index} = steps[{index}]")
        lines.append(
            f"    instance_{index} = _resolve_step_instance_with_overrides("
            f"context=context, "
            f"plan_step=plan_step_{index}, "
            f"instance_results=instance_results, "
            f"override_targets=step_override_targets[{index}], "
            f"override_map=override_map, "
            f"any_overrides_present=any_overrides_present, "
            f"root_spell_id=root_spell_id, "
            f"path_registry=path_registry, "
            f"root_positional_override=root_positional_override)"
        )
        lines.append(f"    instance_results[plan_step_{index}.instance_key] = instance_{index}")

    lines.extend([
        "    if root_instance_key not in instance_results:",
        "        raise MeldExecutionError(",
        "            spell_id=root_instance_key[0],",
        "            spell_name=root_instance_key[0],",
        "            message=(",
        "                \"Phase 12 override executor did not produce the root \"",
        "                f\"instance '{root_instance_key[0]}'.\"",
        "            ),",
        "        )",
        "    return instance_results[root_instance_key]",
    ])
    return "\n".join(lines)


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
            "Phase 12 overrides schema rows require spell_lookup for step hydration."
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
                    "Phase 12 overrides step schema is missing required field "
                    f"'{field_name}' at index {row_index}."
                )

        spell_id = row["spell_id"]
        spell = spell_lookup.get(spell_id)
        if spell is None:
            raise RuntimeError(
                f"Phase 12 overrides step schema references unknown spell_id '{spell_id}'."
            )

        existence_name = row["existence"]
        try:
            existence = Existence[existence_name]
        except KeyError as exc:
            raise RuntimeError(
                "Phase 12 overrides step schema contains unknown existence "
                f"'{existence_name}' at index {row_index}."
            ) from exc

        dependency_resolution_order = tuple(
            (
                param_name,
                tuple(dependency_keys),
            )
            for param_name, dependency_keys in row["dependency_resolution_order"]
        )
        contract_payload = None
        if row["has_contract_payload"]:
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
                has_contract_payload=row["has_contract_payload"],
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
        instance_key = plan_step.instance_key
        if instance_key[0] == root_spell_id and instance_key[1] is None:
            return instance_key
    for plan_step in steps:
        instance_key = plan_step.instance_key
        if instance_key[0] == root_spell_id:
            return instance_key
    return None


def _build_step_override_targets(
        *,
        steps: Tuple[Any, ...],
        override_targets_by_spell_id: Dict[str, Tuple[Any, ...]],
) -> Tuple[Tuple[Any, ...], ...]:
    """
    Build per-step override target tuples from spell-id grouped targets.

    Contract:
        - Preserves deterministic target order provided by the caller.
        - Returns empty tuples for steps with no targeted sockets.
    """
    step_targets = []
    for plan_step in steps:
        spell_id = plan_step.spell.spell_index.current
        step_targets.append(override_targets_by_spell_id.get(spell_id, ()))
    return tuple(step_targets)


def _resolve_step_instance_with_overrides(
        *,
        context: Any,
        plan_step: Any,
        instance_results: Dict[Tuple[str, Optional[int]], Any],
        override_targets: Tuple[Any, ...],
        override_map: Dict[Any, Any],
        any_overrides_present: bool,
        root_spell_id: str,
        path_registry: Optional[Any],
        root_positional_override: Optional[Sequence[Any]],
) -> Any:
    """
    Resolve one step using override-aware creation, reuse, and registration rules.

    Contract:
        - Existence.many always constructs and never raises reuse override errors.
        - Non-`many` existences raise when an existing instance is reused while
          overrides target the instance (or root overrides target the root spell).
        - Lock ordering follows Phase 11 lock hints.
    """
    spell = plan_step.spell
    existence = plan_step.existence
    creations = _select_creations_for_target_kind(
        context=context,
        plan_step=plan_step,
        spell=spell,
    )
    has_targeted_overrides = bool(override_targets)
    is_root_step = spell.spell_index.current == root_spell_id

    def _construct() -> Any:
        return _construct_spell_instance_with_overrides(
            plan_step=plan_step,
            instance_results=instance_results,
            override_targets=override_targets,
            override_map=override_map,
            path_registry=path_registry,
            root_positional_override=root_positional_override if is_root_step else None,
        )

    if existence is Existence.many:
        instance = _construct()
        if plan_step.must_register:
            with creations._lock:
                _register_spell_instance(
                    spell=spell,
                    instance=instance,
                    creations=creations,
                    existence=existence,
                )
        return instance

    if existence in (
            Existence.unique_per_conduit,
            Existence.unique_per_spell_space,
    ):
        with creations._lock:
            instance = _get_existing_creation(
                spell=spell,
                creations=creations,
                existence=existence,
            )
            if instance is not None:
                _raise_override_on_existing_instance(
                    spell=spell,
                    has_targeted_overrides=has_targeted_overrides,
                    any_overrides_present=any_overrides_present,
                    root_spell_id=root_spell_id,
                )
                return instance
            instance = _construct()
            _register_spell_instance(
                spell=spell,
                instance=instance,
                creations=creations,
                existence=existence,
            )
            return instance

    use_spell_lock = plan_step.use_spell_lock_hint
    if (
            use_spell_lock
            and context is not None
            and context.caller_creations_lock_held
            and creations is context.caller_creations
    ):
        use_spell_lock = False

    if use_spell_lock:
        with spell._lock:
            with creations._lock:
                instance = _get_existing_creation(
                    spell=spell,
                    creations=creations,
                    existence=existence,
                )
            if instance is not None:
                _raise_override_on_existing_instance(
                    spell=spell,
                    has_targeted_overrides=has_targeted_overrides,
                    any_overrides_present=any_overrides_present,
                    root_spell_id=root_spell_id,
                )
                return instance
            instance = _construct()
            with creations._lock:
                _register_spell_instance(
                    spell=spell,
                    instance=instance,
                    creations=creations,
                    existence=existence,
                )
            return instance

    with creations._lock:
        instance = _get_existing_creation(
            spell=spell,
            creations=creations,
            existence=existence,
        )
        if instance is not None:
            _raise_override_on_existing_instance(
                spell=spell,
                has_targeted_overrides=has_targeted_overrides,
                any_overrides_present=any_overrides_present,
                root_spell_id=root_spell_id,
            )
            return instance
        instance = _construct()
        _register_spell_instance(
            spell=spell,
            instance=instance,
            creations=creations,
            existence=existence,
        )
        return instance


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
        path_registry: Optional[Any],
        root_positional_override: Optional[Sequence[Any]],
) -> Any:
    """
    Construct one step instance with override-aware kwargs materialization.

    Contract:
        - Dependency values are read from prior step results.
        - Override values supersede dependency and contract payload values.
        - ``root_positional_override`` is applied as ``"__args__"`` for root steps.
    """
    override_values = _build_instance_override_map(
        plan_step=plan_step,
        override_targets=override_targets,
        override_map=override_map,
        path_registry=path_registry,
    )
    if root_positional_override is not None:
        override_values["__args__"] = root_positional_override
    kwargs = _build_kwargs_with_overrides(
        plan_step=plan_step,
        instance_results=instance_results,
        override_values=override_values,
    )
    return _invoke_spell_with_kwargs(
        spell=plan_step.spell,
        kwargs=kwargs,
    )


def _build_instance_override_map(
        *,
        plan_step: Any,
        override_targets: Tuple[Any, ...],
        override_map: Dict[Any, Any],
        path_registry: Optional[Any],
) -> Dict[str, Any]:
    """
    Resolve override values that apply to the current plan step instance.

    Contract:
        - Shared instances accept all targeted socket values for the spell id.
        - Non-shared instances match socket path parent to the step prefix path.
    """
    if not override_targets:
        return {}

    shared = plan_step.shared_instance
    match_prefix = plan_step.override_match_prefix
    match_prefix_len = plan_step.override_match_prefix_len
    values: Dict[str, Any] = {}
    for socket_ref in override_targets:
        if socket_ref not in override_map:
            continue
        value = override_map[socket_ref]
        if shared:
            values[socket_ref.param_name] = value
            continue
        if match_prefix is None or path_registry is None:
            continue
        parent_id = path_registry.parent_id(socket_ref.param_path_id)
        if parent_id is None or parent_id != match_prefix:
            continue
        if path_registry.depth(socket_ref.param_path_id) != match_prefix_len + 1:
            continue
        values[socket_ref.param_name] = value
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
    spell = plan_step.spell
    spell_id = spell.spell_index.current
    kwargs: Dict[str, Any] = {}

    for param_name, dependency_keys in plan_step.dependency_resolution_order:
        if param_name in override_values:
            kwargs[param_name] = override_values[param_name]
            continue
        values = []
        for dependency_key in dependency_keys:
            if dependency_key not in instance_results:
                raise MeldExecutionError(
                    spell_id=spell_id,
                    spell_name=spell_id,
                    node_id=spell_id,
                    param_name=param_name,
                    message=(
                        f"Dependency '{dependency_key[0]}' missing while "
                        f"building args for '{spell_id}'."
                    ),
                )
            values.append(instance_results[dependency_key])
        if not values:
            continue
        if len(values) == 1:
            kwargs[param_name] = values[0]
        else:
            kwargs[param_name] = values

    if plan_step.contract_positional_override is not None:
        kwargs["__args__"] = plan_step.contract_positional_override

    if plan_step.has_contract_payload:
        contract_payload = plan_step.contract_payload
        if contract_payload:
            for param_name, value in contract_payload.items():
                if param_name == "__args__" and plan_step.uses_positional_override:
                    continue
                if param_name in override_values:
                    continue
                kwargs[param_name] = value

    for param_name, value in override_values.items():
        kwargs[param_name] = value
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

    call_kwargs = dict(kwargs)
    raw_args = call_kwargs.pop("__args__", [])
    if isinstance(raw_args, Sequence) and not isinstance(raw_args, (str, bytes)):
        args = list(raw_args)
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
