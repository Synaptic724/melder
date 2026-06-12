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
    inner_source = emit_step_plan_source(
        rows=rows,
        root_instance_key=resolved_root_instance_key,
    )
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
        root_instance_key: Tuple[str, Any],
) -> str:
    """
    Emit the inner no-overrides step-plan executor source from manifest rows.

    Contract:
        - Pure function of row data plus the root key's POSITION (the emitted
          source embeds step indices only, never identity values, so factory
          sharing across same-shape spells is preserved).
        - Faithful port of the legacy step-plan emission semantics (existence
          routing, lock disciplines, registration stores, inlined common-shape
          constructors) with reuse reads inlined as direct `_creations.get`
          dict reads.
        - LOCALS MODE: when every step is inlinable and every dependency key
          resolves to an emitted step, step results live in per-step local
          variables and dependency reads compile to direct local loads - no
          `instance_results` dict, no tuple-key hashing, and no runtime root
          presence check (root assignment is statically guaranteed).
        - DICT MODE: any generic-constructor step falls back to the
          `instance_results` dict so `_construct_spell_instance` keeps its
          full recipe surface.
    """
    key_to_step_index: Dict[Any, int] = {}
    for step_index, row in enumerate(rows):
        key_to_step_index[tuple(row["instance_key"])] = step_index

    locals_mode = True
    normalized_root_key = (root_instance_key[0], root_instance_key[1])
    if normalized_root_key not in key_to_step_index:
        locals_mode = False
    if locals_mode:
        for row in rows:
            inlinable_params = row_inlinable_common_shape(row)
            if inlinable_params is None:
                locals_mode = False
                break
            for _param_name, dependency_key in inlinable_params:
                dependency_key_tuple = (
                    dependency_key[0],
                    dependency_key[1],
                )
                if dependency_key_tuple not in key_to_step_index:
                    locals_mode = False
                    break
            if not locals_mode:
                break

    lines = [
        f"def {EXECUTOR_NAME}(",
        "        caller_creations=None,",
        "        owner_creations=None,",
        "        caller_creations_lock_held=False,",
        "        steps=steps,",
        "        step_spells=step_spells,",
        "        step_spell_ids=step_spell_ids,",
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
    ]
    if not locals_mode:
        lines.append("    instance_results = {}")
    # Hoist the caller_creations guard: it is call-constant, so checking it
    # once replaces the per-step re-checks the CALLER/SPELLSPACE routing
    # used to emit (6-7 redundant branches per body on the gauntlet graph).
    if any(
            row["creations_target_kind"]
            in (
                SpellGeneralizedCodegenPlanTargetKind.CALLER,
                SpellGeneralizedCodegenPlanTargetKind.SPELLSPACE,
            )
            for row in rows
    ):
        lines.extend([
            "    if caller_creations is None:",
            "        raise RuntimeError(",
            "            \"No-overrides codegen CALLER/SPELLSPACE execution requires caller_creations.\"",
            "        )",
        ])
    for step_index, row in enumerate(rows):
        _append_step_resolution_source(
            lines=lines,
            step_index=step_index,
            row=row,
            key_to_step_index=key_to_step_index if locals_mode else None,
        )
    if locals_mode:
        lines.append(
            f"    return instance_{key_to_step_index[normalized_root_key]}"
        )
    else:
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
        key_to_step_index: Optional[Dict[Any, int]] = None,
) -> None:
    """
    Append emitted source for one step from its manifest row.

    Contract:
        - When `key_to_step_index` is supplied (locals mode), step results
          are plain locals: no `instance_results` stores are emitted and
          inlined constructor dependencies compile to direct local loads.
    """
    existence = Existence[row["existence"]]
    inlinable_params = row_inlinable_common_shape(row)
    # Bind-time spell truth stamped by the manifest builder; disposal facts
    # compose into the spell fingerprint, so this can never go stale without
    # rolling the spell version (and with it, this manifest).
    has_disposal_methods = bool(row["spell_has_disposal_methods"])
    needs_register_block = not (
        existence is Existence.many and not has_disposal_methods
    )

    # Emit only the aliases this step's branches actually read. existence_N
    # died with the inlined reuse reads; plan_step_N exists only for the
    # generic constructor path; disposal aliases exist only when a register
    # block is emitted; many-without-disposal needs no spell_id at all.
    if inlinable_params is None:
        lines.append(f"    plan_step_{step_index} = steps[{step_index}]")
    if (
            inlinable_params is not None
            or row["creations_target_kind"]
            == SpellGeneralizedCodegenPlanTargetKind.OWNER
            or existence is not Existence.many
    ):
        lines.append(f"    spell_{step_index} = step_spells[{step_index}]")
    if existence is not Existence.many or needs_register_block:
        lines.append(
            f"    spell_id_{step_index} = step_spell_ids[{step_index}]"
        )
    if needs_register_block and has_disposal_methods:
        lines.append(
            f"    disposal_methods_{step_index} = "
            f"step_disposal_methods[{step_index}]"
        )
    if inlinable_params and key_to_step_index is None:
        lines.append(
            f"    step_dep_keys_{step_index} = step_dep_keys[{step_index}]"
        )
    _append_creations_target_source(
        lines=lines,
        step_index=step_index,
        target_kind=row["creations_target_kind"],
        # many-without-disposal steps are pure constructor calls: no
        # registration block, no lock, so their creations alias is dead.
        needs_creations_alias=not (
            existence is Existence.many and not has_disposal_methods
        ),
    )

    if existence is Existence.many:
        _emit_construct_instance(
            lines=lines,
            step_index=step_index,
            inlinable_params=inlinable_params,
            indent="    ",
            key_to_step_index=key_to_step_index,
        )
        if has_disposal_methods:
            # Disposal presence is emit-time row truth, so the lock and the
            # registration stores are emitted only when registration actually
            # happens; disposal-free many steps pay zero lock cycles here.
            lines.append(f"    with creations_{step_index}._lock:")
            _append_register_source(
                lines=lines,
                step_index=step_index,
                indent="        ",
                existence=existence,
                has_disposal_methods=has_disposal_methods,
            )
        if key_to_step_index is None:
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
            key_to_step_index=key_to_step_index,
        )
        _append_register_source(
            lines=lines,
            step_index=step_index,
            indent="                ",
            existence=existence,
            has_disposal_methods=has_disposal_methods,
        )
        if key_to_step_index is None:
            lines.append(
                f"    instance_results[step_instance_keys[{step_index}]] = instance_{step_index}"
            )
        return

    if row["use_spell_lock_hint"]:
        # The lock-mode decision is only consumed on a MISS, so it is
        # computed inside the miss branch: warm hits (singletons after
        # cycle #1) skip the two reads and the compare entirely.
        lines.extend([
            (
                f"    instance_{step_index} = "
                f"creations_{step_index}._creations.get(spell_id_{step_index})"
            ),
            f"    if instance_{step_index} is None:",
            f"        use_spell_lock_{step_index} = not (",
            "            caller_creations_lock_held",
            f"            and creations_{step_index} is caller_creations",
            "        )",
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
            key_to_step_index=key_to_step_index,
        )
        lines.append(f"                    with creations_{step_index}._lock:")
        _append_register_source(
            lines=lines,
            step_index=step_index,
            indent="                        ",
            existence=existence,
            has_disposal_methods=has_disposal_methods,
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
            key_to_step_index=key_to_step_index,
        )
        _append_register_source(
            lines=lines,
            step_index=step_index,
            indent="                    ",
            existence=existence,
            has_disposal_methods=has_disposal_methods,
        )
        if key_to_step_index is None:
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
        has_disposal_methods=has_disposal_methods,
    )
    if key_to_step_index is None:
        lines.append(
            f"    instance_results[step_instance_keys[{step_index}]] = instance_{step_index}"
        )


def _append_creations_target_source(
        *,
        lines: list,
        step_index: int,
        target_kind: int,
        needs_creations_alias: bool = True,
) -> None:
    """
    Append static creations-target routing source for one step.

    Contract:
        - `needs_creations_alias=False` (caller/spellspace lanes only)
          suppresses the `creations_N` local for steps whose emitted body
          never reads it; OWNER routing always emits because the alias IS
          the routing result and the branch carries a real guard.
    """
    if target_kind in (
            SpellGeneralizedCodegenPlanTargetKind.CALLER,
            SpellGeneralizedCodegenPlanTargetKind.SPELLSPACE,
    ):
        # The None guard is hoisted to the top of the emitted body (it is
        # call-constant); steps that never read their creations alias
        # (many-without-disposal: pure constructor, no registration and no
        # lock) skip the dead assignment entirely.
        if needs_creations_alias:
            lines.append(f"    creations_{step_index} = caller_creations")
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
        key_to_step_index: Optional[Dict[Any, int]] = None,
) -> None:
    """
    Append construction source for one step at `indent`.

    Contract:
        - In locals mode (`key_to_step_index` supplied), dependency arguments
          compile to direct per-step local loads instead of tuple-keyed
          `instance_results` reads.
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
        for arg_index, (param_name, dependency_key) in enumerate(
                inlinable_params,
        ):
            if key_to_step_index is not None:
                dependency_step_index = key_to_step_index[
                    (dependency_key[0], dependency_key[1])
                ]
                lines.append(
                    f"{indent}        {param_name}="
                    f"instance_{dependency_step_index},"
                )
            else:
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
        has_disposal_methods: bool,
) -> None:
    """
    Append inline registration stores specialized for one existence mode.

    Contract:
        - Emits direct `_creations` / `_disposable_creations` stores instead
          of `add_creation` / `add_many_creations` calls. The store methods
          are lock-free with caller-held locking, and every branch inside
          them is decided by fingerprint-stable facts (existence, disposal),
          so the call is pure dispatch overhead on this path.
        - The legacy duplicate-key guard is intentionally not emitted: every
          caller registers under `creations._lock` immediately after a locked
          re-check found no live entry, and disposal/live slots are co-written
          only by this path, so duplicates are structurally impossible here.
        - The `many` slot is always a list for this spell id because existence
          is fingerprint-stable; the legacy non-list slot guard is likewise
          structurally unreachable.
    """
    if existence in (
            Existence.unique,
            Existence.unique_per_conduit,
            Existence.unique_per_conduit_cluster,
            Existence.unique_per_conduit_lineage,
            Existence.unique_per_spell_space,
    ):
        lines.append(
            f"{indent}creations_{step_index}._creations"
            f"[spell_id_{step_index}] = instance_{step_index}"
        )
        if has_disposal_methods:
            lines.append(
                f"{indent}creations_{step_index}._disposable_creations"
                f"[spell_id_{step_index}] = "
                f"(instance_{step_index}, list(disposal_methods_{step_index}))"
            )
        return

    if existence is Existence.many:
        # Callers emit this block only when disposal truth is present.
        lines.extend([
            (
                f"{indent}many_live_{step_index} = "
                f"creations_{step_index}._creations.get(spell_id_{step_index})"
            ),
            f"{indent}if many_live_{step_index} is None:",
            f"{indent}    many_live_{step_index} = []",
            (
                f"{indent}    creations_{step_index}._creations"
                f"[spell_id_{step_index}] = many_live_{step_index}"
            ),
            f"{indent}many_live_{step_index}.append(instance_{step_index})",
            (
                f"{indent}many_disposable_{step_index} = "
                f"creations_{step_index}._disposable_creations"
                f".get(spell_id_{step_index})"
            ),
            f"{indent}if many_disposable_{step_index} is None:",
            f"{indent}    many_disposable_{step_index} = []",
            (
                f"{indent}    creations_{step_index}._disposable_creations"
                f"[spell_id_{step_index}] = many_disposable_{step_index}"
            ),
            (
                f"{indent}many_disposable_{step_index}.append("
                f"(instance_{step_index}, list(disposal_methods_{step_index})))"
            ),
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
