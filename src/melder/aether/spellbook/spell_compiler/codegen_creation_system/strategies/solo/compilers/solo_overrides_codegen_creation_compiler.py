from typing import Any, Callable, Dict, Optional, Sequence, Tuple

from melder.aether.spellbook.spell_compiler.executor_code_cache import (
    get_or_compile_executor_code,
)


def compile_solo_overrides_codegen_creation_executor(
        *,
        spell: Any,
        solo_emit_key: str,
) -> Callable[..., Any]:
    """
    Compile the solo overrides executor for one root spell.

    Purpose:
        Emit deterministic per-lane source for the solo family so the code
        object can be cached instead of returning handwritten Python closures.

    Contract:
        - Preserves the current callable contract exactly.
        - Emits the same route/existence logic that previously lived in the
          handwritten closure branches in this file.
        - Reuses the process-wide executor cache keyed by emitted source.
    """
    has_disposal_methods = spell.has_disposal_methods
    has_prebound_owner_creations = spell._owner_creations is not None
    source_name = (
        "<solo_overrides_codegen_creation:"
        f"{solo_emit_key}:"
        f"{int(has_disposal_methods)}:"
        f"{int(has_prebound_owner_creations)}>"
    )
    source = _build_source(
        solo_emit_key=solo_emit_key,
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
        "_invoke_with_overrides": _invoke_with_overrides,
    }
    try:
        code_object = get_or_compile_executor_code(
            source=source,
            source_name=source_name,
        )
        exec(code_object, namespace, local_namespace)
    except Exception as exc:
        raise RuntimeError(
            "Solo overrides codegen executor generation failed."
        ) from exc
    executor = local_namespace.get("_solo_overrides_codegen_creation_executor")
    if callable(executor):
        compiled_executor: Callable[..., Any] = executor
        return compiled_executor
    raise RuntimeError(
        "Solo overrides codegen source did not define callable "
        "_solo_overrides_codegen_creation_executor."
    )


def _build_source(
        *,
        solo_emit_key: str,
        has_disposal_methods: bool,
        has_prebound_owner_creations: bool,
) -> str:
    """
    Return the literal emitted source for one solo overrides lane.
    """
    if solo_emit_key == "many":
        if has_disposal_methods:
            return """def _solo_overrides_codegen_creation_executor(
        caller_creations,
        overrides,
        caller_creations_lock_held=False,
):
    instance = _invoke_with_overrides(
        call_target=call_target,
        overrides=overrides,
    )
    caller_creations.add_many_creations(
        spell_id,
        instance,
        has_disposal_methods=True,
        disposal_methods=disposal_methods,
    )
    return instance
"""
        return """def _solo_overrides_codegen_creation_executor(
        caller_creations,
        overrides,
        caller_creations_lock_held=False,
):
    return _invoke_with_overrides(
        call_target=call_target,
        overrides=overrides,
    )
"""

    if solo_emit_key == "unique_per_conduit":
        if has_disposal_methods:
            return """def _solo_overrides_codegen_creation_executor(
        caller_creations,
        overrides,
        caller_creations_lock_held=False,
):
    instance = _invoke_with_overrides(
        call_target=call_target,
        overrides=overrides,
    )
    caller_creations.add_creation(
        spell_id,
        instance,
        has_disposal_methods=True,
        disposal_methods=disposal_methods,
    )
    return instance
"""
        return """def _solo_overrides_codegen_creation_executor(
        caller_creations,
        overrides,
        caller_creations_lock_held=False,
):
    instance = _invoke_with_overrides(
        call_target=call_target,
        overrides=overrides,
    )
    caller_creations.add_creation(
        spell_id,
        instance,
    )
    return instance
"""

    if solo_emit_key == "unique_per_spell_space":
        if has_disposal_methods:
            return """def _solo_overrides_codegen_creation_executor(
        caller_creations,
        overrides,
        caller_creations_lock_held=False,
):
    instance = _invoke_with_overrides(
        call_target=call_target,
        overrides=overrides,
    )
    caller_creations.add_creation(
        spell_id,
        instance,
        has_disposal_methods=True,
        disposal_methods=disposal_methods,
    )
    return instance
"""
        return """def _solo_overrides_codegen_creation_executor(
        caller_creations,
        overrides,
        caller_creations_lock_held=False,
):
    instance = _invoke_with_overrides(
        call_target=call_target,
        overrides=overrides,
    )
    caller_creations.add_creation(
        spell_id,
        instance,
    )
    return instance
"""

    if solo_emit_key == "existing_creation":
        return """def _solo_overrides_codegen_creation_executor(
        caller_creations,
        overrides,
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
                return """def _solo_overrides_codegen_creation_executor(
        caller_creations,
        overrides,
        caller_creations_lock_held=False,
):
    instance = _invoke_with_overrides(
        call_target=call_target,
        overrides=overrides,
    )
    prebound_owner_creations.add_creation(
        spell_id,
        instance,
        has_disposal_methods=True,
        disposal_methods=disposal_methods,
    )
    return instance
"""
            return """def _solo_overrides_codegen_creation_executor(
        caller_creations,
        overrides,
        caller_creations_lock_held=False,
):
    instance = _invoke_with_overrides(
        call_target=call_target,
        overrides=overrides,
    )
    prebound_owner_creations.add_creation(
        spell_id,
        instance,
    )
    return instance
"""
        if has_disposal_methods:
            return """def _solo_overrides_codegen_creation_executor(
        caller_creations,
        overrides,
        caller_creations_lock_held=False,
):
    instance = _invoke_with_overrides(
        call_target=call_target,
        overrides=overrides,
    )
    dynamic_owner_creations = spell._owner_creations
    dynamic_owner_creations.add_creation(
        spell_id,
        instance,
        has_disposal_methods=True,
        disposal_methods=disposal_methods,
    )
    return instance
"""
        return """def _solo_overrides_codegen_creation_executor(
        caller_creations,
        overrides,
        caller_creations_lock_held=False,
):
    instance = _invoke_with_overrides(
        call_target=call_target,
        overrides=overrides,
    )
    dynamic_owner_creations = spell._owner_creations
    dynamic_owner_creations.add_creation(
        spell_id,
        instance,
    )
    return instance
"""

    if solo_emit_key == "unique_per_conduit_cluster":
        if has_prebound_owner_creations:
            if has_disposal_methods:
                return """def _solo_overrides_codegen_creation_executor(
        caller_creations,
        overrides,
        caller_creations_lock_held=False,
):
    instance = _invoke_with_overrides(
        call_target=call_target,
        overrides=overrides,
    )
    prebound_owner_creations.add_creation(
        spell_id,
        instance,
        has_disposal_methods=True,
        disposal_methods=disposal_methods,
    )
    return instance
"""
            return """def _solo_overrides_codegen_creation_executor(
        caller_creations,
        overrides,
        caller_creations_lock_held=False,
):
    instance = _invoke_with_overrides(
        call_target=call_target,
        overrides=overrides,
    )
    prebound_owner_creations.add_creation(
        spell_id,
        instance,
    )
    return instance
"""
        if has_disposal_methods:
            return """def _solo_overrides_codegen_creation_executor(
        caller_creations,
        overrides,
        caller_creations_lock_held=False,
):
    instance = _invoke_with_overrides(
        call_target=call_target,
        overrides=overrides,
    )
    dynamic_owner_creations = spell._owner_creations
    dynamic_owner_creations.add_creation(
        spell_id,
        instance,
        has_disposal_methods=True,
        disposal_methods=disposal_methods,
    )
    return instance
"""
        return """def _solo_overrides_codegen_creation_executor(
        caller_creations,
        overrides,
        caller_creations_lock_held=False,
):
    instance = _invoke_with_overrides(
        call_target=call_target,
        overrides=overrides,
    )
    dynamic_owner_creations = spell._owner_creations
    dynamic_owner_creations.add_creation(
        spell_id,
        instance,
    )
    return instance
"""

    if solo_emit_key == "unique_per_conduit_lineage":
        if has_prebound_owner_creations:
            if has_disposal_methods:
                return """def _solo_overrides_codegen_creation_executor(
        caller_creations,
        overrides,
        caller_creations_lock_held=False,
):
    instance = _invoke_with_overrides(
        call_target=call_target,
        overrides=overrides,
    )
    prebound_owner_creations.add_creation(
        spell_id,
        instance,
        has_disposal_methods=True,
        disposal_methods=disposal_methods,
    )
    return instance
"""
            return """def _solo_overrides_codegen_creation_executor(
        caller_creations,
        overrides,
        caller_creations_lock_held=False,
):
    instance = _invoke_with_overrides(
        call_target=call_target,
        overrides=overrides,
    )
    prebound_owner_creations.add_creation(
        spell_id,
        instance,
    )
    return instance
"""
        if has_disposal_methods:
            return """def _solo_overrides_codegen_creation_executor(
        caller_creations,
        overrides,
        caller_creations_lock_held=False,
):
    instance = _invoke_with_overrides(
        call_target=call_target,
        overrides=overrides,
    )
    dynamic_owner_creations = spell._owner_creations
    dynamic_owner_creations.add_creation(
        spell_id,
        instance,
        has_disposal_methods=True,
        disposal_methods=disposal_methods,
    )
    return instance
"""
        return """def _solo_overrides_codegen_creation_executor(
        caller_creations,
        overrides,
        caller_creations_lock_held=False,
):
    instance = _invoke_with_overrides(
        call_target=call_target,
        overrides=overrides,
    )
    dynamic_owner_creations = spell._owner_creations
    dynamic_owner_creations.add_creation(
        spell_id,
        instance,
    )
    return instance
"""

    raise RuntimeError(
        f"Unsupported solo overrides emit key: {solo_emit_key}"
    )


def _invoke_with_overrides(
        *,
        call_target: Any,
        overrides: Optional[Dict[str, Any]],
) -> Any:
    """
    Invoke the solo root call target with root-only override payloads.
    """
    if not overrides:
        return call_target()

    raw_args = overrides.get("__args__")
    if raw_args is None:
        return call_target(**overrides)

    if isinstance(raw_args, tuple):
        positional_overrides = raw_args
    elif isinstance(raw_args, list):
        positional_overrides = tuple(raw_args)
    else:
        raise RuntimeError("__args__ override must be a list or tuple.")

    if len(overrides) == 1:
        return call_target(*positional_overrides)

    keyword_overrides: Dict[str, Any] = {}
    for param_name, value in overrides.items():
        if param_name == "__args__":
            continue
        keyword_overrides[param_name] = value
    return call_target(*positional_overrides, **keyword_overrides)


def _normalize_disposal_methods(
        disposal_method_names: Sequence[str],
) -> Optional[Tuple[str, ...]]:
    """
    Normalize spell-owned disposal metadata for creations registration.
    """
    if not disposal_method_names:
        return None
    return tuple(disposal_method_names)
