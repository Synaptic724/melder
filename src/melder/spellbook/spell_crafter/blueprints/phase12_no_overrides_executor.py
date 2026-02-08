from types import SimpleNamespace
from typing import Any, Callable, Dict, Optional, Sequence, Tuple

from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.blueprints.execution_plan import (
    ExecutionPlanCallMode,
    ExecutionPlanTargetKind,
)
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.utilities.custom_exceptions.spell_space_scope_error import SpellSpaceScopeError

_TRANSIENT_SCHEMA_SEQUENCE_FIELDS = (
    "call_modes",
    "dep1",
    "dep2a",
    "dep2b",
    "dep3a",
    "dep3b",
    "dep3c",
    "dep4a",
    "dep4b",
    "dep4c",
    "dep4d",
    "dep5a",
    "dep5b",
    "dep5c",
    "dep5d",
    "dep5e",
    "dep6a",
    "dep6b",
    "dep6c",
    "dep6d",
    "dep6e",
    "dep6f",
    "dep7a",
    "dep7b",
    "dep7c",
    "dep7d",
    "dep7e",
    "dep7f",
    "dep7g",
    "dep8a",
    "dep8b",
    "dep8c",
    "dep8d",
    "dep8e",
    "dep8f",
    "dep8g",
    "dep8h",
)


def compile_phase12_no_overrides_executor(
        *,
        codegen_ir: Dict[str, Any],
        spell_lookup: Optional[Dict[str, Any]] = None,
) -> Optional[Callable[[Any], Any]]:
    """
    Compile a spell-scoped Phase 12 no-overrides executor from Codegen IR.

    Purpose:
        Build the no-overrides execution callable consumed by MeldRuntime so
        meld no longer depends on legacy engine execution for no-overrides calls.

    Contract:
        - Returns a callable when the IR contains a no-overrides step plan.
        - Returns None when no steps are present for this variant.
        - Uses a transient unrolled executor when the IR carries a compatible
          transient-only schema.
        - Uses emitted step-plan source for all non-transient-compatible plans.
        - Does not use Python loop-based interpreter fallback executors.
        - Raises when transient codegen source compilation or namespace wiring
          fails for an otherwise compatible transient schema.

    Args:
        codegen_ir:
            Phase 11 variant payload produced by SpellCrafter IR export.
        spell_lookup:
            Optional spell-id lookup used to hydrate schema-only step rows.

    Returns:
        Optional[Callable[[Any], Any]]:
            Compiled executor receiving an optional MeldContext.

    Raises:
        ValueError:
            If codegen_ir is None.
        RuntimeError:
            If the root instance key cannot be resolved from the IR payload.
            If transient codegen source compilation or executor lookup fails.
    """
    if codegen_ir is None:
        raise ValueError("codegen_ir must not be None.")

    steps_rows = codegen_ir.get("steps_rows")
    steps = None
    if steps_rows:
        steps = _hydrate_steps_from_rows(
            steps_rows=steps_rows,
            spell_lookup=spell_lookup,
        )
    if not steps:
        return None
    root_spell_id = codegen_ir.get("root_spell_id")
    root_instance_key = _resolve_root_instance_key(
        steps=steps,
        root_spell_id=root_spell_id,
    )
    if root_instance_key is None:
        raise RuntimeError("Phase 12 IR is missing a resolvable root instance key.")

    transient_schema = codegen_ir.get("transient_schema")
    if transient_schema is not None and _supports_transient_unrolled_plan(steps):
        normalized_transient_schema = _normalize_transient_schema(
            transient_schema=transient_schema,
        )
        source = _build_phase12_executor_source(transient_schema=normalized_transient_schema)
        if source is not None:
            namespace = _build_executor_namespace(
                transient_schema=normalized_transient_schema,
                steps=steps,
            )
            return _compile_emitted_no_overrides_executor(
                source=source,
                namespace=namespace,
                source_name="<melder_phase12_no_overrides_transient_executor>",
                compile_failure_message=(
                    "Phase 12 no-overrides transient executor code generation failed."
                ),
            )

    step_source = _build_step_plan_executor_source(
        steps=steps,
    )
    step_namespace = _build_step_executor_namespace(
        steps=steps,
        root_instance_key=root_instance_key,
    )
    return _compile_emitted_no_overrides_executor(
        source=step_source,
        namespace=step_namespace,
        source_name="<melder_phase12_no_overrides_step_executor>",
        compile_failure_message=(
            "Phase 12 no-overrides executor code generation failed."
        ),
    )


def _hydrate_steps_from_rows(
        *,
        steps_rows: Sequence[Dict[str, Any]],
        spell_lookup: Optional[Dict[str, Any]],
) -> Tuple[Any, ...]:
    """
    Hydrate executable step adapters from schema-only Phase11 step rows.

    Contract:
        - Requires spell_lookup when schema rows are used.
        - Validates required row fields and existence enum names.
        - Returns adapters exposing the same attributes consumed by the no-
          overrides compiler/runtime helpers in this module.
    """
    if spell_lookup is None:
        raise RuntimeError(
            "Phase 12 no-overrides schema rows require spell_lookup for step hydration."
        )

    hydrated_steps = []
    for row_index, row in enumerate(steps_rows):
        required_fields = (
            "instance_key",
            "spell_id",
            "existence",
            "creations_target_kind",
            "dependency_resolution_order",
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
                    "Phase 12 no-overrides schema row is missing required field "
                    f"'{field_name}' at index {row_index}."
                )

        spell_id = row["spell_id"]
        spell = spell_lookup.get(spell_id)
        if spell is None:
            raise RuntimeError(
                f"Phase 12 no-overrides step schema references unknown spell_id '{spell_id}'."
            )

        existence_name = row["existence"]
        try:
            existence = Existence[existence_name]
        except KeyError as exc:
            raise RuntimeError(
                "Phase 12 no-overrides step schema contains unknown existence "
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

        hydrated_steps.append(
            SimpleNamespace(
                instance_key=tuple(row["instance_key"]),
                spell=spell,
                existence=existence,
                creations_target_kind=row["creations_target_kind"],
                dependency_resolution_order=dependency_resolution_order,
                uses_positional_override=row["uses_positional_override"],
                contract_positional_override=row["contract_positional_override"],
                has_contract_payload=row["has_contract_payload"],
                contract_payload=contract_payload,
                use_spell_lock_hint=row["use_spell_lock_hint"],
                must_register=row["must_register"],
            )
        )
    return tuple(hydrated_steps)


def _normalize_transient_schema(
        *,
        transient_schema: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Validate and normalize schema-only transient payload fields.

    Contract:
        - Requires `step_count`, `root_step_index`, and all transient arrays.
        - Enforces sequence lengths equal to `step_count`.
        - Returns tuples for all transient arrays to stabilize downstream access.
    """
    required_fields = ("step_count", "root_step_index") + _TRANSIENT_SCHEMA_SEQUENCE_FIELDS
    for field_name in required_fields:
        if field_name not in transient_schema:
            raise RuntimeError(
                "Phase 12 no-overrides transient schema is missing required "
                f"field '{field_name}'."
            )

    step_count = transient_schema["step_count"]
    if not isinstance(step_count, int) or step_count < 0:
        raise RuntimeError(
            "Phase 12 no-overrides transient schema 'step_count' must be a non-negative int."
        )

    root_step_index = transient_schema["root_step_index"]
    if not isinstance(root_step_index, int):
        raise RuntimeError(
            "Phase 12 no-overrides transient schema 'root_step_index' must be an int."
        )

    normalized = {
        "step_count": step_count,
        "root_step_index": root_step_index,
    }
    for field_name in _TRANSIENT_SCHEMA_SEQUENCE_FIELDS:
        value = transient_schema[field_name]
        if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
            raise RuntimeError(
                "Phase 12 no-overrides transient schema field "
                f"'{field_name}' must be a sequence."
            )
        values = tuple(value)
        if len(values) != step_count:
            raise RuntimeError(
                "Phase 12 no-overrides transient schema field "
                f"'{field_name}' length must equal step_count."
            )
        normalized[field_name] = values

    if step_count == 0:
        if root_step_index != 0:
            raise RuntimeError(
                "Phase 12 no-overrides transient schema with step_count 0 must use root_step_index 0."
            )
    elif root_step_index < 0 or root_step_index >= step_count:
        raise RuntimeError(
            "Phase 12 no-overrides transient schema root_step_index is out of range."
        )

    return normalized


def _resolve_root_instance_key(
        *,
        steps: Tuple[Any, ...],
        root_spell_id: Optional[str],
) -> Optional[Tuple[str, Optional[int]]]:
    """
    Resolve the root instance key from Phase 11 step metadata.

    Contract:
        - Prefers the canonical (spell_id, None) root key when present.
        - Falls back to the first step whose spell_id matches root_spell_id.
        - Returns None when no matching step exists.
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


def _supports_transient_unrolled_plan(steps: Tuple[Any, ...]) -> bool:
    """
    Decide whether the transient unrolled executor can be used safely.

    Contract:
        - Returns True only for plans where every step is Existence.many and
          no step requires registration.
        - Returns False for any plan requiring creations context.
    """
    for plan_step in steps:
        if plan_step.existence is not Existence.many:
            return False
        if plan_step.must_register:
            return False
    return True


def _compile_emitted_no_overrides_executor(
        *,
        source: str,
        namespace: Dict[str, Any],
        source_name: str,
        compile_failure_message: str,
) -> Callable[[Any], Any]:
    """
    Compile generated no-overrides source and return `_phase12_executor`.

    Contract:
        - Raises RuntimeError when source compilation/execution fails.
        - Raises RuntimeError when `_phase12_executor` is not callable.
    """
    local_namespace: Dict[str, Any] = {}
    try:
        exec(
            compile(source, source_name, "exec"),
            namespace,
            local_namespace,
        )
    except Exception as exc:
        raise RuntimeError(compile_failure_message) from exc
    executor = local_namespace.get("_phase12_executor")
    if callable(executor):
        return executor
    raise RuntimeError(
        "Phase 12 no-overrides executor source did not define a callable _phase12_executor."
    )


def _build_step_plan_executor_source(
        *,
        steps: Tuple[Any, ...],
) -> str:
    """
    Build emitted source for general no-overrides step-plan execution.

    Contract:
        - Emits one direct step-resolution block per plan step.
        - Inlines existence/lock/reuse/register routing in generated source.
        - Preserves root-instance verification semantics.
    """
    step_count = len(steps)
    lines = [
        "def _phase12_executor(",
        "        context=None,",
        "        *,",
        "        steps=steps,",
        "        step_creations_target_kinds=step_creations_target_kinds,",
        "        root_instance_key=root_instance_key,",
        "        ExecutionPlanTargetKind=ExecutionPlanTargetKind,",
        "        _construct_spell_instance=_construct_spell_instance,",
        "        _get_existing_creation=_get_existing_creation,",
        "        _register_spell_instance=_register_spell_instance,",
        "        MeldExecutionError=MeldExecutionError,",
        "    ):",
        "    instance_results = {}",
    ]
    for index, plan_step in enumerate(steps):
        _append_step_resolution_source(
            lines=lines,
            step_index=index,
            plan_step=plan_step,
        )
    lines.extend([
        "    if root_instance_key not in instance_results:",
        "        raise MeldExecutionError(",
        "            spell_id=root_instance_key[0],",
        "            spell_name=root_instance_key[0],",
        "            message=f\"Phase 12 root instance '{root_instance_key[0]}' is missing.\",",
        "        )",
        "    return instance_results[root_instance_key]",
    ])
    return "\n".join(lines)


def _append_step_resolution_source(
        *,
        lines: list[str],
        step_index: int,
        plan_step: Any,
) -> None:
    """
    Append emitted source lines for one no-overrides plan step.

    Contract:
        - Emits deterministic variable names per step index.
        - Mirrors `_resolve_step_instance` semantics for all existence modes.
    """
    lines.extend([
        f"    plan_step_{step_index} = steps[{step_index}]",
        f"    spell_{step_index} = plan_step_{step_index}.spell",
        f"    target_kind_{step_index} = step_creations_target_kinds[{step_index}]",
        (
            f"    if target_kind_{step_index} in ("
            f"ExecutionPlanTargetKind.CALLER, ExecutionPlanTargetKind.SPELLSPACE):"
        ),
        "        if context is None:",
        "            raise RuntimeError(",
        "                \"Phase 12 CALLER/SPELLSPACE execution requires a MeldContext.\"",
        "            )",
        f"        creations_{step_index} = context.caller_creations",
        f"    elif target_kind_{step_index} == ExecutionPlanTargetKind.OWNER:",
        f"        owner_creations_{step_index} = spell_{step_index}._owner_creations",
        f"        if owner_creations_{step_index} is not None:",
        f"            creations_{step_index} = owner_creations_{step_index}",
        "        elif context is None:",
        "            raise RuntimeError(",
        "                \"Phase 12 OWNER execution requires owner creations context.\"",
        "            )",
        "        else:",
        f"            creations_{step_index} = context.owner_creations",
        "    else:",
        (
            f"        raise RuntimeError("
            f"f\"Unsupported creations target kind '{{target_kind_{step_index}}}' "
            f"for spell '{{spell_{step_index}.spell_id}}'.\")"
        ),
    ])

    existence = plan_step.existence
    if existence is Existence.many:
        lines.append(
            f"    instance_{step_index} = _construct_spell_instance("
            f"plan_step=plan_step_{step_index}, "
            f"instance_results=instance_results)"
        )
        if plan_step.must_register:
            lines.extend([
                f"    with creations_{step_index}._lock:",
                (
                    f"        _register_spell_instance("
                    f"spell=spell_{step_index}, "
                    f"instance=instance_{step_index}, "
                    f"creations=creations_{step_index}, "
                    f"existence=plan_step_{step_index}.existence)"
                ),
            ])
        lines.append(f"    instance_results[plan_step_{step_index}.instance_key] = instance_{step_index}")
        return

    if existence in (
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
            f"    if instance_{step_index} is None:",
            f"        with creations_{step_index}._lock:",
            (
                f"            instance_{step_index} = _get_existing_creation("
                f"spell=spell_{step_index}, "
                f"creations=creations_{step_index}, "
                f"existence=plan_step_{step_index}.existence)"
            ),
            f"            if instance_{step_index} is None:",
            (
                f"                instance_{step_index} = _construct_spell_instance("
                f"plan_step=plan_step_{step_index}, "
                f"instance_results=instance_results)"
            ),
            (
                f"                _register_spell_instance("
                f"spell=spell_{step_index}, "
                f"instance=instance_{step_index}, "
                f"creations=creations_{step_index}, "
                f"existence=plan_step_{step_index}.existence)"
            ),
            f"    instance_results[plan_step_{step_index}.instance_key] = instance_{step_index}",
        ])
        return

    if plan_step.use_spell_lock_hint:
        lines.extend([
            f"    use_spell_lock_{step_index} = True",
            "    if (",
            "            context is not None",
            "            and context.caller_creations_lock_held",
            f"            and creations_{step_index} is context.caller_creations",
            "    ):",
            f"        use_spell_lock_{step_index} = False",
            f"    if use_spell_lock_{step_index}:",
            f"        with spell_{step_index}._lock:",
            f"            with creations_{step_index}._lock:",
            (
                f"                instance_{step_index} = _get_existing_creation("
                f"spell=spell_{step_index}, "
                f"creations=creations_{step_index}, "
                f"existence=plan_step_{step_index}.existence)"
            ),
            f"            if instance_{step_index} is None:",
            (
                f"                instance_{step_index} = _construct_spell_instance("
                f"plan_step=plan_step_{step_index}, "
                f"instance_results=instance_results)"
            ),
            f"                with creations_{step_index}._lock:",
            (
                f"                    _register_spell_instance("
                f"spell=spell_{step_index}, "
                f"instance=instance_{step_index}, "
                f"creations=creations_{step_index}, "
                f"existence=plan_step_{step_index}.existence)"
            ),
            "    else:",
            f"        with creations_{step_index}._lock:",
            (
                f"            instance_{step_index} = _get_existing_creation("
                f"spell=spell_{step_index}, "
                f"creations=creations_{step_index}, "
                f"existence=plan_step_{step_index}.existence)"
            ),
            f"            if instance_{step_index} is None:",
            (
                f"                instance_{step_index} = _construct_spell_instance("
                f"plan_step=plan_step_{step_index}, "
                f"instance_results=instance_results)"
            ),
            (
                f"                _register_spell_instance("
                f"spell=spell_{step_index}, "
                f"instance=instance_{step_index}, "
                f"creations=creations_{step_index}, "
                f"existence=plan_step_{step_index}.existence)"
            ),
            f"    instance_results[plan_step_{step_index}.instance_key] = instance_{step_index}",
        ])
        return

    lines.extend([
        f"    with creations_{step_index}._lock:",
        (
            f"        instance_{step_index} = _get_existing_creation("
            f"spell=spell_{step_index}, "
            f"creations=creations_{step_index}, "
            f"existence=plan_step_{step_index}.existence)"
        ),
        f"        if instance_{step_index} is None:",
        (
            f"            instance_{step_index} = _construct_spell_instance("
            f"plan_step=plan_step_{step_index}, "
            f"instance_results=instance_results)"
        ),
        (
            f"            _register_spell_instance("
            f"spell=spell_{step_index}, "
            f"instance=instance_{step_index}, "
            f"creations=creations_{step_index}, "
            f"existence=plan_step_{step_index}.existence)"
        ),
        f"    instance_results[plan_step_{step_index}.instance_key] = instance_{step_index}",
    ])


def _build_step_executor_namespace(
        *,
        steps: Tuple[Any, ...],
        root_instance_key: Tuple[str, Optional[int]],
) -> Dict[str, Any]:
    """
    Build namespace values for emitted no-overrides step executor source.

    Contract:
        - Captures immutable plan values as function defaults.
        - Exposes helper callables used by generated source.
    """
    return {
        "MeldExecutionError": MeldExecutionError,
        "ExecutionPlanTargetKind": ExecutionPlanTargetKind,
        "_construct_spell_instance": _construct_spell_instance,
        "_get_existing_creation": _get_existing_creation,
        "_register_spell_instance": _register_spell_instance,
        "step_creations_target_kinds": tuple(
            plan_step.creations_target_kind
            for plan_step in steps
        ),
        "steps": steps,
        "root_instance_key": root_instance_key,
    }

def _select_creations_for_target_kind(
        *,
        context: Any,
        plan_step: Any,
        spell: Any,
) -> Any:
    """
    Select the creations container from plan metadata.

    Contract:
        - CALLER and SPELLSPACE target caller_creations.
        - OWNER targets spell owner creations, then context owner_creations.
        - Requires context for CALLER/SPELLSPACE targets.
    """
    target_kind = plan_step.creations_target_kind
    if target_kind in (
            ExecutionPlanTargetKind.CALLER,
            ExecutionPlanTargetKind.SPELLSPACE,
    ):
        if context is None:
            raise RuntimeError(
                "Phase 12 CALLER/SPELLSPACE execution requires a MeldContext."
            )
        return context.caller_creations

    if target_kind == ExecutionPlanTargetKind.OWNER:
        owner_creations = spell._owner_creations
        if owner_creations is not None:
            return owner_creations
        if context is None:
            raise RuntimeError(
                "Phase 12 OWNER execution requires owner creations context."
            )
        return context.owner_creations

    raise RuntimeError(
        f"Unsupported creations target kind '{target_kind}' for spell '{spell.spell_id}'."
    )


def _construct_spell_instance(
        *,
        plan_step: Any,
        instance_results: Dict[Tuple[str, Optional[int]], Any],
) -> Any:
    """
    Construct one spell instance from dependency results and plan metadata.

    Contract:
        - Reads dependencies from prior step results using plan_step call recipe.
        - Applies plan-time contract payload fields.
        - Supports __args__ positional payloads when present.
        - Raises MeldExecutionError when dependency results are missing or call
          target invocation fails.
    """
    spell = plan_step.spell
    kwargs = _build_kwargs_no_overrides(
        plan_step=plan_step,
        instance_results=instance_results,
    )

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


def _build_kwargs_no_overrides(
        *,
        plan_step: Any,
        instance_results: Dict[Tuple[str, Optional[int]], Any],
) -> Dict[str, Any]:
    """
    Build keyword arguments for one step without runtime override payloads.

    Contract:
        - Uses dependency_resolution_order produced by Phase 9.
        - Single dependency maps to one value; multiple map to a list.
        - Includes plan-time contract payload values.
    """
    spell = plan_step.spell
    spell_id = spell.spell_index.current
    kwargs: Dict[str, Any] = {}
    for param_name, dependency_keys in plan_step.dependency_resolution_order:
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
                kwargs[param_name] = value

    return kwargs


def _get_existing_creation(
        *,
        spell: Any,
        creations: Any,
        existence: Existence,
) -> Optional[Any]:
    """
    Resolve an existing creation from the selected creations container.

    Contract:
        - Shared and per-conduit singleton scopes read from creations._creations.
        - Spellspace scope reads from the active SpellSpace bucket.
        - Existence.many always returns None.
    """
    if existence is Existence.many:
        return None
    spell_id = spell.spell_id
    if existence in (
            Existence.unique,
            Existence.unique_per_conduit,
            Existence.unique_per_conduit_cluster,
            Existence.unique_per_conduit_lineage,
    ):
        creation = creations._creations.get(spell_id)
        if creation is None:
            return None
        return creation.value

    if existence is Existence.unique_per_spell_space:
        spellspace = creations._conduit.get_active_spellspace()
        if spellspace is None:
            raise SpellSpaceScopeError(
                "Existence.unique_per_spell_space requires an active SpellSpace. "
                "Use 'with conduit.enter_spellspace()' when melding."
            )
        if spellspace.owner_conduit is not creations._conduit:
            raise SpellSpaceScopeError(
                "Active SpellSpace belongs to a different conduit."
            )
        creation = creations.get_spellspace_creation(spellspace.id, spell_id)
        return creation.value if creation is not None else None

    raise RuntimeError(
        f"[MELD] Unsupported Existence '{existence}' for creation reuse "
        f"(spell_id={spell_id})."
    )


def _register_spell_instance(
        *,
        spell: Any,
        instance: Any,
        creations: Any,
        existence: Existence,
) -> None:
    """
    Register a constructed instance into creations for no-overrides execution.

    Contract:
        - Shared/per-conduit singleton scopes use add_creation.
        - many uses add_many_creations only when disposal methods exist.
        - spellspace scope uses register_spellspace_creation for active spellspace.
    """
    spell_id = spell.spell_id
    has_disposal_methods = spell.has_disposal_methods
    disposal_methods = spell.disposal_method_names

    if existence in (
            Existence.unique,
            Existence.unique_per_conduit,
            Existence.unique_per_conduit_cluster,
            Existence.unique_per_conduit_lineage,
    ):
        creations.add_creation(
            spell_id,
            instance,
            has_disposal_methods=has_disposal_methods,
            disposal_methods=disposal_methods,
        )
        return

    if existence is Existence.many:
        if not has_disposal_methods:
            return
        creations.add_many_creations(
            spell_id,
            instance,
            has_disposal_methods=has_disposal_methods,
            disposal_methods=disposal_methods,
        )
        return

    if existence is Existence.unique_per_spell_space:
        spellspace = creations._conduit.get_active_spellspace()
        if spellspace is None:
            raise SpellSpaceScopeError(
                "Existence.unique_per_spell_space requires an active SpellSpace. "
                "Use 'with conduit.enter_spellspace()' when melding."
            )
        if spellspace.owner_conduit is not creations._conduit:
            raise SpellSpaceScopeError(
                "Active SpellSpace belongs to a different conduit."
            )
        creations.register_spellspace_creation(
            spellspace.id,
            spell_id,
            instance,
            has_disposal_methods=has_disposal_methods,
            disposal_methods=disposal_methods,
        )
        return

    raise RuntimeError(
        f"[MELD] Unsupported Existence '{existence}' for registration "
        f"(spell_id={spell_id})."
    )


def _build_phase12_executor_source(
        *,
        transient_schema: Dict[str, Any],
) -> Optional[str]:
    """
    Build Python source for a transient-schema unrolled Phase 12 executor.

    Contract:
        - Emits one direct call statement per transient step.
        - Returns None when any step uses CALLN or an unsupported call mode.
        - Emits a context-accepting function signature for API consistency.
    """
    transient_step_count = transient_schema["step_count"]
    transient_root_index = transient_schema["root_step_index"]
    transient_call_modes = transient_schema["call_modes"]
    transient_dep1 = transient_schema["dep1"]
    transient_dep2a = transient_schema["dep2a"]
    transient_dep2b = transient_schema["dep2b"]
    transient_dep3a = transient_schema["dep3a"]
    transient_dep3b = transient_schema["dep3b"]
    transient_dep3c = transient_schema["dep3c"]
    transient_dep4a = transient_schema["dep4a"]
    transient_dep4b = transient_schema["dep4b"]
    transient_dep4c = transient_schema["dep4c"]
    transient_dep4d = transient_schema["dep4d"]
    transient_dep5a = transient_schema["dep5a"]
    transient_dep5b = transient_schema["dep5b"]
    transient_dep5c = transient_schema["dep5c"]
    transient_dep5d = transient_schema["dep5d"]
    transient_dep5e = transient_schema["dep5e"]
    transient_dep6a = transient_schema["dep6a"]
    transient_dep6b = transient_schema["dep6b"]
    transient_dep6c = transient_schema["dep6c"]
    transient_dep6d = transient_schema["dep6d"]
    transient_dep6e = transient_schema["dep6e"]
    transient_dep6f = transient_schema["dep6f"]
    transient_dep7a = transient_schema["dep7a"]
    transient_dep7b = transient_schema["dep7b"]
    transient_dep7c = transient_schema["dep7c"]
    transient_dep7d = transient_schema["dep7d"]
    transient_dep7e = transient_schema["dep7e"]
    transient_dep7f = transient_schema["dep7f"]
    transient_dep7g = transient_schema["dep7g"]
    transient_dep8a = transient_schema["dep8a"]
    transient_dep8b = transient_schema["dep8b"]
    transient_dep8c = transient_schema["dep8c"]
    transient_dep8d = transient_schema["dep8d"]
    transient_dep8e = transient_schema["dep8e"]
    transient_dep8f = transient_schema["dep8f"]
    transient_dep8g = transient_schema["dep8g"]
    transient_dep8h = transient_schema["dep8h"]

    lines = [
        "def _phase12_executor(",
        "        context=None,",
        "        *,",
        "        transient_root_index=transient_root_index,",
        "        transient_targets=transient_targets,",
        "        transient_dep1=transient_dep1,",
        "        transient_dep2a=transient_dep2a,",
        "        transient_dep2b=transient_dep2b,",
        "        transient_dep3a=transient_dep3a,",
        "        transient_dep3b=transient_dep3b,",
        "        transient_dep3c=transient_dep3c,",
        "        transient_dep4a=transient_dep4a,",
        "        transient_dep4b=transient_dep4b,",
        "        transient_dep4c=transient_dep4c,",
        "        transient_dep4d=transient_dep4d,",
        "        transient_dep5a=transient_dep5a,",
        "        transient_dep5b=transient_dep5b,",
        "        transient_dep5c=transient_dep5c,",
        "        transient_dep5d=transient_dep5d,",
        "        transient_dep5e=transient_dep5e,",
        "        transient_dep6a=transient_dep6a,",
        "        transient_dep6b=transient_dep6b,",
        "        transient_dep6c=transient_dep6c,",
        "        transient_dep6d=transient_dep6d,",
        "        transient_dep6e=transient_dep6e,",
        "        transient_dep6f=transient_dep6f,",
        "        transient_dep7a=transient_dep7a,",
        "        transient_dep7b=transient_dep7b,",
        "        transient_dep7c=transient_dep7c,",
        "        transient_dep7d=transient_dep7d,",
        "        transient_dep7e=transient_dep7e,",
        "        transient_dep7f=transient_dep7f,",
        "        transient_dep7g=transient_dep7g,",
        "        transient_dep8a=transient_dep8a,",
        "        transient_dep8b=transient_dep8b,",
        "        transient_dep8c=transient_dep8c,",
        "        transient_dep8d=transient_dep8d,",
        "        transient_dep8e=transient_dep8e,",
        "        transient_dep8f=transient_dep8f,",
        "        transient_dep8g=transient_dep8g,",
        "        transient_dep8h=transient_dep8h,",
        "        steps=steps,",
        "    ):",
    ]

    for step_index in range(transient_step_count):
        lines.append(f"    t{step_index} = transient_targets[{step_index}]")

    lines.append("    __step_index = 0")
    lines.append("    try:")

    for step_index in range(transient_step_count):
        call_mode = transient_call_modes[step_index]
        call_expression = _build_unrolled_call_expression(
            step_index=step_index,
            call_mode=call_mode,
            transient_dep1=transient_dep1,
            transient_dep2a=transient_dep2a,
            transient_dep2b=transient_dep2b,
            transient_dep3a=transient_dep3a,
            transient_dep3b=transient_dep3b,
            transient_dep3c=transient_dep3c,
            transient_dep4a=transient_dep4a,
            transient_dep4b=transient_dep4b,
            transient_dep4c=transient_dep4c,
            transient_dep4d=transient_dep4d,
            transient_dep5a=transient_dep5a,
            transient_dep5b=transient_dep5b,
            transient_dep5c=transient_dep5c,
            transient_dep5d=transient_dep5d,
            transient_dep5e=transient_dep5e,
            transient_dep6a=transient_dep6a,
            transient_dep6b=transient_dep6b,
            transient_dep6c=transient_dep6c,
            transient_dep6d=transient_dep6d,
            transient_dep6e=transient_dep6e,
            transient_dep6f=transient_dep6f,
            transient_dep7a=transient_dep7a,
            transient_dep7b=transient_dep7b,
            transient_dep7c=transient_dep7c,
            transient_dep7d=transient_dep7d,
            transient_dep7e=transient_dep7e,
            transient_dep7f=transient_dep7f,
            transient_dep7g=transient_dep7g,
            transient_dep8a=transient_dep8a,
            transient_dep8b=transient_dep8b,
            transient_dep8c=transient_dep8c,
            transient_dep8d=transient_dep8d,
            transient_dep8e=transient_dep8e,
            transient_dep8f=transient_dep8f,
            transient_dep8g=transient_dep8g,
            transient_dep8h=transient_dep8h,
        )
        if call_expression is None:
            return None

        lines.append(f"        __step_index = {step_index}")
        lines.append(f"        v{step_index} = {call_expression}")

    lines.extend([
        "    except Exception as exc:",
        "        step_spell = steps[__step_index].spell",
        "        raise MeldExecutionError(",
        "            spell_id=step_spell.spell_index.current,",
        "            spell_name=step_spell.spell_name,",
        "            message=f\"Error invoking spell '{step_spell.spell_name}'.\",",
        "            inner=exc,",
        "        ) from exc",
        f"    return v{transient_root_index}",
    ])
    return "\n".join(lines)


def _build_unrolled_call_expression(
        *,
        step_index: int,
        call_mode: int,
        transient_dep1: Sequence[int],
        transient_dep2a: Sequence[int],
        transient_dep2b: Sequence[int],
        transient_dep3a: Sequence[int],
        transient_dep3b: Sequence[int],
        transient_dep3c: Sequence[int],
        transient_dep4a: Sequence[int],
        transient_dep4b: Sequence[int],
        transient_dep4c: Sequence[int],
        transient_dep4d: Sequence[int],
        transient_dep5a: Sequence[int],
        transient_dep5b: Sequence[int],
        transient_dep5c: Sequence[int],
        transient_dep5d: Sequence[int],
        transient_dep5e: Sequence[int],
        transient_dep6a: Sequence[int],
        transient_dep6b: Sequence[int],
        transient_dep6c: Sequence[int],
        transient_dep6d: Sequence[int],
        transient_dep6e: Sequence[int],
        transient_dep6f: Sequence[int],
        transient_dep7a: Sequence[int],
        transient_dep7b: Sequence[int],
        transient_dep7c: Sequence[int],
        transient_dep7d: Sequence[int],
        transient_dep7e: Sequence[int],
        transient_dep7f: Sequence[int],
        transient_dep7g: Sequence[int],
        transient_dep8a: Sequence[int],
        transient_dep8b: Sequence[int],
        transient_dep8c: Sequence[int],
        transient_dep8d: Sequence[int],
        transient_dep8e: Sequence[int],
        transient_dep8f: Sequence[int],
        transient_dep8g: Sequence[int],
        transient_dep8h: Sequence[int],
) -> Optional[str]:
    """
    Build a direct call expression for one transient step.

    Contract:
        - Returns None for unsupported call modes.
    """
    if call_mode == ExecutionPlanCallMode.CALL0:
        return f"t{step_index}()"
    if call_mode == ExecutionPlanCallMode.CALL1:
        return f"t{step_index}(v{transient_dep1[step_index]})"
    if call_mode == ExecutionPlanCallMode.CALL2:
        return (
            f"t{step_index}(v{transient_dep2a[step_index]}, "
            f"v{transient_dep2b[step_index]})"
        )
    if call_mode == ExecutionPlanCallMode.CALL3:
        return (
            f"t{step_index}(v{transient_dep3a[step_index]}, "
            f"v{transient_dep3b[step_index]}, "
            f"v{transient_dep3c[step_index]})"
        )
    if call_mode == ExecutionPlanCallMode.CALL4:
        return (
            f"t{step_index}(v{transient_dep4a[step_index]}, "
            f"v{transient_dep4b[step_index]}, "
            f"v{transient_dep4c[step_index]}, "
            f"v{transient_dep4d[step_index]})"
        )
    if call_mode == ExecutionPlanCallMode.CALL5:
        return (
            f"t{step_index}(v{transient_dep5a[step_index]}, "
            f"v{transient_dep5b[step_index]}, "
            f"v{transient_dep5c[step_index]}, "
            f"v{transient_dep5d[step_index]}, "
            f"v{transient_dep5e[step_index]})"
        )
    if call_mode == ExecutionPlanCallMode.CALL6:
        return (
            f"t{step_index}(v{transient_dep6a[step_index]}, "
            f"v{transient_dep6b[step_index]}, "
            f"v{transient_dep6c[step_index]}, "
            f"v{transient_dep6d[step_index]}, "
            f"v{transient_dep6e[step_index]}, "
            f"v{transient_dep6f[step_index]})"
        )
    if call_mode == ExecutionPlanCallMode.CALL7:
        return (
            f"t{step_index}(v{transient_dep7a[step_index]}, "
            f"v{transient_dep7b[step_index]}, "
            f"v{transient_dep7c[step_index]}, "
            f"v{transient_dep7d[step_index]}, "
            f"v{transient_dep7e[step_index]}, "
            f"v{transient_dep7f[step_index]}, "
            f"v{transient_dep7g[step_index]})"
        )
    if call_mode == ExecutionPlanCallMode.CALL8:
        return (
            f"t{step_index}(v{transient_dep8a[step_index]}, "
            f"v{transient_dep8b[step_index]}, "
            f"v{transient_dep8c[step_index]}, "
            f"v{transient_dep8d[step_index]}, "
            f"v{transient_dep8e[step_index]}, "
            f"v{transient_dep8f[step_index]}, "
            f"v{transient_dep8g[step_index]}, "
            f"v{transient_dep8h[step_index]})"
        )
    return None


def _build_executor_namespace(
        *,
        transient_schema: Dict[str, Any],
        steps: Tuple[Any, ...],
) -> Dict[str, Any]:
    """
    Build the globals namespace for transient unrolled compilation.

    Contract:
        - Exposes transient schema arrays and derived call targets.
        - Exposes hydrated steps for deterministic error reporting.
    """
    transient_step_count = transient_schema["step_count"]
    transient_targets = _resolve_transient_targets(
        steps=steps,
        transient_step_count=transient_step_count,
    )

    return {
        "MeldExecutionError": MeldExecutionError,
        "transient_root_index": transient_schema["root_step_index"],
        "transient_targets": transient_targets,
        "transient_dep1": transient_schema["dep1"],
        "transient_dep2a": transient_schema["dep2a"],
        "transient_dep2b": transient_schema["dep2b"],
        "transient_dep3a": transient_schema["dep3a"],
        "transient_dep3b": transient_schema["dep3b"],
        "transient_dep3c": transient_schema["dep3c"],
        "transient_dep4a": transient_schema["dep4a"],
        "transient_dep4b": transient_schema["dep4b"],
        "transient_dep4c": transient_schema["dep4c"],
        "transient_dep4d": transient_schema["dep4d"],
        "transient_dep5a": transient_schema["dep5a"],
        "transient_dep5b": transient_schema["dep5b"],
        "transient_dep5c": transient_schema["dep5c"],
        "transient_dep5d": transient_schema["dep5d"],
        "transient_dep5e": transient_schema["dep5e"],
        "transient_dep6a": transient_schema["dep6a"],
        "transient_dep6b": transient_schema["dep6b"],
        "transient_dep6c": transient_schema["dep6c"],
        "transient_dep6d": transient_schema["dep6d"],
        "transient_dep6e": transient_schema["dep6e"],
        "transient_dep6f": transient_schema["dep6f"],
        "transient_dep7a": transient_schema["dep7a"],
        "transient_dep7b": transient_schema["dep7b"],
        "transient_dep7c": transient_schema["dep7c"],
        "transient_dep7d": transient_schema["dep7d"],
        "transient_dep7e": transient_schema["dep7e"],
        "transient_dep7f": transient_schema["dep7f"],
        "transient_dep7g": transient_schema["dep7g"],
        "transient_dep8a": transient_schema["dep8a"],
        "transient_dep8b": transient_schema["dep8b"],
        "transient_dep8c": transient_schema["dep8c"],
        "transient_dep8d": transient_schema["dep8d"],
        "transient_dep8e": transient_schema["dep8e"],
        "transient_dep8f": transient_schema["dep8f"],
        "transient_dep8g": transient_schema["dep8g"],
        "transient_dep8h": transient_schema["dep8h"],
        "steps": steps,
    }


def _resolve_transient_targets(
        *,
        steps: Tuple[Any, ...],
        transient_step_count: int,
) -> Tuple[Any, ...]:
    """
    Derive transient call targets from hydrated step spell metadata.

    Contract:
        - Transient schema step_count must match hydrated step count.
        - Every step must be callable under transient execution constraints.
    """
    if transient_step_count != len(steps):
        raise RuntimeError(
            "Phase 12 no-overrides transient schema step_count does not match hydrated steps."
        )

    transient_targets = []
    for step_index, plan_step in enumerate(steps):
        spell = plan_step.spell
        if not (spell.is_class_spell or spell.is_method_spell or spell.is_lambda_spell):
            raise RuntimeError(
                "Phase 12 no-overrides transient schema requires callable steps; "
                f"step {step_index} is not callable."
            )
        transient_targets.append(spell.spell)
    return tuple(transient_targets)
