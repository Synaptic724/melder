import base64
import marshal
from typing import Any, Dict, Optional, Tuple

from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.codegen_creation_schema_helpers import (
    CodegenCreationSchemaHelpers as SharedCompilerExecutions,
)
from melder.aether.spellbook.spell_compiler.executor_code_cache import (
    get_or_compile_executor_code,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_no_overrides_codegen_creation_compiler import (
    _build_no_overrides_codegen_executor_source,
    _build_step_plan_executor_source,
    _normalize_transient_schema,
    _supports_transient_unrolled_plan,
)


def build_spell_cache_payload(
        *,
        spell: Any,
) -> Dict[str, Any]:
    """
    Build one cache payload from the current spell-owned compiler/runtime state.

    Purpose:
        Export the current no-overrides creation-context-facing runtime package
        for one spell into the conduit cache format owned by `CachingSystem`.

    Contract:
        - Requires phase-11 `spell_codegen_creation` to already exist.
        - Requires a no-overrides lane plan on the current `SpellCodegenPlan`.
        - Emits the no-overrides runtime payload plus route metadata.
        - Does not persist a generic overrides payload yet.
        - Stores emitted source plus marshaled code object bytes so later load
          paths can skip `compile()` when desired.

    Args:
        spell:
            Spell whose current runtime payload should be exported.

    Returns:
        Dict[str, Any]:
            JSON-serializable spell cache payload for one `spell_id`.

    Raises:
        RuntimeError:
            If the spell does not yet expose the phase-11 creation handoff.
    """
    artifact = spell._compiler_artifact
    spell_codegen_creation = artifact._spell_codegen_creation
    if spell_codegen_creation is None:
        raise RuntimeError(
            "Spell cache export requires spell_codegen_creation."
        )
    spell_codegen_plan = artifact._spell_codegen_plan
    if spell_codegen_plan is None or spell_codegen_plan.no_overrides_plan is None:
        raise RuntimeError(
            "Spell cache export requires a no_overrides lane plan."
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
    compiled_code = get_or_compile_executor_code(
        source=emitted_source,
        source_name=source_name,
    )
    creation_metadata = spell_codegen_creation.metadata
    resolve_route_key = creation_metadata.get("resolve_route_key")
    if not isinstance(resolve_route_key, str):
        raise RuntimeError(
            "Spell cache export requires resolve_route_key."
        )

    return {
        "spell_id": spell.spell_id,
        "spell_name": spell.spell_name,
        "resolve_route_key": resolve_route_key,
        "fast_transient_no_overrides_enabled": bool(
            creation_metadata.get("fast_transient_no_overrides_enabled")
        ),
        "no_overrides": {
            "root_spell_id": no_overrides_plan.root_spell_id,
            "step_spell_ids": step_spell_ids,
            "steps_rows": steps_rows,
            "transient_schema": transient_schema,
            "source_name": source_name,
            "source": emitted_source,
            "code_object_base64": base64.b64encode(
                marshal.dumps(compiled_code)
            ).decode("ascii"),
        },
    }


def _build_no_overrides_source_package(
        *,
        steps: Tuple[Any, ...],
        transient_schema: Optional[Dict[str, Any]],
) -> Tuple[str, str]:
    """
    Build emitted no-overrides source and its synthetic source name.

    Args:
        steps:
            Ordered no-overrides plan steps.
        transient_schema:
            Optional fast-transient schema for the lane.

    Returns:
        Tuple[str, str]:
            Emitted source and deterministic synthetic source name.
    """
    if transient_schema is not None and _supports_transient_unrolled_plan(steps):
        normalized_transient_schema = _normalize_transient_schema(
            transient_schema=transient_schema,
        )
        transient_source = _build_no_overrides_codegen_executor_source(
            transient_schema=normalized_transient_schema,
        )
        if transient_source is not None:
            return (
                transient_source,
                "<melder_no_overrides_codegen_creation_transient_executor>",
            )
    return (
        _build_step_plan_executor_source(steps=steps),
        "<melder_no_overrides_codegen_creation_step_executor>",
    )
