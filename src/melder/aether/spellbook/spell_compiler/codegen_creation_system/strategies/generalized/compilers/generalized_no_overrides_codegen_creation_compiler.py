from types import SimpleNamespace
from typing import Any, Callable, Dict, Optional, Sequence, Tuple, Union

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.executor_code_cache import (
    get_or_compile_executor_code,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.data.spell_generalized_codegen_lane_plan import (
    SpellGeneralizedCodegenPlanCallMode,
    SpellGeneralizedCodegenPlanTargetKind,
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

def compile_no_overrides_codegen_creation_executor(
        *,
        codegen_ir: Dict[str, Any],
        spell_lookup: Optional[Dict[str, Any]] = None,
        return_compiled_code_object: bool = False,
) -> Optional[Union[Callable[..., Any], Tuple[Callable[..., Any], Any]]]:
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
        return_compiled_code_object=return_compiled_code_object,
    )


def compile_no_overrides_codegen_creation_executor_from_plan(
        *,
        plan: Any,
        transient_schema: Optional[Dict[str, Any]] = None,
        return_compiled_code_object: bool = False,
) -> Optional[Union[Callable[..., Any], Tuple[Callable[..., Any], Any]]]:
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
        return_compiled_code_object=return_compiled_code_object,
    )


def _compile_no_overrides_executor_from_entry_inputs(
        *,
        steps: Tuple[Any, ...],
        root_instance_key: Optional[Tuple[str, Optional[int]]],
        root_spell_id: Optional[str],
        transient_schema: Optional[Dict[str, Any]],
        missing_root_instance_key_message: str,
        return_compiled_code_object: bool = False,
) -> Union[Callable[..., Any], Tuple[Callable[..., Any], Any]]:
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
        return_compiled_code_object=return_compiled_code_object,
    )


def _compile_no_overrides_executor_from_steps(
        *,
        steps: Tuple[Any, ...],
        root_instance_key: Tuple[str, Optional[int]],
        transient_schema: Optional[Dict[str, Any]],
        return_compiled_code_object: bool = False,
) -> Union[Callable[..., Any], Tuple[Callable[..., Any], Any]]:
    """
    Compile a no-overrides executor from hydrated steps plus optional transient schema.

    Contract:
        - Tries transient unrolled source emission when transient schema is
          provided and the plan supports transient unrolling.
        - Falls back to emitted step-plan source when transient source is
          unavailable or plan support checks fail.
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
    if transient_schema is not None and _supports_transient_unrolled_plan(steps):
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
                return_compiled_code_object=return_compiled_code_object,
            )

    step_source = _build_step_plan_executor_source(
        steps=steps,
        root_instance_key=root_instance_key,
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
        return_compiled_code_object=return_compiled_code_object,
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
        return_compiled_code_object: bool = False,
) -> Union[Callable[..., Any], Tuple[Callable[..., Any], Any]]:
    """
    Compile generated no-overrides source and return the emitted executor.

    Contract:
        - Raises RuntimeError when source compilation/execution fails.
        - Raises RuntimeError when the emitted executor symbol is not callable.
        - Uses the process-wide emitted-source code-object cache.
        - When `return_compiled_code_object` is true, also returns the
          compiled `CodeType` used to build the executor.
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
        if return_compiled_code_object:
            return compiled_executor, code_object
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
        spell_id=spell.spell_index.selected_spell_id,
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
        instance_index_by_key: Optional[Dict[Tuple[str, Optional[int]], int]] = None,
) -> None:
    """
    Append the construction source for one step at ``indent``.

    For the common shape (``inlinable_params`` is not ``None``) this emits a
    direct ``spell.spell(**kwargs)`` call, so no per-meld recipe interpretation
    happens. For every other shape it emits the generic
    ``_construct_spell_instance`` call unchanged.

    Dependency-reference mode:
        - When ``instance_index_by_key`` is ``None`` (the dict path), inlined
          dependency arguments read ``instance_results[...]`` exactly as before.
        - When it is provided (the unrolled path), they read straight-line
          ``instance_{dep_index}`` locals -- no dict and no ``step_dep_keys``
          binding. The generic ``_construct_spell_instance`` shape is never
          emitted on the unrolled path (it is gated to all-inlinable plans).
    """
    if inlinable_params is None:
        # `plan_step_{step_index}` is consumed only by this generic construct
        # path, so it is bound here (cold) rather than in the per-step preamble.
        lines.append(f"{indent}plan_step_{step_index} = steps[{step_index}]")
        lines.append(
            f"{indent}instance_{step_index} = _construct_spell_instance("
            f"plan_step=plan_step_{step_index}, "
            f"instance_results=instance_results)"
        )
        return
    lines.append(f"{indent}try:")
    if inlinable_params:
        if instance_index_by_key is None:
            # step_dep_keys_{step_index} is consumed only by this inlined
            # construct on the dict path, so it is bound here (cold).
            lines.append(
                f"{indent}    step_dep_keys_{step_index} = step_dep_keys[{step_index}]"
            )
        lines.append(
            f"{indent}    instance_{step_index} = spell_{step_index}.spell("
        )
        for arg_index, (param_name, dependency_key) in enumerate(
                inlinable_params,
        ):
            if instance_index_by_key is None:
                dependency_reference = (
                    f"instance_results[step_dep_keys_{step_index}[{arg_index}]]"
                )
            else:
                dependency_reference = (
                    f"instance_{instance_index_by_key[dependency_key]}"
                )
            lines.append(
                f"{indent}        {param_name}={dependency_reference},"
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
        root_instance_key: Optional[Tuple[str, Optional[int]]] = None,
) -> str:
    """
    Build emitted source for general no-overrides step-plan execution.

    Emission modes:
        - DICT path (default): each step publishes into `instance_results`,
          dependencies read it, and the root returns via
          `instance_results[root_instance_key]`.
        - UNROLLED path: chosen when `root_instance_key` is supplied, every step
          is inlinable, and the root key maps to a step. Results stay in
          `instance_{i}` locals; dependencies read those locals; the root is
          returned directly. No `instance_results` dict, no per-step dict writes,
          no `step_dep_keys` indexing, and no final membership check are emitted.
          Unused signature defaults (step_instance_keys / step_dep_keys /
          root_instance_key / helper callables) are harmless on this path.
    """
    step_count = len(steps)

    instance_index_by_key: Optional[Dict[Tuple[str, Optional[int]], int]] = None
    root_step_index: Optional[int] = None
    if root_instance_key is not None and _all_steps_inlinable(steps):
        candidate_index_by_key = _instance_index_by_key(steps)
        candidate_root_index = candidate_index_by_key.get(root_instance_key)
        if candidate_root_index is not None:
            instance_index_by_key = candidate_index_by_key
            root_step_index = candidate_root_index

    lines = [
        "def _no_overrides_codegen_creation_executor(",
        "        meld,",
        "        steps=steps,",
        "        step_spells=step_spells,",
        "        step_spell_ids=step_spell_ids,",
        "        step_has_disposal_methods=step_has_disposal_methods,",
        "        step_disposal_methods=step_disposal_methods,",
        "        step_existences=step_existences,",
        "        step_instance_keys=step_instance_keys,",
        "        step_dep_keys=step_dep_keys,",
        "        root_instance_key=root_instance_key,",
        "        SpellGeneralizedCodegenPlanTargetKind=SpellGeneralizedCodegenPlanTargetKind,",
        "        _construct_spell_instance=_construct_spell_instance,",
        "        _raise_meld_construction_error=_raise_meld_construction_error,",
        "        _get_existing_creation=_get_existing_creation,",
        "        _register_spell_instance_prebound=_register_spell_instance_prebound,",
        "        MeldExecutionError=MeldExecutionError,",
        "        SpellSpaceScopeError=SpellSpaceScopeError,",
        "    ):",
    ]
    if instance_index_by_key is None:
        lines.append("    instance_results = {}")
    for index, plan_step in enumerate(steps):
        _append_step_resolution_source(
            lines=lines,
            step_index=index,
            plan_step=plan_step,
            instance_index_by_key=instance_index_by_key,
        )
    if instance_index_by_key is None:
        lines.extend([
            "    if root_instance_key not in instance_results:",
            "        raise MeldExecutionError(",
            "            spell_id=root_instance_key[0],",
            "            spell_name=root_instance_key[0],",
            "            message=f\"No-overrides codegen root instance '{root_instance_key[0]}' is missing.\",",
            "        )",
            "    return instance_results[root_instance_key]",
        ])
    else:
        lines.append(f"    return instance_{root_step_index}")
    return "\n".join(lines)


def _append_step_creations_target_source(
        *,
        lines: list[str],
        step_index: int,
        existence: Existence,
) -> None:
    """
    Append emitted source resolving this step's creations store off the meld.

    Contract:
        - Routes by the step's compile-time existence to the store the meld
          front doors select: `many` -> innermost active scope (spellspace store
          when melded through a SpellSpaceMeld, else the conduit store);
          `unique_per_conduit` -> conduit store; `unique_per_spell_space` ->
          spellspace store; `unique_per_conduit_lineage` -> lineage-root store;
          `unique_per_conduit_cluster` -> elected-leader store; `unique` -> the
          binding owner's `spell._owner_creations`.
        - Each store is read straight off the resolving `meld`, never a
          pre-selected `caller_creations`/`owner_creations` argument.
    """
    if existence is Existence.many:
        lines.extend([
            f"    creations_{step_index} = meld._spellspace_creations",
            f"    if creations_{step_index} is None:",
            f"        creations_{step_index} = meld._conduit_creations",
        ])
        return
    if existence is Existence.unique_per_conduit:
        lines.append(f"    creations_{step_index} = meld._conduit_creations")
        return
    if existence is Existence.unique_per_spell_space:
        lines.append(f"    creations_{step_index} = meld._spellspace_creations")
        return
    if existence is Existence.unique_per_conduit_lineage:
        lines.append(f"    creations_{step_index} = meld._root_creations")
        return
    if existence is Existence.unique_per_conduit_cluster:
        lines.append(
            f"    creations_{step_index} = meld._cluster_creations.resolved_store()"
        )
        return
    if existence is Existence.unique:
        lines.append(
            f"    creations_{step_index} = spell_{step_index}._owner_creations"
        )
        return

    raise RuntimeError(
        f"Unsupported existence for generalized no-overrides creations routing: "
        f"{existence!r}"
    )


def _all_steps_inlinable(steps: Tuple[Any, ...]) -> bool:
    """
    Return True when every plan step is an inlinable common-shape step.

    The unrolled (straight-line locals) executor reads dependencies from
    `instance_{dep_index}` locals, which requires every step's construction to be
    the inlined `spell.spell(**deps)` shape. A generic `_construct_spell_instance`
    step reads its dependencies from the `instance_results` dict internally, so a
    plan containing one is not unroll-eligible and stays on the dict path.
    """
    return all(
        _inlinable_common_shape(plan_step) is not None
        for plan_step in steps
    )


def _instance_index_by_key(
        steps: Tuple[Any, ...],
) -> Dict[Tuple[str, Optional[int]], int]:
    """
    Map each step's instance key to its step index (its `instance_{i}` local).

    The unrolled path uses this to turn a dependency's instance key into a direct
    `instance_{dep_index}` local reference. Steps are in topological order, so a
    dependency's index is always less than the dependent's and its local is in
    scope by the time it is read.
    """
    return {
        plan_step.instance_key: index
        for index, plan_step in enumerate(steps)
    }


def _append_step_result_store(
        *,
        lines: list[str],
        step_index: int,
        instance_index_by_key: Optional[Dict[Tuple[str, Optional[int]], int]],
) -> None:
    """
    Append the per-step result publish.

    Dict path (`instance_index_by_key` is None): store the result into
    `instance_results` keyed by the step's instance key, for cross-step
    dependency lookups and the final root return. Unrolled path: the result
    already lives in the `instance_{step_index}` local, so nothing is emitted.
    """
    if instance_index_by_key is None:
        lines.append(
            f"    instance_results[step_instance_keys[{step_index}]] = instance_{step_index}"
        )


def _append_step_resolution_source(
        *,
        lines: list[str],
        step_index: int,
        plan_step: Any,
        instance_index_by_key: Optional[Dict[Tuple[str, Optional[int]], int]] = None,
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
    # Only `spell_{step_index}` (OWNER routing + construct) is needed by every
    # step's preamble. `spell_id_{step_index}` is needed on the warm path only by
    # the singleton reuse read; a `many` step uses it solely inside its
    # disposal-gated register, so for `many` it is bound there instead (cold).
    # The remaining construct-only locals are likewise bound lazily on the cold
    # path: `plan_step_{step_index}` in `_emit_construct_instance` and
    # `has_disposal_methods_{step_index}` / `disposal_methods_{step_index}` in
    # `_append_step_register_source`, so warm reuse melds do not pay for them.
    lines.append(f"    spell_{step_index} = step_spells[{step_index}]")
    if plan_step.existence is not Existence.many:
        lines.append(f"    spell_id_{step_index} = step_spell_ids[{step_index}]")
    _append_step_creations_target_source(
        lines=lines,
        step_index=step_index,
        existence=plan_step.existence,
    )

    existence = plan_step.existence
    if existence is Existence.many:
        _emit_construct_instance(
            lines=lines,
            step_index=step_index,
            inlinable_params=inlinable_params,
            indent="    ",
            instance_index_by_key=instance_index_by_key,
        )
        # `many` registers ONLY to track disposal, and disposal-ness is
        # spell-static -- so the decision is made here at COMPILE time (matching
        # the solo / many_only families). A non-disposal `many` step emits no
        # register at all: no lock, no add, no per-meld disposal binds or branch.
        # Only a disposal-bearing `many` emits the lock + registration.
        if plan_step.spell.has_disposal_methods:
            _append_step_register_source(
                lines=lines,
                step_index=step_index,
                indent="    ",
                existence=existence,
            )
        _append_step_result_store(
            lines=lines,
            step_index=step_index,
            instance_index_by_key=instance_index_by_key,
        )
        return

    # Singleton reuse read is emitted inline as `creations.get_creation(spell_id)`
    # rather than the runtime-dispatching `_get_existing_creation(...)` helper:
    # existence is compile-time-known per step, `spell_id_{step_index}` is the
    # same key the helper reads by and register writes by, and every singleton
    # existence reduces to exactly `creations.get_creation(spell_id)`. The helper
    # is provably equivalent here; inlining drops a call frame + a `spell.spell_id`
    # attribute read + an existence branch ladder from the warm reuse path.
    if existence in (
            Existence.unique_per_conduit,
            Existence.unique_per_spell_space,
    ):
        lines.extend([
            f"    instance_{step_index} = creations_{step_index}.get_creation(spell_id_{step_index})",
            f"    if instance_{step_index} is None:",
            f"        with creations_{step_index}._lock:",
            f"            instance_{step_index} = creations_{step_index}.get_creation(spell_id_{step_index})",
            f"            if instance_{step_index} is None:",
        ])
        _emit_construct_instance(
            lines=lines,
            step_index=step_index,
            inlinable_params=inlinable_params,
            indent="                ",
            instance_index_by_key=instance_index_by_key,
        )
        _append_step_register_source(
            lines=lines,
            step_index=step_index,
            indent="                ",
            existence=existence,
        )
        _append_step_result_store(
            lines=lines,
            step_index=step_index,
            instance_index_by_key=instance_index_by_key,
        )
        return

    if plan_step.use_spell_lock_hint:
        lines.extend([
            f"    instance_{step_index} = creations_{step_index}.get_creation(spell_id_{step_index})",
            f"    if instance_{step_index} is None:",
            # use_spell_lock_{step_index} is consulted only on the construct path,
            # so compute it here (cold) instead of on every warm meld.
            f"        use_spell_lock_{step_index} = True",
            f"        if use_spell_lock_{step_index}:",
            f"            with spell_{step_index}._lock:",
            f"                with creations_{step_index}._lock:",
            f"                    instance_{step_index} = creations_{step_index}.get_creation(spell_id_{step_index})",
            f"                if instance_{step_index} is None:",
        ])
        _emit_construct_instance(
            lines=lines,
            step_index=step_index,
            inlinable_params=inlinable_params,
            indent="                    ",
            instance_index_by_key=instance_index_by_key,
        )
        lines.append(f"                    with creations_{step_index}._lock:")
        _append_step_register_source(
            lines=lines,
            step_index=step_index,
            indent="                        ",
            existence=existence,
        )
        lines.extend([
            "        else:",
            f"            with creations_{step_index}._lock:",
            f"                instance_{step_index} = creations_{step_index}.get_creation(spell_id_{step_index})",
            f"                if instance_{step_index} is None:",
        ])
        _emit_construct_instance(
            lines=lines,
            step_index=step_index,
            inlinable_params=inlinable_params,
            indent="                    ",
            instance_index_by_key=instance_index_by_key,
        )
        _append_step_register_source(
            lines=lines,
            step_index=step_index,
            indent="                    ",
            existence=existence,
        )
        _append_step_result_store(
            lines=lines,
            step_index=step_index,
            instance_index_by_key=instance_index_by_key,
        )
        return

    lines.extend([
        f"    instance_{step_index} = creations_{step_index}.get_creation(spell_id_{step_index})",
        f"    if instance_{step_index} is None:",
        f"        with creations_{step_index}._lock:",
        f"            instance_{step_index} = creations_{step_index}.get_creation(spell_id_{step_index})",
        f"            if instance_{step_index} is None:",
    ])
    _emit_construct_instance(
        lines=lines,
        step_index=step_index,
        inlinable_params=inlinable_params,
        indent="                ",
        instance_index_by_key=instance_index_by_key,
    )
    _append_step_register_source(
        lines=lines,
        step_index=step_index,
        indent="                ",
        existence=existence,
    )
    _append_step_result_store(
        lines=lines,
        step_index=step_index,
        instance_index_by_key=instance_index_by_key,
    )


def _append_step_register_source(
        *,
        lines: list[str],
        step_index: int,
        indent: str,
        existence: Existence,
) -> None:
    """
    Append emitted registration lines specialized for one step existence mode.

    Contract:
        - Preserves `_register_spell_instance_prebound(...)` routing semantics.
        - Emits direct creations method calls to avoid per-registration helper
          dispatch and existence branching at runtime.
        - Singleton / spellspace branches assume the caller has already emitted
          the required creations lock around this registration.
        - The `many` branch is emitted ONLY for disposal-bearing `many` steps
          (the caller gates on disposal at compile time), so it registers
          unconditionally under the creations lock with no runtime disposal
          check. The caller must NOT pre-emit a lock for the `many` branch.
        - Binds `has_disposal_methods_{step_index}` / `disposal_methods_{step_index}`
          here (cold construct/register path) so warm reuse melds never pay for
          those per-step lookups.
    """
    lines.extend([
        (
            f"{indent}has_disposal_methods_{step_index} = "
            f"step_has_disposal_methods[{step_index}]"
        ),
        (
            f"{indent}disposal_methods_{step_index} = "
            f"step_disposal_methods[{step_index}]"
        ),
    ])
    if existence in (
            Existence.unique,
            Existence.unique_per_conduit,
            Existence.unique_per_conduit_cluster,
            Existence.unique_per_conduit_lineage,
    ):
        lines.extend([
            f"{indent}creations_{step_index}.add_creation(",
            f"{indent}    spell_id_{step_index},",
            f"{indent}    instance_{step_index},",
            (
                f"{indent}    has_disposal_methods="
                f"has_disposal_methods_{step_index},"
            ),
            f"{indent}    disposal_methods=disposal_methods_{step_index},",
            f"{indent})",
        ])
        return

    if existence is Existence.many:
        # The caller gates this branch on disposal at COMPILE time, so it is
        # emitted only for disposal-bearing `many` steps -- registration is
        # unconditional here, with no runtime `if has_disposal_methods_N`.
        # `many` is transient (a new instance per meld, never cached), so the
        # append is lockless -- matching the solo / many_only families.
        lines.extend([
            f"{indent}spell_id_{step_index} = step_spell_ids[{step_index}]",
            f"{indent}creations_{step_index}.add_many_creations(",
            f"{indent}    spell_id_{step_index},",
            f"{indent}    instance_{step_index},",
            (
                f"{indent}    has_disposal_methods="
                f"has_disposal_methods_{step_index},"
            ),
            (
                f"{indent}    disposal_methods="
                f"disposal_methods_{step_index},"
            ),
            f"{indent})",
        ])
        return

    if existence is Existence.unique_per_spell_space:
        lines.extend([
            f"{indent}creations_{step_index}.add_creation(",
            f"{indent}    spell_id_{step_index},",
            f"{indent}    instance_{step_index},",
            (
                f"{indent}    has_disposal_methods="
                f"has_disposal_methods_{step_index},"
            ),
            f"{indent}    disposal_methods=disposal_methods_{step_index},",
            f"{indent})",
        ])
        return

    raise RuntimeError(
        f"Unsupported emitted existence registration mode: {existence!r}"
    )


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
        "SpellGeneralizedCodegenPlanTargetKind": SpellGeneralizedCodegenPlanTargetKind,
        "_construct_spell_instance": _construct_spell_instance,
        "_raise_meld_construction_error": _raise_meld_construction_error,
        "_get_existing_creation": _get_existing_creation,
        "_register_spell_instance_prebound": _register_spell_instance_prebound,
        "_register_spell_instance": _register_spell_instance,
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

def _select_creations_for_target_kind(
        *,
        caller_creations: Any,
        owner_creations: Any,
        plan_step: Any,
        spell: Any,
) -> Any:
    """
    Select the creations container from plan metadata.

    Contract:
        - CALLER and SPELLSPACE target caller_creations.
        - OWNER targets spell owner creations, then `owner_creations`.
        - Requires caller_creations for CALLER/SPELLSPACE targets.
    """
    target_kind = plan_step.creations_target_kind
    if target_kind in (
            SpellGeneralizedCodegenPlanTargetKind.CALLER,
            SpellGeneralizedCodegenPlanTargetKind.SPELLSPACE,
    ):
        if caller_creations is None:
            raise RuntimeError(
                "No-overrides codegen CALLER/SPELLSPACE execution requires caller_creations."
            )
        return caller_creations

    if target_kind == SpellGeneralizedCodegenPlanTargetKind.OWNER:
        spell_owner_creations = spell._owner_creations
        if spell_owner_creations is not None:
            return spell_owner_creations
        if owner_creations is None:
            raise RuntimeError(
                "No-overrides codegen OWNER execution requires owner_creations."
            )
        return owner_creations

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
            spell_id=spell.spell_index.selected_spell_id,
            spell_name=spell.spell_name,
            message="__args__ override must be a list or tuple.",
        )

    try:
        return spell.spell(*args, **call_kwargs)
    except Exception as exc:
        raise MeldExecutionError(
            spell_id=spell.spell_index.selected_spell_id,
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
    spell_id = spell.spell_index.selected_spell_id
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
        creation = creations.get_creation(spell_id)
        if creation is None:
            return None
        return creation

    if existence is Existence.unique_per_spell_space:
        creation = creations.get_creation(spell_id)
        return creation

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
        - spellspace scope uses add_creation on the direct spellspace-owned store.
    """
    _register_spell_instance_prebound(
        spell_id=spell.spell_id,
        instance=instance,
        creations=creations,
        existence=existence,
        has_disposal_methods=spell.has_disposal_methods,
        disposal_methods=spell.disposal_method_names,
    )


def _register_spell_instance_prebound(
        *,
        spell_id: str,
        instance: Any,
        creations: Any,
        existence: Existence,
        has_disposal_methods: bool,
        disposal_methods: Optional[Sequence[str]],
) -> None:
    """
    Register a constructed instance using prebound spell registration metadata.

    Contract:
        - Uses spell-static metadata (`spell_id`, disposal flags/methods)
          supplied by the generated step lane.
        - Preserves the same existence routing semantics as
          `_register_spell_instance`.
    """

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
        creations.add_creation(
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
        "        meld,",
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

    # Per-slot constructor defaults: the default expressions index the
    # factory-local `transient_targets` ONCE at def-execution time, so the
    # per-call alias loads the previous body paid on every meld are gone.
    # Inserted after the `transient_targets` signature line (index 3); the
    # binding surface consumed by every caller is unchanged.
    for step_index in range(transient_step_count):
        lines.insert(
            4 + step_index,
            f"        t{step_index}=transient_targets[{step_index}],",
        )

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

        # Per-step zero-cost handler (3.11+ exception tables): constant
        # step attribution replaces the live `__step_index` bookkeeping the
        # previous body paid as one dead store per step per call.
        lines.append("    try:")
        lines.append(f"        v{step_index} = {call_expression}")
        lines.append("    except Exception as exc:")
        lines.append(f"        step_spell = steps[{step_index}].spell")
        lines.append("        raise MeldExecutionError(")
        lines.append(
            "            spell_id=step_spell.spell_index.selected_spell_id,"
        )
        lines.append("            spell_name=step_spell.spell_name,")
        lines.append(
            "            message=f\"Error invoking spell "
            "'{step_spell.spell_name}'.\","
        )
        lines.append("            inner=exc,")
        lines.append("        ) from exc")

    lines.append(f"    return v{transient_root_index}")
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
    if call_mode == SpellGeneralizedCodegenPlanCallMode.CALL0:
        return ()
    if call_mode == SpellGeneralizedCodegenPlanCallMode.CALL1:
        return (
            f"v{transient_dep1[step_index]}",
        )
    if call_mode == SpellGeneralizedCodegenPlanCallMode.CALL2:
        return (
            f"v{transient_dep2a[step_index]}",
            f"v{transient_dep2b[step_index]}",
        )
    if call_mode == SpellGeneralizedCodegenPlanCallMode.CALL3:
        return (
            f"v{transient_dep3a[step_index]}",
            f"v{transient_dep3b[step_index]}",
            f"v{transient_dep3c[step_index]}",
        )
    if call_mode == SpellGeneralizedCodegenPlanCallMode.CALL4:
        return (
            f"v{transient_dep4a[step_index]}",
            f"v{transient_dep4b[step_index]}",
            f"v{transient_dep4c[step_index]}",
            f"v{transient_dep4d[step_index]}",
        )
    if call_mode == SpellGeneralizedCodegenPlanCallMode.CALL5:
        return (
            f"v{transient_dep5a[step_index]}",
            f"v{transient_dep5b[step_index]}",
            f"v{transient_dep5c[step_index]}",
            f"v{transient_dep5d[step_index]}",
            f"v{transient_dep5e[step_index]}",
        )
    if call_mode == SpellGeneralizedCodegenPlanCallMode.CALL6:
        return (
            f"v{transient_dep6a[step_index]}",
            f"v{transient_dep6b[step_index]}",
            f"v{transient_dep6c[step_index]}",
            f"v{transient_dep6d[step_index]}",
            f"v{transient_dep6e[step_index]}",
            f"v{transient_dep6f[step_index]}",
        )
    if call_mode == SpellGeneralizedCodegenPlanCallMode.CALL7:
        return (
            f"v{transient_dep7a[step_index]}",
            f"v{transient_dep7b[step_index]}",
            f"v{transient_dep7c[step_index]}",
            f"v{transient_dep7d[step_index]}",
            f"v{transient_dep7e[step_index]}",
            f"v{transient_dep7f[step_index]}",
            f"v{transient_dep7g[step_index]}",
        )
    if call_mode == SpellGeneralizedCodegenPlanCallMode.CALL8:
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

