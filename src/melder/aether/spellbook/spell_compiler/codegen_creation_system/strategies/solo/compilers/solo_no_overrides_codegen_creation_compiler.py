from typing import Any, Callable, Optional, Sequence, Tuple, Union

from melder.aether.spellbook.spell_compiler.executor_code_cache import (
    get_or_compile_executor_code,
)

def compile_solo_no_overrides_codegen_creation_executor(
        *,
        spell: Any,
        solo_emit_key: str,
        fast_transient_no_overrides_enabled: bool,
        return_compiled_code_object: bool = False,
) -> Union[Callable[..., Any], Tuple[Callable[..., Any], Any]]:
    """
    Compile the solo no-overrides executor for one root spell.

    Purpose:
        Emit deterministic per-lane source for the solo family so the code
        object can be retained instead of returning handwritten Python closures.

    Contract:
        - Preserves the current callable contract exactly.
        - Emits the same route/existence logic that previously lived in the
          handwritten closure branches in this file.
        - Uses the process-wide emitted-source code-object cache.
        - When `return_compiled_code_object` is true, also returns the
          compiled `CodeType`.
    """
    has_disposal_methods = spell.has_disposal_methods
    # unique_per_conduit_lineage and unique_per_conduit_cluster both resolve into
    # the store the RESOLVING door supplies at runtime as the `owner_creations`
    # param -- the lineage-root store for lineage, the elected-leader store for
    # cluster. Neither may bind the binding-owner store, so the param path is
    # forced for both by disabling the prebound binding here.
    has_prebound_owner_creations = (
        spell._owner_creations is not None
        and solo_emit_key != "unique_per_conduit_lineage"
        and solo_emit_key != "unique_per_conduit_cluster"
    )
    source_name = (
        "<solo_no_overrides_codegen_creation:"
        f"{solo_emit_key}:"
        f"{int(fast_transient_no_overrides_enabled)}:"
        f"{int(has_disposal_methods)}:"
        f"{int(has_prebound_owner_creations)}>"
    )
    source = _build_source(
        solo_emit_key=solo_emit_key,
        fast_transient_no_overrides_enabled=fast_transient_no_overrides_enabled,
        has_disposal_methods=has_disposal_methods,
        has_prebound_owner_creations=has_prebound_owner_creations,
    )
    local_namespace: dict[str, Any] = {}
    namespace = {
        "call_target": spell.spell,
        "spell": spell,
        "spell_id": spell.spell_id,
        "prebound_owner_creations": spell._owner_creations,
        "disposal_methods": _normalize_disposal_methods(
            spell.disposal_method_names
        ),
    }
    try:
        code_object = get_or_compile_executor_code(
            source=source,
            source_name=source_name,
        )
        exec(code_object, namespace, local_namespace)
    except Exception as exc:
        raise RuntimeError(
            "Solo no-overrides codegen executor generation failed."
        ) from exc
    executor = local_namespace.get("_solo_no_overrides_codegen_creation_executor")
    if callable(executor):
        compiled_executor: Callable[..., Any] = executor
        if return_compiled_code_object:
            return compiled_executor, code_object
        return compiled_executor
    raise RuntimeError(
        "Solo no-overrides codegen source did not define callable "
        "_solo_no_overrides_codegen_creation_executor."
    )


def _build_source(
        *,
        solo_emit_key: str,
        fast_transient_no_overrides_enabled: bool,
        has_disposal_methods: bool,
        has_prebound_owner_creations: bool,
) -> str:
    """
    Return the literal emitted source for one solo no-overrides lane.
    """
    if solo_emit_key == "many":
        if fast_transient_no_overrides_enabled:
            return """def _solo_no_overrides_codegen_creation_executor():
    return call_target()
"""
        if has_disposal_methods:
            return """def _solo_no_overrides_codegen_creation_executor(
        caller_creations,
        owner_creations=None,
        caller_creations_lock_held=False,
):
    instance = call_target()
    caller_creations.add_many_creations(
        spell_id,
        instance,
        has_disposal_methods=True,
        disposal_methods=disposal_methods,
    )
    return instance
"""
        return """def _solo_no_overrides_codegen_creation_executor(
        caller_creations,
        owner_creations=None,
        caller_creations_lock_held=False,
):
    return call_target()
"""

    if solo_emit_key == "unique_per_conduit":
        if has_disposal_methods:
            return """def _solo_no_overrides_codegen_creation_executor(
        caller_creations,
        owner_creations=None,
        caller_creations_lock_held=False,
):
    instance = call_target()
    caller_creations.add_creation(
        spell_id,
        instance,
        has_disposal_methods=True,
        disposal_methods=disposal_methods,
    )
    return instance
"""
        return """def _solo_no_overrides_codegen_creation_executor(
        caller_creations,
        owner_creations=None,
        caller_creations_lock_held=False,
):
    instance = call_target()
    caller_creations.add_creation(
        spell_id,
        instance,
    )
    return instance
"""

    if solo_emit_key == "unique_per_spell_space":
        if has_disposal_methods:
            return """def _solo_no_overrides_codegen_creation_executor(
        caller_creations,
        owner_creations=None,
        caller_creations_lock_held=False,
):
    instance = call_target()
    caller_creations.add_creation(
        spell_id,
        instance,
        has_disposal_methods=True,
        disposal_methods=disposal_methods,
    )
    return instance
"""
        return """def _solo_no_overrides_codegen_creation_executor(
        caller_creations,
        owner_creations=None,
        caller_creations_lock_held=False,
):
    instance = call_target()
    caller_creations.add_creation(
        spell_id,
        instance,
    )
    return instance
"""

    if solo_emit_key == "existing_creation":
        return """def _solo_no_overrides_codegen_creation_executor(
        caller_creations,
        owner_creations=None,
        caller_creations_lock_held=False,
):
    instance = spell.user_created_object
    if instance is None:
        raise RuntimeError(
            "[MELD] EXISTING_CREATION spell has no `user_created_object` "
            f"(spell_id={spell_id})."
        )
    return instance
"""

    if solo_emit_key == "unique":
        if has_prebound_owner_creations:
            if has_disposal_methods:
                return """def _solo_no_overrides_codegen_creation_executor(
        caller_creations,
        owner_creations=None,
        caller_creations_lock_held=False,
):
    instance = call_target()
    prebound_owner_creations.add_creation(
        spell_id,
        instance,
        has_disposal_methods=True,
        disposal_methods=disposal_methods,
    )
    return instance
"""
            return """def _solo_no_overrides_codegen_creation_executor(
        caller_creations,
        owner_creations=None,
        caller_creations_lock_held=False,
):
    instance = call_target()
    prebound_owner_creations.add_creation(
        spell_id,
        instance,
    )
    return instance
"""
        if has_disposal_methods:
            return """def _solo_no_overrides_codegen_creation_executor(
        caller_creations,
        owner_creations=None,
        caller_creations_lock_held=False,
):
    instance = call_target()
    owner_creations.add_creation(
        spell_id,
        instance,
        has_disposal_methods=True,
        disposal_methods=disposal_methods,
    )
    return instance
"""
        return """def _solo_no_overrides_codegen_creation_executor(
        caller_creations,
        owner_creations=None,
        caller_creations_lock_held=False,
):
    instance = call_target()
    owner_creations.add_creation(
        spell_id,
        instance,
    )
    return instance
"""

    if solo_emit_key == "unique_per_conduit_cluster":
        if has_prebound_owner_creations:
            if has_disposal_methods:
                return """def _solo_no_overrides_codegen_creation_executor(
        caller_creations,
        owner_creations=None,
        caller_creations_lock_held=False,
):
    instance = call_target()
    prebound_owner_creations.add_creation(
        spell_id,
        instance,
        has_disposal_methods=True,
        disposal_methods=disposal_methods,
    )
    return instance
"""
            return """def _solo_no_overrides_codegen_creation_executor(
        caller_creations,
        owner_creations=None,
        caller_creations_lock_held=False,
):
    instance = call_target()
    prebound_owner_creations.add_creation(
        spell_id,
        instance,
    )
    return instance
"""
        if has_disposal_methods:
            return """def _solo_no_overrides_codegen_creation_executor(
        caller_creations,
        owner_creations=None,
        caller_creations_lock_held=False,
):
    instance = call_target()
    owner_creations.add_creation(
        spell_id,
        instance,
        has_disposal_methods=True,
        disposal_methods=disposal_methods,
    )
    return instance
"""
        return """def _solo_no_overrides_codegen_creation_executor(
        caller_creations,
        owner_creations=None,
        caller_creations_lock_held=False,
):
    instance = call_target()
    owner_creations.add_creation(
        spell_id,
        instance,
    )
    return instance
"""

    if solo_emit_key == "unique_per_conduit_lineage":
        if has_prebound_owner_creations:
            if has_disposal_methods:
                return """def _solo_no_overrides_codegen_creation_executor(
        caller_creations,
        owner_creations=None,
        caller_creations_lock_held=False,
):
    instance = call_target()
    prebound_owner_creations.add_creation(
        spell_id,
        instance,
        has_disposal_methods=True,
        disposal_methods=disposal_methods,
    )
    return instance
"""
            return """def _solo_no_overrides_codegen_creation_executor(
        caller_creations,
        owner_creations=None,
        caller_creations_lock_held=False,
):
    instance = call_target()
    prebound_owner_creations.add_creation(
        spell_id,
        instance,
    )
    return instance
"""
        if has_disposal_methods:
            return """def _solo_no_overrides_codegen_creation_executor(
        caller_creations,
        owner_creations=None,
        caller_creations_lock_held=False,
):
    instance = call_target()
    owner_creations.add_creation(
        spell_id,
        instance,
        has_disposal_methods=True,
        disposal_methods=disposal_methods,
    )
    return instance
"""
        return """def _solo_no_overrides_codegen_creation_executor(
        caller_creations,
        owner_creations=None,
        caller_creations_lock_held=False,
):
    instance = call_target()
    owner_creations.add_creation(
        spell_id,
        instance,
    )
    return instance
"""

    raise RuntimeError(
        f"Unsupported solo no-overrides emit key: {solo_emit_key}"
    )


def _normalize_disposal_methods(
        disposal_method_names: Sequence[str],
) -> Optional[Tuple[str, ...]]:
    """
    Normalize spell-owned disposal metadata for creations registration.
    """
    if not disposal_method_names:
        return None
    return tuple(disposal_method_names)
