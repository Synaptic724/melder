from types import SimpleNamespace
from typing import Any, Callable, Dict, Optional, Sequence, Tuple
from melder.aether.spellbook.spell_compiler.executor_code_cache import (
    get_or_compile_executor_code,
)
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.utilities.custom_exceptions.spell_space_scope_error import SpellSpaceScopeError

_MISSING = object()

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


class ManyOnlyCodegenPlanTargetKind:
    """
    Many-only compiler-local creations target kind labels.
    """

    __slots__ = ()
    CALLER: int = 1
    OWNER: int = 2
    SPELLSPACE: int = 3


class ManyOnlyCodegenPlanCallMode:
    """
    Many-only compiler-local call-mode labels.
    """

    __slots__ = ()
    CALL0: int = 0
    CALL1: int = 1
    CALL2: int = 2
    CALL3: int = 3
    CALL4: int = 4
    CALL5: int = 5
    CALL6: int = 6
    CALL7: int = 7
    CALL8: int = 8
    CALLN: int = 9

def compile_no_overrides_codegen_creation_executor(
        *,
        codegen_ir: Dict[str, Any],
        spell_lookup: Optional[Dict[str, Any]] = None,
) -> Optional[Callable[..., Any]]:
    """
    Compile a spell-scoped no-overrides codegen executor from Codegen IR.

    Purpose:
        Build the no-overrides execution callable consumed by Meld's runtime path so
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
        Optional[Callable[..., Any]]:
            Compiled executor receiving direct creations inputs.

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
    return _compile_no_overrides_executor_from_entry_inputs(
        steps=steps,
        root_instance_key=None,
        root_spell_id=codegen_ir.get("root_spell_id"),
        transient_schema=codegen_ir.get("transient_schema"),
        missing_root_instance_key_message=(
            "No-overrides codegen IR is missing a resolvable root instance key."
        ),
    )


def compile_no_overrides_codegen_creation_executor_from_plan(
        *,
        plan: Any,
        transient_schema: Optional[Dict[str, Any]] = None,
) -> Optional[Callable[..., Any]]:
    """
    Compile a spell-scoped no-overrides codegen executor from a generalized lane plan.

    Purpose:
        Support hot phase11 compile wiring without requiring schema-row export
        payload construction when plan objects are already available.

    Contract:
        - Returns a callable when the plan contains executable steps.
        - Returns None when the plan has zero steps.
        - Uses transient-unrolled emission when the provided transient schema is
          compatible with the plan steps.
        - Uses emitted step-plan source for all other plans.
        - Raises when root instance key cannot be resolved from the plan.

    Args:
        plan:
            Lane-plan-like object exposing `steps`, `root_instance_key`,
            and `root_spell_id`.
        transient_schema:
            Optional schema-only transient payload derived from the plan's fast
            transient data.

    Returns:
        Optional[Callable[..., Any]]:
            Compiled executor receiving direct creations inputs.

    Raises:
        ValueError:
            If plan is None.
        RuntimeError:
            If the root instance key cannot be resolved.
            If transient codegen source compilation or namespace wiring fails.
    """
    if plan is None:
        raise ValueError("plan must not be None.")

    steps = plan.steps
    if not steps:
        return None
    return _compile_no_overrides_executor_from_entry_inputs(
        steps=steps,
        root_instance_key=plan.root_instance_key,
        root_spell_id=plan.root_spell_id,
        transient_schema=transient_schema,
        missing_root_instance_key_message=(
            "No-overrides codegen plan is missing a resolvable root instance key."
        ),
    )


def _compile_no_overrides_executor_from_entry_inputs(
        *,
        steps: Tuple[Any, ...],
        root_instance_key: Optional[Tuple[str, Optional[int]]],
        root_spell_id: Optional[str],
        transient_schema: Optional[Dict[str, Any]],
        missing_root_instance_key_message: str,
) -> Callable[..., Any]:
    """
    Resolve shared entrypoint inputs, then compile no-overrides executor source.

    Contract:
        - Reuses caller-provided `root_instance_key` when present.
        - Resolves missing root keys from `root_spell_id` using plan-step
          metadata.
        - Raises RuntimeError using caller-provided message when no root key is
          resolvable.
        - Delegates transient-vs-step-plan source selection to
          `_compile_no_overrides_executor_from_steps`.

    Args:
        steps:
            Hydrated no-overrides plan steps.
        root_instance_key:
            Optional pre-resolved root instance key from entrypoint payload.
        root_spell_id:
            Root spell id used for fallback root key resolution.
        transient_schema:
            Optional transient schema used by transient codegen path.
        missing_root_instance_key_message:
            Entrypoint-specific error message when root resolution fails.

    Returns:
        Callable[..., Any]:
            Compiled no-overrides executor for the provided entrypoint payload.

    Raises:
        RuntimeError:
            If root instance key cannot be resolved from the provided inputs.
    """
    resolved_root_instance_key = root_instance_key
    if resolved_root_instance_key is None:
        resolved_root_instance_key = _resolve_root_instance_key(
            steps=steps,
            root_spell_id=root_spell_id,
        )
    if resolved_root_instance_key is None:
        raise RuntimeError(missing_root_instance_key_message)
    return _compile_no_overrides_executor_from_steps(
        steps=steps,
        root_instance_key=resolved_root_instance_key,
        transient_schema=transient_schema,
    )


def _compile_no_overrides_executor_from_steps(
        *,
        steps: Tuple[Any, ...],
        root_instance_key: Tuple[str, Optional[int]],
        transient_schema: Optional[Dict[str, Any]],
) -> Callable[..., Any]:
    """
    Compile a no-overrides executor from hydrated steps plus optional transient schema.

    Contract:
        - Uses transient unrolled source emission whenever phase 10 already
          provided a fast-transient schema for the many-only family.
        - Falls back to emitted step-plan source only when that schema is
          absent.
        - Preserves compile source names and failure message semantics for both
          transient and step-plan compilation paths.

    Args:
        steps:
            Hydrated no-overrides plan steps.
        root_instance_key:
            Root instance lookup key used by emitted step-plan executors.
        transient_schema:
            Optional transient-only schema payload for unrolled transient
            execution codegen.

    Returns:
        Callable[..., Any]:
            Compiled no-overrides executor for the provided plan shape.
    """
    if transient_schema is not None:
        normalized_transient_schema = _normalize_transient_schema(
            transient_schema=transient_schema,
        )
        source = _build_no_overrides_codegen_executor_source(
            transient_schema=normalized_transient_schema,
        )
        if source is not None:
            namespace = _build_executor_namespace(
                transient_schema=normalized_transient_schema,
                steps=steps,
            )
            return _compile_emitted_no_overrides_executor(
                source=source,
                namespace=namespace,
                source_name="<melder_no_overrides_codegen_creation_transient_executor>",
                compile_failure_message=(
                    "No-overrides codegen transient executor generation failed."
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
        source_name="<melder_no_overrides_codegen_creation_step_executor>",
        compile_failure_message=(
            "No-overrides codegen executor generation failed."
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
            "No-overrides codegen schema rows require spell_lookup for step hydration."
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
                    "No-overrides codegen schema row is missing required field "
                    f"'{field_name}' at index {row_index}."
                )

        spell_id = row["spell_id"]
        spell = spell_lookup.get(spell_id)
        if spell is None:
            raise RuntimeError(
                f"No-overrides codegen step schema references unknown spell_id '{spell_id}'."
            )

        existence_name = row["existence"]
        try:
            existence = Existence[existence_name]
        except KeyError as exc:
            raise RuntimeError(
                "No-overrides codegen step schema contains unknown existence "
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
                "No-overrides codegen transient schema is missing required "
                f"field '{field_name}'."
            )

    step_count = transient_schema["step_count"]
    if not isinstance(step_count, int) or step_count < 0:
        raise RuntimeError(
            "No-overrides codegen transient schema 'step_count' must be a non-negative int."
        )

    root_step_index = transient_schema["root_step_index"]
    if not isinstance(root_step_index, int):
        raise RuntimeError(
            "No-overrides codegen transient schema 'root_step_index' must be an int."
        )

    normalized: Dict[str, Any] = {
        "step_count": step_count,
        "root_step_index": root_step_index,
    }
    for field_name in _TRANSIENT_SCHEMA_SEQUENCE_FIELDS:
        value = transient_schema[field_name]
        if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
            raise RuntimeError(
                "No-overrides codegen transient schema field "
                f"'{field_name}' must be a sequence."
            )
        values = tuple(value)
        if len(values) != step_count:
            raise RuntimeError(
                "No-overrides codegen transient schema field "
                f"'{field_name}' length must equal step_count."
            )
        normalized[field_name] = values

    if step_count == 0:
        if root_step_index != 0:
            raise RuntimeError(
                "No-overrides codegen transient schema with step_count 0 must use root_step_index 0."
            )
    elif root_step_index < 0 or root_step_index >= step_count:
        raise RuntimeError(
            "No-overrides codegen transient schema root_step_index is out of range."
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
        # Concrete typing for mypy: callers only rely on 2-tuple instance keys.
        instance_key: Tuple[str, Optional[int]] = plan_step.instance_key
        if instance_key[0] == root_spell_id and instance_key[1] is None:
            return instance_key
    for plan_step in steps:
        # Concrete typing for mypy: fallback branch expects a tuple instance key.
        fallback_instance_key: Tuple[str, Optional[int]] = plan_step.instance_key
        if fallback_instance_key[0] == root_spell_id:
            return fallback_instance_key
    return None


def _compile_emitted_no_overrides_executor(
        *,
        source: str,
        namespace: Dict[str, Any],
        source_name: str,
        compile_failure_message: str,
) -> Callable[..., Any]:
    """
    Compile generated no-overrides source and return the emitted executor.

    Contract:
        - Raises RuntimeError when source compilation/execution fails.
        - Raises RuntimeError when the emitted executor symbol is not callable.
        - Resolves the code object through the process-wide executor code
          cache: identity-free source that has been compiled before (this
          conjure, an earlier conjure, or another Spellbook) reuses the cached
          code object instead of recompiling. `exec` still runs per call
          against the supplied per-spell `namespace`.
    """
    local_namespace: Dict[str, Any] = {}
    try:
        code_object = get_or_compile_executor_code(
            source=source,
            source_name=source_name,
        )
        exec(
            code_object,
            namespace,
            local_namespace,
        )
    except Exception as exc:
        raise RuntimeError(compile_failure_message) from exc
    executor = local_namespace.get("_no_overrides_codegen_creation_executor")
    if callable(executor):
        compiled_executor: Callable[..., Any] = executor
        return compiled_executor
    raise RuntimeError(
        "No-overrides codegen executor source did not define a callable _no_overrides_codegen_creation_executor."
    )


def _inlinable_common_shape(
        plan_step: Any,
) -> Optional[Tuple[Tuple[str, Any], ...]]:
    """
    Return inlinable ``(param_name, dependency_key)`` pairs for a step, or
    ``None`` when the step must use the generic ``_construct_spell_instance``.

    A step is inlinable when its construction is exactly
    ``spell.spell(**{param: instance_results[key] ...})`` -- the common shape:
    a callable (class/method/lambda) spell that is not an existing-creation,
    carries no contract payload, no positional ``__args__`` override, and whose
    every constructor parameter resolves to exactly one dependency (no
    collection DI). Any other shape returns ``None`` so the proven generic
    helper handles it.

    Returned pairs are in constructor-argument order; an empty tuple means an
    inlinable spell with no dependency arguments (``spell.spell()``).
    """
    spell = plan_step.spell
    if not (
            spell.is_class_spell
            or spell.is_method_spell
            or spell.is_lambda_spell
    ):
        return None
    if spell.is_existing_creation:
        return None
    if plan_step.has_contract_payload:
        return None
    if plan_step.contract_positional_override is not None:
        return None
    if plan_step.uses_positional_override:
        return None
    params: list[Tuple[str, Any]] = []
    for param_name, dependency_keys in plan_step.dependency_resolution_order:
        dependency_count = len(dependency_keys)
        if dependency_count == 0:
            continue
        if dependency_count != 1:
            return None
        params.append((param_name, dependency_keys[0]))
    return tuple(params)


def _raise_meld_construction_error(spell: Any, exc: BaseException) -> None:
    """
    Raise the ``MeldExecutionError`` for a failed inlined constructor call.

    Mirrors the error wrapping in ``_construct_spell_instance`` so the inlined
    fast path and the generic fallback report construction failures
    identically. Lives off the hot path: only the failure branch calls it.
    """
    raise MeldExecutionError(
        spell_id=spell.spell_index.current,
        spell_name=spell.spell_name,
        message=f"Error invoking spell '{spell.spell_name}'.",
        inner=exc,
    ) from exc


def _emit_construct_instance(
        *,
        lines: list[str],
        step_index: int,
        inlinable_params: Optional[Tuple[Tuple[str, Any], ...]],
        indent: str,
) -> None:
    """
    Append the construction source for one step at ``indent``.

    For the common shape (``inlinable_params`` is not ``None``) this emits a
    direct ``spell.spell(**kwargs)`` call, so no per-meld recipe interpretation
    happens. For every other shape it emits the generic
    ``_construct_spell_instance`` call unchanged.
    """
    if inlinable_params is None:
        lines.append(
            f"{indent}instance_{step_index} = _construct_spell_instance("
            f"plan_step=plan_step_{step_index}, "
            f"instance_results=instance_results)"
        )
        return
    lines.append(f"{indent}try:")
    if inlinable_params:
        lines.append(
            f"{indent}    instance_{step_index} = spell_{step_index}.spell("
        )
        for arg_index, (param_name, _dependency_key) in enumerate(
                inlinable_params,
        ):
            lines.append(
                f"{indent}        {param_name}="
                f"instance_results[step_dep_keys_{step_index}[{arg_index}]],"
            )
        lines.append(f"{indent}    )")
    else:
        lines.append(
            f"{indent}    instance_{step_index} = spell_{step_index}.spell()"
        )
    lines.extend([
        f"{indent}except Exception as exc:",
        f"{indent}    _raise_meld_construction_error(spell_{step_index}, exc)",
    ])


def _build_step_plan_executor_source(
        *,
        steps: Tuple[Any, ...],
) -> str:
    """
    Build emitted source for general no-overrides step-plan execution.

    Contract:
        - Emits one direct step-resolution block per plan step.
        - Inlines existence/lock/reuse/register routing in generated source.
        - Inlines the constructor call for the common spell shape; other
          shapes keep the generic `_construct_spell_instance` path.
        - Preserves root-instance verification semantics.
    """
    step_count = len(steps)
    lines = [
        "def _no_overrides_codegen_creation_executor(",
        "        caller_creations=None,",
        "        owner_creations=None,",
        "        caller_creations_lock_held=False,",
        "        steps=steps,",
        "        step_spells=step_spells,",
        "        step_spell_ids=step_spell_ids,",
        "        step_has_disposal_methods=step_has_disposal_methods,",
        "        step_disposal_methods=step_disposal_methods,",
        "        step_instance_keys=step_instance_keys,",
        "        step_dep_keys=step_dep_keys,",
        "        root_instance_key=root_instance_key,",
        "        ManyOnlyCodegenPlanTargetKind=ManyOnlyCodegenPlanTargetKind,",
        "        _construct_spell_instance=_construct_spell_instance,",
        "        _raise_meld_construction_error=_raise_meld_construction_error,",
        "        MeldExecutionError=MeldExecutionError,",
        "        SpellSpaceScopeError=SpellSpaceScopeError,",
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
        "            message=f\"No-overrides codegen root instance '{root_instance_key[0]}' is missing.\",",
        "        )",
        "    return instance_results[root_instance_key]",
    ])
    return "\n".join(lines)


def _append_step_creations_target_source(
        *,
        lines: list[str],
        step_index: int,
        target_kind: int,
) -> None:
    """
    Append emitted source lines for static creations-target routing.

    Contract:
        - Emits one fixed routing path from compile-time `target_kind`.
        - Avoids per-step runtime target-kind branch ladders.
    """
    if target_kind in (
            ManyOnlyCodegenPlanTargetKind.CALLER,
            ManyOnlyCodegenPlanTargetKind.SPELLSPACE,
    ):
        lines.extend([
            "    if caller_creations is None:",
            "        raise RuntimeError(",
            "            \"No-overrides codegen CALLER/SPELLSPACE execution requires caller_creations.\"",
            "        )",
            f"    creations_{step_index} = caller_creations",
        ])
        return

    if target_kind == ManyOnlyCodegenPlanTargetKind.OWNER:
        lines.extend([
            f"    owner_creations_{step_index} = spell_{step_index}._owner_creations",
            f"    if owner_creations_{step_index} is not None:",
            f"        creations_{step_index} = owner_creations_{step_index}",
            "    elif owner_creations is None:",
            "        raise RuntimeError(",
            "            \"No-overrides codegen OWNER execution requires owner_creations.\"",
            "        )",
            "    else:",
            f"        creations_{step_index} = owner_creations",
        ])
        return

    lines.append(
        f"    raise RuntimeError("
        f"f\"Unsupported creations target kind '{target_kind}' "
        f"for spell '{{spell_{step_index}.spell_id}}'.\")"
    )


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
        - Emits static creations-target routing from plan metadata.
        - Emits an inlined constructor call for the common spell shape and
          falls back to `_construct_spell_instance` for every other shape.
    """
    inlinable_params = _inlinable_common_shape(plan_step)
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
    ])
    if inlinable_params:
        lines.append(
            f"    step_dep_keys_{step_index} = step_dep_keys[{step_index}]"
        )
    _append_step_creations_target_source(
        lines=lines,
        step_index=step_index,
        target_kind=plan_step.creations_target_kind,
    )
    _emit_construct_instance(
        lines=lines,
        step_index=step_index,
        inlinable_params=inlinable_params,
        indent="    ",
    )
    lines.append(f"    with creations_{step_index}._lock:")
    _emit_construct_instance(
        lines=lines,
        step_index=step_index,
        inlinable_params=inlinable_params,
        indent="        ",
    )
    _append_step_register_source(
        lines=lines,
        step_index=step_index,
        indent="        ",
    )
    lines.append(f"    instance_results[step_instance_keys[{step_index}]] = instance_{step_index}")


def _append_step_register_source(
        *,
        lines: list[str],
        step_index: int,
        indent: str,
) -> None:
    """
    Append emitted registration lines specialized for one step existence mode.

    Contract:
        - Emits the direct many-only registration semantics only.
        - Registers only when disposal methods exist for the step spell.
        - Assumes caller has already emitted the required creations lock.
    """
    lines.extend([
        f"{indent}if has_disposal_methods_{step_index}:",
        f"{indent}    creations_{step_index}.add_many_creations(",
        f"{indent}        spell_id_{step_index},",
        f"{indent}        instance_{step_index},",
        (
            f"{indent}        has_disposal_methods="
            f"has_disposal_methods_{step_index},"
        ),
        (
            f"{indent}        disposal_methods="
            f"disposal_methods_{step_index},"
        ),
        f"{indent}    )",
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
        "SpellSpaceScopeError": SpellSpaceScopeError,
        "ManyOnlyCodegenPlanTargetKind": ManyOnlyCodegenPlanTargetKind,
        "_construct_spell_instance": _construct_spell_instance,
        "_raise_meld_construction_error": _raise_meld_construction_error,
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
        "step_instance_keys": tuple(
            plan_step.instance_key
            for plan_step in steps
        ),
        "step_dep_keys": tuple(
            tuple(
                dependency_key
                for _param_name, dependency_key in (
                    _inlinable_common_shape(plan_step) or ()
                )
            )
            for plan_step in steps
        ),
        "steps": steps,
        "root_instance_key": root_instance_key,
    }

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
        - Preserves tuple positional payloads without rebuilding list objects.
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
    dependency_resolution_order = plan_step.dependency_resolution_order
    contract_positional_override = plan_step.contract_positional_override
    if (
            not dependency_resolution_order
            and contract_positional_override is None
            and not plan_step.has_contract_payload
    ):
        return {}
    if (
            not dependency_resolution_order
            and contract_positional_override is None
            and plan_step.has_contract_payload
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
                kwargs[param_name] = value

    return kwargs




def _build_no_overrides_codegen_executor_source(
        *,
        transient_schema: Dict[str, Any],
) -> Optional[str]:
    """
    Build Python source for a transient-schema unrolled no-overrides codegen executor.

    Contract:
        - Emits one direct call statement per transient step.
        - Returns None when any step uses CALLN or an unsupported call mode.
        - Emits a creations-parameter signature for API consistency.
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
        "def _no_overrides_codegen_creation_executor(",
        "        caller_creations=None,",
        "        owner_creations=None,",
        "        caller_creations_lock_held=False,",
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
    ]
    lines.extend([
        "        steps=steps,",
        "    ):",
    ])

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
    arg_refs = _build_unrolled_call_arg_refs(
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
    if arg_refs is None:
        return None
    if not arg_refs:
        return f"t{step_index}()"
    return f"t{step_index}({', '.join(arg_refs)})"


def _build_unrolled_call_arg_refs(
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
) -> Optional[Tuple[str, ...]]:
    """
    Build ordered argument references for one transient call mode.

    Contract:
        - Returns tuple of local variable references for CALL0..CALL8.
        - Returns None for unsupported call modes.
    """
    if call_mode == ManyOnlyCodegenPlanCallMode.CALL0:
        return ()
    if call_mode == ManyOnlyCodegenPlanCallMode.CALL1:
        return (
            f"v{transient_dep1[step_index]}",
        )
    if call_mode == ManyOnlyCodegenPlanCallMode.CALL2:
        return (
            f"v{transient_dep2a[step_index]}",
            f"v{transient_dep2b[step_index]}",
        )
    if call_mode == ManyOnlyCodegenPlanCallMode.CALL3:
        return (
            f"v{transient_dep3a[step_index]}",
            f"v{transient_dep3b[step_index]}",
            f"v{transient_dep3c[step_index]}",
        )
    if call_mode == ManyOnlyCodegenPlanCallMode.CALL4:
        return (
            f"v{transient_dep4a[step_index]}",
            f"v{transient_dep4b[step_index]}",
            f"v{transient_dep4c[step_index]}",
            f"v{transient_dep4d[step_index]}",
        )
    if call_mode == ManyOnlyCodegenPlanCallMode.CALL5:
        return (
            f"v{transient_dep5a[step_index]}",
            f"v{transient_dep5b[step_index]}",
            f"v{transient_dep5c[step_index]}",
            f"v{transient_dep5d[step_index]}",
            f"v{transient_dep5e[step_index]}",
        )
    if call_mode == ManyOnlyCodegenPlanCallMode.CALL6:
        return (
            f"v{transient_dep6a[step_index]}",
            f"v{transient_dep6b[step_index]}",
            f"v{transient_dep6c[step_index]}",
            f"v{transient_dep6d[step_index]}",
            f"v{transient_dep6e[step_index]}",
            f"v{transient_dep6f[step_index]}",
        )
    if call_mode == ManyOnlyCodegenPlanCallMode.CALL7:
        return (
            f"v{transient_dep7a[step_index]}",
            f"v{transient_dep7b[step_index]}",
            f"v{transient_dep7c[step_index]}",
            f"v{transient_dep7d[step_index]}",
            f"v{transient_dep7e[step_index]}",
            f"v{transient_dep7f[step_index]}",
            f"v{transient_dep7g[step_index]}",
        )
    if call_mode == ManyOnlyCodegenPlanCallMode.CALL8:
        return (
            f"v{transient_dep8a[step_index]}",
            f"v{transient_dep8b[step_index]}",
            f"v{transient_dep8c[step_index]}",
            f"v{transient_dep8d[step_index]}",
            f"v{transient_dep8e[step_index]}",
            f"v{transient_dep8f[step_index]}",
            f"v{transient_dep8g[step_index]}",
            f"v{transient_dep8h[step_index]}",
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
            "No-overrides codegen transient schema step_count does not match hydrated steps."
        )

    transient_targets = []
    for step_index, plan_step in enumerate(steps):
        spell = plan_step.spell
        if not (spell.is_class_spell or spell.is_method_spell or spell.is_lambda_spell):
            raise RuntimeError(
                "No-overrides codegen transient schema requires callable steps; "
                f"step {step_index} is not callable."
            )
        transient_targets.append(spell.spell)
    return tuple(transient_targets)

