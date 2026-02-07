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
        execution_plan: Any,
        override_targets_by_spell_id: Dict[str, Tuple[Any, ...]],
        any_overrides_present: bool,
        path_registry: Optional[Any],
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

    Returns:
        Callable[[Any, Dict[Any, Any], Optional[Sequence[Any]]], Any]:
            Executor receiving `(context, override_map, root_positional_override)`.

    Raises:
        ValueError:
            If required inputs are missing.
        RuntimeError:
            If the execution plan has no root instance key.
    """
    if execution_plan is None:
        raise ValueError("execution_plan must not be None.")
    if override_targets_by_spell_id is None:
        raise ValueError("override_targets_by_spell_id must not be None.")

    root_instance_key = execution_plan.root_instance_key
    if root_instance_key is None:
        raise RuntimeError("Phase 12 override executor requires a root instance key.")

    steps = tuple(execution_plan.steps)
    step_override_targets = _build_step_override_targets(
        steps=steps,
        override_targets_by_spell_id=override_targets_by_spell_id,
    )
    root_spell_id = execution_plan.root_spell_id

    def _phase12_executor(
            context: Any,
            override_map: Dict[Any, Any],
            root_positional_override: Optional[Sequence[Any]],
    ) -> Any:
        instance_results: Dict[Tuple[str, Optional[int]], Any] = {}
        for index, plan_step in enumerate(steps):
            instance = _resolve_step_instance_with_overrides(
                context=context,
                plan_step=plan_step,
                instance_results=instance_results,
                override_targets=step_override_targets[index],
                override_map=override_map,
                any_overrides_present=any_overrides_present,
                root_spell_id=root_spell_id,
                path_registry=path_registry,
                root_positional_override=root_positional_override,
            )
            instance_results[plan_step.instance_key] = instance
        if root_instance_key not in instance_results:
            raise MeldExecutionError(
                spell_id=root_instance_key[0],
                spell_name=root_instance_key[0],
                message=(
                    "Phase 12 override executor did not produce the root "
                    f"instance '{root_instance_key[0]}'."
                ),
            )
        return instance_results[root_instance_key]

    return _phase12_executor


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
