"""
Cache codec for the generalized codegen-creation family.

The package IS the manifest. Because phase 11 already flows through
serialization-shaped data, cache export is "read the manifest off the creation
artifact" and cache load is "publish lazy doors over the manifest". There is
no second assembly program and no rehydration at conjure.

Contract:
    - `build_package(spell)` returns a marshal-safe dict (pure data, no code
      objects). Compiled code is reconstructed deterministically at first meld
      through the process-wide executor code/factory caches, so the compile
      cost is one-time per source shape per process.
    - `load_creation_context_lazy(spell, package, publish=...)` publishes one
      `CreationContext` with zero hydration work; the first meld hydrates and
      swaps the hot doors in.
    - `load_creation_context(spell, package, publish=...)` is the eager
      variant for tests/diagnostics that want hydration to happen at load.
"""

from typing import Any, Dict

from melder.aether.conduit.meld.creation_context.creation_context import (
    CreationContext,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.hydration.generalized_binding_resolver import (
    SpellbookBindingResolver,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.hydration.generalized_hydrator import (
    build_lazy_creation_executors,
    hydrate_creation_executors,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.manifest.generalized_manifest import (
    FAMILY_ID,
    MANIFEST_METADATA_KEY,
    validate_generalized_manifest,
)

PACKAGE_VERSION = 2


def build_package(spell: Any) -> Dict[str, Any]:
    """
    Build the marshal-safe cache package for one generalized spell.

    Raises:
        RuntimeError:
            When phase-11 output or the family manifest is missing.
    """
    artifact = spell._compiler_artifact
    if artifact is None:
        raise RuntimeError("cache export requires a compiler artifact.")
    spell_codegen_creation = artifact._spell_codegen_creation
    if spell_codegen_creation is None:
        raise RuntimeError("cache export requires spell_codegen_creation.")
    manifest = spell_codegen_creation.metadata.get(MANIFEST_METADATA_KEY)
    if manifest is None:
        raise RuntimeError(
            "cache export requires a generalized manifest; the spell's "
            "phase-11 output was not produced by the generalized family."
        )
    validate_generalized_manifest(manifest)
    return {
        "package_version": PACKAGE_VERSION,
        "family_id": FAMILY_ID,
        "spell_id": spell.spell_id,
        "manifest": manifest,
    }


def is_generalized_manifest_package(package: Any) -> bool:
    """
    Return whether one decoded cache payload is a generalized manifest package.

    Contract:
        - Pure shape check; never raises on foreign payload shapes.
    """
    return (
        isinstance(package, dict)
        and package.get("family_id") == FAMILY_ID
        and package.get("package_version") == PACKAGE_VERSION
        and isinstance(package.get("manifest"), dict)
    )


def load_creation_context_lazy(
        spell: Any,
        package: Dict[str, Any],
        *,
        publish: bool = True,
) -> CreationContext:
    """
    Publish one spell-bound `CreationContext` with ZERO hydration work.

    Purpose:
        Make the conjure-time cache load free. The published context carries
        cold doors that hydrate both lanes once - on the first meld call -
        then swap the hot doors into the context's executor slots so every
        later meld runs the unwrapped fast path.

    Raises:
        RuntimeError:
            At load time when the package shape is invalid; at first meld when
            live prerequisites (phases 1-7, ownership wiring) are missing.
    """
    if package.get("package_version") != PACKAGE_VERSION:
        raise RuntimeError(
            "generalized package version mismatch: "
            f"{package.get('package_version')!r} != {PACKAGE_VERSION}."
        )
    if package.get("family_id") != FAMILY_ID:
        raise RuntimeError(
            "generalized package family mismatch: "
            f"{package.get('family_id')!r}."
        )
    manifest = validate_generalized_manifest(package.get("manifest"))

    creation_context_factory = spell._creation_context_factory
    if creation_context_factory is None:
        raise RuntimeError("Spell has no CreationContextFactory.")
    creation_gate, creation_gate_index_id = (
        creation_context_factory._resolve_runtime_gate_for_spell(spell)
    )
    cold_no_overrides_door, cold_overrides_door = (
        build_lazy_creation_executors(
            manifest=manifest,
            spell=spell,
        )
    )
    return CreationContext.load_cached(
        spell=spell,
        dynamic_environment=spell._dynamic_environment,
        creation_gate=creation_gate,
        creation_gate_index_id=creation_gate_index_id,
        no_overrides_executor=cold_no_overrides_door,
        overrides_executor=cold_overrides_door,
        publish=publish,
    )


def load_creation_context(
        spell: Any,
        package: Dict[str, Any],
        *,
        publish: bool = True,
) -> CreationContext:
    """
    Rebuild one spell-bound `CreationContext` eagerly from a family package.

    Contract:
        - Hydrates both runtime doors immediately through the exact assembly
          program the lazy path runs at first meld. Intended for tests and
          diagnostics; production loads should use the lazy variant.
    """
    if package.get("package_version") != PACKAGE_VERSION:
        raise RuntimeError(
            "generalized package version mismatch: "
            f"{package.get('package_version')!r} != {PACKAGE_VERSION}."
        )
    if package.get("family_id") != FAMILY_ID:
        raise RuntimeError(
            "generalized package family mismatch: "
            f"{package.get('family_id')!r}."
        )
    manifest = validate_generalized_manifest(package.get("manifest"))

    resolver = SpellbookBindingResolver(spell=spell)
    hydrated = hydrate_creation_executors(
        manifest=manifest,
        resolver=resolver,
    )

    creation_context_factory = spell._creation_context_factory
    if creation_context_factory is None:
        raise RuntimeError("Spell has no CreationContextFactory.")
    creation_gate, creation_gate_index_id = (
        creation_context_factory._resolve_runtime_gate_for_spell(spell)
    )
    return CreationContext.load_cached(
        spell=spell,
        dynamic_environment=spell._dynamic_environment,
        creation_gate=creation_gate,
        creation_gate_index_id=creation_gate_index_id,
        no_overrides_executor=hydrated.no_overrides_executor,
        overrides_executor=hydrated.overrides_executor,
        publish=publish,
    )
