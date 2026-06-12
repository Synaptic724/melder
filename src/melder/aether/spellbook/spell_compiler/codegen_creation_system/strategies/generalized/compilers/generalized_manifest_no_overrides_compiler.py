"""
Family-owned no-overrides lane compiler for the generalized family.

This module owns the no-overrides lane end to end:
    - row-driven source emission (manifest rows in, factory source out;
      no live spells touched during emission),
    - executor bindings construction (flat arrays + slotted runtime rows),
    - hydration through the process-wide executor factory cache (one compile
      plus one exec per source shape per process; one factory call per spell).

Emission semantics are a faithful port of the legacy step-plan emitter with
one deliberate hot-path improvement: reuse reads are inlined as direct
`creations._creations.get(spell_id)` dict reads. The existence routing the
legacy `_get_existing_creation` helper performed at runtime is compile-time
constant per step, and `Creations.get_creation` is a bare dict read, so the
two-call helper chain is pure overhead on the meld hot path.

Row requirements beyond the shared phase-11 row schema:
    - `spell_is_callable`: class/method/lambda flag, stamped by the family
      manifest builder.
    - `spell_is_existing_creation`: existing-creation flag, stamped by the
      family manifest builder.
"""

from typing import Any, Callable, Dict, Optional, Sequence, Tuple

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_runtime_library import (
    SpellGeneralizedCodegenPlanTargetKind,
    build_transient_no_overrides_source,
    construct_spell_instance,
    normalize_transient_schema,
    raise_meld_construction_error,
    register_spell_instance,
    register_spell_instance_prebound,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_runtime_rows import (
    CodegenStepRuntimeRow,
    build_runtime_rows,
)
from melder.aether.spellbook.spell_compiler.executor_factory_cache import (
    build_executor_factory_source,
    get_or_build_executor_factory,
)
from melder.utilities.custom_exceptions.meld_execution_error import (
    MeldExecutionError,
)
from melder.utilities.custom_exceptions.spell_space_scope_error import (
    SpellSpaceScopeError,
)

EXECUTOR_NAME = "_no_overrides_codegen_creation_executor"

_STEP_FACTORY_SOURCE_NAME = (
    "<melder_generalized_no_overrides_step_factory>"
)
_TRANSIENT_FACTORY_SOURCE_NAME = (
    "<melder_generalized_no_overrides_transient_factory>"
)

_STEP_BINDING_NAMES = (
    "steps",
    "step_spells",
    "step_spell_ids",
    "step_has_disposal_methods",
    "step_disposal_methods",
    "step_existences",
    "step_instance_keys",
    "step_dep_keys",
    "root_instance_key",
)

_STEP_STATIC_NAMESPACE = {
    "MeldExecutionError": MeldExecutionError,
    "SpellSpaceScopeError": SpellSpaceScopeError,
    "SpellGeneralizedCodegenPlanTargetKind": SpellGeneralizedCodegenPlanTargetKind,
    "_construct_spell_instance": construct_spell_instance,
    "_raise_meld_construction_error": raise_meld_construction_error,
    "_register_spell_instance_prebound": register_spell_instance_prebound,
    "_register_spell_instance": register_spell_instance,
}

_TRANSIENT_STATIC_NAMESPACE = {
    "MeldExecutionError": MeldExecutionError,
}

_TRANSIENT_SCHEMA_SEQUENCE_FIELDS = (
    "dep1",
    "dep2a", "dep2b",
    "dep3a", "dep3b", "dep3c",
    "dep4a", "dep4b", "dep4c", "dep4d",
    "dep5a", "dep5b", "dep5c", "dep5d", "dep5e",
    "dep6a", "dep6b", "dep6c", "dep6d", "dep6e", "dep6f",
    "dep7a", "dep7b", "dep7c", "dep7d", "dep7e", "dep7f", "dep7g",
    "dep8a", "dep8b", "dep8c", "dep8d", "dep8e", "dep8f", "dep8g", "dep8h",
)


# ---------------------------------------------------------------------------
# Public hydration entrypoint
# ---------------------------------------------------------------------------

def hydrate_no_overrides_executor(
        *,
        rows: Sequence[Dict[str, Any]],
        transient_schema: Optional[Dict[str, Any]],
        root_instance_key: Optional[Tuple[str, Optional[int]]],
        root_spell_id: Optional[str],
        spell_lookup: Dict[str, Any],
) -> Callable[..., Any]:
    """
    Hydrate the inner no-overrides executor from manifest rows.

    Contract:
        - Emission is a pure function of rows/schema; live spells are touched
          only by bindings construction.
        - Transient unrolled emission is used exactly under the legacy rule:
          schema present, every step `many`, no step registering, and all
          call modes supported by the unrolled builder.
        - One compile + one exec per source shape per process via the factory
          cache; one factory call here.

    Raises:
        RuntimeError:
            When rows are invalid or the root instance key is unresolvable.
    """
    runtime_rows = build_runtime_rows(
        rows=rows,
        spell_lookup=spell_lookup,
    )

    if transient_schema is not None and _rows_support_transient(rows):
        normalized_schema = normalize_transient_schema(
            transient_schema=transient_schema,
        )
        transient_source = build_transient_no_overrides_source(
            transient_schema=normalized_schema,
        )
        if transient_source is not None:
            bindings = _build_transient_bindings(
                normalized_schema=normalized_schema,
                runtime_rows=runtime_rows,
            )
            factory_source = build_executor_factory_source(
                inner_source=transient_source,
                binding_names=tuple(bindings.keys()),
                executor_name=EXECUTOR_NAME,
            )
            factory = get_or_build_executor_factory(
                factory_source=factory_source,
                source_name=_TRANSIENT_FACTORY_SOURCE_NAME,
                static_namespace=_TRANSIENT_STATIC_NAMESPACE,
            )
            return factory(bindings)

    resolved_root_instance_key = resolve_root_instance_key_from_rows(
        rows=rows,
        explicit_root_instance_key=root_instance_key,
        root_spell_id=root_spell_id,
    )
    inner_source = emit_step_plan_source(rows=rows)
    bindings = _build_step_bindings(
        rows=rows,
        runtime_rows=runtime_rows,
        root_instance_key=resolved_root_instance_key,
    )
    factory_source = build_executor_factory_source(
        inner_source=inner_source,
        binding_names=_STEP_BINDING_NAMES,
        executor_name=EXECUTOR_NAME,
    )
    factory = get_or_build_executor_factory(
        factory_source=factory_source,
        source_name=_STEP_FACTORY_SOURCE_NAME,
        static_namespace=_STEP_STATIC_NAMESPACE,
    )
    return factory(bindings)


# ---------------------------------------------------------------------------
# Row-driven emission (owned)
# ---------------------------------------------------------------------------

def emit_step_plan_source(
        *,
        rows: Sequence[Dict[str, Any]],
) -> str:
    """
    Emit the inner no-overrides step-plan executor source from manifest rows.

    Contract:
        - Pure function of row data; no live objects consulted.
        - Faithful port of the legacy step-plan emission semantics (existence
          routing, lock disciplines, registration calls, inlined common-shape
          constructors, root verification) with reuse reads inlined as direct
          `_creations.get` dict reads.
    """
    lines = [
        f"def {EXECUTOR_NAME}(",
        "        caller_creations=None,",
        "        owner_creations=None,",
        "        caller_creations_lock_held=False,",
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
        "        _register_spell_instance_prebound=_register_spell_instance_prebound,",
        "        MeldExecutionError=MeldExecutionError,",
        "        SpellSpaceScopeError=SpellSpaceScopeError,",
        "    ):",
        "    instance_results = {}",
    ]
    for step_index, row in enumerate(rows):
        _append_step_resolution_source(
            lines=lines,
            step_index=step_index,
            row=row,
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


def _append_step_resolution_source(
        *,
        lines: list,
        step_index: int,
        row: Dict[str, Any],
) -> None:
    """
    Append emitted source for one step from its manifest row.
    """
    existence = Existence[row["existence"]]
    inlinable_params = row_inlinable_common_shape(row)

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
    ])
    if inlinable_params:
        lines.append(
            f"    step_dep_keys_{step_index} = step_dep_keys[{step_index}]"
        )
    _append_creations_target_source(
        lines=lines,
        step_index=step_index,
        target_kind=row["creations_target_kind"],
    )

    if existence is Existence.many:
        _emit_construct_instance(
            lines=lines,
            step_index=step_index,
            inlinable_params=inlinable_params,
            indent="    ",
        )
        lines.append(f"    with creations_{step_index}._lock:")
        _append_register_source(
            lines=lines,
            step_index=step_index,
            indent="        ",
            existence=existence,
        )
        lines.append(
            f"    instance_results[step_instance_keys[{step_index}]] = instance_{step_index}"
        )
        return

    if existence in (
            Existence.unique_per_conduit,
            Existence.unique_per_spell_space,
    ):
        lines.extend([
            (
                f"    instance_{step_index} = "
                f"creations_{step_index}._creations.get(spell_id_{step_index})"
            ),
            f"    if instance_{step_index} is None:",
            f"        with creations_{step_index}._lock:",
            (
                f"            instance_{step_index} = "
                f"creations_{step_index}._creations.get(spell_id_{step_index})"
            ),
            f"            if instance_{step_index} is None:",
        ])
        _emit_construct_instance(
            lines=lines,
            step_index=step_index,
            inlinable_params=inlinable_params,
            indent="                ",
        )
        _append_register_source(
            lines=lines,
            step_index=step_index,
            indent="                ",
            existence=existence,
        )
        lines.append(
            f"    instance_results[step_instance_keys[{step_index}]] = instance_{step_index}"
        )
        return

    if row["use_spell_lock_hint"]:
        lines.extend([
            f"    use_spell_lock_{step_index} = True",
            "    if (",
            "            caller_creations_lock_held",
            f"            and creations_{step_index} is caller_creations",
            "    ):",
            f"        use_spell_lock_{step_index} = False",
            (
                f"    instance_{step_index} = "
                f"creations_{step_index}._creations.get(spell_id_{step_index})"
            ),
            f"    if instance_{step_index} is None:",
            f"        if use_spell_lock_{step_index}:",
            f"            with spell_{step_index}._lock:",
            f"                with creations_{step_index}._lock:",
            (
                f"                    instance_{step_index} = "
                f"creations_{step_index}._creations.get(spell_id_{step_index})"
            ),
            f"                if instance_{step_index} is None:",
        ])
        _emit_construct_instance(
            lines=lines,
            step_index=step_index,
            inlinable_params=inlinable_params,
            indent="                    ",
        )
        lines.append(f"                    with creations_{step_index}._lock:")
        _append_register_source(
            lines=lines,
            step_index=step_index,
            indent="                        ",
            existence=existence,
        )
        lines.extend([
            "        else:",
            f"            with creations_{step_index}._lock:",
            (
                f"                instance_{step_index} = "
                f"creations_{step_index}._creations.get(spell_id_{step_index})"
            ),
            f"                if instance_{step_index} is None:",
        ])
        _emit_construct_instance(
            lines=lines,
            step_index=step_index,
            inlinable_params=inlinable_params,
            indent="                    ",
        )
        _append_register_source(
            lines=lines,
            step_index=step_index,
            indent="                    ",
            existence=existence,
        )
        lines.append(
            f"    instance_results[step_instance_keys[{step_index}]] = instance_{step_index}"
        )
        return

    lines.extend([
        (
            f"    instance_{step_index} = "
            f"creations_{step_index}._creations.get(spell_id_{step_index})"
        ),
        f"    if instance_{step_index} is None:",
        f"        with creations_{step_index}._lock:",
        (
            f"            instance_{step_index} = "
            f"creations_{step_index}._creations.get(spell_id_{step_index})"
        ),
        f"            if instance_{step_index} is None:",
    ])
    _emit_construct_instance(
        lines=lines,
        step_index=step_index,
        inlinable_params=inlinable_params,
        indent="                ",
    )
    _append_register_source(
        lines=lines,
        step_index=step_index,
        indent="                ",
        existence=existence,
    )
    lines.append(
        f"    instance_results[step_instance_keys[{step_index}]] = instance_{step_index}"
    )


def _append_creations_target_source(
        *,
        lines: list,
        step_index: int,
        target_kind: int,
) -> None:
    """
    Append static creations-target routing source for one step.
    """
    if target_kind in (
            SpellGeneralizedCodegenPlanTargetKind.CALLER,
            SpellGeneralizedCodegenPlanTargetKind.SPELLSPACE,
    ):
        lines.extend([
            "    if caller_creations is None:",
            "        raise RuntimeError(",
            "            \"No-overrides codegen CALLER/SPELLSPACE execution requires caller_creations.\"",
            "        )",
            f"    creations_{step_index} = caller_creations",
        ])
        return

    if target_kind == SpellGeneralizedCodegenPlanTargetKind.OWNER:
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


def _emit_construct_instance(
        *,
        lines: list,
        step_index: int,
        inlinable_params: Optional[Tuple[Tuple[str, Any], ...]],
        indent: str,
) -> None:
    """
    Append construction source for one step at `indent`.
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


def _append_register_source(
        *,
        lines: list,
        step_index: int,
        indent: str,
        existence: Existence,
) -> None:
    """
    Append registration source specialized for one existence mode.
    """
    if existence in (
            Existence.unique,
            Existence.unique_per_conduit,
            Existence.unique_per_conduit_cluster,
            Existence.unique_per_conduit_lineage,
            Existence.unique_per_spell_space,
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
        return

    raise RuntimeError(
        f"Unsupported emitted existence registration mode: {existence!r}"
    )


def row_inlinable_common_shape(
        row: Dict[str, Any],
) -> Optional[Tuple[Tuple[str, Any], ...]]:
    """
    Return inlinable (param_name, dependency_key) pairs from one manifest row.

    Contract:
        - Row-driven port of the legacy inlinable-shape rule: callable,
          non-existing-creation spells with no contract payload, no positional
          override, and exactly one dependency per parameter.
        - Requires the family row flags `spell_is_callable` and
          `spell_is_existing_creation`. Family manifest rows always carry
          them (the manifest builder stamps both), so access is direct; a
          missing flag is a row-contract violation and raises KeyError.
    """
    if not row["spell_is_callable"]:
        return None
    if row["spell_is_existing_creation"]:
        return None
    if row["has_contract_payload"]:
        return None
    if row["contract_positional_override"] is not None:
        return None
    if row["uses_positional_override"]:
        return None
    params = []
    for param_name, dependency_keys in row["dependency_resolution_order"]:
        dependency_count = len(dependency_keys)
        if dependency_count == 0:
            continue
        if dependency_count != 1:
            return None
        params.append((param_name, dependency_keys[0]))
    return tuple(params)


# ---------------------------------------------------------------------------
# Bindings (owned)
# ---------------------------------------------------------------------------

def _build_step_bindings(
        *,
        rows: Sequence[Dict[str, Any]],
        runtime_rows: Tuple[CodegenStepRuntimeRow, ...],
        root_instance_key: Tuple[str, Optional[int]],
) -> Dict[str, Any]:
    """
    Build flat step-lane bindings from manifest rows plus runtime rows.
    """
    return {
        "steps": runtime_rows,
        "step_spells": tuple(
            runtime_row.spell
            for runtime_row in runtime_rows
        ),
        "step_spell_ids": tuple(
            runtime_row.spell.spell_id
            for runtime_row in runtime_rows
        ),
        "step_has_disposal_methods": tuple(
            runtime_row.spell.has_disposal_methods
            for runtime_row in runtime_rows
        ),
        "step_disposal_methods": tuple(
            runtime_row.spell.disposal_method_names
            for runtime_row in runtime_rows
        ),
        "step_existences": tuple(
            runtime_row.existence
            for runtime_row in runtime_rows
        ),
        "step_instance_keys": tuple(
            runtime_row.instance_key
            for runtime_row in runtime_rows
        ),
        "step_dep_keys": tuple(
            tuple(
                dependency_key
                for _param_name, dependency_key in (
                    row_inlinable_common_shape(row) or ()
                )
            )
            for row in rows
        ),
        "root_instance_key": root_instance_key,
    }


def _build_transient_bindings(
        *,
        normalized_schema: Dict[str, Any],
        runtime_rows: Tuple[CodegenStepRuntimeRow, ...],
) -> Dict[str, Any]:
    """
    Build transient-lane bindings from the normalized schema plus live targets.

    Raises:
        RuntimeError:
            When schema step count mismatches rows or a step is not callable.
    """
    step_count = normalized_schema["step_count"]
    if step_count != len(runtime_rows):
        raise RuntimeError(
            "generalized transient schema step_count does not match rows."
        )
    transient_targets = []
    for step_index, runtime_row in enumerate(runtime_rows):
        spell = runtime_row.spell
        if not (
                spell.is_class_spell
                or spell.is_method_spell
                or spell.is_lambda_spell
        ):
            raise RuntimeError(
                "generalized transient lane requires callable steps; "
                f"step {step_index} is not callable."
            )
        transient_targets.append(spell.spell)

    bindings: Dict[str, Any] = {
        "transient_root_index": normalized_schema["root_step_index"],
        "transient_targets": tuple(transient_targets),
        "steps": runtime_rows,
    }
    for field_name in _TRANSIENT_SCHEMA_SEQUENCE_FIELDS:
        bindings[f"transient_{field_name}"] = normalized_schema[field_name]
    return bindings


def _rows_support_transient(rows: Sequence[Dict[str, Any]]) -> bool:
    """
    Row-driven port of the transient-support rule.

    Contract:
        - True only when every row is Existence.many and no row registers.
    """
    for row in rows:
        if row["existence"] != Existence.many.name:
            return False
        if row["must_register"]:
            return False
    return True


def resolve_root_instance_key_from_rows(
        *,
        rows: Sequence[Dict[str, Any]],
        explicit_root_instance_key: Optional[Tuple[str, Optional[int]]],
        root_spell_id: Optional[str],
) -> Tuple[str, Optional[int]]:
    """
    Resolve the root instance key from the manifest, rows, or root spell id.
    """
    if explicit_root_instance_key is not None:
        return (
            explicit_root_instance_key[0],
            explicit_root_instance_key[1],
        )
    if root_spell_id is not None:
        for row in rows:
            instance_key = row["instance_key"]
            if instance_key[0] == root_spell_id and instance_key[1] is None:
                return (instance_key[0], instance_key[1])
        for row in rows:
            instance_key = row["instance_key"]
            if instance_key[0] == root_spell_id:
                return (instance_key[0], instance_key[1])
    raise RuntimeError(
        "generalized no-overrides lane could not resolve a root "
        "instance key."
    )
