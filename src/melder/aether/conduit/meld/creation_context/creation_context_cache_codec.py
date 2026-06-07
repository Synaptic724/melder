"""
Reloadable codec for CreationContext-facing phase-11 assets.

Purpose:
    Build and reload the durable, conduit-agnostic cache payload for one
    spell's no-overrides runtime lane. The cached unit is the *inner*
    codegen-creation executor (its emitted source compiled to a `CodeType`)
    plus the schema-only rows needed to rebuild its execution namespace from
    the live Spellbook. The owner-dependent outer route wrapper is rebuilt at
    load time, so nothing conduit-scoped is ever frozen into the cache.

Contract:
    - `build_no_overrides_package(spell)` returns a marshal-safe dict
      (primitives, tuples, dicts, and one `CodeType`) for the no-overrides lane.
    - `load_no_overrides_executor(spell, package)` rebuilds the inner executor
      from the package against the live Spellbook, then wraps it with the
      owner-aware outer template using `spell._owner_creations`.
    - The payload deliberately excludes any per-conduit runtime object so a
      cached `CodeType` is reusable across conduits/runs (subject only to the
      Python-version stamp owned by `CachingSystem`).

Note:
    The override lane is not cached here yet. A full_hit consumer is expected
    to rebuild the override lane through the normal phase-11 path until override
    reload lands.
"""

from typing import Any, Dict, Optional, Tuple

from melder.aether.conduit.meld.creation_context.creation_context_codegen import (
    compile_creation_context_hooks_no_overrides_executor,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.codegen_creation_schema_helpers import (
    CodegenCreationSchemaHelpers as SharedCompilerExecutions,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_no_overrides_codegen_creation_compiler import (
    _build_executor_namespace,
    _build_no_overrides_codegen_executor_source,
    _build_step_executor_namespace,
    _build_step_plan_executor_source,
    _hydrate_steps_from_rows,
    _normalize_transient_schema,
    _resolve_root_instance_key,
    _supports_transient_unrolled_plan,
)
from melder.utilities.custom_exceptions.spell_space_scope_error import (
    SpellSpaceScopeError,
)


PACKAGE_VERSION: int = 1
_NO_OVERRIDES_EXECUTOR_NAME = "_no_overrides_codegen_creation_executor"
_NO_OVERRIDES_TRANSIENT_SOURCE_NAME = (
    "<melder_no_overrides_codegen_creation_transient_executor>"
)
_NO_OVERRIDES_STEP_SOURCE_NAME = (
    "<melder_no_overrides_codegen_creation_step_executor>"
)

_SHARED_ROUTE_FAMILIES = (
    "spellspace",
    "unique_per_conduit",
    "many",
    "shared",
)


def build_no_overrides_package(spell: Any) -> Dict[str, Any]:
    """
    Build the marshal-safe no-overrides cache package for one spell.

    Contract:
        - Requires constructed-spell phase-11 output to already exist.
        - Returns a dict of primitives/tuples/dicts plus one compiled
          `CodeType` for the inner no-overrides executor.

    Raises:
        RuntimeError:
            When phase-11 creation/plan output is missing.
    """
    artifact = spell._compiler_artifact
    spell_codegen_creation = artifact._spell_codegen_creation
    if spell_codegen_creation is None:
        raise RuntimeError(
            "no-overrides cache export requires spell_codegen_creation."
        )
    spell_codegen_plan = artifact._spell_codegen_plan
    if spell_codegen_plan is None or spell_codegen_plan.no_overrides_plan is None:
        raise RuntimeError(
            "no-overrides cache export requires a no_overrides lane plan."
        )
    spell_codegen_model = artifact._spell_codegen_model
    if spell_codegen_model is None:
        raise RuntimeError(
            "no-overrides cache export requires a spell_codegen_model."
        )

    no_overrides_plan = spell_codegen_plan.no_overrides_plan
    steps = tuple(no_overrides_plan.steps)
    steps_rows = tuple(
        SharedCompilerExecutions.build_phase11_step_ir_row(
            step,
            include_override_metadata=False,
        )
        for step in steps
    )
    step_spell_ids = tuple(
        step.spell.spell_index.current
        for step in steps
    )
    transient_schema = SharedCompilerExecutions.build_fast_transient_schema(
        no_overrides_plan.fast_transient_plan,
    )
    emitted_source, source_name = _build_no_overrides_source_package(
        steps=steps,
        transient_schema=transient_schema,
    )
    compiled_code = compile(emitted_source, source_name, "exec")

    return {
        "package_version": PACKAGE_VERSION,
        "spell_id": spell.spell_id,
        "resolve_route_key": _resolve_route_key(spell_codegen_model),
        "fast_transient_no_overrides_enabled": bool(
            no_overrides_plan.fast_transient_plan is not None
        ),
        "no_overrides": {
            "root_spell_id": no_overrides_plan.root_spell_id,
            "step_spell_ids": step_spell_ids,
            "steps_rows": steps_rows,
            "transient_schema": transient_schema,
            "source_name": source_name,
            "code_object": compiled_code,
        },
    }


def load_no_overrides_executor(spell: Any, package: Dict[str, Any]) -> Any:
    """
    Rebuild the owner-aware outer no-overrides executor from a cache package.

    Contract:
        - Rebuilds the inner executor from the package against the live
          Spellbook spell pool.
        - Wraps the inner executor with the owner-aware outer template using
          the spell's currently bound `_owner_creations`.

    Raises:
        RuntimeError:
            When the package references an unknown spell id, cannot resolve the
            root instance key, or does not produce a callable inner executor.
    """
    no_overrides_payload = package["no_overrides"]
    spellbook = spell._spellbook
    if spellbook is None:
        raise RuntimeError("Spell has no owning Spellbook surface.")

    spell_lookup: Dict[str, Any] = {}
    for spell_id in no_overrides_payload["step_spell_ids"]:
        resolved_spell = spellbook._spell_id_pool.get(spell_id)
        if resolved_spell is None:
            raise RuntimeError(
                "Cached no-overrides payload references unknown spell_id "
                f"'{spell_id}'."
            )
        spell_lookup[spell_id] = resolved_spell

    steps = _hydrate_steps_from_rows(
        steps_rows=no_overrides_payload["steps_rows"],
        spell_lookup=spell_lookup,
    )
    transient_schema = no_overrides_payload["transient_schema"]
    if transient_schema is not None and _supports_transient_unrolled_plan(steps):
        namespace = _build_executor_namespace(
            transient_schema=_normalize_transient_schema(
                transient_schema=transient_schema,
            ),
            steps=steps,
        )
    else:
        root_instance_key = _resolve_root_instance_key(
            steps=steps,
            root_spell_id=no_overrides_payload["root_spell_id"],
        )
        if root_instance_key is None:
            raise RuntimeError(
                "Cached no-overrides payload could not resolve root_instance_key."
            )
        namespace = _build_step_executor_namespace(
            steps=steps,
            root_instance_key=root_instance_key,
        )

    local_namespace: Dict[str, Any] = {}
    exec(no_overrides_payload["code_object"], namespace, local_namespace)
    inner_executor = local_namespace.get(_NO_OVERRIDES_EXECUTOR_NAME)
    if not callable(inner_executor):
        raise RuntimeError(
            "Cached no-overrides payload did not define a callable "
            f"{_NO_OVERRIDES_EXECUTOR_NAME}."
        )

    return compile_creation_context_hooks_no_overrides_executor(
        resolve_route_key=package["resolve_route_key"],
        fast_transient_no_overrides_enabled=bool(
            package["fast_transient_no_overrides_enabled"]
        ),
        spell=spell,
        spell_id=spell.spell_id,
        owner_creations=spell._owner_creations,
        no_overrides_executor=inner_executor,
        spell_space_scope_error_type=SpellSpaceScopeError,
    )


def _build_no_overrides_source_package(
        *,
        steps: Tuple[Any, ...],
        transient_schema: Optional[Dict[str, Any]],
) -> Tuple[str, str]:
    """
    Build emitted inner no-overrides source plus its synthetic source name.

    Mirrors the live phase-11 source selection: a transient unrolled body when
    the plan supports it, otherwise the general step-plan body.
    """
    if transient_schema is not None and _supports_transient_unrolled_plan(steps):
        normalized_transient_schema = _normalize_transient_schema(
            transient_schema=transient_schema,
        )
        transient_source = _build_no_overrides_codegen_executor_source(
            transient_schema=normalized_transient_schema,
        )
        if transient_source is not None:
            return transient_source, _NO_OVERRIDES_TRANSIENT_SOURCE_NAME
    step_source = _build_step_plan_executor_source(
        steps=steps,
    )
    return step_source, _NO_OVERRIDES_STEP_SOURCE_NAME


def _resolve_route_key(spell_codegen_model: Any) -> str:
    """
    Resolve the runtime route key from the codegen model.

    Mirrors the phase-11 finalize route resolution so the cached package can
    rebuild the correct outer template at load time.
    """
    if spell_codegen_model.build_kind == "existing_creation":
        return "existing_creation"
    route_family = spell_codegen_model.route_family
    if route_family in _SHARED_ROUTE_FAMILIES:
        return route_family
    raise RuntimeError(
        "SpellCodegenModel route_family is not cacheable for the no-overrides "
        f"lane: {route_family!r}."
    )
