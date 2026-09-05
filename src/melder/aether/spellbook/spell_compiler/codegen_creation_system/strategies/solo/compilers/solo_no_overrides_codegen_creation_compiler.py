from typing import Any, Callable, Optional, Tuple, Union

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
        - Binds the established Spell disposal list directly into each fresh
          executor namespace, including when its code object is reused.
        - When `return_compiled_code_object` is true, also returns the
          compiled `CodeType`.
    """
    has_disposal_methods = spell.has_disposal_methods
    source_name = (
        "<solo_no_overrides_codegen_creation:"
        f"{solo_emit_key}:"
        f"{int(fast_transient_no_overrides_enabled)}:"
        f"{int(has_disposal_methods)}>"
    )
    source = _build_source(
        solo_emit_key=solo_emit_key,
        fast_transient_no_overrides_enabled=fast_transient_no_overrides_enabled,
        has_disposal_methods=has_disposal_methods,
    )
    local_namespace: dict[str, Any] = {}
    namespace = {
        "call_target": spell.spell,
        "spell": spell,
        "spell_id": spell.spell_id,
    }
    if has_disposal_methods:
        namespace["disposal_methods"] = _normalize_disposal_methods(
            spell.disposal_method_names
        )
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
) -> str:
    """
    Return the literal emitted source for one solo no-overrides lane.

    Each lane takes the resolving `meld` and reads its own creation store off
    it, mirroring the per-existence store selection the meld front doors
    perform: `unique_per_conduit` -> `meld._conduit_creations`,
    `unique_per_spell_space` -> `meld._spellspace_creations`,
    `unique_per_conduit_lineage` -> `meld._root_creations`,
    `unique_per_conduit_cluster` -> `meld._cluster_creations.resolved_store()`.
    `unique` adds to the spell-owned `spell._owner_creations` store, and
    `many` with disposal is tracked in the innermost active scope.
    """
    if solo_emit_key == "many":
        if fast_transient_no_overrides_enabled:
            return """def _solo_no_overrides_codegen_creation_executor(meld):
    return call_target()
"""
        if has_disposal_methods:
            # `many` with disposal is tracked for cleanup in the innermost active
            # scope of the resolving meld: the spellspace scope store when melded
            # through a SpellSpaceMeld, otherwise the owning conduit store.
            # `_spellspace_creations` is None on a ConduitMeld and the live scope
            # store on a SpellSpaceMeld, so one None check routes it.
            return """def _solo_no_overrides_codegen_creation_executor(meld):
    instance = call_target()
    many_creations = meld._spellspace_creations
    if many_creations is None:
        many_creations = meld._conduit_creations
    many_creations.add_many_creations(
        spell_id,
        instance,
        has_disposal_methods=True,
        disposal_methods=disposal_methods,
    )
    return instance
"""
        return """def _solo_no_overrides_codegen_creation_executor(meld):
    return call_target()
"""

    if solo_emit_key == "unique_per_conduit":
        if has_disposal_methods:
            return """def _solo_no_overrides_codegen_creation_executor(meld):
    instance = call_target()
    meld._conduit_creations.add_creation(
        spell_id,
        instance,
        has_disposal_methods=True,
        disposal_methods=disposal_methods,
    )
    return instance
"""
        return """def _solo_no_overrides_codegen_creation_executor(meld):
    instance = call_target()
    meld._conduit_creations.add_creation(
        spell_id,
        instance,
    )
    return instance
"""

    if solo_emit_key == "unique_per_spell_space":
        if has_disposal_methods:
            return """def _solo_no_overrides_codegen_creation_executor(meld):
    instance = call_target()
    meld._spellspace_creations.add_creation(
        spell_id,
        instance,
        has_disposal_methods=True,
        disposal_methods=disposal_methods,
    )
    return instance
"""
        return """def _solo_no_overrides_codegen_creation_executor(meld):
    instance = call_target()
    meld._spellspace_creations.add_creation(
        spell_id,
        instance,
    )
    return instance
"""

    if solo_emit_key == "existing_creation":
        return """def _solo_no_overrides_codegen_creation_executor(meld):
    instance = spell.user_created_object
    if instance is None:
        raise RuntimeError(
            "[MELD] EXISTING_CREATION spell has no `user_created_object` "
            f"(spell_id={spell_id})."
        )
    return instance
"""

    if solo_emit_key == "unique":
        if has_disposal_methods:
            return """def _solo_no_overrides_codegen_creation_executor(meld):
    instance = call_target()
    spell._owner_creations.add_creation(
        spell_id,
        instance,
        has_disposal_methods=True,
        disposal_methods=disposal_methods,
    )
    return instance
"""
        return """def _solo_no_overrides_codegen_creation_executor(meld):
    instance = call_target()
    spell._owner_creations.add_creation(
        spell_id,
        instance,
    )
    return instance
"""

    if solo_emit_key == "unique_per_conduit_cluster":
        if has_disposal_methods:
            return """def _solo_no_overrides_codegen_creation_executor(meld):
    instance = call_target()
    meld._cluster_creations.resolved_store().add_creation(
        spell_id,
        instance,
        has_disposal_methods=True,
        disposal_methods=disposal_methods,
    )
    return instance
"""
        return """def _solo_no_overrides_codegen_creation_executor(meld):
    instance = call_target()
    meld._cluster_creations.resolved_store().add_creation(
        spell_id,
        instance,
    )
    return instance
"""

    if solo_emit_key == "unique_per_conduit_lineage":
        if has_disposal_methods:
            return """def _solo_no_overrides_codegen_creation_executor(meld):
    instance = call_target()
    meld._root_creations.add_creation(
        spell_id,
        instance,
        has_disposal_methods=True,
        disposal_methods=disposal_methods,
    )
    return instance
"""
        return """def _solo_no_overrides_codegen_creation_executor(meld):
    instance = call_target()
    meld._root_creations.add_creation(
        spell_id,
        instance,
    )
    return instance
"""

    raise RuntimeError(
        f"Unsupported solo no-overrides emit key: {solo_emit_key}"
    )


def _normalize_disposal_methods(
        disposal_method_names: list[str],
) -> Optional[list[str]]:
    """
    Retain the established Spell list for registration; an empty list remains None.

    No names are copied, reordered, or revalidated. Binding owns that policy,
    and this namespace must not own a separate disposal collection.
    """
    if not disposal_method_names:
        return None
    return disposal_method_names
