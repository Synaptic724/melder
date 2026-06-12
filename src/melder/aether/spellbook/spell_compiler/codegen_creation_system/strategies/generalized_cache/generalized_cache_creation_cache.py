"""
Cache codec for the generalized_cache codegen-creation family.

The package IS the manifest. Because phase 11 already flows through
serialization-shaped data, cache export is "read the manifest off the creation
artifact" and cache load is "run the same hydrator the live path ran". There
is no second assembly program, no step re-hydration logic, and no private
compiler imports in this module.

Contract:
    - `build_package(spell)` returns a marshal-safe dict (pure data, no code
      objects). Compiled code is reconstructed deterministically at load
      through the process-wide executor code/factory caches, so the compile
      cost is one-time per source shape per process.
    - `load_creation_context(spell, package, publish=...)` requires phases 1-7
      to be live and ownership wiring done (`spell._owner_creations`), exactly
      like the legacy loader. It rebuilds both doors through the family
      hydrator and publishes one `CreationContext`.
"""

from typing import Any, Dict

from melder.aether.conduit.meld.creation_context.creation_context import (
    CreationContext,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized_cache.hydration.generalized_cache_binding_resolver import (
    SpellbookBindingResolver,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized_cache.hydration.generalized_cache_hydrator import (
    hydrate_creation_executors,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized_cache.manifest.generalized_cache_manifest import (
    FAMILY_ID,
    MANIFEST_METADATA_KEY,
    validate_generalized_cache_manifest,
)

PACKAGE_VERSION = 1


def build_package(spell: Any) -> Dict[str, Any]:
    """
    Build the marshal-safe cache package for one generalized_cache spell.

    Contract:
        - Requires the spell's phase-11 output to have been produced by the
          generalized_cache family (the manifest must be present in creation
          metadata).

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
            "cache export requires a generalized_cache manifest; the spell's "
            "phase-11 output was not produced by the generalized_cache family."
        )
    validate_generalized_cache_manifest(manifest)
    return {
        "package_version": PACKAGE_VERSION,
        "family_id": FAMILY_ID,
        "spell_id": spell.spell_id,
        "manifest": manifest,
    }


def load_creation_context(
        spell: Any,
        package: Dict[str, Any],
        *,
        publish: bool = True,
) -> CreationContext:
    """
    Rebuild one spell-bound `CreationContext` from a family cache package.

    Contract:
        - Hydrates both runtime doors through the exact assembly program the
          live phase-11 path runs (`hydrate_creation_executors`).
        - Requires phases 1-7 live (phase-5 path registry) and ownership
          wiring (`spell._owner_creations`).

    Raises:
        RuntimeError:
            When the package or live prerequisites are invalid.
    """
    if package.get("package_version") != PACKAGE_VERSION:
        raise RuntimeError(
            "generalized_cache package version mismatch: "
            f"{package.get('package_version')!r} != {PACKAGE_VERSION}."
        )
    if package.get("family_id") != FAMILY_ID:
        raise RuntimeError(
            "generalized_cache package family mismatch: "
            f"{package.get('family_id')!r}."
        )
    manifest = validate_generalized_cache_manifest(package.get("manifest"))

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
