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

from types import FunctionType
from typing import Any, Callable, Dict, Optional, Sequence, Tuple

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.codegen_creation_schema_helpers import (
    CodegenCreationSchemaHelpers,
)
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
    "step_owner_creations",
    "step_targets",
    "step_contract_values",
    "step_positional_args",
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
    "_raise_meld_construction_error": raise_meld_construction_error,
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
        - Contract override payload references in the rows are resolved to the
          consumer's LIVE descriptor values first (`resolve_contract_payload_rows`),
          so every binding and runtime row below carries the object itself, by
          identity, in-process and after a cache load alike (2026-09-26).
        - Emission is a pure function of rows/schema plus each step's
          positional-dependency prefix. Live spells are touched only by
          bindings construction and by `rows_positional_dependency_names`,
          which reads each step target's construction path, never its
          annotations.
        - Transient unrolled emission is used exactly under the legacy rule:
          schema present, every step `many`, no step registering, and all
          call modes supported by the unrolled builder.
        - One compile + one exec per source shape per process via the factory
          cache; one factory call here.

    Raises:
        RuntimeError:
            When rows are invalid or the root instance key is unresolvable.
    """
    rows = resolve_contract_payload_rows(rows=rows, spell_lookup=spell_lookup)
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
        positional_dependency_names=rows_positional_dependency_names(
            rows=rows,
            spell_lookup=spell_lookup,
        ),
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
        positional_dependency_names: Optional[Tuple[Tuple[str, ...], ...]] = None,
) -> str:
    """
    Emit the inner no-overrides step-plan executor source from manifest rows.

    Contract:
        - Pure function of row data plus the root key's POSITION (the emitted
          source embeds step indices only, never identity values, so factory
          sharing across same-shape spells is preserved) and, when supplied,
          each step's positional-dependency prefix.
        - POSITIONAL PREFIX: `positional_dependency_names` holds one tuple per
          row (built by `rows_positional_dependency_names`). A step passes the
          named dependency values positionally, in that order, ahead of its
          remaining keyword arguments; every value still binds to the
          parameter it was resolved for. `None` keeps every argument keyword,
          which is what a caller without live spells gets. A tuple whose
          length differs from `rows` raises RuntimeError.
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
    _require_positional_names_per_row(
        rows=rows,
        positional_dependency_names=positional_dependency_names,
    )
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
            for _param_name, dependency_keys in inlinable_params:
                for dependency_key in dependency_keys:
                    dependency_key_tuple = (
                        dependency_key[0],
                        dependency_key[1],
                    )
                    if dependency_key_tuple not in key_to_step_index:
                        locals_mode = False
                        break
                if not locals_mode:
                    break
            if not locals_mode:
                break

    # Step-constant aliases execute ONCE at factory-call time (per
    # hydration) and reach the executor as CLOSURE CELLS: zero per-call
    # setup, LOAD_DEREF at use sites, and - decisive under free-threading -
    # no per-call incref/decref sweep over shared spells/stores the way
    # signature defaults are filled. Probe-measured: the default-param form
    # of this hoist was a wash (fill cost == removed bytecode).
    lines = _step_alias_hoist_lines(
        rows=rows,
        locals_mode=locals_mode,
    )
    lines.append(f"def {EXECUTOR_NAME}(meld):")
    if not locals_mode:
        lines.append("    instance_results = {}")
    for step_index, row in enumerate(rows):
        _append_step_resolution_source(
            lines=lines,
            step_index=step_index,
            row=row,
            key_to_step_index=key_to_step_index if locals_mode else None,
            positional_names=(
                positional_dependency_names[step_index]
                if positional_dependency_names is not None
                else ()
            ),
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
        positional_names: Tuple[str, ...] = (),
) -> None:
    """
    Append emitted source for one step from its manifest row.

    Contract:
        - When `key_to_step_index` is supplied (locals mode), step results
          are plain locals: no `instance_results` stores are emitted and
          inlined constructor dependencies compile to direct local loads.
        - `positional_names` is the step's positional-dependency prefix; it is
          forwarded unchanged to every constructor emission for this step.
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

    # Step-constant aliases (spell_N / spell_id_N / disposal_methods_N /
    # plan_step_N / step_dep_keys_N / instance_key_N) are no longer emitted
    # here as per-call body statements: they ride the executor SIGNATURE as
    # per-slot default parameters built by `_step_alias_signature_params`,
    # which mirrors the exact per-branch read conditions (single source of
    # truth). existence_N died earlier with the inlined reuse reads.
    _append_creations_target_source(
        lines=lines,
        step_index=step_index,
        existence=existence,
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
            row=row,
            positional_names=positional_names,
        )
        if has_disposal_methods:
            # `many` is transient (a new instance per meld, never cached), so
            # there is no build guard. The append goes through
            # `add_many_creations`, which takes the store lock as a leaf (the
            # former lockless inline append could lose a first-use bucket).
            _append_register_source(
                lines=lines,
                step_index=step_index,
                indent="    ",
                existence=existence,
                has_disposal_methods=has_disposal_methods,
            )
        if key_to_step_index is None:
            lines.append(
                f"    instance_results[instance_key_{step_index}] = instance_{step_index}"
            )
        return

    if existence in (
            Existence.unique_per_conduit,
            Existence.unique_per_spell_space,
            # cluster/lineage are CALLER-routed (meld supplies the leader /
            # lineage-root store as caller_creations), so they take the same
            # reuse-read + slot-guard path as unique_per_conduit -- which
            # correctly threads key_to_step_index for locals mode. (The fall-
            # through 'plain' branch below does not, and is unreachable.)
            Existence.unique_per_conduit_cluster,
            Existence.unique_per_conduit_lineage,
    ):
        lines.extend([
            (
                f"    instance_{step_index} = "
                f"creations_{step_index}._creations.get(spell_id_{step_index})"
            ),
            f"    if instance_{step_index} is None:",
            # Build-once under this slot's guard; `add_creation` takes the
            # store lock itself as a leaf (see Creations.slot_guard).
            f"        with (creations_{step_index}._slot_guards.get(spell_id_{step_index}) or creations_{step_index}.slot_guard(spell_id_{step_index})):",
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
            row=row,
            positional_names=positional_names,
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
                f"    instance_results[instance_key_{step_index}] = instance_{step_index}"
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
            f"        use_spell_lock_{step_index} = True",
            f"        if use_spell_lock_{step_index}:",
            # `unique` has one slot (its owner store), so Spell._lock is its
            # slot guard; the recheck is a plain dict read and `add_creation`
            # takes the store lock itself as a leaf.
            f"            with spell_{step_index}._lock:",
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
            row=row,
            positional_names=positional_names,
        )
        _append_register_source(
            lines=lines,
            step_index=step_index,
            indent="                    ",
            existence=existence,
            has_disposal_methods=has_disposal_methods,
        )
        lines.extend([
            "        else:",
            f"            with (creations_{step_index}._slot_guards.get(spell_id_{step_index}) or creations_{step_index}.slot_guard(spell_id_{step_index})):",
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
            row=row,
            positional_names=positional_names,
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
                f"    instance_results[instance_key_{step_index}] = instance_{step_index}"
            )
        return

    lines.extend([
        (
            f"    instance_{step_index} = "
            f"creations_{step_index}._creations.get(spell_id_{step_index})"
        ),
        f"    if instance_{step_index} is None:",
        f"        with (creations_{step_index}._slot_guards.get(spell_id_{step_index}) or creations_{step_index}.slot_guard(spell_id_{step_index})):",
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
        row=row,
        positional_names=positional_names,
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
            f"    instance_results[instance_key_{step_index}] = instance_{step_index}"
        )


def _append_creations_target_source(
        *,
        lines: list,
        step_index: int,
        existence: Existence,
        needs_creations_alias: bool = True,
) -> None:
    """
    Append source resolving this step's creations store off the meld.

    Contract:
        - Routes by the step's compile-time existence to the store the meld
          front doors select: `many` -> innermost active scope (spellspace store
          when melded through a SpellSpaceMeld, else conduit store);
          `unique_per_conduit` -> conduit store; `unique_per_spell_space` ->
          spellspace store; `unique_per_conduit_lineage` -> lineage-root store;
          `unique_per_conduit_cluster` -> elected-leader store; `unique` -> the
          binding owner's `spell._owner_creations`.
        - `needs_creations_alias=False` (many-without-disposal: pure
          constructor, no registration, no lock) skips the alias entirely.
    """
    if not needs_creations_alias:
        return
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
        # The owner store rides the signature as `creations_N` (see
        # `_step_alias_signature_params`): the per-call shared attr read on
        # the spell object was the last hydration-constant load in this walk.
        return

    raise RuntimeError(
        f"Unsupported existence for generalized no-overrides creations routing: "
        f"{existence!r}"
    )


def _emit_construct_instance(
        *,
        lines: list,
        step_index: int,
        inlinable_params: Optional[Tuple[Tuple[str, Any], ...]],
        indent: str,
        key_to_step_index: Optional[Dict[Any, int]] = None,
        row: Optional[Dict[str, Any]] = None,
        positional_names: Tuple[str, ...] = (),
) -> None:
    """
    Append construction source for one step at `indent`.

    Contract:
        - In locals mode (`key_to_step_index` supplied), dependency arguments
          compile to direct per-step local loads instead of tuple-keyed
          `instance_results` reads.
        - Contract-payload keywords compile to `name=contract_values_N[j]`
          constants and an effective positional payload compiles to a leading
          `*positional_N` splat (values ride bindings; see
          `_row_contract_call_extras`). Keyword ORDER is deps-then-payload;
          the generic path keeps an overridden name at its original dict
          position instead - visible only to constructors introspecting
          `**kwargs` insertion order for payload-overridden names.
        - Dependency values named in `positional_names` compile to leading
          positional arguments in that order, which is the target's own
          parameter order (see `positional_dependency_names`); every other
          dependency stays a keyword. A step with a `*positional_N` payload
          splat ignores the prefix, because the splat already owns the
          leading positions. Why: on CPython 3.14 a positional class call
          takes the interpreter's specialized allocate-and-init path, while a
          keyword call builds a kwargs dict and goes through the generic
          `type.__call__` route (3.14t: 77 ns vs 170 ns for a two-parameter
          class).

    Raises:
        RuntimeError:
            When a `positional_names` entry is not an emitted dependency of
            this step.
    """
    if inlinable_params is None:
        lines.append(
            f"{indent}instance_{step_index} = _construct_spell_instance("
            f"plan_step=plan_step_{step_index}, "
            f"instance_results=instance_results)"
        )
        return
    payload_names: Tuple[str, ...] = ()
    positional: Optional[Any] = None
    collection_param_names: frozenset[str] = frozenset()
    if row is not None:
        extras = _row_contract_call_extras(row)
        if extras is not None:
            payload_names, positional = extras
        collection_param_names = frozenset(row["collection_param_names"])
    has_call_args = bool(
        inlinable_params or payload_names or positional is not None
    )
    lines.append(f"{indent}try:")
    if has_call_args:
        lines.append(
            f"{indent}    instance_{step_index} = target_{step_index}("
        )
        if positional is not None:
            lines.append(f"{indent}        *positional_{step_index},")
        # Signature-order prefix first (positional), then every other
        # dependency by keyword, then payload keywords. A payload splat owns
        # the leading positions, so it disables the prefix.
        leading_names = positional_names if positional is None else ()
        leading_values: Dict[str, str] = {}
        keyword_lines: list = []
        # Flat cursor over the row's flattened dependency-key tuple: single-dep
        # NON-collection params compile to one scalar reference; collection-DI
        # params compile to an order-preserving list literal REGARDLESS of
        # member count (parity with the generic `_build_kwargs_no_overrides`:
        # collection socket -> list even with 1 member; >=2 deps -> list).
        flat_dep_cursor = 0
        for param_name, dependency_keys in inlinable_params:
            if key_to_step_index is not None:
                references = [
                    f"instance_{key_to_step_index[(key[0], key[1])]}"
                    for key in dependency_keys
                ]
            else:
                references = [
                    f"instance_results[step_dep_keys_{step_index}"
                    f"[{flat_dep_cursor + offset}]]"
                    for offset in range(len(dependency_keys))
                ]
            flat_dep_cursor += len(dependency_keys)
            if (
                    len(dependency_keys) == 1
                    and param_name not in collection_param_names
            ):
                value_expression = references[0]
            else:
                value_expression = "[" + ", ".join(references) + "]"
            if param_name in leading_names:
                leading_values[param_name] = value_expression
            else:
                keyword_lines.append(
                    f"{indent}        {param_name}={value_expression},"
                )
        for leading_name in leading_names:
            if leading_name not in leading_values:
                raise RuntimeError(
                    f"Positional prefix name '{leading_name}' is not an "
                    f"emitted dependency of step {step_index}."
                )
            lines.append(f"{indent}        {leading_values[leading_name]},")
        lines.extend(keyword_lines)
        for payload_index, payload_name in enumerate(payload_names):
            lines.append(
                f"{indent}        {payload_name}"
                f"=contract_values_{step_index}[{payload_index}],"
            )
        lines.append(f"{indent}    )")
    else:
        lines.append(
            f"{indent}    instance_{step_index} = target_{step_index}()"
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
    Append registration calls specialized for one existence mode.

    Contract:
        - Callers hold only the slot's build lock (slot guard, or Spell._lock
          for unique) around this block, never the store lock. (Before
          2026-09-25 the caller held the store lock across the whole build,
          and the disposal-bearing `many` append ran with no lock at all.)
        - Singleton entries WITHOUT disposal methods publish with one direct
          `_creations` store: the build lock excludes every other publisher of
          the key and a single dict store is atomic, so no store lock and no
          duplicate check are needed (the same reasoning as the lock-free
          branch of `Creations.add_creation`; measured to matter on the cold
          path). A store retired by `cleanup()` fails on its missing registry.
        - Singleton entries WITH disposal methods, and every disposal-bearing
          `many` append, go through `add_creation` / `add_many_creations`,
          which take the store lock as a LEAF so the live and disposal writes
          land together, and refuse a store cleaned during the build.
        - Both storage shapes retain the bound Spell disposal list directly,
          matching Creations registration without allocating a copied policy.
    """
    disposal_arguments = (
        [
            f"{indent}    has_disposal_methods=True,",
            f"{indent}    disposal_methods=disposal_methods_{step_index},",
        ]
        if has_disposal_methods
        else []
    )
    if existence in (
            Existence.unique,
            Existence.unique_per_conduit,
            Existence.unique_per_conduit_cluster,
            Existence.unique_per_conduit_lineage,
            Existence.unique_per_spell_space,
    ):
        if not has_disposal_methods:
            lines.append(
                f"{indent}creations_{step_index}._creations"
                f"[spell_id_{step_index}] = instance_{step_index}"
            )
            return
        lines.extend([
            f"{indent}creations_{step_index}.add_creation(",
            f"{indent}    spell_id_{step_index},",
            f"{indent}    instance_{step_index},",
            *disposal_arguments,
            f"{indent})",
        ])
        return

    if existence is Existence.many:
        # Callers emit this block only when disposal truth is present.
        lines.extend([
            f"{indent}creations_{step_index}.add_many_creations(",
            f"{indent}    spell_id_{step_index},",
            f"{indent}    instance_{step_index},",
            *disposal_arguments,
            f"{indent})",
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
        - Returns (param_name, dependency_key_tuple) pairs; every entry is a
          TUPLE of keys (single-dep params carry a 1-tuple).
        - Callable, non-existing-creation spells with no contract payload and
          no positional override are inlinable; collection-DI params are
          inlinable too - emission produces an order-preserving list literal,
          matching the generic `_build_kwargs_no_overrides` semantics exactly
          (collection socket -> list even with exactly 1 member; >=2 deps ->
          list; non-collection 1 dep -> scalar; 0 deps -> `[]` for collection
          sockets, otherwise the parameter is omitted).
        - Requires the family row flags `spell_is_callable` and
          `spell_is_existing_creation`. Family manifest rows always carry
          them (the manifest builder stamps both), so access is direct; a
          missing flag is a row-contract violation and raises KeyError.
    """
    if not row["spell_is_callable"]:
        return None
    if row["spell_is_existing_creation"]:
        return None
    extras = _row_contract_call_extras(row)
    if extras is None:
        # Unrepresentable positional payload (non tuple/list): stay on the
        # generic path so the per-call MeldExecutionError timing is identical.
        return None
    payload_names, _positional = extras
    collection_param_names = frozenset(row["collection_param_names"])
    params = []
    for param_name, dependency_keys in row["dependency_resolution_order"]:
        if len(dependency_keys) == 0:
            if (
                    param_name in collection_param_names
                    and param_name not in payload_names
            ):
                # Zero-provider required collection socket: keep the entry so
                # emission renders an empty list literal (owner policy) - the
                # list-literal arm joins zero references into `[]`.
                params.append((param_name, ()))
            continue
        if param_name in payload_names:
            # Contract payload wins over the dependency value by name (the
            # generic kwargs builder overwrites after dep assembly), so the
            # dependency read is dead and emitting both keywords would be a
            # syntax error. The payload value is emitted instead.
            continue
        params.append((param_name, tuple(dependency_keys)))
    return tuple(params)


def positional_dependency_names(
        *,
        target: Any,
        dependency_param_names: Tuple[str, ...],
) -> Tuple[str, ...]:
    """
    Return the leading dependency parameters `target` receives by position.

    Purpose:
        Let emitted constructor calls pass dependency values positionally.
        On CPython 3.14 a positional class call takes the interpreter's
        specialized allocate-and-init path; a keyword call builds a kwargs
        dict and runs the generic `type.__call__` route (measured on 3.14t:
        77 ns vs 170 ns for a two-parameter class).

    Contract:
        - Qualifies only plain construction: `target` is a class whose
          metaclass keeps `type.__call__`, whose `__new__` is
          `object.__new__` (so it ignores the arguments), and whose
          `__init__` is a plain Python function. Anything else returns `()`
          and the step keeps its keyword call.
        - Reads parameter order from `__init__.__code__` - the function that
          actually receives the arguments - so a positional value binds to
          exactly the parameter the keyword would have named. Annotations,
          `__signature__` and wrapper metadata are never consulted or
          evaluated (a TYPE_CHECKING-only annotation cannot raise here).
        - Returns the longest prefix of the positional parameters (after
          `self`, positional-only included) whose every name is in
          `dependency_param_names`. The first parameter that is not a
          dependency - a default, an unresolved input, a payload name -
          ends the prefix, so no value can shift into another parameter.
          Keyword-only parameters are never in the prefix.
        - Pure: attribute reads only, no side effects.

    Args:
        target:
            The step's construction target (`Spell.spell`).
        dependency_param_names:
            Parameter names the step fills from resolved dependencies, as
            returned by `row_inlinable_common_shape`.

    Returns:
        Tuple[str, ...]: Prefix names in the target's parameter order; empty
        when the target does not qualify or its first parameter is not a
        dependency.
    """
    if not dependency_param_names or not isinstance(target, type):
        return ()
    if type(target).__call__ is not type.__call__:
        return ()
    if target.__new__ is not object.__new__:
        return ()
    initializer = target.__init__
    if type(initializer) is not FunctionType:
        return ()
    code = initializer.__code__
    prefix = []
    for parameter_name in code.co_varnames[1:code.co_argcount]:
        if parameter_name not in dependency_param_names:
            break
        prefix.append(parameter_name)
    return tuple(prefix)


def rows_positional_dependency_names(
        *,
        rows: Sequence[Dict[str, Any]],
        spell_lookup: Dict[str, Any],
) -> Tuple[Tuple[str, ...], ...]:
    """
    Compute each row's positional-dependency prefix from its live target.

    Contract:
        - One tuple per row, in row order, for `emit_step_plan_source` and
          `emit_specialized_step_plan_source`.
        - Non-inlinable rows (generic constructor, existing creation), rows
          with no dependency parameters and rows whose call carries a
          `*positional_N` payload splat get `()` without a spell lookup.
        - Every other row gets `positional_dependency_names` over its
          `Spell.spell`, with the dependency names from
          `row_inlinable_common_shape`.
        - Expects RESOLVED rows (`resolve_contract_payload_rows`), the same
          rows emission receives.

    Args:
        rows:
            Resolved manifest step rows for the no-overrides lane.
        spell_lookup:
            Spell id -> live Spell for every step row.

    Returns:
        Tuple[Tuple[str, ...], ...]: Positional prefix names per row.

    Raises:
        RuntimeError:
            When an inlinable row's spell is missing from `spell_lookup`.
    """
    names_by_row = []
    for row in rows:
        inlinable_params = row_inlinable_common_shape(row)
        if not inlinable_params:
            names_by_row.append(())
            continue
        _payload_names, positional = _row_contract_call_extras(row)
        if positional is not None:
            names_by_row.append(())
            continue
        spell = spell_lookup.get(row["spell_id"])
        if spell is None:
            raise RuntimeError(
                "Cannot compute the positional dependency prefix: spell "
                f"'{row['spell_id']}' is missing from spell_lookup."
            )
        names_by_row.append(positional_dependency_names(
            target=spell.spell,
            dependency_param_names=tuple(
                param_name for param_name, _keys in inlinable_params
            ),
        ))
    return tuple(names_by_row)


def _require_positional_names_per_row(
        *,
        rows: Sequence[Dict[str, Any]],
        positional_dependency_names: Optional[Tuple[Tuple[str, ...], ...]],
) -> None:
    """
    Fail fast when a positional-prefix tuple does not match the rows.

    Raises:
        RuntimeError:
            When `positional_dependency_names` is supplied with a length
            other than `len(rows)`.
    """
    if (
            positional_dependency_names is not None
            and len(positional_dependency_names) != len(rows)
    ):
        raise RuntimeError(
            "positional_dependency_names must hold exactly one entry per "
            f"row: {len(positional_dependency_names)} entries for "
            f"{len(rows)} rows."
        )


def _row_contract_call_extras(
        row: Dict[str, Any],
) -> Optional[Tuple[Tuple[str, ...], Optional[Any]]]:
    """
    Resolve one row's contract-call extras for inlined emission.

    Purpose:
        Make contract payloads and positional overrides inlinable: both are
        fingerprint-stable row constants, so paying the generic
        `_construct_spell_instance` path (dict assembly + per-dep tuple-hash
        reads + payload overwrite loop + `__args__` extraction + double
        splat) per call - and dragging the WHOLE graph into dict mode - was
        pure overhead.

    Contract:
        - Mirrors `_build_kwargs_no_overrides` + `_construct_spell_instance`
          exactly: payload items dedupe like `dict(items)` (first position,
          last value); the effective positional tuple is
          `contract_positional_override` unless a payload `__args__` item
          overwrites it (which the generic path skips only when
          `uses_positional_override` is set).
        - Returns None when the effective positional payload exists but is
          not a tuple/list: the generic path raises MeldExecutionError for
          that shape PER CALL, so such rows must stay on the generic path to
          preserve error timing and type.
        - Payload VALUES never appear in emitted source (identity-free
          emission); they ride the `step_contract_values` /
          `step_positional_args` bindings.
        - A row straight from a manifest may carry phase-9 REFERENCES in place
          of object values (2026-09-26); this helper reads only names and the
          positional container's shape, so it is correct on raw and on resolved
          rows alike. `_build_step_bindings` resolves the values before binding.

    Args:
        row: One manifest step row.

    Returns:
        Optional[Tuple[Tuple[str, ...], Optional[Any]]]: (payload parameter
        names in emission order, effective positional payload or None), or
        None when the row must stay on the generic constructor path.
    """
    payload_map: Dict[str, Any] = {}
    if row["has_contract_payload"]:
        for param_name, value in row["contract_payload_items"]:
            payload_map[param_name] = value
    positional = row["contract_positional_override"]
    if "__args__" in payload_map and not row["uses_positional_override"]:
        positional = payload_map["__args__"]
    if positional is not None and not isinstance(positional, (tuple, list)):
        return None
    payload_names = tuple(
        param_name for param_name in payload_map if param_name != "__args__"
    )
    return (payload_names, positional)


def _step_alias_hoist_lines(
        *,
        rows: Sequence[Dict[str, Any]],
        locals_mode: bool,
        skip_step_indexes: Any = frozenset(),
) -> list:
    """
    Build factory-level hoist statements for step-constant aliases.

    Purpose:
        Compute hydration-constant per-step aliases (spell_N, spell_id_N,
        disposal_methods_N, plan_step_N, step_dep_keys_N, instance_key_N,
        target_N, creations_N for `unique`, contract_values_N, positional_N)
        exactly ONCE per hydration: the lines run in the factory body before
        the executor `def`, so the executor closes over them as cells. Calls
        pay LOAD_DEREF at use sites and nothing at frame setup - unlike the
        earlier signature-default form, whose per-call default fill
        (pointer copy + incref per param, on shared objects, under
        free-threading) measured as a wash against the removed bytecode.

    Contract:
        - Single source of truth for alias existence: the conditions here
          mirror the per-branch reads emitted by `_append_step_resolution_
          source` exactly (plan_step: generic-constructor steps only; spell:
          inlinable OR owner-target OR non-many; spell_id: non-many OR
          register block; disposal_methods: register block with disposal;
          step_dep_keys: inlinable steps in dict mode only; target: inlinable
          steps; creations: `unique` steps; contract_values/positional: rows
          with inlinable contract extras), so hoist and body cannot drift
          independently.
        - `instance_key_N` is emitted for EVERY step in dict mode (including
          skipped/captured steps): every dict-mode step stores its result (or
          captured seed) under its instance key.
        - `skip_step_indexes` suppresses the branch aliases for steps whose
          resolution source is not emitted (the specialized emitter's
          captured steps).
        - Emitted lines are identity-free (binding names + integer indexes
          only), preserving factory-cache sharing by shape.

    Args:
        rows:
            Manifest step rows for the no-overrides lane.
        locals_mode:
            The emitter's locals-mode decision for this shape.
        skip_step_indexes:
            Step indexes whose resolution source is not emitted.

    Returns:
        list: Factory-level assignment lines (top-level indentation).
    """
    params: list = []
    for step_index, row in enumerate(rows):
        if not locals_mode:
            params.append(
                f"instance_key_{step_index} = step_instance_keys[{step_index}]"
            )
        if step_index in skip_step_indexes:
            continue
        existence = Existence[row["existence"]]
        inlinable_params = row_inlinable_common_shape(row)
        has_disposal_methods = bool(row["spell_has_disposal_methods"])
        needs_register_block = not (
            existence is Existence.many and not has_disposal_methods
        )
        if inlinable_params is None:
            params.append(
                f"plan_step_{step_index} = steps[{step_index}]"
            )
        if inlinable_params is not None:
            params.append(
                f"target_{step_index} = step_targets[{step_index}]"
            )
        if existence is Existence.unique:
            params.append(
                f"creations_{step_index} = step_owner_creations[{step_index}]"
            )
        if (
                inlinable_params is not None
                or row["creations_target_kind"]
                == SpellGeneralizedCodegenPlanTargetKind.OWNER
                or existence is not Existence.many
        ):
            params.append(
                f"spell_{step_index} = step_spells[{step_index}]"
            )
        if existence is not Existence.many or needs_register_block:
            params.append(
                f"spell_id_{step_index} = step_spell_ids[{step_index}]"
            )
        if needs_register_block and has_disposal_methods:
            params.append(
                f"disposal_methods_{step_index} = step_disposal_methods[{step_index}]"
            )
        if inlinable_params and not locals_mode:
            params.append(
                f"step_dep_keys_{step_index} = step_dep_keys[{step_index}]"
            )
        if inlinable_params is not None:
            extras = _row_contract_call_extras(row)
            if extras is not None:
                payload_names, positional = extras
                if payload_names:
                    params.append(
                        f"contract_values_{step_index} = step_contract_values[{step_index}]"
                    )
                if positional is not None:
                    params.append(
                        f"positional_{step_index} = step_positional_args[{step_index}]"
                    )
    return params


def _row_contract_value_binding(row: Dict[str, Any]) -> Tuple[Any, ...]:
    """
    Build one row's contract-payload value tuple for bindings.

    Contract:
        - Values are ordered exactly like the emission-order payload names
          from `_row_contract_call_extras` (dict(items) semantics: first
          position, last value; `__args__` excluded), so
          `contract_values_N[j]` pairs with the j-th emitted payload keyword.
        - Rows without an inlinable payload contribute an empty tuple.
        - Expects a RESOLVED row (`_build_step_bindings` replaces phase-9
          references with live values first); on a raw manifest row the tuple
          would carry the references themselves.
    """
    extras = _row_contract_call_extras(row)
    if extras is None:
        return ()
    payload_names, _positional = extras
    if not payload_names:
        return ()
    payload_map: Dict[str, Any] = dict(row["contract_payload_items"])
    return tuple(payload_map[name] for name in payload_names)


def resolve_contract_payload_rows(
        *,
        rows: Sequence[Dict[str, Any]],
        spell_lookup: Dict[str, Any],
) -> Tuple[Dict[str, Any], ...]:
    """
    Replace the phase-9 references in manifest rows with the consumer's live values.

    Purpose:
        The single resolution point of the manifest-first no-overrides lane
        (2026-09-26): rows persist a contract override payload entry as a
        scalar or as a reference to the consumer's descriptor, and this turns
        every reference back into the object the descriptor holds right now,
        before runtime rows, bindings or specialization read the rows.

    Contract:
        - Rows without a payload and without a positional override are returned
          as they are (same object); every other row is a shallow copy with
          `contract_payload_items` and `contract_positional_override` resolved
          through `CodegenCreationSchemaHelpers.resolve_contract_payload_row_values`.
        - `spell_lookup` must contain the consumer named by each reference; it
          always does for a lane's own step spells, because the consumer is a
          step of the same lane.
        - Descriptor reads are memoized per call; the input rows are never
          mutated.

    Raises:
        RuntimeError:
            When a reference cannot be resolved (consumer missing from
            `spell_lookup`, descriptor without a payload, key absent).
    """
    descriptor_cache: Dict[Tuple[str, str], Any] = {}
    resolved_rows = []
    for row in rows:
        if not row["has_contract_payload"] and row["contract_positional_override"] is None:
            resolved_rows.append(row)
            continue
        items, positional = CodegenCreationSchemaHelpers.resolve_contract_payload_row_values(
            row, spell_lookup, descriptor_cache,
        )
        resolved_row = dict(row)
        resolved_row["contract_payload_items"] = items
        resolved_row["contract_positional_override"] = positional
        resolved_rows.append(resolved_row)
    return tuple(resolved_rows)


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

    Contract:
        - Expects RESOLVED rows (`resolve_contract_payload_rows`): the
          `step_contract_values` and `step_positional_args` bindings are read
          straight off the rows, so a raw manifest row would bind its phase-9
          references instead of the live values.
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
                for _param_name, dependency_keys in (
                    row_inlinable_common_shape(row) or ()
                )
                for dependency_key in dependency_keys
            )
            for row in rows
        ),
        # Frozen at hydration by the same invalidation envelope as the spell
        # objects themselves: `_owner_creations` is reassigned only through
        # the ownership-recording path and `Spell.spell` never changes on a
        # live spell; both paths run `_cleanup_creation_context()` first,
        # which cuts every route to this executor (audited 2026-07-02).
        "step_owner_creations": tuple(
            runtime_row.spell._owner_creations
            for runtime_row in runtime_rows
        ),
        "step_targets": tuple(
            runtime_row.spell.spell
            for runtime_row in runtime_rows
        ),
        "step_contract_values": tuple(
            _row_contract_value_binding(row)
            for row in rows
        ),
        "step_positional_args": tuple(
            (_row_contract_call_extras(row) or ((), None))[1]
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


# ---------------------------------------------------------------------------
# Singleton warm-tail specialization (patch lane:
# generalized_singleton_specialization_2026_07_01)
# ---------------------------------------------------------------------------

SPECIALIZED_EXECUTOR_NAME = (
    "_specialized_no_overrides_codegen_creation_executor"
)

_SPECIALIZED_FACTORY_SOURCE_NAME = (
    "<melder_generalized_no_overrides_specialized_factory>"
)


def select_specializable_step_indexes(
        rows: Sequence[Dict[str, Any]],
) -> Tuple[int, ...]:
    """
    Return the step indexes eligible for singleton warm-tail capture.

    Purpose:
        Identify the OWNER-store `unique` steps whose live instances may be
        closed over by a specialized executor body after first construction.

    Contract:
        - Capture set is `Existence.unique` ONLY. The owner store is
          frame-global and conduit-independent, so a spell-owned executor that
          serves every conduit may capture it. Caller-varying stores
          (`unique_per_conduit`, spellspace, lineage, cluster) and transient
          `many` steps are never selected.
        - Pure function of manifest row data; no live spells consulted.

    Args:
        rows:
            Manifest step rows for the no-overrides lane.

    Returns:
        Tuple[int, ...]: Ascending step indexes eligible for capture. Empty
        when the graph has no `unique` steps (callers must then skip
        specialization entirely).
    """
    unique_name = Existence.unique.name
    return tuple(
        step_index
        for step_index, row in enumerate(rows)
        if row["existence"] == unique_name
    )


def emit_specialized_step_plan_source(
        *,
        rows: Sequence[Dict[str, Any]],
        captured_step_indexes: Tuple[int, ...],
        root_instance_key: Tuple[str, Any],
        positional_dependency_names: Optional[Tuple[Tuple[str, ...], ...]] = None,
) -> str:
    """
    Emit the specialized no-overrides executor source for one capture shape.

    Purpose:
        Replace each captured `unique` step's warm walk (spell tuple load +
        `_owner_creations` attr read + shared `_creations` dict get + None
        branch) with one frame-local int compare, while emitting every
        non-captured step exactly as the generic emitter does.

    Contract:
        - Pure function of rows plus capture POSITIONS: the source embeds step
          indexes and per-slot binding names only, never identity values, so
          the executor factory cache shares one compiled factory across every
          spell with the same shape and capture set.
        - Guard prologue: per captured step,
          `cap_spell_K._door_epoch != cap_epoch_K` tail-calls the deopt
          target `_deopt_notify` (deopt: slower, never wrong). The prologue
          is wrapped in one try/except AttributeError so a cleaned captured
          spell also deopts to the canonical generic behavior instead of
          leaking a slot error from this lane. `_deopt_notify` is a factory
          binding: the generic inner directly, or a counting wrapper that
          re-pins the plain doors after repeated misses (see the hydrator's
          3-strike deopt re-pin) - either way the source stays identity-free
          and one factory serves every (shape, capture-set).
        - Captured instances arrive as per-slot default parameters
          (`cap_inst_K`) and are re-exposed to downstream step emission via
          `instance_K` locals (locals mode) or `instance_results` stores (dict
          mode), so the existing per-step emitters compile against them with
          zero changes.
        - Root-is-captured collapses the tail to `return cap_inst_K` with no
          alias emission for the root slot.
        - Store-clear soundness is NOT guarded here by design: owner stores
          clear only on teardown paths already blocked by lineage/validity
          gating before any executor runs (see patch lane architecture doc,
          Guard Policy).

    Args:
        rows:
            Manifest step rows for the no-overrides lane.
        captured_step_indexes:
            Ascending step indexes to capture; must be non-empty and must all
            reference `unique` rows (validated).
        root_instance_key:
            Resolved root instance key for the lane.
        positional_dependency_names:
            Optional per-row positional-dependency prefixes (see
            `emit_step_plan_source`); non-captured steps receive theirs so
            they compile exactly as in the generic body.

    Returns:
        str: Identity-free specialized executor source (one `def` statement).

    Raises:
        RuntimeError:
            When the capture set is empty or references a non-`unique` row,
            or when `positional_dependency_names` does not hold one entry per
            row.
    """
    _require_positional_names_per_row(
        rows=rows,
        positional_dependency_names=positional_dependency_names,
    )
    if not captured_step_indexes:
        raise RuntimeError(
            "specialized emission requires a non-empty capture set; callers "
            "must skip specialization when no `unique` steps exist."
        )
    captured_set = set(captured_step_indexes)
    unique_name = Existence.unique.name
    for step_index in captured_step_indexes:
        if rows[step_index]["existence"] != unique_name:
            raise RuntimeError(
                "specialized emission capture set may only reference "
                f"Existence.unique rows; step {step_index} is "
                f"'{rows[step_index]['existence']}'."
            )

    # Mirror the generic emitter's locals-mode decision exactly so the
    # non-captured steps compile identically in both bodies.
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
            for _param_name, dependency_keys in inlinable_params:
                for dependency_key in dependency_keys:
                    dependency_key_tuple = (
                        dependency_key[0],
                        dependency_key[1],
                    )
                    if dependency_key_tuple not in key_to_step_index:
                        locals_mode = False
                        break
                if not locals_mode:
                    break
            if not locals_mode:
                break

    root_step_index = key_to_step_index.get(normalized_root_key)
    root_is_captured = (
        locals_mode
        and root_step_index is not None
        and root_step_index in captured_set
    )

    # In locals mode, alias `instance_K = cap_inst_K` only for captured steps
    # some non-captured constructor actually reads; the captured root returns
    # its slot directly with no alias.
    read_captured: set = set()
    if locals_mode:
        for step_index, row in enumerate(rows):
            if step_index in captured_set:
                continue
            for _param_name, dependency_keys in (
                    row_inlinable_common_shape(row) or ()
            ):
                for dependency_key in dependency_keys:
                    dependency_step_index = key_to_step_index[
                        (dependency_key[0], dependency_key[1])
                    ]
                    if dependency_step_index in captured_set:
                        read_captured.add(dependency_step_index)
        if (
                root_step_index is not None
                and root_step_index in captured_set
        ):
            # Direct-return path; no alias needed for the root slot itself.
            read_captured.discard(root_step_index)

    # Non-captured steps read the same factory-level hoisted aliases as the
    # generic body; captured slots (cap_*), `_generic_inner`, and the fixed
    # binding names are factory locals already, so the executor closes over
    # them directly - the signature is bare `(meld)` (see the generic
    # emitter's closure-cell rationale).
    lines = _step_alias_hoist_lines(
        rows=rows,
        locals_mode=locals_mode,
        skip_step_indexes=captured_set,
    )
    lines.extend([
        f"def {SPECIALIZED_EXECUTOR_NAME}(meld):",
        "    try:",
    ])
    for step_index in captured_step_indexes:
        lines.extend([
            (
                f"        if cap_spell_{step_index}._door_epoch "
                f"!= cap_epoch_{step_index}:"
            ),
            "            return _deopt_notify(meld)",
        ])
    lines.extend([
        "    except AttributeError:",
        "        return _deopt_notify(meld)",
    ])

    if not locals_mode:
        lines.append("    instance_results = {}")
        for step_index in captured_step_indexes:
            lines.append(
                f"    instance_results[instance_key_{step_index}]"
                f" = cap_inst_{step_index}"
            )
    else:
        for step_index in sorted(read_captured):
            lines.append(
                f"    instance_{step_index} = cap_inst_{step_index}"
            )

    for step_index, row in enumerate(rows):
        if step_index in captured_set:
            continue
        _append_step_resolution_source(
            lines=lines,
            step_index=step_index,
            row=row,
            key_to_step_index=key_to_step_index if locals_mode else None,
            positional_names=(
                positional_dependency_names[step_index]
                if positional_dependency_names is not None
                else ()
            ),
        )

    if root_is_captured:
        lines.append(f"    return cap_inst_{root_step_index}")
    elif locals_mode:
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


def build_specialized_no_overrides_executor(
        *,
        rows: Sequence[Dict[str, Any]],
        root_instance_key: Optional[Tuple[str, Optional[int]]],
        root_spell_id: Optional[str],
        spell_lookup: Dict[str, Any],
        generic_inner_executor: Callable[..., Any],
        deopt_notify: Optional[Callable[..., Any]] = None,
) -> Optional[Callable[..., Any]]:
    """
    Build the specialized inner executor from live warm-state, or decline.

    Purpose:
        One-shot post-first-run specialization: capture the live `unique`
        instances plus their spells' door epochs, emit the specialized body,
        and hydrate it through the shared executor factory cache.

    Contract:
        - Returns None (decline) when the lane has no `unique` steps or when
          any capture target is not yet live in its owner store; callers may
          retry on a later meld or give up.
        - Capture ordering is epoch-BEFORE-instance per step: if an
          invalidation lands between the two reads, the recorded epoch pairs
          with a pre-bump live epoch that keeps advancing on further events,
          so a stale pairing fails the guard compare on first use and deopts.
          The reverse order would admit a stale instance behind a fresh epoch.
        - Emission/compile ride `get_or_build_executor_factory`, so one
          compile + one exec per (shape, capture-set) per process; per-spell
          cost is one factory call.
        - The returned callable has the same `(meld)` signature and
          bare-instance return contract as the generic inner executor; the
          route-keyed door compiler wraps it into the tuple-returning runtime
          door exactly as it wraps the generic inner.

    Args:
        rows:
            Manifest step rows for the no-overrides lane.
        root_instance_key:
            Optional explicit root instance key from the manifest.
        root_spell_id:
            Root spell id used when the explicit key is absent.
        spell_lookup:
            Resolved spell-id -> live Spell map for every step row.
        generic_inner_executor:
            Already-hydrated generic inner executor; canonical deopt
            behavior and the default deopt target.
        deopt_notify:
            Optional `(meld) -> instance` deopt target bound as
            `_deopt_notify` in the emitted body. When provided it MUST
            delegate to the generic inner (same signature/return contract);
            it may additionally count misses and re-pin the plain doors
            (3-strike re-pin). When None, `_deopt_notify` binds to
            `generic_inner_executor` directly - identical behavior to the
            pre-notify contract.

    Returns:
        Optional[Callable[..., Any]]: Specialized inner executor, or None
        when specialization declines.

    Raises:
        RuntimeError:
            When rows are invalid or the root instance key is unresolvable
            (mirrors the generic hydration contract).
    """
    rows = resolve_contract_payload_rows(rows=rows, spell_lookup=spell_lookup)
    captured_step_indexes = select_specializable_step_indexes(rows)
    if not captured_step_indexes:
        return None

    captured_spells: Dict[int, Any] = {}
    captured_epochs: Dict[int, int] = {}
    captured_instances: Dict[int, Any] = {}
    for step_index in captured_step_indexes:
        row = rows[step_index]
        spell = spell_lookup.get(row["spell_id"])
        if spell is None:
            return None
        # Epoch BEFORE instance (see contract): a racing invalidation makes
        # the pairing fail its first guard compare instead of pinning a
        # stale instance behind a fresh epoch.
        captured_epoch = spell._door_epoch
        owner_creations = spell._owner_creations
        if owner_creations is None:
            return None
        live_instance = owner_creations._creations.get(row["spell_id"])
        if live_instance is None:
            return None
        captured_spells[step_index] = spell
        captured_epochs[step_index] = captured_epoch
        captured_instances[step_index] = live_instance

    resolved_root_instance_key = resolve_root_instance_key_from_rows(
        rows=rows,
        explicit_root_instance_key=root_instance_key,
        root_spell_id=root_spell_id,
    )
    inner_source = emit_specialized_step_plan_source(
        rows=rows,
        captured_step_indexes=captured_step_indexes,
        root_instance_key=resolved_root_instance_key,
        positional_dependency_names=rows_positional_dependency_names(
            rows=rows,
            spell_lookup=spell_lookup,
        ),
    )

    runtime_rows = build_runtime_rows(
        rows=rows,
        spell_lookup=spell_lookup,
    )
    bindings = _build_step_bindings(
        rows=rows,
        runtime_rows=runtime_rows,
        root_instance_key=resolved_root_instance_key,
    )
    for step_index in captured_step_indexes:
        bindings[f"cap_spell_{step_index}"] = captured_spells[step_index]
        bindings[f"cap_epoch_{step_index}"] = captured_epochs[step_index]
        bindings[f"cap_inst_{step_index}"] = captured_instances[step_index]
    bindings["_generic_inner"] = generic_inner_executor
    # Stable deopt-target binding: one identity-free source (and therefore
    # one cached factory) per shape regardless of whether a re-pin wrapper
    # is installed.
    bindings["_deopt_notify"] = (
        generic_inner_executor if deopt_notify is None else deopt_notify
    )

    factory_source = build_executor_factory_source(
        inner_source=inner_source,
        binding_names=tuple(bindings.keys()),
        executor_name=SPECIALIZED_EXECUTOR_NAME,
    )
    factory = get_or_build_executor_factory(
        factory_source=factory_source,
        source_name=_SPECIALIZED_FACTORY_SOURCE_NAME,
        static_namespace=_STEP_STATIC_NAMESPACE,
    )
    return factory(bindings)
